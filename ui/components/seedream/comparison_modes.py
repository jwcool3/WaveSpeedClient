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
from tkinter import ttk
from PIL import Image, ImageTk
from typing import Optional, Callable
from core.logger import get_logger

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
        
        # Current mode
        self.current_mode = "side_by_side"  # side_by_side, overlay, original_only, result_only
        
        # Overlay state
        self.overlay_opacity = 0.5
        self.overlay_canvas = None
        self.overlay_image_id = None
        
        # Opacity update debouncing
        self.opacity_update_timer = None
        self.opacity_update_delay = 500  # ms delay for debouncing
        
        # UI references
        self.mode_var = tk.StringVar(value="side_by_side")
        self.opacity_var = tk.DoubleVar(value=0.5)
        
        logger.info("ComparisonController initialized")
    
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
        
        # View mode buttons
        btn_frame = ttk.Frame(controls_frame)
        btn_frame.pack(side=tk.LEFT, padx=5)
        
        ttk.Radiobutton(
            btn_frame,
            text="↔️ Side by Side",
            variable=self.mode_var,
            value="side_by_side",
            command=lambda: self.set_mode("side_by_side")
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Radiobutton(
            btn_frame,
            text="📊 Overlay",
            variable=self.mode_var,
            value="overlay",
            command=lambda: self.set_mode("overlay")
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Radiobutton(
            btn_frame,
            text="📷 Original",
            variable=self.mode_var,
            value="original_only",
            command=lambda: self.set_mode("original_only")
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Radiobutton(
            btn_frame,
            text="✨ Result",
            variable=self.mode_var,
            value="result_only",
            command=lambda: self.set_mode("result_only")
        ).pack(side=tk.LEFT, padx=2)
        
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
        
        # Zoom level dropdown
        zoom_frame = ttk.Frame(controls_frame)
        zoom_frame.pack(side=tk.LEFT, padx=(20, 0))
        
        ttk.Label(zoom_frame, text="Zoom:", font=('Arial', 9)).pack(side=tk.LEFT, padx=(0, 5))
        
        zoom_combo = ttk.Combobox(
            zoom_frame,
            textvariable=self.layout.zoom_var,
            values=["Fit", "50%", "75%", "100%", "125%", "150%", "200%", "300%", "400%"],
            state="readonly",
            width=8,
            font=('Arial', 9)
        )
        zoom_combo.pack(side=tk.LEFT)
        zoom_combo.bind('<<ComboboxSelected>>', self._on_zoom_changed)
        
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
        
        # Swap button
        ttk.Button(
            controls_frame,
            text="🔄 Swap",
            command=self.swap_images,
            width=10
        ).pack(side=tk.RIGHT, padx=2)
        
        logger.info("Comparison controls UI created")
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
    
    def get_current_mode(self) -> str:
        """Get current comparison mode"""
        return self.current_mode
    
    def get_opacity(self) -> float:
        """Get current overlay opacity"""
        return self.overlay_opacity
    
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
    
    def _on_zoom_changed(self, event=None):
        """Handle zoom dropdown change"""
        zoom_level = self.layout.zoom_var.get()
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
                        result_path,  # Use the variable we just set
                        'result',
                        self.layout.result_canvas,
                        self.layout.zoom_var
                    )
            except Exception as e:
                logger.error(f"Error applying zoom change: {e}")


# Export
__all__ = ['ComparisonController']

