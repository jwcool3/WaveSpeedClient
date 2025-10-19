"""
Image Editor Utilities

Provides image editing tools for preprocessing input images:
- Crop tool with visual selection
- Resize tool with aspect ratio options
- Quick presets for common operations
"""

import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk, ImageDraw
import os
from typing import Optional, Tuple, Callable
from core.logger import get_logger

logger = get_logger()


class ImageCropTool:
    """Interactive crop tool with visual selection"""
    
    def __init__(self, parent, image_path: str, callback: Callable):
        """
        Initialize crop tool
        
        Args:
            parent: Parent window
            image_path: Path to image to crop
            callback: Callback function(cropped_image_path)
        """
        self.parent = parent
        self.image_path = image_path
        self.callback = callback
        
        # Load original image
        try:
            self.original_image = Image.open(image_path)
            self.image_width, self.image_height = self.original_image.size
        except Exception as e:
            logger.error(f"Failed to load image for cropping: {e}")
            messagebox.showerror("Error", f"Failed to load image: {str(e)}")
            return
        
        # Crop selection state
        self.crop_start = None
        self.crop_end = None
        self.crop_rect = None
        
        # Aspect ratio state
        self.lock_aspect = tk.BooleanVar(value=False)
        self.aspect_ratio = None  # Will be set based on selection
        
        # Create dialog
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Crop Image")
        self.dialog.geometry("900x750")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self._create_ui()
    
    def _create_ui(self):
        """Create crop tool UI"""
        # Instructions
        instructions = ttk.Label(
            self.dialog,
            text="Click and drag to select crop area. Use aspect ratio presets to constrain proportions.",
            font=('Arial', 10)
        )
        instructions.pack(pady=10)
        
        # Canvas for image display
        canvas_frame = ttk.Frame(self.dialog)
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Calculate display size (fit to 800x550)
        max_display_width = 800
        max_display_height = 550
        
        scale = min(max_display_width / self.image_width, 
                   max_display_height / self.image_height, 1.0)
        
        self.display_width = int(self.image_width * scale)
        self.display_height = int(self.image_height * scale)
        self.scale_factor = scale
        
        self.canvas = tk.Canvas(
            canvas_frame,
            width=self.display_width,
            height=self.display_height,
            bg='gray',
            cursor='crosshair'
        )
        self.canvas.pack()
        
        # Display image
        display_image = self.original_image.resize(
            (self.display_width, self.display_height),
            Image.Resampling.LANCZOS
        )
        self.photo = ImageTk.PhotoImage(display_image)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)
        
        # Bind mouse events
        self.canvas.bind('<ButtonPress-1>', self._on_mouse_down)
        self.canvas.bind('<B1-Motion>', self._on_mouse_drag)
        self.canvas.bind('<ButtonRelease-1>', self._on_mouse_up)
        
        # Info label
        self.info_label = ttk.Label(self.dialog, text="No selection", font=('Arial', 9))
        self.info_label.pack(pady=5)
        
        # Aspect ratio controls
        aspect_frame = ttk.LabelFrame(self.dialog, text="Aspect Ratio Options", padding="10")
        aspect_frame.pack(pady=10, padx=10, fill=tk.X)
        
        # Lock aspect ratio checkbox
        lock_frame = ttk.Frame(aspect_frame)
        lock_frame.pack(fill=tk.X, pady=5)
        
        ttk.Checkbutton(
            lock_frame,
            text="Lock Aspect Ratio",
            variable=self.lock_aspect,
            command=self._on_lock_aspect_changed
        ).pack(side=tk.LEFT)
        
        # Aspect ratio presets
        preset_frame = ttk.Frame(aspect_frame)
        preset_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(preset_frame, text="Preset:").pack(side=tk.LEFT, padx=(0, 5))
        
        self.aspect_preset_var = tk.StringVar(value="Free")
        aspect_combo = ttk.Combobox(
            preset_frame,
            textvariable=self.aspect_preset_var,
            values=["Free", "Original", "1:1 (Square)", "16:9", "9:16", "4:3", "3:4", "3:2", "2:3"],
            state="readonly",
            width=20
        )
        aspect_combo.pack(side=tk.LEFT, padx=5)
        aspect_combo.bind('<<ComboboxSelected>>', self._on_aspect_preset_changed)
        
        # Buttons
        btn_frame = ttk.Frame(self.dialog)
        btn_frame.pack(pady=10)
        
        ttk.Button(
            btn_frame,
            text="Apply Crop",
            command=self._apply_crop,
            width=15
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            btn_frame,
            text="Reset Selection",
            command=self._reset_selection,
            width=15
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            btn_frame,
            text="Cancel",
            command=self.dialog.destroy,
            width=15
        ).pack(side=tk.LEFT, padx=5)
    
    def _on_mouse_down(self, event):
        """Handle mouse down event"""
        self.crop_start = (event.x, event.y)
        self.crop_end = None
        
        # Clear previous rectangle
        if self.crop_rect:
            self.canvas.delete(self.crop_rect)
            self.crop_rect = None
    
    def _on_mouse_drag(self, event):
        """Handle mouse drag event"""
        if not self.crop_start:
            return
        
        # Constrain to canvas bounds
        x = max(0, min(event.x, self.display_width))
        y = max(0, min(event.y, self.display_height))
        
        # Apply aspect ratio constraint if locked
        if self.lock_aspect.get() and self.aspect_ratio:
            x, y = self._constrain_to_aspect_ratio(
                self.crop_start[0], self.crop_start[1], x, y
            )
        
        # Update end position
        self.crop_end = (x, y)
        
        # Clear previous rectangle
        if self.crop_rect:
            self.canvas.delete(self.crop_rect)
        
        # Draw selection rectangle
        self.crop_rect = self.canvas.create_rectangle(
            self.crop_start[0], self.crop_start[1],
            x, y,
            outline='yellow',
            width=2
        )
        
        # Update info
        self._update_info()
    
    def _on_mouse_up(self, event):
        """Handle mouse up event"""
        if self.crop_start:
            x = max(0, min(event.x, self.display_width))
            y = max(0, min(event.y, self.display_height))
            
            # Apply aspect ratio constraint if locked
            if self.lock_aspect.get() and self.aspect_ratio:
                x, y = self._constrain_to_aspect_ratio(
                    self.crop_start[0], self.crop_start[1], x, y
                )
            
            self.crop_end = (x, y)
            self._update_info()
    
    def _constrain_to_aspect_ratio(self, x1, y1, x2, y2):
        """Constrain selection to maintain aspect ratio"""
        # Calculate current dimensions
        width = abs(x2 - x1)
        height = abs(y2 - y1)
        
        if width == 0 or height == 0:
            return x2, y2
        
        # Calculate new dimensions based on aspect ratio
        # Determine which dimension to constrain based on drag direction
        current_aspect = width / height
        
        if current_aspect > self.aspect_ratio:
            # Width is too large, constrain it
            new_width = int(height * self.aspect_ratio)
            if x2 > x1:
                x2 = x1 + new_width
            else:
                x2 = x1 - new_width
        else:
            # Height is too large, constrain it
            new_height = int(width / self.aspect_ratio)
            if y2 > y1:
                y2 = y1 + new_height
            else:
                y2 = y1 - new_height
        
        # Ensure within canvas bounds
        x2 = max(0, min(x2, self.display_width))
        y2 = max(0, min(y2, self.display_height))
        
        return x2, y2
    
    def _on_lock_aspect_changed(self):
        """Handle lock aspect ratio checkbox change"""
        if self.lock_aspect.get():
            # Get the current preset and set aspect ratio
            self._on_aspect_preset_changed()
    
    def _on_aspect_preset_changed(self, event=None):
        """Handle aspect ratio preset selection"""
        preset = self.aspect_preset_var.get()
        
        # Map preset to aspect ratio
        aspect_map = {
            "Free": None,
            "Original": self.image_width / self.image_height,
            "1:1 (Square)": 1.0,
            "16:9": 16/9,
            "9:16": 9/16,
            "4:3": 4/3,
            "3:4": 3/4,
            "3:2": 3/2,
            "2:3": 2/3,
        }
        
        self.aspect_ratio = aspect_map.get(preset)
        
        # If "Free" is selected, uncheck lock
        if preset == "Free":
            self.lock_aspect.set(False)
        else:
            self.lock_aspect.set(True)
        
        logger.debug(f"Aspect ratio set to: {preset} ({self.aspect_ratio})")
    
    def _update_info(self):
        """Update selection info label"""
        if self.crop_start and self.crop_end:
            # Calculate original image coordinates
            x1 = int(min(self.crop_start[0], self.crop_end[0]) / self.scale_factor)
            y1 = int(min(self.crop_start[1], self.crop_end[1]) / self.scale_factor)
            x2 = int(max(self.crop_start[0], self.crop_end[0]) / self.scale_factor)
            y2 = int(max(self.crop_start[1], self.crop_end[1]) / self.scale_factor)
            
            width = x2 - x1
            height = y2 - y1
            
            # Calculate aspect ratio
            if height > 0:
                current_aspect = width / height
                aspect_text = f"  |  Aspect: {current_aspect:.2f}:1"
            else:
                aspect_text = ""
            
            self.info_label.config(
                text=f"Selection: {width} × {height} px  |  Position: ({x1}, {y1}) to ({x2}, {y2}){aspect_text}"
            )
        else:
            self.info_label.config(text="No selection")
    
    def _reset_selection(self):
        """Reset crop selection"""
        self.crop_start = None
        self.crop_end = None
        
        if self.crop_rect:
            self.canvas.delete(self.crop_rect)
            self.crop_rect = None
        
        self.info_label.config(text="No selection")
    
    def _apply_crop(self):
        """Apply crop and save result"""
        if not self.crop_start or not self.crop_end:
            messagebox.showwarning("No Selection", "Please select a crop area first.")
            return
        
        try:
            # Calculate crop coordinates in original image space
            x1 = int(min(self.crop_start[0], self.crop_end[0]) / self.scale_factor)
            y1 = int(min(self.crop_start[1], self.crop_end[1]) / self.scale_factor)
            x2 = int(max(self.crop_start[0], self.crop_end[0]) / self.scale_factor)
            y2 = int(max(self.crop_start[1], self.crop_end[1]) / self.scale_factor)
            
            # Validate crop area
            if x2 - x1 < 10 or y2 - y1 < 10:
                messagebox.showwarning("Invalid Selection", "Crop area is too small. Please select a larger area.")
                return
            
            # Crop image
            cropped = self.original_image.crop((x1, y1, x2, y2))
            
            # Save to temp file
            import tempfile
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='_cropped.png')
            cropped.save(temp_file.name, quality=95)
            temp_file.close()
            
            logger.info(f"Image cropped: {x2-x1}×{y2-y1} from {self.image_width}×{self.image_height}")
            
            # Call callback
            self.callback(temp_file.name)
            
            # Close dialog
            self.dialog.destroy()
            
        except Exception as e:
            logger.error(f"Error applying crop: {e}")
            messagebox.showerror("Error", f"Failed to crop image: {str(e)}")


class ImageResizeTool:
    """Interactive resize tool with presets"""
    
    def __init__(self, parent, image_path: str, callback: Callable):
        """
        Initialize resize tool
        
        Args:
            parent: Parent window
            image_path: Path to image to resize
            callback: Callback function(resized_image_path)
        """
        self.parent = parent
        self.image_path = image_path
        self.callback = callback
        
        # Load original image
        try:
            self.original_image = Image.open(image_path)
            self.original_width, self.original_height = self.original_image.size
            self.original_aspect = self.original_width / self.original_height
        except Exception as e:
            logger.error(f"Failed to load image for resizing: {e}")
            messagebox.showerror("Error", f"Failed to load image: {str(e)}")
            return
        
        # Create dialog
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Resize Image")
        self.dialog.geometry("500x450")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self._create_ui()
    
    def _create_ui(self):
        """Create resize tool UI"""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Current size info
        info_frame = ttk.LabelFrame(main_frame, text="Current Image", padding="10")
        info_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(
            info_frame,
            text=f"Size: {self.original_width} × {self.original_height} px",
            font=('Arial', 10, 'bold')
        ).pack()
        
        ttk.Label(
            info_frame,
            text=f"Aspect Ratio: {self.original_aspect:.2f}:1",
            font=('Arial', 9)
        ).pack()
        
        # Resize presets
        preset_frame = ttk.LabelFrame(main_frame, text="Quick Presets", padding="10")
        preset_frame.pack(fill=tk.X, pady=(0, 15))
        
        presets = [
            ("1024×1024 (Square)", 1024, 1024),
            ("1920×1080 (16:9)", 1920, 1080),
            ("1080×1920 (9:16)", 1080, 1920),
            ("2048×2048 (Square)", 2048, 2048),
            ("50% Scale", int(self.original_width * 0.5), int(self.original_height * 0.5)),
            ("75% Scale", int(self.original_width * 0.75), int(self.original_height * 0.75)),
        ]
        
        for i, (name, w, h) in enumerate(presets):
            btn = ttk.Button(
                preset_frame,
                text=name,
                command=lambda w=w, h=h: self._set_size(w, h),
                width=25
            )
            btn.grid(row=i//2, column=i%2, padx=5, pady=3, sticky="ew")
        
        preset_frame.columnconfigure(0, weight=1)
        preset_frame.columnconfigure(1, weight=1)
        
        # Custom size
        custom_frame = ttk.LabelFrame(main_frame, text="Custom Size", padding="10")
        custom_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Width
        width_frame = ttk.Frame(custom_frame)
        width_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(width_frame, text="Width:", width=12).pack(side=tk.LEFT)
        self.width_var = tk.StringVar(value=str(self.original_width))
        self.width_entry = ttk.Entry(width_frame, textvariable=self.width_var, width=10)
        self.width_entry.pack(side=tk.LEFT, padx=5)
        self.width_entry.bind('<KeyRelease>', self._on_width_change)
        
        ttk.Label(width_frame, text="px").pack(side=tk.LEFT)
        
        # Height
        height_frame = ttk.Frame(custom_frame)
        height_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(height_frame, text="Height:", width=12).pack(side=tk.LEFT)
        self.height_var = tk.StringVar(value=str(self.original_height))
        self.height_entry = ttk.Entry(height_frame, textvariable=self.height_var, width=10)
        self.height_entry.pack(side=tk.LEFT, padx=5)
        self.height_entry.bind('<KeyRelease>', self._on_height_change)
        
        ttk.Label(height_frame, text="px").pack(side=tk.LEFT)
        
        # Lock aspect ratio
        self.lock_aspect_var = tk.BooleanVar(value=True)
        self.lock_check = ttk.Checkbutton(
            custom_frame,
            text="Lock aspect ratio",
            variable=self.lock_aspect_var
        )
        self.lock_check.pack(pady=5)
        
        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=10)
        
        ttk.Button(
            btn_frame,
            text="Apply Resize",
            command=self._apply_resize,
            width=15
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            btn_frame,
            text="Cancel",
            command=self.dialog.destroy,
            width=15
        ).pack(side=tk.LEFT, padx=5)
    
    def _set_size(self, width: int, height: int):
        """Set size to preset values"""
        self.width_var.set(str(width))
        self.height_var.set(str(height))
    
    def _on_width_change(self, event=None):
        """Handle width change"""
        if not self.lock_aspect_var.get():
            return
        
        try:
            width = int(self.width_var.get())
            height = int(width / self.original_aspect)
            self.height_var.set(str(height))
        except:
            pass
    
    def _on_height_change(self, event=None):
        """Handle height change"""
        if not self.lock_aspect_var.get():
            return
        
        try:
            height = int(self.height_var.get())
            width = int(height * self.original_aspect)
            self.width_var.set(str(width))
        except:
            pass
    
    def _apply_resize(self):
        """Apply resize and save result"""
        try:
            # Get new dimensions
            new_width = int(self.width_var.get())
            new_height = int(self.height_var.get())
            
            # Validate
            if new_width < 1 or new_height < 1:
                messagebox.showwarning("Invalid Size", "Width and height must be greater than 0.")
                return
            
            if new_width > 8192 or new_height > 8192:
                messagebox.showwarning("Invalid Size", "Maximum dimension is 8192 pixels.")
                return
            
            # Resize image
            resized = self.original_image.resize(
                (new_width, new_height),
                Image.Resampling.LANCZOS
            )
            
            # Save to temp file
            import tempfile
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='_resized.png')
            resized.save(temp_file.name, quality=95)
            temp_file.close()
            
            logger.info(f"Image resized: {self.original_width}×{self.original_height} → {new_width}×{new_height}")
            
            # Call callback
            self.callback(temp_file.name)
            
            # Close dialog
            self.dialog.destroy()
            
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid numbers for width and height.")
        except Exception as e:
            logger.error(f"Error applying resize: {e}")
            messagebox.showerror("Error", f"Failed to resize image: {str(e)}")


# Convenience functions
def open_crop_tool(parent, image_path: str, callback: Callable):
    """Open crop tool dialog"""
    ImageCropTool(parent, image_path, callback)


def open_resize_tool(parent, image_path: str, callback: Callable):
    """Open resize tool dialog"""
    ImageResizeTool(parent, image_path, callback)

