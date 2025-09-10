"""
Enhanced Tab Manager for WaveSpeed AI Application

Adds keyboard shortcuts, tooltips, processing indicators, and context menus to tabs.
"""

import tkinter as tk
from tkinter import ttk
from core.logger import get_logger

logger = get_logger()


class EnhancedTabManager:
    """Enhanced tab management with shortcuts, tooltips, and visual indicators"""
    
    def __init__(self, notebook, main_app):
        self.notebook = notebook
        self.main_app = main_app
        self.processing_indicators = {}
        self.tab_tooltips = {}
        
        # Tab descriptions for tooltips
        self.tab_descriptions = {
            0: "🍌 Nano Banana Editor\nGoogle's advanced image editing AI\nBest for: Creative edits, style changes",
            1: "✨ SeedEdit V3\nByteDance precision image editing\nBest for: Fine-tuned modifications",
            2: "🌟 Seedream V4\nState-of-the-art multi-modal editing\nBest for: Complex transformations, high-quality results",
            3: "🔍 Image Upscaler\nEnhance resolution up to 8K\nBest for: Quality enhancement, detail restoration",
            4: "🎬 Wan 2.2\nImage to video generation\nBest for: Creating short videos from images",
            5: "🕺 SeedDance Pro\nAdvanced video generation (480p/720p)\nBest for: High-quality video content"
        }
        
        self.setup_enhancements()
    
    def setup_enhancements(self):
        """Setup all tab enhancements"""
        self.setup_keyboard_shortcuts()
        self.setup_tab_tooltips()
        self.setup_tab_context_menus()
        self.setup_processing_indicators()
    
    def setup_keyboard_shortcuts(self):
        """Setup keyboard shortcuts for tab navigation"""
        root = self.main_app.root
        
        # Ctrl+1 through Ctrl+6 for direct tab access
        for i in range(6):
            root.bind(f'<Control-Key-{i+1}>', lambda e, tab=i: self.switch_to_tab(tab))
        
        # Ctrl+Tab for next tab
        root.bind('<Control-Tab>', self.next_tab)
        
        # Ctrl+Shift+Tab for previous tab
        root.bind('<Control-Shift-Tab>', self.previous_tab)
        
        # Add to help menu or show in status
        self.show_shortcuts_hint()
    
    def setup_tab_tooltips(self):
        """Setup informative tooltips for each tab"""
        # Note: tkinter doesn't have built-in tab tooltips, so we'll create custom ones
        self.notebook.bind('<Motion>', self.on_tab_hover)
        self.notebook.bind('<Leave>', self.hide_tooltip)
        
        # Create tooltip window (initially hidden)
        self.tooltip = tk.Toplevel(self.main_app.root)
        self.tooltip.withdraw()
        self.tooltip.overrideredirect(True)
        self.tooltip.configure(bg='#ffffe0', relief='solid', bd=1)
        
        self.tooltip_label = tk.Label(
            self.tooltip,
            bg='#ffffe0',
            fg='black',
            font=('Arial', 9),
            justify=tk.LEFT,
            padx=5,
            pady=3
        )
        self.tooltip_label.pack()
    
    def setup_tab_context_menus(self):
        """Setup right-click context menus for tabs"""
        self.notebook.bind('<Button-3>', self.show_tab_context_menu)
        self.notebook.bind('<Control-Button-1>', self.show_tab_context_menu)  # Mac support
    
    def setup_processing_indicators(self):
        """Setup visual indicators for processing status"""
        # We'll modify tab text to include status indicators
        pass
    
    def on_tab_hover(self, event):
        """Handle mouse hover over tabs"""
        try:
            # Get tab index under mouse
            tab_index = self.notebook.index(f'@{event.x},{event.y}')
            
            if tab_index in self.tab_descriptions:
                # Show tooltip
                self.show_tooltip(event, self.tab_descriptions[tab_index])
        except tk.TclError:
            # Mouse not over a tab
            self.hide_tooltip()
    
    def show_tooltip(self, event, text):
        """Show tooltip at mouse position"""
        self.tooltip_label.config(text=text)
        
        # Position tooltip near mouse
        x = event.x_root + 10
        y = event.y_root + 10
        
        # Adjust if tooltip would go off screen
        self.tooltip.update_idletasks()
        tooltip_width = self.tooltip.winfo_reqwidth()
        tooltip_height = self.tooltip.winfo_reqheight()
        screen_width = self.tooltip.winfo_screenwidth()
        screen_height = self.tooltip.winfo_screenheight()
        
        if x + tooltip_width > screen_width:
            x = event.x_root - tooltip_width - 10
        if y + tooltip_height > screen_height:
            y = event.y_root - tooltip_height - 10
        
        self.tooltip.geometry(f'+{x}+{y}')
        self.tooltip.deiconify()
    
    def hide_tooltip(self, event=None):
        """Hide tooltip"""
        if self.tooltip:
            self.tooltip.withdraw()
    
    def show_tab_context_menu(self, event):
        """Show context menu for tab"""
        try:
            # Get tab index under mouse
            tab_index = self.notebook.index(f'@{event.x},{event.y}')
            
            # Create context menu
            context_menu = tk.Menu(self.main_app.root, tearoff=0)
            
            # Get current tab name
            tab_text = self.notebook.tab(tab_index, 'text')
            
            context_menu.add_command(
                label=f"📍 Go to {tab_text}",
                command=lambda: self.switch_to_tab(tab_index)
            )
            
            context_menu.add_separator()
            
            # Add "Send Current Result To..." if there's a result
            if hasattr(self.main_app, 'get_current_result') and self.main_app.get_current_result():
                send_menu = tk.Menu(context_menu, tearoff=0)
                
                # Add options for other tabs
                for i, desc in self.tab_descriptions.items():
                    if i != tab_index:
                        tab_name = desc.split('\n')[0]
                        send_menu.add_command(
                            label=tab_name,
                            command=lambda target=i: self.send_result_to_tab(target)
                        )
                
                context_menu.add_cascade(label="📤 Send Result To", menu=send_menu)
                context_menu.add_separator()
            
            # Processing controls
            context_menu.add_command(
                label="⏸️ Pause Processing",
                command=lambda: self.pause_tab_processing(tab_index)
            )
            
            context_menu.add_command(
                label="🔄 Refresh Tab",
                command=lambda: self.refresh_tab(tab_index)
            )
            
            # Show menu
            context_menu.post(event.x_root, event.y_root)
            
        except (tk.TclError, IndexError):
            # Not over a tab or error occurred
            pass
    
    def switch_to_tab(self, tab_index):
        """Switch to specified tab"""
        try:
            if 0 <= tab_index < self.notebook.index('end'):
                self.notebook.select(tab_index)
                logger.info(f"Switched to tab {tab_index}")
        except tk.TclError:
            pass
    
    def next_tab(self, event=None):
        """Switch to next tab"""
        try:
            current = self.notebook.index(self.notebook.select())
            total_tabs = self.notebook.index('end')
            next_tab = (current + 1) % total_tabs
            self.switch_to_tab(next_tab)
        except tk.TclError:
            pass
    
    def previous_tab(self, event=None):
        """Switch to previous tab"""
        try:
            current = self.notebook.index(self.notebook.select())
            total_tabs = self.notebook.index('end')
            prev_tab = (current - 1) % total_tabs
            self.switch_to_tab(prev_tab)
        except tk.TclError:
            pass
    
    def set_tab_processing(self, tab_index, is_processing):
        """Set processing indicator for tab"""
        try:
            current_text = self.notebook.tab(tab_index, 'text')
            
            # Remove existing indicators
            clean_text = current_text.replace(' 🟡', '').replace(' ✅', '').replace(' ❌', '')
            
            if is_processing:
                new_text = clean_text + ' 🟡'  # Yellow dot for processing
            else:
                new_text = clean_text
            
            self.notebook.tab(tab_index, text=new_text)
            self.processing_indicators[tab_index] = is_processing
            
        except tk.TclError:
            pass
    
    def set_tab_success(self, tab_index):
        """Set success indicator for tab"""
        try:
            current_text = self.notebook.tab(tab_index, 'text')
            clean_text = current_text.replace(' 🟡', '').replace(' ✅', '').replace(' ❌', '')
            new_text = clean_text + ' ✅'  # Green checkmark
            
            self.notebook.tab(tab_index, text=new_text)
            
            # Remove after 3 seconds
            self.main_app.root.after(3000, lambda: self.clear_tab_indicator(tab_index))
            
        except tk.TclError:
            pass
    
    def set_tab_error(self, tab_index):
        """Set error indicator for tab"""
        try:
            current_text = self.notebook.tab(tab_index, 'text')
            clean_text = current_text.replace(' 🟡', '').replace(' ✅', '').replace(' ❌', '')
            new_text = clean_text + ' ❌'  # Red X
            
            self.notebook.tab(tab_index, text=new_text)
            
            # Remove after 5 seconds
            self.main_app.root.after(5000, lambda: self.clear_tab_indicator(tab_index))
            
        except tk.TclError:
            pass
    
    def clear_tab_indicator(self, tab_index):
        """Clear status indicator from tab"""
        try:
            current_text = self.notebook.tab(tab_index, 'text')
            clean_text = current_text.replace(' 🟡', '').replace(' ✅', '').replace(' ❌', '')
            self.notebook.tab(tab_index, text=clean_text)
            
            if tab_index in self.processing_indicators:
                del self.processing_indicators[tab_index]
                
        except tk.TclError:
            pass
    
    def send_result_to_tab(self, target_tab_index):
        """Send current result to target tab"""
        try:
            # This would integrate with existing cross-tab functionality
            current_tab_index = self.notebook.index(self.notebook.select())
            logger.info(f"Sending result from tab {current_tab_index} to tab {target_tab_index}")
            
            # Switch to target tab
            self.switch_to_tab(target_tab_index)
            
            # The actual result transfer would be handled by existing cross-tab system
            
        except Exception as e:
            logger.error(f"Error sending result to tab: {e}")
    
    def pause_tab_processing(self, tab_index):
        """Pause processing for specific tab (placeholder)"""
        logger.info(f"Pause processing requested for tab {tab_index}")
        # This would integrate with actual processing management
    
    def refresh_tab(self, tab_index):
        """Refresh/reset specific tab (placeholder)"""
        logger.info(f"Refresh requested for tab {tab_index}")
        # This would reset the tab to initial state
    
    def show_shortcuts_hint(self):
        """Show keyboard shortcuts hint in status or help"""
        shortcuts_text = (
            "Keyboard Shortcuts: "
            "Ctrl+1-6 (Switch Tabs) | "
            "Ctrl+Tab (Next) | "
            "Ctrl+Shift+Tab (Previous)"
        )
        
        # This could be shown in a status bar or help tooltip
        logger.info(f"Keyboard shortcuts available: {shortcuts_text}")
    
    def get_shortcuts_help(self):
        """Return help text for keyboard shortcuts"""
        return """Keyboard Shortcuts:
        
Tab Navigation:
• Ctrl+1 through Ctrl+6 - Switch directly to specific tabs
• Ctrl+Tab - Next tab
• Ctrl+Shift+Tab - Previous tab

Tab Features:
• Hover over tabs for detailed descriptions
• Right-click tabs for context menu
• Status indicators show processing state

Processing Indicators:
• 🟡 Currently processing
• ✅ Successfully completed
• ❌ Error occurred"""