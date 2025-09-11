"""
Auto-Save System for WaveSpeed AI Application

This module handles automatic saving of all AI-generated results with organized
folder structure and intelligent naming conventions.
"""

import os
import json
from datetime import datetime
from pathlib import Path
import requests
from PIL import Image
import tempfile

from app.config import Config
from core.logger import logger
from utils.utils import show_success, show_error


class AutoSaveManager:
    """Manages automatic saving of AI results"""
    
    def __init__(self):
        self.base_folder = Config.AUTO_SAVE_FOLDER
        self.subfolders = Config.AUTO_SAVE_SUBFOLDERS
        self.ensure_folders_exist()
        
    def ensure_folders_exist(self):
        """Create auto-save folder structure if it doesn't exist"""
        try:
            # Create base folder
            Path(self.base_folder).mkdir(exist_ok=True)
            
            # Create subfolders for each AI model
            for subfolder in self.subfolders.values():
                folder_path = Path(self.base_folder) / subfolder
                folder_path.mkdir(exist_ok=True)
                
            logger.info(f"Auto-save folders initialized in: {self.base_folder}")
            
        except Exception as e:
            logger.error(f"Failed to create auto-save folders: {e}")
    
    def generate_filename(self, ai_model, file_type="image", prompt=None, extra_info=None):
        """Generate automatic filename with timestamp and model info"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Clean prompt for filename (first 30 chars, safe characters only)
        prompt_part = ""
        if prompt:
            # Remove special characters and limit length
            safe_prompt = "".join(c for c in prompt if c.isalnum() or c in (' ', '-', '_')).strip()
            if safe_prompt:
                prompt_part = f"_{safe_prompt[:30].replace(' ', '_')}"
        
        # Add extra info if provided
        extra_part = ""
        if extra_info:
            # Sanitize extra_info for filename compatibility
            safe_extra_info = self.sanitize_filename_part(extra_info)
            extra_part = f"_{safe_extra_info}"
        
        # Determine file extension
        extension = ".mp4" if file_type == "video" else ".png"
        
        # Combine all parts
        filename = f"{ai_model}_{timestamp}{prompt_part}{extra_part}{extension}"
        
        return filename
    
    def sanitize_filename_part(self, text):
        """Sanitize a part of filename to remove invalid characters"""
        import re
        # Replace invalid characters with underscores
        invalid_chars = r'[<>:"/\\|?*]'
        sanitized = re.sub(invalid_chars, '_', text)
        # Remove multiple consecutive underscores
        sanitized = re.sub(r'_+', '_', sanitized)
        # Remove leading/trailing underscores
        sanitized = sanitized.strip('_')
        return sanitized
    
    def save_result(self, ai_model, result_url, prompt=None, extra_info=None, file_type="image"):
        """
        Automatically save AI result with organized naming
        
        Args:
            ai_model: The AI model used ('image_editor', 'seededit', etc.)
            result_url: URL of the result to download and save
            prompt: Optional prompt used for generation (for filename)
            extra_info: Optional extra info for filename (e.g., "upscaled_4k")
            file_type: 'image' or 'video'
        
        Returns:
            tuple: (success: bool, saved_path: str or None, error: str or None)
        """
        if not Config.AUTO_SAVE_ENABLED:
            return True, None, "Auto-save is disabled"
            
        try:
            # Get the appropriate subfolder
            subfolder = self.subfolders.get(ai_model, 'Other')
            save_dir = Path(self.base_folder) / subfolder
            
            # Generate filename
            filename = self.generate_filename(ai_model, file_type, prompt, extra_info)
            save_path = save_dir / filename
            
            # Download and save the result
            logger.info(f"Auto-saving {ai_model} result: {filename}")
            
            response = requests.get(result_url, timeout=30)
            response.raise_for_status()
            
            with open(save_path, 'wb') as f:
                f.write(response.content)
            
            # Create metadata file
            self.save_metadata(save_path, ai_model, result_url, prompt, extra_info)
            
            logger.info(f"Auto-saved result to: {save_path}")
            return True, str(save_path), None
            
        except Exception as e:
            error_msg = f"Auto-save failed: {str(e)}"
            logger.error(error_msg)
            return False, None, error_msg
    
    def save_metadata(self, file_path, ai_model, result_url, prompt=None, extra_info=None):
        """Save metadata alongside the result file"""
        try:
            metadata = {
                "timestamp": datetime.now().isoformat(),
                "ai_model": ai_model,
                "result_url": result_url,
                "prompt": prompt,
                "extra_info": extra_info,
                "file_path": str(file_path)
            }
            
            # Save metadata as JSON file
            metadata_path = file_path.with_suffix('.json')
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.warning(f"Failed to save metadata: {e}")
    
    def get_save_location(self, ai_model):
        """Get the save location for a specific AI model"""
        subfolder = self.subfolders.get(ai_model, 'Other')
        return Path(self.base_folder) / subfolder
    
    def get_recent_files(self, ai_model=None, limit=10):
        """Get recently saved files for a specific model or all models"""
        try:
            files = []
            
            if ai_model:
                # Get files for specific model
                subfolder = self.subfolders.get(ai_model, 'Other')
                search_dir = Path(self.base_folder) / subfolder
                if search_dir.exists():
                    for file in search_dir.glob('*.png'):
                        files.append(file)
                    for file in search_dir.glob('*.mp4'):
                        files.append(file)
            else:
                # Get files from all subfolders
                base_path = Path(self.base_folder)
                if base_path.exists():
                    for subfolder in self.subfolders.values():
                        subfolder_path = base_path / subfolder
                        if subfolder_path.exists():
                            for file in subfolder_path.glob('*.png'):
                                files.append(file)
                            for file in subfolder_path.glob('*.mp4'):
                                files.append(file)
            
            # Sort by modification time (newest first) and limit
            files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            return files[:limit]
            
        except Exception as e:
            logger.error(f"Failed to get recent files: {e}")
            return []
    
    def open_results_folder(self, ai_model=None):
        """Open the results folder in file explorer"""
        try:
            if ai_model:
                subfolder = self.subfolders.get(ai_model, 'Other')
                folder_path = Path(self.base_folder) / subfolder
            else:
                folder_path = Path(self.base_folder)
            
            if folder_path.exists():
                # Open folder in default file manager
                import subprocess
                import platform
                
                if platform.system() == 'Windows':
                    subprocess.run(['explorer', str(folder_path)])
                elif platform.system() == 'Darwin':  # macOS
                    subprocess.run(['open', str(folder_path)])
                else:  # Linux
                    subprocess.run(['xdg-open', str(folder_path)])
                    
                return True
            else:
                return False
                
        except Exception as e:
            logger.error(f"Failed to open results folder: {e}")
            return False


# Global auto-save manager instance
auto_save_manager = AutoSaveManager()
