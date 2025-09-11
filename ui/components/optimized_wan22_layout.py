"""
Optimized Wan 2.2 Video Generation Layout
1. Eliminate vertical scrolling with 2-column design
2. Generate button immediately after prompts
3. Large video player with integrated controls
4. Collapsible saved prompts section
5. Video-optimized settings and workflow
6. Clean video preview → generate → playback loop
"""

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os
import time


class OptimizedWan22Layout:
    """Optimized layout specifically designed for video generation workflow"""
    
    def __init__(self, parent_frame):
        self.parent_frame = parent_frame
        self.selected_image_path = None
        self.result_video_path = None
        
        # Settings variables
        self.duration_var = tk.StringVar(value="5s")
        self.seed_var = tk.StringVar(value="-1")
        self.last_image_url_var = tk.StringVar(value="")
        self.saved_prompts_expanded = False
        
        # Processing tracking
        self.start_time = None
        
        self.setup_layout()
    
    def setup_layout(self):
        """Setup optimized 2-column layout for video generation"""
        
        # Main container
        main_container = ttk.Frame(self.parent_frame)
        main_container.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        
        # Configure grid - 2 columns optimized for video workflow
        main_container.columnconfigure(0, weight=1, minsize=380)  # Left: Controls
        main_container.columnconfigure(1, weight=2, minsize=520)  # Right: Video player (2x weight)
        main_container.rowconfigure(0, weight=1)
        main_container.rowconfigure(1, weight=0)  # Bottom toolbar
        
        # Left Column - Video Controls
        self.setup_left_column(main_container)
        
        # Right Column - Large Video Player
        self.setup_right_column(main_container)
        
        # Bottom Toolbar - Video Playback Controls
        self.setup_bottom_toolbar(main_container)
    
    def setup_left_column(self, parent):
        """Setup left column with video generation workflow"""
        left_frame = ttk.Frame(parent, relief='groove', borderwidth=1, padding="8")
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 4))
        left_frame.columnconfigure(0, weight=1)
        
        # Configure rows for optimal video workflow
        left_frame.rowconfigure(0, weight=0)  # Image input - compact
        left_frame.rowconfigure(1, weight=0)  # Settings - compact
        left_frame.rowconfigure(2, weight=0)  # Prompts - expandable but controlled
        left_frame.rowconfigure(3, weight=0)  # Primary action - prominent
        left_frame.rowconfigure(4, weight=0)  # Collapsible saved prompts
        left_frame.rowconfigure(5, weight=1)  # Spacer
        left_frame.rowconfigure(6, weight=0)  # Status/Progress
        
        # 1. COMPACT IMAGE INPUT
        self.setup_image_input(left_frame)
        
        # 2. VIDEO SETTINGS (compact horizontal layout)
        self.setup_video_settings(left_frame)
        
        # 3. PROMPT SECTIONS (video + negative)
        self.setup_prompt_sections(left_frame)
        
        # 4. PRIMARY ACTION (right after prompts!)
        self.setup_primary_action(left_frame)
        
        # 5. COLLAPSIBLE SAVED PROMPTS
        self.setup_saved_prompts_section(left_frame)
        
        # 6. SPACER
        spacer = ttk.Frame(left_frame)
        spacer.grid(row=5, column=0, sticky="nsew")
        
        # 7. STATUS/PROGRESS
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
    
    def setup_video_settings(self, parent):
        """Compact video-specific settings"""
        settings_frame = ttk.LabelFrame(parent, text="🎬 Video Settings", padding="6")
        settings_frame.grid(row=1, column=0, sticky="ew", pady=(0, 8))
        settings_frame.columnconfigure(1, weight=1)
        settings_frame.columnconfigure(3, weight=1)
        
        # Row 1: Duration + Seed
        ttk.Label(settings_frame, text="Duration:", font=('Arial', 9)).grid(
            row=0, column=0, sticky="w", padx=(0, 4)
        )
        
        duration_combo = ttk.Combobox(
            settings_frame,
            textvariable=self.duration_var,
            values=["2s", "3s", "5s", "10s", "15s"],
            state="readonly",
            width=6,
            font=('Arial', 9)
        )
        duration_combo.grid(row=0, column=1, sticky="w", padx=(0, 12))
        
        ttk.Label(settings_frame, text="Seed:", font=('Arial', 9)).grid(
            row=0, column=2, sticky="w", padx=(0, 4)
        )
        
        seed_entry = ttk.Entry(
            settings_frame,
            textvariable=self.seed_var,
            width=8,
            font=('Arial', 9)
        )
        seed_entry.grid(row=0, column=3, sticky="w")
        
        # Row 2: Last Image URL (optional advanced setting)
        ttk.Label(settings_frame, text="Last Frame URL:", font=('Arial', 8)).grid(
            row=1, column=0, sticky="w", pady=(4, 0)
        )
        
        url_entry = ttk.Entry(
            settings_frame,
            textvariable=self.last_image_url_var,
            font=('Arial', 8)
        )
        url_entry.grid(row=1, column=1, columnspan=3, sticky="ew", pady=(4, 0), padx=(4, 0))
    
    def setup_prompt_sections(self, parent):
        """Video and negative prompt sections"""
        prompts_frame = ttk.LabelFrame(parent, text="✏️ Video Prompts", padding="6")
        prompts_frame.grid(row=2, column=0, sticky="ew", pady=(0, 8))
        prompts_frame.columnconfigure(0, weight=1)
        
        # Video Prompt (main)
        ttk.Label(prompts_frame, text="Video Prompt:", font=('Arial', 9, 'bold')).grid(
            row=0, column=0, sticky="w", pady=(0, 2)
        )
        
        self.video_prompt_text = tk.Text(
            prompts_frame,
            height=4,  # Slightly larger for video descriptions
            wrap=tk.WORD,
            font=('Arial', 10),
            relief='solid',
            borderwidth=1
        )
        self.video_prompt_text.grid(row=1, column=0, sticky="ew", pady=(0, 6))
        
        # Placeholder text
        self.video_prompt_text.insert("1.0", "Describe the video motion and scene you want to create...")
        self.video_prompt_text.bind("<FocusIn>", self.clear_video_placeholder)
        self.video_prompt_text.bind("<FocusOut>", self.add_video_placeholder)
        
        # Negative Prompt (smaller)
        ttk.Label(prompts_frame, text="Negative Prompt:", font=('Arial', 9)).grid(
            row=2, column=0, sticky="w", pady=(6, 2)
        )
        
        self.negative_prompt_text = tk.Text(
            prompts_frame,
            height=2,  # Smaller for negative prompts
            wrap=tk.WORD,
            font=('Arial', 9),
            relief='solid',
            borderwidth=1
        )
        self.negative_prompt_text.grid(row=3, column=0, sticky="ew")
        
        # Negative prompt placeholder
        self.negative_prompt_text.insert("1.0", "What to avoid in the video...")
        self.negative_prompt_text.bind("<FocusIn>", self.clear_negative_placeholder)
        self.negative_prompt_text.bind("<FocusOut>", self.add_negative_placeholder)
    
    def setup_primary_action(self, parent):
        """Primary action - immediately after prompts"""
        action_frame = ttk.Frame(parent)
        action_frame.grid(row=3, column=0, sticky="ew", pady=8)
        action_frame.columnconfigure(0, weight=1)
        
        # PROMINENT generate button
        self.generate_btn = ttk.Button(
            action_frame,
            text="🎬 Generate with Wan 2.2",
            command=self.process_video_generation,
            style='Accent.TButton'
        )
        self.generate_btn.grid(row=0, column=0, sticky="ew")
        
        # Quick action buttons (horizontal)
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
            text="💾 Saved Prompts",
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
        """Status and progress section"""
        status_frame = ttk.LabelFrame(parent, text="📊 Status", padding="4")
        status_frame.grid(row=6, column=0, sticky="ew")
        status_frame.columnconfigure(0, weight=1)
        
        # Status label
        self.status_label = ttk.Label(
            status_frame,
            text="Ready for Wan 2.2 generation",
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
        """Video-specific controls and info"""
        controls_frame = ttk.Frame(parent)
        controls_frame.grid(row=0, column=0, sticky="ew", pady=(0, 4))
        controls_frame.columnconfigure(1, weight=1)
        
        # Video info
        ttk.Label(controls_frame, text="🎬 Video Preview", font=('Arial', 11, 'bold')).grid(
            row=0, column=0, sticky="w"
        )
        
        # Video info label
        self.video_info_label = ttk.Label(
            controls_frame,
            text="No video generated yet",
            font=('Arial', 9),
            foreground="gray"
        )
        self.video_info_label.grid(row=0, column=1, sticky="e")
    
    def setup_video_player(self, parent):
        """Large video player area"""
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
        self.show_video_placeholder()
    
    def setup_bottom_toolbar(self, parent):
        """Global video playback toolbar"""
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
    
    def show_video_placeholder(self):
        """Show placeholder in video area"""
        self.video_canvas.delete("all")
        
        # Get canvas dimensions
        canvas_width = self.video_canvas.winfo_width()
        canvas_height = self.video_canvas.winfo_height()
        
        if canvas_width <= 1:
            canvas_width = 520
            canvas_height = 400
        
        # Create placeholder
        center_x = canvas_width // 2
        center_y = canvas_height // 2
        
        # Video icon
        self.video_canvas.create_text(
            center_x, center_y - 20,
            text="🎬",
            font=('Arial', 48),
            fill='white'
        )
        
        # Text
        self.video_canvas.create_text(
            center_x, center_y + 30,
            text="Video will appear here after generation\n\nClick 'Generate with Wan 2.2' to create video",
            font=('Arial', 12),
            fill='#ccc',
            justify=tk.CENTER
        )
    
    # Event handlers and processing methods
    def browse_image(self):
        """Browse for input image"""
        from tkinter import filedialog
        file_path = filedialog.askopenfilename(
            title="Select Input Image for Video Generation",
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
    
    def process_video_generation(self):
        """Process video generation"""
        if not self.selected_image_path:
            self.status_label.config(text="❌ Please select an input image first", foreground="red")
            return
        
        video_prompt = self.video_prompt_text.get("1.0", tk.END).strip()
        if not video_prompt or video_prompt == "Describe the video motion and scene you want to create...":
            self.status_label.config(text="❌ Please enter a video prompt", foreground="red")
            return
        
        # Get settings
        duration = self.duration_var.get()
        seed = self.seed_var.get()
        negative_prompt = self.negative_prompt_text.get("1.0", tk.END).strip()
        last_image_url = self.last_image_url_var.get().strip()
        
        # Start processing
        self.start_time = time.time()
        
        # Show processing state
        self.generate_btn.config(state='disabled', text="Generating Video...")
        self.progress_bar.grid(row=1, column=0, sticky="ew", pady=(4, 0))
        self.progress_bar.start()
        self.status_label.config(text="🎬 Generating video with Wan 2.2...", foreground="blue")
        
        # Update progress info
        self.progress_info_label.config(text=f"Duration: {duration} | Seed: {seed}")
        
        # Here you would call your actual Wan 2.2 API
        # For demo, simulate processing
        self.parent_frame.after(5000, self.after_video_generation)  # Simulate 5 second processing
    
    def after_video_generation(self):
        """Called after video generation completes"""
        # Calculate processing time
        processing_time = time.time() - self.start_time if self.start_time else 0
        
        # Hide progress
        self.progress_bar.stop()
        self.progress_bar.grid_remove()
        self.generate_btn.config(state='normal', text="🎬 Generate with Wan 2.2")
        
        # Update status
        self.status_label.config(text=f"✅ Video generated successfully in {processing_time:.1f}s", foreground="green")
        
        # Update video info
        duration = self.duration_var.get()
        self.video_info_label.config(text=f"MP4 • {duration} • 1024×576", foreground="black")
        
        # Update progress info
        self.progress_info_label.config(text="Ready for playback")
        
        # Show video thumbnail or first frame in canvas
        self.show_video_ready()
        
        # Mark as having result
        self.result_video_path = "generated_video.mp4"  # Placeholder
    
    def show_video_ready(self):
        """Show that video is ready"""
        self.video_canvas.delete("all")
        
        canvas_width = self.video_canvas.winfo_width()
        canvas_height = self.video_canvas.winfo_height()
        
        if canvas_width <= 1:
            canvas_width = 520
            canvas_height = 400
        
        center_x = canvas_width // 2
        center_y = canvas_height // 2
        
        # Video ready icon
        self.video_canvas.create_text(
            center_x, center_y - 20,
            text="🎥",
            font=('Arial', 48),
            fill='#4CAF50'
        )
        
        # Text
        self.video_canvas.create_text(
            center_x, center_y + 30,
            text="✅ Video Generated Successfully!\n\nClick Play to preview or use toolbar controls",
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
    def clear_video_placeholder(self, event):
        current_text = self.video_prompt_text.get("1.0", tk.END).strip()
        if current_text == "Describe the video motion and scene you want to create...":
            self.video_prompt_text.delete("1.0", tk.END)
    
    def add_video_placeholder(self, event):
        current_text = self.video_prompt_text.get("1.0", tk.END).strip()
        if not current_text:
            self.video_prompt_text.insert("1.0", "Describe the video motion and scene you want to create...")
    
    def clear_negative_placeholder(self, event):
        current_text = self.negative_prompt_text.get("1.0", tk.END).strip()
        if current_text == "What to avoid in the video...":
            self.negative_prompt_text.delete("1.0", tk.END)
    
    def add_negative_placeholder(self, event):
        current_text = self.negative_prompt_text.get("1.0", tk.END).strip()
        if not current_text:
            self.negative_prompt_text.insert("1.0", "What to avoid in the video...")
    
    # Event handlers
    def on_video_canvas_configure(self, event):
        """Handle video canvas resize"""
        if not self.result_video_path:
            self.show_video_placeholder()
        else:
            self.show_video_ready()
    
    def on_video_click(self, event):
        """Handle video canvas click"""
        if self.result_video_path:
            self.play_video()
    
    # Video playback methods (placeholders)
    def play_video(self):
        """Play video"""
        if self.result_video_path:
            self.status_label.config(text="▶️ Playing video...", foreground="blue")
    
    def pause_video(self):
        """Pause video"""
        if self.result_video_path:
            self.status_label.config(text="⏸️ Video paused", foreground="gray")
    
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
            self.status_label.config(text="💾 Video downloaded", foreground="green")
    
    # Prompt management methods (placeholders)
    def improve_with_ai(self): pass
    def load_sample(self): pass
    def clear_all(self): pass
    def on_saved_prompt_selected(self, event): pass
    def save_current_prompt(self): pass
    def delete_saved_prompt(self): pass


"""
KEY IMPROVEMENTS FOR WAN 2.2 VIDEO GENERATION:

✅ 1. ELIMINATE VERTICAL SCROLLING
   - 2-column layout: Controls (38%) | Video Player (62%)
   - Generate button immediately after prompts
   - No scrolling needed for typical workflow

✅ 2. GENERATE BUTTON RIGHT AFTER PROMPTS
   - Perfect video workflow: Write prompt → Click generate → Watch video
   - Prominent "🎬 Generate with Wan 2.2" button
   - Quick actions (AI, Sample, Clear) in horizontal row below

✅ 3. LARGE VIDEO PLAYER AREA
   - 62% of screen width dedicated to video preview
   - Professional video controls and info
   - Clear placeholder and ready states

✅ 4. COLLAPSIBLE SAVED PROMPTS
   - Collapsed by default to save space
   - Click ▶/▼ to expand only when needed
   - Clean prompt management without clutter

✅ 5. VIDEO-OPTIMIZED SETTINGS
   - Duration, Seed, Last Frame URL in compact layout
   - Video-specific prompts (main + negative)
   - Appropriate text box sizes for video descriptions

✅ 6. GLOBAL VIDEO TOOLBAR
   - ▶️ Play | ⏸️ Pause controls
   - 🌐 Open in Browser | 📱 Play in System
   - 💾 Download | Progress info
   - Consistent across all video tabs

✅ 7. CLEAN VIDEO WORKFLOW
   - Input → Settings → Prompts → **GENERATE** → Preview → Playback
   - All steps visible without scrolling
   - Video-focused user experience

✅ 8. PROPER VIDEO STATUS
   - Processing time tracking
   - Video format and duration info
   - Clear ready/error states

This layout transforms Wan 2.2 from a scrolling text-heavy interface
into a streamlined video generation workspace where everything flows
naturally from prompt to preview to playback!
"""
