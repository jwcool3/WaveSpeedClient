"""
Enhanced Configuration Management for WaveSpeed AI Application

This module provides an improved configuration system using dataclasses
with validation and type safety.
"""

import os
from dataclasses import dataclass, field
from typing import Optional, Dict, List, Tuple, Any
from pathlib import Path
from dotenv import load_dotenv

from app.constants import (
    ModelNames, FileFormats, PrivacyModes, ValidationRanges,
    SeedreamV4Sizes, SeedDanceVersions, UIColors, DefaultValues,
    AutoSaveFolders, OutputFormats, HTTPStatusCodes
)
from core.validation import (
    validate_api_key, validate_window_size, validate_boolean,
    validate_positive_number, ValidationError
)
from core.exceptions import ConfigurationError

# Load environment variables
load_dotenv()


@dataclass
class APIConfig:
    """API configuration settings"""
    api_key: Optional[str] = None
    base_url: str = "https://api.wavespeed.ai/api/v3"
    timeout: int = 300  # 5 minutes
    max_retries: int = 3
    poll_interval: float = 1.0
    video_poll_interval: float = 2.0
    
    # AI Prompt Advisor
    claude_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    ai_advisor_provider: str = "claude"
    
    def __post_init__(self):
        """Validate API configuration after initialization"""
        if self.api_key:
            is_valid, error = validate_api_key(self.api_key)
            if not is_valid:
                raise ConfigurationError(f"Invalid API key: {error}", "api_key")
        
        if self.claude_api_key:
            is_valid, error = validate_api_key(self.claude_api_key)
            if not is_valid:
                raise ConfigurationError(f"Invalid Claude API key: {error}", "claude_api_key")
        
        if self.openai_api_key:
            is_valid, error = validate_api_key(self.openai_api_key)
            if not is_valid:
                raise ConfigurationError(f"Invalid OpenAI API key: {error}", "openai_api_key")
        
        if self.ai_advisor_provider not in ["claude", "openai"]:
            raise ConfigurationError("AI advisor provider must be 'claude' or 'openai'", "ai_advisor_provider")


@dataclass
class UIConfig:
    """UI configuration settings"""
    window_size: str = "1200x900"
    window_min_size: Tuple[int, int] = (800, 600)
    window_title: str = "WaveSpeed AI - Complete Creative Suite"
    max_image_size: Tuple[int, int] = (350, 250)
    colors: Dict[str, str] = field(default_factory=lambda: {
        'success': UIColors.SUCCESS,
        'error': UIColors.ERROR,
        'warning': UIColors.WARNING,
        'info': UIColors.INFO,
        'background': UIColors.BACKGROUND,
        'drop_zone': UIColors.DROP_ZONE,
        'drop_hover': UIColors.DROP_HOVER,
        'drop_active': UIColors.DROP_ACTIVE
    })
    
    def __post_init__(self):
        """Validate UI configuration after initialization"""
        is_valid, error = validate_window_size(self.window_size)
        if not is_valid:
            raise ConfigurationError(f"Invalid window size: {error}", "window_size")
        
        if len(self.window_min_size) != 2:
            raise ConfigurationError("Window min size must be a tuple of 2 integers", "window_min_size")
        
        if len(self.max_image_size) != 2:
            raise ConfigurationError("Max image size must be a tuple of 2 integers", "max_image_size")


@dataclass
class FileConfig:
    """File handling configuration"""
    supported_formats: List[str] = field(default_factory=lambda: [f'.{fmt}' for fmt in FileFormats.IMAGE_FORMATS])
    max_file_size: int = 50 * 1024 * 1024  # 50MB
    temp_prefix: str = "temp_"
    prompts_file: str = "saved_prompts.json"
    
    def __post_init__(self):
        """Validate file configuration after initialization"""
        if self.max_file_size <= 0:
            raise ConfigurationError("Max file size must be positive", "max_file_size")


@dataclass
class AutoSaveConfig:
    """Auto-save configuration"""
    enabled: bool = True
    base_folder: str = "WaveSpeed_Results"
    subfolders: Dict[str, str] = field(default_factory=lambda: AutoSaveFolders.FOLDERS.copy())
    
    def __post_init__(self):
        """Validate auto-save configuration after initialization"""
        if not isinstance(self.enabled, bool):
            raise ConfigurationError("Auto-save enabled must be a boolean", "enabled")


@dataclass
class PrivacyConfig:
    """Privacy and upload configuration"""
    mode: str = PrivacyModes.MEDIUM
    temp_upload_expire_hours: int = 1
    
    def __post_init__(self):
        """Validate privacy configuration after initialization"""
        if self.mode not in [PrivacyModes.HIGH, PrivacyModes.MEDIUM, PrivacyModes.LOW]:
            raise ConfigurationError(f"Privacy mode must be one of: {PrivacyModes.HIGH}, {PrivacyModes.MEDIUM}, {PrivacyModes.LOW}", "mode")
        
        if self.temp_upload_expire_hours <= 0:
            raise ConfigurationError("Temp upload expire hours must be positive", "temp_upload_expire_hours")


@dataclass
class ValidationConfig:
    """Validation configuration"""
    video_durations: List[int] = field(default_factory=lambda: ValidationRanges.VIDEO_DURATIONS.copy())
    seeddance_durations: List[int] = field(default_factory=lambda: ValidationRanges.SEEDDANCE_DURATIONS.copy())
    seed_range: Tuple[int, int] = ValidationRanges.SEED_RANGE
    creativity_range: Tuple[int, int] = ValidationRanges.CREATIVITY_RANGE
    guidance_scale_range: Tuple[float, float] = ValidationRanges.GUIDANCE_SCALE_RANGE
    resolutions: List[str] = field(default_factory=lambda: ValidationRanges.RESOLUTIONS.copy())
    seedream_v4_sizes: List[str] = field(default_factory=lambda: SeedreamV4Sizes.SIZES.copy())
    seeddance_versions: Dict[str, str] = field(default_factory=lambda: SeedDanceVersions.VERSIONS.copy())
    output_formats: Dict[str, List[str]] = field(default_factory=lambda: {
        'image': OutputFormats.IMAGE_FORMATS.copy(),
        'video': OutputFormats.VIDEO_FORMATS.copy()
    })


@dataclass
class SampleURLsConfig:
    """Sample URLs for demonstration mode"""
    urls: Dict[str, str] = field(default_factory=lambda: {
        'upscaler': "https://d1q70pf5vjeyhc.cloudfront.net/media/6af332dfb8b245f4bd44fc6389f5a86a/images/1756969345097954105_vYnmieb7.jpg",
        'video': "https://d1q70pf5vjeyhc.cloudfront.net/media/6af332dfb8b245f4bd44fc6389f5a86a/images/1756971220323861267_eULQTVWW.png",
        'seededit': "https://d1q70pf5vjeyhc.cloudfront.net/media/6af332dfb8b245f4bd44fc6389f5a86a/images/1756972920861221095_bqH0XVRO.png",
        'seedream_v4': "https://d1q70pf5vjeyhc.cloudfront.net/media/6af332dfb8b245f4bd44fc6389f5a86a/images/1756972920861221095_bqH0XVRO.png",
        'seeddance': "https://d1q70pf5vjeyhc.cloudfront.net/media/6af332dfb8b245f4bd44fc6389f5a86a/images/1756972742227172839_EZxtqmie.png",
        'seeddance_480p': "https://d1q70pf5vjeyhc.cloudfront.net/media/6af332dfb8b245f4bd44fc6389f5a86a/images/1756972742227172839_EZxtqmie.png",
        'seeddance_720p': "https://d3gnftk2yhz9lr.wavespeed.ai/media/images/1750742499545258689_aeXmGbsM.jpg"
    })


@dataclass
class AppConfig:
    """Main application configuration"""
    api: APIConfig = field(default_factory=APIConfig)
    ui: UIConfig = field(default_factory=UIConfig)
    file: FileConfig = field(default_factory=FileConfig)
    auto_save: AutoSaveConfig = field(default_factory=AutoSaveConfig)
    privacy: PrivacyConfig = field(default_factory=PrivacyConfig)
    validation: ValidationConfig = field(default_factory=ValidationConfig)
    sample_urls: SampleURLsConfig = field(default_factory=SampleURLsConfig)
    
    # API Endpoints
    endpoints: Dict[str, str] = field(default_factory=lambda: {})
    
    def __post_init__(self):
        """Initialize endpoints after configuration is created"""
        if not self.endpoints:
            self.endpoints = {
                'image_edit': f"{self.api.base_url}/google/nano-banana/edit",
                'seededit': f"{self.api.base_url}/bytedance/seededit-v3",
                'seedream_v4': f"{self.api.base_url}/bytedance/seedream-v4/edit",
                'image_upscale': f"{self.api.base_url}/wavespeed-ai/image-upscaler",
                'image_to_video': f"{self.api.base_url}/wavespeed-ai/wan-2.2/i2v-480p",
                'seeddance': f"{self.api.base_url}/bytedance/seedance-v1-pro-i2v-480p",
                'seeddance_480p': f"{self.api.base_url}/bytedance/seedance-v1-pro-i2v-480p",
                'seeddance_720p': f"{self.api.base_url}/bytedance/seedance-v1-pro-i2v-720p",
                'result_poll': f"{self.api.base_url}/predictions/{{request_id}}/result",
                'balance': f"{self.api.base_url}/balance"
            }
    
    @classmethod
    def from_env(cls) -> 'AppConfig':
        """Create configuration from environment variables"""
        return cls(
            api=APIConfig(
                api_key=os.getenv("WAVESPEED_API_KEY"),
                claude_api_key=os.getenv("CLAUDE_API_KEY"),
                openai_api_key=os.getenv("OPENAI_API_KEY"),
                ai_advisor_provider=os.getenv("AI_ADVISOR_PROVIDER", "claude")
            )
        )
    
    def validate(self) -> List[str]:
        """Validate entire configuration and return list of errors"""
        errors = []
        
        try:
            # Validate API configuration
            if not self.api.api_key:
                errors.append("WAVESPEED_API_KEY not found in environment variables")
        except ConfigurationError as e:
            errors.append(str(e))
        
        return errors
    
    def get_temp_filename(self, prefix: str = "", suffix: str = ".png") -> str:
        """Generate temporary filename"""
        return f"{self.file.temp_prefix}{prefix}{suffix}"
    
    def is_supported_format(self, filename: str) -> bool:
        """Check if file format is supported"""
        return filename.lower().endswith(tuple(self.file.supported_formats))
    
    def get_auto_save_folder(self, model_type: str) -> str:
        """Get auto-save folder for model type"""
        return self.auto_save.subfolders.get(model_type, "Other")
    
    def get_sample_url(self, model_type: str) -> Optional[str]:
        """Get sample URL for model type"""
        return self.sample_urls.urls.get(model_type)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            'api': {
                'base_url': self.api.base_url,
                'timeout': self.api.timeout,
                'max_retries': self.api.max_retries,
                'poll_interval': self.api.poll_interval,
                'video_poll_interval': self.api.video_poll_interval,
                'ai_advisor_provider': self.api.ai_advisor_provider
            },
            'ui': {
                'window_size': self.ui.window_size,
                'window_min_size': self.ui.window_min_size,
                'window_title': self.ui.window_title,
                'max_image_size': self.ui.max_image_size
            },
            'file': {
                'supported_formats': self.file.supported_formats,
                'max_file_size': self.file.max_file_size,
                'temp_prefix': self.file.temp_prefix,
                'prompts_file': self.file.prompts_file
            },
            'auto_save': {
                'enabled': self.auto_save.enabled,
                'base_folder': self.auto_save.base_folder,
                'subfolders': self.auto_save.subfolders
            },
            'privacy': {
                'mode': self.privacy.mode,
                'temp_upload_expire_hours': self.privacy.temp_upload_expire_hours
            }
        }


# Global configuration instance
config = AppConfig.from_env()


def get_config() -> AppConfig:
    """Get the global configuration instance"""
    return config


def reload_config() -> AppConfig:
    """Reload configuration from environment variables"""
    global config
    config = AppConfig.from_env()
    return config
