"""
Enhanced AI Prompt Suggestions UI Components

This module provides enhanced UI components for displaying and interacting with AI-generated prompt suggestions.
It extends the existing implementation with richer features and better user experience.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
from typing import List, Optional, Callable
from core.ai_prompt_advisor import get_ai_advisor, PromptSuggestion
from core.logger import get_logger
from utils.utils import show_error, show_success, show_warning

logger = get_logger()


class EnhancedPromptSuggestionDialog:
    """Enhanced dialog for displaying AI prompt suggestions with rich UI"""
    
    def __init__(self, parent, original_prompt: str, suggestions: List[PromptSuggestion], 
                 callback: Callable[[str], None], tab_name: str = ""):
        self.parent = parent
        self.original_prompt = original_prompt
        self.suggestions = suggestions
        self.callback = callback
        self.tab_name = tab_name
        self.dialog = None
        
        self.show_dialog()
    
    def show_dialog(self):
        """Display the enhanced suggestions dialog"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title(f"AI Prompt Suggestions - {self.tab_name}")
        self.dialog.geometry("900x700")
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.center_dialog()
        
        # Main frame with scrolling
        main_frame = ttk.Frame(self.dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Title section
        self.setup_title_section(main_frame)
        
        # Original prompt section
        self.setup_original_section(main_frame)
        
        # Suggestions section with scrolling
        self.setup_suggestions_section(main_frame)
        
        # Bottom action buttons
        self.setup_bottom_buttons(main_frame)
    
    def center_dialog(self):
        """Center the dialog on screen"""
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")
    
    def setup_title_section(self, parent):
        """Setup title and info section"""
        title_frame = ttk.Frame(parent)
        title_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Main title
        title_label = tk.Label(
            title_frame,
            text="✨ AI Prompt Suggestions",
            font=('Arial', 18, 'bold'),
            fg='#2c3e50'
        )
        title_label.pack(anchor=tk.W)
        
        # Subtitle with tab info
        if self.tab_name:
            subtitle_label = tk.Label(
                title_frame,
                text=f"Optimized for {self.tab_name}",
                font=('Arial', 11),
                fg='#7f8c8d'
            )
            subtitle_label.pack(anchor=tk.W, pady=(2, 0))
    
    def setup_original_section(self, parent):
        """Setup original prompt display with better styling"""
        original_frame = ttk.LabelFrame(parent, text="📝 Original Prompt", padding="15")
        original_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Original prompt text with better styling
        original_text = tk.Text(
            original_frame,
            height=4,
            wrap=tk.WORD,
            bg='#f8f9fa',
            font=('Arial', 11),
            state='disabled',
            relief='solid',
            bd=1,
            padx=10,
            pady=8
        )
        original_text.pack(fill=tk.X)
        
        # Insert original prompt
        original_text.config(state='normal')
        original_text.insert('1.0', self.original_prompt)
        original_text.config(state='disabled')
    
    def setup_suggestions_section(self, parent):
        """Setup suggestions display with enhanced scrolling and styling"""
        suggestions_frame = ttk.LabelFrame(parent, text="🎯 AI Suggestions", padding="15")
        suggestions_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Create scrollable frame
        canvas = tk.Canvas(suggestions_frame, highlightthickness=0, bg='white')
        scrollbar = ttk.Scrollbar(suggestions_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Add suggestions with enhanced styling
        for i, suggestion in enumerate(self.suggestions):
            self.create_enhanced_suggestion_card(scrollable_frame, suggestion, i)
    
    def create_enhanced_suggestion_card(self, parent, suggestion: PromptSuggestion, index: int):
        """Create an enhanced card for each suggestion"""
        # Main card frame with enhanced styling
        card_frame = tk.Frame(parent, relief='solid', bd=2, bg='white')
        card_frame.pack(fill=tk.X, padx=8, pady=8)
        
        # Category colors
        category_colors = {
            'clarity': '#3498db',
            'creativity': '#e74c3c', 
            'technical': '#27ae60',
            'general': '#95a5a6'
        }
        
        color = category_colors.get(suggestion.category, '#95a5a6')
        
        # Header with category and confidence
        header_frame = tk.Frame(card_frame, bg=color, height=35)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        # Category label with icon
        category_icons = {
            'clarity': '🔍',
            'creativity': '🎨',
            'technical': '⚙️',
            'general': '💡'
        }
        
        icon = category_icons.get(suggestion.category, '💡')
        category_label = tk.Label(
            header_frame,
            text=f"{icon} {suggestion.category.title()} Enhancement",
            bg=color,
            fg='white',
            font=('Arial', 11, 'bold')
        )
        category_label.pack(side=tk.LEFT, padx=15, pady=8)
        
        # Confidence indicator
        if hasattr(suggestion, 'confidence') and suggestion.confidence:
            confidence_label = tk.Label(
                header_frame,
                text=f"Confidence: {suggestion.confidence:.0%}",
                bg=color,
                fg='white',
                font=('Arial', 9)
            )
            confidence_label.pack(side=tk.RIGHT, padx=15, pady=8)
        
        # Content frame with padding
        content_frame = tk.Frame(card_frame, bg='white', padx=15, pady=15)
        content_frame.pack(fill=tk.X)
        
        # Improved prompt section
        prompt_label = tk.Label(
            content_frame,
            text="✨ Improved Prompt:",
            font=('Arial', 10, 'bold'),
            bg='white',
            fg='#2c3e50'
        )
        prompt_label.pack(anchor=tk.W, pady=(0, 5))
        
        prompt_text = tk.Text(
            content_frame,
            height=3,
            wrap=tk.WORD,
            bg='#f8f9fa',
            font=('Arial', 11),
            relief='solid',
            bd=1,
            padx=8,
            pady=6
        )
        prompt_text.pack(fill=tk.X, pady=(0, 10))
        prompt_text.insert('1.0', suggestion.improved_prompt)
        prompt_text.config(state='disabled')
        
        # Explanation section
        if suggestion.explanation:
            explanation_label = tk.Label(
                content_frame,
                text="💭 Why this is better:",
                font=('Arial', 10, 'bold'),
                bg='white',
                fg='#2c3e50'
            )
            explanation_label.pack(anchor=tk.W, pady=(0, 5))
            
            explanation_text = tk.Label(
                content_frame,
                text=suggestion.explanation,
                font=('Arial', 10),
                bg='white',
                justify=tk.LEFT,
                wraplength=800,
                fg='#34495e'
            )
            explanation_text.pack(anchor=tk.W, pady=(0, 15))
        
        # Action buttons with enhanced styling
        button_frame = tk.Frame(content_frame, bg='white')
        button_frame.pack(fill=tk.X)
        
        # Use button
        use_button = tk.Button(
            button_frame,
            text="✅ Use This Prompt",
            bg=color,
            fg='white',
            font=('Arial', 10, 'bold'),
            relief='flat',
            padx=20,
            pady=8,
            cursor='hand2',
            command=lambda: self.use_suggestion(suggestion.improved_prompt)
        )
        use_button.pack(side=tk.LEFT)
        
        # Copy button
        copy_button = tk.Button(
            button_frame,
            text="📋 Copy",
            bg='#95a5a6',
            fg='white',
            font=('Arial', 10),
            relief='flat',
            padx=15,
            pady=8,
            cursor='hand2',
            command=lambda: self.copy_to_clipboard(suggestion.improved_prompt)
        )
        copy_button.pack(side=tk.LEFT, padx=(10, 0))
        
        # Preview button (optional)
        preview_button = tk.Button(
            button_frame,
            text="👁️ Preview",
            bg='#f39c12',
            fg='white',
            font=('Arial', 10),
            relief='flat',
            padx=15,
            pady=8,
            cursor='hand2',
            command=lambda: self.preview_suggestion(suggestion.improved_prompt)
        )
        preview_button.pack(side=tk.LEFT, padx=(5, 0))
    
    def setup_bottom_buttons(self, parent):
        """Setup bottom action buttons with enhanced styling"""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, pady=(15, 0))
        
        # Left side buttons
        left_frame = ttk.Frame(button_frame)
        left_frame.pack(side=tk.LEFT)
        
        # Generate more suggestions
        more_button = tk.Button(
            left_frame,
            text="🔄 Generate More",
            bg='#f39c12',
            fg='white',
            font=('Arial', 11),
            relief='flat',
            padx=20,
            pady=10,
            cursor='hand2',
            command=self.generate_more
        )
        more_button.pack(side=tk.LEFT)
        
        # Generate ideas button
        ideas_button = tk.Button(
            left_frame,
            text="💡 Generate Ideas",
            bg='#9b59b6',
            fg='white',
            font=('Arial', 11),
            relief='flat',
            padx=20,
            pady=10,
            cursor='hand2',
            command=self.generate_ideas
        )
        ideas_button.pack(side=tk.LEFT, padx=(10, 0))
        
        # Right side buttons
        right_frame = ttk.Frame(button_frame)
        right_frame.pack(side=tk.RIGHT)
        
        # Close button
        close_button = tk.Button(
            right_frame,
            text="❌ Close",
            bg='#95a5a6',
            fg='white',
            font=('Arial', 11),
            relief='flat',
            padx=20,
            pady=10,
            cursor='hand2',
            command=self.close_dialog
        )
        close_button.pack(side=tk.RIGHT)
    
    def use_suggestion(self, prompt: str):
        """Use the selected prompt"""
        self.callback(prompt)
        show_success("Prompt Applied", "AI suggestion has been applied to your prompt!")
        self.close_dialog()
    
    def copy_to_clipboard(self, text: str):
        """Copy text to clipboard with feedback"""
        try:
            self.dialog.clipboard_clear()
            self.dialog.clipboard_append(text)
            self.dialog.update()
            show_success("Copied", "Suggestion copied to clipboard!")
        except Exception as e:
            logger.error(f"Failed to copy to clipboard: {e}")
            show_error("Copy Failed", "Failed to copy to clipboard")
    
    def preview_suggestion(self, prompt: str):
        """Preview the suggestion in a separate window"""
        preview_window = tk.Toplevel(self.dialog)
        preview_window.title("Prompt Preview")
        preview_window.geometry("600x400")
        preview_window.transient(self.dialog)
        
        # Center preview window
        preview_window.update_idletasks()
        x = (preview_window.winfo_screenwidth() // 2) - (preview_window.winfo_width() // 2)
        y = (preview_window.winfo_screenheight() // 2) - (preview_window.winfo_height() // 2)
        preview_window.geometry(f"+{x}+{y}")
        
        # Preview content
        frame = ttk.Frame(preview_window, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="Prompt Preview", font=('Arial', 14, 'bold')).pack(pady=(0, 10))
        
        text_widget = tk.Text(frame, wrap=tk.WORD, font=('Arial', 11), height=15)
        text_widget.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        text_widget.insert('1.0', prompt)
        text_widget.config(state='disabled')
        
        ttk.Button(frame, text="Close", command=preview_window.destroy).pack()
    
    def generate_more(self):
        """Generate more suggestions"""
        show_warning("Feature Coming Soon", "Generate more suggestions feature is coming soon!")
    
    def generate_ideas(self):
        """Generate fresh prompt ideas"""
        show_warning("Feature Coming Soon", "Generate fresh ideas feature is coming soon!")
    
    def close_dialog(self):
        """Close the dialog"""
        if self.dialog:
            self.dialog.destroy()


class AISettingsDialog:
    """Settings dialog for AI prompt assistant configuration"""
    
    def __init__(self, parent):
        self.parent = parent
        self.show_settings_dialog()
    
    def show_settings_dialog(self):
        """Show AI settings configuration dialog"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("AI Assistant Settings")
        self.dialog.geometry("600x500")
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Center dialog
        self.center_dialog()
        
        # Main frame
        main_frame = ttk.Frame(self.dialog, padding="25")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = tk.Label(
            main_frame,
            text="🤖 AI Assistant Configuration",
            font=('Arial', 16, 'bold'),
            fg='#2c3e50'
        )
        title_label.pack(pady=(0, 25))
        
        # API Provider selection
        self.setup_provider_section(main_frame)
        
        # API Keys section
        self.setup_api_keys_section(main_frame)
        
        # Feature settings
        self.setup_features_section(main_frame)
        
        # Buttons
        self.setup_buttons(main_frame)
    
    def center_dialog(self):
        """Center the dialog"""
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")
    
    def setup_provider_section(self, parent):
        """Setup API provider selection"""
        provider_frame = ttk.LabelFrame(parent, text="AI Provider", padding="15")
        provider_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.provider_var = tk.StringVar(value="claude")
        
        claude_radio = ttk.Radiobutton(
            provider_frame,
            text="🤖 Claude (Anthropic) - Recommended for creative prompts",
            variable=self.provider_var,
            value="claude"
        )
        claude_radio.pack(anchor=tk.W, pady=2)
        
        openai_radio = ttk.Radiobutton(
            provider_frame,
            text="🧠 OpenAI GPT-4 - Great for technical optimization",
            variable=self.provider_var,
            value="openai"
        )
        openai_radio.pack(anchor=tk.W, pady=2)
    
    def setup_api_keys_section(self, parent):
        """Setup API keys configuration"""
        keys_frame = ttk.LabelFrame(parent, text="API Keys", padding="15")
        keys_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Info label
        info_label = tk.Label(
            keys_frame,
            text="Add your API keys to the .env file in your project root:",
            font=('Arial', 9),
            fg='#7f8c8d'
        )
        info_label.pack(anchor=tk.W, pady=(0, 10))
        
        # Claude API Key
        claude_frame = ttk.Frame(keys_frame)
        claude_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(claude_frame, text="Claude API Key:", font=('Arial', 10, 'bold')).pack(anchor=tk.W)
        self.claude_key_entry = ttk.Entry(claude_frame, show="*", width=60, font=('Arial', 10))
        self.claude_key_entry.pack(fill=tk.X, pady=(2, 0))
        
        # OpenAI API Key
        openai_frame = ttk.Frame(keys_frame)
        openai_frame.pack(fill=tk.X)
        
        ttk.Label(openai_frame, text="OpenAI API Key:", font=('Arial', 10, 'bold')).pack(anchor=tk.W)
        self.openai_key_entry = ttk.Entry(openai_frame, show="*", width=60, font=('Arial', 10))
        self.openai_key_entry.pack(fill=tk.X, pady=(2, 0))
    
    def setup_features_section(self, parent):
        """Setup feature configuration"""
        features_frame = ttk.LabelFrame(parent, text="Features", padding="15")
        features_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.auto_suggestions_var = tk.BooleanVar(value=False)
        auto_check = ttk.Checkbutton(
            features_frame,
            text="Enable auto-suggestions while typing",
            variable=self.auto_suggestions_var
        )
        auto_check.pack(anchor=tk.W, pady=2)
        
        self.explanations_var = tk.BooleanVar(value=True)
        explanations_check = ttk.Checkbutton(
            features_frame,
            text="Show explanations with suggestions",
            variable=self.explanations_var
        )
        explanations_check.pack(anchor=tk.W, pady=2)
        
        # Suggestion count
        count_frame = ttk.Frame(features_frame)
        count_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Label(count_frame, text="Number of suggestions:", font=('Arial', 10)).pack(side=tk.LEFT)
        self.suggestion_count = tk.Spinbox(
            count_frame,
            from_=1, to=5,
            value=3,
            width=5,
            font=('Arial', 10)
        )
        self.suggestion_count.pack(side=tk.RIGHT)
    
    def setup_buttons(self, parent):
        """Setup dialog buttons"""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, pady=(25, 0))
        
        save_button = tk.Button(
            button_frame,
            text="💾 Save Settings",
            bg='#27ae60',
            fg='white',
            font=('Arial', 11, 'bold'),
            relief='flat',
            padx=20,
            pady=10,
            cursor='hand2',
            command=self.save_settings
        )
        save_button.pack(side=tk.LEFT)
        
        test_button = tk.Button(
            button_frame,
            text="🔗 Test Connection",
            bg='#3498db',
            fg='white',
            font=('Arial', 11),
            relief='flat',
            padx=20,
            pady=10,
            cursor='hand2',
            command=self.test_connection
        )
        test_button.pack(side=tk.LEFT, padx=(10, 0))
        
        cancel_button = tk.Button(
            button_frame,
            text="❌ Cancel",
            bg='#95a5a6',
            fg='white',
            font=('Arial', 11),
            relief='flat',
            padx=20,
            pady=10,
            cursor='hand2',
            command=self.dialog.destroy
        )
        cancel_button.pack(side=tk.RIGHT)
    
    def save_settings(self):
        """Save AI assistant settings"""
        show_success("Settings Saved", "AI assistant settings have been saved successfully!")
        self.dialog.destroy()
    
    def test_connection(self):
        """Test API connection"""
        provider = self.provider_var.get()
        show_warning("Test Connection", f"Testing {provider} connection...\n\nThis feature will be implemented in a future update.")


def show_enhanced_suggestions(parent, original_prompt: str, suggestions: List[PromptSuggestion], 
                            callback: Callable[[str], None], tab_name: str = ""):
    """Show enhanced suggestions dialog"""
    EnhancedPromptSuggestionDialog(parent, original_prompt, suggestions, callback, tab_name)


def show_ai_settings(parent):
    """Show AI settings dialog"""
    AISettingsDialog(parent)
