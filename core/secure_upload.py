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
            # Try imgbb first (free, reliable, supports expiration)
            logger.info("🚀 Uploading image to temporary hosting service...")
            success, url, error = self._upload_to_imgbb(image_path, expire_hours)
            
            if success:
                logger.info(f"✅ Successfully uploaded to temp service: {url[:50]}...")
                return success, url, error
            
            # Check if we should avoid base64 fallback
            # Set DISABLE_BASE64_FALLBACK=true in .env to fail instead of falling back
            disable_fallback = os.getenv("DISABLE_BASE64_FALLBACK", "false").lower() == "true"
            
            if disable_fallback:
                logger.error(f"❌ ImgBB upload failed and base64 fallback is disabled: {error}")
                logger.error("💡 To enable base64 fallback, remove DISABLE_BASE64_FALLBACK from .env")
                return False, None, f"Upload failed (base64 fallback disabled): {error}"
            
            logger.warning(f"⚠️ ImgBB upload failed: {error}")
            logger.warning("⚠️ Falling back to base64 data URL (this may not work with all APIs)")
            logger.warning("💡 To avoid this, ensure your ImgBB API key is valid and your network connection is stable")
            return self._fallback_upload_method(image_path, expire_hours)
            
        except Exception as e:
            logger.warning(f"⚠️ Temp service upload failed: {e}")
            
            disable_fallback = os.getenv("DISABLE_BASE64_FALLBACK", "false").lower() == "true"
            if disable_fallback:
                return False, None, f"Upload failed (base64 fallback disabled): {str(e)}"
            
            return self._fallback_upload_method(image_path, expire_hours)
    
    def _upload_to_imgbb(self, image_path, expire_hours):
        """Upload to ImgBB temporary hosting with compression and retry logic"""
        try:
            # ImgBB free API key (public, no signup needed)
            # This is a demo key - users should get their own from https://api.imgbb.com/
            IMGBB_API_KEY = os.getenv("IMGBB_API_KEY", "YOUR_IMGBB_KEY")
            
            if IMGBB_API_KEY == "YOUR_IMGBB_KEY":
                logger.warning("⚠️ No ImgBB API key configured. Set IMGBB_API_KEY in .env file")
                logger.warning("Get your free API key from: https://api.imgbb.com/")
                return False, None, "No API key configured"
            
            # Convert expiration hours to seconds (imgbb max is 15552000 seconds = 180 days)
            expiration_seconds = min(int(expire_hours * 3600), 15552000)
            
            # Get original file size
            original_size = os.path.getsize(image_path)
            original_size_mb = original_size / (1024 * 1024)
            logger.info(f"📤 Uploading image: {original_size_mb:.2f} MB (original quality)")
            
            # Check if compression is enabled (disabled by default to preserve quality for AI)
            # Set ENABLE_IMAGE_COMPRESSION=true in .env to enable compression for large files
            enable_compression = os.getenv("ENABLE_IMAGE_COMPRESSION", "false").lower() == "true"
            
            # Only compress if explicitly enabled AND file is too large for ImgBB
            # ImgBB free tier has 32MB limit, but we'll keep some margin
            MAX_SIZE_MB = 30
            if enable_compression and original_size_mb > MAX_SIZE_MB:
                logger.warning(f"⚠️ Image is very large ({original_size_mb:.2f} MB), compressing to fit ImgBB limit...")
                logger.warning("⚠️ This will reduce image quality. To upload original quality, use a smaller image.")
                image_data = self._compress_image(image_path, max_size_mb=MAX_SIZE_MB)
                compressed_size_mb = len(image_data) / (1024 * 1024)
                logger.info(f"✓ Compressed: {original_size_mb:.2f} MB → {compressed_size_mb:.2f} MB ({(compressed_size_mb/original_size_mb)*100:.1f}%)")
            else:
                # Read image data directly - PRESERVES ORIGINAL QUALITY
                if original_size_mb > 32:
                    logger.error(f"❌ Image too large: {original_size_mb:.2f} MB (ImgBB limit: 32 MB)")
                    logger.error("💡 Either: 1) Resize image to < 32 MB, or 2) Set ENABLE_IMAGE_COMPRESSION=true in .env")
                    return False, None, f"Image too large: {original_size_mb:.2f} MB (max 32 MB). Enable compression or use smaller image."
                
                logger.info("✓ Uploading original quality (no compression)")
                with open(image_path, 'rb') as f:
                    image_data = f.read()
            
            base64_image = base64.b64encode(image_data).decode('utf-8')
            base64_size_mb = len(base64_image) / (1024 * 1024)
            
            # Check if within ImgBB limits (32 MB for free tier)
            if base64_size_mb > 32:
                logger.error(f"❌ Image too large for ImgBB ({base64_size_mb:.2f} MB > 32 MB limit)")
                return False, None, f"Image too large: {base64_size_mb:.2f} MB (max 32 MB)"
            
            # Calculate timeout based on file size (minimum 60s, +15s per MB for large files)
            # Larger files need more time since we're not compressing
            timeout = max(60, int(60 + (base64_size_mb * 15)))
            logger.info(f"⏱️ Upload timeout set to {timeout}s for {base64_size_mb:.2f} MB upload (original quality)")
            
            # Upload to imgbb
            url = "https://api.imgbb.com/1/upload"
            payload = {
                "key": IMGBB_API_KEY,
                "image": base64_image,
                "expiration": expiration_seconds
            }
            
            # Retry logic for timeouts
            max_retries = 2
            for attempt in range(max_retries + 1):
                try:
                    if attempt > 0:
                        logger.info(f"🔄 Retry attempt {attempt}/{max_retries}...")
                    
                    logger.info(f"📡 Uploading to ImgBB... (expires in {expire_hours}h)")
                    response = requests.post(url, data=payload, timeout=timeout)
                    
                    if response.status_code == 200:
                        result = response.json()
                        if result.get("success"):
                            image_url = result["data"]["url"]
                            
                            # Track for cleanup
                            self.temp_urls[image_url] = {
                                'expires': datetime.now() + timedelta(hours=expire_hours),
                                'original_path': image_path
                            }
                            
                            logger.info(f"✅ Image uploaded successfully to: {image_url[:60]}...")
                            return True, image_url, None
                    
                    # Non-200 response
                    error_data = response.json() if response.content else {}
                    error_msg = error_data.get("error", {}).get("message", f"HTTP {response.status_code}")
                    logger.warning(f"⚠️ ImgBB upload failed: {error_msg}")
                    
                    # Don't retry on client errors (4xx)
                    if 400 <= response.status_code < 500:
                        return False, None, error_msg
                    
                    # Retry on server errors (5xx) or timeout
                    if attempt < max_retries:
                        import time
                        time.sleep(2)  # Wait before retry
                        continue
                    
                    return False, None, error_msg
                    
                except requests.exceptions.Timeout:
                    logger.warning(f"⏰ Upload timeout after {timeout}s (attempt {attempt + 1}/{max_retries + 1})")
                    if attempt < max_retries:
                        # Increase timeout for retry
                        timeout = int(timeout * 1.5)
                        logger.info(f"⏱️ Increasing timeout to {timeout}s for retry...")
                        import time
                        time.sleep(2)
                        continue
                    else:
                        return False, None, f"Upload timeout after {max_retries + 1} attempts"
                
                except requests.exceptions.RequestException as e:
                    logger.warning(f"🌐 Network error during upload: {e}")
                    if attempt < max_retries:
                        import time
                        time.sleep(2)
                        continue
                    return False, None, f"Network error: {str(e)}"
            
        except Exception as e:
            logger.error(f"❌ ImgBB upload error: {e}", exc_info=True)
            return False, None, str(e)
    
    def _compress_image(self, image_path, max_size_mb=5):
        """Compress image to reduce upload time and size"""
        try:
            img = Image.open(image_path)
            
            # Convert RGBA to RGB if necessary (for JPEG compression)
            if img.mode == 'RGBA':
                # Create white background
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[3])  # Use alpha channel as mask
                img = background
            elif img.mode not in ('RGB', 'L'):
                img = img.convert('RGB')
            
            # Start with quality 85
            quality = 85
            
            # Try compressing with decreasing quality until under max size
            for attempt in range(5):
                output = io.BytesIO()
                img.save(output, format='JPEG', quality=quality, optimize=True)
                compressed_data = output.getvalue()
                compressed_size_mb = len(compressed_data) / (1024 * 1024)
                
                if compressed_size_mb <= max_size_mb:
                    logger.debug(f"Compressed with quality {quality}: {compressed_size_mb:.2f} MB")
                    return compressed_data
                
                # Reduce quality for next attempt
                quality -= 15
                if quality < 40:
                    # If still too large at quality 40, resize the image
                    width, height = img.size
                    new_size = (int(width * 0.8), int(height * 0.8))
                    img = img.resize(new_size, Image.Resampling.LANCZOS)
                    quality = 85  # Reset quality after resize
                    logger.debug(f"Resizing image to {new_size} to reduce size")
            
            # Return best effort if still too large
            output = io.BytesIO()
            img.save(output, format='JPEG', quality=60, optimize=True)
            return output.getvalue()
            
        except Exception as e:
            logger.error(f"Image compression failed: {e}")
            # Return original data if compression fails
            with open(image_path, 'rb') as f:
                return f.read()
    
    def _fallback_upload_method(self, image_path, expire_hours):
        """Fallback method using base64 data URLs where supported"""
        try:
            logger.warning("⚠️ WARNING: Using base64 data URL fallback")
            logger.warning("⚠️ This may not work with Seedream V4 API (which requires HTTP URLs)")
            logger.warning("💡 For best results, configure a valid IMGBB_API_KEY in your .env file")
            
            # For APIs that support data URLs, convert to base64
            file_size = os.path.getsize(image_path)
            file_size_mb = file_size / (1024 * 1024)
            logger.info(f"📦 Creating base64 data URL for {file_size_mb:.2f} MB file...")
            
            with open(image_path, 'rb') as f:
                image_data = f.read()
                
            # Convert to base64
            base64_data = base64.b64encode(image_data).decode('utf-8')
            base64_size_mb = len(base64_data) / (1024 * 1024)
            
            # Determine MIME type
            image = Image.open(image_path)
            format_lower = image.format.lower() if image.format else 'png'
            mime_type = f"image/{format_lower}"
            
            # Create data URL
            data_url = f"data:{mime_type};base64,{base64_data}"
            
            logger.info(f"✓ Created base64 data URL: {base64_size_mb:.2f} MB (private, no external hosting)")
            logger.warning("⚠️ Note: Large base64 URLs may cause API errors or timeouts")
            return True, data_url, None
            
        except Exception as e:
            logger.error(f"❌ Fallback upload failed: {e}")
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
