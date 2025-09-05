"""
SeedDance Tab Component

This module contains the ByteDance SeedDance-v1-Pro image-to-video functionality.
"""

import tkinter as tk
from tkinter import ttk
import threading
import webbrowser
import os
import requests
import tempfile
import time
from ui.components.ui_components import BaseTab, ImagePreview, SettingsPanel
from ui.components.enhanced_image_display import EnhancedImageSelector
from app.config import Config
from utils.utils import *
from core.auto_save import auto_save_manager
from core.logger import get_logger
from ui.components.video_player_mixin import VideoPlayerMixin

logger = get_logger()


class SeedDanceTab(BaseTab, VideoPlayerMixin):
    """SeedDance Image to Video Tab"""
    
    def __init__(self, parent_frame, api_client, main_app=None):
        self.main_app = main_app  # Reference to main app for cross-tab operations
        BaseTab.__init__(self, parent_frame, api_client)
        VideoPlayerMixin.__init__(self)
    
    def setup_ui(self):
        """Setup the SeedDance UI"""
        self.frame.columnconfigure(1, weight=1)
        
        # Enhanced image selector (compact for video tabs)
        self.image_selector = EnhancedImageSelector(
            self.frame, 0, self.on_image_selected, "Select Image for SeedDance Video:", show_preview=False
        )
        
        # Image preview (modified for video context)
        self.image_preview = ImagePreview(self.frame, 2, "Image & Video Preview")
        self.image_preview.result_frame.config(text="Generated Video")
        
        # Setup drag and drop
        self.image_preview.setup_drag_and_drop(self.on_drop)
        
        # Video result section (replace the image result)
        self.setup_video_result_section()
        
        # Prompt section
        self.setup_prompt_section()
        
        # Settings panel
        self.setup_settings_panel()
        
        # Progress and results (moved up since button is now sticky)
        self.setup_progress_section(6)
        self.setup_results_section(7)
        
        # Setup sticky buttons at the bottom
        buttons_config = [
            ("Generate SeedDance Video", self.process_task, "primary"),
        ]
        self.setup_sticky_buttons(buttons_config)
    
    def setup_video_result_section(self):
        """Setup video result display section"""
        self.setup_video_result_section_with_player(self.image_preview.result_frame)
    
    def setup_prompt_section(self):
        """Setup prompt section for video generation"""
        prompt_section = ttk.LabelFrame(self.frame, text="SeedDance Video Settings", padding="10")
        prompt_section.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 10))
        prompt_section.columnconfigure(0, weight=1)
        
        # Video prompt (optional)
        prompt_frame = ttk.Frame(prompt_section)
        prompt_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        prompt_frame.columnconfigure(0, weight=1)
        
        ttk.Label(prompt_frame, text="Video Prompt (Optional):", font=('Arial', 10, 'bold')).grid(
            row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        self.prompt_text = tk.Text(prompt_frame, height=3, wrap=tk.WORD, font=('Arial', 11))
        self.prompt_text.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        prompt_scroll = ttk.Scrollbar(prompt_frame, orient="vertical", command=self.prompt_text.yview)
        prompt_scroll.grid(row=1, column=1, sticky=(tk.N, tk.S))
        self.prompt_text.configure(yscrollcommand=prompt_scroll.set)
        
        # Prompt actions
        prompt_actions = ttk.Frame(prompt_frame)
        prompt_actions.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        
        ttk.Button(prompt_actions, text="Clear Prompt", 
                  command=lambda: self.prompt_text.delete("1.0", tk.END)).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(prompt_actions, text="Sample Prompt", 
                  command=self.load_sample_prompt).pack(side=tk.LEFT)
        
        # Info label
        info_label = ttk.Label(prompt_section, 
                              text="💡 SeedDance generates high-quality videos from static images. Camera position can be fixed or dynamic.",
                              font=('Arial', 9), foreground='#666666')
        info_label.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
    
    def setup_settings_panel(self):
        """Setup settings panel"""
        self.settings_panel = SettingsPanel(self.frame, 4, "SeedDance Settings")
        
        # Duration
        self.duration_var = tk.StringVar(value="5")
        duration_options = [str(d) for d in Config.SEEDDANCE_DURATIONS]
        self.settings_panel.add_combobox(
            "Duration (seconds)", self.duration_var, duration_options
        )
        
        # Camera Fixed
        self.camera_fixed_var = tk.StringVar(value="True")
        self.settings_panel.add_combobox(
            "Camera Position", self.camera_fixed_var, ["True", "False"]
        )
        
        # Seed
        self.seed_var = tk.StringVar(value="-1")
        self.settings_panel.add_text_field("Seed (-1 for random)", self.seed_var, 15)
    
    def load_sample_prompt(self):
        """Load a sample prompt for demonstration"""
        sample_prompts = [
            "smooth camera movement, cinematic lighting",
            "gentle zoom in, natural motion",
            "dynamic movement, flowing hair",
            "subtle animation, realistic motion",
            "cinematic pan, professional quality",
            "smooth transition, elegant movement"
        ]
        
        import random
        sample = random.choice(sample_prompts)
        self.prompt_text.delete("1.0", tk.END)
        self.prompt_text.insert("1.0", sample)
    
    def on_image_selected(self, image_path):
        """Handle image selection"""
        # Check if replacing existing image
        replacing_image = hasattr(self, 'selected_image_path') and self.selected_image_path is not None
        
        self.selected_image_path = image_path
        self.original_image = self.image_preview.update_original_image(image_path)
        
        # Reset video result
        self.video_label.config(text="🎬 No video generated yet\n\nSeedDance video will be available as a download link")
        self.open_video_button.config(state="disabled")
        self.copy_url_button.config(state="disabled")
        self.result_video_url = None
        
        # Provide feedback about image replacement
        if replacing_image:
            self.update_status(f"Image replaced: {os.path.basename(image_path)} - Ready for SeedDance")
        else:
            self.update_status(f"Image selected: {os.path.basename(image_path)} - Ready for SeedDance")
    
    def on_drop(self, event):
        """Handle drag and drop with robust file path parsing"""
        # Parse the drag & drop data
        success, result = parse_drag_drop_data(event.data)
        
        if not success:
            show_error("Drag & Drop Error", result)
            return
        
        file_path = result
        
        # Validate the image file
        is_valid, error = validate_image_file(file_path)
        if not is_valid:
            show_error("Invalid File", f"{error}\n\nDropped file: {file_path}")
            return
        
        # Update UI and process the file
        self.image_selector.selected_path = file_path
        self.image_selector.image_path_label.config(
            text=os.path.basename(file_path), foreground="black"
        )
        self.on_image_selected(file_path)
    
    def process_task(self):
        """Process SeedDance video generation task"""
        if not self.validate_inputs():
            return
        
        self.show_progress("Starting SeedDance video generation...")
        
        # Start processing in background thread
        thread = threading.Thread(target=self.process_thread)
        thread.daemon = True
        thread.start()
    
    def process_thread(self):
        """Process in background thread"""
        try:
            # Update status
            self.frame.after(0, lambda: self.update_status("Preparing image..."))
            
            # For SeedDance, we need a public URL
            # This is a placeholder - in production, you'd upload the image
            image_url = self.upload_image_for_seeddance(self.selected_image_path)
            if not image_url:
                self.frame.after(0, lambda: self.handle_error("Failed to prepare image for SeedDance video generation"))
                return
            
            # Get parameters
            prompt = self.prompt_text.get("1.0", tk.END).strip()
            duration = int(self.duration_var.get())
            camera_fixed = self.camera_fixed_var.get().lower() == "true"
            
            try:
                seed = int(self.seed_var.get()) if self.seed_var.get().strip() != "-1" else -1
            except ValueError:
                seed = -1
            
            # Update status
            self.frame.after(0, lambda: self.update_status("Submitting SeedDance video generation task..."))
            
            # Submit task
            request_id, error = self.api_client.submit_seeddance_task(
                image_url, duration, prompt, camera_fixed, seed
            )
            
            if error:
                self.frame.after(0, lambda: self.handle_error(error))
                return
            
            self.current_request_id = request_id
            self.frame.after(0, lambda: self.update_status(f"Task submitted. ID: {request_id}"))
            
            # Poll for results
            def progress_callback(status, result):
                self.frame.after(0, lambda: self.update_status(f"Generating video... Status: {status}"))
            
            output_url, error, duration_time = self.api_client.poll_until_complete(
                request_id, progress_callback, poll_interval=2.0  # Longer interval for video
            )
            
            if error:
                self.frame.after(0, lambda: self.handle_error(error))
            else:
                self.frame.after(0, lambda: self.handle_success(output_url, duration_time))
                
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            self.frame.after(0, lambda: self.handle_error(error_msg))
    
    def upload_image_for_seeddance(self, image_path):
        """Upload image and return URL for SeedDance video generation"""
        try:
            # Use the privacy-aware uploader
            from core.secure_upload import privacy_uploader
            success, image_url, privacy_info = privacy_uploader.upload_with_privacy_warning(image_path, 'seeddance')
            
            if success and image_url:
                logger.info(f"SeedDance image uploaded: {privacy_info}")
                
                # Show privacy info to user (non-blocking)
                if Config.PRIVACY_MODE.lower() != "high":  # Don't show for high privacy since it works
                    self.frame.after(0, lambda: show_info(
                        "Upload Status", 
                        f"{privacy_info}\n\nSelected image: {os.path.basename(image_path)}"
                    ))
                
                return image_url
            else:
                # Fallback to sample URL if upload fails
                sample_url = Config.SAMPLE_URLS.get('seeddance', Config.SAMPLE_URLS.get('seededit'))
                
                self.frame.after(0, lambda: show_warning(
                    "Using Sample Image", 
                    f"Could not upload your image: {privacy_info}\n\n"
                    f"Using sample image for demonstration.\n"
                    f"Your selected image: {os.path.basename(image_path)}"
                ))
                
                return sample_url
                
        except Exception as e:
            logger.error(f"Upload failed: {e}")
            sample_url = Config.SAMPLE_URLS.get('seeddance', Config.SAMPLE_URLS.get('seededit'))
            
            self.frame.after(0, lambda: show_warning(
                "Upload Error", 
                f"Upload failed: {str(e)}\n\nUsing sample image for demonstration."
            ))
            
            return sample_url
    
    def handle_success(self, output_url, duration_time):
        """Handle successful completion"""
        # Use mixin method for video handling
        self.handle_video_success(output_url)
        
        # Auto-save the result
        prompt = self.prompt_text.get("1.0", tk.END).strip() if hasattr(self, 'prompt_text') else ""
        duration = self.duration_var.get()
        camera_fixed = self.camera_fixed_var.get()
        seed = self.seed_var.get()
        extra_info = f"{duration}s_cam{camera_fixed}_seed{seed}"
        
        success, saved_path, error = auto_save_manager.save_result(
            'seeddance', 
            output_url, 
            prompt=prompt,
            extra_info=extra_info,
            file_type="video"
        )
        
        # Show results
        message = f"SeedDance video generated successfully!\n"
        message += f"Processing time: {format_duration(duration_time)}\n"
        message += f"Video duration: {duration} seconds\n"
        message += f"Camera fixed: {camera_fixed}\n"
        message += f"Seed: {seed}\n"
        message += f"Video URL: {output_url}\n"
        
        if success and saved_path:
            message += f"Auto-saved to: {saved_path}\n"
        elif error:
            message += f"Auto-save failed: {error}\n"
        
        message += "\nClick 'Open Video in Browser' to view and download the video."
        
        self.show_results(message, True)
        
        success_msg = f"SeedDance video generated successfully in {format_duration(duration_time)}!"
        if saved_path:
            success_msg += f"\n\nAuto-saved to:\n{saved_path}"
        
        show_success("Success", success_msg)
    
    def handle_error(self, error_message):
        """Handle error"""
        self.video_label.config(
            text="❌ SeedDance Video Generation Failed\n\nCheck the results section for details",
            fg='red'
        )
        self.show_results(f"Error: {error_message}", False)
        show_error("Error", error_message)
    
    def open_video_in_browser(self):
        """Open video in browser"""
        if not self.result_video_url:
            show_error("Error", "No video URL available.")
            return
        
        try:
            webbrowser.open(self.result_video_url)
        except Exception as e:
            show_error("Error", f"Failed to open browser: {str(e)}")
    
    def copy_video_url(self):
        """Copy video URL to clipboard"""
        if not self.result_video_url:
            show_error("Error", "No video URL available.")
            return
        
        try:
            # Copy to clipboard
            self.frame.clipboard_clear()
            self.frame.clipboard_append(self.result_video_url)
            self.frame.update()  # Required for clipboard to work
            show_success("Success", "Video URL copied to clipboard!")
        except Exception as e:
            show_error("Error", f"Failed to copy URL: {str(e)}")
    
    def validate_inputs(self):
        """Validate inputs before processing"""
        if not super().validate_inputs():
            return False
        
        # Check video-specific inputs
        try:
            duration = int(self.duration_var.get())
            if duration not in Config.SEEDDANCE_DURATIONS:
                show_error("Error", f"Duration must be one of: {', '.join(map(str, Config.SEEDDANCE_DURATIONS))} seconds.")
                return False
        except ValueError:
            show_error("Error", "Invalid duration value.")
            return False
        
        try:
            seed = self.seed_var.get().strip()
            if seed and seed != "-1":
                seed_int = int(seed)
                if seed_int < -1 or seed_int > Config.SEED_RANGE[1]:
                    show_error("Error", f"Seed must be -1 or between 0 and {Config.SEED_RANGE[1]}.")
                    return False
        except ValueError:
            show_error("Error", "Invalid seed value. Use -1 for random or a valid integer.")
            return False
        
        return True
