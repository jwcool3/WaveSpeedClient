"""
Updated Main App with Fixed AI Integration
For WaveSpeed AI Creative Suite

This fixes the AI assistant menu and integrates the universal AI system.
"""

import os
import sys
import tkinter as tk
from tkinter import ttk

# Try to import drag and drop support
try:
    from tkinterdnd2 import TkinterDnD
    DND_AVAILABLE = True
except ImportError:
    DND_AVAILABLE = False
    print("tkinterdnd2 not available. Drag and drop will be disabled.")

from app.config import Config
from core.logger import get_logger
from core.resource_manager import get_resource_manager
from core.api_client import WaveSpeedAPIClient
from ui.tabs.image_editor_tab import ImageEditorTab
from ui.tabs.image_upscaler_tab import ImageUpscalerTab
from ui.tabs.video_generation_tab import VideoGenerationTab
from ui.tabs.seededit_tab import SeedEditTab
from ui.components.balance_indicator import BalanceIndicator
from ui.components.recent_results_panel import RecentResultsPanel
from utils.utils import show_error, show_warning, show_success
import utils.utils as utils
from core.auto_save import auto_save_manager

# Import the new AI integration system
from ui.components.universal_ai_integration import universal_ai_integrator, refresh_ai_button_states
from ui.components.fixed_ai_settings import show_ai_settings, get_ai_status
from ui.components.prompt_analytics import show_prompt_analytics

logger = get_logger()
resource_manager = get_resource_manager()


class WaveSpeedAIApp:
    """Main WaveSpeed AI Application with Fixed AI Integration"""
    
    def __init__(self):
        logger.info("Initializing WaveSpeed AI Application")
        
        # Validate configuration
        config_errors = Config.validate()
        if config_errors:
            logger.warning(f"Configuration issues: {config_errors}")
        
        # Clean up old temp files
        resource_manager.cleanup_old_temp_files()
        
        # Initialize root window
        try:
            if DND_AVAILABLE:
                self.root = TkinterDnD.Tk()
                logger.info("Drag and drop support enabled")
            else:
                self.root = tk.Tk()
                logger.info("Drag and drop support disabled")
        except Exception as e:
            logger.error(f"Failed to initialize main window: {str(e)}")
            raise
        
        self.root.title(Config.WINDOW_TITLE)
        self.root.geometry(Config.WINDOW_SIZE)
        self.root.minsize(*Config.WINDOW_MIN_SIZE)
        self.root.configure(bg=Config.COLORS['background'], highlightthickness=0, bd=0)
        
        # Setup responsive layout
        self.setup_responsive_layout()
        
        # Set window icon if available
        self.set_window_icon()
        
        # Initialize API client
        self.api_client = WaveSpeedAPIClient()
        
        # Tab references
        self.editor_tab = None
        self.upscaler_tab = None
        self.video_tab = None
        self.seededit_tab = None
        self.notebook = None
        
        # Setup UI
        self.setup_ui()
        
        # Auto-integrate AI features with all tabs after UI is ready
        self.root.after(500, self.integrate_ai_features)
    
    def setup_responsive_layout(self):
        """Configure responsive layout"""
        # Bind to window resize events
        self.root.bind('<Configure>', self._on_window_resize)
        
        # Configure weight distribution for main container
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
    
    def _on_window_resize(self, event):
        """Handle window resize"""
        if event.widget == self.root:
            # Trigger layout updates for all tabs
            self._update_layout_for_size(event.width, event.height)
    
    def _update_layout_for_size(self, width, height):
        """Update layout based on window size"""
        # Update any size-dependent layouts
        if hasattr(self, 'notebook') and self.notebook:
            # Force notebook to update its layout
            self.notebook.update_idletasks()
    
    def integrate_ai_features(self):
        """Integrate AI features with all tabs"""
        try:
            # Integration mapping: tab_instance -> (model_type, prompt_widget_name)
            integrations = [
                (self.editor_tab, "nano_banana", "prompt_text"),
                (self.seededit_tab, "seededit", "prompt_text"),
                (self.upscaler_tab, "upscaler", None),  # Upscaler doesn't have prompts
                (self.video_tab, "video_generation", "prompt_text")
            ]
            
            # Check if Seedream V4 tab exists
            if hasattr(self, 'seedream_tab') and self.seedream_tab:
                integrations.append((self.seedream_tab, "seedream_v4", "prompt_text"))
            
            successful_integrations = 0
            for tab_instance, model_type, prompt_widget_name in integrations:
                if tab_instance and prompt_widget_name:  # Skip tabs without prompts
                    try:
                        success = universal_ai_integrator.integrate_with_tab(
                            tab_instance, 
                            model_type, 
                            prompt_widget_name
                        )
                        if success:
                            successful_integrations += 1
                            logger.info(f"Successfully integrated AI features with {model_type} tab")
                        else:
                            logger.warning(f"Failed to integrate AI features with {model_type} tab")
                    except Exception as e:
                        logger.error(f"Error integrating AI with {model_type} tab: {e}")
            
            logger.info(f"AI integration complete: {successful_integrations}/{len([i for i in integrations if i[2]])} tabs integrated")
            
            # Update menu with current AI status
            self.update_ai_menu_status()
            
        except Exception as e:
            logger.error(f"Error during AI integration: {e}")
    
    def update_ai_menu_status(self):
        """Update AI menu with current status"""
        try:
            ai_status = get_ai_status()
            
            # Update menu title based on availability
            if ai_status['any_available']:
                provider = ai_status['preferred_provider'].title()
                menu_title = f"🤖 AI Assistant ({provider})"
            else:
                menu_title = "🤖 AI Assistant (Configure)"
            
            # Find and update the AI menu
            menubar = self.root['menu']
            if menubar:
                # Update the menu cascade label
                try:
                    menu_index = None
                    for i in range(menubar.index('end') + 1):
                        if '🤖' in menubar.entrycget(i, 'label'):
                            menu_index = i
                            break
                    
                    if menu_index is not None:
                        menubar.entryconfig(menu_index, label=menu_title)
                except:
                    pass  # Menu might not exist yet
            
        except Exception as e:
            logger.error(f"Error updating AI menu status: {e}")
    
    def set_window_icon(self):
        """Set application window icon"""
        try:
            icon_path = os.path.join("assets", "icon.ico")
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
            else:
                # Try PNG icon
                icon_path = os.path.join("assets", "icon.png")
                if os.path.exists(icon_path):
                    from PIL import Image, ImageTk
                    img = Image.open(icon_path)
                    img = img.resize((32, 32), Image.Resampling.LANCZOS)
                    icon = ImageTk.PhotoImage(img)
                    self.root.iconphoto(True, icon)
        except Exception as e:
            logger.debug(f"Could not set window icon: {e}")
    
    def setup_ui(self):
        """Setup the user interface"""
        # Create menu bar
        self.create_menu_bar()
        
        # Configure styles to remove all padding/borders
        style = ttk.Style()
        style.configure('Flat.TPanedwindow', background='white', borderwidth=0, relief='flat')
        style.configure('Flat.TFrame', borderwidth=0, relief='flat')
        # Remove notebook padding at the top - aggressive settings
        style.configure('TNotebook', borderwidth=0, relief='flat', padding=0)
        style.configure('TNotebook.Tab', padding=[5, 0])  # Zero vertical padding on tabs
        style.configure('TFrame.Label', padding=0)
        
        # Additional style tweaks to eliminate gaps
        try:
            style.configure('TNotebook', tabmargins=[0, 0, 0, 0])
        except:
            pass  # May not be supported on all platforms
        
        # Create main container with paned window for resizable layout (no borders/padding)
        # Use tk.PanedWindow instead of ttk for more control over spacing
        self.main_paned_window = tk.PanedWindow(
            self.root, 
            orient=tk.HORIZONTAL, 
            borderwidth=0, 
            sashwidth=3,  # Thin sash for resizing
            sashrelief=tk.FLAT,
            bg=Config.COLORS['background']
        )
        self.main_paned_window.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        
        # Create left panel for main content (no padding for full space)
        # Use tk.Frame for tk.PanedWindow compatibility
        self.left_panel = tk.Frame(self.main_paned_window, borderwidth=0, highlightthickness=0)
        self.main_paned_window.add(self.left_panel)
        
        # Create right panel for recent results (no padding for full space)
        self.right_panel = tk.Frame(self.main_paned_window, borderwidth=0, highlightthickness=0)
        self.main_paned_window.add(self.right_panel)
        
        # Create notebook for tabs in left panel
        self.create_notebook()
        
        # Create recent results panel in right panel
        self.create_recent_results_panel()
        
        # Create balance indicator at bottom left
        self.create_balance_indicator()
        
        # Setup keyboard shortcuts
        self.setup_keyboard_shortcuts()
        
        # Load layout configuration
        self.load_layout_config()
        
        logger.info("UI setup completed")
    
    def create_menu_bar(self):
        """Create the application menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open Results Folder", command=self.open_results_folder)
        file_menu.add_separator()
        file_menu.add_command(label="Privacy Settings", command=self.show_privacy_settings)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_closing)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Switch to Nano Banana Editor", command=lambda: self.switch_to_tab(0))
        tools_menu.add_command(label="Switch to SeedEdit", command=lambda: self.switch_to_tab(1))
        tools_menu.add_command(label="Switch to Image Upscaler", command=lambda: self.switch_to_tab(2))
        tools_menu.add_command(label="Switch to Video Generator", command=lambda: self.switch_to_tab(3))
        tools_menu.add_command(label="Switch to SeedDance Pro", command=lambda: self.switch_to_tab(4))
        tools_menu.add_separator()
        tools_menu.add_command(label="💾 Save Seedream Layout", command=self.save_seedream_layout)
        tools_menu.add_command(label="📂 Load Seedream Layout", command=self.load_seedream_layout)
        tools_menu.add_separator()
        
        # Upload method toggle for Seedream V4 (for speed testing)
        self.use_image_hosting = tk.BooleanVar(value=True)  # Default to image hosting (privacy uploader)
        self.load_upload_preference()  # Load saved preference
        tools_menu.add_checkbutton(
            label="🌐 Use Image Hosting (Seedream V4)", 
            variable=self.use_image_hosting,
            command=self.toggle_upload_method
        )
        tools_menu.add_separator()
        tools_menu.add_command(label="📊 Prompt Analytics", command=self.show_prompt_analytics)
        
        # AI Assistant menu (improved)
        ai_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="🤖 AI Assistant", menu=ai_menu)
        ai_menu.add_command(label="⚙️ Settings", command=self.show_ai_settings)
        ai_menu.add_separator()
        ai_menu.add_command(label="🔄 Refresh AI Features", command=self.refresh_ai_features)
        ai_menu.add_separator()
        ai_menu.add_command(label="ℹ️ About AI Assistant", command=self.show_ai_about)
        ai_menu.add_command(label="📚 Help & Documentation", command=self.show_ai_help)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        
        logger.info("Menu bar created")
    
    def create_notebook(self):
        """Create the main notebook for tabs"""
        # Create notebook directly in left_panel (no container to avoid extra spacing)
        self.notebook = ttk.Notebook(self.left_panel, padding=0)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        
        # Create tabs
        self.create_tabs()
        
        logger.info("Notebook created with tabs")
    
    def create_tabs(self):
        """Create all application tabs"""
        try:
            # Nano Banana Editor Tab
            self.editor_tab = ImageEditorTab(self.notebook, self.api_client, self)
            self.notebook.add(self.editor_tab.container, text="🍌 Nano Banana Editor")
            
            # SeedEdit Tab
            self.seededit_tab = SeedEditTab(self.notebook, self.api_client, self)
            self.notebook.add(self.seededit_tab.container, text="✨ SeedEdit")
            
            # Image Upscaler Tab
            self.upscaler_tab = ImageUpscalerTab(self.notebook, self.api_client, self)
            self.notebook.add(self.upscaler_tab.container, text="🔍 Image Upscaler")
            
            # Unified Video Generation Tab (Wan 2.2 + SeedDance)
            self.video_tab = VideoGenerationTab(self.notebook, self.api_client, self)
            self.notebook.add(self.video_tab.container, text="🎬 Video Generation")
            
            # Try to add Seedream V4 tab if available
            try:
                from ui.tabs.seedream_v4_tab import SeedreamV4Tab
                self.seedream_tab = SeedreamV4Tab(self.notebook, self.api_client, self)
                # Insert before upscaler (at index 2)
                self.notebook.insert(2, self.seedream_tab.container, text="🌟 Seedream V4")
                logger.info("Seedream V4 tab added successfully")
            except ImportError:
                logger.info("Seedream V4 tab not available")
                self.seedream_tab = None
            
            logger.info("All tabs created successfully")
            
        except Exception as e:
            logger.error(f"Error creating tabs: {str(e)}")
            show_error("Tab Creation Error", f"Failed to create application tabs: {str(e)}")
    
    def create_recent_results_panel(self):
        """Create the recent results panel"""
        try:
            self.recent_results_panel = RecentResultsPanel(
                self.right_panel, 
                self  # Pass main app instance
            )
            logger.info("Recent results panel created")
        except Exception as e:
            logger.error(f"Error creating recent results panel: {str(e)}")
    
    def create_balance_indicator(self):
        """Create the balance indicator as an overlay at bottom left corner"""
        try:
            # Create balance indicator with root as parent for overlay positioning
            self.balance_indicator = BalanceIndicator(self.root, self.api_client)
            
            # Position at bottom-left corner (10px from left, 10px from bottom)
            # Using relx and rely with anchor='sw' to position relative to window size
            self.balance_indicator.get_frame().place(relx=0.0, rely=1.0, x=10, y=-10, anchor='sw')
            
            # Start balance updates after a short delay to ensure main loop is ready
            self.root.after(1000, self.balance_indicator.start_balance_updates)
            
            logger.info("Balance indicator created at bottom-left corner (overlay, no layout impact)")
        except Exception as e:
            logger.error(f"Error creating balance indicator: {str(e)}")
    
    def handle_recent_result_selected(self, image_path, metadata):
        """Handle selection of a recent result"""
        try:
            # Get the current active tab
            current_tab_index = self.get_current_tab_index()
            
            # Map tab indices to tab instances
            tabs = [
                self.editor_tab,
                self.seededit_tab, 
                self.upscaler_tab,
                self.video_tab
            ]
            
            # Add Seedream V4 tab if it exists
            if hasattr(self, 'seedream_tab') and self.seedream_tab:
                tabs.insert(2, self.seedream_tab)  # Insert at index 2
            
            if 0 <= current_tab_index < len(tabs) and tabs[current_tab_index]:
                current_tab = tabs[current_tab_index]
                
                # Load the image into the current tab
                if hasattr(current_tab, 'load_image_from_path'):
                    current_tab.load_image_from_path(image_path)
                elif hasattr(current_tab, 'selected_image_path'):
                    current_tab.selected_image_path = image_path
                    # Trigger image loading if there's a method for it
                    if hasattr(current_tab, 'load_selected_image'):
                        current_tab.load_selected_image()
                
                logger.info(f"Loaded recent result into tab {current_tab_index}: {image_path}")
            else:
                logger.warning(f"Invalid tab index or tab not available: {current_tab_index}")
                
        except Exception as e:
            logger.error(f"Error handling recent result selection: {e}")
            show_error("Error", f"Failed to load recent result: {str(e)}")
    
    def setup_keyboard_shortcuts(self):
        """Setup keyboard shortcuts"""
        try:
            # Layout shortcuts
            self.root.bind('<Control-bracketleft>', lambda e: self.toggle_right_panel())
            self.root.bind('<Control-bracketright>', lambda e: self.toggle_right_panel())
            self.root.bind('<Control-equal>', lambda e: self.reset_layout())
            
            # Tab shortcuts
            self.root.bind('<Control-1>', lambda e: self.switch_to_tab(0))
            self.root.bind('<Control-2>', lambda e: self.switch_to_tab(1))
            self.root.bind('<Control-3>', lambda e: self.switch_to_tab(2))
            self.root.bind('<Control-4>', lambda e: self.switch_to_tab(3))
            self.root.bind('<Control-5>', lambda e: self.switch_to_tab(4))
            
            logger.info("Keyboard shortcuts configured")
        except Exception as e:
            logger.error(f"Error setting up keyboard shortcuts: {str(e)}")
    
    def toggle_right_panel(self):
        """Toggle the right panel visibility"""
        # Implementation for toggling right panel
        pass
    
    def reset_layout(self):
        """Reset the layout to default"""
        # Implementation for resetting layout
        pass
    
    def load_layout_config(self):
        """Load layout configuration"""
        # Implementation for loading layout config
        pass
    
    def switch_to_tab(self, tab_index):
        """Switch to a specific tab"""
        try:
            self.notebook.select(tab_index)
        except tk.TclError:
            pass  # Tab doesn't exist or invalid index
    
    def get_current_tab_index(self):
        """Get the current active tab index"""
        try:
            return self.notebook.index(self.notebook.select())
        except Exception as e:
            logger.debug(f"Error getting current tab index: {e}")
            return 0
    
    def open_results_folder(self):
        """Open the auto-save results folder"""
        try:
            success = auto_save_manager.open_results_folder()
            if not success:
                show_warning("Folder Not Found", 
                           f"Results folder not found.\n\n"
                           f"Generate some results first, then the folder will be created at:\n"
                           f"{Config.AUTO_SAVE_FOLDER}")
        except Exception as e:
            show_error("Error", f"Failed to open results folder: {str(e)}")
    
    def save_seedream_layout(self):
        """Save the current Seedream V4 layout configuration"""
        try:
            if hasattr(self, 'seedream_tab') and self.seedream_tab:
                if hasattr(self.seedream_tab, 'improved_layout') and self.seedream_tab.improved_layout:
                    self.seedream_tab.improved_layout.save_layout_manually()
                else:
                    show_warning("Not Available", "Seedream layout is not initialized yet.")
            else:
                show_warning("Not Available", 
                           "Seedream V4 tab is not available.\n\n"
                           "Please switch to the Seedream V4 tab first.")
        except Exception as e:
            logger.error(f"Error saving Seedream layout: {e}")
            show_error("Save Failed", f"Failed to save layout:\n{str(e)}")
    
    def load_seedream_layout(self):
        """Load and apply the saved Seedream V4 layout configuration"""
        try:
            if hasattr(self, 'seedream_tab') and self.seedream_tab:
                if hasattr(self.seedream_tab, 'improved_layout') and self.seedream_tab.improved_layout:
                    self.seedream_tab.improved_layout.load_layout_manually()
                else:
                    show_warning("Not Available", "Seedream layout is not initialized yet.")
            else:
                show_warning("Not Available", 
                           "Seedream V4 tab is not available.\n\n"
                           "Please switch to the Seedream V4 tab first.")
        except Exception as e:
            logger.error(f"Error loading Seedream layout: {e}")
            show_error("Load Failed", f"Failed to load layout:\n{str(e)}")
    
    def toggle_upload_method(self):
        """Toggle between image hosting and direct upload for Seedream V4"""
        try:
            use_hosting = self.use_image_hosting.get()
            self.save_upload_preference()
            
            method_name = "Image Hosting (Privacy Uploader)" if use_hosting else "Direct Upload"
            logger.info(f"Seedream V4 upload method changed to: {method_name}")
            
            # Show confirmation message
            from tkinter import messagebox
            messagebox.showinfo(
                "Upload Method Changed", 
                f"Seedream V4 will now use:\n\n{method_name}\n\n"
                f"This setting is saved and will persist across restarts.\n"
                f"You can test the speed difference between both methods."
            )
        except Exception as e:
            logger.error(f"Error toggling upload method: {e}")
    
    def save_upload_preference(self):
        """Save upload method preference to file"""
        try:
            import json
            from pathlib import Path
            
            prefs_file = Path("data/upload_preferences.json")
            prefs_file.parent.mkdir(parents=True, exist_ok=True)
            
            preferences = {
                "use_image_hosting": self.use_image_hosting.get()
            }
            
            with open(prefs_file, 'w') as f:
                json.dump(preferences, f, indent=2)
            
            logger.debug(f"Upload preference saved: {preferences}")
        except Exception as e:
            logger.error(f"Error saving upload preference: {e}")
    
    def load_upload_preference(self):
        """Load upload method preference from file"""
        try:
            import json
            from pathlib import Path
            
            prefs_file = Path("data/upload_preferences.json")
            
            if prefs_file.exists():
                with open(prefs_file, 'r') as f:
                    preferences = json.load(f)
                
                use_hosting = preferences.get("use_image_hosting", True)
                self.use_image_hosting.set(use_hosting)
                
                logger.info(f"Loaded upload preference: {'Image Hosting' if use_hosting else 'Direct Upload'}")
            else:
                # Default to image hosting (current behavior)
                self.use_image_hosting.set(True)
                logger.debug("No upload preference found, using default (Image Hosting)")
        except Exception as e:
            logger.error(f"Error loading upload preference: {e}")
            self.use_image_hosting.set(True)  # Fallback to default
    
    def show_privacy_settings(self):
        """Show privacy settings dialog"""
        # Implementation for privacy settings
        show_warning("Feature Coming Soon", "Privacy settings dialog will be available in a future update.")
    
    def show_ai_settings(self):
        """Show AI assistant settings dialog"""
        try:
            show_ai_settings(self.root)
            # Refresh AI features after settings dialog is closed
            self.root.after(100, self.refresh_ai_features)
        except Exception as e:
            logger.error(f"Error showing AI settings: {e}")
            show_error("AI Settings Error", f"Failed to show AI settings: {str(e)}")
    
    def refresh_ai_features(self):
        """Refresh AI features in all tabs"""
        try:
            refresh_ai_button_states()
            self.update_ai_menu_status()
            show_success("AI Features Refreshed", "AI assistant features have been refreshed in all tabs.")
            logger.info("AI features refreshed successfully")
        except Exception as e:
            logger.error(f"Error refreshing AI features: {e}")
            show_error("Refresh Error", f"Failed to refresh AI features: {str(e)}")
    
    def show_ai_about(self):
        """Show AI assistant information"""
        ai_status = get_ai_status()
        
        if ai_status['any_available']:
            status_text = f"✅ Active (Primary: {ai_status['preferred_provider'].title()})"
            providers_text = []
            if ai_status['claude_available']:
                providers_text.append("• ✅ Claude API configured")
            else:
                providers_text.append("• ❌ Claude API not configured")
            
            if ai_status['openai_available']:
                providers_text.append("• ✅ OpenAI API configured")
            else:
                providers_text.append("• ❌ OpenAI API not configured")
            
            providers_info = "\n".join(providers_text)
        else:
            status_text = "❌ Not configured"
            providers_info = "No API keys configured. Go to Settings to configure."
        
        about_text = f"""🤖 AI Prompt Assistant

Status: {status_text}

Configuration:
{providers_info}

Features:
• ✨ Improve existing prompts for better results
• 💡 Generate creative prompt ideas  
• 🎯 Tab-specific optimization for each AI model
• 🧠 Context-aware suggestions
• 🛡️ Filter training mode for safety research
• ⚙️ Configurable settings and preferences

Setup:
1. Add API keys to your .env file:
   - CLAUDE_API_KEY=your_claude_key
   - OPENAI_API_KEY=your_openai_key

2. Restart the application

3. Use "✨ Improve with AI" buttons in any tab

The AI Assistant helps you create more effective prompts that lead to better AI generations!"""
        
        from tkinter import messagebox
        messagebox.showinfo("AI Prompt Assistant", about_text)
    
    def show_ai_help(self):
        """Show AI assistant help documentation"""
        help_dialog = tk.Toplevel(self.root)
        help_dialog.title("AI Assistant Help")
        help_dialog.geometry("800x600")
        help_dialog.transient(self.root)
        help_dialog.grab_set()
        
        # Center dialog
        help_dialog.update_idletasks()
        x = (help_dialog.winfo_screenwidth() // 2) - (help_dialog.winfo_width() // 2)
        y = (help_dialog.winfo_screenheight() // 2) - (help_dialog.winfo_height() // 2)
        help_dialog.geometry(f"+{x}+{y}")
        
        # Create scrollable text widget
        text_frame = tk.Frame(help_dialog)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        text_widget = tk.Text(
            text_frame,
            wrap=tk.WORD,
            font=('Arial', 11),
            bg='#f8f9fa',
            fg='#2c3e50'
        )
        
        scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        help_content = """🤖 AI Assistant Complete Guide

OVERVIEW
========
The AI Assistant provides intelligent prompt suggestions using Claude or OpenAI APIs to help you create better prompts for all AI models in the WaveSpeed AI Creative Suite.

SETUP INSTRUCTIONS
==================
1. Get API Keys:
   • Claude: Visit console.anthropic.com
   • OpenAI: Visit platform.openai.com/api-keys

2. Configure .env file:
   Add these lines to your .env file:
   CLAUDE_API_KEY=your_claude_api_key_here
   OPENAI_API_KEY=your_openai_api_key_here
   AI_ADVISOR_PROVIDER=claude

3. Restart the application

HOW TO USE
==========
Method 1: AI Improve Button
• Enter your prompt in any tab's prompt field
• Click "✨ Improve with AI" button
• Review suggestions in the enhanced dialog
• Click "✅ Use This Prompt" to apply

Method 2: Right-Click Context Menu
• Right-click in any prompt text field
• Select "✨ Improve with AI" from context menu
• Choose from suggestions and apply

Method 3: Filter Training (Research Only)
• Enter a prompt in any tab
• Click "🛡️ Filter Training" button
• Confirm warning dialog about safety research
• Review generated examples for filter training

SUGGESTION TYPES
================
• Clarity: Makes prompts clearer and more specific
• Creativity: Adds artistic flair and creative elements
• Technical: Optimizes for technical accuracy and model performance

MODEL-SPECIFIC GUIDANCE
=======================
🍌 Nano Banana: Artistic transformations with vivid, descriptive language
✨ SeedEdit: Precise, controlled edits with technical precision
🌟 Seedream V4: Complex multi-step transformations with structured prompts
🎬 Wan 2.2: Natural motion and realistic animations
🕺 SeedDance Pro: Cinematic movement and camera work

TROUBLESHOOTING
===============
Buttons Not Appearing:
• Check that API keys are configured in .env file
• Restart the application
• Go to AI Assistant → Refresh AI Features

API Errors:
• Verify your API keys are valid
• Check that you have sufficient quota/credits
• Test connection in AI Assistant → Settings

No Suggestions Generated:
• Check your internet connection
• Try with a different prompt
• Switch to alternative provider if available

Empty Prompts:
• Enter some text in the prompt field before requesting suggestions
• The AI needs context to provide meaningful improvements

PRIVACY & SECURITY
==================
• API keys are stored securely in .env file
• Only current prompt text is sent to AI APIs
• No permanent storage of AI suggestions
• Users control which suggestions to apply

ADVANCED FEATURES
=================
• Auto-detection of available APIs
• Graceful fallback between providers
• Context-aware suggestions for each model
• Filter training for safety research
• Copy suggestions to clipboard
• Preview before applying

GETTING HELP
============
• Check this help documentation
• Visit AI Assistant → Settings for configuration
• Test API connections in settings
• Check application logs for detailed error information

For additional support, refer to the main application documentation."""
        
        text_widget.insert('1.0', help_content)
        text_widget.config(state='disabled')
        
        # Close button
        close_btn = tk.Button(
            help_dialog,
            text="Close",
            command=help_dialog.destroy,
            bg='#3498db',
            fg='white',
            font=('Arial', 11),
            padx=20,
            pady=5
        )
        close_btn.pack(pady=(0, 20))
    
    def show_prompt_analytics(self):
        """Show prompt analytics window"""
        try:
            show_prompt_analytics(self.root)
        except Exception as e:
            logger.error(f"Error showing prompt analytics: {e}")
            show_error("Error", f"Failed to open prompt analytics: {e}")
    
    def show_about(self):
        """Show about dialog"""
        about_text = f"""WaveSpeed AI Creative Suite
Version: {Config.VERSION}

A comprehensive GUI application for AI-powered image editing, upscaling, and video generation.

Created by Jackson Weed

Features:
• Multiple AI models (Nano Banana, SeedEdit, Seedream V4, etc.)
• Enhanced prompt management with database
• AI-powered prompt suggestions
• Cross-tab workflow integration
• Auto-save and organization
• Professional video player
• Real-time balance tracking

Visit: https://wavespeed.ai"""
        
        from tkinter import messagebox
        messagebox.showinfo("About WaveSpeed AI", about_text)
    
    def on_closing(self):
        """Handle application closing"""
        try:
            # Save layout configuration
            self.save_layout_config()
            
            # Cleanup resources
            resource_manager.cleanup_all()
            
            logger.info("Application closing")
            self.root.quit()
            self.root.destroy()
            
        except Exception as e:
            logger.error(f"Error during application shutdown: {str(e)}")
            self.root.quit()
            self.root.destroy()
    
    def save_layout_config(self):
        """Save layout configuration"""
        # Implementation for saving layout config
        pass
    
    def run(self):
        """Run the application"""
        try:
            # Check API key configuration
            if not Config.API_KEY:
                show_warning("Configuration", 
                    "Please set WAVESPEED_API_KEY in your .env file.\n\n"
                    "Copy env_example.txt to .env and add your API key."
                )
            else:
                logger.info("API key loaded successfully")
            
            # Setup cleanup on window close
            self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
            
            # Start the main loop
            logger.info("Starting GUI main loop")
            self.root.mainloop()
            
        except Exception as e:
            logger.error(f"Error running application: {str(e)}")
            show_error("Application Error", f"Failed to run application: {str(e)}")
        finally:
            logger.info("Application shutdown")

# Example usage and testing
if __name__ == "__main__":
    try:
        app = WaveSpeedAIApp()
        app.run()
    except Exception as e:
        print(f"Failed to start application: {e}")
        import traceback
        traceback.print_exc()