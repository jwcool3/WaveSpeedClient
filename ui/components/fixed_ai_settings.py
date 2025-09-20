"""
Fixed AI Assistant Settings and Integration
For WaveSpeed AI Creative Suite

This fixes the AI assistant configuration and integration issues.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import os
from typing import Optional, Dict, Any
from core.logger import get_logger

logger = get_logger()

class AIAssistantManager:
    """Manages AI assistant configuration and status"""
    
    def __init__(self):
        self._status_cache = None
        self._last_check = 0
    
    def get_api_status(self) -> Dict[str, Any]:
        """Get current API status"""
        import time
        
        # Cache for 30 seconds to avoid excessive checks
        current_time = time.time()
        if self._status_cache and (current_time - self._last_check) < 30:
            return self._status_cache
        
        status = {
            'claude_available': bool(os.getenv('CLAUDE_API_KEY')),
            'openai_available': bool(os.getenv('OPENAI_API_KEY')),
            'preferred_provider': os.getenv('AI_ADVISOR_PROVIDER', 'claude'),
            'any_available': False
        }
        
        status['any_available'] = status['claude_available'] or status['openai_available']
        
        self._status_cache = status
        self._last_check = current_time
        
        return status
    
    def test_api_connection(self, provider: str) -> tuple[bool, str]:
        """Test API connection for a specific provider"""
        try:
            if provider == 'claude':
                if not os.getenv('CLAUDE_API_KEY'):
                    return False, "Claude API key not found in .env file"
                
                # Simple test - just check if we can import and initialize
                from core.ai_prompt_advisor import get_ai_advisor
                advisor = get_ai_advisor()
                
                if advisor.claude_available:
                    return True, "Claude API connection successful"
                else:
                    return False, "Claude API key may be invalid"
                    
            elif provider == 'openai':
                if not os.getenv('OPENAI_API_KEY'):
                    return False, "OpenAI API key not found in .env file"
                
                from core.ai_prompt_advisor import get_ai_advisor
                advisor = get_ai_advisor()
                
                if advisor.openai_available:
                    return True, "OpenAI API connection successful"
                else:
                    return False, "OpenAI API key may be invalid"
            
            return False, f"Unknown provider: {provider}"
            
        except Exception as e:
            logger.error(f"Error testing {provider} connection: {e}")
            return False, f"Connection test failed: {str(e)}"
    
    def clear_cache(self):
        """Clear status cache to force refresh"""
        self._status_cache = None
        self._last_check = 0

# Global instance
ai_manager = AIAssistantManager()

class ModernAISettingsDialog:
    """Modern AI settings dialog that works with .env configuration"""
    
    def __init__(self, parent):
        self.parent = parent
        self.show_settings_dialog()
    
    def show_settings_dialog(self):
        """Show AI settings configuration dialog"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("🤖 AI Assistant Settings")
        self.dialog.geometry("700x600")
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Center dialog
        self.center_dialog()
        
        # Main container with modern styling
        main_container = tk.Frame(self.dialog, bg='#f8f9fa')
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Header
        self.create_header(main_container)
        
        # Status section
        self.create_status_section(main_container)
        
        # Configuration section
        self.create_config_section(main_container)
        
        # Provider preferences
        self.create_provider_section(main_container)
        
        # Actions
        self.create_actions_section(main_container)
        
        # Load current status
        self.refresh_status()
    
    def center_dialog(self):
        """Center the dialog on parent window"""
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")
    
    def create_header(self, parent):
        """Create dialog header"""
        header_frame = tk.Frame(parent, bg='#2c3e50', height=80)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(
            header_frame,
            text="🤖 AI Assistant Configuration",
            font=('Arial', 18, 'bold'),
            fg='white',
            bg='#2c3e50'
        )
        title_label.pack(expand=True)
        
        subtitle_label = tk.Label(
            header_frame,
            text="Configure AI-powered prompt suggestions",
            font=('Arial', 11),
            fg='#ecf0f1',
            bg='#2c3e50'
        )
        subtitle_label.pack()
    
    def create_status_section(self, parent):
        """Create API status section"""
        status_frame = tk.LabelFrame(
            parent,
            text="🔍 API Status",
            font=('Arial', 12, 'bold'),
            bg='#f8f9fa',
            fg='#2c3e50',
            padx=20,
            pady=15
        )
        status_frame.pack(fill=tk.X, padx=20, pady=(20, 10))
        
        # Status indicators
        self.claude_status = tk.Label(
            status_frame,
            text="Claude API: Checking...",
            font=('Arial', 11),
            bg='#f8f9fa'
        )
        self.claude_status.pack(anchor=tk.W, pady=5)
        
        self.openai_status = tk.Label(
            status_frame,
            text="OpenAI API: Checking...",
            font=('Arial', 11),
            bg='#f8f9fa'
        )
        self.openai_status.pack(anchor=tk.W, pady=5)
        
        self.overall_status = tk.Label(
            status_frame,
            text="Overall Status: Checking...",
            font=('Arial', 11, 'bold'),
            bg='#f8f9fa'
        )
        self.overall_status.pack(anchor=tk.W, pady=(10, 5))
    
    def create_config_section(self, parent):
        """Create configuration instruction section"""
        config_frame = tk.LabelFrame(
            parent,
            text="⚙️ Configuration",
            font=('Arial', 12, 'bold'),
            bg='#f8f9fa',
            fg='#2c3e50',
            padx=20,
            pady=15
        )
        config_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Instructions
        instructions = tk.Label(
            config_frame,
            text="API keys are configured via environment variables for security.",
            font=('Arial', 11),
            bg='#f8f9fa',
            fg='#2c3e50'
        )
        instructions.pack(anchor=tk.W, pady=(0, 10))
        
        # .env file instructions
        env_frame = tk.Frame(config_frame, bg='#e9ecef', relief='solid', bd=1)
        env_frame.pack(fill=tk.X, pady=10)
        
        env_title = tk.Label(
            env_frame,
            text="📝 Add to your .env file:",
            font=('Arial', 10, 'bold'),
            bg='#e9ecef',
            fg='#495057'
        )
        env_title.pack(anchor=tk.W, padx=10, pady=(10, 5))
        
        env_content = tk.Text(
            env_frame,
            height=4,
            font=('Courier', 10),
            bg='#ffffff',
            fg='#495057',
            relief='flat',
            wrap=tk.NONE
        )
        env_content.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        env_text = """# AI Prompt Advisor Configuration
CLAUDE_API_KEY=your_claude_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
AI_ADVISOR_PROVIDER=claude"""
        
        env_content.insert('1.0', env_text)
        env_content.config(state='disabled')
        
        # API key links
        links_frame = tk.Frame(config_frame, bg='#f8f9fa')
        links_frame.pack(fill=tk.X, pady=(10, 0))
        
        claude_link = tk.Button(
            links_frame,
            text="🔗 Get Claude API Key",
            bg='#3498db',
            fg='white',
            font=('Arial', 10),
            relief='flat',
            padx=15,
            pady=5,
            cursor='hand2',
            command=lambda: self.open_url("https://console.anthropic.com/")
        )
        claude_link.pack(side=tk.LEFT, padx=(0, 10))
        
        openai_link = tk.Button(
            links_frame,
            text="🔗 Get OpenAI API Key",
            bg='#27ae60',
            fg='white',
            font=('Arial', 10),
            relief='flat',
            padx=15,
            pady=5,
            cursor='hand2',
            command=lambda: self.open_url("https://platform.openai.com/api-keys")
        )
        openai_link.pack(side=tk.LEFT)
    
    def create_provider_section(self, parent):
        """Create provider preference section"""
        provider_frame = tk.LabelFrame(
            parent,
            text="🎯 Provider Preferences",
            font=('Arial', 12, 'bold'),
            bg='#f8f9fa',
            fg='#2c3e50',
            padx=20,
            pady=15
        )
        provider_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Current provider
        current_provider = os.getenv('AI_ADVISOR_PROVIDER', 'claude')
        
        provider_info = tk.Label(
            provider_frame,
            text=f"Current preferred provider: {current_provider.title()}",
            font=('Arial', 11),
            bg='#f8f9fa',
            fg='#2c3e50'
        )
        provider_info.pack(anchor=tk.W, pady=(0, 10))
        
        # Provider comparison
        comparison_text = """• Claude: Better for creative and nuanced suggestions
• OpenAI: Excellent for technical and structured prompts
• The system automatically falls back to the available provider"""
        
        comparison_label = tk.Label(
            provider_frame,
            text=comparison_text,
            font=('Arial', 10),
            bg='#f8f9fa',
            fg='#6c757d',
            justify=tk.LEFT
        )
        comparison_label.pack(anchor=tk.W)
    
    def create_actions_section(self, parent):
        """Create action buttons"""
        actions_frame = tk.Frame(parent, bg='#f8f9fa')
        actions_frame.pack(fill=tk.X, padx=20, pady=(20, 20))
        
        # Test connections
        test_frame = tk.Frame(actions_frame, bg='#f8f9fa')
        test_frame.pack(fill=tk.X, pady=(0, 15))
        
        test_claude_btn = tk.Button(
            test_frame,
            text="🧪 Test Claude",
            bg='#9b59b6',
            fg='white',
            font=('Arial', 10, 'bold'),
            relief='flat',
            padx=20,
            pady=8,
            cursor='hand2',
            command=lambda: self.test_connection('claude')
        )
        test_claude_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        test_openai_btn = tk.Button(
            test_frame,
            text="🧪 Test OpenAI",
            bg='#e67e22',
            fg='white',
            font=('Arial', 10, 'bold'),
            relief='flat',
            padx=20,
            pady=8,
            cursor='hand2',
            command=lambda: self.test_connection('openai')
        )
        test_openai_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        refresh_btn = tk.Button(
            test_frame,
            text="🔄 Refresh Status",
            bg='#3498db',
            fg='white',
            font=('Arial', 10, 'bold'),
            relief='flat',
            padx=20,
            pady=8,
            cursor='hand2',
            command=self.refresh_status
        )
        refresh_btn.pack(side=tk.LEFT)
        
        # Bottom buttons
        bottom_frame = tk.Frame(actions_frame, bg='#f8f9fa')
        bottom_frame.pack(fill=tk.X)
        
        help_btn = tk.Button(
            bottom_frame,
            text="❓ Help & Documentation",
            bg='#95a5a6',
            fg='white',
            font=('Arial', 11),
            relief='flat',
            padx=25,
            pady=10,
            cursor='hand2',
            command=self.show_help
        )
        help_btn.pack(side=tk.LEFT)
        
        close_btn = tk.Button(
            bottom_frame,
            text="✅ Close",
            bg='#27ae60',
            fg='white',
            font=('Arial', 11, 'bold'),
            relief='flat',
            padx=30,
            pady=10,
            cursor='hand2',
            command=self.dialog.destroy
        )
        close_btn.pack(side=tk.RIGHT)
    
    def refresh_status(self):
        """Refresh API status"""
        # Clear cache to force fresh check
        ai_manager.clear_cache()
        status = ai_manager.get_api_status()
        
        # Update Claude status
        if status['claude_available']:
            self.claude_status.config(
                text="✅ Claude API: Configured",
                fg='#27ae60'
            )
        else:
            self.claude_status.config(
                text="❌ Claude API: Not configured",
                fg='#e74c3c'
            )
        
        # Update OpenAI status
        if status['openai_available']:
            self.openai_status.config(
                text="✅ OpenAI API: Configured",
                fg='#27ae60'
            )
        else:
            self.openai_status.config(
                text="❌ OpenAI API: Not configured",
                fg='#e74c3c'
            )
        
        # Update overall status
        if status['any_available']:
            provider = status['preferred_provider'].title()
            self.overall_status.config(
                text=f"✅ AI Assistant: Ready (Primary: {provider})",
                fg='#27ae60'
            )
        else:
            self.overall_status.config(
                text="❌ AI Assistant: No API keys configured",
                fg='#e74c3c'
            )
    
    def test_connection(self, provider: str):
        """Test connection for specific provider"""
        # Show loading
        self.dialog.config(cursor='wait')
        self.dialog.update()
        
        try:
            success, message = ai_manager.test_api_connection(provider)
            
            if success:
                messagebox.showinfo(
                    f"{provider.title()} Test",
                    f"✅ {message}\n\nThe AI Assistant is ready to help improve your prompts!"
                )
            else:
                messagebox.showerror(
                    f"{provider.title()} Test Failed",
                    f"❌ {message}\n\nPlease check your API key configuration."
                )
                
        except Exception as e:
            messagebox.showerror(
                "Test Error",
                f"Failed to test {provider} connection:\n{str(e)}"
            )
        finally:
            self.dialog.config(cursor='')
    
    def open_url(self, url: str):
        """Open URL in browser"""
        import webbrowser
        try:
            webbrowser.open(url)
        except Exception as e:
            messagebox.showerror("Error", f"Could not open URL: {str(e)}")
    
    def show_help(self):
        """Show help information"""
        help_text = """🤖 AI Assistant Help

The AI Assistant provides intelligent prompt suggestions to improve your results across all AI models.

🚀 Getting Started:
1. Add API keys to your .env file
2. Restart the application
3. Look for "✨ Improve with AI" buttons in each tab
4. Right-click in prompt fields for quick access

🎯 Features:
• Smart prompt enhancement for each AI model
• 3 types of suggestions: Clarity, Creativity, Technical
• Filter training mode for safety research
• Cross-model compatibility

🔧 Troubleshooting:
• Buttons not appearing? Check that API keys are configured
• API errors? Verify your keys are valid and have quota
• No suggestions? Check your internet connection

📚 Need help getting API keys?
• Claude: console.anthropic.com
• OpenAI: platform.openai.com/api-keys"""
        
        help_dialog = tk.Toplevel(self.dialog)
        help_dialog.title("AI Assistant Help")
        help_dialog.geometry("600x500")
        help_dialog.transient(self.dialog)
        
        text_widget = tk.Text(
            help_dialog,
            wrap=tk.WORD,
            font=('Arial', 11),
            padx=20,
            pady=20,
            bg='#f8f9fa'
        )
        text_widget.pack(fill=tk.BOTH, expand=True)
        text_widget.insert('1.0', help_text)
        text_widget.config(state='disabled')
        
        close_help_btn = tk.Button(
            help_dialog,
            text="Close",
            command=help_dialog.destroy,
            bg='#3498db',
            fg='white',
            font=('Arial', 11),
            padx=20,
            pady=5
        )
        close_help_btn.pack(pady=10)

def show_ai_settings(parent):
    """Show the modern AI settings dialog"""
    ModernAISettingsDialog(parent)

def get_ai_status():
    """Get current AI assistant status"""
    return ai_manager.get_api_status()

def is_ai_available():
    """Check if AI assistant is available"""
    status = ai_manager.get_api_status()
    return status['any_available']

# Integration function for easy checking
def check_and_show_ai_unavailable_message(parent):
    """Check AI availability and show message if unavailable"""
    if not is_ai_available():
        messagebox.showwarning(
            "AI Assistant Unavailable",
            "The AI Assistant requires API keys to be configured.\n\n"
            "Go to '🤖 AI Assistant' → '⚙️ Settings' to configure your API keys."
        )
        return False
    return True
