"""
Prompt Integration Helper
For WaveSpeed AI Creative Suite

Provides easy integration of the enhanced prompt browser with existing tabs.
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable
from ui.components.enhanced_prompt_browser import show_enhanced_prompt_browser
from core.logger import get_logger

logger = get_logger()

def add_enhanced_prompt_button(parent_frame, prompt_text_widget, model_type: str, 
                              on_prompt_selected: Optional[Callable] = None) -> ttk.Button:
    """
    Add an enhanced prompt browser button to an existing prompt section.
    
    Args:
        parent_frame: The frame to add the button to
        prompt_text_widget: The text widget that will receive the selected prompt
        model_type: The AI model type (e.g., "nano_banana", "seededit", etc.)
        on_prompt_selected: Optional callback when a prompt is selected
    
    Returns:
        The created button widget
    """
    
    def handle_prompt_selection(prompt_content: str):
        """Handle prompt selection from the browser"""
        try:
            # Clear existing content
            prompt_text_widget.delete("1.0", tk.END)
            
            # Insert new prompt
            prompt_text_widget.insert("1.0", prompt_content)
            
            # Call custom callback if provided
            if on_prompt_selected:
                on_prompt_selected(prompt_content)
                
            logger.info(f"Applied prompt to {model_type} tab")
            
        except Exception as e:
            logger.error(f"Error applying prompt: {e}")
    
    def show_browser():
        """Show the enhanced prompt browser"""
        try:
            show_enhanced_prompt_browser(
                parent=parent_frame.winfo_toplevel(),
                model_type=model_type,
                on_select=handle_prompt_selection
            )
        except Exception as e:
            logger.error(f"Error showing prompt browser: {e}")
    
    # Create the enhanced prompt button
    enhanced_btn = ttk.Button(
        parent_frame,
        text="📚 Enhanced Library",
        command=show_browser,
        style="Accent.TButton"  # Use accent style if available
    )
    
    return enhanced_btn


def replace_simple_prompt_buttons(tab_instance, model_type: str):
    """
    Replace simple prompt loading buttons with enhanced prompt browser.
    
    This function can be called in tab __init__ methods to upgrade
    existing prompt management to the enhanced system.
    
    Args:
        tab_instance: The tab instance (e.g., self in a tab class)
        model_type: The AI model type for this tab
    """
    
    # Find existing prompt action frames and replace buttons
    def find_and_replace_buttons(widget):
        """Recursively find and replace prompt buttons"""
        try:
            for child in widget.winfo_children():
                if isinstance(child, ttk.Frame):
                    # Check if this frame contains prompt buttons
                    has_prompt_buttons = False
                    for grandchild in child.winfo_children():
                        if isinstance(grandchild, ttk.Button):
                            button_text = grandchild.cget("text").lower()
                            if any(keyword in button_text for keyword in ["prompt", "load", "save"]):
                                has_prompt_buttons = True
                                break
                    
                    if has_prompt_buttons:
                        # Add enhanced prompt button to this frame
                        enhanced_btn = add_enhanced_prompt_button(
                            child,
                            tab_instance.prompt_text,
                            model_type
                        )
                        
                        # Use the same geometry manager as other buttons
                        if hasattr(child, 'grid_info') and child.grid_info():
                            # Frame uses grid
                            enhanced_btn.grid(row=0, column=2, sticky=(tk.W, tk.E), padx=(5, 0))
                        else:
                            # Frame uses pack
                            enhanced_btn.pack(side=tk.LEFT, padx=(5, 0))
                        
                        logger.info(f"Added enhanced prompt button to {model_type} tab")
                        return True
                
                # Recursively search children
                if find_and_replace_buttons(child):
                    return True
                    
        except Exception as e:
            logger.error(f"Error finding prompt buttons: {e}")
        
        return False
    
    # Start search from the tab's main frame
    if hasattr(tab_instance, 'parent_frame'):
        find_and_replace_buttons(tab_instance.parent_frame)
    elif hasattr(tab_instance, 'main_frame'):
        find_and_replace_buttons(tab_instance.main_frame)


def create_prompt_management_section(parent_frame, prompt_text_widget, model_type: str,
                                   on_save: Optional[Callable] = None,
                                   on_load: Optional[Callable] = None) -> ttk.Frame:
    """
    Create a complete prompt management section with enhanced features.
    
    Args:
        parent_frame: Parent frame to add the section to
        prompt_text_widget: Text widget for prompt content
        model_type: AI model type
        on_save: Optional callback for save functionality
        on_load: Optional callback for load functionality
    
    Returns:
        The created prompt management frame
    """
    
    # Create main prompt management frame
    prompt_frame = ttk.LabelFrame(parent_frame, text="📝 Prompt Management", padding="10")
    
    # Prompt text area
    prompt_text_frame = ttk.Frame(prompt_frame)
    prompt_text_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
    
    # Add scrollbar to prompt text
    prompt_scrollbar = ttk.Scrollbar(prompt_text_frame)
    prompt_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    prompt_text_widget.config(yscrollcommand=prompt_scrollbar.set)
    prompt_text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    prompt_scrollbar.config(command=prompt_text_widget.yview)
    
    # Action buttons frame
    actions_frame = ttk.Frame(prompt_frame)
    actions_frame.pack(fill=tk.X, pady=(10, 0))
    
    # Enhanced prompt browser button
    enhanced_btn = add_enhanced_prompt_button(
        actions_frame,
        prompt_text_widget,
        model_type
    )
    enhanced_btn.pack(side=tk.LEFT, padx=(0, 10))
    
    # Save button (if callback provided)
    if on_save:
        save_btn = ttk.Button(
            actions_frame,
            text="💾 Save Prompt",
            command=on_save
        )
        save_btn.pack(side=tk.LEFT, padx=(0, 10))
    
    # Load button (if callback provided)
    if on_load:
        load_btn = ttk.Button(
            actions_frame,
            text="📋 Load Prompt",
            command=on_load
        )
        load_btn.pack(side=tk.LEFT, padx=(0, 10))
    
    # Clear button
    clear_btn = ttk.Button(
        actions_frame,
        text="🗑️ Clear",
        command=lambda: prompt_text_widget.delete("1.0", tk.END)
    )
    clear_btn.pack(side=tk.LEFT)
    
    return prompt_frame


# Example usage for tab integration
def integrate_with_existing_tab(tab_class, model_type: str):
    """
    Decorator/helper to integrate enhanced prompt management with existing tabs.
    
    Usage:
        @integrate_with_existing_tab("nano_banana")
        class ImageEditorTab(BaseTab):
            # existing code...
    """
    
    def decorator(cls):
        original_init = cls.__init__
        
        def new_init(self, *args, **kwargs):
            # Call original init
            original_init(self, *args, **kwargs)
            
            # Add enhanced prompt management
            self.model_type = model_type
            
            # Try to find and enhance existing prompt sections
            replace_simple_prompt_buttons(self, model_type)
            
            logger.info(f"Enhanced prompt management integrated with {cls.__name__}")
        
        cls.__init__ = new_init
        return cls
    
    return decorator


# Quick integration examples for each tab type
INTEGRATION_EXAMPLES = {
    "nano_banana": {
        "model_type": "nano_banana",
        "description": "Nano Banana Editor prompts"
    },
    "seededit": {
        "model_type": "seededit", 
        "description": "SeedEdit prompts"
    },
    "seedream_v4": {
        "model_type": "seedream_v4",
        "description": "Seedream V4 prompts"
    },
    "wan_22": {
        "model_type": "wan_22",
        "description": "Wan 2.2 video prompts"
    },
    "seeddance": {
        "model_type": "seeddance",
        "description": "SeedDance Pro prompts"
    }
}


if __name__ == "__main__":
    # Test the integration
    root = tk.Tk()
    root.title("Prompt Integration Test")
    
    # Create a test prompt text widget
    prompt_text = tk.Text(root, height=10, width=50)
    prompt_text.pack(pady=10)
    
    # Create a test frame for buttons
    button_frame = ttk.Frame(root)
    button_frame.pack(pady=10)
    
    # Add enhanced prompt button
    enhanced_btn = add_enhanced_prompt_button(
        button_frame,
        prompt_text,
        "nano_banana"
    )
    enhanced_btn.pack(side=tk.LEFT, padx=5)
    
    # Test button
    test_btn = ttk.Button(button_frame, text="Test", command=lambda: print("Test"))
    test_btn.pack(side=tk.LEFT, padx=5)
    
    root.mainloop()
