"""
Unified Video Generation Tab Component

This module contains unified video generation functionality supporting multiple models:
- Wan 2.2 (Image to Video)
- SeedDance-v1-Pro (Dance/Motion Videos)

Consolidated from image_to_video_tab.py and seeddance_tab.py
"""

import tkinter as tk
from tkinter import ttk
import threading
import webbrowser
import os
import requests
import tempfile
import time
from ui.components.ui_components import BaseTab, ImagePreview, SettingsPanel
from ui.components.enhanced_image_display import EnhancedImageSelector
from ui.components.optimized_video_layout import OptimizedVideoLayout
from ui.components.ai_prompt_suggestions import add_ai_features_to_prompt_section
from utils.utils import *
from core.auto_save import auto_save_manager
from core.logger import get_logger
from app.config import Config
from ui.components.video_player_mixin import VideoPlayerMixin

logger = get_logger()


class VideoGenerationTab(BaseTab, VideoPlayerMixin):
    """Unified Video Generation Tab supporting multiple models"""
    
    def __init__(self, parent_frame, api_client, main_app=None):
        # Model selection
        self.model_var = tk.StringVar(value="wan22")  # Default to Wan 2.2
        
        # Unified prompt storage
        self.prompts_file = "data/video_prompts.json"
        self.saved_prompts = load_json_file(self.prompts_file, [])
        self.main_app = main_app  # Reference to main app for cross-tab operations
        
        BaseTab.__init__(self, parent_frame, api_client)
        VideoPlayerMixin.__init__(self)
    
    def apply_ai_suggestion(self, improved_prompt: str):
        """Apply AI suggestion to prompt text"""
        self.prompt_text.delete("1.0", tk.END)
        self.prompt_text.insert("1.0", improved_prompt)
    
    def setup_ui(self):
        """Setup the unified video generation UI"""
        # Hide the scrollable canvas components since we're using direct container layout
        self.canvas.pack_forget()
        self.scrollbar.pack_forget()
        
        # Use optimized layout (will adapt based on model selection)
        self.setup_dynamic_layout()
        
        # Connect the layout methods to our functionality
        self.connect_optimized_layout()
        
        # Setup model-specific settings
        self.setup_video_settings_optimized()
        
        # Setup progress section
        self.setup_compact_progress_section_optimized()
        
        logger.info("Unified Video Generation UI setup complete")
    
    def setup_dynamic_layout(self):
        """Setup layout that adapts to selected model"""
        model = self.model_var.get()
        
        if model == "seeddance":
            from ui.components.optimized_seeddance_layout import OptimizedSeedDanceLayout
            self.optimized_layout = OptimizedSeedDanceLayout(self.container)
        else:  # Default to wan22 layout
            from ui.components.optimized_wan22_layout import OptimizedWan22Layout
            self.optimized_layout = OptimizedWan22Layout(self.container)
    
    def on_model_changed(self, event=None):
        """Handle model selection change"""
        model = self.model_var.get()
        
        # Recreate layout for new model
        self.setup_dynamic_layout()
        self.connect_optimized_layout()
        self.setup_model_specific_settings()
        
        # Update UI elements based on model
        if hasattr(self, 'prompt_text'):
            if model == "seeddance":
                # SeedDance uses optional prompts
                self.update_status("Ready for SeedDance video generation")
            else:
                # Wan 2.2 uses required prompts
                self.update_status("Ready for Wan 2.2 video generation")
        
        # Update button text if available
        if hasattr(self.optimized_layout, 'generate_btn'):
            if model == "seeddance":
                self.optimized_layout.generate_btn.config(text="🕺 Generate SeedDance")
            else:
                self.optimized_layout.generate_btn.config(text="🎬 Generate Wan 2.2")
    
    def connect_optimized_layout(self):
        """Connect the optimized layout methods to our existing functionality"""
        # Connect image browsing
        self.optimized_layout.browse_image = self.browse_image
        
        # Connect processing (unified method)
        if hasattr(self.optimized_layout, 'process_video_generation'):
            self.optimized_layout.process_video_generation = self.process_task
        elif hasattr(self.optimized_layout, 'process_dance_generation'):
            self.optimized_layout.process_dance_generation = self.process_task
        
        # Connect result actions
        self.optimized_layout.open_in_browser = self.open_video_in_browser
        self.optimized_layout.play_in_system = self.play_in_system_placeholder
        self.optimized_layout.download_video = self.download_video_placeholder
        
        # Connect utility methods
        self.optimized_layout.clear_all = self.clear_prompts
        self.optimized_layout.load_sample = self.load_sample_prompt
        self.optimized_layout.improve_with_ai = self.improve_with_ai_placeholder
        
        # Connect prompt management
        self.optimized_layout.save_current_prompt = self.save_current_prompt
        self.optimized_layout.delete_saved_prompt = self.delete_selected_prompt
        self.optimized_layout.on_saved_prompt_selected = self.on_saved_prompt_selected_placeholder
        
        # Store references to layout components for easy access
        if hasattr(self.optimized_layout, 'video_prompt_text'):
            self.prompt_text = self.optimized_layout.video_prompt_text
        
        # Handle different layout component names
        if hasattr(self.optimized_layout, 'negative_prompt_text'):
            self.negative_prompt_text = self.optimized_layout.negative_prompt_text
        
        if hasattr(self.optimized_layout, 'status_label'):
            self.status_label = self.optimized_layout.status_label
        
        if hasattr(self.optimized_layout, 'progress_bar'):
            self.progress_bar = self.optimized_layout.progress_bar
        
        if hasattr(self.optimized_layout, 'generate_btn'):
            self.generate_btn = self.optimized_layout.generate_btn
    
    def browse_image(self):
        """Browse for image file"""
        from tkinter import filedialog
        
        model = self.model_var.get()
        title = f"Select Image for {model.upper()} Video Generation"
        
        file_path = filedialog.askopenfilename(
            title=title,
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.gif *.bmp *.webp"),
                ("PNG files", "*.png"),
                ("JPEG files", "*.jpg *.jpeg"),
                ("All files", "*.*")
            ]
        )
        if file_path:
            self.on_image_selected(file_path)
    
    def setup_model_selection_ui(self):
        """Setup model selection UI"""
        # Add model selection at the top
        model_frame = ttk.LabelFrame(self.container, text="🎬 Video Model", padding="5")
        model_frame.pack(fill=tk.X, padx=5, pady=(5, 0))
        
        # Model selection
        ttk.Label(model_frame, text="Model:", font=('Arial', 9, 'bold')).pack(side=tk.LEFT)
        
        model_combo = ttk.Combobox(
            model_frame,
            textvariable=self.model_var,
            values=["wan22", "seeddance"],
            state="readonly",
            width=15
        )
        model_combo.pack(side=tk.LEFT, padx=(5, 0))
        model_combo.bind('<<ComboboxSelected>>', self.on_model_changed)
        
        # Model description
        self.model_desc_label = ttk.Label(
            model_frame, 
            text="Wan 2.2: High-quality image-to-video conversion",
            font=('Arial', 8),
            foreground="gray"
        )
        self.model_desc_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Update description when model changes
        def update_description():
            model = self.model_var.get()
            if model == "seeddance":
                self.model_desc_label.config(text="SeedDance: Dance/motion video generation")
            else:
                self.model_desc_label.config(text="Wan 2.2: High-quality image-to-video conversion")
        
        model_combo.bind('<<ComboboxSelected>>', lambda e: update_description())
    
    def setup_video_settings_optimized(self):
        """Setup video-specific settings based on selected model"""
        # Add model selection at the top
        self.setup_model_selection_ui()
        
        # Ensure model-specific settings are properly exposed
        self.setup_model_specific_settings()
    
    def setup_model_specific_settings(self):
        """Setup model-specific settings that might not be exposed by layouts"""
        model = self.model_var.get()
        
        if model == "seeddance":
            self.setup_seeddance_specific_settings()
        else:
            self.setup_wan22_specific_settings()
    
    def setup_wan22_specific_settings(self):
        """Ensure Wan 2.2 specific settings are available"""
        # Check if the layout provides all required Wan 2.2 settings
        required_vars = ['duration_var', 'seed_var', 'negative_prompt_text', 'last_image_url_var']
        
        # Duration setting (5, 8 seconds)
        if not hasattr(self.optimized_layout, 'duration_var'):
            self.duration_var = tk.StringVar(value="5")
        else:
            self.duration_var = self.optimized_layout.duration_var
        
        # Seed setting
        if not hasattr(self.optimized_layout, 'seed_var'):
            self.seed_var = tk.StringVar(value="-1")
        else:
            self.seed_var = self.optimized_layout.seed_var
        
        # Last image URL setting (optional)
        if not hasattr(self.optimized_layout, 'last_image_url_var'):
            self.last_image_url_var = tk.StringVar(value="")
        else:
            self.last_image_url_var = self.optimized_layout.last_image_url_var
        
        # Ensure negative prompt is available
        if hasattr(self.optimized_layout, 'negative_prompt_text'):
            self.negative_prompt_text = self.optimized_layout.negative_prompt_text
    
    def setup_seeddance_specific_settings(self):
        """Ensure SeedDance specific settings are available"""
        # Check if the layout provides all required SeedDance settings
        
        # Duration setting (SeedDance durations)
        if not hasattr(self.optimized_layout, 'duration_var'):
            self.duration_var = tk.StringVar(value="5")
        else:
            self.duration_var = self.optimized_layout.duration_var
        
        # Resolution/Version setting (480p, 720p)
        if not hasattr(self.optimized_layout, 'resolution_var') and not hasattr(self.optimized_layout, 'version_var'):
            self.resolution_var = tk.StringVar(value="720p")
        else:
            self.resolution_var = getattr(self.optimized_layout, 'resolution_var', 
                                        getattr(self.optimized_layout, 'version_var', tk.StringVar(value="720p")))
        
        # Camera Fixed setting
        if not hasattr(self.optimized_layout, 'camera_fixed_var'):
            self.camera_fixed_var = tk.BooleanVar(value=True)
        else:
            self.camera_fixed_var = self.optimized_layout.camera_fixed_var
        
        # Seed setting
        if not hasattr(self.optimized_layout, 'seed_var'):
            self.seed_var = tk.StringVar(value="-1")
        else:
            self.seed_var = self.optimized_layout.seed_var
    
    def setup_compact_progress_section_optimized(self):
        """Setup compact progress section in the optimized layout"""
        # The optimized layout already has the progress section built-in
        pass
    
    def load_sample_prompt(self):
        """Load a sample prompt based on selected model"""
        model = self.model_var.get()
        
        if model == "seeddance":
            # SeedDance sample prompts
            sample_prompts = [
                "Girl playing piano, multiple camera switches, cinematic quality",
                "A girl turns toward the camera, her earrings swaying gently with the motion. The camera rotates, bathed in dreamy sunlight",
                "Person walking through a magical forest, leaves falling, golden hour lighting, smooth camera movement",
                "Dancer performing contemporary moves, flowing fabric, dramatic lighting, multiple angles",
                "Portrait shot with gentle breeze moving hair, soft focus background, cinematic mood",
                "Close-up of hands creating art, paint flowing, time-lapse style, artistic lighting"
            ]
            import random
            sample_prompt = random.choice(sample_prompts)
            sample_negative = ""
        else:
            # Wan 2.2 sample prompts
            sample_prompt = "A beautiful woman walking through a garden, gentle breeze, natural lighting, cinematic movement"
            sample_negative = "blurry, low quality, static, no movement"
        
        # Apply sample prompt
        if hasattr(self, 'prompt_text'):
            self.prompt_text.delete("1.0", tk.END)
            self.prompt_text.insert("1.0", sample_prompt)
        
        # Apply negative prompt if available and model supports it
        if hasattr(self, 'negative_prompt_text') and model == "wan22" and sample_negative:
            self.negative_prompt_text.delete("1.0", tk.END)
            self.negative_prompt_text.insert("1.0", sample_negative)
    
    def on_image_selected(self, image_path, replacing_image=False):
        """Handle image selection"""
        # Check if replacing existing image
        if not replacing_image:
            replacing_image = hasattr(self, 'selected_image_path') and self.selected_image_path is not None
        
        # Update the optimized layout with the new image
        if hasattr(self.optimized_layout, 'load_image'):
            self.optimized_layout.load_image(image_path)
        elif hasattr(self.optimized_layout, 'on_image_selected'):
            original_image = self.optimized_layout.on_image_selected(image_path)
            if hasattr(self, 'original_image'):
                self.original_image = original_image
        
        # Store references for compatibility
        self.selected_image_path = image_path
        
        # Provide feedback about image replacement
        model_name = "SeedDance" if self.model_var.get() == "seeddance" else "Wan 2.2"
        if replacing_image:
            self.update_status(f"Image replaced: {os.path.basename(image_path)} - Ready for {model_name}")
        else:
            self.update_status(f"Image selected: {os.path.basename(image_path)} - Ready for {model_name}")
    
    def on_drop(self, event):
        """Handle drag and drop with robust file path parsing"""
        # Parse the drag & drop data
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
        
        # Update UI and process the file
        if hasattr(self, 'image_selector'):
            self.image_selector.selected_path = file_path
            self.image_selector.image_path_label.config(
                text=os.path.basename(file_path), foreground="black"
            )
        self.on_image_selected(file_path)
    
    def setup_prompt_management(self, parent):
        """Setup unified prompt management UI"""
        # Saved prompts section
        ttk.Label(parent, text="Saved Prompts:", font=('Arial', 9, 'bold')).grid(
            row=4, column=0, sticky=tk.W, pady=(10, 2))
        
        # Saved prompts listbox with scrollbar
        listbox_frame = ttk.Frame(parent)
        listbox_frame.grid(row=5, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        listbox_frame.columnconfigure(0, weight=1)
        
        self.saved_prompts_listbox = tk.Listbox(listbox_frame, height=4, font=('Arial', 9))
        self.saved_prompts_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        listbox_scroll = ttk.Scrollbar(listbox_frame, orient="vertical", 
                                     command=self.saved_prompts_listbox.yview)
        listbox_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.saved_prompts_listbox.configure(yscrollcommand=listbox_scroll.set)
        
        # Prompt management buttons
        buttons_frame = ttk.Frame(parent)
        buttons_frame.grid(row=6, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        buttons_frame.columnconfigure(0, weight=1)
        buttons_frame.columnconfigure(1, weight=1)
        buttons_frame.columnconfigure(2, weight=1)
        
        ttk.Button(buttons_frame, text="💾 Save", command=self.save_current_prompt, 
                  width=8).grid(row=0, column=0, padx=(0, 2))
        ttk.Button(buttons_frame, text="📋 Load", command=self.load_selected_prompt, 
                  width=8).grid(row=0, column=1, padx=2)
        ttk.Button(buttons_frame, text="🗑️ Delete", command=self.delete_selected_prompt, 
                  width=8).grid(row=0, column=2, padx=(2, 0))
        
        # Load saved prompts into listbox
        self.refresh_prompts_list()

    def refresh_prompts_list(self):
        """Refresh the saved prompts list"""
        if not hasattr(self, 'saved_prompts_listbox'):
            return
        
        self.saved_prompts_listbox.delete(0, tk.END)
        for i, prompt_data in enumerate(self.saved_prompts):
            display_text = prompt_data.get('name', f'Prompt {i+1}')
            # Add model indicator
            model = prompt_data.get('model', 'unknown')
            display_text = f"[{model.upper()}] {display_text}"
            self.saved_prompts_listbox.insert(tk.END, display_text)

    def save_current_prompt(self):
        """Save current prompt to the unified prompts list"""
        if not hasattr(self, 'prompt_text'):
            return
        
        video_prompt = self.prompt_text.get("1.0", tk.END).strip()
        model = self.model_var.get()
        
        if not video_prompt:
            show_error("Error", "Please enter a video prompt before saving.")
            return
        
        # Create a simple dialog to get prompt name
        from tkinter import simpledialog
        prompt_name = simpledialog.askstring(
            "Save Prompt", 
            f"Enter a name for this {model.upper()} prompt:",
            initialvalue=video_prompt[:30] + "..." if len(video_prompt) > 30 else video_prompt
        )
        
        if prompt_name:
            prompt_data = {
                'name': prompt_name,
                'model': model,
                'video_prompt': video_prompt
            }
            
            # Add negative prompt for Wan 2.2
            if model == "wan22" and hasattr(self, 'negative_prompt_text'):
                negative_prompt = self.negative_prompt_text.get("1.0", tk.END).strip()
                prompt_data['negative_prompt'] = negative_prompt
            
            self.saved_prompts.append(prompt_data)
            save_json_file(self.prompts_file, self.saved_prompts)
            self.refresh_prompts_list()

    def load_selected_prompt(self):
        """Load the selected prompt from the saved prompts list"""
        if not hasattr(self, 'saved_prompts_listbox'):
            return
        
        selection = self.saved_prompts_listbox.curselection()
        if not selection:
            show_error("Error", "Please select a prompt to load.")
            return
        
        prompt_data = self.saved_prompts[selection[0]]
        
        # Load prompt into text area
        if hasattr(self, 'prompt_text'):
            self.prompt_text.delete("1.0", tk.END)
            self.prompt_text.insert("1.0", prompt_data.get('video_prompt', ''))
        
        # Load negative prompt if available and current model supports it
        if (self.model_var.get() == "wan22" and 
            hasattr(self, 'negative_prompt_text') and 
            'negative_prompt' in prompt_data):
            self.negative_prompt_text.delete("1.0", tk.END)
            self.negative_prompt_text.insert("1.0", prompt_data.get('negative_prompt', ''))

    def delete_selected_prompt(self):
        """Delete the selected prompt from the saved prompts list"""
        if not hasattr(self, 'saved_prompts_listbox'):
            return
        
        selection = self.saved_prompts_listbox.curselection()
        if not selection:
            show_error("Error", "Please select a prompt to delete.")
            return
        
        prompt_data = self.saved_prompts[selection[0]]
        
        from tkinter import messagebox
        if messagebox.askyesno("Confirm Delete", f"Delete prompt '{prompt_data['name']}'?"):
            del self.saved_prompts[selection[0]]
            save_json_file(self.prompts_file, self.saved_prompts)
            self.refresh_prompts_list()

    def clear_prompts(self):
        """Clear all prompts"""
        if hasattr(self.optimized_layout, 'clear_all'):
            self.optimized_layout.clear_all()
        else:
            if hasattr(self, 'prompt_text'):
                self.prompt_text.delete("1.0", tk.END)
            if hasattr(self, 'negative_prompt_text'):
                self.negative_prompt_text.delete("1.0", tk.END)
    
    def update_status(self, message):
        """Update status display"""
        if hasattr(self.optimized_layout, 'status_label'):
            self.optimized_layout.status_label.config(text=message)
        elif hasattr(self, 'status_label'):
            self.status_label.config(text=message)
    
    def show_progress(self, message):
        """Show progress"""
        self.update_status(message)
        if hasattr(self.optimized_layout, 'progress_bar'):
            self.optimized_layout.progress_bar.start()
        elif hasattr(self, 'progress_bar'):
            self.progress_bar.start()
    
    def hide_progress(self):
        """Hide progress"""
        if hasattr(self.optimized_layout, 'progress_bar'):
            self.optimized_layout.progress_bar.stop()
        elif hasattr(self, 'progress_bar'):
            self.progress_bar.stop()
    
    def process_task(self):
        """Process video generation task based on selected model"""
        if not self.validate_inputs():
            return
        
        model = self.model_var.get()
        prompt = self.prompt_text.get("1.0", tk.END).strip() if hasattr(self, 'prompt_text') else ""
        
        # Validate prompt requirements based on model
        if model == "wan22" and not prompt:
            show_error("Error", "Please enter a video prompt for Wan 2.2.")
            return
        
        model_name = "SeedDance" if model == "seeddance" else "Wan 2.2"
        self.show_progress(f"Starting {model_name} video generation...")
        
        # Start processing in background thread
        thread = threading.Thread(target=self.process_thread, args=(model,))
        thread.daemon = True
        thread.start()
    
    def process_thread(self, model):
        """Process in background thread"""
        try:
            # Update status
            self.frame.after(0, lambda: self.update_status("Preparing image..."))
            
            # Upload image based on model
            if model == "seeddance":
                image_url = self.upload_image_for_seeddance(self.selected_image_path)
            else:
                image_url = self.upload_image_for_video(self.selected_image_path)
            
            if not image_url:
                self.frame.after(0, lambda: self.handle_error("Failed to prepare image for video generation"))
                return
            
            # Get common parameters
            prompt = self.prompt_text.get("1.0", tk.END).strip() if hasattr(self, 'prompt_text') else ""
            
            # Update status
            model_name = "SeedDance" if model == "seeddance" else "Wan 2.2"
            self.frame.after(0, lambda: self.update_status(f"Submitting {model_name} task..."))
            
            # Submit task based on model
            if model == "seeddance":
                request_id, error = self.submit_seeddance_task(image_url, prompt)
            else:
                request_id, error = self.submit_wan22_task(image_url, prompt)
            
            if error:
                self.frame.after(0, lambda: self.handle_error(error))
                return
            
            self.current_request_id = request_id
            self.frame.after(0, lambda: self.update_status(f"Task submitted. ID: {request_id}"))
            
            # Poll for results
            def progress_callback(status, result):
                self.frame.after(0, lambda: self.update_status(f"Generating video... Status: {status}"))
            
            output_url, error, duration_time = self.api_client.poll_until_complete(
                request_id, progress_callback, poll_interval=2.0
            )
            
            if error:
                self.frame.after(0, lambda: self.handle_error(error))
            else:
                self.frame.after(0, lambda: self.handle_success(output_url, duration_time, model))
                
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            self.frame.after(0, lambda: self.handle_error(error_msg))
    
    def submit_wan22_task(self, image_url, prompt):
        """Submit Wan 2.2 video generation task"""
        # Get negative prompt (required for Wan 2.2)
        negative_prompt = ""
        if hasattr(self, 'negative_prompt_text'):
            negative_prompt = self.negative_prompt_text.get("1.0", tk.END).strip()
        
        # Get last image URL (optional for video chaining)
        last_image = ""
        if hasattr(self, 'last_image_url_var'):
            last_image = self.last_image_url_var.get().strip()
        elif hasattr(self.optimized_layout, 'last_image_url_var'):
            last_image = self.optimized_layout.last_image_url_var.get().strip()
        
        # Get duration (5 or 8 seconds for Wan 2.2)
        duration = 5  # Default
        if hasattr(self, 'duration_var'):
            duration = int(self.duration_var.get())
        elif hasattr(self.optimized_layout, 'duration_var'):
            duration = int(self.optimized_layout.duration_var.get())
        
        # Get seed
        seed = -1
        if hasattr(self, 'seed_var'):
            try:
                seed = int(self.seed_var.get())
            except ValueError:
                seed = -1
        elif hasattr(self.optimized_layout, 'seed_var'):
            try:
                seed = int(self.optimized_layout.seed_var.get())
            except ValueError:
                seed = -1
        
        return self.api_client.submit_image_to_video_task(
            image_url, prompt, duration, negative_prompt, last_image, seed
        )
    
    def submit_seeddance_task(self, image_url, prompt):
        """Submit SeedDance video generation task"""
        # Get duration (SeedDance supports different durations)
        duration = 5  # Default
        if hasattr(self, 'duration_var'):
            duration = int(self.duration_var.get())
        elif hasattr(self.optimized_layout, 'duration_var'):
            duration = int(self.optimized_layout.duration_var.get())
        
        # Get camera fixed setting (important for SeedDance)
        camera_fixed = True  # Default
        if hasattr(self, 'camera_fixed_var'):
            camera_fixed = self.camera_fixed_var.get()
        elif hasattr(self.optimized_layout, 'camera_fixed_var'):
            camera_fixed = self.optimized_layout.camera_fixed_var.get()
        
        # Get seed
        seed = -1
        if hasattr(self, 'seed_var'):
            try:
                seed_str = self.seed_var.get().strip()
                seed = int(seed_str) if seed_str != "-1" else -1
            except (ValueError, AttributeError):
                seed = -1
        elif hasattr(self.optimized_layout, 'seed_var'):
            try:
                seed_str = self.optimized_layout.seed_var.get().strip()
                seed = int(seed_str) if seed_str != "-1" else -1
            except (ValueError, AttributeError):
                seed = -1
        
        # Get resolution/version (480p or 720p)
        version = "720p"  # Default
        if hasattr(self, 'resolution_var'):
            version = self.resolution_var.get()
        elif hasattr(self.optimized_layout, 'resolution_var'):
            version = self.optimized_layout.resolution_var.get()
        elif hasattr(self.optimized_layout, 'version_var'):
            version = self.optimized_layout.version_var.get()
        
        return self.api_client.submit_seeddance_task(
            image_url, duration, prompt, camera_fixed, seed, version
        )
    
    def upload_image_for_video(self, image_path):
        """Upload image and return URL for Wan 2.2 video generation"""
        try:
            from core.secure_upload import privacy_uploader
            success, image_url, privacy_info = privacy_uploader.upload_with_privacy_warning(image_path, 'video')
            
            if success and image_url:
                logger.info(f"Wan 2.2 image uploaded: {privacy_info}")
                return image_url
            else:
                sample_url = Config.SAMPLE_URLS.get('video', Config.SAMPLE_URLS.get('seededit'))
                self.frame.after(0, lambda: self._show_sample_image_warning(
                    image_path, 'video', privacy_info
                ))
                return sample_url
                
        except Exception as e:
            logger.error(f"Upload failed: {e}")
            sample_url = Config.SAMPLE_URLS.get('video', Config.SAMPLE_URLS.get('seededit'))
            self.frame.after(0, lambda: self._show_sample_image_warning(
                image_path, 'video', f"Upload error: {str(e)}"
            ))
            return sample_url
    
    def upload_image_for_seeddance(self, image_path):
        """Upload image and return URL for SeedDance video generation"""
        try:
            from core.secure_upload import privacy_uploader
            success, image_url, privacy_info = privacy_uploader.upload_with_privacy_warning(image_path, 'seeddance')
            
            if success and image_url:
                logger.info(f"SeedDance image uploaded: {privacy_info}")
                return image_url
            else:
                # Get version-specific sample URL
                version = "720p"
                if hasattr(self.optimized_layout, 'version_var'):
                    version = self.optimized_layout.version_var.get()
                
                sample_url = Config.SAMPLE_URLS.get(f'seeddance_{version}', 
                                                  Config.SAMPLE_URLS.get('seeddance', 
                                                  Config.SAMPLE_URLS.get('seededit')))
                
                self.frame.after(0, lambda: show_warning(
                    "Using Sample Image", 
                    f"Could not upload your image: {privacy_info}\n\n"
                    f"Using sample image for demonstration.\n"
                    f"Your selected image: {os.path.basename(image_path)}"
                ))
                return sample_url
                
        except Exception as e:
            logger.error(f"Upload failed: {e}")
            version = "720p"
            if hasattr(self.optimized_layout, 'version_var'):
                version = self.optimized_layout.version_var.get()
            
            sample_url = Config.SAMPLE_URLS.get(f'seeddance_{version}', 
                                              Config.SAMPLE_URLS.get('seeddance', 
                                              Config.SAMPLE_URLS.get('seededit')))
            
            self.frame.after(0, lambda: show_warning(
                "Upload Error", 
                f"Upload failed: {str(e)}\n\nUsing sample image for demonstration."
            ))
            return sample_url
    
    def _show_sample_image_warning(self, image_path, ai_model, reason):
        """Show enhanced warning dialog for sample image usage"""
        from utils.warning_dialogs import show_sample_image_warning
        show_sample_image_warning(self.frame, image_path, ai_model, reason)
    
    def handle_success(self, output_url, duration_time, model):
        """Handle successful completion"""
        # Hide progress
        self.hide_progress()
        
        # Update the optimized layout with the result
        if hasattr(self.optimized_layout, 'result_video_path'):
            self.optimized_layout.result_video_path = output_url
            if hasattr(self.optimized_layout, 'show_video_ready'):
                self.optimized_layout.show_video_ready()
        
        # Store result URL
        self.result_video_url = output_url
        
        # Load video in modern player if available
        if hasattr(self, 'modern_video_player') and self.modern_video_player:
            try:
                self.modern_video_player.load_video(output_url)
            except Exception as e:
                logger.error(f"Failed to load video in modern player: {e}")
        
        # Auto-save the result
        prompt = self.prompt_text.get("1.0", tk.END).strip() if hasattr(self, 'prompt_text') else ""
        
        # Get model-specific parameters for extra info
        if model == "seeddance":
            extra_info = self.get_seeddance_extra_info()
        else:
            extra_info = self.get_wan22_extra_info()
        
        success, saved_path, error = auto_save_manager.save_result(
            model, 
            output_url, 
            prompt=prompt,
            extra_info=extra_info,
            file_type="video"
        )
        
        # Update status with success info
        model_name = "SeedDance" if model == "seeddance" else "Wan 2.2"
        success_msg = f"✅ {model_name} video generated in {format_duration(duration_time)}!"
        if saved_path:
            success_msg += f" Auto-saved locally."
        self.update_status(success_msg)
    
    def get_wan22_extra_info(self):
        """Get Wan 2.2 specific extra info for auto-save"""
        duration = "5s"
        seed = "-1"
        
        if hasattr(self.optimized_layout, 'duration_var'):
            duration = f"{self.optimized_layout.duration_var.get()}s"
        
        if hasattr(self.optimized_layout, 'seed_var'):
            seed = self.optimized_layout.seed_var.get()
        
        return f"{duration}_seed{seed}"
    
    def get_seeddance_extra_info(self):
        """Get SeedDance specific extra info for auto-save"""
        duration = "5s"
        camera_fixed = "True"
        seed = "-1"
        version = "720p"
        
        if hasattr(self.optimized_layout, 'duration_var'):
            duration = f"{self.optimized_layout.duration_var.get()}s"
        
        if hasattr(self.optimized_layout, 'camera_fixed_var'):
            camera_fixed = str(self.optimized_layout.camera_fixed_var.get())
        
        if hasattr(self.optimized_layout, 'seed_var'):
            seed = self.optimized_layout.seed_var.get()
        
        if hasattr(self.optimized_layout, 'version_var'):
            version = self.optimized_layout.version_var.get()
        
        return f"duration_{duration}_camera_{'fixed' if camera_fixed == 'True' else 'dynamic'}_{version}_seed_{seed}"
    
    def handle_error(self, error_message):
        """Handle error"""
        # Hide progress
        self.hide_progress()
        
        # Update status
        self.update_status(f"❌ Error: {error_message}")
        
        # Show error dialog
        model_name = "SeedDance" if self.model_var.get() == "seeddance" else "Wan 2.2"
        show_error(f"{model_name} Generation Error", error_message)
    
    def open_video_in_browser(self):
        """Open video in browser"""
        if not hasattr(self, 'result_video_url') or not self.result_video_url:
            show_error("Error", "No video URL available.")
            return
        
        try:
            webbrowser.open(self.result_video_url)
        except Exception as e:
            show_error("Error", f"Failed to open browser: {str(e)}")
    
    def copy_video_url(self):
        """Copy video URL to clipboard"""
        if not hasattr(self, 'result_video_url') or not self.result_video_url:
            show_error("Error", "No video URL available.")
            return
        
        try:
            self.frame.clipboard_clear()
            self.frame.clipboard_append(self.result_video_url)
            self.frame.update()
        except Exception as e:
            show_error("Error", f"Failed to copy URL: {str(e)}")
    
    def validate_inputs(self):
        """Validate inputs before processing"""
        # Check if image is selected
        if not hasattr(self.optimized_layout, 'get_selected_image'):
            if not hasattr(self, 'selected_image_path') or not self.selected_image_path:
                show_error("Error", "Please select an image for video generation.")
                return False
        else:
            if not self.optimized_layout.get_selected_image():
                show_error("Error", "Please select an image for video generation.")
                return False
        
        model = self.model_var.get()
        
        # Model-specific validation
        if model == "seeddance":
            return self.validate_seeddance_inputs()
        else:
            return self.validate_wan22_inputs()
    
    def validate_wan22_inputs(self):
        """Validate Wan 2.2 specific inputs"""
        # Check duration (5 or 8 seconds for Wan 2.2)
        duration_var = getattr(self, 'duration_var', getattr(self.optimized_layout, 'duration_var', None))
        if duration_var:
            try:
                duration = int(duration_var.get())
                if duration not in [5, 8]:
                    show_error("Error", "Duration must be 5 or 8 seconds for Wan 2.2.")
                    return False
            except ValueError:
                show_error("Error", "Invalid duration value.")
                return False
        
        # Check seed
        seed_var = getattr(self, 'seed_var', getattr(self.optimized_layout, 'seed_var', None))
        if seed_var:
            try:
                seed = seed_var.get().strip()
                if seed and seed != "-1":
                    seed_int = int(seed)
                    if seed_int < -1 or seed_int > 2147483647:
                        show_error("Error", "Seed must be -1 or between 0 and 2147483647.")
                        return False
            except ValueError:
                show_error("Error", "Invalid seed value. Use -1 for random or a valid integer.")
                return False
        
        return True
    
    def validate_seeddance_inputs(self):
        """Validate SeedDance specific inputs"""
        # Check duration (SeedDance may support different durations based on config)
        duration_var = getattr(self, 'duration_var', getattr(self.optimized_layout, 'duration_var', None))
        if duration_var:
            try:
                duration = int(duration_var.get())
                # Use Config.SEEDDANCE_DURATIONS if available, otherwise default to [5]
                from app.config import Config
                valid_durations = getattr(Config, 'SEEDDANCE_DURATIONS', [5])
                if duration not in valid_durations:
                    show_error("Error", f"Duration must be one of {valid_durations} seconds for SeedDance.")
                    return False
            except ValueError:
                show_error("Error", "Invalid duration value.")
                return False
        
        # Check resolution
        resolution_var = getattr(self, 'resolution_var', getattr(self.optimized_layout, 'resolution_var', 
                               getattr(self.optimized_layout, 'version_var', None)))
        if resolution_var:
            resolution = resolution_var.get()
            if resolution not in ["480p", "720p"]:
                show_error("Error", "Resolution must be 480p or 720p for SeedDance.")
                return False
        
        # Check seed
        seed_var = getattr(self, 'seed_var', getattr(self.optimized_layout, 'seed_var', None))
        if seed_var:
            try:
                seed = seed_var.get().strip()
                if seed and seed != "-1":
                    seed_int = int(seed)
                    if seed_int < -1 or seed_int > 2147483647:
                        show_error("Error", "Seed must be -1 or between 0 and 2147483647.")
                        return False
            except ValueError:
                show_error("Error", "Invalid seed value. Use -1 for random or a valid integer.")
                return False
        
        return True
    
    # Placeholder methods for layout compatibility
    def play_in_system_placeholder(self):
        """Placeholder for playing video in system player"""
        if hasattr(self, 'result_video_url') and self.result_video_url:
            self.update_status("📱 Opening in system player...")
    
    def download_video_placeholder(self):
        """Placeholder for downloading video"""
        if hasattr(self, 'result_video_url') and self.result_video_url:
            self.update_status("💾 Video downloaded")
    
    def improve_with_ai_placeholder(self):
        """Placeholder for AI improvement functionality"""
        pass
    
    def on_saved_prompt_selected_placeholder(self, event=None):
        """Placeholder for saved prompt selection"""
        pass