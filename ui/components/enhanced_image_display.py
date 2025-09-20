"""
Enhanced Image Display Components for WaveSpeed AI Application

This module provides improved image display functionality with larger previews,
expandable views, and better user interaction.
"""

import tkinter as tk
from tkinter import ttk
import os
from PIL import Image, ImageTk
from utils.utils import load_image_preview, download_image_from_url, validate_image_file, show_error
from tkinter import filedialog

# Try to import drag and drop support
try:
    from tkinterdnd2 import DND_FILES
    DND_AVAILABLE = True
except ImportError:
    DND_AVAILABLE = False


class ExpandableImageViewer:
    """Full-screen expandable image viewer"""
    
    def __init__(self, parent, image, title="Image Viewer"):
        self.parent = parent
        self.image = image
        self.title = title
        
        # Create top-level window
        self.window = tk.Toplevel(parent)
        self.window.title(title)
        self.window.geometry("800x600")
        self.window.configure(bg='black')
        
        # Center the window
        self.center_window()
        
        # Make it modal
        self.window.transient(parent)
        self.window.grab_set()
        
        # Create UI
        self.setup_ui()
        
        # Bind keys
        self.window.bind('<Escape>', lambda e: self.close())
        self.window.bind('<Return>', lambda e: self.close())
        self.window.bind('<space>', lambda e: self.close())
        
        # Focus the window
        self.window.focus_set()
    
    def center_window(self):
        """Center the window on screen"""
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f"{width}x{height}+{x}+{y}")
    
    def setup_ui(self):
        """Setup the viewer UI"""
        # Main frame
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Image frame with scrollbars
        self.setup_scrollable_image(main_frame)
        
        # Control frame
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Info label
        image_info = f"Size: {self.image.size[0]} x {self.image.size[1]} pixels"
        info_label = ttk.Label(control_frame, text=image_info)
        info_label.pack(side=tk.LEFT)
        
        # Buttons
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(side=tk.RIGHT)
        
        ttk.Button(button_frame, text="Save Image", command=self.save_image).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Close (ESC)", command=self.close).pack(side=tk.LEFT)
    
    def setup_scrollable_image(self, parent):
        """Setup scrollable image display"""
        # Create canvas with scrollbars
        canvas_frame = ttk.Frame(parent)
        canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(canvas_frame, bg='white', highlightthickness=0)
        v_scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=self.canvas.yview)
        h_scrollbar = ttk.Scrollbar(canvas_frame, orient="horizontal", command=self.canvas.xview)
        
        self.canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack scrollbars and canvas
        v_scrollbar.pack(side="right", fill="y")
        h_scrollbar.pack(side="bottom", fill="x")
        self.canvas.pack(side="left", fill="both", expand=True)
        
        # Display image at full resolution (up to screen size)
        self.display_image()
        
        # Bind mouse wheel
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind("<Button-4>", self._on_mousewheel)
        self.canvas.bind("<Button-5>", self._on_mousewheel)
    
    def display_image(self):
        """Display the image in the canvas"""
        # Get screen dimensions
        screen_width = self.window.winfo_screenwidth() - 100
        screen_height = self.window.winfo_screenheight() - 200
        
        # Calculate display size (maintain aspect ratio)
        img_width, img_height = self.image.size
        scale_w = screen_width / img_width
        scale_h = screen_height / img_height
        scale = min(scale_w, scale_h, 1.0)  # Don't upscale beyond original
        
        if scale < 1.0:
            new_width = int(img_width * scale)
            new_height = int(img_height * scale)
            display_image = self.image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        else:
            display_image = self.image
        
        # Convert to PhotoImage
        self.photo = ImageTk.PhotoImage(display_image)
        
        # Add to canvas
        self.canvas.create_image(0, 0, anchor="nw", image=self.photo)
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling"""
        if event.delta:
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        elif event.num == 4:
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            self.canvas.yview_scroll(1, "units")
    
    def save_image(self):
        """Save the image"""
        file_path = filedialog.asksaveasfilename(
            title="Save Image",
            defaultextension=".png",
            filetypes=[
                ("PNG files", "*.png"),
                ("JPEG files", "*.jpg"),
                ("WebP files", "*.webp"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            try:
                # Determine format
                ext = os.path.splitext(file_path)[1].lower()
                format_map = {
                    '.png': 'PNG',
                    '.jpg': 'JPEG',
                    '.jpeg': 'JPEG',
                    '.webp': 'WEBP'
                }
                save_format = format_map.get(ext, 'PNG')
                
                self.image.save(file_path, format=save_format)
                
                # Show success message briefly
                original_text = self.window.title()
                self.window.title(f"✅ Saved: {os.path.basename(file_path)}")
                self.window.after(2000, lambda: self.window.title(original_text))
                
            except Exception as e:
                show_error("Save Error", f"Failed to save image: {str(e)}")
    
    def close(self):
        """Close the viewer"""
        self.window.destroy()


class EnhancedImageSelector:
    """Enhanced image selector with smaller preview"""
    
    def __init__(self, parent_frame, row, callback, title="Select Image:", show_preview=True):
        self.parent_frame = parent_frame
        self.callback = callback
        self.selected_path = None
        self.show_preview = show_preview
        
        # Image selection section
        ttk.Label(parent_frame, text=title, font=('Arial', 12, 'bold')).grid(
            row=row, column=0, sticky=tk.W, pady=(10, 5))
        
        # Selection controls
        selection_frame = ttk.Frame(parent_frame)
        selection_frame.grid(row=row+1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 5))
        selection_frame.columnconfigure(1, weight=1)
        
        self.select_button = ttk.Button(selection_frame, text="Browse Image", 
                                       command=self.select_image)
        self.select_button.grid(row=0, column=0, padx=(0, 10))
        
        self.image_path_label = ttk.Label(selection_frame, text="No image selected", 
                                         foreground="gray")
        self.image_path_label.grid(row=0, column=1, sticky=(tk.W, tk.E))
        
        # Small preview (optional)
        if self.show_preview:
            self.preview_frame = ttk.Frame(parent_frame)
            self.preview_frame.grid(row=row+2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
            
            self.preview_label = tk.Label(
                self.preview_frame,
                text="📁 No image selected",
                bg='#f8f8f8', fg='#666666', font=('Arial', 9),
                relief='groove', bd=1, width=30, height=8
            )
            self.preview_label.grid(row=0, column=0, padx=(0, 10), sticky=(tk.W, tk.E, tk.N, tk.S))
            
            # Setup drag and drop on preview
            self.setup_drag_and_drop()
        else:
            self.preview_label = None
    
    def setup_drag_and_drop(self):
        """Setup drag and drop functionality"""
        if not DND_AVAILABLE or not self.preview_label:
            return
        
        try:
            self.preview_label.drop_target_register(DND_FILES)
            self.preview_label.dnd_bind('<<Drop>>', self.on_drop)
            self.preview_label.dnd_bind('<<DragEnter>>', self.on_drag_enter)
            self.preview_label.dnd_bind('<<DragLeave>>', self.on_drag_leave)
        except Exception as e:
            print(f"Drag and drop setup failed: {e}")
    
    def on_drop(self, event):
        """Handle file drop"""
        from utils import parse_drag_drop_data
        success, file_path = parse_drag_drop_data(event.data)
        
        if success:
            is_valid, error = validate_image_file(file_path)
            if is_valid:
                self.selected_path = file_path
                self.update_display(file_path)
                if self.callback:
                    self.callback(file_path)
            else:
                show_error("Invalid File", error)
        else:
            show_error("Drop Error", file_path)
    
    def on_drag_enter(self, event):
        """Handle drag enter"""
        if self.preview_label:
            self.preview_label.config(bg='#e8f4f8')
    
    def on_drag_leave(self, event):
        """Handle drag leave"""
        if self.preview_label:
            self.preview_label.config(bg='#f8f8f8')
    
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
            self.update_display(file_path)
            if self.callback:
                self.callback(file_path)
    
    def update_display(self, file_path):
        """Update the display with selected image"""
        # Update path label
        self.image_path_label.config(text=os.path.basename(file_path), foreground="black")
        
        # Update small preview if enabled
        if self.show_preview and self.preview_label:
            photo, _, error = load_image_preview(file_path, max_size=(120, 80))
            if error:
                self.preview_label.config(text=f"Error: {error}", image="", bg='#ffe6e6')
                self.preview_label.image = None
            else:
                self.preview_label.config(image=photo, text="", bg='#f8f8f8')
                self.preview_label.image = photo


class EnhancedImagePreview:
    """Enhanced image preview with larger result display and expandable view"""
    
    def __init__(self, parent_frame, row, title="Images", result_size=(500, 400)):
        self.parent_frame = parent_frame
        self.result_size = result_size
        self.current_result_image = None
        
        # Image preview section
        self.images_frame = ttk.LabelFrame(parent_frame, text=title, padding="10")
        self.images_frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        self.images_frame.columnconfigure(1, weight=1)  # Result column gets more space
        
        # Original image section (smaller)
        self.original_frame = ttk.LabelFrame(self.images_frame, text="Input", padding="5")
        self.original_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N), padx=(0, 10))
        
        # Small input preview
        self.original_image_label = tk.Label(
            self.original_frame,
            text="📁 Input image\nwill appear here",
            bg='#f8f8f8', fg='#666666', font=('Arial', 9),
            width=20, height=10, relief='groove', bd=1
        )
        self.original_image_label.grid(row=0, column=0, padx=5, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Result section (larger)
        self.result_frame = ttk.LabelFrame(self.images_frame, text="Result", padding="5")
        self.result_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 0))
        
        # Large result display
        self.result_image_label = tk.Label(
            self.result_frame,
            text="🎨 Result will appear here\n\n💡 Double-click to view full size",
            bg='white', fg='#666666', font=('Arial', 11),
            relief='groove', bd=1, cursor='hand2'
        )
        self.result_image_label.grid(row=0, column=0, padx=5, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Bind double-click to expand
        self.result_image_label.bind('<Double-Button-1>', self.expand_result_image)
        self.result_image_label.bind('<Button-3>', self.show_context_menu)  # Right-click menu
        
        # Setup drag and drop for original image
        self.setup_drag_and_drop()
    
    def setup_drag_and_drop(self, callback=None):
        """Setup drag and drop for the original image area"""
        self.drop_callback = callback
        
        if not DND_AVAILABLE:
            return
        
        try:
            self.original_image_label.drop_target_register(DND_FILES)
            self.original_image_label.dnd_bind('<<Drop>>', self.on_drop)
            self.original_image_label.dnd_bind('<<DragEnter>>', self.on_drag_enter)
            self.original_image_label.dnd_bind('<<DragLeave>>', self.on_drag_leave)
        except Exception as e:
            print(f"Drag and drop setup failed: {e}")
    
    def on_drop(self, event):
        """Handle file drop on original image area"""
        if self.drop_callback:
            self.drop_callback(event)
    
    def on_drag_enter(self, event):
        """Handle drag enter"""
        self.original_image_label.config(bg='#e8f4f8')
    
    def on_drag_leave(self, event):
        """Handle drag leave"""
        self.original_image_label.config(bg='#f8f8f8')
    
    def update_original_image(self, image_path):
        """Update original image preview (small)"""
        photo, original, error = load_image_preview(image_path, max_size=(150, 120))
        if error:
            self.original_image_label.config(text=f"Error loading image:\n{error}", image="", bg='#ffe6e6')
            self.original_image_label.image = None
            return None
        
        self.original_image_label.config(image=photo, text="", bg='#f8f8f8')
        self.original_image_label.image = photo
        
        # Clear result
        self.result_image_label.config(
            text="🎨 Processing...\n\n💡 Result will appear here",
            image="", bg='white'
        )
        self.result_image_label.image = None
        self.current_result_image = None
        
        return original
    
    def update_result_image(self, image_url=None, image=None):
        """Update result image preview (large)"""
        if image_url:
            image, error = download_image_from_url(image_url)
            if error:
                self.result_image_label.config(
                    text=f"❌ Error loading result:\n{error}",
                    bg='#ffe6e6'
                )
                return None
        
        if image:
            # Store full image for expansion
            self.current_result_image = image
            
            # Create larger thumbnail for display
            display_image = image.copy()
            display_image.thumbnail(self.result_size, Image.Resampling.LANCZOS)
            
            photo = ImageTk.PhotoImage(display_image)
            self.result_image_label.config(
                image=photo, text="",
                bg='white', cursor='hand2'
            )
            self.result_image_label.image = photo
            
            return image
        
        return None
    
    def expand_result_image(self, event=None):
        """Expand result image to full screen viewer"""
        if self.current_result_image:
            viewer = ExpandableImageViewer(
                self.parent_frame,
                self.current_result_image,
                "WaveSpeed AI - Result Image"
            )
    
    def show_context_menu(self, event):
        """Show right-click context menu"""
        if not self.current_result_image:
            return
        
        menu = tk.Menu(self.parent_frame, tearoff=0)
        menu.add_command(label="🔍 View Full Size", command=self.expand_result_image)
        menu.add_command(label="💾 Save Image", command=self.save_result_image)
        
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()
    
    def save_result_image(self):
        """Save the result image"""
        if self.current_result_image:
            from utils import save_image_dialog
            file_path, error = save_image_dialog(self.current_result_image, "Save Result Image")
            if file_path:
                # Show brief success message
                original_text = self.result_image_label.cget('text')
                self.result_image_label.config(text=f"✅ Saved: {os.path.basename(file_path)}")
                self.parent_frame.after(2000, lambda: self.result_image_label.config(text=original_text))
