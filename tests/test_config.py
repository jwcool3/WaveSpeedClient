"""
Unit tests for configuration module
"""

import unittest
import os
import tempfile
from unittest.mock import patch

from app.config_enhanced import (
    APIConfig, UIConfig, FileConfig, AutoSaveConfig,
    PrivacyConfig, ValidationConfig, AppConfig,
    get_config, reload_config
)
from core.exceptions import ConfigurationError


class TestAPIConfig(unittest.TestCase):
    """Test cases for APIConfig"""
    
    def test_valid_api_config(self):
        """Test valid API configuration"""
        config = APIConfig(
            api_key="sk-1234567890abcdef",
            base_url="https://api.example.com",
            timeout=300
        )
        self.assertEqual(config.api_key, "sk-1234567890abcdef")
        self.assertEqual(config.base_url, "https://api.example.com")
        self.assertEqual(config.timeout, 300)
    
    def test_invalid_api_key(self):
        """Test invalid API key raises ConfigurationError"""
        with self.assertRaises(ConfigurationError) as context:
            APIConfig(api_key="short")
        
        self.assertIn("Invalid API key", str(context.exception))
        self.assertEqual(context.exception.config_key, "api_key")
    
    def test_invalid_ai_advisor_provider(self):
        """Test invalid AI advisor provider raises ConfigurationError"""
        with self.assertRaises(ConfigurationError) as context:
            APIConfig(ai_advisor_provider="invalid")
        
        self.assertIn("AI advisor provider must be 'claude' or 'openai'", str(context.exception))
        self.assertEqual(context.exception.config_key, "ai_advisor_provider")


class TestUIConfig(unittest.TestCase):
    """Test cases for UIConfig"""
    
    def test_valid_ui_config(self):
        """Test valid UI configuration"""
        config = UIConfig(
            window_size="1200x900",
            window_min_size=(800, 600),
            max_image_size=(350, 250)
        )
        self.assertEqual(config.window_size, "1200x900")
        self.assertEqual(config.window_min_size, (800, 600))
        self.assertEqual(config.max_image_size, (350, 250))
    
    def test_invalid_window_size(self):
        """Test invalid window size raises ConfigurationError"""
        with self.assertRaises(ConfigurationError) as context:
            UIConfig(window_size="invalid")
        
        self.assertIn("Invalid window size", str(context.exception))
        self.assertEqual(context.exception.config_key, "window_size")
    
    def test_invalid_window_min_size(self):
        """Test invalid window min size raises ConfigurationError"""
        with self.assertRaises(ConfigurationError) as context:
            UIConfig(window_min_size=(800,))  # Only one value
        
        self.assertIn("Window min size must be a tuple of 2 integers", str(context.exception))
        self.assertEqual(context.exception.config_key, "window_min_size")


class TestFileConfig(unittest.TestCase):
    """Test cases for FileConfig"""
    
    def test_valid_file_config(self):
        """Test valid file configuration"""
        config = FileConfig(
            max_file_size=50 * 1024 * 1024,
            temp_prefix="temp_"
        )
        self.assertEqual(config.max_file_size, 50 * 1024 * 1024)
        self.assertEqual(config.temp_prefix, "temp_")
    
    def test_invalid_max_file_size(self):
        """Test invalid max file size raises ConfigurationError"""
        with self.assertRaises(ConfigurationError) as context:
            FileConfig(max_file_size=-1)
        
        self.assertIn("Max file size must be positive", str(context.exception))
        self.assertEqual(context.exception.config_key, "max_file_size")


class TestAutoSaveConfig(unittest.TestCase):
    """Test cases for AutoSaveConfig"""
    
    def test_valid_auto_save_config(self):
        """Test valid auto-save configuration"""
        config = AutoSaveConfig(
            enabled=True,
            base_folder="WaveSpeed_Results"
        )
        self.assertTrue(config.enabled)
        self.assertEqual(config.base_folder, "WaveSpeed_Results")
    
    def test_invalid_enabled_type(self):
        """Test invalid enabled type raises ConfigurationError"""
        with self.assertRaises(ConfigurationError) as context:
            AutoSaveConfig(enabled="yes")  # Should be boolean
        
        self.assertIn("Auto-save enabled must be a boolean", str(context.exception))
        self.assertEqual(context.exception.config_key, "enabled")


class TestPrivacyConfig(unittest.TestCase):
    """Test cases for PrivacyConfig"""
    
    def test_valid_privacy_config(self):
        """Test valid privacy configuration"""
        config = PrivacyConfig(
            mode="high",
            temp_upload_expire_hours=1
        )
        self.assertEqual(config.mode, "high")
        self.assertEqual(config.temp_upload_expire_hours, 1)
    
    def test_invalid_privacy_mode(self):
        """Test invalid privacy mode raises ConfigurationError"""
        with self.assertRaises(ConfigurationError) as context:
            PrivacyConfig(mode="invalid")
        
        self.assertIn("Privacy mode must be one of: high, medium, low", str(context.exception))
        self.assertEqual(context.exception.config_key, "mode")
    
    def test_invalid_expire_hours(self):
        """Test invalid expire hours raises ConfigurationError"""
        with self.assertRaises(ConfigurationError) as context:
            PrivacyConfig(temp_upload_expire_hours=0)
        
        self.assertIn("Temp upload expire hours must be positive", str(context.exception))
        self.assertEqual(context.exception.config_key, "temp_upload_expire_hours")


class TestAppConfig(unittest.TestCase):
    """Test cases for AppConfig"""
    
    def test_default_config(self):
        """Test default configuration creation"""
        config = AppConfig()
        self.assertIsInstance(config.api, APIConfig)
        self.assertIsInstance(config.ui, UIConfig)
        self.assertIsInstance(config.file, FileConfig)
        self.assertIsInstance(config.auto_save, AutoSaveConfig)
        self.assertIsInstance(config.privacy, PrivacyConfig)
        self.assertIsInstance(config.validation, ValidationConfig)
    
    def test_endpoints_initialization(self):
        """Test endpoints are properly initialized"""
        config = AppConfig()
        self.assertIn('image_edit', config.endpoints)
        self.assertIn('balance', config.endpoints)
        self.assertIn('result_poll', config.endpoints)
    
    @patch.dict(os.environ, {
        'WAVESPEED_API_KEY': 'sk-test123456789',
        'CLAUDE_API_KEY': 'claude-test123456789',
        'AI_ADVISOR_PROVIDER': 'claude'
    })
    def test_from_env(self):
        """Test configuration creation from environment variables"""
        config = AppConfig.from_env()
        self.assertEqual(config.api.api_key, 'sk-test123456789')
        self.assertEqual(config.api.claude_api_key, 'claude-test123456789')
        self.assertEqual(config.api.ai_advisor_provider, 'claude')
    
    def test_validate_without_api_key(self):
        """Test validation without API key"""
        config = AppConfig()
        errors = config.validate()
        self.assertIn("WAVESPEED_API_KEY not found in environment variables", errors)
    
    def test_get_temp_filename(self):
        """Test temporary filename generation"""
        config = AppConfig()
        filename = config.get_temp_filename("test", ".png")
        self.assertEqual(filename, "temp_test.png")
    
    def test_is_supported_format(self):
        """Test supported format checking"""
        config = AppConfig()
        self.assertTrue(config.is_supported_format("image.png"))
        self.assertTrue(config.is_supported_format("image.JPG"))
        self.assertFalse(config.is_supported_format("image.txt"))
    
    def test_get_auto_save_folder(self):
        """Test auto-save folder retrieval"""
        config = AppConfig()
        folder = config.get_auto_save_folder("image_editor")
        self.assertEqual(folder, "Nano_Banana_Editor")
        
        # Test with unknown model type
        folder = config.get_auto_save_folder("unknown")
        self.assertEqual(folder, "Other")
    
    def test_get_sample_url(self):
        """Test sample URL retrieval"""
        config = AppConfig()
        url = config.get_sample_url("upscaler")
        self.assertIsNotNone(url)
        self.assertTrue(url.startswith("https://"))
        
        # Test with unknown model type
        url = config.get_sample_url("unknown")
        self.assertIsNone(url)
    
    def test_to_dict(self):
        """Test configuration to dictionary conversion"""
        config = AppConfig()
        config_dict = config.to_dict()
        
        self.assertIn('api', config_dict)
        self.assertIn('ui', config_dict)
        self.assertIn('file', config_dict)
        self.assertIn('auto_save', config_dict)
        self.assertIn('privacy', config_dict)
        
        # Check some specific values
        self.assertEqual(config_dict['api']['base_url'], config.api.base_url)
        self.assertEqual(config_dict['ui']['window_size'], config.ui.window_size)


class TestGlobalConfig(unittest.TestCase):
    """Test cases for global configuration functions"""
    
    def test_get_config(self):
        """Test getting global configuration"""
        config = get_config()
        self.assertIsInstance(config, AppConfig)
    
    @patch.dict(os.environ, {
        'WAVESPEED_API_KEY': 'sk-test123456789',
        'AI_ADVISOR_PROVIDER': 'openai'
    })
    def test_reload_config(self):
        """Test reloading configuration from environment"""
        config = reload_config()
        self.assertIsInstance(config, AppConfig)
        self.assertEqual(config.api.api_key, 'sk-test123456789')
        self.assertEqual(config.api.ai_advisor_provider, 'openai')


if __name__ == '__main__':
    unittest.main()
