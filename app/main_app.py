"""
Main WaveSpeed AI GUI Application

This is the main application file that creates the tabbed interface
and manages all the different AI tools.
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
from ui.tabs.image_to_video_tab import ImageToVideoTab
from ui.tabs.seededit_tab import SeedEditTab
from ui.tabs.seeddance_tab import SeedDanceTab
from ui.components.balance_indicator import BalanceIndicator
from ui.components.recent_results_panel import RecentResultsPanel
from utils.utils import show_error, show_warning, show_success
import utils.utils as utils
from core.auto_save import auto_save_manager

logger = get_logger()
resource_manager = get_resource_manager()


class WaveSpeedAIApp:
    """Main WaveSpeed AI Application"""
    
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
        self.root.minsize(*Config.WINDOW_MIN_SIZE)  # Set minimum window size
        self.root.configure(bg=Config.COLORS['background'])
        
        # Set window icon if available
        self.set_window_icon()
        
        # Initialize API client
        self.api_client = WaveSpeedAPIClient()
        
        # Tab references
        self.editor_tab = None
        self.upscaler_tab = None
        self.video_tab = None
        self.seededit_tab = None
        self.seeddance_tab = None
        self.notebook = None
        
        # Setup error handling
        self.setup_error_handling()
        
        self.setup_ui()
        
        logger.info("Application initialized successfully")
    
    def set_window_icon(self):
        """Set window icon if available"""
        try:
            # Try to set icon from file
            icon_path = "assets/icon.ico"
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except Exception as e:
            logger.debug(f"Could not set window icon: {str(e)}")
    
    def setup_error_handling(self):
        """Setup global error handling"""
        def handle_exception(exc_type, exc_value, exc_traceback):
            if issubclass(exc_type, KeyboardInterrupt):
                sys.__excepthook__(exc_type, exc_value, exc_traceback)
                return
            
            logger.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
            show_error(
                "Unexpected Error",
                f"An unexpected error occurred:\n\n{exc_type.__name__}: {exc_value}\n\n"
                "Please check the logs for more details."
            )
        
        sys.excepthook = handle_exception
    
    def setup_ui(self):
        """Setup the main UI"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)  # Main frame expands
        main_frame.rowconfigure(2, weight=1)  # Content area expands vertically
        
        # Create header frame to hold title and balance indicator
        header_frame = ttk.Frame(main_frame)
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        header_frame.columnconfigure(0, weight=1)  # Title takes most space
        
        # Title
        title_label = ttk.Label(
            header_frame, 
            text="WaveSpeed AI - Image Editor, Upscaler & Video Generator", 
            font=('Arial', 16, 'bold')
        )
        title_label.grid(row=0, column=0, sticky=tk.W)
        
        # Balance indicator in top-right corner
        if self.api_client.api_key:  # Only show if API key is available
            self.balance_indicator = BalanceIndicator(header_frame, self.api_client)
            self.balance_indicator.get_frame().grid(row=0, column=1, sticky=tk.E, padx=(10, 0))
        
        # API Key status
        api_status = "✓ API Key loaded" if self.api_client.api_key else "✗ API Key not found"
        api_color = "green" if self.api_client.api_key else "red"
        api_label = tk.Label(
            main_frame, text=api_status, fg=api_color, 
            bg='#f0f0f0', font=('Arial', 10)
        )
        api_label.grid(row=1, column=0, pady=(0, 10))
        
        # Create resizable paned window for main content
        self.setup_resizable_layout(main_frame)
        
        # Create tabs
        self.setup_tabs()
        
        # Setup menu
        self.setup_menu()
    
    def setup_resizable_layout(self, parent):
        """Setup resizable paned window layout"""
        # Create horizontal paned window (resizable splitter)
        self.paned_window = tk.PanedWindow(
            parent,
            orient=tk.HORIZONTAL,
            sashrelief=tk.RAISED,
            sashwidth=4,
            bg='#e0e0e0',
            handlesize=8,
            handlepad=20
        )
        self.paned_window.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        
        # Create recent results panel (left pane)
        self.setup_recent_results_panel(self.paned_window)
        
        # Create notebook for tabs (right pane)
        self.notebook = ttk.Notebook(self.paned_window)
        
        # Add both panes to the paned window
        self.paned_window.add(self.recent_results_frame, minsize=150, width=200)  # Left pane: min 150px, default 200px
        self.paned_window.add(self.notebook, minsize=400)  # Right pane: min 400px, gets remaining space
        
        # Configure the paned window to be responsive
        self.paned_window.paneconfigure(self.recent_results_frame, sticky="nsew")
        self.paned_window.paneconfigure(self.notebook, sticky="nsew")
        
        # Bind keyboard shortcuts for quick resizing
        self.root.bind('<Control-bracketleft>', self.collapse_sidebar)  # Ctrl+[ to collapse sidebar
        self.root.bind('<Control-bracketright>', self.expand_sidebar)   # Ctrl+] to expand sidebar
        self.root.bind('<Control-equal>', self.reset_splitter)          # Ctrl+= to reset splitter
        
        # Load saved splitter position if available
        self.load_splitter_position()
    
    def setup_recent_results_panel(self, parent):
        """Setup the recent results panel"""
        # Create frame for recent results (for paned window)
        self.recent_results_frame = ttk.LabelFrame(parent, text="📂 Recent Results", padding="3")
        
        # Create recent results panel
        self.recent_results_panel = RecentResultsPanel(self.recent_results_frame, self)
        self.recent_results_panel.get_frame().pack(fill=tk.BOTH, expand=True)
    
    def setup_tabs(self):
        """Setup all application tabs"""
        # Nano Banana Editor Tab
        self.editor_tab = ImageEditorTab(self.notebook, self.api_client, self)
        self.notebook.add(self.editor_tab.container, text="🍌 Nano Banana Editor")
        
        # SeedEdit Tab (V3)
        self.seededit_tab = SeedEditTab(self.notebook, self.api_client, self)
        self.notebook.add(self.seededit_tab.container, text="✨ SeedEdit")
        
        # NEW: Seedream V4 Tab
        from ui.tabs.seedream_v4_tab import SeedreamV4Tab
        self.seedream_v4_tab = SeedreamV4Tab(self.notebook, self.api_client, self)
        self.notebook.add(self.seedream_v4_tab.container, text="🌟 Seedream V4")
        
        # Image Upscaler Tab
        self.upscaler_tab = ImageUpscalerTab(self.notebook, self.api_client, self)
        self.notebook.add(self.upscaler_tab.container, text="🔍 Image Upscaler")
        
        # Wan 2.2 Tab
        self.video_tab = ImageToVideoTab(self.notebook, self.api_client, self)
        self.notebook.add(self.video_tab.container, text="🎬 Wan 2.2")
        
        # SeedDance Tab
        self.seeddance_tab = SeedDanceTab(self.notebook, self.api_client, self)
        self.notebook.add(self.seeddance_tab.container, text="🕺 SeedDance Pro")
        
        # Setup enhanced tab management
        from ui.components.enhanced_tab_manager import EnhancedTabManager
        self.tab_manager = EnhancedTabManager(self.notebook, self)
    
    def setup_menu(self):
        """Setup application menu"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_separator()
        file_menu.add_command(label="Open Results Folder", command=self.open_results_folder)
        file_menu.add_separator()
        file_menu.add_command(label="Privacy Settings", command=self.show_privacy_settings)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Switch to Editor", command=lambda: self.switch_to_tab(0))
        tools_menu.add_command(label="Switch to SeedEdit", command=lambda: self.switch_to_tab(1))
        tools_menu.add_command(label="Switch to Seedream V4", command=lambda: self.switch_to_tab(2))  # NEW
        tools_menu.add_command(label="Switch to Upscaler", command=lambda: self.switch_to_tab(3))      # Updated index
        tools_menu.add_command(label="Switch to Video Generator", command=lambda: self.switch_to_tab(4))  # Updated index
        tools_menu.add_command(label="Switch to SeedDance Pro", command=lambda: self.switch_to_tab(5))     # Updated index
        
        # AI Assistant menu
        ai_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="🤖 AI Assistant", menu=ai_menu)
        ai_menu.add_command(label="⚙️ Settings", command=self.show_ai_settings)
        ai_menu.add_separator()
        ai_menu.add_command(label="ℹ️ About AI Assistant", command=self.show_ai_about)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
    
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
    
    def show_privacy_settings(self):
        """Show privacy settings dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Privacy Settings")
        dialog.geometry("500x400")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center the dialog
        dialog.geometry("+%d+%d" % (self.root.winfo_rootx() + 50, self.root.winfo_rooty() + 50))
        
        # Main frame
        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="🔒 Privacy & Upload Settings", font=('Arial', 14, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Current setting
        current_frame = ttk.LabelFrame(main_frame, text="Current Privacy Mode", padding="10")
        current_frame.pack(fill=tk.X, pady=(0, 20))
        
        current_label = ttk.Label(current_frame, text=f"Currently using: {Config.PRIVACY_MODE.upper()} privacy mode")
        current_label.pack()
        
        # Privacy options
        options_frame = ttk.LabelFrame(main_frame, text="Privacy Options", padding="10")
        options_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        privacy_var = tk.StringVar(value=Config.PRIVACY_MODE)
        
        # High privacy option
        high_frame = ttk.Frame(options_frame)
        high_frame.pack(fill=tk.X, pady=5)
        
        ttk.Radiobutton(high_frame, text="🔒 HIGH PRIVACY", variable=privacy_var, value="high").pack(anchor=tk.W)
        ttk.Label(high_frame, text="• Uses base64 data URLs (no external hosting)\n• Most secure but may not work with all APIs\n• Your images never leave your computer", 
                 font=('Arial', 9), foreground='green').pack(anchor=tk.W, padx=20)
        
        # Medium privacy option
        medium_frame = ttk.Frame(options_frame)
        medium_frame.pack(fill=tk.X, pady=5)
        
        ttk.Radiobutton(medium_frame, text="⚠️ MEDIUM PRIVACY", variable=privacy_var, value="medium").pack(anchor=tk.W)
        ttk.Label(medium_frame, text="• Temporary hosting with 1-hour auto-delete\n• Good balance of privacy and compatibility\n• Images automatically removed after processing", 
                 font=('Arial', 9), foreground='orange').pack(anchor=tk.W, padx=20)
        
        # Low privacy option (demo)
        low_frame = ttk.Frame(options_frame)
        low_frame.pack(fill=tk.X, pady=5)
        
        ttk.Radiobutton(low_frame, text="🔓 DEMO MODE", variable=privacy_var, value="low").pack(anchor=tk.W)
        ttk.Label(low_frame, text="• Uses sample images for demonstration\n• Your images are not uploaded anywhere\n• For testing the application interface", 
                 font=('Arial', 9), foreground='blue').pack(anchor=tk.W, padx=20)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        def save_settings():
            Config.PRIVACY_MODE = privacy_var.get()
            try:
                show_success("Settings Saved", f"Privacy mode set to: {Config.PRIVACY_MODE.upper()}")
            except NameError:
                utils.show_success("Settings Saved", f"Privacy mode set to: {Config.PRIVACY_MODE.upper()}")
            dialog.destroy()
        
        ttk.Button(button_frame, text="Save Settings", command=save_settings).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.RIGHT)
    
    def switch_to_editor_with_image(self, image_path):
        """Switch to editor tab and load an image"""
        try:
            # Switch to editor tab
            self.notebook.select(0)  # Editor is tab 0
            
            # Set the image in editor
            if self.editor_tab:
                self.editor_tab.image_selector.selected_path = image_path
                self.editor_tab.image_selector.image_path_label.config(
                    text=os.path.basename(image_path) + " (from upscaler)", 
                    foreground="blue"
                )
                self.editor_tab.on_image_selected(image_path)
                
        except Exception as e:
            show_error("Error", f"Failed to switch to editor: {str(e)}")
    
    def show_about(self):
        """Show about dialog"""
        about_text = """WaveSpeed AI Complete Creative Suite
        
Version: 2.7
Created by: Jackson Weed
        
🆕 Latest Features:
• NEW: Seedream V4 - State-of-the-art image editing surpassing nano banana
• UPGRADED: SeedDance Pro - Now supports both 480p and 720p video generation
• Enhanced User Experience (No popup interruptions)
• Improved Stability & Performance 
• Enhanced Prompt Management for all tabs
• Universal Drag & Drop support
• Fixed Cross-Tab Sharing & File Handling

🤖 AI Models:
• 🍌 Nano Banana Editor - Advanced image editing
• ✨ SeedEdit - Precise image modifications (V3)
• 🌟 Seedream V4 - State-of-the-art multi-modal image generation (NEW!)
• 🔍 Image Upscaler - 2k/4k/8k resolution enhancement
• 🎬 Wan 2.2 - Image to video generation
• 🕺 SeedDance Pro - Professional video generation (480p/720p)

🌟 Seedream V4 Highlights:
• Multi-modal image generation support
• Precise instruction editing with high feature retention
• Deep understanding ability with ultra-fast inference (1.8s for 2K)
• Ultra-high-resolution output up to 4096x4096
• Complex editing operations: object addition/deletion, style changes, etc.

🕺 SeedDance Pro Highlights:
• Dual resolution support: 480p and 720p video generation
• Extended duration options: 5-10 seconds for both versions
• Professional-grade video quality with cinematic effects
• Dynamic camera movement and fixed camera options
• Advanced prompt understanding for complex video scenarios

🎯 Professional Features:
• Real-time Balance Indicator
• Recent Results Panel with visual gallery
• Cross-tab Result Sharing & Workflows
• Resizable UI Sections with keyboard shortcuts
• Enhanced Video Player (YouTube-like experience)
• Auto-save System with organized folders

Powered by WaveSpeed AI APIs
Built with Python, tkinter, and modern UI/UX principles"""
        
        about_window = tk.Toplevel(self.root)
        about_window.title("About WaveSpeed AI")
        about_window.geometry("450x350")  # Slightly larger for new content
        about_window.resizable(False, False)
        
        # Center the window
        about_window.transient(self.root)
        about_window.grab_set()
        
        # Content
        text_widget = tk.Text(about_window, wrap=tk.WORD, padx=20, pady=20)
        text_widget.pack(fill=tk.BOTH, expand=True)
        text_widget.insert("1.0", about_text)
        text_widget.config(state=tk.DISABLED)
        
        # Close button
        close_button = ttk.Button(about_window, text="Close", command=about_window.destroy)
        close_button.pack(pady=10)
    
    def run(self):
        """Run the application"""
        logger.info("Starting WaveSpeed AI Application")
        
        try:
            # Check API key on startup
            if not self.api_client.api_key:
                logger.warning("API key not found")
                show_error(
                    "API Key Missing", 
                    "No API key found. Please set WAVESPEED_API_KEY in your .env file.\n\n"
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
    
    def show_ai_settings(self):
        """Show AI assistant settings dialog"""
        try:
            from ui.components.enhanced_ai_suggestions import show_ai_settings
            show_ai_settings(self.root)
        except ImportError:
            from tkinter import messagebox
            messagebox.showinfo("AI Assistant", 
                              "AI Assistant settings are not available.\n\n"
                              "Please ensure the enhanced AI components are properly installed.")
    
    def show_ai_about(self):
        """Show AI assistant information"""
        from tkinter import messagebox
        about_text = """🤖 AI Prompt Assistant

Powered by Claude (Anthropic) and OpenAI GPT-4

Features:
• ✨ Improve existing prompts for better results
• 💡 Generate creative prompt ideas  
• 🎯 Tab-specific optimization for each AI model
• 🧠 Context-aware suggestions
• ⚙️ Configurable settings and preferences

Setup:
1. Add API keys to your .env file:
   - CLAUDE_API_KEY=your_claude_key
   - OPENAI_API_KEY=your_openai_key

2. Restart the application

3. Use "✨ Improve with AI" buttons in any tab

The AI Assistant helps you create more effective prompts that lead to better AI generations!"""
        
        messagebox.showinfo("AI Assistant", about_text)
    
    def on_closing(self):
        """Handle application closing"""
        try:
            logger.info("Application closing - cleaning up resources")
            
            # Stop balance indicator updates
            if hasattr(self, 'balance_indicator'):
                self.balance_indicator.destroy()
            
            # Cleanup recent results panel
            if hasattr(self, 'recent_results_panel'):
                self.recent_results_panel.destroy()
            
            # Save splitter position before closing
            self.save_splitter_position()
            
            resource_manager.cleanup_all()
            self.root.quit()
            self.root.destroy()
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")
            self.root.quit()
    
    def collapse_sidebar(self, event=None):
        """Collapse the sidebar to minimum size"""
        if hasattr(self, 'paned_window'):
            self.paned_window.paneconfigure(self.recent_results_frame, width=150)
    
    def expand_sidebar(self, event=None):
        """Expand the sidebar to larger size"""
        if hasattr(self, 'paned_window'):
            self.paned_window.paneconfigure(self.recent_results_frame, width=300)
    
    def reset_splitter(self, event=None):
        """Reset splitter to default position"""
        if hasattr(self, 'paned_window'):
            self.paned_window.paneconfigure(self.recent_results_frame, width=200)
    
    def save_splitter_position(self):
        """Save current splitter position to config"""
        try:
            if hasattr(self, 'paned_window'):
                # Get current sash position (splitter position)
                sash_pos = self.paned_window.sash_coord(0)[0]  # Get x-coordinate of first sash
                
                # Save to a simple config file
                config_file = "ui_layout.conf"
                with open(config_file, 'w') as f:
                    f.write(f"splitter_position={sash_pos}\n")
                
                logger.info(f"Saved splitter position: {sash_pos}")
        except Exception as e:
            logger.error(f"Error saving splitter position: {e}")
    
    def load_splitter_position(self):
        """Load saved splitter position from config"""
        try:
            config_file = "ui_layout.conf"
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    for line in f:
                        if line.startswith("splitter_position="):
                            pos = int(line.split("=")[1].strip())
                            # Apply the position after a short delay to ensure UI is ready
                            self.root.after(100, lambda: self.paned_window.sash_place(0, pos, 0))
                            logger.info(f"Loaded splitter position: {pos}")
                            break
        except Exception as e:
            logger.error(f"Error loading splitter position: {e}")


def main():
    """Main entry point"""
    app = WaveSpeedAIApp()
    app.run()


if __name__ == "__main__":
    main()
