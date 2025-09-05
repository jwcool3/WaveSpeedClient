"""
Image to Video Tab Component

This module contains the image-to-video functionality.
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
from utils.utils import *
from core.auto_save import auto_save_manager
from core.logger import get_logger
from app.config import Config
from ui.components.video_player_mixin import VideoPlayerMixin

logger = get_logger()


class ImageToVideoTab(BaseTab, VideoPlayerMixin):
    """Image to Video Tab"""
    
    def __init__(self, parent_frame, api_client, main_app=None):
        self.main_app = main_app  # Reference to main app for cross-tab operations
        BaseTab.__init__(self, parent_frame, api_client)
        VideoPlayerMixin.__init__(self)
    
    def setup_ui(self):
        """Setup the image-to-video UI"""
        self.frame.columnconfigure(1, weight=1)
        
        # Enhanced image selector (compact for video tabs)
        self.image_selector = EnhancedImageSelector(
            self.frame, 0, self.on_image_selected, "Select Image for Video:", show_preview=False
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
            ("Generate Video", self.process_task, "primary"),
        ]
        self.setup_sticky_buttons(buttons_config)
    
    def setup_video_result_section(self):
        """Setup video result display section"""
        self.setup_video_result_section_with_player(self.image_preview.result_frame)
    
    def setup_prompt_section(self):
        """Setup prompt section for video generation"""
        prompt_section = ttk.LabelFrame(self.frame, text="Video Generation Prompts", padding="10")
        prompt_section.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 10))
        prompt_section.columnconfigure(0, weight=1)
        
        # Main prompt
        prompt_frame = ttk.Frame(prompt_section)
        prompt_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        prompt_frame.columnconfigure(0, weight=1)
        
        ttk.Label(prompt_frame, text="Video Prompt:", font=('Arial', 10, 'bold')).grid(
            row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        self.prompt_text = tk.Text(prompt_frame, height=3, wrap=tk.WORD, font=('Arial', 11))
        self.prompt_text.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        prompt_scroll = ttk.Scrollbar(prompt_frame, orient="vertical", command=self.prompt_text.yview)
        prompt_scroll.grid(row=1, column=1, sticky=(tk.N, tk.S))
        self.prompt_text.configure(yscrollcommand=prompt_scroll.set)
        
        # Negative prompt
        neg_prompt_frame = ttk.Frame(prompt_section)
        neg_prompt_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        neg_prompt_frame.columnconfigure(0, weight=1)
        
        ttk.Label(neg_prompt_frame, text="Negative Prompt (Optional):", font=('Arial', 10, 'bold')).grid(
            row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        self.negative_prompt_text = tk.Text(neg_prompt_frame, height=2, wrap=tk.WORD, font=('Arial', 11))
        self.negative_prompt_text.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        neg_prompt_scroll = ttk.Scrollbar(neg_prompt_frame, orient="vertical", 
                                        command=self.negative_prompt_text.yview)
        neg_prompt_scroll.grid(row=1, column=1, sticky=(tk.N, tk.S))
        self.negative_prompt_text.configure(yscrollcommand=neg_prompt_scroll.set)
        
        # Prompt actions
        prompt_actions = ttk.Frame(prompt_section)
        prompt_actions.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        
        ttk.Button(prompt_actions, text="Clear Prompts", 
                  command=self.clear_prompts).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(prompt_actions, text="Sample Prompt", 
                  command=self.load_sample_prompt).pack(side=tk.LEFT)
    
    def setup_settings_panel(self):
        """Setup settings panel"""
        self.settings_panel = SettingsPanel(self.frame, 4, "Video Generation Settings")
        
        # Duration
        self.duration_var = tk.StringVar(value="5")
        self.settings_panel.add_combobox(
            "Duration (seconds)", self.duration_var, ["5", "8"]
        )
        
        # Seed
        self.seed_var = tk.StringVar(value="-1")
        self.settings_panel.add_text_field("Seed (-1 for random)", self.seed_var, 15)
        
        # Last image (optional)
        self.last_image_var = tk.StringVar(value="")
        self.settings_panel.add_text_field("Last Image URL (optional)", self.last_image_var, 30)
    
    def on_image_selected(self, image_path):
        """Handle image selection"""
        # Check if replacing existing image
        replacing_image = hasattr(self, 'selected_image_path') and self.selected_image_path is not None
        
        self.selected_image_path = image_path
        self.original_image = self.image_preview.update_original_image(image_path)
        
        # Reset video result
        self.video_label.config(text="🎬 No video generated yet\n\nVideo will be available as a download link")
        self.open_video_button.config(state="disabled")
        self.copy_url_button.config(state="disabled")
        self.result_video_url = None
        
        # Provide feedback about image replacement
        if replacing_image:
            self.update_status(f"Image replaced: {os.path.basename(image_path)} - Ready to generate video")
        else:
            self.update_status(f"Image selected: {os.path.basename(image_path)} - Ready to generate video")
    
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
    
    def clear_prompts(self):
        """Clear all prompts"""
        self.prompt_text.delete("1.0", tk.END)
        self.negative_prompt_text.delete("1.0", tk.END)
    
    def load_sample_prompt(self):
        """Load a sample prompt for demonstration"""
        sample_prompt = "A beautiful woman walking through a garden, gentle breeze, natural lighting, cinematic movement"
        self.prompt_text.delete("1.0", tk.END)
        self.prompt_text.insert("1.0", sample_prompt)
        
        sample_negative = "blurry, low quality, static, no movement"
        self.negative_prompt_text.delete("1.0", tk.END)
        self.negative_prompt_text.insert("1.0", sample_negative)
    
    def process_task(self):
        """Process image-to-video task"""
        if not self.validate_inputs():
            return
        
        prompt = self.prompt_text.get("1.0", tk.END).strip()
        if not prompt:
            show_error("Error", "Please enter a video prompt.")
            return
        
        self.show_progress("Starting video generation...")
        
        # Start processing in background thread
        thread = threading.Thread(target=self.process_thread, args=(prompt,))
        thread.daemon = True
        thread.start()
    
    def process_thread(self, prompt):
        """Process in background thread"""
        try:
            # Update status
            self.frame.after(0, lambda: self.update_status("Preparing image..."))
            
            # For video generation, we need a public URL
            # This is a placeholder - in production, you'd upload the image
            image_url = self.upload_image_for_video(self.selected_image_path)
            if not image_url:
                self.frame.after(0, lambda: self.handle_error("Failed to prepare image for video generation"))
                return
            
            # Get parameters
            negative_prompt = self.negative_prompt_text.get("1.0", tk.END).strip()
            last_image = self.last_image_var.get().strip()
            duration = int(self.duration_var.get())
            
            try:
                seed = int(self.seed_var.get())
            except ValueError:
                seed = -1
            
            # Update status
            self.frame.after(0, lambda: self.update_status("Submitting video generation task..."))
            
            # Submit task
            request_id, error = self.api_client.submit_image_to_video_task(
                image_url, prompt, duration, negative_prompt, last_image, seed
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
    
    def upload_image_for_video(self, image_path):
        """Upload image and return URL for video generation"""
        try:
            # Use the privacy-aware uploader
            from core.secure_upload import privacy_uploader
            success, image_url, privacy_info = privacy_uploader.upload_with_privacy_warning(image_path, 'video')
            
            if success and image_url:
                logger.info(f"Image to Video upload: {privacy_info}")
                
                # Show privacy info to user (non-blocking)
                if Config.PRIVACY_MODE.lower() != "high":  # Don't show for high privacy since it works
                    self.frame.after(0, lambda: show_info(
                        "Upload Status", 
                        f"{privacy_info}\n\nSelected image: {os.path.basename(image_path)}"
                    ))
                
                return image_url
            else:
                # Fallback to sample URL if upload fails
                sample_url = Config.SAMPLE_URLS.get('video', Config.SAMPLE_URLS.get('seededit'))
                
                # Show enhanced warning dialog
                self.frame.after(0, lambda: self._show_sample_image_warning(
                    image_path, 'video', privacy_info
                ))
                
                return sample_url
                
        except Exception as e:
            logger.error(f"Upload failed: {e}")
            sample_url = Config.SAMPLE_URLS.get('video', Config.SAMPLE_URLS.get('seededit'))
            error_msg = str(e)  # Capture the error message
            
            # Show enhanced warning dialog
            self.frame.after(0, lambda: self._show_sample_image_warning(
                image_path, 'video', f"Upload error: {error_msg}"
            ))
            
            return sample_url
    
    def _show_sample_image_warning(self, image_path, ai_model, reason):
        """Show enhanced warning dialog for sample image usage"""
        from utils.warning_dialogs import show_sample_image_warning
        show_sample_image_warning(self.frame, image_path, ai_model, reason)
    
    def handle_success(self, output_url, duration_time):
        """Handle successful completion"""
        # Use mixin method for video handling
        self.handle_video_success(output_url)
        
        # Auto-save the result
        prompt = self.prompt_text.get("1.0", tk.END).strip()
        duration = self.duration_var.get()
        seed = self.seed_var.get()
        extra_info = f"{duration}s_seed{seed}"
        
        success, saved_path, error = auto_save_manager.save_result(
            'video', 
            output_url, 
            prompt=prompt,
            extra_info=extra_info,
            file_type="video"
        )
        
        # Show results
        message = f"Video generated successfully!\n"
        message += f"Processing time: {format_duration(duration_time)}\n"
        message += f"Video duration: {duration} seconds\n"
        message += f"Video URL: {output_url}\n"
        
        if success and saved_path:
            message += f"Auto-saved to: {saved_path}\n"
        elif error:
            message += f"Auto-save failed: {error}\n"
        
        message += "\nClick 'Open Video in Browser' to view and download the video."
        
        self.show_results(message, True)
        
        success_msg = f"Video generated successfully in {format_duration(duration_time)}!"
        if saved_path:
            success_msg += f"\n\nAuto-saved to:\n{saved_path}"
        
        show_success("Success", success_msg)
    
    def handle_error(self, error_message):
        """Handle error"""
        self.video_label.config(
            text="❌ Video Generation Failed\n\nCheck the results section for details",
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
            if duration not in [5, 8]:
                show_error("Error", "Duration must be 5 or 8 seconds.")
                return False
        except ValueError:
            show_error("Error", "Invalid duration value.")
            return False
        
        try:
            seed = self.seed_var.get().strip()
            if seed and seed != "-1":
                seed_int = int(seed)
                if seed_int < -1 or seed_int > 2147483647:
                    show_error("Error", "Seed must be -1 or between 0 and 2147483647.")
                    return False
        except ValueError:
            show_error("Error", "Invalid seed value. Use -1 for random or a valid integer.")
            return False
        
        return True
