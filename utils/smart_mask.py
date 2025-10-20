"""
Smart Mask Utility
Difference-based selective masking to preserve unchanged areas

Uses difference detection to create masks that only apply AI changes
to intended areas while preserving original background, face, and objects.
"""

import numpy as np
from PIL import Image, ImageFilter, ImageChops
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
    
    def create_difference_mask(
        self, 
        original_path: str, 
        result_path: str,
        threshold: int = None,
        feather: int = None,
        focus_primary: bool = None,
        min_region_size: float = None
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
            
            # Ensure same size
            if original.size != result.size:
                result = result.resize(original.size, Image.Resampling.LANCZOS)
            
            # Calculate pixel-wise difference
            diff = ImageChops.difference(original, result)
            
            # Convert to grayscale and normalize
            diff_gray = diff.convert('L')
            diff_array = np.array(diff_gray, dtype=np.float32)
            
            # Normalize to 0-100 range
            diff_normalized = (diff_array / 255.0) * 100.0
            
            # Apply threshold
            mask_array = np.where(diff_normalized >= threshold, 255, 0).astype(np.uint8)
            mask = Image.fromarray(mask_array, mode='L')
            
            # Focus on primary region if enabled (isolate main clothing change)
            if focus_primary:
                mask = self._isolate_primary_region(mask, min_region_size)
            
            # Clean up mask with morphological operations
            mask = self._clean_mask(mask)
            
            # Apply feathering to edges
            if feather > 0:
                mask = self._feather_mask(mask, feather)
            
            logger.info(f"Created smart mask with threshold={threshold}%, feather={feather}px, focus_primary={focus_primary}")
            return mask
            
        except Exception as e:
            logger.error(f"Error creating difference mask: {e}")
            return None
    
    def _create_mask_from_images(
        self,
        original: Image.Image,
        result: Image.Image,
        threshold: int = None,
        feather: int = None,
        focus_primary: bool = None,
        min_region_size: float = None
    ) -> Optional[Image.Image]:
        """
        Create mask from pre-loaded Image objects (used for optimization)
        
        Args:
            original: Original PIL Image
            result: Result PIL Image
            threshold: Difference threshold
            feather: Feather radius
            focus_primary: Focus on primary region
            min_region_size: Minimum region size
            
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
            
            # Calculate pixel-wise difference
            diff = ImageChops.difference(original, result)
            
            # Convert to grayscale and normalize
            diff_gray = diff.convert('L')
            diff_array = np.array(diff_gray, dtype=np.float32)
            
            # Normalize to 0-100 range
            diff_normalized = (diff_array / 255.0) * 100.0
            
            # Apply threshold
            mask_array = np.where(diff_normalized >= threshold, 255, 0).astype(np.uint8)
            mask = Image.fromarray(mask_array, mode='L')
            
            # Focus on primary region if enabled
            if focus_primary:
                mask = self._isolate_primary_region(mask, min_region_size)
            
            # Clean up mask
            mask = self._clean_mask(mask)
            
            # Apply feathering
            if feather > 0:
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
    
    def apply_smart_composite(
        self,
        original_path: str,
        result_path: str,
        mask: Optional[Image.Image] = None,
        threshold: int = None,
        feather: int = None,
        focus_primary: bool = None,
        min_region_size: float = None
    ) -> Optional[Image.Image]:
        """
        Apply smart masking to composite result with original
        
        Args:
            original_path: Path to original image
            result_path: Path to AI result image
            mask: Pre-computed mask (optional, will create if None)
            threshold: Difference threshold if creating mask
            feather: Feather radius if creating mask
            focus_primary: Focus on largest changed region if creating mask
            min_region_size: Minimum region size if creating mask
            
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
            
            # Composite using mask
            # PIL's composite: composite(image1, image2, mask)
            # Where mask is white, use image1; where black, use image2
            composited = Image.composite(result, original, mask)
            
            logger.info("Applied smart composite successfully")
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
    
    def calculate_adaptive_threshold(self, difference_image: np.ndarray) -> float:
        """
        Automatically calculate optimal threshold from difference histogram
        
        Uses valley detection to find the separation between noise/artifacts
        and legitimate transformations.
        
        Args:
            difference_image: Normalized difference array (0-100%)
            
        Returns:
            Recommended threshold value (0-20%)
        """
        try:
            from scipy.ndimage import gaussian_filter1d
            from scipy.signal import find_peaks
            
            logger.info("Calculating adaptive threshold from difference histogram")
            
            # Flatten to 1D and get histogram
            diff_flat = difference_image.flatten()
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
    
    def detect_and_exclude_faces(self, mask: Image.Image, original_image: Image.Image) -> Image.Image:
        """
        Detect faces in original image and exclude them from mask using elliptical region
        
        Uses OpenCV Haar Cascade for fast face detection, then creates an
        elliptical exclusion zone for face + hair instead of rectangular box.
        
        Args:
            mask: Input mask to modify
            original_image: Original image for face detection
            
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
            
            # Convert to OpenCV format
            img_array = np.array(original_image.convert('RGB'))
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            
            # Get image dimensions for filtering
            img_height, img_width = gray.shape
            
            # Detect faces with balanced parameters
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,   # Less sensitive (was 1.05)
                minNeighbors=5,    # Higher threshold (was 4)
                minSize=(80, 80),  # Larger minimum (was 30x30) to filter tiny false positives
                flags=cv2.CASCADE_SCALE_IMAGE
            )
            
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
                # Create elliptical exclusion zone for face + hair
                # REDUCED from v2.1: User feedback that shoulders/clothing were being excluded
                center_x = x + w // 2
                center_y = y + h // 2
                
                # Ellipse radii: REDUCED to be less aggressive
                radius_x = int(w * 0.55)           # 55% wider (was 70%)
                radius_y = int(h * 0.95)           # 95% taller (was 120%)
                
                # Shift center upward to cover hair better
                center_y = center_y - int(h * 0.1)  # 10% shift (was 15%)
                
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
                
                logger.info(f"Excluded elliptical face+hair region: center ({center_x},{center_y}), size ({w}x{h}), radii ({radius_x}x{radius_y})")
            
            result_mask = Image.fromarray(mask_array, mode='L')
            logger.info(f"✅ Face exclusion complete: {len(faces)} face(s) excluded from mask (elliptical regions)")
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
                       focus_primary: bool = True, min_region_size: float = 0.05) -> Optional[Image.Image]:
    """Apply smart masking and return composited result"""
    return _processor.apply_smart_composite(original_path, result_path, None, threshold, feather, focus_primary, min_region_size)


def preview_smart_mask(original_path: str, result_path: str,
                      threshold: int = 15, feather: int = 20,
                      focus_primary: bool = True, min_region_size: float = 0.05) -> Optional[Image.Image]:
    """Preview the mask as a red overlay"""
    return _processor.preview_mask(original_path, result_path, threshold, feather, focus_primary, min_region_size)

