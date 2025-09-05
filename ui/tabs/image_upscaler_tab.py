"""
Image Upscaler Tab Component

This module contains the image upscaler functionality.
"""

import tkinter as tk
from tkinter import ttk
import threading
import os
from ui.components.ui_components import BaseTab, SettingsPanel
from ui.components.enhanced_image_display import EnhancedImageSelector, EnhancedImagePreview
from utils.utils import *
from core.auto_save import auto_save_manager
from core.logger import get_logger
from app.config import Config

logger = get_logger()


class ImageUpscalerTab(BaseTab):
    """Image Upscaler Tab"""
    
    def __init__(self, parent_frame, api_client, main_app=None):
        self.result_image = None
        self.main_app = main_app  # Reference to main app for cross-tab operations
        super().__init__(parent_frame, api_client)
    
    def setup_ui(self):
        """Setup the image upscaler UI"""
        self.frame.columnconfigure(1, weight=1)
        
        # Enhanced image selector (smaller preview)
        self.image_selector = EnhancedImageSelector(
            self.frame, 0, self.on_image_selected, "Select Image to Upscale:", show_preview=True
        )
        
        # Enhanced image preview (larger result display)
        self.image_preview = EnhancedImagePreview(self.frame, 2, "Image Upscaler", result_size=(700, 500))
        self.image_preview.result_frame.config(text="Upscaled Result")
        
        # Setup drag and drop
        self.image_preview.setup_drag_and_drop(self.on_drop)
        
        # Result buttons
        button_frame = ttk.Frame(self.image_preview.result_frame)
        button_frame.pack(pady=(10, 0))
        
        self.save_button = ttk.Button(button_frame, text="Save Result Image", 
                                     command=self.save_result_image, state="disabled")
        self.save_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.use_result_button = ttk.Button(button_frame, text="Use as Editor Input", 
                                           command=self.use_result_as_editor_input, state="disabled")
        self.use_result_button.pack(side=tk.LEFT)
        
        # Settings panel
        self.setup_settings_panel()
        
        # Progress and results (moved up since button is now sticky)
        self.setup_progress_section(4)
        self.setup_results_section(5)
        
        # Setup sticky buttons at the bottom
        buttons_config = [
            ("Upscale Image", self.process_task, "primary"),
        ]
        self.setup_sticky_buttons(buttons_config)
    
    def setup_settings_panel(self):
        """Setup settings panel"""
        self.settings_panel = SettingsPanel(self.frame, 3, "Upscaler Settings")
        
        # Target Resolution
        self.resolution_var = tk.StringVar(value="4k")
        self.settings_panel.add_combobox(
            "Target Resolution", self.resolution_var, ["2k", "4k", "8k"]
        )
        
        # Creativity Level
        self.creativity_var = tk.StringVar(value="0")
        self.settings_panel.add_combobox(
            "Creativity Level", self.creativity_var, ["-2", "-1", "0", "1", "2"]
        )
        
        # Output Format
        self.format_var = tk.StringVar(value="png")
        self.settings_panel.add_combobox(
            "Output Format", self.format_var, ["png", "jpeg", "webp"]
        )
    
    def on_image_selected(self, image_path):
        """Handle image selection"""
        # Check if replacing existing image
        replacing_image = hasattr(self, 'selected_image_path') and self.selected_image_path is not None
        
        self.selected_image_path = image_path
        self.original_image = self.image_preview.update_original_image(image_path)
        
        # Reset result buttons and clear previous results
        self.save_button.config(state="disabled")
        self.use_result_button.config(state="disabled")
        
        # Provide feedback about image replacement
        if replacing_image:
            self.update_status(f"Image replaced: {os.path.basename(image_path)} - Ready to upscale")
        else:
            self.update_status(f"Image selected: {os.path.basename(image_path)} - Ready to upscale")
    
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
        """Process image upscaling task"""
        if not self.validate_inputs():
            return
        
        self.show_progress("Starting image upscaling...")
        
        # Start processing in background thread
        thread = threading.Thread(target=self.process_thread)
        thread.daemon = True
        thread.start()
    
    def process_thread(self):
        """Process in background thread"""
        try:
            # Update status
            self.frame.after(0, lambda: self.update_status("Preparing image..."))
            
            # For upscaler, we need a public URL
            # This is a placeholder - in production, you'd upload the image
            image_url = self.upload_image_for_upscaler(self.selected_image_path)
            if not image_url:
                self.frame.after(0, lambda: self.handle_error("Failed to prepare image for upscaling"))
                return
            
            # Update status
            self.frame.after(0, lambda: self.update_status("Submitting upscaling task..."))
            
            # Submit task
            request_id, error = self.api_client.submit_image_upscale_task(
                image_url,
                self.resolution_var.get(),
                int(self.creativity_var.get()),
                self.format_var.get()
            )
            
            if error:
                self.frame.after(0, lambda: self.handle_error(error))
                return
            
            self.current_request_id = request_id
            self.frame.after(0, lambda: self.update_status(f"Task submitted. ID: {request_id}"))
            
            # Poll for results
            def progress_callback(status, result):
                self.frame.after(0, lambda: self.update_status(f"Upscaling... Status: {status}"))
            
            output_url, error, duration = self.api_client.poll_until_complete(
                request_id, progress_callback
            )
            
            if error:
                self.frame.after(0, lambda: self.handle_error(error))
            else:
                self.frame.after(0, lambda: self.handle_success(output_url, duration))
                
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            self.frame.after(0, lambda: self.handle_error(error_msg))
    
    def upload_image_for_upscaler(self, image_path):
        """Upload image and return URL for upscaler"""
        try:
            # Use the privacy-aware uploader
            from core.secure_upload import privacy_uploader
            success, image_url, privacy_info = privacy_uploader.upload_with_privacy_warning(image_path, 'upscaler')
            
            if success and image_url:
                logger.info(f"Upscaler image uploaded: {privacy_info}")
                
                # Show privacy info to user (non-blocking)
                if Config.PRIVACY_MODE.lower() != "high":  # Don't show for high privacy since it works
                    self.frame.after(0, lambda: show_info(
                        "Upload Status", 
                        f"{privacy_info}\n\nSelected image: {os.path.basename(image_path)}"
                    ))
                
                return image_url
            else:
                # Fallback to sample URL if upload fails
                sample_url = Config.SAMPLE_URLS.get('upscaler', Config.SAMPLE_URLS.get('seededit'))
                
                self.frame.after(0, lambda: show_warning(
                    "Using Sample Image", 
                    f"Could not upload your image: {privacy_info}\n\n"
                    f"Using sample image for demonstration.\n"
                    f"Your selected image: {os.path.basename(image_path)}"
                ))
                
                return sample_url
                
        except Exception as e:
            logger.error(f"Upload failed: {e}")
            sample_url = Config.SAMPLE_URLS.get('upscaler', Config.SAMPLE_URLS.get('seededit'))
            
            self.frame.after(0, lambda: show_warning(
                "Upload Error", 
                f"Upload failed: {str(e)}\n\nUsing sample image for demonstration."
            ))
            
            return sample_url
    
    def handle_success(self, output_url, duration):
        """Handle successful completion"""
        # Download and display result
        self.result_image = self.image_preview.update_result_image(output_url)
        
        if self.result_image:
            # Enable buttons
            self.save_button.config(state="normal")
            self.use_result_button.config(state="normal")
            
            # Auto-save the result
            resolution = self.resolution_var.get().upper()
            creativity = self.creativity_var.get()
            extra_info = f"upscaled_{resolution}_c{creativity}"
            
            success, saved_path, error = auto_save_manager.save_result(
                'upscaler', 
                output_url, 
                prompt=None,  # Upscaler doesn't use prompts
                extra_info=extra_info
            )
            
            # Show results
            message = f"Image upscaled successfully!\n"
            message += f"Processing time: {format_duration(duration)}\n"
            message += f"Target resolution: {resolution}\n"
            message += f"Creativity level: {creativity}\n"
            message += f"Result URL: {output_url}\n"
            
            if success and saved_path:
                message += f"Auto-saved to: {saved_path}\n"
            elif error:
                message += f"Auto-save failed: {error}\n"
            
            message += "\nThe upscaled image is displayed above."
            
            self.show_results(message, True)
            
            success_msg = f"Image upscaled successfully in {format_duration(duration)}!"
            if saved_path:
                success_msg += f"\n\nAuto-saved to:\n{saved_path}"
            
            show_success("Success", success_msg)
        else:
            self.handle_error("Failed to download result image")
    
    def handle_error(self, error_message):
        """Handle error"""
        self.show_results(f"Error: {error_message}", False)
        show_error("Error", error_message)
    
    def save_result_image(self):
        """Save result image"""
        if not self.result_image:
            show_error("Error", "No result image to save.")
            return
        
        file_path, error = save_image_dialog(self.result_image, "Save Upscaled Image")
        if file_path:
            show_success("Success", f"Upscaled image saved to:\n{file_path}")
        elif error and "cancelled" not in error.lower():
            show_error("Error", error)
    
    def use_result_as_editor_input(self):
        """Use upscaled result as input for editor tab"""
        if not self.result_image:
            show_error("Error", "No upscaled result image available.")
            return
        
        if not self.main_app:
            show_error("Error", "Cannot access editor tab.")
            return
        
        try:
            # Create temporary file
            temp_path, error = create_temp_file(self.result_image, "temp_upscaled_image")
            if error:
                show_error("Error", error)
                return
            
            # Switch to editor tab and set image
            self.main_app.switch_to_editor_with_image(temp_path)
            show_success("Success", "Upscaled image is now set as the editor input image!")
            
        except Exception as e:
            show_error("Error", f"Failed to use upscaled result as editor input: {str(e)}")
