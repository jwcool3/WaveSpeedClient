"""
Seedream V4 Tab Component

This module contains the ByteDance Seedream V4 image editing functionality.
The state-of-the-art image model surpassing nano banana in every aspect.
"""

import tkinter as tk
from tkinter import ttk
import threading
import os
from ui.components.ui_components import BaseTab, SettingsPanel
from ui.components.enhanced_image_display import EnhancedImageSelector, EnhancedImagePreview
from ui.components.optimized_image_layout import OptimizedImageLayout
from ui.components.ai_prompt_suggestions import add_ai_features_to_prompt_section
from app.config import Config
from utils.utils import *
from core.auto_save import auto_save_manager
from core.secure_upload import privacy_uploader
from core.logger import get_logger

logger = get_logger()


class SeedreamV4Tab(BaseTab):
    """Seedream V4 Image Editor Tab"""
    
    def __init__(self, parent_frame, api_client, main_app=None):
        self.result_image = None
        self.main_app = main_app  # Reference to main app for cross-tab operations
        
        # Prompt storage for Seedream V4
        self.seedream_v4_prompts_file = "data/seedream_v4_prompts.json"
        self.saved_seedream_v4_prompts = load_json_file(self.seedream_v4_prompts_file, [])
        
        super().__init__(parent_frame, api_client)
    
    def apply_ai_suggestion(self, improved_prompt: str):
        """Apply AI suggestion to prompt text"""
        self.prompt_text.delete("1.0", tk.END)
        self.prompt_text.insert("1.0", improved_prompt)
    
    def setup_ui(self):
        """Setup the optimized Seedream V4 UI"""
        # Hide the scrollable canvas components since we're using direct container layout
        self.canvas.pack_forget()
        self.scrollbar.pack_forget()
        
        # For optimized layout, bypass the scrollable canvas and use the main container directly
        # This ensures full window expansion without canvas constraints
        self.optimized_layout = OptimizedImageLayout(self.container, "Seedream V4")
        
        # Setup the layout with Seedream V4 specific settings
        self.setup_seedream_v4_settings()
        
        # Setup prompt section in the left panel
        self.setup_compact_prompt_section()
        
        # Configure main action button
        self.optimized_layout.set_main_action("🌟 Apply Seedream V4", self.process_task)
        
        # Connect image selector
        self.optimized_layout.set_image_selector_command(self.browse_image)
        
        # Connect result buttons
        self.optimized_layout.set_result_button_commands(
            self.save_result_image, 
            self.use_result_as_editor_input
        )
        
        # Connect sample and clear buttons
        self.optimized_layout.sample_button.config(command=self.load_sample_prompt)
        self.optimized_layout.clear_button.config(command=self.clear_prompts)
        
        # Connect drag and drop handling
        self.optimized_layout.set_parent_tab(self)
        
        # Setup cross-tab sharing
        self.optimized_layout.create_cross_tab_button(self.main_app, "Seedream V4")
        
        # Setup progress section in the left panel
        self.setup_compact_progress_section()
    
    def browse_image(self):
        """Browse for image file"""
        from tkinter import filedialog
        
        file_path = filedialog.askopenfilename(
            title="Select Image for Seedream V4",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.gif *.bmp *.webp"),
                ("PNG files", "*.png"),
                ("JPEG files", "*.jpg *.jpeg"),
                ("All files", "*.*")
            ]
        )
        if file_path:
            self.on_image_selected(file_path)
    
    def setup_seedream_v4_settings(self):
        """Setup Seedream V4 specific settings"""
        # Image Size setting
        size_frame = ttk.Frame(self.optimized_layout.settings_container)
        size_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        size_frame.columnconfigure(1, weight=1)
        
        ttk.Label(size_frame, text="Size:", font=('Arial', 9)).grid(row=0, column=0, sticky=tk.W)
        self.size_var = tk.StringVar(value="2048*2048")
        size_combo = ttk.Combobox(size_frame, textvariable=self.size_var, 
                                 values=Config.SEEDREAM_V4_SIZES, 
                                 state="readonly", width=12)
        size_combo.grid(row=0, column=1, sticky=tk.E, padx=(5, 0))
        
        # Seed setting
        seed_frame = ttk.Frame(self.optimized_layout.settings_container)
        seed_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        seed_frame.columnconfigure(1, weight=1)
        
        ttk.Label(seed_frame, text="Seed:", font=('Arial', 9)).grid(row=0, column=0, sticky=tk.W)
        self.seed_var = tk.StringVar(value="-1")
        seed_entry = ttk.Entry(seed_frame, textvariable=self.seed_var, width=10)
        seed_entry.grid(row=0, column=1, sticky=tk.E, padx=(5, 0))
    
    def setup_compact_prompt_section(self):
        """Setup compact prompt section for Seedream V4"""
        prompt_container = self.optimized_layout.prompt_container
        
        # Multi-line prompt entry
        ttk.Label(prompt_container, text="Editing Instruction:", font=('Arial', 9, 'bold')).grid(row=0, column=0, sticky=tk.W, pady=(0, 2))
        
        # Create text widget with scrollbar
        text_frame = ttk.Frame(prompt_container)
        text_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 5))
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)
        
        self.prompt_text = tk.Text(text_frame, height=4, width=30, wrap=tk.WORD, font=('Arial', 9))
        prompt_scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=self.prompt_text.yview)
        self.prompt_text.configure(yscrollcommand=prompt_scrollbar.set)
        
        self.prompt_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        prompt_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Prompt guidance
        guidance_label = ttk.Label(prompt_container, 
                                  text="💡 Use clear instructions:\n'change action + change object + target feature'", 
                                  font=('Arial', 8), foreground="gray")
        guidance_label.grid(row=2, column=0, sticky=tk.W, pady=(0, 5))
        
        # Setup prompt management UI
        self.setup_prompt_management(prompt_container)
        
        # Add AI features
        add_ai_features_to_prompt_section(
            prompt_container, 
            self.prompt_text, 
            "Seedream V4",
            on_suggestion_selected=self.apply_ai_suggestion
        )
    
    def setup_prompt_management(self, parent):
        """Setup prompt management UI for Seedream V4"""
        # Saved prompts section
        ttk.Label(parent, text="Saved Prompts:", font=('Arial', 9, 'bold')).grid(row=3, column=0, sticky=tk.W, pady=(10, 2))
        
        # Saved prompts listbox with scrollbar
        listbox_frame = ttk.Frame(parent)
        listbox_frame.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        listbox_frame.columnconfigure(0, weight=1)
        
        self.prompts_listbox = tk.Listbox(listbox_frame, height=4, font=('Arial', 8))
        prompts_scrollbar = ttk.Scrollbar(listbox_frame, orient="vertical", command=self.prompts_listbox.yview)
        self.prompts_listbox.configure(yscrollcommand=prompts_scrollbar.set)
        
        self.prompts_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E))
        prompts_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Prompt management buttons
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=5, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        button_frame.columnconfigure(2, weight=1)
        
        ttk.Button(button_frame, text="Save", command=self.save_current_prompt, width=8).grid(row=0, column=0, padx=(0, 2))
        ttk.Button(button_frame, text="Load", command=self.load_selected_prompt, width=8).grid(row=0, column=1, padx=1)
        ttk.Button(button_frame, text="Delete", command=self.delete_selected_prompt, width=8).grid(row=0, column=2, padx=(2, 0))
        
        # Bind listbox selection
        self.prompts_listbox.bind('<Double-Button-1>', lambda e: self.load_selected_prompt())
        
        # Populate saved prompts
        self.refresh_prompts_list()
    
    def load_sample_prompt(self):
        """Load sample prompt for Seedream V4"""
        sample_prompts = [
            "Transform the person into a Renaissance-style painting with oil paint texture and classical lighting",
            "Change the background to a futuristic cyberpunk cityscape with neon lights",
            "Convert this image to anime style with vibrant colors and stylized features",
            "Add magical elements like floating particles and glowing effects around the subject",
            "Transform the scene to vintage black and white photography with film grain",
            "Change the clothing style to medieval fantasy armor with intricate details"
        ]
        
        import random
        sample = random.choice(sample_prompts)
        self.prompt_text.delete("1.0", tk.END)
        self.prompt_text.insert("1.0", sample)
    
    def clear_prompts(self):
        """Clear the prompt text"""
        self.prompt_text.delete("1.0", tk.END)
    
    def save_current_prompt(self):
        """Save the current prompt"""
        prompt = self.prompt_text.get("1.0", tk.END).strip()
        if prompt and prompt not in self.saved_seedream_v4_prompts:
            self.saved_seedream_v4_prompts.append(prompt)
            save_json_file(self.seedream_v4_prompts_file, self.saved_seedream_v4_prompts)
            self.refresh_prompts_list()
            self.update_status("Prompt saved successfully")
    
    def load_selected_prompt(self):
        """Load the selected prompt"""
        selection = self.prompts_listbox.curselection()
        if selection:
            prompt = self.saved_seedream_v4_prompts[selection[0]]
            self.prompt_text.delete("1.0", tk.END)
            self.prompt_text.insert("1.0", prompt)
    
    def delete_selected_prompt(self):
        """Delete the selected prompt"""
        selection = self.prompts_listbox.curselection()
        if selection:
            del self.saved_seedream_v4_prompts[selection[0]]
            save_json_file(self.seedream_v4_prompts_file, self.saved_seedream_v4_prompts)
            self.refresh_prompts_list()
            self.update_status("Prompt deleted")
    
    def refresh_prompts_list(self):
        """Refresh the prompts listbox"""
        self.prompts_listbox.delete(0, tk.END)
        for prompt in self.saved_seedream_v4_prompts:
            display_text = prompt[:50] + "..." if len(prompt) > 50 else prompt
            self.prompts_listbox.insert(tk.END, display_text)
    
    def on_image_selected(self, image_path, replacing_image=False):
        """Handle image selection for Seedream V4"""
        logger.info(f"Seedream V4 image selected: {image_path}")
        
        # Let the optimized layout handle the image display
        original_image = self.optimized_layout.on_image_selected(image_path)
        
        # Store references for compatibility
        self.selected_image_path = image_path
        self.original_image = original_image
        
        # Provide feedback about image replacement
        if replacing_image:
            self.update_status(f"Image replaced: {os.path.basename(image_path)} - Ready for Seedream V4")
        else:
            self.update_status(f"Image selected: {os.path.basename(image_path)} - Ready for Seedream V4")
    
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
    
    def setup_compact_progress_section(self):
        """Setup compact progress section in the left panel"""
        progress_container = self.optimized_layout.status_container
        
        # Status label
        self.status_label = ttk.Label(progress_container, text="Ready for Seedream V4", 
                                     font=('Arial', 9), foreground="green")
        self.status_label.pack(anchor=tk.W, pady=(0, 5))
        
        # Progress bar (initially hidden)
        self.progress_bar = ttk.Progressbar(progress_container, mode='indeterminate')
        
        # Request ID label (initially hidden)
        self.request_id_label = ttk.Label(progress_container, text="", 
                                         font=('Arial', 8), foreground="gray")
    
    def show_progress(self, message):
        """Show progress indicator"""
        self.status_label.config(text=message, foreground="blue")
        self.progress_bar.pack(fill=tk.X, pady=(0, 5))
        self.progress_bar.start()
    
    def hide_progress(self):
        """Hide progress indicator"""
        self.progress_bar.stop()
        self.progress_bar.pack_forget()
        if hasattr(self, 'request_id_label'):
            self.request_id_label.pack_forget()
    
    def update_status(self, message):
        """Update status message"""
        if "error" in message.lower() or "failed" in message.lower():
            color = "red"
        elif "processing" in message.lower() or "submitting" in message.lower():
            color = "blue"
        else:
            color = "green"
        
        self.status_label.config(text=message, foreground=color)
    
    def process_task(self):
        """Process Seedream V4 image editing task"""
        # Validation
        if not hasattr(self, 'selected_image_path') or not self.selected_image_path:
            show_error("No Image", "Please select an image first.")
            return
        
        prompt = self.prompt_text.get("1.0", tk.END).strip()
        if not prompt:
            show_error("No Prompt", "Please enter an editing instruction.")
            return
        
        self.show_progress("Starting Seedream V4 processing...")
        
        # Start processing in background thread
        thread = threading.Thread(target=self.process_thread, args=(prompt,))
        thread.daemon = True
        thread.start()
    
    def process_thread(self, prompt):
        """Process in background thread"""
        try:
            # Notify tab manager of processing start
            if hasattr(self.main_app, 'tab_manager'):
                tab_index = self.main_app.get_current_tab_index()
                self.main_app.tab_manager.set_tab_processing(tab_index, True)
            
            # Update status
            self.frame.after(0, lambda: self.update_status("Preparing image..."))
            
            # Upload image for Seedream V4
            image_url = self.upload_image_for_seedream_v4(self.selected_image_path)
            if not image_url:
                self.frame.after(0, lambda: self.handle_error("Failed to prepare image for Seedream V4"))
                return
            
            # Get parameters
            size = self.size_var.get()
            
            try:
                seed = int(self.seed_var.get()) if self.seed_var.get().strip() != "-1" else -1
                if seed != -1 and not (Config.SEED_RANGE[0] <= seed <= Config.SEED_RANGE[1]):
                    raise ValueError("Seed out of range")
            except ValueError:
                self.frame.after(0, lambda: self.handle_error("Invalid seed. Use -1 for random or a valid integer"))
                return
            
            # Update status
            self.frame.after(0, lambda: self.update_status("Submitting Seedream V4 task..."))
            
            # Submit task
            request_id, error = self.api_client.submit_seedream_v4_task(
                image_url, prompt, size, seed
            )
            
            if error:
                self.frame.after(0, lambda: self.handle_error(error))
                return
            
            self.current_request_id = request_id
            self.frame.after(0, lambda: self.update_status(f"Task submitted. ID: {request_id}"))
            
            # Poll for results
            def progress_callback(status, result):
                self.frame.after(0, lambda: self.update_status(f"Processing... Status: {status}"))
            
            output_url, error, duration = self.api_client.poll_until_complete(
                request_id, progress_callback, poll_interval=0.5  # Faster polling for Seedream V4
            )
            
            if error:
                self.frame.after(0, lambda: self.handle_error(error))
            else:
                self.frame.after(0, lambda: self.handle_success(output_url, duration))
                
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            self.frame.after(0, lambda: self.handle_error(error_msg))
        finally:
            # Clear processing indicator
            if hasattr(self.main_app, 'tab_manager'):
                tab_index = self.main_app.get_current_tab_index()
                self.main_app.tab_manager.set_tab_processing(tab_index, False)
    
    def upload_image_for_seedream_v4(self, image_path):
        """Upload image securely for Seedream V4"""
        try:
            # Use privacy-friendly upload
            success, url, privacy_info = privacy_uploader.upload_with_privacy_warning(image_path, 'seedream_v4')
            
            if success:
                logger.info(f"Seedream V4 image uploaded: {privacy_info}")
                return url
            else:
                # Fallback to sample URL with explanation
                self.frame.after(0, lambda: show_warning(
                    "Upload Failed - Using Sample", 
                    f"Could not upload your image securely.\n\n"
                    f"Error: {privacy_info}\n\n"
                    f"Using sample image for demonstration.\n"
                    f"Your selected image: {image_path}\n\n"
                    f"To use your own images, ensure internet connection\n"
                    f"or implement a custom upload solution."
                ))
                
                return Config.SAMPLE_URLS['seedream_v4']
                
        except Exception as e:
            logger.error(f"Seedream V4 upload error: {e}")
            
            # Fallback to sample URL
            self.frame.after(0, lambda: show_error(
                "Upload Error", 
                f"Failed to upload image: {str(e)}\n\n"
                f"Using sample image for demonstration."
            ))
            
            return Config.SAMPLE_URLS['seedream_v4']
    
    def handle_success(self, output_url, duration):
        """Handle successful processing"""
        self.hide_progress()
        self.update_status(f"✅ Seedream V4 completed in {duration:.1f}s")
        
        # Notify tab manager of success
        if hasattr(self.main_app, 'tab_manager'):
            tab_index = self.main_app.get_current_tab_index()
            self.main_app.tab_manager.set_tab_success(tab_index)
        
        # Display result
        self.optimized_layout.display_result(output_url)
        self.result_image = output_url
        
        # Auto-save with enhanced info
        prompt = self.prompt_text.get("1.0", tk.END).strip()
        size = self.size_var.get()
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
        show_error("Seedream V4 Error", error_message)
        
        # Notify tab manager of error
        if hasattr(self.main_app, 'tab_manager'):
            tab_index = self.main_app.get_current_tab_index()
            self.main_app.tab_manager.set_tab_error(tab_index)
    
    def save_result_image(self):
        """Save the result image"""
        if not self.result_image:
            show_error("No Result", "No result image to save.")
            return
        
        from tkinter import filedialog
        file_path = filedialog.asksaveasfilename(
            title="Save Seedream V4 Result",
            defaultextension=".png",
            filetypes=[
                ("PNG files", "*.png"),
                ("JPEG files", "*.jpg"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            success = download_and_save_image(self.result_image, file_path)
            if success:
                self.update_status(f"Result saved: {os.path.basename(file_path)}")
            else:
                show_error("Save Failed", "Failed to save the result image.")
    
    def use_result_as_editor_input(self):
        """Send result to Nano Banana Editor"""
        if not self.result_image or not self.main_app:
            show_error("No Result", "No result image to send to editor.")
            return
        
        try:
            # Download result image to temp file
            temp_path = download_temp_image(self.result_image, "seedream_v4_to_editor")
            if temp_path:
                # Switch to editor tab and load image
                self.main_app.notebook.select(0)  # Editor is first tab
                self.update_status("Result sent to Nano Banana Editor")
                self.main_app.editor_tab.on_image_selected(temp_path)
                
        except Exception as e:
            show_error("Error", f"Failed to switch to editor: {str(e)}")
