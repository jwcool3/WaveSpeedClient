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
        """Setup the SeedEdit UI"""
        self.frame.columnconfigure(1, weight=1)
        
        # Enhanced image selector (smaller preview)
        self.image_selector = EnhancedImageSelector(
            self.frame, 0, self.on_image_selected, "Select Image to Edit with SeedEdit:", show_preview=True
        )
        
        # Enhanced image preview (larger result display)
        self.image_preview = EnhancedImagePreview(self.frame, 2, "SeedEdit", result_size=(600, 450))
        self.image_preview.result_frame.config(text="SeedEdit Result")
        
        # Setup drag and drop
        self.image_preview.setup_drag_and_drop(self.on_drop)
        
        # Result buttons
        button_frame = ttk.Frame(self.image_preview.result_frame)
        button_frame.pack(pady=(10, 0))
        
        self.save_button = ttk.Button(button_frame, text="Save Result Image", 
                                     command=self.save_result_image, state="disabled")
        self.save_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.use_result_button = ttk.Button(button_frame, text="Use as Editor Input", 
                                           command=self.use_result_as_editor_input, state="disabled")
        self.use_result_button.pack(side=tk.LEFT)
        
        # Prompt section
        self.setup_prompt_section()
        
        # Settings panel
        self.setup_settings_panel()
        
        # Progress and results (moved up since button is now sticky)
        self.setup_progress_section(5)
        self.setup_results_section(6)
        
        # Setup sticky buttons at the bottom
        buttons_config = [
            ("Apply SeedEdit", self.process_task, "primary"),
        ]
        self.setup_sticky_buttons(buttons_config)
    
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
        
        self.selected_image_path = image_path
        self.original_image = self.image_preview.update_original_image(image_path)
        
        # Reset result buttons and clear previous results
        self.save_button.config(state="disabled")
        self.use_result_button.config(state="disabled")
        
        # Provide feedback about image replacement
        if replacing_image:
            self.update_status(f"Image replaced: {os.path.basename(image_path)}")
        else:
            self.update_status(f"Image selected: {os.path.basename(image_path)}")
    
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
                # Show privacy information to user
                self.frame.after(0, lambda: show_success(
                    "Image Upload", 
                    f"Image uploaded for SeedEdit processing.\n\n"
                    f"Privacy Status: {privacy_info}\n\n"
                    f"Your image: {os.path.basename(image_path)}\n"
                    f"Processing will begin shortly..."
                ))
                
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
        # Download and display result
        self.result_image = self.image_preview.update_result_image(output_url)
        
        if self.result_image:
            # Enable buttons
            self.save_button.config(state="normal")
            self.use_result_button.config(state="normal")
            
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
            
            # Show results
            message = f"SeedEdit processing completed successfully!\n"
            message += f"Processing time: {format_duration(duration)}\n"
            message += f"Guidance scale: {guidance_scale}\n"
            message += f"Seed: {seed}\n"
            message += f"Result URL: {output_url}\n"
            
            if success and saved_path:
                message += f"Auto-saved to: {saved_path}\n"
            elif error:
                message += f"Auto-save failed: {error}\n"
            
            message += "\nThe edited image is displayed above."
            
            self.show_results(message, True)
            
            success_msg = f"SeedEdit completed successfully in {format_duration(duration)}!"
            if saved_path:
                success_msg += f"\n\nAuto-saved to:\n{saved_path}"
            
            show_success("Success", success_msg)
        else:
            self.handle_error("Failed to download result image")
    
    def handle_error(self, error_message):
        """Handle error"""
        self.show_results(f"Error: {error_message}", False)
        show_error("Error", error_message)
    
    def save_result_image(self):
        """Save result image"""
        if not self.result_image:
            show_error("Error", "No result image to save.")
            return
        
        file_path, error = save_image_dialog(self.result_image, "Save SeedEdit Result")
        if file_path:
            show_success("Success", f"SeedEdit result saved to:\n{file_path}")
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
            show_success("Success", "SeedEdit result is now set as the editor input image!")
            
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
