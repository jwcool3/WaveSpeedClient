"""
Improved Seedream V4 Tab Layout - Fixing All Issues
1. Two-column structure eliminates vertical scrolling
2. Compact horizontal settings (1/3 the height)  
3. Apply button directly under prompt
4. Collapsible advanced sections
5. Large dynamic preview with minimal margins
6. No wasted horizontal space
7. ENHANCED: Unified status console and keyboard shortcuts
"""

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os
import asyncio
from ui.components.unified_status_console import UnifiedStatusConsole
from ui.components.keyboard_manager import KeyboardManager
from ui.components.ai_chat_integration_helper import AIChatMixin
from core.logger import get_logger

logger = get_logger()


class ImprovedSeedreamLayout(AIChatMixin):
    """Improved Seedream V4 layout with efficient space usage and better UX"""
    
    def __init__(self, parent_frame):
        self.parent_frame = parent_frame
        self.selected_image_path = None
        self.result_image_path = None
        self.tab_name = "Seedream V4"  # For AI integration
        
        # Settings variables
        self.width_var = tk.IntVar(value=1024)
        self.height_var = tk.IntVar(value=1024)
        self.seed_var = tk.StringVar(value="-1")
        self.sync_mode_var = tk.BooleanVar(value=False)
        self.base64_var = tk.BooleanVar(value=False)
        
        # Size presets
        self.size_presets = [
            ("1K", 1024, 1024),
            ("2K", 2048, 2048), 
            ("4K", 3840, 2160),
            ("Square", 1024, 1024),
            ("Portrait", 768, 1024),
            ("Landscape", 1024, 768)
        ]
        
        # Enhanced components
        self.status_console = None
        self.keyboard_manager = None
        
        self.setup_layout()
        self.setup_enhanced_features()
    
    def setup_layout(self):
        """Setup the improved 2-column layout"""
        
        # Main container
        main_container = ttk.Frame(self.parent_frame)
        main_container.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        
        # Configure grid - 2 columns with no wasted space
        main_container.columnconfigure(0, weight=1, minsize=380)  # Left: Controls (slightly wider for settings)
        main_container.columnconfigure(1, weight=2, minsize=520)  # Right: Images (2x weight)
        main_container.rowconfigure(0, weight=1)
        
        # Left Column - Compact Controls
        self.setup_left_column(main_container)
        
        # Right Column - Large Image Display  
        self.setup_right_column(main_container)
    
    def setup_left_column(self, parent):
        """Setup left column with logical flow and compact sections"""
        left_frame = ttk.Frame(parent, padding="8")
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 4))
        left_frame.columnconfigure(0, weight=1)
        
        # Configure rows to eliminate vertical scrolling
        left_frame.rowconfigure(0, weight=0)  # Image input - compact
        left_frame.rowconfigure(1, weight=0)  # Settings - MUCH more compact
        left_frame.rowconfigure(2, weight=0)  # Prompt section - compact  
        left_frame.rowconfigure(3, weight=0)  # Primary action - prominent
        left_frame.rowconfigure(4, weight=0)  # Advanced sections - collapsible
        left_frame.rowconfigure(5, weight=0)  # Status console - professional feedback
        left_frame.rowconfigure(6, weight=1)  # Spacer
        left_frame.rowconfigure(7, weight=0)  # Secondary actions - bottom
        
        # 1. COMPACT IMAGE INPUT
        self.setup_compact_image_input(left_frame)
        
        # 2. SUPER COMPACT SETTINGS (key improvement!)
        self.setup_compact_settings(left_frame)
        
        # 3. PROMPT SECTION
        self.setup_prompt_section(left_frame)
        
        # 4. PRIMARY ACTION (right under prompt!)
        self.setup_primary_action(left_frame)
        
        # 5. COLLAPSIBLE ADVANCED SECTIONS
        self.setup_advanced_sections(left_frame)
        
        # 6. STATUS CONSOLE (professional feedback)
        self.setup_status_console(left_frame)
        
        # 7. SPACER
        spacer = ttk.Frame(left_frame)
        spacer.grid(row=6, column=0, sticky="nsew")
        
        # 8. SECONDARY ACTIONS (at bottom)
        self.setup_secondary_actions(left_frame)
    
    def setup_compact_image_input(self, parent):
        """Very compact image input section"""
        input_frame = ttk.LabelFrame(parent, text="📥 Input Image", padding="6")
        input_frame.grid(row=0, column=0, sticky="ew", pady=(0, 6))
        input_frame.columnconfigure(1, weight=1)
        
        # Thumbnail + Info in one row (same as SeedEdit)
        self.thumbnail_label = tk.Label(
            input_frame,
            text="📁",
            width=8, height=4,
            bg='#f5f5f5',
            relief='solid',
            borderwidth=1,
            cursor="hand2",
            font=('Arial', 10)
        )
        self.thumbnail_label.grid(row=0, column=0, padx=(0, 8), rowspan=2)
        self.thumbnail_label.bind("<Button-1>", lambda e: self.browse_image())
        
        # Image info
        self.image_name_label = ttk.Label(
            input_frame,
            text="No image selected",
            font=('Arial', 9, 'bold'),
            foreground="gray"
        )
        self.image_name_label.grid(row=0, column=1, sticky="w")
        
        info_frame = ttk.Frame(input_frame)
        info_frame.grid(row=1, column=1, sticky="ew")
        
        self.image_size_label = ttk.Label(
            info_frame,
            text="",
            font=('Arial', 8),
            foreground="gray"
        )
        self.image_size_label.pack(side=tk.LEFT)
        
        browse_btn = ttk.Button(
            info_frame,
            text="Browse",
            command=self.browse_image,
            width=8
        )
        browse_btn.pack(side=tk.RIGHT)
    
    def setup_compact_settings(self, parent):
        """SUPER compact settings - key improvement! 1/3 the height"""
        settings_frame = ttk.LabelFrame(parent, text="⚙️ Settings", padding="6")
        settings_frame.grid(row=1, column=0, sticky="ew", pady=(0, 6))
        settings_frame.columnconfigure(1, weight=1)
        settings_frame.columnconfigure(3, weight=1)
        
        # Row 1: Width + Height (side by side with sliders)
        ttk.Label(settings_frame, text="Size:", font=('Arial', 9, 'bold')).grid(
            row=0, column=0, sticky="w", columnspan=4, pady=(0, 2)
        )
        
        # Width
        ttk.Label(settings_frame, text="W:", font=('Arial', 8)).grid(
            row=1, column=0, sticky="w"
        )
        
        width_frame = ttk.Frame(settings_frame)
        width_frame.grid(row=1, column=1, sticky="ew", padx=(2, 8))
        
        self.width_scale = ttk.Scale(
            width_frame,
            from_=256, to=4096,
            variable=self.width_var,
            orient=tk.HORIZONTAL,
            length=80,
            command=self.on_size_changed
        )
        self.width_scale.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.width_entry = ttk.Entry(
            width_frame,
            textvariable=self.width_var,
            width=5,
            font=('Arial', 8)
        )
        self.width_entry.pack(side=tk.RIGHT, padx=(2, 0))
        
        # Height  
        ttk.Label(settings_frame, text="H:", font=('Arial', 8)).grid(
            row=1, column=2, sticky="w"
        )
        
        height_frame = ttk.Frame(settings_frame)
        height_frame.grid(row=1, column=3, sticky="ew")
        
        self.height_scale = ttk.Scale(
            height_frame,
            from_=256, to=4096,
            variable=self.height_var,
            orient=tk.HORIZONTAL,
            length=80,
            command=self.on_size_changed
        )
        self.height_scale.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.height_entry = ttk.Entry(
            height_frame,
            textvariable=self.height_var,
            width=5,
            font=('Arial', 8)
        )
        self.height_entry.pack(side=tk.RIGHT, padx=(2, 0))
        
        # Row 2: Size presets (grid layout - much more compact!)
        preset_frame = ttk.Frame(settings_frame)
        preset_frame.grid(row=2, column=0, columnspan=4, sticky="ew", pady=(4, 2))
        
        # Preset buttons in a 3x2 grid
        for i, (name, width, height) in enumerate(self.size_presets):
            btn = ttk.Button(
                preset_frame,
                text=name,
                command=lambda w=width, h=height: self.set_size_preset(w, h),
                width=6
            )
            btn.grid(row=i//3, column=i%3, padx=1, pady=1, sticky="ew")
        
        # Configure preset frame columns
        for i in range(3):
            preset_frame.columnconfigure(i, weight=1)
        
        # Row 3: Seed + Options (horizontal)
        ttk.Label(settings_frame, text="Seed:", font=('Arial', 8)).grid(
            row=3, column=0, sticky="w", pady=(4, 0)
        )
        
        seed_entry = ttk.Entry(
            settings_frame,
            textvariable=self.seed_var,
            width=8,
            font=('Arial', 8)
        )
        seed_entry.grid(row=3, column=1, sticky="w", pady=(4, 0))
        
        # Lock aspect ratio button
        self.lock_aspect_btn = ttk.Button(
            settings_frame,
            text="🔒",
            width=3,
            command=self.toggle_aspect_lock
        )
        self.lock_aspect_btn.grid(row=3, column=2, sticky="w", padx=(8, 0), pady=(4, 0))
        
        # Auto-resolution button
        auto_btn = ttk.Button(
            settings_frame,
            text="Auto",
            width=6,
            command=self.auto_set_resolution
        )
        auto_btn.grid(row=3, column=3, sticky="e", pady=(4, 0))
    
    def setup_prompt_section(self, parent):
        """Compact prompt section"""
        prompt_frame = ttk.LabelFrame(parent, text="✏️ Transformation Prompt", padding="6")
        prompt_frame.grid(row=2, column=0, sticky="ew", pady=(0, 6))
        prompt_frame.columnconfigure(0, weight=1)
        
        # Preset management (horizontal row)
        preset_frame = ttk.Frame(prompt_frame)
        preset_frame.grid(row=0, column=0, sticky="ew", pady=(0, 4))
        preset_frame.columnconfigure(0, weight=1)
        
        # Preset dropdown
        self.preset_var = tk.StringVar()
        self.preset_combo = ttk.Combobox(
            preset_frame,
            textvariable=self.preset_var,
            font=('Arial', 9),
            width=20
        )
        self.preset_combo.grid(row=0, column=0, sticky="ew", padx=(0, 4))
        self.preset_combo.bind('<<ComboboxSelected>>', self.load_preset)
        
        # Preset buttons (small) - AI integration target
        self.ai_chat_container = ttk.Frame(preset_frame)
        self.ai_chat_container.grid(row=0, column=1)
        
        ttk.Button(self.ai_chat_container, text="💾", width=3, command=self.save_preset).pack(side=tk.LEFT, padx=1)
        ttk.Button(self.ai_chat_container, text="🎲", width=3, command=self.load_sample).pack(side=tk.LEFT, padx=1)
        ttk.Button(self.ai_chat_container, text="🤖", width=3, command=self.improve_with_ai).pack(side=tk.LEFT, padx=1)
        
        # Prompt text (compact)
        self.prompt_text = tk.Text(
            prompt_frame,
            height=4,  # Compact height
            wrap=tk.WORD,
            font=('Arial', 10),
            relief='solid',
            borderwidth=1
        )
        self.prompt_text.grid(row=1, column=0, sticky="ew", pady=(4, 0))
        
        # Placeholder text
        self.prompt_text.insert("1.0", "Describe the transformation you want to apply to the image...")
        self.prompt_text.bind("<FocusIn>", self.clear_placeholder)
        self.prompt_text.bind("<FocusOut>", self.add_placeholder)
    
    def setup_primary_action(self, parent):
        """Primary action button RIGHT under prompt - key UX improvement!"""
        action_frame = ttk.Frame(parent)
        action_frame.grid(row=3, column=0, sticky="ew", pady=6)
        action_frame.columnconfigure(0, weight=1)
        
        # PROMINENT primary action button
        self.primary_btn = ttk.Button(
            action_frame,
            text="🌟 Apply Seedream V4",
            command=self.process_seedream,
            style='Accent.TButton'
        )
        self.primary_btn.grid(row=0, column=0, sticky="ew")
        
        # Status indicator right below
        self.status_label = ttk.Label(
            action_frame,
            text="Ready for transformation",
            font=('Arial', 9),
            foreground="green"
        )
        self.status_label.grid(row=1, column=0, pady=(4, 0))
        
        # Progress bar (hidden by default)
        self.progress_bar = ttk.Progressbar(
            action_frame,
            mode='indeterminate'
        )
        # Don't grid it yet - only show when processing
    
    def setup_advanced_sections(self, parent):
        """Collapsible advanced sections - saves lots of space!"""
        advanced_frame = ttk.Frame(parent)
        advanced_frame.grid(row=4, column=0, sticky="ew", pady=(0, 6))
        advanced_frame.columnconfigure(0, weight=1)
        
        # AI Assistant (collapsible)
        self.ai_section = self.create_collapsible_section(
            advanced_frame, 
            "🤖 AI Assistant", 
            row=0
        )
        
        # Add AI assistant content
        ai_btn = ttk.Button(
            self.ai_section['content'],
            text="✨ Improve Prompt with AI",
            command=self.improve_with_ai,
            width=20
        )
        ai_btn.pack(pady=2)
        
        filter_btn = ttk.Button(
            self.ai_section['content'],
            text="🛡️ Filter Training Mode",
            command=self.filter_training,
            width=20
        )
        filter_btn.pack(pady=2)
        
        # Advanced Options (collapsible)
        self.options_section = self.create_collapsible_section(
            advanced_frame,
            "🔧 Advanced Options",
            row=1
        )
        
        # Add advanced options content
        options_content = ttk.Frame(self.options_section['content'])
        options_content.pack(fill=tk.X, pady=2)
        options_content.columnconfigure(1, weight=1)
        
        ttk.Checkbutton(
            options_content,
            text="Sync Mode",
            variable=self.sync_mode_var
        ).grid(row=0, column=0, sticky="w")
        
        ttk.Checkbutton(
            options_content,
            text="Base64 Output",
            variable=self.base64_var
        ).grid(row=0, column=1, sticky="w", padx=(10, 0))
        
        # Progress Log (collapsible)
        self.log_section = self.create_collapsible_section(
            advanced_frame,
            "📊 Progress Log",
            row=2
        )
        
        # Add log content
        self.log_text = tk.Text(
            self.log_section['content'],
            height=4,
            width=1,
            font=('Courier', 8),
            bg='#f8f8f8',
            state=tk.DISABLED
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, pady=2)
    
    def create_collapsible_section(self, parent, title, row):
        """Create a collapsible section"""
        section_frame = ttk.Frame(parent)
        section_frame.grid(row=row, column=0, sticky="ew", pady=1)
        section_frame.columnconfigure(1, weight=1)
        
        # Header with toggle button
        toggle_btn = ttk.Button(
            section_frame,
            text="▶",
            width=3,
            command=lambda: self.toggle_section(section_frame, toggle_btn)
        )
        toggle_btn.grid(row=0, column=0, sticky="w")
        
        title_label = ttk.Label(
            section_frame,
            text=title,
            font=('Arial', 9, 'bold')
        )
        title_label.grid(row=0, column=1, sticky="w", padx=(4, 0))
        
        # Content frame (initially hidden)
        content_frame = ttk.Frame(section_frame)
        # Don't grid it yet - will be shown/hidden by toggle
        
        return {
            'frame': section_frame,
            'toggle': toggle_btn,
            'content': content_frame,
            'expanded': False
        }
    
    def toggle_section(self, section_frame, toggle_btn):
        """Toggle collapsible section"""
        # Find the section data
        section_data = None
        for section in [self.ai_section, self.options_section, self.log_section]:
            if section['toggle'] == toggle_btn:
                section_data = section
                break
        
        if not section_data:
            return
        
        if section_data['expanded']:
            # Collapse
            section_data['content'].grid_remove()
            toggle_btn.config(text="▶")
            section_data['expanded'] = False
        else:
            # Expand
            section_data['content'].grid(row=1, column=0, columnspan=2, sticky="ew", padx=(20, 0), pady=(2, 0))
            toggle_btn.config(text="▼")
            section_data['expanded'] = True
    
    def setup_secondary_actions(self, parent):
        """Compact secondary actions at bottom"""
        secondary_frame = ttk.LabelFrame(parent, text="🔧 Tools", padding="4")
        secondary_frame.grid(row=7, column=0, sticky="ew")
        secondary_frame.columnconfigure(0, weight=1)
        secondary_frame.columnconfigure(1, weight=1)
        
        # Row 1: Clear and Sample
        ttk.Button(
            secondary_frame,
            text="🧹 Clear",
            command=self.clear_all,
            width=10
        ).grid(row=0, column=0, sticky="ew", padx=(0, 1), pady=1)
        
        ttk.Button(
            secondary_frame,
            text="🎲 Sample",
            command=self.load_sample,
            width=10
        ).grid(row=0, column=1, sticky="ew", padx=(1, 0), pady=1)
        
        # Row 2: Save and Load
        ttk.Button(
            secondary_frame,
            text="💾 Save",
            command=self.save_result,
            width=10
        ).grid(row=1, column=0, sticky="ew", padx=(0, 1), pady=1)
        
        ttk.Button(
            secondary_frame,
            text="📂 Load",
            command=self.load_result,
            width=10
        ).grid(row=1, column=1, sticky="ew", padx=(1, 0), pady=1)
    
    def setup_status_console(self, parent):
        """Setup unified status console for professional feedback"""
        self.status_console = UnifiedStatusConsole(
            parent, 
            title="📊 Status", 
            height=3  # Compact height for Seedream V4
        )
        self.status_console.grid(row=5, column=0, sticky="ew", pady=(0, 4))
        self.status_console.log_ready("Seedream V4")
    
    def setup_enhanced_features(self):
        """Setup keyboard manager and enhanced functionality"""
        # Setup keyboard manager
        self.keyboard_manager = KeyboardManager(self.parent_frame, "Seedream V4")
        
        # Register primary action (will be connected by tab)
        # self.keyboard_manager.register_primary_action(self.process_seedream, self.apply_btn)
        
        # Register file operations (will be connected by tab)
        # self.keyboard_manager.register_file_actions(
        #     open_file=self.browse_image,
        #     save_result=self.save_result,
        #     clear_all=self.clear_all
        # )
        
        # Register AI actions (will be connected by tab)
        # self.keyboard_manager.register_ai_actions(
        #     improve_callback=self.improve_with_ai,
        #     filter_callback=self.filter_training,
        #     chat_callback=self.ai_chat
        # )
    
    def setup_right_column(self, parent):
        """Setup right column with large dynamic image display"""
        right_frame = ttk.Frame(parent, padding="4")
        right_frame.grid(row=0, column=1, sticky="nsew", padx=(4, 0))
        right_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(1, weight=1)
        
        # Image viewing controls
        self.setup_image_controls(right_frame)
        
        # Large image display
        self.setup_image_display(right_frame)
    
    def setup_image_controls(self, parent):
        """Setup image viewing controls"""
        controls_frame = ttk.Frame(parent)
        controls_frame.grid(row=0, column=0, sticky="ew", pady=(0, 4))
        controls_frame.columnconfigure(2, weight=1)
        
        # View mode buttons
        self.view_original_btn = ttk.Button(
            controls_frame,
            text="📥 Original",
            command=lambda: self.set_view_mode("original"),
            width=10
        )
        self.view_original_btn.grid(row=0, column=0, padx=(0, 2))
        
        self.view_result_btn = ttk.Button(
            controls_frame,
            text="🌟 Result",
            command=lambda: self.set_view_mode("result"),
            width=10
        )
        self.view_result_btn.grid(row=0, column=1, padx=(0, 8))
        
        # Comparison and zoom controls (same as SeedEdit)
        self.comparison_btn = ttk.Button(
            controls_frame,
            text="⚖️ Compare",
            command=self.toggle_comparison_mode,
            width=10
        )
        self.comparison_btn.grid(row=0, column=3, padx=(8, 0))
        
        zoom_frame = ttk.Frame(controls_frame)
        zoom_frame.grid(row=0, column=4, padx=(8, 0))
        
        ttk.Label(zoom_frame, text="Zoom:", font=('Arial', 9)).pack(side=tk.LEFT)
        
        self.zoom_var = tk.StringVar(value="Fit")
        zoom_combo = ttk.Combobox(
            zoom_frame,
            textvariable=self.zoom_var,
            values=["Fit", "50%", "100%", "150%", "200%"],
            state="readonly",
            width=6,
            font=('Arial', 9)
        )
        zoom_combo.pack(side=tk.LEFT, padx=(2, 0))
        zoom_combo.bind('<<ComboboxSelected>>', self.on_zoom_changed)
    
    def setup_image_display(self, parent):
        """Setup large image display with minimal margins"""
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
        """Show default message"""
        self.image_canvas.delete("all")
        self.image_canvas.create_text(
            260, 200,
            text="Select an image to transform\n\nDrag & drop supported",
            font=('Arial', 14),
            fill='#888',
            justify=tk.CENTER
        )
    
    # Event handlers and utility methods
    def browse_image(self):
        """Browse for image file"""
        from tkinter import filedialog
        file_path = filedialog.askopenfilename(
            title="Select Image for Seedream V4",
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
            img.thumbnail((50, 50), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            
            self.thumbnail_label.config(image=photo, text="")
            self.thumbnail_label.image = photo
            
            # Update info
            filename = os.path.basename(image_path)
            if len(filename) > 25:
                filename = filename[:22] + "..."
            self.image_name_label.config(text=filename, foreground="black")
            
            # Get image size
            original = Image.open(image_path)
            self.image_size_label.config(text=f"{original.width}×{original.height}")
            
            # Auto-set resolution if enabled
            self.auto_set_resolution()
            
            # Display in main canvas
            self.set_view_mode("original")
            
        except Exception as e:
            self.status_label.config(text=f"Error loading image: {str(e)}", foreground="red")
    
    def set_size_preset(self, width, height):
        """Set size preset"""
        self.width_var.set(width)
        self.height_var.set(height)
        self.log_message(f"Size preset set to {width}×{height}")
    
    def auto_set_resolution(self):
        """Auto-set resolution based on input image"""
        if not self.selected_image_path:
            return
        
        try:
            img = Image.open(self.selected_image_path)
            # Set to input image size or closest preset
            self.width_var.set(img.width)
            self.height_var.set(img.height)
            self.log_message(f"Auto-set resolution to {img.width}×{img.height}")
        except:
            pass
    
    def toggle_aspect_lock(self):
        """Toggle aspect ratio lock"""
        # Implementation for aspect ratio locking
        pass
    
    def on_size_changed(self, value):
        """Handle size slider changes"""
        # Could implement aspect ratio locking here
        pass
    
    def process_seedream(self):
        """Process with Seedream V4"""
        if not self.selected_image_path:
            self.status_label.config(text="Please select an image first", foreground="red")
            return
        
        prompt = self.prompt_text.get("1.0", tk.END).strip()
        if not prompt or prompt == "Describe the transformation you want to apply to the image...":
            self.status_label.config(text="Please enter transformation instructions", foreground="red")
            return
        
        # Show processing state
        self.status_label.config(text="Processing with Seedream V4...", foreground="blue")
        self.progress_bar.grid(row=2, column=0, sticky="ew", pady=(4, 0))
        self.progress_bar.start()
        self.primary_btn.config(state='disabled', text="Processing...")
        
        # Log the start
        self.log_message(f"Starting Seedream V4 processing...")
        self.log_message(f"Size: {self.width_var.get()}×{self.height_var.get()}")
        self.log_message(f"Seed: {self.seed_var.get()}")
        
        # Here you would call your actual Seedream V4 API
        self.after_processing()
    
    def after_processing(self):
        """Called after processing completes"""
        # Hide progress
        self.progress_bar.stop()
        self.progress_bar.grid_remove()
        self.primary_btn.config(state='normal', text="🌟 Apply Seedream V4")
        self.status_label.config(text="✅ Transformation complete!", foreground="green")
        
        # Log completion
        self.log_message("✅ Processing completed successfully!")
        
        # Enable result view
        self.view_result_btn.config(state='normal')
        self.comparison_btn.config(state='normal')
    
    def log_message(self, message):
        """Add message to progress log"""
        if hasattr(self, 'log_text'):
            self.log_text.config(state=tk.NORMAL)
            self.log_text.insert(tk.END, f"{message}\n")
            self.log_text.see(tk.END)
            self.log_text.config(state=tk.DISABLED)
    
    # Image display methods (same as SeedEdit)
    def set_view_mode(self, mode):
        """Set image viewing mode"""
        self.current_view_mode = mode
        
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
            self.status_label.config(text="Need both images for comparison", foreground="orange")
            return
        
        self.comparison_btn.config(relief='sunken')
        self.view_original_btn.config(relief='raised')
        self.view_result_btn.config(relief='raised')
        
        self.display_comparison()
    
    def display_image(self, image_path, position="center"):
        """Display image with dynamic scaling"""
        # Same implementation as SeedEdit layout
        try:
            self.image_canvas.delete("all")
            
            img = Image.open(image_path)
            canvas_width = self.image_canvas.winfo_width()
            canvas_height = self.image_canvas.winfo_height()
            
            if canvas_width <= 1:
                canvas_width = 520
                canvas_height = 400
            
            zoom_value = self.zoom_var.get()
            if zoom_value == "Fit":
                scale_factor = min(
                    (canvas_width - 10) / img.width,
                    (canvas_height - 10) / img.height
                )
            else:
                scale_factor = float(zoom_value.rstrip('%')) / 100
            
            new_width = int(img.width * scale_factor)
            new_height = int(img.height * scale_factor)
            img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            photo = ImageTk.PhotoImage(img_resized)
            
            x = max(5, (canvas_width - new_width) // 2)
            y = max(5, (canvas_height - new_height) // 2)
            
            self.image_canvas.create_image(x, y, anchor=tk.NW, image=photo)
            self.image_canvas.image = photo
            
            self.image_canvas.configure(scrollregion=self.image_canvas.bbox("all"))
            
        except Exception as e:
            self.image_canvas.delete("all")
            self.image_canvas.create_text(
                260, 200,
                text=f"Error loading image:\n{str(e)}",
                font=('Arial', 12),
                fill='red',
                justify=tk.CENTER
            )
    
    def display_comparison(self):
        """Display side-by-side comparison"""
        # Same implementation as SeedEdit
        pass
    
    # Utility methods
    def clear_placeholder(self, event):
        current_text = self.prompt_text.get("1.0", tk.END).strip()
        if current_text == "Describe the transformation you want to apply to the image...":
            self.prompt_text.delete("1.0", tk.END)
    
    def add_placeholder(self, event):
        current_text = self.prompt_text.get("1.0", tk.END).strip()
        if not current_text:
            self.prompt_text.insert("1.0", "Describe the transformation you want to apply to the image...")
    
    def on_canvas_configure(self, event):
        """Handle canvas resize"""
        pass
    
    def on_canvas_click(self, event):
        """Handle canvas click"""
        pass
    
    def on_mouse_wheel(self, event):
        """Handle mouse wheel"""
        pass
    
    def on_zoom_changed(self, event):
        """Handle zoom change"""
        pass
    
    # Placeholder methods
    def load_preset(self, event=None): pass
    def save_preset(self): pass
    def load_sample(self): pass
    # AI integration methods inherited from AIChatMixin
    # improve_prompt_with_ai() and open_filter_training() are provided by the mixin
    
    def improve_with_ai(self):
        """Wrapper for improve_prompt_with_ai to maintain backwards compatibility"""
        self.improve_prompt_with_ai()
    
    def filter_training(self):
        """Wrapper for open_filter_training to maintain backwards compatibility"""  
        self.open_filter_training()
    
    def add_ai_chat_interface(self, prompt_widget, model_type, tab_instance):
        """Add AI chat interface for universal AI integration system"""
        try:
            # Store prompt widget reference
            self.prompt_widget = prompt_widget
            
            # Find or create AI container
            if hasattr(self, 'ai_chat_container'):
                container = self.ai_chat_container
            else:
                # Create a fallback container if needed
                container = ttk.Frame(self.parent_frame)
                container.pack(fill=tk.X, pady=2)
                self.ai_chat_container = container
            
            # Clear existing buttons
            for widget in container.winfo_children():
                widget.destroy()
            
            # Add AI buttons
            ttk.Button(container, text="🤖", width=3, 
                      command=self.improve_with_ai).pack(side=tk.LEFT, padx=1)
            ttk.Button(container, text="🛡️", width=3, 
                      command=self.filter_training).pack(side=tk.LEFT, padx=1)
            ttk.Button(container, text="💾", width=3, 
                      command=self.save_preset).pack(side=tk.LEFT, padx=1)
            ttk.Button(container, text="🎲", width=3, 
                      command=self.load_sample).pack(side=tk.LEFT, padx=1)
            
            return True
            
        except Exception as e:
            logger.error(f"Error adding AI chat interface to Seedream layout: {e}")
            return False
    
    def update_status(self, message: str, status_type: str = "info"):
        """Update status for AI integration"""
        try:
            if hasattr(self, 'status_console') and self.status_console:
                if status_type == "success":
                    self.status_console.log_success("AI", message)
                elif status_type == "error":
                    self.status_console.log_error("AI", message)
                elif status_type == "warning":
                    self.status_console.log_warning("AI", message)
                else:
                    self.status_console.log_info("AI", message)
            else:
                print(f"[{status_type.upper()}] {message}")
        except Exception as e:
            print(f"Status update error: {e}")
            print(f"[{status_type.upper()}] {message}")
    def clear_all(self): pass
    def load_result(self): pass
    def save_result(self): pass

    # Helper methods for tab integration
    
    def log_status(self, message: str, status_type: str = "info"):
        """Log status message to console"""
        if self.status_console:
            self.status_console.log_status(message, status_type)
    
    def log_processing_start(self, operation: str, details: str = ""):
        """Log start of processing with timing"""
        if self.status_console:
            self.status_console.log_processing_start(operation, details)
    
    def log_processing_complete(self, operation: str, success: bool = True, details: str = ""):
        """Log completion of processing with timing"""
        if self.status_console:
            self.status_console.log_processing_complete(operation, success, details)
    
    def log_file_operation(self, operation: str, filename: str, success: bool = True):
        """Log file operations"""
        if self.status_console:
            self.status_console.log_file_operation(operation, filename, success)
    
    def log_error(self, error_message: str, context: str = ""):
        """Log error message"""
        if self.status_console:
            self.status_console.log_error(error_message, context)
    
    def show_progress(self):
        """Show progress bar"""
        if self.status_console:
            self.status_console.show_progress()
    
    def hide_progress(self):
        """Hide progress bar"""
        if self.status_console:
            self.status_console.hide_progress()
    
    def setup_keyboard_callbacks(self, primary_action=None, primary_widget=None, 
                                browse_image=None, save_result=None, clear_all=None,
                                improve_ai=None, filter_training=None, ai_chat=None):
        """Setup keyboard callbacks from the parent tab"""
        if self.keyboard_manager:
            if primary_action and primary_widget:
                self.keyboard_manager.register_primary_action(primary_action, primary_widget)
            
            if browse_image or save_result or clear_all:
                self.keyboard_manager.register_file_actions(
                    open_file=browse_image,
                    save_result=save_result,
                    new_operation=clear_all
                )
            
            if improve_ai or filter_training or ai_chat:
                self.keyboard_manager.register_ai_actions(
                    improve_callback=improve_ai,
                    filter_callback=filter_training,
                    chat_callback=ai_chat
                )
    
    def set_operation_in_progress(self, in_progress: bool):
        """Update operation status for keyboard manager"""
        if self.keyboard_manager:
            self.keyboard_manager.set_operation_in_progress(in_progress)
