"""
Enhanced Compact Layout for WaveSpeed AI
A drop-in replacement for existing tab layouts with full integration
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk, ImageOps
import os
import json
from pathlib import Path
from typing import Optional, Callable, Dict, Any
from core.logger import get_logger
from core.auto_save import auto_save_manager
from core.prompt_tracker import prompt_tracker

logger = get_logger()


class EnhancedCompactLayout:
    """Enhanced compact layout with full WaveSpeed AI integration"""
    
    def __init__(self, parent_frame, tab_instance, model_type: str, title: str = "Image Processing"):
        self.parent_frame = parent_frame
        self.tab_instance = tab_instance
        self.model_type = model_type
        self.title = title
        
        # State variables
        self.selected_image_path = None
        self.result_image = None
        self.result_url = None
        self.is_processing = False
        
        # Callbacks
        self.on_image_selected: Optional[Callable] = None
        self.on_process_requested: Optional[Callable] = None
        self.on_status_update: Optional[Callable] = None
        
        # UI Components
        self.setup_layout()
        self.load_saved_prompts()
    
    def setup_layout(self):
        """Setup the enhanced compact layout"""
        
        # Main container
        main_container = ttk.Frame(self.parent_frame)
        main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Configure main grid
        main_container.columnconfigure(0, weight=0, minsize=280)  # Left controls
        main_container.columnconfigure(1, weight=1, minsize=500)  # Center image
        main_container.columnconfigure(2, weight=0, minsize=220)  # Right actions
        main_container.rowconfigure(0, weight=1)
        
        # Create panels
        self.setup_left_controls(main_container)
        self.setup_center_image_display(main_container)
        self.setup_right_actions(main_container)
    
    def setup_left_controls(self, parent):
        """Setup enhanced left control panel"""
        left_panel = ttk.Frame(parent, relief='groove', borderwidth=1, padding="8")
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        left_panel.columnconfigure(0, weight=1)
        
        # Configure rows
        for i in range(6):
            left_panel.rowconfigure(i, weight=0)
        left_panel.rowconfigure(6, weight=1, minsize=50)  # Spacer
        
        # 1. Image Selection
        self.setup_image_section(left_panel)
        
        # 2. Model-specific Settings
        self.setup_model_settings(left_panel)
        
        # 3. Prompts Management
        self.setup_prompts_section(left_panel)
        
        # 4. Advanced Options (collapsible)
        self.setup_advanced_options(left_panel)
        
        # 5. AI Integration
        self.setup_ai_integration(left_panel)
        
        # 6. Spacer
        spacer = ttk.Frame(left_panel)
        spacer.grid(row=6, column=0, sticky="nsew")
    
    def setup_image_section(self, parent):
        """Enhanced image selection section"""
        image_frame = ttk.LabelFrame(parent, text="📸 Image Input", padding="8")
        image_frame.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        image_frame.columnconfigure(1, weight=1)
        
        # Thumbnail with drag & drop support
        self.thumbnail_label = tk.Label(
            image_frame, 
            text="📁\nDrop\nImage", 
            width=8, 
            height=4,
            bg='#f8f9fa', 
            relief='solid', 
            borderwidth=1,
            cursor="hand2",
            font=('Arial', 8)
        )
        self.thumbnail_label.grid(row=0, column=0, padx=(0, 8), rowspan=3)
        self.thumbnail_label.bind("<Button-1>", lambda e: self.browse_image())
        
        # Image info
        info_frame = ttk.Frame(image_frame)
        info_frame.grid(row=0, column=1, sticky="nsew")
        info_frame.columnconfigure(0, weight=1)
        
        self.image_name_label = ttk.Label(
            info_frame, 
            text="No image selected", 
            font=('Arial', 9, 'bold'),
            foreground="#6c757d"
        )
        self.image_name_label.grid(row=0, column=0, sticky="w")
        
        self.image_size_label = ttk.Label(
            info_frame, 
            text="", 
            font=('Arial', 8),
            foreground="#6c757d"
        )
        self.image_size_label.grid(row=1, column=0, sticky="w")
        
        # Action buttons
        btn_frame = ttk.Frame(info_frame)
        btn_frame.grid(row=2, column=0, sticky="w", pady=(4, 0))
        
        ttk.Button(btn_frame, text="Browse", command=self.browse_image, width=8).pack(side=tk.LEFT, padx=(0, 4))
        ttk.Button(btn_frame, text="Clear", command=self.clear_image, width=6).pack(side=tk.LEFT)
    
    def setup_model_settings(self, parent):
        """Model-specific settings based on model type"""
        settings_frame = ttk.LabelFrame(parent, text="⚙️ Settings", padding="8")
        settings_frame.grid(row=1, column=0, sticky="ew", pady=(0, 8))
        settings_frame.columnconfigure(1, weight=1)
        
        if self.model_type == "seedream_v4":
            self.setup_seedream_v4_settings(settings_frame)
        elif self.model_type == "seededit":
            self.setup_seededit_settings(settings_frame)
        elif self.model_type == "image_editor":
            self.setup_image_editor_settings(settings_frame)
        else:
            self.setup_generic_settings(settings_frame)
    
    def setup_seedream_v4_settings(self, parent):
        """Seedream V4 specific settings"""
        # Size controls
        size_frame = ttk.Frame(parent)
        size_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 4))
        size_frame.columnconfigure(1, weight=1)
        size_frame.columnconfigure(3, weight=1)
        
        ttk.Label(size_frame, text="Size:", font=('Arial', 9)).grid(row=0, column=0, sticky="w")
        
        # Width
        ttk.Label(size_frame, text="W:", font=('Arial', 8)).grid(row=0, column=1, sticky="w", padx=(10, 2))
        self.width_var = tk.IntVar(value=1024)
        width_entry = ttk.Entry(size_frame, textvariable=self.width_var, width=6, font=('Arial', 8))
        width_entry.grid(row=0, column=2, sticky="w")
        
        # Height
        ttk.Label(size_frame, text="H:", font=('Arial', 8)).grid(row=0, column=3, sticky="w", padx=(10, 2))
        self.height_var = tk.IntVar(value=1024)
        height_entry = ttk.Entry(size_frame, textvariable=self.height_var, width=6, font=('Arial', 8))
        height_entry.grid(row=0, column=4, sticky="w")
        
        # Seed
        seed_frame = ttk.Frame(parent)
        seed_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(4, 0))
        seed_frame.columnconfigure(1, weight=1)
        
        ttk.Label(seed_frame, text="Seed:", font=('Arial', 9)).grid(row=0, column=0, sticky="w")
        self.seed_var = tk.StringVar(value="1")
        seed_entry = ttk.Entry(seed_frame, textvariable=self.seed_var, width=8, font=('Arial', 8))
        seed_entry.grid(row=0, column=1, sticky="w", padx=(10, 0))
        
        ttk.Button(seed_frame, text="🎲", width=3, command=self.randomize_seed).grid(row=0, column=2, padx=(5, 0))
    
    def setup_seededit_settings(self, parent):
        """SeedEdit specific settings"""
        # Guidance Scale
        gs_frame = ttk.Frame(parent)
        gs_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 4))
        gs_frame.columnconfigure(1, weight=1)
        
        ttk.Label(gs_frame, text="Guidance Scale:", font=('Arial', 9)).grid(row=0, column=0, sticky="w")
        self.guidance_scale_var = tk.DoubleVar(value=7.5)
        gs_entry = ttk.Entry(gs_frame, textvariable=self.guidance_scale_var, width=8, font=('Arial', 8))
        gs_entry.grid(row=0, column=1, sticky="w", padx=(10, 0))
        
        # Steps
        steps_frame = ttk.Frame(parent)
        steps_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(4, 0))
        steps_frame.columnconfigure(1, weight=1)
        
        ttk.Label(steps_frame, text="Steps:", font=('Arial', 9)).grid(row=0, column=0, sticky="w")
        self.steps_var = tk.IntVar(value=20)
        steps_entry = ttk.Entry(steps_frame, textvariable=self.steps_var, width=8, font=('Arial', 8))
        steps_entry.grid(row=0, column=1, sticky="w", padx=(10, 0))
    
    def setup_image_editor_settings(self, parent):
        """Image Editor specific settings"""
        # Output format
        format_frame = ttk.Frame(parent)
        format_frame.grid(row=0, column=0, columnspan=2, sticky="ew")
        format_frame.columnconfigure(1, weight=1)
        
        ttk.Label(format_frame, text="Format:", font=('Arial', 9)).grid(row=0, column=0, sticky="w")
        self.format_var = tk.StringVar(value="png")
        format_combo = ttk.Combobox(
            format_frame, 
            textvariable=self.format_var,
            values=["png", "jpg", "webp"],
            state="readonly",
            width=8,
            font=('Arial', 8)
        )
        format_combo.grid(row=0, column=1, sticky="w", padx=(10, 0))
    
    def setup_generic_settings(self, parent):
        """Generic settings for other models"""
        ttk.Label(parent, text="No specific settings", font=('Arial', 8), foreground="gray").grid(row=0, column=0, sticky="w")
    
    def setup_prompts_section(self, parent):
        """Enhanced prompts section"""
        prompts_frame = ttk.LabelFrame(parent, text="✏️ Prompts", padding="8")
        prompts_frame.grid(row=2, column=0, sticky="ew", pady=(0, 8))
        prompts_frame.columnconfigure(0, weight=1)
        
        # Prompts dropdown with actions
        prompts_controls = ttk.Frame(prompts_frame)
        prompts_controls.grid(row=0, column=0, sticky="ew", pady=(0, 6))
        prompts_controls.columnconfigure(0, weight=1)
        
        self.saved_prompts_var = tk.StringVar()
        self.prompts_combo = ttk.Combobox(
            prompts_controls,
            textvariable=self.saved_prompts_var,
            font=('Arial', 9),
            height=8
        )
        self.prompts_combo.grid(row=0, column=0, sticky="ew", padx=(0, 4))
        self.prompts_combo.bind('<<ComboboxSelected>>', self.on_prompt_selected)
        
        # Action buttons
        btn_frame = ttk.Frame(prompts_controls)
        btn_frame.grid(row=0, column=1)
        
        ttk.Button(btn_frame, text="💾", width=3, command=self.save_prompt, tooltip="Save prompt").pack(side=tk.LEFT, padx=1)
        ttk.Button(btn_frame, text="🗑️", width=3, command=self.delete_prompt, tooltip="Delete prompt").pack(side=tk.LEFT, padx=1)
        ttk.Button(btn_frame, text="🎲", width=3, command=self.load_sample, tooltip="Load sample").pack(side=tk.LEFT, padx=1)
        
        # Prompt text area
        self.prompt_text = tk.Text(
            prompts_frame,
            height=4,
            width=1,
            wrap=tk.WORD,
            font=('Arial', 10),
            relief='solid',
            borderwidth=1,
            padx=4,
            pady=4
        )
        self.prompt_text.grid(row=1, column=0, sticky="ew")
        
        # Add placeholder
        self.prompt_text.insert("1.0", "Describe what you want to create or edit...")
        self.prompt_text.bind("<FocusIn>", self.clear_placeholder)
        self.prompt_text.bind("<FocusOut>", self.add_placeholder)
    
    def setup_advanced_options(self, parent):
        """Collapsible advanced options"""
        self.advanced_frame = ttk.LabelFrame(parent, text="🔧 Advanced", padding="8")
        self.advanced_frame.grid(row=3, column=0, sticky="ew", pady=(0, 8))
        self.advanced_frame.columnconfigure(0, weight=1)
        
        # Toggle button
        self.advanced_toggle = ttk.Button(
            self.advanced_frame,
            text="Show Advanced Options",
            command=self.toggle_advanced_options,
            width=20
        )
        self.advanced_toggle.grid(row=0, column=0, sticky="ew")
        
        # Advanced options container (hidden by default)
        self.advanced_container = ttk.Frame(self.advanced_frame)
        # Don't grid it yet - will be shown when toggled
        
        # Advanced options content
        self.setup_advanced_content()
    
    def setup_advanced_content(self):
        """Setup advanced options content"""
        # Auto-save toggle
        auto_save_frame = ttk.Frame(self.advanced_container)
        auto_save_frame.grid(row=0, column=0, sticky="ew", pady=(0, 4))
        
        self.auto_save_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            auto_save_frame,
            text="Auto-save results",
            variable=self.auto_save_var,
            font=('Arial', 8)
        ).grid(row=0, column=0, sticky="w")
        
        # Base64 output toggle
        base64_frame = ttk.Frame(self.advanced_container)
        base64_frame.grid(row=1, column=0, sticky="ew", pady=(0, 4))
        
        self.base64_output_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            base64_frame,
            text="Base64 output",
            variable=self.base64_output_var,
            font=('Arial', 8)
        ).grid(row=0, column=0, sticky="w")
        
        # Sync mode (for Seedream V4)
        if self.model_type == "seedream_v4":
            sync_frame = ttk.Frame(self.advanced_container)
            sync_frame.grid(row=2, column=0, sticky="ew", pady=(0, 4))
            
            self.sync_mode_var = tk.BooleanVar(value=False)
            ttk.Checkbutton(
                sync_frame,
                text="Sync mode",
                variable=self.sync_mode_var,
                font=('Arial', 8)
            ).grid(row=0, column=0, sticky="w")
    
    def setup_ai_integration(self, parent):
        """AI integration section"""
        ai_frame = ttk.LabelFrame(parent, text="🤖 AI Assistant", padding="8")
        ai_frame.grid(row=4, column=0, sticky="ew", pady=(0, 8))
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
    
    def setup_center_image_display(self, parent):
        """Enhanced center image display"""
        image_panel = ttk.Frame(parent, relief='groove', borderwidth=1)
        image_panel.grid(row=0, column=1, sticky="nsew", padx=5)
        image_panel.columnconfigure(0, weight=1)
        image_panel.rowconfigure(1, weight=1)
        
        # Tab header
        tab_frame = ttk.Frame(image_panel)
        tab_frame.grid(row=0, column=0, sticky="ew", padx=8, pady=(8, 0))
        
        self.input_tab_btn = ttk.Button(
            tab_frame,
            text="📥 Input",
            command=lambda: self.switch_image_view('input'),
            width=12
        )
        self.input_tab_btn.pack(side=tk.LEFT, padx=(0, 4))
        
        self.result_tab_btn = ttk.Button(
            tab_frame,
            text="✨ Result",
            command=lambda: self.switch_image_view('result'),
            width=12
        )
        self.result_tab_btn.pack(side=tk.LEFT)
        
        # Image canvas with scrollbars
        canvas_frame = ttk.Frame(image_panel)
        canvas_frame.grid(row=1, column=0, sticky="nsew", padx=8, pady=8)
        canvas_frame.columnconfigure(0, weight=1)
        canvas_frame.rowconfigure(0, weight=1)
        
        self.image_canvas = tk.Canvas(
            canvas_frame,
            bg='white',
            highlightthickness=1,
            highlightbackground='#dee2e6',
            cursor="crosshair"
        )
        self.image_canvas.grid(row=0, column=0, sticky="nsew")
        
        # Scrollbars
        h_scroll = ttk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL, command=self.image_canvas.xview)
        v_scroll = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=self.image_canvas.yview)
        
        self.image_canvas.configure(xscrollcommand=h_scroll.set, yscrollcommand=v_scroll.set)
        
        h_scroll.grid(row=1, column=0, sticky="ew")
        v_scroll.grid(row=0, column=1, sticky="ns")
        
        # Default message
        self.image_canvas.create_text(
            250, 200,
            text="Select an image to get started\n\nDrag & drop supported\nClick to browse",
            font=('Arial', 12),
            fill='#6c757d',
            justify=tk.CENTER
        )
    
    def setup_right_actions(self, parent):
        """Enhanced right actions panel"""
        actions_panel = ttk.Frame(parent, relief='groove', borderwidth=1, padding="8")
        actions_panel.grid(row=0, column=2, sticky="nsew", padx=(5, 0))
        actions_panel.columnconfigure(0, weight=1)
        
        # Main action button
        self.main_action_btn = ttk.Button(
            actions_panel,
            text=self.get_main_action_text(),
            command=self.process_image,
            style='Accent.TButton'
        )
        self.main_action_btn.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        
        # Status section
        status_frame = ttk.LabelFrame(actions_panel, text="📊 Status", padding="8")
        status_frame.grid(row=1, column=0, sticky="ew", pady=(0, 12))
        status_frame.columnconfigure(0, weight=1)
        
        self.status_label = ttk.Label(
            status_frame,
            text="Ready",
            font=('Arial', 9),
            foreground="#28a745"
        )
        self.status_label.grid(row=0, column=0, sticky="w")
        
        # Progress bar (hidden by default)
        self.progress_bar = ttk.Progressbar(
            status_frame,
            mode='indeterminate',
            length=180
        )
        
        # Quick actions
        quick_frame = ttk.LabelFrame(actions_panel, text="⚡ Quick Actions", padding="8")
        quick_frame.grid(row=2, column=0, sticky="ew", pady=(0, 12))
        quick_frame.columnconfigure(0, weight=1)
        
        ttk.Button(quick_frame, text="🧹 Clear All", command=self.clear_all, width=15).grid(row=0, column=0, sticky="ew", pady=2)
        ttk.Button(quick_frame, text="🎲 Load Sample", command=self.load_sample, width=15).grid(row=1, column=0, sticky="ew", pady=2)
        ttk.Button(quick_frame, text="💾 Save Result", command=self.save_result, width=15).grid(row=2, column=0, sticky="ew", pady=2)
        
        # Results history
        history_frame = ttk.LabelFrame(actions_panel, text="📚 Recent Results", padding="8")
        history_frame.grid(row=3, column=0, sticky="nsew", pady=(0, 12))
        history_frame.columnconfigure(0, weight=1)
        
        self.results_listbox = tk.Listbox(
            history_frame,
            height=8,
            font=('Arial', 8),
            selectmode=tk.SINGLE
        )
        self.results_listbox.grid(row=0, column=0, sticky="ew")
        self.results_listbox.bind('<<ListboxSelect>>', self.on_result_selected)
        
        # Spacer
        spacer = ttk.Frame(actions_panel)
        spacer.grid(row=4, column=0, sticky="nsew")
        actions_panel.rowconfigure(4, weight=1)
    
    def get_main_action_text(self):
        """Get main action button text based on model type"""
        action_texts = {
            "seedream_v4": "🚀 Generate with Seedream V4",
            "seededit": "✏️ Edit with SeedEdit",
            "image_editor": "🍌 Edit with Nano Banana",
            "image_upscaler": "⬆️ Upscale Image",
            "image_to_video": "🎬 Create Video",
            "seeddance": "💃 Generate with SeedDance"
        }
        return action_texts.get(self.model_type, "🔄 Process Image")
    
    # Event handlers and utility methods
    def browse_image(self):
        """Browse for image file"""
        file_path = filedialog.askopenfilename(
            title="Select Image",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.gif *.bmp *.webp"),
                ("All files", "*.*")
            ]
        )
        if file_path:
            self.load_image(file_path)
    
    def load_image(self, image_path):
        """Load and display image"""
        self.selected_image_path = image_path
        
        try:
            # Update thumbnail
            img = Image.open(image_path)
            img = ImageOps.exif_transpose(img)  # Fix orientation
            img.thumbnail((60, 60), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            
            self.thumbnail_label.config(image=photo, text="")
            self.thumbnail_label.image = photo
            
            # Update info
            filename = os.path.basename(image_path)
            if len(filename) > 25:
                filename = filename[:22] + "..."
            self.image_name_label.config(text=filename, foreground="#212529")
            
            # Get original image size
            original = Image.open(image_path)
            original = ImageOps.exif_transpose(original)
            self.image_size_label.config(text=f"{original.width}×{original.height}px")
            
            # Load into main canvas
            self.display_image_in_canvas(image_path)
            
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
        self.image_canvas.create_text(
            250, 200,
            text="Select an image to get started\n\nDrag & drop supported\nClick to browse",
            font=('Arial', 12),
            fill='#6c757d',
            justify=tk.CENTER
        )
        self.update_status("Image cleared", "info")
    
    def display_image_in_canvas(self, image_path):
        """Display image in canvas with proper scaling"""
        try:
            img = Image.open(image_path)
            img = ImageOps.exif_transpose(img)
            
            # Get canvas size
            self.image_canvas.update_idletasks()
            canvas_width = self.image_canvas.winfo_width()
            canvas_height = self.image_canvas.winfo_height()
            
            if canvas_width <= 1 or canvas_height <= 1:
                canvas_width = 500
                canvas_height = 400
            
            # Scale image to fit canvas
            img_ratio = img.width / img.height
            canvas_ratio = canvas_width / canvas_height
            
            if img_ratio > canvas_ratio:
                new_width = min(canvas_width - 20, img.width)
                new_height = int(new_width / img_ratio)
            else:
                new_height = min(canvas_height - 20, img.height)
                new_width = int(new_height * img_ratio)
            
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            
            # Clear and display
            self.image_canvas.delete("all")
            x = (canvas_width - new_width) // 2
            y = (canvas_height - new_height) // 2
            self.image_canvas.create_image(x, y, anchor=tk.NW, image=photo)
            self.image_canvas.image = photo
            
            # Update scroll region
            self.image_canvas.configure(scrollregion=self.image_canvas.bbox("all"))
            
        except Exception as e:
            logger.error(f"Error displaying image: {e}")
            self.image_canvas.delete("all")
            self.image_canvas.create_text(
                250, 200,
                text=f"Error loading image:\n{str(e)}",
                font=('Arial', 10),
                fill='red',
                justify=tk.CENTER
            )
    
    def switch_image_view(self, view_type):
        """Switch between input and result views"""
        if view_type == 'input' and self.selected_image_path:
            self.display_image_in_canvas(self.selected_image_path)
            self.input_tab_btn.config(relief='sunken')
            self.result_tab_btn.config(relief='raised')
        elif view_type == 'result' and self.result_image:
            self.display_image_in_canvas(self.result_image)
            self.result_tab_btn.config(relief='sunken')
            self.input_tab_btn.config(relief='raised')
    
    def process_image(self):
        """Process the image"""
        if not self.selected_image_path:
            self.update_status("Please select an image first", "error")
            return
        
        prompt = self.prompt_text.get("1.0", tk.END).strip()
        if not prompt or prompt == "Describe what you want to create or edit...":
            self.update_status("Please enter a prompt", "error")
            return
        
        if self.is_processing:
            self.update_status("Already processing...", "warning")
            return
        
        # Show progress
        self.is_processing = True
        self.update_status("Processing...", "info")
        self.progress_bar.grid(row=1, column=0, sticky="ew", pady=(8, 0))
        self.progress_bar.start()
        self.main_action_btn.config(state='disabled')
        
        # Notify parent to handle processing
        if self.on_process_requested:
            self.on_process_requested()
    
    def after_processing(self, success: bool, result_url: str = None, error_message: str = None):
        """Called after processing is complete"""
        self.is_processing = False
        
        # Hide progress
        self.progress_bar.stop()
        self.progress_bar.grid_remove()
        self.main_action_btn.config(state='normal')
        
        if success:
            self.result_url = result_url
            self.update_status("Processing complete!", "success")
            self.result_tab_btn.config(text="✨ Result ✓")
            
            # Auto-save if enabled
            if self.auto_save_var.get():
                self.auto_save_result()
        else:
            self.update_status(f"Error: {error_message}", "error")
    
    def auto_save_result(self):
        """Auto-save the result"""
        if not self.result_url:
            return
        
        try:
            prompt = self.prompt_text.get("1.0", tk.END).strip()
            extra_info = self.get_extra_info()
            
            success, saved_path, error = auto_save_manager.save_result(
                self.model_type,
                self.result_url,
                prompt=prompt,
                extra_info=extra_info
            )
            
            if success:
                self.update_status(f"Auto-saved to: {os.path.basename(saved_path)}", "success")
                
                # Track successful prompt
                prompt_tracker.log_successful_prompt(
                    prompt=prompt,
                    ai_model=self.model_type,
                    result_url=self.result_url,
                    save_path=saved_path,
                    additional_context=self.get_context_data()
                )
            else:
                self.update_status(f"Auto-save failed: {error}", "warning")
                
        except Exception as e:
            logger.error(f"Auto-save error: {e}")
            self.update_status(f"Auto-save error: {str(e)}", "warning")
    
    def get_extra_info(self):
        """Get extra info for auto-save"""
        extra_info = []
        
        if self.model_type == "seedream_v4":
            width = self.width_var.get()
            height = self.height_var.get()
            seed = self.seed_var.get()
            extra_info.append(f"{width}x{height}_seed{seed}")
        elif self.model_type == "seededit":
            gs = self.guidance_scale_var.get()
            steps = self.steps_var.get()
            extra_info.append(f"gs{gs}_steps{steps}")
        
        return "_".join(extra_info) if extra_info else None
    
    def get_context_data(self):
        """Get context data for prompt tracking"""
        context = {
            "auto_saved": True,
            "model_type": self.model_type
        }
        
        if self.model_type == "seedream_v4":
            context.update({
                "width": self.width_var.get(),
                "height": self.height_var.get(),
                "seed": self.seed_var.get(),
                "sync_mode": self.sync_mode_var.get(),
                "base64_output": self.base64_output_var.get()
            })
        elif self.model_type == "seededit":
            context.update({
                "guidance_scale": self.guidance_scale_var.get(),
                "steps": self.steps_var.get()
            })
        
        return context
    
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
    
    def toggle_advanced_options(self):
        """Toggle advanced options visibility"""
        if self.advanced_container.winfo_viewable():
            self.advanced_container.grid_remove()
            self.advanced_toggle.config(text="Show Advanced Options")
        else:
            self.advanced_container.grid(row=1, column=0, sticky="ew", pady=(8, 0))
            self.advanced_toggle.config(text="Hide Advanced Options")
    
    def clear_placeholder(self, event):
        """Clear placeholder text"""
        if self.prompt_text.get("1.0", tk.END).strip() == "Describe what you want to create or edit...":
            self.prompt_text.delete("1.0", tk.END)
    
    def add_placeholder(self, event):
        """Add placeholder text"""
        if not self.prompt_text.get("1.0", tk.END).strip():
            self.prompt_text.insert("1.0", "Describe what you want to create or edit...")
    
    def randomize_seed(self):
        """Randomize seed value"""
        import random
        self.seed_var.set(str(random.randint(1, 999999)))
    
    def load_saved_prompts(self):
        """Load saved prompts from file"""
        try:
            prompts_file = Path("data") / f"{self.model_type}_prompts.json"
            if prompts_file.exists():
                with open(prompts_file, 'r', encoding='utf-8') as f:
                    prompts_data = json.load(f)
                    prompts = list(prompts_data.keys())
                    self.prompts_combo['values'] = prompts
        except Exception as e:
            logger.error(f"Error loading saved prompts: {e}")
    
    def save_prompt(self):
        """Save current prompt"""
        prompt = self.prompt_text.get("1.0", tk.END).strip()
        if not prompt or prompt == "Describe what you want to create or edit...":
            messagebox.showwarning("No Prompt", "Please enter a prompt to save.")
            return
        
        # Get prompt name from user
        name = tk.simpledialog.askstring("Save Prompt", "Enter a name for this prompt:")
        if not name:
            return
        
        try:
            prompts_file = Path("data") / f"{self.model_type}_prompts.json"
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
            self.prompts_combo['values'] = list(prompts_data.keys())
            self.saved_prompts_var.set(name)
            
            self.update_status(f"Prompt '{name}' saved", "success")
            
        except Exception as e:
            logger.error(f"Error saving prompt: {e}")
            messagebox.showerror("Error", f"Failed to save prompt: {str(e)}")
    
    def delete_prompt(self):
        """Delete selected prompt"""
        selected = self.saved_prompts_var.get()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a prompt to delete.")
            return
        
        if messagebox.askyesno("Confirm Delete", f"Delete prompt '{selected}'?"):
            try:
                prompts_file = Path("data") / f"{self.model_type}_prompts.json"
                if prompts_file.exists():
                    with open(prompts_file, 'r', encoding='utf-8') as f:
                        prompts_data = json.load(f)
                    
                    if selected in prompts_data:
                        del prompts_data[selected]
                        
                        with open(prompts_file, 'w', encoding='utf-8') as f:
                            json.dump(prompts_data, f, indent=2, ensure_ascii=False)
                        
                        # Update dropdown
                        self.prompts_combo['values'] = list(prompts_data.keys())
                        self.saved_prompts_var.set("")
                        
                        self.update_status(f"Prompt '{selected}' deleted", "success")
                        
            except Exception as e:
                logger.error(f"Error deleting prompt: {e}")
                messagebox.showerror("Error", f"Failed to delete prompt: {str(e)}")
    
    def on_prompt_selected(self, event):
        """Handle prompt selection"""
        selected = self.saved_prompts_var.get()
        if selected:
            try:
                prompts_file = Path("data") / f"{self.model_type}_prompts.json"
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
        sample_prompts = {
            "seedream_v4": "Transform the subject into a cyberpunk character with neon lights and futuristic clothing",
            "seededit": "Change the background to a beautiful sunset landscape",
            "image_editor": "Make the person smile and add a warm glow effect",
            "image_upscaler": "Enhance details and improve sharpness",
            "image_to_video": "Create a smooth zoom-in effect with subtle camera movement",
            "seeddance": "Generate a dancing animation with fluid movements"
        }
        
        sample = sample_prompts.get(self.model_type, "Create something amazing!")
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
        self.prompt_text.insert("1.0", "Describe what you want to create or edit...")
        self.saved_prompts_var.set("")
        self.update_status("All cleared", "info")
    
    def save_result(self):
        """Save result manually"""
        if not self.result_url:
            messagebox.showwarning("No Result", "No result to save.")
            return
        
        # This would implement manual save functionality
        self.update_status("Manual save not yet implemented", "info")
    
    def on_result_selected(self, event):
        """Handle result selection from history"""
        # This would implement result history functionality
        pass
