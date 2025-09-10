"""
Input Validation Module for WaveSpeed AI Application

This module provides comprehensive validation functions for all user inputs,
API keys, file paths, and configuration values.
"""

import os
import re
from pathlib import Path
from typing import Optional, Tuple, List, Union
from PIL import Image

from app.constants import (
    FileFormats, ValidationRanges, SeedreamV4Sizes, 
    SeedDanceVersions, ErrorMessages, HTTPStatusCodes
)


class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass


def validate_api_key(api_key: Optional[str]) -> Tuple[bool, Optional[str]]:
    """
    Validate API key format and presence
    
    Args:
        api_key: The API key to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not api_key:
        return False, "API key is required"
    
    if not isinstance(api_key, str):
        return False, "API key must be a string"
    
    api_key = api_key.strip()
    
    if len(api_key) < 10:
        return False, "API key is too short (minimum 10 characters)"
    
    if len(api_key) > 200:
        return False, "API key is too long (maximum 200 characters)"
    
    # Basic format validation (alphanumeric and common special chars)
    if not re.match(r'^[a-zA-Z0-9_\-\.]+$', api_key):
        return False, "API key contains invalid characters"
    
    return True, None


def validate_file_path(file_path: Union[str, Path]) -> Tuple[bool, Optional[str]]:
    """
    Validate file path exists and is accessible
    
    Args:
        file_path: Path to the file to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not file_path:
        return False, "File path is required"
    
    try:
        path = Path(file_path)
        
        if not path.exists():
            return False, f"File not found: {file_path}"
        
        if not path.is_file():
            return False, f"Path is not a file: {file_path}"
        
        if not os.access(path, os.R_OK):
            return False, f"File is not readable: {file_path}"
        
        return True, None
        
    except Exception as e:
        return False, f"Invalid file path: {str(e)}"


def validate_image_file(file_path: Union[str, Path]) -> Tuple[bool, Optional[str]]:
    """
    Validate image file format and integrity
    
    Args:
        file_path: Path to the image file to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    # First validate file path
    is_valid_path, error = validate_file_path(file_path)
    if not is_valid_path:
        return False, error
    
    try:
        path = Path(file_path)
        
        # Check file extension
        if not path.suffix.lower() in [f'.{fmt}' for fmt in FileFormats.IMAGE_FORMATS]:
            return False, f"Unsupported image format. Supported formats: {', '.join(FileFormats.IMAGE_FORMATS)}"
        
        # Check file size (max 50MB)
        file_size = path.stat().st_size
        max_size = 50 * 1024 * 1024  # 50MB
        if file_size > max_size:
            return False, f"Image file too large. Maximum size: 50MB, current: {file_size / (1024*1024):.1f}MB"
        
        # Try to open with PIL to validate image integrity
        try:
            with Image.open(path) as img:
                img.verify()
        except Exception as e:
            return False, f"Invalid image file: {str(e)}"
        
        return True, None
        
    except Exception as e:
        return False, f"Error validating image file: {str(e)}"


def validate_prompt(prompt: Optional[str]) -> Tuple[bool, Optional[str]]:
    """
    Validate prompt text
    
    Args:
        prompt: The prompt text to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not prompt:
        return False, "Prompt is required"
    
    if not isinstance(prompt, str):
        return False, "Prompt must be a string"
    
    prompt = prompt.strip()
    
    if len(prompt) < 1:
        return False, "Prompt cannot be empty"
    
    if len(prompt) > 2000:
        return False, "Prompt is too long (maximum 2000 characters)"
    
    # Check for potentially harmful content (basic check)
    harmful_patterns = [
        r'<script.*?>.*?</script>',
        r'javascript:',
        r'data:text/html',
    ]
    
    for pattern in harmful_patterns:
        if re.search(pattern, prompt, re.IGNORECASE):
            return False, "Prompt contains potentially harmful content"
    
    return True, None


def validate_seed(seed: Union[int, str]) -> Tuple[bool, Optional[str]]:
    """
    Validate seed value
    
    Args:
        seed: The seed value to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        if isinstance(seed, str):
            seed = int(seed)
        
        if not isinstance(seed, int):
            return False, "Seed must be an integer"
        
        min_seed, max_seed = ValidationRanges.SEED_RANGE
        if seed < min_seed or seed > max_seed:
            return False, f"Seed must be between {min_seed} and {max_seed}"
        
        return True, None
        
    except ValueError:
        return False, "Seed must be a valid integer"


def validate_guidance_scale(guidance_scale: Union[float, str]) -> Tuple[bool, Optional[str]]:
    """
    Validate guidance scale value
    
    Args:
        guidance_scale: The guidance scale value to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        if isinstance(guidance_scale, str):
            guidance_scale = float(guidance_scale)
        
        if not isinstance(guidance_scale, (int, float)):
            return False, "Guidance scale must be a number"
        
        min_val, max_val = ValidationRanges.GUIDANCE_SCALE_RANGE
        if guidance_scale < min_val or guidance_scale > max_val:
            return False, f"Guidance scale must be between {min_val} and {max_val}"
        
        return True, None
        
    except ValueError:
        return False, "Guidance scale must be a valid number"


def validate_creativity(creativity: Union[int, str]) -> Tuple[bool, Optional[str]]:
    """
    Validate creativity value
    
    Args:
        creativity: The creativity value to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        if isinstance(creativity, str):
            creativity = int(creativity)
        
        if not isinstance(creativity, int):
            return False, "Creativity must be an integer"
        
        min_val, max_val = ValidationRanges.CREATIVITY_RANGE
        if creativity < min_val or creativity > max_val:
            return False, f"Creativity must be between {min_val} and {max_val}"
        
        return True, None
        
    except ValueError:
        return False, "Creativity must be a valid integer"


def validate_duration(duration: Union[int, str], model_type: str = "video") -> Tuple[bool, Optional[str]]:
    """
    Validate duration value based on model type
    
    Args:
        duration: The duration value to validate
        model_type: Type of model (video, seeddance)
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        if isinstance(duration, str):
            duration = int(duration)
        
        if not isinstance(duration, int):
            return False, "Duration must be an integer"
        
        if model_type == "seeddance":
            valid_durations = ValidationRanges.SEEDDANCE_DURATIONS
        else:
            valid_durations = ValidationRanges.VIDEO_DURATIONS
        
        if duration not in valid_durations:
            return False, f"Duration must be one of: {', '.join(map(str, valid_durations))}"
        
        return True, None
        
    except ValueError:
        return False, "Duration must be a valid integer"


def validate_resolution(resolution: Optional[str]) -> Tuple[bool, Optional[str]]:
    """
    Validate resolution value
    
    Args:
        resolution: The resolution value to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not resolution:
        return False, "Resolution is required"
    
    if not isinstance(resolution, str):
        return False, "Resolution must be a string"
    
    resolution = resolution.lower().strip()
    
    if resolution not in ValidationRanges.RESOLUTIONS:
        return False, f"Resolution must be one of: {', '.join(ValidationRanges.RESOLUTIONS)}"
    
    return True, None


def validate_seedream_v4_size(size: Optional[str]) -> Tuple[bool, Optional[str]]:
    """
    Validate Seedream V4 size value
    
    Args:
        size: The size value to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not size:
        return False, "Size is required"
    
    if not isinstance(size, str):
        return False, "Size must be a string"
    
    if size not in SeedreamV4Sizes.SIZES:
        return False, f"Size must be one of: {', '.join(SeedreamV4Sizes.SIZES)}"
    
    return True, None


def validate_seeddance_version(version: Optional[str]) -> Tuple[bool, Optional[str]]:
    """
    Validate SeedDance version
    
    Args:
        version: The version value to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not version:
        return False, "Version is required"
    
    if not isinstance(version, str):
        return False, "Version must be a string"
    
    if version not in SeedDanceVersions.VERSIONS:
        return False, f"Version must be one of: {', '.join(SeedDanceVersions.VERSIONS.keys())}"
    
    return True, None


def validate_output_format(format_type: Optional[str], content_type: str = "image") -> Tuple[bool, Optional[str]]:
    """
    Validate output format
    
    Args:
        format_type: The output format to validate
        content_type: Type of content (image, video)
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not format_type:
        return False, "Output format is required"
    
    if not isinstance(format_type, str):
        return False, "Output format must be a string"
    
    format_type = format_type.lower().strip()
    
    if content_type == "image":
        valid_formats = FileFormats.IMAGE_FORMATS
    elif content_type == "video":
        valid_formats = FileFormats.VIDEO_FORMATS
    else:
        return False, f"Invalid content type: {content_type}"
    
    if format_type not in valid_formats:
        return False, f"Output format must be one of: {', '.join(valid_formats)}"
    
    return True, None


def validate_http_status_code(status_code: int) -> Tuple[bool, Optional[str]]:
    """
    Validate HTTP status code and return user-friendly error message
    
    Args:
        status_code: HTTP status code to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    error_messages = {
        HTTPStatusCodes.UNAUTHORIZED: ErrorMessages.INVALID_API_KEY,
        HTTPStatusCodes.RATE_LIMIT: ErrorMessages.RATE_LIMIT_EXCEEDED,
        HTTPStatusCodes.INTERNAL_SERVER_ERROR: ErrorMessages.SERVER_ERROR,
        HTTPStatusCodes.SERVICE_UNAVAILABLE: ErrorMessages.SERVER_ERROR,
        HTTPStatusCodes.BAD_REQUEST: "Invalid request parameters. Please check your input.",
        HTTPStatusCodes.FORBIDDEN: "Access forbidden. Please check your API permissions.",
        HTTPStatusCodes.NOT_FOUND: "Resource not found. Please check the endpoint URL.",
    }
    
    if status_code == HTTPStatusCodes.OK:
        return True, None
    
    error_message = error_messages.get(status_code, ErrorMessages.UNKNOWN_ERROR)
    return False, error_message


def validate_window_size(size: str) -> Tuple[bool, Optional[str]]:
    """
    Validate window size string
    
    Args:
        size: Window size string in format "WIDTHxHEIGHT"
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not size:
        return False, "Window size is required"
    
    if not isinstance(size, str):
        return False, "Window size must be a string"
    
    # Check format: WIDTHxHEIGHT
    if not re.match(r'^\d+x\d+$', size):
        return False, "Window size must be in format 'WIDTHxHEIGHT' (e.g., '1200x900')"
    
    try:
        width, height = map(int, size.split('x'))
        
        if width < 400 or height < 300:
            return False, "Window size too small (minimum 400x300)"
        
        if width > 4000 or height > 3000:
            return False, "Window size too large (maximum 4000x3000)"
        
        return True, None
        
    except ValueError:
        return False, "Invalid window size format"


def validate_boolean(value: Union[bool, str]) -> Tuple[bool, Optional[str]]:
    """
    Validate boolean value
    
    Args:
        value: Value to validate as boolean
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if isinstance(value, bool):
        return True, None
    
    if isinstance(value, str):
        value = value.lower().strip()
        if value in ['true', 'false', '1', '0', 'yes', 'no', 'on', 'off']:
            return True, None
    
    return False, "Value must be a boolean (true/false)"


def validate_positive_number(value: Union[int, float, str], min_value: float = 0.0) -> Tuple[bool, Optional[str]]:
    """
    Validate positive number
    
    Args:
        value: Value to validate
        min_value: Minimum allowed value
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        if isinstance(value, str):
            value = float(value)
        
        if not isinstance(value, (int, float)):
            return False, "Value must be a number"
        
        if value < min_value:
            return False, f"Value must be at least {min_value}"
        
        return True, None
        
    except ValueError:
        return False, "Value must be a valid number"
