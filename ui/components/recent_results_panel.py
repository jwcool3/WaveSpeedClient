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
        
        # Dynamic sizing variables
        self.min_thumbnail_size = 45
        self.max_thumbnail_size = 120
        self.current_thumbnail_size = 60
        self.min_cols = 2
        self.max_cols = 6
        self.current_cols = 3
        
        self.max_results = 50
        
        # No popup window needed - using main display
        
        self.setup_ui()
        self.load_recent_results()
        
        # Bind resize events
        self.parent.bind('<Configure>', self.on_panel_resize)
    
    def setup_ui(self):
        """Setup the enhanced recent results panel UI"""
        # Main panel frame
        self.panel_frame = ttk.Frame(self.parent)
        
        # Header section
        self.setup_header()
        
        # Filter section
        self.setup_filter_section()
        
        # Scrollable results area
        self.setup_scrollable_area()
        
        # Status bar
        self.setup_status_bar()
    
    def setup_header(self):
        """Setup header with title and controls"""
        header_frame = ttk.Frame(self.panel_frame)
        header_frame.pack(fill=tk.X, padx=3, pady=(3, 0))
        
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
        filter_frame.pack(fill=tk.X, padx=3, pady=(3, 0))
        
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
        """Setup enhanced scrollable area for results grid"""
        # Create canvas frame
        canvas_frame = ttk.Frame(self.panel_frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=3, pady=(3, 0))
        
        # Canvas and scrollbar
        self.canvas = tk.Canvas(canvas_frame, highlightthickness=0, bg='#f8f8f8')
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        # Configure scrolling
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.update_scroll_region()
        )
        
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas and scrollbar
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind events
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind('<Configure>', self.on_canvas_configure)
        
        # Results grid frame
        self.results_grid = ttk.Frame(self.scrollable_frame)
        self.results_grid.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
    
    def setup_status_bar(self):
        """Setup status bar at bottom"""
        status_frame = ttk.Frame(self.panel_frame)
        status_frame.pack(fill=tk.X, padx=3, pady=(0, 3))
        
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
        if event and event.widget == self.parent:
            self.calculate_optimal_layout()
            self.render_results_grid()
    
    def on_canvas_configure(self, event):
        """Handle canvas resize"""
        # Update scrollable frame width to match canvas
        canvas_width = event.width
        self.canvas.itemconfig(self.canvas_window, width=canvas_width)
        
        # Recalculate layout if canvas width changed significantly
        self.calculate_optimal_layout()
    
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
            optimal_cols = max(self.min_cols, min(self.max_cols, available_width // thumb_width))
            
            if optimal_cols != self.current_cols:
                self.current_cols = optimal_cols
                self.render_results_grid()
                
        except Exception as e:
            logger.debug(f"Layout calculation error: {e}")
    
    def increase_thumbnail_size(self):
        """Increase thumbnail size"""
        new_size = min(self.max_thumbnail_size, self.current_thumbnail_size + 10)
        if new_size != self.current_thumbnail_size:
            self.current_thumbnail_size = new_size
            self.size_label.config(text=f"{self.current_thumbnail_size}px")
            self.calculate_optimal_layout()
            self.render_results_grid()
    
    def decrease_thumbnail_size(self):
        """Decrease thumbnail size"""
        new_size = max(self.min_thumbnail_size, self.current_thumbnail_size - 10)
        if new_size != self.current_thumbnail_size:
            self.current_thumbnail_size = new_size
            self.size_label.config(text=f"{self.current_thumbnail_size}px")
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
                    self.parent.after(0, lambda: self.update_results_display([]))
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
                                    
                                    result_info = {
                                        'image_path': image_path,
                                        'tab_name': tab_name,
                                        'timestamp': mod_time,
                                        'metadata': metadata,
                                        'filename': os.path.basename(image_path)
                                    }
                                    results.append(result_info)
                                    
                                except Exception as e:
                                    logger.debug(f"Error processing {image_path}: {e}")
                
                # Sort by timestamp (newest first)
                results.sort(key=lambda x: x['timestamp'], reverse=True)
                
                # Limit to max results
                results = results[:self.max_results]
                
                # Update UI in main thread
                self.parent.after(0, lambda: self.update_results_display(results))
                
            except Exception as e:
                logger.error(f"Error loading recent results: {e}")
                self.parent.after(0, lambda: self.update_results_display([]))
        
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
            
            def on_leave(event):
                parent.config(relief=tk.RAISED, bd=1)
                main_frame.config(bg='white')
                info_frame.config(bg='white')
                tab_label.config(bg='white')
                time_label.config(bg='white')
            
            parent.bind("<Enter>", on_enter)
            parent.bind("<Leave>", on_leave)
            
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
        """Load thumbnail with dynamic sizing"""
        try:
            with Image.open(image_path) as img:
                # Convert to RGB if necessary
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")
                
                # Resize to current thumbnail size
                img.thumbnail((self.current_thumbnail_size, self.current_thumbnail_size), Image.Resampling.LANCZOS)
                return ImageTk.PhotoImage(img)
                
        except Exception as e:
            logger.debug(f"Error loading thumbnail for {image_path}: {e}")
            # Return placeholder image
            placeholder = Image.new('RGB', (self.current_thumbnail_size, self.current_thumbnail_size), '#f0f0f0')
            return ImageTk.PhotoImage(placeholder)
    
    def show_image_preview(self, result):
        """Show image preview in the current tab's image display"""
        try:
            if not self.main_app:
                show_error("Error", "Cannot access main application")
                return
            
            # Get the current active tab
            current_tab = self.get_current_active_tab()
            if not current_tab:
                show_error("Error", "No active tab found")
                return
            
            # Try to load the image in the current tab's image display
            if hasattr(current_tab, 'optimized_layout') and hasattr(current_tab.optimized_layout, 'update_input_image'):
                # Use the optimized layout's image display
                success = current_tab.optimized_layout.update_input_image(result['image_path'])
                if success:
                    # Also call the tab's image selection method if available
                    if hasattr(current_tab, 'on_image_selected'):
                        try:
                            # Try with replacing_image parameter first
                            current_tab.on_image_selected(result['image_path'], replacing_image=True)
                        except TypeError:
                            # Fallback to without the parameter
                            current_tab.on_image_selected(result['image_path'])
                    
                    # Image loaded successfully (no popup needed)
                else:
                    show_error("Preview Error", "Failed to load image in current tab")
            elif hasattr(current_tab, 'image_selector') and hasattr(current_tab.image_selector, 'update_image'):
                # Use the image selector's display
                current_tab.image_selector.update_image(result['image_path'])
                # Image loaded successfully (no popup needed)
            else:
                # Fallback: try to send to the current tab
                self.send_result_to_current_tab(result)
                
        except Exception as e:
            logger.error(f"Error showing image preview: {e}")
            show_error("Preview Error", f"Failed to show preview: {str(e)}")
    
    def get_current_active_tab(self):
        """Get the currently active tab"""
        try:
            if not hasattr(self.main_app, 'notebook'):
                return None
            
            current_index = self.main_app.notebook.index(self.main_app.notebook.select())
            tabs = [
                self.main_app.editor_tab,
                self.main_app.seededit_tab,
                self.main_app.seedream_v4_tab,
                self.main_app.upscaler_tab,
                self.main_app.video_tab,
                self.main_app.seeddance_tab
            ]
            
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
            
            if messagebox.askyesno("Delete Result", 
                                 f"Are you sure you want to delete this result?\n\n{result['filename']}"):
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
        """Refresh the results list"""
        self.load_recent_results()
    
    def get_frame(self):
        """Get the main panel frame"""
        return self.panel_frame
    
    def destroy(self):
        """Clean up resources"""
        if hasattr(self, 'panel_frame'):
            self.panel_frame.destroy()