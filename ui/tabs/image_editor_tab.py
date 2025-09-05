"""
Image Editor Tab Component

This module contains the image editor functionality.
"""

import tkinter as tk
from tkinter import ttk
import threading
from ui.components.ui_components import BaseTab, SettingsPanel
from ui.components.enhanced_image_display import EnhancedImageSelector, EnhancedImagePreview
from utils.utils import *
from core.auto_save import auto_save_manager


class ImageEditorTab(BaseTab):
    """Image Editor Tab"""
    
    def __init__(self, parent_frame, api_client):
        self.prompts_file = "data/saved_prompts.json"
        self.saved_prompts = load_json_file(self.prompts_file, [])
        self.result_image = None
        
        super().__init__(parent_frame, api_client)
    
    def setup_ui(self):
        """Setup the image editor UI"""
        self.frame.columnconfigure(1, weight=1)
        
        # Enhanced image selector (smaller preview)
        self.image_selector = EnhancedImageSelector(
            self.frame, 0, self.on_image_selected, "Select Image to Edit:", show_preview=True
        )
        
        # Enhanced image preview (larger result display)
        self.image_preview = EnhancedImagePreview(self.frame, 2, "Image Editor", result_size=(600, 450))
        self.image_preview.result_frame.config(text="Edited Result")
        
        # Setup drag and drop
        self.image_preview.setup_drag_and_drop(self.on_drop)
        
        # Result buttons
        button_frame = ttk.Frame(self.image_preview.result_frame)
        button_frame.pack(pady=(10, 0))
        
        self.save_button = ttk.Button(button_frame, text="Save Result Image", 
                                     command=self.save_result_image, state="disabled")
        self.save_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.use_result_button = ttk.Button(button_frame, text="Use as Next Input", 
                                           command=self.use_result_as_input, state="disabled")
        self.use_result_button.pack(side=tk.LEFT)
        
        # Prompt section
        self.setup_prompt_section()
        
        # Settings panel
        self.setup_settings_panel()
        
        # Progress and results (moved up since button is now sticky)
        self.setup_progress_section(6)
        self.setup_results_section(7)
        
        # Setup sticky buttons at the bottom
        buttons_config = [
            ("Edit Image", self.process_task, "primary"),
        ]
        self.setup_sticky_buttons(buttons_config)
    
    def setup_prompt_section(self):
        """Setup prompt management section"""
        prompt_section = ttk.LabelFrame(self.frame, text="Edit Prompt", padding="10")
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
        
        ttk.Button(prompt_actions, text="Save Prompt", 
                  command=self.save_current_prompt).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(prompt_actions, text="Clear", 
                  command=lambda: self.prompt_text.delete("1.0", tk.END)).pack(side=tk.LEFT)
        
        # Saved prompts section
        saved_prompts_frame = ttk.Frame(prompt_section)
        saved_prompts_frame.grid(row=1, column=0, sticky=(tk.W, tk.E))
        saved_prompts_frame.columnconfigure(0, weight=1)
        
        ttk.Label(saved_prompts_frame, text="Saved Prompts:", font=('Arial', 10, 'bold')).grid(
            row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        # Saved prompts listbox
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
        
        ttk.Button(saved_actions, text="Use Selected", 
                  command=self.use_selected_prompt).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(saved_actions, text="Delete Selected", 
                  command=self.delete_selected_prompt).pack(side=tk.LEFT)
        
        # Load saved prompts
        self.refresh_prompts_list()
    
    def setup_settings_panel(self):
        """Setup settings panel"""
        self.settings_panel = SettingsPanel(self.frame, 4, "Output Settings")
        
        self.format_var = tk.StringVar(value="png")
        self.settings_panel.add_combobox(
            "Output Format", self.format_var, ["png", "jpg", "webp"]
        )
    
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
            self.update_status(f"Image replaced: {os.path.basename(image_path)} - Ready to edit")
        else:
            self.update_status(f"Image selected: {os.path.basename(image_path)} - Ready to edit")
    
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
        """Process image editing task"""
        if not self.validate_inputs():
            return
        
        prompt = self.prompt_text.get("1.0", tk.END).strip()
        if not prompt:
            show_error("Error", "Please enter a prompt.")
            return
        
        self.show_progress("Starting image editing...")
        
        # Start processing in background thread
        thread = threading.Thread(target=self.process_thread, args=(prompt,))
        thread.daemon = True
        thread.start()
    
    def process_thread(self, prompt):
        """Process in background thread"""
        try:
            # Update status
            self.frame.after(0, lambda: self.update_status("Submitting task..."))
            
            # Submit task
            request_id, error = self.api_client.submit_image_edit_task(
                self.selected_image_path, prompt, self.format_var.get()
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
                request_id, progress_callback
            )
            
            if error:
                self.frame.after(0, lambda: self.handle_error(error))
            else:
                self.frame.after(0, lambda: self.handle_success(output_url, duration))
                
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            self.frame.after(0, lambda: self.handle_error(error_msg))
    
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
            success, saved_path, error = auto_save_manager.save_result(
                'image_editor', 
                output_url, 
                prompt=prompt,
                extra_info="edited"
            )
            
            # Show results
            message = f"Image edited successfully!\n"
            message += f"Processing time: {format_duration(duration)}\n"
            message += f"Result URL: {output_url}\n"
            
            if success and saved_path:
                message += f"Auto-saved to: {saved_path}\n"
            elif error:
                message += f"Auto-save failed: {error}\n"
            
            message += "\nThe edited image is displayed above."
            
            self.show_results(message, True)
            
            success_msg = f"Image edited successfully in {format_duration(duration)}!"
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
        
        file_path, error = save_image_dialog(self.result_image, "Save Edited Image")
        if file_path:
            show_success("Success", f"Image saved to:\n{file_path}")
        elif error and "cancelled" not in error.lower():
            show_error("Error", error)
    
    def use_result_as_input(self):
        """Use result image as next input"""
        if not self.result_image:
            show_error("Error", "No result image available.")
            return
        
        temp_path, error = create_temp_file(self.result_image, "temp_result_image")
        if error:
            show_error("Error", error)
            return
        
        self.image_selector.selected_path = temp_path
        self.image_selector.image_path_label.config(
            text="Result Image (temp)", foreground="blue"
        )
        self.on_image_selected(temp_path)
        show_success("Success", "Result image is now set as the input image!")
    
    def save_current_prompt(self):
        """Save current prompt"""
        current_prompt = self.prompt_text.get("1.0", tk.END).strip()
        if not current_prompt:
            show_warning("Warning", "Please enter a prompt first.")
            return
        
        if current_prompt in self.saved_prompts:
            show_success("Info", "This prompt is already saved.")
            return
        
        self.saved_prompts.append(current_prompt)
        success, error = save_json_file(self.prompts_file, self.saved_prompts)
        
        if success:
            self.refresh_prompts_list()
            show_success("Success", "Prompt saved successfully!")
        else:
            show_error("Error", error)
    
    def use_selected_prompt(self):
        """Use selected prompt"""
        selection = self.prompts_listbox.curselection()
        if not selection:
            show_warning("Warning", "Please select a prompt first.")
            return
        
        selected_prompt = self.saved_prompts[selection[0]]
        self.prompt_text.delete("1.0", tk.END)
        self.prompt_text.insert("1.0", selected_prompt)
    
    def delete_selected_prompt(self):
        """Delete selected prompt"""
        selection = self.prompts_listbox.curselection()
        if not selection:
            show_warning("Warning", "Please select a prompt to delete.")
            return
        
        selected_prompt = self.saved_prompts[selection[0]]
        if ask_yes_no("Confirm Delete", 
                     f"Are you sure you want to delete this prompt?\n\n{selected_prompt[:100]}..."):
            del self.saved_prompts[selection[0]]
            success, error = save_json_file(self.prompts_file, self.saved_prompts)
            
            if success:
                self.refresh_prompts_list()
                show_success("Success", "Prompt deleted successfully!")
            else:
                show_error("Error", error)
    
    def refresh_prompts_list(self):
        """Refresh prompts listbox"""
        self.prompts_listbox.delete(0, tk.END)
        for prompt in self.saved_prompts:
            display_text = prompt[:50] + "..." if len(prompt) > 50 else prompt
            self.prompts_listbox.insert(tk.END, display_text)
