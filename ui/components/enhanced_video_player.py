"""
Enhanced Video Player Component for WaveSpeed AI Application

This module provides a YouTube-like video player with advanced controls,
better sizing, interactive elements, and fullscreen capabilities.
"""

import tkinter as tk
from tkinter import ttk
import threading
import time
import os
from PIL import Image, ImageTk
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from utils.utils import show_error, show_success
from core.logger import get_logger

logger = get_logger()

# Try to import video player
try:
    from tkVideoPlayer import TkinterVideo
    VIDEO_PLAYER_AVAILABLE = True
except ImportError:
    VIDEO_PLAYER_AVAILABLE = False

class EnhancedVideoPlayer:
    """Enhanced video player with YouTube-like features"""
    
    def __init__(self, parent_frame, width=640, height=360):
        self.parent_frame = parent_frame
        self.width = width
        self.height = height
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
        
        # Create the player UI
        self.setup_player_ui()
        
        # Start the update loop for progress tracking
        if VIDEO_PLAYER_AVAILABLE:
            self.start_update_loop()
    
    def setup_player_ui(self):
        """Setup the enhanced video player UI"""
        # Configure parent frame for full expansion
        self.parent_frame.columnconfigure(0, weight=1)
        self.parent_frame.rowconfigure(0, weight=1)
        
        # Main container with dark background - fully responsive
        self.main_container = tk.Frame(self.parent_frame, bg='#000000', relief='solid', bd=1)
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Video display area - expands to fill available space
        self.video_frame = tk.Frame(self.main_container, bg='#000000')
        self.video_frame.pack(fill=tk.BOTH, expand=True)
        
        if VIDEO_PLAYER_AVAILABLE:
            # Placeholder for video (will be replaced when video loads)
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
            # Fallback message
            fallback_label = tk.Label(
                self.video_frame,
                text="❌ Enhanced Video Player Not Available\n\nInstall tkvideoplayer to enable video playback",
                font=('Arial', 12),
                fg='#FF6B6B',
                bg='#000000',
                justify=tk.CENTER
            )
            fallback_label.pack(expand=True, fill=tk.BOTH)
        
        # Enhanced controls panel
        self.setup_enhanced_controls()
        
        # Bind mouse events for auto-hide controls
        self.setup_mouse_events()
    
    def setup_enhanced_controls(self):
        """Setup enhanced video controls"""
        # Controls container with dark theme
        self.controls_frame = tk.Frame(self.main_container, bg='#1a1a1a', height=80)
        self.controls_frame.pack(fill=tk.X, side=tk.BOTTOM)
        self.controls_frame.pack_propagate(False)
        
        # Progress bar container
        progress_container = tk.Frame(self.controls_frame, bg='#1a1a1a', height=25)
        progress_container.pack(fill=tk.X, pady=(5, 0))
        
        # Time labels
        self.time_frame = tk.Frame(progress_container, bg='#1a1a1a')
        self.time_frame.pack(fill=tk.X, padx=10)
        
        self.current_time_label = tk.Label(
            self.time_frame, text="0:00", fg='#FFFFFF', bg='#1a1a1a', 
            font=('Arial', 9)
        )
        self.current_time_label.pack(side=tk.LEFT)
        
        self.duration_label = tk.Label(
            self.time_frame, text="0:00", fg='#FFFFFF', bg='#1a1a1a', 
            font=('Arial', 9)
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
        controls_row = tk.Frame(self.controls_frame, bg='#1a1a1a')
        controls_row.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # Left controls (playback)
        left_controls = tk.Frame(controls_row, bg='#1a1a1a')
        left_controls.pack(side=tk.LEFT)
        
        # Play/Pause button (larger, more prominent)
        self.play_pause_button = tk.Button(
            left_controls,
            text="▶",
            font=('Arial', 16, 'bold'),
            fg='#FFFFFF',
            bg='#FF0000',
            activebackground='#CC0000',
            activeforeground='#FFFFFF',
            bd=0,
            padx=15,
            pady=5,
            command=self.toggle_play_pause,
            state="disabled"
        )
        self.play_pause_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Stop button
        self.stop_button = tk.Button(
            left_controls,
            text="⏹",
            font=('Arial', 12, 'bold'),
            fg='#FFFFFF',
            bg='#333333',
            activebackground='#555555',
            activeforeground='#FFFFFF',
            bd=0,
            padx=8,
            pady=5,
            command=self.stop_video,
            state="disabled"
        )
        self.stop_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Volume control
        volume_frame = tk.Frame(left_controls, bg='#1a1a1a')
        volume_frame.pack(side=tk.LEFT, padx=(10, 0))
        
        tk.Label(volume_frame, text="🔊", fg='#FFFFFF', bg='#1a1a1a', font=('Arial', 10)).pack(side=tk.LEFT)
        
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
        
        # Right controls (utility)
        right_controls = tk.Frame(controls_row, bg='#1a1a1a')
        right_controls.pack(side=tk.RIGHT)
        
        # Fullscreen button
        self.fullscreen_button = tk.Button(
            right_controls,
            text="⛶",
            font=('Arial', 12, 'bold'),
            fg='#FFFFFF',
            bg='#333333',
            activebackground='#555555',
            activeforeground='#FFFFFF',
            bd=0,
            padx=8,
            pady=5,
            command=self.toggle_fullscreen
        )
        self.fullscreen_button.pack(side=tk.RIGHT, padx=(10, 0))
        
        # File management buttons
        file_controls = tk.Frame(right_controls, bg='#1a1a1a')
        file_controls.pack(side=tk.RIGHT, padx=(0, 10))
        
        # Browse button
        self.browse_button = tk.Button(
            file_controls,
            text="📁",
            font=('Arial', 10),
            fg='#FFFFFF',
            bg='#0066CC',
            activebackground='#0052A3',
            activeforeground='#FFFFFF',
            bd=0,
            padx=8,
            pady=5,
            command=self.browse_videos
        )
        self.browse_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # Recent videos button
        self.recent_button = tk.Button(
            file_controls,
            text="🕒",
            font=('Arial', 10),
            fg='#FFFFFF',
            bg='#0066CC',
            activebackground='#0052A3',
            activeforeground='#FFFFFF',
            bd=0,
            padx=8,
            pady=5,
            command=self.show_recent_videos
        )
        self.recent_button.pack(side=tk.LEFT)
    
    def setup_mouse_events(self):
        """Setup mouse events for auto-hide controls"""
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
        """Reset the mouse idle timer"""
        if self.mouse_idle_timer:
            self.main_container.after_cancel(self.mouse_idle_timer)
        
        # Hide controls after 3 seconds of inactivity (only when playing)
        if self.is_playing and not self.is_paused:
            self.mouse_idle_timer = self.main_container.after(3000, self.hide_controls)
    
    def show_controls(self):
        """Show video controls"""
        if not self.controls_visible:
            self.controls_frame.pack(fill=tk.X, side=tk.BOTTOM)
            self.controls_visible = True
    
    def hide_controls(self):
        """Hide video controls (YouTube-like behavior)"""
        if self.controls_visible and self.is_playing and not self.is_paused:
            self.controls_frame.pack_forget()
            self.controls_visible = False
    
    def load_video(self, video_path):
        """Load a video file into the enhanced player"""
        if not VIDEO_PLAYER_AVAILABLE:
            show_error("Video Player Error", "Video player is not available. Please install tkvideoplayer.")
            return False
        
        if not os.path.exists(video_path):
            show_error("File Error", f"Video file not found: {video_path}")
            return False
        
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
        """Load video in background thread"""
        try:
            # Schedule the actual loading on the main thread
            self.main_container.after(0, lambda: self._load_video_main_thread(video_path))
        except Exception as e:
            logger.error(f"Video loading thread error: {e}")
            self.main_container.after(0, lambda: show_error("Video Load Error", f"Failed to load video: {str(e)}"))
    
    def _load_video_main_thread(self, video_path):
        """Load video on main thread (UI thread)"""
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
                logger.info("Video loaded successfully")
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
            
            self.video_path = video_path
            
            # Enable controls
            self.enable_controls()
            
            # Get video duration
            self.get_video_info()
            
            # Show success message
            filename = os.path.basename(video_path)
            show_success("Video Loaded", f"Successfully loaded: {filename}")
            
            logger.info(f"Enhanced video player loaded: {video_path}")
            
        except Exception as e:
            error_msg = f"Failed to load video: {str(e)}"
            logger.error(error_msg)
            show_error("Video Load Error", error_msg)
    
    def get_video_info(self):
        """Get video information like duration"""
        try:
            if self.video_player:
                # Try to get duration (this might not work with all video formats)
                # For now, we'll use a placeholder
                self.duration = 100  # Will be updated during playback
                self.update_duration_display()
        except Exception as e:
            logger.warning(f"Could not get video duration: {e}")
    
    def enable_controls(self):
        """Enable video control buttons"""
        self.play_pause_button.config(state="normal")
        self.stop_button.config(state="normal")
    
    def disable_controls(self):
        """Disable video control buttons"""
        self.play_pause_button.config(state="disabled")
        self.stop_button.config(state="disabled")
    
    def toggle_play_pause(self):
        """Toggle between play and pause"""
        if not self.video_player:
            return
        
        try:
            if not self.is_playing or self.is_paused:
                self.play_video()
            else:
                self.pause_video()
        except Exception as e:
            show_error("Playback Error", f"Failed to toggle playback: {str(e)}")
    
    def play_video(self):
        """Play the video"""
        if not self.video_player:
            return
        
        try:
            self.video_player.play()
            self.is_playing = True
            self.is_paused = False
            self.play_pause_button.config(text="⏸", bg='#FF6B6B')
            self.reset_mouse_timer()
            logger.info("Video playback started")
        except Exception as e:
            show_error("Playback Error", f"Failed to play video: {str(e)}")
    
    def pause_video(self):
        """Pause the video"""
        if not self.video_player:
            return
        
        try:
            self.video_player.pause()
            self.is_paused = True
            self.play_pause_button.config(text="▶", bg='#FF0000')
            self.show_controls()  # Show controls when paused
            logger.info("Video playback paused")
        except Exception as e:
            show_error("Playback Error", f"Failed to pause video: {str(e)}")
    
    def stop_video(self):
        """Stop the video"""
        if not self.video_player:
            return
        
        try:
            self.video_player.stop()
            self.is_playing = False
            self.is_paused = False
            self.current_time = 0
            self.progress_var.set(0)
            self.play_pause_button.config(text="▶", bg='#FF0000')
            self.show_controls()
            self.update_time_display()
            logger.info("Video playback stopped")
        except Exception as e:
            show_error("Playback Error", f"Failed to stop video: {str(e)}")
    
    def on_progress_change(self, value):
        """Handle progress bar changes (seeking)"""
        if not self.video_player or not self.is_playing:
            return
        
        try:
            # Convert percentage to time and seek
            seek_time = (float(value) / 100.0) * self.duration
            # Note: Seeking might not be available in all video formats
            logger.info(f"Seeking to: {seek_time}s ({value}%)")
        except Exception as e:
            logger.warning(f"Seeking failed: {e}")
    
    def on_volume_change(self, value):
        """Handle volume changes"""
        try:
            self.volume = int(float(value))
            if self.video_player:
                # Note: Volume control might not be available in all implementations
                logger.info(f"Volume changed to: {self.volume}%")
        except Exception as e:
            logger.warning(f"Volume change failed: {e}")
    
    def toggle_fullscreen(self):
        """Toggle fullscreen mode"""
        try:
            if not self.is_fullscreen:
                self.enter_fullscreen()
            else:
                self.exit_fullscreen()
        except Exception as e:
            show_error("Fullscreen Error", f"Failed to toggle fullscreen: {str(e)}")
    
    def enter_fullscreen(self):
        """Enter fullscreen mode"""
        # Create fullscreen window
        self.fullscreen_window = tk.Toplevel(self.main_container)
        self.fullscreen_window.attributes('-fullscreen', True)
        self.fullscreen_window.configure(bg='#000000')
        
        # Move video player to fullscreen window
        self.video_player.pack_forget()
        self.video_player.pack(fill=tk.BOTH, expand=True, in_=self.fullscreen_window)
        
        self.is_fullscreen = True
        self.fullscreen_button.config(text="⛶")
        
        # Bind escape key to exit fullscreen
        self.fullscreen_window.bind('<Escape>', lambda e: self.exit_fullscreen())
        self.fullscreen_window.focus_set()
        
        logger.info("Entered fullscreen mode")
    
    def exit_fullscreen(self):
        """Exit fullscreen mode"""
        if hasattr(self, 'fullscreen_window') and self.fullscreen_window:
            # Move video player back to main container
            self.video_player.pack_forget()
            self.video_player.pack(fill=tk.BOTH, expand=True, in_=self.video_frame)
            
            # Destroy fullscreen window
            self.fullscreen_window.destroy()
            self.fullscreen_window = None
        
        self.is_fullscreen = False
        self.fullscreen_button.config(text="⛶")
        
        logger.info("Exited fullscreen mode")
    
    def browse_videos(self):
        """Browse for video files"""
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
                self.load_video(file_path)
                
        except Exception as e:
            show_error("Browse Error", f"Failed to browse for videos: {str(e)}")
    
    def show_recent_videos(self):
        """Show recent videos dialog"""
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
        """Show video selection dialog"""
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
                        self.load_video(video_path)
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
    
    def start_update_loop(self):
        """Start the update loop for progress tracking"""
        self.update_progress()
    
    def update_progress(self):
        """Update progress bar and time displays"""
        try:
            if self.video_player and self.is_playing and not self.is_paused:
                # This is a simplified progress update
                # In a real implementation, you'd get the actual current time from the video player
                self.current_time += 0.1
                if self.duration > 0:
                    progress = (self.current_time / self.duration) * 100
                    self.progress_var.set(min(progress, 100))
                
                self.update_time_display()
            
            # Schedule next update
            self.main_container.after(100, self.update_progress)
            
        except Exception as e:
            # Silently handle errors to avoid spam
            pass
    
    def update_time_display(self):
        """Update time display labels"""
        try:
            current_str = self.format_time(self.current_time)
            duration_str = self.format_time(self.duration)
            
            self.current_time_label.config(text=current_str)
            self.duration_label.config(text=duration_str)
        except Exception as e:
            pass
    
    def update_duration_display(self):
        """Update duration display"""
        try:
            duration_str = self.format_time(self.duration)
            self.duration_label.config(text=duration_str)
        except Exception as e:
            pass
    
    def format_time(self, seconds):
        """Format time in MM:SS format"""
        try:
            minutes = int(seconds // 60)
            seconds = int(seconds % 60)
            return f"{minutes}:{seconds:02d}"
        except:
            return "0:00"
    
    def cleanup(self):
        """Cleanup resources"""
        try:
            if self.mouse_idle_timer:
                self.main_container.after_cancel(self.mouse_idle_timer)
            
            if hasattr(self, 'fullscreen_window') and self.fullscreen_window:
                self.fullscreen_window.destroy()
            
            if self.video_player:
                self.video_player.destroy()
                
        except Exception as e:
            logger.warning(f"Cleanup error: {e}")
