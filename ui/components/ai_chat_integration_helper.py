"""
AI Chat Integration Helper
Provides reusable methods for integrating AI chat across all layout components
"""

import tkinter as tk
import asyncio
from core.logger import get_logger

logger = get_logger()

class AIChatIntegrationHelper:
    """Helper class to provide AI chat integration methods to layout components"""
    
    @staticmethod
    def open_ai_prompt_assistant(parent_widget, current_prompt_widget, tab_name: str, on_prompt_updated_callback=None):
        """Open regular AI prompt assistant (not filter training)"""
        try:
            # Get current prompt
            current_prompt = current_prompt_widget.get("1.0", tk.END).strip()
            
            # Clear placeholder text if it exists
            placeholder_texts = [
                "Describe the changes you want to make to the image...",
                "Enter your prompt here...",
                "Describe your editing instructions...",
                "Enter prompt..."
            ]
            
            if current_prompt in placeholder_texts or not current_prompt:
                current_prompt = "Improve the image quality while maintaining the original composition"
            
            # Import and show AI chat
            from ui.components.ai_prompt_chat import show_ai_prompt_chat
            
            # Create AI chat window
            chat_window = tk.Toplevel(parent_widget)
            chat_window.title(f"🤖 AI Prompt Assistant - {tab_name}")
            chat_window.geometry("800x700")
            chat_window.resizable(True, True)
            
            # Make it modal
            chat_window.transient(parent_widget)
            chat_window.grab_set()
            
            # Center the window
            try:
                x = parent_widget.winfo_rootx() + 100
                y = parent_widget.winfo_rooty() + 50
                chat_window.geometry(f"+{x}+{y}")
            except:
                pass  # Fallback to default positioning
            
            # Create chat interface
            chat = show_ai_prompt_chat(
                parent=chat_window,
                current_prompt=current_prompt,
                tab_name=tab_name,
                on_prompt_updated=on_prompt_updated_callback
            )
            
            # Normal AI mode (not filter training)
            chat.filter_training = False
            chat.setup_action_buttons()
            chat.update_placeholder_text()
            
            return chat
            
        except Exception as e:
            logger.error(f"Error opening AI assistant: {e}")
            raise
    
    @staticmethod
    def open_filter_training_assistant(parent_widget, current_prompt_widget, tab_name: str, on_prompt_updated_callback=None, current_image_path=None):
        """Open filter training assistant"""
        try:
            # Get current prompt
            current_prompt = current_prompt_widget.get("1.0", tk.END).strip()
            
            # Clear placeholder text if it exists
            placeholder_texts = [
                "Describe the changes you want to make to the image...",
                "Enter your prompt here...",
                "Describe your editing instructions...",
                "Enter prompt..."
            ]
            
            if current_prompt in placeholder_texts or not current_prompt:
                current_prompt = "Remove clothing from the subject while maintaining realistic appearance"
            
            # Import and show AI chat
            from ui.components.ai_prompt_chat import show_ai_prompt_chat
            
            # Create AI chat window
            chat_window = tk.Toplevel(parent_widget)
            chat_window.title(f"🛡️ Filter Training Assistant - {tab_name}")
            chat_window.geometry("800x700")
            chat_window.resizable(True, True)
            
            # Make it modal
            chat_window.transient(parent_widget)
            chat_window.grab_set()
            
            # Center the window
            try:
                x = parent_widget.winfo_rootx() + 100
                y = parent_widget.winfo_rooty() + 50
                chat_window.geometry(f"+{x}+{y}")
            except:
                pass  # Fallback to default positioning
            
            # Create chat interface
            chat = show_ai_prompt_chat(
                parent=chat_window,
                current_prompt=current_prompt,
                tab_name=f"{tab_name} Filter Training",
                on_prompt_updated=on_prompt_updated_callback
            )
            
            # Enable filter training mode
            chat.filter_training = True
            chat.setup_action_buttons()
            chat.update_placeholder_text()
            
            # Set current image if available
            if current_image_path:
                chat.set_current_image(current_image_path)
            
            return chat
            
        except Exception as e:
            logger.error(f"Error opening filter training: {e}")
            raise
    
    @staticmethod
    def create_prompt_update_callback(prompt_widget, status_update_callback=None, is_filter_training=False):
        """Create a callback function for prompt updates"""
        def _on_prompt_updated(new_prompt: str):
            try:
                # Update the prompt text field
                prompt_widget.delete("1.0", tk.END)
                prompt_widget.insert("1.0", new_prompt)
                
                # Remove placeholder styling if it exists
                try:
                    prompt_widget.config(foreground='black')
                except:
                    pass
                
                # Update status if callback provided
                if status_update_callback:
                    if is_filter_training:
                        status_update_callback("🛡️ Filter training prompt applied - Ready for processing", "success")
                    else:
                        status_update_callback("🤖 AI-improved prompt applied - Ready for processing", "success")
                
            except Exception as e:
                logger.error(f"Error updating prompt: {e}")
                if status_update_callback:
                    status_update_callback(f"Error updating prompt: {str(e)}", "error")
        
        return _on_prompt_updated

class AIChatMixin:
    """Mixin class that can be added to layout components to provide AI chat integration"""
    
    def improve_prompt_with_ai(self):
        """Improve prompt with AI (regular mode, not filter training)"""
        try:
            # Get prompt widget - try common names
            prompt_widget = getattr(self, 'prompt_text', None) or getattr(self, 'prompt_widget', None)
            if not prompt_widget:
                raise AttributeError("No prompt widget found")
            
            # Get status update callback
            status_callback = getattr(self, 'update_status', None)
            
            # Create callback for prompt updates
            update_callback = AIChatIntegrationHelper.create_prompt_update_callback(
                prompt_widget, 
                status_callback, 
                is_filter_training=False
            )
            
            # Get tab name
            tab_name = getattr(self, 'tab_name', 'Unknown Tab')
            
            # Open AI assistant
            chat = AIChatIntegrationHelper.open_ai_prompt_assistant(
                parent_widget=self.parent_frame if hasattr(self, 'parent_frame') else self,
                current_prompt_widget=prompt_widget,
                tab_name=tab_name,
                on_prompt_updated_callback=update_callback
            )
            
            # Update status
            if status_callback:
                status_callback("🤖 AI assistant opened - Get help improving your prompt", "info")
                
        except Exception as e:
            logger.error(f"Error opening AI assistant: {e}")
            status_callback = getattr(self, 'update_status', None)
            if status_callback:
                status_callback(f"Error opening AI assistant: {str(e)}", "error")
    
    def open_filter_training(self):
        """Open filter training chat interface"""
        try:
            # Get prompt widget - try common names
            prompt_widget = getattr(self, 'prompt_text', None) or getattr(self, 'prompt_widget', None)
            if not prompt_widget:
                raise AttributeError("No prompt widget found")
            
            # Get status update callback
            status_callback = getattr(self, 'update_status', None)
            
            # Create callback for prompt updates
            update_callback = AIChatIntegrationHelper.create_prompt_update_callback(
                prompt_widget, 
                status_callback, 
                is_filter_training=True
            )
            
            # Get tab name
            tab_name = getattr(self, 'tab_name', 'Unknown Tab')
            
            # Get current image if available
            current_image = getattr(self, 'selected_image_path', None) or getattr(self, 'current_image_path', None)
            
            # Open filter training assistant
            chat = AIChatIntegrationHelper.open_filter_training_assistant(
                parent_widget=self.parent_frame if hasattr(self, 'parent_frame') else self,
                current_prompt_widget=prompt_widget,
                tab_name=tab_name,
                on_prompt_updated_callback=update_callback,
                current_image_path=current_image
            )
            
            # Update status
            if status_callback:
                status_callback("🛡️ Filter training assistant opened - Generate harmful examples for safety research", "info")
                
            # Show learning panel if available
            if hasattr(self, 'learning_panel'):
                try:
                    self.learning_panel.learning_frame.grid()
                except:
                    pass
                    
        except Exception as e:
            logger.error(f"Error opening filter training: {e}")
            status_callback = getattr(self, 'update_status', None)
            if status_callback:
                status_callback(f"Error opening filter training: {str(e)}", "error")