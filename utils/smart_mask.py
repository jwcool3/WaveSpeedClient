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
        Clean up mask using morphological operations
        Removes small noise and fills small holes
        
        Args:
            mask: Input mask image
            
        Returns:
            Cleaned mask image
        """
        try:
            # Convert to numpy for morphological operations
            mask_array = np.array(mask)
            
            # OPTIMIZED: Reduced iterations for speed
            # Simple erosion followed by dilation (opening operation)
            from scipy import ndimage
            mask_array = ndimage.binary_erosion(mask_array, iterations=1).astype(np.uint8) * 255
            mask_array = ndimage.binary_dilation(mask_array, iterations=1).astype(np.uint8) * 255
            
            # Fill small holes (this is fast)
            mask_array = ndimage.binary_fill_holes(mask_array).astype(np.uint8) * 255
            
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

