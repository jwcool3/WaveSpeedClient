"""
Custom Exceptions for WaveSpeed AI Application

This module defines custom exception classes for better error handling
and user-friendly error messages.
"""

from typing import Optional, Dict, Any


class WaveSpeedAIError(Exception):
    """Base exception class for WaveSpeed AI application"""
    
    def __init__(self, message: str, error_code: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}
    
    def __str__(self) -> str:
        if self.error_code:
            return f"[{self.error_code}] {self.message}"
        return self.message


class APIError(WaveSpeedAIError):
    """Exception raised for API-related errors"""
    
    def __init__(self, message: str, status_code: Optional[int] = None, endpoint: Optional[str] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.status_code = status_code
        self.endpoint = endpoint


class AuthenticationError(APIError):
    """Exception raised for authentication failures"""
    
    def __init__(self, message: str = "Authentication failed", **kwargs):
        super().__init__(message, status_code=401, **kwargs)


class RateLimitError(APIError):
    """Exception raised for rate limit exceeded"""
    
    def __init__(self, message: str = "Rate limit exceeded", retry_after: Optional[int] = None, **kwargs):
        super().__init__(message, status_code=429, **kwargs)
        self.retry_after = retry_after


class InsufficientBalanceError(APIError):
    """Exception raised for insufficient account balance"""
    
    def __init__(self, message: str = "Insufficient account balance", current_balance: Optional[float] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.current_balance = current_balance


class ValidationError(WaveSpeedAIError):
    """Exception raised for validation errors"""
    
    def __init__(self, message: str, field: Optional[str] = None, value: Optional[Any] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.field = field
        self.value = value


class FileError(WaveSpeedAIError):
    """Exception raised for file-related errors"""
    
    def __init__(self, message: str, file_path: Optional[str] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.file_path = file_path


class ImageProcessingError(FileError):
    """Exception raised for image processing errors"""
    
    def __init__(self, message: str, file_path: Optional[str] = None, **kwargs):
        super().__init__(message, file_path, **kwargs)


class VideoProcessingError(FileError):
    """Exception raised for video processing errors"""
    
    def __init__(self, message: str, file_path: Optional[str] = None, **kwargs):
        super().__init__(message, file_path, **kwargs)


class ConfigurationError(WaveSpeedAIError):
    """Exception raised for configuration errors"""
    
    def __init__(self, message: str, config_key: Optional[str] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.config_key = config_key


class NetworkError(WaveSpeedAIError):
    """Exception raised for network-related errors"""
    
    def __init__(self, message: str, url: Optional[str] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.url = url


class TimeoutError(WaveSpeedAIError):
    """Exception raised for timeout errors"""
    
    def __init__(self, message: str, timeout_duration: Optional[float] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.timeout_duration = timeout_duration


class TaskError(WaveSpeedAIError):
    """Exception raised for task-related errors"""
    
    def __init__(self, message: str, task_id: Optional[str] = None, status: Optional[str] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.task_id = task_id
        self.status = status


class TaskFailedError(TaskError):
    """Exception raised when a task fails"""
    
    def __init__(self, message: str, task_id: Optional[str] = None, error_details: Optional[str] = None, **kwargs):
        super().__init__(message, task_id, "failed", **kwargs)
        self.error_details = error_details


class TaskTimeoutError(TaskError):
    """Exception raised when a task times out"""
    
    def __init__(self, message: str, task_id: Optional[str] = None, timeout_duration: Optional[float] = None, **kwargs):
        super().__init__(message, task_id, "timeout", **kwargs)
        self.timeout_duration = timeout_duration


class UIError(WaveSpeedAIError):
    """Exception raised for UI-related errors"""
    
    def __init__(self, message: str, component: Optional[str] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.component = component


class ResourceError(WaveSpeedAIError):
    """Exception raised for resource-related errors"""
    
    def __init__(self, message: str, resource_type: Optional[str] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.resource_type = resource_type


class DependencyError(WaveSpeedAIError):
    """Exception raised for missing dependencies"""
    
    def __init__(self, message: str, dependency: Optional[str] = None, **kwargs):
        super().__init__(message, **kwargs)
        self.dependency = dependency


# Error handling utilities
def handle_api_error(response, endpoint: Optional[str] = None) -> APIError:
    """
    Convert HTTP response to appropriate API error
    
    Args:
        response: HTTP response object
        endpoint: API endpoint that was called
        
    Returns:
        Appropriate APIError instance
    """
    status_code = response.status_code
    message = f"API request failed with status {status_code}"
    
    try:
        error_data = response.json()
        if 'message' in error_data:
            message = error_data['message']
        elif 'error' in error_data:
            message = error_data['error']
    except:
        pass
    
    if status_code == 401:
        return AuthenticationError(message, endpoint=endpoint)
    elif status_code == 429:
        retry_after = response.headers.get('Retry-After')
        retry_after = int(retry_after) if retry_after else None
        return RateLimitError(message, retry_after=retry_after, endpoint=endpoint)
    elif status_code == 402:  # Payment required
        return InsufficientBalanceError(message, endpoint=endpoint)
    else:
        return APIError(message, status_code=status_code, endpoint=endpoint)


def handle_validation_error(field: str, value: Any, error_message: str) -> ValidationError:
    """
    Create a validation error with context
    
    Args:
        field: Field name that failed validation
        value: Value that failed validation
        error_message: Error message
        
    Returns:
        ValidationError instance
    """
    return ValidationError(error_message, field=field, value=value)


def handle_file_error(file_path: str, error_message: str) -> FileError:
    """
    Create a file error with context
    
    Args:
        file_path: Path to the file that caused the error
        error_message: Error message
        
    Returns:
        FileError instance
    """
    return FileError(error_message, file_path=file_path)


def handle_network_error(url: str, error_message: str) -> NetworkError:
    """
    Create a network error with context
    
    Args:
        url: URL that caused the error
        error_message: Error message
        
    Returns:
        NetworkError instance
    """
    return NetworkError(error_message, url=url)


def handle_timeout_error(timeout_duration: float, error_message: str) -> TimeoutError:
    """
    Create a timeout error with context
    
    Args:
        timeout_duration: Duration of the timeout
        error_message: Error message
        
    Returns:
        TimeoutError instance
    """
    return TimeoutError(error_message, timeout_duration=timeout_duration)
