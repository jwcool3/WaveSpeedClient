"""
Resource Management for WaveSpeed AI Application

This module handles cleanup of temporary files and resource management.
"""

import os
import glob
import tempfile
import atexit
from pathlib import Path
from typing import List, Optional
from app.config import Config
from core.logger import get_logger

logger = get_logger()


class ResourceManager:
    """Manages application resources and cleanup"""
    
    def __init__(self):
        self.temp_files: List[str] = []
        self.temp_dir: Optional[str] = None
        
        # Register cleanup on exit
        atexit.register(self.cleanup_all)
    
    def create_temp_file(self, prefix="", suffix=".png", content=None):
        """Create a temporary file and track it for cleanup"""
        try:
            # Create temp file
            if not self.temp_dir:
                self.temp_dir = tempfile.mkdtemp(prefix="wavespeed_")
            
            temp_path = os.path.join(
                self.temp_dir, 
                Config.get_temp_filename(prefix, suffix)
            )
            
            # Write content if provided
            if content:
                if hasattr(content, 'save'):  # PIL Image
                    content.save(temp_path, format="PNG")
                else:  # Raw data
                    with open(temp_path, 'wb') as f:
                        f.write(content)
            
            # Track the file
            self.temp_files.append(temp_path)
            logger.debug(f"Created temporary file: {temp_path}")
            
            return temp_path, None
            
        except Exception as e:
            error_msg = f"Failed to create temporary file: {str(e)}"
            logger.error(error_msg)
            return None, error_msg
    
    def cleanup_temp_file(self, file_path: str):
        """Clean up a specific temporary file"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                if file_path in self.temp_files:
                    self.temp_files.remove(file_path)
                logger.debug(f"Cleaned up temporary file: {file_path}")
                return True
        except Exception as e:
            logger.error(f"Failed to cleanup temp file {file_path}: {str(e)}")
        return False
    
    def cleanup_old_temp_files(self, max_age_hours=24):
        """Clean up old temporary files from previous sessions"""
        try:
            pattern = Config.get_temp_filename("*", "*")
            old_files = glob.glob(pattern)
            
            current_time = os.path.getctime
            max_age_seconds = max_age_hours * 3600
            
            cleaned_count = 0
            for file_path in old_files:
                try:
                    if os.path.exists(file_path):
                        file_age = current_time(file_path)
                        if (current_time - file_age) > max_age_seconds:
                            os.remove(file_path)
                            cleaned_count += 1
                except Exception as e:
                    logger.warning(f"Failed to cleanup old file {file_path}: {str(e)}")
            
            if cleaned_count > 0:
                logger.info(f"Cleaned up {cleaned_count} old temporary files")
                
        except Exception as e:
            logger.error(f"Failed to cleanup old temp files: {str(e)}")
    
    def cleanup_all(self):
        """Clean up all tracked temporary files"""
        cleaned_count = 0
        for file_path in self.temp_files[:]:  # Copy list to avoid modification during iteration
            if self.cleanup_temp_file(file_path):
                cleaned_count += 1
        
        # Clean up temp directory if empty
        if self.temp_dir and os.path.exists(self.temp_dir):
            try:
                os.rmdir(self.temp_dir)
                logger.debug(f"Cleaned up temporary directory: {self.temp_dir}")
            except OSError:
                # Directory not empty, that's ok
                pass
        
        if cleaned_count > 0:
            logger.info(f"Cleaned up {cleaned_count} temporary files on exit")
    
    def get_file_size_mb(self, file_path: str) -> float:
        """Get file size in MB"""
        try:
            size_bytes = os.path.getsize(file_path)
            return size_bytes / (1024 * 1024)
        except Exception:
            return 0.0
    
    def validate_file_size(self, file_path: str, max_size_mb: float = 50.0) -> tuple:
        """Validate file size"""
        try:
            size_mb = self.get_file_size_mb(file_path)
            if size_mb > max_size_mb:
                return False, f"File size ({size_mb:.1f} MB) exceeds limit ({max_size_mb} MB)"
            return True, None
        except Exception as e:
            return False, f"Failed to check file size: {str(e)}"
    
    def ensure_directory_exists(self, directory: str):
        """Ensure directory exists"""
        try:
            Path(directory).mkdir(parents=True, exist_ok=True)
            return True, None
        except Exception as e:
            error_msg = f"Failed to create directory {directory}: {str(e)}"
            logger.error(error_msg)
            return False, error_msg


# Global resource manager
resource_manager = ResourceManager()


def get_resource_manager():
    """Get the global resource manager"""
    return resource_manager
