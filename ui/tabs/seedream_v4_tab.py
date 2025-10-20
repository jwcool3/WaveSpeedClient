"""
Seedream V4 Tab Component - Multi-Modal Image Generation (IMPROVED VERSION)
For WaveSpeed AI Creative Suite

This module contains the ByteDance Seedream V4 image editing functionality.
Completely rewritten to match SeedEdit tab quality and fix all layout issues.
"""

import tkinter as tk
from tkinter import ttk
import threading
import os
import json
import random
# Lazy-load PIL (saves ~61ms on startup) - imported when needed
from ui.components.ui_components import BaseTab
from ui.components.optimized_image_layout import OptimizedImageLayout
from ui.components.enhanced_image_display import EnhancedImageSelector, EnhancedImagePreview
from utils.utils import *
from core.auto_save import auto_save_manager
from core.secure_upload import privacy_uploader
from core.logger import get_logger
from core.prompt_tracker import prompt_tracker

logger = get_logger()


class SeedreamV4Tab(BaseTab):
    """Seedream V4 Multi-Modal Image Editor Tab - IMPROVED VERSION"""
    
    def __init__(self, parent_frame, api_client, main_app=None, tab_id="1"):
        self.result_image = None
        self.main_app = main_app
        self.tab_id = tab_id  # Unique identifier for this tab instance
        # NOTE: self.selected_image_path is now a property that delegates to
        # self.improved_layout.image_manager.selected_image_paths (single source of truth)
        self.auto_resolution = True  # Auto-set resolution based on input image
        
        # Prompt storage for Seedream V4
        self.seedream_v4_prompts_file = "data/seedream_v4_prompts.json"
        self.saved_seedream_v4_prompts = load_json_file(self.seedream_v4_prompts_file, [])
        
        # Size limits for validation
        self.min_size = 256
        self.max_size = 4096
        
        # Aspect ratio tracking
        self.original_aspect_ratio = None
        self.aspect_ratio_locked = False

        # Thread safety for polling
        self._polling_lock = threading.Lock()
        self._polling_active = False
        self._polling_thread = None
        self._polling_task_id = None

        # Skip creating BaseTab's content frame since we use ImprovedSeedreamLayout
        super().__init__(parent_frame, api_client, create_content_frame=False)
    
    def apply_ai_suggestion(self, improved_prompt: str):
        """Apply AI suggestion to prompt text"""
        # Clear any placeholder state first
        if hasattr(self.improved_layout, 'prompt_has_placeholder'):
            self.improved_layout.prompt_has_placeholder = False
        
        # Set the improved prompt
        self.prompt_text.delete("1.0", tk.END)
        self.prompt_text.insert("1.0", improved_prompt)
        self.prompt_text.config(fg='#333333')  # Ensure normal text color
        
        # Update status if available
        if hasattr(self.improved_layout, 'on_prompt_text_changed'):
            self.improved_layout.on_prompt_text_changed(None)
    
    def setup_ui(self):
        """Setup the improved Seedream V4 UI with new compact layout"""
        # Use the new improved layout (refactored modular system)
        from ui.components.seedream import ImprovedSeedreamLayout
        self.improved_layout = ImprovedSeedreamLayout(self.scrollable_frame, self.api_client, self)
        
        # Connect the improved layout methods to our existing functionality
        self.connect_improved_layout()
        
        # Setup Seedream V4 specific settings in the improved layout
        self.setup_seedream_v4_settings_improved()
        
        # Setup prompt section in the improved layout
        self.setup_compact_prompt_section_improved()
        
        # Setup progress section in the improved layout
        self.setup_compact_progress_section_improved()
    
    def connect_improved_layout(self):
        """Connect the improved layout methods to our existing functionality"""
        # Connect image browsing
        self.improved_layout.browse_image = self.browse_image
        
        # Don't override the layout's process_seedream method - it has the real implementation
        # self.improved_layout.process_seedream = self.process_task
        
        # Connect result actions
        self.improved_layout.save_result = self.save_result_image
        self.improved_layout.load_result = self.load_saved_prompt
        
        # Connect utility methods
        self.improved_layout.clear_all = self.clear_all
        self.improved_layout.load_sample = self.load_sample_prompt
        self.improved_layout.improve_with_ai = self.improve_with_ai_placeholder
        
        # Connect prompt management
        self.improved_layout.save_preset = self.save_current_prompt
        self.improved_layout.load_preset = self.load_saved_prompt
        
        # Connect settings
        self.improved_layout.auto_set_resolution = self.auto_set_resolution
        
        # Store references to layout components for easy access
        self.prompt_text = self.improved_layout.prompt_text
        
        # Refresh the dropdown with any existing saved prompts
        if hasattr(self.improved_layout, 'refresh_preset_dropdown'):
            self.improved_layout.refresh_preset_dropdown()
        self.width_var = self.improved_layout.width_var
        self.height_var = self.improved_layout.height_var
        self.seed_var = self.improved_layout.seed_var
        self.sync_mode_var = self.improved_layout.sync_mode_var
        
        # Add missing variables that other methods expect
        self.size_display_var = tk.StringVar()
        self.aspect_ratio_lock_var = tk.BooleanVar()

    @property
    def selected_image_path(self):
        """
        Get the currently selected image path from the authoritative source.

        Single source of truth: self.improved_layout.image_manager.selected_image_paths

        Returns:
            str or None: Path to first selected image, or None if no image selected
        """
        if not hasattr(self, 'improved_layout'):
            return None
        if not hasattr(self.improved_layout, 'image_manager'):
            return None
        paths = self.improved_layout.image_manager.selected_image_paths
        return paths[0] if paths else None

    @selected_image_path.setter
    def selected_image_path(self, value):
        """
        Set the selected image path by updating the authoritative source.

        Args:
            value: Image path string or None to clear
        """
        if not hasattr(self, 'improved_layout'):
            logger.warning("Attempted to set selected_image_path before improved_layout initialized")
            return
        if not hasattr(self.improved_layout, 'image_manager'):
            logger.warning("Attempted to set selected_image_path before image_manager initialized")
            return

        # Update the authoritative source
        if value is None:
            self.improved_layout.image_manager.selected_image_paths = []
        else:
            self.improved_layout.image_manager.selected_image_paths = [value]

    def update_size_display(self):
        """Update size display when dimensions change"""
        try:
            width = self.width_var.get()
            height = self.height_var.get()
            self.size_display_var.set(f"{width} x {height}")
            logger.debug(f"Size display updated: {width}x{height}")
        except Exception as e:
            logger.error(f"Error updating size display: {e}")
    
    def handle_result_ready(self, result_path, result_url=None):
        """Handle when processing result is ready"""
        try:
            # Set the result image
            self.result_image = result_path
            
            # Store the result URL for auto-save if available
            if result_url:
                self.last_result_url = result_url
            
            # Note: Auto-save is handled in handle_success() method with the proper URL
            # Don't duplicate auto-save here since result_path is a local temp file
            
            # Track the prompt if successful
            if hasattr(prompt_tracker, 'track_success'):
                prompt_tracker.track_success(
                    self.prompt_text.get("1.0", tk.END).strip(),
                    "seedream_v4"
                )
                
            logger.info(f"Seedream V4 processing completed successfully: {result_path}")
            
        except Exception as e:
            logger.error(f"Error handling result: {e}")
        
        # Add alias for AI integration compatibility
        self.optimized_layout = self.improved_layout
    
    def improve_with_ai_placeholder(self):
        """Improve prompt with AI assistance"""
        current_prompt = self.prompt_text.get("1.0", tk.END).strip()
        
        # Clear placeholder text
        if current_prompt == "Describe the transformation you want to apply to the image...":
            current_prompt = ""
        
        # Use the AIChatMixin functionality (inherited by the layout)
        if hasattr(self.improved_layout, 'improve_prompt_with_ai'):
            self.improved_layout.improve_prompt_with_ai()
        else:
            # Fallback: open AI chat directly
            try:
                from ui.components.ai_prompt_chat import show_ai_prompt_chat
                
                def on_prompt_updated(new_prompt):
                    self.apply_ai_suggestion(new_prompt)
                
                show_ai_prompt_chat(
                    parent=self.parent_frame,
                    current_prompt=current_prompt,
                    tab_name="Seedream V4",
                    on_prompt_updated=on_prompt_updated
                )
            except Exception as e:
                logger.error(f"Error opening AI chat: {e}")
                from utils.utils import show_error
                show_error("AI Error", f"Failed to open AI assistant: {str(e)}")
    
    def setup_seedream_v4_settings_improved(self):
        """Setup Seedream V4 specific settings in the improved layout"""
        # The improved layout already has all settings built-in
        # Load saved values into the layout's controls
        try:
            # Set default values if not already set
            if self.improved_layout.width_var.get() == 1024 and self.improved_layout.height_var.get() == 1024:
                # Auto-set resolution if we have an image
                if hasattr(self, 'selected_image_path') and self.selected_image_path:
                    self.auto_set_resolution()
        except Exception as e:
            logger.error(f"Error setting up improved settings: {e}")
    
    def setup_compact_prompt_section_improved(self):
        """Setup compact prompt section in the improved layout"""
        # The improved layout already has the prompt section built-in
        # Just ensure our saved prompts are loaded
        try:
            # Load any default or saved prompts if needed
            if hasattr(self, 'saved_seedream_v4_prompts'):
                logger.info(f"Loaded {len(self.saved_seedream_v4_prompts)} saved prompts")
        except Exception as e:
            logger.error(f"Error setting up improved prompt section: {e}")
    
    def setup_compact_progress_section_improved(self):
        """Setup compact progress section in the improved layout"""
        # The improved layout already has the progress section built-in
        # Just connect any additional status tracking if needed
        try:
            # Store references for easy access
            if hasattr(self.improved_layout, 'status_label'):
                self.status_label = self.improved_layout.status_label
            if hasattr(self.improved_layout, 'progress_bar'):
                self.progress_bar = self.improved_layout.progress_bar
        except Exception as e:
            logger.error(f"Error setting up improved progress section: {e}")

    # ============================================================================
    # OLD DEAD CODE REMOVED
    # The following methods were removed because they reference non-existent UI
    # elements (self.optimized_layout.settings_container, self.width_slider, etc.)
    # All this functionality is now in ui/components/seedream/ modular system:
    # - setup_seedream_v4_settings() - replaced by SettingsPanelManager
    # - toggle_auto_size() - replaced by SettingsPanelManager
    # - toggle_aspect_ratio_lock() - replaced by SettingsPanelManager
    # ============================================================================

    def calculate_original_aspect_ratio(self):
        """Calculate aspect ratio from the original image"""
        if not self.selected_image_path:
            return

        try:
            from PIL import Image, ImageOps  # Lazy import
            image = Image.open(self.selected_image_path)
            image = ImageOps.exif_transpose(image)
            width, height = image.size
            self.original_aspect_ratio = width / height
            logger.info(f"Calculated original aspect ratio: {self.original_aspect_ratio:.3f} ({width}x{height})")
        except Exception as e:
            logger.error(f"Error calculating aspect ratio: {e}")
            self.original_aspect_ratio = None

    # ============================================================================
    # MORE OLD DEAD CODE REMOVED
    # - update_size_display() - references non-existent self.width_var, self.height_var
    # - on_width_entry_change() - references non-existent self.width_slider
    # - on_height_entry_change() - references non-existent self.height_slider
    # - set_preset_size() - only called from removed UI code
    # - generate_random_seed() - only called from removed UI code
    # All replaced by SettingsPanelManager
    # ============================================================================

    def auto_set_resolution(self):
        """Automatically set resolution based on input image - pixel perfect matching"""
        if not self.selected_image_path:
            return
        
        try:
            from PIL import Image, ImageOps  # Lazy import
            # Fix image rotation before getting dimensions
            image = Image.open(self.selected_image_path)

            # Apply EXIF orientation correction
            image = ImageOps.exif_transpose(image)
            
            original_width, original_height = image.size
            logger.info(f"Original image dimensions: {original_width}x{original_height}")
            
            # Pixel-perfect matching: use exact dimensions if within limits
            target_width = original_width
            target_height = original_height
            
            # Ensure dimensions are within supported range (256-4096)
            target_width = max(256, min(4096, target_width))
            target_height = max(256, min(4096, target_height))
            
            # If we had to clamp dimensions, maintain aspect ratio
            if target_width != original_width or target_height != original_height:
                aspect_ratio = original_width / original_height
                
                if target_width != original_width:
                    # Width was clamped, adjust height to maintain aspect ratio
                    target_height = int(target_width / aspect_ratio)
                    target_height = max(256, min(4096, target_height))
                elif target_height != original_height:
                    # Height was clamped, adjust width to maintain aspect ratio
                    target_width = int(target_height * aspect_ratio)
                    target_width = max(256, min(4096, target_width))
            
            # Set the resolution (improved layout's SettingsPanelManager handles display update)
            self.width_var.set(target_width)
            self.height_var.set(target_height)

            logger.info(f"Auto-set resolution to {target_width}x{target_height} for image {original_width}x{original_height}")

        except Exception as e:
            logger.error(f"Error auto-setting resolution: {e}")
            # Fallback to default
            self.width_var.set(2048)
            self.height_var.set(2048)
    
    def browse_image(self):
        """Browse for image files (supports multiple selection)"""
        from tkinter import filedialog
        
        file_paths = filedialog.askopenfilenames(
            title="Select Images for Seedream V4 (up to 10 images)",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.gif *.bmp *.webp"),
                ("PNG files", "*.png"),
                ("JPEG files", "*.jpg *.jpeg"),
                ("All files", "*.*")
            ]
        )
        if file_paths:
            self.on_images_selected(file_paths)
    
    def on_images_selected(self, file_paths):
        """Handle multiple image selection"""
        try:
            # Validate all images
            valid_paths = []
            for file_path in file_paths:
                if validate_image_file(file_path):
                    valid_paths.append(file_path)
                else:
                    show_error("Invalid Image", f"Invalid image file: {os.path.basename(file_path)}")
            
            if not valid_paths:
                show_error("No Valid Images", "No valid image files selected.")
                return
            
            # Limit to 10 images as per API specification
            if len(valid_paths) > 10:
                show_warning("Too Many Images", f"Maximum 10 images allowed. Using first 10 of {len(valid_paths)} selected.")
                valid_paths = valid_paths[:10]
            
            # Update the improved layout with multiple images
            if hasattr(self, 'improved_layout'):
                self.improved_layout.load_images(valid_paths)
            else:
                # Fallback to single image (first one)
                self.on_image_selected(valid_paths[0])
            
            # Update status
            if len(valid_paths) == 1:
                filename = os.path.basename(valid_paths[0])
                self.update_status(f"📁 Image loaded: {filename}")
            else:
                self.update_status(f"📁 {len(valid_paths)} images loaded")
                
        except Exception as e:
            logger.error(f"Error selecting images: {e}")
            show_error("Error", f"Failed to load images: {str(e)}")
    
    def on_image_selected(self, file_path, replacing_image=False):
        """Handle single image selection with auto-resolution and rotation fix"""
        try:
            if not validate_image_file(file_path):
                show_error("Invalid Image", "Please select a valid image file.")
                return
            
            self.selected_image_path = file_path
            
            # Calculate aspect ratio for potential locking
            self.calculate_original_aspect_ratio()

            # Update the improved layout's image display
            self.improved_layout.load_image(file_path)
            
            # Update status
            filename = os.path.basename(file_path)
            self.update_status(f"📁 Image loaded: {filename}")
                
        except Exception as e:
            logger.error(f"Error selecting image: {e}")
            show_error("Error", f"Failed to load image: {str(e)}")

    # ============================================================================
    # MORE OLD DEAD CODE REMOVED (lines 433-556)
    # - setup_compact_prompt_section() - references non-existent self.optimized_layout.prompt_container
    # - clear_placeholder() - only used by removed setup_compact_prompt_section()
    # - setup_compact_progress_section() - references non-existent self.optimized_layout.progress_container
    # All replaced by PromptSectionManager and improved layout
    # ============================================================================

    def show_progress(self, message="Processing..."):
        """Show progress indicator"""
        if hasattr(self, 'progress_bar') and self.progress_bar:
            self.progress_bar.grid()
            self.progress_bar.start(10)
        if hasattr(self, 'status_label') and self.status_label and hasattr(self.status_label, 'config'):
            self.status_label.config(text=message)
        else:
            logger.info(f"Progress: {message}")
    
    def hide_progress(self):
        """Hide progress indicator"""
        if hasattr(self, 'progress_bar') and self.progress_bar:
            self.progress_bar.stop()
            self.progress_bar.grid_remove()
    
    def update_status(self, message):
        """Update status message"""
        if hasattr(self, 'status_label') and self.status_label and hasattr(self.status_label, 'config'):
            self.status_label.config(text=message)
        else:
            # Fallback to logging if status label not available
            logger.info(f"Status: {message}")
    
    def save_current_prompt(self):
        """Save current prompt to file"""
        prompt = self.prompt_text.get("1.0", tk.END).strip()
        if not prompt or prompt == "remove man":
            show_error("Save Error", "Please enter a prompt before saving.")
            return
        
        # Check if prompt already exists
        if prompt in self.saved_seedream_v4_prompts:
            show_error("Duplicate Prompt", "This prompt is already saved.")
            return
        
        # Add to saved prompts
        self.saved_seedream_v4_prompts.append(prompt)
        
        # Save to file
        save_json_file(self.seedream_v4_prompts_file, self.saved_seedream_v4_prompts)
        
        # Refresh the improved layout dropdown
        if hasattr(self, 'improved_layout') and hasattr(self.improved_layout, 'refresh_preset_dropdown'):
            self.improved_layout.refresh_preset_dropdown()
        
        show_success("Prompt Saved", f"Prompt saved successfully!\nTotal saved: {len(self.saved_seedream_v4_prompts)}")
    
    def load_saved_prompt(self):
        """Load a saved prompt"""
        if not self.saved_seedream_v4_prompts:
            show_error("No Prompts", "No saved prompts found.")
            return
        
        # Create selection dialog
        from tkinter import simpledialog
        
        # Show list of prompts
        prompt_list = "\n".join([f"{i+1}. {prompt[:50]}..." if len(prompt) > 50 else f"{i+1}. {prompt}" 
                                for i, prompt in enumerate(self.saved_seedream_v4_prompts)])
        
        selection = simpledialog.askinteger(
            "Load Prompt",
            f"Select a prompt to load:\n\n{prompt_list}",
            minvalue=1,
            maxvalue=len(self.saved_seedream_v4_prompts)
        )
        
        if selection:
            selected_prompt = self.saved_seedream_v4_prompts[selection - 1]
            self.prompt_text.delete("1.0", tk.END)
            self.prompt_text.insert("1.0", selected_prompt)
    
    def delete_saved_prompt(self):
        """Delete a saved prompt"""
        if not self.saved_seedream_v4_prompts:
            show_error("No Prompts", "No saved prompts found.")
            return
        
        # Create selection dialog
        from tkinter import simpledialog, messagebox
        
        # Show list of prompts
        prompt_list = "\n".join([f"{i+1}. {prompt[:50]}..." if len(prompt) > 50 else f"{i+1}. {prompt}" 
                                for i, prompt in enumerate(self.saved_seedream_v4_prompts)])
        
        selection = simpledialog.askinteger(
            "Delete Prompt",
            f"Select a prompt to delete:\n\n{prompt_list}",
            minvalue=1,
            maxvalue=len(self.saved_seedream_v4_prompts)
        )
        
        if selection:
            prompt_to_delete = self.saved_seedream_v4_prompts[selection - 1]
            
            # Confirm deletion
            if messagebox.askyesno("Confirm Delete", f"Delete this prompt?\n\n{prompt_to_delete}"):
                self.saved_seedream_v4_prompts.pop(selection - 1)
                save_json_file(self.seedream_v4_prompts_file, self.saved_seedream_v4_prompts)
                
                # Refresh the improved layout dropdown
                if hasattr(self, 'improved_layout') and hasattr(self.improved_layout, 'refresh_preset_dropdown'):
                    self.improved_layout.refresh_preset_dropdown()
                
                show_success("Prompt Deleted", "Prompt deleted successfully.")
    
    def load_sample_prompt(self):
        """Load a sample prompt"""
        sample_prompts = [
            "remove man",
            "Transform the person into a Renaissance-style painting with oil paint texture",
            "Change the background to a futuristic cyberpunk cityscape with neon lights",
            "Convert this image to anime style with vibrant colors",
            "Add magical elements like floating particles and glowing effects",
            "Change the clothing to a formal business suit",
            "Add a beautiful sunset sky in the background",
            "Transform the scene into a winter wonderland with snow",
            "Add professional studio lighting effects",
            "Convert to black and white with dramatic contrast"
        ]
        
        import random
        sample = random.choice(sample_prompts)
        self.prompt_text.delete("1.0", tk.END)
        self.prompt_text.insert("1.0", sample)
    
    def clear_all(self):
        """Clear all inputs"""
        self.prompt_text.delete("1.0", tk.END)
        self.prompt_text.insert("1.0", "remove man")
        self.seed_var.set("-1")
        self.width_var.set(2048)
        self.height_var.set(2048)
        self.sync_mode_var.set(False)
        self.base64_output_var.set(False)
        self.auto_size_var.set(True)
        self.aspect_ratio_lock_var.set(False)
        self.width_slider.config(state="disabled")
        self.height_slider.config(state="disabled")
        self.width_entry.config(state="disabled")
        self.height_entry.config(state="disabled")
        
        # Reset aspect ratio tracking
        self.original_aspect_ratio = None
        self.aspect_ratio_locked = False
        
        # Disable preset buttons
        for btn in self.preset_buttons:
            btn.config(state="disabled")
        
        # Update display
        self.update_size_display()
        
        # Clear images (both single and multiple)
        self.selected_image_path = None
        self.result_image = None
        
        # Clear multiple images if using improved layout
        if hasattr(self, 'improved_layout'):
            self.improved_layout.selected_image_paths = []
            self.improved_layout.update_image_count_display()
        
        if hasattr(self, 'improved_layout'):
            # Clear improved layout images
            self.improved_layout.selected_image_path = None
            self.improved_layout.result_image_path = None
            self.improved_layout.show_default_message()
        else:
            # Fallback to old layout
            self.optimized_layout.clear_input_image()
            self.optimized_layout.clear_result_image()
        
        self.update_status("All inputs cleared")
    
    def process_task(self):
        """Process Seedream V4 task"""
        # Stop any existing polling before starting new task
        if hasattr(self, '_polling_active'):
            self._polling_active = False
        
        # Validate inputs
        prompt = self.prompt_text.get("1.0", tk.END).strip()
        if not prompt or prompt == "remove man":
            show_error("Missing Prompt", "Please enter an editing instruction.")
            return
        
        if not self.selected_image_path:
            show_error("Missing Image", "Please select an input image.")
            return
        
        # Show progress
        self.show_progress("Uploading and processing with Seedream V4...")
        
        # Process in background thread
        def background_process():
            try:
                # Upload image with rotation fix
                image_url = self.upload_image_with_rotation_fix(self.selected_image_path)

                if image_url:
                    # Submit task
                    self.submit_seedream_v4_task(image_url, prompt)
                else:
                    # Upload returned None - error already shown to user
                    # Just hide progress and log
                    logger.warning("Upload failed, aborting processing")
                    self.frame.after(0, lambda: self.hide_progress())
                    self.frame.after(0, lambda: self.update_status("❌ Upload failed - Ready"))

            except Exception as e:
                logger.error(f"Background process error: {e}")
                # Use default arg to capture exception message (early binding, thread-safe)
                error_str = str(e)
                self.frame.after(0, lambda err=error_str: self.handle_error(f"Processing error: {err}"))
        
        thread = threading.Thread(target=background_process)
        thread.daemon = True
        thread.start()
    
    def upload_image_with_rotation_fix(self, image_path):
        """Upload image securely for Seedream V4 with rotation fix"""
        try:
            # Fix image rotation before upload
            from PIL import Image, ImageOps
            import tempfile
            
            # Open image and fix rotation
            image = Image.open(image_path)
            
            # Apply EXIF orientation correction
            image = ImageOps.exif_transpose(image)
            
            # Save corrected image to temporary file
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
                temp_path = temp_file.name
                image.save(temp_path, 'PNG')
            
            try:
                # Use privacy-friendly upload with corrected image
                from core.secure_upload import privacy_uploader
                success, url, privacy_info = privacy_uploader.upload_with_privacy_warning(temp_path, 'seedream_v4')
            finally:
                # Clean up temp file
                try:
                    os.unlink(temp_path)
                except:
                    pass
            
            if success:
                # Privacy info logged but no popup
                logger.info(f"Seedream V4 image uploaded: {privacy_info}")
                return url
            else:
                # Upload failed - show error and abort
                from utils.utils import show_error
                show_error(
                    "Upload Failed",
                    f"Could not upload your image.\n\n"
                    f"Error: {privacy_info}\n\n"
                    f"Please check your connection and try again.\n"
                    f"Selected image: {image_path}"
                )
                logger.error(f"Upload failed: {privacy_info}")
                return None

        except Exception as e:
            logger.error(f"Image upload with rotation fix failed: {e}")

            # Upload error - show error and abort
            from utils.utils import show_error
            show_error(
                "Upload Error",
                f"Failed to upload image: {str(e)}\n\n"
                f"Please try again or select a different image."
            )

            return None
    
    def start_polling(self, task_id, duration):
        """Start polling for task results with proper thread safety"""
        # Thread-safe stopping of existing polling using instance lock
        with self._polling_lock:
            if self._polling_active:
                logger.info("Stopping existing polling thread")
                self._polling_active = False
                # Wait for existing thread to finish
                if self._polling_thread and self._polling_thread.is_alive():
                    # Don't wait while holding lock - release and rejoin
                    thread_to_wait = self._polling_thread
            else:
                thread_to_wait = None

            self._polling_active = True
            self._polling_task_id = task_id
            logger.info(f"Starting polling for task: {task_id}")

        # Wait for old thread outside lock to avoid deadlock
        if thread_to_wait and thread_to_wait.is_alive():
            thread_to_wait.join(timeout=1.0)
        
        # Add timeout protection (5 minutes maximum)
        self._polling_start_time = time.time()
        self._polling_timeout = 300  # 5 minutes
        
        def poll_for_results():
            try:
                while self._polling_active:
                    # Check timeout
                    if time.time() - self._polling_start_time > self._polling_timeout:
                        self._polling_active = False
                        logger.warning(f"Polling timeout reached for task: {task_id}")
                        self.frame.after(0, lambda: self.handle_error("Processing timeout - maximum wait time exceeded"))
                        return
                    
                    # Check if we should continue polling for this specific task
                    if not hasattr(self, '_polling_task_id') or self._polling_task_id != task_id:
                        logger.info(f"Stopping polling for task {task_id} - newer task started")
                        return
                    
                    result = self.api_client.get_seedream_v4_result(task_id)
                    
                    if result['success']:
                        status = result.get('status')
                        
                        if status == 'completed':
                            self._polling_active = False
                            logger.info(f"Task completed, stopping polling for task: {task_id}")
                            output_url = result.get('output_url')
                            if output_url:
                                # Use default args to capture variables (early binding, thread-safe)
                                self.frame.after(0, lambda url=output_url, dur=duration: self.handle_success(url, dur))
                            else:
                                self.frame.after(0, lambda: self.handle_error("No output URL in completed result"))
                            return
                        elif status == 'failed':
                            self._polling_active = False
                            error_msg = result.get('error', 'Task failed')
                            # Use default arg to capture error_msg (early binding, thread-safe)
                            self.frame.after(0, lambda msg=error_msg: self.handle_error(msg))
                            return
                        else:
                            # Still processing, wait before next poll
                            time.sleep(2)
                    else:
                        self._polling_active = False
                        error_msg = result.get('error', 'Failed to get task status')
                        # Use default arg to capture error_msg (early binding, thread-safe)
                        self.frame.after(0, lambda msg=error_msg: self.handle_error(msg))
                        return

            except Exception as e:
                self._polling_active = False
                logger.error(f"Error polling for results: {e}")
                # Use default arg to capture exception message (early binding, thread-safe)
                error_str = str(e)
                self.frame.after(0, lambda err=error_str: self.handle_error(f"Error checking task status: {err}"))
        
        # Start polling in background thread with proper reference tracking
        import threading, time
        self._polling_thread = threading.Thread(target=poll_for_results, name=f"SeedreamPolling-{task_id}")
        self._polling_thread.daemon = True
        self._polling_thread.start()
    
    def submit_seedream_v4_task(self, image_url, prompt):
        """Submit Seedream V4 task with detailed logging"""
        try:
            # Get settings
            width = int(self.width_var.get())
            height = int(self.height_var.get())
            size = f"{width}*{height}"
            seed = int(self.seed_var.get()) if self.seed_var.get() != "-1" else -1
            sync_mode = self.sync_mode_var.get()
            base64_output = self.base64_output_var.get()
            
            # Log request details before submission
            self.log_request_submission(prompt, image_url, size, seed, sync_mode, base64_output)
            
            # Submit task
            result = self.api_client.submit_seedream_v4_task(
                prompt=prompt,
                images=[image_url],  # Seedream V4 expects array
                size=size,
                seed=seed,
                enable_sync_mode=sync_mode,
                enable_base64_output=base64_output
            )
            
            if result['success']:
                task_id = result['task_id']
                duration = result.get('duration', 0)
                
                # Log successful submission
                logger.info(f"Seedream V4 task submitted successfully. Task ID: {task_id}")
                
                # Start polling for results
                logger.info(f"About to start polling for task: {task_id}")
                self.start_polling(task_id, duration)
            else:
                error_msg = result.get('error', 'Unknown error occurred')
                # Use default arg to capture error_msg (early binding, thread-safe)
                self.frame.after(0, lambda msg=error_msg: self.handle_error(msg))

        except Exception as e:
            logger.error(f"Seedream V4 task submission failed: {e}")
            # Use default arg to capture exception message (early binding, thread-safe)
            error_str = str(e)
            self.frame.after(0, lambda err=error_str: self.handle_error(f"Task submission failed: {err}"))
    
    def log_request_submission(self, prompt, image_url, size, seed, sync_mode, base64_output):
        """Log request details before submission"""
        try:
            # Get image info
            image_path = self.selected_image_path if hasattr(self, 'selected_image_path') else "N/A"
            image_filename = os.path.basename(image_path) if image_path and image_path != "N/A" else "N/A"
            
            # Log request information
            logger.info("=" * 80)
            logger.info("SEEDREAM V4 REQUEST SUBMISSION")
            logger.info("=" * 80)
            logger.info(f"Prompt: {prompt}")
            logger.info(f"Image: {image_filename} ({image_path})")
            logger.info(f"Image URL: {image_url}")
            logger.info(f"Size: {size}")
            logger.info(f"Seed: {seed}")
            logger.info(f"Sync Mode: {sync_mode}")
            logger.info(f"Base64 Output: {base64_output}")
            logger.info(f"Timestamp: {self.get_current_timestamp()}")
            logger.info("=" * 80)
            
        except Exception as e:
            logger.error(f"Error logging request submission details: {e}")
    
    def handle_success(self, output_url, duration):
        """Handle successful completion with proper backend integration"""
        # Hide progress
        self.hide_progress()
        
        # Get current prompt and settings for logging
        prompt = self.prompt_text.get("1.0", tk.END).strip()
        width = int(self.width_var.get())
        height = int(self.height_var.get())
        seed = self.seed_var.get()
        
        # Use the stored result URL if available, otherwise use the output_url parameter
        result_url = getattr(self, 'last_result_url', None) or output_url
        
        # Download and display result in improved layout
        if hasattr(self, 'improved_layout'):
            # Use the proper download and display method
            self.improved_layout.download_and_display_result(result_url)
            success = True
        else:
            # Fallback to old layout
            success = self.optimized_layout.update_result_image(result_url)
            if success:
                self.result_image = self.optimized_layout.result_image
        
        if success:
            # Show completion status
            self.update_status(f"✅ Seedream V4 completed in {format_duration(duration)}!")
            
            # Attempt auto-save if enabled
            auto_save_success = False
            saved_path = None
            auto_save_error = None
            
            try:
                from app.config import Config
                if Config.AUTO_SAVE_ENABLED:
                    # Check if we have a URL or a local file path
                    if result_url and (result_url.startswith('http://') or result_url.startswith('https://')):
                        # Use URL-based auto-save
                        result = auto_save_manager.save_result(
                            "seedream_v4",
                            result_url,
                            prompt=prompt,
                            extra_info=f"{width}x{height}_seed{seed}"
                        )
                    elif hasattr(self, 'result_image') and self.result_image:
                        # Use local file-based auto-save
                        result = auto_save_manager.save_local_file(
                            "seedream_v4",
                            self.result_image,
                            prompt=prompt,
                            extra_info=f"{width}x{height}_seed{seed}"
                        )
                    else:
                        auto_save_error = "No result URL or local file available for auto-save"
                        result = (False, None, auto_save_error)
                    
                    if isinstance(result, tuple) and len(result) == 3:
                        auto_save_success, saved_path, auto_save_error = result
                        if auto_save_success and saved_path:
                            logger.info(f"Auto-saved Seedream V4 result to: {saved_path}")
                        else:
                            logger.error(f"Auto-save failed: {auto_save_error}")
                    else:
                        # Handle legacy return format
                        saved_path = result
                        auto_save_success = bool(saved_path)
                        if auto_save_success:
                            logger.info(f"Auto-saved Seedream V4 result to: {saved_path}")
                        else:
                            auto_save_error = "Auto-save returned empty path"
            except Exception as e:
                auto_save_error = str(e)
                logger.error(f"Auto-save failed: {e}")
            
            # Track successful prompt
            additional_context = {
                "width": width,
                "height": height,
                "seed": seed,
                "sync_mode": self.sync_mode_var.get(),
                "base64_output": self.base64_output_var.get(),
                "auto_size": getattr(self, 'auto_size_var', tk.BooleanVar()).get(),
                "aspect_ratio_locked": getattr(self, 'aspect_ratio_lock_var', tk.BooleanVar()).get(),
                "auto_saved": auto_save_success
            }
            
            prompt_tracker.log_successful_prompt(
                prompt=prompt,
                ai_model="seedream_v4",
                result_url=result_url,
                save_path=saved_path,
                save_method="auto" if auto_save_success else "manual",
                additional_context=additional_context
            )
            
            # Update status with auto-save information
            if auto_save_success and saved_path:
                self.update_status(f"✅ Seedream V4 completed in {format_duration(duration)}! Auto-saved to: {os.path.basename(saved_path)}")
            else:
                self.update_status(f"✅ Seedream V4 completed in {format_duration(duration)}! (Auto-save failed)")
            
            # Create success message
            success_msg = f"Seedream V4 completed successfully in {format_duration(duration)}!"
            if auto_save_success and saved_path:
                success_msg += f"\n\nResult auto-saved to:\n{saved_path}"
            elif not auto_save_success and auto_save_error:
                success_msg += f"\n\nAuto-save failed: {auto_save_error}"
                # Show warning about auto-save failure
                from utils.utils import show_warning
                show_warning("Auto-Save Failed", f"Result generated successfully but auto-save failed:\n{auto_save_error}\n\nYou can still save the result manually using the Save button.")
            
            show_success("Seedream V4 Complete", success_msg)
        else:
            self.handle_error("Failed to download result image")
    
    def handle_error(self, error_message):
        """Handle processing error with detailed logging"""
        self.hide_progress()
        self.update_status("❌ Processing failed")
        
        # Log detailed error information
        self.log_request_denial(error_message)
        
        # Track failed prompt
        prompt = self.prompt_text.get("1.0", tk.END).strip()
        width = int(self.width_var.get())
        height = int(self.height_var.get())
        seed = self.seed_var.get()
        
        additional_context = {
            "width": width,
            "height": height,
            "seed": seed,
            "sync_mode": self.sync_mode_var.get(),
            "base64_output": self.base64_output_var.get(),
            "auto_size": self.auto_size_var.get(),
            "aspect_ratio_locked": self.aspect_ratio_lock_var.get()
        }
        
        # Determine failure reason from message
        from core.enhanced_prompt_tracker import FailureReason
        
        failure_reason = FailureReason.OTHER
        if "denied" in error_message.lower() or "content policy" in error_message.lower():
            failure_reason = FailureReason.CONTENT_FILTER
        elif "timeout" in error_message.lower():
            failure_reason = FailureReason.TIMEOUT
        elif "invalid" in error_message.lower() or "parameter" in error_message.lower():
            failure_reason = FailureReason.INVALID_PARAMETERS
        elif "quota" in error_message.lower() or "limit" in error_message.lower():
            failure_reason = FailureReason.QUOTA_EXCEEDED
        elif "network" in error_message.lower() or "connection" in error_message.lower():
            failure_reason = FailureReason.NETWORK_ERROR
        elif "server" in error_message.lower() or "500" in error_message or "503" in error_message:
            failure_reason = FailureReason.SERVER_ERROR
        elif "nsfw" in error_message.lower() or "adult content" in error_message.lower():
            failure_reason = FailureReason.NSFW_CONTENT
        elif "api" in error_message.lower() or "401" in error_message or "403" in error_message:
            failure_reason = FailureReason.API_ERROR
        
        prompt_tracker.log_failed_prompt(
            prompt=prompt,
            ai_model="seedream_v4",
            error_message=error_message,
            failure_reason=failure_reason,
            model_parameters=additional_context
        )
        
        show_error("Seedream V4 Error", error_message)
    
    def log_request_denial(self, error_message):
        """Log detailed information about denied requests"""
        try:
            # Get current prompt
            prompt = self.prompt_text.get("1.0", tk.END).strip() if hasattr(self, 'prompt_text') else "N/A"
            
            # Get current settings
            width = int(self.width_var.get()) if hasattr(self, 'width_var') else "N/A"
            height = int(self.height_var.get()) if hasattr(self, 'height_var') else "N/A"
            size = f"{width}*{height}" if width != "N/A" and height != "N/A" else "N/A"
            seed = self.seed_var.get() if hasattr(self, 'seed_var') else "N/A"
            sync_mode = self.sync_mode_var.get() if hasattr(self, 'sync_mode_var') else "N/A"
            base64_output = self.base64_output_var.get() if hasattr(self, 'base64_output_var') else "N/A"
            
            # Get image info
            image_path = self.selected_image_path if hasattr(self, 'selected_image_path') else "N/A"
            image_filename = os.path.basename(image_path) if image_path and image_path != "N/A" else "N/A"
            
            # Log comprehensive denial information
            logger.error("=" * 80)
            logger.error("SEEDREAM V4 REQUEST DENIED")
            logger.error("=" * 80)
            logger.error(f"Error Message: {error_message}")
            logger.error(f"Prompt: {prompt}")
            logger.error(f"Image: {image_filename} ({image_path})")
            logger.error(f"Size: {size}")
            logger.error(f"Seed: {seed}")
            logger.error(f"Sync Mode: {sync_mode}")
            logger.error(f"Base64 Output: {base64_output}")
            logger.error(f"Timestamp: {self.get_current_timestamp()}")
            logger.error("=" * 80)
            
        except Exception as e:
            logger.error(f"Error logging request denial details: {e}")
    
    def get_current_timestamp(self):
        """Get current timestamp for logging"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def sanitize_filename(self, filename):
        """Sanitize filename to remove invalid characters for Windows/Unix compatibility"""
        import re
        # Remove or replace invalid characters
        invalid_chars = r'[<>:"/\\|?*]'
        sanitized = re.sub(invalid_chars, '_', filename)
        # Remove multiple consecutive underscores
        sanitized = re.sub(r'_+', '_', sanitized)
        # Remove leading/trailing underscores
        sanitized = sanitized.strip('_')
        return sanitized
    
    def save_result_image_directly(self, prompt, extra_info):
        """Save result image directly as fallback when URL auto-save fails"""
        try:
            from datetime import datetime
            from pathlib import Path
            
            # Create save directory
            save_dir = Path("WaveSpeed_Results") / "Seedream_V4"
            save_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            prompt_part = ""
            if prompt:
                # Clean prompt for filename
                clean_prompt = "".join(c for c in prompt[:30] if c.isalnum() or c in (' ', '-', '_')).strip()
                prompt_part = f"_{clean_prompt.replace(' ', '_')}"
            
            # Create and sanitize filename
            filename = f"seedream_v4_{timestamp}{prompt_part}_{extra_info}.png"
            filename = self.sanitize_filename(filename)
            save_path = save_dir / filename
            
            # Save the image
            self.result_image.save(save_path, 'PNG')
            
            # Create metadata file
            metadata = {
                "ai_model": "seedream_v4",
                "timestamp": timestamp,
                "prompt": prompt,
                "extra_info": extra_info,
                "filename": filename,
                "saved_directly": True
            }
            
            metadata_path = save_path.with_suffix('.json')
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            logger.info(f"Direct save successful: {save_path}")
            return True, str(save_path)
            
        except Exception as e:
            logger.error(f"Direct save failed: {e}")
            return False, str(e)
    
    def save_result_image(self):
        """Save result image to file"""
        if not self.result_image:
            show_error("No Result", "No result image to save.")
            return
        
        from tkinter import filedialog
        
        file_path = filedialog.asksaveasfilename(
            title="Save Seedream V4 Result",
            defaultextension=".png",
            filetypes=[
                ("PNG files", "*.png"),
                ("JPEG files", "*.jpg"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            try:
                self.result_image.save(file_path)
                
                # Log successful prompt when user saves
                prompt = self.prompt_text.get("1.0", tk.END).strip()
                width = int(self.width_var.get())
                height = int(self.height_var.get())
                seed = self.seed_var.get()
                
                additional_context = {
                    "width": width,
                    "height": height,
                    "seed": seed,
                    "sync_mode": self.sync_mode_var.get(),
                    "base64_output": self.base64_output_var.get(),
                    "auto_size": self.auto_size_var.get(),
                    "aspect_ratio_locked": self.aspect_ratio_lock_var.get(),
                    "manual_save": True
                }
                
                prompt_tracker.log_successful_prompt(
                    prompt=prompt,
                    ai_model="seedream_v4",
                    result_url=getattr(self, 'last_result_url', None),
                    save_path=file_path,
                    additional_context=additional_context
                )
                
                show_success("Image Saved", f"Result saved to:\n{file_path}")
            except Exception as e:
                show_error("Save Error", f"Failed to save image: {str(e)}")
    
    def use_result_as_input(self):
        """Use result image as new input"""
        if not self.result_image:
            show_error("No Result", "No result image to use as input.")
            return
        
        try:
            from PIL import Image
            import tempfile
            
            # Handle both string path and PIL Image object
            if isinstance(self.result_image, str):
                # It's already a path, use it directly if it exists
                if os.path.exists(self.result_image):
                    result_path = self.result_image
                else:
                    # Try to get from improved layout
                    if hasattr(self, 'improved_layout') and hasattr(self.improved_layout, 'result_image_path'):
                        result_path = self.improved_layout.result_image_path
                    else:
                        show_error("Error", "Result image file not found.")
                        return
            else:
                # It's a PIL Image object, save to temp file
                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
                    result_path = temp_file.name
                    self.result_image.save(result_path, 'PNG')
            
            # Use as new input
            self.on_image_selected(result_path)
            
            # Update status
            self.update_status("✅ Result image set as new input")
                
        except Exception as e:
            logger.error(f"Error using result as input: {e}")
            show_error("Error", f"Failed to use result as input: {str(e)}")
    
    def cleanup_temp_file(self, file_path):
        """Clean up temporary file"""
        try:
            if os.path.exists(file_path):
                os.unlink(file_path)
        except:
            pass
    
    def handle_drag_drop(self, event):
        """Handle drag and drop from system file manager"""
        try:
            # Parse the drag and drop data
            files = parse_drag_drop_data(event.data)
            
            if files:
                first_file = files[0]
                if validate_image_file(first_file):
                    self.on_image_selected(first_file)
                else:
                    show_error("Invalid File", "Please drop a valid image file.")
            
        except Exception as e:
            logger.error(f"Drag and drop error: {e}")
            show_error("Drop Error", f"Failed to process dropped file: {str(e)}")

    def cleanup(self):
        """
        Clean up resources when tab is destroyed or switched away from.

        Prevents memory leaks by:
        - Stopping polling threads
        - Cancelling pending timers
        - Clearing image caches
        - Cleaning up modular components
        """
        try:
            logger.info(f"Cleaning up Seedream V4 tab {self.tab_id}")

            # Stop polling threads
            with self._polling_lock:
                if self._polling_active:
                    logger.info(f"Stopping polling thread for tab {self.tab_id}")
                    self._polling_active = False

                    # Wait for thread to finish (with timeout)
                    if self._polling_thread and self._polling_thread.is_alive():
                        self._polling_thread.join(timeout=0.5)
                        if self._polling_thread.is_alive():
                            logger.warning(f"Polling thread for tab {self.tab_id} did not stop cleanly")

            # Clean up modular components (cascades to all managers)
            if hasattr(self, 'improved_layout'):
                if hasattr(self.improved_layout, 'cleanup'):
                    logger.debug(f"Cleaning up improved layout for tab {self.tab_id}")
                    self.improved_layout.cleanup()

            # Clear any pending after() callbacks
            # Note: Tkinter automatically cancels after() callbacks when widgets are destroyed
            # but we can be explicit about critical ones

            logger.info(f"Cleanup completed for Seedream V4 tab {self.tab_id}")

        except Exception as e:
            logger.error(f"Error during cleanup of tab {self.tab_id}: {e}")