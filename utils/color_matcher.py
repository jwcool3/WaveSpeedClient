"""
Color Matching Utility

Provides non-AI color correction methods to match result images to source images.
Uses statistical color transfer in LAB color space for natural-looking corrections.
"""

import numpy as np
from PIL import Image
import cv2
from core.logger import get_logger

logger = get_logger()


class ColorMatcher:
    """Color matching and correction using classical computer vision techniques"""
    
    @staticmethod
    def match_colors_lab(source_path: str, target_path: str, strength: float = 0.6) -> Image.Image:
        """
        Match target image colors to source image using LAB color space transfer.
        
        Args:
            source_path: Path to source/reference image
            target_path: Path to target image to correct
            strength: Correction strength (0.0 = no change, 1.0 = full match). Default 0.6 for subtle correction.
            
        Returns:
            PIL Image with corrected colors
        """
        try:
            # Load images
            source = cv2.imread(source_path)
            target = cv2.imread(target_path)
            
            if source is None or target is None:
                logger.error("Failed to load images for color matching")
                return Image.open(target_path)
            
            # Convert BGR to RGB
            source = cv2.cvtColor(source, cv2.COLOR_BGR2RGB)
            target = cv2.cvtColor(target, cv2.COLOR_BGR2RGB)
            
            # Convert to LAB color space
            source_lab = cv2.cvtColor(source, cv2.COLOR_RGB2LAB).astype(np.float32)
            target_lab = cv2.cvtColor(target, cv2.COLOR_RGB2LAB).astype(np.float32)
            
            # Calculate statistics for each channel
            source_mean = source_lab.mean(axis=(0, 1))
            source_std = source_lab.std(axis=(0, 1))
            
            target_mean = target_lab.mean(axis=(0, 1))
            target_std = target_lab.std(axis=(0, 1))
            
            # Avoid division by zero
            target_std = np.where(target_std == 0, 1, target_std)
            
            # Transfer color statistics
            # Formula: (target - target_mean) * (source_std / target_std) + source_mean
            result_lab = target_lab.copy()
            
            for channel in range(3):
                # Normalize target channel
                result_lab[:, :, channel] = (target_lab[:, :, channel] - target_mean[channel]) / target_std[channel]
                # Scale to source std and shift to source mean
                result_lab[:, :, channel] = result_lab[:, :, channel] * source_std[channel] + source_mean[channel]
            
            # Apply strength factor (blend between original and corrected)
            result_lab = target_lab * (1 - strength) + result_lab * strength
            
            # Clip to valid range
            result_lab = np.clip(result_lab, 0, 255).astype(np.uint8)
            
            # Convert back to RGB
            result_rgb = cv2.cvtColor(result_lab, cv2.COLOR_LAB2RGB)
            
            # Convert to PIL Image
            result_image = Image.fromarray(result_rgb)
            
            logger.info(f"Color matching applied with {strength:.0%} strength")
            return result_image
            
        except Exception as e:
            logger.error(f"Error in color matching: {e}")
            # Return original target image on error
            try:
                return Image.open(target_path)
            except:
                return None
    
    @staticmethod
    def match_colors_histogram(source_path: str, target_path: str, strength: float = 0.6) -> Image.Image:
        """
        Match target image colors using histogram matching.
        
        Args:
            source_path: Path to source/reference image
            target_path: Path to target image to correct
            strength: Correction strength (0.0 = no change, 1.0 = full match)
            
        Returns:
            PIL Image with corrected colors
        """
        try:
            # Load images
            source = cv2.imread(source_path)
            target = cv2.imread(target_path)
            
            if source is None or target is None:
                logger.error("Failed to load images for histogram matching")
                return Image.open(target_path)
            
            # Convert BGR to RGB
            source = cv2.cvtColor(source, cv2.COLOR_BGR2RGB)
            target = cv2.cvtColor(target, cv2.COLOR_BGR2RGB)
            
            # Match histogram for each channel
            result = np.zeros_like(target)
            
            for channel in range(3):
                # Calculate histograms
                source_hist, bins = np.histogram(source[:, :, channel].flatten(), 256, [0, 256])
                target_hist, _ = np.histogram(target[:, :, channel].flatten(), 256, [0, 256])
                
                # Calculate cumulative distribution functions
                source_cdf = source_hist.cumsum()
                target_cdf = target_hist.cumsum()
                
                # Normalize
                source_cdf = source_cdf / source_cdf[-1]
                target_cdf = target_cdf / target_cdf[-1]
                
                # Create lookup table
                lookup = np.zeros(256, dtype=np.uint8)
                j = 0
                for i in range(256):
                    while j < 255 and target_cdf[j] < source_cdf[i]:
                        j += 1
                    lookup[i] = j
                
                # Apply lookup table
                result[:, :, channel] = lookup[target[:, :, channel]]
            
            # Blend with original based on strength
            result = (target * (1 - strength) + result * strength).astype(np.uint8)
            
            # Convert to PIL Image
            result_image = Image.fromarray(result)
            
            logger.info(f"Histogram matching applied with {strength:.0%} strength")
            return result_image
            
        except Exception as e:
            logger.error(f"Error in histogram matching: {e}")
            try:
                return Image.open(target_path)
            except:
                return None
    
    @staticmethod
    def subtle_color_correction(source_path: str, target_path: str, method: str = 'lab') -> Image.Image:
        """
        Apply subtle color correction optimized for minor adjustments.
        
        Args:
            source_path: Path to source/reference image
            target_path: Path to target image to correct
            method: 'lab' or 'histogram'
            
        Returns:
            PIL Image with subtle color correction applied
        """
        # Use 60% strength for subtle corrections (not too aggressive)
        if method == 'lab':
            return ColorMatcher.match_colors_lab(source_path, target_path, strength=0.6)
        elif method == 'histogram':
            return ColorMatcher.match_colors_histogram(source_path, target_path, strength=0.6)
        else:
            logger.warning(f"Unknown color matching method: {method}")
            return Image.open(target_path)


# Convenience function for external use
def match_image_colors(source_path: str, target_path: str, output_path: str = None, 
                       method: str = 'lab', strength: float = 0.6) -> bool:
    """
    Match colors from target image to source image and optionally save result.
    
    Args:
        source_path: Path to source/reference image
        target_path: Path to target image to correct
        output_path: Optional path to save corrected image
        method: 'lab' or 'histogram'
        strength: Correction strength (0.0-1.0), default 0.6 for subtle correction
        
    Returns:
        True if successful, False otherwise
    """
    try:
        matcher = ColorMatcher()
        
        if method == 'lab':
            result = matcher.match_colors_lab(source_path, target_path, strength)
        elif method == 'histogram':
            result = matcher.match_colors_histogram(source_path, target_path, strength)
        else:
            logger.error(f"Unknown method: {method}")
            return False
        
        if result and output_path:
            result.save(output_path, quality=95)
            logger.info(f"Color-matched image saved to: {output_path}")
            return True
        
        return result is not None
        
    except Exception as e:
        logger.error(f"Error in match_image_colors: {e}")
        return False

