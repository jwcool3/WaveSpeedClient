"""
Seedream Settings Panel Module
Phase 2 of the improved_seedream_layout.py refactoring

This module handles all settings-related functionality including:
- Resolution controls (width/height)
- Seed management
- Aspect ratio locking
- Size presets and multipliers
- Validation logic
- Settings persistence
"""

# Standard library imports
import json
import os
import threading
from typing import Optional, Dict, Any, Tuple, Callable

# Third-party imports
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
# PIL lazy-loaded when needed (saves ~61ms on startup)

# Local application imports
from core.logger import get_logger
from ui.components.seedream.resolution_optimizer import SeedreamResolutionOptimizer

logger = get_logger()

# File lock for settings save/load
_settings_file_lock = threading.Lock()


class SettingsPanelManager:
    """Manages all settings controls and validation for Seedream V4"""
    
    def __init__(self, parent_layout):
        """
        Initialize settings panel manager
        
        Args:
            parent_layout: Reference to the main layout instance
        """
        self.parent_layout = parent_layout
        self.parent_frame = None
        
        # Settings variables
        self.width_var = tk.IntVar(value=1024)
        self.height_var = tk.IntVar(value=1024)
        self.seed_var = tk.StringVar(value="-1")
        self.sync_mode_var = tk.BooleanVar(value=False)
        self.base64_var = tk.BooleanVar(value=False)
        
        # Aspect ratio locking
        self.aspect_lock_var = tk.BooleanVar(value=False)
        self.locked_aspect_ratio = None
        self._updating_size = False  # Flag to prevent recursion
        
        # Size presets - multipliers based on CURRENT generation resolution (not input image)
        self.size_presets = [
            ("1.5x", 1.5),
            ("2x", 2.0),
            ("2.5x", 2.5)
        ]
        
        # Store original image dimensions (for auto-set and reference only, not for multipliers)
        self.original_image_width = None
        self.original_image_height = None
        
        # Resolution optimizer
        self.resolution_optimizer = SeedreamResolutionOptimizer()
        self.resolution_info_frame = None
        self.input_resolution_label = None
        self.output_resolution_label = None
        self.resolution_warning_label = None
        self.optimize_button = None
        
        # UI references
        self.settings_frame = None
        self.width_scale = None
        self.height_scale = None
        self.lock_aspect_btn = None
        self.width_entry = None
        self.height_entry = None

        # Settings persistence (tab-specific to avoid conflicts between Tab #1 and #2)
        tab_id = getattr(parent_layout.tab_instance, 'tab_id', '1') if hasattr(parent_layout, 'tab_instance') else '1'
        self.settings_file = f"data/seedream_settings_tab{tab_id}.json"
        self._save_timer = None  # Debounce timer for auto-save
        self._loading_settings = False  # Flag to prevent auto-save during load

        logger.debug(f"SettingsPanelManager using settings file: {self.settings_file}")
        
        # Entry change debouncing
        self._entry_update_id = None  # Debounce timer for entry changes
        
        # Validation callbacks
        self.validation_callbacks = []
        
        logger.info("SettingsPanelManager initialized")
    
    def setup_settings_panel(self, parent_frame: tk.Widget) -> None:
        """Setup the settings panel UI"""
        self.parent_frame = parent_frame
        
        try:
            logger.info("Setting up settings panel")
            
            # Main settings frame - optimized padding and layout
            self.settings_frame = ttk.LabelFrame(
                parent_frame,
                text="⚙️ Generation Settings",
                padding="6"
            )
            self.settings_frame.grid(row=1, column=0, sticky="nsew", pady=(0, 4))
            # Configure grid to use all available space
            self.settings_frame.columnconfigure(1, weight=1)  # Let sliders expand
            self.settings_frame.rowconfigure(99, weight=1)  # Push content up, let bottom expand
            
            # Setup components
            self._setup_resolution_controls()
            self._setup_resolution_analyzer()  # NEW: Resolution analysis display
            self._setup_size_presets()
            self._setup_options_row()
            self._setup_advanced_options()
            
            # Bind change events
            self._bind_change_events()
            
            # Load saved settings
            self.load_settings()
            
            logger.info("Settings panel setup complete")
            
        except Exception as e:
            logger.error(f"Error setting up settings panel: {e}")
            raise
    
    def _setup_resolution_controls(self) -> None:
        """Setup resolution width/height controls"""
        # Row 0: Width controls - compact and optimized
        ttk.Label(self.settings_frame, text="W:", font=('Arial', 8, 'bold')).grid(
            row=0, column=0, sticky="w", pady=(0, 2), padx=(0, 2)
        )
        
        # Width scale (256-4096) - expanded to use available space
        self.width_scale = tk.Scale(
            self.settings_frame,
            from_=256,
            to=4096,
            orient=tk.HORIZONTAL,
            variable=self.width_var,
            length=200,  # Wider for better control
            font=('Arial', 8),
            command=self._on_width_changed,
            showvalue=False  # Hide default value display
        )
        self.width_scale.grid(row=0, column=1, sticky="ew", pady=(0, 2))
        
        # Width entry - compact
        self.width_entry = ttk.Entry(
            self.settings_frame,
            textvariable=self.width_var,
            width=5,
            font=('Arial', 8),
            justify='center'
        )
        self.width_entry.grid(row=0, column=2, sticky="w", padx=(4, 0), pady=(0, 2))
        
        # Row 1: Height controls - compact and optimized
        ttk.Label(self.settings_frame, text="H:", font=('Arial', 8, 'bold')).grid(
            row=1, column=0, sticky="w", pady=(0, 2), padx=(0, 2)
        )
        
        # Height scale (256-4096) - expanded to use available space
        self.height_scale = tk.Scale(
            self.settings_frame,
            from_=256,
            to=4096,
            orient=tk.HORIZONTAL,
            variable=self.height_var,
            length=200,  # Wider for better control
            font=('Arial', 8),
            command=self._on_height_changed,
            showvalue=False  # Hide default value display
        )
        self.height_scale.grid(row=1, column=1, sticky="ew", pady=(0, 2))
        
        # Height entry - compact
        self.height_entry = ttk.Entry(
            self.settings_frame,
            textvariable=self.height_var,
            width=5,
            font=('Arial', 8),
            justify='center'
        )
        self.height_entry.grid(row=1, column=2, sticky="w", padx=(4, 0), pady=(0, 2))
    
    def _setup_resolution_analyzer(self) -> None:
        """Setup resolution analysis and optimization UI"""
        try:
            # Resolution info frame - compact padding (placed at row 2, before size presets)
            self.resolution_info_frame = ttk.LabelFrame(
                self.settings_frame,
                text="📊 Resolution Analysis",
                padding="4"
            )
            self.resolution_info_frame.grid(row=3, column=0, columnspan=4, sticky="ew", pady=(8, 0))
            self.resolution_info_frame.columnconfigure(1, weight=1)
            
            # Input image resolution (Row 0)
            ttk.Label(
                self.resolution_info_frame,
                text="Input:",
                font=('Arial', 8, 'bold')
            ).grid(row=0, column=0, sticky="w", padx=(0, 5))
            
            self.input_resolution_label = ttk.Label(
                self.resolution_info_frame,
                text="No image loaded",
                font=('Arial', 8),
                foreground="gray"
            )
            self.input_resolution_label.grid(row=0, column=1, sticky="w")
            
            # Output settings resolution (Row 1)
            ttk.Label(
                self.resolution_info_frame,
                text="Output:",
                font=('Arial', 8, 'bold')
            ).grid(row=1, column=0, sticky="w", padx=(0, 5), pady=(2, 0))
            
            self.output_resolution_label = ttk.Label(
                self.resolution_info_frame,
                text="1024×1024 (1:1, 1.0M pixels)",
                font=('Arial', 8),
                foreground="gray"
            )
            self.output_resolution_label.grid(row=1, column=1, sticky="w", pady=(2, 0))
            
            # Warning/recommendation label (Row 2)
            self.resolution_warning_label = ttk.Label(
                self.resolution_info_frame,
                text="",
                font=('Arial', 8),
                foreground="#ff8c00",  # Orange for warnings
                wraplength=320,  # Wider to prevent excessive wrapping
                justify="left"
            )
            self.resolution_warning_label.grid(row=2, column=0, columnspan=2, sticky="w", pady=(4, 0))
            
            # Optimize button (Row 3)
            button_frame = ttk.Frame(self.resolution_info_frame)
            button_frame.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(4, 0))
            
            self.optimize_button = ttk.Button(
                button_frame,
                text="✨ Optimize Resolution",
                command=self.optimize_resolution,
                state="disabled"  # Enabled when optimization is beneficial
            )
            self.optimize_button.pack(side="left", padx=(0, 5))
            
            # Info button to show all recommended resolutions
            ttk.Button(
                button_frame,
                text="ℹ️ View All",
                command=self.show_resolution_guide,
                width=10
            ).pack(side="left")
            
            logger.debug("Resolution analyzer UI created")
            
        except Exception as e:
            logger.error(f"Error setting up resolution analyzer: {e}")
    
    def _setup_size_presets(self) -> None:
        """Setup size preset buttons"""
        # Row 3: Size presets - more compact
        preset_frame = ttk.Frame(self.settings_frame)
        preset_frame.grid(row=3, column=0, columnspan=3, sticky="ew", pady=(2, 2))
        
        # Preset buttons in a row
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
    
    def _setup_options_row(self) -> None:
        """Setup seed and option controls"""
        # Row 4: Seed + Options - more compact
        ttk.Label(self.settings_frame, text="Seed:", font=('Arial', 8, 'bold')).grid(
            row=4, column=0, sticky="w", pady=(2, 0), padx=(0, 2)
        )
        
        seed_entry = ttk.Entry(
            self.settings_frame,
            textvariable=self.seed_var,
            width=7,
            font=('Arial', 8)
        )
        seed_entry.grid(row=4, column=1, sticky="w", pady=(2, 0))
        
        # Options buttons in compact layout
        btn_frame = ttk.Frame(self.settings_frame)
        btn_frame.grid(row=4, column=2, sticky="e", padx=(2, 0), pady=(2, 0))
        
        # Lock aspect ratio button
        self.lock_aspect_btn = ttk.Button(
            btn_frame,
            text="🔓",
            width=3,
            command=self.toggle_aspect_lock
        )
        self.lock_aspect_btn.pack(side=tk.LEFT, padx=(0, 2))
        
        # Auto-resolution button
        auto_btn = ttk.Button(
            btn_frame,
            text="Auto",
            width=5,
            command=self.auto_set_resolution
        )
        auto_btn.pack(side=tk.LEFT)
    
    def _setup_advanced_options(self) -> None:
        """Setup advanced options (sync mode, base64 output)"""
        # Row 5: Advanced options - more compact
        options_frame = ttk.Frame(self.settings_frame)
        options_frame.grid(row=5, column=0, columnspan=3, sticky="ew", pady=(4, 0))
        
        # Sync mode checkbox
        sync_check = ttk.Checkbutton(
            options_frame,
            text="Sync Mode",
            variable=self.sync_mode_var,
            command=self._on_setting_changed
        )
        sync_check.grid(row=0, column=0, sticky="w")
        
        # Base64 output checkbox
        base64_check = ttk.Checkbutton(
            options_frame,
            text="Base64 Output",
            variable=self.base64_var,
            command=self._on_setting_changed
        )
        base64_check.grid(row=0, column=1, sticky="w", padx=(16, 0))
    
    def _bind_change_events(self) -> None:
        """Bind change events to settings controls"""
        # Bind entry validation
        self.width_entry.bind('<FocusOut>', self._validate_width_entry)
        self.height_entry.bind('<FocusOut>', self._validate_height_entry)
        self.width_entry.bind('<Return>', self._validate_width_entry)
        self.height_entry.bind('<Return>', self._validate_height_entry)
        
        # Register validate command for real-time validation (optional)
        # This provides live validation as the user types
        vcmd = (self.parent_frame.register(self.validate_integer), '%P')
        try:
            self.width_entry.config(validate='key', validatecommand=vcmd)
            self.height_entry.config(validate='key', validatecommand=vcmd)
        except Exception as e:
            logger.warning(f"Could not set validation command: {e}")
        
        # Bind variable traces
        self.seed_var.trace('w', self._on_seed_changed)
    
    def _on_width_changed(self, value: str) -> None:
        """Handle width scale changes"""
        if self._updating_size:
            return
        
        try:
            self._handle_aspect_lock_change('width', int(float(value)))
            self._on_setting_changed()
        except Exception as e:
            logger.error(f"Error handling width change: {e}")
    
    def _on_height_changed(self, value: str) -> None:
        """Handle height scale changes"""
        if self._updating_size:
            return
        
        try:
            self._handle_aspect_lock_change('height', int(float(value)))
            self._on_setting_changed()
        except Exception as e:
            logger.error(f"Error handling height change: {e}")
    
    def _handle_aspect_lock_change(self, changed_dimension: str, new_value: int) -> None:
        """Handle aspect ratio lock when dimensions change"""
        if not self.aspect_lock_var.get() or not self.locked_aspect_ratio:
            return
        
        try:
            self._updating_size = True
            
            if changed_dimension == 'width':
                # Width changed, adjust height
                new_height = int(new_value / self.locked_aspect_ratio)
                clamped_height = max(256, min(4096, new_height))  # Clamp to valid range
                self.height_var.set(clamped_height)
                
                # Update locked ratio if clamping occurred
                if clamped_height != new_height:
                    self.locked_aspect_ratio = new_value / clamped_height
                    logger.debug(f"Aspect ratio updated due to clamping: {self.locked_aspect_ratio:.4f}")
            else:
                # Height changed, adjust width
                new_width = int(new_value * self.locked_aspect_ratio)
                clamped_width = max(256, min(4096, new_width))  # Clamp to valid range
                self.width_var.set(clamped_width)
                
                # Update locked ratio if clamping occurred
                if clamped_width != new_width:
                    self.locked_aspect_ratio = clamped_width / new_value
                    logger.debug(f"Aspect ratio updated due to clamping: {self.locked_aspect_ratio:.4f}")
                
        finally:
            self._updating_size = False
    
    def _validate_width_entry(self, event=None) -> None:
        """Validate width entry field"""
        try:
            value = self.width_entry.get()
            if not value:  # Empty field - show validation error
                logger.warning("Width entry is empty")
                return
            
            width = int(value)
            if 256 <= width <= 4096:
                self.width_var.set(width)
                self._handle_aspect_lock_change('width', width)
            else:
                # Out of range - clamp silently and log
                clamped_width = max(256, min(4096, width))
                logger.warning(f"Width {width} out of range, clamped to {clamped_width}")
                self.width_var.set(clamped_width)
                self.width_entry.delete(0, tk.END)
                self.width_entry.insert(0, str(clamped_width))
        except ValueError:
            logger.error(f"Invalid width value: {value}")
            # Reset to current var value
            self.width_entry.delete(0, tk.END)
            self.width_entry.insert(0, str(self.width_var.get()))
    
    def _validate_height_entry(self, event=None) -> None:
        """Validate height entry field"""
        try:
            value = self.height_entry.get()
            if not value:  # Empty field - show validation error
                logger.warning("Height entry is empty")
                return
            
            height = int(value)
            if 256 <= height <= 4096:
                self.height_var.set(height)
                self._handle_aspect_lock_change('height', height)
            else:
                # Out of range - clamp silently and log
                clamped_height = max(256, min(4096, height))
                logger.warning(f"Height {height} out of range, clamped to {clamped_height}")
                self.height_var.set(clamped_height)
                self.height_entry.delete(0, tk.END)
                self.height_entry.insert(0, str(clamped_height))
        except ValueError:
            logger.error(f"Invalid height value: {value}")
            # Reset to current var value
            self.height_entry.delete(0, tk.END)
            self.height_entry.insert(0, str(self.height_var.get()))
    
    def _on_seed_changed(self, *args) -> None:
        """Handle seed value changes"""
        try:
            seed_value = self.seed_var.get().strip()
            if seed_value and seed_value != "-1":
                # Validate seed is a valid integer
                try:
                    seed_int = int(seed_value)
                    if seed_int < -1 or seed_int > 2147483647:
                        logger.warning(f"Seed {seed_int} out of valid range")
                except ValueError:
                    logger.warning(f"Invalid seed value: {seed_value}")
            
            self._on_setting_changed()
        except Exception as e:
            logger.error(f"Error handling seed change: {e}")
    
    def _on_setting_changed(self) -> None:
        """Called when any setting changes - debounced to prevent excessive file I/O"""
        try:
            # Run validation callbacks immediately
            for callback in self.validation_callbacks:
                try:
                    callback()
                except Exception as e:
                    logger.error(f"Error in validation callback: {e}")
            
            # Don't auto-save if we're loading settings (prevents overwriting ui_preferences)
            if self._loading_settings:
                logger.debug("Skipping auto-save during settings load")
                return
            
            # Cancel previous save timer
            if self._save_timer is not None:
                try:
                    self.parent_frame.after_cancel(self._save_timer)
                except:
                    pass
            
            # Schedule save after 500ms of no changes (debounce)
            self._save_timer = self.parent_frame.after(500, self._do_auto_save)
            
            # Update resolution analysis (immediate feedback)
            self.update_resolution_analysis()
            
        except Exception as e:
            logger.error(f"Error handling setting change: {e}")
    
    def _do_auto_save(self) -> None:
        """Actually save settings (called after debounce delay)"""
        try:
            self.save_settings()
            logger.debug(f"Settings auto-saved: {self.get_current_settings()}")
        except Exception as e:
            logger.error(f"Error auto-saving settings: {e}")
    
    def toggle_aspect_lock(self) -> None:
        """Toggle aspect ratio lock"""
        try:
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
                    if hasattr(self.parent_layout, 'log_message'):
                        self.parent_layout.log_message(
                            f"🔒 Aspect ratio locked: {current_width}:{current_height} "
                            f"(ratio: {self.locked_aspect_ratio:.3f})"
                        )
                else:
                    # Can't lock with zero height
                    self.aspect_lock_var.set(False)
                    if hasattr(self.parent_layout, 'log_message'):
                        self.parent_layout.log_message("❌ Cannot lock aspect ratio with zero height")
            else:
                # Unlocking
                self.locked_aspect_ratio = None
                self.lock_aspect_btn.config(text="🔓", style="")
                if hasattr(self.parent_layout, 'log_message'):
                    self.parent_layout.log_message("🔓 Aspect ratio unlocked")
            
            self._on_setting_changed()
                
        except Exception as e:
            logger.error(f"Error toggling aspect lock: {e}")
            self.aspect_lock_var.set(False)
            self.locked_aspect_ratio = None
    
    def set_size_multiplier(self, multiplier: float) -> None:
        """Set size based on multiplier of CURRENT generation resolution (not original image)"""
        try:
            # Get CURRENT generation resolution settings (not original image!)
            current_width = self.width_var.get()
            current_height = self.height_var.get()
            
            # Validate current settings exist
            if not current_width or not current_height or current_width < 256 or current_height < 256:
                messagebox.showwarning(
                    "Invalid Resolution", 
                    "Please set a valid generation resolution first (or load an image)"
                )
                return
            
            # Calculate new dimensions based on CURRENT generation resolution
            new_width = int(current_width * multiplier)
            new_height = int(current_height * multiplier)
            
            # Clamp to valid ranges
            new_width = max(256, min(4096, new_width))
            new_height = max(256, min(4096, new_height))
            
            # Update both dimensions
            self._updating_size = True
            try:
                self.width_var.set(new_width)
                self.height_var.set(new_height)
            finally:
                self._updating_size = False
            
            # Update aspect ratio if locked
            if self.aspect_lock_var.get():
                self.locked_aspect_ratio = new_width / new_height
            
            if hasattr(self.parent_layout, 'log_message'):
                self.parent_layout.log_message(
                    f"📐 Resolution scaled {multiplier}x: {current_width}×{current_height} → {new_width}×{new_height}"
                )
            
            logger.info(f"Resolution multiplier {multiplier}x: {current_width}×{current_height} → {new_width}×{new_height}")
            self._on_setting_changed()
            
        except Exception as e:
            logger.error(f"Error setting size multiplier: {e}")
            messagebox.showerror("Error", f"Failed to set size multiplier: {str(e)}")
    
    def show_custom_scale_dialog(self) -> None:
        """Show custom scale multiplier dialog based on CURRENT generation resolution"""
        try:
            # Get CURRENT generation resolution settings
            current_width = self.width_var.get()
            current_height = self.height_var.get()
            
            # Validate current settings exist
            if not current_width or not current_height or current_width < 256 or current_height < 256:
                messagebox.showwarning(
                    "Invalid Resolution", 
                    "Please set a valid generation resolution first (or load an image)"
                )
                return
            
            # Get custom multiplier from user
            multiplier_str = simpledialog.askstring(
                "Custom Scale",
                f"Enter scale multiplier for current resolution:\n"
                f"{current_width}×{current_height}\n\n"
                f"(e.g., 1.5 for 1.5x size, 0.5 for half size)",
                initialvalue="2.0"
            )
            
            if multiplier_str:
                try:
                    multiplier = float(multiplier_str)
                    if 0.1 <= multiplier <= 16.0:  # Reasonable range
                        self.set_size_multiplier(multiplier)
                    else:
                        messagebox.showerror(
                            "Invalid Multiplier", 
                            "Multiplier must be between 0.1 and 16.0"
                        )
                except ValueError:
                    messagebox.showerror("Invalid Input", "Please enter a valid number")
                    
        except Exception as e:
            logger.error(f"Error in custom scale dialog: {e}")
            messagebox.showerror("Error", f"Failed to show custom scale dialog: {str(e)}")
    
    def auto_set_resolution(self) -> None:
        """Auto-set resolution based on loaded image"""
        try:
            # Get image path from refactored image_manager
            image_path = None
            if hasattr(self.parent_layout, 'image_manager'):
                if hasattr(self.parent_layout.image_manager, 'selected_image_paths'):
                    paths = self.parent_layout.image_manager.selected_image_paths
                    if paths and len(paths) > 0:
                        image_path = paths[0]  # Use first image
            
            # Fallback: Check old attribute name for backward compatibility
            if not image_path and hasattr(self.parent_layout, 'selected_image_path'):
                image_path = self.parent_layout.selected_image_path
            
            if image_path:
                # Try to get image dimensions
                try:
                    from PIL import Image  # Lazy import
                    with Image.open(image_path) as img:
                        self.original_image_width, self.original_image_height = img.size
                        
                        # Set resolution to image size (clamped to valid range)
                        width = max(256, min(4096, self.original_image_width))
                        height = max(256, min(4096, self.original_image_height))
                        
                        self._updating_size = True
                        try:
                            self.width_var.set(width)
                            self.height_var.set(height)
                        finally:
                            self._updating_size = False
                        
                        # Update aspect ratio if locked
                        if self.aspect_lock_var.get():
                            self.locked_aspect_ratio = width / height
                        
                        if hasattr(self.parent_layout, 'log_message'):
                            self.parent_layout.log_message(
                                f"🎯 Auto-set resolution: {width} x {height}"
                            )
                        
                        self._on_setting_changed()
                        
                except Exception as img_error:
                    logger.error(f"Error reading image dimensions: {img_error}")
                    messagebox.showerror("Error", "Could not read image dimensions")
            else:
                messagebox.showwarning("No Image", "Please load an image first")
                
        except Exception as e:
            logger.error(f"Error in auto_set_resolution: {e}")
            messagebox.showerror("Error", f"Failed to auto-set resolution: {str(e)}")
    
    def update_original_image_dimensions(self, width: int, height: int) -> None:
        """Update stored original image dimensions"""
        try:
            self.original_image_width = width
            self.original_image_height = height
            logger.debug(f"Updated original image dimensions: {width}x{height}")
        except Exception as e:
            logger.error(f"Error updating original image dimensions: {e}")
    
    def get_current_settings(self) -> Dict[str, Any]:
        """Get current settings as dictionary"""
        try:
            # Convert seed from string to int
            seed_str = self.seed_var.get()
            try:
                seed = int(seed_str) if seed_str else -1
            except ValueError:
                logger.warning(f"Invalid seed value '{seed_str}', using -1")
                seed = -1
            
            return {
                'width': self.width_var.get(),
                'height': self.height_var.get(),
                'seed': seed,  # Now properly converted to int
                'sync_mode': self.sync_mode_var.get(),
                'base64_output': self.base64_var.get(),
                'aspect_locked': self.aspect_lock_var.get(),
                'locked_aspect_ratio': self.locked_aspect_ratio
            }
        except Exception as e:
            logger.error(f"Error getting current settings: {e}")
            return {}
    
    def apply_settings(self, settings: Dict[str, Any]) -> None:
        """Apply settings from dictionary"""
        try:
            self._updating_size = True
            try:
                if 'width' in settings:
                    self.width_var.set(settings['width'])
                if 'height' in settings:
                    self.height_var.set(settings['height'])
                if 'seed' in settings:
                    self.seed_var.set(settings['seed'])
                if 'sync_mode' in settings:
                    self.sync_mode_var.set(settings['sync_mode'])
                if 'base64_output' in settings:
                    self.base64_var.set(settings['base64_output'])
                if 'aspect_locked' in settings:
                    self.aspect_lock_var.set(settings['aspect_locked'])
                if 'locked_aspect_ratio' in settings:
                    self.locked_aspect_ratio = settings['locked_aspect_ratio']
                    
                # Update lock button state
                if self.lock_aspect_btn:
                    if self.aspect_lock_var.get():
                        self.lock_aspect_btn.config(text="🔒", style="Accent.TButton")
                    else:
                        self.lock_aspect_btn.config(text="🔓", style="")
                        
            finally:
                self._updating_size = False
                
            logger.debug(f"Applied settings: {settings}")
            
        except Exception as e:
            logger.error(f"Error applying settings: {e}")
    
    def validate_settings(self) -> Tuple[bool, Optional[str]]:
        """Validate current settings"""
        try:
            # Validate width
            width = self.width_var.get()
            if not (256 <= width <= 4096):
                return False, f"Width {width} must be between 256 and 4096"
            
            # Validate height
            height = self.height_var.get()
            if not (256 <= height <= 4096):
                return False, f"Height {height} must be between 256 and 4096"
            
            # Validate seed
            seed_str = self.seed_var.get().strip()
            if seed_str and seed_str != "-1":
                try:
                    seed_int = int(seed_str)
                    if seed_int < -1 or seed_int > 2147483647:
                        return False, f"Seed {seed_int} must be -1 or between 0 and 2147483647"
                except ValueError:
                    return False, f"Seed '{seed_str}' must be a valid integer or -1"
            
            return True, None
            
        except Exception as e:
            logger.error(f"Error validating settings: {e}")
            return False, f"Validation error: {str(e)}"
    
    def save_settings(self, ui_preferences: Dict[str, Any] = None) -> None:
        """
        Save current settings to file (thread-safe)
        
        Args:
            ui_preferences: Optional dict of UI preferences to merge (splitter_position, zoom_level, etc.)
        """
        try:
            settings = self.get_current_settings()
            
            # Merge UI preferences if provided
            if ui_preferences:
                if 'ui_preferences' not in settings:
                    settings['ui_preferences'] = {}
                settings['ui_preferences'].update(ui_preferences)
                logger.info(f"💾 Merging {len(ui_preferences)} UI preferences into settings")
                logger.debug(f"UI preferences keys: {list(ui_preferences.keys())}")
            
            os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)

            # Thread-safe file write (optimized - no verification read)
            with _settings_file_lock:
                with open(self.settings_file, 'w') as f:
                    json.dump(settings, f, indent=2)

            # Log success (no need to read back - write succeeded without exception)
            logger.info(f"✅ Settings saved to {self.settings_file}")
            logger.debug(f"   - Saved keys: {list(settings.keys())}")
            if 'ui_preferences' in settings:
                logger.debug(f"   - UI preferences: {list(settings['ui_preferences'].keys())}")
            
        except Exception as e:
            logger.error(f"Error saving settings: {e}", exc_info=True)
    
    def load_settings(self) -> Dict[str, Any]:
        """
        Load settings from file with validation
        
        Returns:
            Dict containing loaded settings and ui_preferences
        """
        try:
            if os.path.exists(self.settings_file):
                # Thread-safe file read
                with _settings_file_lock:
                    with open(self.settings_file, 'r') as f:
                        settings = json.load(f)
                
                # Validate loaded settings
                if self._validate_loaded_settings(settings):
                    # Set flag to prevent auto-save while loading
                    self._loading_settings = True
                    logger.info("🔒 Auto-save disabled during settings load")
                    try:
                        self.apply_settings(settings)
                        logger.debug(f"Settings loaded from {self.settings_file}")
                    finally:
                        # Always clear flag even if apply_settings fails
                        self._loading_settings = False
                        logger.info("🔓 Auto-save re-enabled after settings load")
                    
                    # Return full settings including UI preferences
                    return settings
                else:
                    logger.warning("Invalid saved settings, using defaults")
            else:
                logger.debug("No saved settings file found, using defaults")
                
        except json.JSONDecodeError as e:
            logger.error(f"Corrupted settings file: {e}, using defaults")
        except Exception as e:
            logger.error(f"Error loading settings: {e}, using defaults")
        
        return {}
    
    def _validate_loaded_settings(self, settings: Dict[str, Any]) -> bool:
        """Validate settings loaded from file"""
        try:
            # Check required keys
            if not isinstance(settings, dict):
                logger.warning("Settings validation failed: not a dictionary")
                return False
            
            # Validate width/height ranges
            width = settings.get('width', 1024)
            height = settings.get('height', 1024)
            
            # Ensure width/height are integers
            try:
                width = int(width)
                height = int(height)
            except (ValueError, TypeError):
                logger.warning(f"Settings validation failed: invalid width/height types ({width}, {height})")
                return False
            
            if not (256 <= width <= 4096 and 256 <= height <= 4096):
                logger.warning(f"Settings validation failed: width/height out of range ({width}, {height})")
                return False
            
            # Validate seed range (can be string or int)
            seed_value = settings.get('seed', '-1')
            if seed_value not in ['-1', -1]:  # Allow both string and int -1
                try:
                    seed_int = int(seed_value)
                    if seed_int < 0 or seed_int > 2147483647:
                        logger.warning(f"Settings validation failed: seed out of range ({seed_int})")
                        return False
                except (ValueError, TypeError):
                    logger.warning(f"Settings validation failed: invalid seed type ({seed_value})")
                    return False
            
            logger.debug("✓ Settings validation passed")
            return True
            
        except Exception as e:
            logger.error(f"Error validating loaded settings: {e}")
            return False
    
    def add_validation_callback(self, callback: Callable) -> None:
        """Add a validation callback that's called when settings change"""
        if callback not in self.validation_callbacks:
            self.validation_callbacks.append(callback)
    
    def update_resolution_analysis(self) -> None:
        """Update the resolution analysis display based on current settings"""
        try:
            # Get current output settings
            width = self.width_var.get()
            height = self.height_var.get()
            
            # Analyze output resolution
            output_analysis = self.resolution_optimizer.analyze_resolution(width, height)
            
            # Update output label
            ratio_display = output_analysis['aspect_ratio']['ratio_display']
            pixels_m = output_analysis['pixels'] / 1_000_000
            tier_name = output_analysis['tier']['name']
            
            output_text = f"{width}×{height} ({ratio_display}, {pixels_m:.2f}M pixels)"
            
            # Color code based on optimization status
            if output_analysis['is_optimal']:
                output_color = "#28a745"  # Green - optimal
                output_text += " ✓"
            elif output_analysis['aspect_ratio']['is_standard']:
                output_color = "#ffc107"  # Yellow - standard aspect but not optimal resolution
            else:
                output_color = "#dc3545"  # Red - non-standard
            
            if self.output_resolution_label:
                self.output_resolution_label.config(text=output_text, foreground=output_color)
            
            # Update input label if image is loaded
            if self.original_image_width and self.original_image_height:
                input_analysis = self.resolution_optimizer.analyze_resolution(
                    self.original_image_width,
                    self.original_image_height
                )
                input_ratio = input_analysis['aspect_ratio']['ratio_display']
                input_pixels_m = input_analysis['pixels'] / 1_000_000
                input_text = f"{self.original_image_width}×{self.original_image_height} ({input_ratio}, {input_pixels_m:.2f}M pixels)"
                
                if self.input_resolution_label:
                    self.input_resolution_label.config(
                        text=input_text,
                        foreground="#28a745" if input_analysis['is_optimal'] else "#666"
                    )
            
            # Update warnings and recommendations
            warnings = output_analysis.get('warnings', [])
            recommendations = output_analysis.get('recommendations', [])
            
            if warnings or recommendations:
                warning_text = ""
                if warnings:
                    warning_text = " • ".join(warnings[:2])  # Show first 2 warnings
                elif recommendations:
                    high_priority = [r for r in recommendations if r.get('priority') == 'high']
                    if high_priority:
                        warning_text = f"💡 {high_priority[0]['reason']}"
                
                if self.resolution_warning_label:
                    self.resolution_warning_label.config(text=warning_text)
            else:
                if self.resolution_warning_label:
                    self.resolution_warning_label.config(text="✓ Optimal resolution")
            
            # Enable/disable optimize button
            if self.optimize_button:
                if not output_analysis['is_optimal'] and output_analysis['nearest_recommended']:
                    self.optimize_button.config(state="normal")
                else:
                    self.optimize_button.config(state="disabled")
            
            logger.debug(f"Resolution analysis updated: {output_text}")
            
        except Exception as e:
            logger.error(f"Error updating resolution analysis: {e}")
    
    def optimize_resolution(self) -> None:
        """Snap to the nearest recommended resolution"""
        try:
            width = self.width_var.get()
            height = self.height_var.get()
            
            # Find nearest recommended
            nearest = self.resolution_optimizer.find_nearest_recommended(width, height)
            
            if not nearest:
                messagebox.showinfo(
                    "Already Optimal",
                    "Current resolution is already optimal or no better recommendation available."
                )
                return
            
            recommended = nearest['recommended']
            adjustment = nearest['adjustment']
            
            # Apply the optimized resolution immediately (no confirmation)
            self.width_var.set(recommended['rounded_w'])
            self.height_var.set(recommended['rounded_h'])
            
            # Update aspect ratio lock if enabled
            if self.aspect_lock_var.get():
                self.locked_aspect_ratio = recommended['rounded_w'] / recommended['rounded_h']
            
            # Update analysis
            self.update_resolution_analysis()
            
            # Trigger validation
            for callback in self.validation_callbacks:
                callback()
            
            # Log the optimization with details
            pixel_change_pct = abs(adjustment['pixel_change_pct'])
            logger.info(
                f"✨ Resolution optimized: {width}×{height} → {recommended['rounded_w']}×{recommended['rounded_h']} "
                f"({recommended['ratio']} {recommended['tier']}, {adjustment['width_diff']:+d}w {adjustment['height_diff']:+d}h, "
                f"{pixel_change_pct:.1f}% {'increase' if adjustment['pixel_diff'] > 0 else 'decrease'})"
            )
            
        except Exception as e:
            logger.error(f"Error optimizing resolution: {e}")
            messagebox.showerror("Error", f"Failed to optimize resolution: {str(e)}")
    
    def show_resolution_guide(self) -> None:
        """Show a guide with all recommended resolutions"""
        try:
            # Create popup window
            guide_window = tk.Toplevel(self.parent_frame)
            guide_window.title("Seedream V4 - Recommended Resolutions")
            guide_window.geometry("650x500")
            guide_window.transient(self.parent_frame)
            
            # Main frame with scrollbar
            main_frame = ttk.Frame(guide_window, padding="10")
            main_frame.pack(fill="both", expand=True)
            
            # Title
            title_label = ttk.Label(
                main_frame,
                text="📊 Seedream V4 Recommended Resolutions",
                font=('Arial', 12, 'bold')
            )
            title_label.pack(pady=(0, 10))
            
            # Info text
            info_text = ttk.Label(
                main_frame,
                text="Choose resolutions that match these recommendations for best quality.",
                font=('Arial', 9),
                foreground="gray"
            )
            info_text.pack(pady=(0, 10))
            
            # Create notebook for different tiers
            notebook = ttk.Notebook(main_frame)
            notebook.pack(fill="both", expand=True)
            
            # Create tabs for each tier
            for tier_name, tier_label in [("2M", "High Quality (2M)"), ("1M", "Good Quality (1M)"), ("100K", "Draft (100K)")]:
                tier_frame = ttk.Frame(notebook, padding="10")
                notebook.add(tier_frame, text=tier_label)
                
                # Create table for this tier
                self._create_resolution_table(tier_frame, tier_name)
            
            # Close button
            close_btn = ttk.Button(
                main_frame,
                text="Close",
                command=guide_window.destroy
            )
            close_btn.pack(pady=(10, 0))
            
            # Center window
            guide_window.update_idletasks()
            x = (guide_window.winfo_screenwidth() // 2) - (guide_window.winfo_width() // 2)
            y = (guide_window.winfo_screenheight() // 2) - (guide_window.winfo_height() // 2)
            guide_window.geometry(f"+{x}+{y}")
            
        except Exception as e:
            logger.error(f"Error showing resolution guide: {e}")
            messagebox.showerror("Error", f"Failed to show resolution guide: {str(e)}")
    
    def _create_resolution_table(self, parent, tier_name):
        """Create a table of resolutions for a specific tier"""
        try:
            # Get resolutions for this tier
            resolutions = self.resolution_optimizer.RECOMMENDED_RESOLUTIONS[tier_name]
            
            # Create headers
            headers = ["Aspect Ratio", "Resolution", "Pixels", "Use"]
            for col, header in enumerate(headers):
                label = ttk.Label(
                    parent,
                    text=header,
                    font=('Arial', 9, 'bold'),
                    relief="solid",
                    borderwidth=1,
                    padding=5
                )
                label.grid(row=0, column=col, sticky="ew", padx=1, pady=1)
            
            # Add resolution rows
            for row, res in enumerate(resolutions, start=1):
                # Aspect ratio
                ttk.Label(
                    parent,
                    text=f"{res['ratio']}",
                    relief="solid",
                    borderwidth=1,
                    padding=5
                ).grid(row=row, column=0, sticky="ew", padx=1, pady=1)
                
                # Resolution
                ttk.Label(
                    parent,
                    text=f"{res['rounded_w']}×{res['rounded_h']}",
                    relief="solid",
                    borderwidth=1,
                    padding=5
                ).grid(row=row, column=1, sticky="ew", padx=1, pady=1)
                
                # Pixels
                pixels_m = res['pixels'] / 1_000_000
                ttk.Label(
                    parent,
                    text=f"{pixels_m:.2f}M",
                    relief="solid",
                    borderwidth=1,
                    padding=5
                ).grid(row=row, column=2, sticky="ew", padx=1, pady=1)
                
                # Use button
                use_btn = ttk.Button(
                    parent,
                    text="Apply",
                    width=8,
                    command=lambda w=res['rounded_w'], h=res['rounded_h']: self._apply_resolution_from_guide(w, h)
                )
                use_btn.grid(row=row, column=3, sticky="ew", padx=3, pady=1)
            
            # Configure column weights
            for col in range(4):
                parent.columnconfigure(col, weight=1)
                
        except Exception as e:
            logger.error(f"Error creating resolution table: {e}")
    
    def _apply_resolution_from_guide(self, width, height):
        """Apply resolution from the guide"""
        try:
            self.width_var.set(width)
            self.height_var.set(height)
            
            # Update aspect ratio lock if enabled
            if self.aspect_lock_var.get():
                self.locked_aspect_ratio = width / height
            
            # Update analysis
            self.update_resolution_analysis()
            
            logger.info(f"Applied resolution from guide: {width}×{height}")
            
        except Exception as e:
            logger.error(f"Error applying resolution from guide: {e}")
    
    def update_original_image_dimensions(self, width: int, height: int) -> None:
        """Update stored original image dimensions and refresh analysis"""
        self.original_image_width = width
        self.original_image_height = height
        self.update_resolution_analysis()
        logger.debug(f"Updated original image dimensions: {width}×{height}")
    
    def cleanup(self) -> None:
        """Cleanup resources and callbacks"""
        try:
            # Cancel any pending save timer
            if self._save_timer is not None:
                try:
                    self.parent_frame.after_cancel(self._save_timer)
                except:
                    pass
                self._save_timer = None
            
            # Clear callbacks to prevent memory leaks
            self.validation_callbacks.clear()
            
            logger.debug("SettingsPanelManager cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    def remove_validation_callback(self, callback: Callable) -> None:
        """Remove a validation callback"""
        if callback in self.validation_callbacks:
            self.validation_callbacks.remove(callback)
    
    def set_size_preset(self, width: int, height: int) -> None:
        """
        Set size preset (legacy method for backward compatibility).
        
        Args:
            width: Width in pixels
            height: Height in pixels
        """
        try:
            # Clamp to valid ranges
            width = max(256, min(4096, width))
            height = max(256, min(4096, height))
            
            self._updating_size = True
            try:
                self.width_var.set(width)
                self.height_var.set(height)
            finally:
                self._updating_size = False
            
            if hasattr(self.parent_layout, 'log_message'):
                self.parent_layout.log_message(f"Size preset set to {width}×{height}")
            
            self._on_setting_changed()
            
        except Exception as e:
            logger.error(f"Error setting size preset: {e}")
    
    def validate_integer(self, value: str) -> bool:
        """
        Validate that the input is a positive integer (allows partial input while typing).
        
        Args:
            value: String value to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        if value == "" or value == "-":
            return True  # Allow empty field or negative sign during typing
        
        try:
            int_value = int(value)
            # Allow any positive integer while typing - range validation happens on FocusOut
            return int_value >= 0  # Just check it's a valid non-negative integer
        except ValueError:
            return False
    
    def reset_to_defaults(self) -> None:
        """Reset all settings to default values"""
        try:
            self._updating_size = True
            try:
                self.width_var.set(1024)
                self.height_var.set(1024)
                self.seed_var.set("-1")
                self.sync_mode_var.set(False)
                self.base64_var.set(False)
                self.aspect_lock_var.set(False)
                self.locked_aspect_ratio = None
                
                if self.lock_aspect_btn:
                    self.lock_aspect_btn.config(text="🔓", style="")
                    
            finally:
                self._updating_size = False
            
            if hasattr(self.parent_layout, 'log_message'):
                self.parent_layout.log_message("🔄 Settings reset to defaults")
            
            self._on_setting_changed()
            
        except Exception as e:
            logger.error(f"Error resetting settings to defaults: {e}")
    
    def get_resolution_string(self) -> str:
        """
        Get resolution as a formatted string.
        
        Returns:
            str: Resolution in format "1024x1024"
        """
        return f"{self.width_var.get()}x{self.height_var.get()}"
    
    def get_aspect_ratio(self) -> float:
        """
        Get current aspect ratio.
        
        Returns:
            float: Aspect ratio (width/height)
        """
        height = self.height_var.get()
        if height > 0:
            return self.width_var.get() / height
        return 1.0
    
    def set_resolution_from_string(self, resolution_str: str) -> bool:
        """
        Set resolution from string format (e.g., "1024x1024").
        
        Args:
            resolution_str: Resolution string in format "WIDTHxHEIGHT"
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            parts = resolution_str.lower().split('x')
            if len(parts) == 2:
                width = int(parts[0])
                height = int(parts[1])
                
                if 256 <= width <= 4096 and 256 <= height <= 4096:
                    self._updating_size = True
                    try:
                        self.width_var.set(width)
                        self.height_var.set(height)
                    finally:
                        self._updating_size = False
                    
                    self._on_setting_changed()
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error setting resolution from string '{resolution_str}': {e}")
            return False
    
    def get_settings_summary(self) -> str:
        """
        Get human-readable summary of current settings.
        
        Returns:
            str: Formatted settings summary
        """
        settings = self.get_current_settings()
        lines = [
            f"Resolution: {settings['width']}×{settings['height']} (ratio: {self.get_aspect_ratio():.2f})",
            f"Seed: {settings['seed']}",
            f"Sync Mode: {'✓' if settings['sync_mode'] else '✗'}",
            f"Base64 Output: {'✓' if settings['base64_output'] else '✗'}",
            f"Aspect Lock: {'🔒 Locked' if settings['aspect_locked'] else '🔓 Unlocked'}"
        ]
        if settings['aspect_locked'] and settings['locked_aspect_ratio']:
            lines.append(f"  └─ Locked Ratio: {settings['locked_aspect_ratio']:.3f}")
        
        if self.original_image_width and self.original_image_height:
            lines.append(f"Reference Image: {self.original_image_width}×{self.original_image_height}")

        return "\n".join(lines)

    def cleanup(self):
        """Clean up resources and cancel pending timers"""
        try:
            logger.debug("Cleaning up SettingsPanelManager")

            # Cancel debounce timers
            if self._save_timer is not None:
                try:
                    self.parent_layout.parent_frame.after_cancel(self._save_timer)
                    self._save_timer = None
                except:
                    pass

            if self._entry_update_id is not None:
                try:
                    self.parent_layout.parent_frame.after_cancel(self._entry_update_id)
                    self._entry_update_id = None
                except:
                    pass

            # Save settings one last time before cleanup
            try:
                self.save_settings()
            except Exception as e:
                logger.error(f"Error saving settings during cleanup: {e}")

            logger.debug("SettingsPanelManager cleanup completed")

        except Exception as e:
            logger.error(f"Error during SettingsPanelManager cleanup: {e}")