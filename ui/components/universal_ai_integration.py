"""
Universal AI Button Integration System
For WaveSpeed AI Creative Suite

This system automatically adds AI improvement buttons to all tabs and fixes integration issues.
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable, List, Dict, Any
import asyncio
import threading
from core.logger import get_logger

logger = get_logger()

class UniversalAIIntegrator:
    """Universal system to add AI features to any tab"""
    
    def __init__(self):
        self.integrated_tabs = {}
        self.ai_available = False
        self._check_ai_availability()
    
    def _check_ai_availability(self):
        """Check if AI features are available"""
        try:
            import os
            self.ai_available = bool(os.getenv('CLAUDE_API_KEY') or os.getenv('OPENAI_API_KEY'))
        except:
            self.ai_available = False
    
    def integrate_with_tab(self, tab_instance, model_type: str, prompt_widget_name: str = 'prompt_text'):
        """Integrate AI features with any tab"""
        try:
            # Get the prompt text widget
            prompt_widget = getattr(tab_instance, prompt_widget_name, None)
            if not prompt_widget:
                logger.warning(f"Could not find prompt widget '{prompt_widget_name}' in {model_type} tab")
                return False
            
            # Find the best place to add AI buttons
            button_parent = self._find_button_parent(tab_instance)
            if not button_parent:
                logger.warning(f"Could not find suitable button parent in {model_type} tab")
                return False
            
            # Add AI buttons
            self._add_ai_buttons(button_parent, prompt_widget, model_type, tab_instance)
            
            # Add context menu
            self._add_context_menu(prompt_widget, model_type, tab_instance)
            
            # Track integration
            self.integrated_tabs[model_type] = {
                'tab_instance': tab_instance,
                'prompt_widget': prompt_widget,
                'button_parent': button_parent
            }
            
            logger.info(f"Successfully integrated AI features with {model_type} tab")
            return True
            
        except Exception as e:
            logger.error(f"Failed to integrate AI features with {model_type} tab: {e}")
            return False
    
    def _find_button_parent(self, tab_instance):
        """Find the best place to add AI buttons"""
        # Strategy 1: Check if optimized_layout has AI chat container
        if hasattr(tab_instance, 'optimized_layout') and hasattr(tab_instance.optimized_layout, 'ai_chat_container'):
            return tab_instance.optimized_layout.ai_chat_container
        
        # Strategy 2: Look for existing prompt action frames
        candidates = []
        
        def search_for_button_frames(widget, depth=0):
            if depth > 5:  # Prevent infinite recursion
                return
            
            try:
                for child in widget.winfo_children():
                    if isinstance(child, (ttk.Frame, tk.Frame)):
                        # Check if this frame contains buttons
                        button_count = 0
                        for grandchild in child.winfo_children():
                            if isinstance(grandchild, (ttk.Button, tk.Button)):
                                button_count += 1
                        
                        if button_count > 0:
                            candidates.append((child, button_count))
                        
                        # Recursively search
                        search_for_button_frames(child, depth + 1)
            except:
                pass
        
        # Start search from various possible root widgets
        search_roots = []
        for attr_name in ['container', 'main_frame', 'parent_frame', 'optimized_layout']:
            attr = getattr(tab_instance, attr_name, None)
            if attr:
                search_roots.append(attr)
        
        # Add the main widget if available
        if hasattr(tab_instance, 'winfo_children'):
            search_roots.append(tab_instance)
        
        # Special case: check if optimized_layout has a button_frame
        if hasattr(tab_instance, 'optimized_layout') and hasattr(tab_instance.optimized_layout, 'button_frame'):
            candidates.append((tab_instance.optimized_layout.button_frame, 1))
        
        for root in search_roots:
            search_for_button_frames(root)
        
        # Return the frame with the most buttons (likely the action frame)
        if candidates:
            best_frame = max(candidates, key=lambda x: x[1])[0]
            return best_frame
        
        return None
    
    def _add_ai_buttons(self, parent_frame, prompt_widget, model_type: str, tab_instance):
        """Add AI improvement buttons to the parent frame"""
        try:
            # Check if this is an optimized layout with add_ai_chat_interface method
            layout = None
            if hasattr(tab_instance, 'optimized_layout'):
                layout = tab_instance.optimized_layout
            elif hasattr(tab_instance, 'layout'):
                layout = tab_instance.layout
            
            if layout and hasattr(layout, 'add_ai_chat_interface'):
                # Use the new AI chat interface
                success = layout.add_ai_chat_interface(prompt_widget, model_type, tab_instance)
                if success:
                    logger.info(f"Added AI chat interface to {model_type} tab")
                    return
                else:
                    logger.warning(f"Failed to add AI chat interface to {model_type} tab, falling back to buttons")
            
            # Check if layout uses AIChatMixin (has the methods but no add_ai_chat_interface)
            if layout and hasattr(layout, 'improve_prompt_with_ai') and hasattr(layout, 'open_filter_training'):
                # Layout already has AI integration via mixin, don't add duplicate buttons
                logger.info(f"Layout for {model_type} already has AI integration via AIChatMixin")
                return
            
            # Fallback to traditional buttons
            # Create AI improve button
            improve_button = ttk.Button(
                parent_frame,
                text="✨ Improve with AI",
                command=lambda: self._show_ai_suggestions(prompt_widget, model_type, tab_instance)
            )
            
            # Create filter training button
            filter_button = ttk.Button(
                parent_frame,
                text="🛡️ Filter Training",
                command=lambda: self._show_filter_training(prompt_widget, model_type, tab_instance)
            )
            
            # Determine geometry manager used by existing buttons
            geometry_manager = self._detect_geometry_manager(parent_frame)
            
            if geometry_manager == 'grid':
                # Find next available column
                max_column = 0
                for child in parent_frame.winfo_children():
                    try:
                        info = child.grid_info()
                        if info and 'column' in info:
                            max_column = max(max_column, info['column'])
                    except:
                        pass
                
                improve_button.grid(row=0, column=max_column + 1, padx=(5, 0), sticky='ew')
                filter_button.grid(row=0, column=max_column + 2, padx=(5, 0), sticky='ew')
                
            elif geometry_manager == 'pack':
                improve_button.pack(side=tk.LEFT, padx=(5, 0))
                filter_button.pack(side=tk.LEFT, padx=(5, 0))
            
            # Update button states based on AI availability
            self._update_button_states([improve_button, filter_button])
            
            logger.info(f"Added AI buttons to {model_type} tab using {geometry_manager}")
            
        except Exception as e:
            logger.error(f"Error adding AI buttons to {model_type}: {e}")
    
    def _detect_geometry_manager(self, parent_frame):
        """Detect which geometry manager is used in the frame"""
        grid_count = 0
        pack_count = 0
        
        for child in parent_frame.winfo_children():
            try:
                if child.grid_info():
                    grid_count += 1
                if child.pack_info():
                    pack_count += 1
            except:
                pass
        
        return 'grid' if grid_count >= pack_count else 'pack'
    
    def _add_context_menu(self, prompt_widget, model_type: str, tab_instance):
        """Add right-click context menu to prompt widget"""
        try:
            def show_context_menu(event):
                context_menu = tk.Menu(prompt_widget, tearoff=0)
                
                # Standard text operations
                context_menu.add_command(label="Cut", command=lambda: prompt_widget.event_generate("<<Cut>>"))
                context_menu.add_command(label="Copy", command=lambda: prompt_widget.event_generate("<<Copy>>"))
                context_menu.add_command(label="Paste", command=lambda: prompt_widget.event_generate("<<Paste>>"))
                context_menu.add_separator()
                
                # AI features
                if self.ai_available:
                    context_menu.add_command(
                        label="✨ Improve with AI",
                        command=lambda: self._show_ai_suggestions(prompt_widget, model_type, tab_instance)
                    )
                    context_menu.add_command(
                        label="🛡️ Filter Training",
                        command=lambda: self._show_filter_training(prompt_widget, model_type, tab_instance)
                    )
                else:
                    context_menu.add_command(
                        label="✨ AI Features (Unavailable)",
                        state="disabled"
                    )
                
                try:
                    context_menu.tk_popup(event.x_root, event.y_root)
                finally:
                    context_menu.grab_release()
            
            prompt_widget.bind("<Button-3>", show_context_menu)  # Right-click
            logger.info(f"Added context menu to {model_type} prompt widget")
            
        except Exception as e:
            logger.error(f"Error adding context menu to {model_type}: {e}")
    
    def _update_button_states(self, buttons: List[tk.Widget]):
        """Update button states based on AI availability"""
        state = "normal" if self.ai_available else "disabled"
        tooltip_text = "Configure API keys in AI Assistant → Settings" if not self.ai_available else ""
        
        for button in buttons:
            button.config(state=state)
            if not self.ai_available and hasattr(button, 'bind'):
                # Add tooltip for disabled buttons
                self._add_tooltip(button, tooltip_text)
    
    def _add_tooltip(self, widget, text):
        """Add tooltip to widget"""
        def show_tooltip(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            
            label = tk.Label(
                tooltip,
                text=text,
                background="yellow",
                relief="solid",
                borderwidth=1,
                font=("Arial", 9)
            )
            label.pack()
            
            # Auto-hide after 3 seconds
            tooltip.after(3000, tooltip.destroy)
        
        def hide_tooltip(event):
            pass
        
        widget.bind("<Enter>", show_tooltip)
        widget.bind("<Leave>", hide_tooltip)
    
    def _show_ai_suggestions(self, prompt_widget, model_type: str, tab_instance):
        """Show AI chat interface for prompt improvement"""
        try:
            from ui.components.fixed_ai_settings import check_and_show_ai_unavailable_message
            
            if not check_and_show_ai_unavailable_message(prompt_widget.winfo_toplevel()):
                return
            
            # Get current prompt
            current_prompt = prompt_widget.get("1.0", tk.END).strip()
            if not current_prompt:
                tk.messagebox.showwarning("No Prompt", "Please enter a prompt first.")
                return
            
            # Import and show the new AI chat interface
            from ui.components.ai_prompt_chat import show_ai_prompt_chat
            
            # Create callback to apply improved prompts
            def apply_prompt_callback(improved_prompt: str):
                prompt_widget.delete("1.0", tk.END)
                prompt_widget.insert("1.0", improved_prompt)
                logger.info("Applied improved prompt from AI chat")
            
            # Show the chat interface
            show_ai_prompt_chat(
                parent=tab_instance.frame.winfo_toplevel(),
                current_prompt=current_prompt,
                tab_name=model_type,
                on_prompt_updated=apply_prompt_callback
            )
            
        except Exception as e:
            logger.error(f"Error showing AI chat: {e}")
            tk.messagebox.showerror("Error", f"Failed to show AI chat: {str(e)}")
    
    def _show_filter_training(self, prompt_widget, model_type: str, tab_instance):
        """Show filter training chat interface"""
        try:
            from ui.components.fixed_ai_settings import check_and_show_ai_unavailable_message
            
            if not check_and_show_ai_unavailable_message(prompt_widget.winfo_toplevel()):
                return
            
            # Show warning dialog
            result = tk.messagebox.askyesno(
                "Filter Training Mode",
                "⚠️ WARNING: Filter Training Mode generates harmful prompt examples for safety filter development only.\n\n"
                "These examples are NEVER executed for generation - they are used to train safety filters.\n\n"
                "Do you want to continue?",
                icon="warning"
            )
            
            if not result:
                return
            
            current_prompt = prompt_widget.get("1.0", tk.END).strip()
            if not current_prompt:
                tk.messagebox.showwarning("No Prompt", "Please enter a prompt first.")
                return
            
            # Import and show the AI chat interface in filter training mode
            from ui.components.ai_prompt_chat import AIPromptChat
            
            # Create callback to apply filter training results
            def apply_prompt_callback(improved_prompt: str):
                prompt_widget.delete("1.0", tk.END)
                prompt_widget.insert("1.0", improved_prompt)
                logger.info("Applied filter training prompt from AI chat")
            
            # Create chat interface in filter training mode
            chat = AIPromptChat(
                parent=tab_instance.frame.winfo_toplevel(),
                on_prompt_updated=apply_prompt_callback
            )
            chat.show_chat(current_prompt, model_type)
            # Set filter training mode
            chat.filter_training = True
            
        except Exception as e:
            logger.error(f"Error showing filter training chat: {e}")
            tk.messagebox.showerror("Error", f"Failed to show filter training chat: {str(e)}")
    
    def _show_suggestions_async(self, prompt_widget, current_prompt: str, model_type: str, tab_instance):
        """Show AI suggestions asynchronously"""
        def run_async():
            try:
                # Import here to avoid circular imports
                from core.ai_prompt_advisor import get_ai_advisor
                from ui.components.enhanced_ai_suggestions import show_enhanced_suggestions, PromptSuggestion
                
                advisor = get_ai_advisor()
                
                # Show loading dialog
                loading_dialog = self._show_loading_dialog(prompt_widget.winfo_toplevel(), "Getting AI suggestions...")
                
                def callback(suggestions_data):
                    try:
                        loading_dialog.destroy()
                        
                        if suggestions_data and 'suggestions' in suggestions_data:
                            suggestions = []
                            for item in suggestions_data['suggestions']:
                                suggestion = PromptSuggestion(
                                    improved_prompt=item.get('improved_prompt', ''),
                                    explanation=item.get('explanation', ''),
                                    category=item.get('category', 'general'),
                                    confidence=item.get('confidence', 0.8)
                                )
                                suggestions.append(suggestion)
                            
                            # Apply suggestion callback
                            def apply_suggestion(improved_prompt: str):
                                prompt_widget.delete("1.0", tk.END)
                                prompt_widget.insert("1.0", improved_prompt)
                                
                                # Call tab-specific callback if available
                                if hasattr(tab_instance, 'apply_ai_suggestion'):
                                    tab_instance.apply_ai_suggestion(improved_prompt)
                            
                            show_enhanced_suggestions(
                                prompt_widget.winfo_toplevel(),
                                current_prompt,
                                suggestions,
                                apply_suggestion,
                                model_type
                            )
                        else:
                            tk.messagebox.showinfo("No Suggestions", "No AI suggestions were generated. Please try again.")
                    
                    except Exception as e:
                        logger.error(f"Error processing suggestions: {e}")
                        tk.messagebox.showerror("Error", f"Error processing suggestions: {str(e)}")
                
                # Run async request
                threading.Thread(
                    target=lambda: self._get_suggestions_threaded(advisor, current_prompt, model_type, callback),
                    daemon=True
                ).start()
                
            except Exception as e:
                logger.error(f"Error in async suggestions: {e}")
                tk.messagebox.showerror("Error", f"Failed to get AI suggestions: {str(e)}")
        
        run_async()
    
    def _show_filter_training_async(self, prompt_widget, current_prompt: str, model_type: str, tab_instance):
        """Show filter training suggestions asynchronously"""
        def run_async():
            try:
                from core.ai_prompt_advisor import get_ai_advisor
                from ui.components.enhanced_ai_suggestions import show_enhanced_suggestions, PromptSuggestion
                
                advisor = get_ai_advisor()
                
                loading_dialog = self._show_loading_dialog(prompt_widget.winfo_toplevel(), "Generating filter training data...")
                
                def callback(suggestions_data):
                    try:
                        loading_dialog.destroy()
                        
                        if suggestions_data and 'suggestions' in suggestions_data:
                            suggestions = []
                            for item in suggestions_data['suggestions']:
                                suggestion = PromptSuggestion(
                                    improved_prompt=item.get('improved_prompt', ''),
                                    explanation=item.get('explanation', ''),
                                    category=f"Filter Training - {item.get('category', 'general').title()}",
                                    confidence=item.get('confidence', 0.8)
                                )
                                suggestions.append(suggestion)
                            
                            def apply_suggestion(improved_prompt: str):
                                # For filter training, just copy to clipboard instead of applying
                                prompt_widget.winfo_toplevel().clipboard_clear()
                                prompt_widget.winfo_toplevel().clipboard_append(improved_prompt)
                                tk.messagebox.showinfo(
                                    "Copied to Clipboard",
                                    "Filter training example copied to clipboard.\n\n"
                                    "⚠️ Remember: This is for safety filter development only!"
                                )
                            
                            show_enhanced_suggestions(
                                prompt_widget.winfo_toplevel(),
                                current_prompt,
                                suggestions,
                                apply_suggestion,
                                f"{model_type} - Filter Training"
                            )
                        else:
                            tk.messagebox.showinfo("No Data", "No filter training data was generated. Please try again.")
                    
                    except Exception as e:
                        logger.error(f"Error processing filter training: {e}")
                        tk.messagebox.showerror("Error", f"Error processing filter training: {str(e)}")
                
                # Run async request for filter training
                threading.Thread(
                    target=lambda: self._get_filter_training_threaded(advisor, current_prompt, model_type, callback),
                    daemon=True
                ).start()
                
            except Exception as e:
                logger.error(f"Error in async filter training: {e}")
                tk.messagebox.showerror("Error", f"Failed to get filter training data: {str(e)}")
        
        run_async()
    
    def _get_suggestions_threaded(self, advisor, prompt: str, model_type: str, callback):
        """Get suggestions in a background thread"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(advisor.improve_prompt(prompt, model_type))
            callback(result)
        except Exception as e:
            logger.error(f"Error getting suggestions: {e}")
            callback(None)
    
    def _get_filter_training_threaded(self, advisor, prompt: str, model_type: str, callback):
        """Get filter training data in a background thread"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(advisor.generate_filter_training_data(prompt, model_type))
            callback(result)
        except Exception as e:
            logger.error(f"Error getting filter training: {e}")
            callback(None)
    
    def _show_loading_dialog(self, parent, message: str):
        """Show a loading dialog"""
        dialog = tk.Toplevel(parent)
        dialog.title("AI Assistant")
        dialog.geometry("300x150")
        dialog.transient(parent)
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Content
        tk.Label(
            dialog,
            text="🤖",
            font=('Arial', 24)
        ).pack(pady=(20, 10))
        
        tk.Label(
            dialog,
            text=message,
            font=('Arial', 11),
            wraplength=250
        ).pack(pady=(0, 20))
        
        return dialog
    
    def refresh_ai_availability(self):
        """Refresh AI availability status"""
        self._check_ai_availability()
        
        # Update all integrated buttons
        for model_type, integration in self.integrated_tabs.items():
            try:
                button_parent = integration['button_parent']
                buttons = [child for child in button_parent.winfo_children() 
                          if isinstance(child, (ttk.Button, tk.Button)) and 
                          ('AI' in child.cget('text') or '✨' in child.cget('text') or '🛡️' in child.cget('text'))]
                self._update_button_states(buttons)
            except Exception as e:
                logger.error(f"Error updating buttons for {model_type}: {e}")

# Global integrator instance
universal_ai_integrator = UniversalAIIntegrator()

def integrate_ai_with_tab(tab_instance, model_type: str, prompt_widget_name: str = 'prompt_text'):
    """Integrate AI features with any tab - public interface"""
    return universal_ai_integrator.integrate_with_tab(tab_instance, model_type, prompt_widget_name)

def refresh_ai_button_states():
    """Refresh AI button states - call after settings changes"""
    universal_ai_integrator.refresh_ai_availability()

# Auto-integration decorator
def auto_integrate_ai(model_type: str, prompt_widget_name: str = 'prompt_text'):
    """Decorator to automatically integrate AI features with a tab class"""
    def decorator(cls):
        original_init = cls.__init__
        
        def new_init(self, *args, **kwargs):
            # Call original init
            original_init(self, *args, **kwargs)
            
            # Integrate AI features after a short delay to ensure UI is ready
            def delayed_integration():
                integrate_ai_with_tab(self, model_type, prompt_widget_name)
            
            # Schedule integration after UI is fully constructed
            if hasattr(self, 'after'):
                self.after(100, delayed_integration)
            else:
                # Fallback for cases where 'after' is not available
                import threading
                threading.Timer(0.1, delayed_integration).start()
        
        cls.__init__ = new_init
        return cls
    
    return decorator
