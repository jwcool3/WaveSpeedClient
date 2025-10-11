"""
Progress Overlay Module
Provides visual feedback during processing operations

Features:
- Semi-transparent overlay
- Progress spinner/animation
- Status messages
- Cancellable operations
"""

import tkinter as tk
from tkinter import ttk
from core.logger import get_logger

logger = get_logger()


class ProgressOverlay:
    """
    Progress overlay for visual feedback during processing
    
    Shows a semi-transparent overlay with spinner and status message
    """
    
    def __init__(self, parent_widget):
        """
        Initialize progress overlay
        
        Args:
            parent_widget: Parent widget to overlay (usually the main frame)
        """
        self.parent = parent_widget
        self.overlay_frame = None
        self.status_label = None
        self.progress_bar = None
        self.cancel_callback = None
        self.animation_id = None
        self.animation_step = 0
        
        logger.info("ProgressOverlay initialized")
    
    def show(self, message: str = "Processing...", cancelable: bool = False, 
             cancel_callback=None):
        """
        Show the progress overlay
        
        Args:
            message: Status message to display
            cancelable: Whether operation can be cancelled
            cancel_callback: Function to call on cancel
        """
        if self.overlay_frame:
            # Already showing, just update message
            self.update_message(message)
            return
        
        # Create overlay frame
        self.overlay_frame = tk.Frame(
            self.parent,
            bg='#000000',  # Black background
            bd=0,
            highlightthickness=0
        )
        
        # Make it semi-transparent (if supported)
        try:
            self.overlay_frame.attributes('-alpha', 0.7)
        except:
            pass  # Alpha not supported on all platforms
        
        # Place over entire parent
        self.overlay_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
        
        # Create content frame (centered)
        content_frame = tk.Frame(
            self.overlay_frame,
            bg='#2b2b2b',
            relief='raised',
            bd=2
        )
        content_frame.place(relx=0.5, rely=0.5, anchor='center')
        
        # Spinner/animation
        self.spinner_label = tk.Label(
            content_frame,
            text="⏳",
            font=('Arial', 32),
            bg='#2b2b2b',
            fg='white'
        )
        self.spinner_label.pack(pady=(20, 10))
        
        # Status message
        self.status_label = tk.Label(
            content_frame,
            text=message,
            font=('Arial', 12),
            bg='#2b2b2b',
            fg='white'
        )
        self.status_label.pack(pady=10, padx=40)
        
        # Progress bar (indeterminate mode)
        style = ttk.Style()
        style.configure("Progress.Horizontal.TProgressbar", 
                       background='#4a9eff',
                       troughcolor='#1a1a1a')
        
        self.progress_bar = ttk.Progressbar(
            content_frame,
            mode='indeterminate',
            length=300,
            style="Progress.Horizontal.TProgressbar"
        )
        self.progress_bar.pack(pady=10, padx=20)
        self.progress_bar.start(10)  # Start animation
        
        # Cancel button (if cancelable)
        if cancelable and cancel_callback:
            self.cancel_callback = cancel_callback
            cancel_btn = tk.Button(
                content_frame,
                text="✖ Cancel",
                command=self._on_cancel,
                bg='#d32f2f',
                fg='white',
                font=('Arial', 10, 'bold'),
                relief='flat',
                padx=20,
                pady=5,
                cursor='hand2'
            )
            cancel_btn.pack(pady=(10, 20))
        else:
            # Just add some bottom padding
            tk.Label(content_frame, text="", bg='#2b2b2b', height=1).pack()
        
        # Start spinner animation
        self._animate_spinner()
        
        # Force update
        self.overlay_frame.update_idletasks()
        
        logger.info(f"Progress overlay shown: {message}")
    
    def _animate_spinner(self):
        """Animate the spinner icon"""
        if not self.spinner_label or not self.overlay_frame:
            return
        
        # Spinner characters (rotating effect)
        spinners = ["⏳", "⌛", "⏳", "⌛"]
        self.animation_step = (self.animation_step + 1) % len(spinners)
        
        try:
            self.spinner_label.config(text=spinners[self.animation_step])
            # Schedule next frame
            self.animation_id = self.overlay_frame.after(500, self._animate_spinner)
        except:
            pass  # Widget may have been destroyed
    
    def update_message(self, message: str):
        """
        Update the status message
        
        Args:
            message: New message to display
        """
        if self.status_label:
            try:
                self.status_label.config(text=message)
                self.status_label.update_idletasks()
                logger.debug(f"Progress message updated: {message}")
            except:
                pass  # Widget may have been destroyed
    
    def hide(self):
        """Hide the progress overlay"""
        # Cancel animation
        if self.animation_id:
            try:
                self.overlay_frame.after_cancel(self.animation_id)
            except:
                pass
            self.animation_id = None
        
        # Stop progress bar
        if self.progress_bar:
            try:
                self.progress_bar.stop()
            except:
                pass
        
        # Destroy overlay
        if self.overlay_frame:
            try:
                self.overlay_frame.destroy()
            except:
                pass
            self.overlay_frame = None
            self.status_label = None
            self.progress_bar = None
            self.spinner_label = None
        
        logger.info("Progress overlay hidden")
    
    def _on_cancel(self):
        """Handle cancel button click"""
        logger.info("Progress overlay cancelled by user")
        self.hide()
        if self.cancel_callback:
            try:
                self.cancel_callback()
            except Exception as e:
                logger.error(f"Error in cancel callback: {e}")
    
    def is_showing(self) -> bool:
        """Check if overlay is currently showing"""
        return self.overlay_frame is not None


# Convenience function for quick use
def show_progress(parent, message="Processing...", cancelable=False, cancel_callback=None):
    """
    Quick function to show progress overlay
    
    Returns the ProgressOverlay instance for further control
    """
    overlay = ProgressOverlay(parent)
    overlay.show(message, cancelable, cancel_callback)
    return overlay


# Export
__all__ = ['ProgressOverlay', 'show_progress']

