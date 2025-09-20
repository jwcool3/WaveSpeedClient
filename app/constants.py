"""
Constants and Enums for WaveSpeed AI Application

This module centralizes all constant values, model names, and configuration constants.
"""

from enum import Enum
from typing import List, Dict, Tuple


class ModelNames:
    """AI Model identifiers"""
    NANO_BANANA = "nano-banana"
    SEEDREAM_V4 = "seedream-v4"
    UPSCALER = "upscaler"
    WAN_22 = "wan-2.2"
    SEEDDANCE = "seeddance-pro"
    SEEDEDIT = "seededit-v3"


class FileFormats:
    """Supported file formats"""
    PNG = "png"
    JPEG = "jpeg"
    JPG = "jpg"
    WEBP = "webp"
    GIF = "gif"
    BMP = "bmp"
    MP4 = "mp4"
    
    # Image formats
    IMAGE_FORMATS = [PNG, JPEG, JPG, WEBP, GIF, BMP]
    
    # Video formats
    VIDEO_FORMATS = [MP4]


class PrivacyModes:
    """Privacy mode levels"""
    HIGH = "high"      # Base64 data URLs only (most private)
    MEDIUM = "medium"  # Temporary hosting with auto-delete
    LOW = "low"        # Use sample URLs (demo mode)


class TaskStatus:
    """Task status values"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class APIEndpoints:
    """API endpoint paths"""
    IMAGE_EDIT = "image_edit"
    SEEDEDIT = "seededit"
    SEEDREAM_V4 = "seedream_v4"
    IMAGE_UPSCALE = "image_upscale"
    IMAGE_TO_VIDEO = "image_to_video"
    SEEDDANCE = "seeddance"
    SEEDDANCE_480P = "seeddance_480p"
    SEEDDANCE_720P = "seeddance_720p"
    RESULT_POLL = "result_poll"
    BALANCE = "balance"


class UIColors:
    """UI color constants"""
    SUCCESS = 'green'
    ERROR = 'red'
    WARNING = 'orange'
    INFO = 'blue'
    BACKGROUND = '#f0f0f0'
    DROP_ZONE = '#f8f8f8'
    DROP_HOVER = '#f0f8ff'
    DROP_ACTIVE = '#e8f4f8'


class ValidationRanges:
    """Validation range constants"""
    VIDEO_DURATIONS = [5, 8]
    SEEDDANCE_DURATIONS = [5, 6, 7, 8, 9, 10]
    SEED_RANGE = (-1, 2147483647)
    CREATIVITY_RANGE = (-2, 2)
    GUIDANCE_SCALE_RANGE = (0.0, 1.0)
    RESOLUTIONS = ["2k", "4k", "8k"]


class SeedreamV4Sizes:
    """Seedream V4 supported sizes"""
    SIZES = [
        "1024*1024",
        "1024*2048", 
        "2048*1024",
        "2048*2048",
        "2048*4096",
        "4096*2048"
    ]


class SeedDanceVersions:
    """SeedDance version identifiers"""
    V480P = "480p"
    V720P = "720p"
    
    VERSIONS = {
        V480P: "bytedance/seedance-v1-pro-i2v-480p",
        V720P: "bytedance/seedance-v1-pro-i2v-720p"
    }


class ErrorMessages:
    """Standardized error messages"""
    INVALID_API_KEY = "Invalid API key. Please check your .env file."
    RATE_LIMIT_EXCEEDED = "Rate limit exceeded. Please wait and try again."
    SERVER_ERROR = "Server error. Please try again later."
    NETWORK_ERROR = "Network error. Please check your internet connection."
    TIMEOUT_ERROR = "Request timed out. Please try again."
    INVALID_FILE_FORMAT = "Invalid file format. Please use a supported image format."
    FILE_NOT_FOUND = "File not found. Please check the file path."
    INSUFFICIENT_BALANCE = "Insufficient account balance. Please add funds."
    UNKNOWN_ERROR = "An unexpected error occurred. Please try again."


class HTTPStatusCodes:
    """HTTP status code constants"""
    OK = 200
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    RATE_LIMIT = 429
    INTERNAL_SERVER_ERROR = 500
    SERVICE_UNAVAILABLE = 503


class DefaultValues:
    """Default configuration values"""
    WINDOW_SIZE = "1200x900"
    WINDOW_MIN_SIZE = (800, 600)
    WINDOW_TITLE = "WaveSpeed AI - Complete Creative Suite"
    MAX_IMAGE_SIZE = (350, 250)
    DEFAULT_POLL_INTERVAL = 1.0
    VIDEO_POLL_INTERVAL = 2.0
    MAX_RETRIES = 3
    TIMEOUT = 300  # 5 minutes
    TEMP_UPLOAD_EXPIRE_HOURS = 1


class AutoSaveFolders:
    """Auto-save folder mappings"""
    FOLDERS = {
        'image_editor': 'Nano_Banana_Editor',
        'seededit': 'SeedEdit',
        'seedream_v4': 'Seedream_V4',
        'upscaler': 'Image_Upscaler',
        'video': 'Wan_2.2',
        'seeddance': 'SeedDance_Pro'
    }


class OutputFormats:
    """Output format options"""
    IMAGE_FORMATS = ["png", "jpg", "webp"]
    VIDEO_FORMATS = ["mp4"]


# Type aliases for better code documentation
ApiKey = str
RequestId = str
ImagePath = str
VideoPath = str
Prompt = str
Balance = float
Duration = float
Seed = int
GuidanceScale = float
Creativity = int
Resolution = str
OutputFormat = str
