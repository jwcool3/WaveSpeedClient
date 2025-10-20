"""
Enhanced Recent Results Panel Component for WaveSpeed AI Application

Improvements:
- Dynamic grid sizing based on panel width
- Responsive thumbnails that scale with available space
- Click to preview functionality with enlarged view
- Better scrolling and layout management
- Visual selection feedback
"""

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os
import json
import glob
from pathlib import Path
from datetime import datetime
import threading
from core.logger import get_logger
from utils.utils import show_error, show_success
from ui.components.cross_tab_navigator import CrossTabNavigator

logger = get_logger()


class RecentResultsPanel:
    """Enhanced panel for displaying and managing recent AI generation results"""
    
    def __init__(self, parent, main_app):
        self.parent = parent
        self.main_app = main_app
        self.results_data = []
        self.filtered_results = []
        self.current_filter = "All"
        self.selected_result = None
        
        # Dynamic sizing variables (expanded range for more zoom levels)
        self.min_thumbnail_size = 30   # Much smaller - show many at once
        self.max_thumbnail_size = 300  # Much larger - 1-2 images at a time
        self.current_thumbnail_size = 60
        self.min_cols = 1  # Allow single column for large images
        self.max_cols = 8  # Allow more columns for tiny thumbnails
        self.current_cols = 3
        
        self.max_results = 50
        
        # Performance optimization: thumbnail cache
        self._thumbnail_cache = {}  # Cache loaded thumbnails
        self._zoom_debounce_id = None  # For debouncing zoom operations
        
        # Prevent recursion flags
        self._resizing = False
        self._rendering = False
        self._last_width = 0
        
        # No popup window needed - using main display
        
        self.setup_ui()
        
        # Bind resize events
        self.parent.bind('<Configure>', self.on_panel_resize)
        
        # Schedule loading after main loop starts (avoid "main thread not in main loop" error)
        self.parent.after(100, self.load_recent_results)
    
    def setup_ui(self):
        """Setup the enhanced recent results panel UI"""
        # Main panel frame (no padding to fill all space, constrained to window)
        self.panel_frame = ttk.Frame(self.parent, padding="0")
        self.panel_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        
        # Header section (fixed height)
        self.setup_header()
        
        # Filter section (fixed height)
        self.setup_filter_section()
        
        # Scrollable results area (expands to fill remaining space)
        self.setup_scrollable_area()
        
        # Status bar (fixed height at bottom)
        self.setup_status_bar()
    
    def setup_header(self):
        """Setup header with title and controls"""
        header_frame = ttk.Frame(self.panel_frame)
        header_frame.pack(fill=tk.X, padx=(3, 0), pady=(0, 0))  # Left padding only, no right gap
        
        # Title with icon
        title_label = ttk.Label(
            header_frame, 
            text="📂 Recent Results", 
            font=('Arial', 10, 'bold')
        )
        title_label.pack(side=tk.LEFT)
        
        # Control buttons frame
        controls_frame = ttk.Frame(header_frame)
        controls_frame.pack(side=tk.RIGHT)
        
        # Comparison studio button
        ttk.Button(
            controls_frame,
            text="🔍 Compare",
            width=10,
            command=self.open_comparison_studio
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        # Size adjustment buttons
        ttk.Button(
            controls_frame,
            text="🔍+",
            width=3,
            command=self.increase_thumbnail_size
        ).pack(side=tk.LEFT, padx=1)
        
        ttk.Button(
            controls_frame,
            text="🔍-",
            width=3,
            command=self.decrease_thumbnail_size
        ).pack(side=tk.LEFT, padx=1)
        
        # Refresh button
        ttk.Button(
            controls_frame,
            text="🔄",
            width=3,
            command=self.refresh_results
        ).pack(side=tk.LEFT, padx=(2, 0))
    
    def setup_filter_section(self):
        """Setup filter controls"""
        filter_frame = ttk.Frame(self.panel_frame)
        filter_frame.pack(fill=tk.X, padx=(3, 0), pady=(3, 0))  # Left padding only, no right gap
        
        ttk.Label(filter_frame, text="Filter:", font=('Arial', 8)).pack(side=tk.LEFT)
        
        self.filter_var = tk.StringVar(value="All")
        filter_combo = ttk.Combobox(
            filter_frame,
            textvariable=self.filter_var,
            values=["All", "Nano Banana", "SeedEdit", "Seedream V4", "Upscaler", "Wan 2.2", "SeedDance Pro"],
            state="readonly",
            width=12,
            font=('Arial', 7)
        )
        filter_combo.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(5, 0))
        filter_combo.bind('<<ComboboxSelected>>', self.on_filter_changed)
    
    def setup_scrollable_area(self):
        """Setup enhanced scrollable area for results grid with proper height constraint"""
        # Create canvas frame (will constrain to available height)
        canvas_frame = ttk.Frame(self.panel_frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=(0, 0))  # No padding to eliminate gaps
        
        # Canvas and scrollbar (canvas height will be constrained by parent)
        self.canvas = tk.Canvas(canvas_frame, highlightthickness=0, bg='#f8f8f8', height=1)
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        # Configure scrolling
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.update_scroll_region()
        )
        
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas and scrollbar (canvas will expand to fill available space)
        # Canvas on left, scrollbar flush on right edge
        self.canvas.pack(side="left", fill="both", expand=True, padx=0, pady=0)
        scrollbar.pack(side="right", fill="y", padx=0, pady=0)
        
        # Bind events
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind('<Configure>', self.on_canvas_configure)
        
        # Bind mousewheel to scrollable frame as well (so it works when hovering over content)
        self.scrollable_frame.bind("<MouseWheel>", self._on_mousewheel)
        
        # Results grid frame - minimal padding to avoid gap near scrollbar
        self.results_grid = ttk.Frame(self.scrollable_frame)
        self.results_grid.pack(fill=tk.BOTH, expand=True, padx=(3, 0), pady=2)  # Left padding only
        
        # Bind mousewheel to results grid too
        self.results_grid.bind("<MouseWheel>", self._on_mousewheel)
    
    def setup_status_bar(self):
        """Setup status bar at bottom"""
        status_frame = ttk.Frame(self.panel_frame)
        status_frame.pack(fill=tk.X, padx=(3, 0), pady=(0, 3))  # Left padding only, no right gap
        
        # Results count
        self.count_label = ttk.Label(
            status_frame, 
            text="0 results", 
            font=('Arial', 8),
            foreground='#666666'
        )
        self.count_label.pack(side=tk.LEFT)
        
        # Size info
        self.size_label = ttk.Label(
            status_frame,
            text=f"{self.current_thumbnail_size}px",
            font=('Arial', 7),
            foreground='#999999'
        )
        self.size_label.pack(side=tk.RIGHT)
    
    def on_panel_resize(self, event=None):
        """Handle panel resize to adjust grid layout"""
        # Prevent recursive calls
        if self._resizing:
            return
        
        try:
            self._resizing = True
            
            if event and event.widget == self.parent:
                # Only recalculate if width changed significantly
                current_width = self.parent.winfo_width()
                if abs(current_width - self._last_width) > 50:  # Only if changed by 50+ pixels
                    self._last_width = current_width
                    self.calculate_optimal_layout()
                    self.render_results_grid()
        finally:
            self._resizing = False
    
    def on_canvas_configure(self, event):
        """Handle canvas resize"""
        # Prevent recursive calls
        if self._resizing:
            return
        
        try:
            self._resizing = True
            
            # Update scrollable frame width to match canvas
            canvas_width = event.width
            self.canvas.itemconfig(self.canvas_window, width=canvas_width)
            
            # Only recalculate if width changed significantly
            if abs(canvas_width - self._last_width) > 50:  # Only if changed by 50+ pixels
                self._last_width = canvas_width
                self.calculate_optimal_layout()
        finally:
            self._resizing = False
    
    def calculate_optimal_layout(self):
        """Calculate optimal grid layout based on current panel width"""
        try:
            # Get available width
            panel_width = self.canvas.winfo_width()
            if panel_width <= 1:  # Not yet sized
                return
            
            # Calculate optimal number of columns
            # Account for padding and scrollbar
            available_width = panel_width - 20  # Account for padding and scrollbar
            
            # Calculate how many thumbnails can fit
            thumb_width = self.current_thumbnail_size + 10  # Add margin
            if thumb_width > 0:
                optimal_cols = max(self.min_cols, min(self.max_cols, available_width // thumb_width))
            else:
                optimal_cols = self.current_cols
            
            if optimal_cols != self.current_cols:
                self.current_cols = optimal_cols
                self.render_results_grid()
                
        except Exception as e:
            logger.debug(f"Layout calculation error: {e}")
    
    def increase_thumbnail_size(self):
        """Increase thumbnail size (with debouncing for performance)"""
        # Larger steps for faster zooming
        step = 20 if self.current_thumbnail_size < 100 else 30
        new_size = min(self.max_thumbnail_size, self.current_thumbnail_size + step)
        if new_size != self.current_thumbnail_size:
            self.current_thumbnail_size = new_size
            self.size_label.config(text=f"{self.current_thumbnail_size}px")
            self._debounced_zoom_update()
    
    def decrease_thumbnail_size(self):
        """Decrease thumbnail size (with debouncing for performance)"""
        # Larger steps for faster zooming
        step = 20 if self.current_thumbnail_size < 100 else 30
        new_size = max(self.min_thumbnail_size, self.current_thumbnail_size - step)
        if new_size != self.current_thumbnail_size:
            self.current_thumbnail_size = new_size
            self.size_label.config(text=f"{self.current_thumbnail_size}px")
            self._debounced_zoom_update()
    
    def open_comparison_studio(self):
        """Open the result comparison studio"""
        try:
            from ui.components.result_comparison_tool import open_comparison_studio
            
            if not self.loaded_results:
                from tkinter import messagebox
                messagebox.showinfo(
                    "No Results",
                    "No results available to compare.\n\nGenerate some results first!"
                )
                return
            
            # Open comparison studio
            open_comparison_studio(self.parent, self)
            logger.info("Comparison Studio opened from Recent Results panel")
            
        except Exception as e:
            logger.error(f"Error opening comparison studio: {e}")
            from tkinter import messagebox
            messagebox.showerror("Error", f"Failed to open comparison studio: {str(e)}")
    
    def _debounced_zoom_update(self):
        """Debounce zoom updates to prevent lag when clicking multiple times"""
        # Cancel any pending zoom update
        if self._zoom_debounce_id:
            self.parent.after_cancel(self._zoom_debounce_id)
        
        # Schedule new update after 150ms of inactivity
        self._zoom_debounce_id = self.parent.after(300, self._apply_zoom_update)
    
    def _apply_zoom_update(self):
        """Apply the zoom update (called after debounce delay)"""
        self._zoom_debounce_id = None
        # Clear thumbnail cache when size changes
        self._thumbnail_cache.clear()
        self.calculate_optimal_layout()
        self.render_results_grid()
    
    def update_scroll_region(self):
        """Update scroll region"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling"""
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def load_recent_results(self):
        """Load recent results from auto-save directories"""
        def _load_in_background():
            try:
                results = []
                
                # Scan auto-save directories
                from app.config import Config
                base_folder = Config.AUTO_SAVE_FOLDER
                
                if not os.path.exists(base_folder):
                    try:
                        self.parent.after(0, lambda: self.update_results_display([]))
                    except tk.TclError:
                        # Widget destroyed or main loop not running
                        pass
                    return
                
                # Map folders to tab names
                folder_to_tab = {
                    'Nano_Banana_Editor': 'Nano Banana',
                    'SeedEdit': 'SeedEdit',
                    'Seedream_V4': 'Seedream V4',
                    'Image_Upscaler': 'Upscaler',
                    'Wan_2.2': 'Wan 2.2',
                    'SeedDance': 'SeedDance Pro'
                }
                
                for folder_name, tab_name in folder_to_tab.items():
                    folder_path = os.path.join(base_folder, folder_name)
                    if os.path.exists(folder_path):
                        # Find image files
                        for ext in ['*.png', '*.jpg', '*.jpeg', '*.gif', '*.bmp', '*.webp']:
                            for image_path in glob.glob(os.path.join(folder_path, ext)):
                                try:
                                    # Get file info
                                    stat = os.stat(image_path)
                                    mod_time = stat.st_mtime
                                    
                                    # Try to load metadata
                                    metadata = {}
                                    json_path = os.path.splitext(image_path)[0] + ".json"
                                    if os.path.exists(json_path):
                                        try:
                                            with open(json_path, 'r', encoding='utf-8') as f:
                                                metadata = json.load(f)
                                        except:
                                            pass
                                    
                                    # Extract tab_id from metadata (for dual Seedream tabs)
                                    tab_id = metadata.get('tab_id', '1') if metadata else '1'
                                    
                                    # Extract feedback and prompt
                                    feedback = metadata.get('feedback', None) if metadata else None
                                    prompt = metadata.get('prompt', '') if metadata else ''
                                    
                                    result_info = {
                                        'image_path': image_path,
                                        'tab_name': tab_name,
                                        'tab_id': tab_id,
                                        'timestamp': mod_time,
                                        'metadata': metadata,
                                        'filename': os.path.basename(image_path),
                                        'feedback': feedback,
                                        'prompt': prompt
                                    }
                                    results.append(result_info)
                                    
                                except Exception as e:
                                    logger.debug(f"Error processing {image_path}: {e}")
                
                # Sort by timestamp (newest first)
                results.sort(key=lambda x: x['timestamp'], reverse=True)
                
                # Limit to max results
                results = results[:self.max_results]
                
                # Update UI in main thread
                try:
                    self.parent.after(0, lambda: self.update_results_display(results))
                except tk.TclError:
                    # Widget destroyed or main loop not running
                    pass
                
            except Exception as e:
                logger.error(f"Error loading recent results: {e}")
                try:
                    self.parent.after(0, lambda: self.update_results_display([]))
                except tk.TclError:
                    # Widget destroyed or main loop not running
                    pass
        
        # Load in background thread
        threading.Thread(target=_load_in_background, daemon=True).start()
    
    def update_results_display(self, results):
        """Update the results display (must be called from main thread)"""
        try:
            self.results_data = results
            self.apply_filter()
            
        except Exception as e:
            logger.error(f"Error updating results display: {e}")
    
    def apply_filter(self):
        """Apply current filter to results"""
        if self.current_filter == "All":
            self.filtered_results = self.results_data
        else:
            self.filtered_results = [
                result for result in self.results_data 
                if result['tab_name'] == self.current_filter
            ]
        
        self.render_results_grid()
        self.update_count_label()
    
    def render_results_grid(self):
        """Render the enhanced results grid with dynamic sizing"""
        # Prevent recursive/concurrent renders
        if self._rendering:
            return
        
        try:
            self._rendering = True
            
            # Clear existing grid
            for widget in self.results_grid.winfo_children():
                widget.destroy()
            
            if not self.filtered_results:
                # Show empty state
                empty_label = ttk.Label(
                    self.results_grid,
                    text="No recent results found.\nGenerate some images to see them here!",
                    font=('Arial', 9),
                    foreground='#666666',
                    justify=tk.CENTER
                )
                empty_label.pack(pady=20)
                return
            
            # Dynamic grid layout
            for i, result in enumerate(self.filtered_results):
                row = i // self.current_cols
                col = i % self.current_cols
                
                # Create result item frame
                item_frame = tk.Frame(self.results_grid, relief=tk.RAISED, bd=1, bg='white')
                item_frame.grid(row=row, column=col, padx=2, pady=2, sticky="nsew")
                
                # Configure grid weights for responsive layout
                self.results_grid.columnconfigure(col, weight=1)
                
                self.create_enhanced_result_item(item_frame, result)
            
            # Update scroll region after rendering
            self.parent.after(10, self.update_scroll_region)
        finally:
            self._rendering = False
    
    def create_enhanced_result_item(self, parent, result):
        """Create an enhanced result item widget with better interaction"""
        try:
            # Load and resize image thumbnail
            thumbnail = self.load_dynamic_thumbnail(result['image_path'])
            
            # Main clickable area
            main_frame = tk.Frame(parent, bg='white')
            main_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
            
            # Image button (clickable for preview)
            img_button = tk.Button(
                main_frame,
                image=thumbnail,
                relief=tk.FLAT,
                bg='white',
                activebackground='#e3f2fd',
                bd=0,
                command=lambda: self.show_image_preview(result)
            )
            img_button.pack()
            img_button.image = thumbnail  # Keep reference
            
            # Info frame
            info_frame = tk.Frame(main_frame, bg='white')
            info_frame.pack(fill=tk.X, pady=(2, 0))
            
            # Tab label with icon
            tab_icons = {
                "Nano Banana": "🍌",
                "SeedEdit": "✨", 
                "Seedream V4": "🌟",
                "Upscaler": "🔍",
                "Wan 2.2": "🎬",
                "SeedDance Pro": "🕺"
            }
            
            icon = tab_icons.get(result['tab_name'], "🎨")
            tab_label = tk.Label(
                info_frame,
                text=f"{icon}",
                font=('Arial', 8),
                bg='white',
                fg='#666666'
            )
            tab_label.pack()
            
            # Timestamp
            time_str = datetime.fromtimestamp(result['timestamp']).strftime("%m/%d %H:%M")
            time_label = tk.Label(
                info_frame,
                text=time_str,
                font=('Arial', 6),
                bg='white',
                fg='#999999'
            )
            time_label.pack()
            
            # Feedback buttons frame
            feedback_frame = tk.Frame(info_frame, bg='white')
            feedback_frame.pack(fill=tk.X, pady=(2, 0))
            
            # Get current feedback status
            feedback_status = result.get('feedback', None)
            
            # Thumbs up button
            thumbs_up_btn = tk.Button(
                feedback_frame,
                text="👍",
                font=('Arial', 8),
                bg='#e8f5e9' if feedback_status == 'good' else 'white',
                fg='#4caf50' if feedback_status == 'good' else '#999',
                relief=tk.FLAT,
                bd=0,
                padx=2,
                pady=0,
                command=lambda r=result: self.mark_result_good(r)
            )
            thumbs_up_btn.pack(side=tk.LEFT, padx=1)
            
            # Thumbs down button
            thumbs_down_btn = tk.Button(
                feedback_frame,
                text="👎",
                font=('Arial', 8),
                bg='#ffebee' if feedback_status == 'bad' else 'white',
                fg='#f44336' if feedback_status == 'bad' else '#999',
                relief=tk.FLAT,
                bd=0,
                padx=2,
                pady=0,
                command=lambda r=result: self.mark_result_bad(r)
            )
            thumbs_down_btn.pack(side=tk.LEFT, padx=1)
            
            # Bind right-click for context menu
            def show_context_menu(event):
                self.show_result_actions(result, event.x_root, event.y_root)
            
            # Bind context menu to all elements
            for widget in [img_button, main_frame, info_frame, tab_label, time_label]:
                widget.bind("<Button-3>", show_context_menu)  # Right click
                widget.bind("<Control-Button-1>", show_context_menu)  # Ctrl+click for Mac
            
            # Add hover effects
            def on_enter(event):
                parent.config(relief=tk.RAISED, bd=2)
                main_frame.config(bg='#f0f8ff')
                info_frame.config(bg='#f0f8ff')
                tab_label.config(bg='#f0f8ff')
                time_label.config(bg='#f0f8ff')
                feedback_frame.config(bg='#f0f8ff')
            
            def on_leave(event):
                parent.config(relief=tk.RAISED, bd=1)
                main_frame.config(bg='white')
                info_frame.config(bg='white')
                tab_label.config(bg='white')
                time_label.config(bg='white')
                feedback_frame.config(bg='white')
            
            parent.bind("<Enter>", on_enter)
            parent.bind("<Leave>", on_leave)
            
            # Bind mousewheel to all item widgets for smooth scrolling
            for widget in [parent, img_button, main_frame, info_frame, tab_label, time_label, feedback_frame, thumbs_up_btn, thumbs_down_btn]:
                widget.bind("<MouseWheel>", self._on_mousewheel)
            
        except Exception as e:
            logger.error(f"Error creating result item: {e}")
            # Create error placeholder
            error_label = ttk.Label(
                parent,
                text="❌\nError",
                font=('Arial', 8),
                foreground='red',
                justify=tk.CENTER
            )
            error_label.pack(pady=5)
    
    def load_dynamic_thumbnail(self, image_path):
        """Load thumbnail with dynamic sizing and caching for performance"""
        try:
            # Create cache key with path and size
            cache_key = f"{image_path}_{self.current_thumbnail_size}"
            
            # Check cache first
            if cache_key in self._thumbnail_cache:
                return self._thumbnail_cache[cache_key]
            
            # Load and process image
            with Image.open(image_path) as img:
                # Convert to RGB if necessary
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")
                
                # Resize to current thumbnail size
                img.thumbnail((self.current_thumbnail_size, self.current_thumbnail_size), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                
                # Cache the thumbnail (limit cache size to prevent memory issues)
                if len(self._thumbnail_cache) < 200:  # Max 200 cached thumbnails
                    self._thumbnail_cache[cache_key] = photo
                
                return photo
                
        except Exception as e:
            logger.debug(f"Error loading thumbnail for {image_path}: {e}")
            # Return placeholder image
            placeholder = Image.new('RGB', (self.current_thumbnail_size, self.current_thumbnail_size), '#f0f0f0')
            return ImageTk.PhotoImage(placeholder)
    
    def show_image_preview(self, result):
        """Show image preview - switches to Seedream V4 tab and loads INPUT image and prompt"""
        try:
            if not self.main_app:
                show_error("Error", "Cannot access main application")
                return
            
            # Determine which tab this image belongs to
            tab_name = result.get('tab_name', 'Seedream V4')
            tab_id = result.get('tab_id', '1')  # Default to tab 1
            
            # Determine target tab
            target_tab = None
            
            # If it's a Seedream V4 result (or unknown), try to get Seedream tab
            if tab_name == 'Seedream V4' or tab_name not in ['Nano Banana', 'SeedEdit', 'Upscaler', 'Wan 2.2', 'SeedDance Pro']:
                # Try to get the specific Seedream tab
                if tab_id == '2' and hasattr(self.main_app, 'seedream_tab_2'):
                    target_tab = self.main_app.seedream_tab_2
                    tab_name_for_log = "Seedream V4 #2"
                elif hasattr(self.main_app, 'seedream_tab_1'):
                    target_tab = self.main_app.seedream_tab_1
                    tab_name_for_log = "Seedream V4 #1"
                elif hasattr(self.main_app, 'seedream_v4_tab'):
                    target_tab = self.main_app.seedream_v4_tab
                    tab_name_for_log = "Seedream V4"
                
                # Try to switch to the target tab
                if target_tab and hasattr(self.main_app, 'notebook'):
                    try:
                        # Build list of all tabs
                        tabs = []
                        for tab_attr in ['editor_tab', 'seededit_tab', 'seedream_tab_1', 'seedream_v4_tab', 
                                        'seedream_tab_2', 'upscaler_tab', 'video_tab', 'seeddance_tab']:
                            if hasattr(self.main_app, tab_attr):
                                tab = getattr(self.main_app, tab_attr)
                                if tab is not None:
                                    tabs.append(tab)
                        
                        # Find the index of target tab
                        if target_tab in tabs:
                            seedream_index = tabs.index(target_tab)
                            self.main_app.notebook.select(seedream_index)
                            logger.info(f"✓ Switched to {tab_name_for_log}")
                            
                            # Give UI a moment to render the tab, then load INPUT image and prompt
                            self.parent.after(50, lambda: self._load_into_seedream(result, target_tab))
                            return
                        else:
                            logger.warning(f"Target tab not found in tabs list")
                    except Exception as e:
                        logger.error(f"Could not switch to Seedream V4 tab: {e}")
            
            # Fallback: Try to use currently active tab if we couldn't switch to target
            if not target_tab:
                target_tab = self.get_current_active_tab()
            
            if not target_tab:
                # Last resort: try any Seedream tab
                for tab_attr in ['seedream_tab_1', 'seedream_v4_tab', 'seedream_tab_2']:
                    if hasattr(self.main_app, tab_attr):
                        target_tab = getattr(self.main_app, tab_attr)
                        if target_tab:
                            logger.info(f"Using fallback tab: {tab_attr}")
                            break
            
            if not target_tab:
                show_error("Error", "No compatible tab found. Please open a Seedream V4 tab first.")
                return
            
            # Try to load the INPUT image and prompt
            self._try_load_into_tab(target_tab, result)
                
        except Exception as e:
            logger.error(f"Error showing image preview: {e}")
            show_error("Preview Error", f"Failed to show preview: {str(e)}")
    
    def _load_into_seedream(self, result, target_tab=None):
        """Load INPUT image into Seedream V4 tab (called after tab switch)"""
        try:
            # Use provided target_tab or fallback to seedream_v4_tab
            if target_tab is None:
                target_tab = (self.main_app.seedream_v4_tab if hasattr(self.main_app, 'seedream_v4_tab') 
                             else self.main_app.seedream_tab_1 if hasattr(self.main_app, 'seedream_tab_1') 
                             else None)
            
            if target_tab:
                self._try_load_into_tab(target_tab, result)
            else:
                logger.error("No Seedream V4 tab available")
        except Exception as e:
            logger.error(f"Error loading into Seedream: {e}")
    
    def _get_input_image_from_metadata(self, result):
        """Get the input image path from the result's metadata JSON file"""
        try:
            # Construct the JSON metadata file path
            image_path = result['image_path']
            json_path = str(Path(image_path).with_suffix('.json'))
            
            # Read the metadata
            if Path(json_path).exists():
                with open(json_path, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                    
                # Try to get input image path
                input_path = metadata.get('input_image_path')
                
                # Verify the input image exists
                if input_path and Path(input_path).exists():
                    return input_path
                else:
                    logger.debug(f"Input image path from metadata doesn't exist: {input_path}")
            else:
                logger.debug(f"Metadata JSON not found: {json_path}")
                
        except Exception as e:
            logger.error(f"Error reading metadata for input image: {e}")
        
        return None
    
    def _try_load_into_tab(self, current_tab, result):
        """Try various methods to load INPUT image and prompt into a tab"""
        try:
            # First, get the INPUT image path and prompt from the metadata
            input_image_path = self._get_input_image_from_metadata(result)
            prompt_text = result.get('prompt', '')  # Get prompt from result data
            
            if not input_image_path:
                logger.warning(f"No input image found in metadata for {result['filename']}")
                # Fallback to showing the result image itself
                input_image_path = result['image_path']
            
            # 1. Try improved_layout first (new refactored system for Seedream V4)
            if hasattr(current_tab, 'improved_layout'):
                try:
                    # Load image
                    if hasattr(current_tab.improved_layout, 'load_image'):
                        current_tab.improved_layout.load_image(input_image_path)
                        logger.info(f"✓ Loaded INPUT image into improved layout from: {Path(input_image_path).name}")
                    
                    # Load prompt
                    if prompt_text:
                        self._load_prompt_into_tab(current_tab, prompt_text)
                    
                    return
                except Exception as e:
                    logger.debug(f"Could not use improved_layout: {e}")
            
            # 2. Try on_image_selected method (most tabs have this)
            if hasattr(current_tab, 'on_image_selected'):
                try:
                    # Try with replacing_image parameter first
                    current_tab.on_image_selected(input_image_path, replacing_image=True)
                    logger.info(f"✓ Loaded INPUT image via on_image_selected from: {Path(input_image_path).name}")
                    
                    # Load prompt
                    if prompt_text:
                        self._load_prompt_into_tab(current_tab, prompt_text)
                    
                    return
                except TypeError:
                    # Fallback to without the parameter
                    current_tab.on_image_selected(input_image_path)
                    logger.info(f"✓ Loaded INPUT image via on_image_selected from: {Path(input_image_path).name}")
                    
                    # Load prompt
                    if prompt_text:
                        self._load_prompt_into_tab(current_tab, prompt_text)
                    
                    return
                except Exception as e:
                    logger.debug(f"Could not use on_image_selected: {e}")
            
            # 3. Try optimized_layout (older system)
            if hasattr(current_tab, 'optimized_layout') and hasattr(current_tab.optimized_layout, 'update_input_image'):
                success = current_tab.optimized_layout.update_input_image(input_image_path)
                if success:
                    logger.info(f"✓ Loaded INPUT image via optimized_layout from: {Path(input_image_path).name}")
                    
                    # Load prompt
                    if prompt_text:
                        self._load_prompt_into_tab(current_tab, prompt_text)
                    
                    return
            
            # 4. Try image_selector
            if hasattr(current_tab, 'image_selector') and hasattr(current_tab.image_selector, 'update_image'):
                current_tab.image_selector.update_image(input_image_path)
                logger.info(f"✓ Loaded INPUT image via image_selector from: {Path(input_image_path).name}")
                
                # Load prompt
                if prompt_text:
                    self._load_prompt_into_tab(current_tab, prompt_text)
                
                return
            
            # No method worked
            show_error("Preview Error", "This tab doesn't support loading images")
                
        except Exception as e:
            logger.error(f"Error trying to load into tab: {e}")
    
    def _load_prompt_into_tab(self, current_tab, prompt_text):
        """Load prompt text into the appropriate prompt field"""
        try:
            # Try improved_layout prompt_manager (new Seedream V4 system)
            if hasattr(current_tab, 'improved_layout') and hasattr(current_tab.improved_layout, 'prompt_manager'):
                if hasattr(current_tab.improved_layout.prompt_manager, 'set_prompt_text'):
                    current_tab.improved_layout.prompt_manager.set_prompt_text(prompt_text)
                    logger.info(f"✓ Loaded prompt via prompt_manager: {prompt_text[:50]}...")
                    return
            
            # Try direct prompt_text widget (common in many tabs)
            if hasattr(current_tab, 'prompt_text'):
                try:
                    # Clear placeholder if exists
                    if hasattr(current_tab, '_clear_placeholder'):
                        current_tab._clear_placeholder()
                    
                    # Set the prompt text
                    current_tab.prompt_text.delete("1.0", tk.END)
                    current_tab.prompt_text.insert("1.0", prompt_text)
                    
                    # Update placeholder state
                    if hasattr(current_tab, 'prompt_has_placeholder'):
                        current_tab.prompt_has_placeholder = False
                    
                    # Trigger any change handlers
                    if hasattr(current_tab, '_on_prompt_text_changed'):
                        current_tab._on_prompt_text_changed()
                    
                    logger.info(f"✓ Loaded prompt via prompt_text: {prompt_text[:50]}...")
                    return
                except Exception as e:
                    logger.debug(f"Could not use prompt_text widget: {e}")
            
            # Try improved_layout direct prompt_text access
            if hasattr(current_tab, 'improved_layout') and hasattr(current_tab.improved_layout, 'prompt_text'):
                try:
                    # Use the set_prompt_text method if available
                    if hasattr(current_tab.improved_layout, 'set_prompt_text'):
                        current_tab.improved_layout.set_prompt_text(prompt_text)
                    else:
                        # Direct widget access
                        current_tab.improved_layout.prompt_text.delete("1.0", tk.END)
                        current_tab.improved_layout.prompt_text.insert("1.0", prompt_text)
                    
                    logger.info(f"✓ Loaded prompt via improved_layout.prompt_text: {prompt_text[:50]}...")
                    return
                except Exception as e:
                    logger.debug(f"Could not use improved_layout.prompt_text: {e}")
            
            logger.debug("No compatible prompt field found in tab")
                
        except Exception as e:
            logger.error(f"Error loading prompt into tab: {e}")
    
    def get_current_active_tab(self):
        """Get the currently active tab"""
        try:
            if not hasattr(self.main_app, 'notebook'):
                return None
            
            current_index = self.main_app.notebook.index(self.main_app.notebook.select())
            tabs = [
                self.main_app.editor_tab,
                self.main_app.seededit_tab,
                self.main_app.seedream_tab_1 if hasattr(self.main_app, 'seedream_tab_1') else self.main_app.seedream_v4_tab,
                self.main_app.seedream_tab_2 if hasattr(self.main_app, 'seedream_tab_2') else None,
                self.main_app.upscaler_tab,
                self.main_app.video_tab,
                self.main_app.seeddance_tab
            ]
            
            # Remove None entries
            tabs = [t for t in tabs if t is not None]
            
            if 0 <= current_index < len(tabs):
                return tabs[current_index]
            
        except Exception as e:
            logger.debug(f"Error getting current tab: {e}")
        
        return None
    
    def send_result_to_current_tab(self, result):
        """Send result to the current active tab"""
        try:
            current_tab = self.get_current_active_tab()
            if not current_tab:
                show_error("Error", "No active tab found")
                return
            
            # Try different methods to load the image
            if hasattr(current_tab, 'on_image_selected'):
                try:
                    # Try with replacing_image parameter first
                    current_tab.on_image_selected(result['image_path'], replacing_image=True)
                except TypeError:
                    # Fallback to without the parameter
                    current_tab.on_image_selected(result['image_path'])
                # Image loaded successfully (no popup needed)
            elif hasattr(current_tab, 'load_image'):
                current_tab.load_image(result['image_path'])
                # Image loaded successfully (no popup needed)
            else:
                show_error("Error", f"Cannot load image in {self.get_current_tab_name()}")
                
        except Exception as e:
            logger.error(f"Error sending result to current tab: {e}")
            show_error("Error", f"Failed to load image: {str(e)}")
    
    def show_send_to_menu(self, result, button):
        """Show send to menu for result"""
        try:
            navigator = CrossTabNavigator(self.main_app)
            current_tab_name = self.get_current_tab_name()
            target_tabs = navigator.get_available_targets(current_tab_name)
            
            if not target_tabs:
                show_error("No Targets", "No compatible tabs available.")
                return
            
            # Create popup menu
            popup = tk.Menu(self.parent, tearoff=0)
            
            for tab_info in target_tabs:
                tab_id, tab_name, tab_icon = tab_info
                popup.add_command(
                    label=f"{tab_icon} {tab_name}",
                    command=lambda tid=tab_id, tname=tab_name: self.send_result_to_tab(
                        result, tid, tname
                    )
                )
            
            # Show popup at button
            button.update_idletasks()
            x = button.winfo_rootx()
            y = button.winfo_rooty() + button.winfo_height()
            popup.post(x, y)
            
        except Exception as e:
            logger.error(f"Error showing send menu: {e}")
    
    def show_result_actions(self, result, x=None, y=None):
        """Show action menu for selected result"""
        try:
            # Create popup menu
            popup = tk.Menu(self.parent, tearoff=0)
            
            # Preview option
            popup.add_command(
                label="🔍 Preview",
                command=lambda: self.show_image_preview(result)
            )
            
            # Send To options
            navigator = CrossTabNavigator(self.main_app)
            current_tab_name = self.get_current_tab_name()
            target_tabs = navigator.get_available_targets(current_tab_name)
            
            if target_tabs:
                popup.add_separator()
                send_menu = tk.Menu(popup, tearoff=0)
                
                for tab_info in target_tabs:
                    tab_id, tab_name, tab_icon = tab_info
                    send_menu.add_command(
                        label=f"{tab_icon} {tab_name}",
                        command=lambda tid=tab_id, tname=tab_name: self.send_result_to_tab(
                            result, tid, tname
                        )
                    )
                
                popup.add_cascade(label="📤 Send To", menu=send_menu)
            
            # Other actions
            popup.add_separator()
            popup.add_command(
                label="📁 Show in Folder",
                command=lambda: self.show_in_folder(result['image_path'])
            )
            popup.add_command(
                label="🗑️ Delete",
                command=lambda: self.delete_result(result)
            )
            
            # Show popup at specified position or mouse position
            if x is not None and y is not None:
                popup.post(x, y)
            else:
                popup.post(self.parent.winfo_pointerx(), self.parent.winfo_pointery())
                
        except Exception as e:
            logger.error(f"Error showing result actions: {e}")
        finally:
            try:
                popup.grab_release()
            except:
                pass
    
    def send_result_to_tab(self, result, tab_id, tab_name):
        """Send result to specified tab"""
        try:
            navigator = CrossTabNavigator(self.main_app)
            success = navigator.send_to_tab(result['image_path'], tab_id, tab_name, "Recent Results")
            
            if success:
                # Image sent successfully
                pass
        except Exception as e:
            logger.error(f"Error sending result to tab: {e}")
            show_error("Send Error", f"Failed to send result to {tab_name}: {str(e)}")
    
    def show_in_folder(self, image_path):
        """Show image file in file explorer"""
        try:
            import subprocess
            import platform
            
            folder_path = os.path.dirname(image_path)
            
            if platform.system() == "Windows":
                subprocess.run(['explorer', '/select,', image_path])
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(['open', '-R', image_path])
            else:  # Linux
                subprocess.run(['xdg-open', folder_path])
                
        except Exception as e:
            logger.error(f"Error opening folder: {e}")
            show_error("Error", f"Failed to open folder: {str(e)}")
    
    def delete_result(self, result):
        """Delete result file"""
        try:
            from tkinter import messagebox
            from core.prompt_result_tracker import get_prompt_tracker
            
            if messagebox.askyesno("Delete Result", 
                                 f"Are you sure you want to delete this result?\n\n{result['filename']}"):
                # Track deletion as negative feedback (before deleting)
                prompt = result.get('prompt', '')
                if prompt:
                    tracker = get_prompt_tracker()
                    
                    # Get image description from metadata if available
                    image_desc = result.get('metadata', {}).get('image_description') if result.get('metadata') else None
                    
                    metadata_dict = {
                        'source': result.get('tab_name', 'manual'),
                        'tab_id': result.get('tab_id', '1'),
                        'image_description': image_desc
                    }
                    tracker.track_result_deleted(prompt, result['image_path'], metadata_dict, image_desc)
                
                # Delete image file
                if os.path.exists(result['image_path']):
                    os.remove(result['image_path'])
                
                # Delete metadata file if exists
                json_path = os.path.splitext(result['image_path'])[0] + ".json"
                if os.path.exists(json_path):
                    os.remove(json_path)
                
                # Result deleted successfully
                
                # Refresh display
                self.refresh_results()
                # Result deleted successfully (no popup needed)
                
        except Exception as e:
            logger.error(f"Error deleting result: {e}")
            show_error("Error", f"Failed to delete result: {str(e)}")
    
    def mark_result_good(self, result):
        """Mark result as good (positive feedback)"""
        try:
            from core.prompt_result_tracker import get_prompt_tracker
            
            # Get prompt from metadata
            prompt = result.get('prompt', '')
            if not prompt:
                # Try loading from metadata file
                json_path = os.path.splitext(result['image_path'])[0] + ".json"
                if os.path.exists(json_path):
                    with open(json_path, 'r', encoding='utf-8') as f:
                        metadata = json.load(f)
                        prompt = metadata.get('prompt', '')
            
            if prompt:
                tracker = get_prompt_tracker()
                
                # Get image description from metadata if available
                image_desc = result.get('metadata', {}).get('image_description') if result.get('metadata') else None
                
                metadata_dict = {
                    'source': result.get('tab_name', 'manual'),
                    'tab_id': result.get('tab_id', '1'),
                    'image_description': image_desc
                }
                tracker.track_feedback(prompt, 'good', result['image_path'], metadata_dict, image_desc)
                
                # Update result feedback in memory
                result['feedback'] = 'good'
                
                # Save feedback to metadata file
                json_path = os.path.splitext(result['image_path'])[0] + ".json"
                if os.path.exists(json_path):
                    with open(json_path, 'r', encoding='utf-8') as f:
                        metadata_file = json.load(f)
                    metadata_file['feedback'] = 'good'
                    with open(json_path, 'w', encoding='utf-8') as f:
                        json.dump(metadata_file, f, indent=2)
                
                logger.info(f"✅ Marked result as GOOD")
                # Refresh to update button colors
                self.render_results_grid()
            else:
                logger.warning("No prompt found for result, cannot track feedback")
                
        except Exception as e:
            logger.error(f"Error marking result as good: {e}")
    
    def mark_result_bad(self, result):
        """Mark result as bad (negative feedback)"""
        try:
            from core.prompt_result_tracker import get_prompt_tracker
            
            # Get prompt from metadata
            prompt = result.get('prompt', '')
            if not prompt:
                # Try loading from metadata file
                json_path = os.path.splitext(result['image_path'])[0] + ".json"
                if os.path.exists(json_path):
                    with open(json_path, 'r', encoding='utf-8') as f:
                        metadata = json.load(f)
                        prompt = metadata.get('prompt', '')
            
            if prompt:
                tracker = get_prompt_tracker()
                
                # Get image description from metadata if available
                image_desc = result.get('metadata', {}).get('image_description') if result.get('metadata') else None
                
                metadata_dict = {
                    'source': result.get('tab_name', 'manual'),
                    'tab_id': result.get('tab_id', '1'),
                    'image_description': image_desc
                }
                tracker.track_feedback(prompt, 'bad', result['image_path'], metadata_dict, image_desc)
                
                # Update result feedback in memory
                result['feedback'] = 'bad'
                
                # Save feedback to metadata file
                json_path = os.path.splitext(result['image_path'])[0] + ".json"
                if os.path.exists(json_path):
                    with open(json_path, 'r', encoding='utf-8') as f:
                        metadata_file = json.load(f)
                    metadata_file['feedback'] = 'bad'
                    with open(json_path, 'w', encoding='utf-8') as f:
                        json.dump(metadata_file, f, indent=2)
                
                logger.info(f"❌ Marked result as BAD")
                # Refresh to update button colors
                self.render_results_grid()
            else:
                logger.warning("No prompt found for result, cannot track feedback")
                
        except Exception as e:
            logger.error(f"Error marking result as bad: {e}")
    
    def get_current_tab_name(self):
        """Get the name of currently active tab"""
        try:
            if hasattr(self.main_app, 'notebook'):
                current_index = self.main_app.notebook.index(self.main_app.notebook.select())
                tab_names = [
                    "Nano Banana Editor", 
                    "SeedEdit", 
                    "Seedream V4",
                    "Image Upscaler",
                    "Wan 2.2",  
                    "SeedDance Pro"
                ]
                return tab_names[current_index] if current_index < len(tab_names) else "Unknown"
        except:
            pass
        return "Unknown"
    
    def on_filter_changed(self, event=None):
        """Handle filter change"""
        self.current_filter = self.filter_var.get()
        self.apply_filter()
    
    def update_count_label(self):
        """Update the results count label"""
        count = len(self.filtered_results)
        total = len(self.results_data)
        
        if self.current_filter == "All":
            text = f"{count} results"
        else:
            text = f"{count} of {total} results"
        
        self.count_label.config(text=text)
    
    def refresh_results(self):
        """Refresh the results list and clear cache"""
        self._thumbnail_cache.clear()  # Clear cache for fresh thumbnails
        self.load_recent_results()
    
    def get_frame(self):
        """Get the main panel frame"""
        return self.panel_frame
    
    def destroy(self):
        """Clean up resources"""
        if hasattr(self, 'panel_frame'):
            self.panel_frame.destroy()