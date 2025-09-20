"""
Enhanced Prompt Tracking Integration Guide
Step-by-step integration for all layouts and tabs
"""

from core.enhanced_prompt_tracker import enhanced_prompt_tracker, FailureReason
from core.quality_rating_widget import QualityRatingWidget

class PromptTrackingIntegrator:
    """Helper class for integrating enhanced prompt tracking into existing layouts"""
    
    @staticmethod
    def integrate_into_layout(layout_instance, model_name: str):
        """
        Integrate enhanced prompt tracking into any layout
        
        Args:
            layout_instance: The layout instance to integrate tracking into
            model_name: Name of the AI model (e.g., 'seededit', 'seedream_v4', 'wan22')
        """
        # Add tracking variables
        layout_instance.current_prompt = None
        layout_instance.current_prompt_hash = None
        layout_instance.quality_rating_widget = None
        layout_instance.model_name = model_name
        
        # Store original methods
        original_process_method = getattr(layout_instance, 'process_' + model_name.replace('-', '_'), None)
        original_after_method = getattr(layout_instance, 'after_processing', None)
        
        # Enhance process method
        def enhanced_process(*args, **kwargs):
            # Store current prompt
            prompt = layout_instance.get_current_prompt()  # Layout must implement this
            layout_instance.current_prompt = prompt
            layout_instance.current_prompt_hash = hash(prompt) if prompt else None
            
            # Call original method
            if original_process_method:
                return original_process_method(*args, **kwargs)
        
        # Enhance after processing method
        def enhanced_after_processing(success: bool, result_url: str = None, error_message: str = None):
            if success and layout_instance.current_prompt:
                # Log successful prompt
                enhanced_prompt_tracker.log_successful_prompt(
                    prompt=layout_instance.current_prompt,
                    ai_model=model_name,
                    result_url=result_url,
                    save_method="auto",
                    model_parameters=layout_instance.get_model_parameters(),  # Layout must implement this
                )
                
                # Show quality rating
                PromptTrackingIntegrator.show_quality_rating(layout_instance, result_url)
                
            elif not success and layout_instance.current_prompt:
                # Log failed prompt
                enhanced_prompt_tracker.log_failed_prompt(
                    prompt=layout_instance.current_prompt,
                    ai_model=model_name,
                    error_message=error_message,
                    failure_reason=PromptTrackingIntegrator.categorize_failure(error_message),
                    model_parameters=layout_instance.get_model_parameters(),
                )
            
            # Call original after processing
            if original_after_method:
                return original_after_method(success, result_url, error_message)
        
        # Replace methods
        setattr(layout_instance, 'process_' + model_name.replace('-', '_'), enhanced_process)
        setattr(layout_instance, 'after_processing', enhanced_after_processing)
    
    @staticmethod
    def show_quality_rating(layout_instance, result_url: str):
        """Show quality rating widget in the layout"""
        if not hasattr(layout_instance, 'rating_container'):
            # Create rating container if it doesn't exist
            PromptTrackingIntegrator.create_rating_container(layout_instance)
        
        # Clear existing rating widget
        for widget in layout_instance.rating_container.winfo_children():
            widget.destroy()
        
        # Create new quality rating widget
        layout_instance.quality_rating_widget = QualityRatingWidget(
            parent=layout_instance.rating_container,
            prompt=layout_instance.current_prompt,
            result_path=result_url,
            prompt_hash=layout_instance.current_prompt_hash
        )
        layout_instance.quality_rating_widget.pack(fill="x")
        
        # Show the rating frame
        if hasattr(layout_instance, 'rating_frame'):
            layout_instance.rating_frame.pack(fill="x", pady=(0, 4))
    
    @staticmethod
    def create_rating_container(layout_instance):
        """Create rating container for layouts that don't have one"""
        import tkinter as tk
        from tkinter import ttk
        
        # Try to find a suitable parent (usually the left column or main container)
        parent = None
        if hasattr(layout_instance, 'left_frame'):
            parent = layout_instance.left_frame
        elif hasattr(layout_instance, 'parent_frame'):
            parent = layout_instance.parent_frame
        
        if parent:
            layout_instance.rating_frame = ttk.LabelFrame(parent, text="⭐ Rate Result Quality", padding="8")
            layout_instance.rating_container = ttk.Frame(layout_instance.rating_frame)
            layout_instance.rating_container.pack(fill="x")
    
    @staticmethod
    def categorize_failure(error_message: str) -> FailureReason:
        """Categorize error message into failure reason"""
        if not error_message:
            return FailureReason.OTHER
        
        error_lower = error_message.lower()
        
        if "filter" in error_lower or "content policy" in error_lower:
            return FailureReason.CONTENT_FILTER
        elif "timeout" in error_lower:
            return FailureReason.TIMEOUT
        elif "network" in error_lower or "connection" in error_lower:
            return FailureReason.NETWORK_ERROR
        elif "server" in error_lower or "500" in error_lower or "503" in error_lower:
            return FailureReason.SERVER_ERROR
        elif "quota" in error_lower or "limit exceeded" in error_lower or "rate limit" in error_lower:
            return FailureReason.QUOTA_EXCEEDED
        elif "parameter" in error_lower or "invalid" in error_lower or "bad request" in error_lower:
            return FailureReason.INVALID_PARAMETERS
        elif "nsfw" in error_lower or "adult content" in error_lower or "inappropriate" in error_lower:
            return FailureReason.NSFW_CONTENT
        elif "api" in error_lower or "401" in error_lower or "403" in error_lower:
            return FailureReason.API_ERROR
        else:
            return FailureReason.OTHER

# Integration examples for different layout types
class LayoutIntegrationExamples:
    """Examples of how to integrate tracking into different layout types"""
    
    @staticmethod
    def integrate_seededit_layout(layout):
        """Example integration for SeedEdit layout"""
        def get_current_prompt():
            return layout.prompt_text.get("1.0", "end").strip()
        
        def get_model_parameters():
            return {
                "guidance_scale": layout.guidance_scale_var.get(),
                "steps": layout.steps_var.get(),
                "seed": layout.seed_var.get(),
                "format": layout.format_var.get()
            }
        
        layout.get_current_prompt = get_current_prompt
        layout.get_model_parameters = get_model_parameters
        
        PromptTrackingIntegrator.integrate_into_layout(layout, "seededit")
    
    @staticmethod
    def integrate_seedream_layout(layout):
        """Example integration for Seedream layout"""
        def get_current_prompt():
            return layout.change_prompt_text.get("1.0", "end").strip()
        
        def get_model_parameters():
            return {
                "width": layout.width_var.get(),
                "height": layout.height_var.get(),
                "guidance_scale": layout.guidance_scale_var.get(),
                "steps": layout.steps_var.get(),
                "seed": layout.seed_var.get()
            }
        
        layout.get_current_prompt = get_current_prompt
        layout.get_model_parameters = get_model_parameters
        
        PromptTrackingIntegrator.integrate_into_layout(layout, "seedream_v4")
    
    @staticmethod
    def integrate_wan22_layout(layout):
        """Example integration for Wan 2.2 video layout"""
        def get_current_prompt():
            return layout.video_prompt_text.get("1.0", "end").strip()
        
        def get_model_parameters():
            return {
                "duration": layout.duration_var.get(),
                "seed": layout.seed_var.get(),
                "negative_prompt": layout.negative_prompt_text.get("1.0", "end").strip()
            }
        
        layout.get_current_prompt = get_current_prompt
        layout.get_model_parameters = get_model_parameters
        
        PromptTrackingIntegrator.integrate_into_layout(layout, "wan22")

# Quick integration function
def quick_integrate_tracking(layout, model_name: str, prompt_getter, params_getter):
    """
    Quick integration function for any layout
    
    Args:
        layout: Layout instance
        model_name: AI model name
        prompt_getter: Function that returns current prompt
        params_getter: Function that returns model parameters dict
    """
    layout.get_current_prompt = prompt_getter
    layout.get_model_parameters = params_getter
    PromptTrackingIntegrator.integrate_into_layout(layout, model_name)