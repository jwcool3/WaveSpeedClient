"""
Unified Status Console Component
Professional console-style status feedback for all WaveSpeed AI tabs
"""

import tkinter as tk
from tkinter import ttk
import time
from typing import Optional, Callable
from core.logger import get_logger

logger = get_logger()


class UnifiedStatusConsole:
    """
    Professional status console with timestamp logging, progress tracking,
    and consistent styling across all tabs.
    """
    
    def __init__(self, parent_frame: tk.Widget, title: str = "📊 Status", height: int = 4):
        """
        Initialize unified status console
        
        Args:
            parent_frame: Parent tkinter widget
            title: Console title (with emoji)
            height: Height in text lines
        """
        self.parent_frame = parent_frame
        self.title = title
        self.height = height
        self.start_time: Optional[float] = None
        
        # Callbacks for status updates
        self.on_status_change: Optional[Callable] = None
        
        self.setup_console()
        
        # Log initial ready state
        self.log_ready()
    
    def setup_console(self):
        """Setup the console UI components"""
        # Console frame with title
        self.console_frame = ttk.LabelFrame(
            self.parent_frame, 
            text=self.title, 
            padding="6"
        )
        
        # Status text area - professional console styling
        self.status_text = tk.Text(
            self.console_frame,
            height=self.height,
            width=1,
            font=('Courier', 9),  # Monospace for professional look
            bg='#f8f8f8',        # Light gray background
            fg='#333',           # Dark gray text
            relief='flat',       # Clean appearance
            borderwidth=0,
            state=tk.DISABLED,   # Read-only
            wrap=tk.WORD,
            cursor='arrow'       # Not editable
        )
        self.status_text.pack(fill=tk.BOTH, expand=True)
        
        # Optional progress bar (initially hidden)
        self.progress_bar = ttk.Progressbar(
            self.console_frame,
            mode='indeterminate'
        )
        # Don't pack by default - show when needed
        
        # Grid the console frame
        # Note: Parent should call grid() on the console_frame to position it
    
    def grid(self, **kwargs):
        """Grid the console frame in parent"""
        self.console_frame.grid(**kwargs)
    
    def pack(self, **kwargs):
        """Pack the console frame in parent"""
        self.console_frame.pack(**kwargs)
    
    def log_status(self, message: str, status_type: str = "info", include_timestamp: bool = True):
        """
        Add message to status console with professional formatting
        
        Args:
            message: Status message to log
            status_type: Type of status (info, success, error, warning, processing)
            include_timestamp: Whether to include timestamp
        """
        # Add emoji prefix based on status type
        emoji_map = {
            "info": "ℹ️",
            "success": "✅", 
            "error": "❌",
            "warning": "⚠️",
            "processing": "🔄",
            "ready": "🟢",
            "loading": "📥",
            "saving": "💾",
            "complete": "🎉"
        }
        
        emoji = emoji_map.get(status_type, "ℹ️")
        
        # Format message with timestamp
        if include_timestamp:
            timestamp = time.strftime("%H:%M:%S")
            formatted_message = f"[{timestamp}] {emoji} {message}\\n"
        else:
            formatted_message = f"{emoji} {message}\\n"
        
        # Update text area
        self.status_text.config(state=tk.NORMAL)
        self.status_text.insert(tk.END, formatted_message)
        self.status_text.see(tk.END)  # Auto-scroll to latest
        self.status_text.config(state=tk.DISABLED)
        
        # Log to application logger as well
        logger.info(f"Status Console: {message}")
        
        # Callback for status changes
        if self.on_status_change:
            self.on_status_change(message, status_type)
    
    def log_ready(self, tool_name: str = "tool"):
        """Log ready state for the tool"""
        self.log_status(f"Ready to use {tool_name}", "ready")
    
    def log_processing_start(self, operation: str, details: str = ""):
        """Log start of processing operation"""
        self.start_time = time.time()
        message = f"Starting {operation}"
        if details:
            message += f": {details}"
        self.log_status(message, "processing")
    
    def log_processing_complete(self, operation: str, success: bool = True, details: str = ""):
        """Log completion of processing operation with timing"""
        # Calculate processing time
        processing_time = time.time() - self.start_time if self.start_time else 0
        
        if success:
            message = f"{operation} completed successfully in {processing_time:.1f}s"
            if details:
                message += f" - {details}"
            self.log_status(message, "success")
        else:
            message = f"{operation} failed after {processing_time:.1f}s"
            if details:
                message += f" - {details}"
            self.log_status(message, "error")
        
        self.start_time = None
    
    def log_file_operation(self, operation: str, filename: str, success: bool = True):
        """Log file operations (load, save, etc.)"""
        if success:
            self.log_status(f"{operation}: {filename}", "loading" if "load" in operation.lower() else "saving")
        else:
            self.log_status(f"Failed to {operation.lower()}: {filename}", "error")
    
    def log_api_call(self, model: str, parameters: str = ""):
        """Log API call initiation"""
        message = f"Calling {model} API"
        if parameters:
            message += f" with {parameters}"
        self.log_status(message, "processing")
    
    def log_error(self, error_message: str, context: str = ""):
        """Log error with optional context"""
        message = error_message
        if context:
            message = f"{context}: {error_message}"
        self.log_status(message, "error")
    
    def show_progress(self):
        """Show indeterminate progress bar"""
        self.progress_bar.pack(fill=tk.X, pady=(4, 0))
        self.progress_bar.start()
    
    def hide_progress(self):
        """Hide progress bar"""
        self.progress_bar.stop()
        self.progress_bar.pack_forget()
    
    def clear_console(self):
        """Clear all console messages"""
        self.status_text.config(state=tk.NORMAL)
        self.status_text.delete(1.0, tk.END)
        self.status_text.config(state=tk.DISABLED)
        self.log_ready()
    
    def get_console_text(self) -> str:
        """Get all console text for debugging/export"""
        return self.status_text.get(1.0, tk.END)
    
    def configure_title(self, new_title: str):
        """Update console title"""
        self.title = new_title
        self.console_frame.config(text=new_title)


# Convenience functions for common operations
def create_status_console(parent: tk.Widget, title: str = "📊 Status", height: int = 4) -> UnifiedStatusConsole:
    """
    Factory function to create a unified status console
    
    Args:
        parent: Parent widget
        title: Console title
        height: Console height in lines
        
    Returns:
        UnifiedStatusConsole instance
    """
    return UnifiedStatusConsole(parent, title, height)