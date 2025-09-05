import os
import requests
import json
import time
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
from PIL import Image, ImageTk
import io
from dotenv import load_dotenv
from urllib.request import urlopen
import base64

# Try to import drag and drop support
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    DND_AVAILABLE = True
except ImportError:
    DND_AVAILABLE = False
    print("tkinterdnd2 not available. Drag and drop will be disabled.")

load_dotenv()



class ImageEditorGUI:
    def __init__(self, root):
        # Initialize drag and drop if available
        if DND_AVAILABLE:
            self.root = TkinterDnD.Tk() if root is None else root
        else:
            self.root = root
            
        self.root.title("WaveSpeed AI Image Editor & Upscaler")
        self.root.geometry("1000x800")
        self.root.configure(bg='#f0f0f0')
        
        # API configuration
        self.api_key = os.getenv("WAVESPEED_API_KEY")
        self.selected_image_path = None
        self.current_request_id = None
        self.result_image_url = None
        self.original_image = None
        self.result_image = None
        
        # Upscaler-specific variables
        self.upscaler_selected_image_path = None
        self.upscaler_current_request_id = None
        self.upscaler_result_image_url = None
        self.upscaler_original_image = None
        self.upscaler_result_image = None
        
        # Prompt storage
        self.prompts_file = "saved_prompts.json"
        self.saved_prompts = self.load_prompts()
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="WaveSpeed AI Image Editor & Upscaler", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, pady=(0, 20))
        
        # API Key status
        api_status = "✓ API Key loaded" if self.api_key else "✗ API Key not found"
        api_color = "green" if self.api_key else "red"
        api_label = tk.Label(main_frame, text=api_status, fg=api_color, 
                            bg='#f0f0f0', font=('Arial', 10))
        api_label.grid(row=1, column=0, pady=(0, 10))
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        
        # Create frames for each tab
        self.editor_frame = ttk.Frame(self.notebook, padding="10")
        self.upscaler_frame = ttk.Frame(self.notebook, padding="10")
        
        # Add tabs to notebook
        self.notebook.add(self.editor_frame, text="Image Editor")
        self.notebook.add(self.upscaler_frame, text="Image Upscaler")
        
        # Setup each tab
        self.setup_editor_tab()
        self.setup_upscaler_tab()
        
    def setup_editor_tab(self):
        """Setup the image editor tab with existing functionality"""
        # Configure grid weights
        self.editor_frame.columnconfigure(1, weight=1)
        
        # Image selection section
        ttk.Label(self.editor_frame, text="Select Image:", font=('Arial', 12, 'bold')).grid(
            row=0, column=0, sticky=tk.W, pady=(10, 5))
        
        image_frame = ttk.Frame(self.editor_frame)
        image_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        image_frame.columnconfigure(1, weight=1)
        
        self.select_button = ttk.Button(image_frame, text="Browse Image", 
                                       command=self.select_image)
        self.select_button.grid(row=0, column=0, padx=(0, 10))
        
        self.image_path_label = ttk.Label(image_frame, text="No image selected", 
                                         foreground="gray")
        self.image_path_label.grid(row=0, column=1, sticky=(tk.W, tk.E))
        
        # Image preview and results section
        images_frame = ttk.LabelFrame(self.editor_frame, text="Images", padding="10")
        images_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        images_frame.columnconfigure(0, weight=1)
        images_frame.columnconfigure(1, weight=1)
        
        # Original image section with drag and drop
        original_frame = ttk.LabelFrame(images_frame, text="Original Image (Drop image here or browse)", padding="5")
        original_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        
        # Create a frame for the drop zone with dashed border effect
        self.drop_frame = tk.Frame(original_frame, bg='#f8f8f8', relief='groove', bd=2)
        self.drop_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.original_image_label = tk.Label(self.drop_frame, text="📁 Drop image here or click 'Browse Image'\n\nSupported formats: PNG, JPG, JPEG, GIF, BMP, WebP", 
                                            bg='#f8f8f8', fg='#666666', font=('Arial', 10))
        self.original_image_label.pack(expand=True)
        
        # Result image section
        result_frame = ttk.LabelFrame(images_frame, text="Edited Result", padding="5")
        result_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0))
        
        self.result_image_label = ttk.Label(result_frame, text="No result yet")
        self.result_image_label.pack()
        
        # Buttons for result actions
        button_frame = ttk.Frame(result_frame)
        button_frame.pack(pady=(10, 0))
        
        self.save_button = ttk.Button(button_frame, text="Save Result Image", 
                                     command=self.save_result_image, state="disabled")
        self.save_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.use_result_button = ttk.Button(button_frame, text="Use as Next Input", 
                                           command=self.use_result_as_input, state="disabled")
        self.use_result_button.pack(side=tk.LEFT)
        
        # Prompt section
        prompt_section = ttk.LabelFrame(self.editor_frame, text="Edit Prompt", padding="10")
        prompt_section.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 10))
        prompt_section.columnconfigure(0, weight=1)
        
        # Current prompt input
        current_prompt_frame = ttk.Frame(prompt_section)
        current_prompt_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        current_prompt_frame.columnconfigure(0, weight=1)
        
        ttk.Label(current_prompt_frame, text="Current Prompt:", font=('Arial', 10, 'bold')).grid(
            row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        self.prompt_text = tk.Text(current_prompt_frame, height=3, wrap=tk.WORD, 
                                  font=('Arial', 11))
        self.prompt_text.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        prompt_scroll = ttk.Scrollbar(current_prompt_frame, orient="vertical", 
                                     command=self.prompt_text.yview)
        prompt_scroll.grid(row=1, column=1, sticky=(tk.N, tk.S))
        self.prompt_text.configure(yscrollcommand=prompt_scroll.set)
        
        # Prompt actions
        prompt_actions = ttk.Frame(current_prompt_frame)
        prompt_actions.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        
        self.save_prompt_button = ttk.Button(prompt_actions, text="Save Prompt", 
                                           command=self.save_current_prompt)
        self.save_prompt_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.clear_prompt_button = ttk.Button(prompt_actions, text="Clear", 
                                            command=lambda: self.prompt_text.delete("1.0", tk.END))
        self.clear_prompt_button.pack(side=tk.LEFT)
        
        # Saved prompts section
        saved_prompts_frame = ttk.Frame(prompt_section)
        saved_prompts_frame.grid(row=1, column=0, sticky=(tk.W, tk.E))
        saved_prompts_frame.columnconfigure(0, weight=1)
        
        ttk.Label(saved_prompts_frame, text="Saved Prompts:", font=('Arial', 10, 'bold')).grid(
            row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        # Saved prompts listbox with scrollbar
        prompts_list_frame = ttk.Frame(saved_prompts_frame)
        prompts_list_frame.grid(row=1, column=0, sticky=(tk.W, tk.E))
        prompts_list_frame.columnconfigure(0, weight=1)
        
        self.prompts_listbox = tk.Listbox(prompts_list_frame, height=4, font=('Arial', 10))
        self.prompts_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        prompts_list_scroll = ttk.Scrollbar(prompts_list_frame, orient="vertical", 
                                          command=self.prompts_listbox.yview)
        prompts_list_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.prompts_listbox.configure(yscrollcommand=prompts_list_scroll.set)
        
        # Saved prompts actions
        saved_actions = ttk.Frame(saved_prompts_frame)
        saved_actions.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        
        self.use_prompt_button = ttk.Button(saved_actions, text="Use Selected", 
                                          command=self.use_selected_prompt)
        self.use_prompt_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.delete_prompt_button = ttk.Button(saved_actions, text="Delete Selected", 
                                             command=self.delete_selected_prompt)
        self.delete_prompt_button.pack(side=tk.LEFT)
        
        # Load saved prompts into listbox
        self.refresh_prompts_list()
        
        # Output format section
        format_frame = ttk.Frame(self.editor_frame)
        format_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(format_frame, text="Output Format:", font=('Arial', 12, 'bold')).grid(
            row=0, column=0, sticky=tk.W, padx=(0, 10))
        
        self.format_var = tk.StringVar(value="png")
        format_combo = ttk.Combobox(format_frame, textvariable=self.format_var, 
                                   values=["png", "jpg", "webp"], state="readonly", width=10)
        format_combo.grid(row=0, column=1, sticky=tk.W)
        
        # Process button
        self.process_button = ttk.Button(self.editor_frame, text="Process Image", 
                                        command=self.process_image, 
                                        style="Accent.TButton")
        self.process_button.grid(row=5, column=0, columnspan=2, pady=20)
        
        # Progress section
        self.progress_frame = ttk.LabelFrame(self.editor_frame, text="Progress", padding="10")
        self.progress_frame.grid(row=6, column=0, columnspan=2, 
                                sticky=(tk.W, tk.E), pady=(0, 10))
        self.progress_frame.columnconfigure(0, weight=1)
        
        self.progress_bar = ttk.Progressbar(self.progress_frame, mode='indeterminate')
        self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        
        self.status_label = ttk.Label(self.progress_frame, text="Ready to process")
        self.status_label.grid(row=1, column=0, sticky=tk.W)
        
        # Results section
        self.results_frame = ttk.LabelFrame(self.editor_frame, text="Results", padding="10")
        self.results_frame.grid(row=7, column=0, columnspan=2, 
                               sticky=(tk.W, tk.E), pady=(0, 10))
        self.results_frame.columnconfigure(0, weight=1)
        
        self.result_text = tk.Text(self.results_frame, height=4, wrap=tk.WORD, 
                                  font=('Arial', 10), state=tk.DISABLED)
        self.result_text.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        result_scroll = ttk.Scrollbar(self.results_frame, orient="vertical", 
                                     command=self.result_text.yview)
        result_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.result_text.configure(yscrollcommand=result_scroll.set)
        
        # Initially hide progress and results
        self.progress_frame.grid_remove()
        self.results_frame.grid_remove()
        
        # Setup drag and drop
        self.setup_drag_and_drop()
        
    def setup_upscaler_tab(self):
        """Setup the image upscaler tab with new functionality"""
        # Configure grid weights
        self.upscaler_frame.columnconfigure(1, weight=1)
        
        # Image selection section for upscaler
        ttk.Label(self.upscaler_frame, text="Select Image to Upscale:", font=('Arial', 12, 'bold')).grid(
            row=0, column=0, sticky=tk.W, pady=(10, 5))
        
        upscaler_image_frame = ttk.Frame(self.upscaler_frame)
        upscaler_image_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        upscaler_image_frame.columnconfigure(1, weight=1)
        
        self.upscaler_select_button = ttk.Button(upscaler_image_frame, text="Browse Image", 
                                               command=self.select_upscaler_image)
        self.upscaler_select_button.grid(row=0, column=0, padx=(0, 10))
        
        self.upscaler_image_path_label = ttk.Label(upscaler_image_frame, text="No image selected", 
                                                 foreground="gray")
        self.upscaler_image_path_label.grid(row=0, column=1, sticky=(tk.W, tk.E))
        
        # Image preview and results section for upscaler
        upscaler_images_frame = ttk.LabelFrame(self.upscaler_frame, text="Images", padding="10")
        upscaler_images_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        upscaler_images_frame.columnconfigure(0, weight=1)
        upscaler_images_frame.columnconfigure(1, weight=1)
        
        # Original image section for upscaler
        upscaler_original_frame = ttk.LabelFrame(upscaler_images_frame, text="Original Image", padding="5")
        upscaler_original_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        
        # Create a frame for the upscaler drop zone
        self.upscaler_drop_frame = tk.Frame(upscaler_original_frame, bg='#f8f8f8', relief='groove', bd=2)
        self.upscaler_drop_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.upscaler_original_image_label = tk.Label(self.upscaler_drop_frame, 
                                                    text="📁 Click 'Browse Image' to select\n\nSupported formats: PNG, JPG, JPEG, GIF, BMP, WebP", 
                                                    bg='#f8f8f8', fg='#666666', font=('Arial', 10))
        self.upscaler_original_image_label.pack(expand=True)
        
        # Result image section for upscaler
        upscaler_result_frame = ttk.LabelFrame(upscaler_images_frame, text="Upscaled Result", padding="5")
        upscaler_result_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0))
        
        self.upscaler_result_image_label = ttk.Label(upscaler_result_frame, text="No result yet")
        self.upscaler_result_image_label.pack()
        
        # Buttons for upscaler result actions
        upscaler_button_frame = ttk.Frame(upscaler_result_frame)
        upscaler_button_frame.pack(pady=(10, 0))
        
        self.upscaler_save_button = ttk.Button(upscaler_button_frame, text="Save Result Image", 
                                             command=self.save_upscaler_result_image, state="disabled")
        self.upscaler_save_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.upscaler_use_result_button = ttk.Button(upscaler_button_frame, text="Use as Editor Input", 
                                                   command=self.use_upscaler_result_as_editor_input, state="disabled")
        self.upscaler_use_result_button.pack(side=tk.LEFT)
        
        # Upscaler settings section
        settings_section = ttk.LabelFrame(self.upscaler_frame, text="Upscaler Settings", padding="10")
        settings_section.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 10))
        settings_section.columnconfigure(0, weight=1)
        
        # Settings grid
        settings_grid = ttk.Frame(settings_section)
        settings_grid.grid(row=0, column=0, sticky=(tk.W, tk.E))
        settings_grid.columnconfigure(1, weight=1)
        settings_grid.columnconfigure(3, weight=1)
        
        # Target Resolution
        ttk.Label(settings_grid, text="Target Resolution:", font=('Arial', 10, 'bold')).grid(
            row=0, column=0, sticky=tk.W, padx=(0, 10), pady=(0, 10))
        
        self.upscaler_resolution_var = tk.StringVar(value="4k")
        resolution_combo = ttk.Combobox(settings_grid, textvariable=self.upscaler_resolution_var, 
                                       values=["2k", "4k", "8k"], state="readonly", width=10)
        resolution_combo.grid(row=0, column=1, sticky=tk.W, pady=(0, 10))
        
        # Creativity Level
        ttk.Label(settings_grid, text="Creativity Level:", font=('Arial', 10, 'bold')).grid(
            row=0, column=2, sticky=tk.W, padx=(20, 10), pady=(0, 10))
        
        self.upscaler_creativity_var = tk.StringVar(value="0")
        creativity_combo = ttk.Combobox(settings_grid, textvariable=self.upscaler_creativity_var, 
                                       values=["-2", "-1", "0", "1", "2"], state="readonly", width=10)
        creativity_combo.grid(row=0, column=3, sticky=tk.W, pady=(0, 10))
        
        # Output Format
        ttk.Label(settings_grid, text="Output Format:", font=('Arial', 10, 'bold')).grid(
            row=1, column=0, sticky=tk.W, padx=(0, 10))
        
        self.upscaler_format_var = tk.StringVar(value="png")
        upscaler_format_combo = ttk.Combobox(settings_grid, textvariable=self.upscaler_format_var, 
                                           values=["png", "jpeg", "webp"], state="readonly", width=10)
        upscaler_format_combo.grid(row=1, column=1, sticky=tk.W)
        
        # Process button for upscaler
        self.upscaler_process_button = ttk.Button(self.upscaler_frame, text="Upscale Image", 
                                                command=self.process_upscaler_image, 
                                                style="Accent.TButton")
        self.upscaler_process_button.grid(row=4, column=0, columnspan=2, pady=20)
        
        # Progress section for upscaler
        self.upscaler_progress_frame = ttk.LabelFrame(self.upscaler_frame, text="Progress", padding="10")
        self.upscaler_progress_frame.grid(row=5, column=0, columnspan=2, 
                                        sticky=(tk.W, tk.E), pady=(0, 10))
        self.upscaler_progress_frame.columnconfigure(0, weight=1)
        
        self.upscaler_progress_bar = ttk.Progressbar(self.upscaler_progress_frame, mode='indeterminate')
        self.upscaler_progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        
        self.upscaler_status_label = ttk.Label(self.upscaler_progress_frame, text="Ready to upscale")
        self.upscaler_status_label.grid(row=1, column=0, sticky=tk.W)
        
        # Results section for upscaler
        self.upscaler_results_frame = ttk.LabelFrame(self.upscaler_frame, text="Results", padding="10")
        self.upscaler_results_frame.grid(row=6, column=0, columnspan=2, 
                                       sticky=(tk.W, tk.E), pady=(0, 10))
        self.upscaler_results_frame.columnconfigure(0, weight=1)
        
        self.upscaler_result_text = tk.Text(self.upscaler_results_frame, height=4, wrap=tk.WORD, 
                                          font=('Arial', 10), state=tk.DISABLED)
        self.upscaler_result_text.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        upscaler_result_scroll = ttk.Scrollbar(self.upscaler_results_frame, orient="vertical", 
                                             command=self.upscaler_result_text.yview)
        upscaler_result_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.upscaler_result_text.configure(yscrollcommand=upscaler_result_scroll.set)
        
        # Initially hide progress and results for upscaler
        self.upscaler_progress_frame.grid_remove()
        self.upscaler_results_frame.grid_remove()
        
        # Setup drag and drop for upscaler
        self.setup_upscaler_drag_and_drop()
        
    def setup_drag_and_drop(self):
        """Setup drag and drop functionality"""
        if not DND_AVAILABLE:
            # Update label to indicate drag and drop is not available
            self.original_image_label.config(text="📁 Click 'Browse Image' to select\n\nSupported formats: PNG, JPG, JPEG, GIF, BMP, WebP")
            return
            
        try:
            # Enable drag and drop on the drop frame
            self.drop_frame.drop_target_register(DND_FILES)
            self.drop_frame.dnd_bind('<<Drop>>', self.on_drop)
            self.drop_frame.dnd_bind('<<DragEnter>>', self.on_drag_enter_dnd)
            self.drop_frame.dnd_bind('<<DragLeave>>', self.on_drag_leave_dnd)
            
            # Add visual feedback for hover operations
            self.drop_frame.bind('<Enter>', self.on_hover_enter)
            self.drop_frame.bind('<Leave>', self.on_hover_leave)
            self.original_image_label.bind('<Button-1>', lambda e: self.select_image())
            
        except Exception as e:
            print(f"Drag and drop setup failed: {e}")
            # Update label to indicate drag and drop failed
            self.original_image_label.config(text="📁 Click 'Browse Image' to select\n\nSupported formats: PNG, JPG, JPEG, GIF, BMP, WebP")
    
    def on_drag_enter_dnd(self, event):
        """Visual feedback when drag enters drop zone"""
        self.drop_frame.config(bg='#e8f4f8', relief='solid', bd=3)
        self.original_image_label.config(bg='#e8f4f8', text="🎯 Drop image here!")
        
    def on_drag_leave_dnd(self, event):
        """Visual feedback when drag leaves drop zone"""
        self.drop_frame.config(bg='#f8f8f8', relief='groove', bd=2)
        if not self.selected_image_path:
            self.original_image_label.config(bg='#f8f8f8', 
                text="📁 Drop image here or click 'Browse Image'\n\nSupported formats: PNG, JPG, JPEG, GIF, BMP, WebP")
            
    def on_hover_enter(self, event):
        """Visual feedback when mouse hovers over drop zone"""
        if not self.selected_image_path:
            self.drop_frame.config(bg='#f0f8ff', relief='solid')
        
    def on_hover_leave(self, event):
        """Visual feedback when mouse leaves drop zone"""
        if not self.selected_image_path:
            self.drop_frame.config(bg='#f8f8f8', relief='groove')
            
    def on_drop(self, event):
        """Handle files dropped on the application"""
        files = event.data.split()
        if files:
            # Take the first file if multiple are dropped
            file_path = files[0]
            # Remove curly braces if present (Windows paths)
            if file_path.startswith('{') and file_path.endswith('}'):
                file_path = file_path[1:-1]
            self.handle_dropped_file(file_path)
        
    def handle_dropped_file(self, file_path):
        """Handle file dropped onto the application"""
        # Validate file extension
        valid_extensions = ('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp')
        if not file_path.lower().endswith(valid_extensions):
            messagebox.showerror("Invalid File", 
                               f"Please drop an image file.\nSupported formats: {', '.join(valid_extensions)}")
            return
            
        # Check if file exists
        if not os.path.exists(file_path):
            messagebox.showerror("File Not Found", f"The file does not exist:\n{file_path}")
            return
            
        # Process the dropped file same as browse selection
        self.selected_image_path = file_path
        self.image_path_label.config(text=os.path.basename(file_path), foreground="black")
        self.load_image_preview(file_path)
        
    def select_image(self):
        file_path = filedialog.askopenfilename(
            title="Select an image",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.gif *.bmp *.webp"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            self.selected_image_path = file_path
            self.image_path_label.config(text=os.path.basename(file_path), 
                                        foreground="black")
            self.load_image_preview(file_path)
            
    def load_image_preview(self, image_path):
        try:
            # Open and resize image for preview
            with Image.open(image_path) as img:
                # Store original image for comparison
                self.original_image = img.copy()
                
                # Calculate size maintaining aspect ratio
                max_size = (350, 250)
                img.thumbnail(max_size, Image.Resampling.LANCZOS)
                
                # Convert to PhotoImage
                photo = ImageTk.PhotoImage(img)
                
                # Update original image label
                self.original_image_label.config(image=photo, text="")
                self.original_image_label.image = photo  # Keep a reference
                
                # Clear result image when new original is loaded
                self.result_image_label.config(text="No result yet", image="")
                self.result_image_label.image = None
                self.save_button.config(state="disabled")
                self.use_result_button.config(state="disabled")
                
        except Exception as e:
            self.original_image_label.config(text=f"Error loading image: {str(e)}", image="")
            self.original_image_label.image = None
            
    def upload_image_to_api(self, image_path):
        """Upload image and return URL (placeholder - you may need to implement actual upload)"""
        # For now, we'll use a placeholder URL
        # In a real implementation, you might need to upload to a temporary storage
        # or use base64 encoding if the API supports it
        return "https://example.com/uploaded-image.png"
        
    def process_image(self):
        if not self.api_key:
            messagebox.showerror("Error", "API key not found. Please set WAVESPEED_API_KEY in your .env file.")
            return
            
        if not self.selected_image_path:
            messagebox.showerror("Error", "Please select an image first.")
            return
            
        prompt = self.prompt_text.get("1.0", tk.END).strip()
        if not prompt:
            messagebox.showerror("Error", "Please enter a prompt.")
            return
            
        # Disable the process button
        self.process_button.config(state="disabled")
        
        # Show progress
        self.progress_frame.grid()
        self.results_frame.grid_remove()
        self.progress_bar.start()
        self.status_label.config(text="Starting image processing...")
        
        # Start processing in a separate thread
        thread = threading.Thread(target=self.process_image_thread, 
                                 args=(self.selected_image_path, prompt))
        thread.daemon = True
        thread.start()
        
    def process_image_thread(self, image_path, prompt):
        try:
            # Update status
            self.root.after(0, lambda: self.status_label.config(text="Converting image to base64..."))
            
            # Convert the selected image to base64
            image_base64 = self.convert_image_to_base64(image_path)
            if not image_base64:
                self.root.after(0, lambda: self.handle_error("Failed to convert image to base64"))
                return
            
            # Prepare API request
            url = "https://api.wavespeed.ai/api/v3/google/nano-banana/edit"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            }
            payload = {
                "enable_base64_output": False,
                "enable_sync_mode": False,
                "images": [f"data:image/png;base64,{image_base64}"],
                "output_format": self.format_var.get(),
                "prompt": prompt
            }
            
            # Update status
            self.root.after(0, lambda: self.status_label.config(text="Sending request to API..."))
            
            begin = time.time()
            response = requests.post(url, headers=headers, data=json.dumps(payload))
            
            if response.status_code == 200:
                result = response.json()["data"]
                request_id = result["id"]
                self.current_request_id = request_id
                
                self.root.after(0, lambda: self.status_label.config(
                    text=f"Task submitted. Request ID: {request_id}"))
                
                # Poll for results
                self.poll_for_results(request_id, begin)
                
            else:
                error_msg = f"API Error: {response.status_code}, {response.text}"
                self.root.after(0, lambda: self.handle_error(error_msg))
                
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            self.root.after(0, lambda: self.handle_error(error_msg))
            
    def poll_for_results(self, request_id, start_time):
        try:
            url = f"https://api.wavespeed.ai/api/v3/predictions/{request_id}/result"
            headers = {"Authorization": f"Bearer {self.api_key}"}
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                result = response.json()["data"]
                status = result["status"]
                
                if status == "completed":
                    end_time = time.time()
                    duration = end_time - start_time
                    output_url = result["outputs"][0]
                    
                    self.root.after(0, lambda: self.handle_success(output_url, duration))
                    
                elif status == "failed":
                    error_msg = f"Task failed: {result.get('error', 'Unknown error')}"
                    self.root.after(0, lambda: self.handle_error(error_msg))
                    
                else:
                    # Still processing
                    self.root.after(0, lambda: self.status_label.config(
                        text=f"Processing... Status: {status}"))
                    
                    # Continue polling
                    self.root.after(1000, lambda: self.poll_for_results(request_id, start_time))
                    
            else:
                error_msg = f"Polling error: {response.status_code}, {response.text}"
                self.root.after(0, lambda: self.handle_error(error_msg))
                
        except Exception as e:
            error_msg = f"Polling error: {str(e)}"
            self.root.after(0, lambda: self.handle_error(error_msg))
            
    def handle_success(self, output_url, duration):
        self.progress_bar.stop()
        self.progress_frame.grid_remove()
        self.results_frame.grid()
        
        # Store result URL
        self.result_image_url = output_url
        
        # Display results
        result_message = f"✓ Task completed successfully!\n"
        result_message += f"Processing time: {duration:.2f} seconds\n"
        result_message += f"Result URL: {output_url}\n\n"
        result_message += "The edited image is displayed above. You can save it using the 'Save Result Image' button."
        
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete("1.0", tk.END)
        self.result_text.insert("1.0", result_message)
        self.result_text.config(state=tk.DISABLED)
        
        # Download and display result image
        self.download_and_display_result(output_url)
        
        # Re-enable process button
        self.process_button.config(state="normal")
        
        # Show success message
        messagebox.showinfo("Success", f"Image processed successfully in {duration:.2f} seconds!")
        
    def handle_error(self, error_message):
        self.progress_bar.stop()
        self.progress_frame.grid_remove()
        self.results_frame.grid()
        
        # Display error
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete("1.0", tk.END)
        self.result_text.insert("1.0", f"✗ Error: {error_message}")
        self.result_text.config(state=tk.DISABLED)
        
        # Re-enable process button
        self.process_button.config(state="normal")
        
        # Show error message
        messagebox.showerror("Error", error_message)
        
    def download_and_display_result(self, image_url):
        """Download the result image and display it in the GUI"""
        try:
            # Update status
            self.status_label.config(text="Downloading result image...")
            
            # Download image in a separate thread to avoid blocking UI
            thread = threading.Thread(target=self.download_result_thread, args=(image_url,))
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            self.result_image_label.config(text=f"Error downloading image: {str(e)}")
            
    def download_result_thread(self, image_url):
        """Download image in background thread"""
        try:
            # Download the image
            with urlopen(image_url) as response:
                image_data = response.read()
                
            # Open image with PIL
            image = Image.open(io.BytesIO(image_data))
            self.result_image = image.copy()  # Store full resolution image
            
            # Create thumbnail for display
            display_image = image.copy()
            max_size = (350, 250)
            display_image.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Convert to PhotoImage
            photo = ImageTk.PhotoImage(display_image)
            
            # Update UI in main thread
            self.root.after(0, lambda: self.display_result_image(photo))
            
        except Exception as e:
            error_msg = f"Error downloading result: {str(e)}"
            self.root.after(0, lambda: self.result_image_label.config(text=error_msg))
            
    def display_result_image(self, photo):
        """Display the result image in the GUI"""
        self.result_image_label.config(image=photo, text="")
        self.result_image_label.image = photo  # Keep a reference
        self.save_button.config(state="normal")  # Enable save button
        self.use_result_button.config(state="normal")  # Enable use as input button
        self.status_label.config(text="Result image loaded successfully!")
        
    def save_result_image(self):
        """Save the result image to a file"""
        if not self.result_image:
            messagebox.showerror("Error", "No result image to save.")
            return
            
        # Ask user where to save
        file_path = filedialog.asksaveasfilename(
            title="Save Result Image",
            defaultextension=".png",
            filetypes=[
                ("PNG files", "*.png"),
                ("JPEG files", "*.jpg"),
                ("WebP files", "*.webp"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            try:
                # Determine format from extension
                format_map = {
                    '.png': 'PNG',
                    '.jpg': 'JPEG',
                    '.jpeg': 'JPEG',
                    '.webp': 'WEBP'
                }
                
                ext = os.path.splitext(file_path)[1].lower()
                save_format = format_map.get(ext, 'PNG')
                
                # Save the image
                self.result_image.save(file_path, format=save_format)
                messagebox.showinfo("Success", f"Image saved successfully to:\n{file_path}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save image: {str(e)}")
                
    def convert_image_to_base64(self, image_path):
        """Convert image file to base64 string"""
        try:
            with Image.open(image_path) as img:
                # Convert to RGB if necessary
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")
                
                # Save to bytes buffer
                buffer = io.BytesIO()
                img.save(buffer, format="PNG")
                
                # Encode to base64
                image_base64 = base64.b64encode(buffer.getvalue()).decode()
                return image_base64
                
        except Exception as e:
            print(f"Error converting image to base64: {e}")
            return None
            
    def use_result_as_input(self):
        """Use the result image as the next input image"""
        if not self.result_image:
            messagebox.showerror("Error", "No result image available.")
            return
            
        try:
            # Save result image temporarily
            temp_path = "temp_result_image.png"
            self.result_image.save(temp_path, format="PNG")
            
            # Load it as the new input
            self.selected_image_path = temp_path
            self.image_path_label.config(text="Result Image (temp)", foreground="blue")
            self.load_image_preview(temp_path)
            
            messagebox.showinfo("Success", "Result image is now set as the input image!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to use result as input: {str(e)}")
    
    # ===== UPSCALER FUNCTIONALITY =====
    
    def setup_upscaler_drag_and_drop(self):
        """Setup drag and drop functionality for upscaler tab"""
        if not DND_AVAILABLE:
            return
            
        try:
            # Enable drag and drop on the upscaler drop frame
            self.upscaler_drop_frame.drop_target_register(DND_FILES)
            self.upscaler_drop_frame.dnd_bind('<<Drop>>', self.on_upscaler_drop)
            self.upscaler_drop_frame.dnd_bind('<<DragEnter>>', self.on_upscaler_drag_enter)
            self.upscaler_drop_frame.dnd_bind('<<DragLeave>>', self.on_upscaler_drag_leave)
            
            # Add visual feedback for hover operations
            self.upscaler_drop_frame.bind('<Enter>', self.on_upscaler_hover_enter)
            self.upscaler_drop_frame.bind('<Leave>', self.on_upscaler_hover_leave)
            self.upscaler_original_image_label.bind('<Button-1>', lambda e: self.select_upscaler_image())
            
        except Exception as e:
            print(f"Upscaler drag and drop setup failed: {e}")
    
    def on_upscaler_drag_enter(self, event):
        """Visual feedback when drag enters upscaler drop zone"""
        self.upscaler_drop_frame.config(bg='#e8f4f8', relief='solid', bd=3)
        self.upscaler_original_image_label.config(bg='#e8f4f8', text="🎯 Drop image here!")
        
    def on_upscaler_drag_leave(self, event):
        """Visual feedback when drag leaves upscaler drop zone"""
        self.upscaler_drop_frame.config(bg='#f8f8f8', relief='groove', bd=2)
        if not self.upscaler_selected_image_path:
            self.upscaler_original_image_label.config(bg='#f8f8f8', 
                text="📁 Click 'Browse Image' to select\n\nSupported formats: PNG, JPG, JPEG, GIF, BMP, WebP")
            
    def on_upscaler_hover_enter(self, event):
        """Visual feedback when mouse hovers over upscaler drop zone"""
        if not self.upscaler_selected_image_path:
            self.upscaler_drop_frame.config(bg='#f0f8ff', relief='solid')
        
    def on_upscaler_hover_leave(self, event):
        """Visual feedback when mouse leaves upscaler drop zone"""
        if not self.upscaler_selected_image_path:
            self.upscaler_drop_frame.config(bg='#f8f8f8', relief='groove')
            
    def on_upscaler_drop(self, event):
        """Handle files dropped on the upscaler application"""
        files = event.data.split()
        if files:
            file_path = files[0]
            if file_path.startswith('{') and file_path.endswith('}'):
                file_path = file_path[1:-1]
            self.handle_upscaler_dropped_file(file_path)
        
    def handle_upscaler_dropped_file(self, file_path):
        """Handle file dropped onto the upscaler application"""
        valid_extensions = ('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp')
        if not file_path.lower().endswith(valid_extensions):
            messagebox.showerror("Invalid File", 
                               f"Please drop an image file.\nSupported formats: {', '.join(valid_extensions)}")
            return
            
        if not os.path.exists(file_path):
            messagebox.showerror("File Not Found", f"The file does not exist:\n{file_path}")
            return
            
        self.upscaler_selected_image_path = file_path
        self.upscaler_image_path_label.config(text=os.path.basename(file_path), foreground="black")
        self.load_upscaler_image_preview(file_path)
        
    def select_upscaler_image(self):
        """Select image for upscaling"""
        file_path = filedialog.askopenfilename(
            title="Select an image to upscale",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.gif *.bmp *.webp"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            self.upscaler_selected_image_path = file_path
            self.upscaler_image_path_label.config(text=os.path.basename(file_path), 
                                                foreground="black")
            self.load_upscaler_image_preview(file_path)
            
    def load_upscaler_image_preview(self, image_path):
        """Load image preview for upscaler"""
        try:
            with Image.open(image_path) as img:
                self.upscaler_original_image = img.copy()
                
                max_size = (350, 250)
                img.thumbnail(max_size, Image.Resampling.LANCZOS)
                
                photo = ImageTk.PhotoImage(img)
                
                self.upscaler_original_image_label.config(image=photo, text="")
                self.upscaler_original_image_label.image = photo
                
                # Clear result image when new original is loaded
                self.upscaler_result_image_label.config(text="No result yet", image="")
                self.upscaler_result_image_label.image = None
                self.upscaler_save_button.config(state="disabled")
                self.upscaler_use_result_button.config(state="disabled")
                
        except Exception as e:
            self.upscaler_original_image_label.config(text=f"Error loading image: {str(e)}", image="")
            self.upscaler_original_image_label.image = None
            
    def process_upscaler_image(self):
        """Process image with upscaler API"""
        if not self.api_key:
            messagebox.showerror("Error", "API key not found. Please set WAVESPEED_API_KEY in your .env file.")
            return
            
        if not self.upscaler_selected_image_path:
            messagebox.showerror("Error", "Please select an image first.")
            return
            
        # Disable the process button
        self.upscaler_process_button.config(state="disabled")
        
        # Show progress
        self.upscaler_progress_frame.grid()
        self.upscaler_results_frame.grid_remove()
        self.upscaler_progress_bar.start()
        self.upscaler_status_label.config(text="Starting image upscaling...")
        
        # Start processing in a separate thread
        thread = threading.Thread(target=self.process_upscaler_image_thread, 
                                 args=(self.upscaler_selected_image_path,))
        thread.daemon = True
        thread.start()
        
    def process_upscaler_image_thread(self, image_path):
        """Process upscaler image in background thread"""
        try:
            # Update status
            self.root.after(0, lambda: self.upscaler_status_label.config(text="Uploading image..."))
            
            # For now, we'll use a URL approach - in a real implementation you might need to upload the image
            # This is a placeholder implementation - you may need to implement actual image upload
            image_url = self.upload_image_for_upscaler(image_path)
            if not image_url:
                self.root.after(0, lambda: self.handle_upscaler_error("Failed to prepare image for upscaling"))
                return
            
            # Prepare API request
            url = "https://api.wavespeed.ai/api/v3/wavespeed-ai/image-upscaler"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            }
            payload = {
                "creativity": int(self.upscaler_creativity_var.get()),
                "enable_base64_output": False,
                "enable_sync_mode": False,
                "image": image_url,
                "output_format": self.upscaler_format_var.get(),
                "target_resolution": self.upscaler_resolution_var.get()
            }
            
            # Update status
            self.root.after(0, lambda: self.upscaler_status_label.config(text="Sending request to API..."))
            
            begin = time.time()
            response = requests.post(url, headers=headers, data=json.dumps(payload))
            
            if response.status_code == 200:
                result = response.json()["data"]
                request_id = result["id"]
                self.upscaler_current_request_id = request_id
                
                self.root.after(0, lambda: self.upscaler_status_label.config(
                    text=f"Task submitted. Request ID: {request_id}"))
                
                # Poll for results
                self.poll_upscaler_results(request_id, begin)
                
            else:
                error_msg = f"API Error: {response.status_code}, {response.text}"
                self.root.after(0, lambda: self.handle_upscaler_error(error_msg))
                
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            self.root.after(0, lambda: self.handle_upscaler_error(error_msg))
            
    def upload_image_for_upscaler(self, image_path):
        """Upload image and return URL for upscaler"""
        # For the upscaler API, we need to provide a public URL to the image
        # Since the API expects a URL, you have several options:
        
        # Option 1: Use a service like imgur, cloudinary, or similar to upload the image
        # Option 2: Use a temporary file hosting service
        # Option 3: Host the image on your own server
        
        # For demonstration purposes, we'll use the sample URL from your documentation
        # In a production environment, you would implement actual image upload logic
        
        # This is the sample URL from your documentation
        sample_url = "https://d1q70pf5vjeyhc.cloudfront.net/media/6af332dfb8b245f4bd44fc6389f5a86a/images/1756969345097954105_vYnmieb7.jpg"
        
        # TODO: Implement actual image upload logic here
        # For now, return the sample URL to demonstrate the API integration
        print(f"Note: Using sample URL for demonstration. In production, upload {image_path} to a public URL.")
        return sample_url
        
    def poll_upscaler_results(self, request_id, start_time):
        """Poll for upscaler results"""
        try:
            url = f"https://api.wavespeed.ai/api/v3/predictions/{request_id}/result"
            headers = {"Authorization": f"Bearer {self.api_key}"}
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                result = response.json()["data"]
                status = result["status"]
                
                if status == "completed":
                    end_time = time.time()
                    duration = end_time - start_time
                    output_url = result["outputs"][0]
                    
                    self.root.after(0, lambda: self.handle_upscaler_success(output_url, duration))
                    
                elif status == "failed":
                    error_msg = f"Task failed: {result.get('error', 'Unknown error')}"
                    self.root.after(0, lambda: self.handle_upscaler_error(error_msg))
                    
                else:
                    # Still processing
                    self.root.after(0, lambda: self.upscaler_status_label.config(
                        text=f"Processing... Status: {status}"))
                    
                    # Continue polling
                    self.root.after(1000, lambda: self.poll_upscaler_results(request_id, start_time))
                    
            else:
                error_msg = f"Polling error: {response.status_code}, {response.text}"
                self.root.after(0, lambda: self.handle_upscaler_error(error_msg))
                
        except Exception as e:
            error_msg = f"Polling error: {str(e)}"
            self.root.after(0, lambda: self.handle_upscaler_error(error_msg))
            
    def handle_upscaler_success(self, output_url, duration):
        """Handle successful upscaler completion"""
        self.upscaler_progress_bar.stop()
        self.upscaler_progress_frame.grid_remove()
        self.upscaler_results_frame.grid()
        
        # Store result URL
        self.upscaler_result_image_url = output_url
        
        # Display results
        result_message = f"✓ Upscaling completed successfully!\n"
        result_message += f"Processing time: {duration:.2f} seconds\n"
        result_message += f"Result URL: {output_url}\n\n"
        result_message += "The upscaled image is displayed above. You can save it or use it in the editor."
        
        self.upscaler_result_text.config(state=tk.NORMAL)
        self.upscaler_result_text.delete("1.0", tk.END)
        self.upscaler_result_text.insert("1.0", result_message)
        self.upscaler_result_text.config(state=tk.DISABLED)
        
        # Download and display result image
        self.download_and_display_upscaler_result(output_url)
        
        # Re-enable process button
        self.upscaler_process_button.config(state="normal")
        
        # Show success message
        messagebox.showinfo("Success", f"Image upscaled successfully in {duration:.2f} seconds!")
        
    def handle_upscaler_error(self, error_message):
        """Handle upscaler error"""
        self.upscaler_progress_bar.stop()
        self.upscaler_progress_frame.grid_remove()
        self.upscaler_results_frame.grid()
        
        # Display error
        self.upscaler_result_text.config(state=tk.NORMAL)
        self.upscaler_result_text.delete("1.0", tk.END)
        self.upscaler_result_text.insert("1.0", f"✗ Error: {error_message}")
        self.upscaler_result_text.config(state=tk.DISABLED)
        
        # Re-enable process button
        self.upscaler_process_button.config(state="normal")
        
        # Show error message
        messagebox.showerror("Error", error_message)
        
    def download_and_display_upscaler_result(self, image_url):
        """Download the upscaler result image and display it in the GUI"""
        try:
            self.upscaler_status_label.config(text="Downloading result image...")
            
            thread = threading.Thread(target=self.download_upscaler_result_thread, args=(image_url,))
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            self.upscaler_result_image_label.config(text=f"Error downloading image: {str(e)}")
            
    def download_upscaler_result_thread(self, image_url):
        """Download upscaler image in background thread"""
        try:
            with urlopen(image_url) as response:
                image_data = response.read()
                
            image = Image.open(io.BytesIO(image_data))
            self.upscaler_result_image = image.copy()
            
            display_image = image.copy()
            max_size = (350, 250)
            display_image.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            photo = ImageTk.PhotoImage(display_image)
            
            self.root.after(0, lambda: self.display_upscaler_result_image(photo))
            
        except Exception as e:
            error_msg = f"Error downloading result: {str(e)}"
            self.root.after(0, lambda: self.upscaler_result_image_label.config(text=error_msg))
            
    def display_upscaler_result_image(self, photo):
        """Display the upscaler result image in the GUI"""
        self.upscaler_result_image_label.config(image=photo, text="")
        self.upscaler_result_image_label.image = photo
        self.upscaler_save_button.config(state="normal")
        self.upscaler_use_result_button.config(state="normal")
        self.upscaler_status_label.config(text="Result image loaded successfully!")
        
    def save_upscaler_result_image(self):
        """Save the upscaler result image to a file"""
        if not self.upscaler_result_image:
            messagebox.showerror("Error", "No result image to save.")
            return
            
        file_path = filedialog.asksaveasfilename(
            title="Save Upscaled Result Image",
            defaultextension=".png",
            filetypes=[
                ("PNG files", "*.png"),
                ("JPEG files", "*.jpg"),
                ("WebP files", "*.webp"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            try:
                format_map = {
                    '.png': 'PNG',
                    '.jpg': 'JPEG',
                    '.jpeg': 'JPEG',
                    '.webp': 'WEBP'
                }
                
                ext = os.path.splitext(file_path)[1].lower()
                save_format = format_map.get(ext, 'PNG')
                
                self.upscaler_result_image.save(file_path, format=save_format)
                messagebox.showinfo("Success", f"Upscaled image saved successfully to:\n{file_path}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save image: {str(e)}")
                
    def use_upscaler_result_as_editor_input(self):
        """Use the upscaler result image as input for the editor tab"""
        if not self.upscaler_result_image:
            messagebox.showerror("Error", "No upscaled result image available.")
            return
            
        try:
            # Save upscaler result image temporarily
            temp_path = "temp_upscaled_image.png"
            self.upscaler_result_image.save(temp_path, format="PNG")
            
            # Switch to editor tab
            self.notebook.select(self.editor_frame)
            
            # Load it as the new input in the editor
            self.selected_image_path = temp_path
            self.image_path_label.config(text="Upscaled Image (temp)", foreground="blue")
            self.load_image_preview(temp_path)
            
            messagebox.showinfo("Success", "Upscaled image is now set as the editor input image!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to use upscaled result as editor input: {str(e)}")
            
    def load_prompts(self):
        """Load saved prompts from JSON file"""
        try:
            if os.path.exists(self.prompts_file):
                with open(self.prompts_file, 'r') as f:
                    return json.load(f)
            return []
        except Exception as e:
            print(f"Error loading prompts: {e}")
            return []
            
    def save_prompts(self):
        """Save prompts to JSON file"""
        try:
            with open(self.prompts_file, 'w') as f:
                json.dump(self.saved_prompts, f, indent=2)
        except Exception as e:
            print(f"Error saving prompts: {e}")
            
    def refresh_prompts_list(self):
        """Refresh the prompts listbox"""
        self.prompts_listbox.delete(0, tk.END)
        for prompt in self.saved_prompts:
            # Show first 50 characters of each prompt
            display_text = prompt[:50] + "..." if len(prompt) > 50 else prompt
            self.prompts_listbox.insert(tk.END, display_text)
            
    def save_current_prompt(self):
        """Save the current prompt to the list"""
        current_prompt = self.prompt_text.get("1.0", tk.END).strip()
        if not current_prompt:
            messagebox.showwarning("Warning", "Please enter a prompt first.")
            return
            
        if current_prompt in self.saved_prompts:
            messagebox.showinfo("Info", "This prompt is already saved.")
            return
            
        self.saved_prompts.append(current_prompt)
        self.save_prompts()
        self.refresh_prompts_list()
        messagebox.showinfo("Success", "Prompt saved successfully!")
        
    def use_selected_prompt(self):
        """Use the selected prompt from the list"""
        selection = self.prompts_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a prompt first.")
            return
            
        selected_prompt = self.saved_prompts[selection[0]]
        self.prompt_text.delete("1.0", tk.END)
        self.prompt_text.insert("1.0", selected_prompt)
        
    def delete_selected_prompt(self):
        """Delete the selected prompt from the list"""
        selection = self.prompts_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a prompt to delete.")
            return
            
        selected_prompt = self.saved_prompts[selection[0]]
        result = messagebox.askyesno("Confirm Delete", 
                                   f"Are you sure you want to delete this prompt?\n\n{selected_prompt[:100]}...")
        
        if result:
            del self.saved_prompts[selection[0]]
            self.save_prompts()
            self.refresh_prompts_list()
            messagebox.showinfo("Success", "Prompt deleted successfully!")

def main():
    if DND_AVAILABLE:
        root = TkinterDnD.Tk()
    else:
        root = tk.Tk()
    app = ImageEditorGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
