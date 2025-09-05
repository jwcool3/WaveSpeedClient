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
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Title
        title_label = ttk.Label(
            main_frame, 
            text="WaveSpeed AI - Image Editor, Upscaler & Video Generator", 
            font=('Arial', 16, 'bold')
        )
        title_label.grid(row=0, column=0, pady=(0, 20))
        
        # API Key status
        api_status = "✓ API Key loaded" if self.api_client.api_key else "✗ API Key not found"
        api_color = "green" if self.api_client.api_key else "red"
        api_label = tk.Label(
            main_frame, text=api_status, fg=api_color, 
            bg='#f0f0f0', font=('Arial', 10)
        )
        api_label.grid(row=1, column=0, pady=(0, 10))
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        
        # Create tabs
        self.setup_tabs()
        
        # Setup menu
        self.setup_menu()
    
    def setup_tabs(self):
        """Setup all application tabs"""
        # Image Editor Tab
        self.editor_tab = ImageEditorTab(self.notebook, self.api_client)
        self.notebook.add(self.editor_tab.container, text="🎨 Image Editor")
        
        # SeedEdit Tab
        self.seededit_tab = SeedEditTab(self.notebook, self.api_client, self)
        self.notebook.add(self.seededit_tab.container, text="✨ SeedEdit")
        
        # Image Upscaler Tab
        self.upscaler_tab = ImageUpscalerTab(self.notebook, self.api_client, self)
        self.notebook.add(self.upscaler_tab.container, text="🔍 Image Upscaler")
        
        # Image to Video Tab
        self.video_tab = ImageToVideoTab(self.notebook, self.api_client, self)
        self.notebook.add(self.video_tab.container, text="🎬 Image to Video")
        
        # SeedDance Tab
        self.seeddance_tab = SeedDanceTab(self.notebook, self.api_client, self)
        self.notebook.add(self.seeddance_tab.container, text="🕺 SeedDance")
    
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
        tools_menu.add_command(label="Switch to Upscaler", command=lambda: self.switch_to_tab(2))
        tools_menu.add_command(label="Switch to Video Generator", command=lambda: self.switch_to_tab(3))
        tools_menu.add_command(label="Switch to SeedDance", command=lambda: self.switch_to_tab(4))
        
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
        about_text = """WaveSpeed AI GUI Application
        
Version: 2.2
        
Features:
• Image Editing with AI prompts
• SeedEdit - Precise image modifications
• Image Upscaling (2K, 4K, 8K)
• Image to Video Generation (WAN-2.2)
• SeedDance - Pro video generation
• Drag & Drop Support
• Cross-tab Workflows

Powered by WaveSpeed AI APIs
        
Created with Python and tkinter"""
        
        about_window = tk.Toplevel(self.root)
        about_window.title("About WaveSpeed AI")
        about_window.geometry("400x300")
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
    
    def on_closing(self):
        """Handle application closing"""
        try:
            logger.info("Application closing - cleaning up resources")
            resource_manager.cleanup_all()
            self.root.quit()
            self.root.destroy()
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")
            self.root.quit()


def main():
    """Main entry point"""
    app = WaveSpeedAIApp()
    app.run()


if __name__ == "__main__":
    main()
