"""
Configuration Management for WaveSpeed AI Application

This module handles all configuration settings and constants.
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration"""
    
    # API Configuration
    API_KEY = os.getenv("WAVESPEED_API_KEY")
    BASE_URL = "https://api.wavespeed.ai/api/v3"
    
    # API Endpoints
    ENDPOINTS = {
        'image_edit': f"{BASE_URL}/google/nano-banana/edit",
        'seededit': f"{BASE_URL}/bytedance/seededit-v3",
        'image_upscale': f"{BASE_URL}/wavespeed-ai/image-upscaler",
        'image_to_video': f"{BASE_URL}/wavespeed-ai/wan-2.2/i2v-480p",
        'seeddance': f"{BASE_URL}/bytedance/seedance-v1-pro-i2v-480p",
        'result_poll': f"{BASE_URL}/predictions/{{request_id}}/result"
    }
    
    # UI Configuration
    WINDOW_SIZE = "1200x900"
    WINDOW_MIN_SIZE = (800, 600)  # Minimum window size
    WINDOW_TITLE = "WaveSpeed AI - Complete Creative Suite"
    
    # Image Processing
    MAX_IMAGE_SIZE = (350, 250)  # Preview thumbnail size
    SUPPORTED_FORMATS = ('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp')
    
    # File Management
    PROMPTS_FILE = "saved_prompts.json"
    TEMP_PREFIX = "temp_"
    
    # Auto-Save Configuration
    AUTO_SAVE_ENABLED = True
    AUTO_SAVE_FOLDER = "WaveSpeed_Results"
    AUTO_SAVE_SUBFOLDERS = {
        'image_editor': 'Image_Editor',
        'seededit': 'SeedEdit',
        'upscaler': 'Image_Upscaler',
        'video': 'Image_to_Video',
        'seeddance': 'SeedDance'
    }
    
    # Privacy & Upload Configuration
    PRIVACY_MODE = "medium"  # "high", "medium", "low"
    # high: Base64 data URLs only (most private, no external hosting)
    # medium: Temporary hosting with 1-hour auto-delete
    # low: Use sample URLs (demo mode)
    
    TEMP_UPLOAD_EXPIRE_HOURS = 1  # Auto-delete after 1 hour
    
    # Processing Configuration
    DEFAULT_POLL_INTERVAL = 1.0
    VIDEO_POLL_INTERVAL = 2.0
    MAX_RETRIES = 3
    TIMEOUT = 300  # 5 minutes
    
    # Sample URLs (for demonstration)
    SAMPLE_URLS = {
        'upscaler': "https://d1q70pf5vjeyhc.cloudfront.net/media/6af332dfb8b245f4bd44fc6389f5a86a/images/1756969345097954105_vYnmieb7.jpg",
        'video': "https://d1q70pf5vjeyhc.cloudfront.net/media/6af332dfb8b245f4bd44fc6389f5a86a/images/1756971220323861267_eULQTVWW.png",
        'seededit': "https://d1q70pf5vjeyhc.cloudfront.net/media/6af332dfb8b245f4bd44fc6389f5a86a/images/1756972920861221095_bqH0XVRO.png",
        'seeddance': "https://d1q70pf5vjeyhc.cloudfront.net/media/6af332dfb8b245f4bd44fc6389f5a86a/images/1756972742227172839_EZxtqmie.png"
    }
    
    # UI Colors
    COLORS = {
        'success': 'green',
        'error': 'red',
        'warning': 'orange',
        'info': 'blue',
        'background': '#f0f0f0',
        'drop_zone': '#f8f8f8',
        'drop_hover': '#f0f8ff',
        'drop_active': '#e8f4f8'
    }
    
    # Validation Rules
    VIDEO_DURATIONS = [5, 8]
    SEEDDANCE_DURATIONS = [5, 6, 7, 8, 9, 10]
    SEED_RANGE = (-1, 2147483647)
    CREATIVITY_RANGE = (-2, 2)
    GUIDANCE_SCALE_RANGE = (0.0, 1.0)
    RESOLUTIONS = ["2k", "4k", "8k"]
    OUTPUT_FORMATS = {
        'image': ["png", "jpg", "webp"],
        'video': ["mp4"]
    }
    
    @classmethod
    def validate(cls):
        """Validate configuration"""
        errors = []
        
        if not cls.API_KEY:
            errors.append("WAVESPEED_API_KEY not found in environment variables")
        
        return errors
    
    @classmethod
    def get_temp_filename(cls, prefix="", suffix=".png"):
        """Generate temporary filename"""
        return f"{cls.TEMP_PREFIX}{prefix}{suffix}"
    
    @classmethod
    def is_supported_format(cls, filename):
        """Check if file format is supported"""
        return filename.lower().endswith(cls.SUPPORTED_FORMATS)
