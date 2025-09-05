"""
Enhanced Warning Dialog System for WaveSpeed AI

Provides prominent warning dialogs for important user notifications.
"""

import tkinter as tk
from tkinter import ttk
from utils.utils import show_warning, show_info
import os


def show_sample_image_warning(parent_frame, image_path, ai_model, reason="Upload failed"):
    """
    Show a prominent warning when using sample image instead of user's image
    
    Args:
        parent_frame: Parent tkinter frame
        image_path: Path to user's selected image
        ai_model: AI model being used ('video', 'upscaler', 'seededit', 'seeddance')
        reason: Reason for fallback (default: "Upload failed")
    """
    
    # Create a more prominent warning dialog
    warning_window = tk.Toplevel()
    warning_window.title("⚠️ Using Sample Image")
    warning_window.geometry("500x350")
    warning_window.resizable(False, False)
    warning_window.grab_set()  # Make it modal
    
    # Center the window
    warning_window.transient(parent_frame.winfo_toplevel())
    warning_window.geometry("+%d+%d" % (
        parent_frame.winfo_toplevel().winfo_rootx() + 100,
        parent_frame.winfo_toplevel().winfo_rooty() + 100
    ))
    
    # Main frame
    main_frame = ttk.Frame(warning_window, padding="20")
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    # Warning icon and title
    title_frame = ttk.Frame(main_frame)
    title_frame.pack(fill=tk.X, pady=(0, 20))
    
    warning_label = ttk.Label(
        title_frame, 
        text="⚠️ IMPORTANT NOTICE", 
        font=('Arial', 16, 'bold'),
        foreground='orange'
    )
    warning_label.pack()
    
    # Main message
    message_frame = ttk.LabelFrame(main_frame, text="What's Happening", padding="15")
    message_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
    
    ai_model_names = {
        'video': 'Image-to-Video',
        'upscaler': 'Image Upscaler', 
        'seededit': 'SeedEdit',
        'seeddance': 'SeedDance'
    }
    
    model_name = ai_model_names.get(ai_model, ai_model.title())
    
    message_text = f"""🔄 Your image could not be uploaded for {model_name} processing.

📁 Your selected image:
   {os.path.basename(image_path)}

🎯 What we're doing instead:
   Using a sample demonstration image for {model_name} processing.

⚠️ This means:
   • The AI will process a sample image, not your image
   • You'll see how the {model_name} feature works
   • Your actual image remains on your computer

💡 Why this happened:
   {reason}

🔧 To use your own images:
   • Check your internet connection
   • Verify privacy settings (File → Privacy Settings)
   • Try a different image format (PNG, JPG recommended)"""
    
    message_label = tk.Label(
        message_frame,
        text=message_text,
        font=('Arial', 10),
        justify=tk.LEFT,
        wraplength=450,
        bg='#fff8dc'  # Light yellow background
    )
    message_label.pack(fill=tk.BOTH, expand=True)
    
    # Button frame
    button_frame = ttk.Frame(main_frame)
    button_frame.pack(fill=tk.X)
    
    # Buttons
    def continue_processing():
        warning_window.destroy()
    
    def open_privacy_settings():
        warning_window.destroy()
        # This would open privacy settings - you can implement this
        show_info("Privacy Settings", 
                 "Go to File → Privacy Settings in the main menu to adjust privacy modes.\n\n"
                 "HIGH PRIVACY: Uses base64 encoding (most secure)\n"
                 "MEDIUM PRIVACY: Temporary upload with auto-deletion\n"
                 "DEMO MODE: Always uses sample images")
    
    ttk.Button(
        button_frame, 
        text="Continue with Sample Image", 
        command=continue_processing,
        style='Accent.TButton'
    ).pack(side=tk.RIGHT, padx=(5, 0))
    
    ttk.Button(
        button_frame, 
        text="Privacy Settings", 
        command=open_privacy_settings
    ).pack(side=tk.RIGHT)
    
    # Auto-focus and center
    warning_window.focus_force()
    warning_window.wait_window()


def show_upload_success_notification(parent_frame, image_path, ai_model, privacy_info):
    """
    Show a brief success notification for successful uploads
    
    Args:
        parent_frame: Parent tkinter frame
        image_path: Path to uploaded image
        ai_model: AI model being used
        privacy_info: Privacy information string
    """
    
    # Create a small notification window
    notification = tk.Toplevel()
    notification.title("✅ Upload Success")
    notification.geometry("400x200")
    notification.resizable(False, False)
    notification.attributes('-topmost', True)
    
    # Position in top-right corner of parent
    parent_x = parent_frame.winfo_toplevel().winfo_rootx()
    parent_y = parent_frame.winfo_toplevel().winfo_rooty()
    notification.geometry(f"+{parent_x + 200}+{parent_y + 50}")
    
    # Content
    frame = ttk.Frame(notification, padding="15")
    frame.pack(fill=tk.BOTH, expand=True)
    
    ttk.Label(
        frame, 
        text="✅ Image Upload Successful", 
        font=('Arial', 12, 'bold'),
        foreground='green'
    ).pack(pady=(0, 10))
    
    ttk.Label(
        frame,
        text=f"📁 {os.path.basename(image_path)}",
        font=('Arial', 10)
    ).pack(pady=(0, 5))
    
    ttk.Label(
        frame,
        text=privacy_info,
        font=('Arial', 9),
        foreground='#666666',
        wraplength=350
    ).pack(pady=(0, 10))
    
    ttk.Button(
        frame,
        text="OK",
        command=notification.destroy
    ).pack()
    
    # Auto-close after 4 seconds
    notification.after(4000, notification.destroy)
