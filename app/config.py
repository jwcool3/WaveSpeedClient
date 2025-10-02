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
    
    # AI Prompt Advisor Configuration
    CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    AI_ADVISOR_PROVIDER = os.getenv("AI_ADVISOR_PROVIDER", "claude")  # "claude" or "openai"
    
    # API Endpoints
    ENDPOINTS = {
        'image_edit': f"{BASE_URL}/google/nano-banana/edit",
        'seededit': f"{BASE_URL}/bytedance/seededit-v3",
        'seedream_v4': f"{BASE_URL}/bytedance/seedream-v4/edit",
        'image_upscale': f"{BASE_URL}/wavespeed-ai/image-upscaler",
        'image_to_video': f"{BASE_URL}/wavespeed-ai/wan-2.2/i2v-480p",
        'seeddance': f"{BASE_URL}/bytedance/seedance-v1-pro-i2v-480p",  # Default to 480p
        'seeddance_480p': f"{BASE_URL}/bytedance/seedance-v1-pro-i2v-480p",   # SeedDance V1 Pro 480p
        'seeddance_720p': f"{BASE_URL}/bytedance/seedance-v1-pro-i2v-720p",   # SeedDance V1 Pro 720p
        'result_poll': f"{BASE_URL}/predictions/{{request_id}}/result",
        'balance': f"{BASE_URL}/balance"
    }
    
    # Seedream V4 Configuration
    SEEDREAM_V4_SIZES = [
        "1024*1024",
        "1024*2048", 
        "2048*1024",
        "2048*2048",
        "2048*4096",
        "4096*2048",
        "3840*2160",  # 4K landscape
        "2160*3840"   # 4K portrait
    ]
    
    # UI Configuration
    WINDOW_SIZE = "1400x900"
    WINDOW_MIN_SIZE = (1000, 600)  # Minimum window size
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
        'image_editor': 'Nano_Banana_Editor',
        'seededit': 'SeedEdit',
        'seedream_v4': 'Seedream_V4',
        'upscaler': 'Image_Upscaler',
        'video': 'Wan_2.2',
        'seeddance': 'SeedDance_Pro'  # Updated folder name
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
        'seedream_v4': "https://d1q70pf5vjeyhc.cloudfront.net/media/6af332dfb8b245f4bd44fc6389f5a86a/images/1756972920861221095_bqH0XVRO.png",
        'seeddance': "https://d1q70pf5vjeyhc.cloudfront.net/media/6af332dfb8b245f4bd44fc6389f5a86a/images/1756972742227172839_EZxtqmie.png",
        'seeddance_480p': "https://d1q70pf5vjeyhc.cloudfront.net/media/6af332dfb8b245f4bd44fc6389f5a86a/images/1756972742227172839_EZxtqmie.png",
        'seeddance_720p': "https://d3gnftk2yhz9lr.wavespeed.ai/media/images/1750742499545258689_aeXmGbsM.jpg"  # NEW
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
    SEEDDANCE_DURATIONS = [5, 6, 7, 8, 9, 10]  # Extended duration options for both versions
    SEED_RANGE = (-1, 2147483647)
    CREATIVITY_RANGE = (-2, 2)
    GUIDANCE_SCALE_RANGE = (0.0, 1.0)
    RESOLUTIONS = ["2k", "4k", "8k"]
    OUTPUT_FORMATS = {
        'image': ["png", "jpg", "webp"],
        'video': ["mp4"]
    }
    
    # Seedream V4 specific settings
    SEEDREAM_V4_SIZES = [
        "1024*1024",
        "1024*2048", 
        "2048*1024",
        "2048*2048",
        "2048*4096",
        "4096*2048"
    ]
    
    # SeedDance V1 Pro versions and settings
    SEEDDANCE_VERSIONS = {
        "480p": "bytedance/seedance-v1-pro-i2v-480p",
        "720p": "bytedance/seedance-v1-pro-i2v-720p"
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
