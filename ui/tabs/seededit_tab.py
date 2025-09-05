"""
SeedEdit Tab Component

This module contains the ByteDance SeedEdit-v3 image editing functionality.
"""

import tkinter as tk
from tkinter import ttk
import threading
import os
from ui.components.ui_components import BaseTab, SettingsPanel
from ui.components.enhanced_image_display import EnhancedImageSelector, EnhancedImagePreview
from ui.components.optimized_image_layout import OptimizedImageLayout
from app.config import Config
from utils.utils import *
from core.auto_save import auto_save_manager
from core.secure_upload import privacy_uploader
from core.logger import get_logger

logger = get_logger()


class SeedEditTab(BaseTab):
    """SeedEdit Image Editor Tab"""
    
    def __init__(self, parent_frame, api_client, main_app=None):
        self.result_image = None
        self.main_app = main_app  # Reference to main app for cross-tab operations
        
        # Prompt storage for SeedEdit
        self.seededit_prompts_file = "data/seededit_prompts.json"
        self.saved_seededit_prompts = load_json_file(self.seededit_prompts_file, [])
        
        super().__init__(parent_frame, api_client)
    
    def setup_ui(self):
        """Setup the optimized SeedEdit UI"""
        # Hide the scrollable canvas components since we're using direct container layout
        self.canvas.pack_forget()
        self.scrollbar.pack_forget()
        
        # For optimized layout, bypass the scrollable canvas and use the main container directly
        # This ensures full window expansion without canvas constraints
        self.optimized_layout = OptimizedImageLayout(self.container, "SeedEdit")
        
        # Setup the layout with SeedEdit specific settings
        self.setup_seededit_settings()
        
        # Setup prompt section in the left panel
        self.setup_compact_prompt_section()
        
        # Configure main action button
        self.optimized_layout.set_main_action("🌱 Apply SeedEdit", self.process_task)
        
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
        self.optimized_layout.create_cross_tab_button(self.main_app, "SeedEdit")
        
        # Setup progress section in the left panel
        self.setup_compact_progress_section()
    
    def browse_image(self):
        """Browse for image file"""
        from tkinter import filedialog
        
        file_path = filedialog.askopenfilename(
            title="Select Image for SeedEdit",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.gif *.bmp *.webp"),
                ("PNG files", "*.png"),
                ("JPEG files", "*.jpg *.jpeg"),
                ("All files", "*.*")
            ]
        )
        if file_path:
            self.on_image_selected(file_path)
    
    def setup_seededit_settings(self):
        """Setup SeedEdit specific settings"""
        # Guidance Scale setting
        guidance_frame = ttk.Frame(self.optimized_layout.settings_container)
        guidance_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        guidance_frame.columnconfigure(1, weight=1)
        
        ttk.Label(guidance_frame, text="Guidance Scale:", font=('Arial', 9)).grid(row=0, column=0, sticky=tk.W)
        self.guidance_scale_var = tk.StringVar(value="0.5")
        guidance_combo = ttk.Combobox(guidance_frame, textvariable=self.guidance_scale_var, 
                                     values=["0.1", "0.2", "0.3", "0.4", "0.5", "0.6", "0.7", "0.8", "0.9", "1.0"], 
                                     state="readonly", width=8)
        guidance_combo.grid(row=0, column=1, sticky=tk.E, padx=(5, 0))
        
        # Seed setting
        seed_frame = ttk.Frame(self.optimized_layout.settings_container)
        seed_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        seed_frame.columnconfigure(1, weight=1)
        
        ttk.Label(seed_frame, text="Seed:", font=('Arial', 9)).grid(row=0, column=0, sticky=tk.W)
        self.seed_var = tk.StringVar(value="-1")
        seed_entry = ttk.Entry(seed_frame, textvariable=self.seed_var, width=10)
        seed_entry.grid(row=0, column=1, sticky=tk.E, padx=(5, 0))
    
    def setup_compact_prompt_section(self):
        """Setup compact prompt section"""
        # Add prompt section in the spacer area
        prompt_frame = ttk.LabelFrame(self.optimized_layout.settings_frame.master, text="🌱 SeedEdit Prompt", padding="8")
        prompt_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        prompt_frame.columnconfigure(0, weight=1)
        prompt_frame.rowconfigure(1, weight=1)  # Make prompt text area expandable
        
        # Prompt input
        ttk.Label(prompt_frame, text="Edit instruction:", font=('Arial', 9, 'bold')).grid(row=0, column=0, sticky=tk.W)
        self.prompt_text = tk.Text(prompt_frame, height=4, wrap=tk.WORD, font=('Arial', 10))
        self.prompt_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(2, 5))
        
        # Prompt scrollbar
        prompt_scroll = ttk.Scrollbar(prompt_frame, orient="vertical", command=self.prompt_text.yview)
        prompt_scroll.grid(row=1, column=1, sticky=(tk.N, tk.S), padx=(2, 0))
        self.prompt_text.configure(yscrollcommand=prompt_scroll.set)
        
        # Prompt actions
        prompt_actions = ttk.Frame(prompt_frame)
        prompt_actions.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 0))
        prompt_actions.columnconfigure(0, weight=1)
        prompt_actions.columnconfigure(1, weight=1)
        
        ttk.Button(prompt_actions, text="💾 Save", command=self.save_current_seededit_prompt).grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 2))
        ttk.Button(prompt_actions, text="📋 Load", command=self.show_saved_seededit_prompts).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(2, 0))
        
        # Info label
        info_label = ttk.Label(prompt_frame, 
                              text="💡 SeedEdit: Precise image modifications", 
                              font=('Arial', 8), foreground="gray")
        info_label.grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=(2, 0))
    
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
        self.status_label = ttk.Label(progress_frame, text="Ready for SeedEdit", font=('Arial', 9))
        self.status_label.grid(row=1, column=0, sticky=tk.W)
    
    def clear_prompts(self):
        """Clear the prompt text"""
        self.prompt_text.delete("1.0", tk.END)
    
    def show_saved_seededit_prompts(self):
        """Show saved SeedEdit prompts in a dialog"""
        if not self.saved_seededit_prompts:
            show_info("No Saved Prompts", "No saved SeedEdit prompts available.")
            return
        
        # Create a simple selection dialog
        from tkinter import simpledialog
        
        # Create list of prompts with indices
        prompt_list = []
        for i, prompt in enumerate(self.saved_seededit_prompts):
            preview = prompt[:50] + "..." if len(prompt) > 50 else prompt
            prompt_list.append(f"{i+1}. {preview}")
        
        selection = simpledialog.askstring(
            "Select SeedEdit Prompt",
            "Enter the number of the prompt to load:\n\n" + "\n".join(prompt_list)
        )
        
        if selection:
            try:
                index = int(selection) - 1
                if 0 <= index < len(self.saved_seededit_prompts):
                    self.prompt_text.delete("1.0", tk.END)
                    self.prompt_text.insert("1.0", self.saved_seededit_prompts[index])
                else:
                    show_error("Invalid Selection", "Please enter a valid prompt number.")
            except ValueError:
                show_error("Invalid Input", "Please enter a valid number.")
    
    def setup_prompt_section(self):
        """Setup prompt section with full prompt management"""
        prompt_section = ttk.LabelFrame(self.frame, text="SeedEdit Prompt", padding="10")
        prompt_section.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 10))
        prompt_section.columnconfigure(0, weight=1)
        
        # Current prompt input
        current_prompt_frame = ttk.Frame(prompt_section)
        current_prompt_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        current_prompt_frame.columnconfigure(0, weight=1)
        
        ttk.Label(current_prompt_frame, text="Edit Instruction:", font=('Arial', 10, 'bold')).grid(
            row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        self.prompt_text = tk.Text(current_prompt_frame, height=3, wrap=tk.WORD, font=('Arial', 11))
        self.prompt_text.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        prompt_scroll = ttk.Scrollbar(current_prompt_frame, orient="vertical", command=self.prompt_text.yview)
        prompt_scroll.grid(row=1, column=1, sticky=(tk.N, tk.S))
        self.prompt_text.configure(yscrollcommand=prompt_scroll.set)
        
        # Prompt actions
        prompt_actions = ttk.Frame(current_prompt_frame)
        prompt_actions.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        
        ttk.Button(prompt_actions, text="Save Prompt", 
                  command=self.save_current_seededit_prompt).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(prompt_actions, text="Clear", 
                  command=lambda: self.prompt_text.delete("1.0", tk.END)).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(prompt_actions, text="Sample Prompt", 
                  command=self.load_sample_prompt).pack(side=tk.LEFT)
        
        # Saved prompts section
        saved_prompts_frame = ttk.Frame(prompt_section)
        saved_prompts_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        saved_prompts_frame.columnconfigure(0, weight=1)
        
        ttk.Label(saved_prompts_frame, text="Saved SeedEdit Prompts:", font=('Arial', 10, 'bold')).grid(
            row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        # Saved prompts listbox with scrollbar
        prompts_list_frame = ttk.Frame(saved_prompts_frame)
        prompts_list_frame.grid(row=1, column=0, sticky=(tk.W, tk.E))
        prompts_list_frame.columnconfigure(0, weight=1)
        
        self.seededit_prompts_listbox = tk.Listbox(prompts_list_frame, height=4, font=('Arial', 10))
        self.seededit_prompts_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        prompts_list_scroll = ttk.Scrollbar(prompts_list_frame, orient="vertical", 
                                          command=self.seededit_prompts_listbox.yview)
        prompts_list_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.seededit_prompts_listbox.configure(yscrollcommand=prompts_list_scroll.set)
        
        # Saved prompts actions
        saved_actions = ttk.Frame(saved_prompts_frame)
        saved_actions.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        
        ttk.Button(saved_actions, text="Use Selected", 
                  command=self.use_selected_seededit_prompt).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(saved_actions, text="Delete Selected", 
                  command=self.delete_selected_seededit_prompt).pack(side=tk.LEFT)
        
        # Load saved prompts into listbox
        self.refresh_seededit_prompts_list()
        
        # Info label
        info_label = ttk.Label(prompt_section, 
                              text="💡 SeedEdit is optimized for precise image modifications. Describe specific changes you want to make.",
                              font=('Arial', 9), foreground='#666666')
        info_label.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
    
    def setup_settings_panel(self):
        """Setup settings panel"""
        self.settings_panel = SettingsPanel(self.frame, 4, "SeedEdit Settings")
        
        # Guidance Scale
        self.guidance_scale_var = tk.StringVar(value="0.5")
        self.settings_panel.add_combobox(
            "Guidance Scale", self.guidance_scale_var, 
            ["0.1", "0.2", "0.3", "0.4", "0.5", "0.6", "0.7", "0.8", "0.9", "1.0"]
        )
        
        # Seed
        self.seed_var = tk.StringVar(value="-1")
        self.settings_panel.add_text_field("Seed (-1 for random)", self.seed_var, 15)
    
    def load_sample_prompt(self):
        """Load a sample prompt for demonstration"""
        sample_prompts = [
            "Change the background to a beach scene",
            "Make the person smile",
            "Add sunglasses",
            "Change hair color to blonde",
            "Add a hat",
            "Make it nighttime",
            "Add flowers in the background"
        ]
        
        import random
        sample = random.choice(sample_prompts)
        self.prompt_text.delete("1.0", tk.END)
        self.prompt_text.insert("1.0", sample)
    
    def on_image_selected(self, image_path):
        """Handle image selection"""
        # Check if replacing existing image
        replacing_image = hasattr(self, 'selected_image_path') and self.selected_image_path is not None
        
        # Update the optimized layout with the new image
        success = self.optimized_layout.update_input_image(image_path)
        
        if success:
            self.selected_image_path = image_path
            
            # Reset result buttons and clear previous results
            self.optimized_layout.save_result_button.config(state="disabled")
            self.optimized_layout.use_result_button.config(state="disabled")
            
            # Provide feedback about image replacement
            if replacing_image:
                self.update_status(f"Image replaced: {os.path.basename(image_path)} - Ready for SeedEdit")
            else:
                self.update_status(f"Image selected: {os.path.basename(image_path)} - Ready for SeedEdit")
    
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
        
        # Process the dropped file
        self.on_image_selected(file_path)
    
    def process_task(self):
        """Process SeedEdit task"""
        if not self.validate_inputs():
            return
        
        prompt = self.prompt_text.get("1.0", tk.END).strip()
        if not prompt:
            show_error("Error", "Please enter an edit instruction.")
            return
        
        self.show_progress("Starting SeedEdit processing...")
        
        # Start processing in background thread
        thread = threading.Thread(target=self.process_thread, args=(prompt,))
        thread.daemon = True
        thread.start()
    
    def process_thread(self, prompt):
        """Process in background thread"""
        try:
            # Update status
            self.frame.after(0, lambda: self.update_status("Preparing image..."))
            
            # For SeedEdit, we need a public URL
            # This is a placeholder - in production, you'd upload the image
            image_url = self.upload_image_for_seededit(self.selected_image_path)
            if not image_url:
                self.frame.after(0, lambda: self.handle_error("Failed to prepare image for SeedEdit"))
                return
            
            # Get parameters
            try:
                guidance_scale = float(self.guidance_scale_var.get())
                if not (Config.GUIDANCE_SCALE_RANGE[0] <= guidance_scale <= Config.GUIDANCE_SCALE_RANGE[1]):
                    raise ValueError("Guidance scale out of range")
            except ValueError:
                self.frame.after(0, lambda: self.handle_error("Invalid guidance scale. Must be between 0.0 and 1.0"))
                return
            
            try:
                seed = int(self.seed_var.get()) if self.seed_var.get().strip() != "-1" else -1
                if seed != -1 and not (Config.SEED_RANGE[0] <= seed <= Config.SEED_RANGE[1]):
                    raise ValueError("Seed out of range")
            except ValueError:
                self.frame.after(0, lambda: self.handle_error("Invalid seed. Use -1 for random or a valid integer"))
                return
            
            # Update status
            self.frame.after(0, lambda: self.update_status("Submitting SeedEdit task..."))
            
            # Submit task
            request_id, error = self.api_client.submit_seededit_task(
                image_url, prompt, guidance_scale, seed
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
                request_id, progress_callback, poll_interval=0.5  # Faster polling for SeedEdit
            )
            
            if error:
                self.frame.after(0, lambda: self.handle_error(error))
            else:
                self.frame.after(0, lambda: self.handle_success(output_url, duration))
                
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            self.frame.after(0, lambda: self.handle_error(error_msg))
    
    def upload_image_for_seededit(self, image_path):
        """Upload image securely for SeedEdit"""
        try:
            # Use privacy-friendly upload
            success, url, privacy_info = privacy_uploader.upload_with_privacy_warning(image_path, 'seededit')
            
            if success:
                # Privacy info logged but no popup
                
                logger.info(f"SeedEdit image uploaded: {privacy_info}")
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
                
                return Config.SAMPLE_URLS['seededit']
                
        except Exception as e:
            logger.error(f"SeedEdit upload error: {e}")
            
            # Fallback to sample URL
            self.frame.after(0, lambda: show_error(
                "Upload Error", 
                f"Failed to upload image: {str(e)}\n\n"
                f"Using sample image for demonstration."
            ))
            
            return Config.SAMPLE_URLS['seededit']
    
    def handle_success(self, output_url, duration):
        """Handle successful completion"""
        # Hide progress
        self.hide_progress()
        
        # Download and display result in optimized layout
        success = self.optimized_layout.update_result_image(output_url)
        
        if success:
            self.result_image = self.optimized_layout.result_image
            
            # Auto-save the result
            prompt = self.prompt_text.get("1.0", tk.END).strip()
            guidance_scale = self.guidance_scale_var.get()
            seed = self.seed_var.get()
            extra_info = f"gs{guidance_scale}_seed{seed}"
            
            success, saved_path, error = auto_save_manager.save_result(
                'seededit', 
                output_url, 
                prompt=prompt,
                extra_info=extra_info
            )
            
            # Update status
            self.update_status(f"✅ SeedEdit completed in {format_duration(duration)}!")
            
            success_msg = f"SeedEdit completed successfully in {format_duration(duration)}!"
            success_msg += f"\nGuidance Scale: {guidance_scale} | Seed: {seed}"
            if saved_path:
                success_msg += f"\n\nAuto-saved to:\n{saved_path}"
            elif error:
                success_msg += f"\n\nAuto-save failed: {error}"
            
            # Update status instead of showing dialog
            self.update_status("✅ " + success_msg.replace('\n\n', ' '))
        else:
            self.handle_error("Failed to download result image")
    
    def handle_error(self, error_message):
        """Handle error"""
        # Hide progress
        self.hide_progress()
        
        # Update status
        self.update_status(f"❌ Error: {error_message}")
        
        # Show error dialog
        show_error("SeedEdit Error", error_message)
    
    def show_progress(self, message):
        """Show progress"""
        self.progress_bar.start()
        self.update_status(message)
    
    def hide_progress(self):
        """Hide progress"""
        self.progress_bar.stop()
    
    def update_status(self, message):
        """Update status label"""
        self.status_label.config(text=message)
    
    def validate_inputs(self):
        """Validate inputs before processing"""
        if not hasattr(self, 'selected_image_path') or not self.selected_image_path:
            show_error("Error", "Please select an image first.")
            return False
        
        prompt = self.prompt_text.get("1.0", tk.END).strip()
        if not prompt:
            show_error("Error", "Please enter an edit instruction.")
            return False
        
        # Validate guidance scale
        try:
            guidance_scale = float(self.guidance_scale_var.get())
            if not (0.0 <= guidance_scale <= 1.0):
                show_error("Error", "Guidance scale must be between 0.0 and 1.0")
                return False
        except ValueError:
            show_error("Error", "Invalid guidance scale value.")
            return False
        
        # Validate seed
        try:
            seed_str = self.seed_var.get().strip()
            if seed_str != "-1":
                seed = int(seed_str)
                if seed < 0:
                    show_error("Error", "Seed must be -1 or a positive integer.")
                    return False
        except ValueError:
            show_error("Error", "Invalid seed value. Use -1 for random or a valid integer.")
            return False
        
        return True
    
    def save_result_image(self):
        """Save result image"""
        if not self.result_image:
            show_error("Error", "No result image to save.")
            return
        
        file_path, error = save_image_dialog(self.result_image, "Save SeedEdit Result")
        if file_path:
            # File saved successfully - no dialog needed
            pass
        elif error and "cancelled" not in error.lower():
            show_error("Error", error)
    
    def use_result_as_editor_input(self):
        """Use result as input for editor tab"""
        if not self.result_image:
            show_error("Error", "No result image available.")
            return
        
        if not self.main_app:
            show_error("Error", "Cannot access editor tab.")
            return
        
        try:
            # Create temporary file
            temp_path, error = create_temp_file(self.result_image, "temp_seededit_image")
            if error:
                show_error("Error", error)
                return
            
            # Switch to editor tab and set image
            self.main_app.switch_to_editor_with_image(temp_path)
            # Image set successfully - no dialog needed
            
        except Exception as e:
            show_error("Error", f"Failed to use SeedEdit result as editor input: {str(e)}")
    
    def validate_inputs(self):
        """Validate inputs before processing"""
        if not super().validate_inputs():
            return False
        
        # Validate guidance scale
        try:
            guidance_scale = float(self.guidance_scale_var.get())
            if not (Config.GUIDANCE_SCALE_RANGE[0] <= guidance_scale <= Config.GUIDANCE_SCALE_RANGE[1]):
                show_error("Error", f"Guidance scale must be between {Config.GUIDANCE_SCALE_RANGE[0]} and {Config.GUIDANCE_SCALE_RANGE[1]}")
                return False
        except ValueError:
            show_error("Error", "Invalid guidance scale value.")
            return False
        
        # Validate seed
        try:
            seed_str = self.seed_var.get().strip()
            if seed_str != "-1":
                seed = int(seed_str)
                if not (Config.SEED_RANGE[0] <= seed <= Config.SEED_RANGE[1]):
                    show_error("Error", f"Seed must be -1 or between {Config.SEED_RANGE[0]} and {Config.SEED_RANGE[1]}")
                    return False
        except ValueError:
            show_error("Error", "Invalid seed value. Use -1 for random or a valid integer.")
            return False
        
        return True
    
    # ===== PROMPT MANAGEMENT METHODS =====
    
    def save_current_seededit_prompt(self):
        """Save the current SeedEdit prompt"""
        current_prompt = self.prompt_text.get("1.0", tk.END).strip()
        if not current_prompt:
            show_warning("Warning", "Please enter a prompt first.")
            return
        
        if current_prompt in self.saved_seededit_prompts:
            show_success("Info", "This SeedEdit prompt is already saved.")
            return
        
        self.saved_seededit_prompts.append(current_prompt)
        success, error = save_json_file(self.seededit_prompts_file, self.saved_seededit_prompts)
        
        if success:
            self.refresh_seededit_prompts_list()
            show_success("Success", "SeedEdit prompt saved successfully!")
        else:
            show_error("Error", error)
    
    def use_selected_seededit_prompt(self):
        """Use the selected SeedEdit prompt"""
        selection = self.seededit_prompts_listbox.curselection()
        if not selection:
            show_warning("Warning", "Please select a SeedEdit prompt first.")
            return
        
        selected_prompt = self.saved_seededit_prompts[selection[0]]
        self.prompt_text.delete("1.0", tk.END)
        self.prompt_text.insert("1.0", selected_prompt)
    
    def delete_selected_seededit_prompt(self):
        """Delete the selected SeedEdit prompt"""
        selection = self.seededit_prompts_listbox.curselection()
        if not selection:
            show_warning("Warning", "Please select a SeedEdit prompt to delete.")
            return
        
        selected_prompt = self.saved_seededit_prompts[selection[0]]
        if ask_yes_no("Confirm Delete", 
                     f"Are you sure you want to delete this SeedEdit prompt?\n\n{selected_prompt[:100]}..."):
            del self.saved_seededit_prompts[selection[0]]
            success, error = save_json_file(self.seededit_prompts_file, self.saved_seededit_prompts)
            
            if success:
                self.refresh_seededit_prompts_list()
                show_success("Success", "SeedEdit prompt deleted successfully!")
            else:
                show_error("Error", error)
    
    def refresh_seededit_prompts_list(self):
        """Refresh the SeedEdit prompts listbox"""
        self.seededit_prompts_listbox.delete(0, tk.END)
        for prompt in self.saved_seededit_prompts:
            display_text = prompt[:50] + "..." if len(prompt) > 50 else prompt
            self.seededit_prompts_listbox.insert(tk.END, display_text)
