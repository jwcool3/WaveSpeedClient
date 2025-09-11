"""
Example Integration of Enhanced Compact Layout
Shows how to integrate the new compact layout into existing tabs
"""

import tkinter as tk
from tkinter import ttk
from ui.components.enhanced_compact_layout import EnhancedCompactLayout
from ui.components.ui_components import BaseTab
from core.logger import get_logger

logger = get_logger()


class ExampleCompactTab(BaseTab):
    """Example tab using the enhanced compact layout"""
    
    def __init__(self, parent_frame, api_client, main_app=None):
        super().__init__(parent_frame, api_client, main_app)
        
        # Create the enhanced compact layout
        self.layout = EnhancedCompactLayout(
            parent_frame=self.frame,
            tab_instance=self,
            model_type="seedream_v4",  # or "seededit", "image_editor", etc.
            title="Seedream V4 - Compact Layout"
        )
        
        # Set up callbacks
        self.layout.on_image_selected = self.on_image_selected
        self.layout.on_process_requested = self.on_process_requested
        self.layout.on_status_update = self.on_status_update
        
        # Configure the main action button
        self.layout.main_action_btn.config(
            text="🚀 Generate with Seedream V4",
            command=self.process_seedream_v4
        )
    
    def on_image_selected(self, image_path):
        """Called when an image is selected"""
        logger.info(f"Image selected: {image_path}")
        # You can add any additional logic here
    
    def on_process_requested(self):
        """Called when process button is clicked"""
        logger.info("Process requested")
        # Start your actual processing here
        self.process_seedream_v4()
    
    def on_status_update(self, message, status_type):
        """Called when status is updated"""
        logger.info(f"Status update: {message} ({status_type})")
        # You can add additional status handling here
    
    def process_seedream_v4(self):
        """Process with Seedream V4"""
        try:
            # Get parameters from the layout
            prompt = self.layout.prompt_text.get("1.0", tk.END).strip()
            width = self.layout.width_var.get()
            height = self.layout.height_var.get()
            seed = self.layout.seed_var.get()
            
            # Your actual API call here
            # result = self.api_client.submit_seedream_v4_task(...)
            
            # Simulate processing
            import threading
            import time
            
            def simulate_processing():
                time.sleep(3)  # Simulate processing time
                
                # Simulate success
                self.layout.after_processing(
                    success=True,
                    result_url="https://example.com/result.png"
                )
            
            threading.Thread(target=simulate_processing, daemon=True).start()
            
        except Exception as e:
            logger.error(f"Error processing: {e}")
            self.layout.after_processing(
                success=False,
                error_message=str(e)
            )


# Integration with existing tabs
class SeedreamV4TabCompact(BaseTab):
    """Seedream V4 tab using compact layout"""
    
    def __init__(self, parent_frame, api_client, main_app=None):
        super().__init__(parent_frame, api_client, main_app)
        
        # Replace the existing layout with compact layout
        self.layout = EnhancedCompactLayout(
            parent_frame=self.frame,
            tab_instance=self,
            model_type="seedream_v4",
            title="Seedream V4"
        )
        
        # Set up callbacks
        self.layout.on_image_selected = self.on_image_selected
        self.layout.on_process_requested = self.submit_seedream_v4_task
        self.layout.on_status_update = self.on_status_update
    
    def on_image_selected(self, image_path):
        """Handle image selection"""
        self.selected_image_path = image_path
        # Add any additional image processing logic here
    
    def submit_seedream_v4_task(self):
        """Submit Seedream V4 task"""
        try:
            # Get parameters from compact layout
            prompt = self.layout.prompt_text.get("1.0", tk.END).strip()
            width = self.layout.width_var.get()
            height = self.layout.height_var.get()
            seed = self.layout.seed_var.get()
            sync_mode = self.layout.sync_mode_var.get()
            base64_output = self.layout.base64_output_var.get()
            
            # Submit to API
            result = self.api_client.submit_seedream_v4_task(
                image_path=self.selected_image_path,
                prompt=prompt,
                size=f"{width}*{height}",
                seed=seed,
                sync_mode=sync_mode,
                base64_output=base64_output
            )
            
            if result:
                # Handle success
                self.layout.after_processing(
                    success=True,
                    result_url=result.get('result_url')
                )
            else:
                # Handle error
                self.layout.after_processing(
                    success=False,
                    error_message="API request failed"
                )
                
        except Exception as e:
            logger.error(f"Error submitting task: {e}")
            self.layout.after_processing(
                success=False,
                error_message=str(e)
            )
    
    def on_status_update(self, message, status_type):
        """Handle status updates"""
        # You can add additional status handling logic here
        pass


class SeedEditTabCompact(BaseTab):
    """SeedEdit tab using compact layout"""
    
    def __init__(self, parent_frame, api_client, main_app=None):
        super().__init__(parent_frame, api_client, main_app)
        
        # Create compact layout for SeedEdit
        self.layout = EnhancedCompactLayout(
            parent_frame=self.frame,
            tab_instance=self,
            model_type="seededit",
            title="SeedEdit"
        )
        
        # Set up callbacks
        self.layout.on_image_selected = self.on_image_selected
        self.layout.on_process_requested = self.submit_seededit_task
        self.layout.on_status_update = self.on_status_update
    
    def on_image_selected(self, image_path):
        """Handle image selection"""
        self.selected_image_path = image_path
    
    def submit_seededit_task(self):
        """Submit SeedEdit task"""
        try:
            # Get parameters
            prompt = self.layout.prompt_text.get("1.0", tk.END).strip()
            guidance_scale = self.layout.guidance_scale_var.get()
            steps = self.layout.steps_var.get()
            
            # Submit to API
            result = self.api_client.submit_seededit_task(
                image_path=self.selected_image_path,
                prompt=prompt,
                guidance_scale=guidance_scale,
                num_inference_steps=steps
            )
            
            if result:
                self.layout.after_processing(
                    success=True,
                    result_url=result.get('result_url')
                )
            else:
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
        pass


"""
How to integrate into existing tabs:

1. Replace the existing layout creation with:
   self.layout = EnhancedCompactLayout(
       parent_frame=self.frame,
       tab_instance=self,
       model_type="your_model_type",
       title="Your Tab Title"
   )

2. Set up callbacks:
   self.layout.on_image_selected = self.on_image_selected
   self.layout.on_process_requested = self.your_process_method
   self.layout.on_status_update = self.on_status_update

3. Update your process method to use layout parameters:
   prompt = self.layout.prompt_text.get("1.0", tk.END).strip()
   # Get other parameters based on model type

4. Call after_processing when done:
   self.layout.after_processing(success=True, result_url=url)
   # or
   self.layout.after_processing(success=False, error_message=error)

Benefits:
- ✅ Eliminates vertical scrolling
- ✅ Much larger image display area
- ✅ Compact, accessible controls
- ✅ Prominent action buttons
- ✅ Better space utilization
- ✅ Integrated AI features
- ✅ Auto-save functionality
- ✅ Prompt tracking
- ✅ Status updates
- ✅ Progress indicators
"""
