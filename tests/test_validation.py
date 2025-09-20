"""
Unit tests for validation module
"""

import unittest
import tempfile
import os
from pathlib import Path
from PIL import Image

from core.validation import (
    validate_api_key, validate_file_path, validate_image_file,
    validate_prompt, validate_seed, validate_guidance_scale,
    validate_creativity, validate_duration, validate_resolution,
    validate_output_format, validate_http_status_code,
    ValidationError
)


class TestValidation(unittest.TestCase):
    """Test cases for validation functions"""
    
    def test_validate_api_key_valid(self):
        """Test valid API key validation"""
        valid_keys = [
            "sk-1234567890abcdef",
            "test_api_key_123",
            "valid-key-with-dashes",
            "key_with_underscores_123"
        ]
        
        for key in valid_keys:
            is_valid, error = validate_api_key(key)
            self.assertTrue(is_valid, f"API key '{key}' should be valid")
            self.assertIsNone(error)
    
    def test_validate_api_key_invalid(self):
        """Test invalid API key validation"""
        invalid_cases = [
            (None, "API key is required"),
            ("", "API key is required"),
            ("short", "API key is too short"),
            ("a" * 201, "API key is too long"),
            ("invalid@key", "API key contains invalid characters"),
            ("key with spaces", "API key contains invalid characters")
        ]
        
        for key, expected_error in invalid_cases:
            is_valid, error = validate_api_key(key)
            self.assertFalse(is_valid, f"API key '{key}' should be invalid")
            self.assertIn(expected_error, error)
    
    def test_validate_prompt_valid(self):
        """Test valid prompt validation"""
        valid_prompts = [
            "A beautiful landscape",
            "Change the color to red",
            "Make it more artistic",
            "A" * 1000  # Long but valid prompt
        ]
        
        for prompt in valid_prompts:
            is_valid, error = validate_prompt(prompt)
            self.assertTrue(is_valid, f"Prompt '{prompt[:50]}...' should be valid")
            self.assertIsNone(error)
    
    def test_validate_prompt_invalid(self):
        """Test invalid prompt validation"""
        invalid_cases = [
            (None, "Prompt is required"),
            ("", "Prompt is required"),
            ("   ", "Prompt cannot be empty"),
            ("A" * 2001, "Prompt is too long"),
            ("<script>alert('xss')</script>", "potentially harmful content")
        ]
        
        for prompt, expected_error in invalid_cases:
            is_valid, error = validate_prompt(prompt)
            self.assertFalse(is_valid, f"Prompt '{prompt}' should be invalid")
            self.assertIn(expected_error, error)
    
    def test_validate_seed_valid(self):
        """Test valid seed validation"""
        valid_seeds = [-1, 0, 1, 100, 2147483647]
        
        for seed in valid_seeds:
            is_valid, error = validate_seed(seed)
            self.assertTrue(is_valid, f"Seed {seed} should be valid")
            self.assertIsNone(error)
    
    def test_validate_seed_invalid(self):
        """Test invalid seed validation"""
        invalid_cases = [
            (-2, "Seed must be between -1 and 2147483647"),
            (2147483648, "Seed must be between -1 and 2147483647"),
            ("invalid", "Seed must be a valid integer"),
            (None, "Seed must be an integer")
        ]
        
        for seed, expected_error in invalid_cases:
            is_valid, error = validate_seed(seed)
            self.assertFalse(is_valid, f"Seed {seed} should be invalid")
            self.assertIn(expected_error, error)
    
    def test_validate_guidance_scale_valid(self):
        """Test valid guidance scale validation"""
        valid_scales = [0.0, 0.5, 1.0, 0.25, 0.75]
        
        for scale in valid_scales:
            is_valid, error = validate_guidance_scale(scale)
            self.assertTrue(is_valid, f"Guidance scale {scale} should be valid")
            self.assertIsNone(error)
    
    def test_validate_guidance_scale_invalid(self):
        """Test invalid guidance scale validation"""
        invalid_cases = [
            (-0.1, "Guidance scale must be between 0.0 and 1.0"),
            (1.1, "Guidance scale must be between 0.0 and 1.0"),
            ("invalid", "Guidance scale must be a valid number"),
            (None, "Guidance scale must be a number")
        ]
        
        for scale, expected_error in invalid_cases:
            is_valid, error = validate_guidance_scale(scale)
            self.assertFalse(is_valid, f"Guidance scale {scale} should be invalid")
            self.assertIn(expected_error, error)
    
    def test_validate_creativity_valid(self):
        """Test valid creativity validation"""
        valid_creativities = [-2, -1, 0, 1, 2]
        
        for creativity in valid_creativities:
            is_valid, error = validate_creativity(creativity)
            self.assertTrue(is_valid, f"Creativity {creativity} should be valid")
            self.assertIsNone(error)
    
    def test_validate_creativity_invalid(self):
        """Test invalid creativity validation"""
        invalid_cases = [
            (-3, "Creativity must be between -2 and 2"),
            (3, "Creativity must be between -2 and 2"),
            ("invalid", "Creativity must be a valid integer"),
            (None, "Creativity must be an integer")
        ]
        
        for creativity, expected_error in invalid_cases:
            is_valid, error = validate_creativity(creativity)
            self.assertFalse(is_valid, f"Creativity {creativity} should be invalid")
            self.assertIn(expected_error, error)
    
    def test_validate_duration_valid(self):
        """Test valid duration validation"""
        valid_durations = [5, 8]  # Video durations
        
        for duration in valid_durations:
            is_valid, error = validate_duration(duration, "video")
            self.assertTrue(is_valid, f"Duration {duration} should be valid for video")
            self.assertIsNone(error)
        
        # SeedDance durations
        seeddance_durations = [5, 6, 7, 8, 9, 10]
        for duration in seeddance_durations:
            is_valid, error = validate_duration(duration, "seeddance")
            self.assertTrue(is_valid, f"Duration {duration} should be valid for seeddance")
            self.assertIsNone(error)
    
    def test_validate_duration_invalid(self):
        """Test invalid duration validation"""
        invalid_cases = [
            (3, "video", "Duration must be one of: 5, 8"),
            (10, "video", "Duration must be one of: 5, 8"),
            (3, "seeddance", "Duration must be one of: 5, 6, 7, 8, 9, 10"),
            ("invalid", "video", "Duration must be a valid integer")
        ]
        
        for duration, model_type, expected_error in invalid_cases:
            is_valid, error = validate_duration(duration, model_type)
            self.assertFalse(is_valid, f"Duration {duration} should be invalid for {model_type}")
            self.assertIn(expected_error, error)
    
    def test_validate_resolution_valid(self):
        """Test valid resolution validation"""
        valid_resolutions = ["2k", "4k", "8k"]
        
        for resolution in valid_resolutions:
            is_valid, error = validate_resolution(resolution)
            self.assertTrue(is_valid, f"Resolution {resolution} should be valid")
            self.assertIsNone(error)
    
    def test_validate_resolution_invalid(self):
        """Test invalid resolution validation"""
        invalid_cases = [
            (None, "Resolution is required"),
            ("", "Resolution is required"),
            ("1080p", "Resolution must be one of: 2k, 4k, 8k"),
            ("invalid", "Resolution must be one of: 2k, 4k, 8k")
        ]
        
        for resolution, expected_error in invalid_cases:
            is_valid, error = validate_resolution(resolution)
            self.assertFalse(is_valid, f"Resolution {resolution} should be invalid")
            self.assertIn(expected_error, error)
    
    def test_validate_output_format_valid(self):
        """Test valid output format validation"""
        valid_image_formats = ["png", "jpg", "webp"]
        valid_video_formats = ["mp4"]
        
        for format_type in valid_image_formats:
            is_valid, error = validate_output_format(format_type, "image")
            self.assertTrue(is_valid, f"Format {format_type} should be valid for image")
            self.assertIsNone(error)
        
        for format_type in valid_video_formats:
            is_valid, error = validate_output_format(format_type, "video")
            self.assertTrue(is_valid, f"Format {format_type} should be valid for video")
            self.assertIsNone(error)
    
    def test_validate_output_format_invalid(self):
        """Test invalid output format validation"""
        invalid_cases = [
            (None, "image", "Output format is required"),
            ("", "image", "Output format is required"),
            ("gif", "image", "Output format must be one of: png, jpg, webp"),
            ("avi", "video", "Output format must be one of: mp4"),
            ("png", "invalid", "Invalid content type: invalid")
        ]
        
        for format_type, content_type, expected_error in invalid_cases:
            is_valid, error = validate_output_format(format_type, content_type)
            self.assertFalse(is_valid, f"Format {format_type} should be invalid for {content_type}")
            self.assertIn(expected_error, error)
    
    def test_validate_http_status_code(self):
        """Test HTTP status code validation"""
        # Valid status code
        is_valid, error = validate_http_status_code(200)
        self.assertTrue(is_valid)
        self.assertIsNone(error)
        
        # Invalid status codes with error messages
        invalid_cases = [
            (401, "Invalid API key"),
            (429, "Rate limit exceeded"),
            (500, "Server error"),
            (404, "Resource not found")
        ]
        
        for status_code, expected_error in invalid_cases:
            is_valid, error = validate_http_status_code(status_code)
            self.assertFalse(is_valid, f"Status code {status_code} should be invalid")
            self.assertIn(expected_error, error)
    
    def test_validate_file_path_valid(self):
        """Test valid file path validation"""
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_path = tmp_file.name
            tmp_file.write(b"test content")
        
        try:
            is_valid, error = validate_file_path(tmp_path)
            self.assertTrue(is_valid, f"File path {tmp_path} should be valid")
            self.assertIsNone(error)
        finally:
            os.unlink(tmp_path)
    
    def test_validate_file_path_invalid(self):
        """Test invalid file path validation"""
        invalid_cases = [
            (None, "File path is required"),
            ("", "File path is required"),
            ("/nonexistent/file.txt", "File not found"),
            (".", "Path is not a file")  # Current directory
        ]
        
        for file_path, expected_error in invalid_cases:
            is_valid, error = validate_file_path(file_path)
            self.assertFalse(is_valid, f"File path {file_path} should be invalid")
            self.assertIn(expected_error, error)
    
    def test_validate_image_file_valid(self):
        """Test valid image file validation"""
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
            # Create a simple PNG image
            img = Image.new('RGB', (100, 100), color='red')
            img.save(tmp_file.name, 'PNG')
            tmp_path = tmp_file.name
        
        try:
            is_valid, error = validate_image_file(tmp_path)
            self.assertTrue(is_valid, f"Image file {tmp_path} should be valid")
            self.assertIsNone(error)
        finally:
            os.unlink(tmp_path)
    
    def test_validate_image_file_invalid(self):
        """Test invalid image file validation"""
        # Test with non-existent file
        is_valid, error = validate_image_file("/nonexistent/image.png")
        self.assertFalse(is_valid)
        self.assertIn("File not found", error)
        
        # Test with unsupported format
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as tmp_file:
            tmp_file.write(b"not an image")
            tmp_path = tmp_file.name
        
        try:
            is_valid, error = validate_image_file(tmp_path)
            self.assertFalse(is_valid, f"Text file {tmp_path} should be invalid as image")
            self.assertIn("Unsupported image format", error)
        finally:
            os.unlink(tmp_path)


if __name__ == '__main__':
    unittest.main()
