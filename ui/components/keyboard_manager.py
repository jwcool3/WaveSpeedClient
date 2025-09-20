"""
Universal Keyboard Manager Component
Consistent keyboard shortcuts across all WaveSpeed AI tabs
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Callable, Optional, List, Tuple
from core.logger import get_logger

logger = get_logger()


class KeyboardManager:
    """
    Universal keyboard shortcut manager providing consistent shortcuts
    across all tabs in WaveSpeed AI Creative Suite.
    """
    
    # Standard shortcuts across all tabs
    UNIVERSAL_SHORTCUTS = {
        '<Control-Return>': 'primary_action',     # Ctrl+Enter: Generate/Apply/Process
        '<Control-Key-Return>': 'primary_action', # Alternative binding
        '<Return>': 'primary_action_if_focused',  # Enter: Primary action if button focused
        '<Escape>': 'cancel_operation',           # Esc: Cancel current operation
        '<Control-r>': 'refresh_ai',              # Ctrl+R: Refresh AI features
        '<Control-s>': 'save_result',             # Ctrl+S: Save result
        '<Control-n>': 'new_operation',           # Ctrl+N: New/Clear operation
        '<Control-o>': 'open_file',               # Ctrl+O: Open/Browse file
        '<F1>': 'show_help',                      # F1: Show help/shortcuts
        '<Control-1>': 'quick_setting_1',         # Ctrl+1: Quick setting preset 1
        '<Control-2>': 'quick_setting_2',         # Ctrl+2: Quick setting preset 2  
        '<Control-3>': 'quick_setting_3',         # Ctrl+3: Quick setting preset 3
        '<Control-Tab>': 'next_tab',              # Ctrl+Tab: Switch to next tab
        '<Control-Shift-Tab>': 'prev_tab',        # Ctrl+Shift+Tab: Previous tab
        '<Alt-Left>': 'prev_tab',                 # Alt+Left: Previous tab
        '<Alt-Right>': 'next_tab',                # Alt+Right: Next tab
    }
    
    # AI-specific shortcuts
    AI_SHORTCUTS = {
        '<Control-i>': 'improve_prompt',          # Ctrl+I: Improve with AI
        '<Control-f>': 'filter_training',         # Ctrl+F: Filter training
        '<Control-h>': 'ai_chat',                 # Ctrl+H: AI chat
    }
    
    # Navigation shortcuts
    NAVIGATION_SHORTCUTS = {
        '<Tab>': 'next_widget',                   # Tab: Navigate to next widget
        '<Shift-Tab>': 'prev_widget',             # Shift+Tab: Previous widget
        '<Control-Home>': 'focus_first',          # Ctrl+Home: Focus first input
        '<Control-End>': 'focus_last',            # Ctrl+End: Focus primary action
    }
    
    def __init__(self, root_widget: tk.Widget, tab_name: str = ""):
        """
        Initialize keyboard manager for a tab
        
        Args:
            root_widget: Root widget to bind shortcuts to (usually the main tab frame)
            tab_name: Name of the tab for logging
        """
        self.root_widget = root_widget
        self.tab_name = tab_name
        
        # Action callbacks
        self.action_callbacks: Dict[str, Callable] = {}
        
        # Widget references for navigation
        self.primary_action_widget: Optional[tk.Widget] = None
        self.prompt_widgets: List[tk.Widget] = []
        self.setting_widgets: List[tk.Widget] = []
        
        # Status tracking
        self.operation_in_progress = False
        self.shortcuts_enabled = True
        
        # Setup keyboard bindings
        self.setup_bindings()
        
        logger.info(f"KeyboardManager initialized for tab: {tab_name}")
    
    def setup_bindings(self):
        """Setup all keyboard bindings"""
        # Make widget focusable for key events
        self.root_widget.focus_set()
        
        # Combine all shortcuts
        all_shortcuts = {
            **self.UNIVERSAL_SHORTCUTS,
            **self.AI_SHORTCUTS, 
            **self.NAVIGATION_SHORTCUTS
        }
        
        # Bind all shortcuts
        for key_combo, action in all_shortcuts.items():
            self.root_widget.bind(key_combo, lambda event, a=action: self._handle_shortcut(event, a))
        
        logger.info(f"Bound {len(all_shortcuts)} keyboard shortcuts")
    
    def _handle_shortcut(self, event, action: str):
        """
        Handle keyboard shortcut activation
        
        Args:
            event: Tkinter event
            action: Action name to execute
        """
        if not self.shortcuts_enabled:
            return "break"  # Prevent default handling
        
        # Get callback for action
        callback = self.action_callbacks.get(action)
        if callback:
            try:
                # Special handling for certain actions
                if action == 'cancel_operation' and self.operation_in_progress:
                    callback()
                elif action == 'primary_action' and not self.operation_in_progress:
                    callback()
                elif action == 'primary_action_if_focused':
                    # Only trigger if primary action button has focus
                    if self.primary_action_widget and self.root_widget.focus_get() == self.primary_action_widget:
                        callback()
                else:
                    callback()
                
                logger.info(f"Executed keyboard shortcut: {action}")
                return "break"  # Prevent default handling
                
            except Exception as e:
                logger.error(f"Error executing keyboard shortcut '{action}': {e}")
        else:
            # Handle built-in navigation
            if action == 'next_widget':
                self._navigate_next()
            elif action == 'prev_widget':
                self._navigate_prev()
            elif action == 'focus_first':
                self._focus_first_input()
            elif action == 'focus_last':
                self._focus_primary_action()
        
        return "break"
    
    def register_action(self, action: str, callback: Callable):
        """
        Register callback for keyboard action
        
        Args:
            action: Action name (e.g., 'primary_action', 'cancel_operation')
            callback: Function to call when shortcut is pressed
        """
        self.action_callbacks[action] = callback
        logger.debug(f"Registered keyboard action: {action}")
    
    def register_primary_action(self, callback: Callable, widget: Optional[tk.Widget] = None):
        """Register primary action (Ctrl+Enter) and optionally the button widget"""
        self.register_action('primary_action', callback)
        self.register_action('primary_action_if_focused', callback)
        if widget:
            self.primary_action_widget = widget
    
    def register_ai_actions(self, improve_callback: Callable = None, 
                          filter_callback: Callable = None, 
                          chat_callback: Callable = None):
        """Register AI-related shortcuts"""
        if improve_callback:
            self.register_action('improve_prompt', improve_callback)
        if filter_callback:
            self.register_action('filter_training', filter_callback)
        if chat_callback:
            self.register_action('ai_chat', chat_callback)
    
    def register_file_actions(self, open_callback: Callable = None,
                             save_callback: Callable = None,
                             new_callback: Callable = None):
        """Register file operation shortcuts"""
        if open_callback:
            self.register_action('open_file', open_callback)
        if save_callback:
            self.register_action('save_result', save_callback)
        if new_callback:
            self.register_action('new_operation', new_callback)
    
    def register_navigation_widgets(self, prompt_widgets: List[tk.Widget] = None,
                                   setting_widgets: List[tk.Widget] = None):
        """Register widgets for Tab navigation"""
        if prompt_widgets:
            self.prompt_widgets = prompt_widgets
        if setting_widgets:
            self.setting_widgets = setting_widgets
    
    def set_operation_in_progress(self, in_progress: bool):
        """
        Update operation status to control shortcut behavior
        
        Args:
            in_progress: True if operation is running
        """
        self.operation_in_progress = in_progress
        
        # Could disable certain shortcuts during processing
        if in_progress:
            logger.debug("Operation in progress - some shortcuts disabled")
        else:
            logger.debug("Operation complete - all shortcuts enabled")
    
    def enable_shortcuts(self, enabled: bool = True):
        """Enable or disable all keyboard shortcuts"""
        self.shortcuts_enabled = enabled
        status = "enabled" if enabled else "disabled"
        logger.info(f"Keyboard shortcuts {status}")
    
    def _navigate_next(self):
        """Navigate to next widget in tab order"""
        current_widget = self.root_widget.focus_get()
        if current_widget:
            current_widget.tk_focusNext().focus_set()
    
    def _navigate_prev(self):
        """Navigate to previous widget in tab order"""
        current_widget = self.root_widget.focus_get()
        if current_widget:
            current_widget.tk_focusPrev().focus_set()
    
    def _focus_first_input(self):
        """Focus first input widget (usually image or prompt)"""
        if self.prompt_widgets:
            self.prompt_widgets[0].focus_set()
        elif self.setting_widgets:
            self.setting_widgets[0].focus_set()
    
    def _focus_primary_action(self):
        """Focus primary action button"""
        if self.primary_action_widget:
            self.primary_action_widget.focus_set()
    
    def show_shortcuts_help(self):
        """Show keyboard shortcuts help dialog"""
        help_window = tk.Toplevel(self.root_widget)
        help_window.title(f"Keyboard Shortcuts - {self.tab_name}")
        help_window.geometry("500x400")
        help_window.transient(self.root_widget)
        help_window.grab_set()
        
        # Create help content
        help_frame = ttk.Frame(help_window, padding="10")
        help_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(help_frame, text="⌨️ Keyboard Shortcuts", 
                               font=('Arial', 12, 'bold'))
        title_label.pack(pady=(0, 10))
        
        # Create scrollable text widget
        text_frame = ttk.Frame(help_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        text_widget = tk.Text(text_frame, wrap=tk.WORD, padx=10, pady=10)
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text_widget.yview)
        text_widget.config(yscrollcommand=scrollbar.set)
        
        # Shortcuts content
        shortcuts_text = """
🚀 MAIN ACTIONS:
Ctrl+Enter    Execute primary action (Generate/Apply/Process)
Ctrl+S        Save result
Ctrl+O        Open/Browse file
Ctrl+N        New/Clear operation
Escape        Cancel current operation

🤖 AI FEATURES:
Ctrl+I        Improve prompt with AI
Ctrl+F        Filter training mode
Ctrl+H        Open AI chat
Ctrl+R        Refresh AI features

⚙️ QUICK SETTINGS:
Ctrl+1        Quick setting preset 1
Ctrl+2        Quick setting preset 2
Ctrl+3        Quick setting preset 3

🧭 NAVIGATION:
Tab           Next widget
Shift+Tab     Previous widget
Ctrl+Home     Focus first input
Ctrl+End      Focus primary action button
Ctrl+Tab      Next tab
Ctrl+Shift+Tab Previous tab
Alt+Left      Previous tab
Alt+Right     Next tab

❓ HELP:
F1            Show this help dialog
        """
        
        text_widget.insert(tk.END, shortcuts_text.strip())
        text_widget.config(state=tk.DISABLED)
        
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Close button
        close_btn = ttk.Button(help_frame, text="Close", command=help_window.destroy)
        close_btn.pack(pady=(10, 0))
        
        # Center the window
        help_window.update_idletasks()
        x = (help_window.winfo_screenwidth() // 2) - (help_window.winfo_width() // 2)
        y = (help_window.winfo_screenheight() // 2) - (help_window.winfo_height() // 2)
        help_window.geometry(f"+{x}+{y}")


# Convenience functions
def setup_keyboard_manager(root_widget: tk.Widget, tab_name: str = "") -> KeyboardManager:
    """
    Factory function to create and setup keyboard manager
    
    Args:
        root_widget: Root widget to bind shortcuts to
        tab_name: Name of the tab
        
    Returns:
        KeyboardManager instance
    """
    return KeyboardManager(root_widget, tab_name)


def bind_standard_shortcuts(keyboard_manager: KeyboardManager,
                           primary_action: Callable,
                           primary_widget: tk.Widget = None,
                           open_file: Callable = None,
                           save_result: Callable = None,
                           clear_all: Callable = None):
    """
    Helper to bind the most common shortcuts
    
    Args:
        keyboard_manager: KeyboardManager instance
        primary_action: Main action function (generate/apply/process)
        primary_widget: Primary action button widget
        open_file: File open function
        save_result: Save result function
        clear_all: Clear/new operation function
    """
    keyboard_manager.register_primary_action(primary_action, primary_widget)
    
    if open_file:
        keyboard_manager.register_action('open_file', open_file)
    if save_result:
        keyboard_manager.register_action('save_result', save_result)
    if clear_all:
        keyboard_manager.register_action('new_operation', clear_all)
    
    # Always register help
    keyboard_manager.register_action('show_help', keyboard_manager.show_shortcuts_help)