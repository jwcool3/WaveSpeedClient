"""
Utility functions for the WaveSpeed AI GUI application
"""

import os
import json
import tkinter as tk
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk
import io
from urllib.request import urlopen
import webbrowser


def parse_drag_drop_data(raw_data):
    """
    Robustly parse drag & drop data to extract file path
    
    Args:
        raw_data (str): Raw drag & drop data from tkinterdnd2
        
    Returns:
        tuple: (success, file_path_or_error_message)
    """
    try:
        if not raw_data or not raw_data.strip():
            return False, "No file was dropped"
        
        raw_data = raw_data.strip()
        print(f"Raw drag & drop data: '{raw_data}'")
        
        file_path = None
        
        # Handle curly brace wrapped paths: {C:\path\file.jpg}
        if raw_data.startswith('{') and '}' in raw_data:
            end_brace = raw_data.find('}')
            file_path = raw_data[1:end_brace]
        
        # Handle space-separated multiple files (take first)
        elif ' ' in raw_data:
            files = raw_data.split()
            if files:
                file_path = files[0]
                # Remove curly braces if present
                if file_path.startswith('{') and file_path.endswith('}'):
                    file_path = file_path[1:-1]
        
        # Handle single file path
        else:
            file_path = raw_data
            # Remove curly braces if present
            if file_path.startswith('{') and file_path.endswith('}'):
                file_path = file_path[1:-1]
        
        if not file_path:
            return False, "Could not extract file path from dropped data"
        
        # Normalize the path
        file_path = os.path.normpath(file_path.strip())
        print(f"Processed file path: '{file_path}'")
        
        # Check if file exists
        if not os.path.exists(file_path):
            return False, f"The dropped file could not be found:\n{file_path}\n\nRaw data was: {raw_data}"
        
        return True, file_path
        
    except Exception as e:
        return False, f"Error processing dropped file: {str(e)}"


def validate_image_file(file_path):
    """Validate if the file is a supported image format"""
    valid_extensions = ('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp')
    if not file_path.lower().endswith(valid_extensions):
        return False, f"Please select an image file.\nSupported formats: {', '.join(valid_extensions)}"
    
    if not os.path.exists(file_path):
        return False, f"The file does not exist:\n{file_path}"
    
    return True, None


def load_image_preview(image_path, max_size=(350, 250)):
    """Load and resize image for preview"""
    try:
        with Image.open(image_path) as img:
            original_image = img.copy()
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            return photo, original_image, None
    except Exception as e:
        return None, None, f"Error loading image: {str(e)}"


def download_image_from_url(image_url):
    """Download image from URL and return PIL Image"""
    try:
        with urlopen(image_url) as response:
            image_data = response.read()
        image = Image.open(io.BytesIO(image_data))
        return image, None
    except Exception as e:
        return None, f"Error downloading image: {str(e)}"


def save_image_dialog(image, title="Save Image", default_extension=".png"):
    """Show save dialog and save image"""
    file_path = filedialog.asksaveasfilename(
        title=title,
        defaultextension=default_extension,
        filetypes=[
            ("PNG files", "*.png"),
            ("JPEG files", "*.jpg"),
            ("WebP files", "*.webp"),
            ("All files", "*.*")
        ]
    )
    
    if file_path:
        try:
            format_map = {
                '.png': 'PNG',
                '.jpg': 'JPEG',
                '.jpeg': 'JPEG',
                '.webp': 'WEBP'
            }
            
            ext = os.path.splitext(file_path)[1].lower()
            save_format = format_map.get(ext, 'PNG')
            
            image.save(file_path, format=save_format)
            return file_path, None
        except Exception as e:
            return None, f"Failed to save image: {str(e)}"
    
    return None, "Save cancelled"


def save_video_dialog(video_url, title="Save Video"):
    """Show save dialog for video and open download URL"""
    result = messagebox.askyesno(
        title,
        f"Video is ready!\n\nURL: {video_url}\n\nWould you like to open the video in your browser to download it?"
    )
    
    if result:
        try:
            webbrowser.open(video_url)
            return True, None
        except Exception as e:
            return False, f"Failed to open browser: {str(e)}"
    
    return False, "User cancelled"


def load_json_file(file_path, default=None):
    """Load JSON file with error handling"""
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                return json.load(f)
        return default if default is not None else []
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return default if default is not None else []


def save_json_file(file_path, data):
    """Save data to JSON file with error handling"""
    try:
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        return True, None
    except Exception as e:
        return False, f"Error saving {file_path}: {e}"


def create_temp_file(image, prefix="temp_", suffix=".png"):
    """Create a temporary file from PIL Image"""
    from core.resource_manager import get_resource_manager
    resource_manager = get_resource_manager()
    return resource_manager.create_temp_file(prefix, suffix, image)


def setup_drag_and_drop(widget, callback, dnd_available=True):
    """Setup drag and drop functionality for a widget"""
    if not dnd_available:
        return False
    
    try:
        from tkinterdnd2 import DND_FILES
        widget.drop_target_register(DND_FILES)
        widget.dnd_bind('<<Drop>>', callback)
        return True
    except ImportError:
        print("tkinterdnd2 not available. Drag and drop disabled.")
        return False
    except Exception as e:
        print(f"Drag and drop setup failed: {e}")
        return False


def format_duration(seconds):
    """Format duration in seconds to human readable format"""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds // 60
        secs = seconds % 60
        return f"{int(minutes)}m {secs:.1f}s"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        return f"{int(hours)}h {int(minutes)}m {secs:.1f}s"


def show_error(title, message):
    """Show error message dialog"""
    messagebox.showerror(title, message)


def show_success(title, message):
    """Show success message dialog"""
    messagebox.showinfo(title, message)


def show_warning(title, message):
    """Show warning message dialog"""
    messagebox.showwarning(title, message)


def show_info(title, message):
    """Show info message dialog"""
    messagebox.showinfo(title, message)


def ask_yes_no(title, message):
    """Show yes/no question dialog"""
    return messagebox.askyesno(title, message)


def get_file_size_mb(file_path):
    """Get file size in MB"""
    try:
        size_bytes = os.path.getsize(file_path)
        size_mb = size_bytes / (1024 * 1024)
        return size_mb
    except:
        return 0
