"""
Secure Temporary Image Upload System

This module provides secure, temporary image hosting for APIs that require public URLs
while maintaining privacy by using temporary, auto-expiring uploads.
"""

import os
import base64
import json
import tempfile
from datetime import datetime, timedelta
import requests
from PIL import Image
import io

from core.logger import get_logger
from app.config import Config

logger = get_logger()


class SecureImageUploader:
    """Handles secure, temporary image uploads for API compatibility"""
    
    def __init__(self):
        self.temp_urls = {}  # Track temporary URLs for cleanup
        
    def upload_image_securely(self, image_path, expire_hours=1):
        """
        Upload image to a temporary, secure location
        
        Args:
            image_path: Path to local image file
            expire_hours: Hours until automatic deletion (default: 1 hour)
            
        Returns:
            tuple: (success: bool, url: str or None, error: str or None)
        """
        try:
            # Method 1: Use a temporary image hosting service (recommended)
            return self._upload_to_temp_service(image_path, expire_hours)
            
        except Exception as e:
            logger.error(f"Secure upload failed: {e}")
            return False, None, str(e)
    
    def _upload_to_temp_service(self, image_path, expire_hours):
        """Upload to a temporary hosting service with auto-deletion"""
        try:
            # For medium privacy mode, we'll use base64 as a secure fallback
            # since external temp services are unreliable and may not work consistently
            logger.info("Medium privacy: Using base64 encoding (secure, no external hosting)")
            return self._fallback_upload_method(image_path, expire_hours)
            
        except Exception as e:
            logger.warning(f"Temp service upload failed: {e}")
            return self._fallback_upload_method(image_path, expire_hours)
    
    def _fallback_upload_method(self, image_path, expire_hours):
        """Fallback method using base64 data URLs where supported"""
        try:
            # For APIs that support data URLs, convert to base64
            with open(image_path, 'rb') as f:
                image_data = f.read()
                
            # Convert to base64
            base64_data = base64.b64encode(image_data).decode('utf-8')
            
            # Determine MIME type
            image = Image.open(image_path)
            format_lower = image.format.lower() if image.format else 'png'
            mime_type = f"image/{format_lower}"
            
            # Create data URL
            data_url = f"data:{mime_type};base64,{base64_data}"
            
            logger.info("Using base64 data URL (private, no external hosting)")
            return True, data_url, None
            
        except Exception as e:
            logger.error(f"Fallback upload failed: {e}")
            return False, None, str(e)
    
    def cleanup_expired_urls(self):
        """Clean up expired temporary URLs"""
        try:
            now = datetime.now()
            expired_urls = []
            
            for url, info in self.temp_urls.items():
                if now > info['expires']:
                    expired_urls.append(url)
            
            for url in expired_urls:
                del self.temp_urls[url]
                logger.info(f"Cleaned up expired temporary URL")
                
        except Exception as e:
            logger.warning(f"Cleanup failed: {e}")
    
    def get_upload_status(self):
        """Get status of current temporary uploads"""
        try:
            self.cleanup_expired_urls()
            active_count = len(self.temp_urls)
            
            status = {
                'active_uploads': active_count,
                'uploads': []
            }
            
            for url, info in self.temp_urls.items():
                status['uploads'].append({
                    'expires_in': str(info['expires'] - datetime.now()),
                    'original_file': os.path.basename(info['original_path'])
                })
            
            return status
            
        except Exception as e:
            logger.error(f"Status check failed: {e}")
            return {'active_uploads': 0, 'uploads': []}


class PrivacyFriendlyUploader:
    """Alternative uploader that prioritizes privacy"""
    
    def __init__(self):
        self.uploader = SecureImageUploader()
    
    def upload_with_privacy_warning(self, image_path, ai_model):
        """
        Upload image with clear privacy information
        
        Args:
            image_path: Path to local image
            ai_model: AI model name for context
            
        Returns:
            tuple: (success: bool, url: str or None, privacy_info: str)
        """
        try:
            privacy_mode = Config.PRIVACY_MODE.lower()
            
            if privacy_mode == "high":
                # Most private: Base64 data URLs only
                success, url, error = self.uploader._fallback_upload_method(image_path, 1)
                
                if success and url.startswith('data:'):
                    privacy_info = "🔒 HIGH PRIVACY: Using base64 data (no external hosting)"
                    return True, url, privacy_info
                else:
                    privacy_info = "❌ HIGH PRIVACY MODE: API doesn't support base64 data URLs"
                    return False, None, privacy_info
            
            elif privacy_mode == "medium":
                # Balanced: Use base64 encoding (secure, no external hosting)
                success, url, error = self.uploader.upload_image_securely(image_path, Config.TEMP_UPLOAD_EXPIRE_HOURS)
                
                if success:
                    if url and url.startswith('data:'):
                        privacy_info = "🔐 MEDIUM PRIVACY: Using base64 data (secure, no external hosting)"
                    else:
                        privacy_info = f"🔐 MEDIUM PRIVACY: Secure upload (auto-deletes in {Config.TEMP_UPLOAD_EXPIRE_HOURS}h)"
                    return True, url, privacy_info
                else:
                    privacy_info = f"❌ MEDIUM PRIVACY FAILED: {error}"
                    return False, None, privacy_info
            
            else:  # privacy_mode == "low" or demo mode
                # Demo mode: Use sample URLs
                sample_url = Config.SAMPLE_URLS.get(ai_model, Config.SAMPLE_URLS.get('seededit'))
                privacy_info = "🔓 DEMO MODE: Using sample image (your image not uploaded)"
                return True, sample_url, privacy_info
                
        except Exception as e:
            privacy_info = f"❌ ERROR: {str(e)}"
            return False, None, privacy_info


# Global instances
secure_uploader = SecureImageUploader()
privacy_uploader = PrivacyFriendlyUploader()
