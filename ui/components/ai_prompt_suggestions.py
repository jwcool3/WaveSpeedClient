"""
AI Prompt Suggestions UI Components

This module provides UI components for displaying and interacting with AI-generated prompt suggestions.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import asyncio
import threading
from typing import List, Optional, Callable
from core.ai_prompt_advisor import get_ai_advisor, PromptSuggestion
from core.logger import get_logger
from utils.utils import show_error, show_success

# Try to import enhanced components
try:
    from ui.components.enhanced_ai_suggestions import show_enhanced_suggestions, show_ai_settings
    ENHANCED_AVAILABLE = True
except ImportError:
    ENHANCED_AVAILABLE = False

logger = get_logger()


class PromptSuggestionPanel:
    """Panel for displaying AI prompt suggestions"""
    
    def __init__(self, parent, on_suggestion_selected: Optional[Callable] = None):
        self.parent = parent
        self.on_suggestion_selected = on_suggestion_selected
        self.suggestions = []
        self.current_tab_name = ""
        self.current_prompt = ""
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the suggestion panel UI"""
        # Main container
        self.container = ttk.Frame(self.parent)
        
        # Header
        header_frame = ttk.Frame(self.container)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(header_frame, text="✨ AI Prompt Suggestions", 
                 font=('Arial', 12, 'bold')).pack(side=tk.LEFT)
        
        # Close button
        close_btn = ttk.Button(header_frame, text="✕", width=3,
                              command=self.hide_panel)
        close_btn.pack(side=tk.RIGHT)
        
        # Suggestions container
        self.suggestions_frame = ttk.Frame(self.container)
        self.suggestions_frame.pack(fill=tk.BOTH, expand=True)
        
        # Loading indicator
        self.loading_label = ttk.Label(self.container, text="🤖 Generating suggestions...", 
                                      font=('Arial', 10), foreground="blue")
        
        # Error label
        self.error_label = ttk.Label(self.container, text="", 
                                    font=('Arial', 10), foreground="red")
    
    def show_panel(self, current_prompt: str, tab_name: str, filter_training: bool = False):
        """Show the suggestion panel with current prompt"""
        self.current_prompt = current_prompt
        self.current_tab_name = tab_name
        self.filter_training = filter_training
        
        # Clear previous suggestions
        for widget in self.suggestions_frame.winfo_children():
            widget.destroy()
        
        # Show loading
        self.loading_label.pack(pady=20)
        self.error_label.pack_forget()
        
        # Show container
        self.container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Generate suggestions in background
        self.generate_suggestions_async()
    
    def hide_panel(self):
        """Hide the suggestion panel"""
        self.container.pack_forget()
    
    def generate_suggestions_async(self):
        """Generate suggestions asynchronously"""
        def run_async():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                if self.filter_training:
                    suggestions = loop.run_until_complete(
                        get_ai_advisor().generate_filter_training_data(
                            self.current_prompt, 
                            self.current_tab_name
                        )
                    )
                else:
                    suggestions = loop.run_until_complete(
                        get_ai_advisor().improve_prompt(
                            self.current_prompt, 
                            self.current_tab_name
                        )
                    )
                # Update UI in main thread
                self.parent.after(0, lambda: self.display_suggestions(suggestions))
            except Exception as e:
                logger.error(f"Error generating suggestions: {e}")
                self.parent.after(0, lambda: self.show_error("Failed to generate suggestions"))
            finally:
                loop.close()
        
        thread = threading.Thread(target=run_async, daemon=True)
        thread.start()
    
    def display_suggestions(self, suggestions: List[PromptSuggestion]):
        """Display the generated suggestions"""
        self.suggestions = suggestions
        
        # Hide loading
        self.loading_label.pack_forget()
        
        if not suggestions:
            self.show_error("No suggestions available. Check your API configuration.")
            return
        
        # Use enhanced dialog if available
        if ENHANCED_AVAILABLE:
            def apply_suggestion(improved_prompt: str):
                if self.on_suggestion_selected:
                    self.on_suggestion_selected(improved_prompt)
                self.hide_panel()
            
            show_enhanced_suggestions(
                self.parent, 
                self.current_prompt, 
                suggestions, 
                apply_suggestion, 
                self.current_tab_name
            )
            self.hide_panel()  # Hide the simple panel
            return
        
        # Fallback to simple display
        for i, suggestion in enumerate(suggestions):
            self.create_suggestion_widget(suggestion, i)
    
    def create_suggestion_widget(self, suggestion: PromptSuggestion, index: int):
        """Create a widget for a single suggestion"""
        # Suggestion frame
        suggestion_frame = ttk.LabelFrame(
            self.suggestions_frame, 
            text=f"Option {index + 1}: {suggestion.category.title()}", 
            padding="10"
        )
        suggestion_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Improved prompt
        prompt_frame = ttk.Frame(suggestion_frame)
        prompt_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(prompt_frame, text="Improved Prompt:", 
                 font=('Arial', 9, 'bold')).pack(anchor=tk.W)
        
        prompt_text = tk.Text(prompt_frame, height=3, wrap=tk.WORD, 
                             font=('Arial', 10), state=tk.DISABLED)
        prompt_text.pack(fill=tk.X, pady=(2, 0))
        
        # Insert text
        prompt_text.config(state=tk.NORMAL)
        prompt_text.insert("1.0", suggestion.improved_prompt)
        prompt_text.config(state=tk.DISABLED)
        
        # Explanation
        if suggestion.explanation:
            explanation_frame = ttk.Frame(suggestion_frame)
            explanation_frame.pack(fill=tk.X, pady=(5, 0))
            
            ttk.Label(explanation_frame, text="Why this is better:", 
                     font=('Arial', 9, 'bold')).pack(anchor=tk.W)
            
            explanation_text = tk.Text(explanation_frame, height=2, wrap=tk.WORD, 
                                     font=('Arial', 9), state=tk.DISABLED,
                                     foreground="gray")
            explanation_text.pack(fill=tk.X, pady=(2, 0))
            
            explanation_text.config(state=tk.NORMAL)
            explanation_text.insert("1.0", suggestion.explanation)
            explanation_text.config(state=tk.DISABLED)
        
        # Action buttons
        button_frame = ttk.Frame(suggestion_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        use_btn = ttk.Button(button_frame, text="Use This Prompt",
                            command=lambda: self.use_suggestion(suggestion))
        use_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        copy_btn = ttk.Button(button_frame, text="Copy",
                             command=lambda: self.copy_suggestion(suggestion))
        copy_btn.pack(side=tk.LEFT)
    
    def use_suggestion(self, suggestion: PromptSuggestion):
        """Use the selected suggestion"""
        if self.on_suggestion_selected:
            self.on_suggestion_selected(suggestion.improved_prompt)
        self.hide_panel()
        show_success("Prompt Updated", "AI suggestion applied to your prompt!")
    
    def copy_suggestion(self, suggestion: PromptSuggestion):
        """Copy suggestion to clipboard"""
        self.parent.clipboard_clear()
        self.parent.clipboard_append(suggestion.improved_prompt)
        show_success("Copied", "Suggestion copied to clipboard!")
    
    def show_error(self, message: str):
        """Show error message"""
        self.loading_label.pack_forget()
        self.error_label.config(text=f"❌ {message}")
        self.error_label.pack(pady=20)


class AIImproveButton:
    """AI Improve button component"""
    
    def __init__(self, parent, prompt_text_widget, tab_name: str, 
                 on_suggestion_selected: Optional[Callable] = None):
        self.parent = parent
        self.prompt_text_widget = prompt_text_widget
        self.tab_name = tab_name
        self.on_suggestion_selected = on_suggestion_selected
        self.suggestion_panel = None
        
        self.setup_button()
    
    def setup_button(self):
        """Setup the AI improve button"""
        self.button = ttk.Button(
            self.parent,
            text="✨ Improve with AI",
            command=self.show_suggestions,
            state=tk.NORMAL if get_ai_advisor().is_available() else tk.DISABLED
        )
        
        # Add filter training button (for safety research only)
        self.filter_training_button = ttk.Button(
            self.parent,
            text="🛡️ Filter Training",
            command=self.show_filter_training,
            state=tk.NORMAL if get_ai_advisor().is_available() else tk.DISABLED
        )
        
        # Add tooltip
        self.create_tooltip()
    
    def create_tooltip(self):
        """Create tooltip for the button"""
        def show_tooltip(event):
            if not get_ai_advisor().is_available():
                tooltip = tk.Toplevel()
                tooltip.wm_overrideredirect(True)
                tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
                
                label = ttk.Label(tooltip, text="AI Advisor not available.\nAdd API keys in .env file.", 
                                 background="lightyellow", relief="solid", borderwidth=1)
                label.pack()
                
                def hide_tooltip():
                    tooltip.destroy()
                
                tooltip.after(3000, hide_tooltip)
        
        self.button.bind("<Enter>", show_tooltip)
    
    def show_suggestions(self):
        """Show AI suggestions for current prompt"""
        current_prompt = self.prompt_text_widget.get("1.0", tk.END).strip()
        
        if not current_prompt:
            show_error("No Prompt", "Please enter a prompt first before requesting AI suggestions.")
            return
        
        if not get_ai_advisor().is_available():
            show_error("AI Advisor Unavailable", 
                      "Please configure Claude or OpenAI API keys in your .env file.")
            return
        
        # Create suggestion panel if it doesn't exist
        if self.suggestion_panel is None:
            self.suggestion_panel = PromptSuggestionPanel(
                self.parent.master,  # Use parent's master for proper positioning
                on_suggestion_selected=self.on_suggestion_selected
            )
        
        # Show suggestions
        self.suggestion_panel.show_panel(current_prompt, self.tab_name)
    
    def show_filter_training(self):
        """Show filter training suggestions (for safety research only)"""
        current_prompt = self.prompt_text_widget.get("1.0", tk.END).strip()
        
        if not current_prompt:
            show_error("No Prompt", "Please enter a prompt first before requesting filter training data.")
            return
        
        if not get_ai_advisor().is_available():
            show_error("AI Advisor Unavailable", 
                      "Please configure Claude or OpenAI API keys in your .env file.")
            return
        
        # Show warning dialog
        from tkinter import messagebox
        result = messagebox.askyesno(
            "Filter Training Mode",
            "⚠️ WARNING: Filter Training Mode generates harmful prompt examples for safety filter development only.\n\n"
            "These examples are NEVER executed for generation - they are used to train safety filters.\n\n"
            "Do you want to continue?",
            icon="warning"
        )
        
        if not result:
            return
        
        # Create suggestion panel if it doesn't exist
        if self.suggestion_panel is None:
            self.suggestion_panel = PromptSuggestionPanel(
                self.parent.master,  # Use parent's master for proper positioning
                on_suggestion_selected=self.on_suggestion_selected
            )
        
        # Show filter training suggestions
        self.suggestion_panel.show_panel(current_prompt, self.tab_name, filter_training=True)
    
    def update_availability(self):
        """Update button state based on AI advisor availability"""
        self.button.config(state=tk.NORMAL if get_ai_advisor().is_available() else tk.DISABLED)
        self.filter_training_button.config(state=tk.NORMAL if get_ai_advisor().is_available() else tk.DISABLED)


class PromptContextMenu:
    """Right-click context menu for prompt text widgets"""
    
    def __init__(self, prompt_text_widget, tab_name: str, 
                 on_suggestion_selected: Optional[Callable] = None):
        self.prompt_text_widget = prompt_text_widget
        self.tab_name = tab_name
        self.on_suggestion_selected = on_suggestion_selected
        
        self.setup_context_menu()
    
    def setup_context_menu(self):
        """Setup right-click context menu"""
        self.context_menu = tk.Menu(self.prompt_text_widget, tearoff=0)
        
        # Add AI improve option
        self.context_menu.add_command(
            label="✨ Improve with AI",
            command=self.show_ai_suggestions
        )
        
        self.context_menu.add_separator()
        
        # Standard text operations
        self.context_menu.add_command(label="Cut", command=self.cut_text)
        self.context_menu.add_command(label="Copy", command=self.copy_text)
        self.context_menu.add_command(label="Paste", command=self.paste_text)
        
        # Bind right-click
        self.prompt_text_widget.bind("<Button-3>", self.show_context_menu)
    
    def show_context_menu(self, event):
        """Show context menu at cursor position"""
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()
    
    def show_ai_suggestions(self):
        """Show AI suggestions"""
        current_prompt = self.prompt_text_widget.get("1.0", tk.END).strip()
        
        if not current_prompt:
            show_error("No Prompt", "Please enter a prompt first.")
            return
        
        if not get_ai_advisor().is_available():
            show_error("AI Advisor Unavailable", 
                      "Please configure API keys in your .env file.")
            return
        
        # Create and show suggestion panel
        suggestion_panel = PromptSuggestionPanel(
            self.prompt_text_widget.master,
            on_suggestion_selected=self.on_suggestion_selected
        )
        suggestion_panel.show_panel(current_prompt, self.tab_name)
    
    def cut_text(self):
        """Cut selected text"""
        try:
            self.prompt_text_widget.event_generate("<<Cut>>")
        except:
            pass
    
    def copy_text(self):
        """Copy selected text"""
        try:
            self.prompt_text_widget.event_generate("<<Copy>>")
        except:
            pass
    
    def paste_text(self):
        """Paste text"""
        try:
            self.prompt_text_widget.event_generate("<<Paste>>")
        except:
            pass


def add_ai_features_to_prompt_section(prompt_frame, prompt_text_widget, tab_name: str, 
                                    on_suggestion_selected: Optional[Callable] = None):
    """Add AI features to an existing prompt section"""
    
    # Add AI improve button to prompt actions
    prompt_actions = None
    for child in prompt_frame.winfo_children():
        if isinstance(child, ttk.Frame):
            # Look for frame with buttons (prompt actions)
            for grandchild in child.winfo_children():
                if isinstance(grandchild, ttk.Button):
                    prompt_actions = child
                    break
            if prompt_actions:
                break
    
    if prompt_actions:
        # Add AI improve button
        ai_button = AIImproveButton(
            prompt_actions, 
            prompt_text_widget, 
            tab_name,
            on_suggestion_selected
        )
        
        # Check which geometry manager is being used in the prompt_actions frame
        # by looking at existing children
        uses_grid = False
        for child in prompt_actions.winfo_children():
            try:
                # Try to get grid info - if it exists, the frame uses grid
                grid_info = child.grid_info()
                if grid_info:
                    uses_grid = True
                    break
            except:
                pass
        
        if uses_grid:
            # Use grid for consistency
            ai_button.button.grid(row=0, column=2, sticky=(tk.W, tk.E), padx=(5, 0))
            ai_button.filter_training_button.grid(row=0, column=3, sticky=(tk.W, tk.E), padx=(5, 0))
        else:
            # Use pack for consistency
            ai_button.button.pack(side=tk.LEFT, padx=(5, 0))
            ai_button.filter_training_button.pack(side=tk.LEFT, padx=(5, 0))
    
    # Add context menu to prompt text widget
    PromptContextMenu(prompt_text_widget, tab_name, on_suggestion_selected)
    
    return ai_button if prompt_actions else None
