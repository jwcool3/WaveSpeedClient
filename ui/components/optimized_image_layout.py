"""
Optimized Image Layout Component for WaveSpeed AI Application

This module provides a space-efficient layout for image editing tabs,
with large image displays and compact, well-organized controls.
"""

import tkinter as tk
from tkinter import ttk
import os
from PIL import Image, ImageTk
from utils.utils import load_image_preview, validate_image_file, show_error, parse_drag_drop_data
from ui.components.enhanced_image_display import EnhancedImageSelector, EnhancedImagePreview
from core.logger import get_logger

logger = get_logger()

# Try to import drag and drop support
try:
    from tkinterdnd2 import DND_FILES
    DND_AVAILABLE = True
except ImportError:
    DND_AVAILABLE = False


class OptimizedImageLayout:
    """Optimized layout for image editing tabs with better space utilization"""
    
    def __init__(self, parent_frame, title="Image Processing"):
        self.parent_frame = parent_frame
        self.title = title
        self.selected_image_path = None
        self.result_image = None
        
        # Parent frame will be managed by pack, so no grid configuration needed
        
        # Create main layout
        self.setup_optimized_layout()
    
    def setup_optimized_layout(self):
        """Setup the optimized layout with better space utilization"""
        
        # Main container with horizontal layout - use pack to be compatible with BaseTab
        main_container = ttk.Frame(self.parent_frame)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        main_container.columnconfigure(1, weight=3)  # Images get 3x more space
        main_container.columnconfigure(0, weight=1)  # Controls get 1x space
        main_container.rowconfigure(0, weight=1)
        
        # Left panel - Compact controls (30% of width)
        self.setup_left_panel(main_container)
        
        # Right panel - Large image displays (70% of width)
        self.setup_right_panel(main_container)
    
    def setup_left_panel(self, parent):
        """Setup compact left control panel"""
        left_panel = ttk.Frame(parent)
        left_panel.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        left_panel.columnconfigure(0, weight=1)
        
        # Configure rows for proper vertical distribution
        left_panel.rowconfigure(0, weight=0)  # Image selector - fixed size
        left_panel.rowconfigure(1, weight=0)  # Settings - fixed size
        left_panel.rowconfigure(2, weight=1)  # Prompts - expandable
        left_panel.rowconfigure(3, weight=0)  # Action buttons - fixed size
        left_panel.rowconfigure(4, weight=0)  # Progress - fixed size
        
        # Compact image selection
        self.setup_compact_image_selector(left_panel)
        
        # Compact settings
        self.setup_compact_settings(left_panel)
        
        # Action buttons with spacer
        self.setup_action_buttons(left_panel)
    
    def setup_compact_image_selector(self, parent):
        """Setup very compact image selector"""
        # Image selection section
        image_section = ttk.LabelFrame(parent, text="📸 Input Image", padding="8")
        image_section.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        image_section.columnconfigure(0, weight=1)
        
        # File browser button
        browse_frame = ttk.Frame(image_section)
        browse_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))
        browse_frame.columnconfigure(0, weight=1)
        
        self.browse_button = ttk.Button(browse_frame, text="📁 Browse Image")
        self.browse_button.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # Selected image label
        self.image_path_label = ttk.Label(browse_frame, text="No image selected", 
                                         foreground="gray", font=('Arial', 9))
        self.image_path_label.grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        
        # Small preview area
        self.preview_frame = ttk.Frame(image_section)
        self.preview_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        self.preview_frame.columnconfigure(0, weight=1)
        
        self.preview_label = ttk.Label(self.preview_frame, text="📷", 
                                      font=('Arial', 24), foreground="lightgray")
        self.preview_label.grid(row=0, column=0)
    
    def setup_compact_settings(self, parent):
        """Setup compact settings section"""
        self.settings_frame = ttk.LabelFrame(parent, text="⚙️ Settings", padding="8")
        self.settings_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        self.settings_frame.columnconfigure(0, weight=1)
        
        # Placeholder for settings - will be populated by subclasses
        self.settings_container = ttk.Frame(self.settings_frame)
        self.settings_container.grid(row=0, column=0, sticky=(tk.W, tk.E))
        self.settings_container.columnconfigure(0, weight=1)
    
    def setup_action_buttons(self, parent):
        """Setup action buttons with vertical spacer"""
        # Create a spacer that expands to push buttons to bottom
        spacer_frame = ttk.Frame(parent)
        spacer_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Action buttons at the bottom of left panel
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        button_frame.columnconfigure(0, weight=1)
        
        # Main action button (will be set by specific tab)
        self.main_action_button = ttk.Button(
            button_frame,
            text="Process Image",
            style="Accent.TButton"
        )
        self.main_action_button.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # Secondary buttons
        secondary_frame = ttk.Frame(button_frame)
        secondary_frame.grid(row=1, column=0, sticky=(tk.W, tk.E))
        secondary_frame.columnconfigure(0, weight=1)
        secondary_frame.columnconfigure(1, weight=1)
        
        self.clear_button = ttk.Button(
            secondary_frame,
            text="🗑️ Clear",
            command=self.clear_all
        )
        self.clear_button.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 2))
        
        self.sample_button = ttk.Button(
            secondary_frame,
            text="📝 Sample",
            command=self.load_sample
        )
        self.sample_button.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(2, 0))
    
    def setup_right_panel(self, parent):
        """Setup large image display panel"""
        right_panel = ttk.Frame(parent)
        right_panel.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        right_panel.columnconfigure(0, weight=1)
        right_panel.rowconfigure(0, weight=1)
        
        # Create notebook for before/after images
        self.image_notebook = ttk.Notebook(right_panel)
        self.image_notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Input image tab
        self.input_frame = ttk.Frame(self.image_notebook)
        self.image_notebook.add(self.input_frame, text="📷 Input Image")
        
        # Result image tab
        self.result_frame = ttk.Frame(self.image_notebook)
        self.image_notebook.add(self.result_frame, text="✨ Edited Result")
        
        # Setup image displays
        self.setup_input_image_display()
        self.setup_result_image_display()
    
    def setup_input_image_display(self):
        """Setup input image display"""
        self.input_frame.columnconfigure(0, weight=1)
        self.input_frame.rowconfigure(0, weight=1)
        
        # Input image display
        self.input_display_frame = ttk.Frame(self.input_frame, relief='solid', borderwidth=1)
        self.input_display_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=10)
        self.input_display_frame.columnconfigure(0, weight=1)
        self.input_display_frame.rowconfigure(0, weight=1)
        
        # Placeholder for input image
        self.input_image_label = tk.Label(
            self.input_display_frame,
            text="📷 Select an image to edit\n\nDrag & drop supported",
            font=('Arial', 16),
            fg='#666666',
            bg='#f8f8f8',
            justify=tk.CENTER
        )
        self.input_image_label.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Setup drag and drop for input
        if DND_AVAILABLE:
            try:
                self.input_display_frame.drop_target_register(DND_FILES)
                self.input_display_frame.dnd_bind('<<Drop>>', self.on_drop)
                logger.info("Drag and drop enabled for image input")
            except Exception as e:
                logger.warning(f"Failed to setup drag and drop: {e}")
        
        # Store reference to parent tab for drag and drop handling
        self.parent_tab = None
    
    def setup_result_image_display(self):
        """Setup result image display"""
        self.result_frame.columnconfigure(0, weight=1)
        self.result_frame.rowconfigure(0, weight=1)
        
        # Result image display
        self.result_display_frame = ttk.Frame(self.result_frame, relief='solid', borderwidth=1)
        self.result_display_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=(10, 5))
        self.result_display_frame.columnconfigure(0, weight=1)
        self.result_display_frame.rowconfigure(0, weight=1)
        
        # Placeholder for result image
        self.result_image_label = tk.Label(
            self.result_display_frame,
            text="✨ Edited result will appear here\n\nDouble-click to view full size",
            font=('Arial', 16),
            fg='#666666',
            bg='#f8f8f8',
            justify=tk.CENTER
        )
        self.result_image_label.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Result action buttons
        result_buttons_frame = ttk.Frame(self.result_frame)
        result_buttons_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), padx=10, pady=(0, 10))
        result_buttons_frame.columnconfigure(0, weight=1)
        result_buttons_frame.columnconfigure(1, weight=1)
        
        self.save_result_button = ttk.Button(
            result_buttons_frame,
            text="💾 Save Result",
            state="disabled"
        )
        self.save_result_button.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        self.use_result_button = ttk.Button(
            result_buttons_frame,
            text="🔄 Use as Input",
            state="disabled"
        )
        self.use_result_button.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 0))
    
    def set_main_action(self, text, command):
        """Set the main action button"""
        self.main_action_button.config(text=text, command=command)
    
    def set_image_selector_command(self, command):
        """Set the image selector browse command"""
        self.browse_button.config(command=command)
    
    def set_result_button_commands(self, save_command, use_command):
        """Set result button commands"""
        self.save_result_button.config(command=save_command)
        self.use_result_button.config(command=use_command)
    
    def update_input_image(self, image_path):
        """Update the input image display"""
        try:
            self.selected_image_path = image_path
            
            # Update path label
            filename = os.path.basename(image_path)
            self.image_path_label.config(text=filename, foreground="black")
            
            # Load and display image
            image = Image.open(image_path)
            
            # Calculate size to fit display area while maintaining aspect ratio
            display_width = 800  # Max width for display
            display_height = 600  # Max height for display
            
            image.thumbnail((display_width, display_height), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(image)
            
            # Update input display
            self.input_image_label.config(image=photo, text="")
            self.input_image_label.image = photo  # Keep a reference
            
            # Update small preview
            preview_image = image.copy()
            preview_image.thumbnail((80, 80), Image.Resampling.LANCZOS)
            preview_photo = ImageTk.PhotoImage(preview_image)
            self.preview_label.config(image=preview_photo, text="")
            self.preview_label.image = preview_photo
            
            # Switch to input tab
            self.image_notebook.select(self.input_frame)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to load input image: {e}")
            show_error("Error", f"Failed to load image: {str(e)}")
            return False
    
    def update_result_image(self, image_or_url):
        """Update the result image display"""
        try:
            # Handle both PIL Image objects and URLs
            if isinstance(image_or_url, str):
                # It's a URL, download it
                import requests
                import tempfile
                
                response = requests.get(image_or_url)
                response.raise_for_status()
                
                with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
                    tmp_file.write(response.content)
                    temp_path = tmp_file.name
                
                image = Image.open(temp_path)
                os.unlink(temp_path)  # Clean up temp file
            else:
                # It's already a PIL Image
                image = image_or_url
            
            self.result_image = image
            
            # Calculate size to fit display area while maintaining aspect ratio
            display_width = 800  # Max width for display
            display_height = 600  # Max height for display
            
            display_image = image.copy()
            display_image.thumbnail((display_width, display_height), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(display_image)
            
            # Update result display
            self.result_image_label.config(image=photo, text="")
            self.result_image_label.image = photo  # Keep a reference
            
            # Enable result buttons
            self.save_result_button.config(state="normal")
            self.use_result_button.config(state="normal")
            
            # Switch to result tab
            self.image_notebook.select(self.result_frame)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to load result image: {e}")
            show_error("Error", f"Failed to load result image: {str(e)}")
            return False
    
    def clear_all(self):
        """Clear all inputs and results - to be overridden by subclasses"""
        pass
    
    def load_sample(self):
        """Load sample data - to be overridden by subclasses"""
        pass
    
    def set_parent_tab(self, parent_tab):
        """Set reference to parent tab for event handling"""
        self.parent_tab = parent_tab
    
    def on_drop(self, event):
        """Handle drag and drop"""
        if self.parent_tab and hasattr(self.parent_tab, 'on_drop'):
            self.parent_tab.on_drop(event)
        else:
            logger.warning("No parent tab set for drag and drop handling")
