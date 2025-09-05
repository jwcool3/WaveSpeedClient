"""
Logging Configuration for WaveSpeed AI Application

This module provides centralized logging functionality.
"""

import logging
import os
from datetime import datetime
from pathlib import Path


class AppLogger:
    """Application logger with file and console output"""
    
    def __init__(self, name="WaveSpeedAI", log_level=logging.INFO):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(log_level)
        
        # Avoid duplicate handlers
        if not self.logger.handlers:
            self.setup_handlers()
    
    def setup_handlers(self):
        """Setup logging handlers"""
        # Create logs directory if it doesn't exist
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # File handler
        log_file = log_dir / f"wavespeed_ai_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        
        # Console handler with UTF-8 encoding
        import sys
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        
        # Set console encoding to UTF-8 if possible
        if hasattr(sys.stdout, 'reconfigure'):
            try:
                sys.stdout.reconfigure(encoding='utf-8')
            except:
                pass
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Add handlers
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def info(self, message, **kwargs):
        """Log info message"""
        self.logger.info(message, extra=kwargs)
    
    def error(self, message, **kwargs):
        """Log error message"""
        # Handle exc_info separately to avoid conflicts
        exc_info = kwargs.pop('exc_info', None)
        self.logger.error(message, exc_info=exc_info, extra=kwargs)
    
    def warning(self, message, **kwargs):
        """Log warning message"""
        self.logger.warning(message, extra=kwargs)
    
    def debug(self, message, **kwargs):
        """Log debug message"""
        self.logger.debug(message, extra=kwargs)
    
    def log_api_request(self, endpoint, request_id=None, status="started"):
        """Log API request"""
        message = f"API Request - Endpoint: {endpoint}"
        if request_id:
            message += f", Request ID: {request_id}"
        message += f", Status: {status}"
        self.info(message)
    
    def log_api_response(self, request_id, status, duration=None, error=None):
        """Log API response"""
        message = f"API Response - Request ID: {request_id}, Status: {status}"
        if duration:
            message += f", Duration: {duration:.2f}s"
        if error:
            message += f", Error: {error}"
            self.error(message)
        else:
            self.info(message)
    
    def log_user_action(self, action, details=None):
        """Log user action"""
        message = f"User Action - {action}"
        if details:
            message += f" - {details}"
        self.info(message)
    
    def log_error_with_context(self, error, context=None):
        """Log error with context"""
        message = f"Error: {str(error)}"
        if context:
            message += f" - Context: {context}"
        self.error(message)


# Global logger instance
logger = AppLogger()


def get_logger():
    """Get the global logger instance"""
    return logger
