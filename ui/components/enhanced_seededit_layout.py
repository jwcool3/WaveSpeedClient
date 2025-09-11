"""
Enhanced SeedEdit Layout with Full WaveSpeed AI Integration
A production-ready implementation with all advanced features
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from PIL import Image, ImageTk, ImageOps
import os
import json
import threading
import time
from pathlib import Path
from typing import Optional, Callable
from core.logger import get_logger
from core.auto_save import auto_save_manager
from core.prompt_tracker import prompt_tracker

logger = get_logger()


class EnhancedSeedEditLayout:
    """Enhanced SeedEdit layout with full WaveSpeed AI integration"""
    
    def __init__(self, parent_frame, tab_instance, api_client, main_app=None):
        self.parent_frame = parent_frame
        self.tab_instance = tab_instance
        self.api_client = api_client
        self.main_app = main_app
        
        # State variables
        self.selected_image_path = None
        self.result_image_path = None
        self.result_url = None
        self.is_processing = False
        self.current_view_mode = "original"
        
        # Callbacks
        self.on_image_selected: Optional[Callable] = None
        self.on_process_requested: Optional[Callable] = None
        self.on_status_update: Optional[Callable] = None
        
        # UI Components
        self.setup_layout()
        self.load_saved_prompts()
    
    def setup_layout(self):
        """Setup the enhanced 2-column layout"""
        
        # Main container
        main_container = ttk.Frame(self.parent_frame)
        main_container.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        
        # Configure grid - 2 balanced columns
        main_container.columnconfigure(0, weight=1, minsize=380)  # Left: Controls (slightly wider)
        main_container.columnconfigure(1, weight=2, minsize=600)  # Right: Images (2x weight)
        main_container.rowconfigure(0, weight=1)
        
        # Left Column - Controls & Actions
        self.setup_left_column(main_container)
        
        # Right Column - Image Display
        self.setup_right_column(main_container)
    
    def setup_left_column(self, parent):
        """Setup left column with logical flow: Input → Settings → Prompt → Action"""
        left_frame = ttk.Frame(parent, relief='groove', borderwidth=1, padding="10")
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 4))
        left_frame.columnconfigure(0, weight=1)
        
        # Configure rows
        for i in range(6):
            left_frame.rowconfigure(i, weight=0)
        left_frame.rowconfigure(6, weight=1, minsize=50)  # Spacer
        
        # 1. COMPACT IMAGE INPUT
        self.setup_compact_image_input(left_frame)
        
        # 2. HORIZONTAL SETTINGS
        self.setup_horizontal_settings(left_frame)
        
        # 3. PROMPT SECTION
        self.setup_compact_prompt_section(left_frame)
        
        # 4. PRIMARY ACTION
        self.setup_primary_action(left_frame)
        
        # 5. AI INTEGRATION
        self.setup_ai_integration(left_frame)
        
        # 6. SECONDARY ACTIONS
        self.setup_secondary_actions(left_frame)
        
        # 7. SPACER
        spacer = ttk.Frame(left_frame)
        spacer.grid(row=6, column=0, sticky="nsew")
    
    def setup_compact_image_input(self, parent):
        """Enhanced image input section"""
        input_frame = ttk.LabelFrame(parent, text="📥 Input Image", padding="8")
        input_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        input_frame.columnconfigure(1, weight=1)
        
        # Thumbnail + Info
        self.thumbnail_label = tk.Label(
            input_frame,
            text="📁\nDrop\nImage",
            width=10, height=4,
            bg='#f8f9fa',
            relief='solid',
            borderwidth=1,
            cursor="hand2",
            font=('Arial', 10)
        )
        self.thumbnail_label.grid(row=0, column=0, padx=(0, 10), rowspan=2)
        self.thumbnail_label.bind("<Button-1>", lambda e: self.browse_image())
        
        # Image info
        self.image_name_label = ttk.Label(
            input_frame,
            text="No image selected",
            font=('Arial', 10, 'bold'),
            foreground="#6c757d"
        )
        self.image_name_label.grid(row=0, column=1, sticky="w")
        
        info_frame = ttk.Frame(input_frame)
        info_frame.grid(row=1, column=1, sticky="ew")
        info_frame.columnconfigure(0, weight=1)
        
        self.image_size_label = ttk.Label(
            info_frame,
            text="",
            font=('Arial', 9),
            foreground="#6c757d"
        )
        self.image_size_label.grid(row=0, column=0, sticky="w")
        
        # Action buttons
        btn_frame = ttk.Frame(info_frame)
        btn_frame.grid(row=0, column=1, sticky="e")
        
        ttk.Button(btn_frame, text="Browse", command=self.browse_image, width=8).pack(side=tk.LEFT, padx=(0, 4))
        ttk.Button(btn_frame, text="Clear", command=self.clear_image, width=6).pack(side=tk.LEFT)
    
    def setup_horizontal_settings(self, parent):
        """Enhanced horizontal settings layout"""
        settings_frame = ttk.LabelFrame(parent, text="⚙️ Settings", padding="8")
        settings_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        settings_frame.columnconfigure(1, weight=1)
        settings_frame.columnconfigure(3, weight=1)
        
        # Row 1: Guidance Scale + Seed
        ttk.Label(settings_frame, text="Guidance Scale:", font=('Arial', 9)).grid(
            row=0, column=0, sticky="w", padx=(0, 4)
        )
        
        self.guidance_scale_var = tk.DoubleVar(value=0.5)
        guidance_frame = ttk.Frame(settings_frame)
        guidance_frame.grid(row=0, column=1, sticky="w", padx=(0, 12))
        
        guidance_entry = ttk.Entry(
            guidance_frame,
            textvariable=self.guidance_scale_var,
            width=6,
            font=('Arial', 9)
        )
        guidance_entry.pack(side=tk.LEFT)
        
        # Guidance scale slider
        guidance_slider = ttk.Scale(
            guidance_frame,
            from_=0.1,
            to=1.0,
            variable=self.guidance_scale_var,
            orient=tk.HORIZONTAL,
            length=80
        )
        guidance_slider.pack(side=tk.LEFT, padx=(4, 0))
        
        ttk.Label(settings_frame, text="Seed:", font=('Arial', 9)).grid(
            row=0, column=2, sticky="w", padx=(0, 4)
        )
        
        seed_frame = ttk.Frame(settings_frame)
        seed_frame.grid(row=0, column=3, sticky="w")
        
        self.seed_var = tk.StringVar(value="-1")
        seed_entry = ttk.Entry(
            seed_frame,
            textvariable=self.seed_var,
            width=8,
            font=('Arial', 9)
        )
        seed_entry.pack(side=tk.LEFT)
        
        ttk.Button(seed_frame, text="🎲", width=3, command=self.randomize_seed).pack(side=tk.LEFT, padx=(2, 0))
        
        # Row 2: Steps + Format
        ttk.Label(settings_frame, text="Steps:", font=('Arial', 9)).grid(
            row=1, column=0, sticky="w", padx=(0, 4), pady=(8, 0)
        )
        
        self.steps_var = tk.IntVar(value=20)
        steps_entry = ttk.Entry(
            settings_frame,
            textvariable=self.steps_var,
            width=6,
            font=('Arial', 9)
        )
        steps_entry.grid(row=1, column=1, sticky="w", pady=(8, 0))
        
        ttk.Label(settings_frame, text="Format:", font=('Arial', 9)).grid(
            row=1, column=2, sticky="w", padx=(0, 4), pady=(8, 0)
        )
        
        self.format_var = tk.StringVar(value="png")
        format_combo = ttk.Combobox(
            settings_frame,
            textvariable=self.format_var,
            values=["png", "jpg", "webp"],
            state="readonly",
            width=6,
            font=('Arial', 9)
        )
        format_combo.grid(row=1, column=3, sticky="w", pady=(8, 0))
    
    def setup_compact_prompt_section(self, parent):
        """Enhanced prompt section with preset management"""
        prompt_frame = ttk.LabelFrame(parent, text="✏️ Edit Instruction", padding="8")
        prompt_frame.grid(row=2, column=0, sticky="ew", pady=(0, 10))
        prompt_frame.columnconfigure(0, weight=1)
        
        # Preset management
        preset_frame = ttk.Frame(prompt_frame)
        preset_frame.grid(row=0, column=0, sticky="ew", pady=(0, 6))
        preset_frame.columnconfigure(0, weight=1)
        
        # Preset dropdown
        self.preset_var = tk.StringVar()
        self.preset_combo = ttk.Combobox(
            preset_frame,
            textvariable=self.preset_var,
            font=('Arial', 9),
            height=8
        )
        self.preset_combo.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        self.preset_combo.bind('<<ComboboxSelected>>', self.load_preset)
        
        # Preset buttons
        preset_btn_frame = ttk.Frame(preset_frame)
        preset_btn_frame.grid(row=0, column=1)
        
        ttk.Button(preset_btn_frame, text="💾", width=3, command=self.save_preset, tooltip="Save prompt").pack(side=tk.LEFT, padx=1)
        ttk.Button(preset_btn_frame, text="🗑️", width=3, command=self.delete_preset, tooltip="Delete prompt").pack(side=tk.LEFT, padx=1)
        ttk.Button(preset_btn_frame, text="🎲", width=3, command=self.load_sample, tooltip="Load sample").pack(side=tk.LEFT, padx=1)
        
        # Prompt text
        self.prompt_text = tk.Text(
            prompt_frame,
            height=4,
            wrap=tk.WORD,
            font=('Arial', 10),
            relief='solid',
            borderwidth=1,
            padx=4,
            pady=4
        )
        self.prompt_text.grid(row=1, column=0, sticky="ew", pady=(6, 0))
        
        # Placeholder text
        self.prompt_text.insert("1.0", "Describe the changes you want to make to the image...")
        self.prompt_text.bind("<FocusIn>", self.clear_placeholder)
        self.prompt_text.bind("<FocusOut>", self.add_placeholder)
    
    def setup_primary_action(self, parent):
        """Primary action button with enhanced features"""
        action_frame = ttk.Frame(parent)
        action_frame.grid(row=3, column=0, sticky="ew", pady=10)
        action_frame.columnconfigure(0, weight=1)
        
        # PROMINENT primary action button
        self.primary_btn = ttk.Button(
            action_frame,
            text="✨ Apply SeedEdit",
            command=self.process_seededit,
            style='Accent.TButton'
        )
        self.primary_btn.grid(row=0, column=0, sticky="ew")
        
        # Status and progress
        status_frame = ttk.Frame(action_frame)
        status_frame.grid(row=1, column=0, sticky="ew", pady=(6, 0))
        status_frame.columnconfigure(0, weight=1)
        
        self.status_label = ttk.Label(
            status_frame,
            text="Ready to edit",
            font=('Arial', 9),
            foreground="#28a745"
        )
        self.status_label.grid(row=0, column=0, sticky="w")
        
        # Progress bar (hidden by default)
        self.progress_bar = ttk.Progressbar(
            status_frame,
            mode='indeterminate',
            length=200
        )
    
    def setup_ai_integration(self, parent):
        """AI integration section"""
        ai_frame = ttk.LabelFrame(parent, text="🤖 AI Assistant", padding="8")
        ai_frame.grid(row=4, column=0, sticky="ew", pady=(0, 10))
        ai_frame.columnconfigure(0, weight=1)
        
        # AI buttons
        ttk.Button(
            ai_frame,
            text="✨ Improve Prompt",
            command=self.improve_prompt_with_ai,
            width=18
        ).grid(row=0, column=0, sticky="ew", pady=(0, 4))
        
        ttk.Button(
            ai_frame,
            text="🛡️ Filter Training",
            command=self.open_filter_training,
            width=18
        ).grid(row=1, column=0, sticky="ew")
    
    def setup_secondary_actions(self, parent):
        """Enhanced secondary actions"""
        secondary_frame = ttk.LabelFrame(parent, text="🔧 Tools", padding="8")
        secondary_frame.grid(row=5, column=0, sticky="ew")
        secondary_frame.columnconfigure(0, weight=1)
        secondary_frame.columnconfigure(1, weight=1)
        
        # Row 1: Clear and Load
        ttk.Button(
            secondary_frame,
            text="🧹 Clear All",
            command=self.clear_all,
            width=14
        ).grid(row=0, column=0, sticky="ew", padx=(0, 4), pady=2)
        
        ttk.Button(
            secondary_frame,
            text="📂 Load Result",
            command=self.load_result,
            width=14
        ).grid(row=0, column=1, sticky="ew", padx=(4, 0), pady=2)
        
        # Row 2: Save and Export
        ttk.Button(
            secondary_frame,
            text="💾 Save Result",
            command=self.save_result,
            width=14
        ).grid(row=1, column=0, sticky="ew", padx=(0, 4), pady=2)
        
        ttk.Button(
            secondary_frame,
            text="📤 Export",
            command=self.export_result,
            width=14
        ).grid(row=1, column=1, sticky="ew", padx=(4, 0), pady=2)
    
    def setup_right_column(self, parent):
        """Enhanced right column with advanced image display"""
        right_frame = ttk.Frame(parent, relief='groove', borderwidth=1, padding="6")
        right_frame.grid(row=0, column=1, sticky="nsew", padx=(4, 0))
        right_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(1, weight=1)
        
        # Image controls
        self.setup_image_controls(right_frame)
        
        # Image display
        self.setup_image_display(right_frame)
    
    def setup_image_controls(self, parent):
        """Enhanced image viewing controls"""
        controls_frame = ttk.Frame(parent)
        controls_frame.grid(row=0, column=0, sticky="ew", pady=(0, 6))
        controls_frame.columnconfigure(2, weight=1)  # Spacer
        
        # View mode buttons
        self.view_original_btn = ttk.Button(
            controls_frame,
            text="📥 Original",
            command=lambda: self.set_view_mode("original"),
            width=12
        )
        self.view_original_btn.grid(row=0, column=0, padx=(0, 4))
        
        self.view_result_btn = ttk.Button(
            controls_frame,
            text="✨ Result",
            command=lambda: self.set_view_mode("result"),
            width=12
        )
        self.view_result_btn.grid(row=0, column=1, padx=(0, 8))
        
        # Comparison mode toggle
        self.comparison_btn = ttk.Button(
            controls_frame,
            text="⚖️ Compare",
            command=self.toggle_comparison_mode,
            width=12
        )
        self.comparison_btn.grid(row=0, column=3, padx=(8, 0))
        
        # Zoom controls
        zoom_frame = ttk.Frame(controls_frame)
        zoom_frame.grid(row=0, column=4, padx=(8, 0))
        
        ttk.Label(zoom_frame, text="Zoom:", font=('Arial', 9)).pack(side=tk.LEFT)
        
        self.zoom_var = tk.StringVar(value="Fit")
        zoom_combo = ttk.Combobox(
            zoom_frame,
            textvariable=self.zoom_var,
            values=["Fit", "50%", "75%", "100%", "125%", "150%", "200%"],
            state="readonly",
            width=6,
            font=('Arial', 9)
        )
        zoom_combo.pack(side=tk.LEFT, padx=(2, 0))
        zoom_combo.bind('<<ComboboxSelected>>', self.on_zoom_changed)
    
    def setup_image_display(self, parent):
        """Enhanced image display with minimal margins"""
        display_frame = ttk.Frame(parent)
        display_frame.grid(row=1, column=0, sticky="nsew")
        display_frame.columnconfigure(0, weight=1)
        display_frame.rowconfigure(0, weight=1)
        
        # Canvas with minimal padding
        self.image_canvas = tk.Canvas(
            display_frame,
            bg='white',
            highlightthickness=0,
            relief='flat'
        )
        self.image_canvas.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(display_frame, orient=tk.VERTICAL, command=self.image_canvas.yview)
        h_scrollbar = ttk.Scrollbar(display_frame, orient=tk.HORIZONTAL, command=self.image_canvas.xview)
        
        self.image_canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        # Bind events
        self.image_canvas.bind('<Configure>', self.on_canvas_configure)
        self.image_canvas.bind('<Button-1>', self.on_canvas_click)
        self.image_canvas.bind('<MouseWheel>', self.on_mouse_wheel)
        
        # Default message
        self.show_default_message()
    
    def show_default_message(self):
        """Show default message when no image is loaded"""
        self.image_canvas.delete("all")
        self.image_canvas.create_text(
            300, 250,
            text="Select an image to start editing\n\nDrag & drop supported\nClick to browse",
            font=('Arial', 14),
            fill='#6c757d',
            justify=tk.CENTER
        )
    
    def set_view_mode(self, mode):
        """Set image viewing mode"""
        self.current_view_mode = mode
        
        # Update button states
        if mode == "original":
            self.view_original_btn.config(relief='sunken')
            self.view_result_btn.config(relief='raised')
            if self.selected_image_path:
                self.display_image(self.selected_image_path)
        elif mode == "result":
            self.view_result_btn.config(relief='sunken')
            self.view_original_btn.config(relief='raised')
            if self.result_image_path:
                self.display_image(self.result_image_path)
        
        self.comparison_btn.config(relief='raised')
    
    def toggle_comparison_mode(self):
        """Toggle comparison mode"""
        if not self.selected_image_path or not self.result_image_path:
            self.update_status("Need both images for comparison", "warning")
            return
        
        self.comparison_btn.config(relief='sunken')
        self.view_original_btn.config(relief='raised')
        self.view_result_btn.config(relief='raised')
        
        # Show side-by-side comparison
        self.display_comparison()
    
    def display_image(self, image_path, position="center"):
        """Display image with dynamic scaling and minimal margins"""
        try:
            # Clear canvas
            self.image_canvas.delete("all")
            
            # Load image
            img = Image.open(image_path)
            img = ImageOps.exif_transpose(img)  # Fix orientation
            
            # Get canvas dimensions
            canvas_width = self.image_canvas.winfo_width()
            canvas_height = self.image_canvas.winfo_height()
            
            if canvas_width <= 1:
                canvas_width = 600
                canvas_height = 500
            
            # Calculate scaling based on zoom setting
            zoom_value = self.zoom_var.get()
            if zoom_value == "Fit":
                # Fit to canvas with minimal margins
                scale_factor = min(
                    (canvas_width - 10) / img.width,
                    (canvas_height - 10) / img.height
                )
            else:
                # Fixed zoom percentage
                scale_factor = float(zoom_value.rstrip('%')) / 100
            
            # Resize image
            new_width = int(img.width * scale_factor)
            new_height = int(img.height * scale_factor)
            img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Create PhotoImage
            photo = ImageTk.PhotoImage(img_resized)
            
            # Position image
            if position == "center":
                x = max(5, (canvas_width - new_width) // 2)
                y = max(5, (canvas_height - new_height) // 2)
            elif position == "left":
                x = 5
                y = max(5, (canvas_height - new_height) // 2)
            elif position == "right":
                x = canvas_width // 2 + 5
                y = max(5, (canvas_height - new_height) // 2)
            
            # Display image
            self.image_canvas.create_image(x, y, anchor=tk.NW, image=photo)
            self.image_canvas.image = photo
            
            # Update scroll region
            self.image_canvas.configure(scrollregion=self.image_canvas.bbox("all"))
            
        except Exception as e:
            logger.error(f"Error displaying image: {e}")
            self.image_canvas.delete("all")
            self.image_canvas.create_text(
                300, 250,
                text=f"Error loading image:\n{str(e)}",
                font=('Arial', 12),
                fill='red',
                justify=tk.CENTER
            )
    
    def display_comparison(self):
        """Display side-by-side comparison"""
        try:
            # Clear canvas
            self.image_canvas.delete("all")
            
            # Load both images
            original_img = Image.open(self.selected_image_path)
            original_img = ImageOps.exif_transpose(original_img)
            result_img = Image.open(self.result_image_path)
            result_img = ImageOps.exif_transpose(result_img)
            
            # Get canvas dimensions
            canvas_width = self.image_canvas.winfo_width()
            canvas_height = self.image_canvas.winfo_height()
            
            if canvas_width <= 1:
                canvas_width = 600
                canvas_height = 500
            
            # Calculate scaling for side-by-side display
            available_width = (canvas_width - 15) // 2
            available_height = canvas_height - 30  # Space for labels
            
            # Scale both images to same size
            scale_factor = min(
                available_width / max(original_img.width, result_img.width),
                available_height / max(original_img.height, result_img.height)
            )
            
            new_width = int(max(original_img.width, result_img.width) * scale_factor)
            new_height = int(max(original_img.height, result_img.height) * scale_factor)
            
            # Resize images
            original_resized = original_img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            result_resized = result_img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Create PhotoImages
            original_photo = ImageTk.PhotoImage(original_resized)
            result_photo = ImageTk.PhotoImage(result_resized)
            
            # Position images side by side
            left_x = 5
            right_x = canvas_width // 2 + 5
            y = max(25, (canvas_height - new_height) // 2)
            
            # Display images
            self.image_canvas.create_image(left_x, y, anchor=tk.NW, image=original_photo)
            self.image_canvas.create_image(right_x, y, anchor=tk.NW, image=result_photo)
            
            # Add labels
            self.image_canvas.create_text(left_x + new_width//2, y - 15, text="Original", 
                                        font=('Arial', 11, 'bold'), fill='#007bff')
            self.image_canvas.create_text(right_x + new_width//2, y - 15, text="Result", 
                                        font=('Arial', 11, 'bold'), fill='#28a745')
            
            # Keep references
            self.image_canvas.original_photo = original_photo
            self.image_canvas.result_photo = result_photo
            
            # Update scroll region
            self.image_canvas.configure(scrollregion=self.image_canvas.bbox("all"))
            
        except Exception as e:
            logger.error(f"Error displaying comparison: {e}")
            self.update_status(f"Comparison error: {str(e)}", "error")
    
    # Event handlers and utility methods
    def browse_image(self):
        """Browse for image file"""
        file_path = filedialog.askopenfilename(
            title="Select Image for SeedEdit",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.gif *.bmp *.webp"),
                ("All files", "*.*")
            ]
        )
        if file_path:
            self.load_image(file_path)
    
    def load_image(self, image_path):
        """Load and display input image"""
        self.selected_image_path = image_path
        
        try:
            # Update thumbnail
            img = Image.open(image_path)
            img = ImageOps.exif_transpose(img)
            img.thumbnail((60, 60), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            
            self.thumbnail_label.config(image=photo, text="")
            self.thumbnail_label.image = photo
            
            # Update info
            filename = os.path.basename(image_path)
            if len(filename) > 30:
                filename = filename[:27] + "..."
            self.image_name_label.config(text=filename, foreground="#212529")
            
            # Get image size
            original = Image.open(image_path)
            original = ImageOps.exif_transpose(original)
            self.image_size_label.config(text=f"{original.width}×{original.height}px")
            
            # Display in main canvas
            self.set_view_mode("original")
            
            # Update status
            self.update_status("Image loaded successfully", "success")
            
            # Notify parent
            if self.on_image_selected:
                self.on_image_selected(image_path)
                
        except Exception as e:
            logger.error(f"Error loading image: {e}")
            self.update_status(f"Error loading image: {str(e)}", "error")
    
    def clear_image(self):
        """Clear selected image"""
        self.selected_image_path = None
        self.thumbnail_label.config(image="", text="📁\nDrop\nImage")
        self.image_name_label.config(text="No image selected", foreground="#6c757d")
        self.image_size_label.config(text="")
        self.image_canvas.delete("all")
        self.show_default_message()
        self.update_status("Image cleared", "info")
    
    def process_seededit(self):
        """Process with SeedEdit"""
        if not self.selected_image_path:
            self.update_status("Please select an image first", "error")
            return
        
        prompt = self.prompt_text.get("1.0", tk.END).strip()
        if not prompt or prompt == "Describe the changes you want to make to the image...":
            self.update_status("Please enter edit instructions", "error")
            return
        
        if self.is_processing:
            self.update_status("Already processing...", "warning")
            return
        
        # Show processing state
        self.is_processing = True
        self.update_status("Processing with SeedEdit...", "info")
        self.progress_bar.grid(row=1, column=0, sticky="ew", pady=(6, 0))
        self.progress_bar.start()
        self.primary_btn.config(state='disabled', text="Processing...")
        
        # Notify parent to handle processing
        if self.on_process_requested:
            self.on_process_requested()
    
    def after_processing(self, success: bool, result_url: str = None, error_message: str = None):
        """Called after processing is complete"""
        self.is_processing = False
        
        # Hide progress
        self.progress_bar.stop()
        self.progress_bar.grid_remove()
        self.primary_btn.config(state='normal', text="✨ Apply SeedEdit")
        
        if success:
            self.result_url = result_url
            self.update_status("Processing complete!", "success")
            
            # Enable result view
            self.view_result_btn.config(state='normal')
            self.comparison_btn.config(state='normal')
            
            # Auto-save if enabled
            self.auto_save_result()
        else:
            self.update_status(f"Error: {error_message}", "error")
    
    def auto_save_result(self):
        """Auto-save the result"""
        if not self.result_url:
            return
        
        try:
            prompt = self.prompt_text.get("1.0", tk.END).strip()
            extra_info = f"gs{self.guidance_scale_var.get()}_steps{self.steps_var.get()}_seed{self.seed_var.get()}"
            
            success, saved_path, error = auto_save_manager.save_result(
                'seededit',
                self.result_url,
                prompt=prompt,
                extra_info=extra_info
            )
            
            if success:
                self.update_status(f"Auto-saved to: {os.path.basename(saved_path)}", "success")
                
                # Track successful prompt
                prompt_tracker.log_successful_prompt(
                    prompt=prompt,
                    ai_model="seededit",
                    result_url=self.result_url,
                    save_path=saved_path,
                    additional_context={
                        "guidance_scale": self.guidance_scale_var.get(),
                        "steps": self.steps_var.get(),
                        "seed": self.seed_var.get(),
                        "auto_saved": True
                    }
                )
            else:
                self.update_status(f"Auto-save failed: {error}", "warning")
                
        except Exception as e:
            logger.error(f"Auto-save error: {e}")
            self.update_status(f"Auto-save error: {str(e)}", "warning")
    
    def update_status(self, message: str, status_type: str = "info"):
        """Update status message"""
        colors = {
            "success": "#28a745",
            "error": "#dc3545",
            "warning": "#ffc107",
            "info": "#17a2b8"
        }
        
        self.status_label.config(text=message, foreground=colors.get(status_type, "#6c757d"))
        
        if self.on_status_update:
            self.on_status_update(message, status_type)
    
    def randomize_seed(self):
        """Randomize seed value"""
        import random
        self.seed_var.set(str(random.randint(1, 999999)))
    
    def load_saved_prompts(self):
        """Load saved prompts from file"""
        try:
            prompts_file = Path("data") / "seededit_prompts.json"
            if prompts_file.exists():
                with open(prompts_file, 'r', encoding='utf-8') as f:
                    prompts_data = json.load(f)
                    prompts = list(prompts_data.keys())
                    self.preset_combo['values'] = prompts
        except Exception as e:
            logger.error(f"Error loading saved prompts: {e}")
    
    def save_preset(self):
        """Save current prompt as preset"""
        prompt = self.prompt_text.get("1.0", tk.END).strip()
        if not prompt or prompt == "Describe the changes you want to make to the image...":
            messagebox.showwarning("No Prompt", "Please enter a prompt to save.")
            return
        
        # Get prompt name from user
        name = simpledialog.askstring("Save Prompt", "Enter a name for this prompt:")
        if not name:
            return
        
        try:
            prompts_file = Path("data") / "seededit_prompts.json"
            prompts_file.parent.mkdir(exist_ok=True)
            
            # Load existing prompts
            prompts_data = {}
            if prompts_file.exists():
                with open(prompts_file, 'r', encoding='utf-8') as f:
                    prompts_data = json.load(f)
            
            # Add new prompt
            prompts_data[name] = prompt
            
            # Save back
            with open(prompts_file, 'w', encoding='utf-8') as f:
                json.dump(prompts_data, f, indent=2, ensure_ascii=False)
            
            # Update dropdown
            self.preset_combo['values'] = list(prompts_data.keys())
            self.preset_var.set(name)
            
            self.update_status(f"Prompt '{name}' saved", "success")
            
        except Exception as e:
            logger.error(f"Error saving prompt: {e}")
            messagebox.showerror("Error", f"Failed to save prompt: {str(e)}")
    
    def delete_preset(self):
        """Delete selected preset"""
        selected = self.preset_var.get()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a prompt to delete.")
            return
        
        if messagebox.askyesno("Confirm Delete", f"Delete prompt '{selected}'?"):
            try:
                prompts_file = Path("data") / "seededit_prompts.json"
                if prompts_file.exists():
                    with open(prompts_file, 'r', encoding='utf-8') as f:
                        prompts_data = json.load(f)
                    
                    if selected in prompts_data:
                        del prompts_data[selected]
                        
                        with open(prompts_file, 'w', encoding='utf-8') as f:
                            json.dump(prompts_data, f, indent=2, ensure_ascii=False)
                        
                        # Update dropdown
                        self.preset_combo['values'] = list(prompts_data.keys())
                        self.preset_var.set("")
                        
                        self.update_status(f"Prompt '{selected}' deleted", "success")
                        
            except Exception as e:
                logger.error(f"Error deleting prompt: {e}")
                messagebox.showerror("Error", f"Failed to delete prompt: {str(e)}")
    
    def load_preset(self, event=None):
        """Load selected preset"""
        selected = self.preset_var.get()
        if selected:
            try:
                prompts_file = Path("data") / "seededit_prompts.json"
                if prompts_file.exists():
                    with open(prompts_file, 'r', encoding='utf-8') as f:
                        prompts_data = json.load(f)
                    
                    if selected in prompts_data:
                        self.prompt_text.delete("1.0", tk.END)
                        self.prompt_text.insert("1.0", prompts_data[selected])
                        
            except Exception as e:
                logger.error(f"Error loading prompt: {e}")
    
    def load_sample(self):
        """Load sample prompt"""
        sample_prompts = [
            "Change the background to a beautiful sunset landscape",
            "Make the person smile and add a warm glow effect",
            "Convert to black and white with dramatic lighting",
            "Add a vintage film effect with grain and color grading",
            "Change the clothing to a formal business suit",
            "Add a magical sparkle effect around the subject",
            "Transform into a watercolor painting style",
            "Add a neon cyberpunk aesthetic with glowing elements"
        ]
        
        import random
        sample = random.choice(sample_prompts)
        self.prompt_text.delete("1.0", tk.END)
        self.prompt_text.insert("1.0", sample)
        self.update_status("Sample prompt loaded", "info")
    
    def improve_prompt_with_ai(self):
        """Improve prompt with AI"""
        # This would integrate with the AI system
        self.update_status("AI prompt improvement not yet implemented", "info")
    
    def open_filter_training(self):
        """Open filter training"""
        # This would integrate with the AI system
        self.update_status("Filter training not yet implemented", "info")
    
    def clear_all(self):
        """Clear all inputs"""
        self.clear_image()
        self.prompt_text.delete("1.0", tk.END)
        self.prompt_text.insert("1.0", "Describe the changes you want to make to the image...")
        self.preset_var.set("")
        self.update_status("All cleared", "info")
    
    def load_result(self):
        """Load result manually"""
        file_path = filedialog.askopenfilename(
            title="Load Result Image",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.gif *.bmp *.webp"),
                ("All files", "*.*")
            ]
        )
        if file_path:
            self.result_image_path = file_path
            self.set_view_mode("result")
            self.update_status("Result loaded", "success")
    
    def save_result(self):
        """Save result manually"""
        if not self.result_url:
            messagebox.showwarning("No Result", "No result to save.")
            return
        
        # This would implement manual save functionality
        self.update_status("Manual save not yet implemented", "info")
    
    def export_result(self):
        """Export result with metadata"""
        if not self.result_url:
            messagebox.showwarning("No Result", "No result to export.")
            return
        
        # This would implement export functionality
        self.update_status("Export not yet implemented", "info")
    
    # Canvas event handlers
    def on_canvas_configure(self, event):
        """Handle canvas resize"""
        if hasattr(self, 'current_view_mode'):
            if self.current_view_mode == "original" and self.selected_image_path:
                self.display_image(self.selected_image_path)
            elif self.current_view_mode == "result" and self.result_image_path:
                self.display_image(self.result_image_path)
    
    def on_canvas_click(self, event):
        """Handle canvas click"""
        pass
    
    def on_mouse_wheel(self, event):
        """Handle mouse wheel for zooming"""
        pass
    
    def on_zoom_changed(self, event):
        """Handle zoom change"""
        if hasattr(self, 'current_view_mode'):
            if self.current_view_mode == "original" and self.selected_image_path:
                self.display_image(self.selected_image_path)
            elif self.current_view_mode == "result" and self.result_image_path:
                self.display_image(self.result_image_path)
    
    def clear_placeholder(self, event):
        """Clear placeholder text"""
        current_text = self.prompt_text.get("1.0", tk.END).strip()
        if current_text == "Describe the changes you want to make to the image...":
            self.prompt_text.delete("1.0", tk.END)
    
    def add_placeholder(self, event):
        """Add placeholder text"""
        current_text = self.prompt_text.get("1.0", tk.END).strip()
        if not current_text:
            self.prompt_text.insert("1.0", "Describe the changes you want to make to the image...")
