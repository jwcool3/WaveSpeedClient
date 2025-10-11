"""
Comparison Modes Module
Provides advanced comparison features for before/after images

Features:
- Side-by-side view
- Overlay view with opacity control
- Swipe/slider comparison
- Split view
"""

import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from typing import Optional, Callable
import tempfile
import os
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
        
        # Use discrete 10% increments to reduce lag
        # ttk.Scale doesn't support resolution, but we'll snap to 10% in the handler
        opacity_scale = ttk.Scale(
            self.opacity_frame,
            from_=0.0,
            to=1.0,
            orient=tk.HORIZONTAL,
            variable=self.opacity_var,
            command=self._on_opacity_changed,
            length=150
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
            
            # Automatically set zoom to "Fit" for optimal overlay viewing
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
            
            if hasattr(self.layout, 'selected_image_path'):
                source_path = self.layout.selected_image_path
            
            if hasattr(self.layout, 'result_image_path'):
                result_path = self.layout.result_image_path
            
            # Validate paths
            if not source_path or not os.path.exists(source_path):
                messagebox.showwarning(
                    "No Source Image",
                    "Please load an input image first to use as color reference."
                )
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
                
                # Update result path
                self.layout.result_image_path = temp_file.name
                
                # Refresh display
                if hasattr(self.layout.image_manager, 'display_image_in_panel'):
                    self.layout.image_manager.display_image_in_panel(
                        temp_file.name, 'result'
                    )
                
                # If in overlay mode, refresh overlay
                if self.current_mode == "overlay":
                    self._refresh_overlay_from_zoom()
                
                logger.info("✅ Color correction applied successfully")
                messagebox.showinfo(
                    "Success",
                    "Subtle color correction applied!\n\n"
                    "Result colors now match the source image better.\n"
                    "The correction is subtle to preserve the AI's edits."
                )
            else:
                messagebox.showerror("Error", "Failed to apply color matching.")
                
        except Exception as e:
            logger.error(f"Error applying color matching: {e}")
            messagebox.showerror("Error", f"Color matching failed: {str(e)}")
    
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


# Export
__all__ = ['ComparisonController']

