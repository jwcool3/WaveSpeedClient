"""
Modern Video Player Component for WaveSpeed AI Application

A lightweight, reliable video player with modern UI and better integration.
"""

import tkinter as tk
from tkinter import ttk
import threading
import subprocess
import platform
import os
import webbrowser
from PIL import Image, ImageTk
import tempfile
import requests
from utils.utils import show_error, show_success, show_warning
from core.logger import get_logger

logger = get_logger()


class ModernVideoPlayer:
    """Modern video player with multiple playback options and clean UI"""
    
    def __init__(self, parent_frame):
        self.parent_frame = parent_frame
        self.current_video_url = None
        self.current_video_file = None
        self.thumbnail_image = None
        
        self.setup_modern_ui()
    
    def setup_modern_ui(self):
        """Setup modern, clean video player UI"""
        # Configure parent
        self.parent_frame.columnconfigure(0, weight=1)
        self.parent_frame.rowconfigure(0, weight=1)
        
        # Main container with rounded corners effect
        self.main_container = tk.Frame(
            self.parent_frame, 
            bg='#f8f9fa', 
            relief='solid', 
            bd=1
        )
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.main_container.columnconfigure(0, weight=1)
        self.main_container.rowconfigure(1, weight=1)
        
        # Header with video info
        self.setup_video_header()
        
        # Video display area
        self.setup_video_display()
        
        # Modern controls
        self.setup_modern_controls()
    
    def setup_video_header(self):
        """Setup clean video header with info"""
        header_frame = tk.Frame(self.main_container, bg='#f8f9fa', height=40)
        header_frame.pack(fill=tk.X, padx=10, pady=(10, 0))
        header_frame.pack_propagate(False)
        
        # Video icon and title
        title_frame = tk.Frame(header_frame, bg='#f8f9fa')
        title_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        tk.Label(
            title_frame,
            text="🎬",
            font=('Arial', 16),
            bg='#f8f9fa'
        ).pack(side=tk.LEFT, padx=(0, 8))
        
        self.video_title_label = tk.Label(
            title_frame,
            text="Video Player",
            font=('Arial', 12, 'bold'),
            bg='#f8f9fa',
            fg='#2c3e50'
        )
        self.video_title_label.pack(side=tk.LEFT, anchor=tk.W)
        
        # Status indicator
        self.status_label = tk.Label(
            header_frame,
            text="Ready",
            font=('Arial', 9),
            bg='#f8f9fa',
            fg='#7f8c8d'
        )
        self.status_label.pack(side=tk.RIGHT, anchor=tk.E)
    
    def setup_video_display(self):
        """Setup modern video display area"""
        # Video container with subtle shadow effect
        video_container = tk.Frame(self.main_container, bg='#ffffff', relief='solid', bd=1)
        video_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        video_container.columnconfigure(0, weight=1)
        video_container.rowconfigure(0, weight=1)
        
        # Video display area
        self.video_display = tk.Frame(video_container, bg='#000000')
        self.video_display.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # Default state - elegant placeholder
        self.setup_placeholder()
    
    def setup_placeholder(self):
        """Setup elegant placeholder for when no video is loaded"""
        # Clear existing content
        for widget in self.video_display.winfo_children():
            widget.destroy()
        
        placeholder_frame = tk.Frame(self.video_display, bg='#2c3e50')
        placeholder_frame.pack(fill=tk.BOTH, expand=True)
        
        # Centered content
        content_frame = tk.Frame(placeholder_frame, bg='#2c3e50')
        content_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # Large play icon
        tk.Label(
            content_frame,
            text="🎥",
            font=('Arial', 48),
            bg='#2c3e50',
            fg='#ecf0f1'
        ).pack(pady=(0, 10))
        
        # Instructions
        tk.Label(
            content_frame,
            text="Generate a video to see it here",
            font=('Arial', 14),
            bg='#2c3e50',
            fg='#ecf0f1'
        ).pack(pady=(0, 5))
        
        tk.Label(
            content_frame,
            text="Or click the buttons below to open existing videos",
            font=('Arial', 10),
            bg='#2c3e50',
            fg='#bdc3c7'
        ).pack()
    
    def setup_modern_controls(self):
        """Setup modern, clean control panel"""
        controls_frame = tk.Frame(self.main_container, bg='#f8f9fa', height=60)
        controls_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        controls_frame.pack_propagate(False)
        
        # Primary actions (left side)
        primary_frame = tk.Frame(controls_frame, bg='#f8f9fa')
        primary_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        # Play in System Player button (primary action)
        self.play_system_button = tk.Button(
            primary_frame,
            text="▶ Play in System Player",
            font=('Arial', 10, 'bold'),
            bg='#3498db',
            fg='white',
            activebackground='#2980b9',
            activeforeground='white',
            relief='flat',
            bd=0,
            padx=20,
            pady=8,
            command=self.play_in_system_player,
            state='disabled'
        )
        self.play_system_button.pack(pady=5)
        
        # Secondary actions (center)
        secondary_frame = tk.Frame(controls_frame, bg='#f8f9fa')
        secondary_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        # Open in Browser button
        self.browser_button = tk.Button(
            secondary_frame,
            text="🌐 Open in Browser",
            font=('Arial', 9),
            bg='#95a5a6',
            fg='white',
            activebackground='#7f8c8d',
            activeforeground='white',
            relief='flat',
            bd=0,
            padx=15,
            pady=8,
            command=self.open_in_browser,
            state='disabled'
        )
        self.browser_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # Download button
        self.download_button = tk.Button(
            secondary_frame,
            text="💾 Download",
            font=('Arial', 9),
            bg='#27ae60',
            fg='white',
            activebackground='#229954',
            activeforeground='white',
            relief='flat',
            bd=0,
            padx=15,
            pady=8,
            command=self.download_video,
            state='disabled'
        )
        self.download_button.pack(side=tk.LEFT, padx=5)
        
        # File management (right side)
        file_frame = tk.Frame(controls_frame, bg='#f8f9fa')
        file_frame.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Browse Videos button
        tk.Button(
            file_frame,
            text="📁 Browse Videos",
            font=('Arial', 9),
            bg='#e74c3c',
            fg='white',
            activebackground='#c0392b',
            activeforeground='white',
            relief='flat',
            bd=0,
            padx=15,
            pady=8,
            command=self.browse_videos
        ).pack(side=tk.RIGHT, padx=(5, 0))
        
        # Open Results Folder
        tk.Button(
            file_frame,
            text="📂 Results Folder",
            font=('Arial', 9),
            bg='#f39c12',
            fg='white',
            activebackground='#e67e22',
            activeforeground='white',
            relief='flat',
            bd=0,
            padx=15,
            pady=8,
            command=self.open_results_folder
        ).pack(side=tk.RIGHT, padx=5)
    
    def load_video(self, video_url):
        """Load a video from URL"""
        self.current_video_url = video_url
        self.current_video_file = None
        
        # Update UI
        self.update_video_display(video_url)
        self.enable_controls()
        
        # Update status
        self.status_label.config(text="Video loaded", fg='#27ae60')
        self.video_title_label.config(text="Generated Video")
        
        logger.info(f"Video loaded: {video_url}")
    
    def load_video_file(self, video_path):
        """Load a local video file"""
        self.current_video_file = video_path
        self.current_video_url = None
        
        # Update UI
        self.update_video_display(video_path, is_local=True)
        self.enable_controls_for_local()
        
        # Update status
        self.status_label.config(text="Local video loaded", fg='#27ae60')
        filename = os.path.basename(video_path)
        self.video_title_label.config(text=filename)
        
        logger.info(f"Local video loaded: {video_path}")
    
    def update_video_display(self, video_source, is_local=False):
        """Update video display with thumbnail or video info"""
        # Clear placeholder
        for widget in self.video_display.winfo_children():
            widget.destroy()
        
        # Create video info display
        info_frame = tk.Frame(self.video_display, bg='#34495e')
        info_frame.pack(fill=tk.BOTH, expand=True)
        
        # Centered content
        content_frame = tk.Frame(info_frame, bg='#34495e')
        content_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # Video ready icon
        tk.Label(
            content_frame,
            text="🎬" if is_local else "🎥",
            font=('Arial', 64),
            bg='#34495e',
            fg='#ecf0f1'
        ).pack(pady=(0, 15))
        
        # Status text
        status_text = "Local Video Ready" if is_local else "Generated Video Ready"
        tk.Label(
            content_frame,
            text=status_text,
            font=('Arial', 16, 'bold'),
            bg='#34495e',
            fg='#ecf0f1'
        ).pack(pady=(0, 5))
        
        # Instructions
        instruction = "Click 'Play in System Player' to watch" if is_local else "Choose your preferred viewing option below"
        tk.Label(
            content_frame,
            text=instruction,
            font=('Arial', 11),
            bg='#34495e',
            fg='#bdc3c7'
        ).pack()
        
        # Show video path/URL (truncated)
        source_display = video_source
        if len(source_display) > 60:
            source_display = source_display[:57] + "..."
        
        tk.Label(
            content_frame,
            text=source_display,
            font=('Arial', 8),
            bg='#34495e',
            fg='#95a5a6',
            wraplength=400
        ).pack(pady=(10, 0))
    
    def enable_controls(self):
        """Enable controls for online video"""
        self.play_system_button.config(state='normal')
        self.browser_button.config(state='normal')
        self.download_button.config(state='normal')
    
    def enable_controls_for_local(self):
        """Enable controls for local video"""
        self.play_system_button.config(state='normal')
        self.browser_button.config(state='disabled')  # Can't browse to local files
        self.download_button.config(state='disabled')  # Already local
    
    def disable_controls(self):
        """Disable all controls"""
        self.play_system_button.config(state='disabled')
        self.browser_button.config(state='disabled')
        self.download_button.config(state='disabled')
    
    def play_in_system_player(self):
        """Open video in system's default video player"""
        try:
            if self.current_video_file:
                # Local file
                self.open_file_with_system_player(self.current_video_file)
            elif self.current_video_url:
                # Download first, then play
                self.download_and_play()
            else:
                show_error("No Video", "No video loaded to play.")
        except Exception as e:
            logger.error(f"Error playing video: {e}")
            show_error("Playback Error", f"Failed to play video: {str(e)}")
    
    def open_file_with_system_player(self, file_path):
        """Open file with system's default video player"""
        try:
            system = platform.system()
            
            if system == "Windows":
                os.startfile(file_path)
            elif system == "Darwin":  # macOS
                subprocess.run(["open", file_path])
            elif system == "Linux":
                subprocess.run(["xdg-open", file_path])
            else:
                show_warning("Unsupported System", "Cannot open video player on this system.")
                return
            
            self.status_label.config(text="Opened in system player", fg='#27ae60')
            
        except Exception as e:
            logger.error(f"Error opening with system player: {e}")
            show_error("System Player Error", f"Failed to open video: {str(e)}")
    
    def download_and_play(self):
        """Download video and play in system player"""
        if not self.current_video_url:
            return
        
        def download_thread():
            try:
                self.status_label.config(text="Downloading video...", fg='#f39c12')
                
                # Download to temp file
                response = requests.get(self.current_video_url, stream=True)
                response.raise_for_status()
                
                # Create temp file with proper extension
                with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp_file:
                    for chunk in response.iter_content(chunk_size=8192):
                        temp_file.write(chunk)
                    temp_path = temp_file.name
                
                # Open with system player
                self.parent_frame.after(0, lambda: self.open_file_with_system_player(temp_path))
                
            except Exception as e:
                logger.error(f"Error downloading video: {e}")
                self.parent_frame.after(0, lambda: show_error("Download Error", f"Failed to download video: {str(e)}"))
                self.parent_frame.after(0, lambda: self.status_label.config(text="Download failed", fg='#e74c3c'))
        
        # Start download in background
        threading.Thread(target=download_thread, daemon=True).start()
    
    def open_in_browser(self):
        """Open video URL in web browser"""
        if not self.current_video_url:
            show_error("No Video URL", "No video URL available to open in browser.")
            return
        
        try:
            webbrowser.open(self.current_video_url)
            self.status_label.config(text="Opened in browser", fg='#27ae60')
        except Exception as e:
            logger.error(f"Error opening browser: {e}")
            show_error("Browser Error", f"Failed to open browser: {str(e)}")
    
    def download_video(self):
        """Download video to user's chosen location"""
        if not self.current_video_url:
            show_error("No Video", "No video URL available for download.")
            return
        
        from tkinter import filedialog
        
        # Ask user where to save
        file_path = filedialog.asksaveasfilename(
            title="Save Video As",
            defaultextension=".mp4",
            filetypes=[
                ("MP4 files", "*.mp4"),
                ("All files", "*.*")
            ]
        )
        
        if not file_path:
            return
        
        def download_thread():
            try:
                self.status_label.config(text="Downloading...", fg='#f39c12')
                
                response = requests.get(self.current_video_url, stream=True)
                response.raise_for_status()
                
                with open(file_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                self.parent_frame.after(0, lambda: self.status_label.config(text="Download complete", fg='#27ae60'))
                # Note: Removed success popup as per user request
                
            except Exception as e:
                logger.error(f"Error downloading video: {e}")
                self.parent_frame.after(0, lambda: show_error("Download Error", f"Failed to download video: {str(e)}"))
                self.parent_frame.after(0, lambda: self.status_label.config(text="Download failed", fg='#e74c3c'))
        
        # Start download in background
        threading.Thread(target=download_thread, daemon=True).start()
    
    def browse_videos(self):
        """Browse for local video files"""
        from tkinter import filedialog
        
        file_path = filedialog.askopenfilename(
            title="Select Video File",
            filetypes=[
                ("Video files", "*.mp4 *.avi *.mov *.mkv *.wmv *.flv"),
                ("MP4 files", "*.mp4"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            self.load_video_file(file_path)
    
    def open_results_folder(self):
        """Open the results folder in file explorer"""
        try:
            from app.config import Config
            results_folder = Config.AUTO_SAVE_FOLDER
            
            if not os.path.exists(results_folder):
                os.makedirs(results_folder)
            
            system = platform.system()
            
            if system == "Windows":
                os.startfile(results_folder)
            elif system == "Darwin":  # macOS
                subprocess.run(["open", results_folder])
            elif system == "Linux":
                subprocess.run(["xdg-open", results_folder])
            
            self.status_label.config(text="Results folder opened", fg='#27ae60')
            
        except Exception as e:
            logger.error(f"Error opening results folder: {e}")
            show_error("Folder Error", f"Failed to open results folder: {str(e)}")
    
    def clear_video(self):
        """Clear current video and return to placeholder"""
        self.current_video_url = None
        self.current_video_file = None
        self.setup_placeholder()
        self.disable_controls()
        self.status_label.config(text="Ready", fg='#7f8c8d')
        self.video_title_label.config(text="Video Player")
