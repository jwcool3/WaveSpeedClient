"""
Integration Example: Using Improved SeedEdit Layout in Actual Tab
Shows how to replace existing SeedEdit layout with the improved version
"""

import tkinter as tk
from tkinter import ttk
from ui.components.improved_seededit_layout import ImprovedSeedEditLayout
from ui.components.enhanced_seededit_layout import EnhancedSeedEditLayout
from ui.components.ui_components import BaseTab
from core.logger import get_logger

logger = get_logger()


class SeedEditTabWithImprovedLayout(BaseTab):
    """SeedEdit tab using the improved layout - Basic Version"""
    
    def __init__(self, parent_frame, api_client, main_app=None):
        super().__init__(parent_frame, api_client, main_app)
        
        # Replace the existing layout with improved layout
        self.layout = ImprovedSeedEditLayout(self.frame)
        
        # Override the process_seededit method to use our API
        self.layout.process_seededit = self.process_with_api
    
    def process_with_api(self):
        """Process with actual API call"""
        if not self.layout.selected_image_path:
            self.layout.status_label.config(text="Please select an image first", foreground="red")
            return
        
        prompt = self.layout.prompt_text.get("1.0", tk.END).strip()
        if not prompt or prompt == "Describe the changes you want to make to the image...":
            self.layout.status_label.config(text="Please enter edit instructions", foreground="red")
            return
        
        # Show processing state
        self.layout.status_label.config(text="Processing with SeedEdit...", foreground="blue")
        self.layout.progress_bar.grid(row=2, column=0, sticky="ew", pady=(4, 0))
        self.layout.progress_bar.start()
        self.layout.primary_btn.config(state='disabled', text="Processing...")
        
        # Get parameters
        guidance_scale = float(self.layout.guidance_var.get())
        seed = self.layout.seed_var.get()
        steps = 20  # Default steps
        
        # Submit to API
        try:
            result = self.api_client.submit_seededit_task(
                image_path=self.layout.selected_image_path,
                prompt=prompt,
                guidance_scale=guidance_scale,
                seed=seed,
                num_inference_steps=steps
            )
            
            if result:
                # Handle success
                self.layout.after_processing()
                self.layout.result_image_path = result.get('result_path')  # Set result path
                self.layout.view_result_btn.config(state='normal')
                self.layout.comparison_btn.config(state='normal')
            else:
                # Handle error
                self.layout.status_label.config(text="API request failed", foreground="red")
                self.layout.progress_bar.stop()
                self.layout.progress_bar.grid_remove()
                self.layout.primary_btn.config(state='normal', text="✨ Apply SeedEdit")
                
        except Exception as e:
            logger.error(f"Error processing SeedEdit: {e}")
            self.layout.status_label.config(text=f"Error: {str(e)}", foreground="red")
            self.layout.progress_bar.stop()
            self.layout.progress_bar.grid_remove()
            self.layout.primary_btn.config(state='normal', text="✨ Apply SeedEdit")


class SeedEditTabWithEnhancedLayout(BaseTab):
    """SeedEdit tab using the enhanced layout - Full Integration Version"""
    
    def __init__(self, parent_frame, api_client, main_app=None):
        super().__init__(parent_frame, api_client, main_app)
        
        # Create enhanced layout with full integration
        self.layout = EnhancedSeedEditLayout(
            parent_frame=self.frame,
            tab_instance=self,
            api_client=api_client,
            main_app=main_app
        )
        
        # Set up callbacks
        self.layout.on_image_selected = self.on_image_selected
        self.layout.on_process_requested = self.submit_seededit_task
        self.layout.on_status_update = self.on_status_update
    
    def on_image_selected(self, image_path):
        """Handle image selection"""
        self.selected_image_path = image_path
        logger.info(f"Image selected: {image_path}")
    
    def submit_seededit_task(self):
        """Submit SeedEdit task to API"""
        try:
            # Get parameters from layout
            prompt = self.layout.prompt_text.get("1.0", tk.END).strip()
            guidance_scale = self.layout.guidance_scale_var.get()
            steps = self.layout.steps_var.get()
            seed = self.layout.seed_var.get()
            
            # Submit to API
            result = self.api_client.submit_seededit_task(
                image_path=self.selected_image_path,
                prompt=prompt,
                guidance_scale=guidance_scale,
                num_inference_steps=steps,
                seed=seed
            )
            
            if result:
                # Handle success
                result_url = result.get('result_url')
                self.layout.after_processing(
                    success=True,
                    result_url=result_url
                )
                
                # Set result image path for comparison
                if result_url:
                    self.layout.result_image_path = result_url
            else:
                # Handle error
                self.layout.after_processing(
                    success=False,
                    error_message="API request failed"
                )
                
        except Exception as e:
            logger.error(f"Error submitting SeedEdit task: {e}")
            self.layout.after_processing(
                success=False,
                error_message=str(e)
            )
    
    def on_status_update(self, message, status_type):
        """Handle status updates"""
        logger.info(f"Status update: {message} ({status_type})")
        # You can add additional status handling logic here


class SeedEditTabMigration:
    """Helper class for migrating existing SeedEdit tabs to improved layout"""
    
    @staticmethod
    def migrate_existing_tab(existing_tab):
        """Migrate an existing SeedEdit tab to use improved layout"""
        
        # Store existing state
        existing_state = {
            'selected_image_path': getattr(existing_tab, 'selected_image_path', None),
            'prompt_text': getattr(existing_tab, 'prompt_text', None),
            'guidance_scale': getattr(existing_tab, 'guidance_scale_var', None),
            'seed': getattr(existing_tab, 'seed_var', None),
            'api_client': existing_tab.api_client,
            'main_app': existing_tab.main_app
        }
        
        # Clear existing layout
        for widget in existing_tab.frame.winfo_children():
            widget.destroy()
        
        # Create new improved layout
        existing_tab.layout = EnhancedSeedEditLayout(
            parent_frame=existing_tab.frame,
            tab_instance=existing_tab,
            api_client=existing_tab.api_client,
            main_app=existing_tab.main_app
        )
        
        # Restore state
        if existing_state['selected_image_path']:
            existing_tab.layout.load_image(existing_state['selected_image_path'])
        
        if existing_state['prompt_text']:
            existing_tab.layout.prompt_text.delete("1.0", tk.END)
            existing_tab.layout.prompt_text.insert("1.0", existing_state['prompt_text'])
        
        if existing_state['guidance_scale']:
            existing_tab.layout.guidance_scale_var.set(existing_state['guidance_scale'].get())
        
        if existing_state['seed']:
            existing_tab.layout.seed_var.set(existing_state['seed'].get())
        
        # Set up callbacks
        existing_tab.layout.on_image_selected = existing_tab.on_image_selected if hasattr(existing_tab, 'on_image_selected') else None
        existing_tab.layout.on_process_requested = existing_tab.submit_seededit_task if hasattr(existing_tab, 'submit_seededit_task') else None
        existing_tab.layout.on_status_update = existing_tab.on_status_update if hasattr(existing_tab, 'on_status_update') else None
        
        logger.info("Successfully migrated SeedEdit tab to improved layout")
        return existing_tab


"""
Migration Guide:

1. BASIC MIGRATION (Minimal Changes):
   - Replace existing layout creation with ImprovedSeedEditLayout
   - Override the process_seededit method
   - Keep existing API integration

2. ENHANCED MIGRATION (Full Integration):
   - Use EnhancedSeedEditLayout with full callbacks
   - Implement proper callback methods
   - Get full auto-save and prompt tracking features

3. EXISTING TAB MIGRATION:
   - Use SeedEditTabMigration.migrate_existing_tab()
   - Preserves existing state
   - Minimal code changes required

Benefits of Migration:
✅ Eliminates vertical scrolling
✅ Much larger image display area
✅ Primary action button right under prompt
✅ Side-by-side comparison instead of tabs
✅ Horizontal settings layout saves space
✅ No wasted space between columns
✅ Better user experience
✅ Maintains all existing functionality
✅ Adds new features (auto-save, prompt tracking, AI integration)

Example Usage:

# Basic migration
class MySeedEditTab(BaseTab):
    def __init__(self, parent_frame, api_client, main_app=None):
        super().__init__(parent_frame, api_client, main_app)
        self.layout = ImprovedSeedEditLayout(self.frame)
        self.layout.process_seededit = self.my_process_method

# Enhanced migration
class MyEnhancedSeedEditTab(BaseTab):
    def __init__(self, parent_frame, api_client, main_app=None):
        super().__init__(parent_frame, api_client, main_app)
        self.layout = EnhancedSeedEditLayout(
            parent_frame=self.frame,
            tab_instance=self,
            api_client=api_client,
            main_app=main_app
        )
        self.layout.on_process_requested = self.submit_task

# Migrate existing tab
migrated_tab = SeedEditTabMigration.migrate_existing_tab(existing_seededit_tab)
"""
