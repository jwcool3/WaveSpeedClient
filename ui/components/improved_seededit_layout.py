"""
Improved SeedEdit Tab Layout - Addressing All Issues
1. Two balanced columns instead of vertical stacking
2. Primary action button right under prompt
3. Dynamic image scaling with minimal margins
4. Side-by-side comparison instead of tabs
5. Horizontal settings layout to save space
6. No wasted space between columns
"""

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os

# Try to import drag and drop support
try:
    from tkinterdnd2 import DND_FILES
    DND_AVAILABLE = True
except ImportError:
    DND_AVAILABLE = False


class ImprovedSeedEditLayout:
    """Improved SeedEdit layout with efficient space usage and better UX"""
    
    def __init__(self, parent_frame, tab_instance=None):
        self.parent_frame = parent_frame
        self.tab_instance = tab_instance
        self.selected_image_path = None
        self.result_image_path = None
        self.comparison_mode = "side_by_side"  # "side_by_side" or "overlay"
        
        self.setup_layout()
    
    def setup_layout(self):
        """Setup the improved 2-column layout"""
        
        # Main container
        main_container = ttk.Frame(self.parent_frame)
        main_container.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        
        # Configure grid - 2 balanced columns
        main_container.columnconfigure(0, weight=1, minsize=350)  # Left: Controls
        main_container.columnconfigure(1, weight=2, minsize=500)  # Right: Images (2x weight)
        main_container.rowconfigure(0, weight=1)
        
        # Left Column - Controls & Actions
        self.setup_left_column(main_container)
        
        # Right Column - Image Display
        self.setup_right_column(main_container)
    
    def setup_left_column(self, parent):
        """Setup left column with logical flow: Input → Settings → Prompt → Action"""
        left_frame = ttk.Frame(parent, padding="8")
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 4))
        left_frame.columnconfigure(0, weight=1)
        
        # Configure rows to eliminate excessive vertical space
        left_frame.rowconfigure(0, weight=0)  # Image input - compact
        left_frame.rowconfigure(1, weight=0)  # Settings - compact horizontal
        left_frame.rowconfigure(2, weight=0)  # Prompt section - compact
        left_frame.rowconfigure(3, weight=0)  # Primary action - prominent
        left_frame.rowconfigure(4, weight=1)  # Spacer
        left_frame.rowconfigure(5, weight=0)  # Secondary actions - bottom
        
        # 1. COMPACT IMAGE INPUT
        self.setup_compact_image_input(left_frame)
        
        # 2. HORIZONTAL SETTINGS (save vertical space)
        self.setup_horizontal_settings(left_frame)
        
        # 3. PROMPT SECTION (slightly reduced height)
        self.setup_compact_prompt_section(left_frame)
        
        # 4. PRIMARY ACTION (right under prompt - key improvement!)
        self.setup_primary_action(left_frame)
        
        # 5. SPACER
        spacer = ttk.Frame(left_frame)
        spacer.grid(row=4, column=0, sticky="nsew")
        
        # 6. SECONDARY ACTIONS (at bottom)
        self.setup_secondary_actions(left_frame)
    
    def setup_compact_image_input(self, parent):
        """Very compact image input section"""
        input_frame = ttk.LabelFrame(parent, text="📥 Input Image", padding="6")
        input_frame.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        input_frame.columnconfigure(1, weight=1)
        
        # Thumbnail + Info in one row
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
        
        # Setup drag and drop
        self.setup_drag_drop()
        
        # Image info (compact)
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
        
        # Browse button (small)
        browse_btn = ttk.Button(
            info_frame,
            text="Browse",
            command=self.browse_image,
            width=8
        )
        browse_btn.pack(side=tk.RIGHT)
    
    def setup_horizontal_settings(self, parent):
        """Horizontal settings layout to save vertical space"""
        settings_frame = ttk.LabelFrame(parent, text="⚙️ Settings", padding="6")
        settings_frame.grid(row=1, column=0, sticky="ew", pady=(0, 8))
        settings_frame.columnconfigure(1, weight=1)
        settings_frame.columnconfigure(3, weight=1)
        
        # Row 1: Guidance Scale + Seed
        ttk.Label(settings_frame, text="Guidance:", font=('Arial', 9)).grid(
            row=0, column=0, sticky="w", padx=(0, 4)
        )
        
        self.guidance_var = tk.StringVar(value="0.5")
        # Also create guidance_scale_var for compatibility with tab
        self.guidance_scale_var = self.guidance_var
        guidance_combo = ttk.Combobox(
            settings_frame,
            textvariable=self.guidance_var,
            values=["0.1", "0.2", "0.3", "0.4", "0.5", "0.6", "0.7", "0.8", "0.9", "1.0"],
            state="readonly",
            width=6,
            font=('Arial', 9)
        )
        guidance_combo.grid(row=0, column=1, sticky="w", padx=(0, 12))
        
        ttk.Label(settings_frame, text="Seed:", font=('Arial', 9)).grid(
            row=0, column=2, sticky="w", padx=(0, 4)
        )
        
        self.seed_var = tk.StringVar(value="-1")
        seed_entry = ttk.Entry(
            settings_frame,
            textvariable=self.seed_var,
            width=8,
            font=('Arial', 9)
        )
        seed_entry.grid(row=0, column=3, sticky="w")
        
        # Row 2: Additional settings if needed (format, quality, etc.)
        ttk.Label(settings_frame, text="Format:", font=('Arial', 9)).grid(
            row=1, column=0, sticky="w", padx=(0, 4), pady=(4, 0)
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
        format_combo.grid(row=1, column=1, sticky="w", pady=(4, 0))
    
    def setup_compact_prompt_section(self, parent):
        """Compact prompt section with preset management"""
        prompt_frame = ttk.LabelFrame(parent, text="✏️ Edit Instruction", padding="6")
        prompt_frame.grid(row=2, column=0, sticky="ew", pady=(0, 8))
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
        
        # Preset buttons (small)
        preset_btn_frame = ttk.Frame(preset_frame)
        preset_btn_frame.grid(row=0, column=1)
        
        ttk.Button(preset_btn_frame, text="💾", width=3, command=self.save_preset).pack(side=tk.LEFT, padx=1)
        ttk.Button(preset_btn_frame, text="🎲", width=3, command=self.load_sample).pack(side=tk.LEFT, padx=1)
        ttk.Button(preset_btn_frame, text="🤖", width=3, command=self.improve_with_ai).pack(side=tk.LEFT, padx=1)
        
        # Prompt text (reduced height - key improvement!)
        self.prompt_text = tk.Text(
            prompt_frame,
            height=4,  # Reduced from typical 6-8 lines
            wrap=tk.WORD,
            font=('Arial', 10),
            relief='solid',
            borderwidth=1
        )
        self.prompt_text.grid(row=1, column=0, sticky="ew", pady=(4, 0))
        
        # Placeholder text
        self.prompt_text.insert("1.0", "Describe the changes you want to make to the image...")
        self.prompt_text.bind("<FocusIn>", self.clear_placeholder)
        self.prompt_text.bind("<FocusOut>", self.add_placeholder)
    
    def setup_primary_action(self, parent):
        """Primary action button RIGHT under prompt - key UX improvement!"""
        action_frame = ttk.Frame(parent)
        action_frame.grid(row=3, column=0, sticky="ew", pady=8)
        action_frame.columnconfigure(0, weight=1)
        
        # PROMINENT primary action button
        self.primary_btn = ttk.Button(
            action_frame,
            text="✨ Apply SeedEdit",
            command=self.process_seededit,
            style='Accent.TButton'  # Make it stand out
        )
        self.primary_btn.grid(row=0, column=0, sticky="ew")
        
        # Status indicator right below
        self.status_label = ttk.Label(
            action_frame,
            text="Ready to edit",
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
    
    def setup_secondary_actions(self, parent):
        """Secondary actions at bottom"""
        secondary_frame = ttk.LabelFrame(parent, text="🔧 Tools", padding="6")
        secondary_frame.grid(row=5, column=0, sticky="ew")
        secondary_frame.columnconfigure(0, weight=1)
        secondary_frame.columnconfigure(1, weight=1)
        
        # Row 1: Clear and Load
        ttk.Button(
            secondary_frame,
            text="🧹 Clear All",
            command=self.clear_all,
            width=12
        ).grid(row=0, column=0, sticky="ew", padx=(0, 2), pady=1)
        
        ttk.Button(
            secondary_frame,
            text="📂 Load Result",
            command=self.load_result,
            width=12
        ).grid(row=0, column=1, sticky="ew", padx=(2, 0), pady=1)
        
        # Row 2: Save and Export
        ttk.Button(
            secondary_frame,
            text="💾 Save Result",
            command=self.save_result,
            width=12
        ).grid(row=1, column=0, sticky="ew", padx=(0, 2), pady=1)
        
        ttk.Button(
            secondary_frame,
            text="📤 Export",
            command=self.export_result,
            width=12
        ).grid(row=1, column=1, sticky="ew", padx=(2, 0), pady=1)
    
    def setup_right_column(self, parent):
        """Setup right column with dynamic image scaling and comparison"""
        right_frame = ttk.Frame(parent, padding="4")
        right_frame.grid(row=0, column=1, sticky="nsew", padx=(4, 0))
        right_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(1, weight=1)
        
        # Control bar for image viewing options
        self.setup_image_controls(right_frame)
        
        # Main image display area
        self.setup_image_display(right_frame)
    
    def setup_image_controls(self, parent):
        """Setup image viewing controls"""
        controls_frame = ttk.Frame(parent)
        controls_frame.grid(row=0, column=0, sticky="ew", pady=(0, 4))
        controls_frame.columnconfigure(2, weight=1)  # Spacer
        
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
            text="✨ Result",
            command=lambda: self.set_view_mode("result"),
            width=10
        )
        self.view_result_btn.grid(row=0, column=1, padx=(0, 8))
        
        # Comparison mode toggle
        self.comparison_btn = ttk.Button(
            controls_frame,
            text="⚖️ Compare",
            command=self.toggle_comparison_mode,
            width=10
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
            values=["Fit", "50%", "100%", "150%", "200%"],
            state="readonly",
            width=6,
            font=('Arial', 9)
        )
        zoom_combo.pack(side=tk.LEFT, padx=(2, 0))
        zoom_combo.bind('<<ComboboxSelected>>', self.on_zoom_changed)
    
    def setup_image_display(self, parent):
        """Setup main image display with minimal margins and dynamic scaling"""
        display_frame = ttk.Frame(parent)
        display_frame.grid(row=1, column=0, sticky="nsew")
        display_frame.columnconfigure(0, weight=1)
        display_frame.rowconfigure(0, weight=1)
        
        # Canvas with minimal padding
        self.image_canvas = tk.Canvas(
            display_frame,
            bg='white',
            highlightthickness=0,  # Remove border
            relief='flat'
        )
        self.image_canvas.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)  # Minimal margins
        
        # Scrollbars for large images
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
            250, 200,
            text="Select an image to start editing\n\nDrag & drop supported",
            font=('Arial', 14),
            fill='#888',
            justify=tk.CENTER
        )
    
    def set_view_mode(self, mode):
        """Set image viewing mode"""
        self.current_view_mode = mode
        
        # Update button states using text indicators
        if mode == "original":
            self.view_original_btn.config(text="📥 Original ✓")
            self.view_result_btn.config(text="✨ Result")
            if self.selected_image_path:
                self.display_image(self.selected_image_path)
        elif mode == "result":
            self.view_result_btn.config(text="✨ Result ✓")
            self.view_original_btn.config(text="📥 Original")
            if self.result_image_path:
                self.display_image(self.result_image_path)
        
        self.comparison_btn.config(text="🔄 Compare")
    
    def toggle_comparison_mode(self):
        """Toggle comparison mode (side-by-side or overlay)"""
        if not self.selected_image_path or not self.result_image_path:
            self.status_label.config(text="Need both images for comparison", foreground="orange")
            return
        
        self.comparison_btn.config(text="🔄 Compare ✓")
        self.view_original_btn.config(text="📥 Original")
        self.view_result_btn.config(text="✨ Result")
        
        # Show side-by-side comparison
        self.display_comparison()
    
    def setup_drag_drop(self):
        """Setup drag and drop functionality"""
        if DND_AVAILABLE:
            try:
                # Enable drag and drop on thumbnail (if it exists)
                if hasattr(self, 'thumbnail_label'):
                    self.thumbnail_label.drop_target_register(DND_FILES)
                    self.thumbnail_label.dnd_bind('<<Drop>>', self.on_drop)
                    self.thumbnail_label.dnd_bind('<<DragEnter>>', self.on_drag_enter)
                    self.thumbnail_label.dnd_bind('<<DragLeave>>', self.on_drag_leave)
                
                # Enable drag and drop on image info area (if it exists)
                if hasattr(self, 'image_name_label'):
                    self.image_name_label.drop_target_register(DND_FILES)
                    self.image_name_label.dnd_bind('<<Drop>>', self.on_drop)
                    self.image_name_label.dnd_bind('<<DragEnter>>', self.on_drag_enter)
                    self.image_name_label.dnd_bind('<<DragLeave>>', self.on_drag_leave)
                
            except Exception as e:
                print(f"Drag and drop setup failed: {e}")
    
    def on_drop(self, event):
        """Handle drag and drop"""
        # Try parent tab's on_drop first
        if self.tab_instance and hasattr(self.tab_instance, 'on_drop'):
            self.tab_instance.on_drop(event)
        else:
            # Fallback to direct handling
            from utils.utils import parse_drag_drop_data, validate_image_file, show_error
            
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
            
            # Load the image
            self.load_image(file_path)
    
    def on_drag_enter(self, event):
        """Handle drag enter"""
        self.thumbnail_label.config(bg='#e0e0e0')
    
    def on_drag_leave(self, event):
        """Handle drag leave"""
        self.thumbnail_label.config(bg='#f5f5f5')
    
    def display_image(self, image_path, position="center"):
        """Display image with dynamic scaling and minimal margins"""
        try:
            # Clear canvas
            self.image_canvas.delete("all")
            
            # Load image
            img = Image.open(image_path)
            
            # Get canvas dimensions
            canvas_width = self.image_canvas.winfo_width()
            canvas_height = self.image_canvas.winfo_height()
            
            if canvas_width <= 1:  # Not initialized yet
                canvas_width = 500
                canvas_height = 400
            
            # Calculate scaling based on zoom setting
            zoom_value = self.zoom_var.get()
            if zoom_value == "Fit":
                # Fit to canvas with minimal margins (key improvement!)
                scale_factor = min(
                    (canvas_width - 10) / img.width,  # Minimal 5px margin each side
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
            self.image_canvas.image = photo  # Keep reference
            
            # Update scroll region
            self.image_canvas.configure(scrollregion=self.image_canvas.bbox("all"))
            
        except Exception as e:
            self.image_canvas.delete("all")
            self.image_canvas.create_text(
                250, 200,
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
            result_img = Image.open(self.result_image_path)
            
            # Get canvas dimensions
            canvas_width = self.image_canvas.winfo_width()
            canvas_height = self.image_canvas.winfo_height()
            
            if canvas_width <= 1:
                canvas_width = 500
                canvas_height = 400
            
            # Calculate scaling for side-by-side display
            available_width = (canvas_width - 15) // 2  # Split in half with margins
            available_height = canvas_height - 10
            
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
            y = max(5, (canvas_height - new_height) // 2)
            
            # Display images
            self.image_canvas.create_image(left_x, y, anchor=tk.NW, image=original_photo)
            self.image_canvas.create_image(right_x, y, anchor=tk.NW, image=result_photo)
            
            # Add labels
            self.image_canvas.create_text(left_x + new_width//2, y - 15, text="Original", 
                                        font=('Arial', 10, 'bold'), fill='blue')
            self.image_canvas.create_text(right_x + new_width//2, y - 15, text="Result", 
                                        font=('Arial', 10, 'bold'), fill='green')
            
            # Keep references
            self.image_canvas.original_photo = original_photo
            self.image_canvas.result_photo = result_photo
            
            # Update scroll region
            self.image_canvas.configure(scrollregion=self.image_canvas.bbox("all"))
            
        except Exception as e:
            self.status_label.config(text=f"Comparison error: {str(e)}", foreground="red")
    
    # Event handlers
    def browse_image(self):
        """Browse for image file"""
        from tkinter import filedialog
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
            
            # Display in main canvas
            self.set_view_mode("original")
            
        except Exception as e:
            self.status_label.config(text=f"Error loading image: {str(e)}", foreground="red")
    
    def process_seededit(self):
        """Process with SeedEdit - delegates to tab instance"""
        if self.tab_instance and hasattr(self.tab_instance, 'process_task'):
            # Call the tab's real process method
            self.tab_instance.process_task()
        else:
            # Fallback to basic validation
            if not self.selected_image_path:
                self.status_label.config(text="Please select an image first", foreground="red")
                return
            
            prompt = self.prompt_text.get("1.0", tk.END).strip()
            if not prompt or prompt == "Describe the changes you want to make to the image...":
                self.status_label.config(text="Please enter edit instructions", foreground="red")
                return
            
            self.status_label.config(text="No processing method available", foreground="orange")
    
    def after_processing(self):
        """Called after processing completes"""
        # Hide progress
        self.progress_bar.stop()
        self.progress_bar.grid_remove()
        self.primary_btn.config(state='normal', text="✨ Apply SeedEdit")
        self.status_label.config(text="✅ Processing complete!", foreground="green")
        
        # Enable result view
        self.view_result_btn.config(state='normal')
        self.comparison_btn.config(state='normal')
    
    # Utility methods
    def clear_placeholder(self, event):
        current_text = self.prompt_text.get("1.0", tk.END).strip()
        if current_text == "Describe the changes you want to make to the image...":
            self.prompt_text.delete("1.0", tk.END)
    
    def add_placeholder(self, event):
        current_text = self.prompt_text.get("1.0", tk.END).strip()
        if not current_text:
            self.prompt_text.insert("1.0", "Describe the changes you want to make to the image...")
    
    def on_canvas_configure(self, event):
        """Handle canvas resize"""
        if hasattr(self, 'current_view_mode'):
            if self.current_view_mode == "original" and self.selected_image_path:
                self.display_image(self.selected_image_path)
            elif self.current_view_mode == "result" and self.result_image_path:
                self.display_image(self.result_image_path)
    
    def on_canvas_click(self, event):
        """Handle canvas click for comparison toggle"""
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
    
    def update_result_image(self, image_url):
        """Update the result image display with downloaded image"""
        try:
            import requests
            import tempfile
            
            # Download image from URL
            response = requests.get(image_url)
            response.raise_for_status()
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
                tmp_file.write(response.content)
                temp_path = tmp_file.name
            
            # Load image and create a copy, then clean up temp file
            with Image.open(temp_path) as temp_image:
                image = temp_image.copy()
            os.unlink(temp_path)  # Clean up temp file
            
            # Save result image path
            self.result_image_path = temp_path.replace('.png', '_result.png')
            image.save(self.result_image_path)
            
            # Update display
            self.set_view_mode("result")
            self.display_image(self.result_image_path)
            
            # Update status
            self.status_label.config(text="✅ Result image loaded successfully!", foreground="green")
            
            return True
            
        except Exception as e:
            self.status_label.config(text=f"❌ Error loading result: {str(e)}", foreground="red")
            return False
    
    # Placeholder methods for functionality
    def load_preset(self, event=None): pass
    def save_preset(self): pass
    def load_sample(self): pass
    def improve_with_ai(self): pass
    def clear_all(self): pass
    def load_result(self): pass
    def save_result(self): pass
    def export_result(self): pass


"""
KEY IMPROVEMENTS IMPLEMENTED:

✅ 1. TWO BALANCED COLUMNS instead of vertical stacking
   - Left: Controls (weight=1, 350px min)
   - Right: Images (weight=2, 500px min)

✅ 2. PRIMARY ACTION BUTTON right under prompt
   - "Apply SeedEdit" immediately follows edit instructions
   - No scrolling needed to reach the main action

✅ 3. DYNAMIC IMAGE SCALING with minimal margins
   - Images scale to fill canvas with only 5px margins
   - "Fit" mode uses available space efficiently
   - No large white margins around previews

✅ 4. SIDE-BY-SIDE COMPARISON instead of toggling tabs
   - Compare button shows both images simultaneously
   - Clear labels ("Original" vs "Result")
   - Better for quick comparison

✅ 5. HORIZONTAL SETTINGS layout
   - Guidance Scale + Seed in one row
   - Format + other settings in second row
   - Saves significant vertical space

✅ 6. NO WASTED SPACE between columns
   - 2-column grid with proper weights
   - Right column gets 2x the space for images
   - Every pixel serves a purpose

✅ 7. COMPACT PROMPT section (4 lines instead of 6-8)
   - Still functional but saves vertical space
   - Preset management integrated cleanly

✅ 8. LOGICAL FLOW in left column:
   Input → Settings → Prompt → PRIMARY ACTION → Tools

This layout eliminates scrolling, maximizes image display space, 
and puts the most important action (Apply SeedEdit) right where 
the user expects it after typing their prompt!
"""
