# 🔧 Fix AI Buttons to Use New Chat Interface

## Problem
The "✨ Improve with AI" and "🛡️ Filter Training" buttons are showing up but they're calling the old suggestion system instead of the new AI chat interface.

## Solution
Update the button commands to use the new `AIPromptChatDialog` that we created.

---

## 📁 File 1: Update `ui/components/universal_ai_integration.py`

Replace the `_add_ai_buttons` method and add the new chat methods:

```python
def _add_ai_buttons(self, parent_frame, prompt_widget, model_type: str, tab_instance):
    """Add AI improvement buttons to the parent frame"""
    try:
        # Create AI improve button - NOW USES CHAT INTERFACE
        improve_button = ttk.Button(
            parent_frame,
            text="✨ Improve with AI",
            command=lambda: self._open_ai_chat(prompt_widget, model_type, tab_instance)
        )
        
        # Create filter training button
        filter_button = ttk.Button(
            parent_frame,
            text="🛡️ Filter Training",
            command=lambda: self._open_filter_training_chat(prompt_widget, model_type, tab_instance)
        )
        
        # ... rest of existing layout code stays the same ...
        
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

def _open_ai_chat(self, prompt_widget, model_type: str, tab_instance):
    """Open the AI chat interface for prompt improvement"""
    try:
        # Get current prompt
        current_prompt = ""
        if hasattr(prompt_widget, 'get'):
            if prompt_widget.winfo_class() == 'Text':
                current_prompt = prompt_widget.get("1.0", tk.END).strip()
            else:
                current_prompt = prompt_widget.get().strip()
        
        if not current_prompt:
            from utils.warning_dialogs import show_error
            show_error("No Prompt", "Please enter a prompt first before requesting AI help.")
            return
        
        if not self.ai_advisor.is_available():
            from utils.warning_dialogs import show_error
            show_error("AI Unavailable", 
                      "Please configure Claude or OpenAI API keys in your .env file.\n\n"
                      "Go to AI Assistant → Settings for help.")
            return
        
        # Import and create chat dialog
        from ui.components.ai_prompt_chat import AIPromptChatDialog
        
        chat_dialog = AIPromptChatDialog(
            parent=tab_instance.frame.winfo_toplevel(),
            current_prompt=current_prompt,
            model_type=model_type,
            on_prompt_apply=lambda new_prompt: self._apply_prompt(prompt_widget, new_prompt)
        )
        chat_dialog.show()
        
    except Exception as e:
        logger.error(f"Error opening AI chat: {e}")
        from utils.warning_dialogs import show_error
        show_error("Error", f"Failed to open AI chat: {str(e)}")

def _open_filter_training_chat(self, prompt_widget, model_type: str, tab_instance):
    """Open the AI chat interface for filter training"""
    try:
        # Show warning first
        from utils.warning_dialogs import show_filter_training_warning
        
        if not show_filter_training_warning(parent=tab_instance.frame.winfo_toplevel()):
            return
        
        # Get current prompt
        current_prompt = ""
        if hasattr(prompt_widget, 'get'):
            if prompt_widget.winfo_class() == 'Text':
                current_prompt = prompt_widget.get("1.0", tk.END).strip()
            else:
                current_prompt = prompt_widget.get().strip()
        
        if not current_prompt:
            from utils.warning_dialogs import show_error
            show_error("No Prompt", "Please enter a prompt first before requesting filter training examples.")
            return
        
        if not self.ai_advisor.is_available():
            from utils.warning_dialogs import show_error
            show_error("AI Unavailable", 
                      "Please configure Claude or OpenAI API keys in your .env file.\n\n"
                      "Go to AI Assistant → Settings for help.")
            return
        
        # Import and create chat dialog in filter training mode
        from ui.components.ai_prompt_chat import AIPromptChatDialog
        
        chat_dialog = AIPromptChatDialog(
            parent=tab_instance.frame.winfo_toplevel(),
            current_prompt=current_prompt,
            model_type=model_type,
            filter_training_mode=True,
            on_pro