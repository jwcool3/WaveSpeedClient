"""
Seedream V4 - Image Section Module

This module handles all image-related functionality for the Seedream V4 tab:
- Image loading and caching
- Canvas display and interaction
- Zoom and pan controls
- Synchronized dual-panel viewing
- Comparison modes (side-by-side, overlay)
- Image selection and browsing

Extracted from improved_seedream_layout.py as part of the modular refactoring.
"""

import tkinter as tk
from PIL import Image, ImageTk
import os
from core.logger import get_logger

logger = get_logger()


class SynchronizedImagePanels:
    """Handles synchronized zooming and panning between two image panels with different sized images"""
    
    def __init__(self, original_canvas, result_canvas, sync_zoom_var):
        self.original_canvas = original_canvas
        self.result_canvas = result_canvas
        self.sync_zoom_var = sync_zoom_var
        
        # Store image information for coordinate mapping
        self.original_image_info = {
            'path': None,
            'pil_image': None,
            'display_scale': 1.0,
            'display_offset': (0, 0),
            'natural_size': (0, 0),
            'display_size': (0, 0)
        }
        
        self.result_image_info = {
            'path': None,
            'pil_image': None,
            'display_scale': 1.0,
            'display_offset': (0, 0),
            'natural_size': (0, 0),
            'display_size': (0, 0)
        }
        
        # Track which panel is being dragged
        self.currently_dragging = None
        self.drag_start_data = None
    
    def update_image_info(self, panel_type, image_path, pil_image, display_scale, display_offset, display_size):
        """Update image information for coordinate calculations"""
        info = self.original_image_info if panel_type == 'original' else self.result_image_info
        
        info['path'] = image_path
        info['pil_image'] = pil_image
        info['display_scale'] = display_scale
        info['display_offset'] = display_offset
        info['natural_size'] = pil_image.size if pil_image else (0, 0)
        info['display_size'] = display_size
        
        logger.debug(f"Updated {panel_type} image info: scale={display_scale:.3f}, offset={display_offset}, display_size={display_size}")
    
    def on_synchronized_drag_start(self, event, source_panel):
        """Handle start of synchronized drag"""
        if not self.sync_zoom_var.get():
            return False  # Let normal drag handling proceed
        
        if self.currently_dragging:
            return True  # Already dragging
        
        self.currently_dragging = source_panel
        
        # Store initial positions
        self.drag_start_data = {
            'source_panel': source_panel,
            'mouse_x': event.x,
            'mouse_y': event.y,
            'original_scroll': (self.original_canvas.canvasx(0), self.original_canvas.canvasy(0)),
            'result_scroll': (self.result_canvas.canvasx(0), self.result_canvas.canvasy(0))
        }
        
        # Set scan marks for both canvases
        self.original_canvas.scan_mark(event.x, event.y)
        self.result_canvas.scan_mark(event.x, event.y)
        
        # Change cursors
        self.original_canvas.configure(cursor="fleur")
        self.result_canvas.configure(cursor="fleur")
        
        return True  # Handled
    
    def on_synchronized_drag_motion(self, event, source_panel):
        """Handle synchronized drag motion"""
        if not self.sync_zoom_var.get():
            return False
        
        if self.currently_dragging != source_panel:
            return False
        
        # Calculate movement delta
        dx = event.x - self.drag_start_data['mouse_x']
        dy = event.y - self.drag_start_data['mouse_y']
        
        # Apply synchronized movement with scale compensation
        self.apply_synchronized_pan(dx, dy, source_panel)
        
        return True  # Handled
    
    def apply_synchronized_pan(self, dx, dy, source_panel):
        """Apply panning to both canvases with scale compensation"""
        orig_scale = self.original_image_info['display_scale']
        result_scale = self.result_image_info['display_scale']
        
        if orig_scale <= 0 or result_scale <= 0:
            # Fallback to simple synchronized panning
            self.original_canvas.scan_dragto(
                self.drag_start_data['mouse_x'] + dx,
                self.drag_start_data['mouse_y'] + dy,
                gain=1
            )
            self.result_canvas.scan_dragto(
                self.drag_start_data['mouse_x'] + dx,
                self.drag_start_data['mouse_y'] + dy,
                gain=1
            )
            return
        
        # Calculate scale ratio for synchronized movement
        if source_panel == 'original':
            scale_ratio = result_scale / orig_scale
            result_dx = dx * scale_ratio
            result_dy = dy * scale_ratio
            
            self.original_canvas.scan_dragto(
                self.drag_start_data['mouse_x'] + dx,
                self.drag_start_data['mouse_y'] + dy,
                gain=1
            )
            self.result_canvas.scan_dragto(
                self.drag_start_data['mouse_x'] + result_dx,
                self.drag_start_data['mouse_y'] + result_dy,
                gain=1
            )
        else:
            scale_ratio = orig_scale / result_scale
            orig_dx = dx * scale_ratio
            orig_dy = dy * scale_ratio
            
            self.result_canvas.scan_dragto(
                self.drag_start_data['mouse_x'] + dx,
                self.drag_start_data['mouse_y'] + dy,
                gain=1
            )
            self.original_canvas.scan_dragto(
                self.drag_start_data['mouse_x'] + orig_dx,
                self.drag_start_data['mouse_y'] + orig_dy,
                gain=1
            )
    
    def on_synchronized_drag_end(self, event, source_panel):
        """Handle end of synchronized drag"""
        if not self.sync_zoom_var.get():
            return False
        
        if self.currently_dragging != source_panel:
            return False
        
        self.currently_dragging = None
        
        # Reset cursors
        self.original_canvas.configure(cursor="")
        self.result_canvas.configure(cursor="")
        
        # Clear drag data
        self.drag_start_data = None
        
        return True  # Handled


class EnhancedSyncManager:
    """Enhanced synchronization manager with separate zoom and drag controls"""
    
    def __init__(self, layout_instance):
        self.layout = layout_instance
        self.original_canvas = layout_instance.original_canvas
        self.result_canvas = layout_instance.result_canvas
        
        # Drag state tracking
        self.drag_active = False
        self.drag_source = None
        self.last_drag_x = 0
        self.last_drag_y = 0
        self.drag_event_counter = 0  # For throttling
        
        # Image information for scaling calculations
        self.image_info = {
            'original': {'width': 0, 'height': 0, 'scale': 1.0, 'offset_x': 0, 'offset_y': 0},
            'result': {'width': 0, 'height': 0, 'scale': 1.0, 'offset_x': 0, 'offset_y': 0}
        }
        
        # Zoom debouncing
        self.zoom_timer = None
        self.zoom_delay = 150  # ms delay to debounce scroll events
        self.pending_zoom_delta = 0
        
        logger.info("EnhancedSyncManager initialized")
    
    def setup_enhanced_events(self):
        """Setup proper event bindings with conflict resolution"""
        try:
            # Store existing non-sync bindings we want to preserve
            preserved_bindings = {}
            for event_type in ['<MouseWheel>', '<Button-4>', '<Button-5>']:
                for canvas_name, canvas in [('original', self.original_canvas), ('result', self.result_canvas)]:
                    binding = canvas.bind(event_type)
                    if binding:
                        preserved_bindings[f"{canvas_name}_{event_type}"] = binding
            
            # Bind new synchronized events for drag
            self.original_canvas.bind('<Button-1>', lambda e: self.start_sync_drag(e, 'original'), add='+')
            self.original_canvas.bind('<B1-Motion>', lambda e: self.handle_sync_drag(e, 'original'), add='+')
            self.original_canvas.bind('<ButtonRelease-1>', lambda e: self.end_sync_drag(e, 'original'), add='+')
            
            self.result_canvas.bind('<Button-1>', lambda e: self.start_sync_drag(e, 'result'), add='+')
            self.result_canvas.bind('<B1-Motion>', lambda e: self.handle_sync_drag(e, 'result'), add='+')
            self.result_canvas.bind('<ButtonRelease-1>', lambda e: self.end_sync_drag(e, 'result'), add='+')
            
            # Mouse wheel for zoom sync (add to existing bindings)
            self.original_canvas.bind('<MouseWheel>', lambda e: self.handle_sync_zoom(e, 'original'), add='+')
            self.result_canvas.bind('<MouseWheel>', lambda e: self.handle_sync_zoom(e, 'result'), add='+')
            
            logger.info("Enhanced sync events bound successfully")
        except Exception as e:
            logger.error(f"Error binding enhanced sync events: {e}", exc_info=True)
    
    def update_image_info(self, panel_type, width, height, scale, offset_x, offset_y):
        """Update image information for sync calculations"""
        self.image_info[panel_type] = {
            'width': width,
            'height': height,
            'scale': scale,
            'offset_x': offset_x,
            'offset_y': offset_y
        }
        logger.debug(f"Updated {panel_type} info: {width}x{height}, scale={scale:.3f}")
    
    def start_sync_drag(self, event, source_panel):
        """Start synchronized drag operation"""
        # Only handle if sync drag is enabled
        if not hasattr(self.layout, 'sync_drag_var') or not self.layout.sync_drag_var.get():
            return
        
        if self.drag_active:
            return
        
        self.drag_active = True
        self.drag_source = source_panel
        self.last_drag_x = event.x
        self.last_drag_y = event.y
        
        # Set cursor for both canvases
        self.original_canvas.configure(cursor="fleur")
        self.result_canvas.configure(cursor="fleur")
        
        # Set scan mark for both canvases
        self.original_canvas.scan_mark(event.x, event.y)
        self.result_canvas.scan_mark(event.x, event.y)
        
        logger.debug(f"Started sync drag from {source_panel} at ({event.x}, {event.y})")
    
    def handle_sync_drag(self, event, source_panel):
        """Handle synchronized drag motion with throttling for performance"""
        # Only handle if sync drag is enabled and this is the active drag source
        if not hasattr(self.layout, 'sync_drag_var') or not self.layout.sync_drag_var.get():
            return
        
        if not self.drag_active or self.drag_source != source_panel:
            return
        
        # PERFORMANCE: Throttle drag events - process every 2nd event for smoother performance
        self.drag_event_counter += 1
        if self.drag_event_counter % 2 != 0:
            return  # Skip this event
        
        # Always move the source canvas
        source_canvas = self.original_canvas if source_panel == 'original' else self.result_canvas
        source_canvas.scan_dragto(event.x, event.y, gain=1)
        
        # Move the other canvas with scale compensation
        other_panel = 'result' if source_panel == 'original' else 'original'
        other_canvas = self.result_canvas if source_panel == 'original' else self.original_canvas
        
        # Get scale information for both images
        source_info = self.image_info[source_panel]
        target_info = self.image_info[other_panel]
        
        # Calculate scale ratio (how much bigger/smaller the target is)
        if source_info.get('scale', 0) > 0 and target_info.get('scale', 0) > 0:
            # Use the actual displayed scale to calculate movement ratio
            scale_ratio = target_info['scale'] / source_info['scale']
            
            # Adjust the drag position based on scale ratio
            adjusted_x = self.last_drag_x + (event.x - self.last_drag_x) * scale_ratio
            adjusted_y = self.last_drag_y + (event.y - self.last_drag_y) * scale_ratio
            
            other_canvas.scan_dragto(int(adjusted_x), int(adjusted_y), gain=1)
        else:
            # Fallback to simple 1:1 movement
            other_canvas.scan_dragto(event.x, event.y, gain=1)
        
        self.last_drag_x = event.x
        self.last_drag_y = event.y
    
    def calculate_sync_movement(self, x, y, source_panel, target_panel):
        """Calculate synchronized movement accounting for different image sizes"""
        source_info = self.image_info[source_panel]
        target_info = self.image_info[target_panel]
        
        # If we don't have valid image info, use 1:1 movement
        if (source_info['width'] <= 0 or target_info['width'] <= 0 or
            source_info['height'] <= 0 or target_info['height'] <= 0):
            return x, y
        
        # Calculate scale ratios
        width_ratio = target_info['width'] / source_info['width']
        height_ratio = target_info['height'] / source_info['height']
        
        # Apply scale compensation
        sync_x = x * width_ratio
        sync_y = y * height_ratio
        
        return int(sync_x), int(sync_y)
    
    def end_sync_drag(self, event, source_panel):
        """End synchronized drag operation"""
        if not self.drag_active or self.drag_source != source_panel:
            return
        
        self.drag_active = False
        self.drag_source = None
        self.drag_event_counter = 0  # Reset throttle counter
        
        # Reset cursors
        self.original_canvas.configure(cursor="")
        self.result_canvas.configure(cursor="")
        
        logger.debug(f"Ended sync drag from {source_panel}")
    
    def handle_sync_zoom(self, event, source_panel):
        """Handle synchronized zoom accounting for different image sizes with debouncing"""
        if not hasattr(self.layout, 'sync_zoom_var') or not self.layout.sync_zoom_var.get():
            return
        
        # Get zoom direction
        if hasattr(event, 'delta'):
            delta = event.delta
        elif hasattr(event, 'num'):
            delta = 120 if event.num == 4 else -120
        else:
            return
        
        # Accumulate zoom delta (normalize to +1 or -1)
        zoom_direction = 1 if delta > 0 else -1
        self.pending_zoom_delta += zoom_direction
        
        # Cancel existing timer
        if self.zoom_timer:
            try:
                self.original_canvas.after_cancel(self.zoom_timer)
            except:
                pass
        
        # Set new timer to apply zoom after delay
        self.zoom_timer = self.original_canvas.after(
            self.zoom_delay, 
            lambda: self._apply_debounced_zoom(source_panel)
        )
    
    def _apply_debounced_zoom(self, source_panel):
        """Apply the accumulated zoom changes after debounce delay"""
        if self.pending_zoom_delta == 0:
            return
        
        # Get image size information
        orig_info = self.image_info.get('original', {})
        result_info = self.image_info.get('result', {})
        
        orig_width = orig_info.get('width', 1)
        result_width = result_info.get('width', 1)
        
        # Calculate size ratio (result/original)
        size_ratio = result_width / orig_width if orig_width > 0 else 1.0
        
        # Get current zoom level
        current_zoom = self.layout.zoom_var.get()
        zoom_levels = ["25%", "50%", "75%", "100%", "125%", "150%", "200%", "300%"]
        
        try:
            if current_zoom == "Fit":
                current_index = 3  # 100%
            else:
                current_index = zoom_levels.index(current_zoom)
        except ValueError:
            current_index = 3
        
        # Calculate step size based on accumulated delta and image size ratio
        base_step = 1 if abs(self.pending_zoom_delta) <= 2 else 2
        
        # Don't adjust step size for different image sizes - it makes it too jumpy
        step_size = base_step
        
        # Calculate new index (cap the zoom step to prevent extreme jumps)
        zoom_change = max(-2, min(2, self.pending_zoom_delta)) * step_size
        new_index = current_index + zoom_change
        new_index = max(0, min(new_index, len(zoom_levels) - 1))
        
        # Reset pending delta
        self.pending_zoom_delta = 0
        
        # Apply the zoom
        new_zoom = zoom_levels[new_index]
        if new_zoom != current_zoom:
            self.layout.zoom_var.set(new_zoom)
            if hasattr(self.layout, 'on_zoom_changed'):
                self.layout.on_zoom_changed()
            
            logger.debug(f"Applied debounced zoom: {current_zoom} -> {new_zoom} (size_ratio: {size_ratio:.2f})")


class ImageSectionManager:
    """
    Manages all image-related functionality for the Seedream V4 layout.
    
    This class handles:
    - Image loading and caching
    - Canvas display
    - Zoom and pan controls
    - Comparison views (side-by-side, overlay)
    - Image reordering
    """
    
    def __init__(self, layout_instance):
        """
        Initialize the image section manager.
        
        Args:
            layout_instance: Reference to the main layout instance (ImprovedSeedreamLayout)
        """
        self.layout = layout_instance
        
        # Image caching for performance
        self.image_cache = {}
        self.photo_cache = {}
        self.max_cache_size = 10
        
        # Image paths
        self.selected_image_paths = []
        self.result_image_path = None
        
        logger.info("ImageSectionManager initialized")
    
    def get_cached_image(self, image_path):
        """Get or load image from cache for performance"""
        if image_path not in self.image_cache:
            self.image_cache[image_path] = Image.open(image_path)
            # Cleanup cache if too large
            if len(self.image_cache) > self.max_cache_size:
                oldest_key = next(iter(self.image_cache))
                del self.image_cache[oldest_key]
                logger.debug(f"Removed oldest image from cache: {oldest_key}")
        return self.image_cache[image_path]
    
    def clear_image_cache(self):
        """Clear image caches to free memory"""
        self.image_cache.clear()
        self.photo_cache.clear()
        logger.info("Image caches cleared")
    
    def display_image_in_panel(self, image_path, panel_type, canvas, zoom_var):
        """
        Display image in specific panel with caching.
        
        Args:
            image_path: Path to the image file
            panel_type: 'original' or 'result'
            canvas: The tkinter Canvas widget
            zoom_var: The zoom level StringVar
        """
        try:
            if not canvas.winfo_exists():
                return
            
            canvas.delete("all")
            
            # PERFORMANCE: Use cached image instead of loading from disk every time
            img = self.get_cached_image(image_path)
            canvas_width = canvas.winfo_width()
            canvas_height = canvas.winfo_height()
            
            if canvas_width <= 1:
                canvas_width = 300  # Default for side-by-side
                canvas_height = 400
            
            zoom_value = zoom_var.get()
            if zoom_value == "Fit":
                # Better fit calculation - minimal padding for maximum display space
                scale_factor = min(
                    (canvas_width - 10) / img.width,
                    (canvas_height - 10) / img.height
                )
                # Ensure minimum scale to prevent tiny images
                scale_factor = max(scale_factor, 0.1)
            else:
                scale_factor = float(zoom_value.rstrip('%')) / 100
            
            new_width = int(img.width * scale_factor)
            new_height = int(img.height * scale_factor)
            
            # PERFORMANCE: Cache resized PhotoImage objects for instant redisplay
            cache_key = f"{image_path}_{new_width}_{new_height}"
            if cache_key not in self.photo_cache:
                # PERFORMANCE: Use BILINEAR for faster display (3-5x faster than LANCZOS)
                # Quality difference is minimal for on-screen display
                img_resized = img.resize((new_width, new_height), Image.Resampling.BILINEAR)
                self.photo_cache[cache_key] = ImageTk.PhotoImage(img_resized)
                
                # Cleanup photo cache if too large
                if len(self.photo_cache) > self.max_cache_size * 3:
                    oldest_key = next(iter(self.photo_cache))
                    del self.photo_cache[oldest_key]
                    logger.debug(f"Removed oldest photo from cache")
            
            photo = self.photo_cache[cache_key]
            
            x = max(5, (canvas_width - new_width) // 2)
            y = max(5, (canvas_height - new_height) // 2)
            
            canvas.create_image(x, y, anchor=tk.NW, image=photo)
            canvas.image = photo  # Keep reference
            
            canvas.configure(scrollregion=canvas.bbox("all"))
            
            # Update enhanced sync manager if available
            if hasattr(self.layout, 'enhanced_sync_manager'):
                self.layout.enhanced_sync_manager.update_image_info(
                    panel_type=panel_type,
                    width=new_width,
                    height=new_height,
                    scale=scale_factor,
                    offset_x=x,
                    offset_y=y
                )
            
            logger.debug(f"Displayed {panel_type} image at scale {scale_factor:.2f}")
            
        except Exception as e:
            canvas.delete("all")
            canvas.create_text(
                150, 200,
                text=f"Error loading image:\n{str(e)}",
                fill="red",
                font=('Arial', 10),
                justify=tk.CENTER
            )
            logger.error(f"Error displaying image in {panel_type} panel: {e}")
    
    def show_panel_message(self, panel_type, canvas):
        """Show placeholder message in empty panel"""
        try:
            if not canvas.winfo_exists():
                return
            
            canvas_width = canvas.winfo_width()
            canvas_height = canvas.winfo_height()
            
            # Use reasonable defaults if canvas not ready
            if canvas_width <= 1:
                canvas_width = 300
            if canvas_height <= 1:
                canvas_height = 400
            
            canvas.delete("all")
            
            # Calculate center coordinates
            center_x = canvas_width // 2
            center_y = canvas_height // 2
            
            # Show appropriate message with different colors
            if panel_type == "original":
                message = "Select an image to transform\n\nDrag & drop supported"
                color = "#666"
            else:
                message = "Results will appear here\nafter processing"
                color = "#888"
            
            canvas.create_text(
                center_x, center_y,
                text=message,
                font=('Arial', 11),
                fill=color,
                justify=tk.CENTER
            )
            
            logger.debug(f"Panel message displayed for {panel_type}")
            
        except Exception as e:
            logger.error(f"Error showing panel message for {panel_type}: {e}")
    
    def display_overlay_view(self, original_canvas, original_path, result_path, zoom_var):
        """
        Display overlay comparison view with opacity blending.
        
        Args:
            original_canvas: Canvas to display overlay in
            original_path: Path to original image
            result_path: Path to result image
            zoom_var: Zoom level StringVar
        """
        if not original_path or not result_path:
            self.show_panel_message("original", original_canvas)
            return
        
        try:
            # Load both images from cache
            original_img = self.get_cached_image(original_path)
            result_img = self.get_cached_image(result_path)
            
            # Get canvas dimensions
            canvas_width = original_canvas.winfo_width()
            canvas_height = original_canvas.winfo_height()
            
            if canvas_width <= 1:
                canvas_width = 400
                canvas_height = 400
            
            # Calculate scale factor
            zoom_value = zoom_var.get()
            if zoom_value == "Fit":
                max_width = max(original_img.width, result_img.width)
                max_height = max(original_img.height, result_img.height)
                scale_factor = min(
                    (canvas_width - 10) / max_width,
                    (canvas_height - 10) / max_height
                )
            else:
                scale_factor = float(zoom_value.rstrip('%')) / 100
            
            # Resize to same size
            target_width = max(original_img.width, result_img.width)
            target_height = max(original_img.height, result_img.height)
            
            if original_img.size != (target_width, target_height):
                original_img = original_img.resize((target_width, target_height), Image.Resampling.LANCZOS)
            if result_img.size != (target_width, target_height):
                result_img = result_img.resize((target_width, target_height), Image.Resampling.LANCZOS)
            
            # Apply zoom
            display_width = int(target_width * scale_factor)
            display_height = int(target_height * scale_factor)
            
            original_img = original_img.resize((display_width, display_height), Image.Resampling.LANCZOS)
            result_img = result_img.resize((display_width, display_height), Image.Resampling.LANCZOS)
            
            # Blend images (50/50 opacity)
            blended = Image.blend(original_img.convert('RGBA'), result_img.convert('RGBA'), alpha=0.5)
            
            # Display blended image
            photo = ImageTk.PhotoImage(blended)
            original_canvas.delete("all")
            
            x = (canvas_width - display_width) // 2
            y = (canvas_height - display_height) // 2
            
            original_canvas.create_image(x, y, anchor=tk.NW, image=photo)
            original_canvas.image = photo  # Keep reference
            
            logger.info("Overlay view displayed successfully")
            
        except Exception as e:
            logger.error(f"Error displaying overlay view: {e}")
            original_canvas.delete("all")
            original_canvas.create_text(
                canvas_width // 2, canvas_height // 2,
                text=f"Error creating overlay:\n{str(e)}",
                fill="red",
                font=('Arial', 10),
                justify=tk.CENTER
            )
    
    def swap_images(self, original_canvas, result_canvas, zoom_var):
        """Swap original and result images"""
        if not self.result_image_path or not self.selected_image_paths:
            logger.info("Cannot swap: missing images")
            return
        
        # Swap paths
        temp = self.selected_image_paths[0] if self.selected_image_paths else None
        if temp and self.result_image_path:
            self.selected_image_paths[0] = self.result_image_path
            self.result_image_path = temp
            
            # Redisplay both panels
            self.display_image_in_panel(self.selected_image_paths[0], "original", original_canvas, zoom_var)
            self.display_image_in_panel(self.result_image_path, "result", result_canvas, zoom_var)
            
            logger.info("Images swapped successfully")


# Export public classes
__all__ = [
    'SynchronizedImagePanels',
    'EnhancedSyncManager',
    'ImageSectionManager'
]

