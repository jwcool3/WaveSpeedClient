"""
SeedDance Tab Component

This module contains the ByteDance SeedDance-v1-Pro image-to-video functionality.
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
from app.config import Config
from utils.utils import *
from core.auto_save import auto_save_manager
from core.logger import get_logger
from ui.components.video_player_mixin import VideoPlayerMixin

logger = get_logger()


class SeedDanceTab(BaseTab, VideoPlayerMixin):
    """SeedDance Image to Video Tab"""
    
    def __init__(self, parent_frame, api_client, main_app=None):
        self.prompts_file = "data/seeddance_prompts.json"
        self.saved_prompts = load_json_file(self.prompts_file, [])
        self.main_app = main_app  # Reference to main app for cross-tab operations
        BaseTab.__init__(self, parent_frame, api_client)
        VideoPlayerMixin.__init__(self)
    
    def setup_ui(self):
        """Setup the optimized SeedDance UI"""
        # Hide the scrollable canvas components since we're using direct container layout
        self.canvas.pack_forget()
        self.scrollbar.pack_forget()
        
        # For optimized layout, bypass the scrollable canvas and use the main container directly
        # This ensures full window expansion without canvas constraints
        self.optimized_layout = OptimizedVideoLayout(self.container, "SeedDance Video Generation")
        
        # Setup the layout with SeedDance-specific settings
        self.setup_seeddance_settings()
        
        # Setup prompt section in the left panel
        self.setup_compact_prompt_section()
        
        # Configure main action button
        self.optimized_layout.set_main_action("🎭 Generate SeedDance Video", self.process_task)
        
        # Connect sample button to load sample prompt
        self.optimized_layout.sample_button.config(command=self.load_sample_prompt)
        
        # Connect clear button to clear prompts
        self.optimized_layout.clear_button.config(command=self.clear_prompts)
        
        # Get references to important components
        self.enhanced_video_player = self.optimized_layout.get_video_player()
        
        # Setup progress and results (compact)
        self.setup_compact_progress_section()
        
        logger.info("Optimized SeedDance UI setup complete")
    
    def setup_seeddance_settings(self):
        """Setup SeedDance generation settings in the optimized layout"""
        settings_container = self.optimized_layout.settings_container
        
        # Duration setting
        duration_frame = ttk.Frame(settings_container)
        duration_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=2)
        duration_frame.columnconfigure(1, weight=1)
        
        ttk.Label(duration_frame, text="Duration:", font=('Arial', 9)).grid(row=0, column=0, sticky=tk.W)
        self.duration_var = tk.StringVar(value="5")
        duration_combo = ttk.Combobox(duration_frame, textvariable=self.duration_var, 
                                     values=["5"], state="readonly", width=8)
        duration_combo.grid(row=0, column=1, sticky=tk.E, padx=(5, 0))
        
        # Camera fixed setting
        camera_frame = ttk.Frame(settings_container)
        camera_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=2)
        camera_frame.columnconfigure(1, weight=1)
        
        ttk.Label(camera_frame, text="Camera Fixed:", font=('Arial', 9)).grid(row=0, column=0, sticky=tk.W)
        self.camera_fixed_var = tk.BooleanVar(value=True)
        camera_check = ttk.Checkbutton(camera_frame, variable=self.camera_fixed_var)
        camera_check.grid(row=0, column=1, sticky=tk.E, padx=(5, 0))
        
        # Seed setting
        seed_frame = ttk.Frame(settings_container)
        seed_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=2)
        seed_frame.columnconfigure(1, weight=1)
        
        ttk.Label(seed_frame, text="Seed:", font=('Arial', 9)).grid(row=0, column=0, sticky=tk.W)
        self.seed_var = tk.StringVar(value="-1")
        seed_entry = ttk.Entry(seed_frame, textvariable=self.seed_var, width=10)
        seed_entry.grid(row=0, column=1, sticky=tk.E, padx=(5, 0))
    
    def setup_compact_prompt_section(self):
        """Setup compact prompt section for SeedDance"""
        # Add prompt section below settings (in the spacer area)
        prompt_frame = ttk.LabelFrame(self.optimized_layout.settings_frame.master, text="📝 Video Prompt (Optional)", padding="8")
        prompt_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N), pady=(10, 0))
        prompt_frame.columnconfigure(0, weight=1)
        
        # Video prompt (optional for SeedDance)
        ttk.Label(prompt_frame, text="Describe the motion or scene:", font=('Arial', 9)).grid(row=0, column=0, sticky=tk.W)
        self.prompt_text = tk.Text(prompt_frame, height=3, wrap=tk.WORD, font=('Arial', 10))
        self.prompt_text.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(2, 0))
        
        # Add helpful hint
        hint_label = ttk.Label(prompt_frame, text="💡 Tip: Leave blank for automatic motion detection", 
                              font=('Arial', 8), foreground="gray")
        hint_label.grid(row=2, column=0, sticky=tk.W, pady=(2, 5))
        
        # Prompt management section
        self.setup_prompt_management(prompt_frame)
    
    def setup_compact_progress_section(self):
        """Setup compact progress section"""
        # Add progress bar at the very bottom of left panel
        progress_frame = ttk.Frame(self.optimized_layout.settings_frame.master)
        progress_frame.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        progress_frame.columnconfigure(0, weight=1)
        
        # Progress bar
        self.progress_bar = ttk.Progressbar(progress_frame, mode='indeterminate')
        self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # Status label
        self.status_label = ttk.Label(progress_frame, text="Ready to generate SeedDance video", font=('Arial', 8))
        self.status_label.grid(row=1, column=0, sticky=tk.W)
    
    def setup_video_result_section(self):
        """Setup video result display section (now handled by optimized layout)"""
        # Video display is now handled by the OptimizedVideoLayout
        # The enhanced video player is already created and available
        pass
    
    def setup_prompt_section(self):
        """Setup prompt section for video generation"""
        prompt_section = ttk.LabelFrame(self.frame, text="SeedDance Video Settings", padding="10")
        prompt_section.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 10))
        prompt_section.columnconfigure(0, weight=1)
        
        # Video prompt (optional)
        prompt_frame = ttk.Frame(prompt_section)
        prompt_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        prompt_frame.columnconfigure(0, weight=1)
        
        ttk.Label(prompt_frame, text="Video Prompt (Optional):", font=('Arial', 10, 'bold')).grid(
            row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        self.prompt_text = tk.Text(prompt_frame, height=3, wrap=tk.WORD, font=('Arial', 11))
        self.prompt_text.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        prompt_scroll = ttk.Scrollbar(prompt_frame, orient="vertical", command=self.prompt_text.yview)
        prompt_scroll.grid(row=1, column=1, sticky=(tk.N, tk.S))
        self.prompt_text.configure(yscrollcommand=prompt_scroll.set)
        
        # Prompt actions
        prompt_actions = ttk.Frame(prompt_frame)
        prompt_actions.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        
        ttk.Button(prompt_actions, text="Clear Prompt", 
                  command=lambda: self.prompt_text.delete("1.0", tk.END)).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(prompt_actions, text="Sample Prompt", 
                  command=self.load_sample_prompt).pack(side=tk.LEFT)
        
        # Info label
        info_label = ttk.Label(prompt_section, 
                              text="💡 SeedDance generates high-quality videos from static images. Camera position can be fixed or dynamic.",
                              font=('Arial', 9), foreground='#666666')
        info_label.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
    
    def setup_settings_panel(self):
        """Setup settings panel"""
        self.settings_panel = SettingsPanel(self.frame, 4, "SeedDance Settings")
        
        # Duration
        self.duration_var = tk.StringVar(value="5")
        duration_options = [str(d) for d in Config.SEEDDANCE_DURATIONS]
        self.settings_panel.add_combobox(
            "Duration (seconds)", self.duration_var, duration_options
        )
        
        # Camera Fixed
        self.camera_fixed_var = tk.StringVar(value="True")
        self.settings_panel.add_combobox(
            "Camera Position", self.camera_fixed_var, ["True", "False"]
        )
        
        # Seed
        self.seed_var = tk.StringVar(value="-1")
        self.settings_panel.add_text_field("Seed (-1 for random)", self.seed_var, 15)
    
    def load_sample_prompt(self):
        """Load a sample prompt for demonstration"""
        sample_prompts = [
            "smooth camera movement, cinematic lighting",
            "gentle zoom in, natural motion",
            "dynamic movement, flowing hair",
            "subtle animation, realistic motion",
            "cinematic pan, professional quality",
            "smooth transition, elegant movement"
        ]
        
        import random
        sample = random.choice(sample_prompts)
        self.prompt_text.delete("1.0", tk.END)
        self.prompt_text.insert("1.0", sample)
    
    def on_image_selected(self, image_path):
        """Handle image selection"""
        # Check if replacing existing image
        replacing_image = hasattr(self, 'selected_image_path') and self.selected_image_path is not None
        
        # Use the optimized layout's image selection handler
        original_image = self.optimized_layout.on_image_selected(image_path)
        
        # Store references for compatibility
        self.selected_image_path = image_path
        self.original_image = original_image
        
        # Provide feedback about image replacement
        if replacing_image:
            self.update_status(f"Image replaced: {os.path.basename(image_path)} - Ready for SeedDance")
        else:
            self.update_status(f"Image selected: {os.path.basename(image_path)} - Ready for SeedDance")
    
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
        self.image_selector.selected_path = file_path
        self.image_selector.image_path_label.config(
            text=os.path.basename(file_path), foreground="black"
        )
        self.on_image_selected(file_path)
    
    def setup_prompt_management(self, parent):
        """Setup prompt management UI for SeedDance"""
        # Saved prompts section
        ttk.Label(parent, text="Saved Prompts:", font=('Arial', 9, 'bold')).grid(row=3, column=0, sticky=tk.W, pady=(10, 2))
        
        # Saved prompts listbox with scrollbar
        listbox_frame = ttk.Frame(parent)
        listbox_frame.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        listbox_frame.columnconfigure(0, weight=1)
        
        self.saved_prompts_listbox = tk.Listbox(listbox_frame, height=4, font=('Arial', 9))
        self.saved_prompts_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        listbox_scroll = ttk.Scrollbar(listbox_frame, orient="vertical", command=self.saved_prompts_listbox.yview)
        listbox_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.saved_prompts_listbox.configure(yscrollcommand=listbox_scroll.set)
        
        # Prompt management buttons
        buttons_frame = ttk.Frame(parent)
        buttons_frame.grid(row=5, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        buttons_frame.columnconfigure(0, weight=1)
        buttons_frame.columnconfigure(1, weight=1)
        buttons_frame.columnconfigure(2, weight=1)
        
        ttk.Button(buttons_frame, text="💾 Save", command=self.save_current_prompt, width=8).grid(row=0, column=0, padx=(0, 2))
        ttk.Button(buttons_frame, text="📋 Load", command=self.load_selected_prompt, width=8).grid(row=0, column=1, padx=2)
        ttk.Button(buttons_frame, text="🗑️ Delete", command=self.delete_selected_prompt, width=8).grid(row=0, column=2, padx=(2, 0))
        
        # Load saved prompts into listbox
        self.refresh_prompts_list()

    def refresh_prompts_list(self):
        """Refresh the saved prompts list"""
        self.saved_prompts_listbox.delete(0, tk.END)
        for i, prompt_data in enumerate(self.saved_prompts):
            display_text = prompt_data.get('name', f'Prompt {i+1}')
            self.saved_prompts_listbox.insert(tk.END, display_text)

    def save_current_prompt(self):
        """Save current prompt to the saved prompts list"""
        video_prompt = self.prompt_text.get("1.0", tk.END).strip()
        
        if not video_prompt:
            show_error("Error", "Please enter a video prompt before saving.")
            return
        
        # Create a simple dialog to get prompt name
        from tkinter import simpledialog
        prompt_name = simpledialog.askstring(
            "Save Prompt", 
            "Enter a name for this SeedDance prompt:",
            initialvalue=video_prompt[:30] + "..." if len(video_prompt) > 30 else video_prompt
        )
        
        if prompt_name:
            prompt_data = {
                'name': prompt_name,
                'video_prompt': video_prompt
            }
            
            self.saved_prompts.append(prompt_data)
            save_json_file(self.prompts_file, self.saved_prompts)
            self.refresh_prompts_list()
            show_success("Saved", f"SeedDance prompt '{prompt_name}' saved successfully!")

    def load_selected_prompt(self):
        """Load the selected prompt from the saved prompts list"""
        selection = self.saved_prompts_listbox.curselection()
        if not selection:
            show_error("Error", "Please select a prompt to load.")
            return
        
        prompt_data = self.saved_prompts[selection[0]]
        
        # Load prompt into text area
        self.prompt_text.delete("1.0", tk.END)
        self.prompt_text.insert("1.0", prompt_data.get('video_prompt', ''))
        
        show_success("Loaded", f"SeedDance prompt '{prompt_data['name']}' loaded successfully!")

    def delete_selected_prompt(self):
        """Delete the selected prompt from the saved prompts list"""
        selection = self.saved_prompts_listbox.curselection()
        if not selection:
            show_error("Error", "Please select a prompt to delete.")
            return
        
        prompt_data = self.saved_prompts[selection[0]]
        
        from tkinter import messagebox
        if messagebox.askyesno("Confirm Delete", f"Delete SeedDance prompt '{prompt_data['name']}'?"):
            del self.saved_prompts[selection[0]]
            save_json_file(self.prompts_file, self.saved_prompts)
            self.refresh_prompts_list()
            show_success("Deleted", f"SeedDance prompt '{prompt_data['name']}' deleted successfully!")

    def clear_prompts(self):
        """Clear all prompts"""
        if hasattr(self, 'prompt_text'):
            self.prompt_text.delete("1.0", tk.END)
        # Also clear the image selection
        self.optimized_layout.clear_all()
    
    def update_status(self, message):
        """Update status display"""
        if hasattr(self, 'status_label'):
            self.status_label.config(text=message)
    
    def show_progress(self, message):
        """Show progress"""
        self.update_status(message)
        if hasattr(self, 'progress_bar'):
            self.progress_bar.start()
    
    def hide_progress(self):
        """Hide progress"""
        if hasattr(self, 'progress_bar'):
            self.progress_bar.stop()
    
    def process_task(self):
        """Process SeedDance video generation task"""
        if not self.validate_inputs():
            return
        
        self.show_progress("Starting SeedDance video generation...")
        
        # Start processing in background thread
        thread = threading.Thread(target=self.process_thread)
        thread.daemon = True
        thread.start()
    
    def process_thread(self):
        """Process in background thread"""
        try:
            # Update status
            self.frame.after(0, lambda: self.update_status("Preparing image..."))
            
            # For SeedDance, we need a public URL
            # This is a placeholder - in production, you'd upload the image
            image_url = self.upload_image_for_seeddance(self.selected_image_path)
            if not image_url:
                self.frame.after(0, lambda: self.handle_error("Failed to prepare image for SeedDance video generation"))
                return
            
            # Get parameters
            prompt = self.prompt_text.get("1.0", tk.END).strip()
            duration = int(self.duration_var.get())
            camera_fixed = self.camera_fixed_var.get().lower() == "true"
            
            try:
                seed = int(self.seed_var.get()) if self.seed_var.get().strip() != "-1" else -1
            except ValueError:
                seed = -1
            
            # Update status
            self.frame.after(0, lambda: self.update_status("Submitting SeedDance video generation task..."))
            
            # Submit task
            request_id, error = self.api_client.submit_seeddance_task(
                image_url, duration, prompt, camera_fixed, seed
            )
            
            if error:
                self.frame.after(0, lambda: self.handle_error(error))
                return
            
            self.current_request_id = request_id
            self.frame.after(0, lambda: self.update_status(f"Task submitted. ID: {request_id}"))
            
            # Poll for results
            def progress_callback(status, result):
                self.frame.after(0, lambda: self.update_status(f"Generating video... Status: {status}"))
            
            output_url, error, duration_time = self.api_client.poll_until_complete(
                request_id, progress_callback, poll_interval=2.0  # Longer interval for video
            )
            
            if error:
                self.frame.after(0, lambda: self.handle_error(error))
            else:
                self.frame.after(0, lambda: self.handle_success(output_url, duration_time))
                
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            self.frame.after(0, lambda: self.handle_error(error_msg))
    
    def upload_image_for_seeddance(self, image_path):
        """Upload image and return URL for SeedDance video generation"""
        try:
            # Use the privacy-aware uploader
            from core.secure_upload import privacy_uploader
            success, image_url, privacy_info = privacy_uploader.upload_with_privacy_warning(image_path, 'seeddance')
            
            if success and image_url:
                logger.info(f"SeedDance image uploaded: {privacy_info}")
                
                # Privacy info logged but no popup
                
                return image_url
            else:
                # Fallback to sample URL if upload fails
                sample_url = Config.SAMPLE_URLS.get('seeddance', Config.SAMPLE_URLS.get('seededit'))
                
                self.frame.after(0, lambda: show_warning(
                    "Using Sample Image", 
                    f"Could not upload your image: {privacy_info}\n\n"
                    f"Using sample image for demonstration.\n"
                    f"Your selected image: {os.path.basename(image_path)}"
                ))
                
                return sample_url
                
        except Exception as e:
            logger.error(f"Upload failed: {e}")
            sample_url = Config.SAMPLE_URLS.get('seeddance', Config.SAMPLE_URLS.get('seededit'))
            
            self.frame.after(0, lambda: show_warning(
                "Upload Error", 
                f"Upload failed: {str(e)}\n\nUsing sample image for demonstration."
            ))
            
            return sample_url
    
    def handle_success(self, output_url, duration_time):
        """Handle successful completion"""
        # Hide progress
        self.hide_progress()
        
        # Load video in enhanced player if available
        if self.enhanced_video_player:
            # Download and load the video in the enhanced player
            try:
                # For now, we'll use the existing video handling
                # In the future, we could enhance this to download and load locally
                self.result_video_url = output_url
                self.update_status("SeedDance video generated! Click 'Recent Videos' to load it.")
            except Exception as e:
                logger.error(f"Failed to load video in enhanced player: {e}")
                self.update_status("SeedDance video generated! Available in browser.")
        
        # Auto-save the result
        prompt = self.prompt_text.get("1.0", tk.END).strip() if hasattr(self, 'prompt_text') else ""
        duration = self.duration_var.get()
        camera_fixed = self.camera_fixed_var.get()
        seed = self.seed_var.get()
        extra_info = f"{duration}s_cam{camera_fixed}_seed{seed}"
        
        success, saved_path, error = auto_save_manager.save_result(
            'seeddance', 
            output_url, 
            prompt=prompt,
            extra_info=extra_info,
            file_type="video"
        )
        
        # Update status with success info
        success_msg = f"✅ SeedDance video generated in {format_duration(duration_time)}!"
        if saved_path:
            success_msg += f" Auto-saved locally."
        self.update_status(success_msg)
        
        # Show success dialog
        dialog_msg = f"SeedDance video generated successfully in {format_duration(duration_time)}!"
        if saved_path:
            dialog_msg += f"\n\nAuto-saved to:\n{os.path.basename(saved_path)}"
        dialog_msg += f"\n\nCamera Fixed: {camera_fixed}"
        dialog_msg += f"\nSeed: {seed}"
        dialog_msg += f"\n\nVideo URL: {output_url}"
        
        show_success("SeedDance Complete!", dialog_msg)
    
    def handle_error(self, error_message):
        """Handle error"""
        # Hide progress
        self.hide_progress()
        
        # Update status
        self.update_status(f"❌ Error: {error_message}")
        
        # Show error dialog
        show_error("SeedDance Generation Error", error_message)
    
    def open_video_in_browser(self):
        """Open video in browser"""
        if not self.result_video_url:
            show_error("Error", "No video URL available.")
            return
        
        try:
            webbrowser.open(self.result_video_url)
        except Exception as e:
            show_error("Error", f"Failed to open browser: {str(e)}")
    
    def copy_video_url(self):
        """Copy video URL to clipboard"""
        if not self.result_video_url:
            show_error("Error", "No video URL available.")
            return
        
        try:
            # Copy to clipboard
            self.frame.clipboard_clear()
            self.frame.clipboard_append(self.result_video_url)
            self.frame.update()  # Required for clipboard to work
            show_success("Success", "Video URL copied to clipboard!")
        except Exception as e:
            show_error("Error", f"Failed to copy URL: {str(e)}")
    
    def validate_inputs(self):
        """Validate inputs before processing"""
        # Check if image is selected
        if not self.optimized_layout.get_selected_image():
            show_error("Error", "Please select an image for SeedDance video generation.")
            return False
        
        # Check video-specific inputs
        try:
            duration = int(self.duration_var.get())
            if duration not in [5]:  # SeedDance typically supports 5 seconds
                show_error("Error", "Duration must be 5 seconds for SeedDance.")
                return False
        except ValueError:
            show_error("Error", "Invalid duration value.")
            return False
        
        try:
            seed = self.seed_var.get().strip()
            if seed and seed != "-1":
                seed_int = int(seed)
                if seed_int < -1 or seed_int > 2147483647:
                    show_error("Error", "Seed must be -1 or between 0 and 2147483647.")
                    return False
        except ValueError:
            show_error("Error", "Invalid seed value. Use -1 for random or a valid integer.")
            return False
        
        return True
