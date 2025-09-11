"""
Seedream V4 Tab Component - Multi-Modal Image Generation
For WaveSpeed AI Creative Suite

This module contains the ByteDance Seedream V4 image editing functionality.
Seedream 4.0: Surpassing nano banana in every aspect with multi-modal support.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os
import json
from PIL import Image, ImageTk
from ui.components.ui_components import BaseTab
from utils.utils import *
from core.auto_save import auto_save_manager
from core.secure_upload import privacy_uploader
from core.logger import get_logger

logger = get_logger()


class SeedreamV4Tab(BaseTab):
    """Seedream V4 Multi-Modal Image Editor Tab"""
    
    def __init__(self, parent_frame, api_client, main_app=None):
        self.result_image = None
        self.main_app = main_app
        self.images = []  # List of image URLs/paths for multi-modal support
        self.image_widgets = []  # UI widgets for image management
        
        # Prompt storage for Seedream V4
        self.seedream_v4_prompts_file = "data/seedream_v4_prompts.json"
        self.saved_seedream_v4_prompts = load_json_file(self.seedream_v4_prompts_file, [])
        
        super().__init__(parent_frame, api_client)
    
    def apply_ai_suggestion(self, improved_prompt: str):
        """Apply AI suggestion to prompt text"""
        self.prompt_text.delete("1.0", tk.END)
        self.prompt_text.insert("1.0", improved_prompt)
    
    def setup_ui(self):
        """Setup the comprehensive Seedream V4 UI"""
        # Hide the scrollable canvas components since we're using direct container layout
        self.canvas.pack_forget()
        self.scrollbar.pack_forget()
        
        # Create main container with proper layout
        self.main_container = ttk.Frame(self.container)
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Configure grid weights
        self.main_container.columnconfigure(0, weight=1)
        self.main_container.columnconfigure(1, weight=2)
        self.main_container.rowconfigure(0, weight=1)
        
        # Create left panel for controls
        self.create_left_panel()
        
        # Create right panel for image display
        self.create_right_panel()
        
        # Setup status section
        self.setup_status_section()
    
    def create_left_panel(self):
        """Create the left control panel"""
        self.left_panel = ttk.Frame(self.main_container)
        self.left_panel.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        self.left_panel.columnconfigure(0, weight=1)
        
        # Title
        title_label = ttk.Label(
            self.left_panel, 
            text="🌟 Seedream V4", 
            font=('Arial', 14, 'bold')
        )
        title_label.pack(pady=(0, 10))
        
        # Prompt section
        self.create_prompt_section()
        
        # Images section
        self.create_images_section()
        
        # Settings section
        self.create_settings_section()
        
        # Action buttons
        self.create_action_buttons()
    
    def create_prompt_section(self):
        """Create the prompt input section"""
        prompt_frame = ttk.LabelFrame(self.left_panel, text="Prompt", padding=10)
        prompt_frame.pack(fill=tk.X, pady=(0, 10))
        prompt_frame.columnconfigure(0, weight=1)
        
        # Prompt text area
        self.prompt_text = tk.Text(
            prompt_frame, 
            height=4, 
            wrap=tk.WORD, 
            font=('Arial', 10)
        )
        self.prompt_text.pack(fill=tk.X, pady=(0, 5))
        
        # Prompt guidance
        guidance_text = """💡 Prompt Writing Guide:
• Use clear instructions: "change action + change object + target feature"
• For multiple images: "a series of", "group of images"
• Be specific and detailed for best results"""
        
        guidance_label = ttk.Label(
            prompt_frame, 
            text=guidance_text, 
            font=('Arial', 8), 
            foreground="gray",
            wraplength=300
        )
        guidance_label.pack(anchor=tk.W, pady=(5, 0))
        
        # AI enhancement buttons
        ai_frame = ttk.Frame(prompt_frame)
        ai_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Button(
            ai_frame, 
            text="✨ Improve with AI", 
            command=self.improve_prompt_with_ai
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(
            ai_frame, 
            text="🛡️ Filter Training", 
            command=self.show_filter_training
        ).pack(side=tk.LEFT)
    
    def create_images_section(self):
        """Create the multi-image input section"""
        images_frame = ttk.LabelFrame(self.left_panel, text="Images", padding=10)
        images_frame.pack(fill=tk.X, pady=(0, 10))
        images_frame.columnconfigure(0, weight=1)
        
        # Images list container
        self.images_container = ttk.Frame(images_frame)
        self.images_container.pack(fill=tk.X, pady=(0, 10))
        
        # Add item button
        add_button = ttk.Button(
            images_frame, 
            text="+ Add Item", 
            command=self.add_image_item
        )
        add_button.pack(fill=tk.X)
        
        # Add initial image item
        self.add_image_item()
    
    def create_settings_section(self):
        """Create the settings section"""
        settings_frame = ttk.LabelFrame(self.left_panel, text="Settings", padding=10)
        settings_frame.pack(fill=tk.X, pady=(0, 10))
        settings_frame.columnconfigure(1, weight=1)
        
        # Size setting
        size_frame = ttk.Frame(settings_frame)
        size_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 5))
        size_frame.columnconfigure(1, weight=1)
        size_frame.columnconfigure(2, weight=1)
        
        ttk.Label(size_frame, text="Size:", font=('Arial', 9)).grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        
        # Width
        ttk.Label(size_frame, text="Width:").grid(row=0, column=1, sticky=tk.W, padx=(5, 0))
        self.width_var = tk.StringVar(value="2048")
        width_scale = ttk.Scale(
            size_frame, 
            from_=1024, 
            to=4096, 
            variable=self.width_var, 
            orient=tk.HORIZONTAL,
            command=self.update_size_display
        )
        width_scale.grid(row=0, column=2, sticky=(tk.W, tk.E), padx=(5, 0))
        
        self.width_entry = ttk.Entry(size_frame, textvariable=self.width_var, width=8)
        self.width_entry.grid(row=0, column=3, padx=(5, 0))
        
        # Height
        height_frame = ttk.Frame(settings_frame)
        height_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 5))
        height_frame.columnconfigure(1, weight=1)
        height_frame.columnconfigure(2, weight=1)
        
        ttk.Label(height_frame, text="Height:").grid(row=0, column=1, sticky=tk.W, padx=(5, 0))
        self.height_var = tk.StringVar(value="2048")
        height_scale = ttk.Scale(
            height_frame, 
            from_=1024, 
            to=4096, 
            variable=self.height_var, 
            orient=tk.HORIZONTAL,
            command=self.update_size_display
        )
        height_scale.grid(row=0, column=2, sticky=(tk.W, tk.E), padx=(5, 0))
        
        self.height_entry = ttk.Entry(height_frame, textvariable=self.height_var, width=8)
        self.height_entry.grid(row=0, column=3, padx=(5, 0))
        
        # Seed setting
        seed_frame = ttk.Frame(settings_frame)
        seed_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 0))
        seed_frame.columnconfigure(1, weight=1)
        
        ttk.Label(seed_frame, text="Seed:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.seed_var = tk.StringVar(value="1490001329")
        self.seed_entry = ttk.Entry(seed_frame, textvariable=self.seed_var, width=15)
        self.seed_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 0))
        
        # Random seed button
        random_seed_btn = ttk.Button(
            seed_frame, 
            text="🎲", 
            command=self.generate_random_seed,
            width=3
        )
        random_seed_btn.grid(row=0, column=2, padx=(5, 0))
        
        # Advanced settings
        advanced_frame = ttk.Frame(settings_frame)
        advanced_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        self.enable_sync_mode = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            advanced_frame, 
            text="Enable Sync Mode", 
            variable=self.enable_sync_mode
        ).pack(anchor=tk.W)
        
        self.enable_base64_output = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            advanced_frame, 
            text="Enable Base64 Output", 
            variable=self.enable_base64_output
        ).pack(anchor=tk.W)
    
    def create_action_buttons(self):
        """Create action buttons"""
        buttons_frame = ttk.Frame(self.left_panel)
        buttons_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Main action button
        self.process_button = ttk.Button(
            buttons_frame, 
            text="🌟 Apply Seedream V4", 
            command=self.process_task,
            style="Accent.TButton"
        )
        self.process_button.pack(fill=tk.X, pady=(0, 5))
        
        # Secondary buttons
        secondary_frame = ttk.Frame(buttons_frame)
        secondary_frame.pack(fill=tk.X)
        
        ttk.Button(
            secondary_frame, 
            text="Clear", 
            command=self.clear_all
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(
            secondary_frame, 
            text="Sample", 
            command=self.load_sample_prompt
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(
            secondary_frame, 
            text="Save Prompt", 
            command=self.save_current_prompt
        ).pack(side=tk.LEFT)
    
    def create_right_panel(self):
        """Create the right panel for image display"""
        self.right_panel = ttk.Frame(self.main_container)
        self.right_panel.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.right_panel.columnconfigure(0, weight=1)
        self.right_panel.rowconfigure(1, weight=1)
        
        # Result tabs
        self.result_notebook = ttk.Notebook(self.right_panel)
        self.result_notebook.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Input images tab
        self.input_frame = ttk.Frame(self.result_notebook)
        self.result_notebook.add(self.input_frame, text="Input Images")
        
        # Result tab
        self.result_frame = ttk.Frame(self.result_notebook)
        self.result_notebook.add(self.result_frame, text="Result")
        
        # Image display areas
        self.create_image_display_areas()
    
    def create_image_display_areas(self):
        """Create image display areas"""
        # Input images display
        self.input_canvas = tk.Canvas(
            self.input_frame, 
            bg='white', 
            height=200
        )
        self.input_canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Result display
        self.result_canvas = tk.Canvas(
            self.result_frame, 
            bg='white'
        )
        self.result_canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Initial display
        self.show_placeholder()
    
    def setup_status_section(self):
        """Setup status section"""
        self.status_frame = ttk.Frame(self.main_container)
        self.status_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        self.status_label = ttk.Label(
            self.status_frame, 
            text="Ready for Seedream V4", 
            font=('Arial', 10),
            foreground="green"
        )
        self.status_label.pack(side=tk.LEFT)
        
        self.progress_bar = ttk.Progressbar(
            self.status_frame, 
            mode='indeterminate'
        )
        # Progress bar initially hidden
    
    def add_image_item(self):
        """Add a new image item to the list"""
        item_frame = ttk.Frame(self.images_container)
        item_frame.pack(fill=tk.X, pady=(0, 5))
        item_frame.columnconfigure(1, weight=1)
        
        # URL/Path entry
        url_var = tk.StringVar()
        url_entry = ttk.Entry(item_frame, textvariable=url_var, width=40)
        url_entry.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # Thumbnail display
        thumbnail_label = ttk.Label(item_frame, text="No image", relief="solid", width=20)
        thumbnail_label.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # Buttons
        button_frame = ttk.Frame(item_frame)
        button_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        ttk.Button(
            button_frame, 
            text="📁 Browse", 
            command=lambda: self.browse_image_for_item(url_var, thumbnail_label)
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(
            button_frame, 
            text="🗑️ Delete", 
            command=lambda: self.remove_image_item(item_frame)
        ).pack(side=tk.LEFT)
        
        # Store references
        item_data = {
            'frame': item_frame,
            'url_var': url_var,
            'thumbnail_label': thumbnail_label,
            'image_path': None
        }
        self.image_widgets.append(item_data)
    
    def browse_image_for_item(self, url_var, thumbnail_label):
        """Browse for image file for a specific item"""
        file_path = filedialog.askopenfilename(
            title="Select Image",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.gif *.bmp *.webp"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            url_var.set(file_path)
            self.load_thumbnail(file_path, thumbnail_label)
            
            # Store the image path
            for item in self.image_widgets:
                if item['url_var'] == url_var:
                    item['image_path'] = file_path
                    break
    
    def load_thumbnail(self, image_path, thumbnail_label):
        """Load thumbnail for image"""
        try:
            # Load and resize image for thumbnail
            img = Image.open(image_path)
            img.thumbnail((100, 100), Image.Resampling.LANCZOS)
            
            # Convert to PhotoImage
            photo = ImageTk.PhotoImage(img)
            
            # Update label
            thumbnail_label.config(image=photo, text="")
            thumbnail_label.image = photo  # Keep a reference
            
        except Exception as e:
            logger.error(f"Error loading thumbnail: {e}")
            thumbnail_label.config(text="Error loading image")
    
    def remove_image_item(self, item_frame):
        """Remove an image item"""
        # Find and remove from widgets list
        for i, item in enumerate(self.image_widgets):
            if item['frame'] == item_frame:
                del self.image_widgets[i]
                break
        
        # Destroy the frame
        item_frame.destroy()
    
    def update_size_display(self, value=None):
        """Update size display when sliders change"""
        # This method is called when sliders change
        pass
    
    def generate_random_seed(self):
        """Generate a random seed"""
        import random
        random_seed = random.randint(0, 2147483647)
        self.seed_var.set(str(random_seed))
    
    def improve_prompt_with_ai(self):
        """Improve prompt using AI"""
        try:
            from ui.components.fixed_ai_settings import check_and_show_ai_unavailable_message
            
            if not check_and_show_ai_unavailable_message(self.main_container.winfo_toplevel()):
                return
            
            current_prompt = self.prompt_text.get("1.0", tk.END).strip()
            if not current_prompt:
                messagebox.showwarning("No Prompt", "Please enter a prompt first.")
                return
            
            # Show AI suggestions
            from ui.components.universal_ai_integration import universal_ai_integrator
            universal_ai_integrator._show_ai_suggestions(
                self.prompt_text, 
                "seedream_v4", 
                self
            )
            
        except Exception as e:
            logger.error(f"Error improving prompt: {e}")
            messagebox.showerror("Error", f"Failed to improve prompt: {str(e)}")
    
    def show_filter_training(self):
        """Show filter training mode"""
        try:
            from ui.components.fixed_ai_settings import check_and_show_ai_unavailable_message
            
            if not check_and_show_ai_unavailable_message(self.main_container.winfo_toplevel()):
                return
            
            result = messagebox.askyesno(
                "Filter Training Mode",
                "⚠️ WARNING: Filter Training Mode generates harmful prompt examples for safety filter development only.\n\n"
                "These examples are NEVER executed for generation - they are used to train safety filters.\n\n"
                "Do you want to continue?",
                icon="warning"
            )
            
            if not result:
                return
            
            current_prompt = self.prompt_text.get("1.0", tk.END).strip()
            if not current_prompt:
                messagebox.showwarning("No Prompt", "Please enter a prompt first.")
                return
            
            # Show filter training suggestions
            from ui.components.universal_ai_integration import universal_ai_integrator
            universal_ai_integrator._show_filter_training(
                self.prompt_text, 
                "seedream_v4", 
                self
            )
            
        except Exception as e:
            logger.error(f"Error showing filter training: {e}")
            messagebox.showerror("Error", f"Failed to show filter training: {str(e)}")
    
    def load_sample_prompt(self):
        """Load sample prompt"""
        sample_prompts = [
            "Replace the man in the frame with the face and head of the man from the reference photo. Keep the clothing, lighting, and background from the screen recording image unchanged.",
            "Transform the person into a Renaissance-style painting with oil paint texture and classical lighting",
            "Change the background to a futuristic cyberpunk cityscape with neon lights",
            "Convert this image to anime style with vibrant colors and stylized features",
            "Add magical elements like floating particles and glowing effects around the subject",
            "Transform the scene to vintage black and white photography with film grain"
        ]
        
        import random
        sample = random.choice(sample_prompts)
        self.prompt_text.delete("1.0", tk.END)
        self.prompt_text.insert("1.0", sample)
    
    def clear_all(self):
        """Clear all inputs"""
        self.prompt_text.delete("1.0", tk.END)
        
        # Clear all image items except the first one
        while len(self.image_widgets) > 1:
            self.remove_image_item(self.image_widgets[-1]['frame'])
        
        # Clear the first item
        if self.image_widgets:
            first_item = self.image_widgets[0]
            first_item['url_var'].set("")
            first_item['thumbnail_label'].config(image="", text="No image")
            first_item['image_path'] = None
    
    def save_current_prompt(self):
        """Save the current prompt"""
        prompt = self.prompt_text.get("1.0", tk.END).strip()
        if prompt and prompt not in self.saved_seedream_v4_prompts:
            self.saved_seedream_v4_prompts.append(prompt)
            save_json_file(self.seedream_v4_prompts_file, self.saved_seedream_v4_prompts)
            self.update_status("Prompt saved successfully")
    
    def show_placeholder(self):
        """Show placeholder text"""
        self.input_canvas.delete("all")
        self.input_canvas.create_text(
            self.input_canvas.winfo_width()//2, 
            self.input_canvas.winfo_height()//2,
            text="📷 Select images to edit\nDrag & drop supported",
            font=('Arial', 12),
            fill="gray"
        )
        
        self.result_canvas.delete("all")
        self.result_canvas.create_text(
            self.result_canvas.winfo_width()//2, 
            self.result_canvas.winfo_height()//2,
            text="🌟 Result will appear here after processing",
            font=('Arial', 12),
            fill="gray"
        )
    
    def process_task(self):
        """Process Seedream V4 task"""
        # Validation
        prompt = self.prompt_text.get("1.0", tk.END).strip()
        if not prompt:
            messagebox.showerror("No Prompt", "Please enter an editing instruction.")
            return
        
        # Collect images
        images = []
        for item in self.image_widgets:
            if item['image_path']:
                images.append(item['image_path'])
            elif item['url_var'].get().strip():
                images.append(item['url_var'].get().strip())
        
        if not images:
            messagebox.showerror("No Images", "Please add at least one image.")
            return
        
        # Validate size
        try:
            width = int(self.width_var.get())
            height = int(self.height_var.get())
            if not (1024 <= width <= 4096 and 1024 <= height <= 4096):
                raise ValueError("Size out of range")
        except ValueError:
            messagebox.showerror("Invalid Size", "Size must be between 1024 and 4096 pixels.")
            return
        
        # Validate seed
        try:
            seed = int(self.seed_var.get()) if self.seed_var.get().strip() != "-1" else -1
            if seed != -1 and not (0 <= seed <= 2147483647):
                raise ValueError("Seed out of range")
        except ValueError:
            messagebox.showerror("Invalid Seed", "Seed must be -1 for random or between 0 and 2147483647.")
            return
        
        # Start processing
        self.show_progress("Starting Seedream V4 processing...")
        
        # Start processing in background thread
        thread = threading.Thread(target=self.process_thread, args=(prompt, images, width, height, seed))
        thread.daemon = True
        thread.start()
    
    def process_thread(self, prompt, images, width, height, seed):
        """Process in background thread"""
        try:
            # Update status
            self.main_container.after(0, lambda: self.update_status("Preparing images..."))
            
            # Upload images
            image_urls = []
            for i, image_path in enumerate(images):
                if image_path.startswith('http'):
                    # Already a URL
                    image_urls.append(image_path)
                else:
                    # Upload local image
                    url = self.upload_image(image_path)
                    if url:
                        image_urls.append(url)
                    else:
                        self.main_container.after(0, lambda: self.handle_error("Failed to upload image"))
                        return
            
            if not image_urls:
                self.main_container.after(0, lambda: self.handle_error("No valid images to process"))
                return
            
            # Update status
            self.main_container.after(0, lambda: self.update_status("Submitting Seedream V4 task..."))
            
            # Prepare payload
            size = f"{width}*{height}"
            payload = {
                "prompt": prompt,
                "images": image_urls,
                "size": size,
                "seed": seed,
                "enable_sync_mode": self.enable_sync_mode.get(),
                "enable_base64_output": self.enable_base64_output.get()
            }
            
            # Submit task
            request_id, error = self.api_client.submit_seedream_v4_task(payload)
            
            if error:
                self.main_container.after(0, lambda: self.handle_error(error))
                return
            
            self.current_request_id = request_id
            self.main_container.after(0, lambda: self.update_status(f"Task submitted. ID: {request_id}"))
            
            # Poll for results
            def progress_callback(status, result):
                self.main_container.after(0, lambda: self.update_status(f"Processing... Status: {status}"))
            
            output_url, error, duration = self.api_client.poll_until_complete(
                request_id, progress_callback, poll_interval=0.5
            )
            
            if error:
                self.main_container.after(0, lambda: self.handle_error(error))
            else:
                self.main_container.after(0, lambda: self.handle_success(output_url, duration))
                
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            self.main_container.after(0, lambda: self.handle_error(error_msg))
    
    def upload_image(self, image_path):
        """Upload image and return URL"""
        try:
            # Use privacy-friendly upload
            success, url, privacy_info = privacy_uploader.upload_with_privacy_warning(image_path, 'seedream_v4')
            
            if success:
                logger.info(f"Seedream V4 image uploaded: {privacy_info}")
                return url
            else:
                logger.error(f"Upload failed: {privacy_info}")
                return None
                
        except Exception as e:
            logger.error(f"Upload error: {e}")
            return None
    
    def show_progress(self, message):
        """Show progress indicator"""
        self.status_label.config(text=message, foreground="blue")
        self.progress_bar.pack(side=tk.RIGHT, padx=(10, 0))
        self.progress_bar.start()
    
    def hide_progress(self):
        """Hide progress indicator"""
        self.progress_bar.stop()
        self.progress_bar.pack_forget()
    
    def update_status(self, message):
        """Update status message"""
        if "error" in message.lower() or "failed" in message.lower():
            color = "red"
        elif "processing" in message.lower() or "submitting" in message.lower():
            color = "blue"
        else:
            color = "green"
        
        self.status_label.config(text=message, foreground=color)
    
    def handle_success(self, output_url, duration):
        """Handle successful processing"""
        self.hide_progress()
        self.update_status(f"✅ Seedream V4 completed in {duration:.1f}s")
        
        # Display result
        self.display_result(output_url)
        self.result_image = output_url
        
        # Auto-save
        prompt = self.prompt_text.get("1.0", tk.END).strip()
        size = f"{self.width_var.get()}*{self.height_var.get()}"
        seed = self.seed_var.get()
        
        extra_info = f"size_{size}_seed_{seed}"
        
        auto_save_manager.save_result(
            'seedream_v4', 
            output_url, 
            prompt=prompt, 
            extra_info=extra_info, 
            file_type="image"
        )
    
    def handle_error(self, error_message):
        """Handle processing errors"""
        self.hide_progress()
        self.update_status(f"❌ Error: {error_message}")
        messagebox.showerror("Seedream V4 Error", error_message)
    
    def display_result(self, image_url):
        """Display result image"""
        try:
            # Download and display image
            import requests
            from io import BytesIO
            
            response = requests.get(image_url)
            response.raise_for_status()
            
            # Load image
            img = Image.open(BytesIO(response.content))
            
            # Resize to fit canvas
            canvas_width = self.result_canvas.winfo_width()
            canvas_height = self.result_canvas.winfo_height()
            
            if canvas_width > 1 and canvas_height > 1:  # Canvas is initialized
                img.thumbnail((canvas_width-20, canvas_height-20), Image.Resampling.LANCZOS)
            
            # Convert to PhotoImage
            photo = ImageTk.PhotoImage(img)
            
            # Clear canvas and display image
            self.result_canvas.delete("all")
            self.result_canvas.create_image(
                canvas_width//2, 
                canvas_height//2, 
                image=photo, 
                anchor=tk.CENTER
            )
            
            # Keep reference
            self.result_canvas.image = photo
            
        except Exception as e:
            logger.error(f"Error displaying result: {e}")
            self.result_canvas.delete("all")
            self.result_canvas.create_text(
                self.result_canvas.winfo_width()//2, 
                self.result_canvas.winfo_height()//2,
                text=f"Error loading result: {str(e)}",
                font=('Arial', 10),
                fill="red"
            )
