"""
Comparison Modes Module
Provides advanced comparison features for before/after images

Features:
- Side-by-side view
- Overlay view with opacity control
- Swipe/slider comparison
- Split view
"""

# Standard library imports
import os
import tempfile
from typing import Optional, Callable

# Third-party imports
import tkinter as tk
from tkinter import ttk, messagebox
# PIL lazy-loaded when needed (saves ~61ms on startup)

# Local application imports
from core.logger import get_logger
from utils.color_matcher import ColorMatcher

logger = get_logger()


class ComparisonController:
    """
    Advanced comparison controller for before/after image comparison
    
    Supports multiple comparison modes with smooth transitions
    """
    
    def __init__(self, layout_instance):
        """
        Initialize comparison controller
        
        Args:
            layout_instance: Reference to main layout for canvas access
        """
        self.layout = layout_instance
        
        # Current mode (extended with new modes)
        self.current_mode = "side_by_side"  # side_by_side, overlay, original_only, result_only, difference, split, grid
        
        # Overlay state
        self.overlay_opacity = 0.5
        self.overlay_canvas = None
        self.overlay_image_id = None
        
        # Opacity update debouncing
        self.opacity_update_timer = None
        self.opacity_update_delay = 500  # ms delay for debouncing
        
        # Zoom change debouncing
        self.zoom_update_timer = None
        self.zoom_update_delay = 300  # ms delay for zoom changes
        
        # Split slider state
        self.split_position = 0.5  # 0-1, percentage from left/top
        self.split_orientation = 'vertical'  # vertical or horizontal
        
        # Animation state
        self.animation_active = False
        self.animation_timer = None
        self.animation_direction = 1  # 1 for forward, -1 for reverse
        self.animation_speed = 50  # ms between frames
        
        # Independent zoom (for side-by-side mode)
        self.independent_zoom_enabled = False
        self.left_zoom = "Fit"
        self.right_zoom = "Fit"
        
        # Color matching comparison state
        self.color_match_active = False
        self.original_result_path = None
        self.color_matched_path = None
        self.color_match_buttons_frame = None
        
        # UI references
        self.mode_var = tk.StringVar(value="side_by_side")
        self.opacity_var = tk.DoubleVar(value=0.5)
        
        # Setup zoom change listener after initialization
        self.layout.parent_frame.after(100, self._setup_zoom_listener)
        
        logger.info("ComparisonController initialized with enhanced modes")
    
    def setup_comparison_controls(self, parent_frame) -> tk.Widget:
        """
        Create comparison controls UI
        
        Args:
            parent_frame: Parent frame to add controls to
            
        Returns:
            The controls frame widget
        """
        controls_frame = ttk.Frame(parent_frame, padding="4")
        controls_frame.grid(row=0, column=0, sticky="ew", pady=(0, 2))
        
        # Store reference for color match buttons
        self.controls_frame = controls_frame
        
        # Mode selection
        ttk.Label(controls_frame, text="View Mode:", font=('Arial', 9, 'bold')).pack(side=tk.LEFT, padx=(0, 10))
        
        # View mode dropdown (more compact than radio buttons)
        # Create dropdown with view mode options (including new enhanced modes)
        self.mode_dropdown = ttk.Combobox(
            controls_frame,
            values=[
                "↔️ Side by Side",
                "📊 Overlay",
                "🎯 Difference",
                "✂️ Split View",
                "🏁 Grid (2x2)",
                "📷 Original Only",
                "✨ Result Only"
            ],
            state="readonly",
            width=18,
            font=('Arial', 9)
        )
        self.mode_dropdown.pack(side=tk.LEFT, padx=5)
        
        # Map display names to internal values
        self.mode_display_to_value = {
            "↔️ Side by Side": "side_by_side",
            "📊 Overlay": "overlay",
            "🎯 Difference": "difference",
            "✂️ Split View": "split",
            "🏁 Grid (2x2)": "grid",
            "📷 Original Only": "original_only",
            "✨ Result Only": "result_only"
        }
        self.mode_value_to_display = {v: k for k, v in self.mode_display_to_value.items()}
        
        # Set initial display value
        self.mode_dropdown.set(self.mode_value_to_display.get(self.mode_var.get(), "↔️ Side by Side"))
        
        # Bind selection change
        self.mode_dropdown.bind('<<ComboboxSelected>>', self._on_mode_dropdown_change)
        
        # Sync controls frame (Sync Zoom and Sync Drag)
        sync_frame = ttk.Frame(controls_frame)
        sync_frame.pack(side=tk.LEFT, padx=(20, 0))
        
        # Sync zoom toggle
        sync_zoom_check = ttk.Checkbutton(
            sync_frame,
            text="🔗 Sync Zoom",
            variable=self.layout.sync_zoom_var,
            command=self._on_sync_zoom_changed
        )
        sync_zoom_check.pack(side=tk.LEFT, padx=(0, 8))
        
        # Sync drag toggle
        sync_drag_check = ttk.Checkbutton(
            sync_frame,
            text="🔗 Sync Drag",
            variable=self.layout.sync_drag_var,
            command=self._on_sync_drag_changed
        )
        sync_drag_check.pack(side=tk.LEFT)
        
        # Zoom level slider (with non-linear scale)
        zoom_outer_frame = ttk.Frame(controls_frame)
        zoom_outer_frame.pack(side=tk.LEFT, padx=(20, 0))
        
        # Top row: Label, current value, slider
        zoom_top_frame = ttk.Frame(zoom_outer_frame)
        zoom_top_frame.pack(side=tk.TOP)
        
        ttk.Label(zoom_top_frame, text="Zoom:", font=('Arial', 9, 'bold')).pack(side=tk.LEFT, padx=(0, 5))
        
        # Zoom value label
        self.zoom_label = ttk.Label(zoom_top_frame, text="Fit", font=('Arial', 9), width=6)
        self.zoom_label.pack(side=tk.LEFT, padx=(0, 5))
        
        # Create slider with custom non-linear scale
        # Slider range: 0-100 (will be mapped to zoom percentages)
        self.zoom_slider_var = tk.IntVar(value=50)  # Default to middle (100%)
        self.zoom_slider = ttk.Scale(
            zoom_top_frame,
            from_=0,
            to=100,
            orient=tk.HORIZONTAL,
            variable=self.zoom_slider_var,
            command=self._on_zoom_slider_changed,
            length=200
        )
        self.zoom_slider.pack(side=tk.LEFT, padx=5)
        
        # Bottom row: Tick marks (visual indicators)
        tick_frame = ttk.Frame(zoom_outer_frame)
        tick_frame.pack(side=tk.TOP, pady=(0, 0))
        
        # Add spacing to align with slider
        ttk.Label(tick_frame, text="", width=10).pack(side=tk.LEFT)  # Align with "Zoom: Fit"
        
        # Tick marks container (aligned with slider)
        tick_marks_frame = tk.Frame(tick_frame, width=200)
        tick_marks_frame.pack(side=tk.LEFT, padx=5)
        tick_marks_frame.pack_propagate(False)
        
        # Add tick marks at key positions
        # Scale: 0-25 = Fit-25%, 25-50 = 25%-100%, 50-100 = 150%-300%
        tick_labels = [
            (0, "Fit"),
            (25, "25%"),
            (50, "100%"),
            (75, "225%"),
            (100, "300%")
        ]
        
        for position, label_text in tick_labels:
            # Calculate x position (0-200px range)
            x_pos = int((position / 100) * 200)
            
            tick_label = ttk.Label(
                tick_marks_frame, 
                text=label_text, 
                font=('Arial', 7), 
                foreground='gray'
            )
            tick_label.place(x=x_pos, y=0, anchor='n')
        
        # Initialize zoom to 100%
        self._set_zoom_from_slider(50)
        
        # Opacity control (only visible in overlay mode)
        self.opacity_frame = ttk.Frame(controls_frame)
        self.opacity_frame.pack(side=tk.LEFT, padx=(20, 0))
        
        ttk.Label(self.opacity_frame, text="Blend:").pack(side=tk.LEFT, padx=(0, 5))
        
        # Use tk.Scale instead of ttk.Scale for tick marks and resolution
        opacity_scale = tk.Scale(
            self.opacity_frame,
            from_=0.0,
            to=1.0,
            resolution=0.1,  # 10% increments
            tickinterval=0.1,  # Show tick marks every 10%
            orient=tk.HORIZONTAL,
            variable=self.opacity_var,
            command=self._on_opacity_changed,
            length=150,
            showvalue=0,  # Hide the built-in value display (we use our own label)
            bg='#f0f0f0',
            troughcolor='#d0d0d0',
            activebackground='#0078d7',
            highlightthickness=0,
            bd=1,
            relief=tk.FLAT
        )
        opacity_scale.pack(side=tk.LEFT, padx=5)
        
        self.opacity_label = ttk.Label(self.opacity_frame, text="50%", width=5)
        self.opacity_label.pack(side=tk.LEFT, padx=(0, 5))
        
        # Initially hide opacity controls
        self.opacity_frame.pack_forget()
        
        # Animation toggle button
        self.animation_button = ttk.Button(
            controls_frame,
            text="▶️ Animate",
            command=self.toggle_animation,
            width=12
        )
        self.animation_button.pack(side=tk.RIGHT, padx=2)
        
        # Swap button
        ttk.Button(
            controls_frame,
            text="🔄 Swap",
            command=self.swap_images,
            width=10
        ).pack(side=tk.RIGHT, padx=2)
        
        # Color Match button
        ttk.Button(
            controls_frame,
            text="🎨 Match Colors",
            command=self.apply_color_matching,
            width=14
        ).pack(side=tk.RIGHT, padx=2)
        
        # Smart Mask button
        ttk.Button(
            controls_frame,
            text="🎯 Smart Mask",
            command=self.show_smart_mask_controls,
            width=14
        ).pack(side=tk.RIGHT, padx=2)
        
        # Smart Mask Toggle button (appears after mask is applied)
        self.smart_mask_toggle_btn = ttk.Button(
            controls_frame,
            text="👁️ Toggle Mask",
            command=self.toggle_smart_mask_view,
            width=14,
            state='disabled'  # Initially disabled until mask is applied
        )
        self.smart_mask_toggle_btn.pack(side=tk.RIGHT, padx=2)
        
        # Store paths for smart mask toggle
        self.smart_mask_applied_path = None
        self.smart_mask_original_result_path = None
        self.smart_mask_showing_masked = True
        
        logger.info("Comparison controls UI created with enhanced features")
        return controls_frame
    
    def set_mode(self, mode: str):
        """
        Set comparison mode
        
        Args:
            mode: Mode name ('side_by_side', 'overlay', 'original_only', 'result_only')
        """
        if mode == self.current_mode:
            return
        
        self.current_mode = mode
        self.mode_var.set(mode)
        
        # Update dropdown display
        if hasattr(self, 'mode_dropdown') and hasattr(self, 'mode_value_to_display'):
            display_value = self.mode_value_to_display.get(mode)
            if display_value:
                self.mode_dropdown.set(display_value)
        
        # Show/hide opacity controls
        if mode == "overlay":
            self.opacity_frame.pack(side=tk.LEFT, padx=(20, 0))
        else:
            self.opacity_frame.pack_forget()
        
        # Apply the mode
        self._apply_mode()
        
        logger.info(f"Comparison mode set to: {mode}")
    
    def _apply_mode(self):
        """Apply the current comparison mode to the UI"""
        mode = self.current_mode
        
        if mode == "side_by_side":
            self._show_side_by_side()
        elif mode == "overlay":
            self._show_overlay()
        elif mode == "difference":
            self._show_difference()
        elif mode == "split":
            self._show_split_view()
        elif mode == "grid":
            self._show_grid_view()
        elif mode == "original_only":
            self._show_single_panel("original")
        elif mode == "result_only":
            self._show_single_panel("result")
    
    def _show_side_by_side(self):
        """Show both panels side by side"""
        # Make both panels visible by ensuring display paned window shows both
        if hasattr(self.layout, 'display_paned_window'):
            # Re-add both panels if they were removed
            if hasattr(self.layout, 'original_container') and hasattr(self.layout, 'result_container'):
                # Check if panels are already in the paned window
                try:
                    self.layout.display_paned_window.panes()
                except:
                    pass
                
                # Clear and re-add both panels
                for pane in self.layout.display_paned_window.panes():
                    self.layout.display_paned_window.forget(pane)
                
                self.layout.display_paned_window.add(self.layout.original_container, weight=1)
                self.layout.display_paned_window.add(self.layout.result_container, weight=1)
        
        logger.debug("Showing side-by-side view")
    
    def _show_overlay(self):
        """Show overlay mode with both images blended"""
        try:
            # CRITICAL: Show only the original panel for overlay mode
            # Remove result panel from paned window so original expands to full width
            if hasattr(self.layout, 'display_paned_window') and hasattr(self.layout, 'original_container'):
                # Clear paned window and add only original container (full width)
                for pane in self.layout.display_paned_window.panes():
                    self.layout.display_paned_window.forget(pane)
                
                self.layout.display_paned_window.add(self.layout.original_container, weight=1)
                logger.debug("Showing overlay in full-width original panel")
            
            # Automatically set zoom to "Fit" for optimal overlay viewing and centering
            if hasattr(self.layout, 'zoom_var'):
                current_zoom = self.layout.zoom_var.get()
                if current_zoom != "Fit":
                    self.layout.zoom_var.set("Fit")
                    # Update zoom slider to position 0 (Fit)
                    if hasattr(self, 'zoom_slider_var'):
                        self.zoom_slider_var.set(0)
                    if hasattr(self, 'zoom_label'):
                        self.zoom_label.config(text="Fit")
                    logger.debug("Auto-set zoom to Fit for overlay mode")
            
            # Automatically reset opacity to 50% for optimal comparison
            self.overlay_opacity = 0.5
            self.opacity_var.set(0.5)
            self.opacity_label.config(text="50%")
            logger.debug("Auto-set blend to 50% for overlay mode")
            
            # Get image paths
            original_path = None
            result_path = None
            
            if hasattr(self.layout, 'image_manager') and hasattr(self.layout.image_manager, 'selected_image_paths'):
                paths = self.layout.image_manager.selected_image_paths
                if paths and len(paths) > 0:
                    original_path = paths[0]
            
            if hasattr(self.layout, 'results_manager') and hasattr(self.layout.results_manager, 'result_image_path'):
                result_path = self.layout.results_manager.result_image_path
            elif hasattr(self.layout, 'result_image_path'):
                result_path = self.layout.result_image_path
            
            # Use image manager's overlay display method with current opacity
            if original_path and result_path and hasattr(self.layout, 'image_manager'):
                self.layout.image_manager.display_overlay_view(
                    self.layout.original_canvas,
                    original_path,
                    result_path,
                    self.layout.zoom_var,
                    opacity=self.overlay_opacity  # Pass current opacity value
                )
                logger.debug(f"Showing overlay view with opacity: {self.overlay_opacity:.2f}")
            else:
                # Fall back to side-by-side if images not available
                logger.warning("Cannot show overlay: missing images")
                self._show_side_by_side()
        
        except Exception as e:
            logger.error(f"Error showing overlay view: {e}")
            self._show_side_by_side()
    
    def _show_single_panel(self, panel_type: str):
        """
        Show only one panel
        
        Args:
            panel_type: 'original' or 'result'
        """
        if not hasattr(self.layout, 'display_paned_window'):
            return
        
        if not hasattr(self.layout, 'original_container') or not hasattr(self.layout, 'result_container'):
            return
        
        # Clear paned window and add only the requested panel
        for pane in self.layout.display_paned_window.panes():
            self.layout.display_paned_window.forget(pane)
        
        if panel_type == "original":
            self.layout.display_paned_window.add(self.layout.original_container, weight=1)
        else:
            self.layout.display_paned_window.add(self.layout.result_container, weight=1)
        
        logger.debug(f"Showing {panel_type} only")
    
    def _show_difference(self):
        """Show difference highlighting mode - highlights pixel differences"""
        try:
            # Use only original panel for difference view (full width)
            if hasattr(self.layout, 'display_paned_window') and hasattr(self.layout, 'original_container'):
                for pane in self.layout.display_paned_window.panes():
                    self.layout.display_paned_window.forget(pane)
                
                self.layout.display_paned_window.add(self.layout.original_container, weight=1)
                logger.debug("Showing difference view in full-width panel")
            
            # Get image paths
            original_path = None
            result_path = None
            
            if hasattr(self.layout, 'image_manager') and hasattr(self.layout.image_manager, 'selected_image_paths'):
                paths = self.layout.image_manager.selected_image_paths
                if paths and len(paths) > 0:
                    original_path = paths[0]
            
            if hasattr(self.layout, 'results_manager') and hasattr(self.layout.results_manager, 'result_image_path'):
                result_path = self.layout.results_manager.result_image_path
            elif hasattr(self.layout, 'result_image_path'):
                result_path = self.layout.result_image_path
            
            # Display difference view
            if original_path and result_path and hasattr(self.layout, 'image_manager'):
                self.layout.image_manager.display_difference_view(
                    self.layout.original_canvas,
                    original_path,
                    result_path,
                    self.layout.zoom_var
                )
                logger.debug("Difference view displayed")
            else:
                logger.warning("Cannot show difference: missing images")
                self._show_side_by_side()
                
        except Exception as e:
            logger.error(f"Error showing difference view: {e}")
            self._show_side_by_side()
    
    def _show_split_view(self):
        """Show split slider view with draggable divider"""
        try:
            # Use only original panel for split view (full width)
            if hasattr(self.layout, 'display_paned_window') and hasattr(self.layout, 'original_container'):
                for pane in self.layout.display_paned_window.panes():
                    self.layout.display_paned_window.forget(pane)
                
                self.layout.display_paned_window.add(self.layout.original_container, weight=1)
                logger.debug("Showing split view in full-width panel")
            
            # Get image paths
            original_path = None
            result_path = None
            
            if hasattr(self.layout, 'image_manager') and hasattr(self.layout.image_manager, 'selected_image_paths'):
                paths = self.layout.image_manager.selected_image_paths
                if paths and len(paths) > 0:
                    original_path = paths[0]
            
            if hasattr(self.layout, 'results_manager') and hasattr(self.layout.results_manager, 'result_image_path'):
                result_path = self.layout.results_manager.result_image_path
            elif hasattr(self.layout, 'result_image_path'):
                result_path = self.layout.result_image_path
            
            # Display split view
            if original_path and result_path and hasattr(self.layout, 'image_manager'):
                self.layout.image_manager.display_split_view(
                    self.layout.original_canvas,
                    original_path,
                    result_path,
                    self.layout.zoom_var,
                    split_position=self.split_position,
                    orientation=self.split_orientation
                )
                logger.debug(f"Split view displayed at {self.split_position:.0%}")
            else:
                logger.warning("Cannot show split: missing images")
                self._show_side_by_side()
                
        except Exception as e:
            logger.error(f"Error showing split view: {e}")
            self._show_side_by_side()
    
    def _show_grid_view(self):
        """Show 2x2 grid view (Original, Result, Overlay, Difference)"""
        try:
            # Use only original panel for grid view (full width)
            if hasattr(self.layout, 'display_paned_window') and hasattr(self.layout, 'original_container'):
                for pane in self.layout.display_paned_window.panes():
                    self.layout.display_paned_window.forget(pane)
                
                self.layout.display_paned_window.add(self.layout.original_container, weight=1)
                logger.debug("Showing grid view in full-width panel")
            
            # Get image paths
            original_path = None
            result_path = None
            
            if hasattr(self.layout, 'image_manager') and hasattr(self.layout.image_manager, 'selected_image_paths'):
                paths = self.layout.image_manager.selected_image_paths
                if paths and len(paths) > 0:
                    original_path = paths[0]
            
            if hasattr(self.layout, 'results_manager') and hasattr(self.layout.results_manager, 'result_image_path'):
                result_path = self.layout.results_manager.result_image_path
            elif hasattr(self.layout, 'result_image_path'):
                result_path = self.layout.result_image_path
            
            # Display grid view
            if original_path and result_path and hasattr(self.layout, 'image_manager'):
                self.layout.image_manager.display_grid_view(
                    self.layout.original_canvas,
                    original_path,
                    result_path,
                    self.layout.zoom_var
                )
                logger.debug("Grid view displayed")
            else:
                logger.warning("Cannot show grid: missing images")
                self._show_side_by_side()
                
        except Exception as e:
            logger.error(f"Error showing grid view: {e}")
            self._show_side_by_side()
    
    def toggle_animation(self):
        """Toggle animation between original and result"""
        if self.animation_active:
            # Stop animation
            self.stop_animation()
        else:
            # Start animation
            self.start_animation()
    
    def start_animation(self):
        """Start auto-fade animation between images"""
        try:
            self.animation_active = True
            self.animation_button.config(text="⏸️ Stop")
            self.overlay_opacity = 0.0
            self.opacity_var.set(0.0)
            
            # Switch to overlay mode for animation
            if self.current_mode != "overlay":
                self.set_mode("overlay")
            
            # Start animation loop
            self._animate_frame()
            logger.info("Animation started")
            
        except Exception as e:
            logger.error(f"Error starting animation: {e}")
            self.stop_animation()
    
    def stop_animation(self):
        """Stop animation"""
        try:
            self.animation_active = False
            self.animation_button.config(text="▶️ Animate")
            
            # Cancel timer if exists
            if self.animation_timer:
                try:
                    self.layout.parent_frame.after_cancel(self.animation_timer)
                except:
                    pass
                self.animation_timer = None
            
            logger.info("Animation stopped")
            
        except Exception as e:
            logger.error(f"Error stopping animation: {e}")
    
    def _animate_frame(self):
        """Animate one frame"""
        try:
            if not self.animation_active:
                return
            
            # Update opacity
            current = self.overlay_opacity
            step = 0.02 * self.animation_direction  # 2% per frame
            
            new_opacity = current + step
            
            # Reverse direction at endpoints
            if new_opacity >= 1.0:
                new_opacity = 1.0
                self.animation_direction = -1
            elif new_opacity <= 0.0:
                new_opacity = 0.0
                self.animation_direction = 1
            
            self.overlay_opacity = new_opacity
            self.opacity_var.set(new_opacity)
            self.opacity_label.config(text=f"{int(new_opacity * 100)}%")
            
            # Apply opacity change
            self._apply_overlay_with_opacity()
            
            # Schedule next frame
            self.animation_timer = self.layout.parent_frame.after(
                self.animation_speed,
                self._animate_frame
            )
            
        except Exception as e:
            logger.error(f"Error in animation frame: {e}")
            self.stop_animation()
    
    def _on_opacity_changed(self, value):
        """Handle opacity slider change with debouncing to reduce lag"""
        # Don't snap during drag - just update the value
        raw_value = float(value)
        self.overlay_opacity = raw_value
        self.opacity_label.config(text=f"{int(self.overlay_opacity * 100)}%")
        
        # Cancel previous timer if exists
        if self.opacity_update_timer:
            try:
                self.layout.parent_frame.after_cancel(self.opacity_update_timer)
            except:
                pass
        
        # Schedule update after delay (debouncing)
        if self.current_mode == "overlay":
            self.opacity_update_timer = self.layout.parent_frame.after(
                self.opacity_update_delay,
                self._apply_overlay_with_opacity
            )
    
    def _apply_overlay_with_opacity(self):
        """Apply overlay with current opacity value (without triggering full mode refresh)"""
        try:
            # Directly update the overlay display without going through _apply_mode
            # to avoid triggering zoom or other unwanted refreshes
            if self.current_mode != "overlay":
                return
            
            # Get image paths
            original_path = None
            result_path = None
            
            if hasattr(self.layout, 'image_manager') and hasattr(self.layout.image_manager, 'selected_image_paths'):
                paths = self.layout.image_manager.selected_image_paths
                if paths and len(paths) > 0:
                    original_path = paths[0]
            
            if hasattr(self.layout, 'results_manager') and hasattr(self.layout.results_manager, 'result_image_path'):
                result_path = self.layout.results_manager.result_image_path
            elif hasattr(self.layout, 'result_image_path'):
                result_path = self.layout.result_image_path
            
            # Update only the overlay with new opacity
            if original_path and result_path and hasattr(self.layout, 'image_manager'):
                self.layout.image_manager.display_overlay_view(
                    self.layout.original_canvas,
                    original_path,
                    result_path,
                    self.layout.zoom_var,
                    opacity=self.overlay_opacity
                )
        except Exception as e:
            logger.error(f"Error applying overlay opacity: {e}")
    
    def swap_images(self):
        """Swap original and result images"""
        if not hasattr(self.layout, 'selected_image_path') or not hasattr(self.layout, 'result_image_path'):
            return
        
        # Swap the paths
        temp = self.layout.selected_image_path
        self.layout.selected_image_path = self.layout.result_image_path
        self.layout.result_image_path = temp
        
        # Redraw both panels
        if hasattr(self.layout.image_manager, 'display_image_in_panel'):
            if self.layout.selected_image_path:
                self.layout.image_manager.display_image_in_panel(
                    self.layout.selected_image_path, 'original'
                )
            if self.layout.result_image_path:
                self.layout.image_manager.display_image_in_panel(
                    self.layout.result_image_path, 'result'
                )
        
        logger.info("Images swapped")
    
    def apply_color_matching(self):
        """Apply subtle color correction to result image to match source"""
        try:
            # Get source and result paths
            source_path = None
            result_path = None
            
            # Try multiple ways to get the source image path
            if hasattr(self.layout, 'image_manager') and hasattr(self.layout.image_manager, 'selected_image_paths'):
                paths = self.layout.image_manager.selected_image_paths
                if paths:
                    source_path = paths[0]
            elif hasattr(self.layout, 'selected_image_path'):
                source_path = self.layout.selected_image_path
            
            # Get result path
            if hasattr(self.layout, 'results_manager') and hasattr(self.layout.results_manager, 'result_image_path'):
                result_path = self.layout.results_manager.result_image_path
            elif hasattr(self.layout, 'result_image_path'):
                result_path = self.layout.result_image_path
            
            # Debug logging
            logger.debug(f"Color matching paths - source: {source_path}, result: {result_path}")
            
            # Validate paths
            if not source_path or not os.path.exists(source_path):
                messagebox.showwarning(
                    "No Source Image",
                    "Please load an input image first to use as color reference."
                )
                logger.debug(f"Color matching failed: source_path={source_path}, exists={os.path.exists(source_path) if source_path else False}")
                return
            
            if not result_path or not os.path.exists(result_path):
                messagebox.showwarning(
                    "No Result Image",
                    "Please generate a result image first."
                )
                return
            
            # Show progress
            logger.info(f"Applying color matching: source={source_path}, target={result_path}")
            
            # Apply subtle color correction (60% strength)
            corrected_image = ColorMatcher.subtle_color_correction(
                source_path=source_path,
                target_path=result_path,
                method='lab'
            )
            
            if corrected_image:
                # Save to temporary file
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='_color_matched.png')
                corrected_image.save(temp_file.name, quality=95)
                temp_file.close()
                
                # Store paths for comparison
                self.original_result_path = result_path
                self.color_matched_path = temp_file.name
                self.color_match_active = True
                
                logger.info(f"Color match files ready: original={result_path}, matched={temp_file.name}")
                
                # Show comparison: original (left) vs color-matched (right)
                self._show_color_match_comparison()
                
                logger.info("✅ Color correction applied - showing comparison")
            else:
                messagebox.showerror("Error", "Failed to apply color matching.")
                
        except Exception as e:
            logger.error(f"Error applying color matching: {e}")
            messagebox.showerror("Error", f"Color matching failed: {str(e)}")
    
    def toggle_smart_mask_view(self):
        """Toggle between smart masked result and original AI result"""
        try:
            if not self.smart_mask_applied_path or not self.smart_mask_original_result_path:
                return
            
            # Toggle the state
            self.smart_mask_showing_masked = not self.smart_mask_showing_masked
            
            # Display the appropriate image
            if self.smart_mask_showing_masked:
                display_path = self.smart_mask_applied_path
                self.smart_mask_toggle_btn.config(text="👁️ Show Original")
                logger.info("Showing smart masked result")
            else:
                display_path = self.smart_mask_original_result_path
                self.smart_mask_toggle_btn.config(text="👁️ Show Masked")
                logger.info("Showing original AI result")
            
            # Display in result panel
            self.layout.display_image_in_panel(display_path, 'result')
            
            # Update result path reference
            if hasattr(self.layout, 'results_manager'):
                self.layout.results_manager.result_image_path = display_path
            elif hasattr(self.layout, 'result_image_path'):
                self.layout.result_image_path = display_path
            
        except Exception as e:
            logger.error(f"Error toggling smart mask view: {e}")
    
    def show_smart_mask_controls(self):
        """Show smart mask dialog with preview and controls"""
        try:
            # Get source and result paths
            source_path = None
            result_path = None
            
            # Try multiple ways to get the source image path
            if hasattr(self.layout, 'image_manager') and hasattr(self.layout.image_manager, 'selected_image_paths'):
                paths = self.layout.image_manager.selected_image_paths
                if paths:
                    source_path = paths[0]
            elif hasattr(self.layout, 'selected_image_path'):
                source_path = self.layout.selected_image_path
            
            # Get result path
            if hasattr(self.layout, 'results_manager') and hasattr(self.layout.results_manager, 'result_image_path'):
                result_path = self.layout.results_manager.result_image_path
            elif hasattr(self.layout, 'result_image_path'):
                result_path = self.layout.result_image_path
            
            # Validate paths
            if not source_path or not os.path.exists(source_path):
                messagebox.showwarning(
                    "No Source Image",
                    "Please load an input image first."
                )
                return
            
            if not result_path or not os.path.exists(result_path):
                messagebox.showwarning(
                    "No Result Image",
                    "Please generate a result image first."
                )
                return
            
            # Import smart mask utility
            from utils.smart_mask import SmartMaskProcessor
            
            # Create dialog
            self._show_smart_mask_dialog(source_path, result_path)
            
        except Exception as e:
            logger.error(f"Error showing smart mask controls: {e}")
            messagebox.showerror("Error", f"Failed to open smart mask: {str(e)}")
    
    def _show_smart_mask_dialog(self, source_path: str, result_path: str):
        """Show smart mask dialog with controls"""
        try:
            from utils.smart_mask import SmartMaskProcessor
            
            # Create processor
            processor = SmartMaskProcessor()
            
            # Create dialog window
            dialog = tk.Toplevel(self.layout.parent_frame)
            dialog.title("🎯 Smart Mask - Selective Compositing")
            dialog.geometry("750x850")  # Increased height to fit all controls
            dialog.transient(self.layout.parent_frame.winfo_toplevel())
            dialog.grab_set()
            
            # Instructions
            instructions = ttk.Label(
                dialog,
                text="Preserves background/face by only applying AI changes to modified areas (red preview).\nAdjust settings and click Apply to composite.",
                font=('Arial', 9),
                justify=tk.CENTER
            )
            instructions.pack(pady=10, padx=10)
            
            # Preview canvas
            preview_frame = ttk.LabelFrame(dialog, text="Mask Preview (Red = AI Changes Applied)", padding="5")
            preview_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
            
            preview_canvas = tk.Canvas(preview_frame, bg='gray', width=720, height=450)
            preview_canvas.pack(fill=tk.BOTH, expand=True)
            
            # Store preview image reference
            preview_photo = [None]  # Use list to allow modification in nested function
            
            # Controls frame
            controls_frame = ttk.LabelFrame(dialog, text="Mask Settings", padding="10")
            controls_frame.pack(fill=tk.X, padx=10, pady=5)
            
            # Threshold control (fine-tuned for 0-20% sweet spot with Auto button)
            threshold_frame = ttk.Frame(controls_frame)
            threshold_frame.pack(fill=tk.X, pady=5)
            
            ttk.Label(threshold_frame, text="Threshold:").pack(side=tk.LEFT, padx=(0, 5))
            
            # Auto-calculate button (command will be set after function definition)
            auto_threshold_btn = ttk.Button(
                threshold_frame,
                text="🔮 Auto",
                width=8
            )
            auto_threshold_btn.pack(side=tk.LEFT, padx=(0, 10))
            
            threshold_var = tk.DoubleVar(value=8.0)
            threshold_slider = tk.Scale(
                threshold_frame,
                from_=0.0,
                to=20.0,
                resolution=0.1,
                orient=tk.HORIZONTAL,
                variable=threshold_var,
                length=220,
                showvalue=1,
                digits=3  # Show decimal places
            )
            threshold_slider.pack(side=tk.LEFT, padx=5)
            
            threshold_value_label = ttk.Label(threshold_frame, text=f"{threshold_var.get():.1f}%", width=6)
            threshold_value_label.pack(side=tk.LEFT, padx=(5, 0))
            
            # Update label when slider changes
            def update_threshold_label(*args):
                threshold_value_label.config(text=f"{threshold_var.get():.1f}%")
            threshold_var.trace('w', update_threshold_label)
            
            # Feather control (reduced default to minimize ghost artifacts with Auto button)
            feather_frame = ttk.Frame(controls_frame)
            feather_frame.pack(fill=tk.X, pady=5)
            
            ttk.Label(feather_frame, text="Feather:").pack(side=tk.LEFT, padx=(0, 5))
            
            # Auto-calculate button (command will be set after function definition)
            auto_feather_btn = ttk.Button(
                feather_frame,
                text="🔮 Auto",
                width=8
            )
            auto_feather_btn.pack(side=tk.LEFT, padx=(0, 10))
            
            feather_var = tk.IntVar(value=3)
            feather_slider = tk.Scale(
                feather_frame,
                from_=0,
                to=50,
                resolution=1,
                orient=tk.HORIZONTAL,
                variable=feather_var,
                length=220,
                showvalue=1
            )
            feather_slider.pack(side=tk.LEFT, padx=5)
            
            feather_value_label = ttk.Label(feather_frame, text=f"{feather_var.get()}px", width=6)
            feather_value_label.pack(side=tk.LEFT, padx=(5, 0))
            
            # Update label when slider changes
            def update_feather_label(*args):
                feather_value_label.config(text=f"{feather_var.get()}px")
            feather_var.trace('w', update_feather_label)
            
            # Focus on primary region checkbox
            focus_frame = ttk.Frame(controls_frame)
            focus_frame.pack(fill=tk.X, pady=5)
            
            focus_primary_var = tk.BooleanVar(value=True)
            focus_check = ttk.Checkbutton(
                focus_frame,
                text="🎯 Focus on Primary Region (isolate main clothing change, filter artifacts)",
                variable=focus_primary_var
            )
            focus_check.pack(side=tk.LEFT, padx=(0, 5))
            
            ttk.Label(
                focus_frame, 
                text="← Recommended for clothing transformations",
                font=('Arial', 8),
                foreground='gray'
            ).pack(side=tk.LEFT)
            
            # Face exclusion checkbox (NEW - prevents facial changes)
            face_frame = ttk.Frame(controls_frame)
            face_frame.pack(fill=tk.X, pady=5)
            
            exclude_faces_var = tk.BooleanVar(value=True)
            face_check = ttk.Checkbutton(
                face_frame,
                text="😊 Protect Inner Face (auto-detect core facial features)",
                variable=exclude_faces_var
            )
            face_check.pack(side=tk.LEFT, padx=(0, 5))
            
            ttk.Label(
                face_frame,
                text="← Allows clothes on hair/neck",
                font=('Arial', 8),
                foreground='gray'
            ).pack(side=tk.LEFT)
            
            # Inverted blend checkbox (EXPERIMENTAL - test different feathering direction)
            blend_frame = ttk.Frame(controls_frame)
            blend_frame.pack(fill=tk.X, pady=5)
            
            invert_blend_var = tk.BooleanVar(value=False)
            blend_check = ttk.Checkbutton(
                blend_frame,
                text="🎨 Reduce Ghosting (favor original in blend zones)",
                variable=invert_blend_var
            )
            blend_check.pack(side=tk.LEFT, padx=(0, 5))
            
            ttk.Label(
                blend_frame,
                text="← Try if old clothes bleeding through",
                font=('Arial', 8),
                foreground='orange'
            ).pack(side=tk.LEFT)
            
            # Loading indicator
            loading_text = [None]  # Store text ID
            
            # Auto-calculate threshold function
            def calculate_adaptive_threshold():
                """Calculate and set adaptive threshold from difference image"""
                try:
                    # Disable button during calculation
                    auto_threshold_btn.config(state='disabled', text="⏳ Calculating...")
                    dialog.update()
                    
                    # Load images and calculate difference
                    from PIL import Image
                    import numpy as np
                    
                    original = Image.open(source_path).convert('RGB')
                    result = Image.open(result_path).convert('RGB')
                    
                    # Ensure same size
                    if original.size != result.size:
                        result = result.resize(original.size, Image.Resampling.LANCZOS)
                    
                    # Calculate difference array
                    orig_array = np.array(original, dtype=np.float32)
                    result_array = np.array(result, dtype=np.float32)
                    diff = np.abs(orig_array - result_array)
                    gray_diff = np.mean(diff, axis=2)
                    normalized_diff = (gray_diff / 255.0) * 100  # Percentage
                    
                    # Use processor's adaptive threshold method
                    recommended_threshold = processor.calculate_adaptive_threshold(normalized_diff)
                    
                    # Set the threshold
                    threshold_var.set(recommended_threshold)
                    
                    # Trigger preview update
                    update_preview()
                    
                    logger.info(f"Adaptive threshold set to {recommended_threshold:.1f}%")
                    
                except Exception as e:
                    logger.error(f"Error calculating adaptive threshold: {e}")
                finally:
                    auto_threshold_btn.config(state='normal', text="🔮 Auto")
            
            # Auto-calculate feather function
            def calculate_smart_feather():
                """Calculate and set smart feather from mask structure"""
                try:
                    # Disable button during calculation
                    auto_feather_btn.config(state='disabled', text="⏳ Calculating...")
                    dialog.update()
                    
                    # Generate current mask to analyze
                    threshold = threshold_var.get()
                    focus_primary = focus_primary_var.get()
                    
                    mask = processor.create_difference_mask(
                        source_path, result_path,
                        threshold=threshold,
                        feather=0,  # No feather for analysis
                        focus_primary=focus_primary
                    )
                    
                    if mask:
                        # Use processor's smart feather method
                        recommended_feather = processor.calculate_smart_feather(mask)
                        
                        # Set the feather
                        feather_var.set(recommended_feather)
                        
                        # Trigger preview update
                        update_preview()
                        
                        logger.info(f"Smart feather set to {recommended_feather}px")
                    else:
                        logger.warning("Could not generate mask for smart feather calculation")
                    
                except Exception as e:
                    logger.error(f"Error calculating smart feather: {e}")
                finally:
                    auto_feather_btn.config(state='normal', text="🔮 Auto")
            
            # Update preview function (async with threading)
            # MUST BE DEFINED BEFORE wiring up commands that reference it
            def update_preview():
                try:
                    # Show loading indicator
                    preview_canvas.delete("all")
                    loading_text[0] = preview_canvas.create_text(
                        360, 225,
                        text="Generating preview...\n(Using full resolution pipeline)",
                        font=('Arial', 10),
                        fill='white'
                    )
                    preview_canvas.update()
                    
                    threshold = threshold_var.get()
                    feather = feather_var.get()
                    focus_primary = focus_primary_var.get()
                    exclude_faces = exclude_faces_var.get()
                    
                    # Run preview generation in thread to avoid freezing
                    def generate_preview():
                        try:
                            from PIL import Image, ImageTk
                            import numpy as np
                            
                            # IMPORTANT: Use SAME pipeline as final processing
                            # Load full resolution images first
                            original_full = Image.open(source_path).convert('RGB')
                            
                            # Generate mask at FULL RESOLUTION
                            mask = processor.create_difference_mask(
                                source_path, result_path,
                                threshold=threshold,
                                feather=0,  # Apply feather after face exclusion
                                focus_primary=focus_primary
                            )
                            
                            if not mask:
                                dialog.after(0, lambda: show_error_preview())
                                return
                            
                            # Apply face exclusion at FULL RESOLUTION (not downsampled!)
                            if exclude_faces:
                                mask = processor.detect_and_exclude_faces(mask, original_full)
                            
                            # Now apply feathering at FULL RESOLUTION
                            if feather > 0:
                                mask = processor._feather_mask(mask, feather)
                            
                            # NOW downsample both for display (but processing was at full res)
                            max_preview_size = 800
                            w, h = original_full.size
                            if max(w, h) > max_preview_size:
                                scale = max_preview_size / max(w, h)
                                new_size = (int(w * scale), int(h * scale))
                                original = original_full.resize(new_size, Image.Resampling.LANCZOS)
                                mask_display = mask.resize(new_size, Image.Resampling.LANCZOS)
                            else:
                                original = original_full
                                mask_display = mask
                            
                            # Create red overlay using display-sized images
                            mask_array = np.array(mask_display)
                            original_array = np.array(original)
                            
                            red_overlay = original_array.copy()
                            mask_normalized = mask_array / 255.0
                            red_overlay[:, :, 0] = np.clip(
                                original_array[:, :, 0] + (255 - original_array[:, :, 0]) * mask_normalized * 0.5,
                                0, 255
                            )
                            
                            preview_img = Image.fromarray(red_overlay.astype(np.uint8))

                            logger.info(f"Preview generated at full resolution, displayed at {original.size}")

                            if preview_img:
                                # Schedule UI update on main thread
                                # Use default arg to capture image (early binding, thread-safe)
                                img = preview_img
                                dialog.after(0, lambda i=img: display_preview(i))
                            else:
                                dialog.after(0, lambda: show_error_preview())
                        except Exception as e:
                            logger.error(f"Error generating preview: {e}")
                            dialog.after(0, lambda: show_error_preview())
                    
                    # Start background thread
                    import threading
                    thread = threading.Thread(target=generate_preview, daemon=True)
                    thread.start()
                    
                except Exception as e:
                    logger.error(f"Error updating preview: {e}")
                    show_error_preview()
            
            def display_preview(preview_img):
                """Display the generated preview on main thread"""
                try:
                    from PIL import Image, ImageTk
                    
                    # Resize to fit canvas
                    canvas_width = preview_canvas.winfo_width()
                    canvas_height = preview_canvas.winfo_height()
                    
                    if canvas_width < 10:  # Canvas not yet sized
                        canvas_width = 660
                        canvas_height = 400
                    
                    # Calculate scaling to fit
                    img_ratio = preview_img.width / preview_img.height
                    canvas_ratio = canvas_width / canvas_height
                    
                    if img_ratio > canvas_ratio:
                        new_width = canvas_width - 10
                        new_height = int(new_width / img_ratio)
                    else:
                        new_height = canvas_height - 10
                        new_width = int(new_height * img_ratio)
                    
                    preview_resized = preview_img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                    preview_photo[0] = ImageTk.PhotoImage(preview_resized)
                    
                    # Clear canvas and display
                    preview_canvas.delete("all")
                    x = (canvas_width - new_width) // 2
                    y = (canvas_height - new_height) // 2
                    preview_canvas.create_image(x, y, anchor=tk.NW, image=preview_photo[0])
                    
                except Exception as e:
                    logger.error(f"Error displaying preview: {e}")
                    show_error_preview()
            
            def show_error_preview():
                """Show error message on canvas"""
                preview_canvas.delete("all")
                preview_canvas.create_text(
                    330, 200,
                    text="Error generating preview",
                    font=('Arial', 12),
                    fill='red'
                )
            
            # Wire up Auto buttons (these will call update_preview internally)
            auto_threshold_btn.config(command=calculate_adaptive_threshold)
            auto_feather_btn.config(command=calculate_smart_feather)
            
            # Add manual Refresh Preview button
            refresh_btn_frame = ttk.Frame(controls_frame)
            refresh_btn_frame.pack(fill=tk.X, pady=10)
            
            refresh_preview_btn = ttk.Button(
                refresh_btn_frame,
                text="🔄 Refresh Preview",
                command=update_preview,
                style='Accent.TButton'  # Make it stand out
            )
            refresh_preview_btn.pack(pady=5)
            
            ttk.Label(
                refresh_btn_frame,
                text="Adjust settings above, then click to update preview",
                font=('Arial', 8),
                foreground='gray'
            ).pack()
            
            # Initial preview
            dialog.after(100, update_preview)
            
            # Buttons frame
            button_frame = ttk.Frame(dialog)
            button_frame.pack(fill=tk.X, padx=10, pady=10)
            
            # Track if processing to prevent multiple clicks
            processing = [False]
            
            def apply_masking():
                try:
                    if processing[0]:
                        return  # Already processing
                    
                    processing[0] = True
                    threshold = threshold_var.get()
                    feather = feather_var.get()
                    focus_primary = focus_primary_var.get()
                    exclude_faces = exclude_faces_var.get()
                    invert_blend = invert_blend_var.get()
                    
                    logger.info(f"Applying smart mask with threshold={threshold}, feather={feather}, focus_primary={focus_primary}, exclude_faces={exclude_faces}, invert_blend={invert_blend}")
                    
                    # Disable buttons during processing
                    for widget in button_frame.winfo_children():
                        if isinstance(widget, ttk.Button):
                            widget.config(state='disabled')
                    
                    # Show processing message
                    status_label = ttk.Label(button_frame, text="⏳ Processing...", foreground='blue')
                    status_label.pack(side=tk.LEFT, padx=10)
                    
                    # Run in background thread
                    def process_mask():
                        try:
                            # Generate mask with all settings
                            mask = processor.create_difference_mask(
                                source_path, result_path,
                                threshold=threshold,
                                feather=0,  # Apply feather after face exclusion
                                focus_primary=focus_primary
                            )
                            
                            if not mask:
                                dialog.after(0, lambda: finish_apply(None, False, "Failed to create mask"))
                                return
                            
                            # Apply face exclusion if enabled
                            if exclude_faces:
                                from PIL import Image
                                original_img = Image.open(source_path)
                                mask = processor.detect_and_exclude_faces(mask, original_img)
                            
                            # Now apply feathering
                            if feather > 0:
                                mask = processor._feather_mask(mask, feather)
                            
                            # Apply composite with the prepared mask
                            result_img = processor.apply_smart_composite(
                                source_path, 
                                result_path,
                                mask=mask,  # Pass the pre-generated mask
                                threshold=None,  # Not needed since we have mask
                                feather=None,
                                focus_primary=None,
                                min_region_size=None,
                                invert_blend=invert_blend  # Apply blend direction setting
                            )
                            
                            if result_img:
                                # Save to WaveSpeed_Results with metadata
                                try:
                                    from datetime import datetime
                                    from pathlib import Path
                                    import json
                                    
                                    # Create results directory
                                    results_dir = Path("WaveSpeed_Results/Seedream_V4")
                                    results_dir.mkdir(parents=True, exist_ok=True)
                                    
                                    # Generate filename
                                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                                    
                                    # Get size from result image
                                    size = f"{result_img.width}x{result_img.height}"
                                    
                                    # Get prompt snippet (first 30 chars of prompt, cleaned)
                                    prompt_text = ""
                                    if hasattr(self.layout, 'prompt_manager') and hasattr(self.layout.prompt_manager, 'get_current_prompt'):
                                        prompt_text = self.layout.prompt_manager.get_current_prompt()
                                    elif hasattr(self.layout, 'prompt_manager') and hasattr(self.layout.prompt_manager, 'prompt_text'):
                                        # Fallback: access text widget directly
                                        try:
                                            prompt_text = self.layout.prompt_manager.prompt_text.get("1.0", "end-1c").strip()
                                        except:
                                            pass
                                    
                                    # Clean prompt for filename
                                    prompt_snippet = "SmartMasked"
                                    if prompt_text:
                                        import re
                                        cleaned = re.sub(r'[^a-zA-Z0-9\s_-]', '', prompt_text[:30])
                                        cleaned = re.sub(r'\s+', '_', cleaned.strip())
                                        if cleaned:
                                            prompt_snippet = cleaned
                                    
                                    filename = f"seedream_v4_{timestamp}_{prompt_snippet}_{size}.png"
                                    save_path = results_dir / filename
                                    
                                    # Save image
                                    result_img.save(str(save_path), quality=95, optimize=True)
                                    logger.info(f"Smart masked result saved: {save_path}")
                                    
                                    # Create metadata
                                    metadata = {
                                        "ai_model": "seedream_v4",
                                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                        "prompt": prompt_text,
                                        "result_path": str(save_path.absolute()),
                                        "result_filename": filename,
                                        "processing_type": "smart_mask",
                                        "smart_mask_settings": {
                                            "threshold": float(threshold),
                                            "feather": int(feather),
                                            "focus_primary": bool(focus_primary),
                                            "exclude_faces": bool(exclude_faces),
                                            "invert_blend": bool(invert_blend)
                                        },
                                        "input_image_path": source_path,
                                        "original_ai_result_path": result_path,
                                        "tab_id": getattr(self.layout.tab_instance, 'tab_id', '1') if hasattr(self.layout, 'tab_instance') else '1'
                                    }
                                    
                                    # Get original settings if available
                                    if hasattr(self.layout, 'settings_manager'):
                                        try:
                                            original_settings = {
                                                "width": self.layout.settings_manager.width_var.get(),
                                                "height": self.layout.settings_manager.height_var.get(),
                                                "seed": self.layout.settings_manager.seed_var.get() if hasattr(self.layout.settings_manager, 'seed_var') else None
                                            }
                                            metadata["original_settings"] = original_settings
                                        except:
                                            pass
                                    
                                    # Save JSON metadata
                                    json_path = save_path.with_suffix('.json')
                                    try:
                                        with open(json_path, 'w', encoding='utf-8') as f:
                                            json.dump(metadata, f, indent=2, ensure_ascii=False)
                                        logger.info(f"Metadata saved: {json_path}")
                                    except Exception as json_error:
                                        logger.error(f"Error saving JSON metadata: {json_error}")

                                    # Update UI on main thread with saved path
                                    # Use default arg to capture path (early binding, thread-safe)
                                    path_str = str(save_path)
                                    dialog.after(0, lambda p=path_str: finish_apply(p, True))

                                except Exception as save_error:
                                    logger.error(f"Error saving smart masked result: {save_error}")
                                    # Fall back to temp file
                                    import tempfile
                                    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='_smart_masked.png')
                                    result_img.save(temp_file.name, quality=95)
                                    temp_file.close()
                                    # Use default arg to capture temp path (early binding, thread-safe)
                                    temp_path = temp_file.name
                                    dialog.after(0, lambda p=temp_path: finish_apply(p, True))
                            else:
                                dialog.after(0, lambda: finish_apply(None, False))

                        except Exception as e:
                            logger.error(f"Error in mask processing thread: {e}")
                            # Use default arg to capture error message (early binding, thread-safe)
                            error_str = str(e)
                            dialog.after(0, lambda err=error_str: finish_apply(None, False, err))
                    
                    def finish_apply(temp_path, success, error_msg=None):
                        """Complete the apply operation on main thread"""
                        try:
                            processing[0] = False
                            status_label.destroy()
                            
                            # Re-enable buttons
                            for widget in button_frame.winfo_children():
                                if isinstance(widget, ttk.Button):
                                    widget.config(state='normal')
                            
                            if success and temp_path:
                                logger.info(f"Smart masked image saved to: {temp_path}")
                                
                                # Store paths for toggle functionality
                                self.smart_mask_applied_path = temp_path
                                self.smart_mask_original_result_path = result_path
                                self.smart_mask_showing_masked = True
                                
                                # Enable toggle button
                                if hasattr(self, 'smart_mask_toggle_btn'):
                                    self.smart_mask_toggle_btn.config(state='normal', text="👁️ Show Original")
                                
                                # Display result in result panel
                                self.layout.display_image_in_panel(temp_path, 'result')
                                
                                # Update result path
                                if hasattr(self.layout, 'results_manager'):
                                    self.layout.results_manager.result_image_path = temp_path
                                elif hasattr(self.layout, 'result_image_path'):
                                    self.layout.result_image_path = temp_path
                                
                                # Refresh recent results panel to show new result
                                try:
                                    # Try to refresh recent results if panel exists
                                    if hasattr(self.layout, 'parent_frame'):
                                        # Get the main app window
                                        main_window = self.layout.parent_frame.winfo_toplevel()
                                        # Trigger a refresh by sending a custom event
                                        main_window.event_generate('<<ResultsChanged>>', when='tail')
                                        logger.info("Triggered recent results refresh event")
                                except Exception as refresh_error:
                                    logger.debug(f"Could not trigger results refresh: {refresh_error}")
                                
                                # Show success message with save location
                                from pathlib import Path
                                saved_filename = Path(temp_path).name
                                message = (
                                    f"✅ Smart mask applied and saved!\n\n"
                                    f"📁 Location: WaveSpeed_Results/Seedream_V4/\n"
                                    f"📄 File: {saved_filename}\n\n"
                                    f"Settings:\n"
                                    f"• Threshold: {threshold:.1f}%\n"
                                    f"• Feather: {feather}px\n"
                                    f"• Focus Primary: {'Yes' if focus_primary else 'No'}\n"
                                    f"• Exclude Faces: {'Yes' if exclude_faces else 'No'}\n"
                                    f"• Blend Direction: {'Inverted' if invert_blend else 'Standard'}\n\n"
                                    f"Use 'Toggle Mask' button to compare before/after.\n"
                                    f"Check Recent Results panel to view again."
                                )
                                messagebox.showinfo("Success", message)
                                dialog.destroy()
                            else:
                                error_text = f"Failed to apply mask: {error_msg}" if error_msg else "Failed to apply smart mask."
                                messagebox.showerror("Error", error_text)
                                
                        except Exception as e:
                            logger.error(f"Error finishing apply: {e}")
                            messagebox.showerror("Error", f"Failed to complete: {str(e)}")
                    
                    # Start background thread
                    import threading
                    thread = threading.Thread(target=process_mask, daemon=True)
                    thread.start()
                    
                except Exception as e:
                    processing[0] = False
                    logger.error(f"Error applying smart mask: {e}")
                    messagebox.showerror("Error", f"Failed to apply mask: {str(e)}")
            
            ttk.Button(
                button_frame,
                text="✅ Apply Smart Mask",
                command=apply_masking,
                width=20
            ).pack(side=tk.LEFT, padx=5)
            
            ttk.Button(
                button_frame,
                text="❌ Cancel",
                command=dialog.destroy,
                width=15
            ).pack(side=tk.LEFT, padx=5)
            
            ttk.Button(
                button_frame,
                text="🔄 Refresh Preview",
                command=update_preview,
                width=18
            ).pack(side=tk.RIGHT, padx=5)
            
        except Exception as e:
            logger.error(f"Error creating smart mask dialog: {e}")
            messagebox.showerror("Error", f"Failed to create dialog: {str(e)}")
    
    def _setup_zoom_listener(self):
        """Setup zoom change listener to refresh overlay when zoom changes"""
        try:
            if hasattr(self.layout, 'zoom_var'):
                # Add trace to zoom_var to detect changes
                self.layout.zoom_var.trace_add('write', self._on_zoom_changed)
                logger.debug("Zoom change listener set up for overlay refresh")
        except Exception as e:
            logger.error(f"Error setting up zoom listener: {e}")
    
    def _on_zoom_changed(self, *args):
        """Handle zoom changes - refresh overlay if in overlay mode"""
        try:
            # Only refresh if we're in overlay mode
            if self.current_mode != "overlay":
                return
            
            # Cancel previous timer if exists
            if self.zoom_update_timer:
                try:
                    self.layout.parent_frame.after_cancel(self.zoom_update_timer)
                except:
                    pass
            
            # Schedule overlay refresh with debouncing
            self.zoom_update_timer = self.layout.parent_frame.after(
                self.zoom_update_delay,
                self._refresh_overlay_from_zoom
            )
        except Exception as e:
            logger.error(f"Error handling zoom change in overlay: {e}")
    
    def _refresh_overlay_from_zoom(self):
        """Refresh overlay with new zoom level (debounced)"""
        try:
            if self.current_mode != "overlay":
                return
            
            # Get image paths
            original_path = None
            result_path = None
            
            if hasattr(self.layout, 'image_manager') and hasattr(self.layout.image_manager, 'selected_image_paths'):
                paths = self.layout.image_manager.selected_image_paths
                if paths and len(paths) > 0:
                    original_path = paths[0]
            
            if hasattr(self.layout, 'results_manager') and hasattr(self.layout.results_manager, 'result_image_path'):
                result_path = self.layout.results_manager.result_image_path
            elif hasattr(self.layout, 'result_image_path'):
                result_path = self.layout.result_image_path
            
            # Refresh overlay with current opacity and new zoom
            if original_path and result_path and hasattr(self.layout, 'image_manager'):
                self.layout.image_manager.display_overlay_view(
                    self.layout.original_canvas,
                    original_path,
                    result_path,
                    self.layout.zoom_var,
                    opacity=self.overlay_opacity
                )
                logger.debug(f"Refreshed overlay with new zoom: {self.layout.zoom_var.get()}")
        except Exception as e:
            logger.error(f"Error refreshing overlay from zoom change: {e}")
    
    def get_current_mode(self) -> str:
        """Get current comparison mode"""
        return self.current_mode
    
    def get_opacity(self) -> float:
        """Get current overlay opacity"""
        return self.overlay_opacity
    
    def _on_mode_dropdown_change(self, event=None):
        """Handle view mode dropdown selection change"""
        try:
            selected_display = self.mode_dropdown.get()
            # Convert display name to internal value
            mode = self.mode_display_to_value.get(selected_display)
            if mode:
                self.set_mode(mode)
        except Exception as e:
            logger.error(f"Error handling mode dropdown change: {e}")
    
    def _on_sync_zoom_changed(self):
        """Handle sync zoom checkbox change"""
        is_synced = self.layout.sync_zoom_var.get()
        logger.info(f"Sync zoom {'enabled' if is_synced else 'disabled'}")
        # The sync manager reads directly from sync_zoom_var, no method call needed
    
    def _on_sync_drag_changed(self):
        """Handle sync drag checkbox change"""
        is_synced = self.layout.sync_drag_var.get()
        logger.info(f"Sync drag {'enabled' if is_synced else 'disabled'}")
        # The sync manager reads directly from sync_drag_var, no method call needed
    
    def _slider_to_zoom(self, slider_value: float) -> str:
        """
        Convert slider position (0-100) to zoom percentage using non-linear scale.
        
        Scale breakdown:
        - 0-25: Fit to 25% (tight range for small zooms)
        - 25-50: 25% to 100% (medium zooms) - middle is 100%
        - 50-100: 150% to 300% (large zooms)
        
        Args:
            slider_value: Slider position (0-100)
            
        Returns:
            Zoom string like "Fit", "50%", "100%", etc.
        """
        if slider_value <= 3:
            return "Fit"
        elif slider_value <= 25:
            # Map 3-25 to 10%-25%
            percent = int(10 + ((slider_value - 3) / 22) * 15)
            # Snap to 5% increments
            percent = round(percent / 5) * 5
            return f"{percent}%"
        elif slider_value <= 50:
            # Map 25-50 to 25%-100% (middle point = 100%)
            percent = int(25 + ((slider_value - 25) / 25) * 75)
            # Snap to 10% increments
            percent = round(percent / 10) * 10
            return f"{percent}%"
        else:
            # Map 50-100 to 150%-300%
            percent = int(150 + ((slider_value - 50) / 50) * 150)
            # Snap to 25% increments for large zooms
            percent = round(percent / 25) * 25
            return f"{percent}%"
    
    def _zoom_to_slider(self, zoom_str: str) -> int:
        """
        Convert zoom percentage to slider position (reverse mapping).
        
        Args:
            zoom_str: Zoom string like "Fit", "50%", "100%"
            
        Returns:
            Slider position (0-100)
        """
        if zoom_str == "Fit":
            return 0
        
        try:
            # Extract percentage value
            percent = int(zoom_str.rstrip('%'))
            
            if percent <= 25:
                # Map 10%-25% to 3-25
                return int(3 + ((percent - 10) / 15) * 22)
            elif percent <= 100:
                # Map 25%-100% to 25-50
                return int(25 + ((percent - 25) / 75) * 25)
            else:
                # Map 150%-300% to 50-100
                return int(50 + ((percent - 150) / 150) * 50)
        except:
            return 50  # Default to middle (100%)
    
    def _on_zoom_slider_changed(self, slider_value):
        """Handle zoom slider change"""
        try:
            # Convert to int for mapping
            slider_value = float(slider_value)
            self._set_zoom_from_slider(slider_value)
        except Exception as e:
            logger.error(f"Error handling zoom slider: {e}")
    
    def _set_zoom_from_slider(self, slider_value: float):
        """Set zoom level from slider position"""
        try:
            # Convert slider position to zoom string
            zoom_str = self._slider_to_zoom(slider_value)
            
            # Update zoom variable and label
            self.layout.zoom_var.set(zoom_str)
            self.zoom_label.config(text=zoom_str)
            
            # Apply zoom
            self._apply_zoom_change(zoom_str)
            
        except Exception as e:
            logger.error(f"Error setting zoom from slider: {e}")
    
    def _apply_zoom_change(self, zoom_level: str):
        """Apply zoom change to canvases"""
        logger.info(f"Zoom changed to: {zoom_level}")
        
        # Apply zoom to both canvases via image manager
        if hasattr(self.layout, 'image_manager'):
            try:
                # Refresh original image display with new zoom level
                if hasattr(self.layout.image_manager, 'selected_image_paths'):
                    paths = self.layout.image_manager.selected_image_paths
                    if paths and len(paths) > 0:
                        self.layout.image_manager.display_image_in_panel(
                            paths[0], 
                            'original',
                            self.layout.original_canvas,
                            self.layout.zoom_var
                        )
                
                # Refresh result image if available (check results_manager)
                result_path = None
                if hasattr(self.layout, 'results_manager') and hasattr(self.layout.results_manager, 'result_image_path'):
                    result_path = self.layout.results_manager.result_image_path
                elif hasattr(self.layout, 'result_image_path'):
                    result_path = self.layout.result_image_path
                
                if result_path:
                    self.layout.image_manager.display_image_in_panel(
                        result_path,
                        'result',
                        self.layout.result_canvas,
                        self.layout.zoom_var
                    )
            except Exception as e:
                logger.error(f"Error applying zoom change: {e}")
    
    def _show_color_match_comparison(self):
        """Show before/after comparison for color matching"""
        try:
            logger.debug(f"Starting color match comparison display")
            
            # Load original result on left (original panel)
            if hasattr(self.layout, 'display_image_in_panel'):
                logger.debug(f"Displaying images: original={self.original_result_path}, matched={self.color_matched_path}")
                self.layout.display_image_in_panel(self.original_result_path, 'original')
                self.layout.display_image_in_panel(self.color_matched_path, 'result')
            
            # Switch to side-by-side mode for comparison
            logger.debug("Switching to side-by-side mode")
            self.mode_var.set("side_by_side")
            self._apply_mode()
            
            # Show accept/revert buttons
            logger.debug("Showing color match buttons")
            self._show_color_match_buttons()
            
            logger.info("✅ Color match comparison displayed successfully")
        except Exception as e:
            logger.error(f"Error showing color match comparison: {e}", exc_info=True)
    
    def _show_color_match_buttons(self):
        """Show accept/revert buttons for color matching"""
        try:
            logger.debug("_show_color_match_buttons called")
            
            # Remove existing buttons if present
            if self.color_match_buttons_frame and self.color_match_buttons_frame.winfo_exists():
                logger.debug("Destroying existing color match buttons frame")
                self.color_match_buttons_frame.destroy()
            
            # Create button frame in the controls frame
            if not hasattr(self, 'controls_frame'):
                logger.error("controls_frame attribute not found on ComparisonController")
                return
            
            if not self.controls_frame.winfo_exists():
                logger.error("controls_frame widget no longer exists")
                return
            
            logger.debug(f"Creating color match buttons frame in controls_frame")
            self.color_match_buttons_frame = ttk.Frame(self.controls_frame)
            self.color_match_buttons_frame.pack(side=tk.LEFT, padx=(20, 0))
            
            # Info label
            ttk.Label(
                self.color_match_buttons_frame,
                text="🎨 Color Match:",
                foreground="blue",
                font=("Arial", 9, "bold")
            ).pack(side=tk.LEFT, padx=(0, 5))
            
            # Accept button
            ttk.Button(
                self.color_match_buttons_frame,
                text="✅ Accept",
                command=self._accept_color_match,
                width=10
            ).pack(side=tk.LEFT, padx=2)
            
            # Revert button
            ttk.Button(
                self.color_match_buttons_frame,
                text="↩️ Revert",
                command=self._revert_color_match,
                width=10
            ).pack(side=tk.LEFT, padx=2)
            
            # Toggle view button (switch between overlay/side-by-side)
            ttk.Button(
                self.color_match_buttons_frame,
                text="🔄 Toggle View",
                command=self._toggle_color_match_view,
                width=12
            ).pack(side=tk.LEFT, padx=2)
            
            logger.info("✅ Color match buttons created and displayed successfully")
        except Exception as e:
            logger.error(f"Error showing color match buttons: {e}", exc_info=True)
    
    def _toggle_color_match_view(self):
        """Toggle between overlay and side-by-side for color match comparison"""
        try:
            if self.current_mode == "side_by_side":
                self.mode_var.set("overlay")
                self.opacity_var.set(0.5)
            else:
                self.mode_var.set("side_by_side")
            
            self._apply_mode()
            logger.debug(f"Color match view toggled to {self.current_mode}")
        except Exception as e:
            logger.error(f"Error toggling color match view: {e}")
    
    def _accept_color_match(self):
        """Accept the color matched result"""
        try:
            # Update result path to color-matched version
            self.layout.result_image_path = self.color_matched_path
            if hasattr(self.layout, 'results_manager'):
                self.layout.results_manager.result_image_path = self.color_matched_path
            
            # Restore original image to left panel
            if hasattr(self.layout, 'image_manager') and hasattr(self.layout.image_manager, 'selected_image_paths'):
                paths = self.layout.image_manager.selected_image_paths
                if paths and hasattr(self.layout, 'display_image_in_panel'):
                    self.layout.display_image_in_panel(paths[0], 'original')
            
            # Clear color match state
            self._cleanup_color_match()
            
            logger.info("✅ Color matched result accepted")
            messagebox.showinfo(
                "Accepted",
                "Color correction applied!\n\nThe color-matched result is now your active result."
            )
        except Exception as e:
            logger.error(f"Error accepting color match: {e}")
            messagebox.showerror("Error", f"Failed to accept color match: {str(e)}")
    
    def _revert_color_match(self):
        """Revert to original result (before color matching)"""
        try:
            # Restore original result
            self.layout.result_image_path = self.original_result_path
            if hasattr(self.layout, 'results_manager'):
                self.layout.results_manager.result_image_path = self.original_result_path
            
            # Display original result on right
            if hasattr(self.layout, 'display_image_in_panel'):
                self.layout.display_image_in_panel(self.original_result_path, 'result')
            
            # Restore original image to left panel
            if hasattr(self.layout, 'image_manager') and hasattr(self.layout.image_manager, 'selected_image_paths'):
                paths = self.layout.image_manager.selected_image_paths
                if paths and hasattr(self.layout, 'display_image_in_panel'):
                    self.layout.display_image_in_panel(paths[0], 'original')
            
            # Clean up temp file
            if self.color_matched_path and os.path.exists(self.color_matched_path):
                try:
                    os.remove(self.color_matched_path)
                except:
                    pass
            
            # Clear color match state
            self._cleanup_color_match()
            
            logger.info("↩️ Color match reverted")
            messagebox.showinfo(
                "Reverted",
                "Color correction removed.\n\nReturned to original result."
            )
        except Exception as e:
            logger.error(f"Error reverting color match: {e}")
            messagebox.showerror("Error", f"Failed to revert color match: {str(e)}")
    
    def _cleanup_color_match(self):
        """Clean up color match state and UI"""
        try:
            self.color_match_active = False
            self.original_result_path = None
            self.color_matched_path = None
            
            # Remove buttons
            if self.color_match_buttons_frame and self.color_match_buttons_frame.winfo_exists():
                self.color_match_buttons_frame.destroy()
            
            logger.debug("Color match state cleaned up")
        except Exception as e:
            logger.error(f"Error cleaning up color match: {e}")

    def cleanup(self):
        """Clean up resources and cancel pending timers"""
        try:
            logger.debug("Cleaning up ComparisonController")

            # Cancel animation timers
            if hasattr(self, 'animation_timer') and self.animation_timer:
                try:
                    self.layout.parent_frame.after_cancel(self.animation_timer)
                    self.animation_timer = None
                except:
                    pass

            # Cancel opacity update timer
            if hasattr(self, 'opacity_update_timer') and self.opacity_update_timer:
                try:
                    self.layout.parent_frame.after_cancel(self.opacity_update_timer)
                    self.opacity_update_timer = None
                except:
                    pass

            # Cancel zoom update timer
            if hasattr(self, 'zoom_update_timer') and self.zoom_update_timer:
                try:
                    self.layout.parent_frame.after_cancel(self.zoom_update_timer)
                    self.zoom_update_timer = None
                except:
                    pass

            # Clean up color match state
            try:
                self._cleanup_color_match()
            except:
                pass

            logger.debug("ComparisonController cleanup completed")

        except Exception as e:
            logger.error(f"Error during ComparisonController cleanup: {e}")


# Export
__all__ = ['ComparisonController']

