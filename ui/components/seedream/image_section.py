"""
Seedream V4 - Image Section Module (Enhanced)

This module handles all image-related functionality for the Seedream V4 tab:
- Image loading and caching
- Canvas display and interaction
- Zoom and pan controls
- Synchronized dual-panel viewing
- Comparison modes (side-by-side, overlay)
- Image selection and browsing
- Drag & drop support
- Multiple image management
- Thumbnail display
- Image reordering

Extracted from improved_seedream_layout.py as part of the modular refactoring.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import os
from typing import List, Optional, Tuple
from core.logger import get_logger

logger = get_logger()

# Try to import tkinterdnd2 for drag and drop
try:
    from tkinterdnd2 import DND_FILES
    DND_AVAILABLE = True
except ImportError:
    DND_AVAILABLE = False
    logger.warning("tkinterdnd2 not available - drag and drop will be disabled")


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
            
            # Trigger zoom change through comparison controller
            if hasattr(self.layout, 'comparison_controller') and hasattr(self.layout.comparison_controller, '_on_zoom_changed'):
                self.layout.comparison_controller._on_zoom_changed()
            else:
                # Fallback: manually refresh both images
                self._refresh_both_images_with_zoom(new_zoom)
            
            logger.debug(f"Applied debounced zoom: {current_zoom} -> {new_zoom} (size_ratio: {size_ratio:.2f})")
    
    def _refresh_both_images_with_zoom(self, zoom_level):
        """Refresh both images with new zoom level"""
        try:
            # Refresh original image
            if hasattr(self.layout, 'image_manager') and hasattr(self.layout.image_manager, 'selected_image_paths'):
                paths = self.layout.image_manager.selected_image_paths
                if paths and len(paths) > 0:
                    self.layout.image_manager.display_image_in_panel(
                        paths[0], 
                        'original',
                        self.layout.original_canvas,
                        self.layout.zoom_var
                    )
            
            # Refresh result image if available
            result_path = None
            if hasattr(self.layout, 'results_manager') and hasattr(self.layout.results_manager, 'result_image_path'):
                result_path = self.layout.results_manager.result_image_path
            
            if result_path:
                self.layout.image_manager.display_image_in_panel(
                    result_path,
                    'result',
                    self.layout.result_canvas,
                    self.layout.zoom_var
                )
        except Exception as e:
            logger.error(f"Error refreshing images with zoom: {e}")
    
    def _calculate_synced_zoom_scale(self, current_img, current_panel_type, base_scale):
        """
        Calculate zoom scale adjusted for image size differences.
        
        This ensures both images show the same level of detail/magnification,
        even if they're different sizes (e.g., 1024x1536 vs 1536x2048).
        
        Args:
            current_img: PIL Image object for current panel
            current_panel_type: 'original' or 'result'
            base_scale: Base zoom scale from zoom percentage
            
        Returns:
            Adjusted scale factor
        """
        try:
            # Get the other panel's image size
            other_panel_type = 'result' if current_panel_type == 'original' else 'original'
            other_img = None
            
            # Try to get the other image
            if other_panel_type == 'result':
                if hasattr(self.layout, 'results_manager') and hasattr(self.layout.results_manager, 'result_image_path'):
                    result_path = self.layout.results_manager.result_image_path
                    if result_path:
                        other_img = self.get_cached_image(result_path)
            else:
                if hasattr(self.layout, 'image_manager') and hasattr(self.layout.image_manager, 'selected_image_paths'):
                    paths = self.layout.image_manager.selected_image_paths
                    if paths and len(paths) > 0:
                        other_img = self.get_cached_image(paths[0])
            
            # If we can't get the other image, use base scale
            if not other_img:
                return base_scale
            
            # Calculate the diagonal size ratio (accounts for both dimensions)
            # Using diagonal gives a better "perceived size" match than just width or height
            import math
            current_diagonal = math.sqrt(current_img.width**2 + current_img.height**2)
            other_diagonal = math.sqrt(other_img.width**2 + other_img.height**2)
            
            # If current image is the original, use base scale
            # If current image is the result, adjust scale to match original's apparent size
            if current_panel_type == 'original':
                adjusted_scale = base_scale
            else:
                # Result image: scale it relative to original
                # If result is larger, scale it down more to match original's zoom level
                size_ratio = other_diagonal / current_diagonal  # original / result
                adjusted_scale = base_scale * size_ratio
            
            logger.debug(f"{current_panel_type}: base_scale={base_scale:.3f}, adjusted={adjusted_scale:.3f} (ratio={other_diagonal/current_diagonal:.3f})")
            return adjusted_scale
            
        except Exception as e:
            logger.error(f"Error calculating synced zoom scale: {e}")
            return base_scale


class ImageSectionManager:
    """
    Manages all image-related functionality for the Seedream V4 layout.
    
    This class handles:
    - Image loading and caching
    - Canvas display
    - Zoom and pan controls
    - Comparison views (side-by-side, overlay)
    - Image reordering
    - Drag & drop
    - Thumbnail display
    - Multiple image management (up to 10 images)
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
        
        # Canvas resize debouncing
        self.resize_timer = None
        self.resize_delay = 750  # ms delay for debouncing canvas resize
        self._last_canvas_size = {"original": (0, 0), "result": (0, 0)}
        
        # Image paths (support for multiple images)
        self.selected_image_paths = []
        self.result_image_path = None
        self.original_image_order = []  # For reset functionality
        
        # Original image dimensions for scaling
        self.original_image_width = None
        self.original_image_height = None
        
        # UI widget references (set by setup method)
        self.thumbnail_label = None
        self.image_name_label = None
        self.image_size_label = None
        self.reorder_btn = None
        self.reorder_listbox = None
        
        logger.info("ImageSectionManager initialized")
    
    def set_ui_references(self, thumbnail_label=None, image_name_label=None, 
                         image_size_label=None, reorder_btn=None):
        """
        Set references to UI widgets for updates.
        
        Args:
            thumbnail_label: Label widget for thumbnail display
            image_name_label: Label widget for image name/count
            image_size_label: Label widget for image dimensions
            reorder_btn: Button widget for reordering (enabled/disabled based on count)
        """
        self.thumbnail_label = thumbnail_label
        self.image_name_label = image_name_label
        self.image_size_label = image_size_label
        self.reorder_btn = reorder_btn
        
        # Debug logging
        logger.debug(f"UI references set - thumbnail: {thumbnail_label is not None}, "
                    f"name_label: {image_name_label is not None}, "
                    f"size_label: {image_size_label is not None}, "
                    f"reorder_btn: {reorder_btn is not None}")
        
        # Setup drag and drop if thumbnail is available
        if self.thumbnail_label and DND_AVAILABLE:
            self.setup_drag_drop()
    
    def _safe_config_widget(self, widget, **kwargs):
        """Safely configure a widget with null checks"""
        try:
            if widget and hasattr(widget, 'config'):
                widget.config(**kwargs)
                return True
            else:
                logger.debug(f"Widget is None or has no config method: {widget}")
                return False
        except Exception as e:
            logger.error(f"Error configuring widget {widget}: {e}")
            return False
    
    def browse_image(self) -> bool:
        """
        Browse for image files (supports multiple selection up to 10 images).
        
        Returns:
            bool: True if images were selected, False otherwise
        """
        file_paths = filedialog.askopenfilenames(
            title="Select Images for Seedream V4 (up to 10 images)",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.gif *.bmp *.webp"),
                ("PNG files", "*.png"),
                ("JPEG files", "*.jpg *.jpeg"),
                ("All files", "*.*")
            ]
        )
        
        if not file_paths:
            return False
        
        # Limit to 10 images as per API specification
        if len(file_paths) > 10:
            messagebox.showwarning(
                "Too Many Images", 
                f"Maximum 10 images allowed. Selected {len(file_paths)} images. Using first 10."
            )
            file_paths = file_paths[:10]
        
        # If we have a connected tab instance, use its image selection handler
        if self.layout.tab_instance and hasattr(self.layout.tab_instance, 'on_images_selected'):
            self.layout.tab_instance.on_images_selected(file_paths)
        else:
            # Fallback to direct loading
            self.load_images(file_paths)
        
        return True
    
    def load_images(self, image_paths: List[str]) -> None:
        """
        Load and display multiple input images.
        
        Args:
            image_paths: List of paths to image files
        """
        try:
            # Safety check: Ensure we have valid input
            if not image_paths:
                logger.warning("load_images called with empty image_paths")
                return
            
            self.selected_image_paths = list(image_paths)
            
            # Use the first image for display and scale calculations
            first_image_path = self.selected_image_paths[0]
            logger.debug(f"Loading first image: {first_image_path}")
            
            # Load the first image
            success = self.load_image(first_image_path)
            if not success:
                logger.warning(f"Failed to load first image: {first_image_path}")
            
            # Update the image count display (with defensive checks)
            logger.debug("Updating image count display...")
            try:
                self.update_image_count_display()
            except Exception as display_error:
                logger.error(f"Error updating image count display: {display_error}", exc_info=True)
                # Continue - this is not critical
            
            logger.info(f"Loaded {len(self.selected_image_paths)} images")
            
        except Exception as e:
            logger.error(f"Error in load_images: {e}", exc_info=True)
            # Don't re-raise - allow partial success
            # Show error message to user if possible
            if hasattr(self, 'layout') and hasattr(self.layout, 'log_message'):
                try:
                    self.layout.log_message(f"⚠️ Error loading images: {str(e)}")
                except:
                    pass
    
    def load_image(self, image_path: str) -> bool:
        """
        Load and display input image (single image - for backward compatibility).
        
        Args:
            image_path: Path to the image file
            
        Returns:
            bool: True if successful, False otherwise
        """
        # If this is called directly, treat as single image
        if image_path not in self.selected_image_paths:
            self.selected_image_paths = [image_path]
        
        try:
            # PERFORMANCE: Use cached image for thumbnail
            original = self.get_cached_image(image_path)
            
            # Update thumbnail if widget available
            if self.thumbnail_label:
                img = original.copy()
                img.thumbnail((50, 50), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                
                if self._safe_config_widget(self.thumbnail_label, image=photo, text=""):
                    self.thumbnail_label.image = photo
                else:
                    logger.warning("Failed to update thumbnail label")
            
            # Update info labels if available
            filename = os.path.basename(image_path)
            if len(filename) > 25:
                filename = filename[:22] + "..."
            
            if not self._safe_config_widget(self.image_name_label, text=filename, foreground="black"):
                logger.warning(f"Failed to update image name label (widget: {self.image_name_label})")
            
            # Get image size and store original dimensions (already loaded)
            self.original_image_width = original.width
            self.original_image_height = original.height
            
            if not self._safe_config_widget(self.image_size_label, text=f"{original.width}×{original.height}"):
                logger.warning(f"Failed to update image size label (widget: {self.image_size_label})")
            
            # Update settings manager with image dimensions (for resolution analysis)
            if hasattr(self.layout, 'settings_manager') and hasattr(self.layout.settings_manager, 'update_original_image_dimensions'):
                self.layout.settings_manager.update_original_image_dimensions(original.width, original.height)
            
            # Auto-set resolution if enabled
            if hasattr(self.layout, 'auto_set_resolution'):
                self.layout.auto_set_resolution()
            
            # Display in original panel if available
            if hasattr(self.layout, 'original_canvas') and hasattr(self.layout, 'zoom_var'):
                self.display_image_in_panel(
                    image_path, 
                    "original", 
                    self.layout.original_canvas, 
                    self.layout.zoom_var
                )
            
            logger.info(f"Successfully loaded image: {filename}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading image {image_path}: {e}")
            if hasattr(self.layout, 'status_label'):
                self._safe_config_widget(self.layout.status_label, text=f"Error loading image: {str(e)}", foreground="red")
            return False
    
    def update_image_count_display(self) -> None:
        """Update the display to show number of selected images."""
        try:
            # Safety check: If UI widgets aren't set up yet, skip silently
            if self.image_name_label is None:
                logger.debug("image_name_label is None, UI not ready - skipping update")
                return
            
            # Verify widget is still valid
            if not hasattr(self.image_name_label, 'config'):
                logger.warning(f"image_name_label has no config method: {self.image_name_label}")
                return
            
            count = len(self.selected_image_paths)
            
            if count == 0:
                self._safe_config_widget(self.image_name_label, text="No images selected", foreground="gray")
                self._safe_config_widget(self.reorder_btn, state="disabled")
            elif count == 1:
                filename = os.path.basename(self.selected_image_paths[0])
                if len(filename) > 25:
                    filename = filename[:22] + "..."
                self._safe_config_widget(self.image_name_label, text=filename, foreground="black")
                self._safe_config_widget(self.reorder_btn, state="disabled")
            else:
                # Show count and first image name
                first_filename = os.path.basename(self.selected_image_paths[0])
                if len(first_filename) > 15:
                    first_filename = first_filename[:12] + "..."
                self._safe_config_widget(
                    self.image_name_label,
                    text=f"{count} images ({first_filename} +{count-1} more)", 
                    foreground="blue"
                )
                self._safe_config_widget(self.reorder_btn, state="normal")
            
            logger.debug(f"Updated image count display: {count} images")
            
        except Exception as e:
            logger.error(f"Error updating image count display: {e}", exc_info=True)
    
    def setup_drag_drop(self) -> None:
        """Setup drag and drop functionality."""
        if not DND_AVAILABLE:
            logger.warning("Drag and drop not available - tkinterdnd2 not installed")
            return
        
        try:
            # Enable drag and drop on thumbnail
            if self.thumbnail_label:
                self.thumbnail_label.drop_target_register(DND_FILES)
                self.thumbnail_label.dnd_bind('<<Drop>>', self.on_drop)
                self.thumbnail_label.dnd_bind('<<DragEnter>>', self.on_drag_enter)
                self.thumbnail_label.dnd_bind('<<DragLeave>>', self.on_drag_leave)
            
            # Enable drag and drop on image info area
            if self.image_name_label:
                self.image_name_label.drop_target_register(DND_FILES)
                self.image_name_label.dnd_bind('<<Drop>>', self.on_drop)
                self.image_name_label.dnd_bind('<<DragEnter>>', self.on_drag_enter)
                self.image_name_label.dnd_bind('<<DragLeave>>', self.on_drag_leave)
            
            logger.info("Drag and drop enabled")
                
        except Exception as e:
            logger.error(f"Drag and drop setup failed: {e}")
    
    def on_drop(self, event) -> None:
        """Handle drag and drop event."""
        # Try parent tab's on_drop first
        if self.layout.tab_instance and hasattr(self.layout.tab_instance, 'on_drop'):
            self.layout.tab_instance.on_drop(event)
            return
        
        # Fallback to direct handling
        try:
            from utils.utils import parse_drag_drop_data, validate_image_file, show_error
            
            success, result = parse_drag_drop_data(event.data)
            
            if not success:
                show_error("Drag & Drop Error", result)
                return
            
            file_path = result
            
            # Validate the image file
            is_valid, error = validate_image_file(file_path)
            if not is_valid:
                show_error("Invalid File", f"{error}\n\nDropped file: {file_path}")
                return
            
            # Load the image via load_images for proper state management
            self.load_images([file_path])
            
            # Also update filter manager if available
            if hasattr(self.layout, '_update_filter_manager_image'):
                self.layout._update_filter_manager_image()
            
            logger.info(f"✓ Drag & drop: Image loaded successfully: {file_path}")
            
        except ImportError:
            logger.error("utils.utils module not available for drag and drop handling")
        except Exception as e:
            logger.error(f"Error handling drop event: {e}")
    
    def on_drag_enter(self, event) -> None:
        """Handle drag enter event (visual feedback)."""
        self._safe_config_widget(self.thumbnail_label, bg='#e0e0e0')
    
    def on_drag_leave(self, event) -> None:
        """Handle drag leave event (restore visual state)."""
        self._safe_config_widget(self.thumbnail_label, bg='#f5f5f5')
    
    def show_image_reorder_dialog(self) -> None:
        """Show dialog to reorder selected images."""
        if len(self.selected_image_paths) < 2:
            logger.info("Cannot reorder: less than 2 images selected")
            return
        
        # Create dialog window
        dialog = tk.Toplevel(self.layout.parent_frame)
        dialog.title("Reorder Images")
        dialog.geometry("600x500")
        dialog.transient(self.layout.parent_frame)
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() - dialog.winfo_width()) // 2
        y = (dialog.winfo_screenheight() - dialog.winfo_height()) // 2
        dialog.geometry(f"+{x}+{y}")
        
        # Title
        title_frame = ttk.Frame(dialog)
        title_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(
            title_frame, 
            text="🔄 Reorder Your Images", 
            font=("Arial", 14, "bold")
        ).pack(anchor="w")
        
        ttk.Label(
            title_frame, 
            text="Drag items up/down or use arrow buttons to change processing order:",
            font=("Arial", 9)
        ).pack(anchor="w")
        
        # Main content frame
        content_frame = ttk.Frame(dialog)
        content_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Create scrollable listbox for images
        list_frame = ttk.Frame(content_frame)
        list_frame.pack(fill="both", expand=True)
        
        # Listbox with scrollbar
        listbox_frame = ttk.Frame(list_frame)
        listbox_frame.pack(side="left", fill="both", expand=True)
        
        self.reorder_listbox = tk.Listbox(
            listbox_frame,
            height=12,
            font=("Arial", 10),
            selectmode="single"
        )
        self.reorder_listbox.pack(side="left", fill="both", expand=True)
        
        scrollbar = ttk.Scrollbar(listbox_frame, orient="vertical")
        scrollbar.pack(side="right", fill="y")
        self.reorder_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.reorder_listbox.yview)
        
        # Control buttons
        button_frame = ttk.Frame(list_frame)
        button_frame.pack(side="right", fill="y", padx=(10, 0))
        
        ttk.Button(
            button_frame,
            text="⬆️ Move Up",
            command=lambda: self.move_image_up(dialog),
            width=12
        ).pack(pady=2)
        
        ttk.Button(
            button_frame,
            text="⬇️ Move Down", 
            command=lambda: self.move_image_down(dialog),
            width=12
        ).pack(pady=2)
        
        ttk.Separator(button_frame, orient="horizontal").pack(fill="x", pady=10)
        
        ttk.Button(
            button_frame,
            text="🔝 Move to Top",
            command=lambda: self.move_image_to_top(dialog),
            width=12
        ).pack(pady=2)
        
        ttk.Button(
            button_frame,
            text="🔻 Move to Bottom",
            command=lambda: self.move_image_to_bottom(dialog),
            width=12
        ).pack(pady=2)
        
        # Bottom buttons
        bottom_frame = ttk.Frame(dialog)
        bottom_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Button(
            bottom_frame,
            text="✅ Apply Order",
            command=lambda: self.apply_image_order(dialog)
        ).pack(side="right", padx=(5, 0))
        
        ttk.Button(
            bottom_frame,
            text="❌ Cancel",
            command=dialog.destroy
        ).pack(side="right")
        
        ttk.Button(
            bottom_frame,
            text="🔄 Reset to Original",
            command=lambda: self.reset_image_order(dialog)
        ).pack(side="left")
        
        # Store original order for reset
        self.original_image_order = self.selected_image_paths.copy()
        
        # Populate listbox
        self.populate_reorder_listbox()
        
        # Select first item
        if self.reorder_listbox.size() > 0:
            self.reorder_listbox.selection_set(0)
        
        logger.info("Image reorder dialog opened")
    
    def populate_reorder_listbox(self) -> None:
        """Populate the reorder listbox with current image order."""
        if not self.reorder_listbox:
            return
        
        self.reorder_listbox.delete(0, tk.END)
        
        for i, image_path in enumerate(self.selected_image_paths):
            filename = os.path.basename(image_path)
            # Show position number and filename
            display_text = f"{i+1}. {filename}"
            self.reorder_listbox.insert(tk.END, display_text)
    
    def move_image_up(self, dialog) -> None:
        """Move selected image up in the order."""
        if not self.reorder_listbox:
            return
        
        selection = self.reorder_listbox.curselection()
        if not selection or selection[0] == 0:
            return
        
        index = selection[0]
        # Swap with previous item
        self.selected_image_paths[index], self.selected_image_paths[index-1] = \
            self.selected_image_paths[index-1], self.selected_image_paths[index]
        
        # Update listbox
        self.populate_reorder_listbox()
        self.reorder_listbox.selection_set(index-1)
        logger.debug(f"Moved image up from position {index+1} to {index}")
    
    def move_image_down(self, dialog) -> None:
        """Move selected image down in the order."""
        if not self.reorder_listbox:
            return
        
        selection = self.reorder_listbox.curselection()
        if not selection or selection[0] == len(self.selected_image_paths) - 1:
            return
        
        index = selection[0]
        # Swap with next item
        self.selected_image_paths[index], self.selected_image_paths[index+1] = \
            self.selected_image_paths[index+1], self.selected_image_paths[index]
        
        # Update listbox
        self.populate_reorder_listbox()
        self.reorder_listbox.selection_set(index+1)
        logger.debug(f"Moved image down from position {index+1} to {index+2}")
    
    def move_image_to_top(self, dialog) -> None:
        """Move selected image to the top of the order."""
        if not self.reorder_listbox:
            return
        
        selection = self.reorder_listbox.curselection()
        if not selection or selection[0] == 0:
            return
        
        index = selection[0]
        # Move to top
        image_path = self.selected_image_paths.pop(index)
        self.selected_image_paths.insert(0, image_path)
        
        # Update listbox
        self.populate_reorder_listbox()
        self.reorder_listbox.selection_set(0)
        logger.debug(f"Moved image from position {index+1} to top")
    
    def move_image_to_bottom(self, dialog) -> None:
        """Move selected image to the bottom of the order."""
        if not self.reorder_listbox:
            return
        
        selection = self.reorder_listbox.curselection()
        if not selection or selection[0] == len(self.selected_image_paths) - 1:
            return
        
        index = selection[0]
        # Move to bottom
        image_path = self.selected_image_paths.pop(index)
        self.selected_image_paths.append(image_path)
        
        # Update listbox
        self.populate_reorder_listbox()
        self.reorder_listbox.selection_set(len(self.selected_image_paths) - 1)
        logger.debug(f"Moved image from position {index+1} to bottom")
    
    def reset_image_order(self, dialog) -> None:
        """Reset to original image order."""
        self.selected_image_paths = self.original_image_order.copy()
        self.populate_reorder_listbox()
        if self.reorder_listbox and self.reorder_listbox.size() > 0:
            self.reorder_listbox.selection_set(0)
        logger.info("Image order reset to original")
    
    def apply_image_order(self, dialog) -> None:
        """Apply the new image order and close dialog."""
        # Update the display to reflect new order
        self.update_image_count_display()
        
        # Update the original image display to show the first image in the new order
        if self.selected_image_paths:
            first_image = self.selected_image_paths[0]
            # Update the thumbnail and info display
            self.load_image(first_image)
            # Also update the original canvas display directly
            if hasattr(self.layout, 'original_canvas') and hasattr(self.layout, 'zoom_var'):
                self.display_image_in_panel(
                    first_image, 
                    "original", 
                    self.layout.original_canvas, 
                    self.layout.zoom_var
                )
        
        dialog.destroy()
        logger.info("New image order applied")
    
    def get_image_status(self) -> dict:
        """
        Get current image status.
        
        Returns:
            dict: Dictionary containing image status information
        """
        return {
            "selected_count": len(self.selected_image_paths),
            "selected_paths": self.selected_image_paths.copy(),
            "result_path": self.result_image_path,
            "original_dimensions": (self.original_image_width, self.original_image_height) if self.original_image_width else None,
            "cache_size": len(self.image_cache)
        }
    
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
    
    def _calculate_synced_zoom_scale(self, current_img, current_panel_type, base_scale):
        """
        Calculate zoom scale adjusted for image size differences.
        
        This ensures both images show the same level of detail/magnification,
        even if they're different sizes (e.g., 1024x1536 vs 1536x2048).
        
        Args:
            current_img: PIL Image object for current panel
            current_panel_type: 'original' or 'result'
            base_scale: Base zoom scale from zoom percentage
            
        Returns:
            Adjusted scale factor
        """
        try:
            # Get the other panel's image size
            other_panel_type = 'result' if current_panel_type == 'original' else 'original'
            other_img = None
            
            # Try to get the other image
            if other_panel_type == 'result':
                if self.result_image_path:
                    other_img = self.get_cached_image(self.result_image_path)
            else:
                if self.selected_image_paths and len(self.selected_image_paths) > 0:
                    other_img = self.get_cached_image(self.selected_image_paths[0])
            
            # If we can't get the other image, use base scale
            if not other_img:
                return base_scale
            
            # Calculate the diagonal size ratio (accounts for both dimensions)
            # Using diagonal gives a better "perceived size" match than just width or height
            import math
            current_diagonal = math.sqrt(current_img.width**2 + current_img.height**2)
            other_diagonal = math.sqrt(other_img.width**2 + other_img.height**2)
            
            # If current image is the original, use base scale
            # If current image is the result, adjust scale to match original's apparent size
            if current_panel_type == 'original':
                adjusted_scale = base_scale
            else:
                # Result image: scale it relative to original
                # If result is larger, scale it down more to match original's zoom level
                size_ratio = other_diagonal / current_diagonal  # original / result
                adjusted_scale = base_scale * size_ratio
            
            logger.debug(f"{current_panel_type}: base_scale={base_scale:.3f}, adjusted={adjusted_scale:.3f} (ratio={other_diagonal/current_diagonal:.3f})")
            return adjusted_scale
            
        except Exception as e:
            logger.error(f"Error calculating synced zoom scale: {e}")
            return base_scale
    
    def on_canvas_configure_debounced(self, event, panel_type):
        """Debounced canvas resize handler to prevent performance issues"""
        try:
            # Get canvas size
            new_size = (event.width, event.height)
            
            # Check if size actually changed
            if self._last_canvas_size.get(panel_type) == new_size:
                return
            
            # Cancel existing timer
            if self.resize_timer:
                try:
                    self.layout.parent_frame.after_cancel(self.resize_timer)
                except:
                    pass
            
            # Set new timer to apply resize after delay
            self.resize_timer = self.layout.parent_frame.after(
                self.resize_delay,
                lambda: self._apply_canvas_resize(event, panel_type, new_size)
            )
            
        except Exception as e:
            logger.error(f"Error in debounced canvas configure: {e}")
    
    def _apply_canvas_resize(self, event, panel_type, new_size):
        """Apply canvas resize after debounce delay"""
        try:
            # Update last size
            self._last_canvas_size[panel_type] = new_size
            
            # Redraw image if present
            if panel_type == "original" and self.selected_image_paths:
                self.display_image_in_panel(
                    self.selected_image_paths[0],
                    "original",
                    self.layout.original_canvas,
                    self.layout.zoom_var
                )
            elif panel_type == "result" and self.result_image_path:
                self.display_image_in_panel(
                    self.result_image_path,
                    "result",
                    self.layout.result_canvas,
                    self.layout.zoom_var
                )
            
            logger.debug(f"Canvas {panel_type} resized to {new_size}")
            
        except Exception as e:
            logger.error(f"Error applying canvas resize: {e}")
    
    def display_image_in_panel(self, image_path, panel_type, canvas, zoom_var):
        """
        Display image in specific panel with caching and synced zoom.
        
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
                canvas_width = 400  # Default for side-by-side (larger for fullscreen)
                canvas_height = 600
            
            zoom_value = zoom_var.get()
            if zoom_value == "Fit":
                # Better fit calculation - minimal padding (4px) for maximum display space in fullscreen
                scale_factor = min(
                    (canvas_width - 4) / img.width,
                    (canvas_height - 4) / img.height
                )
                # Ensure minimum scale to prevent tiny images
                scale_factor = max(scale_factor, 0.1)
            else:
                # Get base scale from zoom percentage
                base_scale = float(zoom_value.rstrip('%')) / 100
                
                # SYNCED ZOOM: Adjust scale based on image size ratio when sync is enabled
                if hasattr(self.layout, 'sync_zoom_var') and self.layout.sync_zoom_var.get():
                    scale_factor = self._calculate_synced_zoom_scale(img, panel_type, base_scale)
                else:
                    scale_factor = base_scale
            
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
    
    def show_default_messages(self):
        """Show default placeholder messages in both panels"""
        try:
            # Show message in original panel
            if hasattr(self.layout, 'original_canvas'):
                self.show_panel_message('original', self.layout.original_canvas)
            
            # Show message in result panel
            if hasattr(self.layout, 'result_canvas'):
                self.show_panel_message('result', self.layout.result_canvas)
            
            logger.debug("Default messages displayed in both panels")
            
        except Exception as e:
            logger.error(f"Error showing default messages: {e}")
    
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
                    (canvas_width - 4) / max_width,
                    (canvas_height - 4) / max_height
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

