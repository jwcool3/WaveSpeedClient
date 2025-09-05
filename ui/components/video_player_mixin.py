"""
Video Player Mixin for WaveSpeed AI Application

This module provides shared video player functionality for tabs that generate videos.
"""

import tkinter as tk
from tkinter import ttk
import threading
import requests
import tempfile
import time
import os
from utils.utils import show_error, show_success
from core.logger import get_logger

logger = get_logger()

# Try to import video player
try:
    from tkVideoPlayer import TkinterVideo
    VIDEO_PLAYER_AVAILABLE = True
except ImportError:
    VIDEO_PLAYER_AVAILABLE = False
    print("tkVideoPlayer not available. Video will open in browser only.")


class VideoPlayerMixin:
    """Mixin class that provides video player functionality"""
    
    def __init__(self):
        """Initialize video player attributes"""
        self.video_player = None
        self.temp_video_path = None
        self.result_video_url = None
    
    def setup_video_result_section_with_player(self, result_frame):
        """Setup video result display section with embedded player"""
        # Clear the default result image label and add video-specific controls
        for widget in result_frame.winfo_children():
            if isinstance(widget, ttk.Label):
                widget.destroy()
        
        # Create video display area
        self.video_display_frame = ttk.Frame(result_frame)
        self.video_display_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Video player or placeholder
        if VIDEO_PLAYER_AVAILABLE:
            # Create embedded video player placeholder
            self.video_placeholder = tk.Label(
                self.video_display_frame,
                text="🎬 No video generated yet\n\nVideo will be displayed here when generated",
                font=('Arial', 12), fg='#666666',
                bg='#f0f0f0', relief='sunken', bd=1
            )
            self.video_placeholder.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        else:
            # Fallback to text display
            self.video_label = tk.Label(
                self.video_display_frame, 
                text="🎬 No video generated yet\n\nVideo will be available as a download link\n(Install tkvideoplayer for embedded playback)",
                font=('Arial', 12), fg='#666666'
            )
            self.video_label.pack(expand=True, pady=20)
        
        # Video control buttons
        self.setup_video_controls(result_frame)
    
    def setup_video_controls(self, result_frame):
        """Setup video control buttons"""
        button_frame = ttk.Frame(result_frame)
        button_frame.pack(pady=(10, 0))
        
        if VIDEO_PLAYER_AVAILABLE:
            # Playback controls
            controls_frame = ttk.Frame(button_frame)
            controls_frame.pack(pady=(0, 5))
            
            self.play_button = ttk.Button(controls_frame, text="▶ Play", 
                                        command=self.play_video, state="disabled")
            self.play_button.pack(side=tk.LEFT, padx=2)
            
            self.pause_button = ttk.Button(controls_frame, text="⏸ Pause", 
                                         command=self.pause_video, state="disabled")
            self.pause_button.pack(side=tk.LEFT, padx=2)
            
            self.stop_button = ttk.Button(controls_frame, text="⏹ Stop", 
                                        command=self.stop_video, state="disabled")
            self.stop_button.pack(side=tk.LEFT, padx=2)
        
        # Action buttons
        action_frame = ttk.Frame(button_frame)
        action_frame.pack()
        
        self.open_video_button = ttk.Button(action_frame, text="Open in Browser", 
                                          command=self.open_video_in_browser, state="disabled")
        self.open_video_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.copy_url_button = ttk.Button(action_frame, text="Copy URL", 
                                        command=self.copy_video_url, state="disabled")
        self.copy_url_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.download_button = ttk.Button(action_frame, text="Download Video", 
                                        command=self.download_video, state="disabled")
        self.download_button.pack(side=tk.LEFT)
    
    def load_video_in_player(self, video_url):
        """Load video in embedded player"""
        try:
            if not VIDEO_PLAYER_AVAILABLE:
                return
                
            # Download video to temporary file for local playback
            logger.info(f"Downloading video for playback: {video_url}")
            if hasattr(self, 'update_status'):
                self.update_status("Downloading video for playback...")
            
            # Download video in a separate thread
            threading.Thread(target=self._download_and_load_video, args=(video_url,), daemon=True).start()
            
        except Exception as e:
            logger.error(f"Failed to load video in player: {e}")
            show_error("Video Player Error", f"Failed to load video: {str(e)}")
    
    def _download_and_load_video(self, video_url):
        """Download video and load in player (runs in separate thread)"""
        try:
            # Create temporary file for video
            temp_dir = tempfile.gettempdir()
            temp_video_path = os.path.join(temp_dir, f"wavespeed_video_{int(time.time())}.mp4")
            
            # Download video
            response = requests.get(video_url, stream=True, timeout=30)
            response.raise_for_status()
            
            with open(temp_video_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # Load video in player (must be done on main thread)
            if hasattr(self, 'frame'):
                self.frame.after(0, lambda: self._create_video_player(temp_video_path))
            
        except Exception as e:
            logger.error(f"Failed to download video: {e}")
            if hasattr(self, 'frame'):
                self.frame.after(0, lambda: show_error("Download Error", f"Failed to download video: {str(e)}"))
    
    def _create_video_player(self, video_path):
        """Create and configure video player (runs on main thread)"""
        try:
            # Remove placeholder
            if hasattr(self, 'video_placeholder'):
                self.video_placeholder.destroy()
            
            # Create video player
            self.video_player = TkinterVideo(
                master=self.video_display_frame,
                scaled=True,
                keep_aspect=True
            )
            self.video_player.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            
            # Load video
            self.video_player.load(video_path)
            
            # Store temp file path for cleanup
            self.temp_video_path = video_path
            
            # Enable controls
            self.enable_video_controls()
            
            # Update status
            if hasattr(self, 'update_status'):
                self.update_status("Video loaded successfully!")
            
            logger.info("Video player created and loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to create video player: {e}")
            show_error("Video Player Error", f"Failed to create video player: {str(e)}")
    
    def play_video(self):
        """Play video"""
        if self.video_player:
            try:
                self.video_player.play()
                self.play_button.config(state="disabled")
                self.pause_button.config(state="normal")
                self.stop_button.config(state="normal")
            except Exception as e:
                show_error("Playback Error", f"Failed to play video: {str(e)}")
    
    def pause_video(self):
        """Pause video"""
        if self.video_player:
            try:
                self.video_player.pause()
                self.play_button.config(state="normal")
                self.pause_button.config(state="disabled")
            except Exception as e:
                show_error("Playback Error", f"Failed to pause video: {str(e)}")
    
    def stop_video(self):
        """Stop video"""
        if self.video_player:
            try:
                self.video_player.stop()
                self.play_button.config(state="normal")
                self.pause_button.config(state="disabled")
                self.stop_button.config(state="disabled")
            except Exception as e:
                show_error("Playback Error", f"Failed to stop video: {str(e)}")
    
    def enable_video_controls(self):
        """Enable video control buttons"""
        self.open_video_button.config(state="normal")
        self.copy_url_button.config(state="normal")
        self.download_button.config(state="normal")
        
        if VIDEO_PLAYER_AVAILABLE and self.video_player:
            self.play_button.config(state="normal")
    
    def download_video(self):
        """Download video to user's chosen location"""
        if not self.result_video_url:
            show_error("Error", "No video URL available.")
            return
        
        try:
            from tkinter import filedialog
            
            # Ask user where to save
            file_path = filedialog.asksaveasfilename(
                title="Save Video",
                defaultextension=".mp4",
                filetypes=[("MP4 files", "*.mp4"), ("All files", "*.*")]
            )
            
            if file_path:
                # Download in separate thread
                threading.Thread(target=self._download_video_to_path, args=(file_path,), daemon=True).start()
                
        except Exception as e:
            show_error("Download Error", f"Failed to start download: {str(e)}")
    
    def _download_video_to_path(self, file_path):
        """Download video to specified path"""
        try:
            if hasattr(self, 'frame') and hasattr(self, 'update_status'):
                self.frame.after(0, lambda: self.update_status("Downloading video..."))
            
            response = requests.get(self.result_video_url, stream=True, timeout=60)
            response.raise_for_status()
            
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            if hasattr(self, 'frame') and hasattr(self, 'update_status'):
                self.frame.after(0, lambda: self.update_status("Download completed!"))
                self.frame.after(0, lambda: show_success("Download Complete", f"Video saved to:\n{file_path}"))
            
        except Exception as e:
            error_msg = f"Failed to download video: {str(e)}"
            if hasattr(self, 'frame'):
                self.frame.after(0, lambda: show_error("Download Error", error_msg))
    
    def cleanup_temp_files(self):
        """Clean up temporary video files"""
        if hasattr(self, 'temp_video_path') and self.temp_video_path:
            try:
                if os.path.exists(self.temp_video_path):
                    os.remove(self.temp_video_path)
                    logger.info(f"Cleaned up temporary video file: {self.temp_video_path}")
            except Exception as e:
                logger.warning(f"Failed to cleanup temp video file: {e}")
            finally:
                self.temp_video_path = None
    
    def handle_video_success(self, output_url):
        """Handle successful video generation"""
        self.result_video_url = output_url
        
        # Load video in embedded player if available
        if VIDEO_PLAYER_AVAILABLE:
            self.load_video_in_player(output_url)
        else:
            # Update fallback display
            if hasattr(self, 'video_label'):
                self.video_label.config(
                    text=f"🎬 Video Generated Successfully!\n\nClick 'Open in Browser' to view",
                    fg='green'
                )
        
        # Enable buttons
        self.enable_video_controls()
