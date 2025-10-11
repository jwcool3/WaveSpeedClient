"""
Resolution Optimizer for Seedream V4

This module provides resolution recommendations and aspect ratio analysis
based on Seedream V4's official recommended resolutions.

Features:
- Detect aspect ratio from image dimensions
- Find nearest recommended resolution
- Optimize resolution for best quality
- Display resolution analysis and warnings
"""

import math
from typing import Dict, List, Tuple, Optional
from core.logger import get_logger

logger = get_logger()


class SeedreamResolutionOptimizer:
    """Manages resolution optimization for Seedream V4"""
    
    # Official Seedream V4 Recommended Resolutions
    # Format: (width, height, pixel_count, quality_tier)
    RECOMMENDED_RESOLUTIONS = {
        # 2M Pixel Tier (Highest Quality)
        "2M": [
            {"ratio": "1:1", "width": 1448, "height": 1448, "pixels": 2096704, "rounded_w": 1408, "rounded_h": 1408},
            {"ratio": "3:2", "width": 1773, "height": 1182, "pixels": 2095686, "rounded_w": 1728, "rounded_h": 1152},
            {"ratio": "4:3", "width": 1672, "height": 1254, "pixels": 2096688, "rounded_w": 1664, "rounded_h": 1216},
            {"ratio": "16:9", "width": 1936, "height": 1089, "pixels": 2108304, "rounded_w": 1920, "rounded_h": 1088},
            {"ratio": "21:9", "width": 2212, "height": 948, "pixels": 2096976, "rounded_w": 2176, "rounded_h": 960},
        ],
        # 1M Pixel Tier (Good Quality)
        "1M": [
            {"ratio": "1:1", "width": 1024, "height": 1024, "pixels": 1048576, "rounded_w": 1024, "rounded_h": 1024},
            {"ratio": "3:2", "width": 1254, "height": 836, "pixels": 1048344, "rounded_w": 1216, "rounded_h": 832},
            {"ratio": "4:3", "width": 1182, "height": 887, "pixels": 1048434, "rounded_w": 1152, "rounded_h": 896},
            {"ratio": "16:9", "width": 1365, "height": 768, "pixels": 1048320, "rounded_w": 1344, "rounded_h": 768},
            {"ratio": "21:9", "width": 1564, "height": 670, "pixels": 1047880, "rounded_w": 1536, "rounded_h": 640},
        ],
        # 100K Pixel Tier (Fast/Draft)
        "100K": [
            {"ratio": "1:1", "width": 323, "height": 323, "pixels": 104329, "rounded_w": 320, "rounded_h": 320},
            {"ratio": "3:2", "width": 397, "height": 264, "pixels": 104808, "rounded_w": 384, "rounded_h": 256},
            {"ratio": "4:3", "width": 374, "height": 280, "pixels": 104720, "rounded_w": 448, "rounded_h": 320},
            {"ratio": "16:9", "width": 432, "height": 243, "pixels": 104976, "rounded_w": 448, "rounded_h": 256},
            {"ratio": "21:9", "width": 495, "height": 212, "pixels": 104940, "rounded_w": 576, "rounded_h": 256},
        ]
    }
    
    # Aspect ratio definitions with tolerance
    ASPECT_RATIOS = {
        "1:1": {"ratio": 1.0, "name": "Square", "tolerance": 0.05},
        "5:4": {"ratio": 1.25, "name": "Portrait", "tolerance": 0.05},
        "4:3": {"ratio": 1.333, "name": "Standard", "tolerance": 0.05},
        "3:2": {"ratio": 1.5, "name": "Classic Photo", "tolerance": 0.05},
        "16:9": {"ratio": 1.778, "name": "Widescreen", "tolerance": 0.05},
        "21:9": {"ratio": 2.333, "name": "Ultra-wide", "tolerance": 0.05},
    }
    
    def __init__(self):
        """Initialize the resolution optimizer"""
        self.all_resolutions = []
        # Flatten all resolutions for easier searching
        for tier, resolutions in self.RECOMMENDED_RESOLUTIONS.items():
            for res in resolutions:
                res_copy = res.copy()
                res_copy['tier'] = tier
                self.all_resolutions.append(res_copy)
        
        logger.info("Resolution optimizer initialized with recommended resolutions")
    
    def detect_aspect_ratio(self, width: int, height: int) -> Dict:
        """
        Detect the aspect ratio of given dimensions.
        
        Args:
            width: Image width
            height: Image height
            
        Returns:
            Dict with ratio info: {
                'ratio_name': '16:9',
                'ratio_value': 1.778,
                'ratio_display': '16:9',
                'is_standard': True/False,
                'match_confidence': 0.95
            }
        """
        if height == 0:
            return {
                'ratio_name': 'Invalid',
                'ratio_value': 0,
                'ratio_display': 'N/A',
                'is_standard': False,
                'match_confidence': 0,
                'actual_ratio': 0,
                'is_portrait': False
            }
        
        actual_ratio = width / height
        is_portrait = width < height
        
        # For portrait images, we need to check against inverted ratios
        # e.g., 1290×1678 is 3:4 portrait, not 1:1
        if is_portrait:
            comparison_ratio = height / width  # Invert for comparison
        else:
            comparison_ratio = actual_ratio
        
        # Find closest standard aspect ratio
        best_match = None
        best_distance = float('inf')
        
        for ratio_name, ratio_info in self.ASPECT_RATIOS.items():
            distance = abs(comparison_ratio - ratio_info['ratio'])
            if distance < best_distance:
                best_distance = distance
                best_match = ratio_name
        
        # Calculate match confidence
        ratio_info = self.ASPECT_RATIOS[best_match]
        is_within_tolerance = best_distance <= ratio_info['tolerance']
        confidence = max(0, 1.0 - (best_distance / ratio_info['tolerance']))
        
        # Format display name with portrait indicator
        if is_portrait:
            display_name = f"{best_match} ({ratio_info['name']}) Portrait"
        else:
            display_name = f"{best_match} ({ratio_info['name']})"
        
        return {
            'ratio_name': best_match,
            'ratio_value': actual_ratio,
            'ratio_display': display_name,
            'is_standard': is_within_tolerance,
            'match_confidence': confidence,
            'actual_ratio': actual_ratio,
            'is_portrait': is_portrait
        }
    
    def find_nearest_recommended(self, width: int, height: int, 
                                 prefer_tier: Optional[str] = None) -> Dict:
        """
        Find the nearest recommended resolution.
        
        Args:
            width: Target width
            height: Target height
            prefer_tier: Optional tier preference ('2M', '1M', '100K')
            
        Returns:
            Dict with recommended resolution and analysis
        """
        # Detect aspect ratio first
        ratio_info = self.detect_aspect_ratio(width, height)
        target_pixels = width * height
        is_portrait = ratio_info.get('is_portrait', False)
        
        # Filter resolutions by tier if specified
        search_pool = self.all_resolutions
        if prefer_tier:
            search_pool = [r for r in self.all_resolutions if r['tier'] == prefer_tier]
        
        # Find best match based on:
        # 1. Aspect ratio match (HIGHEST PRIORITY)
        # 2. Size similarity (keep close to original size within 1024-4096 range)
        # 3. Prefer same tier to avoid drastic resolution changes
        best_match = None
        best_score = float('inf')
        
        # Calculate which tier the current resolution falls into
        current_tier = "2M" if target_pixels >= 2000000 else "1M" if target_pixels >= 1000000 else "100K"
        
        for recommended in search_pool:
            # Check if we need to compare with portrait orientation
            rec_width = recommended['rounded_w']
            rec_height = recommended['rounded_h']
            
            # For portrait input, we want portrait output (or we can flip landscape recommendations)
            # Calculate aspect ratio similarity
            if is_portrait:
                # Compare with inverted ratios for better matching
                # 1290×1678 (portrait 3:4) should match 1216×1664 (4:3) flipped
                ratio_target = height / width  # Portrait comparison
                rec_ratio = rec_height / rec_width  # Check if rec would be good in portrait
                
                # Check if this recommendation would work better rotated
                rec_ratio_rotated = rec_width / rec_height
                ratio_diff_normal = abs(ratio_target - rec_ratio)
                ratio_diff_rotated = abs(ratio_target - rec_ratio_rotated)
                
                # Use the better orientation
                ratio_diff = min(ratio_diff_normal, ratio_diff_rotated)
            else:
                # Landscape comparison
                ratio_target = width / height
                rec_ratio = rec_width / rec_height
                ratio_diff = abs(ratio_target - rec_ratio)
            
            # Size similarity score - prefer keeping size close to original
            # But don't penalize too much if it's in valid range (1024-4096)
            pixel_diff_pct = abs(target_pixels - recommended['pixels']) / target_pixels
            
            # If both are in valid range, don't penalize pixel difference as much
            if 1024*1024 <= target_pixels <= 4096*4096 and 1024*1024 <= recommended['pixels'] <= 4096*4096:
                pixel_penalty = pixel_diff_pct * 10  # Light penalty for size difference
            else:
                pixel_penalty = pixel_diff_pct * 50  # Heavier penalty if out of range
            
            # Tier matching bonus - prefer same tier to avoid drastic changes
            tier_penalty = 0 if recommended['tier'] == current_tier else 20
            
            # Dimensional distance (how much width/height changes)
            dim_change_pct = (abs(width - rec_width) / width + abs(height - rec_height) / height) / 2
            
            # Combined score:
            # - Aspect ratio difference is HIGHEST priority (1000x weight)
            # - Size difference is secondary (10-50x weight depending on range)
            # - Dimensional change is tertiary (100x weight)
            # - Tier matching gives small bonus (20 points)
            score = (ratio_diff * 1000) + pixel_penalty + (dim_change_pct * 100) + tier_penalty
            
            if score < best_score:
                best_score = score
                best_match = recommended
        
        if not best_match:
            return None
        
        # For portrait input, check if we should recommend portrait orientation
        # by swapping the recommended dimensions
        rec_width = best_match['rounded_w']
        rec_height = best_match['rounded_h']
        
        if is_portrait:
            # Check if this recommendation works better in portrait orientation
            # Portrait input (1440×1800) should get portrait output (1216×1664), not landscape (1664×1216)
            rec_is_landscape = rec_width > rec_height
            
            if rec_is_landscape:
                # Swap dimensions to make it portrait
                rec_width, rec_height = rec_height, rec_width
                logger.debug(f"Portrait input: swapped recommendation from {best_match['rounded_w']}×{best_match['rounded_h']} to {rec_width}×{rec_height}")
        
        # Calculate adjustment info
        width_diff = rec_width - width
        height_diff = rec_height - height
        pixel_diff = best_match['pixels'] - target_pixels
        pixel_change_pct = (pixel_diff / target_pixels * 100) if target_pixels > 0 else 0
        
        # Create adjusted recommendation dict
        adjusted_recommendation = best_match.copy()
        adjusted_recommendation['rounded_w'] = rec_width
        adjusted_recommendation['rounded_h'] = rec_height
        if is_portrait:
            adjusted_recommendation['ratio'] = f"{best_match['ratio']} Portrait"
        
        return {
            'recommended': adjusted_recommendation,
            'current': {'width': width, 'height': height, 'pixels': target_pixels},
            'adjustment': {
                'width_diff': width_diff,
                'height_diff': height_diff,
                'pixel_diff': pixel_diff,
                'pixel_change_pct': pixel_change_pct
            },
            'match_quality': 'excellent' if best_score < 10 else 'good' if best_score < 50 else 'fair',
            'is_exact_match': width == rec_width and height == rec_height
        }
    
    def analyze_resolution(self, width: int, height: int) -> Dict:
        """
        Comprehensive resolution analysis.
        
        Args:
            width: Image width
            height: Image height
            
        Returns:
            Complete analysis dict with recommendations
        """
        ratio_info = self.detect_aspect_ratio(width, height)
        nearest = self.find_nearest_recommended(width, height)
        pixels = width * height
        
        # Determine quality tier
        if pixels >= 2000000:
            current_tier = "2M"
            tier_name = "High Quality (2M pixels)"
        elif pixels >= 1000000:
            current_tier = "1M"
            tier_name = "Good Quality (1M pixels)"
        elif pixels >= 100000:
            current_tier = "100K"
            tier_name = "Draft Quality (100K pixels)"
        else:
            current_tier = "Below"
            tier_name = "Below Minimum"
        
        # Check if current resolution is optimal
        is_optimal = nearest and nearest['is_exact_match']
        
        # Generate recommendations (FOCUS ON ASPECT RATIO, NOT SIZE)
        recommendations = []
        if not is_optimal and nearest:
            rec = nearest['recommended']
            
            # Calculate how much the aspect ratio differs
            current_ratio = width / height if height > 0 else 1.0
            rec_ratio = rec['rounded_w'] / rec['rounded_h']
            ratio_diff_pct = abs(current_ratio - rec_ratio) / current_ratio * 100
            
            # Determine priority based on aspect ratio difference, not size change
            if not ratio_info['is_standard']:
                # Non-standard aspect ratio = high priority to fix
                priority = 'high'
                reason = f"Fix aspect ratio to {rec['ratio']}"
            elif ratio_diff_pct > 5:
                # Noticeable aspect ratio difference
                priority = 'medium'
                reason = f"Improve aspect ratio to {rec['ratio']}"
            else:
                # Minor adjustment
                priority = 'low'
                reason = f"Fine-tune to {rec['ratio']} {rec['tier']}"
            
            recommendations.append({
                'type': 'optimize',
                'tier': rec['tier'],
                'width': rec['rounded_w'],
                'height': rec['rounded_h'],
                'reason': reason,
                'priority': priority
            })
        
        # DON'T suggest tier changes just based on size - user wants to keep their size
        # Only suggest if aspect ratio is already optimal and size is significantly off
        if is_optimal:
            if current_tier == "Below" and pixels < 1000000:
                recommendations.append({
                    'type': 'upgrade',
                    'tier': '1M',
                    'reason': "Consider larger resolution for better quality",
                    'priority': 'low'
                })
        
        return {
            'width': width,
            'height': height,
            'pixels': pixels,
            'aspect_ratio': ratio_info,
            'tier': {
                'current': current_tier,
                'name': tier_name
            },
            'is_optimal': is_optimal,
            'nearest_recommended': nearest,
            'recommendations': recommendations,
            'warnings': self._generate_warnings(width, height, ratio_info)
        }
    
    def _generate_warnings(self, width: int, height: int, ratio_info: Dict) -> List[str]:
        """Generate warnings for non-optimal resolutions"""
        warnings = []
        
        # Check if resolution is too small
        pixels = width * height
        if pixels < 100000:
            warnings.append("⚠️ Resolution below minimum recommended (100K pixels)")
        
        # Check if resolution is not standard aspect ratio
        if not ratio_info['is_standard']:
            is_portrait = ratio_info.get('is_portrait', False)
            actual_ratio = ratio_info['actual_ratio']
            # Show more helpful message
            if is_portrait:
                warnings.append(f"ℹ️ Close to {ratio_info['ratio_name']} (portrait), optimize for better results")
            else:
                warnings.append(f"ℹ️ Close to {ratio_info['ratio_name']}, optimize for better results")
        
        # Check if dimensions are not divisible by 64 (common AI model requirement)
        # Only show this as info, not as a major warning
        if width % 64 != 0 or height % 64 != 0:
            # Don't show this warning as it's too technical for most users
            pass
        
        # Check if aspect ratio is extreme
        aspect = width / height if height > 0 else 1.0
        if aspect > 3.0 or aspect < 0.33:
            warnings.append("⚠️ Extreme aspect ratio may cause quality issues")
        
        return warnings
    
    def get_tier_recommendations(self, aspect_ratio_name: str) -> List[Dict]:
        """
        Get all recommended resolutions for a specific aspect ratio.
        
        Args:
            aspect_ratio_name: Aspect ratio like '16:9', '1:1', etc.
            
        Returns:
            List of recommended resolutions for that aspect ratio
        """
        recommendations = []
        for res in self.all_resolutions:
            if res['ratio'] == aspect_ratio_name:
                recommendations.append({
                    'tier': res['tier'],
                    'width': res['rounded_w'],
                    'height': res['rounded_h'],
                    'pixels': res['pixels'],
                    'exact_width': res['width'],
                    'exact_height': res['height']
                })
        
        # Sort by tier (2M > 1M > 100K)
        tier_order = {'2M': 0, '1M': 1, '100K': 2}
        recommendations.sort(key=lambda x: tier_order.get(x['tier'], 99))
        
        return recommendations


# Export
__all__ = ['SeedreamResolutionOptimizer']

