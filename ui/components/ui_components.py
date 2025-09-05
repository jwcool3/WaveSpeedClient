"""
UI Components for WaveSpeed AI GUI Application

This module contains reusable UI components and base classes.
"""

import tkinter as tk
from tkinter import ttk
import threading
from abc import ABC, abstractmethod
from core.api_client import WaveSpeedAPIClient
from utils.utils import *

# Try to import drag and drop support
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    DND_AVAILABLE = True
except ImportError:
    DND_AVAILABLE = False


class BaseTab(ABC):
    """Base class for all tabs in the application"""
    
    def __init__(self, parent_frame, api_client):
        # Create main container frame
        self.container = ttk.Frame(parent_frame)
        self.container.pack(fill=tk.BOTH, expand=True)
        
        # Create scrollable canvas
        self.canvas = tk.Canvas(self.container, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.container, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        # Configure scrolling
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        # Create window in canvas
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        
        # Configure canvas scrolling
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Pack canvas and scrollbar
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # Bind canvas resize
        self.canvas.bind('<Configure>', self._on_canvas_configure)
        
        # Bind mouse wheel scrolling
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        
        # The actual content frame (with padding)
        self.frame = ttk.Frame(self.scrollable_frame, padding="10")
        self.frame.pack(fill=tk.BOTH, expand=True)
        
        # Configure main frame column weights for responsiveness
        self.frame.columnconfigure(0, weight=1)
        self.frame.columnconfigure(1, weight=1)
        
        # Create sticky button frame at the bottom of the main container
        self.button_frame = ttk.Frame(self.container, padding="10")
        self.button_frame.pack(side="bottom", fill="x")
        self.button_frame.columnconfigure(0, weight=1)
        
        self.api_client = api_client
        self.current_request_id = None
        self.selected_image_path = None
        self.original_image = None
        self.result_data = None
        
        # UI elements (to be set by subclasses)
        self.progress_frame = None
        self.progress_bar = None
        self.status_label = None
        self.results_frame = None
        self.result_text = None
        self.process_button = None
        
        self.setup_ui()
        
    def _on_canvas_configure(self, event):
        """Handle canvas resize"""
        # Update the scrollable frame width to match canvas width
        canvas_width = event.width
        self.canvas.itemconfig(self.canvas_window, width=canvas_width)
    
    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling"""
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def setup_sticky_buttons(self, buttons_config):
        """
        Setup sticky buttons at the bottom of the tab
        
        Args:
            buttons_config: List of tuples (text, command, style)
        """
        # Clear any existing buttons
        for widget in self.button_frame.winfo_children():
            widget.destroy()
        
        # Create button container
        button_container = ttk.Frame(self.button_frame)
        button_container.pack(expand=True)
        
        # Add buttons
        for i, (text, command, style) in enumerate(buttons_config):
            if style == "primary":
                btn = ttk.Button(button_container, text=text, command=command)
                btn.configure(style="Accent.TButton")  # Use accent style for primary buttons
            else:
                btn = ttk.Button(button_container, text=text, command=command)
            
            btn.pack(side="left", padx=5, pady=5)
            
            # Store reference to process button if it's the main action
            if "process" in text.lower() or "apply" in text.lower() or "generate" in text.lower() or "upscale" in text.lower():
                self.process_button = btn
    
    @abstractmethod
    def setup_ui(self):
        """Setup the UI for this tab"""
        pass
    
    @abstractmethod
    def process_task(self):
        """Process the main task for this tab"""
        pass
    
    def setup_progress_section(self, row):
        """Setup common progress section"""
        self.progress_frame = ttk.LabelFrame(self.frame, text="Progress", padding="10")
        self.progress_frame.grid(row=row, column=0, columnspan=2, 
                                sticky=(tk.W, tk.E), pady=(0, 10))
        self.progress_frame.columnconfigure(0, weight=1)
        
        self.progress_bar = ttk.Progressbar(self.progress_frame, mode='indeterminate')
        self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        
        self.status_label = ttk.Label(self.progress_frame, text="Ready")
        self.status_label.grid(row=1, column=0, sticky=tk.W)
        
        # Initially hide progress
        self.progress_frame.grid_remove()
    
    def setup_results_section(self, row):
        """Setup common results section"""
        self.results_frame = ttk.LabelFrame(self.frame, text="Results", padding="10")
        self.results_frame.grid(row=row, column=0, columnspan=2, 
                               sticky=(tk.W, tk.E), pady=(0, 10))
        self.results_frame.columnconfigure(0, weight=1)
        
        self.result_text = tk.Text(self.results_frame, height=4, wrap=tk.WORD, 
                                  font=('Arial', 10), state=tk.DISABLED)
        self.result_text.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        result_scroll = ttk.Scrollbar(self.results_frame, orient="vertical", 
                                     command=self.result_text.yview)
        result_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.result_text.configure(yscrollcommand=result_scroll.set)
        
        # Initially hide results
        self.results_frame.grid_remove()
    
    def show_progress(self, message="Processing..."):
        """Show progress section with message"""
        self.progress_frame.grid()
        self.results_frame.grid_remove()
        self.progress_bar.start()
        self.status_label.config(text=message)
        if self.process_button:
            self.process_button.config(state="disabled")
    
    def hide_progress(self):
        """Hide progress section"""
        self.progress_bar.stop()
        self.progress_frame.grid_remove()
        if self.process_button:
            self.process_button.config(state="normal")
    
    def show_results(self, message, is_success=True):
        """Show results section with message"""
        self.hide_progress()
        self.results_frame.grid()
        
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete("1.0", tk.END)
        
        prefix = "✓" if is_success else "✗"
        self.result_text.insert("1.0", f"{prefix} {message}")
        self.result_text.config(state=tk.DISABLED)
    
    def update_status(self, message):
        """Update status label"""
        if self.status_label:
            self.status_label.config(text=message)
    
    def validate_inputs(self):
        """Validate inputs before processing"""
        if not self.api_client.api_key:
            show_error("Error", "API key not found. Please set WAVESPEED_API_KEY in your .env file.")
            return False
        
        if not self.selected_image_path:
            show_error("Error", "Please select an image first.")
            return False
        
        return True


class ImageSelector:
    """Reusable image selector component"""
    
    def __init__(self, parent_frame, row, callback, title="Select Image:"):
        self.parent_frame = parent_frame
        self.callback = callback
        self.selected_path = None
        
        # Image selection section
        ttk.Label(parent_frame, text=title, font=('Arial', 12, 'bold')).grid(
            row=row, column=0, sticky=tk.W, pady=(10, 5))
        
        image_frame = ttk.Frame(parent_frame)
        image_frame.grid(row=row+1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        image_frame.columnconfigure(1, weight=1)
        
        self.select_button = ttk.Button(image_frame, text="Browse Image", 
                                       command=self.select_image)
        self.select_button.grid(row=0, column=0, padx=(0, 10))
        
        self.image_path_label = ttk.Label(image_frame, text="No image selected", 
                                         foreground="gray")
        self.image_path_label.grid(row=0, column=1, sticky=(tk.W, tk.E))
    
    def select_image(self):
        """Select image file"""
        file_path = filedialog.askopenfilename(
            title="Select an image",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.gif *.bmp *.webp"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            is_valid, error = validate_image_file(file_path)
            if not is_valid:
                show_error("Invalid File", error)
                return
            
            self.selected_path = file_path
            self.image_path_label.config(text=os.path.basename(file_path), 
                                        foreground="black")
            if self.callback:
                self.callback(file_path)


class ImagePreview:
    """Reusable image preview component"""
    
    def __init__(self, parent_frame, row, title="Images"):
        self.parent_frame = parent_frame
        
        # Image preview section
        self.images_frame = ttk.LabelFrame(parent_frame, text=title, padding="10")
        self.images_frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        self.images_frame.columnconfigure(0, weight=1)
        self.images_frame.columnconfigure(1, weight=1)
        
        # Original image section
        self.original_frame = ttk.LabelFrame(self.images_frame, text="Original Image", padding="5")
        self.original_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        
        # Drop zone
        self.drop_frame = tk.Frame(self.original_frame, bg='#f8f8f8', relief='groove', bd=2)
        self.drop_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.original_image_label = tk.Label(
            self.drop_frame, 
            text="📁 Click 'Browse Image' to select\n\nSupported formats: PNG, JPG, JPEG, GIF, BMP, WebP", 
            bg='#f8f8f8', fg='#666666', font=('Arial', 10)
        )
        self.original_image_label.pack(expand=True)
        
        # Result section
        self.result_frame = ttk.LabelFrame(self.images_frame, text="Result", padding="5")
        self.result_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0))
        
        self.result_image_label = ttk.Label(self.result_frame, text="No result yet")
        self.result_image_label.pack()
    
    def update_original_image(self, image_path):
        """Update original image preview"""
        photo, original, error = load_image_preview(image_path)
        if error:
            self.original_image_label.config(text=error, image="")
            self.original_image_label.image = None
            return None
        
        self.original_image_label.config(image=photo, text="")
        self.original_image_label.image = photo
        
        # Clear result (with safety check)
        try:
            if hasattr(self, 'result_image_label') and self.result_image_label.winfo_exists():
                self.result_image_label.config(text="No result yet", image="")
                self.result_image_label.image = None
        except tk.TclError:
            # Widget was destroyed, ignore
            pass
        
        return original
    
    def update_result_image(self, image_url=None, image=None):
        """Update result image preview"""
        if image_url:
            image, error = download_image_from_url(image_url)
            if error:
                self.result_image_label.config(text=error)
                return None
        
        if image:
            # Create thumbnail for display
            display_image = image.copy()
            max_size = (350, 250)
            display_image.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            photo = ImageTk.PhotoImage(display_image)
            self.result_image_label.config(image=photo, text="")
            self.result_image_label.image = photo
            
            return image
        
        return None
    
    def setup_drag_and_drop(self, callback):
        """Setup drag and drop for the drop zone"""
        if not DND_AVAILABLE:
            return
        
        try:
            self.drop_frame.drop_target_register(DND_FILES)
            self.drop_frame.dnd_bind('<<Drop>>', callback)
            
            # Visual feedback
            self.drop_frame.bind('<Enter>', self._on_hover_enter)
            self.drop_frame.bind('<Leave>', self._on_hover_leave)
            
        except Exception as e:
            print(f"Drag and drop setup failed: {e}")
    
    def _on_hover_enter(self, event):
        """Visual feedback on hover"""
        self.drop_frame.config(bg='#f0f8ff', relief='solid')
    
    def _on_hover_leave(self, event):
        """Visual feedback on hover leave"""
        self.drop_frame.config(bg='#f8f8f8', relief='groove')


class SettingsPanel:
    """Reusable settings panel component"""
    
    def __init__(self, parent_frame, row, title="Settings"):
        self.parent_frame = parent_frame
        self.settings = {}
        
        self.settings_frame = ttk.LabelFrame(parent_frame, text=title, padding="10")
        self.settings_frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 10))
        self.settings_frame.columnconfigure(0, weight=1)
        
        self.grid_frame = ttk.Frame(self.settings_frame)
        self.grid_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        self.current_row = 0
        self.current_col = 0
    
    def add_combobox(self, label, variable, values, default=None, width=10):
        """Add a combobox setting"""
        ttk.Label(self.grid_frame, text=f"{label}:", font=('Arial', 10, 'bold')).grid(
            row=self.current_row, column=self.current_col, sticky=tk.W, 
            padx=(0, 10), pady=(0, 10))
        
        if default:
            variable.set(default)
        
        combo = ttk.Combobox(self.grid_frame, textvariable=variable, 
                           values=values, state="readonly", width=width)
        combo.grid(row=self.current_row, column=self.current_col + 1, 
                  sticky=tk.W, pady=(0, 10))
        
        self.settings[label] = variable
        self._advance_position()
        
        return combo
    
    def add_text_field(self, label, variable, width=20):
        """Add a text field setting"""
        ttk.Label(self.grid_frame, text=f"{label}:", font=('Arial', 10, 'bold')).grid(
            row=self.current_row, column=self.current_col, sticky=tk.W, 
            padx=(0, 10), pady=(0, 10))
        
        entry = ttk.Entry(self.grid_frame, textvariable=variable, width=width)
        entry.grid(row=self.current_row, column=self.current_col + 1, 
                  sticky=tk.W, pady=(0, 10))
        
        self.settings[label] = variable
        self._advance_position()
        
        return entry
    
    def _advance_position(self):
        """Advance grid position"""
        if self.current_col >= 2:  # Move to next row after 2 columns
            self.current_row += 1
            self.current_col = 0
        else:
            self.current_col += 2  # Skip one column for spacing
    
    def get_value(self, label):
        """Get setting value by label"""
        if label in self.settings:
            return self.settings[label].get()
        return None
