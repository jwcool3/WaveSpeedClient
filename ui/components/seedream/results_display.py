"""
Seedream Results Display Module
Phase 6 of the improved_seedream_layout.py refactoring

This module handles all results display functionality including:
- Results browser with grid layout
- Thumbnail generation and caching
- Download and display logic for single/multiple results
- Result selection and management
- Save functionality for individual results
- Image preview and comparison
- Result metadata tracking
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import requests
import tempfile
import shutil
import os
import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable
from PIL import Image, ImageTk
from core.logger import get_logger

logger = get_logger(__name__)


class ResultsDisplayManager:
    """Manages all results display functionality for Seedream V4"""
    
    def __init__(self, parent_layout):
        """
        Initialize results display manager
        
        Args:
            parent_layout: Reference to the main layout instance
        """
        self.parent_layout = parent_layout
        
        # Results state
        self.completed_results = []  # Store all completed results
        self.result_image_path = None
        self.result_url = None
        
        # Image caching for performance
        self.image_cache = {}
        self.max_cache_size = 20
        
        # Auto-save integration
        self.auto_save_enabled = self._check_auto_save_available()
        
        # UI references
        self.result_canvas = None
        
        # Callbacks
        self.on_result_selected_callback = None
        
        logger.info("ResultsDisplayManager initialized")
    
    def _check_auto_save_available(self) -> bool:
        """Check if auto-save functionality is available"""
        try:
            from core.auto_save import auto_save_manager
            return True
        except ImportError:
            return False
    
    def handle_single_result_ready(self, result_data: Dict[str, Any]) -> None:
        """Handle single result ready for display"""
        try:
            # Get the result image URL
            result_url = result_data.get('result_url') or result_data.get('output_url')
            if not result_url:
                raise ValueError("No result image URL received")
            
            self.result_url = result_url
            self._show_message("🎉 Processing completed!")
            
            # Download and display the result
            self.download_and_display_result(result_url)
            
        except Exception as e:
            logger.error(f"Error handling single result: {e}")
            self._show_message(f"❌ Error handling result: {str(e)}")
    
    def handle_multiple_results_ready(self, completed_tasks: List[Dict[str, Any]]) -> None:
        """Handle multiple results ready for display"""
        try:
            self._show_message(f"🎉 Processing complete! {len(completed_tasks)} results ready")
            
            # Download and display all results
            self.download_and_display_multiple_results(completed_tasks)
            
        except Exception as e:
            logger.error(f"Error handling multiple results: {e}")
            self._show_message(f"❌ Error handling results: {str(e)}")
    
    def download_and_display_result(self, result_url: str) -> None:
        """Download and display a single result"""
        try:
            self._show_message("📥 Downloading result...")
            
            # Download in background thread
            import threading
            threading.Thread(
                target=self._download_single_result_thread,
                args=(result_url,),
                daemon=True
            ).start()
            
        except Exception as e:
            logger.error(f"Error downloading result: {e}")
            self._show_message(f"❌ Download failed: {str(e)}")
    
    def download_and_display_multiple_results(self, completed_tasks: List[Dict[str, Any]]) -> None:
        """Download and display multiple results with auto-save"""
        try:
            self._show_message("📥 Downloading all results...")
            
            # Download in background thread
            import threading
            threading.Thread(
                target=self._download_multiple_results_thread,
                args=(completed_tasks,),
                daemon=True
            ).start()
            
        except Exception as e:
            logger.error(f"Error downloading multiple results: {e}")
            self._show_message(f"❌ Download failed: {str(e)}")
    
    def _download_single_result_thread(self, result_url: str) -> None:
        """Background thread for downloading single result"""
        try:
            # Download the image
            response = requests.get(result_url, timeout=60)
            response.raise_for_status()
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
                temp_file.write(response.content)
                temp_path = temp_file.name
            
            # Auto-save if enabled
            saved_path = None
            if self.auto_save_enabled:
                saved_path = self._auto_save_single_result(temp_path, result_url)
            
            # Use saved path if available, otherwise temp path
            final_path = saved_path or temp_path
            self.result_image_path = final_path
            
            # Schedule UI update on main thread
            self.parent_layout.parent_frame.after(
                0,
                lambda: self._display_single_result(final_path)
            )
            
        except Exception as e:
            logger.error(f"Error downloading single result: {e}")
            self.parent_layout.parent_frame.after(
                0,
                lambda: self._show_message(f"❌ Download failed: {str(e)}")
            )
    
    def _download_multiple_results_thread(self, completed_tasks: List[Dict[str, Any]]) -> None:
        """Background thread for downloading multiple results"""
        try:
            self.completed_results = []
            
            for task_info in completed_tasks:
                try:
                    result_url = task_info.get('result_url')
                    request_num = task_info.get('request_num')
                    seed = task_info.get('seed')
                    
                    if not result_url:
                        self.parent_layout.parent_frame.after(
                            0,
                            lambda n=request_num: self._show_message(f"⚠️ Request {n}: No result URL")
                        )
                        continue
                    
                    self.parent_layout.parent_frame.after(
                        0,
                        lambda n=request_num: self._show_message(f"📥 Downloading result {n}...")
                    )
                    
                    # Download the image
                    response = requests.get(result_url, timeout=60)
                    response.raise_for_status()
                    
                    # Save to temporary file
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
                        temp_file.write(response.content)
                        temp_path = temp_file.name
                    
                    # Auto-save if enabled
                    saved_path = None
                    if self.auto_save_enabled:
                        saved_path = self._auto_save_multiple_result(
                            temp_path, result_url, request_num, seed, task_info.get('settings', {})
                        )
                    
                    # Store result info
                    result_info = {
                        'path': saved_path or temp_path,
                        'url': result_url,
                        'request_num': request_num,
                        'seed': seed,
                        'temp_path': temp_path,
                        'saved_path': saved_path,
                        'settings': task_info.get('settings', {})
                    }
                    self.completed_results.append(result_info)
                    
                    self.parent_layout.parent_frame.after(
                        0,
                        lambda n=request_num: self._show_message(f"✅ Downloaded result {n}")
                    )
                    
                except Exception as e:
                    logger.error(f"Error downloading result {task_info.get('request_num', '?')}: {e}")
                    self.parent_layout.parent_frame.after(
                        0,
                        lambda n=task_info.get('request_num', '?'), err=str(e): self._show_message(f"❌ Result {n} failed: {err}")
                    )
            
            if self.completed_results:
                # Schedule UI update for multiple results
                self.parent_layout.parent_frame.after(
                    0,
                    lambda: self._display_multiple_results()
                )
            else:
                self.parent_layout.parent_frame.after(
                    0,
                    lambda: self._show_message("❌ No results downloaded successfully")
                )
                
        except Exception as e:
            logger.error(f"Error in multiple download thread: {e}")
            self.parent_layout.parent_frame.after(
                0,
                lambda: self._show_message(f"❌ Download failed: {str(e)}")
            )
    
    def _auto_save_single_result(self, temp_path: str, result_url: str) -> Optional[str]:
        """Auto-save single result with metadata"""
        try:
            if not self.auto_save_enabled:
                return None
                
            from core.auto_save import auto_save_manager
            from datetime import datetime
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            prompt_snippet = self._get_prompt_snippet()
            size = self._get_size_string()
            
            filename = f"seedream_v4_{timestamp}_{prompt_snippet}_{size}.png"
            
            # Save image
            result = auto_save_manager.save_image(temp_path, filename, "Seedream_V4")
            
            if result['success']:
                saved_path = result['path']
                
                # Create metadata
                metadata = self._create_result_metadata(result_url, saved_path, single=True)
                
                # Save JSON metadata
                json_path = str(Path(saved_path).with_suffix('.json'))
                try:
                    with open(json_path, 'w', encoding='utf-8') as f:
                        json.dump(metadata, f, indent=2, ensure_ascii=False)
                except Exception as json_error:
                    logger.error(f"Error saving JSON metadata: {json_error}")
                
                return saved_path
            else:
                logger.warning(f"Auto-save failed: {result.get('error', 'Unknown error')}")
                return None
                
        except Exception as e:
            logger.error(f"Error in auto-save single result: {e}")
            return None
    
    def _auto_save_multiple_result(self, temp_path: str, result_url: str, request_num: int, 
                                 seed: int, settings: Dict[str, Any]) -> Optional[str]:
        """Auto-save multiple result with metadata"""
        try:
            if not self.auto_save_enabled:
                return None
                
            from core.auto_save import auto_save_manager
            from datetime import datetime
            
            # Generate filename with request number and seed
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            prompt_snippet = self._get_prompt_snippet()
            size = self._get_size_string()
            
            filename = f"seedream_v4_{timestamp}_{prompt_snippet}_{size}_req{request_num}_seed{seed}.png"
            
            # Save image
            result = auto_save_manager.save_image(temp_path, filename, "Seedream_V4")
            
            if result['success']:
                saved_path = result['path']
                
                # Create metadata
                metadata = self._create_result_metadata(
                    result_url, saved_path, single=False, request_num=request_num, 
                    seed=seed, settings=settings
                )
                
                # Save JSON metadata
                json_path = str(Path(saved_path).with_suffix('.json'))
                try:
                    with open(json_path, 'w', encoding='utf-8') as f:
                        json.dump(metadata, f, indent=2, ensure_ascii=False)
                except Exception as json_error:
                    logger.error(f"Error saving JSON metadata for result {request_num}: {json_error}")
                
                return saved_path
            else:
                logger.warning(f"Auto-save failed for result {request_num}: {result.get('error', 'Unknown error')}")
                return None
                
        except Exception as e:
            logger.error(f"Error in auto-save result {request_num}: {e}")
            return None
    
    def _create_result_metadata(self, result_url: str, saved_path: str, single: bool = True,
                              request_num: Optional[int] = None, seed: Optional[int] = None,
                              settings: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create metadata for saved result"""
        try:
            from datetime import datetime
            
            metadata = {
                "ai_model": "seedream_v4",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "prompt": self._get_current_prompt(),
                "result_url": result_url,
                "result_path": saved_path,
                "result_filename": Path(saved_path).name
            }
            
            # Add settings
            if settings:
                metadata["settings"] = settings
            else:
                metadata["settings"] = self._get_current_settings()
            
            # Add multi-request info if applicable
            if not single:
                metadata["multi_request"] = True
                metadata["request_number"] = request_num
                metadata["seed"] = seed
                metadata["total_requests"] = len(self.completed_results) + 1  # +1 for current
            
            # Add input image info
            if hasattr(self.parent_layout, 'selected_image_path'):
                metadata["input_images"] = [self.parent_layout.selected_image_path]
            
            return metadata
            
        except Exception as e:
            logger.error(f"Error creating result metadata: {e}")
            return {}
    
    def _display_single_result(self, result_path: str) -> None:
        """Display single result in UI"""
        try:
            # Display result in image panel
            if hasattr(self.parent_layout, 'display_image_in_panel'):
                self.parent_layout.display_image_in_panel(result_path, "result")
            
            self._show_message("✅ Result ready!")
            
            # Enable result actions
            self._enable_result_actions()
            
            # Trigger callback if set
            if self.on_result_selected_callback:
                self.on_result_selected_callback(result_path)
                
        except Exception as e:
            logger.error(f"Error displaying single result: {e}")
    
    def _display_multiple_results(self) -> None:
        """Display multiple results"""
        try:
            # Display first result in main panel
            if self.completed_results:
                first_result = self.completed_results[0]
                self.result_image_path = first_result['path']
                
                if hasattr(self.parent_layout, 'display_image_in_panel'):
                    self.parent_layout.display_image_in_panel(first_result['path'], "result")
                
                self._show_message(f"✅ {len(self.completed_results)} results ready")
                
                # Show results browser
                self.show_results_browser()
                
                # Enable result actions
                self._enable_result_actions()
            
        except Exception as e:
            logger.error(f"Error displaying multiple results: {e}")
    
    def show_results_browser(self) -> None:
        """Show a browser window for all generated results"""
        try:
            if not self.completed_results:
                messagebox.showinfo("No Results", "No results to display.")
                return
            
            # Create results browser window
            results_window = tk.Toplevel(self.parent_layout.parent_frame)
            results_window.title(f"Seedream Results ({len(self.completed_results)} images)")
            results_window.geometry("1000x700")
            results_window.resizable(True, True)
            
            # Main container
            main_frame = ttk.Frame(results_window, padding="10")
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # Title
            title_label = ttk.Label(
                main_frame,
                text=f"🎨 Generated {len(self.completed_results)} Results",
                font=('Arial', 14, 'bold')
            )
            title_label.pack(pady=(0, 10))
            
            # Info label
            info_label = ttk.Label(
                main_frame,
                text="Click any image to use it as the main result, or use the buttons to save individual results",
                font=('Arial', 9),
                foreground="gray"
            )
            info_label.pack(pady=(0, 10))
            
            # Create scrollable frame for results
            canvas = tk.Canvas(main_frame, bg='white', highlightthickness=0)
            scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
            scrollable_frame = ttk.Frame(canvas)
            
            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )
            
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            # Display each result in a grid (3 columns)
            cols = 3
            for idx, result_info in enumerate(self.completed_results):
                row = idx // cols
                col = idx % cols
                
                # Create frame for this result
                result_frame = ttk.LabelFrame(
                    scrollable_frame,
                    text=f"Result #{result_info['request_num']} (Seed: {result_info['seed']})",
                    padding="5"
                )
                result_frame.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
                
                self._create_result_item(result_frame, result_info, results_window)
            
            # Configure grid weights
            for i in range(cols):
                scrollable_frame.columnconfigure(i, weight=1)
            
            # Pack canvas and scrollbar
            canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            # Bottom buttons
            bottom_frame = ttk.Frame(main_frame)
            bottom_frame.pack(fill=tk.X, pady=(10, 0))
            
            # Save all button
            save_all_btn = ttk.Button(
                bottom_frame,
                text="💾 Save All Results",
                command=self.save_all_results
            )
            save_all_btn.pack(side=tk.LEFT)
            
            # Close button
            close_btn = ttk.Button(
                bottom_frame,
                text="Close",
                command=results_window.destroy
            )
            close_btn.pack(side=tk.RIGHT)
            
            # Bind mousewheel
            def on_mousewheel(event):
                canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            canvas.bind_all("<MouseWheel>", on_mousewheel)
            
        except Exception as e:
            logger.error(f"Error creating results browser: {e}")
            messagebox.showerror("Error", f"Failed to create results browser: {str(e)}")
    
    def _create_result_item(self, parent_frame: tk.Widget, result_info: Dict[str, Any], 
                          browser_window: tk.Toplevel) -> None:
        """Create a result item widget"""
        try:
            # Load and display thumbnail
            thumbnail = self._create_thumbnail(result_info['path'])
            
            if thumbnail:
                # Display image
                img_label = tk.Label(parent_frame, image=thumbnail, cursor="hand2")
                img_label.image = thumbnail  # Keep a reference
                img_label.pack()
                
                # Bind click to use this result
                img_label.bind(
                    "<Button-1>",
                    lambda e, r=result_info: self.use_result_from_browser(r, browser_window)
                )
            else:
                # Error placeholder
                ttk.Label(parent_frame, text="❌ Error loading image").pack()
            
            # Result info
            info_text = f"Seed: {result_info['seed']}\nRequest: #{result_info['request_num']}"
            info_label = ttk.Label(
                parent_frame,
                text=info_text,
                font=('Arial', 8),
                foreground="gray",
                justify=tk.CENTER
            )
            info_label.pack(pady=(2, 5))
            
            # Action buttons
            btn_frame = ttk.Frame(parent_frame)
            btn_frame.pack(fill=tk.X)
            
            use_btn = ttk.Button(
                btn_frame,
                text="Use This",
                command=lambda r=result_info: self.use_result_from_browser(r, browser_window),
                width=8
            )
            use_btn.pack(side=tk.LEFT, padx=(0, 2))
            
            save_btn = ttk.Button(
                btn_frame,
                text="Save",
                command=lambda r=result_info: self.save_individual_result(r),
                width=8
            )
            save_btn.pack(side=tk.RIGHT, padx=(2, 0))
            
        except Exception as e:
            logger.error(f"Error creating result item: {e}")
            ttk.Label(parent_frame, text="❌ Error").pack()
    
    def _create_thumbnail(self, image_path: str, size: tuple = (300, 300)) -> Optional[ImageTk.PhotoImage]:
        """Create thumbnail with caching"""
        try:
            # Check cache first
            cache_key = f"{image_path}_{size[0]}_{size[1]}"
            if cache_key in self.image_cache:
                return self.image_cache[cache_key]
            
            # Load and resize image
            with Image.open(image_path) as img:
                # Convert to RGB if necessary
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")
                
                # Create thumbnail
                img.thumbnail(size, Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                
                # Cache the thumbnail
                self._cache_image(cache_key, photo)
                
                return photo
                
        except Exception as e:
            logger.debug(f"Error creating thumbnail for {image_path}: {e}")
            return None
    
    def _cache_image(self, key: str, photo: ImageTk.PhotoImage) -> None:
        """Cache image with size limit"""
        try:
            # Remove oldest items if cache is full
            if len(self.image_cache) >= self.max_cache_size:
                # Remove first item (oldest)
                oldest_key = next(iter(self.image_cache))
                del self.image_cache[oldest_key]
            
            self.image_cache[key] = photo
            
        except Exception as e:
            logger.error(f"Error caching image: {e}")
    
    def use_result_from_browser(self, result_info: Dict[str, Any], browser_window: tk.Toplevel) -> None:
        """Use a result from the browser as the main result"""
        try:
            self.result_image_path = result_info['path']
            self.result_url = result_info['url']
            
            # Display the selected result in the result panel
            if hasattr(self.parent_layout, 'display_image_in_panel'):
                self.parent_layout.display_image_in_panel(result_info['path'], "result")
            
            self._show_message(f"✅ Using result #{result_info['request_num']} (seed: {result_info['seed']})")
            
            # Trigger callback if set
            if self.on_result_selected_callback:
                self.on_result_selected_callback(result_info['path'])
            
            # Close the browser
            browser_window.destroy()
            
        except Exception as e:
            logger.error(f"Error using result from browser: {e}")
            messagebox.showerror("Error", f"Failed to use result: {str(e)}")
    
    def save_individual_result(self, result_info: Dict[str, Any]) -> None:
        """Save an individual result to a file"""
        try:
            # Suggest a filename
            suggested_name = f"seedream_result_{result_info['request_num']}_seed{result_info['seed']}.png"
            
            file_path = filedialog.asksaveasfilename(
                title=f"Save Result #{result_info['request_num']}",
                defaultextension=".png",
                initialfile=suggested_name,
                filetypes=[
                    ("PNG files", "*.png"),
                    ("JPEG files", "*.jpg"),
                    ("WebP files", "*.webp"),
                    ("All files", "*.*")
                ]
            )
            
            if file_path:
                # Copy the result to the selected location
                shutil.copy2(result_info['path'], file_path)
                self._show_message(f"💾 Saved result #{result_info['request_num']} to: {Path(file_path).name}")
                messagebox.showinfo("Saved", f"Result #{result_info['request_num']} saved successfully!")
                
        except Exception as e:
            logger.error(f"Error saving individual result: {e}")
            messagebox.showerror("Error", f"Failed to save result: {str(e)}")
    
    def save_all_results(self) -> None:
        """Save all results to a selected folder"""
        try:
            if not self.completed_results:
                messagebox.showinfo("No Results", "No results to save.")
                return
            
            # Get folder to save to
            folder_path = filedialog.askdirectory(title="Select Folder to Save All Results")
            
            if folder_path:
                saved_count = 0
                for result_info in self.completed_results:
                    try:
                        filename = f"seedream_result_{result_info['request_num']}_seed{result_info['seed']}.png"
                        dest_path = os.path.join(folder_path, filename)
                        shutil.copy2(result_info['path'], dest_path)
                        saved_count += 1
                    except Exception as e:
                        logger.error(f"Error saving result {result_info['request_num']}: {e}")
                
                if saved_count > 0:
                    self._show_message(f"💾 Saved {saved_count}/{len(self.completed_results)} results")
                    messagebox.showinfo("Saved", f"Successfully saved {saved_count} results to:\n{folder_path}")
                else:
                    messagebox.showerror("Error", "Failed to save any results.")
                    
        except Exception as e:
            logger.error(f"Error saving all results: {e}")
            messagebox.showerror("Error", f"Failed to save results: {str(e)}")
    
    def _enable_result_actions(self) -> None:
        """Enable result-related UI actions"""
        try:
            # This would enable save buttons, etc. in the main UI
            # Implementation depends on parent layout structure
            pass
        except Exception as e:
            logger.error(f"Error enabling result actions: {e}")
    
    def _get_prompt_snippet(self, max_length: int = 30) -> str:
        """Get prompt snippet for filename"""
        try:
            if hasattr(self.parent_layout, 'prompt_text'):
                prompt = self.parent_layout.prompt_text.get("1.0", tk.END).strip()
                # Clean for filename
                clean_prompt = "".join(c for c in prompt if c.isalnum() or c in (' ', '_', '-'))
                return clean_prompt[:max_length].replace(' ', '_')
            return "prompt"
        except:
            return "prompt"
    
    def _get_size_string(self) -> str:
        """Get size string for filename"""
        try:
            if hasattr(self.parent_layout, 'settings_manager'):
                settings = self.parent_layout.settings_manager.get_current_settings()
                return f"{settings.get('width', 1024)}x{settings.get('height', 1024)}"
            return "1024x1024"
        except:
            return "1024x1024"
    
    def _get_current_prompt(self) -> str:
        """Get current prompt text"""
        try:
            if hasattr(self.parent_layout, 'prompt_text'):
                return self.parent_layout.prompt_text.get("1.0", tk.END).strip()
            return ""
        except:
            return ""
    
    def _get_current_settings(self) -> Dict[str, Any]:
        """Get current settings"""
        try:
            if hasattr(self.parent_layout, 'settings_manager'):
                return self.parent_layout.settings_manager.get_current_settings()
            return {"width": 1024, "height": 1024, "seed": -1}
        except:
            return {"width": 1024, "height": 1024, "seed": -1}
    
    def _show_message(self, message: str) -> None:
        """Show message"""
        try:
            if hasattr(self.parent_layout, 'log_message'):
                self.parent_layout.log_message(message)
            else:
                logger.info(f"Results: {message}")
        except Exception as e:
            logger.error(f"Error showing message: {e}")
    
    def set_result_selected_callback(self, callback: Callable) -> None:
        """Set callback for when a result is selected"""
        self.on_result_selected_callback = callback
    
    def clear_results(self) -> None:
        """Clear all results and cache"""
        try:
            self.completed_results.clear()
            self.result_image_path = None
            self.result_url = None
            self.image_cache.clear()
            
        except Exception as e:
            logger.error(f"Error clearing results: {e}")
    
    def get_results_status(self) -> Dict[str, Any]:
        """Get current results status"""
        return {
            "completed_results_count": len(self.completed_results),
            "has_current_result": bool(self.result_image_path),
            "cache_size": len(self.image_cache),
            "auto_save_enabled": self.auto_save_enabled
        }