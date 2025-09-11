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
from PIL import Image, ImageTk, ImageOps
from ui.components.ui_components import BaseTab
from ui.components.optimized_image_layout import OptimizedImageLayout
from ui.components.enhanced_image_display import EnhancedImageSelector, EnhancedImagePreview
from utils.utils import *
from core.auto_save import auto_save_manager
from core.secure_upload import privacy_uploader
from core.logger import get_logger

logger = get_logger()


class SeedreamV4Tab(BaseTab):
    """Seedream V4 Multi-Modal Image Editor Tab - IMPROVED VERSION"""
    
    def __init__(self, parent_frame, api_client, main_app=None):
        self.result_image = None
        self.main_app = main_app
        self.selected_image_path = None
        self.auto_resolution = True  # Auto-set resolution based on input image
        
        # Prompt storage for Seedream V4
        self.seedream_v4_prompts_file = "data/seedream_v4_prompts.json"
        self.saved_seedream_v4_prompts = load_json_file(self.seedream_v4_prompts_file, [])
        
        # Supported sizes as (width, height) tuples for easy calculation
        self.supported_sizes = [
            (1024, 1024),
            (1024, 2048), 
            (2048, 1024),
            (2048, 2048),
            (2048, 4096),
            (4096, 2048),
            (3840, 2160),  # 4K
            (2160, 3840)   # 4K portrait
        ]
        
        super().__init__(parent_frame, api_client)
    
    def apply_ai_suggestion(self, improved_prompt: str):
        """Apply AI suggestion to prompt text"""
        self.prompt_text.delete("1.0", tk.END)
        self.prompt_text.insert("1.0", improved_prompt)
    
    def setup_ui(self):
        """Setup the optimized Seedream V4 UI matching SeedEdit quality"""
        # Keep the scrollable canvas components for proper scrolling
        # Use the same optimized layout as SeedEdit for consistency
        self.optimized_layout = OptimizedImageLayout(self.scrollable_frame, "Seedream V4")
        
        # Setup Seedream V4 specific settings
        self.setup_seedream_v4_settings()
        
        # Setup prompt section in the left panel
        self.setup_compact_prompt_section()
        
        # Configure main action button
        self.optimized_layout.set_main_action("🌟 Apply Seedream V4", self.process_task)
        
        # Connect image selector
        self.optimized_layout.set_image_selector_command(self.browse_image)
        
        # Connect result buttons
        self.optimized_layout.set_result_button_commands(
            self.save_result_image, 
            self.use_result_as_input
        )
        
        # Connect sample and clear buttons
        self.optimized_layout.sample_button.config(command=self.load_sample_prompt)
        self.optimized_layout.clear_button.config(command=self.clear_all)
        
        # Connect drag and drop handling
        self.optimized_layout.set_parent_tab(self)
        
        # Setup cross-tab sharing
        self.optimized_layout.create_cross_tab_button(self.main_app, "Seedream V4")
        
        # Setup progress section in the left panel
        self.setup_compact_progress_section()
    
    def setup_seedream_v4_settings(self):
        """Setup Seedream V4 specific settings"""
        settings_container = self.optimized_layout.settings_container
        
        # Size setting with auto-detection
        size_frame = ttk.Frame(settings_container)
        size_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        size_frame.columnconfigure(1, weight=1)
        
        ttk.Label(size_frame, text="Size:", font=('Arial', 9)).grid(row=0, column=0, sticky=tk.W)
        
        # Auto size checkbox
        self.auto_size_var = tk.BooleanVar(value=True)
        auto_checkbox = ttk.Checkbutton(
            size_frame, 
            text="Auto", 
            variable=self.auto_size_var,
            command=self.toggle_auto_size
        )
        auto_checkbox.grid(row=0, column=1, sticky=tk.W, padx=(5, 0))
        
        # Size selector (initially disabled)
        self.size_var = tk.StringVar(value="2048*2048")
        self.size_combo = ttk.Combobox(
            size_frame, 
            textvariable=self.size_var,
            values=[
                "1024*1024",
                "1024*2048", 
                "2048*1024",
                "2048*2048",
                "2048*4096",
                "4096*2048",
                "3840*2160",
                "2160*3840"
            ],
            state="disabled",  # Start disabled for auto mode
            width=12
        )
        self.size_combo.grid(row=0, column=2, sticky=tk.E, padx=(5, 0))
        
        # Seed setting with random generation
        seed_frame = ttk.Frame(settings_container)
        seed_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        seed_frame.columnconfigure(1, weight=1)
        
        ttk.Label(seed_frame, text="Seed:", font=('Arial', 9)).grid(row=0, column=0, sticky=tk.W)
        
        # Seed controls frame
        seed_controls = ttk.Frame(seed_frame)
        seed_controls.grid(row=0, column=1, sticky=tk.E, padx=(5, 0))
        
        self.seed_var = tk.StringVar(value="-1")
        seed_entry = ttk.Entry(seed_controls, textvariable=self.seed_var, width=12)
        seed_entry.grid(row=0, column=0, padx=(0, 2))
        
        # Random seed button
        random_button = ttk.Button(
            seed_controls, 
            text="🎲", 
            width=3,
            command=self.generate_random_seed
        )
        random_button.grid(row=0, column=1)
        
        # Advanced options
        advanced_frame = ttk.Frame(settings_container)
        advanced_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        advanced_frame.columnconfigure(0, weight=1)
        
        # Sync mode checkbox
        self.sync_mode_var = tk.BooleanVar(value=False)
        sync_checkbox = ttk.Checkbutton(
            advanced_frame,
            text="Enable Sync Mode",
            variable=self.sync_mode_var
        )
        sync_checkbox.grid(row=0, column=0, sticky=tk.W)
        
        # Base64 output checkbox
        self.base64_output_var = tk.BooleanVar(value=False)
        base64_checkbox = ttk.Checkbutton(
            advanced_frame,
            text="Enable Base64 Output",
            variable=self.base64_output_var
        )
        base64_checkbox.grid(row=1, column=0, sticky=tk.W)
    
    def toggle_auto_size(self):
        """Toggle auto size detection"""
        if self.auto_size_var.get():
            self.size_combo.config(state="disabled")
            # If we have an image selected, auto-calculate size
            if self.selected_image_path:
                self.auto_set_resolution()
        else:
            self.size_combo.config(state="readonly")
    
    def generate_random_seed(self):
        """Generate a random seed"""
        random_seed = random.randint(1, 2147483647)
        self.seed_var.set(str(random_seed))
    
    def auto_set_resolution(self):
        """Automatically set resolution based on input image"""
        if not self.selected_image_path:
            return
        
        try:
            # Fix image rotation before getting dimensions
            image = Image.open(self.selected_image_path)
            
            # Apply EXIF orientation correction
            image = ImageOps.exif_transpose(image)
            
            original_width, original_height = image.size
            original_aspect = original_width / original_height
            
            # Find the best matching size that fits within limits and maintains aspect ratio
            best_size = None
            min_scale_factor = float('inf')
            max_dimension = 4096  # Maximum supported dimension
            
            for width, height in self.supported_sizes:
                target_aspect = width / height
                
                # Calculate how much we'd need to scale the original
                if abs(target_aspect - original_aspect) < 0.1:  # Similar aspect ratio
                    scale_factor = max(width / original_width, height / original_height)
                    
                    # Prefer smaller scale factors (less upscaling) but ensure minimum quality
                    if scale_factor <= 4.0 and scale_factor < min_scale_factor:
                        best_size = (width, height)
                        min_scale_factor = scale_factor
            
            # If no good aspect ratio match, find closest by area that doesn't exceed limits
            if not best_size:
                original_area = original_width * original_height
                
                for width, height in self.supported_sizes:
                    if width <= max_dimension and height <= max_dimension:
                        if not best_size:
                            best_size = (width, height)
                        else:
                            # Choose size with area closest to original
                            current_area = width * height
                            best_area = best_size[0] * best_size[1]
                            
                            if abs(current_area - original_area) < abs(best_area - original_area):
                                best_size = (width, height)
            
            # Set the best size
            if best_size:
                size_string = f"{best_size[0]}*{best_size[1]}"
                self.size_var.set(size_string)
                logger.info(f"Auto-set resolution to {size_string} for image {original_width}x{original_height}")
            
        except Exception as e:
            logger.error(f"Error auto-setting resolution: {e}")
            # Fallback to default
            self.size_var.set("2048*2048")
    
    def browse_image(self):
        """Browse for image file"""
        from tkinter import filedialog
        
        file_path = filedialog.askopenfilename(
            title="Select Image for Seedream V4",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.gif *.bmp *.webp"),
                ("PNG files", "*.png"),
                ("JPEG files", "*.jpg *.jpeg"),
                ("All files", "*.*")
            ]
        )
        if file_path:
            self.on_image_selected(file_path)
    
    def on_image_selected(self, file_path, replacing_image=False):
        """Handle image selection with auto-resolution and rotation fix"""
        try:
            if not validate_image_file(file_path):
                show_error("Invalid Image", "Please select a valid image file.")
                return
            
            self.selected_image_path = file_path
            
            # Update the optimized layout's image display
            success = self.optimized_layout.update_input_image(file_path)
            
            if success:
                # Auto-set resolution if enabled
                if self.auto_size_var.get():
                    self.auto_set_resolution()
                
                # Update status
                filename = os.path.basename(file_path)
                self.update_status(f"📁 Image loaded: {filename}")
            else:
                show_error("Load Error", "Failed to load the selected image.")
                
        except Exception as e:
            logger.error(f"Error selecting image: {e}")
            show_error("Error", f"Failed to load image: {str(e)}")
    
    def setup_compact_prompt_section(self):
        """Setup compact prompt section in the left panel"""
        prompt_container = self.optimized_layout.prompt_container
        
        # Enhanced prompt text area with guidance
        prompt_label = ttk.Label(prompt_container, text="✨ Seedream V4 Prompt", font=('Arial', 9, 'bold'))
        prompt_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        # Guidance text
        guidance_text = ("Use clear instructions: \"change action + change object + target feature\"\n"
                        "For multiple images: \"a series of\", \"group of images\"\n"
                        "Be specific and detailed for best results")
        
        guidance_label = ttk.Label(
            prompt_container, 
            text=guidance_text, 
            font=('Arial', 8), 
            foreground='gray',
            wraplength=280
        )
        guidance_label.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 8))
        
        # Prompt text widget
        prompt_frame = ttk.Frame(prompt_container)
        prompt_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        prompt_frame.columnconfigure(0, weight=1)
        prompt_frame.rowconfigure(0, weight=1)
        
        self.prompt_text = tk.Text(
            prompt_frame,
            height=8,
            wrap=tk.WORD,
            font=('Arial', 9),
            bg='white',
            relief='solid',
            borderwidth=1
        )
        self.prompt_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Scrollbar for prompt text
        prompt_scrollbar = ttk.Scrollbar(prompt_frame, orient=tk.VERTICAL, command=self.prompt_text.yview)
        prompt_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.prompt_text.config(yscrollcommand=prompt_scrollbar.set)
        
        # Placeholder text
        self.prompt_text.insert("1.0", "remove man")
        self.prompt_text.bind("<FocusIn>", self.clear_placeholder)
        
        # Add AI enhancement features to the prompt section
        try:
            from ui.components.ai_prompt_suggestions import add_ai_features_to_prompt_section
            add_ai_features_to_prompt_section(prompt_container, self.prompt_text, 'seedream_v4', self)
        except ImportError:
            logger.warning("AI prompt suggestions not available")
        
        # Prompt management buttons
        prompt_buttons_frame = ttk.Frame(prompt_container)
        prompt_buttons_frame.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        prompt_buttons_frame.columnconfigure(0, weight=1)
        prompt_buttons_frame.columnconfigure(1, weight=1)
        prompt_buttons_frame.columnconfigure(2, weight=1)
        
        # Save prompt button
        save_button = ttk.Button(
            prompt_buttons_frame,
            text="💾 Save",
            command=self.save_current_prompt,
            width=8
        )
        save_button.grid(row=0, column=0, sticky=tk.W)
        
        # Load prompt button
        load_button = ttk.Button(
            prompt_buttons_frame,
            text="📂 Load",
            command=self.load_saved_prompt,
            width=8
        )
        load_button.grid(row=0, column=1, padx=5)
        
        # Delete prompt button
        delete_button = ttk.Button(
            prompt_buttons_frame,
            text="🗑️ Delete",
            command=self.delete_saved_prompt,
            width=8
        )
        delete_button.grid(row=0, column=2, sticky=tk.E)
    
    def clear_placeholder(self, event):
        """Clear placeholder text when focused"""
        if self.prompt_text.get("1.0", tk.END).strip() == "remove man":
            self.prompt_text.delete("1.0", tk.END)
    
    def setup_compact_progress_section(self):
        """Setup compact progress section"""
        progress_container = self.optimized_layout.progress_container
        
        # Progress bar
        self.progress_bar = ttk.Progressbar(
            progress_container,
            mode='indeterminate',
            length=200
        )
        self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        
        # Status label
        self.status_label = ttk.Label(
            progress_container,
            text="Ready for Seedream V4 processing",
            font=('Arial', 9)
        )
        self.status_label.grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        
        # Initially hide progress
        self.progress_bar.grid_remove()
    
    def show_progress(self, message="Processing..."):
        """Show progress indicator"""
        self.progress_bar.grid()
        self.progress_bar.start(10)
        self.status_label.config(text=message)
    
    def hide_progress(self):
        """Hide progress indicator"""
        self.progress_bar.stop()
        self.progress_bar.grid_remove()
    
    def update_status(self, message):
        """Update status message"""
        self.status_label.config(text=message)
    
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
        self.size_var.set("2048*2048")
        self.sync_mode_var.set(False)
        self.base64_output_var.set(False)
        self.auto_size_var.set(True)
        self.size_combo.config(state="disabled")
        
        # Clear images
        self.selected_image_path = None
        self.result_image = None
        self.optimized_layout.clear_input_image()
        self.optimized_layout.clear_result_image()
        
        self.update_status("All inputs cleared")
    
    def process_task(self):
        """Process Seedream V4 task"""
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
                    self.frame.after(0, lambda: self.handle_error("Image upload failed"))
                    
            except Exception as e:
                logger.error(f"Background process error: {e}")
                self.frame.after(0, lambda: self.handle_error(f"Processing error: {str(e)}"))
        
        thread = threading.Thread(target=background_process)
        thread.daemon = True
        thread.start()
    
    def upload_image_with_rotation_fix(self, image_path):
        """Upload image with EXIF rotation correction"""
        try:
            # Open image and fix rotation
            image = Image.open(image_path)
            
            # Apply EXIF orientation correction
            image = ImageOps.exif_transpose(image)
            
            # Save corrected image to temporary file
            import tempfile
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
                temp_path = temp_file.name
                image.save(temp_path, 'PNG')
            
            # Upload the corrected image
            try:
                result = privacy_uploader.upload_file(
                    temp_path,
                    auto_delete_after_hours=24
                )
                
                if result['success']:
                    logger.info(f"Seedream V4 image uploaded successfully: {result['url']}")
                    return result['url']
                else:
                    logger.error(f"Upload failed: {result['error']}")
                    return None
                    
            finally:
                # Clean up temp file
                try:
                    os.unlink(temp_path)
                except:
                    pass
                
        except Exception as e:
            logger.error(f"Image upload with rotation fix failed: {e}")
            return None
    
    def submit_seedream_v4_task(self, image_url, prompt):
        """Submit Seedream V4 task"""
        try:
            # Get settings
            size = self.size_var.get()
            seed = int(self.seed_var.get()) if self.seed_var.get() != "-1" else -1
            sync_mode = self.sync_mode_var.get()
            base64_output = self.base64_output_var.get()
            
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
                output_url = result['output_url']
                duration = result.get('duration', 0)
                
                self.frame.after(0, lambda: self.handle_success(output_url, duration))
            else:
                error_msg = result.get('error', 'Unknown error occurred')
                self.frame.after(0, lambda: self.handle_error(error_msg))
                
        except Exception as e:
            logger.error(f"Seedream V4 task submission failed: {e}")
            self.frame.after(0, lambda: self.handle_error(f"Task submission failed: {str(e)}"))
    
    def handle_success(self, output_url, duration):
        """Handle successful completion"""
        # Hide progress
        self.hide_progress()
        
        # Download and display result in optimized layout
        success = self.optimized_layout.update_result_image(output_url)
        
        if success:
            self.result_image = self.optimized_layout.result_image
            
            # Auto-save the result
            prompt = self.prompt_text.get("1.0", tk.END).strip()
            size = self.size_var.get()
            seed = self.seed_var.get()
            extra_info = f"{size}_seed{seed}"
            
            success, saved_path, error = auto_save_manager.save_result(
                'seedream_v4', 
                output_url, 
                prompt=prompt, 
                extra_info=extra_info
            )
            
            # Update status
            self.update_status(f"✅ Seedream V4 completed in {format_duration(duration)}!")
            
            success_msg = f"Seedream V4 completed successfully in {format_duration(duration)}!"
            if success and saved_path:
                success_msg += f"\n\nResult auto-saved to:\n{saved_path}"
            
            show_success("Seedream V4 Complete", success_msg)
        else:
            self.handle_error("Failed to download result image")
    
    def handle_error(self, error_message):
        """Handle processing error"""
        self.hide_progress()
        self.update_status("❌ Processing failed")
        show_error("Seedream V4 Error", error_message)
    
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
                show_success("Image Saved", f"Result saved to:\n{file_path}")
            except Exception as e:
                show_error("Save Error", f"Failed to save image: {str(e)}")
    
    def use_result_as_input(self):
        """Use result image as new input"""
        if not self.result_image:
            show_error("No Result", "No result image to use as input.")
            return
        
        try:
            # Save result to temporary file
            import tempfile
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
                temp_path = temp_file.name
                self.result_image.save(temp_path, 'PNG')
            
            # Use as new input
            self.on_image_selected(temp_path, replacing_image=True)
            
            # Clean up temp file after a delay
            self.frame.after(5000, lambda: self.cleanup_temp_file(temp_path))
                
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