"""
Optimized SeedDance Pro Tab Layout - Streamlined for Dance/Motion Videos
1. Cleaner than Wan 2.2 (no negative prompts)
2. Generate button immediately after video prompt
3. Collapsible saved prompts (saves space)
4. Large video player optimized for motion preview
5. Dance/motion specific settings
6. Seamless prompt → generate → preview workflow
"""

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os
import time
from .unified_status_console import UnifiedStatusConsole
from .keyboard_manager import KeyboardManager


class OptimizedSeedDanceLayout:
    """Streamlined layout specifically designed for dance/motion video generation"""
    
    def __init__(self, parent_frame):
        self.parent_frame = parent_frame
        self.selected_image_path = None
        self.result_video_path = None
        
        # Settings variables
        self.duration_var = tk.StringVar(value="3s")
        self.resolution_var = tk.StringVar(value="1024x576")
        self.camera_fixed_var = tk.BooleanVar(value=True)
        self.seed_var = tk.StringVar(value="-1")
        self.saved_prompts_expanded = False
        
        # Processing tracking
        self.start_time = None
        
        self.setup_layout()
        self.setup_enhanced_features()
    
    def setup_layout(self):
        """Setup streamlined 2-column layout for dance video generation"""
        
        # Main container
        main_container = ttk.Frame(self.parent_frame)
        main_container.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        
        # Configure grid - 2 columns optimized for dance video workflow
        main_container.columnconfigure(0, weight=1, minsize=360)  # Left: Controls (slightly smaller)
        main_container.columnconfigure(1, weight=2, minsize=540)  # Right: Large video player
        main_container.rowconfigure(0, weight=1)
        main_container.rowconfigure(1, weight=0)  # Bottom toolbar
        
        # Left Column - Dance Video Controls
        self.setup_left_column(main_container)
        
        # Right Column - Large Video Player  
        self.setup_right_column(main_container)
        
        # Bottom Toolbar - Video Playback Controls
        self.setup_bottom_toolbar(main_container)
    
    def setup_left_column(self, parent):
        """Setup streamlined left column for dance video workflow"""
        left_frame = ttk.Frame(parent, relief='groove', borderwidth=1, padding="8")
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 4))
        left_frame.columnconfigure(0, weight=1)
        
        # Configure rows for optimal dance video workflow
        left_frame.rowconfigure(0, weight=0)  # Image input - compact
        left_frame.rowconfigure(1, weight=0)  # Settings - compact horizontal
        left_frame.rowconfigure(2, weight=0)  # Video prompt - moderate size
        left_frame.rowconfigure(3, weight=0)  # Primary action - prominent
        left_frame.rowconfigure(4, weight=0)  # Collapsible saved prompts
        left_frame.rowconfigure(5, weight=1)  # Spacer
        left_frame.rowconfigure(6, weight=0)  # Status
        
        # 1. COMPACT IMAGE INPUT
        self.setup_image_input(left_frame)
        
        # 2. DANCE VIDEO SETTINGS (compact horizontal)
        self.setup_dance_settings(left_frame)
        
        # 3. VIDEO PROMPT (single, clean)
        self.setup_video_prompt(left_frame)
        
        # 4. PRIMARY ACTION (right after prompt!)
        self.setup_primary_action(left_frame)
        
        # 5. COLLAPSIBLE SAVED PROMPTS
        self.setup_saved_prompts_section(left_frame)
        
        # 6. SPACER
        spacer = ttk.Frame(left_frame)
        spacer.grid(row=5, column=0, sticky="nsew")
        
        # 7. STATUS
        self.setup_status_section(left_frame)
    
    def setup_image_input(self, parent):
        """Compact image input section"""
        input_frame = ttk.LabelFrame(parent, text="📥 Input Image", padding="6")
        input_frame.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        input_frame.columnconfigure(1, weight=1)
        
        # Thumbnail + Info layout
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
    
    def setup_dance_settings(self, parent):
        """Compact dance/motion video settings"""
        settings_frame = ttk.LabelFrame(parent, text="🕺 Dance Settings", padding="6")
        settings_frame.grid(row=1, column=0, sticky="ew", pady=(0, 8))
        settings_frame.columnconfigure(1, weight=1)
        settings_frame.columnconfigure(3, weight=1)
        
        # Row 1: Duration + Resolution
        ttk.Label(settings_frame, text="Duration:", font=('Arial', 9)).grid(
            row=0, column=0, sticky="w", padx=(0, 4)
        )
        
        duration_combo = ttk.Combobox(
            settings_frame,
            textvariable=self.duration_var,
            values=["1s", "2s", "3s", "5s", "8s"],
            state="readonly",
            width=6,
            font=('Arial', 9)
        )
        duration_combo.grid(row=0, column=1, sticky="w", padx=(0, 12))
        
        ttk.Label(settings_frame, text="Resolution:", font=('Arial', 9)).grid(
            row=0, column=2, sticky="w", padx=(0, 4)
        )
        
        resolution_combo = ttk.Combobox(
            settings_frame,
            textvariable=self.resolution_var,
            values=["512x512", "768x768", "1024x576", "1024x1024"],
            state="readonly",
            width=10,
            font=('Arial', 9)
        )
        resolution_combo.grid(row=0, column=3, sticky="w")
        
        # Row 2: Camera Fixed + Seed
        camera_check = ttk.Checkbutton(
            settings_frame,
            text="Camera Fixed",
            variable=self.camera_fixed_var,
            style='Small.TCheckbutton'
        )
        camera_check.grid(row=1, column=0, columnspan=2, sticky="w", pady=(4, 0))
        
        ttk.Label(settings_frame, text="Seed:", font=('Arial', 9)).grid(
            row=1, column=2, sticky="w", padx=(0, 4), pady=(4, 0)
        )
        
        seed_entry = ttk.Entry(
            settings_frame,
            textvariable=self.seed_var,
            width=10,
            font=('Arial', 9)
        )
        seed_entry.grid(row=1, column=3, sticky="w", pady=(4, 0))
    
    def setup_video_prompt(self, parent):
        """Single, clean video prompt section"""
        prompt_frame = ttk.LabelFrame(parent, text="🎬 Motion Description", padding="6")
        prompt_frame.grid(row=2, column=0, sticky="ew", pady=(0, 8))
        prompt_frame.columnconfigure(0, weight=1)
        
        # Helpful label
        ttk.Label(
            prompt_frame,
            text="Describe the motion, dance, or scene (optional):",
            font=('Arial', 9),
            foreground="#666"
        ).grid(row=0, column=0, sticky="w", pady=(0, 4))
        
        # Video prompt text (moderate size for motion descriptions)
        self.video_prompt_text = tk.Text(
            prompt_frame,
            height=4,  # Good size for motion descriptions
            wrap=tk.WORD,
            font=('Arial', 10),
            relief='solid',
            borderwidth=1
        )
        self.video_prompt_text.grid(row=1, column=0, sticky="ew")
        
        # Placeholder text
        self.video_prompt_text.insert("1.0", "Describe the motion, dance moves, or scene animation...")
        self.video_prompt_text.bind("<FocusIn>", self.clear_prompt_placeholder)
        self.video_prompt_text.bind("<FocusOut>", self.add_prompt_placeholder)
        
        # Quick prompt suggestions
        suggestions_frame = ttk.Frame(prompt_frame)
        suggestions_frame.grid(row=2, column=0, sticky="ew", pady=(4, 0))
        
        ttk.Label(suggestions_frame, text="Quick ideas:", font=('Arial', 8), foreground="#888").pack(side=tk.LEFT)
        
        suggestion_buttons = [
            ("💃 Dance", "A person dancing gracefully with smooth, flowing movements"),
            ("🌊 Wave", "Gentle wave-like motion, swaying back and forth"),
            ("🔄 Spin", "Spinning or rotating motion around the center"),
            ("🚶 Walk", "Natural walking motion forward")
        ]
        
        for text, prompt in suggestion_buttons:
            btn = ttk.Button(
                suggestions_frame,
                text=text,
                command=lambda p=prompt: self.set_suggestion(p),
                width=8
            )
            btn.pack(side=tk.LEFT, padx=(4, 0))
    
    def setup_primary_action(self, parent):
        """Primary action - immediately after prompt"""
        action_frame = ttk.Frame(parent)
        action_frame.grid(row=3, column=0, sticky="ew", pady=8)
        action_frame.columnconfigure(0, weight=1)
        
        # PROMINENT generate button
        self.generate_btn = ttk.Button(
            action_frame,
            text="🕺 Generate SeedDance Video",
            command=self.process_dance_generation,
            style='Accent.TButton'
        )
        self.generate_btn.grid(row=0, column=0, sticky="ew")
        
        # Quick action buttons (horizontal, minimal)
        quick_actions = ttk.Frame(action_frame)
        quick_actions.grid(row=1, column=0, sticky="ew", pady=(4, 0))
        quick_actions.columnconfigure(0, weight=1)
        quick_actions.columnconfigure(1, weight=1)
        quick_actions.columnconfigure(2, weight=1)
        
        ttk.Button(
            quick_actions,
            text="🤖 AI",
            command=self.improve_with_ai,
            width=8
        ).grid(row=0, column=0, sticky="ew", padx=(0, 1))
        
        ttk.Button(
            quick_actions,
            text="🎲 Sample",
            command=self.load_sample,
            width=8
        ).grid(row=0, column=1, sticky="ew", padx=(1, 1))
        
        ttk.Button(
            quick_actions,
            text="🧹 Clear",
            command=self.clear_all,
            width=8
        ).grid(row=0, column=2, sticky="ew", padx=(1, 0))
    
    def setup_saved_prompts_section(self, parent):
        """Collapsible saved prompts section"""
        saved_frame = ttk.Frame(parent)
        saved_frame.grid(row=4, column=0, sticky="ew", pady=(0, 8))
        saved_frame.columnconfigure(1, weight=1)
        
        # Header with toggle button
        self.saved_toggle_btn = ttk.Button(
            saved_frame,
            text="▶",
            width=3,
            command=self.toggle_saved_prompts
        )
        self.saved_toggle_btn.grid(row=0, column=0, sticky="w")
        
        ttk.Label(
            saved_frame,
            text="💾 Saved Motion Prompts",
            font=('Arial', 9, 'bold')
        ).grid(row=0, column=1, sticky="w", padx=(4, 0))
        
        # Content frame (initially hidden)
        self.saved_content_frame = ttk.Frame(saved_frame)
        # Don't grid it yet - will be shown/hidden by toggle
        
        # Saved prompts content
        self.saved_prompts_listbox = tk.Listbox(
            self.saved_content_frame,
            height=4,
            font=('Arial', 9),
            selectmode=tk.SINGLE
        )
        self.saved_prompts_listbox.grid(row=0, column=0, sticky="ew", pady=(4, 2))
        self.saved_prompts_listbox.bind('<<ListboxSelect>>', self.on_saved_prompt_selected)
        
        # Add some sample saved prompts
        sample_prompts = [
            "Graceful ballet dance with flowing movements",
            "Hip-hop dance with sharp, rhythmic moves",
            "Slow-motion walking forward",
            "Gentle swaying like a tree in the wind"
        ]
        for prompt in sample_prompts:
            self.saved_prompts_listbox.insert(tk.END, prompt)
        
        # Saved prompts buttons
        saved_btn_frame = ttk.Frame(self.saved_content_frame)
        saved_btn_frame.grid(row=1, column=0, sticky="ew")
        saved_btn_frame.columnconfigure(0, weight=1)
        saved_btn_frame.columnconfigure(1, weight=1)
        
        ttk.Button(
            saved_btn_frame,
            text="💾 Save",
            command=self.save_current_prompt,
            width=8
        ).grid(row=0, column=0, sticky="ew", padx=(0, 1))
        
        ttk.Button(
            saved_btn_frame,
            text="🗑️ Delete",
            command=self.delete_saved_prompt,
            width=8
        ).grid(row=0, column=1, sticky="ew", padx=(1, 0))
        
        # Configure content frame
        self.saved_content_frame.columnconfigure(0, weight=1)
    
    def setup_status_section(self, parent):
        """Compact status section"""
        status_frame = ttk.LabelFrame(parent, text="📊 Status", padding="4")
        status_frame.grid(row=6, column=0, sticky="ew")
        status_frame.columnconfigure(0, weight=1)
        
        # Status label
        self.status_label = ttk.Label(
            status_frame,
            text="Ready for SeedDance generation",
            font=('Arial', 9),
            foreground="green"
        )
        self.status_label.grid(row=0, column=0, sticky="w")
        
        # Progress bar (hidden by default)
        self.progress_bar = ttk.Progressbar(
            status_frame,
            mode='indeterminate'
        )
        # Don't grid it yet - only show when processing
    
    def setup_right_column(self, parent):
        """Setup right column with large video player"""
        right_frame = ttk.Frame(parent, relief='groove', borderwidth=1, padding="4")
        right_frame.grid(row=0, column=1, sticky="nsew", padx=(4, 0))
        right_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(1, weight=1)
        
        # Video controls header
        self.setup_video_controls(right_frame)
        
        # Large video player area
        self.setup_video_player(right_frame)
    
    def setup_video_controls(self, parent):
        """Dance video specific controls and info"""
        controls_frame = ttk.Frame(parent)
        controls_frame.grid(row=0, column=0, sticky="ew", pady=(0, 4))
        controls_frame.columnconfigure(1, weight=1)
        
        # Video info
        ttk.Label(controls_frame, text="🕺 Dance Video Preview", font=('Arial', 11, 'bold')).grid(
            row=0, column=0, sticky="w"
        )
        
        # Video info label
        self.video_info_label = ttk.Label(
            controls_frame,
            text="No dance video generated yet",
            font=('Arial', 9),
            foreground="gray"
        )
        self.video_info_label.grid(row=0, column=1, sticky="e")
    
    def setup_video_player(self, parent):
        """Large video player area optimized for motion preview"""
        player_frame = ttk.Frame(parent)
        player_frame.grid(row=1, column=0, sticky="nsew")
        player_frame.columnconfigure(0, weight=1)
        player_frame.rowconfigure(0, weight=1)
        
        # Video canvas/player area
        self.video_canvas = tk.Canvas(
            player_frame,
            bg='black',
            highlightthickness=0,
            relief='flat'
        )
        self.video_canvas.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)
        
        # Bind events
        self.video_canvas.bind('<Configure>', self.on_video_canvas_configure)
        self.video_canvas.bind('<Button-1>', self.on_video_click)
        
        # Default message
        self.show_dance_placeholder()
    
    def setup_bottom_toolbar(self, parent):
        """Global dance video playback toolbar"""
        toolbar_frame = ttk.Frame(parent, relief='groove', borderwidth=1, padding="4")
        toolbar_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(4, 0))
        
        # Video playback controls
        ttk.Button(
            toolbar_frame,
            text="▶️ Play",
            command=self.play_video,
            width=8
        ).pack(side=tk.LEFT, padx=(0, 4))
        
        ttk.Button(
            toolbar_frame,
            text="⏸️ Pause",
            command=self.pause_video,
            width=8
        ).pack(side=tk.LEFT, padx=(0, 4))
        
        ttk.Button(
            toolbar_frame,
            text="🔁 Loop",
            command=self.toggle_loop,
            width=8
        ).pack(side=tk.LEFT, padx=(0, 4))
        
        # Separator
        ttk.Separator(toolbar_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=8)
        
        # Export controls
        ttk.Button(
            toolbar_frame,
            text="🌐 Open in Browser",
            command=self.open_in_browser,
            width=15
        ).pack(side=tk.LEFT, padx=(0, 4))
        
        ttk.Button(
            toolbar_frame,
            text="📱 Play in System",
            command=self.play_in_system,
            width=15
        ).pack(side=tk.LEFT, padx=(0, 4))
        
        ttk.Button(
            toolbar_frame,
            text="💾 Download",
            command=self.download_video,
            width=10
        ).pack(side=tk.LEFT, padx=(0, 4))
        
        # Progress info (right side)
        self.progress_info_label = ttk.Label(
            toolbar_frame,
            text="",
            font=('Arial', 8),
            foreground="gray"
        )
        self.progress_info_label.pack(side=tk.RIGHT)
    
    def show_dance_placeholder(self):
        """Show placeholder in dance video area"""
        self.video_canvas.delete("all")
        
        # Get canvas dimensions
        canvas_width = self.video_canvas.winfo_width()
        canvas_height = self.video_canvas.winfo_height()
        
        if canvas_width <= 1:
            canvas_width = 540
            canvas_height = 400
        
        # Create placeholder
        center_x = canvas_width // 2
        center_y = canvas_height // 2
        
        # Dance icon
        self.video_canvas.create_text(
            center_x, center_y - 20,
            text="🕺",
            font=('Arial', 48),
            fill='white'
        )
        
        # Text
        self.video_canvas.create_text(
            center_x, center_y + 30,
            text="Dance video will appear here\n\nClick 'Generate SeedDance Video' to create motion",
            font=('Arial', 12),
            fill='#ccc',
            justify=tk.CENTER
        )
    
    # Event handlers and processing methods
    def browse_image(self):
        """Browse for input image"""
        from tkinter import filedialog
        file_path = filedialog.askopenfilename(
            title="Select Input Image for Dance Video",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.gif *.bmp *.webp"),
                ("All files", "*.*")
            ]
        )
        if file_path:
            self.load_image(file_path)
    
    def load_image(self, image_path):
        """Load input image"""
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
            
            # Enable generate button
            self.generate_btn.config(state='normal')
            
            # Update status
            self.status_label.config(text=f"✅ Input loaded: {filename}", foreground="green")
            
        except Exception as e:
            self.status_label.config(text=f"❌ Error loading image: {str(e)}", foreground="red")
            self.generate_btn.config(state='disabled')
    
    def set_suggestion(self, prompt):
        """Set a suggested prompt"""
        self.video_prompt_text.delete("1.0", tk.END)
        self.video_prompt_text.insert("1.0", prompt)
    
    def process_dance_generation(self):
        """Process dance video generation"""
        if not self.selected_image_path:
            self.status_label.config(text="❌ Please select an input image first", foreground="red")
            return
        
        # Get prompt (optional for SeedDance)
        video_prompt = self.video_prompt_text.get("1.0", tk.END).strip()
        if video_prompt == "Describe the motion, dance moves, or scene animation...":
            video_prompt = ""  # Empty is fine for SeedDance
        
        # Get settings
        duration = self.duration_var.get()
        resolution = self.resolution_var.get()
        camera_fixed = self.camera_fixed_var.get()
        seed = self.seed_var.get()
        
        # Start processing
        self.start_time = time.time()
        
        # Show processing state
        self.generate_btn.config(state='disabled', text="Generating Dance...")
        self.progress_bar.grid(row=1, column=0, sticky="ew", pady=(4, 0))
        self.progress_bar.start()
        self.status_label.config(text="🕺 Generating dance video with SeedDance Pro...", foreground="blue")
        
        # Update progress info
        settings_info = f"Duration: {duration} | Resolution: {resolution}"
        if camera_fixed:
            settings_info += " | Camera Fixed"
        self.progress_info_label.config(text=settings_info)
        
        # Here you would call your actual SeedDance API
        # For demo, simulate processing
        self.parent_frame.after(4000, self.after_dance_generation)  # Simulate 4 second processing
    
    def after_dance_generation(self):
        """Called after dance generation completes"""
        # Calculate processing time
        processing_time = time.time() - self.start_time if self.start_time else 0
        
        # Hide progress
        self.progress_bar.stop()
        self.progress_bar.grid_remove()
        self.generate_btn.config(state='normal', text="🕺 Generate SeedDance Video")
        
        # Update status
        self.status_label.config(text=f"✅ Dance video generated in {processing_time:.1f}s", foreground="green")
        
        # Update video info
        duration = self.duration_var.get()
        resolution = self.resolution_var.get()
        self.video_info_label.config(text=f"MP4 • {duration} • {resolution}", foreground="black")
        
        # Update progress info
        self.progress_info_label.config(text="Ready for playback")
        
        # Show video ready state
        self.show_dance_ready()
        
        # Mark as having result
        self.result_video_path = "generated_dance.mp4"  # Placeholder
    
    def show_dance_ready(self):
        """Show that dance video is ready"""
        self.video_canvas.delete("all")
        
        canvas_width = self.video_canvas.winfo_width()
        canvas_height = self.video_canvas.winfo_height()
        
        if canvas_width <= 1:
            canvas_width = 540
            canvas_height = 400
        
        center_x = canvas_width // 2
        center_y = canvas_height // 2
        
        # Dance ready icon
        self.video_canvas.create_text(
            center_x, center_y - 20,
            text="💃",
            font=('Arial', 48),
            fill='#4CAF50'
        )
        
        # Text
        self.video_canvas.create_text(
            center_x, center_y + 30,
            text="✅ Dance Video Generated!\n\nClick Play to preview or use toolbar controls",
            font=('Arial', 12),
            fill='white',
            justify=tk.CENTER
        )
    
    def toggle_saved_prompts(self):
        """Toggle saved prompts section"""
        if self.saved_prompts_expanded:
            # Collapse
            self.saved_content_frame.grid_remove()
            self.saved_toggle_btn.config(text="▶")
            self.saved_prompts_expanded = False
        else:
            # Expand
            self.saved_content_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=(20, 0), pady=(4, 0))
            self.saved_toggle_btn.config(text="▼")
            self.saved_prompts_expanded = True
    
    # Placeholder text handlers
    def clear_prompt_placeholder(self, event):
        current_text = self.video_prompt_text.get("1.0", tk.END).strip()
        if current_text == "Describe the motion, dance moves, or scene animation...":
            self.video_prompt_text.delete("1.0", tk.END)
    
    def add_prompt_placeholder(self, event):
        current_text = self.video_prompt_text.get("1.0", tk.END).strip()
        if not current_text:
            self.video_prompt_text.insert("1.0", "Describe the motion, dance moves, or scene animation...")
    
    # Event handlers
    def on_video_canvas_configure(self, event):
        """Handle video canvas resize"""
        if not self.result_video_path:
            self.show_dance_placeholder()
        else:
            self.show_dance_ready()
    
    def on_video_click(self, event):
        """Handle video canvas click"""
        if self.result_video_path:
            self.play_video()
    
    # Video playback methods (placeholders)
    def play_video(self):
        """Play dance video"""
        if self.result_video_path:
            self.status_label.config(text="▶️ Playing dance video...", foreground="blue")
    
    def pause_video(self):
        """Pause video"""
        if self.result_video_path:
            self.status_label.config(text="⏸️ Video paused", foreground="gray")
    
    def toggle_loop(self):
        """Toggle video loop"""
        if self.result_video_path:
            self.status_label.config(text="🔁 Loop mode toggled", foreground="blue")
    
    def open_in_browser(self):
        """Open video in browser"""
        if self.result_video_path:
            self.status_label.config(text="🌐 Opening in browser...", foreground="blue")
    
    def play_in_system(self):
        """Play in system player"""
        if self.result_video_path:
            self.status_label.config(text="📱 Opening in system player...", foreground="blue")
    
    def download_video(self):
        """Download video"""
        if self.result_video_path:
            self.status_label.config(text="💾 Dance video downloaded", foreground="green")
    
    def setup_enhanced_features(self):
        """Setup status console and keyboard shortcuts integration"""
        # Initialize keyboard manager for this layout
        self.keyboard_manager = KeyboardManager(self.parent_frame, "SeedDance Pro")
        
        # Register primary action
        self.keyboard_manager.register_primary_action(self.process_dance_generation, self.generate_btn)
        
        # Register file operations
        self.keyboard_manager.register_file_actions(
            self.browse_image,
            self.clear_all
        )
    
    # Prompt management methods (placeholders)
    def improve_with_ai(self): pass
    def load_sample(self): pass
    def clear_all(self): pass
    def on_saved_prompt_selected(self, event): pass
    def save_current_prompt(self): pass
    def delete_saved_prompt(self): pass


"""
KEY IMPROVEMENTS FOR SEEDDANCE PRO:

✅ 1. CLEANER THAN WAN 2.2 (No negative prompts needed)
   - Single video prompt section
   - Streamlined workflow: Input → Settings → Prompt → Generate
   - Less vertical space than Wan 2.2

✅ 2. GENERATE BUTTON IMMEDIATELY AFTER PROMPT
   - Perfect dance workflow: Describe motion → Click generate → Watch dance
   - "🕺 Generate SeedDance Video" right below prompt
   - No scrolling needed for primary action

✅ 3. DANCE-SPECIFIC SETTINGS
   - Duration: 1s, 2s, 3s, 5s, 8s (dance-appropriate durations)
   - Resolution: Square and video formats
   - Camera Fixed: Important for dance/motion consistency
   - Compact horizontal layout saves space

✅ 4. QUICK MOTION SUGGESTIONS
   - 💃 Dance | 🌊 Wave | 🔄 Spin | 🚶 Walk buttons
   - One-click preset motions for quick testing
   - Helps users understand what SeedDance can do

✅ 5. COLLAPSIBLE SAVED PROMPTS
   - Collapsed by default (▶ toggle)
   - Sample dance prompts included
   - Expands only when needed

✅ 6. LARGE DANCE VIDEO PREVIEW
   - 60% of screen width for motion preview
   - Dance-specific placeholder and ready states
   - Optimized for viewing motion and animation

✅ 7. DANCE VIDEO TOOLBAR
   - ▶️ Play | ⏸️ Pause | 🔁 Loop controls
   - Loop is important for dance videos
   - Same export options as Wan 2.2

✅ 8. MOTION-FOCUSED WORKFLOW
   - Input → Settings → Motion Description → **GENERATE** → Dance Preview
   - All steps visible without scrolling
   - Dance/motion-optimized user experience

✅ 9. OPTIONAL PROMPTS
   - Clear indication that prompts are optional
   - SeedDance can work with just the input image
   - Flexible for both guided and free-form generation

This layout is specifically optimized for dance/motion video generation:
- Simpler than Wan 2.2 (no negative prompts)
- Motion-specific settings and suggestions
- Streamlined workflow for quick dance generation
- Large preview area perfect for viewing motion

The collapsible saved prompts and quick suggestions make it 
beginner-friendly while keeping advanced features available!
"""
