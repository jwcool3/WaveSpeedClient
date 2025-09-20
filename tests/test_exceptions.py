"""
Unit tests for custom exceptions module
"""

import unittest
from unittest.mock import Mock

from core.exceptions import (
    WaveSpeedAIError, APIError, AuthenticationError, RateLimitError,
    InsufficientBalanceError, ValidationError, FileError, ImageProcessingError,
    VideoProcessingError, ConfigurationError, NetworkError, TimeoutError,
    TaskError, TaskFailedError, TaskTimeoutError, UIError, ResourceError,
    DependencyError, handle_api_error, handle_validation_error,
    handle_file_error, handle_network_error, handle_timeout_error
)


class TestWaveSpeedAIError(unittest.TestCase):
    """Test cases for base WaveSpeedAIError"""
    
    def test_basic_error(self):
        """Test basic error creation"""
        error = WaveSpeedAIError("Test error message")
        self.assertEqual(str(error), "Test error message")
        self.assertIsNone(error.error_code)
        self.assertEqual(error.details, {})
    
    def test_error_with_code(self):
        """Test error with error code"""
        error = WaveSpeedAIError("Test error", error_code="TEST_001")
        self.assertEqual(str(error), "[TEST_001] Test error")
        self.assertEqual(error.error_code, "TEST_001")
    
    def test_error_with_details(self):
        """Test error with details"""
        details = {"field": "value", "count": 5}
        error = WaveSpeedAIError("Test error", details=details)
        self.assertEqual(error.details, details)


class TestAPIError(unittest.TestCase):
    """Test cases for APIError"""
    
    def test_basic_api_error(self):
        """Test basic API error creation"""
        error = APIError("API request failed")
        self.assertEqual(str(error), "API request failed")
        self.assertIsNone(error.status_code)
        self.assertIsNone(error.endpoint)
    
    def test_api_error_with_status_code(self):
        """Test API error with status code"""
        error = APIError("API request failed", status_code=404)
        self.assertEqual(error.status_code, 404)
    
    def test_api_error_with_endpoint(self):
        """Test API error with endpoint"""
        error = APIError("API request failed", endpoint="/api/test")
        self.assertEqual(error.endpoint, "/api/test")


class TestAuthenticationError(unittest.TestCase):
    """Test cases for AuthenticationError"""
    
    def test_authentication_error(self):
        """Test authentication error creation"""
        error = AuthenticationError()
        self.assertEqual(str(error), "Authentication failed")
        self.assertEqual(error.status_code, 401)
    
    def test_authentication_error_custom_message(self):
        """Test authentication error with custom message"""
        error = AuthenticationError("Custom auth error")
        self.assertEqual(str(error), "Custom auth error")
        self.assertEqual(error.status_code, 401)


class TestRateLimitError(unittest.TestCase):
    """Test cases for RateLimitError"""
    
    def test_rate_limit_error(self):
        """Test rate limit error creation"""
        error = RateLimitError()
        self.assertEqual(str(error), "Rate limit exceeded")
        self.assertEqual(error.status_code, 429)
        self.assertIsNone(error.retry_after)
    
    def test_rate_limit_error_with_retry_after(self):
        """Test rate limit error with retry after"""
        error = RateLimitError(retry_after=60)
        self.assertEqual(error.retry_after, 60)


class TestInsufficientBalanceError(unittest.TestCase):
    """Test cases for InsufficientBalanceError"""
    
    def test_insufficient_balance_error(self):
        """Test insufficient balance error creation"""
        error = InsufficientBalanceError()
        self.assertEqual(str(error), "Insufficient account balance")
        self.assertIsNone(error.current_balance)
    
    def test_insufficient_balance_error_with_balance(self):
        """Test insufficient balance error with current balance"""
        error = InsufficientBalanceError(current_balance=5.50)
        self.assertEqual(error.current_balance, 5.50)


class TestValidationError(unittest.TestCase):
    """Test cases for ValidationError"""
    
    def test_validation_error(self):
        """Test validation error creation"""
        error = ValidationError("Invalid input")
        self.assertEqual(str(error), "Invalid input")
        self.assertIsNone(error.field)
        self.assertIsNone(error.value)
    
    def test_validation_error_with_field(self):
        """Test validation error with field"""
        error = ValidationError("Invalid input", field="email")
        self.assertEqual(error.field, "email")
    
    def test_validation_error_with_value(self):
        """Test validation error with value"""
        error = ValidationError("Invalid input", value="invalid@")
        self.assertEqual(error.value, "invalid@")


class TestFileError(unittest.TestCase):
    """Test cases for FileError"""
    
    def test_file_error(self):
        """Test file error creation"""
        error = FileError("File not found")
        self.assertEqual(str(error), "File not found")
        self.assertIsNone(error.file_path)
    
    def test_file_error_with_path(self):
        """Test file error with file path"""
        error = FileError("File not found", file_path="/path/to/file.txt")
        self.assertEqual(error.file_path, "/path/to/file.txt")


class TestImageProcessingError(unittest.TestCase):
    """Test cases for ImageProcessingError"""
    
    def test_image_processing_error(self):
        """Test image processing error creation"""
        error = ImageProcessingError("Image processing failed")
        self.assertEqual(str(error), "Image processing failed")
        self.assertIsNone(error.file_path)
    
    def test_image_processing_error_with_path(self):
        """Test image processing error with file path"""
        error = ImageProcessingError("Image processing failed", file_path="/path/to/image.png")
        self.assertEqual(error.file_path, "/path/to/image.png")


class TestVideoProcessingError(unittest.TestCase):
    """Test cases for VideoProcessingError"""
    
    def test_video_processing_error(self):
        """Test video processing error creation"""
        error = VideoProcessingError("Video processing failed")
        self.assertEqual(str(error), "Video processing failed")
        self.assertIsNone(error.file_path)
    
    def test_video_processing_error_with_path(self):
        """Test video processing error with file path"""
        error = VideoProcessingError("Video processing failed", file_path="/path/to/video.mp4")
        self.assertEqual(error.file_path, "/path/to/video.mp4")


class TestConfigurationError(unittest.TestCase):
    """Test cases for ConfigurationError"""
    
    def test_configuration_error(self):
        """Test configuration error creation"""
        error = ConfigurationError("Invalid configuration")
        self.assertEqual(str(error), "Invalid configuration")
        self.assertIsNone(error.config_key)
    
    def test_configuration_error_with_key(self):
        """Test configuration error with config key"""
        error = ConfigurationError("Invalid configuration", config_key="api_key")
        self.assertEqual(error.config_key, "api_key")


class TestNetworkError(unittest.TestCase):
    """Test cases for NetworkError"""
    
    def test_network_error(self):
        """Test network error creation"""
        error = NetworkError("Network connection failed")
        self.assertEqual(str(error), "Network connection failed")
        self.assertIsNone(error.url)
    
    def test_network_error_with_url(self):
        """Test network error with URL"""
        error = NetworkError("Network connection failed", url="https://api.example.com")
        self.assertEqual(error.url, "https://api.example.com")


class TestTimeoutError(unittest.TestCase):
    """Test cases for TimeoutError"""
    
    def test_timeout_error(self):
        """Test timeout error creation"""
        error = TimeoutError("Request timed out")
        self.assertEqual(str(error), "Request timed out")
        self.assertIsNone(error.timeout_duration)
    
    def test_timeout_error_with_duration(self):
        """Test timeout error with duration"""
        error = TimeoutError("Request timed out", timeout_duration=30.0)
        self.assertEqual(error.timeout_duration, 30.0)


class TestTaskError(unittest.TestCase):
    """Test cases for TaskError"""
    
    def test_task_error(self):
        """Test task error creation"""
        error = TaskError("Task failed")
        self.assertEqual(str(error), "Task failed")
        self.assertIsNone(error.task_id)
        self.assertIsNone(error.status)
    
    def test_task_error_with_id_and_status(self):
        """Test task error with task ID and status"""
        error = TaskError("Task failed", task_id="task_123", status="failed")
        self.assertEqual(error.task_id, "task_123")
        self.assertEqual(error.status, "failed")


class TestTaskFailedError(unittest.TestCase):
    """Test cases for TaskFailedError"""
    
    def test_task_failed_error(self):
        """Test task failed error creation"""
        error = TaskFailedError("Task failed")
        self.assertEqual(str(error), "Task failed")
        self.assertEqual(error.status, "failed")
        self.assertIsNone(error.error_details)
    
    def test_task_failed_error_with_details(self):
        """Test task failed error with error details"""
        error = TaskFailedError("Task failed", error_details="Out of memory")
        self.assertEqual(error.error_details, "Out of memory")


class TestTaskTimeoutError(unittest.TestCase):
    """Test cases for TaskTimeoutError"""
    
    def test_task_timeout_error(self):
        """Test task timeout error creation"""
        error = TaskTimeoutError("Task timed out")
        self.assertEqual(str(error), "Task timed out")
        self.assertEqual(error.status, "timeout")
        self.assertIsNone(error.timeout_duration)
    
    def test_task_timeout_error_with_duration(self):
        """Test task timeout error with duration"""
        error = TaskTimeoutError("Task timed out", timeout_duration=60.0)
        self.assertEqual(error.timeout_duration, 60.0)


class TestUIError(unittest.TestCase):
    """Test cases for UIError"""
    
    def test_ui_error(self):
        """Test UI error creation"""
        error = UIError("UI component failed")
        self.assertEqual(str(error), "UI component failed")
        self.assertIsNone(error.component)
    
    def test_ui_error_with_component(self):
        """Test UI error with component"""
        error = UIError("UI component failed", component="button")
        self.assertEqual(error.component, "button")


class TestResourceError(unittest.TestCase):
    """Test cases for ResourceError"""
    
    def test_resource_error(self):
        """Test resource error creation"""
        error = ResourceError("Resource not available")
        self.assertEqual(str(error), "Resource not available")
        self.assertIsNone(error.resource_type)
    
    def test_resource_error_with_type(self):
        """Test resource error with resource type"""
        error = ResourceError("Resource not available", resource_type="memory")
        self.assertEqual(error.resource_type, "memory")


class TestDependencyError(unittest.TestCase):
    """Test cases for DependencyError"""
    
    def test_dependency_error(self):
        """Test dependency error creation"""
        error = DependencyError("Missing dependency")
        self.assertEqual(str(error), "Missing dependency")
        self.assertIsNone(error.dependency)
    
    def test_dependency_error_with_dependency(self):
        """Test dependency error with dependency name"""
        error = DependencyError("Missing dependency", dependency="requests")
        self.assertEqual(error.dependency, "requests")


class TestErrorHandlingUtilities(unittest.TestCase):
    """Test cases for error handling utility functions"""
    
    def test_handle_api_error_401(self):
        """Test handling 401 API error"""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {"message": "Unauthorized"}
        
        error = handle_api_error(mock_response, "/api/test")
        self.assertIsInstance(error, AuthenticationError)
        self.assertEqual(error.status_code, 401)
        self.assertEqual(error.endpoint, "/api/test")
    
    def test_handle_api_error_429(self):
        """Test handling 429 API error"""
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.headers = {"Retry-After": "60"}
        mock_response.json.return_value = {"message": "Rate limit exceeded"}
        
        error = handle_api_error(mock_response, "/api/test")
        self.assertIsInstance(error, RateLimitError)
        self.assertEqual(error.status_code, 429)
        self.assertEqual(error.retry_after, 60)
    
    def test_handle_api_error_402(self):
        """Test handling 402 API error"""
        mock_response = Mock()
        mock_response.status_code = 402
        mock_response.json.return_value = {"message": "Payment required"}
        
        error = handle_api_error(mock_response, "/api/test")
        self.assertIsInstance(error, InsufficientBalanceError)
        self.assertEqual(error.status_code, 402)
    
    def test_handle_api_error_generic(self):
        """Test handling generic API error"""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.json.return_value = {"message": "Internal server error"}
        
        error = handle_api_error(mock_response, "/api/test")
        self.assertIsInstance(error, APIError)
        self.assertEqual(error.status_code, 500)
        self.assertEqual(error.endpoint, "/api/test")
    
    def test_handle_validation_error(self):
        """Test handling validation error"""
        error = handle_validation_error("email", "invalid@", "Invalid email format")
        self.assertIsInstance(error, ValidationError)
        self.assertEqual(error.field, "email")
        self.assertEqual(error.value, "invalid@")
        self.assertEqual(str(error), "Invalid email format")
    
    def test_handle_file_error(self):
        """Test handling file error"""
        error = handle_file_error("/path/to/file.txt", "File not found")
        self.assertIsInstance(error, FileError)
        self.assertEqual(error.file_path, "/path/to/file.txt")
        self.assertEqual(str(error), "File not found")
    
    def test_handle_network_error(self):
        """Test handling network error"""
        error = handle_network_error("https://api.example.com", "Connection failed")
        self.assertIsInstance(error, NetworkError)
        self.assertEqual(error.url, "https://api.example.com")
        self.assertEqual(str(error), "Connection failed")
    
    def test_handle_timeout_error(self):
        """Test handling timeout error"""
        error = handle_timeout_error(30.0, "Request timed out")
        self.assertIsInstance(error, TimeoutError)
        self.assertEqual(error.timeout_duration, 30.0)
        self.assertEqual(str(error), "Request timed out")


if __name__ == '__main__':
    unittest.main()
