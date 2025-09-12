"""
Optimized Image Upscaler Tab Layout - Streamlined for Simple Workflow
1. Remove unnecessary prompts section
2. Compact settings with immediate action button
3. Clean status console below upscale button
4. Large dynamic result preview
5. Simple 2-column layout optimized for upscaling workflow
"""

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os
import time
from .unified_status_console import UnifiedStatusConsole
from .keyboard_manager import KeyboardManager


class OptimizedUpscalerLayout:
    """Streamlined layout specifically designed for image upscaling workflow"""
    
    def __init__(self, parent_frame):
        self.parent_frame = parent_frame
        self.selected_image_path = None
        self.result_image_path = None
        
        # Settings variables
        self.upscale_factor_var = tk.StringVar(value="2x")
        self.creativity_var = tk.DoubleVar(value=0.35)
        self.format_var = tk.StringVar(value="png")
        
        # Processing tracking
        self.start_time = None
        
        self.setup_layout()
        self.setup_enhanced_features()
    
    def setup_layout(self):
        """Setup streamlined 2-column layout optimized for upscaling"""
        
        # Main container
        main_container = ttk.Frame(self.parent_frame)
        main_container.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        
        # Configure grid - 2 columns optimized for upscaling workflow
        main_container.columnconfigure(0, weight=1, minsize=320)  # Left: Controls (smaller than other tabs)
        main_container.columnconfigure(1, weight=2, minsize=480)  # Right: Large result view
        main_container.rowconfigure(0, weight=1)
        
        # Left Column - Streamlined Controls
        self.setup_left_column(main_container)
        
        # Right Column - Large Result Display
        self.setup_right_column(main_container)
    
    def setup_left_column(self, parent):
        """Setup streamlined left column - no prompts, just essentials"""
        left_frame = ttk.Frame(parent, relief='groove', borderwidth=1, padding="8")
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 4))
        left_frame.columnconfigure(0, weight=1)
        
        # Configure rows for streamlined layout
        left_frame.rowconfigure(0, weight=0)  # Image input - compact
        left_frame.rowconfigure(1, weight=0)  # Settings - compact
        left_frame.rowconfigure(2, weight=0)  # Primary action - prominent
        left_frame.rowconfigure(3, weight=0)  # Status console - fixed height
        left_frame.rowconfigure(4, weight=1)  # Spacer
        left_frame.rowconfigure(5, weight=0)  # Tools - bottom
        
        # 1. COMPACT IMAGE INPUT
        self.setup_image_input(left_frame)
        
        # 2. STREAMLINED SETTINGS (no prompts!)
        self.setup_upscaler_settings(left_frame)
        
        # 3. PRIMARY ACTION (right after settings!)
        self.setup_primary_action(left_frame)
        
        # 4. STATUS CONSOLE (clean log-style display)
        self.setup_status_console(left_frame)
        
        # 5. SPACER
        spacer = ttk.Frame(left_frame)
        spacer.grid(row=4, column=0, sticky="nsew")
        
        # 6. TOOLS (minimal)
        self.setup_tools_section(left_frame)
    
    def setup_image_input(self, parent):
        """Compact image input section"""
        input_frame = ttk.LabelFrame(parent, text="📥 Input Image", padding="6")
        input_frame.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        input_frame.columnconfigure(1, weight=1)
        
        # Thumbnail + Info layout
        self.thumbnail_label = tk.Label(
            input_frame,
            text="📁",
            width=10, height=5,
            bg='#f5f5f5',
            relief='solid',
            borderwidth=1,
            cursor="hand2",
            font=('Arial', 12)
        )
        self.thumbnail_label.grid(row=0, column=0, padx=(0, 8), rowspan=3)
        self.thumbnail_label.bind("<Button-1>", lambda e: self.browse_image())
        
        # Image info
        self.image_name_label = ttk.Label(
            input_frame,
            text="No image selected",
            font=('Arial', 10, 'bold'),
            foreground="gray"
        )
        self.image_name_label.grid(row=0, column=1, sticky="w")
        
        self.image_size_label = ttk.Label(
            input_frame,
            text="",
            font=('Arial', 9),
            foreground="gray"
        )
        self.image_size_label.grid(row=1, column=1, sticky="w")
        
        # Browse button
        browse_btn = ttk.Button(
            input_frame,
            text="📁 Browse Image",
            command=self.browse_image,
            width=15
        )
        browse_btn.grid(row=2, column=1, sticky="w", pady=(4, 0))
    
    def setup_upscaler_settings(self, parent):
        """Streamlined settings - only what's needed for upscaling"""
        settings_frame = ttk.LabelFrame(parent, text="⚙️ Upscale Settings", padding="6")
        settings_frame.grid(row=1, column=0, sticky="ew", pady=(0, 8))
        settings_frame.columnconfigure(1, weight=1)
        
        # Row 1: Upscale Factor
        ttk.Label(settings_frame, text="Upscale Factor:", font=('Arial', 9, 'bold')).grid(
            row=0, column=0, sticky="w", pady=(0, 4)
        )
        
        factor_combo = ttk.Combobox(
            settings_frame,
            textvariable=self.upscale_factor_var,
            values=["2x", "4x", "8x", "16x"],
            state="readonly",
            width=10,
            font=('Arial', 10)
        )
        factor_combo.grid(row=0, column=1, sticky="w", pady=(0, 4))
        factor_combo.bind('<<ComboboxSelected>>', self.on_factor_changed)
        
        # Row 2: Creativity Slider
        ttk.Label(settings_frame, text="Creativity:", font=('Arial', 9, 'bold')).grid(
            row=1, column=0, sticky="w", pady=(4, 4)
        )
        
        creativity_frame = ttk.Frame(settings_frame)
        creativity_frame.grid(row=1, column=1, sticky="ew", pady=(4, 4))
        creativity_frame.columnconfigure(0, weight=1)
        
        self.creativity_scale = ttk.Scale(
            creativity_frame,
            from_=0.0, to=1.0,
            variable=self.creativity_var,
            orient=tk.HORIZONTAL,
            length=120,
            command=self.on_creativity_changed
        )
        self.creativity_scale.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        
        self.creativity_label = ttk.Label(
            creativity_frame,
            text="0.35",
            font=('Arial', 9),
            width=6
        )
        self.creativity_label.grid(row=0, column=1)
        
        # Row 3: Output Format
        ttk.Label(settings_frame, text="Output Format:", font=('Arial', 9, 'bold')).grid(
            row=2, column=0, sticky="w", pady=(4, 0)
        )
        
        format_combo = ttk.Combobox(
            settings_frame,
            textvariable=self.format_var,
            values=["png", "jpg", "webp"],
            state="readonly",
            width=10,
            font=('Arial', 10)
        )
        format_combo.grid(row=2, column=1, sticky="w", pady=(4, 0))
        
        # Expected output size info
        self.output_info_label = ttk.Label(
            settings_frame,
            text="Select an image to see output size",
            font=('Arial', 8),
            foreground="#666"
        )
        self.output_info_label.grid(row=3, column=0, columnspan=2, sticky="w", pady=(8, 0))
    
    def setup_primary_action(self, parent):
        """Primary action - immediately after settings"""
        action_frame = ttk.Frame(parent)
        action_frame.grid(row=2, column=0, sticky="ew", pady=8)
        action_frame.columnconfigure(0, weight=1)
        
        # PROMINENT upscale button
        self.upscale_btn = ttk.Button(
            action_frame,
            text="🔍 Upscale Image",
            command=self.process_upscale,
            style='Accent.TButton'
        )
        self.upscale_btn.grid(row=0, column=0, sticky="ew")
        
        # Progress bar (hidden by default)
        self.progress_bar = ttk.Progressbar(
            action_frame,
            mode='indeterminate'
        )
        # Don't grid it yet - only show when processing
    
    def setup_status_console(self, parent):
        """Clean status console - log-style display"""
        console_frame = ttk.LabelFrame(parent, text="📊 Status", padding="6")
        console_frame.grid(row=3, column=0, sticky="ew", pady=(0, 8))
        console_frame.columnconfigure(0, weight=1)
        
        # Status text area (read-only, console-style)
        self.status_text = tk.Text(
            console_frame,
            height=4,
            width=1,
            font=('Courier', 9),
            bg='#f8f8f8',
            fg='#333',
            relief='flat',
            borderwidth=0,
            state=tk.DISABLED,
            wrap=tk.WORD
        )
        self.status_text.grid(row=0, column=0, sticky="ew")
        
        # Add initial status
        self.log_status("Ready to upscale images")
    
    def setup_tools_section(self, parent):
        """Minimal tools section"""
        tools_frame = ttk.LabelFrame(parent, text="🔧 Tools", padding="4")
        tools_frame.grid(row=5, column=0, sticky="ew")
        tools_frame.columnconfigure(0, weight=1)
        tools_frame.columnconfigure(1, weight=1)
        
        # Clear and Load buttons
        ttk.Button(
            tools_frame,
            text="🧹 Clear",
            command=self.clear_all,
            width=10
        ).grid(row=0, column=0, sticky="ew", padx=(0, 1), pady=1)
        
        ttk.Button(
            tools_frame,
            text="📂 Load",
            command=self.load_image_dialog,
            width=10
        ).grid(row=0, column=1, sticky="ew", padx=(1, 0), pady=1)
    
    def setup_right_column(self, parent):
        """Setup right column with large result display"""
        right_frame = ttk.Frame(parent, relief='groove', borderwidth=1, padding="4")
        right_frame.grid(row=0, column=1, sticky="nsew", padx=(4, 0))
        right_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(1, weight=1)
        
        # Simple view controls
        self.setup_view_controls(right_frame)
        
        # Large result display
        self.setup_result_display(right_frame)
    
    def setup_view_controls(self, parent):
        """Simple view controls for upscaler"""
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
            text="🔍 Upscaled",
            command=lambda: self.set_view_mode("result"),
            width=10
        )
        self.view_result_btn.grid(row=0, column=1, padx=(0, 8))
        
        # Zoom control
        zoom_frame = ttk.Frame(controls_frame)
        zoom_frame.grid(row=0, column=3, padx=(8, 0))
        
        ttk.Label(zoom_frame, text="Zoom:", font=('Arial', 9)).pack(side=tk.LEFT)
        
        self.zoom_var = tk.StringVar(value="Fit")
        zoom_combo = ttk.Combobox(
            zoom_frame,
            textvariable=self.zoom_var,
            values=["Fit", "25%", "50%", "100%", "200%", "400%"],
            state="readonly",
            width=6,
            font=('Arial', 9)
        )
        zoom_combo.pack(side=tk.LEFT, padx=(2, 0))
        zoom_combo.bind('<<ComboboxSelected>>', self.on_zoom_changed)
    
    def setup_result_display(self, parent):
        """Large result display optimized for upscaling preview"""
        display_frame = ttk.Frame(parent)
        display_frame.grid(row=1, column=0, sticky="nsew")
        display_frame.columnconfigure(0, weight=1)
        display_frame.rowconfigure(0, weight=1)
        
        # Canvas for image display
        self.result_canvas = tk.Canvas(
            display_frame,
            bg='white',
            highlightthickness=0,
            relief='flat'
        )
        self.result_canvas.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)
        
        # Scrollbars for large upscaled images
        v_scrollbar = ttk.Scrollbar(display_frame, orient=tk.VERTICAL, command=self.result_canvas.yview)
        h_scrollbar = ttk.Scrollbar(display_frame, orient=tk.HORIZONTAL, command=self.result_canvas.xview)
        
        self.result_canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        # Bind events
        self.result_canvas.bind('<Configure>', self.on_canvas_configure)
        self.result_canvas.bind('<MouseWheel>', self.on_mouse_wheel)
        
        # Default message
        self.show_default_message()
    
    def show_default_message(self):
        """Show default message when no image is loaded"""
        self.result_canvas.delete("all")
        self.result_canvas.create_text(
            240, 200,
            text="Select an image to upscale\n\nSupported formats: PNG, JPG, WebP\nMaximum input size: 4K",
            font=('Arial', 12),
            fill='#888',
            justify=tk.CENTER
        )
    
    # Event handlers and processing methods
    def browse_image(self):
        """Browse for image file"""
        from tkinter import filedialog
        file_path = filedialog.askopenfilename(
            title="Select Image to Upscale",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.gif *.bmp *.webp"),
                ("PNG files", "*.png"),
                ("JPEG files", "*.jpg *.jpeg"),
                ("WebP files", "*.webp"),
                ("All files", "*.*")
            ]
        )
        if file_path:
            self.load_image(file_path)
    
    def load_image_dialog(self):
        """Alternative load method"""
        self.browse_image()
    
    def load_image(self, image_path):
        """Load and display input image"""
        self.selected_image_path = image_path
        
        try:
            # Update thumbnail
            img = Image.open(image_path)
            img.thumbnail((60, 60), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            
            self.thumbnail_label.config(image=photo, text="")
            self.thumbnail_label.image = photo
            
            # Update info
            filename = os.path.basename(image_path)
            if len(filename) > 25:
                filename = filename[:22] + "..."
            self.image_name_label.config(text=filename, foreground="black")
            
            # Get image size and update info
            original = Image.open(image_path)
            self.image_size_label.config(text=f"{original.width}×{original.height}")
            
            # Update expected output size
            self.update_output_info()
            
            # Display in result canvas
            self.set_view_mode("original")
            
            # Enable upscale button
            self.upscale_btn.config(state='normal')
            
            # Log status
            self.log_status(f"✅ Loaded: {filename} ({original.width}×{original.height})")
            
        except Exception as e:
            self.log_status(f"❌ Error loading image: {str(e)}")
            self.upscale_btn.config(state='disabled')
    
    def update_output_info(self):
        """Update expected output size information"""
        if not self.selected_image_path:
            return
        
        try:
            img = Image.open(self.selected_image_path)
            factor = int(self.upscale_factor_var.get().rstrip('x'))
            new_width = img.width * factor
            new_height = img.height * factor
            
            # Calculate file size estimate
            estimated_mb = (new_width * new_height * 3) / (1024 * 1024)  # Rough RGB estimate
            
            self.output_info_label.config(
                text=f"Output will be: {new_width}×{new_height} (~{estimated_mb:.1f}MB)",
                foreground="#333"
            )
        except:
            pass
    
    def process_upscale(self):
        """Process image upscaling"""
        if not self.selected_image_path:
            self.log_status("❌ Please select an image first")
            return
        
        # Validate settings
        factor = self.upscale_factor_var.get()
        creativity = self.creativity_var.get()
        output_format = self.format_var.get()
        
        # Start processing
        self.start_time = time.time()
        
        # Show processing state
        self.upscale_btn.config(state='disabled', text="Upscaling...")
        self.progress_bar.grid(row=1, column=0, sticky="ew", pady=(4, 0))
        self.progress_bar.start()
        
        # Log start
        self.log_status(f"🔍 Starting upscale: {factor}, creativity={creativity:.2f}")
        
        # Here you would call your actual upscaling API
        # For demo, simulate processing
        self.parent_frame.after(3000, self.after_upscaling)  # Simulate 3 second processing
    
    def after_upscaling(self):
        """Called after upscaling completes"""
        # Calculate processing time
        processing_time = time.time() - self.start_time if self.start_time else 0
        
        # Hide progress
        self.progress_bar.stop()
        self.progress_bar.grid_remove()
        self.upscale_btn.config(state='normal', text="🔍 Upscale Image")
        
        # Log completion
        self.log_status(f"✅ Image upscaled successfully in {processing_time:.1f}s")
        self.log_status(f"📁 Result saved to WaveSpeed_Results/Upscaler/")
        
        # Enable result view
        self.view_result_btn.config(state='normal')
        
        # Switch to result view
        self.set_view_mode("result")
    
    def set_view_mode(self, mode):
        """Set viewing mode"""
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
            else:
                # Show placeholder for result
                self.result_canvas.delete("all")
                self.result_canvas.create_text(
                    240, 200,
                    text="Result will appear here after upscaling\n\nClick 'Upscale Image' to process",
                    font=('Arial', 12),
                    fill='#888',
                    justify=tk.CENTER
                )
    
    def display_image(self, image_path):
        """Display image with proper scaling"""
        try:
            self.result_canvas.delete("all")
            
            img = Image.open(image_path)
            canvas_width = self.result_canvas.winfo_width()
            canvas_height = self.result_canvas.winfo_height()
            
            if canvas_width <= 1:
                canvas_width = 480
                canvas_height = 400
            
            # Calculate scaling
            zoom_value = self.zoom_var.get()
            if zoom_value == "Fit":
                scale_factor = min(
                    (canvas_width - 10) / img.width,
                    (canvas_height - 10) / img.height
                )
            else:
                scale_factor = float(zoom_value.rstrip('%')) / 100
            
            # Resize image
            new_width = int(img.width * scale_factor)
            new_height = int(img.height * scale_factor)
            img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Create PhotoImage
            photo = ImageTk.PhotoImage(img_resized)
            
            # Center image
            x = max(5, (canvas_width - new_width) // 2)
            y = max(5, (canvas_height - new_height) // 2)
            
            # Display image
            self.result_canvas.create_image(x, y, anchor=tk.NW, image=photo)
            self.result_canvas.image = photo
            
            # Update scroll region
            self.result_canvas.configure(scrollregion=self.result_canvas.bbox("all"))
            
        except Exception as e:
            self.result_canvas.delete("all")
            self.result_canvas.create_text(
                240, 200,
                text=f"Error displaying image:\n{str(e)}",
                font=('Arial', 12),
                fill='red',
                justify=tk.CENTER
            )
    
    def log_status(self, message):
        """Add message to status console"""
        timestamp = time.strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}\n"
        
        self.status_text.config(state=tk.NORMAL)
        self.status_text.insert(tk.END, formatted_message)
        self.status_text.see(tk.END)
        self.status_text.config(state=tk.DISABLED)
    
    # Event handlers
    def on_factor_changed(self, event=None):
        """Handle upscale factor change"""
        self.update_output_info()
        factor = self.upscale_factor_var.get()
        self.log_status(f"⚙️ Upscale factor set to {factor}")
    
    def on_creativity_changed(self, value):
        """Handle creativity slider change"""
        creativity = float(value)
        self.creativity_label.config(text=f"{creativity:.2f}")
    
    def on_zoom_changed(self, event=None):
        """Handle zoom change"""
        if hasattr(self, 'current_view_mode'):
            if self.current_view_mode == "original" and self.selected_image_path:
                self.display_image(self.selected_image_path)
            elif self.current_view_mode == "result" and self.result_image_path:
                self.display_image(self.result_image_path)
    
    def on_canvas_configure(self, event):
        """Handle canvas resize"""
        if hasattr(self, 'current_view_mode'):
            if self.current_view_mode == "original" and self.selected_image_path:
                self.display_image(self.selected_image_path)
            elif self.current_view_mode == "result" and self.result_image_path:
                self.display_image(self.result_image_path)
    
    def on_mouse_wheel(self, event):
        """Handle mouse wheel for canvas scrolling"""
        self.result_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def setup_enhanced_features(self):
        """Setup status console and keyboard shortcuts integration"""
        # Initialize keyboard manager for this layout
        self.keyboard_manager = KeyboardManager(self.parent_frame, "Image Upscaler")
        
        # Register primary action
        self.keyboard_manager.register_primary_action(self.process_upscale, self.upscale_btn)
        
        # Register file operations
        self.keyboard_manager.register_file_actions(
            self.browse_image,
            self.clear_all
        )
    
    def clear_all(self):
        """Clear all data"""
        self.selected_image_path = None
        self.result_image_path = None
        
        # Reset thumbnail
        self.thumbnail_label.config(image="", text="📁")
        self.thumbnail_label.image = None
        
        # Reset info
        self.image_name_label.config(text="No image selected", foreground="gray")
        self.image_size_label.config(text="")
        self.output_info_label.config(text="Select an image to see output size")
        
        # Reset UI state
        self.upscale_btn.config(state='disabled')
        self.view_result_btn.config(state='disabled')
        
        # Clear canvas
        self.show_default_message()
        
        # Clear status
        self.status_text.config(state=tk.NORMAL)
        self.status_text.delete("1.0", tk.END)
        self.status_text.config(state=tk.DISABLED)
        self.log_status("Cleared all data")


"""
KEY IMPROVEMENTS FOR IMAGE UPSCALER:

✅ 1. STREAMLINED LAYOUT - No unnecessary elements
   - Removed prompts section entirely (not needed)
   - Compact 2-column layout optimized for upscaling workflow
   - Left column smaller (320px) since fewer controls needed

✅ 2. UPSCALE BUTTON immediately after settings
   - Natural flow: Select image → Choose settings → Click upscale
   - No scrolling needed to reach primary action
   - Prominent styling to make it stand out

✅ 3. CLEAN STATUS CONSOLE 
   - Console-style text area with timestamps
   - Shows processing time, file paths, errors
   - Much better than cramped status line

✅ 4. EFFICIENT SETTINGS PANEL
   - Only essential controls: Factor, Creativity, Format
   - Expected output size calculation and display
   - File size estimates to prevent surprises

✅ 5. LARGE RESULT DISPLAY
   - 2x weight for right column (more space for preview)
   - Proper zoom controls for inspecting upscaled details
   - Scrollbars for very large upscaled images

✅ 6. SMART FEEDBACK
   - Real-time output size calculation
   - Processing time tracking
   - Clear success/error messages with timestamps

✅ 7. MINIMAL TOOLS SECTION
   - Only Clear and Load buttons (simple workflow)
   - No cluttered bottom toolbar
   - Clean and purpose-built

This layout is specifically optimized for the upscaling workflow:
Select → Configure → Process → Review

Much cleaner than forcing it into a prompt-based layout!
The status console provides professional feedback without clutter.
"""
