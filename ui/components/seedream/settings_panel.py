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

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import os
import threading
from typing import Optional, Dict, Any, Tuple, Callable
from PIL import Image  # Import at module level for efficiency
from core.logger import get_logger

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
        
        # Size presets - multipliers based on input image
        self.size_presets = [
            ("1.5x", 1.5),
            ("2x", 2.0),
            ("2.5x", 2.5)
        ]
        
        # Store original image dimensions for multiplier calculations
        self.original_image_width = None
        self.original_image_height = None
        
        # UI references
        self.settings_frame = None
        self.width_scale = None
        self.height_scale = None
        self.lock_aspect_btn = None
        self.width_entry = None
        self.height_entry = None
        
        # Settings persistence
        self.settings_file = "data/seedream_settings.json"
        self._save_timer = None  # Debounce timer for auto-save
        
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
            
            # Main settings frame
            self.settings_frame = ttk.LabelFrame(
                parent_frame,
                text="⚙️ Generation Settings",
                padding="8"
            )
            self.settings_frame.grid(row=1, column=0, sticky="ew", pady=(0, 8))
            self.settings_frame.columnconfigure(3, weight=1)
            
            # Setup components
            self._setup_resolution_controls()
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
        # Row 0: Width controls
        ttk.Label(self.settings_frame, text="Width:", font=('Arial', 8)).grid(
            row=0, column=0, sticky="w", pady=(0, 4)
        )
        
        # Width scale (256-4096)
        self.width_scale = tk.Scale(
            self.settings_frame,
            from_=256,
            to=4096,
            orient=tk.HORIZONTAL,
            variable=self.width_var,
            length=120,
            font=('Arial', 8),
            command=self._on_width_changed
        )
        self.width_scale.grid(row=0, column=1, sticky="w", pady=(0, 4))
        
        # Width entry
        self.width_entry = ttk.Entry(
            self.settings_frame,
            textvariable=self.width_var,
            width=6,
            font=('Arial', 8)
        )
        self.width_entry.grid(row=0, column=2, sticky="w", padx=(4, 0), pady=(0, 4))
        
        # Row 1: Height controls
        ttk.Label(self.settings_frame, text="Height:", font=('Arial', 8)).grid(
            row=1, column=0, sticky="w", pady=(0, 4)
        )
        
        # Height scale (256-4096)
        self.height_scale = tk.Scale(
            self.settings_frame,
            from_=256,
            to=4096,
            orient=tk.HORIZONTAL,
            variable=self.height_var,
            length=120,
            font=('Arial', 8),
            command=self._on_height_changed
        )
        self.height_scale.grid(row=1, column=1, sticky="w", pady=(0, 4))
        
        # Height entry
        self.height_entry = ttk.Entry(
            self.settings_frame,
            textvariable=self.height_var,
            width=6,
            font=('Arial', 8)
        )
        self.height_entry.grid(row=1, column=2, sticky="w", padx=(4, 0), pady=(0, 4))
    
    def _setup_size_presets(self) -> None:
        """Setup size preset buttons"""
        # Row 2: Size presets
        preset_frame = ttk.Frame(self.settings_frame)
        preset_frame.grid(row=2, column=0, columnspan=4, sticky="ew", pady=(4, 2))
        
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
        # Row 3: Seed + Options
        ttk.Label(self.settings_frame, text="Seed:", font=('Arial', 8)).grid(
            row=3, column=0, sticky="w", pady=(4, 0)
        )
        
        seed_entry = ttk.Entry(
            self.settings_frame,
            textvariable=self.seed_var,
            width=8,
            font=('Arial', 8)
        )
        seed_entry.grid(row=3, column=1, sticky="w", pady=(4, 0))
        
        # Lock aspect ratio button
        self.lock_aspect_btn = ttk.Button(
            self.settings_frame,
            text="🔓",
            width=3,
            command=self.toggle_aspect_lock
        )
        self.lock_aspect_btn.grid(row=3, column=2, sticky="w", padx=(8, 0), pady=(4, 0))
        
        # Auto-resolution button
        auto_btn = ttk.Button(
            self.settings_frame,
            text="Auto",
            width=6,
            command=self.auto_set_resolution
        )
        auto_btn.grid(row=3, column=3, sticky="e", pady=(4, 0))
    
    def _setup_advanced_options(self) -> None:
        """Setup advanced options (sync mode, base64 output)"""
        # Row 4: Advanced options
        options_frame = ttk.Frame(self.settings_frame)
        options_frame.grid(row=4, column=0, columnspan=4, sticky="ew", pady=(8, 0))
        
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
            
            # Cancel previous save timer
            if self._save_timer is not None:
                try:
                    self.parent_frame.after_cancel(self._save_timer)
                except:
                    pass
            
            # Schedule save after 500ms of no changes (debounce)
            self._save_timer = self.parent_frame.after(500, self._do_auto_save)
            
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
        """Set size based on multiplier of original image"""
        try:
            if not self.original_image_width or not self.original_image_height:
                messagebox.showwarning(
                    "No Reference Image", 
                    "Load an image first to use size multipliers"
                )
                return
            
            new_width = int(self.original_image_width * multiplier)
            new_height = int(self.original_image_height * multiplier)
            
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
                    f"📐 Size set to {multiplier}x: {new_width} x {new_height}"
                )
            
            self._on_setting_changed()
            
        except Exception as e:
            logger.error(f"Error setting size multiplier: {e}")
            messagebox.showerror("Error", f"Failed to set size multiplier: {str(e)}")
    
    def show_custom_scale_dialog(self) -> None:
        """Show custom scale multiplier dialog"""
        try:
            if not self.original_image_width or not self.original_image_height:
                messagebox.showwarning(
                    "No Reference Image", 
                    "Load an image first to use custom scaling"
                )
                return
            
            # Get custom multiplier from user
            multiplier_str = simpledialog.askstring(
                "Custom Scale",
                f"Enter scale multiplier for {self.original_image_width}x{self.original_image_height}:\n"
                "(e.g., 1.5 for 1.5x size)",
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
                # Try to get image dimensions (PIL imported at module level)
                try:
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
    
    def save_settings(self) -> None:
        """Save current settings to file (thread-safe)"""
        try:
            settings = self.get_current_settings()
            os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
            
            # Thread-safe file write
            with _settings_file_lock:
                with open(self.settings_file, 'w') as f:
                    json.dump(settings, f, indent=2)
                
            logger.debug(f"Settings saved to {self.settings_file}")
            
        except Exception as e:
            logger.error(f"Error saving settings: {e}")
    
    def load_settings(self) -> None:
        """Load settings from file with validation"""
        try:
            if os.path.exists(self.settings_file):
                # Thread-safe file read
                with _settings_file_lock:
                    with open(self.settings_file, 'r') as f:
                        settings = json.load(f)
                
                # Validate loaded settings
                if self._validate_loaded_settings(settings):
                    self.apply_settings(settings)
                    logger.debug(f"Settings loaded from {self.settings_file}")
                else:
                    logger.warning("Invalid saved settings, using defaults")
            else:
                logger.debug("No saved settings file found, using defaults")
                
        except json.JSONDecodeError as e:
            logger.error(f"Corrupted settings file: {e}, using defaults")
        except Exception as e:
            logger.error(f"Error loading settings: {e}, using defaults")
    
    def _validate_loaded_settings(self, settings: Dict[str, Any]) -> bool:
        """Validate settings loaded from file"""
        try:
            # Check required keys
            if not isinstance(settings, dict):
                return False
            
            # Validate width/height ranges
            width = settings.get('width', 1024)
            height = settings.get('height', 1024)
            if not (256 <= width <= 4096 and 256 <= height <= 4096):
                return False
            
            # Validate seed range
            seed_str = settings.get('seed', '-1')
            if seed_str != '-1':
                try:
                    seed_int = int(seed_str)
                    if seed_int < 0 or seed_int > 2147483647:
                        return False
                except ValueError:
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating loaded settings: {e}")
            return False
    
    def add_validation_callback(self, callback: Callable) -> None:
        """Add a validation callback that's called when settings change"""
        if callback not in self.validation_callbacks:
            self.validation_callbacks.append(callback)
    
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
        Validate that the input is a positive integer within valid range (256-4096).
        
        Args:
            value: String value to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        if value == "" or value == "-":
            return True  # Allow empty field or negative sign during typing
        
        try:
            int_value = int(value)
            return 256 <= int_value <= 4096  # Fixed: Match entry validation range
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