"""
Optimized Video Layout Component for WaveSpeed AI Application

This module provides a much more space-efficient layout for video generation tabs,
with a large, prominent video player and compact, well-organized controls.
"""

import tkinter as tk
from tkinter import ttk
import os
from PIL import Image, ImageTk
from utils.utils import load_image_preview, validate_image_file, show_error, parse_drag_drop_data
from ui.components.unified_video_player import UnifiedVideoPlayer
from core.logger import get_logger

logger = get_logger()

# Try to import drag and drop support
try:
    from tkinterdnd2 import DND_FILES
    DND_AVAILABLE = True
except ImportError:
    DND_AVAILABLE = False

class OptimizedVideoLayout:
    """Optimized layout for video generation tabs with better space utilization"""
    
    def __init__(self, parent_frame, title="Video Generation"):
        self.parent_frame = parent_frame
        self.title = title
        self.selected_image_path = None
        self.unified_video_player = None
        
        # Parent frame will be managed by pack, so no grid configuration needed
        
        # Create main layout
        self.setup_optimized_layout()
    
    def setup_optimized_layout(self):
        """Setup the optimized layout with better space utilization"""
        
        # Main container with horizontal layout - use pack to be compatible with BaseTab
        main_container = ttk.Frame(self.parent_frame)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        main_container.columnconfigure(1, weight=3)  # Video gets 3x more space
        main_container.columnconfigure(0, weight=1)  # Controls get 1x space
        main_container.rowconfigure(0, weight=1)
        
        # Left panel - Compact controls (30% of width)
        self.setup_left_panel(main_container)
        
        # Right panel - Large video player (70% of width)
        self.setup_right_panel(main_container)
    
    def setup_left_panel(self, parent):
        """Setup compact left control panel"""
        left_panel = ttk.Frame(parent)
        left_panel.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        left_panel.columnconfigure(0, weight=1)
        
        # Configure rows for proper vertical distribution
        left_panel.rowconfigure(0, weight=0)  # Image selector - fixed size
        left_panel.rowconfigure(1, weight=0)  # Settings - fixed size
        left_panel.rowconfigure(2, weight=1)  # Action buttons - expandable spacer
        left_panel.rowconfigure(3, weight=0)  # Additional content - fixed size
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
        
        # Browse button
        self.browse_button = ttk.Button(
            image_section, 
            text="📁 Browse Image",
            command=self.browse_image
        )
        self.browse_button.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # Selected image info
        self.image_info_frame = ttk.Frame(image_section)
        self.image_info_frame.grid(row=1, column=0, sticky=(tk.W, tk.E))
        self.image_info_frame.columnconfigure(1, weight=1)
        
        # Small thumbnail
        self.thumbnail_label = tk.Label(
            self.image_info_frame,
            text="📁",
            font=('Arial', 20),
            bg='#f0f0f0',
            fg='#666666',
            width=6,
            height=3,
            relief='groove',
            bd=1
        )
        self.thumbnail_label.grid(row=0, column=0, padx=(0, 8), pady=2)
        
        # Image info
        info_frame = ttk.Frame(self.image_info_frame)
        info_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N))
        info_frame.columnconfigure(0, weight=1)
        
        self.image_name_label = ttk.Label(
            info_frame, 
            text="No image selected",
            font=('Arial', 9),
            foreground="gray"
        )
        self.image_name_label.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        self.image_size_label = ttk.Label(
            info_frame,
            text="",
            font=('Arial', 8),
            foreground="gray"
        )
        self.image_size_label.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Setup drag and drop
        self.setup_drag_and_drop()
        
        # Setup drag and drop for browse button area
        self.setup_browse_area_drag_drop()
    
    def setup_compact_settings(self, parent):
        """Setup compact settings panel"""
        # This will be implemented by the specific tab (image-to-video, seeddance, etc.)
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
            text="Generate Video",
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
        """Setup large video player panel"""
        right_panel = ttk.Frame(parent)
        right_panel.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        right_panel.columnconfigure(0, weight=1)
        right_panel.rowconfigure(0, weight=1)
        
        # Video player section
        video_section = ttk.LabelFrame(right_panel, text="🎬 Video Player", padding="10")
        video_section.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        video_section.columnconfigure(0, weight=1)
        video_section.rowconfigure(0, weight=1)
        
        # Unified video player (responsive to window size)
        try:
            # Create unified video player that adapts to container size
            self.unified_video_player = UnifiedVideoPlayer(video_section, style="modern")
            logger.info("Unified video player created successfully")
        except Exception as e:
            logger.error(f"Failed to create unified video player: {e}")
            self.setup_fallback_video_display(video_section)
    
    def setup_fallback_video_display(self, parent):
        """Setup fallback video display"""
        fallback_label = tk.Label(
            parent,
            text="🎬 Enhanced Video Player\n\nInstall tkvideoplayer for embedded video playback\n\nVideos will open in browser",
            font=('Arial', 14),
            fg='#666666',
            bg='#f0f0f0',
            relief='groove',
            bd=2
        )
        fallback_label.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
    
    def setup_drag_and_drop(self):
        """Setup drag and drop functionality"""
        if not DND_AVAILABLE:
            return
        
        try:
            # Enable drag and drop on thumbnail
            self.thumbnail_label.drop_target_register(DND_FILES)
            self.thumbnail_label.dnd_bind('<<Drop>>', self.on_drop)
            
            # Visual feedback
            self.thumbnail_label.dnd_bind('<<DragEnter>>', self.on_drag_enter)
            self.thumbnail_label.dnd_bind('<<DragLeave>>', self.on_drag_leave)
            
        except Exception as e:
            logger.warning(f"Could not setup drag and drop: {e}")
    
    def on_drag_enter(self, event):
        """Handle drag enter"""
        self.thumbnail_label.config(bg='#e6f3ff', relief='solid')
    
    def on_drag_leave(self, event):
        """Handle drag leave"""
        self.thumbnail_label.config(bg='#f0f0f0', relief='groove')
    
    def on_drop(self, event):
        """Handle drag and drop"""
        # Parse the drag & drop data
        success, result = parse_drag_drop_data(event.data)
        
        if not success:
            show_error("Drag & Drop Error", result)
            return
        
        file_path = result
        
        # Validate the image file
        is_valid, error = validate_image_file(file_path)
        if not is_valid:
            show_error("Invalid File", f"{error}\\n\\nDropped file: {file_path}")
            return
        
        # Update UI and process the file
        self.on_image_selected(file_path)
        
        # Reset visual feedback
        self.thumbnail_label.config(bg='#f0f0f0', relief='groove')
    
    def setup_browse_area_drag_drop(self):
        """Setup drag and drop for the browse button area"""
        if DND_AVAILABLE:
            try:
                # Enable drag and drop on the browse button
                self.browse_button.drop_target_register(DND_FILES)
                self.browse_button.dnd_bind('<<Drop>>', self.on_browse_drop)
                self.browse_button.dnd_bind('<<DragEnter>>', self.on_browse_drag_enter)
                self.browse_button.dnd_bind('<<DragLeave>>', self.on_browse_drag_leave)
                
                # Enable drag and drop on the image size label
                self.image_size_label.drop_target_register(DND_FILES)
                self.image_size_label.dnd_bind('<<Drop>>', self.on_browse_drop)
                
                logger.info("Drag and drop enabled for video browse area")
            except Exception as e:
                logger.warning(f"Failed to setup video browse area drag and drop: {e}")
    
    def on_browse_drop(self, event):
        """Handle drag and drop on browse button area"""
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
        
        # Update the image
        self.on_image_selected(file_path)
        
        # Reset visual feedback
        self.reset_browse_drag_feedback()
    
    def on_browse_drag_enter(self, event):
        """Handle drag enter on browse button"""
        self.browse_button.config(style="Accent.TButton")
    
    def on_browse_drag_leave(self, event):
        """Handle drag leave on browse button"""
        self.browse_button.config(style="TButton")
    
    def reset_browse_drag_feedback(self):
        """Reset browse area drag visual feedback"""
        try:
            self.browse_button.config(style="TButton")
        except:
            pass  # Ignore if widgets are destroyed
    
    def browse_image(self):
        """Browse for image file"""
        try:
            from tkinter import filedialog
            
            file_path = filedialog.askopenfilename(
                title="Select Image",
                filetypes=[
                    ("Image files", "*.png *.jpg *.jpeg *.gif *.bmp *.webp"),
                    ("PNG files", "*.png"),
                    ("JPEG files", "*.jpg *.jpeg"),
                    ("All files", "*.*")
                ]
            )
            
            if file_path:
                self.on_image_selected(file_path)
                
        except Exception as e:
            show_error("Browse Error", f"Failed to browse for image: {str(e)}")
    
    def on_image_selected(self, image_path):
        """Handle image selection"""
        self.selected_image_path = image_path
        
        try:
            # Load and display thumbnail
            photo, original, error = load_image_preview(image_path, max_size=(60, 45))
            if error:
                self.thumbnail_label.config(text="❌", bg='#ffe6e6')
                self.image_name_label.config(text="Error loading image")
                self.image_size_label.config(text=error)
                return None
            
            # Update thumbnail
            self.thumbnail_label.config(image=photo, text="", bg='#f0f0f0')
            self.thumbnail_label.image = photo
            
            # Update info
            filename = os.path.basename(image_path)
            if len(filename) > 25:
                filename = filename[:22] + "..."
            self.image_name_label.config(text=filename, foreground="black")
            
            # Get image size
            if original:
                size_text = f"{original.width}×{original.height}"
                self.image_size_label.config(text=size_text)
            
            logger.info(f"Image selected: {image_path}")
            return original
            
        except Exception as e:
            logger.error(f"Error processing selected image: {e}")
            show_error("Image Error", f"Failed to process image: {str(e)}")
            return None
    
    def clear_all(self):
        """Clear all inputs"""
        self.selected_image_path = None
        self.thumbnail_label.config(text="📁", image="", bg='#f0f0f0')
        self.thumbnail_label.image = None
        self.image_name_label.config(text="No image selected", foreground="gray")
        self.image_size_label.config(text="")
    
    def load_sample(self):
        """Load sample data - to be implemented by specific tabs"""
        pass
    
    def get_selected_image(self):
        """Get the currently selected image path"""
        return self.selected_image_path
    
    def get_video_player(self):
        """Get the unified video player instance"""
        return self.unified_video_player
    
    def add_setting_widget(self, widget, row):
        """Add a setting widget to the settings panel"""
        widget.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=2)
    
    def set_main_action(self, text, command):
        """Set the main action button"""
        self.main_action_button.config(text=text, command=command)
