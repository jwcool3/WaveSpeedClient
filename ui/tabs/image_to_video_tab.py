"""
Image to Video Tab Component

This module contains the image-to-video functionality.
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


class ImageToVideoTab(BaseTab, VideoPlayerMixin):
    """Image to Video Tab"""
    
    def __init__(self, parent_frame, api_client, main_app=None):
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
        """Setup the optimized image-to-video UI with new Wan 2.2 layout"""
        # Hide the scrollable canvas components since we're using direct container layout
        self.canvas.pack_forget()
        self.scrollbar.pack_forget()
        
        # Use the new optimized Wan 2.2 layout instead of the generic optimized layout
        from ui.components.optimized_wan22_layout import OptimizedWan22Layout
        self.optimized_layout = OptimizedWan22Layout(self.container)
        
        # Connect the optimized layout methods to our existing functionality
        self.connect_optimized_layout()
        
        # Setup video-specific settings in the optimized layout
        self.setup_video_settings_optimized()
        
        # Setup progress section in the optimized layout
        self.setup_compact_progress_section_optimized()
        
        logger.info("Optimized Wan 2.2 UI setup complete")
    
    def connect_optimized_layout(self):
        """Connect the optimized layout methods to our existing functionality"""
        # Connect image browsing
        self.optimized_layout.browse_image = self.browse_image
        
        # Connect processing
        self.optimized_layout.process_video_generation = self.process_task
        
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
        self.video_prompt_text = self.optimized_layout.video_prompt_text
        self.negative_prompt_text = self.optimized_layout.negative_prompt_text
        self.duration_var = self.optimized_layout.duration_var
        self.seed_var = self.optimized_layout.seed_var
        self.last_image_var = self.optimized_layout.last_image_url_var
        self.status_label = self.optimized_layout.status_label
        self.progress_bar = self.optimized_layout.progress_bar
        self.generate_btn = self.optimized_layout.generate_btn
        
        # For backward compatibility, also set prompt_text
        self.prompt_text = self.video_prompt_text
    
    def play_in_system_placeholder(self):
        """Placeholder for play in system functionality"""
        if hasattr(self, 'result_video_url') and self.result_video_url:
            self.status_label.config(text="📱 Opening in system player...", foreground="blue")
    
    def download_video_placeholder(self):
        """Placeholder for download video functionality"""
        if hasattr(self, 'result_video_url') and self.result_video_url:
            self.status_label.config(text="💾 Video downloaded", foreground="green")
    
    def improve_with_ai_placeholder(self):
        """Placeholder for AI improvement functionality"""
        # This would connect to your existing AI improvement system
        pass
    
    def on_saved_prompt_selected_placeholder(self, event):
        """Placeholder for saved prompt selection"""
        # This would connect to your existing saved prompt system
        pass
    
    def setup_video_settings_optimized(self):
        """Setup video-specific settings in the optimized layout"""
        # The optimized layout already has video settings built-in
        # We just need to connect our existing functionality
        pass
    
    def setup_compact_progress_section_optimized(self):
        """Setup compact progress section in the optimized layout"""
        # The optimized layout already has the progress section built-in
        # We just need to connect our existing functionality
        pass
    
    def setup_video_settings(self):
        """Setup video generation settings in the optimized layout"""
        settings_container = self.optimized_layout.settings_container
        
        # Duration setting
        duration_frame = ttk.Frame(settings_container)
        duration_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=2)
        duration_frame.columnconfigure(1, weight=1)
        
        ttk.Label(duration_frame, text="Duration:", font=('Arial', 9)).grid(row=0, column=0, sticky=tk.W)
        self.duration_var = tk.StringVar(value="5")
        duration_combo = ttk.Combobox(duration_frame, textvariable=self.duration_var, 
                                     values=["5", "8"], state="readonly", width=8)
        duration_combo.grid(row=0, column=1, sticky=tk.E, padx=(5, 0))
        
        # Seed setting
        seed_frame = ttk.Frame(settings_container)
        seed_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=2)
        seed_frame.columnconfigure(1, weight=1)
        
        ttk.Label(seed_frame, text="Seed:", font=('Arial', 9)).grid(row=0, column=0, sticky=tk.W)
        self.seed_var = tk.StringVar(value="-1")
        seed_entry = ttk.Entry(seed_frame, textvariable=self.seed_var, width=10)
        seed_entry.grid(row=0, column=1, sticky=tk.E, padx=(5, 0))
        
        # Last image URL (optional)
        url_frame = ttk.Frame(settings_container)
        url_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=2)
        url_frame.columnconfigure(0, weight=1)
        
        ttk.Label(url_frame, text="Last Image URL (optional):", font=('Arial', 9)).grid(row=0, column=0, sticky=tk.W)
        self.last_image_var = tk.StringVar(value="")
        url_entry = ttk.Entry(url_frame, textvariable=self.last_image_var)
        url_entry.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(2, 0))
    
    def setup_compact_prompt_section(self):
        """Setup compact prompt section"""
        # Add prompt section below settings (in the spacer area)
        prompt_frame = ttk.LabelFrame(self.optimized_layout.settings_frame.master, text="🎬 Wan 2.2 Prompts", padding="8")
        prompt_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N), pady=(10, 0))
        prompt_frame.columnconfigure(0, weight=1)
        
        # Video prompt
        ttk.Label(prompt_frame, text="Video Prompt:", font=('Arial', 9, 'bold')).grid(row=0, column=0, sticky=tk.W)
        self.prompt_text = tk.Text(prompt_frame, height=3, wrap=tk.WORD, font=('Arial', 10))
        self.prompt_text.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(2, 5))
        
        # Negative prompt
        ttk.Label(prompt_frame, text="Negative Prompt:", font=('Arial', 9, 'bold')).grid(row=2, column=0, sticky=tk.W)
        self.negative_prompt_text = tk.Text(prompt_frame, height=2, wrap=tk.WORD, font=('Arial', 10))
        self.negative_prompt_text.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(2, 5))
        
        # Prompt management section
        self.setup_prompt_management(prompt_frame)
        
        # Add AI features
        add_ai_features_to_prompt_section(
            prompt_frame, 
            self.prompt_text, 
            "Wan 2.2",
            on_suggestion_selected=self.apply_ai_suggestion
        )
    
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
        self.status_label = ttk.Label(progress_frame, text="Ready for Wan 2.2 generation", font=('Arial', 8))
        self.status_label.grid(row=1, column=0, sticky=tk.W)
    
    def setup_video_result_section(self):
        """Setup video result display section (now handled by optimized layout)"""
        # Video display is now handled by the OptimizedVideoLayout
        # The enhanced video player is already created and available
        pass
    
    def setup_prompt_section(self):
        """Setup prompt section for video generation"""
        prompt_section = ttk.LabelFrame(self.frame, text="Video Generation Prompts", padding="10")
        prompt_section.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 10))
        prompt_section.columnconfigure(0, weight=1)
        
        # Main prompt
        prompt_frame = ttk.Frame(prompt_section)
        prompt_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        prompt_frame.columnconfigure(0, weight=1)
        
        ttk.Label(prompt_frame, text="Video Prompt:", font=('Arial', 10, 'bold')).grid(
            row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        self.prompt_text = tk.Text(prompt_frame, height=3, wrap=tk.WORD, font=('Arial', 11))
        self.prompt_text.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        prompt_scroll = ttk.Scrollbar(prompt_frame, orient="vertical", command=self.prompt_text.yview)
        prompt_scroll.grid(row=1, column=1, sticky=(tk.N, tk.S))
        self.prompt_text.configure(yscrollcommand=prompt_scroll.set)
        
        # Negative prompt
        neg_prompt_frame = ttk.Frame(prompt_section)
        neg_prompt_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        neg_prompt_frame.columnconfigure(0, weight=1)
        
        ttk.Label(neg_prompt_frame, text="Negative Prompt (Optional):", font=('Arial', 10, 'bold')).grid(
            row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        self.negative_prompt_text = tk.Text(neg_prompt_frame, height=2, wrap=tk.WORD, font=('Arial', 11))
        self.negative_prompt_text.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        neg_prompt_scroll = ttk.Scrollbar(neg_prompt_frame, orient="vertical", 
                                        command=self.negative_prompt_text.yview)
        neg_prompt_scroll.grid(row=1, column=1, sticky=(tk.N, tk.S))
        self.negative_prompt_text.configure(yscrollcommand=neg_prompt_scroll.set)
        
        # Prompt actions
        prompt_actions = ttk.Frame(prompt_section)
        prompt_actions.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        
        ttk.Button(prompt_actions, text="Clear Prompts", 
                  command=self.clear_prompts).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(prompt_actions, text="Sample Prompt", 
                  command=self.load_sample_prompt).pack(side=tk.LEFT)
    
    def setup_settings_panel(self):
        """Setup settings panel"""
        self.settings_panel = SettingsPanel(self.frame, 4, "Video Generation Settings")
        
        # Duration
        self.duration_var = tk.StringVar(value="5")
        self.settings_panel.add_combobox(
            "Duration (seconds)", self.duration_var, ["5", "8"]
        )
        
        # Seed
        self.seed_var = tk.StringVar(value="-1")
        self.settings_panel.add_text_field("Seed (-1 for random)", self.seed_var, 15)
        
        # Last image (optional)
        self.last_image_var = tk.StringVar(value="")
        self.settings_panel.add_text_field("Last Image URL (optional)", self.last_image_var, 30)
    
    def on_image_selected(self, image_path, replacing_image=False):
        """Handle image selection"""
        # Check if replacing existing image (use parameter or detect automatically)
        if not replacing_image:
            replacing_image = hasattr(self, 'selected_image_path') and self.selected_image_path is not None
        
        # Update the optimized layout with the new image
        if hasattr(self.optimized_layout, 'load_image'):
            # Use the new optimized layout's load_image method
            self.optimized_layout.load_image(image_path)
        else:
            # Fallback to old layout if optimized layout not available
            original_image = self.optimized_layout.on_image_selected(image_path)
            self.original_image = original_image
        
        # Store references for compatibility
        self.selected_image_path = image_path
        
        # Provide feedback about image replacement
        if replacing_image:
            self.update_status(f"Image replaced: {os.path.basename(image_path)} - Ready to generate video")
        else:
            self.update_status(f"Image selected: {os.path.basename(image_path)} - Ready to generate video")
    
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
        """Setup prompt management UI"""
        # Saved prompts section
        ttk.Label(parent, text="Saved Prompts:", font=('Arial', 9, 'bold')).grid(row=4, column=0, sticky=tk.W, pady=(10, 2))
        
        # Saved prompts listbox with scrollbar
        listbox_frame = ttk.Frame(parent)
        listbox_frame.grid(row=5, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        listbox_frame.columnconfigure(0, weight=1)
        
        self.saved_prompts_listbox = tk.Listbox(listbox_frame, height=4, font=('Arial', 9))
        self.saved_prompts_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        listbox_scroll = ttk.Scrollbar(listbox_frame, orient="vertical", command=self.saved_prompts_listbox.yview)
        listbox_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.saved_prompts_listbox.configure(yscrollcommand=listbox_scroll.set)
        
        # Prompt management buttons
        buttons_frame = ttk.Frame(parent)
        buttons_frame.grid(row=6, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
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
        negative_prompt = self.negative_prompt_text.get("1.0", tk.END).strip()
        
        if not video_prompt:
            show_error("Error", "Please enter a video prompt before saving.")
            return
        
        # Create a simple dialog to get prompt name
        from tkinter import simpledialog
        prompt_name = simpledialog.askstring(
            "Save Prompt", 
            "Enter a name for this prompt:",
            initialvalue=video_prompt[:30] + "..." if len(video_prompt) > 30 else video_prompt
        )
        
        if prompt_name:
            prompt_data = {
                'name': prompt_name,
                'video_prompt': video_prompt,
                'negative_prompt': negative_prompt
            }
            
            self.saved_prompts.append(prompt_data)
            save_json_file(self.prompts_file, self.saved_prompts)
            self.refresh_prompts_list()
            # Prompt saved successfully (no popup needed)

    def load_selected_prompt(self):
        """Load the selected prompt from the saved prompts list"""
        selection = self.saved_prompts_listbox.curselection()
        if not selection:
            show_error("Error", "Please select a prompt to load.")
            return
        
        prompt_data = self.saved_prompts[selection[0]]
        
        # Load prompts into text areas
        self.prompt_text.delete("1.0", tk.END)
        self.prompt_text.insert("1.0", prompt_data.get('video_prompt', ''))
        
        self.negative_prompt_text.delete("1.0", tk.END)
        self.negative_prompt_text.insert("1.0", prompt_data.get('negative_prompt', ''))
        
        # Prompt loaded successfully (no popup needed)

    def delete_selected_prompt(self):
        """Delete the selected prompt from the saved prompts list"""
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
            # Prompt deleted successfully (no popup needed)

    def clear_prompts(self):
        """Clear all prompts"""
        if hasattr(self.optimized_layout, 'clear_all'):
            # Use the optimized layout's clear_all method
            self.optimized_layout.clear_all()
        else:
            # Fallback to old layout
            self.prompt_text.delete("1.0", tk.END)
            self.negative_prompt_text.delete("1.0", tk.END)
            self.optimized_layout.clear_all()
    
    def load_sample_prompt(self):
        """Load a sample prompt for demonstration"""
        sample_prompt = "A beautiful woman walking through a garden, gentle breeze, natural lighting, cinematic movement"
        self.prompt_text.delete("1.0", tk.END)
        self.prompt_text.insert("1.0", sample_prompt)
        
        sample_negative = "blurry, low quality, static, no movement"
        self.negative_prompt_text.delete("1.0", tk.END)
        self.negative_prompt_text.insert("1.0", sample_negative)
    
    def update_status(self, message):
        """Update status display"""
        if hasattr(self.optimized_layout, 'status_label'):
            # Use the optimized layout's status label
            self.optimized_layout.status_label.config(text=message)
        elif hasattr(self, 'status_label'):
            # Fallback to old status label
            self.status_label.config(text=message)
    
    def show_progress(self, message):
        """Show progress"""
        self.update_status(message)
        if hasattr(self.optimized_layout, 'progress_bar'):
            # Use the optimized layout's progress bar
            self.optimized_layout.progress_bar.start()
        elif hasattr(self, 'progress_bar'):
            # Fallback to old progress bar
            self.progress_bar.start()
    
    def hide_progress(self):
        """Hide progress"""
        if hasattr(self.optimized_layout, 'progress_bar'):
            # Use the optimized layout's progress bar
            self.optimized_layout.progress_bar.stop()
        elif hasattr(self, 'progress_bar'):
            # Fallback to old progress bar
            self.progress_bar.stop()
    
    def process_task(self):
        """Process image-to-video task"""
        if not self.validate_inputs():
            return
        
        prompt = self.prompt_text.get("1.0", tk.END).strip()
        if not prompt:
            show_error("Error", "Please enter a video prompt.")
            return
        
        self.show_progress("Starting video generation...")
        
        # Start processing in background thread
        thread = threading.Thread(target=self.process_thread, args=(prompt,))
        thread.daemon = True
        thread.start()
    
    def process_thread(self, prompt):
        """Process in background thread"""
        try:
            # Update status
            self.frame.after(0, lambda: self.update_status("Preparing image..."))
            
            # For video generation, we need a public URL
            # This is a placeholder - in production, you'd upload the image
            image_url = self.upload_image_for_video(self.selected_image_path)
            if not image_url:
                self.frame.after(0, lambda: self.handle_error("Failed to prepare image for video generation"))
                return
            
            # Get parameters
            negative_prompt = self.negative_prompt_text.get("1.0", tk.END).strip()
            last_image = self.last_image_var.get().strip()
            duration = int(self.duration_var.get())
            
            try:
                seed = int(self.seed_var.get())
            except ValueError:
                seed = -1
            
            # Update status
            self.frame.after(0, lambda: self.update_status("Submitting video generation task..."))
            
            # Submit task
            request_id, error = self.api_client.submit_image_to_video_task(
                image_url, prompt, duration, negative_prompt, last_image, seed
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
    
    def upload_image_for_video(self, image_path):
        """Upload image and return URL for video generation"""
        try:
            # Use the privacy-aware uploader
            from core.secure_upload import privacy_uploader
            success, image_url, privacy_info = privacy_uploader.upload_with_privacy_warning(image_path, 'video')
            
            if success and image_url:
                logger.info(f"Image to Video upload: {privacy_info}")
                
                # Privacy info logged but no popup
                
                return image_url
            else:
                # Fallback to sample URL if upload fails
                sample_url = Config.SAMPLE_URLS.get('video', Config.SAMPLE_URLS.get('seededit'))
                
                # Show enhanced warning dialog
                self.frame.after(0, lambda: self._show_sample_image_warning(
                    image_path, 'video', privacy_info
                ))
                
                return sample_url
                
        except Exception as e:
            logger.error(f"Upload failed: {e}")
            sample_url = Config.SAMPLE_URLS.get('video', Config.SAMPLE_URLS.get('seededit'))
            error_msg = str(e)  # Capture the error message
            
            # Show enhanced warning dialog
            self.frame.after(0, lambda: self._show_sample_image_warning(
                image_path, 'video', f"Upload error: {error_msg}"
            ))
            
            return sample_url
    
    def _show_sample_image_warning(self, image_path, ai_model, reason):
        """Show enhanced warning dialog for sample image usage"""
        from utils.warning_dialogs import show_sample_image_warning
        show_sample_image_warning(self.frame, image_path, ai_model, reason)
    
    def handle_success(self, output_url, duration_time):
        """Handle successful completion"""
        # Hide progress
        self.hide_progress()
        
        # Update the optimized layout with the result
        if hasattr(self.optimized_layout, 'result_video_path'):
            # For the optimized layout, we need to set the result video path
            self.optimized_layout.result_video_path = output_url
            self.optimized_layout.show_video_ready()
            self.result_video_url = output_url
        else:
            # Fallback to old layout
            if self.modern_video_player:
                try:
                    self.modern_video_player.load_video(output_url)
                    self.result_video_url = output_url
                except Exception as e:
                    logger.error(f"Failed to load video in modern player: {e}")
        
        # Auto-save the result
        prompt = self.prompt_text.get("1.0", tk.END).strip()
        duration = self.duration_var.get()
        seed = self.seed_var.get()
        extra_info = f"{duration}s_seed{seed}"
        
        success, saved_path, error = auto_save_manager.save_result(
            'video', 
            output_url, 
            prompt=prompt,
            extra_info=extra_info,
            file_type="video"
        )
        
        # Update status with success info
        success_msg = f"✅ Video generated in {format_duration(duration_time)}!"
        if saved_path:
            success_msg += f" Auto-saved locally."
        self.update_status(success_msg)
        
        # Show success dialog
        dialog_msg = f"Video generated successfully in {format_duration(duration_time)}!"
        if saved_path:
            dialog_msg += f"\n\nAuto-saved to:\n{os.path.basename(saved_path)}"
        dialog_msg += f"\n\nVideo URL: {output_url}"
        
        # Video generated successfully (no popup needed)
    
    def handle_error(self, error_message):
        """Handle error"""
        # Hide progress
        self.hide_progress()
        
        # Update status
        self.update_status(f"❌ Error: {error_message}")
        
        # Show error dialog
        show_error("Wan 2.2 Generation Error", error_message)
    
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
            # Video URL copied to clipboard (no popup needed)
        except Exception as e:
            show_error("Error", f"Failed to copy URL: {str(e)}")
    
    def validate_inputs(self):
        """Validate inputs before processing"""
        # Check if image is selected
        if not self.optimized_layout.get_selected_image():
            show_error("Error", "Please select an image for video generation.")
            return False
        
        # Check video-specific inputs
        try:
            duration = int(self.duration_var.get())
            if duration not in [5, 8]:
                show_error("Error", "Duration must be 5 or 8 seconds.")
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
