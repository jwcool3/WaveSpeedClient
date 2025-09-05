"""
Recent Results Panel Component for WaveSpeed AI Application

This module provides a panel showing recent generated results that can be
easily reused as input in any compatible tab.
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
    """Panel for displaying and managing recent AI generation results"""
    
    def __init__(self, parent, main_app):
        self.parent = parent
        self.main_app = main_app
        self.results_data = []
        self.filtered_results = []
        self.current_filter = "All"
        self.thumbnail_size = (55, 55)  # Even smaller thumbnails for much thinner panel
        self.max_results = 50  # Keep last 50 results
        
        self.setup_ui()
        self.load_recent_results()
    
    def setup_ui(self):
        """Setup the recent results panel UI"""
        # Main panel frame
        self.panel_frame = ttk.Frame(self.parent)
        
        # Header section
        header_frame = ttk.Frame(self.panel_frame)
        header_frame.pack(fill=tk.X, padx=3, pady=(3, 0))
        
        # Title with icon
        title_label = ttk.Label(
            header_frame, 
            text="📂 Recent Results", 
            font=('Arial', 10, 'bold')
        )
        title_label.pack(side=tk.LEFT)
        
        # Refresh button
        refresh_btn = ttk.Button(
            header_frame,
            text="🔄",
            width=3,
            command=self.refresh_results
        )
        refresh_btn.pack(side=tk.RIGHT)
        
        # Filter section
        filter_frame = ttk.Frame(self.panel_frame)
        filter_frame.pack(fill=tk.X, padx=3, pady=(3, 0))
        
        ttk.Label(filter_frame, text="Filter:", font=('Arial', 8)).pack(side=tk.LEFT)
        
        self.filter_var = tk.StringVar(value="All")
        filter_combo = ttk.Combobox(
            filter_frame,
            textvariable=self.filter_var,
            values=["All", "Nano Banana", "SeedEdit", "Upscaler", "Wan 2.2", "SeedDance"],
            state="readonly",
            width=10,
            font=('Arial', 7)
        )
        filter_combo.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(5, 0))
        filter_combo.bind('<<ComboboxSelected>>', self.on_filter_changed)
        
        # Results count
        self.count_label = ttk.Label(
            self.panel_frame, 
            text="0 results", 
            font=('Arial', 8),
            foreground='#666666'
        )
        self.count_label.pack(padx=3, pady=(1, 3))
        
        # Scrollable results area
        self.setup_scrollable_area()
    
    def setup_scrollable_area(self):
        """Setup scrollable area for results grid"""
        # Create canvas and scrollbar for scrolling
        canvas_frame = ttk.Frame(self.panel_frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=3, pady=(0, 3))
        
        self.canvas = tk.Canvas(canvas_frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mouse wheel scrolling
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        
        # Results grid frame
        self.results_grid = ttk.Frame(self.scrollable_frame)
        self.results_grid.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
    
    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling"""
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def load_recent_results(self):
        """Load recent results from auto-save directories"""
        def _load_in_background():
            try:
                results = []
                
                # Scan auto-save directories for recent results
                base_dir = "WaveSpeed_Results"
                if not os.path.exists(base_dir):
                    self.parent.after(0, lambda: self.update_results_display([]))
                    return
                
                # Define subdirectories and their corresponding tab names
                tab_mapping = {
                    "Nano_Banana_Editor": "Nano Banana",
                    "SeedEdit": "SeedEdit", 
                    "Image_Upscaler": "Upscaler",
                    "Wan_2.2": "Wan 2.2",
                    "SeedDance": "SeedDance"
                }
                
                for subdir, tab_name in tab_mapping.items():
                    subdir_path = os.path.join(base_dir, subdir)
                    if not os.path.exists(subdir_path):
                        continue
                    
                    # Find image files (PNG, JPG, JPEG)
                    image_patterns = ["*.png", "*.jpg", "*.jpeg"]
                    for pattern in image_patterns:
                        for image_path in glob.glob(os.path.join(subdir_path, pattern)):
                            # Look for corresponding JSON metadata
                            json_path = os.path.splitext(image_path)[0] + ".json"
                            
                            metadata = {}
                            if os.path.exists(json_path):
                                try:
                                    with open(json_path, 'r') as f:
                                        metadata = json.load(f)
                                except:
                                    pass  # Continue without metadata if JSON is corrupted
                            
                            # Get file modification time
                            mod_time = os.path.getmtime(image_path)
                            
                            result_info = {
                                'image_path': image_path,
                                'tab_name': tab_name,
                                'timestamp': mod_time,
                                'metadata': metadata,
                                'filename': os.path.basename(image_path)
                            }
                            results.append(result_info)
                
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
        """Render the results grid"""
        # Clear existing grid
        for widget in self.results_grid.winfo_children():
            widget.destroy()
        
        if not self.filtered_results:
            # Show empty state
            empty_label = ttk.Label(
                self.results_grid,
                text="No recent results found.\nGenerate some images to see them here!",
                font=('Arial', 10),
                foreground='#666666',
                justify=tk.CENTER
            )
            empty_label.pack(pady=20)
            return
        
        # Grid configuration (3 columns)
        cols = 3
        for i, result in enumerate(self.filtered_results):
            row = i // cols
            col = i % cols
            
            # Create result item frame
            item_frame = ttk.Frame(self.results_grid, style="Card.TFrame")
            item_frame.grid(row=row, column=col, padx=1, pady=1, sticky="nsew")
            
            # Configure grid weights for even distribution
            self.results_grid.columnconfigure(col, weight=1)
            
            self.create_result_item(item_frame, result)
    
    def create_result_item(self, parent, result):
        """Create a single result item widget"""
        try:
            # Load and resize image thumbnail
            thumbnail = self.load_thumbnail(result['image_path'])
            
            # Image button (clickable)
            img_button = tk.Button(
                parent,
                image=thumbnail,
                relief=tk.FLAT,
                bg='white',
                activebackground='#e3f2fd',
                command=lambda: self.show_result_actions(result)
            )
            img_button.pack(pady=1)
            img_button.image = thumbnail  # Keep reference
            
            # Tab label with icon
            tab_icons = {
                "Nano Banana": "🍌",
                "SeedEdit": "✨", 
                "Upscaler": "🔍",
                "Wan 2.2": "🎬",
                "SeedDance": "🕺"
            }
            
            icon = tab_icons.get(result['tab_name'], "🎨")
            tab_label = ttk.Label(
                parent,
                text=f"{icon} {result['tab_name']}",
                font=('Arial', 6),
                foreground='#666666'
            )
            tab_label.pack()
            
            # Timestamp
            time_str = datetime.fromtimestamp(result['timestamp']).strftime("%m/%d %H:%M")
            time_label = ttk.Label(
                parent,
                text=time_str,
                font=('Arial', 5),
                foreground='#999999'
            )
            time_label.pack()
            
            # Add hover tooltip
            self.create_tooltip(img_button, result)
            
        except Exception as e:
            logger.error(f"Error creating result item: {e}")
            # Show error placeholder
            error_label = ttk.Label(parent, text="❌\nError", font=('Arial', 8))
            error_label.pack(pady=10)
    
    def load_thumbnail(self, image_path):
        """Load and create thumbnail for image"""
        try:
            with Image.open(image_path) as img:
                # Convert to RGB if necessary
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")
                
                # Create thumbnail
                img.thumbnail(self.thumbnail_size, Image.Resampling.LANCZOS)
                
                # Convert to PhotoImage
                return ImageTk.PhotoImage(img)
                
        except Exception as e:
            logger.error(f"Error loading thumbnail for {image_path}: {e}")
            
            # Create error placeholder
            placeholder = Image.new('RGB', self.thumbnail_size, color='#f0f0f0')
            return ImageTk.PhotoImage(placeholder)
    
    def create_tooltip(self, widget, result):
        """Create hover tooltip for result item"""
        def show_tooltip(event):
            # Create tooltip with metadata
            tooltip_text = f"File: {result['filename']}\n"
            tooltip_text += f"Generated: {datetime.fromtimestamp(result['timestamp']).strftime('%Y-%m-%d %H:%M:%S')}\n"
            tooltip_text += f"Tab: {result['tab_name']}\n"
            
            # Add metadata if available
            if result['metadata'] and 'prompt' in result['metadata']:
                prompt = result['metadata']['prompt']
                if prompt:  # Check if prompt is not None
                    prompt_text = prompt[:50] + "..." if len(prompt) > 50 else prompt
                    tooltip_text += f"Prompt: {prompt_text}\n"
            
            tooltip_text += "\nClick to use in other tabs"
            
            # Simple tooltip implementation
            widget.config(cursor="hand2")
        
        def hide_tooltip(event):
            widget.config(cursor="")
        
        widget.bind("<Enter>", show_tooltip)
        widget.bind("<Leave>", hide_tooltip)
    
    def show_result_actions(self, result):
        """Show action menu for selected result"""
        # Create popup menu
        popup = tk.Menu(self.parent, tearoff=0)
        
        # Add "Send To" options
        navigator = CrossTabNavigator(self.main_app)
        
        # Determine current tab to exclude from targets
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
        
        # Add other actions
        popup.add_separator()
        popup.add_command(
            label="📁 Show in Folder",
            command=lambda: self.show_in_folder(result['image_path'])
        )
        popup.add_command(
            label="🗑️ Delete",
            command=lambda: self.delete_result(result)
        )
        
        # Show popup at mouse position
        try:
            popup.post(self.parent.winfo_pointerx(), self.parent.winfo_pointery())
        finally:
            popup.grab_release()
    
    def get_current_tab_name(self):
        """Get the name of currently active tab"""
        try:
            if hasattr(self.main_app, 'notebook'):
                current_index = self.main_app.notebook.index(self.main_app.notebook.select())
                tab_names = ["Nano Banana Editor", "SeedEdit", "Image Upscaler", "Wan 2.2", "SeedDance"]
                if 0 <= current_index < len(tab_names):
                    return tab_names[current_index]
        except:
            pass
        return "Unknown"
    
    def send_result_to_tab(self, result, target_tab_id, target_tab_name):
        """Send result to specified tab"""
        try:
            navigator = CrossTabNavigator(self.main_app)
            success = navigator.send_to_tab(
                result['image_path'], 
                target_tab_id, 
                target_tab_name, 
                result['tab_name']
            )
            
            if success:
                show_success(
                    "Image Sent!",
                    f"Result from {result['tab_name']} sent to {target_tab_name}.\n\n"
                    f"You are now on the {target_tab_name} tab."
                )
                
        except Exception as e:
            logger.error(f"Error sending result to tab: {e}")
            show_error("Error", f"Failed to send image to {target_tab_name}: {str(e)}")
    
    def show_in_folder(self, image_path):
        """Show image in file explorer"""
        try:
            import subprocess
            import platform
            
            if platform.system() == "Windows":
                subprocess.run(f'explorer /select,"{image_path}"', shell=True)
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", "-R", image_path])
            else:  # Linux
                subprocess.run(["xdg-open", os.path.dirname(image_path)])
                
        except Exception as e:
            logger.error(f"Error showing file in folder: {e}")
            show_error("Error", f"Could not open folder: {str(e)}")
    
    def delete_result(self, result):
        """Delete result files"""
        try:
            from tkinter import messagebox
            
            # Confirm deletion
            if messagebox.askyesno(
                "Delete Result", 
                f"Delete this result?\n\n{result['filename']}\n\nThis cannot be undone."
            ):
                # Delete image file
                if os.path.exists(result['image_path']):
                    os.remove(result['image_path'])
                
                # Delete metadata file if exists
                json_path = os.path.splitext(result['image_path'])[0] + ".json"
                if os.path.exists(json_path):
                    os.remove(json_path)
                
                # Refresh display
                self.refresh_results()
                show_success("Deleted", "Result deleted successfully.")
                
        except Exception as e:
            logger.error(f"Error deleting result: {e}")
            show_error("Error", f"Failed to delete result: {str(e)}")
    
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
