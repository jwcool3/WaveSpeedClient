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
from core.prompt_tracker import prompt_tracker

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
        
        # Size limits for validation
        self.min_size = 256
        self.max_size = 4096
        
        # Aspect ratio tracking
        self.original_aspect_ratio = None
        self.aspect_ratio_locked = False
        
        super().__init__(parent_frame, api_client)
    
    def apply_ai_suggestion(self, improved_prompt: str):
        """Apply AI suggestion to prompt text"""
        self.prompt_text.delete("1.0", tk.END)
        self.prompt_text.insert("1.0", improved_prompt)
    
    def setup_ui(self):
        """Setup the improved Seedream V4 UI with new compact layout"""
        # Use the new improved layout instead of the old optimized layout
        from ui.components.improved_seedream_layout import ImprovedSeedreamLayout
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
        self.width_var = self.improved_layout.width_var
        self.height_var = self.improved_layout.height_var
        self.seed_var = self.improved_layout.seed_var
        self.sync_mode_var = self.improved_layout.sync_mode_var
        
        # Add missing variables that other methods expect
        self.size_display_var = tk.StringVar()
        self.aspect_ratio_lock_var = tk.BooleanVar()
    
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
            
            # Auto-save if enabled
            from app.config import Config
            if Config.AUTO_SAVE_ENABLED:
                saved_path = auto_save_manager.save_result(
                    "seedream_v4",
                    result_path,
                    prompt=self.prompt_text.get("1.0", tk.END).strip(),
                    extra_info=f"{self.width_var.get()}x{self.height_var.get()}_seed{self.seed_var.get()}"
                )
                logger.info(f"Auto-saved result to: {saved_path}")
            
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
    
    def setup_seedream_v4_settings(self):
        """Setup Seedream V4 specific settings"""
        settings_container = self.optimized_layout.settings_container
        
        # Size setting with auto-detection and slider
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
        
        # Aspect ratio lock checkbox
        self.aspect_ratio_lock_var = tk.BooleanVar(value=False)
        aspect_lock_checkbox = ttk.Checkbutton(
            size_frame, 
            text="Lock Aspect", 
            variable=self.aspect_ratio_lock_var,
            command=self.toggle_aspect_ratio_lock
        )
        aspect_lock_checkbox.grid(row=0, column=3, sticky=tk.W, padx=(5, 0))
        
        # Size display label
        self.size_display_var = tk.StringVar(value="2048 x 2048")
        size_label = ttk.Label(size_frame, textvariable=self.size_display_var, font=('Arial', 9))
        size_label.grid(row=0, column=2, sticky=tk.E, padx=(5, 0))
        
        # Width slider with number input
        width_frame = ttk.Frame(settings_container)
        width_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        width_frame.columnconfigure(1, weight=1)
        
        ttk.Label(width_frame, text="Width:", font=('Arial', 8)).grid(row=0, column=0, sticky=tk.W)
        
        self.width_var = tk.IntVar(value=2048)
        self.width_slider = ttk.Scale(
            width_frame,
            from_=256,
            to=4096,
            variable=self.width_var,
            orient=tk.HORIZONTAL,
            command=self.update_size_display,
            state="disabled"  # Start disabled for auto mode
        )
        self.width_slider.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 0))
        
        # Width number input
        self.width_entry = ttk.Entry(width_frame, textvariable=self.width_var, width=6, state="disabled")
        self.width_entry.grid(row=0, column=2, sticky=tk.E, padx=(5, 0))
        self.width_entry.bind('<Return>', self.on_width_entry_change)
        self.width_entry.bind('<FocusOut>', self.on_width_entry_change)
        
        # Height slider with number input
        height_frame = ttk.Frame(settings_container)
        height_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        height_frame.columnconfigure(1, weight=1)
        
        ttk.Label(height_frame, text="Height:", font=('Arial', 8)).grid(row=0, column=0, sticky=tk.W)
        
        self.height_var = tk.IntVar(value=2048)
        self.height_slider = ttk.Scale(
            height_frame,
            from_=256,
            to=4096,
            variable=self.height_var,
            orient=tk.HORIZONTAL,
            command=self.update_size_display,
            state="disabled"  # Start disabled for auto mode
        )
        self.height_slider.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 0))
        
        # Height number input
        self.height_entry = ttk.Entry(height_frame, textvariable=self.height_var, width=6, state="disabled")
        self.height_entry.grid(row=0, column=2, sticky=tk.E, padx=(5, 0))
        self.height_entry.bind('<Return>', self.on_height_entry_change)
        self.height_entry.bind('<FocusOut>', self.on_height_entry_change)
        
        # Preset size buttons
        preset_frame = ttk.Frame(settings_container)
        preset_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        preset_frame.columnconfigure(0, weight=1)
        preset_frame.columnconfigure(1, weight=1)
        preset_frame.columnconfigure(2, weight=1)
        
        ttk.Label(preset_frame, text="Preset Sizes:", font=('Arial', 8, 'bold')).grid(row=0, column=0, columnspan=3, sticky=tk.W, pady=(0, 5))
        
        # Common sizes
        preset_sizes = [
            ("1K", "1024*1024"),
            ("2K", "2048*2048"), 
            ("4K", "4096*4096"),
            ("HD", "1920*1080"),
            ("2K HD", "2560*1440"),
            ("4K UHD", "3840*2160")
        ]
        
        # Store preset button references for easy management
        self.preset_buttons = []
        for i, (label, size) in enumerate(preset_sizes):
            btn = ttk.Button(
                preset_frame,
                text=label,
                width=6,
                command=lambda s=size: self.set_preset_size(s),
                state="disabled"  # Start disabled for auto mode
            )
            btn.grid(row=1 + i//3, column=i%3, padx=2, pady=2, sticky=(tk.W, tk.E))
            self.preset_buttons.append(btn)
        
        # Seed setting with random generation
        seed_frame = ttk.Frame(settings_container)
        seed_frame.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
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
        advanced_frame.grid(row=5, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
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
            self.width_slider.config(state="disabled")
            self.height_slider.config(state="disabled")
            self.width_entry.config(state="disabled")
            self.height_entry.config(state="disabled")
            # Disable preset buttons
            for btn in self.preset_buttons:
                btn.config(state="disabled")
            # If we have an image selected, auto-calculate size
            if self.selected_image_path:
                self.auto_set_resolution()
        else:
            self.width_slider.config(state="normal")
            self.height_slider.config(state="normal")
            self.width_entry.config(state="normal")
            self.height_entry.config(state="normal")
            # Enable preset buttons
            for btn in self.preset_buttons:
                btn.config(state="normal")
    
    def toggle_aspect_ratio_lock(self):
        """Toggle aspect ratio lock"""
        self.aspect_ratio_locked = self.aspect_ratio_lock_var.get()
        
        if self.aspect_ratio_locked and self.original_aspect_ratio is None:
            # Try to get aspect ratio from current image
            if self.selected_image_path:
                self.calculate_original_aspect_ratio()
            else:
                # Use current slider values to calculate aspect ratio
                current_width = int(self.width_var.get())
                current_height = int(self.height_var.get())
                if current_width > 0 and current_height > 0:
                    self.original_aspect_ratio = current_width / current_height
                    logger.info(f"Locked aspect ratio to current values: {self.original_aspect_ratio:.3f}")
        
        if self.aspect_ratio_locked:
            logger.info(f"Aspect ratio lock enabled: {self.original_aspect_ratio:.3f}")
        else:
            logger.info("Aspect ratio lock disabled")
    
    def calculate_original_aspect_ratio(self):
        """Calculate aspect ratio from the original image"""
        if not self.selected_image_path:
            return
        
        try:
            from PIL import Image, ImageOps
            image = Image.open(self.selected_image_path)
            image = ImageOps.exif_transpose(image)
            width, height = image.size
            self.original_aspect_ratio = width / height
            logger.info(f"Calculated original aspect ratio: {self.original_aspect_ratio:.3f} ({width}x{height})")
        except Exception as e:
            logger.error(f"Error calculating aspect ratio: {e}")
            self.original_aspect_ratio = None
    
    def update_size_display(self, value=None):
        """Update size display when sliders change"""
        width = int(self.width_var.get())
        height = int(self.height_var.get())
        
        # If aspect ratio is locked, adjust the other dimension
        if self.aspect_ratio_locked and self.original_aspect_ratio is not None:
            # Determine which slider was moved (this is approximate)
            if value is not None:
                # If we have a value, it came from a slider
                if hasattr(self, '_last_width') and hasattr(self, '_last_height'):
                    width_diff = abs(width - self._last_width)
                    height_diff = abs(height - self._last_height)
                    
                    if width_diff > height_diff:
                        # Width slider was moved, adjust height
                        new_height = int(width / self.original_aspect_ratio)
                        new_height = max(256, min(4096, new_height))
                        self.height_var.set(new_height)
                        height = new_height
                    else:
                        # Height slider was moved, adjust width
                        new_width = int(height * self.original_aspect_ratio)
                        new_width = max(256, min(4096, new_width))
                        self.width_var.set(new_width)
                        width = new_width
            
            # Store current values for next comparison
            self._last_width = width
            self._last_height = height
        
        # Update main size display
        self.size_display_var.set(f"{width} x {height}")
    
    def on_width_entry_change(self, event=None):
        """Handle width entry field changes"""
        try:
            value = int(self.width_var.get())
            if 256 <= value <= 4096:
                self.width_var.set(value)
                
                # If aspect ratio is locked, adjust height accordingly
                if self.aspect_ratio_locked and self.original_aspect_ratio is not None:
                    new_height = int(value / self.original_aspect_ratio)
                    new_height = max(256, min(4096, new_height))  # Clamp to valid range
                    self.height_var.set(new_height)
                
                self.update_size_display()
            else:
                # Reset to valid range
                if value < 256:
                    self.width_var.set(256)
                elif value > 4096:
                    self.width_var.set(4096)
                self.update_size_display()
        except (ValueError, tk.TclError):
            # Reset to current slider value if invalid input
            self.width_var.set(int(self.width_slider.get()))
            self.update_size_display()
    
    def on_height_entry_change(self, event=None):
        """Handle height entry field changes"""
        try:
            value = int(self.height_var.get())
            if 256 <= value <= 4096:
                self.height_var.set(value)
                
                # If aspect ratio is locked, adjust width accordingly
                if self.aspect_ratio_locked and self.original_aspect_ratio is not None:
                    new_width = int(value * self.original_aspect_ratio)
                    new_width = max(256, min(4096, new_width))  # Clamp to valid range
                    self.width_var.set(new_width)
                
                self.update_size_display()
            else:
                # Reset to valid range
                if value < 256:
                    self.height_var.set(256)
                elif value > 4096:
                    self.height_var.set(4096)
                self.update_size_display()
        except (ValueError, tk.TclError):
            # Reset to current slider value if invalid input
            self.height_var.set(int(self.height_slider.get()))
            self.update_size_display()
    
    def set_preset_size(self, size_string):
        """Set size from preset button"""
        try:
            width_str, height_str = size_string.split('*')
            width = int(width_str)
            height = int(height_str)
            
            self.width_var.set(width)
            self.height_var.set(height)
            self.update_size_display()
            
            logger.info(f"Set preset size: {size_string}")
        except (ValueError, AttributeError) as e:
            logger.error(f"Error setting preset size {size_string}: {e}")
            show_error("Preset Error", f"Invalid preset size: {size_string}")
    
    def generate_random_seed(self):
        """Generate a random seed"""
        random_seed = random.randint(1, 2147483647)
        self.seed_var.set(str(random_seed))
    
    def auto_set_resolution(self):
        """Automatically set resolution based on input image - pixel perfect matching"""
        if not self.selected_image_path:
            return
        
        try:
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
            
            # Set the sliders to the calculated values
            self.width_var.set(target_width)
            self.height_var.set(target_height)
            
            # Update the display
            self.update_size_display()
            
            logger.info(f"Auto-set resolution to {target_width}x{target_height} for image {original_width}x{original_height}")
            
        except Exception as e:
            logger.error(f"Error auto-setting resolution: {e}")
            # Fallback to default
            self.width_var.set(2048)
            self.height_var.set(2048)
            self.update_size_display()
    
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
            
            # Calculate aspect ratio for potential locking
            self.calculate_original_aspect_ratio()
            
            # Update the improved layout's image display
            if hasattr(self, 'improved_layout'):
                self.improved_layout.load_image(file_path)
            else:
                # Fallback to old layout if improved layout not available
                success = self.optimized_layout.update_input_image(file_path)
                if not success:
                    show_error("Load Error", "Failed to load the selected image.")
                    return
            
            # Auto-set resolution if enabled
            if hasattr(self, 'auto_size_var') and self.auto_size_var.get():
                self.auto_set_resolution()
            
            # Update status
            filename = os.path.basename(file_path)
            self.update_status(f"📁 Image loaded: {filename}")
                
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
        
        # Clear images
        self.selected_image_path = None
        self.result_image = None
        
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
                    self.frame.after(0, lambda: self.handle_error("Image upload failed"))
                    
            except Exception as e:
                logger.error(f"Background process error: {e}")
                self.frame.after(0, lambda: self.handle_error(f"Processing error: {str(e)}"))
        
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
                # Fallback to sample URL with explanation
                from utils.utils import show_warning
                show_warning(
                    "Upload Failed - Using Sample", 
                    f"Could not upload your image securely.\n\n"
                    f"Error: {privacy_info}\n\n"
                    f"Using sample image for demonstration.\n"
                    f"Your selected image: {image_path}\n\n"
                    f"Note: This is a demo mode. In production, images would be uploaded securely."
                )
                
                # Fallback to sample URL
                return "https://example.com/sample-image.png"
                
        except Exception as e:
            logger.error(f"Image upload with rotation fix failed: {e}")
            
            # Fallback to sample URL
            from utils.utils import show_error
            show_error(
                "Upload Error", 
                f"Failed to upload image: {str(e)}\n\n"
                f"Using sample image for demonstration."
            )
            
            return "https://example.com/sample-image.png"
    
    def start_polling(self, task_id, duration):
        """Start polling for task results"""
        # Stop any existing polling to prevent multiple threads
        if hasattr(self, '_polling_active') and self._polling_active:
            logger.info("Stopping existing polling thread")
            self._polling_active = False
        
        # Wait a moment for existing thread to stop
        import time
        time.sleep(0.1)
        
        self._polling_active = True
        logger.info(f"Starting polling for task: {task_id}")
        
        def poll_for_results():
            try:
                if not self._polling_active:
                    return
                    
                result = self.api_client.get_seedream_v4_result(task_id)
                
                if result['success']:
                    status = result.get('status')
                    
                    if status == 'completed':
                        self._polling_active = False
                        logger.info(f"Task completed, stopping polling for task: {task_id}")
                        output_url = result.get('output_url')
                        if output_url:
                            self.frame.after(0, lambda: self.handle_success(output_url, duration))
                        else:
                            self.frame.after(0, lambda: self.handle_error("No output URL in completed result"))
                    elif status == 'failed':
                        self._polling_active = False
                        error_msg = result.get('error', 'Task failed')
                        self.frame.after(0, lambda: self.handle_error(error_msg))
                    else:
                        # Still processing, schedule next poll in 2 seconds
                        if self._polling_active:
                            self.frame.after(2000, lambda: self._poll_once(task_id, duration))
                else:
                    self._polling_active = False
                    error_msg = result.get('error', 'Failed to get task status')
                    self.frame.after(0, lambda: self.handle_error(error_msg))
                    
            except Exception as e:
                self._polling_active = False
                logger.error(f"Error polling for results: {e}")
                self.frame.after(0, lambda: self.handle_error(f"Error checking task status: {str(e)}"))
        
        # Start polling in background thread
        import threading
        thread = threading.Thread(target=poll_for_results)
        thread.daemon = True
        thread.start()
    
    def _poll_once(self, task_id, duration):
        """Single poll attempt - prevents recursive thread creation"""
        if not hasattr(self, '_polling_active') or not self._polling_active:
            return
            
        try:
            result = self.api_client.get_seedream_v4_result(task_id)
            
            if result['success']:
                status = result.get('status')
                
                if status == 'completed':
                    self._polling_active = False
                    logger.info(f"Task completed, stopping polling for task: {task_id}")
                    output_url = result.get('output_url')
                    if output_url:
                        self.frame.after(0, lambda: self.handle_success(output_url, duration))
                    else:
                        self.frame.after(0, lambda: self.handle_error("No output URL in completed result"))
                    return  # Exit immediately after completion
                elif status == 'failed':
                    self._polling_active = False
                    error_msg = result.get('error', 'Task failed')
                    self.frame.after(0, lambda: self.handle_error(error_msg))
                    return  # Exit immediately after failure
                else:
                    # Still processing, schedule next poll in 2 seconds
                    if self._polling_active:
                        self.frame.after(2000, lambda: self._poll_once(task_id, duration))
            else:
                self._polling_active = False
                error_msg = result.get('error', 'Failed to get task status')
                self.frame.after(0, lambda: self.handle_error(error_msg))
                
        except Exception as e:
            self._polling_active = False
            logger.error(f"Error polling for results: {e}")
            self.frame.after(0, lambda: self.handle_error(f"Error checking task status: {str(e)}"))
    
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
                self.frame.after(0, lambda: self.handle_error(error_msg))
                
        except Exception as e:
            logger.error(f"Seedream V4 task submission failed: {e}")
            self.frame.after(0, lambda: self.handle_error(f"Task submission failed: {str(e)}"))
    
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
        """Handle successful completion"""
        # Hide progress
        self.hide_progress()
        
        # Download and display result in improved layout
        if hasattr(self, 'improved_layout'):
            # Use the proper download and display method
            self.improved_layout.download_and_display_result(output_url)
            success = True
        else:
            # Fallback to old layout
            success = self.optimized_layout.update_result_image(output_url)
            if success:
                self.result_image = self.optimized_layout.result_image
        
        if success:
            # Show completion status
            self.update_status(f"✅ Seedream V4 completed in {format_duration(duration)}!")
            
            # If auto-save failed, try to save the result image directly
            if not success and self.result_image:
                logger.warning(f"Auto-save from URL failed, attempting to save result image directly: {error}")
                try:
                    # Try to save the result image directly
                    fallback_success, fallback_path = self.save_result_image_directly(prompt, extra_info)
                    if fallback_success:
                        success = True
                        saved_path = fallback_path
                        error = None
                        logger.info(f"Fallback auto-save successful: {saved_path}")
                    else:
                        logger.error(f"Fallback auto-save also failed: {fallback_path}")
                except Exception as e:
                    logger.error(f"Fallback auto-save error: {e}")
            
            # Log auto-save result
            if success:
                logger.info(f"Seedream V4 result auto-saved successfully to: {saved_path}")
                
                # Track successful prompt for auto-saved results
                additional_context = {
                    "width": width,
                    "height": height,
                    "seed": seed,
                    "sync_mode": self.sync_mode_var.get(),
                    "base64_output": self.base64_output_var.get(),
                    "auto_size": self.auto_size_var.get(),
                    "aspect_ratio_locked": self.aspect_ratio_lock_var.get(),
                    "auto_saved": True
                }
                
                prompt_tracker.log_successful_prompt(
                    prompt=prompt,
                    ai_model="seedream_v4",
                    result_url=output_url,
                    save_path=saved_path,
                    additional_context=additional_context
                )
            else:
                logger.error(f"Seedream V4 auto-save failed: {error}")
            
            # Update status with auto-save information
            if success and saved_path:
                self.update_status(f"✅ Seedream V4 completed in {format_duration(duration)}! Auto-saved to: {os.path.basename(saved_path)}")
            else:
                self.update_status(f"✅ Seedream V4 completed in {format_duration(duration)}! (Auto-save failed)")
            
            success_msg = f"Seedream V4 completed successfully in {format_duration(duration)}!"
            if success and saved_path:
                success_msg += f"\n\nResult auto-saved to:\n{saved_path}"
            elif not success:
                success_msg += f"\n\nAuto-save failed: {error}"
                # Show warning about auto-save failure
                from utils.utils import show_warning
                show_warning("Auto-Save Failed", f"Result generated successfully but auto-save failed:\n{error}\n\nYou can still save the result manually using the Save button.")
            
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
        
        # Determine error type from message
        error_type = "api_error"
        if "denied" in error_message.lower():
            error_type = "request_denied"
        elif "timeout" in error_message.lower():
            error_type = "timeout"
        elif "invalid" in error_message.lower():
            error_type = "invalid_parameters"
        elif "quota" in error_message.lower() or "limit" in error_message.lower():
            error_type = "quota_exceeded"
        
        prompt_tracker.log_failed_prompt(
            prompt=prompt,
            ai_model="seedream_v4",
            error_message=error_message,
            error_type=error_type,
            additional_context=additional_context
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
            # Save result to temporary file
            import tempfile
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
                temp_path = temp_file.name
                self.result_image.save(temp_path, 'PNG')
            
            # Use as new input - call the method directly without replacing_image parameter
            self.on_image_selected(temp_path)
            
            # Clean up temp file after a longer delay to ensure it's processed
            self.frame.after(10000, lambda: self.cleanup_temp_file(temp_path))
            
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