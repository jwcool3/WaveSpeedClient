"""
Result Comparison Studio

A dedicated tool for comparing multiple generated results side-by-side.
Features:
- Select multiple results from recent results
- Side-by-side comparison view
- Overlay blend comparison
- Difference highlighting
- Prompt/settings comparison
- Export comparison images
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk, ImageDraw, ImageFont
import os
from typing import List, Dict, Any, Optional
from core.logger import get_logger
import json

logger = get_logger()


class ResultComparisonStudio:
    """
    Comparison studio for analyzing multiple results
    """
    
    def __init__(self, parent, recent_results_panel):
        """
        Initialize comparison studio
        
        Args:
            parent: Parent window
            recent_results_panel: Reference to recent results panel
        """
        self.parent = parent
        self.recent_results_panel = recent_results_panel
        
        # Selected results for comparison
        self.selected_results = []
        self.max_selections = 4  # Compare up to 4 results
        
        # Display state
        self.comparison_mode = "side_by_side"  # side_by_side, overlay, difference, grid
        self.overlay_opacity = 0.5
        self.zoom_level = 1.0  # Zoom for comparison view
        
        # Photo references (prevent garbage collection)
        self.photo_refs = []
        
        # Create dialog
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("🔍 Result Comparison Studio")
        self.dialog.geometry("1400x900")
        self.dialog.transient(parent)
        
        # Bind keyboard shortcuts
        self._setup_keyboard_shortcuts()
        
        self._create_ui()
        
        # Auto-select last two results for quick comparison
        self._auto_select_recent()
        
        logger.info("Result Comparison Studio opened")
    
    def _create_ui(self):
        """Create comparison studio UI"""
        # Main container
        main_frame = ttk.Frame(self.dialog)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create paned window for selection panel and comparison view
        paned = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)
        
        # Left panel: Result selection
        left_panel = ttk.Frame(paned, padding="10")
        paned.add(left_panel, weight=1)
        
        # Right panel: Comparison view
        right_panel = ttk.Frame(paned, padding="10")
        paned.add(right_panel, weight=3)
        
        # Setup left panel (result selector)
        self._setup_selection_panel(left_panel)
        
        # Setup right panel (comparison view)
        self._setup_comparison_panel(right_panel)
        
        # Bottom controls
        self._setup_bottom_controls()
    
    def _setup_selection_panel(self, parent):
        """Setup result selection panel"""
        # Title
        ttk.Label(
            parent,
            text="📋 Select Results to Compare",
            font=('Arial', 11, 'bold')
        ).pack(pady=(0, 10))
        
        # Info label
        self.selection_info = ttk.Label(
            parent,
            text=f"Selected: 0/{self.max_selections}",
            font=('Arial', 9),
            foreground="gray"
        )
        self.selection_info.pack(pady=(0, 10))
        
        # Scrollable list of results
        list_frame = ttk.Frame(parent)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.results_listbox = tk.Listbox(
            list_frame,
            selectmode=tk.MULTIPLE,
            yscrollcommand=scrollbar.set,
            font=('Arial', 9)
        )
        self.results_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.results_listbox.yview)
        
        # Bind selection event
        self.results_listbox.bind('<<ListboxSelect>>', self._on_result_selected)
        
        # Load available results
        self._load_available_results()
        
        # Action buttons
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(pady=(10, 0), fill=tk.X)
        
        ttk.Button(
            btn_frame,
            text="Compare Selected",
            command=self._compare_selected,
            width=20
        ).pack(fill=tk.X, pady=2)
        
        ttk.Button(
            btn_frame,
            text="Clear Selection",
            command=self._clear_selection,
            width=20
        ).pack(fill=tk.X, pady=2)
        
        ttk.Button(
            btn_frame,
            text="Swap First Two",
            command=self._swap_selections,
            width=20
        ).pack(fill=tk.X, pady=2)
        
        ttk.Button(
            btn_frame,
            text="Refresh List",
            command=self._load_available_results,
            width=20
        ).pack(fill=tk.X, pady=2)
        
        # Help button
        ttk.Button(
            btn_frame,
            text="⌨️ Shortcuts",
            command=self._show_shortcuts_help,
            width=20
        ).pack(fill=tk.X, pady=(10, 2))
    
    def _setup_comparison_panel(self, parent):
        """Setup comparison view panel"""
        # Controls at top
        controls_frame = ttk.Frame(parent)
        controls_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Left controls: Mode selector
        left_controls = ttk.Frame(controls_frame)
        left_controls.pack(side=tk.LEFT)
        
        ttk.Label(left_controls, text="View Mode:", font=('Arial', 9, 'bold')).pack(side=tk.LEFT, padx=(0, 10))
        
        self.mode_var = tk.StringVar(value="side_by_side")
        modes = [
            ("Side-by-Side", "side_by_side"),
            ("Overlay", "overlay"),
            ("Difference", "difference"),
            ("Grid", "grid")
        ]
        
        for text, value in modes:
            ttk.Radiobutton(
                left_controls,
                text=text,
                variable=self.mode_var,
                value=value,
                command=self._on_mode_changed
            ).pack(side=tk.LEFT, padx=5)
        
        # Right controls: Zoom and opacity
        right_controls = ttk.Frame(controls_frame)
        right_controls.pack(side=tk.RIGHT)
        
        # Zoom controls
        zoom_frame = ttk.Frame(right_controls)
        zoom_frame.pack(side=tk.LEFT, padx=(0, 15))
        
        ttk.Label(zoom_frame, text="Zoom:", font=('Arial', 9)).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(zoom_frame, text="−", width=3, command=self._zoom_out).pack(side=tk.LEFT, padx=1)
        self.zoom_label = ttk.Label(zoom_frame, text="100%", width=6, font=('Arial', 9))
        self.zoom_label.pack(side=tk.LEFT, padx=3)
        ttk.Button(zoom_frame, text="+", width=3, command=self._zoom_in).pack(side=tk.LEFT, padx=1)
        ttk.Button(zoom_frame, text="Fit", width=4, command=self._zoom_fit).pack(side=tk.LEFT, padx=(5, 0))
        
        # Opacity slider (for overlay mode)
        self.opacity_frame = ttk.Frame(right_controls)
        self.opacity_frame.pack(side=tk.LEFT, padx=10)
        
        ttk.Label(self.opacity_frame, text="Blend:", font=('Arial', 9)).pack(side=tk.LEFT, padx=(0, 5))
        
        self.opacity_var = tk.DoubleVar(value=50)
        self.opacity_slider = ttk.Scale(
            self.opacity_frame,
            from_=0,
            to=100,
            variable=self.opacity_var,
            orient=tk.HORIZONTAL,
            length=150,
            command=self._on_opacity_changed
        )
        self.opacity_slider.pack(side=tk.LEFT)
        
        self.opacity_label = ttk.Label(self.opacity_frame, text="50%", width=5, font=('Arial', 9))
        self.opacity_label.pack(side=tk.LEFT, padx=(5, 0))
        
        # Initially hide opacity controls
        self.opacity_frame.pack_forget()
        
        # Comparison display area
        display_frame = ttk.LabelFrame(parent, text="Comparison View", padding="10")
        display_frame.pack(fill=tk.BOTH, expand=True)
        
        # Canvas for image display
        self.comparison_canvas = tk.Canvas(
            display_frame,
            bg='#2b2b2b',
            highlightthickness=0
        )
        self.comparison_canvas.pack(fill=tk.BOTH, expand=True)
        
        # Metadata/Prompt display
        metadata_frame = ttk.LabelFrame(parent, text="Prompts & Settings", padding="10")
        metadata_frame.pack(fill=tk.BOTH, pady=(10, 0))
        
        # Scrollable text area
        text_container = ttk.Frame(metadata_frame)
        text_container.pack(fill=tk.BOTH, expand=True)
        
        text_scrollbar = ttk.Scrollbar(text_container)
        text_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.metadata_text = tk.Text(
            text_container,
            height=8,
            wrap=tk.WORD,
            yscrollcommand=text_scrollbar.set,
            font=('Consolas', 9)
        )
        self.metadata_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        text_scrollbar.config(command=self.metadata_text.yview)
    
    def _setup_bottom_controls(self):
        """Setup bottom control buttons"""
        bottom_frame = ttk.Frame(self.dialog)
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)
        
        ttk.Button(
            bottom_frame,
            text="💾 Export Comparison",
            command=self._export_comparison,
            width=20
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            bottom_frame,
            text="📋 Copy Prompts",
            command=self._copy_prompts,
            width=20
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            bottom_frame,
            text="Close",
            command=self.dialog.destroy,
            width=15
        ).pack(side=tk.RIGHT, padx=5)
    
    def _load_available_results(self):
        """Load available results from recent results panel"""
        try:
            self.results_listbox.delete(0, tk.END)
            
            # Get results from recent results panel
            if not hasattr(self.recent_results_panel, 'loaded_results'):
                logger.warning("No results available to compare")
                return
            
            results = self.recent_results_panel.loaded_results
            
            if not results:
                self.results_listbox.insert(tk.END, "No results available")
                return
            
            # Add each result to listbox
            for i, result in enumerate(results):
                # Extract basic info for display
                timestamp = result.get('timestamp', 'Unknown')
                tab_id = result.get('tab_id', '?')
                
                # Try to get a short prompt preview
                metadata_path = result.get('metadata_path', '')
                prompt_preview = "No prompt"
                
                if metadata_path and os.path.exists(metadata_path):
                    try:
                        with open(metadata_path, 'r', encoding='utf-8') as f:
                            metadata = json.load(f)
                            prompt = metadata.get('prompt', '')
                            if prompt:
                                prompt_preview = prompt[:40] + "..." if len(prompt) > 40 else prompt
                    except:
                        pass
                
                display_text = f"Tab {tab_id} | {timestamp} | {prompt_preview}"
                self.results_listbox.insert(tk.END, display_text)
            
            logger.info(f"Loaded {len(results)} results for comparison")
            
        except Exception as e:
            logger.error(f"Error loading results: {e}")
            messagebox.showerror("Error", f"Failed to load results: {str(e)}")
    
    def _on_result_selected(self, event):
        """Handle result selection change"""
        try:
            selections = self.results_listbox.curselection()
            
            if len(selections) > self.max_selections:
                # Limit selections
                self.results_listbox.selection_clear(selections[-1])
                messagebox.showwarning(
                    "Selection Limit",
                    f"You can compare up to {self.max_selections} results at once."
                )
                return
            
            # Update info label
            self.selection_info.config(text=f"Selected: {len(selections)}/{self.max_selections}")
            
        except Exception as e:
            logger.error(f"Error handling selection: {e}")
    
    def _compare_selected(self):
        """Start comparison of selected results"""
        try:
            selections = self.results_listbox.curselection()
            
            if len(selections) < 2:
                messagebox.showwarning("Selection Required", "Please select at least 2 results to compare.")
                return
            
            # Get selected results
            results = self.recent_results_panel.loaded_results
            self.selected_results = [results[i] for i in selections]
            
            logger.info(f"Comparing {len(self.selected_results)} results")
            
            # Display comparison
            self._update_comparison_display()
            self._update_metadata_display()
            
        except Exception as e:
            logger.error(f"Error comparing results: {e}")
            messagebox.showerror("Error", f"Failed to compare results: {str(e)}")
    
    def _clear_selection(self):
        """Clear all selections"""
        self.results_listbox.selection_clear(0, tk.END)
        self.selected_results = []
        self.selection_info.config(text=f"Selected: 0/{self.max_selections}")
        
        # Clear display
        self.comparison_canvas.delete("all")
        self.metadata_text.delete('1.0', tk.END)
    
    def _on_mode_changed(self):
        """Handle comparison mode change"""
        mode = self.mode_var.get()
        
        # Show/hide opacity controls for overlay mode
        if mode == "overlay":
            self.opacity_frame.pack(side=tk.RIGHT, padx=10)
        else:
            self.opacity_frame.pack_forget()
        
        # Update display
        self._update_comparison_display()
    
    def _on_opacity_changed(self, value):
        """Handle opacity slider change"""
        opacity = int(float(value))
        self.opacity_label.config(text=f"{opacity}%")
        self.overlay_opacity = opacity / 100.0
        
        # Update display if in overlay mode
        if self.mode_var.get() == "overlay":
            self._update_comparison_display()
    
    def _update_comparison_display(self):
        """Update comparison display based on current mode"""
        try:
            if not self.selected_results:
                return
            
            mode = self.mode_var.get()
            
            # Clear canvas
            self.comparison_canvas.delete("all")
            
            if mode == "side_by_side":
                self._display_side_by_side()
            elif mode == "overlay":
                self._display_overlay()
            elif mode == "difference":
                self._display_difference()
            elif mode == "grid":
                self._display_grid()
            
        except Exception as e:
            logger.error(f"Error updating comparison display: {e}")
    
    def _display_side_by_side(self):
        """Display results side-by-side"""
        try:
            num_results = len(self.selected_results)
            
            # Get canvas size
            canvas_width = self.comparison_canvas.winfo_width()
            canvas_height = self.comparison_canvas.winfo_height()
            
            if canvas_width < 100:  # Canvas not yet rendered
                canvas_width = 1200
            if canvas_height < 100:
                canvas_height = 600
            
            # Calculate layout
            cols = min(num_results, 2)
            rows = (num_results + cols - 1) // cols
            
            cell_width = canvas_width // cols
            cell_height = canvas_height // rows
            
            # Display each result
            for i, result in enumerate(self.selected_results):
                row = i // cols
                col = i % cols
                
                x = col * cell_width
                y = row * cell_height
                
                self._display_result_at(result, x, y, cell_width, cell_height, i + 1)
            
        except Exception as e:
            logger.error(f"Error displaying side-by-side: {e}")
    
    def _display_result_at(self, result, x, y, width, height, label_num):
        """Display a single result at specified position"""
        try:
            image_path = result.get('path')
            
            if not image_path or not os.path.exists(image_path):
                # Draw placeholder
                self.comparison_canvas.create_rectangle(
                    x, y, x + width, y + height,
                    fill='#3a3a3a',
                    outline='#555555'
                )
                self.comparison_canvas.create_text(
                    x + width // 2, y + height // 2,
                    text=f"Result {label_num}\n(Image not found)",
                    fill='gray',
                    font=('Arial', 12)
                )
                return
            
            # Load and resize image
            img = Image.open(image_path)
            
            # Calculate fit size
            img_ratio = img.width / img.height
            cell_ratio = width / height
            
            if img_ratio > cell_ratio:
                # Fit to width
                new_width = width - 20
                new_height = int(new_width / img_ratio)
            else:
                # Fit to height
                new_height = height - 40
                new_width = int(new_height * img_ratio)
            
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Add label
            draw = ImageDraw.Draw(img)
            try:
                font = ImageFont.truetype("arial.ttf", 16)
            except:
                font = ImageFont.load_default()
            
            draw.rectangle([(0, 0), (100, 30)], fill='black')
            draw.text((10, 5), f"Result {label_num}", fill='white', font=font)
            
            # Convert to PhotoImage
            photo = ImageTk.PhotoImage(img)
            
            # Center in cell
            img_x = x + (width - new_width) // 2
            img_y = y + (height - new_height) // 2
            
            # Display
            self.comparison_canvas.create_image(img_x, img_y, anchor=tk.NW, image=photo)
            
            # Keep reference
            if not hasattr(self, 'photo_refs'):
                self.photo_refs = []
            self.photo_refs.append(photo)
            
        except Exception as e:
            logger.error(f"Error displaying result: {e}")
    
    def _display_overlay(self):
        """Display results as overlay blend"""
        try:
            if len(self.selected_results) < 2:
                messagebox.showinfo("Info", "Overlay mode requires at least 2 results.")
                return
            
            # Use first two results for overlay
            result1 = self.selected_results[0]
            result2 = self.selected_results[1]
            
            path1 = result1.get('path')
            path2 = result2.get('path')
            
            if not path1 or not path2 or not os.path.exists(path1) or not os.path.exists(path2):
                return
            
            # Load images
            img1 = Image.open(path1).convert('RGBA')
            img2 = Image.open(path2).convert('RGBA')
            
            # Resize to match
            if img1.size != img2.size:
                # Resize to largest dimensions
                max_width = max(img1.width, img2.width)
                max_height = max(img1.height, img2.height)
                img1 = img1.resize((max_width, max_height), Image.Resampling.LANCZOS)
                img2 = img2.resize((max_width, max_height), Image.Resampling.LANCZOS)
            
            # Blend
            blended = Image.blend(img1, img2, self.overlay_opacity)
            
            # Fit to canvas
            canvas_width = self.comparison_canvas.winfo_width() or 1200
            canvas_height = self.comparison_canvas.winfo_height() or 600
            
            # Calculate fit size
            img_ratio = blended.width / blended.height
            canvas_ratio = canvas_width / canvas_height
            
            if img_ratio > canvas_ratio:
                new_width = canvas_width - 40
                new_height = int(new_width / img_ratio)
            else:
                new_height = canvas_height - 40
                new_width = int(new_height * img_ratio)
            
            blended = blended.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Convert to PhotoImage
            photo = ImageTk.PhotoImage(blended)
            
            # Center on canvas
            x = (canvas_width - new_width) // 2
            y = (canvas_height - new_height) // 2
            
            self.comparison_canvas.create_image(x, y, anchor=tk.NW, image=photo)
            self.photo_refs = [photo]
            
        except Exception as e:
            logger.error(f"Error displaying overlay: {e}")
    
    def _display_difference(self):
        """Display pixel difference between results"""
        try:
            if len(self.selected_results) < 2:
                messagebox.showinfo("Info", "Difference mode requires at least 2 results.")
                return
            
            # Use first two results
            result1 = self.selected_results[0]
            result2 = self.selected_results[1]
            
            path1 = result1.get('path')
            path2 = result2.get('path')
            
            if not path1 or not path2 or not os.path.exists(path1) or not os.path.exists(path2):
                return
            
            # Load images
            img1 = Image.open(path1).convert('RGB')
            img2 = Image.open(path2).convert('RGB')
            
            # Resize to match
            if img1.size != img2.size:
                max_width = max(img1.width, img2.width)
                max_height = max(img1.height, img2.height)
                img1 = img1.resize((max_width, max_height), Image.Resampling.LANCZOS)
                img2 = img2.resize((max_width, max_height), Image.Resampling.LANCZOS)
            
            # Calculate difference using numpy
            import numpy as np
            arr1 = np.array(img1, dtype=np.float32)
            arr2 = np.array(img2, dtype=np.float32)
            
            # Absolute difference
            diff = np.abs(arr1 - arr2).astype(np.uint8)
            
            # Enhance difference (multiply by factor)
            diff = np.clip(diff * 3, 0, 255).astype(np.uint8)
            
            # Convert back to image
            diff_img = Image.fromarray(diff, 'RGB')
            
            # Fit to canvas
            canvas_width = self.comparison_canvas.winfo_width() or 1200
            canvas_height = self.comparison_canvas.winfo_height() or 600
            
            img_ratio = diff_img.width / diff_img.height
            canvas_ratio = canvas_width / canvas_height
            
            if img_ratio > canvas_ratio:
                new_width = canvas_width - 40
                new_height = int(new_width / img_ratio)
            else:
                new_height = canvas_height - 40
                new_width = int(new_height * img_ratio)
            
            diff_img = diff_img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Convert to PhotoImage
            photo = ImageTk.PhotoImage(diff_img)
            
            # Center on canvas
            x = (canvas_width - new_width) // 2
            y = (canvas_height - new_height) // 2
            
            self.comparison_canvas.create_image(x, y, anchor=tk.NW, image=photo)
            self.photo_refs = [photo]
            
        except Exception as e:
            logger.error(f"Error displaying difference: {e}")
    
    def _display_grid(self):
        """Display results in 2x2 grid"""
        self._display_side_by_side()  # Same as side-by-side for now
    
    def _update_metadata_display(self):
        """Update metadata/prompt display with enhanced details"""
        try:
            self.metadata_text.delete('1.0', tk.END)
            
            for i, result in enumerate(self.selected_results, 1):
                metadata_path = result.get('metadata_path', '')
                image_path = result.get('path', '')
                
                self.metadata_text.insert(tk.END, f"\n{'='*80}\n", 'header')
                self.metadata_text.insert(tk.END, f"RESULT {i}\n", 'header')
                self.metadata_text.insert(tk.END, f"{'='*80}\n\n", 'header')
                
                # File information
                if image_path and os.path.exists(image_path):
                    try:
                        # Get file size
                        file_size = os.path.getsize(image_path)
                        file_size_mb = file_size / (1024 * 1024)
                        
                        # Get image dimensions
                        with Image.open(image_path) as img:
                            img_width, img_height = img.size
                            img_format = img.format
                        
                        self.metadata_text.insert(tk.END, "File Info:\n", 'bold')
                        self.metadata_text.insert(tk.END, f"  Dimensions: {img_width} × {img_height} px\n")
                        self.metadata_text.insert(tk.END, f"  File Size: {file_size_mb:.2f} MB\n")
                        self.metadata_text.insert(tk.END, f"  Format: {img_format}\n")
                        self.metadata_text.insert(tk.END, f"  Path: {os.path.basename(image_path)}\n\n")
                    except Exception as e:
                        logger.debug(f"Error reading image info: {e}")
                
                # Prompt and settings from metadata
                if metadata_path and os.path.exists(metadata_path):
                    try:
                        with open(metadata_path, 'r', encoding='utf-8') as f:
                            metadata = json.load(f)
                        
                        # Display prompt
                        prompt = metadata.get('prompt', 'No prompt')
                        self.metadata_text.insert(tk.END, "Prompt:\n", 'bold')
                        self.metadata_text.insert(tk.END, f"{prompt}\n\n")
                        
                        # Display settings
                        settings = metadata.get('settings', {})
                        if settings:
                            self.metadata_text.insert(tk.END, "Generation Settings:\n", 'bold')
                            width = settings.get('width', 'N/A')
                            height = settings.get('height', 'N/A')
                            seed = settings.get('seed', 'N/A')
                            sync_mode = settings.get('sync_mode', False)
                            self.metadata_text.insert(tk.END, f"  Target Resolution: {width}x{height}\n")
                            self.metadata_text.insert(tk.END, f"  Seed: {seed}\n")
                            self.metadata_text.insert(tk.END, f"  Sync Mode: {'Yes' if sync_mode else 'No'}\n")
                        
                        # Display timestamp
                        timestamp = metadata.get('timestamp', 'Unknown')
                        tab_id = metadata.get('tab_id', '?')
                        self.metadata_text.insert(tk.END, f"\nGenerated: {timestamp}\n")
                        self.metadata_text.insert(tk.END, f"Tab: Seedream V4 #{tab_id}\n")
                        
                    except Exception as e:
                        self.metadata_text.insert(tk.END, f"Error loading metadata: {str(e)}\n")
                else:
                    self.metadata_text.insert(tk.END, "No metadata available\n")
            
            # Configure tags
            self.metadata_text.tag_config('header', foreground='blue', font=('Consolas', 9, 'bold'))
            self.metadata_text.tag_config('bold', font=('Consolas', 9, 'bold'))
            
        except Exception as e:
            logger.error(f"Error updating metadata display: {e}")
    
    def _export_comparison(self):
        """Export comparison as image"""
        try:
            if not self.selected_results:
                messagebox.showwarning("No Comparison", "Please compare some results first.")
                return
            
            # Get save path
            file_path = filedialog.asksaveasfilename(
                title="Export Comparison",
                defaultextension=".png",
                filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*")]
            )
            
            if not file_path:
                return
            
            # Create comparison image based on current mode
            mode = self.mode_var.get()
            
            if mode == "side_by_side" or mode == "grid":
                # Create side-by-side composite
                images = []
                for result in self.selected_results:
                    path = result.get('path')
                    if path and os.path.exists(path):
                        images.append(Image.open(path))
                
                if not images:
                    return
                
                # Calculate layout
                cols = min(len(images), 2)
                rows = (len(images) + cols - 1) // cols
                
                # Resize all to same height
                target_height = 800
                resized = []
                for img in images:
                    ratio = target_height / img.height
                    new_width = int(img.width * ratio)
                    resized.append(img.resize((new_width, target_height), Image.Resampling.LANCZOS))
                
                # Calculate total size
                max_width = max(img.width for img in resized)
                total_width = max_width * cols
                total_height = target_height * rows
                
                # Create composite
                composite = Image.new('RGB', (total_width, total_height), (40, 40, 40))
                
                for i, img in enumerate(resized):
                    row = i // cols
                    col = i % cols
                    x = col * max_width + (max_width - img.width) // 2
                    y = row * target_height
                    composite.paste(img, (x, y))
                    
                    # Add label
                    draw = ImageDraw.Draw(composite)
                    try:
                        font = ImageFont.truetype("arial.ttf", 24)
                    except:
                        font = ImageFont.load_default()
                    draw.rectangle([(x, y), (x + 120, y + 40)], fill='black')
                    draw.text((x + 10, y + 5), f"Result {i+1}", fill='white', font=font)
                
                composite.save(file_path, quality=95)
                
            elif mode == "overlay" and len(self.selected_results) >= 2:
                # Save blended overlay
                path1 = self.selected_results[0].get('path')
                path2 = self.selected_results[1].get('path')
                
                img1 = Image.open(path1).convert('RGBA')
                img2 = Image.open(path2).convert('RGBA')
                
                if img1.size != img2.size:
                    max_width = max(img1.width, img2.width)
                    max_height = max(img1.height, img2.height)
                    img1 = img1.resize((max_width, max_height), Image.Resampling.LANCZOS)
                    img2 = img2.resize((max_width, max_height), Image.Resampling.LANCZOS)
                
                blended = Image.blend(img1, img2, self.overlay_opacity)
                blended.save(file_path, quality=95)
            
            messagebox.showinfo("Success", f"Comparison exported to:\n{file_path}")
            logger.info(f"Comparison exported: {file_path}")
            
        except Exception as e:
            logger.error(f"Error exporting comparison: {e}")
            messagebox.showerror("Error", f"Failed to export: {str(e)}")
    
    def _copy_prompts(self):
        """Copy all prompts to clipboard"""
        try:
            prompts_text = ""
            
            for i, result in enumerate(self.selected_results, 1):
                metadata_path = result.get('metadata_path', '')
                
                if metadata_path and os.path.exists(metadata_path):
                    with open(metadata_path, 'r', encoding='utf-8') as f:
                        metadata = json.load(f)
                    
                    prompt = metadata.get('prompt', 'No prompt')
                    prompts_text += f"Result {i}:\n{prompt}\n\n"
            
            if prompts_text:
                self.dialog.clipboard_clear()
                self.dialog.clipboard_append(prompts_text)
                messagebox.showinfo("Success", "Prompts copied to clipboard!")
            else:
                messagebox.showwarning("No Prompts", "No prompts found to copy.")
            
        except Exception as e:
            logger.error(f"Error copying prompts: {e}")
            messagebox.showerror("Error", f"Failed to copy prompts: {str(e)}")


    def _setup_keyboard_shortcuts(self):
        """Setup keyboard shortcuts"""
        self.dialog.bind('<Control-c>', lambda e: self._copy_prompts())
        self.dialog.bind('<Control-e>', lambda e: self._export_comparison())
        self.dialog.bind('<Control-r>', lambda e: self._load_available_results())
        self.dialog.bind('<Control-w>', lambda e: self.dialog.destroy())
        self.dialog.bind('<Escape>', lambda e: self.dialog.destroy())
        
        # Number keys for quick mode switching
        self.dialog.bind('1', lambda e: self.mode_var.set("side_by_side") or self._on_mode_changed())
        self.dialog.bind('2', lambda e: self.mode_var.set("overlay") or self._on_mode_changed())
        self.dialog.bind('3', lambda e: self.mode_var.set("difference") or self._on_mode_changed())
        self.dialog.bind('4', lambda e: self.mode_var.set("grid") or self._on_mode_changed())
        
        # Zoom shortcuts
        self.dialog.bind('<Control-equal>', lambda e: self._zoom_in())  # Ctrl + =
        self.dialog.bind('<Control-plus>', lambda e: self._zoom_in())    # Ctrl + +
        self.dialog.bind('<Control-minus>', lambda e: self._zoom_out())  # Ctrl + -
        self.dialog.bind('<Control-0>', lambda e: self._zoom_fit())       # Ctrl + 0
        
        logger.debug("Keyboard shortcuts configured")
    
    def _auto_select_recent(self):
        """Auto-select the two most recent results for quick comparison"""
        try:
            if not hasattr(self.recent_results_panel, 'loaded_results'):
                return
            
            results = self.recent_results_panel.loaded_results
            if len(results) >= 2:
                # Select last two results
                self.results_listbox.selection_set(len(results) - 2, len(results) - 1)
                self._on_result_selected(None)
                logger.info("Auto-selected 2 most recent results")
                
                # Auto-start comparison
                self.dialog.after(500, self._compare_selected)
        except Exception as e:
            logger.debug(f"Could not auto-select results: {e}")
    
    def _zoom_in(self):
        """Zoom in on comparison view"""
        self.zoom_level = min(3.0, self.zoom_level * 1.25)
        self.zoom_label.config(text=f"{int(self.zoom_level * 100)}%")
        self._update_comparison_display()
        logger.debug(f"Zoomed in to {self.zoom_level:.2f}x")
    
    def _zoom_out(self):
        """Zoom out on comparison view"""
        self.zoom_level = max(0.25, self.zoom_level / 1.25)
        self.zoom_label.config(text=f"{int(self.zoom_level * 100)}%")
        self._update_comparison_display()
        logger.debug(f"Zoomed out to {self.zoom_level:.2f}x")
    
    def _zoom_fit(self):
        """Reset zoom to fit"""
        self.zoom_level = 1.0
        self.zoom_label.config(text="100%")
        self._update_comparison_display()
        logger.debug("Zoom reset to fit")
    
    def _swap_selections(self):
        """Swap the first two selected results"""
        try:
            selections = list(self.results_listbox.curselection())
            
            if len(selections) < 2:
                messagebox.showinfo("Info", "Please select at least 2 results to swap.")
                return
            
            # Swap first two in the selection
            selections[0], selections[1] = selections[1], selections[0]
            
            # Update listbox selection
            self.results_listbox.selection_clear(0, tk.END)
            for idx in selections:
                self.results_listbox.selection_set(idx)
            
            # Refresh comparison if already comparing
            if self.selected_results:
                self._compare_selected()
            
            logger.info("Swapped first two selections")
            
        except Exception as e:
            logger.error(f"Error swapping selections: {e}")
    
    def _show_shortcuts_help(self):
        """Show keyboard shortcuts help dialog"""
        help_text = """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   🔍 COMPARISON STUDIO SHORTCUTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 GENERAL:
  Ctrl+C         Copy all prompts to clipboard
  Ctrl+E         Export comparison image
  Ctrl+R         Refresh results list
  Ctrl+W / Esc   Close studio

🎨 VIEW MODES:
  1              Side-by-Side view
  2              Overlay view
  3              Difference view
  4              Grid view

🔍 ZOOM:
  Ctrl++         Zoom in (25% steps)
  Ctrl+-         Zoom out (25% steps)
  Ctrl+0         Reset zoom to 100%

💡 TIP: Auto-selects last 2 results on open!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        messagebox.showinfo("Keyboard Shortcuts", help_text)


def open_comparison_studio(parent, recent_results_panel):
    """Open result comparison studio"""
    ResultComparisonStudio(parent, recent_results_panel)

