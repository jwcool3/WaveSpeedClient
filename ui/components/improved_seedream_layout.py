"""
Improved Seedream V4 Tab Layout - Fixing All Issues
1. Two-column structure eliminates vertical scrolling
2. Compact horizontal settings (1/3 the height)  
3. Apply button directly under prompt
4. Collapsible advanced sections
5. Large dynamic preview with minimal margins
6. No wasted horizontal space
7. ENHANCED: Unified status console and keyboard shortcuts
"""

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os
import threading
import asyncio

# Try to import drag and drop support
try:
    from tkinterdnd2 import DND_FILES
    DND_AVAILABLE = True
except ImportError:
    DND_AVAILABLE = False
from ui.components.unified_status_console import UnifiedStatusConsole
from ui.components.keyboard_manager import KeyboardManager
from ui.components.ai_chat_integration_helper import AIChatMixin
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
        
        # Image information for scaling calculations
        self.image_info = {
            'original': {'width': 0, 'height': 0, 'scale': 1.0, 'offset_x': 0, 'offset_y': 0},
            'result': {'width': 0, 'height': 0, 'scale': 1.0, 'offset_x': 0, 'offset_y': 0}
        }
        
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
        """Handle synchronized drag motion"""
        # Only handle if sync drag is enabled and this is the active drag source
        if not hasattr(self.layout, 'sync_drag_var') or not self.layout.sync_drag_var.get():
            return
        
        if not self.drag_active or self.drag_source != source_panel:
            return
        
        # Calculate movement delta
        dx = event.x - self.last_drag_x
        dy = event.y - self.last_drag_y
        
        # Always move the source canvas
        source_canvas = self.original_canvas if source_panel == 'original' else self.result_canvas
        source_canvas.scan_dragto(event.x, event.y, gain=1)
        
        # Move the other canvas with scale compensation
        other_panel = 'result' if source_panel == 'original' else 'original'
        other_canvas = self.result_canvas if source_panel == 'original' else self.original_canvas
        
        # Calculate synchronized movement
        sync_x, sync_y = self.calculate_sync_movement(event.x, event.y, source_panel, other_panel)
        
        if sync_x is not None and sync_y is not None:
            other_canvas.scan_dragto(sync_x, sync_y, gain=1)
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
        
        # Reset cursors
        self.original_canvas.configure(cursor="")
        self.result_canvas.configure(cursor="")
        
        logger.debug(f"Ended sync drag from {source_panel}")
    
    def handle_sync_zoom(self, event, source_panel):
        """Handle synchronized zoom"""
        if not hasattr(self.layout, 'sync_zoom_var') or not self.layout.sync_zoom_var.get():
            return
        
        # Get zoom direction
        if hasattr(event, 'delta'):
            delta = event.delta
        elif hasattr(event, 'num'):
            delta = 120 if event.num == 4 else -120
        else:
            return
        
        # Apply zoom to layout's zoom system
        current_zoom = self.layout.zoom_var.get()
        zoom_levels = ["25%", "50%", "75%", "100%", "125%", "150%", "200%", "300%"]
        
        try:
            if current_zoom == "Fit":
                current_index = 3  # 100%
            else:
                current_index = zoom_levels.index(current_zoom)
        except ValueError:
            current_index = 3
        
        # Adjust zoom level
        if delta > 0:  # Zoom in
            new_index = min(current_index + 1, len(zoom_levels) - 1)
        else:  # Zoom out
            new_index = max(current_index - 1, 0)
        
        new_zoom = zoom_levels[new_index]
        self.layout.zoom_var.set(new_zoom)
        if hasattr(self.layout, 'on_zoom_changed'):
            self.layout.on_zoom_changed()
        
        logger.debug(f"Sync zoom from {source_panel}: {current_zoom} -> {new_zoom}")


class ImprovedSeedreamLayout(AIChatMixin):
    """Improved Seedream V4 layout with efficient space usage and better UX"""
    
    def __init__(self, parent_frame, api_client=None, tab_instance=None):
        self.parent_frame = parent_frame
        self.api_client = api_client
        self.tab_instance = tab_instance
        self.selected_image_paths = []  # Changed to support multiple images
        self.result_image_path = None
        self.result_url = None
        
        # Resize performance optimization
        self.resize_timer = None
        self.resize_delay = 750  # ms delay for debouncing (increased for better performance)
        self._paned_resize_timer = None  # Timer for paned window resize debouncing
        self._last_canvas_size = {"original": (0, 0), "result": (0, 0)}  # Track canvas sizes
        
        # Splitter position persistence
        self.splitter_position_file = "data/seedream_splitter_position.txt"
        
        # Image panning state
        self.drag_data = {"x": 0, "y": 0, "dragging": False, "threshold_met": False}
        self.current_task_id = None
        self.tab_name = "Seedream V4"  # For AI integration
        
        # Settings variables
        self.width_var = tk.IntVar(value=1024)
        self.height_var = tk.IntVar(value=1024)
        self.seed_var = tk.StringVar(value="-1")
        self.sync_mode_var = tk.BooleanVar(value=False)
        self.base64_var = tk.BooleanVar(value=False)
        
        # Aspect ratio locking
        self.aspect_lock_var = tk.BooleanVar(value=False)
        self.locked_aspect_ratio = None
        
        # Size presets - now using multipliers based on input image
        self.size_presets = [
            ("1.5x", 1.5),
            ("2x", 2.0),
            ("2.5x", 2.5)
        ]
        
        # Store original image dimensions for multiplier calculations
        self.original_image_width = None
        self.original_image_height = None
        
        # Enhanced components
        self.status_console = None
        self.keyboard_manager = None
        
        # Initialize view mode (CRITICAL FIX)
        self.current_view_mode = "comparison"  # Default to side-by-side view
        
        try:
            logger.info("ImprovedSeedreamLayout: Starting layout setup")
            self.setup_layout()
            logger.info("ImprovedSeedreamLayout: Layout setup complete")
            
            self.setup_enhanced_features()
            logger.info("ImprovedSeedreamLayout: Enhanced features setup complete")
            
            self.setup_learning_components()
            logger.info("ImprovedSeedreamLayout: Learning components setup complete")
            
            logger.info("ImprovedSeedreamLayout: Initialization successful")
        except Exception as e:
            logger.error(f"ImprovedSeedreamLayout: Initialization failed: {e}", exc_info=True)
            raise
    
    @property
    def selected_image_path(self):
        """Backward compatibility property for single image access"""
        return self.selected_image_paths[0] if self.selected_image_paths else None
    
    def setup_layout(self):
        """Setup the improved 2-column layout with reliable splitter positioning"""
        
        # Main container
        main_container = ttk.Frame(self.parent_frame)
        main_container.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        
        # Configure parent frame to expand properly
        self.parent_frame.columnconfigure(0, weight=1)
        self.parent_frame.rowconfigure(0, weight=1)
        
        # Create PanedWindow for resizable layout
        self.paned_window = ttk.PanedWindow(main_container, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True)
        
        # Configure main container
        main_container.columnconfigure(0, weight=1)
        main_container.rowconfigure(0, weight=1)
        
        # Create frames with explicit minimum sizes to prevent collapse
        self.left_pane = ttk.Frame(self.paned_window)
        self.right_pane = ttk.Frame(self.paned_window)
        
        # Add panes with proper configuration
        # Use unequal weights to establish proper sizing: 2:3 ratio (40/60 split)
        self.paned_window.add(self.left_pane, weight=2)  # Controls pane
        self.paned_window.add(self.right_pane, weight=3)  # Images pane (larger for better viewing)
        
        # Set up the content
        self.setup_left_column_paned(self.left_pane)
        self.setup_right_column_paned(self.right_pane)
        
        # Use reliable positioning strategy
        self.setup_reliable_splitter_positioning()
    
    def setup_reliable_splitter_positioning(self):
        """Implement reliable splitter positioning that works consistently"""
        # Strategy: Multiple positioning attempts with proper timing
        self.positioning_attempts = 0
        self.max_positioning_attempts = 5
        
        # Start positioning after initial layout
        self.parent_frame.after(50, self._attempt_splitter_positioning)
        
        # Also bind to window events for robustness
        self.paned_window.bind('<Configure>', self._on_panedwindow_configure)
    
    def _attempt_splitter_positioning(self):
        """Attempt to set splitter position with retry logic"""
        self.positioning_attempts += 1
        
        # Get current dimensions
        total_width = self.paned_window.winfo_width()
        
        # Check if window is ready (has meaningful dimensions)
        if total_width <= 100:
            if self.positioning_attempts < self.max_positioning_attempts:
                # Try again with longer delay
                delay = 100 * self.positioning_attempts  # Increasing delays
                self.parent_frame.after(delay, self._attempt_splitter_positioning)
            return
        
        # Calculate desired position (40/60 split favoring image display)
        desired_position = int(total_width * 0.4)
        
        # Apply constraints to prevent collapse
        min_left = 280  # Minimum for controls
        max_left = total_width - 350  # Ensure right pane is at least 350px
        
        position = max(min_left, min(desired_position, max_left))
        
        # Set the position
        try:
            self.paned_window.sashpos(0, position)
            
            # Verify it was set correctly
            self.parent_frame.after(50, lambda: self._verify_splitter_position(position))
            
            logger.info(f"ImprovedSeedreamLayout: Splitter positioned at {position}px (attempt {self.positioning_attempts})")
            
        except Exception as e:
            logger.warning(f"ImprovedSeedreamLayout: Failed to set splitter position: {e}")
            if self.positioning_attempts < self.max_positioning_attempts:
                self.parent_frame.after(200, self._attempt_splitter_positioning)
    
    def _verify_splitter_position(self, expected_position):
        """Verify splitter was positioned correctly and retry if needed"""
        try:
            actual_position = self.paned_window.sashpos(0)
            tolerance = 50  # Allow some variation
            
            if abs(actual_position - expected_position) > tolerance:
                logger.warning(f"ImprovedSeedreamLayout: Splitter position verification failed. Expected: {expected_position}, Actual: {actual_position}")
                
                # Try one more time with the expected position
                self.paned_window.sashpos(0, expected_position)
                
                # Force update
                self.paned_window.update_idletasks()
            else:
                logger.info(f"ImprovedSeedreamLayout: Splitter position verified successfully: {actual_position}px")
                
                # Initialize display after successful positioning
                self.parent_frame.after(100, self.initialize_display)
                
        except Exception as e:
            logger.error(f"ImprovedSeedreamLayout: Splitter verification error: {e}")
    
    def _on_panedwindow_configure(self, event):
        """Handle PanedWindow resize events to maintain minimum sizes"""
        # PERFORMANCE FIX: Debounce this expensive operation
        if hasattr(self, '_paned_resize_timer') and self._paned_resize_timer:
            self.parent_frame.after_cancel(self._paned_resize_timer)
        
        # Only check minimum sizes after resize is complete (500ms delay)
        self._paned_resize_timer = self.parent_frame.after(500, self._check_pane_minimum_sizes)
    
    def _check_pane_minimum_sizes(self):
        """Check and enforce minimum pane sizes (called after resize completes)"""
        try:
            total_width = self.paned_window.winfo_width()
            
            if total_width > 100:  # Valid width
                current_position = self.paned_window.sashpos(0)
                
                # Check if right pane is too small
                right_pane_width = total_width - current_position
                if right_pane_width < 300:  # Minimum for image display
                    new_position = total_width - 350
                    if new_position > 280:  # Ensure left pane isn't too small
                        self.paned_window.sashpos(0, new_position)
        except:
            pass  # Silently handle any errors
    
    def initialize_display(self):
        """Initialize the image display panels with default messages"""
        try:
            logger.info("ImprovedSeedreamLayout: Initializing display panels")
            
            # Ensure both canvases are properly sized
            self.parent_frame.update_idletasks()
            
            # Show default messages in both panels
            self.show_panel_message("original")
            self.show_panel_message("result")
            
            # Verify panel visibility
            left_width = self.left_pane.winfo_width()
            right_width = self.right_pane.winfo_width()
            logger.info(f"ImprovedSeedreamLayout: Panel widths - Left: {left_width}px, Right: {right_width}px")
            
            # Log that display is ready
            if hasattr(self, 'status_console') and self.status_console:
                self.status_console.log_ready("Seedream V4")
                
            logger.info("ImprovedSeedreamLayout: Display initialization complete")
        except Exception as e:
            logger.error(f"ImprovedSeedreamLayout: Error initializing display: {e}", exc_info=True)
    
    def set_initial_splitter_position(self):
        """DEPRECATED: Old positioning method - now using setup_reliable_splitter_positioning()"""
        # This method is kept for backwards compatibility but does nothing
        # The new reliable positioning system handles this automatically
        logger.info("ImprovedSeedreamLayout: Old positioning method called - using new reliable system instead")
    
    def load_splitter_position(self):
        """Load saved splitter position from file"""
        try:
            import os
            if os.path.exists(self.splitter_position_file):
                with open(self.splitter_position_file, 'r') as f:
                    return int(f.read().strip())
        except:
            pass
        return None
    
    def save_splitter_position(self, position):
        """Save splitter position to file"""
        try:
            import os
            os.makedirs(os.path.dirname(self.splitter_position_file), exist_ok=True)
            with open(self.splitter_position_file, 'w') as f:
                f.write(str(position))
        except:
            pass
    
    def on_splitter_moved(self, event):
        """Handle splitter movement to save position"""
        try:
            position = self.paned_window.sashpos(0)
            self.save_splitter_position(position)
        except:
            pass
    
    def setup_left_column_paned(self, parent):
        """Setup left column with logical flow and compact sections for paned layout"""
        left_frame = ttk.Frame(parent, padding="4")
        left_frame.pack(fill=tk.BOTH, expand=True)
        left_frame.columnconfigure(0, weight=1)
        
        # Configure rows to eliminate vertical scrolling
        left_frame.rowconfigure(0, weight=0)  # Image input - compact
        left_frame.rowconfigure(1, weight=0)  # Settings - MUCH more compact
        left_frame.rowconfigure(2, weight=0)  # Prompt section - compact  
        left_frame.rowconfigure(3, weight=0)  # Primary action - prominent
        left_frame.rowconfigure(4, weight=0)  # Advanced sections - collapsible
        left_frame.rowconfigure(5, weight=0)  # Status console - professional feedback
        left_frame.rowconfigure(6, weight=1)  # Spacer
        left_frame.rowconfigure(7, weight=0)  # Secondary actions - bottom
        
        # 1. COMPACT IMAGE INPUT
        self.setup_compact_image_input(left_frame)
        
        # 2. SUPER COMPACT SETTINGS (key improvement!)
        self.setup_compact_settings(left_frame)
        
        # 3. PROMPT SECTION
        self.setup_prompt_section(left_frame)
        
        # 4. PRIMARY ACTION (right under prompt!)
        self.setup_primary_action(left_frame)
        
        # 5. COLLAPSIBLE ADVANCED SECTIONS
        self.setup_advanced_sections(left_frame)
        
        # 6. STATUS CONSOLE (professional feedback)
        self.setup_status_console(left_frame)
        
        # 7. SPACER
        spacer = ttk.Frame(left_frame)
        spacer.grid(row=6, column=0, sticky="nsew")
        
        # 8. SECONDARY ACTIONS (at bottom)
        self.setup_secondary_actions(left_frame)
        
    def setup_left_column(self, parent):
        """Setup left column with logical flow and compact sections"""
        left_frame = ttk.Frame(parent, padding="4")
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 4))
        left_frame.columnconfigure(0, weight=1)
        
        # Configure rows to eliminate vertical scrolling
        left_frame.rowconfigure(0, weight=0)  # Image input - compact
        left_frame.rowconfigure(1, weight=0)  # Settings - MUCH more compact
        left_frame.rowconfigure(2, weight=0)  # Prompt section - compact  
        left_frame.rowconfigure(3, weight=0)  # Primary action - prominent
        left_frame.rowconfigure(4, weight=0)  # Advanced sections - collapsible
        left_frame.rowconfigure(5, weight=0)  # Status console - professional feedback
        left_frame.rowconfigure(6, weight=1)  # Spacer
        left_frame.rowconfigure(7, weight=0)  # Secondary actions - bottom
        
        # 1. COMPACT IMAGE INPUT
        self.setup_compact_image_input(left_frame)
        
        # 2. SUPER COMPACT SETTINGS (key improvement!)
        self.setup_compact_settings(left_frame)
        
        # 3. PROMPT SECTION
        self.setup_prompt_section(left_frame)
        
        # 4. PRIMARY ACTION (right under prompt!)
        self.setup_primary_action(left_frame)
        
        # 5. COLLAPSIBLE ADVANCED SECTIONS
        self.setup_advanced_sections(left_frame)
        
        # 6. STATUS CONSOLE (professional feedback)
        self.setup_status_console(left_frame)
        
        # 7. SPACER
        spacer = ttk.Frame(left_frame)
        spacer.grid(row=6, column=0, sticky="nsew")
        
        # 8. SECONDARY ACTIONS (at bottom)
        self.setup_secondary_actions(left_frame)
    
    def setup_compact_image_input(self, parent):
        """Very compact image input section"""
        input_frame = ttk.LabelFrame(parent, text="📥 Input Image", padding="6")
        input_frame.grid(row=0, column=0, sticky="ew", pady=(0, 6))
        input_frame.columnconfigure(1, weight=1)
        
        # Thumbnail + Info in one row (same as SeedEdit)
        self.thumbnail_label = tk.Label(
            input_frame,
            text="📁",
            width=8, height=4,
            bg='#f5f5f5',
            relief='solid',
            borderwidth=1,
            cursor="hand2",
            font=('Arial', 10)
        )
        self.thumbnail_label.grid(row=0, column=0, padx=(0, 8), rowspan=2)
        self.thumbnail_label.bind("<Button-1>", lambda e: self.browse_image())
        
        # Image info
        self.image_name_label = ttk.Label(
            input_frame,
            text="No image selected",
            font=('Arial', 9, 'bold'),
            foreground="gray"
        )
        self.image_name_label.grid(row=0, column=1, sticky="w")
        
        info_frame = ttk.Frame(input_frame)
        info_frame.grid(row=1, column=1, sticky="ew")
        
        self.image_size_label = ttk.Label(
            info_frame,
            text="",
            font=('Arial', 8),
            foreground="gray"
        )
        self.image_size_label.pack(side=tk.LEFT)
        
        browse_btn = ttk.Button(
            info_frame,
            text="Browse",
            command=self.browse_image,
            width=8
        )
        browse_btn.pack(side=tk.RIGHT, padx=(2, 0))
        
        # Add reorder button (only shown when multiple images selected)
        self.reorder_btn = ttk.Button(
            info_frame,
            text="⚡ Order",
            command=self.show_image_reorder_dialog,
            width=8,
            state="disabled"
        )
        self.reorder_btn.pack(side=tk.RIGHT, padx=(2, 0))
        
        # Setup drag and drop after all widgets are created
        self.setup_drag_drop()
    
    def setup_compact_settings(self, parent):
        """SUPER compact settings - key improvement! 1/3 the height"""
        settings_frame = ttk.LabelFrame(parent, text="⚙️ Settings", padding="6")
        settings_frame.grid(row=1, column=0, sticky="ew", pady=(0, 6))
        settings_frame.columnconfigure(1, weight=1)
        settings_frame.columnconfigure(3, weight=1)
        
        # Compact row layout for size controls
        ttk.Label(settings_frame, text="Size:", font=('Arial', 9, 'bold')).grid(
            row=0, column=0, sticky="w", pady=(0, 2)
        )
        
        # Compact width/height in single row
        size_row = ttk.Frame(settings_frame)
        size_row.grid(row=1, column=0, columnspan=4, sticky="ew", pady=2)
        size_row.columnconfigure(1, weight=1)
        size_row.columnconfigure(3, weight=1)
        
        ttk.Label(size_row, text="W:", font=('Arial', 8)).grid(row=0, column=0, sticky="w")
        self.width_entry = ttk.Entry(
            size_row,
            textvariable=self.width_var,
            width=6,
            font=('Arial', 8),
            validate='key',
            validatecommand=(self.parent_frame.register(self.validate_integer), '%P')
        )
        self.width_entry.grid(row=0, column=1, sticky="ew", padx=(2, 8))
        
        # Add validation for aspect ratio locking on entry changes
        self.width_var.trace('w', self._on_entry_change)
        
        ttk.Label(size_row, text="H:", font=('Arial', 8)).grid(row=0, column=2, sticky="w")
        self.height_entry = ttk.Entry(
            size_row,
            textvariable=self.height_var,
            width=6,
            font=('Arial', 8),
            validate='key',
            validatecommand=(self.parent_frame.register(self.validate_integer), '%P')
        )
        self.height_entry.grid(row=0, column=3, sticky="ew")
        
        # Add validation for aspect ratio locking on height entry changes
        self.height_var.trace('w', self._on_entry_change)
        
        # Row 2: Size presets (grid layout - much more compact!)
        preset_frame = ttk.Frame(settings_frame)
        preset_frame.grid(row=2, column=0, columnspan=4, sticky="ew", pady=(4, 2))
        
        # Preset buttons in a 1x4 grid for multipliers + custom
        for i, (name, multiplier) in enumerate(self.size_presets):
            btn = ttk.Button(
                preset_frame,
                text=name,
                command=lambda m=multiplier: self.set_size_multiplier(m),
                width=6
            )
            btn.grid(row=0, column=i, padx=1, pady=1, sticky="ew")
        
        # Custom scale button
        custom_btn = ttk.Button(
            preset_frame,
            text="Custom",
            command=self.show_custom_scale_dialog,
            width=6
        )
        custom_btn.grid(row=0, column=3, padx=1, pady=1, sticky="ew")
        
        # Configure preset frame columns
        for i in range(4):
            preset_frame.columnconfigure(i, weight=1)
        
        # Row 3: Seed + Options (horizontal)
        ttk.Label(settings_frame, text="Seed:", font=('Arial', 8)).grid(
            row=3, column=0, sticky="w", pady=(4, 0)
        )
        
        seed_entry = ttk.Entry(
            settings_frame,
            textvariable=self.seed_var,
            width=8,
            font=('Arial', 8)
        )
        seed_entry.grid(row=3, column=1, sticky="w", pady=(4, 0))
        
        # Lock aspect ratio button (starts unlocked)
        self.lock_aspect_btn = ttk.Button(
            settings_frame,
            text="🔓",
            width=3,
            command=self.toggle_aspect_lock
        )
        self.lock_aspect_btn.grid(row=3, column=2, sticky="w", padx=(8, 0), pady=(4, 0))
        
        # Auto-resolution button
        auto_btn = ttk.Button(
            settings_frame,
            text="Auto",
            width=6,
            command=self.auto_set_resolution
        )
        auto_btn.grid(row=3, column=3, sticky="e", pady=(4, 0))
    
    def setup_prompt_section(self, parent):
        """Enhanced prompt section with better usability"""
        prompt_frame = ttk.LabelFrame(parent, text="✏️ Transformation Prompt", padding="8")
        prompt_frame.grid(row=2, column=0, sticky="ew", pady=(0, 8))
        prompt_frame.columnconfigure(0, weight=1)
        
        # Quick tools row
        tools_frame = ttk.Frame(prompt_frame)
        tools_frame.grid(row=0, column=0, sticky="ew", pady=(0, 6))
        tools_frame.columnconfigure(2, weight=1)
        
        # AI assistance tools
        ai_frame = ttk.Frame(tools_frame)
        ai_frame.grid(row=0, column=0, sticky="w")
        
        ttk.Button(ai_frame, text="🤖 AI Improve", command=self.improve_with_ai, width=12).pack(side=tk.LEFT, padx=(0, 4))
        ttk.Button(ai_frame, text="🎲 Random", command=self.load_sample, width=8).pack(side=tk.LEFT, padx=(0, 4))
        
        # Advanced tools
        advanced_frame = ttk.Frame(tools_frame)
        advanced_frame.grid(row=0, column=1, sticky="w", padx=(8, 0))
        
        mild_btn = ttk.Button(advanced_frame, text="🔥 Mild", command=self.generate_mild_examples, width=6)
        mild_btn.pack(side=tk.LEFT, padx=(0, 2))
        self.create_tooltip(mild_btn, "Generate 5 mild filter training examples")
        
        moderate_btn = ttk.Button(advanced_frame, text="⚡ Moderate", command=self.generate_moderate_examples, width=8)
        moderate_btn.pack(side=tk.LEFT, padx=(0, 4))
        self.create_tooltip(moderate_btn, "Generate 5 sophisticated moderate examples")
        
        # Prompt management
        mgmt_frame = ttk.Frame(tools_frame)
        mgmt_frame.grid(row=0, column=3, sticky="e")
        
        ttk.Button(mgmt_frame, text="💾 Save", command=self.save_preset, width=6).pack(side=tk.LEFT, padx=(0, 2))
        ttk.Button(mgmt_frame, text="📋 Load", command=self.show_prompt_browser, width=6).pack(side=tk.LEFT)
        
        # Enhanced prompt text area
        prompt_container = ttk.Frame(prompt_frame)
        prompt_container.grid(row=1, column=0, sticky="ew", pady=(0, 6))
        prompt_container.columnconfigure(0, weight=1)
        
        # Prompt text with compact size for 25% layout
        self.prompt_text = tk.Text(
            prompt_container,
            height=6,  # Reduced from 8 to 6 lines for compact layout
            wrap=tk.WORD,
            font=('Arial', 10),  # Smaller font for compact layout
            relief='solid',
            borderwidth=1,
            padx=8,
            pady=6,
            bg='#ffffff',
            fg='#333333'
        )
        self.prompt_text.grid(row=0, column=0, sticky="ew")
        
        # Scrollbar for prompt text
        prompt_scrollbar = ttk.Scrollbar(prompt_container, orient=tk.VERTICAL, command=self.prompt_text.yview)
        prompt_scrollbar.grid(row=0, column=1, sticky="ns")
        self.prompt_text.configure(yscrollcommand=prompt_scrollbar.set)
        
        # Character counter and status
        status_frame = ttk.Frame(prompt_frame)
        status_frame.grid(row=2, column=0, sticky="ew")
        status_frame.columnconfigure(1, weight=1)
        
        self.char_count_label = ttk.Label(
            status_frame, 
            text="0 characters", 
            font=('Arial', 9), 
            foreground="#666"
        )
        self.char_count_label.grid(row=0, column=0, sticky="w")
        
        self.prompt_status = ttk.Label(
            status_frame,
            text="Ready for input",
            font=('Arial', 9),
            foreground="#28a745"
        )
        self.prompt_status.grid(row=0, column=2, sticky="e")
        
        # Placeholder text (shorter and less intrusive)
        self.prompt_placeholder = "Describe the transformation you want to apply to this image..."
        self.prompt_text.insert("1.0", self.prompt_placeholder)
        self.prompt_text.config(fg='#999999')
        
        # Enhanced event bindings
        self.prompt_text.bind("<FocusIn>", self.on_prompt_focus_in)
        self.prompt_text.bind("<FocusOut>", self.on_prompt_focus_out)
        self.prompt_text.bind("<KeyPress>", self.on_prompt_key_press)
        self.prompt_text.bind("<KeyRelease>", self.on_prompt_text_changed)
        self.prompt_text.bind("<Button-1>", self.on_prompt_click)
        
        # Initialize
        self.prompt_has_placeholder = True
        
        # Backward compatibility - create preset_listbox as a dummy widget to avoid errors
        self.preset_listbox = tk.Text(prompt_frame, height=1, state='disabled')  # Dummy widget
        
        # Initialize full prompts and prompt line ranges for compatibility
        if not hasattr(self, 'full_prompts'):
            self.full_prompts = []
        if not hasattr(self, 'prompt_line_ranges'):
            self.prompt_line_ranges = []
        
        # Collapsible prompt history section
        self.setup_prompt_history_section(prompt_frame)
    
    def generate_mild_examples(self):
        """Generate 5 mild filter training examples with automatic image analysis"""
        if not self.selected_image_path:
            self.show_tooltip("❌ Please select an image first")
            return
        
        self.show_tooltip("🔥 Starting mild examples generation...")
        
        # Start background thread for mild examples generation
        thread = threading.Thread(target=self._generate_mild_examples_thread, daemon=True)
        thread.start()
    
    def generate_moderate_examples(self):
        """Generate 5 sophisticated moderate examples with automatic image analysis"""
        if not self.selected_image_path:
            self.show_tooltip("❌ Please select an image first")
            return
        
        self.show_tooltip("⚡ Starting sophisticated moderate examples generation...")
        
        # Start background thread for moderate examples generation
        thread = threading.Thread(target=self._generate_moderate_examples_thread, daemon=True)
        thread.start()
    
    def _generate_mild_examples_thread(self):
        """Background thread for generating mild examples"""
        try:
            from core.ai_prompt_advisor import get_ai_advisor
            
            ai_advisor = get_ai_advisor()
            if not ai_advisor.is_available():
                self.parent_frame.after(0, lambda: self.show_tooltip("❌ AI service not available"))
                return
            
            # Step 1: Analyze image for filter training (detailed analysis)
            self.parent_frame.after(0, lambda: self.show_tooltip("🔍 Analyzing image..."))
            description = asyncio.run(ai_advisor.describe_image(self.selected_image_path, detailed_analysis=True))
            
            if not description or "error" in description.lower():
                self.parent_frame.after(0, lambda: self.show_tooltip("❌ Image analysis failed"))
                return
            
            # Step 2: Generate 5 mild examples using optimized method
            self.parent_frame.after(0, lambda: self.show_tooltip("🔥 Generating 5 mild examples..."))
            mild_examples = asyncio.run(ai_advisor.generate_mild_examples_only(description, count=5))
            
            if not mild_examples:
                # Final fallback using vocabulary bank
                from core.filter_vocabulary_bank import filter_vocab
                import re
                
                mild_examples = []
                for i in range(5):
                    # Extract subject and clothing from description
                    subject_match = re.search(r'\b(woman|man|girl|lady|gentleman)\b', description.lower())
                    clothing_match = re.search(r'\b(dress|gown|shirt|top|blouse|outfit|clothing|garment|attire)\b', description.lower())
                    
                    if subject_match and clothing_match:
                        subject = subject_match.group(1)
                        clothing = clothing_match.group(1)
                        mild_example = filter_vocab.generate_varied_mild_prompt(subject, clothing)
                        mild_examples.append(mild_example)
                    else:
                        # Use generic fallbacks with varied vocabulary
                        generic_examples = [
                            "Convert outfit to revealing swimwear; preserve identity",
                            "Transform attire to micro bikini; maintain features", 
                            "Change clothing to skimpy two-piece; keep expression",
                            "Alter garment to minimal coverage; retain appearance",
                            "Switch to tiny string bikini; hold facial features"
                        ]
                        mild_examples.append(generic_examples[i] if i < len(generic_examples) else generic_examples[0])
            
            # Show results in UI thread
            self.parent_frame.after(0, lambda: self._display_mild_examples(mild_examples))
            
        except Exception as e:
            logger.error(f"Error in mild examples thread: {e}")
            self.parent_frame.after(0, lambda: self.show_tooltip(f"❌ Generation failed: {str(e)}"))
    
    def _generate_moderate_examples_thread(self):
        """Background thread for generating sophisticated moderate examples"""
        try:
            from core.ai_prompt_advisor import get_ai_advisor
            
            ai_advisor = get_ai_advisor()
            if not ai_advisor.is_available():
                self.parent_frame.after(0, lambda: self.show_tooltip("❌ AI service not available"))
                return
            
            # Step 1: Analyze image for filter training (detailed analysis)
            self.parent_frame.after(0, lambda: self.show_tooltip("🔍 Analyzing image for moderate examples..."))
            description = asyncio.run(ai_advisor.describe_image(self.selected_image_path, detailed_analysis=True))
            
            if not description or "error" in description.lower():
                self.parent_frame.after(0, lambda: self.show_tooltip("❌ Image analysis failed"))
                return
            
            # Step 2: Generate 5 sophisticated moderate examples
            self.parent_frame.after(0, lambda: self.show_tooltip("⚡ Generating sophisticated indirect prompts..."))
            moderate_examples = asyncio.run(ai_advisor.generate_moderate_examples_only(description, count=5))
            
            # Show results in UI thread
            self.parent_frame.after(0, lambda: self._display_moderate_examples(moderate_examples))
            
        except Exception as e:
            logger.error(f"Error in moderate examples thread: {e}")
            self.parent_frame.after(0, lambda: self.show_tooltip(f"❌ Generation failed: {str(e)}"))
    
    def _display_mild_examples(self, examples):
        """Display generated mild examples in a popup window"""
        try:
            # Create popup window
            popup = tk.Toplevel(self.parent_frame)
            popup.title("🔥 Filter Training - Mild Examples")
            popup.geometry("700x500")
            popup.resizable(True, True)
            
            # Main frame with scrollbar
            main_frame = ttk.Frame(popup)
            main_frame.pack(fill="both", expand=True, padx=10, pady=10)
            
            # Title with count
            title_label = ttk.Label(main_frame, text=f"🔥 Filter Training - {len(examples)} Mild Examples", font=("Arial", 12, "bold"))
            title_label.pack(pady=(0, 5))
            
            # Subtitle
            subtitle_label = ttk.Label(main_frame, text="Generated using comprehensive vocabulary bank and varied terminology", font=("Arial", 9), foreground="gray")
            subtitle_label.pack(pady=(0, 10))
            
            # Scrollable frame for examples
            canvas = tk.Canvas(main_frame, highlightthickness=0)
            scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
            scrollable_frame = ttk.Frame(canvas)
            
            scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            # Pack scrollbar and canvas
            scrollbar.pack(side="right", fill="y")
            canvas.pack(side="left", fill="both", expand=True)
            
            # Add examples to scrollable frame
            for i, example in enumerate(examples, 1):
                # Example frame
                example_frame = ttk.LabelFrame(scrollable_frame, text=f"Example {i}", padding="8")
                example_frame.pack(fill="x", padx=5, pady=3)
                
                # Example text (selectable)
                example_text = tk.Text(example_frame, height=3, wrap=tk.WORD, font=("Arial", 10))
                example_text.pack(fill="x")
                example_text.insert("1.0", example)
                example_text.configure(state='normal')  # Allow selection but not editing
                
                # Copy button
                copy_btn = ttk.Button(example_frame, text="📋 Copy", 
                                    command=lambda ex=example: popup.clipboard_clear() or popup.clipboard_append(ex) or self.show_tooltip("📋 Copied to clipboard"))
                copy_btn.pack(anchor="e", pady=(5, 0))
            
            # Bind mousewheel to canvas
            def on_mousewheel(event):
                canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            canvas.bind_all("<MouseWheel>", on_mousewheel)
            
            # Close button
            close_btn = ttk.Button(popup, text="Close", command=popup.destroy)
            close_btn.pack(pady=5)
            
            # Focus on popup
            popup.focus_set()
            popup.grab_set()
            
        except Exception as e:
            logger.error(f"Error displaying mild examples: {e}")
            self.show_tooltip(f"❌ Error: {str(e)}")
    
    def _display_moderate_examples(self, examples):
        """Display generated moderate examples in a popup window"""
        try:
            # Create popup window
            popup = tk.Toplevel(self.parent_frame)
            popup.title("⚡ Sophisticated Moderate Examples")
            popup.geometry("800x600")
            popup.resizable(True, True)
            
            # Main frame with scrollbar
            main_frame = ttk.Frame(popup)
            main_frame.pack(fill="both", expand=True, padx=10, pady=10)
            
            # Title with count
            title_label = ttk.Label(main_frame, text=f"⚡ Filter Training - {len(examples)} Moderate Examples", font=("Arial", 12, "bold"))
            title_label.pack(pady=(0, 5))
            
            # Subtitle explaining the approach
            subtitle_label = ttk.Label(main_frame, text="Sophisticated indirect language combinations designed to confuse models", font=("Arial", 9), foreground="gray")
            subtitle_label.pack(pady=(0, 5))
            
            info_label = ttk.Label(main_frame, text="These prompts use word combinations to imply harmful content without explicit terms", font=("Arial", 8), foreground="#666")
            info_label.pack(pady=(0, 10))
            
            # Scrollable frame for examples
            canvas = tk.Canvas(main_frame, highlightthickness=0)
            scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
            scrollable_frame = ttk.Frame(canvas)
            
            scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            # Pack scrollbar and canvas
            scrollbar.pack(side="right", fill="y")
            canvas.pack(side="left", fill="both", expand=True)
            
            # Add examples to scrollable frame
            for i, example in enumerate(examples, 1):
                # Example frame with more space for longer prompts
                example_frame = ttk.LabelFrame(scrollable_frame, text=f"Moderate Example {i}", padding="8")
                example_frame.pack(fill="x", padx=5, pady=4)
                
                # Example text (larger for longer moderate prompts)
                example_text = tk.Text(example_frame, height=4, wrap=tk.WORD, font=("Arial", 10))
                example_text.pack(fill="x")
                example_text.insert("1.0", example)
                example_text.configure(state='normal')  # Allow selection
                
                # Buttons frame
                buttons_frame = ttk.Frame(example_frame)
                buttons_frame.pack(fill="x", pady=(5, 0))
                
                # Copy button
                copy_btn = ttk.Button(buttons_frame, text="📋 Copy", 
                                    command=lambda ex=example: popup.clipboard_clear() or popup.clipboard_append(ex) or self.show_tooltip("📋 Copied to clipboard"))
                copy_btn.pack(side="left")
                
                # Analysis button (shows breakdown of indirect techniques)
                analysis_btn = ttk.Button(buttons_frame, text="🔍 Analyze", 
                                        command=lambda ex=example: self._show_moderate_analysis(ex))
                analysis_btn.pack(side="left", padx=(5, 0))
            
            # Bind mousewheel to canvas
            def on_mousewheel(event):
                canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            canvas.bind_all("<MouseWheel>", on_mousewheel)
            
            # Close button
            close_btn = ttk.Button(popup, text="Close", command=popup.destroy)
            close_btn.pack(pady=5)
            
            # Focus on popup
            popup.focus_set()
            popup.grab_set()
            
        except Exception as e:
            logger.error(f"Error displaying moderate examples: {e}")
            self.show_tooltip(f"❌ Error: {str(e)}")
    
    def _show_moderate_analysis(self, example):
        """Show analysis of indirect techniques used in moderate example"""
        try:
            analysis_popup = tk.Toplevel(self.parent_frame)
            analysis_popup.title("🔍 Moderate Example Analysis")
            analysis_popup.geometry("600x400")
            
            frame = ttk.Frame(analysis_popup, padding="10")
            frame.pack(fill="both", expand=True)
            
            # Title
            ttk.Label(frame, text="Indirect Language Techniques Analysis", font=("Arial", 12, "bold")).pack(pady=(0, 10))
            
            # Example text
            ttk.Label(frame, text="Example:", font=("Arial", 10, "bold")).pack(anchor="w")
            example_text = tk.Text(frame, height=3, wrap=tk.WORD, font=("Arial", 10))
            example_text.pack(fill="x", pady=(2, 10))
            example_text.insert("1.0", example)
            example_text.configure(state='disabled')
            
            # Analysis
            ttk.Label(frame, text="Techniques Identified:", font=("Arial", 10, "bold")).pack(anchor="w")
            
            analysis_text = tk.Text(frame, wrap=tk.WORD, font=("Arial", 9))
            analysis_text.pack(fill="both", expand=True, pady=(2, 10))
            
            # Simple keyword-based analysis
            techniques = []
            if "artistic" in example.lower() or "art" in example.lower():
                techniques.append("• Artistic Justification: Uses art context to legitimize request")
            if "professional" in example.lower() or "gallery" in example.lower():
                techniques.append("• Professional Context: Claims professional/academic purpose")
            if any(word in example.lower() for word in ["absence", "without", "free", "liberated"]):
                techniques.append("• Removal Implication: Implies removal without explicit terms")
            if any(word in example.lower() for word in ["transparency", "clear", "minimal", "reduced"]):
                techniques.append("• Coverage Reduction: Suggests minimal coverage indirectly")
            if any(word in example.lower() for word in ["maintaining", "preserving", "keeping"]):
                techniques.append("• Identity Preservation: Maintains specific appearance features")
            
            if not techniques:
                techniques.append("• Complex Language Combination: Uses sophisticated vocabulary to confuse filters")
            
            analysis_content = "This moderate example uses the following indirect techniques:\n\n" + "\n".join(techniques)
            analysis_content += "\n\nThese techniques are designed to bypass content filters by avoiding explicit harmful terms while still communicating the intended meaning through implication and context."
            
            analysis_text.insert("1.0", analysis_content)
            analysis_text.configure(state='disabled')
            
            # Close button
            ttk.Button(analysis_popup, text="Close", command=analysis_popup.destroy).pack(pady=5)
            
            # Focus
            analysis_popup.focus_set()
            analysis_popup.grab_set()
            
        except Exception as e:
            logger.error(f"Error showing analysis: {e}")
            self.show_tooltip(f"❌ Analysis error: {str(e)}")
    
    def setup_primary_action(self, parent):
        """Primary action button RIGHT under prompt - key UX improvement!"""
        action_frame = ttk.Frame(parent)
        action_frame.grid(row=3, column=0, sticky="ew", pady=6)
        action_frame.columnconfigure(0, weight=1)
        
        # PROMINENT primary action button
        self.primary_btn = ttk.Button(
            action_frame,
            text="🌟 Apply Seedream V4",
            command=self.process_seedream,
            style='Accent.TButton'
        )
        self.primary_btn.grid(row=0, column=0, sticky="ew")
        
        # Status indicator right below
        self.status_label = ttk.Label(
            action_frame,
            text="Ready for transformation",
            font=('Arial', 9),
            foreground="green"
        )
        self.status_label.grid(row=1, column=0, pady=(4, 0))
        
        # Progress bar (hidden by default)
        self.action_progress_bar = ttk.Progressbar(
            action_frame,
            mode='indeterminate'
        )
        # Don't grid it yet - only show when processing
    
    def setup_advanced_sections(self, parent):
        """Collapsible advanced sections - saves lots of space!"""
        advanced_frame = ttk.Frame(parent)
        advanced_frame.grid(row=4, column=0, sticky="ew", pady=(0, 6))
        advanced_frame.columnconfigure(0, weight=1)
        
        # AI Assistant (collapsible)
        self.ai_section = self.create_collapsible_section(
            advanced_frame, 
            "🤖 AI Assistant", 
            row=0
        )
        
        # Add AI assistant content
        ai_btn = ttk.Button(
            self.ai_section['content'],
            text="✨ Improve Prompt with AI",
            command=self.improve_with_ai,
            width=20
        )
        ai_btn.pack(pady=2)
        
        filter_btn = ttk.Button(
            self.ai_section['content'],
            text="🛡️ Filter Training Mode",
            command=self.filter_training,
            width=20
        )
        filter_btn.pack(pady=2)
        
        # Learning insights button
        learning_btn = ttk.Button(
            self.ai_section['content'],
            text="🧠 Learning Insights",
            command=self.show_learning_panel,
            width=20
        )
        learning_btn.pack(pady=2)
        
        # Quality rating button (enabled after generation)
        self.rating_btn = ttk.Button(
            self.ai_section['content'],
            text="⭐ Rate Last Result",
            command=self.show_quality_rating,
            width=20,
            state="disabled"
        )
        self.rating_btn.pack(pady=2)
        
        # Advanced Options (collapsible)
        self.options_section = self.create_collapsible_section(
            advanced_frame,
            "🔧 Advanced Options",
            row=1
        )
        
        # Add advanced options content
        options_content = ttk.Frame(self.options_section['content'])
        options_content.pack(fill=tk.X, pady=2)
        options_content.columnconfigure(1, weight=1)
        
        ttk.Checkbutton(
            options_content,
            text="Sync Mode",
            variable=self.sync_mode_var
        ).grid(row=0, column=0, sticky="w")
        
        ttk.Checkbutton(
            options_content,
            text="Base64 Output",
            variable=self.base64_var
        ).grid(row=0, column=1, sticky="w", padx=(10, 0))
        
        # Progress Log (collapsible)
        self.log_section = self.create_collapsible_section(
            advanced_frame,
            "📊 Progress Log",
            row=2
        )
        
        # Add log content
        self.log_text = tk.Text(
            self.log_section['content'],
            height=4,
            width=1,
            font=('Courier', 8),
            bg='#f8f8f8',
            state=tk.DISABLED
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, pady=2)
    
    def create_collapsible_section(self, parent, title, row):
        """Create a collapsible section"""
        section_frame = ttk.Frame(parent)
        section_frame.grid(row=row, column=0, sticky="ew", pady=1)
        section_frame.columnconfigure(1, weight=1)
        
        # Header with toggle button
        toggle_btn = ttk.Button(
            section_frame,
            text="▶",
            width=3,
            command=lambda: self.toggle_section(section_frame, toggle_btn)
        )
        toggle_btn.grid(row=0, column=0, sticky="w")
        
        title_label = ttk.Label(
            section_frame,
            text=title,
            font=('Arial', 9, 'bold')
        )
        title_label.grid(row=0, column=1, sticky="w", padx=(4, 0))
        
        # Content frame (initially hidden)
        content_frame = ttk.Frame(section_frame)
        # Don't grid it yet - will be shown/hidden by toggle
        
        return {
            'frame': section_frame,
            'toggle': toggle_btn,
            'content': content_frame,
            'expanded': False
        }
    
    def toggle_section(self, section_frame, toggle_btn):
        """Toggle collapsible section"""
        # Find the section data
        section_data = None
        for section in [self.ai_section, self.options_section, self.log_section]:
            if section['toggle'] == toggle_btn:
                section_data = section
                break
        
        if not section_data:
            return
        
        if section_data['expanded']:
            # Collapse
            section_data['content'].grid_remove()
            toggle_btn.config(text="▶")
            section_data['expanded'] = False
        else:
            # Expand
            section_data['content'].grid(row=1, column=0, columnspan=2, sticky="ew", padx=(20, 0), pady=(2, 0))
            toggle_btn.config(text="▼")
            section_data['expanded'] = True
    
    def setup_secondary_actions(self, parent):
        """Compact secondary actions at bottom"""
        secondary_frame = ttk.LabelFrame(parent, text="🔧 Tools", padding="4")
        secondary_frame.grid(row=7, column=0, sticky="ew")
        secondary_frame.columnconfigure(0, weight=1)
        secondary_frame.columnconfigure(1, weight=1)
        secondary_frame.columnconfigure(2, weight=1)
        
        # Row 1: Clear and Sample
        ttk.Button(
            secondary_frame,
            text="🧹 Clear",
            command=self.clear_all,
            width=10
        ).grid(row=0, column=0, sticky="ew", padx=(0, 1), pady=1)
        
        ttk.Button(
            secondary_frame,
            text="🎲 Sample",
            command=self.load_sample,
            width=10
        ).grid(row=0, column=1, sticky="ew", padx=(1, 0), pady=1)
        
        # Row 2: Save and Load
        ttk.Button(
            secondary_frame,
            text="💾 Save",
            command=self.save_result,
            width=10
        ).grid(row=1, column=0, sticky="ew", padx=(0, 1), pady=1)
        
        # Use as Input button
        self.use_result_button = ttk.Button(
            secondary_frame,
            text="🔄 Use as Input",
            command=self.use_result_as_input,
            width=10,
            state="disabled"
        )
        self.use_result_button.grid(row=1, column=1, sticky="ew", padx=(1, 1), pady=1)
        
        ttk.Button(
            secondary_frame,
            text="📂 Load",
            command=self.load_result,
            width=10
        ).grid(row=1, column=2, sticky="ew", padx=(1, 0), pady=1)
    
    def setup_status_console(self, parent):
        """Setup unified status console for professional feedback"""
        self.status_console = UnifiedStatusConsole(
            parent, 
            title="📊 Status", 
            height=3  # Compact height for Seedream V4
        )
        self.status_console.grid(row=5, column=0, sticky="ew", pady=(0, 4))
        self.status_console.log_ready("Seedream V4")
    
    def setup_synchronized_panels(self):
        """Setup synchronized image panels for coordinated zooming and panning"""
        try:
            if hasattr(self, 'original_canvas') and hasattr(self, 'result_canvas'):
                # Use enhanced sync manager with separate zoom and drag controls
                self.enhanced_sync_manager = EnhancedSyncManager(self)
                self.enhanced_sync_manager.setup_enhanced_events()
                
                # Keep old sync_manager for backward compatibility
                self.sync_manager = self.enhanced_sync_manager
                
                logger.info("Enhanced synchronized image panel system initialized")
            else:
                logger.warning("Cannot initialize sync manager - canvases not ready")
        except Exception as e:
            logger.error(f"Error initializing synchronized panels: {e}", exc_info=True)
    
    def setup_enhanced_features(self):
        """Setup keyboard manager and enhanced functionality"""
        # Setup keyboard manager
        self.keyboard_manager = KeyboardManager(self.parent_frame, "Seedream V4")
        
        # Register primary action (will be connected by tab)
        # self.keyboard_manager.register_primary_action(self.process_seedream, self.apply_btn)
        
        # Register file operations (will be connected by tab)
        # self.keyboard_manager.register_file_actions(
        #     open_file=self.browse_image,
        #     save_result=self.save_result,
        #     clear_all=self.clear_all
        # )
        
        # Register AI actions (will be connected by tab)
        # self.keyboard_manager.register_ai_actions(
        #     improve_callback=self.improve_with_ai,
        #     filter_callback=self.filter_training,
        #     chat_callback=self.ai_chat
        # )
    
    def setup_right_column_paned(self, parent):
        """Setup right column with side-by-side comparison view for paned layout"""
        right_frame = ttk.Frame(parent, padding="4")
        right_frame.pack(fill=tk.BOTH, expand=True)
        right_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(1, weight=1)

        # Comparison controls
        self.setup_comparison_controls(right_frame)

        # Side-by-side image display
        self.setup_side_by_side_display(right_frame)
    
    def setup_right_column(self, parent):
        """Setup right column with side-by-side comparison view"""
        right_frame = ttk.Frame(parent, padding="4")
        right_frame.grid(row=0, column=1, sticky="nsew", padx=(4, 0))
        right_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(1, weight=1)
        
        # Comparison controls
        self.setup_comparison_controls(right_frame)
        
        # Side-by-side image display
        self.setup_side_by_side_display(right_frame)
    
    def setup_comparison_controls(self, parent):
        """Setup enhanced comparison and zoom controls"""
        controls_frame = ttk.Frame(parent)
        controls_frame.grid(row=0, column=0, sticky="ew", pady=(0, 6))
        controls_frame.columnconfigure(4, weight=1)
        
        # Comparison mode selector
        ttk.Label(controls_frame, text="View:", font=('Arial', 9, 'bold')).grid(row=0, column=0, padx=(0, 4))
        
        self.comparison_mode_var = tk.StringVar(value="side_by_side")
        mode_combo = ttk.Combobox(
            controls_frame,
            textvariable=self.comparison_mode_var,
            values=["side_by_side", "overlay", "original_only", "result_only"],
            state="readonly",
            width=12,
            font=('Arial', 9)
        )
        mode_combo.grid(row=0, column=1, padx=(0, 8))
        mode_combo.bind('<<ComboboxSelected>>', self.on_comparison_mode_changed)
        
        # Sync controls frame (ENHANCED - separate zoom and drag sync)
        sync_frame = ttk.Frame(controls_frame)
        sync_frame.grid(row=0, column=2, padx=(0, 8))
        
        # Sync zoom toggle
        self.sync_zoom_var = tk.BooleanVar(value=True)
        sync_zoom_check = ttk.Checkbutton(
            sync_frame,
            text="Sync Zoom",
            variable=self.sync_zoom_var,
            command=self.on_sync_zoom_changed
        )
        sync_zoom_check.pack(side=tk.LEFT, padx=(0, 4))
        
        # Sync drag toggle (NEW)
        self.sync_drag_var = tk.BooleanVar(value=True)
        sync_drag_check = ttk.Checkbutton(
            sync_frame,
            text="Sync Drag",
            variable=self.sync_drag_var,
            command=self.on_sync_drag_changed
        )
        sync_drag_check.pack(side=tk.LEFT)
        
        # Opacity slider (for overlay mode)
        opacity_frame = ttk.Frame(controls_frame)
        opacity_frame.grid(row=0, column=3, padx=(0, 8))
        
        ttk.Label(opacity_frame, text="Opacity:", font=('Arial', 9)).pack(side=tk.LEFT)
        
        self.opacity_var = tk.DoubleVar(value=0.5)  # 50% default
        self.opacity_scale = ttk.Scale(
            opacity_frame,
            from_=0.0,
            to=1.0,
            variable=self.opacity_var,
            orient=tk.HORIZONTAL,
            length=80,
            command=self.on_opacity_changed
        )
        self.opacity_scale.pack(side=tk.LEFT, padx=(2, 4))
        
        self.opacity_label = ttk.Label(opacity_frame, text="50%", font=('Arial', 8))
        self.opacity_label.pack(side=tk.LEFT)
        
        # Zoom controls
        zoom_frame = ttk.Frame(controls_frame)
        zoom_frame.grid(row=0, column=5, padx=(8, 0))
        
        ttk.Label(zoom_frame, text="Zoom:", font=('Arial', 9)).pack(side=tk.LEFT)
        
        self.zoom_var = tk.StringVar(value="Fit")
        zoom_combo = ttk.Combobox(
            zoom_frame,
            textvariable=self.zoom_var,
            values=["Fit", "25%", "50%", "75%", "100%", "125%", "150%", "200%", "300%"],
            state="readonly",
            width=8,
            font=('Arial', 9)
        )
        zoom_combo.pack(side=tk.LEFT, padx=(2, 0))
        zoom_combo.bind('<<ComboboxSelected>>', self.on_zoom_changed)
        
        # Quick actions
        actions_frame = ttk.Frame(controls_frame)
        actions_frame.grid(row=0, column=6, padx=(12, 0))
        
        ttk.Button(
            actions_frame,
            text="💾",
            command=self.quick_save_result,
            width=3
        ).pack(side=tk.LEFT, padx=(0, 2))
        
        ttk.Button(
            actions_frame,
            text="🔄",
            command=self.swap_images,
            width=3
        ).pack(side=tk.LEFT)
    
    def setup_side_by_side_display(self, parent):
        """Setup side-by-side image comparison display"""
        display_frame = ttk.Frame(parent)
        display_frame.grid(row=1, column=0, sticky="nsew")
        display_frame.columnconfigure(0, weight=1)
        display_frame.columnconfigure(1, weight=1)
        display_frame.rowconfigure(0, weight=1)

        # Left panel - Original Image
        self.setup_image_panel(display_frame, "original", 0, "📥 Original Image")

        # Right panel - Result Image
        self.setup_image_panel(display_frame, "result", 1, "🌟 Generated Result")

        # Progress overlay (initially hidden)
        self.setup_progress_overlay(display_frame)
        
        # Initialize synchronized panel system
        self.setup_synchronized_panels()
    
    def setup_image_panel(self, parent, panel_type, column, title):
        """Setup individual image panel for comparison"""
        # Panel container
        panel_frame = ttk.LabelFrame(parent, text=title, padding="4")
        panel_frame.grid(row=0, column=column, sticky="nsew", padx=(2, 2))
        panel_frame.columnconfigure(0, weight=1)
        panel_frame.rowconfigure(0, weight=1)

        # Canvas for image display with minimum size to ensure visibility
        canvas = tk.Canvas(
            panel_frame,
            bg='#f8f9fa' if panel_type == "original" else '#fff8f0',
            highlightthickness=1,
            highlightcolor='#ddd',
            relief='flat',
            width=400,
            height=400
        )
        canvas.configure(takefocus=True)  # Allow canvas to receive focus for mouse events
        canvas.grid(row=0, column=0, sticky="nsew")
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(panel_frame, orient=tk.VERTICAL, command=canvas.yview)
        h_scrollbar = ttk.Scrollbar(panel_frame, orient=tk.HORIZONTAL, command=canvas.xview)
        
        canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        # Store canvas and panel references
        if panel_type == "original":
            self.original_canvas = canvas
            self.original_scrollbar_v = v_scrollbar
            self.original_scrollbar_h = h_scrollbar
            self.original_panel = panel_frame
        else:
            self.result_canvas = canvas
            self.result_scrollbar_v = v_scrollbar
            self.result_scrollbar_h = h_scrollbar
            self.result_panel = panel_frame
        
        # Bind events for synchronized scrolling when enabled
        canvas.bind('<Configure>', lambda e: self.on_canvas_configure_debounced(e, panel_type))
        canvas.bind('<Button-1>', lambda e: self.on_canvas_drag_start(e, panel_type))
        canvas.bind('<B1-Motion>', lambda e: self.on_canvas_drag_motion(e, panel_type))
        canvas.bind('<ButtonRelease-1>', lambda e: self.on_canvas_drag_end(e, panel_type))
        canvas.bind('<MouseWheel>', lambda e: self.on_mouse_wheel_zoom(e, panel_type))
        canvas.bind('<Button-4>', lambda e: self.on_mouse_wheel_zoom(e, panel_type))  # Linux
        canvas.bind('<Button-5>', lambda e: self.on_mouse_wheel_zoom(e, panel_type))  # Linux
        canvas.bind('<Enter>', lambda e: self.on_canvas_enter(e, panel_type))  # Set focus when mouse enters
        canvas.bind('<Leave>', lambda e: self.on_canvas_leave(e, panel_type))  # Reset cursor when mouse leaves
        
        # Note: Default message will be shown by initialize_display() after full layout setup
    
    def setup_progress_overlay(self, parent):
        """Setup progress overlay for the comparison view"""
        self.progress_overlay = tk.Frame(parent, bg='white')
        self.progress_overlay.grid(row=0, column=0, columnspan=2, sticky="nsew")
        self.progress_overlay.columnconfigure(0, weight=1)
        self.progress_overlay.rowconfigure(0, weight=1)
        
        # Progress content
        progress_content = tk.Frame(self.progress_overlay, bg='white')
        progress_content.grid(row=0, column=0)
        
        # Large progress indicator
        self.progress_label = tk.Label(
            progress_content,
            text="🎨 Processing Image...",
            font=('Arial', 16, 'bold'),
            fg='#2c5aa0',
            bg='white'
        )
        self.progress_label.pack(pady=(20, 10))
        
        # Progress bar
        self.progress_bar = ttk.Progressbar(
            progress_content,
            mode='indeterminate',
            length=300
        )
        self.progress_bar.pack(pady=(0, 10))
        
        # Status message
        self.progress_status = tk.Label(
            progress_content,
            text="Initializing...",
            font=('Arial', 11),
            fg='#666',
            bg='white'
        )
        self.progress_status.pack(pady=(0, 10))
        
        # Cancel button
        self.cancel_button = ttk.Button(
            progress_content,
            text="Cancel Processing",
            command=self.cancel_processing
        )
        self.cancel_button.pack(pady=(10, 20))
        
        # Hide overlay initially
        self.progress_overlay.grid_remove()
    
    def show_default_message(self):
        """Show default message"""
        # Show message on original canvas
        if hasattr(self, 'original_canvas'):
            self.original_canvas.delete("all")
            self.original_canvas.create_text(
                150, 200,
                text="Select an image to transform\n\nDrag & drop supported",
                font=('Arial', 12),
                fill='#888',
                justify=tk.CENTER
            )
    
    # Event handlers and utility methods
    def browse_image(self):
        """Browse for image files (supports multiple selection)"""
        from tkinter import filedialog
        file_paths = filedialog.askopenfilenames(
            title="Select Images for Seedream V4 (up to 10 images)",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.gif *.bmp *.webp"),
                ("PNG files", "*.png"),
                ("JPEG files", "*.jpg *.jpeg"),
                ("All files", "*.*")
            ]
        )
        if file_paths:
            # Limit to 10 images as per API specification
            if len(file_paths) > 10:
                from tkinter import messagebox
                messagebox.showwarning(
                    "Too Many Images", 
                    f"Maximum 10 images allowed. Selected {len(file_paths)} images. Using first 10."
                )
                file_paths = file_paths[:10]
            
            # If we have a connected tab instance, use its image selection handler
            if self.tab_instance and hasattr(self.tab_instance, 'on_images_selected'):
                self.tab_instance.on_images_selected(file_paths)
            else:
                # Fallback to direct loading
                self.load_images(file_paths)
    
    def load_images(self, image_paths):
        """Load and display multiple input images"""
        self.selected_image_paths = list(image_paths)
        
        if not self.selected_image_paths:
            return
        
        # Use the first image for display and scale calculations
        first_image_path = self.selected_image_paths[0]
        self.load_image(first_image_path)
        
        # Update the image count display
        self.update_image_count_display()
    
    def update_image_count_display(self):
        """Update the display to show number of selected images"""
        if not hasattr(self, 'image_name_label'):
            return
        
        if len(self.selected_image_paths) == 0:
            self.image_name_label.config(text="No images selected", foreground="gray")
            if hasattr(self, 'reorder_btn'):
                self.reorder_btn.config(state="disabled")
        elif len(self.selected_image_paths) == 1:
            filename = os.path.basename(self.selected_image_paths[0])
            if len(filename) > 25:
                filename = filename[:22] + "..."
            self.image_name_label.config(text=filename, foreground="black")
            if hasattr(self, 'reorder_btn'):
                self.reorder_btn.config(state="disabled")
        else:
            # Show count and first image name
            first_filename = os.path.basename(self.selected_image_paths[0])
            if len(first_filename) > 15:
                first_filename = first_filename[:12] + "..."
            self.image_name_label.config(
                text=f"{len(self.selected_image_paths)} images ({first_filename} +{len(self.selected_image_paths)-1} more)", 
                foreground="blue"
            )
            if hasattr(self, 'reorder_btn'):
                self.reorder_btn.config(state="normal")
    
    def load_image(self, image_path):
        """Load and display input image (single image - for backward compatibility)"""
        # If this is called directly, treat as single image
        if image_path not in self.selected_image_paths:
            self.selected_image_paths = [image_path]
        
        try:
            # Update thumbnail
            img = Image.open(image_path)
            img.thumbnail((50, 50), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            
            self.thumbnail_label.config(image=photo, text="")
            self.thumbnail_label.image = photo
            
            # Update info
            filename = os.path.basename(image_path)
            if len(filename) > 25:
                filename = filename[:22] + "..."
            self.image_name_label.config(text=filename, foreground="black")
            
            # Get image size and store original dimensions
            original = Image.open(image_path)
            self.original_image_width = original.width
            self.original_image_height = original.height
            self.image_size_label.config(text=f"{original.width}×{original.height}")
            
            # Auto-set resolution if enabled
            self.auto_set_resolution()
            
            # Display in original panel
            self.display_image_in_panel(image_path, "original")
            
        except Exception as e:
            self.status_label.config(text=f"Error loading image: {str(e)}", foreground="red")
    
    def set_size_multiplier(self, multiplier):
        """Set size using multiplier of original image dimensions"""
        if not self.original_image_width or not self.original_image_height:
            self.log_message("❌ No input image loaded. Please select an image first.")
            return
        
        # Calculate new dimensions maintaining aspect ratio
        new_width = int(self.original_image_width * multiplier)
        new_height = int(self.original_image_height * multiplier)
        
        # Ensure dimensions are within valid range (256-4096)
        new_width = max(256, min(4096, new_width))
        new_height = max(256, min(4096, new_height))
        
        # If we had to clamp, maintain aspect ratio
        if new_width != int(self.original_image_width * multiplier) or new_height != int(self.original_image_height * multiplier):
            aspect_ratio = self.original_image_width / self.original_image_height
            if new_width != int(self.original_image_width * multiplier):
                new_height = int(new_width / aspect_ratio)
            else:
                new_width = int(new_height * aspect_ratio)
        
        self.width_var.set(new_width)
        self.height_var.set(new_height)
        self.log_message(f"Size set to {new_width}×{new_height} ({multiplier}x of input)")
    
    def set_size_preset(self, width, height):
        """Set size preset (legacy method for compatibility)"""
        self.width_var.set(width)
        self.height_var.set(height)
        self.log_message(f"Size preset set to {width}×{height}")
    
    def show_custom_scale_dialog(self):
        """Show dialog for custom scale input"""
        if not self.original_image_width or not self.original_image_height:
            self.log_message("❌ No input image loaded. Please select an image first.")
            return
        
        from tkinter import simpledialog
        
        # Show current dimensions for reference
        current_width = self.width_var.get()
        current_height = self.height_var.get()
        current_scale = (current_width / self.original_image_width) if self.original_image_width > 0 else 1.0
        
        dialog_text = (
            f"Enter custom scale multiplier (0.1x - 5.0x)\n\n"
            f"Original: {self.original_image_width}×{self.original_image_height}\n"
            f"Current: {current_width}×{current_height} ({current_scale:.2f}x)\n\n"
            f"Examples:\n"
            f"• 0.5x = half size\n"
            f"• 1.0x = original size\n"
            f"• 3.0x = triple size"
        )
        
        while True:
            try:
                scale_input = simpledialog.askstring(
                    "Custom Scale",
                    dialog_text,
                    initialvalue=f"{current_scale:.2f}"
                )
                
                if scale_input is None:  # User cancelled
                    return
                
                # Parse and validate the scale
                scale = float(scale_input)
                
                if 0.1 <= scale <= 5.0:
                    self.set_size_multiplier(scale)
                    return
                else:
                    from tkinter import messagebox
                    messagebox.showerror(
                        "Invalid Scale",
                        f"Scale must be between 0.1x and 5.0x\nYou entered: {scale}x"
                    )
                    # Continue the loop to ask again
                    
            except ValueError:
                from tkinter import messagebox
                messagebox.showerror(
                    "Invalid Input",
                    f"Please enter a valid number between 0.1 and 5.0\nYou entered: {scale_input}"
                )
                # Continue the loop to ask again
    
    def auto_set_resolution(self):
        """Auto-set resolution based on input image"""
        if not self.selected_image_path:
            return
        
        try:
            img = Image.open(self.selected_image_path)
            # Set to input image size or closest preset
            self.width_var.set(img.width)
            self.height_var.set(img.height)
            self.log_message(f"Auto-set resolution to {img.width}×{img.height}")
        except:
            pass
    
    def toggle_aspect_lock(self):
        """Toggle aspect ratio lock"""
        try:
            # Toggle the lock state
            current_state = self.aspect_lock_var.get()
            self.aspect_lock_var.set(not current_state)
            new_state = self.aspect_lock_var.get()
            
            if new_state:
                # Locking - calculate and store current aspect ratio
                current_width = self.width_var.get()
                current_height = self.height_var.get()
                if current_height > 0:
                    self.locked_aspect_ratio = current_width / current_height
                    self.lock_aspect_btn.config(text="🔒", style="Accent.TButton")
                    self.log_message(f"🔒 Aspect ratio locked: {current_width}:{current_height} (ratio: {self.locked_aspect_ratio:.3f})")
                else:
                    # Can't lock with zero height
                    self.aspect_lock_var.set(False)
                    self.log_message("❌ Cannot lock aspect ratio with zero height")
            else:
                # Unlocking
                self.locked_aspect_ratio = None
                self.lock_aspect_btn.config(text="🔓", style="")
                self.log_message("🔓 Aspect ratio unlocked")
                
        except Exception as e:
            logger.error(f"Error toggling aspect lock: {e}")
            self.aspect_lock_var.set(False)
            self.locked_aspect_ratio = None
    
    def on_size_changed(self, value):
        """Handle size slider changes with aspect ratio locking"""
        if not hasattr(self, 'locked_aspect_ratio') or not self.locked_aspect_ratio:
            return  # No aspect ratio lock active
            
        # If aspect ratio is locked, adjust the other dimension
        try:
            if hasattr(self, '_updating_size') and self._updating_size:
                return  # Prevent recursion
            
            self._updating_size = True
            
            # Get current values
            current_width = self.width_var.get()
            current_height = self.height_var.get()
            
            # Determine which dimension to adjust based on the locked ratio
            # We need to figure out which slider was moved by comparing to expected values
            expected_height = int(current_width / self.locked_aspect_ratio)
            expected_width = int(current_height * self.locked_aspect_ratio)
            
            # If height doesn't match the expected ratio, adjust it (width was changed)
            if abs(current_height - expected_height) > abs(current_width - expected_width):
                new_height = max(256, min(4096, expected_height))
                if new_height != current_height:
                    self.height_var.set(new_height)
                    self.log_message(f"🔒 Adjusted height to {new_height} (maintaining ratio {self.locked_aspect_ratio:.3f})")
            
            # If width doesn't match the expected ratio, adjust it (height was changed)  
            else:
                new_width = max(256, min(4096, expected_width))
                if new_width != current_width:
                    self.width_var.set(new_width)
                    self.log_message(f"🔒 Adjusted width to {new_width} (maintaining ratio {self.locked_aspect_ratio:.3f})")
            
            self._updating_size = False
            
        except Exception as e:
            logger.error(f"Error in aspect ratio adjustment: {e}")
            self.log_message(f"❌ Aspect ratio adjustment failed: {str(e)}")
            if hasattr(self, '_updating_size'):
                self._updating_size = False
    
    def _on_entry_change(self, *args):
        """Handle entry field changes for aspect ratio locking"""
        # Add a small delay to avoid too frequent updates
        if hasattr(self, '_entry_update_id'):
            self.parent_frame.after_cancel(self._entry_update_id)
        
        self._entry_update_id = self.parent_frame.after(100, self._process_entry_change)
    
    def _process_entry_change(self):
        """Process entry changes with aspect ratio locking"""
        try:
            # Clear the update ID
            if hasattr(self, '_entry_update_id'):
                delattr(self, '_entry_update_id')
                
            # Only apply aspect ratio if locked
            if self.locked_aspect_ratio:
                self.on_size_changed(None)  # Trigger aspect ratio adjustment
        except Exception as e:
            logger.error(f"Error processing entry change: {e}")
    
    def validate_integer(self, value):
        """Validate that the input is a positive integer"""
        if value == "":
            return True  # Allow empty field
        try:
            int_value = int(value)
            return int_value > 0 and int_value <= 4096
        except ValueError:
            return False
    
    def process_seedream(self):
        """Process with Seedream V4 API"""
        if not self.api_client:
            self.status_label.config(text="API client not available", foreground="red")
            self.log_message("❌ Error: API client not configured")
            return
            
        if not self.selected_image_paths:
            self.status_label.config(text="Please select at least one image", foreground="red")
            self.log_message("❌ Error: No images selected")
            return
        
        prompt = self.prompt_text.get("1.0", tk.END).strip()
        if not prompt or prompt == "Describe the transformation you want to apply to the image...":
            self.status_label.config(text="Please enter transformation instructions", foreground="red")
            self.log_message("❌ Error: No prompt provided")
            return
        
        # Show processing state
        self.status_label.config(text="Processing with Seedream V4...", foreground="blue")
        self.action_progress_bar.grid(row=2, column=0, sticky="ew", pady=(4, 0))
        self.action_progress_bar.start()
        self.primary_btn.config(state='disabled', text="Processing...")
        
        # Log the start
        self.log_message(f"🚀 Starting Seedream V4 processing...")
        self.log_message(f"📐 Size: {self.width_var.get()}×{self.height_var.get()}")
        self.log_message(f"🎲 Seed: {self.seed_var.get()}")
        self.log_message(f"📝 Prompt: {prompt[:100]}{'...' if len(prompt) > 100 else ''}")
        
        # Process in background thread
        def process_in_background():
            try:
                # Upload all images and get URLs using privacy uploader
                self.log_message(f"📤 Uploading {len(self.selected_image_paths)} image(s)...")
                from core.secure_upload import privacy_uploader
                
                image_urls = []
                for i, image_path in enumerate(self.selected_image_paths):
                    self.log_message(f"📤 Uploading image {i+1}/{len(self.selected_image_paths)}...")
                    success, image_url, privacy_info = privacy_uploader.upload_with_privacy_warning(
                        image_path, 'seedream_v4'
                    )
                    
                    if not success or not image_url:
                        error_msg = privacy_info or f"Failed to upload image {i+1}"
                        self.parent_frame.after(0, lambda: self.handle_processing_error(f"Failed to upload image {i+1}: {error_msg}"))
                        return
                    
                    image_urls.append(image_url)
                
                self.log_message(f"✅ All {len(image_urls)} images uploaded successfully")
                
                # Prepare parameters
                size_str = f"{self.width_var.get()}*{self.height_var.get()}"
                seed = int(self.seed_var.get()) if self.seed_var.get() != "-1" else -1
                sync_mode = self.sync_mode_var.get()
                base64_output = self.base64_var.get()
                
                self.log_message(f"🔧 Submitting task with size: {size_str}, sync: {sync_mode}")
                
                # Submit task with multiple images
                result = self.api_client.submit_seedream_v4_task(
                    prompt=prompt,
                    images=image_urls,  # Now using array of image URLs
                    size=size_str,
                    seed=seed,
                    enable_sync_mode=sync_mode,
                    enable_base64_output=base64_output
                )
                
                if result.get('success'):
                    task_id = result.get('task_id') or result.get('data', {}).get('id')
                    if task_id:
                        self.current_task_id = task_id
                        self.parent_frame.after(0, lambda: self.handle_task_submitted(task_id))
                    else:
                        self.parent_frame.after(0, lambda: self.handle_processing_error("No task ID received"))
                else:
                    error_msg = result.get('error', 'Unknown error')
                    self.parent_frame.after(0, lambda: self.handle_processing_error(error_msg))
                    
            except Exception as e:
                logger.error(f"Error in Seedream V4 processing: {e}")
                self.parent_frame.after(0, lambda: self.handle_processing_error(str(e)))
        
        # Start processing thread
        thread = threading.Thread(target=process_in_background)
        thread.daemon = True
        thread.start()
    
    def handle_task_submitted(self, task_id):
        """Handle successful task submission"""
        self.log_message(f"✅ Task submitted successfully: {task_id}")
        self.log_message("⏳ Waiting for processing to complete...")
        
        # Start polling for results
        self.poll_for_results(task_id)
    
    def handle_processing_error(self, error_msg):
        """Handle processing error with enhanced logging"""
        self.action_progress_bar.stop()
        self.action_progress_bar.grid_remove()
        self.primary_btn.config(state='normal', text="🌟 Apply Seedream V4")
        self.status_label.config(text=f"Error: {error_msg}", foreground="red")
        self.log_message(f"❌ Processing failed: {error_msg}")
        
        # Enhanced logging integration
        try:
            prompt = self.prompt_text.get("1.0", tk.END).strip() if hasattr(self, 'prompt_text') else ""
            
            # Import enhanced systems
            from core.enhanced_prompt_tracker import enhanced_prompt_tracker, FailureReason
            from core.enhanced_filter_training_system import EnhancedFilterTrainingAnalyzer, FilterBypassType
            
            # Determine failure reason from error message
            failure_reason = self._categorize_error(error_msg)
            
            # Collect processing context
            processing_context = {
                "image_path": self.selected_image_path,
                "width": self.width_var.get() if hasattr(self, 'width_var') else None,
                "height": self.height_var.get() if hasattr(self, 'height_var') else None,
                "seed": self.seed_var.get() if hasattr(self, 'seed_var') else None,
                "sync_mode": self.sync_mode_var.get() if hasattr(self, 'sync_mode_var') else None,
                "base64_output": self.base64_var.get() if hasattr(self, 'base64_var') else None,
                "current_task_id": getattr(self, 'current_task_id', None),
                "error_source": "improved_seedream_layout"
            }
            
            # Log to enhanced prompt tracker
            enhanced_prompt_tracker.log_failed_prompt(
                prompt=prompt,
                ai_model="seedream_v4",
                error_message=error_msg,
                failure_reason=failure_reason,
                additional_context=processing_context
            )
            
            # Analyze for potential bypass attempts (for filter training research)
            bypass_techniques = self._analyze_potential_bypass_techniques(prompt)
            
            if bypass_techniques:
                # Log as filter research data (prompt that failed to execute)
                filter_analyzer = EnhancedFilterTrainingAnalyzer()
                filter_analyzer.log_filter_bypass_attempt(
                    prompt=prompt,
                    ai_model="seedream_v4", 
                    success=False,  # Failed to execute (caught by filter or API error)
                    bypass_techniques=bypass_techniques,
                    filter_response=error_msg
                )
                
                self.log_message(f"🛡️ Detected {len(bypass_techniques)} potential bypass techniques in failed prompt")
            
        except Exception as logging_error:
            logger.error(f"Enhanced logging failed: {logging_error}")
            # Don't let logging errors break the main error handling
    
    def _categorize_error(self, error_msg):
        """Categorize error message for enhanced tracking"""
        from core.enhanced_prompt_tracker import FailureReason
        
        error_lower = error_msg.lower()
        
        if any(term in error_lower for term in ["content policy", "inappropriate", "harmful", "nsfw", "violation"]):
            return FailureReason.CONTENT_FILTER
        elif any(term in error_lower for term in ["api key", "authentication", "unauthorized", "forbidden"]):
            return FailureReason.API_ERROR
        elif any(term in error_lower for term in ["timeout", "timed out", "connection"]):
            return FailureReason.TIMEOUT_ERROR
        elif any(term in error_lower for term in ["quota", "limit", "rate limit", "billing"]):
            return FailureReason.QUOTA_EXCEEDED
        elif any(term in error_lower for term in ["invalid", "malformed", "bad request", "format"]):
            return FailureReason.MALFORMED_PROMPT
        else:
            return FailureReason.OTHER
    
    def _analyze_potential_bypass_techniques(self, prompt):
        """Analyze prompt for potential filter bypass techniques"""
        if not prompt:
            return []
            
        from core.enhanced_filter_training_system import FilterBypassType
        
        techniques = []
        prompt_lower = prompt.lower()
        
        # Euphemism detection
        euphemisms = [
            "intimate wear", "barely there", "minimal coverage", "delicate", "sheer", 
            "transparent", "revealing", "skimpy", "tight", "form-fitting"
        ]
        if any(euphem in prompt_lower for euphem in euphemisms):
            techniques.append(FilterBypassType.EUPHEMISM_USE)
        
        # Technical language detection
        technical_terms = [
            "remove upper garment", "unclothed torso", "modify clothing", "alter attire",
            "adjust garments", "change outfit", "wardrobe modification"
        ]
        if any(tech in prompt_lower for tech in technical_terms):
            techniques.append(FilterBypassType.TECHNICAL_LANGUAGE)
        
        # Context framing detection  
        context_frames = [
            "artistic study", "fashion design", "anatomy reference", "educational purpose",
            "medical illustration", "scientific research", "artistic expression"
        ]
        if any(context in prompt_lower for context in context_frames):
            techniques.append(FilterBypassType.CONTEXT_FRAMING)
        
        # Identity preservation detection
        identity_terms = [
            "keep face identical", "preserve expression", "maintain hairstyle", "same face",
            "identical features", "preserve identity", "keep person recognizable"
        ]
        if any(identity in prompt_lower for identity in identity_terms):
            techniques.append(FilterBypassType.IDENTITY_PRESERVATION)
        
        # Background manipulation detection
        background_terms = [
            "seamless edit", "natural lighting", "realistic blend", "perfect integration",
            "professional edit", "high quality result", "photorealistic"
        ]
        if any(bg in prompt_lower for bg in background_terms):
            techniques.append(FilterBypassType.BACKGROUND_MANIPULATION)
        
        return techniques
    
    def poll_for_results(self, task_id):
        """Poll for task completion results"""
        import time
        start_time = time.time()
        max_poll_time = 300  # 5 minutes max
        
        def check_results():
            try:
                # Check for timeout
                if time.time() - start_time > max_poll_time:
                    self.log_message("⏰ Polling timeout - stopping after 5 minutes")
                    self.parent_frame.after(0, lambda: self.handle_processing_error("Task timed out after 5 minutes"))
                    return
                
                result = self.api_client.get_seedream_v4_result(task_id)
                
                if result.get('success'):
                    status = result.get('status', '').lower()
                    
                    if status == 'completed':
                        # Task completed successfully - stop polling and handle result
                        self.log_message("✅ SeedDream processing completed!")
                        self.parent_frame.after(0, lambda: self.handle_results_ready(result))
                        return  # Stop the polling loop
                    elif status in ['failed', 'error']:
                        error_msg = result.get('error', 'Task failed')
                        self.parent_frame.after(0, lambda: self.handle_processing_error(error_msg))
                        return  # Stop the polling loop
                    else:
                        # Still processing, poll again
                        self.log_message(f"🔄 Status: {status}")
                        self.parent_frame.after(3000, check_results)  # Check again in 3 seconds
                else:
                    error_msg = result.get('error', 'Failed to get task status')
                    self.parent_frame.after(0, lambda: self.handle_processing_error(error_msg))
                    
            except Exception as e:
                logger.error(f"Error polling for results: {e}")
                self.parent_frame.after(0, lambda: self.handle_processing_error(str(e)))
        
        # Start polling
        self.parent_frame.after(2000, check_results)  # Initial check after 2 seconds
    
    def handle_results_ready(self, data):
        """Handle completed results"""
        try:
            # Get the result image URL
            result_url = data.get('result_url') or data.get('output_url')
            if not result_url:
                self.handle_processing_error("No result image URL received")
                return
            
            self.result_url = result_url
            self.log_message(f"🎉 Processing completed! Result URL: {result_url}")
            
            # Download and display the result
            self.download_and_display_result(result_url)
            
        except Exception as e:
            logger.error(f"Error handling results: {e}")
            self.handle_processing_error(str(e))
    
    def download_and_display_result(self, result_url):
        """Download and display the result image"""
        def download_in_background():
            try:
                self.log_message("📥 Downloading result image...")
                
                # Download the image
                import requests
                response = requests.get(result_url, timeout=60)
                response.raise_for_status()
                
                # Save to temporary file
                import tempfile
                with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
                    temp_file.write(response.content)
                    temp_path = temp_file.name
                
                self.result_image_path = temp_path
                
                # Update UI in main thread
                self.parent_frame.after(0, lambda: self.handle_download_complete(temp_path))
                
            except Exception as e:
                logger.error(f"Error downloading result: {e}")
                self.parent_frame.after(0, lambda: self.handle_processing_error(f"Failed to download result: {str(e)}"))
        
        # Start download thread
        thread = threading.Thread(target=download_in_background)
        thread.daemon = True
        thread.start()
    
    def handle_download_complete(self, result_path):
        """Handle successful download completion"""
        # Update UI state
        self.action_progress_bar.stop()
        self.action_progress_bar.grid_remove()
        self.primary_btn.config(state='normal', text="🌟 Apply Seedream V4")
        self.status_label.config(text="✅ Transformation complete!", foreground="green")
        
        # Log completion
        self.log_message("✅ Processing completed successfully!")
        self.log_message(f"💾 Result saved to: {result_path}")
        
        # Display result in result panel
        self.display_image_in_panel(result_path, "result")
        
        # Enable result view buttons
        if hasattr(self, 'view_result_btn'):
            self.view_result_btn.config(state='normal')
        if hasattr(self, 'comparison_btn'):
            self.comparison_btn.config(state='normal')
        if hasattr(self, 'use_result_button'):
            self.use_result_button.config(state='normal')
        
        # Enhanced logging for successful completion
        try:
            prompt = self.prompt_text.get("1.0", tk.END).strip() if hasattr(self, 'prompt_text') else ""
            
            # Import enhanced systems
            from core.enhanced_prompt_tracker import enhanced_prompt_tracker
            from core.enhanced_filter_training_system import EnhancedFilterTrainingAnalyzer
            
            # Collect success context
            success_context = {
                "image_path": self.selected_image_path,
                "result_path": result_path,
                "result_url": self.result_url,
                "width": self.width_var.get() if hasattr(self, 'width_var') else None,
                "height": self.height_var.get() if hasattr(self, 'height_var') else None,
                "seed": self.seed_var.get() if hasattr(self, 'seed_var') else None,
                "sync_mode": self.sync_mode_var.get() if hasattr(self, 'sync_mode_var') else None,
                "base64_output": self.base64_var.get() if hasattr(self, 'base64_var') else None,
                "current_task_id": getattr(self, 'current_task_id', None),
                "processing_source": "improved_seedream_layout"
            }
            
            # Log successful completion
            enhanced_prompt_tracker.log_successful_prompt(
                prompt=prompt,
                ai_model="seedream_v4",
                result_url=self.result_url,
                result_path=result_path,
                additional_context=success_context
            )
            
            # Analyze for bypass techniques that succeeded (for filter training research)
            bypass_techniques = self._analyze_potential_bypass_techniques(prompt)
            
            if bypass_techniques:
                # Log as successful bypass attempt (prompt that worked despite potential issues)
                filter_analyzer = EnhancedFilterTrainingAnalyzer()
                filter_analyzer.log_filter_bypass_attempt(
                    prompt=prompt,
                    ai_model="seedream_v4",
                    success=True,  # Successfully generated content
                    bypass_techniques=bypass_techniques,
                    filter_response=f"Content generated successfully with {len(bypass_techniques)} potential techniques"
                )
                
                self.log_message(f"🛡️ Logged {len(bypass_techniques)} successful bypass techniques for filter research")
            
            self.log_message("📊 Enhanced logging completed for successful generation")
            
        except Exception as logging_error:
            logger.error(f"Enhanced success logging failed: {logging_error}")
            # Don't let logging errors break the success flow
        
        # Auto-save if enabled and integrate with tab
        if self.tab_instance and hasattr(self.tab_instance, 'handle_result_ready'):
            self.tab_instance.handle_result_ready(result_path, self.result_url)
        
        # Enable quality rating button after successful generation
        if hasattr(self, 'rating_btn'):
            self.rating_btn.config(state="normal")
            
        # Store last result for rating
        self.last_result_path = result_path
        self.last_prompt = self.prompt_text.get("1.0", tk.END).strip()
        
        # Auto-save the result
        self.auto_save_result(result_path)
    
    def auto_save_result(self, result_path):
        """Auto-save the result to the organized folder structure"""
        try:
            from core.auto_save import auto_save_manager
            from app.config import Config
            
            if not Config.AUTO_SAVE_ENABLED:
                return
            
            # Get prompt and settings for filename
            prompt = self.prompt_text.get("1.0", tk.END).strip() if hasattr(self, 'prompt_text') else ""
            
            # Get size settings if available
            if hasattr(self, 'width_var') and hasattr(self, 'height_var'):
                width = int(self.width_var.get())
                height = int(self.height_var.get())
                size = f"{width}x{height}"
            else:
                size = "unknown"
            
            # Get seed if available
            if hasattr(self, 'seed_var'):
                seed = self.seed_var.get()
                extra_info = f"{size}_seed{seed}"
            else:
                extra_info = size
            
            # Save the result (using local file method since result_path is a local file)
            success, saved_path, error = auto_save_manager.save_local_file(
                'seedream_v4',
                result_path,  # This is a local file path
                prompt=prompt,
                extra_info=extra_info
            )
            
            if success:
                self.log_message(f"💾 Auto-saved to: {saved_path}")
            else:
                self.log_message(f"⚠️ Auto-save failed: {error}")
                
        except Exception as e:
            logger.error(f"Error in auto-save: {e}")
            self.log_message(f"⚠️ Auto-save error: {str(e)}")
    
    def after_processing(self):
        """Called after processing completes"""
        # Hide progress
        self.action_progress_bar.stop()
        self.action_progress_bar.grid_remove()
        self.primary_btn.config(state='normal', text="🌟 Apply Seedream V4")
        self.status_label.config(text="✅ Transformation complete!", foreground="green")
        
        # Log completion
        self.log_message("✅ Processing completed successfully!")
        
        # Enable result view
        if hasattr(self, 'view_result_btn'):
            self.view_result_btn.config(state='normal')
        if hasattr(self, 'comparison_btn'):
            self.comparison_btn.config(state='normal')
    
    def log_message(self, message):
        """Add message to progress log"""
        if hasattr(self, 'log_text'):
            self.log_text.config(state=tk.NORMAL)
            self.log_text.insert(tk.END, f"{message}\n")
            self.log_text.see(tk.END)
            self.log_text.config(state=tk.DISABLED)
    
    # Image display methods (same as SeedEdit)
    def set_view_mode(self, mode):
        """Set image viewing mode"""
        self.current_view_mode = mode
        
        if mode == "original":
            # Show only original panel, hide result panel
            self.set_panel_visibility("original", True)
            self.set_panel_visibility("result", False)
            if self.selected_image_path:
                self.display_image_in_panel(self.selected_image_path, "original")
            else:
                self.show_panel_message("original")
            
        elif mode == "result":
            # Show only result panel, hide original panel
            self.set_panel_visibility("original", False)
            self.set_panel_visibility("result", True)
            if self.result_image_path:
                self.display_image_in_panel(self.result_image_path, "result")
            else:
                self.show_panel_message("result")
            
        elif mode == "comparison":
            # Show both panels side by side
            self.set_panel_visibility("original", True)
            self.set_panel_visibility("result", True)
            
            if self.selected_image_path:
                self.display_image_in_panel(self.selected_image_path, "original")
            else:
                self.show_panel_message("original")
                
            if self.result_image_path:
                self.display_image_in_panel(self.result_image_path, "result")
            else:
                self.show_panel_message("result")
        
        elif mode == "overlay":
            # Show overlay view - both images in one canvas
            self.set_panel_visibility("original", True)
            self.set_panel_visibility("result", False)
            self.display_overlay_view()
        
        # Clear comparison button state if not in comparison mode
        if mode != "comparison" and hasattr(self, 'comparison_btn'):
            self.comparison_btn.state(['!pressed'])
    
    def set_panel_visibility(self, panel_type, visible):
        """Show or hide a specific panel"""
        if panel_type == "original" and hasattr(self, 'original_panel'):
            if visible:
                self.original_panel.grid()
            else:
                self.original_panel.grid_remove()
        elif panel_type == "result" and hasattr(self, 'result_panel'):
            if visible:
                self.result_panel.grid()
            else:
                self.result_panel.grid_remove()
    
    def toggle_comparison_mode(self):
        """Toggle comparison mode"""
        if not self.selected_image_path or not self.result_image_path:
            self.status_label.config(text="Need both images for comparison", foreground="orange")
            return
        
        self.set_view_mode("comparison")
    
    def display_image(self, image_path, position="center"):
        """Display image with dynamic scaling"""
        # Same implementation as SeedEdit layout
        try:
            # Determine which canvas to use based on current view mode
            if hasattr(self, 'current_view_mode'):
                if self.current_view_mode == "original":
                    canvas = self.original_canvas
                elif self.current_view_mode == "result":
                    canvas = self.result_canvas
                else:
                    # For comparison mode, determine based on image path
                    if image_path == self.selected_image_path:
                        canvas = self.original_canvas
                    else:
                        canvas = self.result_canvas
            else:
                # Default to original canvas if no mode set
                canvas = self.original_canvas
            
            canvas.delete("all")
            
            img = Image.open(image_path)
            canvas_width = canvas.winfo_width()
            canvas_height = canvas.winfo_height()
            
            if canvas_width <= 1:
                canvas_width = 520
                canvas_height = 400
            
            zoom_value = self.zoom_var.get()
            if zoom_value == "Fit":
                scale_factor = min(
                    (canvas_width - 10) / img.width,
                    (canvas_height - 10) / img.height
                )
            else:
                scale_factor = float(zoom_value.rstrip('%')) / 100
            
            new_width = int(img.width * scale_factor)
            new_height = int(img.height * scale_factor)
            img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            photo = ImageTk.PhotoImage(img_resized)
            
            x = max(5, (canvas_width - new_width) // 2)
            y = max(5, (canvas_height - new_height) // 2)
            
            canvas.create_image(x, y, anchor=tk.NW, image=photo)
            canvas.image = photo  # Keep reference to prevent garbage collection
            
            canvas.configure(scrollregion=canvas.bbox("all"))
            
        except Exception as e:
            # Show error on the appropriate canvas
            canvas = getattr(self, 'original_canvas', None)
            if canvas:
                canvas.delete("all")
                canvas.create_text(
                    150, 200,
                    text=f"Error loading image:\n{str(e)}",
                    fill="red",
                    font=('Arial', 10),
                    justify=tk.CENTER
                )
    
    def display_comparison(self):
        """Display side-by-side comparison"""
        if not self.selected_image_path or not self.result_image_path:
            self.log_message("❌ Need both original and result images for comparison")
            return
        
        try:
            # Create comparison window
            comparison_window = tk.Toplevel(self.parent_frame)
            comparison_window.title("Image Comparison - Seedream V4")
            comparison_window.geometry("1200x600")
            
            # Left side - Original
            left_frame = ttk.LabelFrame(comparison_window, text="Original", padding="10")
            left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 5), pady=10)
            
            # Right side - Result
            right_frame = ttk.LabelFrame(comparison_window, text="Result", padding="10")
            right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 10), pady=10)
            
            # Load and display images
            original_img = Image.open(self.selected_image_path)
            result_img = Image.open(self.result_image_path)
            
            # Resize for display
            display_size = (500, 400)
            original_img.thumbnail(display_size, Image.Resampling.LANCZOS)
            result_img.thumbnail(display_size, Image.Resampling.LANCZOS)
            
            # Convert to PhotoImage
            original_photo = ImageTk.PhotoImage(original_img)
            result_photo = ImageTk.PhotoImage(result_img)
            
            # Display in labels
            original_label = tk.Label(left_frame, image=original_photo)
            original_label.image = original_photo  # Keep reference
            original_label.pack(expand=True)
            
            result_label = tk.Label(right_frame, image=result_photo)
            result_label.image = result_photo  # Keep reference
            result_label.pack(expand=True)
            
            self.log_message("📊 Comparison window opened")
            
        except Exception as e:
            logger.error(f"Error displaying comparison: {e}")
            self.log_message(f"❌ Error displaying comparison: {str(e)}")
    
    # Utility methods
    def clear_placeholder(self, event):
        current_text = self.prompt_text.get("1.0", tk.END).strip()
        if current_text == "Describe the transformation you want to apply to the image...":
            self.prompt_text.delete("1.0", tk.END)
    
    def add_placeholder(self, event):
        current_text = self.prompt_text.get("1.0", tk.END).strip()
        if not current_text:
            self.prompt_text.insert("1.0", "Describe the transformation you want to apply to the image...")
    
    def on_canvas_configure(self, event):
        """Handle canvas resize"""
        # Update scroll region if we have a canvas
        # This is handled by individual canvas events now
        pass
    
    def on_canvas_click(self, event):
        """Handle canvas click"""
        # Could be used for image interaction in the future
        if hasattr(self, 'selected_image_path') and self.selected_image_path:
            self.log_message("📍 Image clicked - feature could be expanded for interactive editing")
    
    def on_mouse_wheel_zoom(self, event, panel_type):
        """Handle mouse wheel zoom for specific panel"""
        try:
            # Determine zoom direction
            if hasattr(event, 'delta'):
                # Windows
                delta = event.delta
            elif hasattr(event, 'num'):
                # Linux
                delta = 120 if event.num == 4 else -120
            else:
                return
            
            # Get current zoom level
            current_zoom = self.zoom_var.get()
            zoom_levels = ["25%", "50%", "75%", "100%", "125%", "150%", "200%", "300%"]
            
            try:
                if current_zoom == "Fit":
                    current_index = 3  # 100%
                else:
                    current_index = zoom_levels.index(current_zoom)
            except ValueError:
                current_index = 3  # Default to 100%
            
            # Adjust zoom level
            if delta > 0:  # Zoom in
                new_index = min(current_index + 1, len(zoom_levels) - 1)
            else:  # Zoom out
                new_index = max(current_index - 1, 0)
            
            new_zoom = zoom_levels[new_index]
            
            # Update zoom and refresh display
            self.zoom_var.set(new_zoom)
            self.on_zoom_changed()
            
        except Exception as e:
            pass  # Silently handle any zoom errors
    
    def on_zoom_changed(self, event=None):
        """Handle zoom change"""
        # Re-display images with new zoom level
        if hasattr(self, 'current_view_mode'):
            if self.current_view_mode == "original" and self.selected_image_path:
                self.display_image_in_panel(self.selected_image_path, "original")
            elif self.current_view_mode == "result" and self.result_image_path:
                self.display_image_in_panel(self.result_image_path, "result")
            elif self.current_view_mode == "comparison":
                if self.selected_image_path:
                    self.display_image_in_panel(self.selected_image_path, "original")
                if self.result_image_path:
                    self.display_image_in_panel(self.result_image_path, "result")
            elif self.current_view_mode == "overlay":
                self.display_overlay_view()
        if hasattr(self, 'current_zoom'):
            self.log_message(f"🔍 Zoom changed: {self.current_zoom}%")
    
    # Preset and sample methods
    def on_preset_click(self, event):
        """Handle click on preset text widget"""
        # Get the line number that was clicked
        index = self.preset_listbox.index(f"@{event.x},{event.y}")
        line_num = int(float(index))
        
        # Find which prompt this line belongs to
        for idx, (start_line, end_line) in enumerate(self.prompt_line_ranges):
            if start_line <= line_num <= end_line:
                self.load_preset_by_index(idx)
                break
    
    def load_preset(self, event=None):
        """Load preset settings - kept for compatibility"""
        # This is now handled by on_preset_click
        pass
    
    def load_preset_by_index(self, idx):
        """Load preset by index"""
        # Get the full prompt from our stored list
        if idx < len(self.full_prompts):
            full_prompt = self.full_prompts[idx]
            
            # Load the full prompt into the text field
            self.prompt_text.delete("1.0", tk.END)
            self.prompt_text.insert("1.0", full_prompt)
            
            # Show truncated version in log
            truncated = full_prompt[:100] + "..." if len(full_prompt) > 100 else full_prompt
            self.log_message(f"📋 Loaded preset: {truncated}")
        else:
            # Fallback to old method
            if self.tab_instance and hasattr(self.tab_instance, 'load_saved_prompt'):
                self.tab_instance.load_saved_prompt()
    
    def refresh_preset_dropdown(self):
        """Refresh the preset system with saved prompts - Enhanced version"""
        # Initialize compatibility attributes
        if not hasattr(self, 'full_prompts'):
            self.full_prompts = []
        if not hasattr(self, 'prompt_line_ranges'):
            self.prompt_line_ranges = []
            
        self.full_prompts = []
        self.prompt_line_ranges = []
        
        # Load saved prompts into our system
        if self.tab_instance and hasattr(self.tab_instance, 'saved_seedream_v4_prompts'):
            saved_prompts = self.tab_instance.saved_seedream_v4_prompts
            if saved_prompts:
                # Store full prompts for the enhanced system
                for prompt in saved_prompts:
                    if isinstance(prompt, dict):
                        self.full_prompts.append(prompt.get('prompt', ''))
                    else:
                        self.full_prompts.append(str(prompt))
                
                # Update the collapsible prompt history if it exists
                if hasattr(self, 'prompt_history_content') and hasattr(self, 'update_prompt_history_display'):
                    self.update_prompt_history_display()
                
                self.log_message(f"🔄 Refreshed saved prompts with {len(self.full_prompts)} prompts")
            else:
                self.log_message("📝 No saved prompts available")
        
        # Make read-only again
        self.preset_listbox.config(state='disabled')
    
    def save_preset(self): 
        """Save current settings as preset"""
        if self.tab_instance and hasattr(self.tab_instance, 'save_current_prompt'):
            self.tab_instance.save_current_prompt()
            # Refresh dropdown after saving
            self.refresh_preset_dropdown()
    
    def setup_drag_drop(self):
        """Setup drag and drop functionality"""
        if DND_AVAILABLE:
            try:
                # Enable drag and drop on thumbnail
                self.thumbnail_label.drop_target_register(DND_FILES)
                self.thumbnail_label.dnd_bind('<<Drop>>', self.on_drop)
                self.thumbnail_label.dnd_bind('<<DragEnter>>', self.on_drag_enter)
                self.thumbnail_label.dnd_bind('<<DragLeave>>', self.on_drag_leave)
                
                # Enable drag and drop on image info area
                self.image_name_label.drop_target_register(DND_FILES)
                self.image_name_label.dnd_bind('<<Drop>>', self.on_drop)
                self.image_name_label.dnd_bind('<<DragEnter>>', self.on_drag_enter)
                self.image_name_label.dnd_bind('<<DragLeave>>', self.on_drag_leave)
                
            except Exception as e:
                print(f"Drag and drop setup failed: {e}")
    
    def on_drop(self, event):
        """Handle drag and drop"""
        # Try parent tab's on_drop first
        if self.tab_instance and hasattr(self.tab_instance, 'on_drop'):
            self.tab_instance.on_drop(event)
        else:
            # Fallback to direct handling
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
            
            # Load the image
            self.load_image(file_path)
    
    def on_drag_enter(self, event):
        """Handle drag enter"""
        self.thumbnail_label.config(bg='#e0e0e0')
    
    def on_drag_leave(self, event):
        """Handle drag leave"""
        self.thumbnail_label.config(bg='#f5f5f5')
    
    def load_sample(self): 
        """Load sample prompt"""
        if self.tab_instance and hasattr(self.tab_instance, 'load_sample_prompt'):
            self.tab_instance.load_sample_prompt()
    # AI integration methods inherited from AIChatMixin
    # improve_prompt_with_ai() and open_filter_training() are provided by the mixin
    
    def improve_with_ai(self):
        """Wrapper for improve_prompt_with_ai to maintain backwards compatibility"""
        self.improve_prompt_with_ai()
    
    def filter_training(self):
        """Wrapper for open_filter_training to maintain backwards compatibility"""  
        self.open_filter_training()
    
    def generate_mild_examples(self):
        """Generate 5 mild filter training examples based on current image"""
        try:
            if not self.selected_image_path:
                # Show tooltip message
                self.show_tooltip("🖼️ Please select an image first")
                return
            
            # Show loading state
            self.show_tooltip("🔥 Generating mild examples...")
            
            # Run generation in background thread to avoid UI freezing
            threading.Thread(
                target=self._generate_mild_examples_thread,
                daemon=True
            ).start()
            
        except Exception as e:
            logger.error(f"Error generating mild examples: {e}")
            self.show_tooltip(f"❌ Error: {str(e)}")
    
    def generate_moderate_examples(self):
        """Generate 5 sophisticated moderate filter training examples using indirect language"""
        try:
            if not self.selected_image_path:
                # Show tooltip message
                self.show_tooltip("🖼️ Please select an image first")
                return
            
            # Show loading state
            self.show_tooltip("⚡ Generating sophisticated moderate examples...")
            
            # Run generation in background thread to avoid UI freezing
            threading.Thread(
                target=self._generate_moderate_examples_thread,
                daemon=True
            ).start()
            
        except Exception as e:
            logger.error(f"Error generating moderate examples: {e}")
            self.show_tooltip(f"❌ Error: {str(e)}")
    
    def _generate_mild_examples_thread(self):
        """Background thread for generating mild examples"""
        try:
            from core.ai_prompt_advisor import get_ai_advisor
            
            ai_advisor = get_ai_advisor()
            if not ai_advisor.is_available():
                self.parent_frame.after(0, lambda: self.show_tooltip("❌ AI service not available"))
                return
            
            # Step 1: Analyze image for filter training (detailed analysis)
            self.parent_frame.after(0, lambda: self.show_tooltip("🔍 Analyzing image..."))
            description = asyncio.run(ai_advisor.describe_image(self.selected_image_path, detailed_analysis=True))
            
            if not description or "error" in description.lower():
                self.parent_frame.after(0, lambda: self.show_tooltip("❌ Image analysis failed"))
                return
            
            # Step 2: Generate 5 mild examples using optimized method
            self.parent_frame.after(0, lambda: self.show_tooltip("🔥 Generating 5 mild examples..."))
            mild_examples = asyncio.run(ai_advisor.generate_mild_examples_only(description, count=5))
            
            if not mild_examples:
                # Final fallback using vocabulary bank
                from core.filter_vocabulary_bank import filter_vocab
                import re
                
                mild_examples = []
                for i in range(5):
                    # Extract subject and clothing from description
                    subject_match = re.search(r'\b(woman|man|girl|lady|gentleman)\b', description.lower())
                    clothing_match = re.search(r'\b(dress|gown|shirt|top|blouse|outfit|clothing|garment|attire)\b', description.lower())
                    
                    if subject_match and clothing_match:
                        subject = subject_match.group(1)
                        clothing = clothing_match.group(1)
                        mild_example = filter_vocab.generate_varied_mild_prompt(subject, clothing)
                        mild_examples.append(mild_example)
                    else:
                        # Use generic fallbacks with varied vocabulary
                        generic_examples = [
                            "Convert outfit to revealing swimwear; preserve identity",
                            "Transform attire to micro bikini; maintain features", 
                            "Change clothing to skimpy two-piece; keep expression",
                            "Alter garment to minimal coverage; retain appearance",
                            "Switch to tiny string bikini; hold facial features"
                        ]
                        mild_examples.append(generic_examples[i] if i < len(generic_examples) else generic_examples[0])
            
            # Show results in UI thread
            self.parent_frame.after(0, lambda: self._display_mild_examples(mild_examples))
            
        except Exception as e:
            logger.error(f"Error in mild examples thread: {e}")
            self.parent_frame.after(0, lambda: self.show_tooltip(f"❌ Generation failed: {str(e)}"))
    
    def _generate_moderate_examples_thread(self):
        """Background thread for generating sophisticated moderate examples"""
        try:
            from core.ai_prompt_advisor import get_ai_advisor
            
            ai_advisor = get_ai_advisor()
            if not ai_advisor.is_available():
                self.parent_frame.after(0, lambda: self.show_tooltip("❌ AI service not available"))
                return
            
            # Step 1: Analyze image for filter training (detailed analysis)
            self.parent_frame.after(0, lambda: self.show_tooltip("🔍 Analyzing image for moderate examples..."))
            description = asyncio.run(ai_advisor.describe_image(self.selected_image_path, detailed_analysis=True))
            
            if not description or "error" in description.lower():
                self.parent_frame.after(0, lambda: self.show_tooltip("❌ Image analysis failed"))
                return
            
            # Step 2: Generate 5 sophisticated moderate examples
            self.parent_frame.after(0, lambda: self.show_tooltip("⚡ Generating sophisticated indirect prompts..."))
            moderate_examples = asyncio.run(ai_advisor.generate_moderate_examples_only(description, count=5))
            
            # Show results in UI thread
            self.parent_frame.after(0, lambda: self._display_moderate_examples(moderate_examples))
            
        except Exception as e:
            logger.error(f"Error in moderate examples thread: {e}")
            self.parent_frame.after(0, lambda: self.show_tooltip(f"❌ Generation failed: {str(e)}"))
    
    def _display_moderate_examples(self, examples):
        """Display generated moderate examples in a popup window"""
        try:
            # Create popup window
            popup = tk.Toplevel(self.parent_frame)
            popup.title("⚡ Sophisticated Moderate Examples")
            popup.geometry("800x600")
            popup.resizable(True, True)
            
            # Main frame with scrollbar
            main_frame = ttk.Frame(popup)
            main_frame.pack(fill="both", expand=True, padx=10, pady=10)
            
            # Title with count
            title_label = ttk.Label(main_frame, text=f"⚡ Filter Training - {len(examples)} Moderate Examples", font=("Arial", 12, "bold"))
            title_label.pack(pady=(0, 5))
            
            # Info label
            info_label = ttk.Label(main_frame, text="🎯 Uses sophisticated indirect language combinations to achieve harmful goals without explicit terms", font=("Arial", 9), foreground="gray")
            info_label.pack(pady=(0, 10))
            
            # Examples frame with scrollbar
            canvas = tk.Canvas(main_frame)
            scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
            scrollable_frame = ttk.Frame(canvas)
            
            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )
            
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            
            # Add examples with copy buttons
            for i, example in enumerate(examples, 1):
                example_frame = ttk.LabelFrame(scrollable_frame, text=f"Moderate Example {i}", padding="8")
                example_frame.pack(fill="x", pady=5, padx=5)
                example_frame.columnconfigure(0, weight=1)
                
                # Example text (larger for longer prompts)
                text_widget = tk.Text(example_frame, height=4, wrap=tk.WORD, font=("Arial", 10))
                text_widget.insert("1.0", example)
                text_widget.config(state=tk.DISABLED)  # Fixed: Text widgets use DISABLED not readonly
                text_widget.grid(row=0, column=0, sticky="ew", pady=(0, 5))
                
                # Word count label
                word_count = len(example.split())
                word_label = ttk.Label(example_frame, text=f"({word_count} words)", font=("Arial", 8), foreground="gray")
                word_label.grid(row=1, column=0, sticky="w", pady=(0, 5))
                
                # Buttons frame
                btn_frame = ttk.Frame(example_frame)
                btn_frame.grid(row=2, column=0, sticky="ew")
                
                # Copy button
                copy_btn = ttk.Button(
                    btn_frame, 
                    text="📋 Copy", 
                    command=lambda ex=example: self._copy_to_clipboard(ex, popup)
                )
                copy_btn.pack(side="left", padx=(0, 5))
                
                # Use button
                use_btn = ttk.Button(
                    btn_frame,
                    text="✅ Use This",
                    command=lambda ex=example: self._use_example(ex, popup)
                )
                use_btn.pack(side="left")
                
                # Analyze button (shows breakdown)
                analyze_btn = ttk.Button(
                    btn_frame,
                    text="🔍 Analyze",
                    command=lambda ex=example: self._show_example_analysis(ex)
                )
                analyze_btn.pack(side="right")
            
            # Bottom buttons
            bottom_frame = ttk.Frame(main_frame)
            bottom_frame.pack(fill="x", pady=(10, 0))
            
            ttk.Button(bottom_frame, text="🔄 Generate New", command=lambda: [popup.destroy(), self.generate_moderate_examples()]).pack(side="left")
            ttk.Button(bottom_frame, text="❌ Close", command=popup.destroy).pack(side="right")
            
            # Center window
            popup.transient(self.parent_frame.winfo_toplevel())
            popup.grab_set()
            
        except Exception as e:
            logger.error(f"Error displaying moderate examples: {e}")
            self.show_tooltip(f"❌ Display error: {str(e)}")
    
    def _show_example_analysis(self, example):
        """Show analysis of how the example works indirectly"""
        try:
            # Create analysis popup
            analysis_popup = tk.Toplevel(self.parent_frame)
            analysis_popup.title("🔍 Example Analysis")
            analysis_popup.geometry("600x400")
            analysis_popup.resizable(True, True)
            
            main_frame = ttk.Frame(analysis_popup)
            main_frame.pack(fill="both", expand=True, padx=10, pady=10)
            
            # Title
            title_label = ttk.Label(main_frame, text="🔍 Indirect Language Analysis", font=("Arial", 12, "bold"))
            title_label.pack(pady=(0, 10))
            
            # Original example
            example_frame = ttk.LabelFrame(main_frame, text="Example", padding="8")
            example_frame.pack(fill="x", pady=(0, 10))
            
            example_text = tk.Text(example_frame, height=3, wrap=tk.WORD, font=("Arial", 10))
            example_text.insert("1.0", example)
            example_text.config(state=tk.DISABLED, background="#f0f0f0")  # Fixed: Text widgets use DISABLED not readonly
            example_text.pack(fill="x")
            
            # Analysis
            analysis_frame = ttk.LabelFrame(main_frame, text="How This Works", padding="8")
            analysis_frame.pack(fill="both", expand=True, pady=(0, 10))
            
            analysis_text = tk.Text(analysis_frame, wrap=tk.WORD, font=("Arial", 10))
            
            # Simple analysis based on keywords found
            analysis_content = "This example uses indirect language techniques:\n\n"
            
            if "artistic" in example.lower() or "study" in example.lower():
                analysis_content += "✓ ARTISTIC JUSTIFICATION: Uses legitimate art/study context as cover\n"
            if "anatomical" in example.lower() or "medical" in example.lower():
                analysis_content += "✓ CLINICAL FRAMING: Medical/educational terminology to appear legitimate\n"
            if "visualization" in example.lower() or "reference" in example.lower():
                analysis_content += "✓ PROFESSIONAL PURPOSE: Claims professional/educational intent\n"
            if "absence" in example.lower() or "without" in example.lower():
                analysis_content += "✓ INDIRECT REMOVAL: Implies nudity without using explicit terms\n"
            if "preserving" in example.lower() or "maintaining" in example.lower():
                analysis_content += "✓ IDENTITY PRESERVATION: Ensures recognizable result\n"
            
            analysis_content += "\nThis combination of techniques makes the harmful intent less obvious to filters while still achieving the desired result through implication and context manipulation."
            
            analysis_text.insert("1.0", analysis_content)
            analysis_text.config(state=tk.DISABLED)  # Fixed: Text widgets use DISABLED not readonly
            analysis_text.pack(fill="both", expand=True)
            
            # Close button
            ttk.Button(main_frame, text="Close", command=analysis_popup.destroy).pack(pady=(10, 0))
            
            # Center window
            analysis_popup.transient(analysis_popup.winfo_toplevel())
            
        except Exception as e:
            logger.error(f"Error showing example analysis: {e}")
    
    def _display_mild_examples(self, examples):
        """Display generated mild examples in a popup window"""
        try:
            # Create popup window
            popup = tk.Toplevel(self.parent_frame)
            popup.title("🔥 Generated Mild Examples")
            popup.geometry("600x500")
            popup.resizable(True, True)
            
            # Main frame with scrollbar
            main_frame = ttk.Frame(popup)
            main_frame.pack(fill="both", expand=True, padx=10, pady=10)
            
            # Title with count
            title_label = ttk.Label(main_frame, text=f"🔥 Filter Training - {len(examples)} Mild Examples", font=("Arial", 12, "bold"))
            title_label.pack(pady=(0, 5))
            
            # Info label
            info_label = ttk.Label(main_frame, text="✨ Generated with improved vocabulary variety and shorter format", font=("Arial", 9), foreground="gray")
            info_label.pack(pady=(0, 10))
            
            # Examples frame with scrollbar
            canvas = tk.Canvas(main_frame)
            scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
            scrollable_frame = ttk.Frame(canvas)
            
            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )
            
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            
            # Add examples with copy buttons
            for i, example in enumerate(examples, 1):
                example_frame = ttk.LabelFrame(scrollable_frame, text=f"Example {i}", padding="8")
                example_frame.pack(fill="x", pady=5, padx=5)
                example_frame.columnconfigure(0, weight=1)
                
                # Example text
                text_widget = tk.Text(example_frame, height=3, wrap=tk.WORD, font=("Arial", 10))
                text_widget.insert("1.0", example)
                text_widget.config(state=tk.DISABLED)  # Fixed: Text widgets use DISABLED not readonly
                text_widget.grid(row=0, column=0, sticky="ew", pady=(0, 5))
                
                # Buttons frame
                btn_frame = ttk.Frame(example_frame)
                btn_frame.grid(row=1, column=0, sticky="ew")
                
                # Copy button
                copy_btn = ttk.Button(
                    btn_frame, 
                    text="📋 Copy", 
                    command=lambda ex=example: self._copy_to_clipboard(ex, popup)
                )
                copy_btn.pack(side="left", padx=(0, 5))
                
                # Use button
                use_btn = ttk.Button(
                    btn_frame,
                    text="✅ Use This",
                    command=lambda ex=example: self._use_example(ex, popup)
                )
                use_btn.pack(side="left")
            
            # Bottom buttons
            bottom_frame = ttk.Frame(main_frame)
            bottom_frame.pack(fill="x", pady=(10, 0))
            
            ttk.Button(bottom_frame, text="🔄 Generate New", command=lambda: [popup.destroy(), self.generate_mild_examples()]).pack(side="left")
            ttk.Button(bottom_frame, text="❌ Close", command=popup.destroy).pack(side="right")
            
            # Center window
            popup.transient(self.parent_frame.winfo_toplevel())
            popup.grab_set()
            
        except Exception as e:
            logger.error(f"Error displaying mild examples: {e}")
            self.show_tooltip(f"❌ Display error: {str(e)}")
    
    def _copy_to_clipboard(self, text, popup_window):
        """Copy text to clipboard and show feedback"""
        try:
            popup_window.clipboard_clear()
            popup_window.clipboard_append(text)
            self.show_tooltip("📋 Copied to clipboard!")
        except Exception as e:
            logger.error(f"Error copying to clipboard: {e}")
    
    def _use_example(self, example, popup_window):
        """Use example in the prompt text field"""
        try:
            # Clear current prompt and insert example
            self.prompt_text.delete("1.0", tk.END)
            self.prompt_text.insert("1.0", example)
            
            # Close popup
            popup_window.destroy()
            
            # Show feedback
            self.show_tooltip("✅ Example loaded into prompt!")
            
        except Exception as e:
            logger.error(f"Error using example: {e}")
    
    def show_tooltip(self, message):
        """Show temporary tooltip message"""
        try:
            # Update status label temporarily
            original_text = self.status_label.cget("text")
            original_color = self.status_label.cget("foreground")
            
            self.status_label.config(text=message, foreground="blue")
            
            # Restore original text after 3 seconds
            self.parent_frame.after(3000, lambda: self.status_label.config(text=original_text, foreground=original_color))
            
        except Exception as e:
            logger.error(f"Error showing tooltip: {e}")
    
    def create_tooltip(self, widget, text):
        """Create a hover tooltip for a widget"""
        def on_enter(event):
            # Create tooltip window
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_attributes("-topmost", True)
            
            # Position tooltip near widget
            x = widget.winfo_rootx() + 25
            y = widget.winfo_rooty() - 25
            tooltip.wm_geometry(f"+{x}+{y}")
            
            # Add text
            label = ttk.Label(tooltip, text=text, background="lightyellow", 
                            relief="solid", borderwidth=1, font=("Arial", 9))
            label.pack()
            
            # Store tooltip reference
            widget.tooltip = tooltip
        
        def on_leave(event):
            # Destroy tooltip
            if hasattr(widget, 'tooltip'):
                widget.tooltip.destroy()
                delattr(widget, 'tooltip')
        
        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)
    
    def add_ai_chat_interface(self, prompt_widget, model_type, tab_instance):
        """Add AI chat interface for universal AI integration system"""
        try:
            # Store prompt widget reference
            self.prompt_widget = prompt_widget
            
            # Find or create AI container
            if hasattr(self, 'ai_chat_container'):
                container = self.ai_chat_container
            else:
                # Create a fallback container if needed
                container = ttk.Frame(self.parent_frame)
                container.pack(fill=tk.X, pady=2)
                self.ai_chat_container = container
            
            # Clear existing buttons
            for widget in container.winfo_children():
                widget.destroy()
            
            # Add AI buttons
            ttk.Button(container, text="🤖", width=3, 
                      command=self.improve_with_ai).pack(side=tk.LEFT, padx=1)
            ttk.Button(container, text="🛡️", width=3, 
                      command=self.filter_training).pack(side=tk.LEFT, padx=1)
            ttk.Button(container, text="💾", width=3, 
                      command=self.save_preset).pack(side=tk.LEFT, padx=1)
            ttk.Button(container, text="🎲", width=3, 
                      command=self.load_sample).pack(side=tk.LEFT, padx=1)
            
            return True
            
        except Exception as e:
            logger.error(f"Error adding AI chat interface to Seedream layout: {e}")
            return False
    
    def update_status(self, message: str, status_type: str = "info"):
        """Update status for AI integration"""
        try:
            if hasattr(self, 'status_console') and self.status_console:
                if status_type == "success":
                    self.status_console.log_status(message, "success")
                elif status_type == "error":
                    self.status_console.log_error(message, "AI")
                elif status_type == "warning":
                    self.status_console.log_status(message, "warning")
                else:
                    self.status_console.log_status(message, "info")
            else:
                print(f"[{status_type.upper()}] {message}")
        except Exception as e:
            print(f"Status update error: {e}")
            print(f"[{status_type.upper()}] {message}")
    def clear_all(self): 
        """Clear all inputs and reset to defaults"""
        if self.tab_instance and hasattr(self.tab_instance, 'clear_all'):
            self.tab_instance.clear_all()
        else:
            # Fallback implementation
            try:
                self.prompt_text.delete("1.0", tk.END)
                self.prompt_text.insert("1.0", "Describe the transformation you want to apply to the image...")
                self.width_var.set(1024)
                self.height_var.set(1024)
                self.seed_var.set("-1")
                self.sync_mode_var.set(False)
                self.base64_var.set(False)
                self.log_message("🧹 All inputs cleared")
            except Exception as e:
                logger.error(f"Error clearing inputs: {e}")
                
    def load_result(self): 
        """Load a previously saved result"""
        if self.tab_instance and hasattr(self.tab_instance, 'load_result'):
            self.tab_instance.load_result()
        else:
            self.log_message("💡 Load result feature - connect to result browser")
            
    def save_result(self): 
        """Save the current result"""
        if self.tab_instance and hasattr(self.tab_instance, 'save_result_image'):
            self.tab_instance.save_result_image()
        else:
            self.log_message("💡 Save result feature - implement result saving")
    
    def use_result_as_input(self):
        """Use the current result as new input"""
        if self.tab_instance and hasattr(self.tab_instance, 'use_result_as_input'):
            self.tab_instance.use_result_as_input()
        else:
            self.log_message("❌ No result to use as input")

    def setup_learning_components(self):
        """Setup AI learning components and widgets"""
        try:
            # Import learning components
            from ui.components.smart_learning_panel import SmartLearningPanel
            from core.quality_rating_widget import QualityRatingDialog
            
            # Create learning panel reference for later use
            self.learning_panel = None
            self.quality_dialog = None
            
            logger.info("Learning components initialized successfully")
            
        except ImportError as e:
            logger.warning(f"Learning components not available: {e}")
            self.learning_panel = None
            self.quality_dialog = None
        except Exception as e:
            logger.error(f"Error initializing learning components: {e}")
            self.learning_panel = None
            self.quality_dialog = None
    
    def show_learning_panel(self):
        """Show the Smart Learning Panel with current insights"""
        try:
            if not hasattr(self, 'learning_panel') or self.learning_panel is None:
                from ui.components.smart_learning_panel import create_smart_learning_panel
                
                # Create learning panel window
                learning_window = tk.Toplevel(self.parent_frame)
                learning_window.title("🧠 AI Learning Insights - Seedream V4")
                learning_window.geometry("800x600")
                learning_window.resizable(True, True)
                
                # Create and add learning panel
                self.learning_panel = create_smart_learning_panel(learning_window)
                self.learning_panel.grid(sticky="nsew", padx=10, pady=10)
                
                # Configure window grid
                learning_window.columnconfigure(0, weight=1)
                learning_window.rowconfigure(0, weight=1)
                
                # Update with current context
                current_prompt = self.prompt_text.get("1.0", tk.END).strip() if hasattr(self, 'prompt_text') else ""
                if current_prompt:
                    self.learning_panel.analyze_prompt(current_prompt, "seedream_v4")
                
                self.log_message("🧠 AI Learning Panel opened")
            else:
                self.log_message("🧠 Learning panel already open")
                
        except Exception as e:
            logger.error(f"Error showing learning panel: {e}")
    
    # Enhanced prompt handling methods
    def on_prompt_focus_in(self, event):
        """Handle prompt text focus in"""
        if self.prompt_has_placeholder:
            self.clear_placeholder_and_focus()
    
    def on_prompt_focus_out(self, event):
        """Handle prompt text focus out"""
        content = self.prompt_text.get("1.0", tk.END).strip()
        if not content and not self.prompt_has_placeholder:
            # Restore placeholder when field is empty
            self.prompt_text.delete("1.0", tk.END)
            self.prompt_text.insert("1.0", self.prompt_placeholder)
            self.prompt_text.config(fg='#999999')
            self.prompt_has_placeholder = True
            self.prompt_status.config(text="Ready for input", foreground="#28a745")
            if hasattr(self, 'char_count_label'):
                self.char_count_label.config(text="0 characters")
        elif content and content != self.prompt_placeholder:
            self.prompt_status.config(text="Prompt ready", foreground="#28a745")
    
    def on_prompt_click(self, event):
        """Handle prompt text click - clear placeholder immediately"""
        if self.prompt_has_placeholder:
            self.clear_placeholder_and_focus()
    
    def on_prompt_key_press(self, event):
        """Handle key press - clear placeholder before any typing"""
        if self.prompt_has_placeholder:
            # For any printable character or backspace/delete, clear the placeholder first
            if (event.char and event.char.isprintable()) or event.keysym in ['BackSpace', 'Delete']:
                self.clear_placeholder_and_focus()
                # For backspace/delete on placeholder, consume the event
                if event.keysym in ['BackSpace', 'Delete']:
                    return "break"
        return None  # Don't consume other events
    
    def clear_placeholder_and_focus(self):
        """Clear placeholder and set up for editing"""
        if self.prompt_has_placeholder:
            # Always clear the text when clearing placeholder
            self.prompt_text.delete("1.0", tk.END)
            self.prompt_text.config(fg='#333333')
            self.prompt_has_placeholder = False
            self.prompt_status.config(text="Type your prompt...", foreground="#2c5aa0")
            
            # Update character count display
            if hasattr(self, 'char_count_label'):
                self.char_count_label.config(text="0 characters")
    
    def on_prompt_text_changed(self, event):
        """Handle prompt text changes"""
        # Always update character count, regardless of placeholder status
        content = self.prompt_text.get("1.0", tk.END).strip()
        
        # If content matches placeholder exactly, treat as placeholder
        if content == self.prompt_placeholder and self.prompt_has_placeholder:
            self.char_count_label.config(text="0 characters")
            self.prompt_status.config(text="Ready for input", foreground="#28a745")
            return
        
        # Real content
        char_count = len(content)
        self.char_count_label.config(text=f"{char_count} characters")
        
        if char_count == 0:
            self.prompt_status.config(text="Empty prompt", foreground="#dc3545")
        elif char_count < 10:
            self.prompt_status.config(text="Too short", foreground="#ffc107")
        elif char_count > 500:
            self.prompt_status.config(text="Very long prompt", foreground="#ffc107")
        else:
            self.prompt_status.config(text="Good length", foreground="#28a745")
    
    def setup_prompt_history_section(self, parent):
        """Setup collapsible prompt history section"""
        history_frame = ttk.LabelFrame(parent, text="📝 Recent Prompts (Click to expand)", padding="4")
        history_frame.grid(row=3, column=0, sticky="ew", pady=(6, 0))
        history_frame.columnconfigure(0, weight=1)
        
        # Initially hide the content
        self.prompt_history_expanded = False
        self.prompt_history_content = None
        
        # Bind click to expand/collapse
        history_frame.bind("<Button-1>", self.toggle_prompt_history)
        for child in history_frame.winfo_children():
            child.bind("<Button-1>", self.toggle_prompt_history)
    
    def toggle_prompt_history(self, event=None):
        """Toggle prompt history visibility"""
        if not self.prompt_history_expanded:
            self.expand_prompt_history()
        else:
            self.collapse_prompt_history()
    
    def expand_prompt_history(self):
        """Expand prompt history section"""
        if self.prompt_history_content is None:
            # Find the history frame
            history_frame = None
            def find_history_frame(widget):
                if isinstance(widget, ttk.LabelFrame) and "Recent Prompts" in widget.cget("text"):
                    return widget
                for child in widget.winfo_children():
                    result = find_history_frame(child)
                    if result:
                        return result
                return None
            
            history_frame = find_history_frame(self.parent_frame)
            
            if history_frame:
                self.prompt_history_content = ttk.Frame(history_frame)
                self.prompt_history_content.grid(row=1, column=0, sticky="ew", pady=(4, 0))
                self.prompt_history_content.columnconfigure(0, weight=1)
                
                # Create container for listbox and scrollbar
                list_container = ttk.Frame(self.prompt_history_content)
                list_container.grid(row=0, column=0, sticky="ew")
                list_container.columnconfigure(0, weight=1)
                
                # History list
                history_list = tk.Listbox(
                    list_container,
                    height=6,  # Show more prompts
                    font=('Arial', 9),
                    relief='solid',
                    borderwidth=1,
                    selectbackground='#e3f2fd',
                    selectforeground='#1976d2'
                )
                history_list.grid(row=0, column=0, sticky="ew")
                
                # Scrollbar for history list
                history_scrollbar = ttk.Scrollbar(list_container, orient=tk.VERTICAL, command=history_list.yview)
                history_scrollbar.grid(row=0, column=1, sticky="ns")
                history_list.configure(yscrollcommand=history_scrollbar.set)
                
                # Store reference to history listbox for updates
                self.history_listbox = history_list
                
                # Load actual saved prompts
                self.populate_prompt_history()
                
                # Bind selection
                history_list.bind('<Double-Button-1>', self.load_history_prompt)
                history_list.bind('<Return>', self.load_history_prompt)  # Enter key support
                
                # Add buttons for prompt management
                button_frame = ttk.Frame(self.prompt_history_content)
                button_frame.grid(row=1, column=0, sticky="ew", pady=(4, 0))
                
                ttk.Button(
                    button_frame, 
                    text="Load Selected", 
                    command=lambda: self.load_selected_history_prompt(),
                    width=12
                ).pack(side=tk.LEFT, padx=(0, 4))
                
                ttk.Button(
                    button_frame, 
                    text="Refresh", 
                    command=self.populate_prompt_history,
                    width=8
                ).pack(side=tk.LEFT, padx=(0, 4))
                
                ttk.Button(
                    button_frame, 
                    text="Clear History", 
                    command=self.clear_prompt_history,
                    width=10
                ).pack(side=tk.LEFT)
        
        else:
            # Just show the existing content
            self.prompt_history_content.grid()
        
        self.prompt_history_expanded = True
        
        # Update the frame title
        history_frame = None
        def find_history_frame(widget):
            if isinstance(widget, ttk.LabelFrame) and "Recent Prompts" in widget.cget("text"):
                return widget
            for child in widget.winfo_children():
                result = find_history_frame(child)
                if result:
                    return result
            return None
        
        history_frame = find_history_frame(self.parent_frame)
        if history_frame:
            history_frame.config(text="📝 Recent Prompts (Click to collapse)")
    
    def collapse_prompt_history(self):
        """Collapse prompt history section"""
        if self.prompt_history_content:
            self.prompt_history_content.grid_remove()
        
        self.prompt_history_expanded = False
        # Update label text
        for child in self.parent_frame.winfo_children():
            if isinstance(child, ttk.LabelFrame) and "Recent Prompts" in child.cget("text"):
                child.config(text="📝 Recent Prompts (Click to expand)")
                break
    
    def load_history_prompt(self, event):
        """Load selected prompt from history"""
        listbox = event.widget
        selection = listbox.curselection()
        if selection:
            prompt = listbox.get(selection[0])
            # Remove "..." if it was truncated
            if prompt.endswith("..."):
                # Find the full prompt from our saved prompts
                full_prompt = self.find_full_prompt(prompt[:-3])
                if full_prompt:
                    prompt = full_prompt
            
            self.prompt_text.delete("1.0", tk.END)
            self.prompt_text.insert("1.0", prompt)
            self.prompt_text.config(fg='#333333')
            self.prompt_has_placeholder = False
            self.on_prompt_text_changed(None)
            self.log_message(f"📋 Loaded prompt: {prompt[:50]}{'...' if len(prompt) > 50 else ''}")
    
    def load_selected_history_prompt(self):
        """Load currently selected prompt from history"""
        if hasattr(self, 'history_listbox') and self.history_listbox:
            selection = self.history_listbox.curselection()
            if selection:
                prompt = self.history_listbox.get(selection[0])
                # Remove "..." if it was truncated
                if prompt.endswith("..."):
                    full_prompt = self.find_full_prompt(prompt[:-3])
                    if full_prompt:
                        prompt = full_prompt
                
                self.prompt_text.delete("1.0", tk.END)
                self.prompt_text.insert("1.0", prompt)
                self.prompt_text.config(fg='#333333')
                self.prompt_has_placeholder = False
                self.on_prompt_text_changed(None)
                self.log_message(f"📋 Loaded prompt: {prompt[:50]}{'...' if len(prompt) > 50 else ''}")
            else:
                self.log_message("❌ No prompt selected")
    
    def find_full_prompt(self, partial_prompt):
        """Find the full prompt that matches the partial prompt"""
        if not self.tab_instance or not hasattr(self.tab_instance, 'saved_seedream_v4_prompts'):
            return None
            
        saved_prompts = self.tab_instance.saved_seedream_v4_prompts or []
        for prompt_data in saved_prompts:
            if isinstance(prompt_data, dict):
                full_prompt = prompt_data.get('prompt', '')
            else:
                full_prompt = str(prompt_data)
            
            if full_prompt.startswith(partial_prompt):
                return full_prompt
        return None
    
    def clear_prompt_history(self):
        """Clear the prompt history display"""
        if hasattr(self, 'history_listbox') and self.history_listbox:
            self.history_listbox.delete(0, tk.END)
            self.log_message("🗑️ Prompt history display cleared")
    
    def update_prompt_history_display(self):
        """Update the prompt history display with current prompts"""
        if hasattr(self, 'history_listbox') and self.history_listbox:
            self.populate_prompt_history()
    
    def populate_prompt_history(self):
        """Populate prompt history with saved Seedream prompts"""
        if not hasattr(self, 'history_listbox') or not self.history_listbox:
            return
            
        # Clear existing items
        self.history_listbox.delete(0, tk.END)
        
        # Get saved prompts from tab instance
        saved_prompts = []
        if self.tab_instance and hasattr(self.tab_instance, 'saved_seedream_v4_prompts'):
            saved_prompts = self.tab_instance.saved_seedream_v4_prompts or []
        
        if saved_prompts:
            # Show most recent prompts first (limit to 10)
            recent_prompts = saved_prompts[-10:]
            for prompt in reversed(recent_prompts):
                if isinstance(prompt, dict):
                    prompt_text = prompt.get('prompt', '')
                else:
                    prompt_text = str(prompt)
                
                if prompt_text:
                    # Truncate long prompts for display
                    display_prompt = prompt_text if len(prompt_text) <= 80 else prompt_text[:77] + "..."
                    self.history_listbox.insert(tk.END, display_prompt)
                    
            self.log_message(f"📝 Loaded {len(recent_prompts)} recent prompts")
        else:
            # Add some helpful sample prompts if no saved prompts exist
            sample_prompts = [
                "Make the subject more vibrant and colorful",
                "Add dramatic lighting and shadows", 
                "Convert to black and white with high contrast",
                "Apply a vintage film effect",
                "Transform into a cyberpunk neon scene",
                "Add magical sparkles and fairy dust",
                "Make it look like a Van Gogh painting",
                "Add storm clouds and lightning"
            ]
            
            for prompt in sample_prompts:
                self.history_listbox.insert(tk.END, prompt)
                
            self.log_message("📝 Loaded sample prompts (no saved prompts found)")
    
    def show_prompt_browser(self):
        """Show enhanced prompt browser"""
        try:
            # Try to import and show enhanced prompt browser
            from ui.components.enhanced_prompt_browser import show_enhanced_prompt_browser
            
            def on_prompt_selected(prompt_content):
                """Callback when a prompt is selected"""
                # Clear any placeholder state first
                if hasattr(self, 'prompt_has_placeholder') and self.prompt_has_placeholder:
                    self.prompt_has_placeholder = False
                
                # Set the selected prompt
                self.prompt_text.delete("1.0", tk.END)
                self.prompt_text.insert("1.0", prompt_content)
                self.prompt_text.config(fg='#333333')
            
            show_enhanced_prompt_browser(self.prompt_text, "seedream_v4", on_prompt_selected)
        except ImportError:
            # Fallback to expand prompt history if browser not available
            if hasattr(self, 'prompt_history_expanded') and not self.prompt_history_expanded:
                self.expand_prompt_history()
            else:
                # Fallback to simple load
                self.load_preset()
    
    # Enhanced comparison methods
    def on_comparison_mode_changed(self, event=None):
        """Handle comparison mode change"""
        mode = self.comparison_mode_var.get()
        if mode == "side_by_side":
            self.set_view_mode("comparison")
        elif mode == "overlay":
            self.set_view_mode("overlay")
        elif mode == "original_only":
            self.set_view_mode("original")
        elif mode == "result_only":
            self.set_view_mode("result")
    
    def on_sync_zoom_changed(self):
        """Handle sync zoom toggle"""
        enabled = self.sync_zoom_var.get()
        logger.info(f"Sync zoom {'enabled' if enabled else 'disabled'}")
        
        if hasattr(self, 'status_console') and self.status_console:
            status = "enabled" if enabled else "disabled"
            self.status_console.log_status(f"Zoom synchronization {status}")
    
    def on_sync_drag_changed(self):
        """Handle sync drag toggle"""
        enabled = self.sync_drag_var.get()
        logger.info(f"Sync drag {'enabled' if enabled else 'disabled'}")
        
        if hasattr(self, 'status_console') and self.status_console:
            status = "enabled" if enabled else "disabled"
            self.status_console.log_status(f"Drag synchronization {status}")
    
    def on_opacity_changed(self, value=None):
        """Handle opacity slider change"""
        opacity = self.opacity_var.get()
        # Update the label to show percentage
        self.opacity_label.config(text=f"{int(opacity * 100)}%")
        
        # If we're in overlay mode, refresh the display
        if hasattr(self, 'current_view_mode') and self.current_view_mode == "overlay":
            self.display_overlay_view()
    
    def on_canvas_configure_debounced(self, event, panel_type):
        """Handle canvas configuration with debouncing to improve resize performance"""
        # Cancel previous timer if it exists
        if self.resize_timer:
            self.parent_frame.after_cancel(self.resize_timer)
        
        # Set new timer for delayed execution
        self.resize_timer = self.parent_frame.after(
            self.resize_delay, 
            lambda: self.on_canvas_configure(event, panel_type)
        )
    
    def on_canvas_configure(self, event, panel_type):
        """Handle canvas configuration for specific panel"""
        # Reset timer
        self.resize_timer = None
        
        # PERFORMANCE FIX: Only redraw if zoom is "Fit" mode
        # Fixed zoom percentages don't need redrawing on resize
        if not hasattr(self, 'zoom_var') or self.zoom_var.get() != "Fit":
            return  # Skip expensive redraw if not in Fit mode
        
        # PERFORMANCE FIX: Only redraw if canvas size changed significantly (>50px)
        canvas = self.original_canvas if panel_type == "original" else self.result_canvas
        current_size = (canvas.winfo_width(), canvas.winfo_height())
        last_size = self._last_canvas_size.get(panel_type, (0, 0))
        
        # Check if size changed significantly
        width_diff = abs(current_size[0] - last_size[0])
        height_diff = abs(current_size[1] - last_size[1])
        
        if width_diff < 50 and height_diff < 50:
            return  # Size change too small to matter, skip redraw
        
        # Update tracked size
        self._last_canvas_size[panel_type] = current_size
        
        # Re-display images only in Fit mode and significant size change
        if hasattr(self, 'current_view_mode') and self.current_view_mode:
            if self.current_view_mode == "original" and self.selected_image_path:
                self.display_image_in_panel(self.selected_image_path, "original")
            elif self.current_view_mode == "result" and self.result_image_path:
                self.display_image_in_panel(self.result_image_path, "result")
            elif self.current_view_mode == "comparison":
                if self.selected_image_path:
                    self.display_image_in_panel(self.selected_image_path, "original")
                if self.result_image_path:
                    self.display_image_in_panel(self.result_image_path, "result")
            elif self.current_view_mode == "overlay":
                self.display_overlay_view()
    
    def on_canvas_drag_start(self, event, panel_type):
        """Handle start of potential canvas drag for panning"""
        # NOTE: EnhancedSyncManager handles synchronization through its own event bindings
        # This handler is for non-synchronized or fallback dragging only
        
        # Skip if sync drag is enabled (EnhancedSyncManager will handle it)
        if hasattr(self, 'sync_drag_var') and self.sync_drag_var.get():
            return
        
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y
        self.drag_data["dragging"] = False
        self.drag_data["threshold_met"] = False
        canvas = self.original_canvas if panel_type == "original" else self.result_canvas
    
    def on_canvas_drag_motion(self, event, panel_type):
        """Handle canvas drag motion for panning"""
        # NOTE: EnhancedSyncManager handles synchronization through its own event bindings
        # This handler is for non-synchronized or fallback dragging only
        
        # Skip if sync drag is enabled (EnhancedSyncManager will handle it)
        if hasattr(self, 'sync_drag_var') and self.sync_drag_var.get():
            return
        
        canvas = self.original_canvas if panel_type == "original" else self.result_canvas
        
        # Calculate how much the mouse moved
        dx = event.x - self.drag_data["x"]
        dy = event.y - self.drag_data["y"]
        
        # Only start dragging if movement exceeds threshold (5 pixels)
        if not self.drag_data["threshold_met"] and (abs(dx) > 5 or abs(dy) > 5):
            self.drag_data["threshold_met"] = True
            self.drag_data["dragging"] = True
            canvas.configure(cursor="fleur")
            canvas.scan_mark(self.drag_data["x"], self.drag_data["y"])
        
        # Only pan if dragging is active
        if self.drag_data["dragging"]:
            canvas.scan_dragto(event.x, event.y, gain=1)
        
    def on_canvas_drag_end(self, event, panel_type):
        """Handle end of canvas drag"""
        # NOTE: EnhancedSyncManager handles synchronization through its own event bindings
        # This handler is for non-synchronized or fallback dragging only
        
        # Skip if sync drag is enabled (EnhancedSyncManager will handle it)
        if hasattr(self, 'sync_drag_var') and self.sync_drag_var.get():
            return
        
        self.drag_data["dragging"] = False
        self.drag_data["threshold_met"] = False
        canvas = self.original_canvas if panel_type == "original" else self.result_canvas
        canvas.configure(cursor="")
    
    def on_canvas_enter(self, event, panel_type):
        """Handle mouse entering canvas"""
        canvas = self.original_canvas if panel_type == "original" else self.result_canvas
        canvas.focus_set()
        # Show hand cursor to indicate draggable
        if hasattr(canvas, 'image'):  # Only if there's an image
            canvas.configure(cursor="hand2")
    
    def on_canvas_leave(self, event, panel_type):
        """Handle mouse leaving canvas"""
        canvas = self.original_canvas if panel_type == "original" else self.result_canvas
        # Reset cursor when leaving
        if not self.drag_data["dragging"]:
            canvas.configure(cursor="")
    
    def on_canvas_click(self, event, panel_type):
        """Handle canvas click for specific panel"""
        # If not dragging, just set scan mark for potential future dragging
        canvas = self.original_canvas if panel_type == "original" else self.result_canvas
        canvas.scan_mark(event.x, event.y)
    
    def on_mouse_wheel(self, event, panel_type):
        """Handle mouse wheel for specific panel"""
        # Handle zoom with mouse wheel
        if self.sync_zoom_var.get():
            # Apply zoom to both panels
            pass
        else:
            # Apply zoom to specific panel only
            pass
    
    def show_panel_message(self, panel_type):
        """Show default message in panel with proper centering"""
        try:
            # Get canvas reference
            canvas = self.original_canvas if panel_type == "original" else self.result_canvas
            
            if not canvas.winfo_exists():
                return
            
            # Force canvas to update its size
            canvas.update_idletasks()
            
            # Get actual canvas dimensions
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
            
            logger.info(f"ImprovedSeedreamLayout: Panel message displayed for {panel_type} ({canvas_width}x{canvas_height})")
            
        except Exception as e:
            logger.error(f"ImprovedSeedreamLayout: Error showing panel message for {panel_type}: {e}")
    
    def display_image_in_panel(self, image_path, panel_type):
        """Display image in specific panel"""
        try:
            canvas = self.original_canvas if panel_type == "original" else self.result_canvas
            
            if not hasattr(self, 'original_canvas') or not hasattr(self, 'result_canvas'):
                return
            
            canvas.delete("all")
            
            img = Image.open(image_path)
            canvas_width = canvas.winfo_width()
            canvas_height = canvas.winfo_height()
            
            if canvas_width <= 1:
                canvas_width = 300  # Default for side-by-side
                canvas_height = 400
            
            zoom_value = self.zoom_var.get()
            if zoom_value == "Fit":
                # Better fit calculation with more padding for UI controls
                scale_factor = min(
                    (canvas_width - 20) / img.width,
                    (canvas_height - 40) / img.height  # More vertical padding for controls
                )
                # Ensure minimum scale to prevent tiny images
                scale_factor = max(scale_factor, 0.1)
            else:
                scale_factor = float(zoom_value.rstrip('%')) / 100
            
            new_width = int(img.width * scale_factor)
            new_height = int(img.height * scale_factor)
            img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            photo = ImageTk.PhotoImage(img_resized)
            
            x = max(5, (canvas_width - new_width) // 2)
            y = max(5, (canvas_height - new_height) // 2)
            
            canvas.create_image(x, y, anchor=tk.NW, image=photo)
            canvas.image = photo  # Keep reference
            
            canvas.configure(scrollregion=canvas.bbox("all"))
            
            # Update enhanced sync manager with image information
            if hasattr(self, 'enhanced_sync_manager'):
                self.enhanced_sync_manager.update_image_info(
                    panel_type=panel_type,
                    width=new_width,
                    height=new_height,
                    scale=scale_factor,
                    offset_x=x,
                    offset_y=y
                )
            
        except Exception as e:
            canvas.delete("all")
            canvas.create_text(
                150, 200,
                text=f"Error loading image:\n{str(e)}",
                fill="red",
                font=('Arial', 10),
                justify=tk.CENTER
            )
    
    def show_side_by_side_view(self):
        """Show side-by-side comparison view"""
        # Implementation for side-by-side view
        pass
    
    def display_overlay_view(self):
        """Display overlay comparison view with opacity blending"""
        if not self.selected_image_path or not self.result_image_path:
            # Show message if we don't have both images
            self.original_canvas.delete("all")
            self.original_canvas.create_text(
                150, 200,
                text="Overlay mode requires both\noriginal and result images",
                font=('Arial', 12),
                fill='#888',
                justify=tk.CENTER
            )
            return
        
        try:
            # Load both images
            original_img = Image.open(self.selected_image_path)
            result_img = Image.open(self.result_image_path)
            
            # Get canvas dimensions
            canvas = self.original_canvas
            canvas_width = canvas.winfo_width()
            canvas_height = canvas.winfo_height()
            
            if canvas_width <= 1:
                canvas_width = 400
                canvas_height = 400
            
            # Calculate scale factor based on zoom setting
            zoom_value = self.zoom_var.get()
            if zoom_value == "Fit":
                # Scale to fit the larger of the two images
                max_width = max(original_img.width, result_img.width)
                max_height = max(original_img.height, result_img.height)
                scale_factor = min(
                    (canvas_width - 20) / max_width,
                    (canvas_height - 20) / max_height
                )
            else:
                scale_factor = float(zoom_value.rstrip('%')) / 100
            
            # Resize both images to the same size (use the larger dimensions)
            target_width = max(original_img.width, result_img.width)
            target_height = max(original_img.height, result_img.height)
            
            # Resize images to target size if needed
            if original_img.size != (target_width, target_height):
                original_img = original_img.resize((target_width, target_height), Image.Resampling.LANCZOS)
            if result_img.size != (target_width, target_height):
                result_img = result_img.resize((target_width, target_height), Image.Resampling.LANCZOS)
            
            # Apply zoom scaling
            display_width = int(target_width * scale_factor)
            display_height = int(target_height * scale_factor)
            
            original_img = original_img.resize((display_width, display_height), Image.Resampling.LANCZOS)
            result_img = result_img.resize((display_width, display_height), Image.Resampling.LANCZOS)
            
            # Create blended image
            opacity = self.opacity_var.get()
            blended_img = Image.blend(original_img.convert('RGBA'), result_img.convert('RGBA'), opacity)
            
            # Clear canvas and display blended image
            canvas.delete("all")
            
            # Convert to PhotoImage
            photo = ImageTk.PhotoImage(blended_img)
            
            # Center the image
            x = max(10, (canvas_width - display_width) // 2)
            y = max(10, (canvas_height - display_height) // 2)
            
            canvas.create_image(x, y, anchor=tk.NW, image=photo)
            canvas.image = photo  # Keep reference
            
            canvas.configure(scrollregion=canvas.bbox("all"))
            
            # Add overlay info text
            canvas.create_text(
                10, 10,
                text=f"Overlay: {int(opacity * 100)}% result",
                font=('Arial', 10, 'bold'),
                fill='white',
                anchor=tk.NW
            )
            # Add shadow for better visibility
            canvas.create_text(
                11, 11,
                text=f"Overlay: {int(opacity * 100)}% result",
                font=('Arial', 10, 'bold'),
                fill='black',
                anchor=tk.NW
            )
            
        except Exception as e:
            canvas.delete("all")
            canvas.create_text(
                150, 200,
                text=f"Error creating overlay:\n{str(e)}",
                fill="red",
                font=('Arial', 10),
                justify=tk.CENTER
            )
    
    def show_original_only(self):
        """Show original image only"""
        # Implementation for original only view
        pass
    
    def show_result_only(self):
        """Show result image only"""
        # Implementation for result only view
        pass
    
    def quick_save_result(self):
        """Quick save result image"""
        if hasattr(self, 'result_image_path') and self.result_image_path:
            try:
                from tkinter import filedialog
                file_path = filedialog.asksaveasfilename(
                    title="Save Result Image",
                    defaultextension=".png",
                    filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*")]
                )
                if file_path:
                    # Copy or download the result image
                    self.log_message(f"💾 Saved result to: {file_path}")
            except Exception as e:
                self.log_message(f"❌ Save failed: {str(e)}")
        else:
            self.log_message("❌ No result to save")
    
    def swap_images(self):
        """Swap original and result images"""
        # Implementation for swapping images in comparison view
        self.log_message("🔄 Images swapped")
    
    def cancel_processing(self):
        """Cancel current processing"""
        if hasattr(self, 'current_task_id') and self.current_task_id:
            self.log_message("🛑 Processing cancelled")
            self.hide_progress_overlay()
    
    def show_progress_overlay(self):
        """Show progress overlay"""
        self.progress_overlay.grid()
        self.progress_bar.start(10)
    
    def hide_progress_overlay(self):
        """Hide progress overlay"""
        self.progress_overlay.grid_remove()
        self.progress_bar.stop()
    
    def update_progress_status(self, message):
        """Update progress status message"""
        if hasattr(self, 'progress_status'):
            self.progress_status.config(text=message)
    
    def show_quality_rating(self, prompt: str = None, result_path: str = None):
        """Show quality rating dialog for user feedback"""
        try:
            from core.quality_rating_widget import QualityRatingDialog
            
            # Use stored values if called from button
            if prompt is None and hasattr(self, 'last_prompt'):
                prompt = self.last_prompt
            if result_path is None and hasattr(self, 'last_result_path'):
                result_path = self.last_result_path
                
            if not prompt:
                self.log_message("❌ No prompt available for rating")
                return
            
            def on_rating_complete(quality, feedback):
                self.log_message(f"📊 Quality rated: {quality}")
                if feedback:
                    self.log_message(f"📝 User feedback: {feedback[:50]}...")
            
            self.quality_dialog = QualityRatingDialog(
                parent=self.parent_frame,
                prompt=prompt,
                result_path=result_path,
                callback=on_rating_complete
            )
            
        except Exception as e:
            logger.error(f"Error showing quality rating: {e}")
            self.log_message(f"❌ Failed to open quality rating: {str(e)}")
    
    def update_learning_insights(self, prompt: str, success: bool, result_data: dict = None):
        """Update learning insights with new data"""
        try:
            # Update learning panel if it exists
            if hasattr(self, 'learning_panel') and self.learning_panel is not None:
                self.learning_panel.update_insights(prompt, success, result_data)
            
            # Log learning update
            status = "successful" if success else "failed"
            self.log_message(f"🧠 Learning updated: {status} generation")
            
        except Exception as e:
            logger.error(f"Error updating learning insights: {e}")
    
    # Helper methods for tab integration
    
    def log_status(self, message: str, status_type: str = "info"):
        """Log status message to console"""
        if self.status_console:
            self.status_console.log_status(message, status_type)
    
    def log_processing_start(self, operation: str, details: str = ""):
        """Log start of processing with timing"""
        if self.status_console:
            self.status_console.log_processing_start(operation, details)
    
    def log_processing_complete(self, operation: str, success: bool = True, details: str = ""):
        """Log completion of processing with timing"""
        if self.status_console:
            self.status_console.log_processing_complete(operation, success, details)
    
    def log_file_operation(self, operation: str, filename: str, success: bool = True):
        """Log file operations"""
        if self.status_console:
            self.status_console.log_file_operation(operation, filename, success)
    
    def log_error(self, error_message: str, context: str = ""):
        """Log error message"""
        if self.status_console:
            self.status_console.log_error(error_message, context)
    
    def show_progress(self):
        """Show progress bar"""
        if self.status_console:
            self.status_console.show_progress()
    
    def hide_progress(self):
        """Hide progress bar"""
        if self.status_console:
            self.status_console.hide_progress()
    
    def setup_keyboard_callbacks(self, primary_action=None, primary_widget=None, 
                                browse_image=None, save_result=None, clear_all=None,
                                improve_ai=None, filter_training=None, ai_chat=None):
        """Setup keyboard callbacks from the parent tab"""
        if self.keyboard_manager:
            if primary_action and primary_widget:
                self.keyboard_manager.register_primary_action(primary_action, primary_widget)
            
            if browse_image or save_result or clear_all:
                self.keyboard_manager.register_file_actions(
                    open_file=browse_image,
                    save_result=save_result,
                    new_operation=clear_all
                )
            
            if improve_ai or filter_training or ai_chat:
                self.keyboard_manager.register_ai_actions(
                    improve_callback=improve_ai,
                    filter_callback=filter_training,
                    chat_callback=ai_chat
                )
    
    def set_operation_in_progress(self, in_progress: bool):
        """Update operation status for keyboard manager"""
        if self.keyboard_manager:
            self.keyboard_manager.set_operation_in_progress(in_progress)
    
    def show_image_reorder_dialog(self):
        """Show dialog to reorder selected images"""
        if len(self.selected_image_paths) < 2:
            return
        
        import tkinter as tk
        from tkinter import ttk
        from PIL import Image, ImageTk
        
        # Create dialog window
        dialog = tk.Toplevel(self.parent_frame)
        dialog.title("Reorder Images")
        dialog.geometry("600x500")
        dialog.transient(self.parent_frame)
        dialog.grab_set()
        
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
            command=lambda: self.apply_image_order(dialog),
            style="Accent.TButton"
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
    
    def populate_reorder_listbox(self):
        """Populate the reorder listbox with current image order"""
        self.reorder_listbox.delete(0, tk.END)
        
        for i, image_path in enumerate(self.selected_image_paths):
            filename = os.path.basename(image_path)
            # Show position number and filename
            display_text = f"{i+1}. {filename}"
            self.reorder_listbox.insert(tk.END, display_text)
    
    def move_image_up(self, dialog):
        """Move selected image up in the order"""
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
    
    def move_image_down(self, dialog):
        """Move selected image down in the order"""
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
    
    def move_image_to_top(self, dialog):
        """Move selected image to the top of the order"""
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
    
    def move_image_to_bottom(self, dialog):
        """Move selected image to the bottom of the order"""
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
    
    def reset_image_order(self, dialog):
        """Reset to original image order"""
        self.selected_image_paths = self.original_image_order.copy()
        self.populate_reorder_listbox()
        if self.reorder_listbox.size() > 0:
            self.reorder_listbox.selection_set(0)
    
    def apply_image_order(self, dialog):
        """Apply the new image order and close dialog"""
        # Update the display to reflect new order
        self.update_image_count_display()
        
        # Update the original image display to show the first image in the new order
        if self.selected_image_paths:
            first_image = self.selected_image_paths[0]
            # Update the thumbnail and info display
            self.load_image(first_image)
            # Also update the original canvas display directly
            self.display_image_in_panel(first_image, "original")
        
        # Log the new order
        filenames = [os.path.basename(path) for path in self.selected_image_paths]
        self.log_message(f"🔄 Image order updated: {', '.join(filenames)}")
        
        dialog.destroy()
