"""
Unified Video Player Component for WaveSpeed AI Application

This module combines the functionality of both EnhancedVideoPlayer and ModernVideoPlayer
into a single, configurable component that preserves all features from both players.

Supports:
- Theme switching (Enhanced dark theme / Modern light theme)
- Playback modes (Direct control / External playback)
- All original features from both players
- Graceful degradation when dependencies are missing
"""

import tkinter as tk
from tkinter import ttk
import threading
import time
import os
import subprocess
import platform
import webbrowser
import tempfile
import requests
from PIL import Image, ImageTk
import sys

from utils.utils import show_error, show_success, show_warning
from core.logger import get_logger

logger = get_logger()

# Try to import video player (Enhanced player dependency)
try:
    from tkVideoPlayer import TkinterVideo
    VIDEO_PLAYER_AVAILABLE = True
except ImportError:
    VIDEO_PLAYER_AVAILABLE = False
    logger.info("TkinterVideo not available - direct playback disabled, external playback available")


class UnifiedVideoPlayer:
    """Unified video player combining Enhanced and Modern player features"""
    
    def __init__(self, parent_frame, style="modern", width=640, height=360, playback_mode="auto"):
        """
        Initialize unified video player
        
        Args:
            parent_frame: Parent tkinter widget
            style: "modern" (light theme) or "enhanced" (dark theme)
            width: Default video width
            height: Default video height
            playback_mode: "auto", "direct", or "external"
        """
        self.parent_frame = parent_frame
        self.style = style
        self.width = width
        self.height = height
        
        # Determine playback mode
        if playback_mode == "auto":
            self.playback_mode = "direct" if VIDEO_PLAYER_AVAILABLE else "external"
        else:
            self.playback_mode = playback_mode
        
        # Enhanced player state
        self.video_player = None
        self.video_path = None
        self.is_playing = False
        self.is_paused = False
        self.duration = 0
        self.current_time = 0
        self.volume = 50
        self.is_fullscreen = False
        self.controls_visible = True
        self.mouse_idle_timer = None
        
        # Modern player state
        self.current_video_url = None
        self.current_video_file = None
        self.thumbnail_image = None
        
        # Theme configurations
        self.themes = {
            "enhanced": {
                "bg_main": "#000000",
                "bg_controls": "#1a1a1a", 
                "bg_container": "#000000",
                "fg_primary": "#FFFFFF",
                "fg_secondary": "#bdc3c7",
                "btn_play": "#FF0000",
                "btn_play_active": "#CC0000",
                "btn_secondary": "#333333",
                "btn_secondary_active": "#555555",
                "btn_browse": "#0066CC",
                "btn_browse_active": "#0052A3"
            },
            "modern": {
                "bg_main": "#f8f9fa",
                "bg_controls": "#f8f9fa",
                "bg_container": "#ffffff", 
                "fg_primary": "#2c3e50",
                "fg_secondary": "#7f8c8d",
                "btn_play": "#3498db",
                "btn_play_active": "#2980b9",
                "btn_secondary": "#95a5a6",
                "btn_secondary_active": "#7f8c8d",
                "btn_browse": "#e74c3c",
                "btn_browse_active": "#c0392b"
            }
        }
        
        self.theme = self.themes[self.style]
        
        # Setup UI
        self.setup_unified_ui()
        
        # Start update loop for direct playback mode
        if self.playback_mode == "direct" and VIDEO_PLAYER_AVAILABLE:
            self.start_update_loop()
    
    def setup_unified_ui(self):
        """Setup unified UI that adapts to theme and playback mode"""
        # Configure parent frame
        self.parent_frame.columnconfigure(0, weight=1)
        self.parent_frame.rowconfigure(0, weight=1)
        
        # Main container with theme-appropriate styling
        self.main_container = tk.Frame(
            self.parent_frame,
            bg=self.theme["bg_main"],
            relief='solid',
            bd=1
        )
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.main_container.columnconfigure(0, weight=1)
        
        # Setup header (Modern style) or skip for Enhanced
        if self.style == "modern":
            self.setup_video_header()
            self.main_container.rowconfigure(1, weight=1)
        else:
            self.main_container.rowconfigure(0, weight=1)
        
        # Video display area
        self.setup_video_display()
        
        # Controls (different for each style and mode)
        self.setup_unified_controls()
        
        # Enhanced features setup
        if self.style == "enhanced":
            self.setup_mouse_events()
    
    def setup_video_header(self):
        """Setup Modern-style video header with info"""
        header_frame = tk.Frame(self.main_container, bg=self.theme["bg_main"], height=40)
        header_frame.pack(fill=tk.X, padx=10, pady=(10, 0))
        header_frame.pack_propagate(False)
        
        # Video icon and title
        title_frame = tk.Frame(header_frame, bg=self.theme["bg_main"])
        title_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        tk.Label(
            title_frame,
            text="🎬",
            font=('Arial', 16),
            bg=self.theme["bg_main"],
            fg=self.theme["fg_primary"]
        ).pack(side=tk.LEFT, padx=(0, 8))
        
        self.video_title_label = tk.Label(
            title_frame,
            text="Video Player",
            font=('Arial', 12, 'bold'),
            bg=self.theme["bg_main"],
            fg=self.theme["fg_primary"]
        )
        self.video_title_label.pack(side=tk.LEFT, anchor=tk.W)
        
        # Status indicator
        self.status_label = tk.Label(
            header_frame,
            text="Ready",
            font=('Arial', 9),
            bg=self.theme["bg_main"],
            fg=self.theme["fg_secondary"]
        )
        self.status_label.pack(side=tk.RIGHT, anchor=tk.E)
    
    def setup_video_display(self):
        """Setup video display area that adapts to theme"""
        if self.style == "enhanced":
            # Enhanced style - direct video area
            self.video_frame = tk.Frame(self.main_container, bg=self.theme["bg_container"])
            self.video_frame.pack(fill=tk.BOTH, expand=True)
        else:
            # Modern style - container with subtle shadow
            video_container = tk.Frame(
                self.main_container, 
                bg=self.theme["bg_container"],
                relief='solid',
                bd=1
            )
            video_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            video_container.columnconfigure(0, weight=1)
            video_container.rowconfigure(0, weight=1)
            
            self.video_frame = tk.Frame(video_container, bg="#000000")
            self.video_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # Setup appropriate placeholder
        self.setup_placeholder()
    
    def setup_placeholder(self):
        """Setup theme-appropriate placeholder"""
        # Clear existing content
        for widget in self.video_frame.winfo_children():
            widget.destroy()
        
        if self.style == "enhanced":
            # Enhanced placeholder
            self.video_placeholder = tk.Label(
                self.video_frame,
                text="🎬 Enhanced Video Player\n\nClick 'Browse Local Videos' or 'Recent Videos' to load a video",
                font=('Arial', 14),
                fg='#FFFFFF',
                bg='#000000',
                justify=tk.CENTER
            )
            self.video_placeholder.pack(expand=True, fill=tk.BOTH)
        else:
            # Modern placeholder
            placeholder_frame = tk.Frame(self.video_frame, bg='#2c3e50')
            placeholder_frame.pack(fill=tk.BOTH, expand=True)
            
            content_frame = tk.Frame(placeholder_frame, bg='#2c3e50')
            content_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
            
            tk.Label(
                content_frame,
                text="🎥",
                font=('Arial', 48),
                bg='#2c3e50',
                fg='#ecf0f1'
            ).pack(pady=(0, 10))
            
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
    
    def setup_unified_controls(self):
        """Setup controls that combine both Enhanced and Modern features"""
        if self.style == "enhanced":
            self.setup_enhanced_controls()
        else:
            self.setup_modern_controls()
    
    def setup_enhanced_controls(self):
        """Setup Enhanced-style controls with direct playback"""
        # Controls container with dark theme
        self.controls_frame = tk.Frame(self.main_container, bg=self.theme["bg_controls"], height=80)
        self.controls_frame.pack(fill=tk.X, side=tk.BOTTOM)
        self.controls_frame.pack_propagate(False)
        
        # Progress bar container (only for direct playback)
        if self.playback_mode == "direct":
            progress_container = tk.Frame(self.controls_frame, bg=self.theme["bg_controls"], height=25)
            progress_container.pack(fill=tk.X, pady=(5, 0))
            
            # Time labels
            self.time_frame = tk.Frame(progress_container, bg=self.theme["bg_controls"])
            self.time_frame.pack(fill=tk.X, padx=10)
            
            self.current_time_label = tk.Label(
                self.time_frame, text="0:00", fg=self.theme["fg_primary"],
                bg=self.theme["bg_controls"], font=('Arial', 9)
            )
            self.current_time_label.pack(side=tk.LEFT)
            
            self.duration_label = tk.Label(
                self.time_frame, text="0:00", fg=self.theme["fg_primary"],
                bg=self.theme["bg_controls"], font=('Arial', 9)
            )
            self.duration_label.pack(side=tk.RIGHT)
            
            # Progress bar
            self.progress_var = tk.DoubleVar()
            self.progress_bar = ttk.Scale(
                progress_container,
                from_=0, to=100,
                orient=tk.HORIZONTAL,
                variable=self.progress_var,
                command=self.on_progress_change
            )
            self.progress_bar.pack(fill=tk.X, padx=10, pady=(0, 5))
        
        # Main controls row
        controls_row = tk.Frame(self.controls_frame, bg=self.theme["bg_controls"])
        controls_row.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # Left controls (playback)
        left_controls = tk.Frame(controls_row, bg=self.theme["bg_controls"])
        left_controls.pack(side=tk.LEFT)
        
        if self.playback_mode == "direct":
            # Direct playback controls
            self.play_pause_button = tk.Button(
                left_controls,
                text="▶",
                font=('Arial', 16, 'bold'),
                fg=self.theme["fg_primary"],
                bg=self.theme["btn_play"],
                activebackground=self.theme["btn_play_active"],
                activeforeground=self.theme["fg_primary"],
                bd=0, padx=15, pady=5,
                command=self.toggle_play_pause,
                state="disabled"
            )
            self.play_pause_button.pack(side=tk.LEFT, padx=(0, 10))
            
            self.stop_button = tk.Button(
                left_controls,
                text="⏹",
                font=('Arial', 12, 'bold'),
                fg=self.theme["fg_primary"],
                bg=self.theme["btn_secondary"],
                activebackground=self.theme["btn_secondary_active"],
                activeforeground=self.theme["fg_primary"],
                bd=0, padx=8, pady=5,
                command=self.stop_video,
                state="disabled"
            )
            self.stop_button.pack(side=tk.LEFT, padx=(0, 10))
            
            # Volume control
            volume_frame = tk.Frame(left_controls, bg=self.theme["bg_controls"])
            volume_frame.pack(side=tk.LEFT, padx=(10, 0))
            
            tk.Label(volume_frame, text="🔊", fg=self.theme["fg_primary"],
                    bg=self.theme["bg_controls"], font=('Arial', 10)).pack(side=tk.LEFT)
            
            self.volume_var = tk.IntVar(value=self.volume)
            self.volume_scale = ttk.Scale(
                volume_frame,
                from_=0, to=100,
                orient=tk.HORIZONTAL,
                variable=self.volume_var,
                command=self.on_volume_change,
                length=80
            )
            self.volume_scale.pack(side=tk.LEFT, padx=(5, 0))
        else:
            # External playback button
            self.play_system_button = tk.Button(
                left_controls,
                text="▶ Play in System Player",
                font=('Arial', 10, 'bold'),
                fg=self.theme["fg_primary"],
                bg=self.theme["btn_play"],
                activebackground=self.theme["btn_play_active"],
                activeforeground=self.theme["fg_primary"],
                bd=0, padx=20, pady=8,
                command=self.play_in_system_player,
                state='disabled'
            )
            self.play_system_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Center controls (Modern features in Enhanced theme)
        center_controls = tk.Frame(controls_row, bg=self.theme["bg_controls"])
        center_controls.pack(side=tk.LEFT, padx=20)
        
        # Browser and download buttons
        self.browser_button = tk.Button(
            center_controls,
            text="🌐 Browser",
            font=('Arial', 9),
            fg=self.theme["fg_primary"],
            bg=self.theme["btn_secondary"],
            activebackground=self.theme["btn_secondary_active"],
            activeforeground=self.theme["fg_primary"],
            bd=0, padx=12, pady=5,
            command=self.open_in_browser,
            state='disabled'
        )
        self.browser_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.download_button = tk.Button(
            center_controls,
            text="💾 Download",
            font=('Arial', 9),
            fg=self.theme["fg_primary"],
            bg="#27ae60",
            activebackground="#229954",
            activeforeground=self.theme["fg_primary"],
            bd=0, padx=12, pady=5,
            command=self.download_video,
            state='disabled'
        )
        self.download_button.pack(side=tk.LEFT, padx=5)
        
        # Right controls
        right_controls = tk.Frame(controls_row, bg=self.theme["bg_controls"])
        right_controls.pack(side=tk.RIGHT)
        
        # Fullscreen button (Enhanced feature)
        if self.playback_mode == "direct":
            self.fullscreen_button = tk.Button(
                right_controls,
                text="⛶",
                font=('Arial', 12, 'bold'),
                fg=self.theme["fg_primary"],
                bg=self.theme["btn_secondary"],
                activebackground=self.theme["btn_secondary_active"],
                activeforeground=self.theme["fg_primary"],
                bd=0, padx=8, pady=5,
                command=self.toggle_fullscreen
            )
            self.fullscreen_button.pack(side=tk.RIGHT, padx=(10, 0))
        
        # File management buttons
        file_controls = tk.Frame(right_controls, bg=self.theme["bg_controls"])
        file_controls.pack(side=tk.RIGHT, padx=(0, 10))
        
        # Browse button
        self.browse_button = tk.Button(
            file_controls,
            text="📁",
            font=('Arial', 10),
            fg=self.theme["fg_primary"],
            bg=self.theme["btn_browse"],
            activebackground=self.theme["btn_browse_active"],
            activeforeground=self.theme["fg_primary"],
            bd=0, padx=8, pady=5,
            command=self.browse_videos
        )
        self.browse_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # Recent videos button (Enhanced feature)
        self.recent_button = tk.Button(
            file_controls,
            text="🕒",
            font=('Arial', 10),
            fg=self.theme["fg_primary"],
            bg=self.theme["btn_browse"],
            activebackground=self.theme["btn_browse_active"],
            activeforeground=self.theme["fg_primary"],
            bd=0, padx=8, pady=5,
            command=self.show_recent_videos
        )
        self.recent_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # Results folder button (Modern feature)
        self.results_button = tk.Button(
            file_controls,
            text="📂",
            font=('Arial', 10),
            fg=self.theme["fg_primary"],
            bg="#f39c12",
            activebackground="#e67e22",
            activeforeground=self.theme["fg_primary"],
            bd=0, padx=8, pady=5,
            command=self.open_results_folder
        )
        self.results_button.pack(side=tk.LEFT)
    
    def setup_modern_controls(self):
        """Setup Modern-style controls with clean design"""
        controls_frame = tk.Frame(self.main_container, bg=self.theme["bg_controls"], height=60)
        controls_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        controls_frame.pack_propagate(False)
        
        # Primary actions (left side)
        primary_frame = tk.Frame(controls_frame, bg=self.theme["bg_controls"])
        primary_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        if self.playback_mode == "direct" and VIDEO_PLAYER_AVAILABLE:
            # Direct playback primary button
            self.play_pause_button = tk.Button(
                primary_frame,
                text="▶ Play Video",
                font=('Arial', 10, 'bold'),
                bg=self.theme["btn_play"],
                fg='white',
                activebackground=self.theme["btn_play_active"],
                activeforeground='white',
                relief='flat', bd=0, padx=20, pady=8,
                command=self.toggle_play_pause,
                state='disabled'
            )
            self.play_pause_button.pack(pady=5)
        else:
            # System player primary button
            self.play_system_button = tk.Button(
                primary_frame,
                text="▶ Play in System Player",
                font=('Arial', 10, 'bold'),
                bg=self.theme["btn_play"],
                fg='white',
                activebackground=self.theme["btn_play_active"],
                activeforeground='white',
                relief='flat', bd=0, padx=20, pady=8,
                command=self.play_in_system_player,
                state='disabled'
            )
            self.play_system_button.pack(pady=5)
        
        # Secondary actions (center)
        secondary_frame = tk.Frame(controls_frame, bg=self.theme["bg_controls"])
        secondary_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        # Browser button
        self.browser_button = tk.Button(
            secondary_frame,
            text="🌐 Open in Browser",
            font=('Arial', 9),
            bg=self.theme["btn_secondary"],
            fg='white',
            activebackground=self.theme["btn_secondary_active"],
            activeforeground='white',
            relief='flat', bd=0, padx=15, pady=8,
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
            relief='flat', bd=0, padx=15, pady=8,
            command=self.download_video,
            state='disabled'
        )
        self.download_button.pack(side=tk.LEFT, padx=5)
        
        # File management (right side)
        file_frame = tk.Frame(controls_frame, bg=self.theme["bg_controls"])
        file_frame.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Browse Videos button
        tk.Button(
            file_frame,
            text="📁 Browse Videos",
            font=('Arial', 9),
            bg=self.theme["btn_browse"],
            fg='white',
            activebackground=self.theme["btn_browse_active"],
            activeforeground='white',
            relief='flat', bd=0, padx=15, pady=8,
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
            relief='flat', bd=0, padx=15, pady=8,
            command=self.open_results_folder
        ).pack(side=tk.RIGHT, padx=5)
        
        # Recent Videos button (Enhanced feature in Modern theme)
        tk.Button(
            file_frame,
            text="🕒 Recent Videos",
            font=('Arial', 9),
            bg=self.theme["btn_browse"],
            fg='white',
            activebackground=self.theme["btn_browse_active"],
            activeforeground='white',
            relief='flat', bd=0, padx=15, pady=8,
            command=self.show_recent_videos
        ).pack(side=tk.RIGHT, padx=5)
    
    def setup_mouse_events(self):
        """Setup Enhanced-style mouse events for auto-hide controls"""
        if self.style != "enhanced":
            return
        
        def on_mouse_motion(event):
            self.show_controls()
            self.reset_mouse_timer()
        
        def on_mouse_leave(event):
            self.reset_mouse_timer()
        
        # Bind to all relevant widgets
        widgets_to_bind = [self.main_container, self.video_frame]
        if hasattr(self, 'video_placeholder'):
            widgets_to_bind.append(self.video_placeholder)
        
        for widget in widgets_to_bind:
            widget.bind('<Motion>', on_mouse_motion)
            widget.bind('<Leave>', on_mouse_leave)
    
    def reset_mouse_timer(self):
        """Reset Enhanced-style mouse idle timer"""
        if self.style != "enhanced":
            return
        
        if self.mouse_idle_timer:
            self.main_container.after_cancel(self.mouse_idle_timer)
        
        # Hide controls after 3 seconds of inactivity (only when playing)
        if self.is_playing and not self.is_paused:
            self.mouse_idle_timer = self.main_container.after(3000, self.hide_controls)
    
    def show_controls(self):
        """Show Enhanced-style video controls"""
        if self.style != "enhanced":
            return
        
        if not self.controls_visible:
            self.controls_frame.pack(fill=tk.X, side=tk.BOTTOM)
            self.controls_visible = True
    
    def hide_controls(self):
        """Hide Enhanced-style video controls"""
        if self.style != "enhanced":
            return
        
        if self.controls_visible and self.is_playing and not self.is_paused:
            self.controls_frame.pack_forget()
            self.controls_visible = False
    
    # === VIDEO LOADING METHODS (Unified) ===
    
    def load_video(self, video_source, source_type="auto"):
        """
        Unified video loading method
        
        Args:
            video_source: URL string or file path
            source_type: "auto", "url", "file"
        """
        # Determine source type automatically if needed
        if source_type == "auto":
            if video_source.startswith(('http://', 'https://')):
                source_type = "url"
            else:
                source_type = "file"
        
        if source_type == "url":
            self.load_video_url(video_source)
        else:
            self.load_video_file(video_source)
    
    def load_video_url(self, video_url):
        """Load video from URL (Modern player functionality)"""
        self.current_video_url = video_url
        self.current_video_file = None
        
        # Update UI
        self.update_video_display(video_url, is_local=False)
        self.enable_controls_for_url()
        
        # Update status and title
        if hasattr(self, 'status_label'):
            self.status_label.config(text="Video loaded", fg='#27ae60')
        if hasattr(self, 'video_title_label'):
            self.video_title_label.config(text="Generated Video")
        
        logger.info(f"Video URL loaded: {video_url}")
    
    def load_video_file(self, video_path):
        """Load local video file (Enhanced + Modern functionality)"""
        if not os.path.exists(video_path):
            show_error("File Error", f"Video file not found: {video_path}")
            return False
        
        # Store both modern and enhanced state
        self.current_video_file = video_path
        self.current_video_url = None
        self.video_path = video_path
        
        if self.playback_mode == "direct" and VIDEO_PLAYER_AVAILABLE:
            # Load for direct playback (Enhanced functionality)
            return self._load_video_for_direct_playback(video_path)
        else:
            # Load for external playback (Modern functionality)
            self.update_video_display(video_path, is_local=True)
            self.enable_controls_for_local()
            
            # Update status and title
            if hasattr(self, 'status_label'):
                self.status_label.config(text="Local video loaded", fg='#27ae60')
            if hasattr(self, 'video_title_label'):
                filename = os.path.basename(video_path)
                self.video_title_label.config(text=filename)
            
            logger.info(f"Local video loaded for external playback: {video_path}")
            return True
    
    def _load_video_for_direct_playback(self, video_path):
        """Load video for direct playback (Enhanced functionality)"""
        try:
            # Load video in a separate thread to avoid blocking UI
            threading.Thread(target=self._load_video_thread, args=(video_path,), daemon=True).start()
            return True
        except Exception as e:
            error_msg = f"Failed to start video loading: {str(e)}"
            logger.error(error_msg)
            show_error("Video Load Error", error_msg)
            return False
    
    def _load_video_thread(self, video_path):
        """Load video in background thread (Enhanced functionality)"""
        try:
            # Schedule the actual loading on the main thread
            self.main_container.after(0, lambda: self._load_video_main_thread(video_path))
        except Exception as e:
            logger.error(f"Video loading thread error: {e}")
            self.main_container.after(0, lambda: show_error("Video Load Error", f"Failed to load video: {str(e)}"))
    
    def _load_video_main_thread(self, video_path):
        """Load video on main thread for direct playback (Enhanced functionality)"""
        try:
            # Remove placeholder if it exists
            if hasattr(self, 'video_placeholder') and self.video_placeholder:
                self.video_placeholder.destroy()
                self.video_placeholder = None
            
            # Remove existing player if any
            if self.video_player:
                try:
                    self.video_player.destroy()
                except:
                    pass  # Ignore errors when destroying old player
            
            # Create new video player with better sizing
            self.video_player = TkinterVideo(
                master=self.video_frame,
                scaled=True,
                keep_aspect=True
            )
            self.video_player.pack(fill=tk.BOTH, expand=True)
            
            # Load the video with comprehensive error handling
            try:
                self.video_player.load(video_path)
                logger.info("Video loaded successfully for direct playback")
            except AttributeError as e:
                if 'fast_seek' in str(e):
                    logger.warning(f"Video player compatibility issue (fast_seek): {e}")
                    logger.info("Video should still work despite this warning")
                    # Continue execution - the video should still work
                else:
                    logger.error(f"Video loading AttributeError: {e}")
                    raise e
            except Exception as e:
                logger.error(f"Video loading error: {e}")
                raise e
            
            # Enable controls and get video info
            self.enable_controls_for_direct()
            self.get_video_info()
            
            # Update title and status
            if hasattr(self, 'video_title_label'):
                filename = os.path.basename(video_path)
                self.video_title_label.config(text=filename)
            if hasattr(self, 'status_label'):
                self.status_label.config(text="Direct playback ready", fg='#27ae60')
            
            # Show success message
            filename = os.path.basename(video_path)
            show_success("Video Loaded", f"Successfully loaded: {filename}")
            
            logger.info(f"Enhanced video player loaded: {video_path}")
            
        except Exception as e:
            error_msg = f"Failed to load video: {str(e)}"
            logger.error(error_msg)
            show_error("Video Load Error", error_msg)
    
    def update_video_display(self, video_source, is_local=False):
        """Update video display with info (Modern player functionality)"""
        # Clear existing content
        for widget in self.video_frame.winfo_children():
            widget.destroy()
        
        # Create video info display
        if self.style == "enhanced":
            bg_color = "#34495e"
        else:
            bg_color = "#34495e"
        
        info_frame = tk.Frame(self.video_frame, bg=bg_color)
        info_frame.pack(fill=tk.BOTH, expand=True)
        
        # Centered content
        content_frame = tk.Frame(info_frame, bg=bg_color)
        content_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # Video ready icon
        tk.Label(
            content_frame,
            text="🎬" if is_local else "🎥",
            font=('Arial', 64),
            bg=bg_color,
            fg='#ecf0f1'
        ).pack(pady=(0, 15))
        
        # Status text
        status_text = "Local Video Ready" if is_local else "Generated Video Ready"
        tk.Label(
            content_frame,
            text=status_text,
            font=('Arial', 16, 'bold'),
            bg=bg_color,
            fg='#ecf0f1'
        ).pack(pady=(0, 5))
        
        # Instructions
        if self.playback_mode == "direct":
            instruction = "Click 'Play' to watch directly" if is_local else "Choose your preferred viewing option below"
        else:
            instruction = "Click 'Play in System Player' to watch" if is_local else "Choose your preferred viewing option below"
        
        tk.Label(
            content_frame,
            text=instruction,
            font=('Arial', 11),
            bg=bg_color,
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
            bg=bg_color,
            fg='#95a5a6',
            wraplength=400
        ).pack(pady=(10, 0))
    
    def get_video_info(self):
        """Get video information for direct playback (Enhanced functionality)"""
        try:
            if self.video_player:
                # Try to get duration (this might not work with all video formats)
                self.duration = 100  # Will be updated during playback
                self.update_duration_display()
        except Exception as e:
            logger.warning(f"Could not get video duration: {e}")
    
    # === CONTROL STATE MANAGEMENT ===
    
    def enable_controls_for_url(self):
        """Enable controls for URL video"""
        if hasattr(self, 'play_system_button'):
            self.play_system_button.config(state='normal')
        if hasattr(self, 'play_pause_button'):
            self.play_pause_button.config(state='normal')
        if hasattr(self, 'browser_button'):
            self.browser_button.config(state='normal')
        if hasattr(self, 'download_button'):
            self.download_button.config(state='normal')
    
    def enable_controls_for_local(self):
        """Enable controls for local video file"""
        if hasattr(self, 'play_system_button'):
            self.play_system_button.config(state='normal')
        if hasattr(self, 'play_pause_button'):
            self.play_pause_button.config(state='normal')
        if hasattr(self, 'browser_button'):
            self.browser_button.config(state='disabled')  # Can't browse to local files
        if hasattr(self, 'download_button'):
            self.download_button.config(state='disabled')  # Already local
    
    def enable_controls_for_direct(self):
        """Enable controls for direct playback (Enhanced functionality)"""
        if hasattr(self, 'play_pause_button'):
            self.play_pause_button.config(state="normal")
        if hasattr(self, 'stop_button'):
            self.stop_button.config(state="normal")
    
    def disable_controls(self):
        """Disable all controls"""
        controls = ['play_system_button', 'play_pause_button', 'stop_button', 
                   'browser_button', 'download_button']
        for control in controls:
            if hasattr(self, control):
                getattr(self, control).config(state='disabled')
    
    # === PLAYBACK CONTROL METHODS (Enhanced functionality) ===
    
    def toggle_play_pause(self):
        """Toggle between play and pause (Enhanced functionality)"""
        if not self.video_player and self.playback_mode == "direct":
            return
        
        if self.playback_mode == "external":
            # For external mode, this acts as system player launcher
            self.play_in_system_player()
            return
        
        try:
            if not self.is_playing or self.is_paused:
                self.play_video()
            else:
                self.pause_video()
        except Exception as e:
            show_error("Playback Error", f"Failed to toggle playback: {str(e)}")
    
    def play_video(self):
        """Play the video (Enhanced functionality)"""
        if not self.video_player or self.playback_mode != "direct":
            return
        
        try:
            self.video_player.play()
            self.is_playing = True
            self.is_paused = False
            
            # Update button appearance
            if hasattr(self, 'play_pause_button'):
                if self.style == "enhanced":
                    self.play_pause_button.config(text="⏸", bg='#FF6B6B')
                else:
                    self.play_pause_button.config(text="⏸ Pause Video")
            
            self.reset_mouse_timer()
            logger.info("Video playback started")
        except Exception as e:
            show_error("Playback Error", f"Failed to play video: {str(e)}")
    
    def pause_video(self):
        """Pause the video (Enhanced functionality)"""
        if not self.video_player or self.playback_mode != "direct":
            return
        
        try:
            self.video_player.pause()
            self.is_paused = True
            
            # Update button appearance
            if hasattr(self, 'play_pause_button'):
                if self.style == "enhanced":
                    self.play_pause_button.config(text="▶", bg='#FF0000')
                else:
                    self.play_pause_button.config(text="▶ Play Video")
            
            self.show_controls()  # Show controls when paused
            logger.info("Video playback paused")
        except Exception as e:
            show_error("Playback Error", f"Failed to pause video: {str(e)}")
    
    def stop_video(self):
        """Stop the video (Enhanced functionality)"""
        if not self.video_player or self.playback_mode != "direct":
            return
        
        try:
            self.video_player.stop()
            self.is_playing = False
            self.is_paused = False
            self.current_time = 0
            
            if hasattr(self, 'progress_var'):
                self.progress_var.set(0)
            if hasattr(self, 'play_pause_button'):
                if self.style == "enhanced":
                    self.play_pause_button.config(text="▶", bg='#FF0000')
                else:
                    self.play_pause_button.config(text="▶ Play Video")
            
            self.show_controls()
            self.update_time_display()
            logger.info("Video playback stopped")
        except Exception as e:
            show_error("Playback Error", f"Failed to stop video: {str(e)}")
    
    def on_progress_change(self, value):
        """Handle progress bar changes for seeking (Enhanced functionality)"""
        if not self.video_player or not self.is_playing or self.playback_mode != "direct":
            return
        
        try:
            # Convert percentage to time and seek
            seek_time = (float(value) / 100.0) * self.duration
            logger.info(f"Seeking to: {seek_time}s ({value}%)")
            # Note: Seeking might not be available in all video formats
        except Exception as e:
            logger.warning(f"Seeking failed: {e}")
    
    def on_volume_change(self, value):
        """Handle volume changes (Enhanced functionality)"""
        try:
            self.volume = int(float(value))
            if self.video_player and self.playback_mode == "direct":
                # Note: Volume control might not be available in all implementations
                logger.info(f"Volume changed to: {self.volume}%")
        except Exception as e:
            logger.warning(f"Volume change failed: {e}")
    
    # === EXTERNAL PLAYBACK METHODS (Modern functionality) ===
    
    def play_in_system_player(self):
        """Open video in system's default video player (Modern functionality)"""
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
        """Open file with system's default video player (Modern functionality)"""
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
            
            if hasattr(self, 'status_label'):
                self.status_label.config(text="Opened in system player", fg='#27ae60')
            
        except Exception as e:
            logger.error(f"Error opening with system player: {e}")
            show_error("System Player Error", f"Failed to open video: {str(e)}")
    
    def download_and_play(self):
        """Download video and play in system player (Modern functionality)"""
        if not self.current_video_url:
            return
        
        def download_thread():
            try:
                if hasattr(self, 'status_label'):
                    self.main_container.after(0, lambda: self.status_label.config(text="Downloading video...", fg='#f39c12'))
                
                # Download to temp file
                response = requests.get(self.current_video_url, stream=True)
                response.raise_for_status()
                
                # Create temp file with proper extension
                with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp_file:
                    for chunk in response.iter_content(chunk_size=8192):
                        temp_file.write(chunk)
                    temp_path = temp_file.name
                
                # Open with system player
                self.main_container.after(0, lambda: self.open_file_with_system_player(temp_path))
                
            except Exception as e:
                logger.error(f"Error downloading video: {e}")
                self.main_container.after(0, lambda: show_error("Download Error", f"Failed to download video: {str(e)}"))
                if hasattr(self, 'status_label'):
                    self.main_container.after(0, lambda: self.status_label.config(text="Download failed", fg='#e74c3c'))
        
        # Start download in background
        threading.Thread(target=download_thread, daemon=True).start()
    
    def open_in_browser(self):
        """Open video URL in web browser (Modern functionality)"""
        if not self.current_video_url:
            show_error("No Video URL", "No video URL available to open in browser.")
            return
        
        try:
            webbrowser.open(self.current_video_url)
            if hasattr(self, 'status_label'):
                self.status_label.config(text="Opened in browser", fg='#27ae60')
        except Exception as e:
            logger.error(f"Error opening browser: {e}")
            show_error("Browser Error", f"Failed to open browser: {str(e)}")
    
    def download_video(self):
        """Download video to user's chosen location (Modern functionality)"""
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
                if hasattr(self, 'status_label'):
                    self.main_container.after(0, lambda: self.status_label.config(text="Downloading...", fg='#f39c12'))
                
                response = requests.get(self.current_video_url, stream=True)
                response.raise_for_status()
                
                with open(file_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                if hasattr(self, 'status_label'):
                    self.main_container.after(0, lambda: self.status_label.config(text="Download complete", fg='#27ae60'))
                
            except Exception as e:
                logger.error(f"Error downloading video: {e}")
                self.main_container.after(0, lambda: show_error("Download Error", f"Failed to download video: {str(e)}"))
                if hasattr(self, 'status_label'):
                    self.main_container.after(0, lambda: self.status_label.config(text="Download failed", fg='#e74c3c'))
        
        # Start download in background
        threading.Thread(target=download_thread, daemon=True).start()
    
    # === FULLSCREEN METHODS (Enhanced functionality) ===
    
    def toggle_fullscreen(self):
        """Toggle fullscreen mode (Enhanced functionality)"""
        if self.playback_mode != "direct":
            return
        
        try:
            if not self.is_fullscreen:
                self.enter_fullscreen()
            else:
                self.exit_fullscreen()
        except Exception as e:
            show_error("Fullscreen Error", f"Failed to toggle fullscreen: {str(e)}")
    
    def enter_fullscreen(self):
        """Enter fullscreen mode (Enhanced functionality)"""
        if not self.video_player:
            return
        
        # Create fullscreen window
        self.fullscreen_window = tk.Toplevel(self.main_container)
        self.fullscreen_window.attributes('-fullscreen', True)
        self.fullscreen_window.configure(bg='#000000')
        
        # Move video player to fullscreen window
        self.video_player.pack_forget()
        self.video_player.pack(fill=tk.BOTH, expand=True, in_=self.fullscreen_window)
        
        self.is_fullscreen = True
        if hasattr(self, 'fullscreen_button'):
            self.fullscreen_button.config(text="⛶")
        
        # Bind escape key to exit fullscreen
        self.fullscreen_window.bind('<Escape>', lambda e: self.exit_fullscreen())
        self.fullscreen_window.focus_set()
        
        logger.info("Entered fullscreen mode")
    
    def exit_fullscreen(self):
        """Exit fullscreen mode (Enhanced functionality)"""
        if hasattr(self, 'fullscreen_window') and self.fullscreen_window:
            # Move video player back to main container
            self.video_player.pack_forget()
            self.video_player.pack(fill=tk.BOTH, expand=True, in_=self.video_frame)
            
            # Destroy fullscreen window
            self.fullscreen_window.destroy()
            self.fullscreen_window = None
        
        self.is_fullscreen = False
        if hasattr(self, 'fullscreen_button'):
            self.fullscreen_button.config(text="⛶")
        
        logger.info("Exited fullscreen mode")
    
    # === FILE MANAGEMENT METHODS ===
    
    def browse_videos(self):
        """Browse for video files (Combined Enhanced + Modern functionality)"""
        try:
            from tkinter import filedialog
            
            # Start in results folder if it exists
            initial_dir = os.path.join(os.getcwd(), "WaveSpeed_Results")
            if not os.path.exists(initial_dir):
                initial_dir = os.getcwd()
            
            file_path = filedialog.askopenfilename(
                title="Select Video File",
                initialdir=initial_dir,
                filetypes=[
                    ("Video files", "*.mp4 *.avi *.mov *.mkv *.wmv *.flv *.webm"),
                    ("MP4 files", "*.mp4"),
                    ("All files", "*.*")
                ]
            )
            
            if file_path:
                self.load_video_file(file_path)
                
        except Exception as e:
            show_error("Browse Error", f"Failed to browse for videos: {str(e)}")
    
    def show_recent_videos(self):
        """Show recent videos dialog (Enhanced functionality)"""
        try:
            from core.auto_save import auto_save_manager
            
            # Get recent video files
            recent_files = auto_save_manager.get_recent_files(limit=10)
            video_files = [f for f in recent_files if f.get('file_path', '').lower().endswith(('.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm'))]
            
            if not video_files:
                show_error("No Videos", "No recent video files found.")
                return
            
            # Show selection dialog
            self._show_video_selection_dialog(video_files)
            
        except Exception as e:
            show_error("Error", f"Failed to get recent videos: {str(e)}")
    
    def _show_video_selection_dialog(self, video_files):
        """Show video selection dialog (Enhanced functionality)"""
        try:
            # Create selection window
            selection_window = tk.Toplevel(self.main_container)
            selection_window.title("Select Video")
            selection_window.geometry("600x400")
            selection_window.configure(bg='#f0f0f0')
            
            # Make it modal
            selection_window.transient(self.main_container.winfo_toplevel())
            selection_window.grab_set()
            
            # Title
            title_label = ttk.Label(selection_window, text="Select a video to play:", font=('Arial', 12, 'bold'))
            title_label.pack(pady=10)
            
            # Listbox with scrollbar
            list_frame = ttk.Frame(selection_window)
            list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 10))
            
            listbox = tk.Listbox(list_frame, font=('Arial', 10), height=15)
            scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=listbox.yview)
            listbox.configure(yscrollcommand=scrollbar.set)
            
            listbox.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            
            # Populate listbox
            for video_file in video_files:
                file_path = video_file.get('file_path', '')
                file_name = os.path.basename(file_path)
                created_time = video_file.get('created', 'Unknown')
                display_text = f"{file_name} ({created_time})"
                listbox.insert(tk.END, display_text)
            
            # Buttons
            button_frame = ttk.Frame(selection_window)
            button_frame.pack(pady=10)
            
            def on_play_selected():
                selection = listbox.curselection()
                if selection:
                    selected_video = video_files[selection[0]]
                    video_path = selected_video.get('file_path', '')
                    if video_path and os.path.exists(video_path):
                        selection_window.destroy()
                        self.load_video_file(video_path)
                    else:
                        show_error("File Error", "Selected video file not found.")
                else:
                    show_error("Selection Error", "Please select a video file.")
            
            # Double-click to play
            listbox.bind('<Double-Button-1>', lambda e: on_play_selected())
            
            ttk.Button(button_frame, text="Play Selected", command=on_play_selected).pack(side=tk.LEFT, padx=5)
            ttk.Button(button_frame, text="Cancel", command=selection_window.destroy).pack(side=tk.LEFT, padx=5)
            
            # Focus and select first item
            selection_window.focus_set()
            if video_files:
                listbox.selection_set(0)
                
        except Exception as e:
            show_error("Dialog Error", f"Failed to show video selection: {str(e)}")
    
    def open_results_folder(self):
        """Open the results folder (Modern functionality)"""
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
            
            if hasattr(self, 'status_label'):
                self.status_label.config(text="Results folder opened", fg='#27ae60')
            
        except Exception as e:
            logger.error(f"Error opening results folder: {e}")
            show_error("Folder Error", f"Failed to open results folder: {str(e)}")
    
    def clear_video(self):
        """Clear current video and return to placeholder (Modern functionality)"""
        self.current_video_url = None
        self.current_video_file = None
        self.video_path = None
        
        # Stop any current playback
        if self.is_playing:
            self.stop_video()
        
        # Remove video player if exists
        if self.video_player:
            try:
                self.video_player.destroy()
                self.video_player = None
            except:
                pass
        
        # Reset state
        self.is_playing = False
        self.is_paused = False
        self.current_time = 0
        self.duration = 0
        
        # Setup placeholder
        self.setup_placeholder()
        self.disable_controls()
        
        # Update status
        if hasattr(self, 'status_label'):
            self.status_label.config(text="Ready", fg=self.theme["fg_secondary"])
        if hasattr(self, 'video_title_label'):
            self.video_title_label.config(text="Video Player")
    
    # === THEME AND CONFIGURATION METHODS ===
    
    def set_theme(self, theme_name):
        """Change theme (Enhanced/Modern)"""
        if theme_name not in self.themes:
            logger.warning(f"Unknown theme: {theme_name}")
            return
        
        self.style = theme_name
        self.theme = self.themes[theme_name]
        
        # Rebuild UI with new theme
        # This would require rebuilding the entire UI - complex operation
        logger.info(f"Theme set to: {theme_name}")
        # Note: Full theme switching would require UI rebuild
    
    def set_playback_mode(self, mode):
        """Change playback mode (direct/external)"""
        if mode == "direct" and not VIDEO_PLAYER_AVAILABLE:
            show_warning("Direct Playback Unavailable", 
                        "TkinterVideo not available. Keeping external playback mode.")
            return
        
        if mode in ["direct", "external"]:
            self.playback_mode = mode
            logger.info(f"Playback mode set to: {mode}")
            # Note: Full mode switching would require UI rebuild
        else:
            logger.warning(f"Unknown playback mode: {mode}")
    
    # === PROGRESS TRACKING AND TIME DISPLAY (Enhanced functionality) ===
    
    def start_update_loop(self):
        """Start the update loop for progress tracking (Enhanced functionality)"""
        if self.playback_mode == "direct":
            self.update_progress()
    
    def update_progress(self):
        """Update progress bar and time displays (Enhanced functionality)"""
        try:
            if (self.video_player and self.is_playing and not self.is_paused 
                and self.playback_mode == "direct"):
                # This is a simplified progress update
                # In a real implementation, you'd get the actual current time from the video player
                self.current_time += 0.1
                if self.duration > 0:
                    progress = (self.current_time / self.duration) * 100
                    if hasattr(self, 'progress_var'):
                        self.progress_var.set(min(progress, 100))
                
                self.update_time_display()
            
            # Schedule next update
            self.main_container.after(100, self.update_progress)
            
        except Exception as e:
            # Silently handle errors to avoid spam
            pass
    
    def update_time_display(self):
        """Update time display labels (Enhanced functionality)"""
        try:
            if hasattr(self, 'current_time_label') and hasattr(self, 'duration_label'):
                current_str = self.format_time(self.current_time)
                duration_str = self.format_time(self.duration)
                
                self.current_time_label.config(text=current_str)
                self.duration_label.config(text=duration_str)
        except Exception as e:
            pass
    
    def update_duration_display(self):
        """Update duration display (Enhanced functionality)"""
        try:
            if hasattr(self, 'duration_label'):
                duration_str = self.format_time(self.duration)
                self.duration_label.config(text=duration_str)
        except Exception as e:
            pass
    
    def format_time(self, seconds):
        """Format time in MM:SS format (Enhanced functionality)"""
        try:
            minutes = int(seconds // 60)
            seconds = int(seconds % 60)
            return f"{minutes}:{seconds:02d}"
        except:
            return "0:00"
    
    # === CLEANUP AND UTILITY METHODS ===
    
    def cleanup(self):
        """Cleanup resources"""
        try:
            # Cancel timers
            if self.mouse_idle_timer:
                self.main_container.after_cancel(self.mouse_idle_timer)
            
            # Close fullscreen if open
            if hasattr(self, 'fullscreen_window') and self.fullscreen_window:
                self.fullscreen_window.destroy()
            
            # Destroy video player
            if self.video_player:
                self.video_player.destroy()
                
        except Exception as e:
            logger.warning(f"Cleanup error: {e}")
    
    # === COMPATIBILITY METHODS ===
    
    def load_video_url_compat(self, video_url):
        """Compatibility method for ModernVideoPlayer interface"""
        return self.load_video_url(video_url)
    
    def load_video_file_compat(self, video_path):
        """Compatibility method for ModernVideoPlayer interface"""
        return self.load_video_file(video_path)
    
    def get_video_player_status(self):
        """Get current player status for debugging"""
        return {
            "style": self.style,
            "playback_mode": self.playback_mode,
            "video_player_available": VIDEO_PLAYER_AVAILABLE,
            "current_video_url": self.current_video_url,
            "current_video_file": self.current_video_file,
            "is_playing": self.is_playing,
            "is_paused": self.is_paused,
            "is_fullscreen": self.is_fullscreen
        }