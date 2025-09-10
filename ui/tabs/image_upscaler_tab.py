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
from ui.components.optimized_image_layout import OptimizedImageLayout
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
        """Setup the optimized image upscaler UI"""
        # Hide the scrollable canvas components since we're using direct container layout
        self.canvas.pack_forget()
        self.scrollbar.pack_forget()
        
        # For optimized layout, bypass the scrollable canvas and use the main container directly
        # This ensures full window expansion without canvas constraints
        self.optimized_layout = OptimizedImageLayout(self.container, "Image Upscaler")
        
        # Setup the layout with upscaler specific settings
        self.setup_upscaler_settings()
        
        # Setup prompt section in the left panel (upscaler doesn't need prompts, so skip)
        
        # Configure main action button
        self.optimized_layout.set_main_action("🔍 Upscale Image", self.process_task)
        
        # Connect image selector
        self.optimized_layout.set_image_selector_command(self.browse_image)
        
        # Connect result buttons
        self.optimized_layout.set_result_button_commands(
            self.save_result_image, 
            self.use_result_as_editor_input
        )
        
        # Connect sample and clear buttons (minimal functionality for upscaler)
        self.optimized_layout.sample_button.config(command=self.load_sample_image)
        self.optimized_layout.clear_button.config(command=self.clear_selection)
        
        # Connect drag and drop handling
        self.optimized_layout.set_parent_tab(self)
        
        # Setup cross-tab sharing
        self.optimized_layout.create_cross_tab_button(self.main_app, "Image Upscaler")
        
        # Setup progress section in the left panel
        self.setup_compact_progress_section()
    
    def browse_image(self):
        """Browse for image file"""
        from tkinter import filedialog
        
        file_path = filedialog.askopenfilename(
            title="Select Image to Upscale",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.gif *.bmp *.webp"),
                ("PNG files", "*.png"),
                ("JPEG files", "*.jpg *.jpeg"),
                ("All files", "*.*")
            ]
        )
        if file_path:
            self.on_image_selected(file_path)
    
    def setup_upscaler_settings(self):
        """Setup upscaler specific settings"""
        # Upscale factor setting
        factor_frame = ttk.Frame(self.optimized_layout.settings_container)
        factor_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        factor_frame.columnconfigure(1, weight=1)
        
        ttk.Label(factor_frame, text="Upscale Factor:", font=('Arial', 9)).grid(row=0, column=0, sticky=tk.W)
        self.upscale_factor_var = tk.StringVar(value="2k")
        factor_combo = ttk.Combobox(factor_frame, textvariable=self.upscale_factor_var, 
                                   values=["2k", "4k", "8k"], state="readonly", width=8)
        factor_combo.grid(row=0, column=1, sticky=tk.E, padx=(5, 0))
        
        # Creativity Level setting
        creativity_frame = ttk.Frame(self.optimized_layout.settings_container)
        creativity_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(5, 5))
        creativity_frame.columnconfigure(1, weight=1)
        
        ttk.Label(creativity_frame, text="Creativity:", font=('Arial', 9)).grid(row=0, column=0, sticky=tk.W)
        self.creativity_var = tk.StringVar(value="0")
        creativity_combo = ttk.Combobox(creativity_frame, textvariable=self.creativity_var, 
                                       values=["-2", "-1", "0", "1", "2"], state="readonly", width=8)
        creativity_combo.grid(row=0, column=1, sticky=tk.E, padx=(5, 0))
        
        # Output Format setting
        format_frame = ttk.Frame(self.optimized_layout.settings_container)
        format_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        format_frame.columnconfigure(1, weight=1)
        
        ttk.Label(format_frame, text="Format:", font=('Arial', 9)).grid(row=0, column=0, sticky=tk.W)
        self.format_var = tk.StringVar(value="png")
        format_combo = ttk.Combobox(format_frame, textvariable=self.format_var, 
                                   values=["png", "jpeg", "webp"], state="readonly", width=8)
        format_combo.grid(row=0, column=1, sticky=tk.E, padx=(5, 0))
    
    def setup_compact_progress_section(self):
        """Setup compact progress section"""
        # Add progress bar at the very bottom of left panel
        progress_frame = ttk.Frame(self.optimized_layout.settings_frame.master)
        progress_frame.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        progress_frame.columnconfigure(0, weight=1)
        
        # Progress bar
        self.progress_bar = ttk.Progressbar(progress_frame, mode='indeterminate')
        self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # Status label
        self.status_label = ttk.Label(progress_frame, text="Ready to upscale images", font=('Arial', 9))
        self.status_label.grid(row=1, column=0, sticky=tk.W)
    
    def load_sample_image(self):
        """Load a sample image (placeholder)"""
        from tkinter import messagebox
        messagebox.showinfo("Sample Image", "Sample image loading not implemented yet.\nPlease select your own image to upscale.")
    
    def clear_selection(self):
        """Clear the current selection"""
        # Reset the layout
        self.optimized_layout.selected_image_path = None
        self.optimized_layout.result_image = None
        
        # Update status
        self.update_status("Ready to upscale images")
    
    def show_progress(self, message):
        """Show progress"""
        self.progress_bar.start()
        self.update_status(message)
    
    def hide_progress(self):
        """Hide progress"""
        self.progress_bar.stop()
    
    def update_status(self, message):
        """Update status label"""
        self.status_label.config(text=message)
    
    def validate_inputs(self):
        """Validate inputs before processing"""
        if not hasattr(self, 'selected_image_path') or not self.selected_image_path:
            show_error("Error", "Please select an image first.")
            return False
        return True
    
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
    
    def on_image_selected(self, image_path, replacing_image=False):
        """Handle image selection"""
        # Check if replacing existing image (use parameter or detect automatically)
        if not replacing_image:
            replacing_image = hasattr(self, 'selected_image_path') and self.selected_image_path is not None
        
        # Update the optimized layout with the new image
        success = self.optimized_layout.update_input_image(image_path)
        
        if success:
            self.selected_image_path = image_path
            
            # Reset result buttons and clear previous results
            self.optimized_layout.save_result_button.config(state="disabled")
            self.optimized_layout.use_result_button.config(state="disabled")
            
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
                self.upscale_factor_var.get(),
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
                
                # Privacy info logged but no popup
                
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
        # Hide progress
        self.hide_progress()
        
        # Download and display result in optimized layout
        success = self.optimized_layout.update_result_image(output_url)
        
        if success:
            self.result_image = self.optimized_layout.result_image
            
            # Auto-save the result
            resolution = self.upscale_factor_var.get()
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
            
            # Result is displayed in the optimized layout - no need for old show_results
            
            success_msg = f"Image upscaled successfully in {format_duration(duration)}!"
            if saved_path:
                success_msg += f"\n\nAuto-saved to:\n{saved_path}"
            
            # Update status instead of showing dialog
            self.update_status("✅ " + success_msg.replace('\n\n', ' '))
        else:
            self.handle_error("Failed to download result image")
    
    def handle_error(self, error_message):
        """Handle error"""
        # Update status in optimized layout
        self.update_status(f"Error: {error_message}")
        self.hide_progress()
        show_error("Error", error_message)
    
    def save_result_image(self):
        """Save result image"""
        if not self.result_image:
            show_error("Error", "No result image to save.")
            return
        
        file_path, error = save_image_dialog(self.result_image, "Save Upscaled Image")
        if file_path:
            # File saved successfully - no dialog needed
            pass
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
            # Image set successfully - no dialog needed
            
        except Exception as e:
            show_error("Error", f"Failed to use upscaled result as editor input: {str(e)}")
