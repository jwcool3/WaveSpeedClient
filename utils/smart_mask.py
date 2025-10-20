"""
Smart Mask Utility
Difference-based selective masking to preserve unchanged areas

Uses difference detection to create masks that only apply AI changes
to intended areas while preserving original background, face, and objects.
"""

import numpy as np
from PIL import Image, ImageFilter, ImageChops, ImageOps
from typing import Tuple, Optional
from core.logger import get_logger

logger = get_logger()

# Optional: OpenCV for face detection (graceful fallback if not available)
try:
    import cv2
    OPENCV_AVAILABLE = True
    logger.info("OpenCV available - face detection enabled")
except ImportError:
    OPENCV_AVAILABLE = False
    logger.warning("OpenCV not available - face detection disabled")


class SmartMaskProcessor:
    """
    Creates intelligent masks based on image differences to selectively
    composite AI results with original images
    """
    
    def __init__(self):
        self.default_threshold = 8.0  # Percentage difference threshold (0.0-20.0, sweet spot 3-12)
        self.default_feather = 3      # Feather radius in pixels (0-50, low to avoid ghosting)
        self.default_focus_primary = True  # Focus on largest changed region
        self.default_min_region_size = 0.03  # Minimum region size (3% of image, more lenient)
        self.face_cascade = None  # Lazy-loaded OpenCV face detector
        self.face_cache = {}  # Cache face detection results by image hash
        self.face_cache_max_size = 50  # Maximum cache entries to prevent memory leaks

        # Preset profiles for quick settings switching
        # All presets now include use_poisson=True by default (v2.5 breakthrough feature)
        self.presets = {
            "portrait_upper": {
                "name": "Portrait - Upper Body",
                "threshold": 6.5,
                "feather": 3,
                "focus_primary": True,
                "use_poisson": True,
                "harmonize_colors": True,
                "description": "Best for upper body clothing changes (most common)"
            },
            "full_body": {
                "name": "Full Body",
                "threshold": 7.0,
                "feather": 5,
                "focus_primary": False,
                "use_poisson": True,
                "harmonize_colors": True,
                "description": "Handles multiple clothing items (top + bottom)"
            },
            "aggressive": {
                "name": "Aggressive",
                "threshold": 5.0,
                "feather": 1,
                "focus_primary": True,
                "use_poisson": True,
                "harmonize_colors": True,
                "description": "Catches subtle changes with Poisson anti-ghosting"
            },
            "conservative": {
                "name": "Conservative",
                "threshold": 9.0,
                "feather": 8,
                "focus_primary": True,
                "use_poisson": True,
                "harmonize_colors": True,
                "description": "Only major changes, smoother blending with Poisson"
            }
        }
    
    def create_difference_mask(
        self, 
        original_path: str, 
        result_path: str,
        threshold: int = None,
        feather: int = None,
        focus_primary: bool = None,
        min_region_size: float = None,
        method: str = 'rgb'
    ) -> Optional[Image.Image]:
        """
        Create a mask based on differences between original and result images
        
        Args:
            original_path: Path to original image
            result_path: Path to AI result image
            threshold: Difference threshold (0-100%), defaults to 15%
            feather: Edge feathering radius in pixels, defaults to 20
            focus_primary: If True, keep only largest changed region (clothing), defaults to True
            min_region_size: Minimum region size as fraction of image (0.0-1.0), defaults to 0.05
            
        Returns:
            PIL Image mask (grayscale) or None if error
        """
        try:
            if threshold is None:
                threshold = self.default_threshold
            if feather is None:
                feather = self.default_feather
            if focus_primary is None:
                focus_primary = self.default_focus_primary
            if min_region_size is None:
                min_region_size = self.default_min_region_size
            
            # Load images
            original = Image.open(original_path).convert('RGB')
            result = Image.open(result_path).convert('RGB')
            
            # Use the shared implementation
            return self._create_mask_from_images(original, result, threshold, feather, focus_primary, min_region_size, method)
            
        except Exception as e:
            logger.error(f"Error creating difference mask: {e}")
            return None
    
    def _calculate_lab_difference(
        self,
        original: Image.Image,
        result: Image.Image
    ) -> np.ndarray:
        """
        Calculate perceptual color difference using LAB color space (ΔE)
        
        LAB is perceptually uniform - equal distances in LAB space correspond
        to equal perceptual differences. This is better than RGB at ignoring
        subtle lighting/shadow changes while catching real color differences.
        
        Args:
            original: Original PIL Image
            result: Result PIL Image
            
        Returns:
            NumPy array of difference values (0-100 scale for consistency with RGB method)
        """
        try:
            from skimage import color
            
            # Convert to numpy arrays (0-1 range for skimage)
            orig_array = np.array(original, dtype=np.float32) / 255.0
            result_array = np.array(result, dtype=np.float32) / 255.0
            
            # Convert RGB to LAB color space
            lab_orig = color.rgb2lab(orig_array)
            lab_result = color.rgb2lab(result_array)
            
            # Calculate ΔE (Euclidean distance in LAB space)
            # ΔE = sqrt((L1-L2)² + (a1-a2)² + (b1-b2)²)
            delta_e = np.sqrt(np.sum((lab_orig - lab_result)**2, axis=2))
            
            # Normalize to 0-100 scale for consistency with RGB method
            # ΔE typically ranges 0-100, where:
            # - ΔE < 1: Imperceptible difference
            # - ΔE 1-2: Perceptible through close observation
            # - ΔE 2-10: Perceptible at a glance  
            # - ΔE 11-49: Colors are more similar than opposite
            # - ΔE > 50: Colors are opposite
            
            # Scale to 0-100 range (most values will be 0-50)
            # We're already in a good range, just ensure 0-100
            diff_normalized = np.clip(delta_e, 0, 100)
            
            logger.debug(f"LAB ΔE range: min={diff_normalized.min():.2f}, max={diff_normalized.max():.2f}, mean={diff_normalized.mean():.2f}")
            
            return diff_normalized
            
        except ImportError:
            logger.warning("scikit-image not available, falling back to RGB method")
            # Fallback to RGB method
            diff = ImageChops.difference(original, result)
            diff_gray = diff.convert('L')
            diff_array = np.array(diff_gray, dtype=np.float32)
            return (diff_array / 255.0) * 100.0
        except Exception as e:
            logger.error(f"Error calculating LAB difference: {e}, falling back to RGB")
            # Fallback to RGB method
            diff = ImageChops.difference(original, result)
            diff_gray = diff.convert('L')
            diff_array = np.array(diff_gray, dtype=np.float32)
            return (diff_array / 255.0) * 100.0
    
    def _create_mask_from_images(
        self,
        original: Image.Image,
        result: Image.Image,
        threshold: int = None,
        feather: int = None,
        focus_primary: bool = None,
        min_region_size: float = None,
        method: str = 'rgb',
        use_edge_aware_feather: bool = False
    ) -> Optional[Image.Image]:
        """
        Create mask from pre-loaded Image objects (used for optimization)

        IMPROVED: Now supports edge-aware feathering

        Args:
            original: Original PIL Image
            result: Result PIL Image
            threshold: Difference threshold
            feather: Feather radius
            focus_primary: Focus on primary region
            min_region_size: Minimum region size
            method: Difference calculation method ('rgb' or 'lab')
            use_edge_aware_feather: If True, use guided filter for edge-aware feathering

        Returns:
            PIL Image mask or None
        """
        try:
            if threshold is None:
                threshold = self.default_threshold
            if feather is None:
                feather = self.default_feather
            if focus_primary is None:
                focus_primary = self.default_focus_primary
            if min_region_size is None:
                min_region_size = self.default_min_region_size

            # Ensure same size
            if original.size != result.size:
                result = result.resize(original.size, Image.Resampling.LANCZOS)

            # Calculate difference based on selected method
            if method == 'lab':
                # LAB color space (perceptual difference - ΔE)
                diff_normalized = self._calculate_lab_difference(original, result)
                logger.info(f"Using LAB (ΔE) color difference method")
            else:
                # RGB method (current/default)
                diff = ImageChops.difference(original, result)
                diff_gray = diff.convert('L')
                diff_array = np.array(diff_gray, dtype=np.float32)
                diff_normalized = (diff_array / 255.0) * 100.0
                logger.info(f"Using RGB color difference method")

            # Apply threshold
            mask_array = np.where(diff_normalized >= threshold, 255, 0).astype(np.uint8)
            mask = Image.fromarray(mask_array, mode='L')

            # Focus on primary region if enabled
            if focus_primary:
                mask = self._isolate_primary_region(mask, min_region_size)

            # Clean up mask
            mask = self._clean_mask(mask)

            # Apply feathering (edge-aware or standard)
            if feather > 0:
                if use_edge_aware_feather:
                    mask = self._apply_edge_aware_feathering(mask, original, feather)
                else:
                    mask = self._feather_mask(mask, feather)

            return mask

        except Exception as e:
            logger.error(f"Error creating mask from images: {e}")
            return None
    
    def _isolate_primary_region(self, mask: Image.Image, min_region_size: float) -> Image.Image:
        """
        Isolate the primary (largest) changed region, filtering out artifacts
        
        This identifies the main transformation area (e.g., clothing) and removes
        small scattered changes (e.g., face/background artifacts)
        
        Args:
            mask: Input binary mask
            min_region_size: Minimum region size as fraction of total image area
            
        Returns:
            Mask with only primary region(s) retained
        """
        try:
            mask_array = np.array(mask)
            
            # Calculate minimum pixel count threshold
            total_pixels = mask_array.size
            min_pixels = int(total_pixels * min_region_size)
            
            try:
                # Use scipy for connected component analysis (more accurate)
                from scipy import ndimage
                
                # Label connected components
                labeled_array, num_features = ndimage.label(mask_array)
                
                if num_features == 0:
                    logger.debug("No regions found in mask")
                    return mask
                
                # OPTIMIZATION: If only 1 region, return immediately
                if num_features == 1:
                    logger.debug("Single region found, no filtering needed")
                    return mask
                
                # Find sizes of all regions (optimized with bincount)
                region_sizes = []
                unique_labels, counts = np.unique(labeled_array[labeled_array > 0], return_counts=True)
                for label, size in zip(unique_labels, counts):
                    region_sizes.append((label, size))
                
                # Sort by size (largest first)
                region_sizes.sort(key=lambda x: x[1], reverse=True)
                
                # Strategy: Keep largest region + any region that's at least 20% of largest
                # This handles cases where clothing change is split into multiple regions
                largest_size = region_sizes[0][1]
                size_threshold = max(min_pixels, largest_size * 0.2)
                
                # Create new mask with only significant regions
                new_mask_array = np.zeros_like(mask_array)
                regions_kept = 0
                
                for region_label, region_size in region_sizes:
                    if region_size >= size_threshold:
                        new_mask_array[labeled_array == region_label] = 255
                        regions_kept += 1
                        logger.debug(f"Keeping region {region_label} with {region_size} pixels")
                    else:
                        logger.debug(f"Filtering out small region {region_label} with {region_size} pixels")
                
                logger.info(f"Primary region isolation: kept {regions_kept}/{num_features} regions (filtered {num_features - regions_kept} artifacts)")
                return Image.fromarray(new_mask_array, mode='L')
                
            except ImportError:
                # Fallback: simpler method using PIL/numpy only
                logger.warning("scipy not available, using simplified region filtering")
                
                # Simple approach: use erosion to disconnect small artifacts, then dilation to restore
                from PIL import ImageFilter
                
                # Erode to separate artifacts
                eroded = mask.filter(ImageFilter.MinFilter(5))
                
                # Convert to binary
                eroded_array = np.array(eroded)
                binary = (eroded_array > 127).astype(np.uint8)
                
                # Find largest contiguous region using basic flood fill approach
                # This is simplified but works reasonably well
                
                # Find all white pixels
                white_pixels = np.argwhere(binary > 0)
                
                if len(white_pixels) == 0:
                    return mask
                
                # Simple approach: keep regions with enough pixels after erosion
                # This removes small scattered artifacts
                result_array = np.where(eroded_array >= min_pixels / 100, 255, 0).astype(np.uint8)
                
                # Dilate back to restore size
                result_mask = Image.fromarray(result_array, mode='L')
                result_mask = result_mask.filter(ImageFilter.MaxFilter(5))
                
                logger.info("Applied simplified primary region filtering")
                return result_mask
                
        except Exception as e:
            logger.error(f"Error isolating primary region: {e}")
            return mask
    
    def _clean_mask(self, mask: Image.Image) -> Image.Image:
        """
        Clean up mask using morphological operations and aggressive artifact filtering
        Removes small noise, fills small holes, and eliminates thin line artifacts
        
        Args:
            mask: Input mask image
            
        Returns:
            Cleaned mask image with artifacts removed
        """
        try:
            # Convert to numpy for morphological operations
            mask_array = np.array(mask)
            
            from scipy import ndimage
            binary_mask = mask_array > 127
            
            # More aggressive erosion to remove thin line artifacts (compression artifacts, edges)
            eroded = ndimage.binary_erosion(binary_mask, iterations=3)
            
            # Fill holes
            filled = ndimage.binary_fill_holes(eroded)
            
            # Dilate to restore size (but less than eroded to keep artifacts gone)
            dilated = ndimage.binary_dilation(filled, iterations=4)
            
            # Convert back
            mask_array = (dilated * 255).astype(np.uint8)
            
            # Additional: filter out elongated regions (thin lines around person)
            try:
                labeled_array, num_features = ndimage.label(mask_array > 127)
                
                if num_features > 1:
                    # Analyze each region
                    cleaned_mask = np.zeros_like(mask_array)
                    
                    for i in range(1, num_features + 1):
                        region = (labeled_array == i)
                        region_pixels = np.argwhere(region)
                        
                        if len(region_pixels) == 0:
                            continue
                        
                        # Get bounding box dimensions
                        y_coords = region_pixels[:, 0]
                        x_coords = region_pixels[:, 1]
                        height = y_coords.max() - y_coords.min() + 1
                        width = x_coords.max() - x_coords.min() + 1
                        
                        # Calculate aspect ratio
                        aspect_ratio = max(width, height) / max(min(width, height), 1)
                        
                        # Calculate fill ratio (actual pixels vs bounding box)
                        fill_ratio = len(region_pixels) / (width * height)
                        
                        # Filter out elongated/thin regions (likely artifacts)
                        # Keep regions that are:
                        # - Not super elongated (aspect ratio < 8)
                        # - Have decent fill ratio (> 0.3, not just thin lines)
                        # - Have enough pixels (> 200)
                        if aspect_ratio < 8 and fill_ratio > 0.3 and len(region_pixels) > 200:
                            cleaned_mask[region] = 255
                    
                    mask_array = cleaned_mask
                    logger.info(f"Filtered elongated artifacts: kept {np.sum(mask_array > 0)} pixels")
            
            except Exception as filter_error:
                logger.warning(f"Could not filter elongated regions: {filter_error}")
            
            logger.info("Applied aggressive artifact filtering and cleanup")
            return Image.fromarray(mask_array, mode='L')
            
        except ImportError:
            # If scipy not available, use simple PIL filters
            logger.warning("scipy not available, using basic mask cleanup")
            # Use minimum filter (erosion) then maximum filter (dilation)
            mask = mask.filter(ImageFilter.MinFilter(3))
            mask = mask.filter(ImageFilter.MaxFilter(5))
            return mask
        except Exception as e:
            logger.error(f"Error cleaning mask: {e}")
            return mask
    
    def _feather_mask(self, mask: Image.Image, radius: int) -> Image.Image:
        """
        Apply Gaussian blur to mask edges with anti-ghosting power curve
        
        The power curve (^2.5) reduces "ghost" artifacts by creating a steeper
        transition. This minimizes the blend zone where original clothing shows
        through semi-transparently.
        
        Args:
            mask: Input mask image
            radius: Blur radius in pixels
            
        Returns:
            Feathered mask image with steep transition curve
        """
        try:
            if radius == 0:
                return mask
            
            logger.info(f"Applying anti-ghost feathering with {radius}px blur + power curve")
            
            # Apply Gaussian blur
            blurred = mask.filter(ImageFilter.GaussianBlur(radius=radius))
            
            # Convert to numpy for power curve application
            mask_array = np.array(blurred).astype(float) / 255.0
            
            # Apply power curve to reduce ghosting (steeper transition)
            # Power of 2.5: smooth edges but minimal blend zone
            # This pushes values toward 0 or 1, avoiding 0.5 ghosting zone
            mask_array = np.power(mask_array, 2.5)
            
            # Convert back to PIL Image
            result_array = (mask_array * 255).astype(np.uint8)
            return Image.fromarray(result_array, mode='L')
            
        except Exception as e:
            logger.error(f"Error feathering mask: {e}")
            return mask
    
    def _harmonize_masked_regions(
        self,
        original: Image.Image,
        result: Image.Image,
        mask: Image.Image,
        strength: float = 0.3
    ) -> Image.Image:
        """
        Harmonize colors in masked regions (preserved areas) to match result's tone
        
        This prevents visible color/tint mismatches when the original's face/background
        is composited back onto the AI result.
        
        Args:
            original: Original input image
            result: AI-generated result image
            mask: Mask image (white=result, black=original)
            strength: How much to apply correction (0.0-1.0, default 0.3 for subtlety)
            
        Returns:
            Original image with harmonized colors in masked regions
        """
        try:
            # Convert to numpy arrays
            orig_array = np.array(original, dtype=np.float32)
            result_array = np.array(result, dtype=np.float32)
            mask_array = np.array(mask, dtype=np.float32) / 255.0
            
            # Invert mask: we want to harmonize the BLACK areas (preserved regions)
            preserved_mask = 1.0 - mask_array
            
            # Calculate mean color of each image in preserved regions
            # Only sample areas that will be preserved (threshold: >50% preserved)
            preserve_threshold = preserved_mask > 0.5
            
            if not np.any(preserve_threshold):
                # No preserved regions, return original as-is
                return original
            
            # Get mean RGB values for preserved regions
            orig_mean_r = np.mean(orig_array[:,:,0][preserve_threshold])
            orig_mean_g = np.mean(orig_array[:,:,1][preserve_threshold])
            orig_mean_b = np.mean(orig_array[:,:,2][preserve_threshold])
            
            # Get mean RGB values for entire result (the target tone)
            result_mean_r = np.mean(result_array[:,:,0])
            result_mean_g = np.mean(result_array[:,:,1])
            result_mean_b = np.mean(result_array[:,:,2])
            
            # Calculate color shift needed
            shift_r = result_mean_r - orig_mean_r
            shift_g = result_mean_g - orig_mean_g
            shift_b = result_mean_b - orig_mean_b
            
            # Apply subtle shift only to preserved regions
            # Use mask to blend: full strength in fully preserved areas, 0 in result areas
            harmonized = orig_array.copy()
            
            # Expand mask to 3 channels
            preserved_mask_3ch = np.stack([preserved_mask, preserved_mask, preserved_mask], axis=2)
            
            # Apply shift with strength multiplier
            harmonized[:,:,0] += shift_r * preserved_mask_3ch[:,:,0] * strength
            harmonized[:,:,1] += shift_g * preserved_mask_3ch[:,:,1] * strength
            harmonized[:,:,2] += shift_b * preserved_mask_3ch[:,:,2] * strength
            
            # Clip to valid range
            harmonized = np.clip(harmonized, 0, 255).astype(np.uint8)
            
            harmonized_img = Image.fromarray(harmonized)
            logger.info(f"Applied color harmonization: RGB shifts ({shift_r:.1f}, {shift_g:.1f}, {shift_b:.1f}) at {strength*100:.0f}% strength")
            
            return harmonized_img
            
        except Exception as e:
            logger.warning(f"Error harmonizing colors, using original: {e}")
            return original
    
    def _apply_poisson_blend(
        self,
        original: Image.Image,
        result: Image.Image,
        mask: Image.Image
    ) -> Optional[Image.Image]:
        """
        Apply gradient-domain (Poisson) blending to eliminate ghosting artifacts

        This solves the neck ghosting problem by blending gradients instead of pixels.
        Much more effective than alpha compositing for preventing ghost artifacts.

        Args:
            original: Original image
            result: AI result image
            mask: Binary mask (white=result region, black=original region)

        Returns:
            Seamlessly blended image or None if error
        """
        if not OPENCV_AVAILABLE:
            logger.warning("Poisson blending unavailable - OpenCV not installed, using standard blend")
            return None

        try:
            # Ensure all images are same size
            if original.size != result.size:
                result = result.resize(original.size, Image.Resampling.LANCZOS)
            if mask.size != original.size:
                mask = mask.resize(original.size, Image.Resampling.LANCZOS)

            # Convert PIL to OpenCV format
            orig_cv = cv2.cvtColor(np.array(original), cv2.COLOR_RGB2BGR)
            result_cv = cv2.cvtColor(np.array(result), cv2.COLOR_RGB2BGR)
            mask_array = np.array(mask)

            # Binarize mask for Poisson blending (needs pure 0 or 255)
            # seamlessClone doesn't work well with grayscale/feathered masks
            binary_mask = np.where(mask_array > 127, 255, 0).astype(np.uint8)

            # Find bounding box of mask region
            coords = np.column_stack(np.where(binary_mask > 127))
            if len(coords) == 0:
                logger.warning("Empty mask for Poisson blending, using original")
                return original

            # Get bounding box
            min_y, min_x = coords.min(axis=0)
            max_y, max_x = coords.max(axis=0)
            h, w = orig_cv.shape[:2]

            # Check if mask is too close to edges (seamlessClone needs padding)
            # If mask touches edges, it will cause ROI out of bounds error
            edge_margin = 5  # pixels
            if min_x < edge_margin or min_y < edge_margin or max_x >= (w - edge_margin) or max_y >= (h - edge_margin):
                logger.warning(f"Mask too close to edges (bbox: {min_x},{min_y} to {max_x},{max_y}), shrinking mask for Poisson blend")

                # Erode mask slightly to pull it away from edges
                kernel = np.ones((5, 5), np.uint8)
                binary_mask = cv2.erode(binary_mask, kernel, iterations=2)

                # Recalculate bounding box after erosion
                coords = np.column_stack(np.where(binary_mask > 127))
                if len(coords) == 0:
                    logger.warning("Mask became empty after erosion, falling back to alpha blend")
                    return None

                min_y, min_x = coords.min(axis=0)
                max_y, max_x = coords.max(axis=0)

            # Calculate center point (centroid of mask region)
            center_y = int(np.mean(coords[:, 0]))
            center_x = int(np.mean(coords[:, 1]))

            # Final validation - ensure center is within image bounds
            center_x = max(0, min(center_x, w - 1))
            center_y = max(0, min(center_y, h - 1))
            center = (center_x, center_y)

            logger.debug(f"Poisson blend: image={w}x{h}, bbox=({min_x},{min_y})-({max_x},{max_y}), center={center}")

            # Apply seamless cloning (Poisson blending)
            # NORMAL_CLONE: Standard Poisson blending
            blended_cv = cv2.seamlessClone(
                result_cv,     # Source (AI result)
                orig_cv,       # Destination (original)
                binary_mask,   # Binary mask (0 or 255)
                center,        # Center point
                cv2.NORMAL_CLONE
            )

            # Convert back to PIL
            blended_rgb = cv2.cvtColor(blended_cv, cv2.COLOR_BGR2RGB)
            blended = Image.fromarray(blended_rgb)

            logger.info(f"✅ Poisson blending successful - ghosting eliminated")
            return blended

        except Exception as e:
            logger.warning(f"Poisson blending failed: {e}, falling back to standard blend")
            return None

    def _apply_edge_aware_feathering(
        self,
        mask: Image.Image,
        guide_image: Image.Image,
        radius: int
    ) -> Image.Image:
        """
        Apply edge-aware feathering using guided filter

        Feathers along edges (perpendicular) instead of across them.
        Fills gaps between clothing regions without bleeding into face/background.

        Args:
            mask: Binary mask to feather
            guide_image: Guide image (original) for edge detection
            radius: Feather radius

        Returns:
            Edge-aware feathered mask
        """
        if not OPENCV_AVAILABLE:
            logger.warning("Edge-aware feathering unavailable - using standard Gaussian")
            return self._feather_mask(mask, radius)

        try:
            # Try to import guidedFilter - it's in cv2.ximgproc in opencv-contrib
            try:
                from cv2.ximgproc import guidedFilter
            except (ImportError, AttributeError):
                logger.debug("opencv-contrib ximgproc.guidedFilter not available, using standard feathering")
                return self._feather_mask(mask, radius)

            # Convert to OpenCV format
            mask_cv = np.array(mask).astype(np.float32) / 255.0
            guide_cv = cv2.cvtColor(np.array(guide_image), cv2.COLOR_RGB2GRAY).astype(np.float32) / 255.0

            # Apply guided filter
            # radius: size of filter kernel
            # eps: regularization (higher = smoother, lower = more edge-preserving)
            eps = 0.01  # Low epsilon preserves edges well
            filtered = guidedFilter(guide_cv, mask_cv, radius, eps)

            # Convert back to PIL
            filtered_uint8 = (filtered * 255).astype(np.uint8)
            result = Image.fromarray(filtered_uint8, mode='L')

            logger.info(f"✅ Applied edge-aware feathering (guided filter) with radius={radius}, eps={eps}")
            return result

        except Exception as e:
            logger.warning(f"Edge-aware feathering failed: {e}, using standard Gaussian")
            return self._feather_mask(mask, radius)

    def apply_smart_composite(
        self,
        original_path: str,
        result_path: str,
        mask: Optional[Image.Image] = None,
        threshold: int = None,
        feather: int = None,
        focus_primary: bool = None,
        min_region_size: float = None,
        invert_blend: bool = False,
        harmonize_colors: bool = True,
        use_poisson: bool = False,
        use_edge_aware_feather: bool = False
    ) -> Optional[Image.Image]:
        """
        Apply smart masking to composite result with original

        IMPROVED: Now supports Poisson blending and edge-aware feathering

        Args:
            original_path: Path to original image
            result_path: Path to AI result image
            mask: Pre-computed mask (optional, will create if None)
            threshold: Difference threshold if creating mask
            feather: Feather radius if creating mask
            focus_primary: Focus on largest changed region if creating mask
            min_region_size: Minimum region size if creating mask
            invert_blend: If True, use inverted blend direction (result bleeds INTO original)
                         If False (default), use standard blend (original bleeds INTO result)
            harmonize_colors: If True, apply subtle color correction to masked regions
                             to match the result's color tone (reduces visible tint mismatch)
            use_poisson: If True, use Poisson (gradient-domain) blending to eliminate ghosting
                        (HIGHLY RECOMMENDED - solves neck ghosting issue)
            use_edge_aware_feather: If True, use guided filter for edge-aware feathering
                                   (requires opencv-contrib, fills gaps without face bleeding)

        Returns:
            Composited image or None if error
        """
        try:
            # Load images
            original = Image.open(original_path).convert('RGB')
            result = Image.open(result_path).convert('RGB')
            
            # Ensure same size
            if original.size != result.size:
                result = result.resize(original.size, Image.Resampling.LANCZOS)
            
            # Create mask if not provided
            if mask is None:
                mask = self.create_difference_mask(
                    original_path, 
                    result_path, 
                    threshold, 
                    feather,
                    focus_primary,
                    min_region_size
                )
                if mask is None:
                    return None
            
            # Ensure mask is same size
            if mask.size != original.size:
                mask = mask.resize(original.size, Image.Resampling.LANCZOS)
            
            # Color harmonization: Adjust original's colors in masked regions to match result
            # This prevents visible tint/color mismatches when compositing
            if harmonize_colors:
                original = self._harmonize_masked_regions(original, result, mask)

            # IMPROVED: Use Poisson blending if requested (eliminates ghosting)
            if use_poisson:
                logger.info("Attempting Poisson (gradient-domain) blending...")
                composited = self._apply_poisson_blend(original, result, mask)
                if composited is not None:
                    logger.info("✅ Poisson blending successful - ghosting eliminated")
                    return composited
                else:
                    logger.info("⚠️ Poisson blending unavailable, falling back to alpha compositing")

            # Composite using mask
            # PIL's composite: composite(image1, image2, mask)
            # Where mask is white, use image1; where black, use image2
            #
            # Standard approach: composite(result, original, mask)
            # - White mask areas = result (new clothes)
            # - Black mask areas = original (face/background)
            # - Feathered edges: 50% gray = 50% result + 50% original
            #
            # Inverted approach: Adjust mask opacity to favor original more
            # - Instead of 50/50 blend, use weighted blend that favors original
            # - This makes result "sit on top" with less bleed-through

            if invert_blend:
                # Adjust mask to favor original in feathered regions
                # Convert mask to array for manipulation
                mask_array = np.array(mask, dtype=np.float32)

                # Apply inverse power curve to feathered regions (gray values)
                # This makes mid-tones darker, favoring the original more
                mask_array = mask_array / 255.0  # Normalize to 0-1
                mask_array = mask_array ** 0.5   # Square root (opposite of power curve)
                mask_array = (mask_array * 255).astype(np.uint8)

                adjusted_mask = Image.fromarray(mask_array, mode='L')
                composited = Image.composite(result, original, adjusted_mask)
                logger.info("Applied smart composite with INVERTED blend (favors original, reduces ghosting)")
            else:
                # Standard blend direction
                composited = Image.composite(result, original, mask)
                logger.info("Applied smart composite with STANDARD blend (50/50 feather blend)")

            return composited
            
        except Exception as e:
            logger.error(f"Error applying smart composite: {e}")
            return None
    
    def preview_mask(
        self,
        original_path: str,
        result_path: str,
        threshold: int = None,
        feather: int = None,
        focus_primary: bool = None,
        min_region_size: float = None,
        max_preview_size: int = 800
    ) -> Optional[Image.Image]:
        """
        Create a visual preview of the mask overlay
        
        OPTIMIZED: Downsamples images for faster preview generation
        
        Args:
            original_path: Path to original image
            result_path: Path to AI result image
            threshold: Difference threshold
            feather: Feather radius
            focus_primary: Focus on largest changed region
            min_region_size: Minimum region size
            max_preview_size: Maximum dimension for preview (default 800px for speed)
            
        Returns:
            Preview image with mask overlay or None if error
        """
        try:
            # OPTIMIZATION: Load and downsample images first for much faster processing
            original_full = Image.open(original_path).convert('RGB')
            result_full = Image.open(result_path).convert('RGB')
            
            # Calculate downsample factor
            max_dim = max(original_full.width, original_full.height)
            if max_dim > max_preview_size:
                scale_factor = max_preview_size / max_dim
                preview_size = (
                    int(original_full.width * scale_factor),
                    int(original_full.height * scale_factor)
                )
                original = original_full.resize(preview_size, Image.Resampling.LANCZOS)
                result = result_full.resize(preview_size, Image.Resampling.LANCZOS)
                
                # Adjust feather for scaled image
                scaled_feather = int(feather * scale_factor) if feather else None
                
                logger.debug(f"Preview optimization: scaled from {original_full.size} to {preview_size} ({scale_factor:.2f}x)")
            else:
                original = original_full
                result = result_full
                scaled_feather = feather
            
            # Create mask on downsampled images (much faster)
            mask = self._create_mask_from_images(
                original,
                result,
                threshold,
                scaled_feather,
                focus_primary,
                min_region_size
            )
            if mask is None:
                return None
            
            # Ensure same size
            if mask.size != original.size:
                mask = mask.resize(original.size, Image.Resampling.LANCZOS)
            
            # Create red overlay where mask is active (using downsampled original for speed)
            mask_array = np.array(mask)
            original_array = np.array(original)
            
            # Create red tint in masked areas
            red_overlay = original_array.copy()
            mask_normalized = mask_array / 255.0
            red_overlay[:, :, 0] = np.clip(
                original_array[:, :, 0] + (255 - original_array[:, :, 0]) * mask_normalized * 0.5,
                0, 255
            )
            
            preview = Image.fromarray(red_overlay.astype(np.uint8))
            
            logger.info(f"Created optimized mask preview ({preview.size})")
            return preview
            
        except Exception as e:
            logger.error(f"Error creating mask preview: {e}")
            return None
    
    def get_preset(self, preset_name: str) -> dict:
        """
        Get settings for a preset profile

        Args:
            preset_name: Name of preset (portrait_upper, full_body, aggressive, conservative)

        Returns:
            Dictionary with threshold, feather, focus_primary settings
        """
        if preset_name in self.presets:
            return self.presets[preset_name].copy()
        else:
            logger.warning(f"Unknown preset '{preset_name}', using defaults")
            return {
                "threshold": self.default_threshold,
                "feather": self.default_feather,
                "focus_primary": self.default_focus_primary
            }

    def list_presets(self) -> list:
        """
        Get list of available presets with descriptions

        Returns:
            List of (key, name, description) tuples
        """
        return [
            (key, preset["name"], preset["description"])
            for key, preset in self.presets.items()
        ]

    def calculate_adaptive_threshold(self, difference_image: np.ndarray, downsample_for_speed: bool = True) -> float:
        """
        Automatically calculate optimal threshold from difference histogram

        OPTIMIZED: Downsamples large images for 50% faster calculation without accuracy loss

        Uses valley detection to find the separation between noise/artifacts
        and legitimate transformations.

        Args:
            difference_image: Normalized difference array (0-100%)
            downsample_for_speed: If True, downsample to 800px max for faster calculation

        Returns:
            Recommended threshold value (0-20%)
        """
        try:
            from scipy.ndimage import gaussian_filter1d
            from scipy.signal import find_peaks

            logger.info("Calculating adaptive threshold from difference histogram")

            # OPTIMIZATION: Downsample for histogram calculation (50% speed boost)
            # Histogram statistics don't need full resolution
            if downsample_for_speed and difference_image.shape[0] > 800:
                scale = 800 / max(difference_image.shape[:2])
                new_shape = (int(difference_image.shape[0] * scale), int(difference_image.shape[1] * scale))

                # Downsample using block averaging for speed
                from scipy.ndimage import zoom
                downsampled = zoom(difference_image, (scale, scale), order=1)
                logger.debug(f"Threshold calc optimization: downsampled from {difference_image.shape} to {downsampled.shape}")
                diff_flat = downsampled.flatten()
            else:
                # Use full resolution
                diff_flat = difference_image.flatten()

            # Get histogram
            hist, bins = np.histogram(diff_flat, bins=100, range=(0, 20))  # Focus on 0-20% range
            
            # Smooth histogram to find valleys
            smoothed_hist = gaussian_filter1d(hist.astype(float), sigma=2)
            
            # Invert to find valleys as peaks
            inverted = np.max(smoothed_hist) - smoothed_hist
            
            # Find valleys (peaks in inverted)
            valleys, _ = find_peaks(inverted, prominence=np.max(inverted) * 0.1)
            
            if len(valleys) > 0:
                # First significant valley is the separation point
                threshold = bins[valleys[0]]
                # Reduce by 15% to be less aggressive (user feedback: auto is too high)
                threshold = threshold * 0.85
                threshold = np.clip(threshold, 3.0, 12.0)  # Constrain to reasonable range (lower max)
                logger.info(f"Adaptive threshold calculated: {threshold:.1f}%")
                return float(threshold)
            else:
                # Fallback: use percentile-based approach
                p75 = np.percentile(diff_flat[diff_flat > 0], 75)
                threshold = np.clip(p75 * 0.5, 3.0, 10.0)  # Lower multiplier and max
                logger.info(f"Adaptive threshold (fallback): {threshold:.1f}%")
                return float(threshold)
                
        except Exception as e:
            logger.warning(f"Error calculating adaptive threshold: {e}, using default")
            return self.default_threshold
    
    def detect_and_exclude_skin(
        self,
        mask: Image.Image,
        original_image: Image.Image,
        aggressiveness: float = 0.8
    ) -> Image.Image:
        """
        Detect skin tones in image and exclude from mask for boundary refinement

        Uses HSV color space for skin detection. Works across most skin tones.
        Solves neck ghosting by definitively excluding all skin pixels.

        Args:
            mask: Input mask to modify
            original_image: Original image for skin detection
            aggressiveness: How aggressively to exclude skin (0.0-1.0, default 0.8)
                           Higher = more skin excluded, safer but may miss clothing near skin

        Returns:
            Modified mask with skin regions excluded
        """
        try:
            if not OPENCV_AVAILABLE:
                logger.debug("Skin detection skipped - OpenCV not available")
                return mask

            # Convert to OpenCV format
            img_array = np.array(original_image.convert('RGB'))
            img_hsv = cv2.cvtColor(img_array, cv2.COLOR_RGB2HSV)

            # HSV ranges for skin tones (works for most skin colors)
            # Hue: 0-25 (red-orange range)
            # Saturation: 30-170 (excludes very pale and very dark)
            # Value: 80-255 (brightness)
            #
            # Adjusted for aggressiveness:
            lower_bound = np.array([0, int(30 * aggressiveness), int(80 * aggressiveness)])
            upper_bound = np.array([25, 170, 255])

            # Create skin mask
            skin_mask = cv2.inRange(img_hsv, lower_bound, upper_bound)

            # Apply morphological operations to clean up
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
            skin_mask = cv2.morphologyEx(skin_mask, cv2.MORPH_CLOSE, kernel)
            skin_mask = cv2.morphologyEx(skin_mask, cv2.MORPH_OPEN, kernel)

            # Exclude skin from mask (set to 0 where skin detected)
            mask_array = np.array(mask)
            mask_array = np.where(skin_mask > 0, 0, mask_array)

            result_mask = Image.fromarray(mask_array, mode='L')

            # Calculate how much was excluded
            skin_pixels = np.sum(skin_mask > 0)
            total_pixels = skin_mask.size
            skin_percent = (skin_pixels / total_pixels) * 100

            logger.info(f"Skin detection: excluded {skin_percent:.1f}% of image as skin (aggressiveness={aggressiveness})")
            return result_mask

        except Exception as e:
            logger.error(f"Error in skin detection: {e}")
            return mask

    def detect_and_exclude_faces(self, mask: Image.Image, original_image: Image.Image, use_cache: bool = True) -> Image.Image:
        """
        Detect faces in original image and exclude them from mask using elliptical region

        OPTIMIZED: Caches face detection results per image for faster adjustments

        Uses OpenCV Haar Cascade for fast face detection, then creates an
        elliptical exclusion zone for face + hair instead of rectangular box.

        Args:
            mask: Input mask to modify
            original_image: Original image for face detection
            use_cache: If True, cache face detection results by image hash

        Returns:
            Modified mask with faces excluded
        """
        if not OPENCV_AVAILABLE:
            logger.debug("Face detection skipped - OpenCV not available")
            return mask

        try:
            # Lazy-load face detector
            if self.face_cascade is None:
                self.face_cascade = cv2.CascadeClassifier(
                    cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
                )
                if self.face_cascade.empty():
                    logger.warning("Failed to load face cascade, disabling face detection")
                    return mask

            # OPTIMIZATION: Check cache first to avoid redundant face detection
            import hashlib
            img_bytes = original_image.tobytes()
            img_hash = hashlib.md5(img_bytes).hexdigest()

            # Get image dimensions (needed for filtering)
            img_height, img_width = original_image.size[1], original_image.size[0]

            if use_cache and img_hash in self.face_cache:
                faces = self.face_cache[img_hash]
                logger.debug(f"Face detection: using cached result ({len(faces)} faces)")
            else:
                # Convert to OpenCV format
                img_array = np.array(original_image.convert('RGB'))
                gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)

                # Detect faces with balanced parameters
                faces = self.face_cascade.detectMultiScale(
                    gray,
                    scaleFactor=1.1,   # Less sensitive (was 1.05)
                    minNeighbors=5,    # Higher threshold (was 4)
                    minSize=(80, 80),  # Larger minimum (was 30x30) to filter tiny false positives
                    flags=cv2.CASCADE_SCALE_IMAGE
                )

                # Cache the result with LRU eviction
                if use_cache:
                    # Evict oldest entry if cache is full (simple FIFO)
                    if len(self.face_cache) >= self.face_cache_max_size:
                        # Remove the first (oldest) entry
                        oldest_key = next(iter(self.face_cache))
                        del self.face_cache[oldest_key]
                        logger.debug(f"Face cache full, evicted oldest entry (cache size: {len(self.face_cache)})")

                    self.face_cache[img_hash] = faces
                    logger.debug(f"Face detection: cached result ({len(faces)} faces, cache size: {len(self.face_cache)}/{self.face_cache_max_size})")

            if len(faces) == 0:
                logger.info("No faces detected")
                return mask

            # Filter out small false positives based on image size
            # Real faces should be at least 3% of the smaller image dimension
            min_face_size = int(min(img_width, img_height) * 0.03)
            
            filtered_faces = []
            for (x, y, w, h) in faces:
                if w >= min_face_size and h >= min_face_size:
                    filtered_faces.append((x, y, w, h))
                else:
                    logger.debug(f"Filtered out small face detection at ({x},{y}) size {w}x{h} (below {min_face_size}px threshold)")
            
            faces = filtered_faces
            
            if len(faces) == 0:
                logger.info("No valid faces after filtering small detections")
                return mask
            
            # If multiple faces detected, prioritize the largest (likely the main subject)
            # Keep all that are at least 30% the size of the largest (for group photos)
            if len(faces) > 1:
                # Sort by area (largest first)
                faces_with_area = [(x, y, w, h, w*h) for (x, y, w, h) in faces]
                faces_with_area.sort(key=lambda f: f[4], reverse=True)
                
                largest_area = faces_with_area[0][4]
                threshold_area = largest_area * 0.3  # 30% of largest
                
                # Keep faces that are significant size
                faces = [(x, y, w, h) for (x, y, w, h, area) in faces_with_area if area >= threshold_area]
                
                logger.info(f"Filtered to {len(faces)} significant face(s) out of {len(filtered_faces)} detected")
            
            logger.info(f"Processing {len(faces)} face(s) for exclusion")
            
            # Create mask for exclusion
            mask_array = np.array(mask)
            height, width = mask_array.shape
            
            for (x, y, w, h) in faces:
                # Create elliptical exclusion zone for INNER FACE ONLY
                # User feedback: Only protect core face, allow clothes to overlap hair/neck
                center_x = x + w // 2
                center_y = y + h // 2
                
                # Ellipse radii: MINIMAL - just the core face area
                radius_x = int(w * 0.40)           # 40% wider - just face width
                radius_y = int(h * 0.50)           # 50% taller - just face height, no hair
                
                # NO upward shift - keep centered on detected face
                # This allows clothing to overlap hair and neck areas
                
                # Create elliptical mask using cv2
                ellipse_mask = np.ones((height, width), dtype=np.uint8) * 255
                cv2.ellipse(
                    ellipse_mask,
                    (center_x, center_y),
                    (radius_x, radius_y),
                    0,  # angle
                    0,  # start angle
                    360,  # end angle
                    0,  # color (black to exclude)
                    -1  # filled
                )
                
                # Apply elliptical exclusion to mask
                mask_array = np.where(ellipse_mask == 0, 0, mask_array)
                
                logger.info(f"Excluded inner face region: center ({center_x},{center_y}), detected ({w}x{h}), exclusion radii ({radius_x}x{radius_y})")
            
            result_mask = Image.fromarray(mask_array, mode='L')
            logger.info(f"✅ Face exclusion complete: {len(faces)} inner face(s) protected (hair/neck allowed)")
            return result_mask
            
        except Exception as e:
            logger.error(f"Error in face detection: {e}")
            return mask
    
    def calculate_smart_feather(self, mask: Image.Image) -> int:
        """
        Analyze mask structure and recommend optimal feather amount
        
        Detects gaps between disconnected regions and suggests feather
        radius to bridge them without excessive ghosting.
        
        Args:
            mask: Binary mask to analyze
            
        Returns:
            Recommended feather radius (0-50 pixels)
        """
        try:
            from scipy.ndimage import label
            
            logger.info("Calculating smart feather based on mask structure")
            
            mask_array = np.array(mask)
            binary_mask = (mask_array > 127).astype(np.uint8)
            
            # Find connected components
            labeled_array, num_features = label(binary_mask)
            
            if num_features <= 1:
                # No gaps - minimal feather needed
                logger.info("Single connected region detected - minimal feather recommended")
                return 3
            
            # Calculate region centroids
            centroids = []
            for i in range(1, num_features + 1):
                region_pixels = np.argwhere(labeled_array == i)
                if len(region_pixels) > 0:
                    centroid = np.mean(region_pixels, axis=0)
                    centroids.append(centroid)
            
            if len(centroids) < 2:
                return 3
            
            # Calculate distances between all pairs of centroids
            min_gap = float('inf')
            for i in range(len(centroids)):
                for j in range(i + 1, len(centroids)):
                    distance = np.linalg.norm(centroids[i] - centroids[j])
                    min_gap = min(min_gap, distance)
            
            # Recommend feather of half the minimum gap (to bridge it)
            # But cap at reasonable values to avoid excessive ghosting
            recommended_feather = int(min_gap / 2)
            recommended_feather = np.clip(recommended_feather, 3, 20)  # Conservative max
            
            logger.info(f"Smart feather calculated: {recommended_feather}px (detected {num_features} regions, min gap {min_gap:.1f}px)")
            return recommended_feather
            
        except Exception as e:
            logger.warning(f"Error calculating smart feather: {e}, using default")
            return self.default_feather


# Convenience functions
_processor = SmartMaskProcessor()


def create_smart_mask(original_path: str, result_path: str, 
                      threshold: int = 15, feather: int = 20,
                      focus_primary: bool = True, min_region_size: float = 0.05) -> Optional[Image.Image]:
    """Create a difference-based mask"""
    return _processor.create_difference_mask(original_path, result_path, threshold, feather, focus_primary, min_region_size)


def apply_smart_masking(original_path: str, result_path: str,
                       threshold: int = 15, feather: int = 20,
                       focus_primary: bool = True, min_region_size: float = 0.05,
                       invert_blend: bool = False, harmonize_colors: bool = True,
                       use_poisson: bool = False, use_edge_aware_feather: bool = False) -> Optional[Image.Image]:
    """
    Apply smart masking and return composited result

    IMPROVED: Now supports Poisson blending and edge-aware feathering

    Args:
        use_poisson: Use gradient-domain blending to eliminate ghosting (RECOMMENDED)
        use_edge_aware_feather: Use guided filter for edge-aware feathering
    """
    return _processor.apply_smart_composite(
        original_path, result_path, None, threshold, feather, focus_primary,
        min_region_size, invert_blend, harmonize_colors, use_poisson, use_edge_aware_feather
    )


def get_presets() -> list:
    """Get list of available preset profiles"""
    return _processor.list_presets()


def apply_preset(preset_name: str, original_path: str, result_path: str, **kwargs) -> Optional[Image.Image]:
    """Apply smart masking using a preset profile"""
    preset = _processor.get_preset(preset_name)
    # Merge preset with any kwargs overrides
    settings = {**preset, **kwargs}
    return apply_smart_masking(original_path, result_path, **settings)


def preview_smart_mask(original_path: str, result_path: str,
                      threshold: int = 15, feather: int = 20,
                      focus_primary: bool = True, min_region_size: float = 0.05) -> Optional[Image.Image]:
    """Preview the mask as a red overlay"""
    return _processor.preview_mask(original_path, result_path, threshold, feather, focus_primary, min_region_size)

