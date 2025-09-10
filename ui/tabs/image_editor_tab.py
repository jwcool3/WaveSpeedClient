"""
Image Editor Tab Component

This module contains the image editor functionality.
"""

import tkinter as tk
from tkinter import ttk
import threading
from ui.components.ui_components import BaseTab, SettingsPanel
from ui.components.enhanced_image_display import EnhancedImageSelector, EnhancedImagePreview
from ui.components.optimized_image_layout import OptimizedImageLayout
from utils.utils import *
from core.auto_save import auto_save_manager


class ImageEditorTab(BaseTab):
    """Image Editor Tab"""
    
    def __init__(self, parent_frame, api_client, main_app=None):
        self.prompts_file = "data/saved_prompts.json"
        self.saved_prompts = load_json_file(self.prompts_file, [])
        self.result_image = None
        self.main_app = main_app  # Reference to main app for cross-tab operations
        
        super().__init__(parent_frame, api_client)
    
    def setup_ui(self):
        """Setup the optimized image editor UI"""
        # Hide the scrollable canvas components since we're using direct container layout
        self.canvas.pack_forget()
        self.scrollbar.pack_forget()
        
        # For optimized layout, bypass the scrollable canvas and use the main container directly
        # This ensures full window expansion without canvas constraints
        self.optimized_layout = OptimizedImageLayout(self.container, "Nano Banana Editor")
        
        # Setup the layout with image editing specific settings
        self.setup_image_editor_settings()
        
        # Setup prompt section in the left panel
        self.setup_compact_prompt_section()
        
        # Configure main action button
        self.optimized_layout.set_main_action("🍌 Edit with Nano Banana", self.process_task)
        
        # Connect image selector
        self.optimized_layout.set_image_selector_command(self.browse_image)
        
        # Connect result buttons
        self.optimized_layout.set_result_button_commands(
            self.save_result_image, 
            self.use_result_as_input
        )
        
        # Connect sample and clear buttons
        self.optimized_layout.sample_button.config(command=self.load_sample_prompt)
        self.optimized_layout.clear_button.config(command=self.clear_prompts)
        
        # Connect drag and drop handling
        self.optimized_layout.set_parent_tab(self)
        
        # Setup cross-tab sharing
        self.optimized_layout.create_cross_tab_button(self.main_app, "Nano Banana Editor")
        
        # Setup progress section in the left panel
        self.setup_compact_progress_section()
    
    def browse_image(self):
        """Browse for image file"""
        from tkinter import filedialog
        
        file_path = filedialog.askopenfilename(
            title="Select Image for Nano Banana Editor",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.gif *.bmp *.webp"),
                ("PNG files", "*.png"),
                ("JPEG files", "*.jpg *.jpeg"),
                ("All files", "*.*")
            ]
        )
        if file_path:
            self.on_image_selected(file_path)
    
    def setup_image_editor_settings(self):
        """Setup image editor specific settings"""
        # Output format setting
        format_frame = ttk.Frame(self.optimized_layout.settings_container)
        format_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        format_frame.columnconfigure(1, weight=1)
        
        ttk.Label(format_frame, text="Output Format:", font=('Arial', 9)).grid(row=0, column=0, sticky=tk.W)
        self.format_var = tk.StringVar(value="png")
        format_combo = ttk.Combobox(format_frame, textvariable=self.format_var, 
                                   values=["png", "jpg", "webp"], state="readonly", width=8)
        format_combo.grid(row=0, column=1, sticky=tk.E, padx=(5, 0))
    
    def setup_compact_prompt_section(self):
        """Setup compact prompt section"""
        # Add prompt section in the spacer area
        prompt_frame = ttk.LabelFrame(self.optimized_layout.settings_frame.master, text="🍌 Nano Banana Prompt", padding="8")
        prompt_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        prompt_frame.columnconfigure(0, weight=1)
        prompt_frame.rowconfigure(1, weight=1)  # Make prompt text area expandable
        
        # Prompt input
        ttk.Label(prompt_frame, text="Describe the edit:", font=('Arial', 9, 'bold')).grid(row=0, column=0, sticky=tk.W)
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
        
        ttk.Button(prompt_actions, text="💾 Save", command=self.save_current_prompt).grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 2))
        ttk.Button(prompt_actions, text="📋 Load", command=self.show_saved_prompts).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(2, 0))
    
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
        self.status_label = ttk.Label(progress_frame, text="Ready for Nano Banana editing", font=('Arial', 9))
        self.status_label.grid(row=1, column=0, sticky=tk.W)
    
    def load_sample_prompt(self):
        """Load a sample prompt"""
        sample_prompts = [
            "Make the sky more dramatic with storm clouds",
            "Change the lighting to golden hour",
            "Add a vintage film effect",
            "Remove the background and make it transparent",
            "Enhance the colors and contrast",
            "Add snow falling in the scene",
            "Make it look like a painting"
        ]
        
        import random
        sample = random.choice(sample_prompts)
        self.prompt_text.delete("1.0", tk.END)
        self.prompt_text.insert("1.0", sample)
    
    def clear_prompts(self):
        """Clear the prompt text"""
        self.prompt_text.delete("1.0", tk.END)
    
    def show_saved_prompts(self):
        """Show saved prompts in a dialog"""
        if not self.saved_prompts:
            show_info("No Saved Prompts", "No saved prompts available.")
            return
        
        # Create a simple selection dialog
        from tkinter import simpledialog
        
        # Create list of prompts with indices
        prompt_list = []
        for i, prompt in enumerate(self.saved_prompts):
            preview = prompt[:50] + "..." if len(prompt) > 50 else prompt
            prompt_list.append(f"{i+1}. {preview}")
        
        selection = simpledialog.askstring(
            "Select Saved Prompt",
            "Enter the number of the prompt to load:\n\n" + "\n".join(prompt_list)
        )
        
        if selection:
            try:
                index = int(selection) - 1
                if 0 <= index < len(self.saved_prompts):
                    self.prompt_text.delete("1.0", tk.END)
                    self.prompt_text.insert("1.0", self.saved_prompts[index])
                else:
                    show_error("Invalid Selection", "Please enter a valid prompt number.")
            except ValueError:
                show_error("Invalid Input", "Please enter a valid number.")
    
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
    
    def on_image_selected(self, image_path, replacing_image=False):
        """Handle image selection"""
        # Check if replacing existing image (use parameter or detect automatically)
        if not replacing_image:
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
        
        # Process the dropped file
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
        # Hide progress
        self.hide_progress()
        
        # Download and display result in optimized layout
        success = self.optimized_layout.update_result_image(output_url)
        
        if success:
            self.result_image = self.optimized_layout.result_image
            
            # Auto-save the result
            prompt = self.prompt_text.get("1.0", tk.END).strip()
            success, saved_path, error = auto_save_manager.save_result(
                'image_editor', 
                output_url, 
                prompt=prompt,
                extra_info="edited"
            )
            
            # Update status
            self.update_status(f"✅ Image edited successfully in {format_duration(duration)}!")
            
            success_msg = f"Image edited successfully in {format_duration(duration)}!"
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
        show_error("Nano Banana Editor Error", error_message)
    
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
            show_error("Error", "Please enter a prompt describing the edit.")
            return False
        
        return True
    
    def save_result_image(self):
        """Save result image"""
        if not self.result_image:
            show_error("Error", "No result image to save.")
            return
        
        file_path, error = save_image_dialog(self.result_image, "Save Edited Image")
        if file_path:
            # File saved successfully - no dialog needed
            pass
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
        
        # Use the result as new input
        self.on_image_selected(temp_path)
        # Image set successfully - no dialog needed
    
    def save_current_prompt(self):
        """Save current prompt"""
        current_prompt = self.prompt_text.get("1.0", tk.END).strip()
        if not current_prompt:
            show_warning("Warning", "Please enter a prompt first.")
            return
        
        if current_prompt in self.saved_prompts:
            # Prompt already saved (no popup needed)
            return
        
        self.saved_prompts.append(current_prompt)
        success, error = save_json_file(self.prompts_file, self.saved_prompts)
        
        if success:
            self.refresh_prompts_list()
            # Prompt saved successfully (no popup needed)
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
                # Prompt deleted successfully (no popup needed)
            else:
                show_error("Error", error)
    
    def refresh_prompts_list(self):
        """Refresh prompts listbox"""
        self.prompts_listbox.delete(0, tk.END)
        for prompt in self.saved_prompts:
            display_text = prompt[:50] + "..." if len(prompt) > 50 else prompt
            self.prompts_listbox.insert(tk.END, display_text)
