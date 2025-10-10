"""
Seedream Actions Handler Module
Phase 5 of the improved_seedream_layout.py refactoring

This module handles all action processing functionality including:
- Generate button and main processing logic
- Multi-request handling and concurrent processing
- Progress tracking and status updates
- Request queue management
- Error handling and recovery
- Task cancellation and cleanup
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import requests
import tempfile
import json
import os
from typing import List, Dict, Any, Optional, Callable
from core.logger import get_logger

logger = get_logger(__name__)


class ActionsHandlerManager:
    """Manages all action processing functionality for Seedream V4"""
    
    def __init__(self, parent_layout):
        """
        Initialize actions handler manager
        
        Args:
            parent_layout: Reference to the main layout instance
        """
        self.parent_layout = parent_layout
        self.api_client = parent_layout.api_client if hasattr(parent_layout, 'api_client') else None
        
        # Processing state
        self.current_task_id = None
        self.active_tasks = {}  # Track multiple concurrent tasks
        self.completed_results = []  # Store all completed results
        self.generation_in_progress = False
        
        # Multi-request settings
        self.num_requests_var = tk.IntVar(value=1)
        self.max_concurrent_requests = 5
        
        # UI references
        self.generate_btn = None
        self.cancel_btn = None
        self.progress_bar = None
        self.status_label = None
        
        # Auto-save integration
        self.auto_save_enabled = self._check_auto_save_available()
        
        # Callbacks
        self.on_results_ready_callback = None
        self.on_processing_error_callback = None
        
        logger.info("ActionsHandlerManager initialized")
    
    def _check_auto_save_available(self) -> bool:
        """Check if auto-save functionality is available"""
        try:
            from core.auto_save import auto_save_manager
            return True
        except ImportError:
            return False
    
    def setup_actions_section(self, parent_frame: tk.Widget) -> None:
        """Setup the actions section UI"""
        try:
            logger.info("Setting up actions section")
            
            # Main actions frame
            actions_frame = ttk.LabelFrame(
                parent_frame,
                text="🚀 Actions",
                padding="8"
            )
            actions_frame.grid(row=3, column=0, sticky="ew", pady=(0, 8))
            actions_frame.columnconfigure(0, weight=1)
            
            # Setup components
            self._setup_multi_request_controls(actions_frame)
            self._setup_action_buttons(actions_frame)
            self._setup_progress_section(actions_frame)
            
            logger.info("Actions section setup complete")
            
        except Exception as e:
            logger.error(f"Error setting up actions section: {e}")
            raise
    
    def _setup_multi_request_controls(self, parent_frame: tk.Widget) -> None:
        """Setup multi-request controls"""
        # Multi-request frame
        multi_frame = ttk.Frame(parent_frame)
        multi_frame.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        multi_frame.columnconfigure(1, weight=1)
        
        # Request count label
        ttk.Label(
            multi_frame,
            text="Count:",
            font=('Arial', 9)
        ).grid(row=0, column=0, sticky="w", padx=(0, 5))
        
        # Request count spinbox
        num_requests_spinbox = tk.Spinbox(
            multi_frame,
            from_=1,
            to=self.max_concurrent_requests,
            textvariable=self.num_requests_var,
            width=6,
            font=('Arial', 9),
            command=self._on_request_count_changed
        )
        num_requests_spinbox.grid(row=0, column=1, sticky="w")
        
        # Info label
        info_label = ttk.Label(
            multi_frame,
            text="concurrent generations (uses random seeds)",
            font=('Arial', 8),
            foreground="gray"
        )
        info_label.grid(row=0, column=2, sticky="w", padx=(5, 0))
        
        # Bind change event
        self.num_requests_var.trace('w', self._on_request_count_changed)
    
    def _setup_action_buttons(self, parent_frame: tk.Widget) -> None:
        """Setup main action buttons"""
        buttons_frame = ttk.Frame(parent_frame)
        buttons_frame.grid(row=1, column=0, sticky="ew", pady=(0, 8))
        buttons_frame.columnconfigure(0, weight=1)
        
        # Main generate button
        self.generate_btn = ttk.Button(
            buttons_frame,
            text="🌟 Apply Seedream V4",
            command=self.process_seedream,
            style="Accent.TButton"
        )
        self.generate_btn.grid(row=0, column=0, sticky="ew", pady=(0, 4))
        
        # Secondary actions frame
        secondary_frame = ttk.Frame(buttons_frame)
        secondary_frame.grid(row=1, column=0, sticky="ew")
        secondary_frame.columnconfigure(0, weight=1)
        secondary_frame.columnconfigure(1, weight=1)
        secondary_frame.columnconfigure(2, weight=1)
        
        # Clear button
        clear_btn = ttk.Button(
            secondary_frame,
            text="🗑️ Clear",
            command=self.clear_all,
            width=10
        )
        clear_btn.grid(row=0, column=0, sticky="ew", padx=(0, 2))
        
        # Cancel button (initially hidden)
        self.cancel_btn = ttk.Button(
            secondary_frame,
            text="❌ Cancel",
            command=self.cancel_processing,
            width=10,
            state='disabled'
        )
        self.cancel_btn.grid(row=0, column=1, sticky="ew", padx=(2, 2))
        
        # Save button
        save_btn = ttk.Button(
            secondary_frame,
            text="💾 Save",
            command=self.save_result,
            width=10
        )
        save_btn.grid(row=0, column=2, sticky="ew", padx=(2, 0))
    
    def _setup_progress_section(self, parent_frame: tk.Widget) -> None:
        """Setup progress tracking section"""
        progress_frame = ttk.Frame(parent_frame)
        progress_frame.grid(row=2, column=0, sticky="ew")
        progress_frame.columnconfigure(0, weight=1)
        
        # Status label
        self.status_label = ttk.Label(
            progress_frame,
            text="Ready to process",
            font=('Arial', 9),
            foreground="gray"
        )
        self.status_label.grid(row=0, column=0, sticky="w", pady=(0, 4))
        
        # Progress bar (initially hidden)
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            mode='indeterminate',
            length=300
        )
        # Don't grid initially - will be shown during processing
    
    def _on_request_count_changed(self, *args) -> None:
        """Handle request count changes"""
        try:
            count = self.num_requests_var.get()
            if count > 1:
                self.generate_btn.config(text=f"🌟 Generate {count} Variations")
            else:
                self.generate_btn.config(text="🌟 Apply Seedream V4")
        except Exception as e:
            logger.error(f"Error updating request count: {e}")
    
    def process_seedream(self) -> None:
        """Main processing entry point"""
        try:
            if self.generation_in_progress:
                self._show_message("⏳ Processing already in progress...")
                return
            
            # Validate inputs
            if not self._validate_inputs():
                return
            
            # Check for multiple requests
            num_requests = self.num_requests_var.get()
            if num_requests > 1:
                self.handle_multiple_requests()
            else:
                self.handle_single_request()
                
        except Exception as e:
            logger.error(f"Error in process_seedream: {e}")
            self.handle_processing_error(f"Processing failed: {str(e)}")
    
    def _validate_inputs(self) -> bool:
        """Validate inputs before processing"""
        try:
            # Check for selected image
            if not hasattr(self.parent_layout, 'selected_image_path') or not self.parent_layout.selected_image_path:
                messagebox.showerror("Missing Image", "Please select an input image.")
                return False
            
            # Check for prompt
            if hasattr(self.parent_layout, 'prompt_text'):
                prompt = self.parent_layout.prompt_text.get("1.0", tk.END).strip()
                if not prompt or len(prompt.strip()) < 3:
                    messagebox.showerror("Missing Prompt", "Please enter a transformation prompt.")
                    return False
            
            # Check API client
            if not self.api_client:
                messagebox.showerror("API Error", "API client not available.")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating inputs: {e}")
            return False
    
    def handle_single_request(self) -> None:
        """Handle single request processing"""
        try:
            self._start_processing()
            
            # Get settings
            settings = self._get_current_settings()
            
            # Run processing in background thread
            threading.Thread(
                target=self._single_request_thread,
                args=(settings,),
                daemon=True
            ).start()
            
        except Exception as e:
            logger.error(f"Error handling single request: {e}")
            self.handle_processing_error(str(e))
    
    def handle_multiple_requests(self) -> None:
        """Handle multiple concurrent requests"""
        try:
            num_requests = self.num_requests_var.get()
            self._start_processing(multiple=True)
            
            # Get base settings
            base_settings = self._get_current_settings()
            
            # Prepare multiple request settings
            request_settings = []
            for i in range(num_requests):
                settings = base_settings.copy()
                settings['request_num'] = i + 1
                settings['seed'] = self._generate_seed_for_request(i, base_settings.get('seed', -1))
                request_settings.append(settings)
            
            # Run processing in background thread
            threading.Thread(
                target=self._multiple_requests_thread,
                args=(request_settings,),
                daemon=True
            ).start()
            
        except Exception as e:
            logger.error(f"Error handling multiple requests: {e}")
            self.handle_processing_error(str(e))
    
    def _generate_seed_for_request(self, request_index: int, base_seed: int) -> int:
        """Generate seed for individual request"""
        if base_seed == -1:
            # Random seeds
            import random
            return random.randint(0, 2147483647)
        else:
            # Sequential seeds
            return base_seed + request_index
    
    def _get_current_settings(self) -> Dict[str, Any]:
        """Get current settings for processing"""
        try:
            settings = {}
            
            # Get prompt
            if hasattr(self.parent_layout, 'prompt_text'):
                settings['prompt'] = self.parent_layout.prompt_text.get("1.0", tk.END).strip()
            
            # Get image path
            if hasattr(self.parent_layout, 'selected_image_path'):
                settings['image_path'] = self.parent_layout.selected_image_path
            
            # Get settings from settings manager if available
            if hasattr(self.parent_layout, 'settings_manager'):
                settings_data = self.parent_layout.settings_manager.get_current_settings()
                settings.update(settings_data)
            else:
                # Fallback settings
                settings.update({
                    'width': 1024,
                    'height': 1024,
                    'seed': -1,
                    'sync_mode': False,
                    'base64_output': False
                })
            
            return settings
            
        except Exception as e:
            logger.error(f"Error getting current settings: {e}")
            return {}
    
    def _single_request_thread(self, settings: Dict[str, Any]) -> None:
        """Background thread for single request processing"""
        try:
            # Submit task
            result = self.api_client.submit_seedream_v4_task(
                prompt=settings['prompt'],
                images=[settings['image_path']],
                size=f"{settings['width']}*{settings['height']}",
                seed=settings['seed'],
                enable_sync_mode=settings['sync_mode'],
                enable_base64_output=settings['base64_output']
            )
            
            if result.get('success'):
                task_id = result['task_id']
                self.current_task_id = task_id
                
                # Schedule task submitted handler
                self.parent_layout.parent_frame.after(
                    0,
                    lambda: self.handle_task_submitted(task_id)
                )
            else:
                error_msg = result.get('error', 'Unknown error')
                self.parent_layout.parent_frame.after(
                    0,
                    lambda: self.handle_processing_error(error_msg)
                )
                
        except Exception as e:
            logger.error(f"Error in single request thread: {e}")
            self.parent_layout.parent_frame.after(
                0,
                lambda: self.handle_processing_error(str(e))
            )
    
    def _multiple_requests_thread(self, request_settings_list: List[Dict[str, Any]]) -> None:
        """Background thread for multiple requests processing"""
        try:
            submitted_tasks = []
            num_requests = len(request_settings_list)
            
            # Submit all requests
            for settings in request_settings_list:
                try:
                    result = self.api_client.submit_seedream_v4_task(
                        prompt=settings['prompt'],
                        images=[settings['image_path']],
                        size=f"{settings['width']}*{settings['height']}",
                        seed=settings['seed'],
                        enable_sync_mode=settings['sync_mode'],
                        enable_base64_output=settings['base64_output']
                    )
                    
                    if result.get('success'):
                        task_id = result['task_id']
                        submitted_tasks.append({
                            'task_id': task_id,
                            'request_num': settings['request_num'],
                            'seed': settings['seed'],
                            'settings': settings,
                            'status': 'submitted'
                        })
                        
                        # Log successful submission
                        self.parent_layout.parent_frame.after(
                            0,
                            lambda r=settings['request_num'], t=task_id: self._show_message(
                                f"✅ Request {r}/{num_requests} submitted: {t}"
                            )
                        )
                    else:
                        error_msg = result.get('error', 'Unknown error')
                        self.parent_layout.parent_frame.after(
                            0,
                            lambda r=settings['request_num'], e=error_msg: self._show_message(
                                f"❌ Request {r}/{num_requests} failed: {e}"
                            )
                        )
                        
                except Exception as e:
                    logger.error(f"Error submitting request {settings['request_num']}: {e}")
            
            if not submitted_tasks:
                self.parent_layout.parent_frame.after(
                    0,
                    lambda: self.handle_processing_error("All requests failed to submit")
                )
                return
            
            # Store task information
            self.active_tasks = {task['task_id']: task for task in submitted_tasks}
            
            # Schedule multiple tasks submitted handler
            self.parent_layout.parent_frame.after(
                0,
                lambda: self.handle_multiple_tasks_submitted(submitted_tasks)
            )
            
        except Exception as e:
            logger.error(f"Error in multiple requests thread: {e}")
            self.parent_layout.parent_frame.after(
                0,
                lambda: self.handle_processing_error(str(e))
            )
    
    def handle_task_submitted(self, task_id: str) -> None:
        """Handle successful task submission (single task)"""
        try:
            self._show_message(f"✅ Task submitted successfully: {task_id}")
            self._show_message("⏳ Waiting for processing to complete...")
            
            # Start polling for results
            self.poll_for_results(task_id)
            
        except Exception as e:
            logger.error(f"Error handling task submitted: {e}")
    
    def handle_multiple_tasks_submitted(self, submitted_tasks: List[Dict[str, Any]]) -> None:
        """Handle multiple task submissions"""
        try:
            total_tasks = len(submitted_tasks)
            self._show_message(f"✅ All {total_tasks} task(s) submitted successfully")
            self._show_message(f"⏳ Polling for {total_tasks} concurrent result(s)...")
            
            # Update status
            self.status_label.config(
                text=f"Waiting for {total_tasks} results...",
                foreground="blue"
            )
            
            # Start polling for all tasks
            for task_info in submitted_tasks:
                self.poll_for_multiple_results(task_info['task_id'], task_info['request_num'])
                
        except Exception as e:
            logger.error(f"Error handling multiple tasks submitted: {e}")
    
    def poll_for_results(self, task_id: str) -> None:
        """Poll for task completion results (single task)"""
        start_time = time.time()
        max_poll_time = 300  # 5 minutes max
        
        def check_results():
            try:
                # Check for timeout
                if time.time() - start_time > max_poll_time:
                    self._show_message("⏰ Polling timeout - stopping after 5 minutes")
                    self.handle_processing_error("Task timed out after 5 minutes")
                    return
                
                # Check if processing was cancelled
                if not self.generation_in_progress:
                    return
                
                result = self.api_client.get_seedream_v4_result(task_id)
                
                if result.get('success'):
                    status = result.get('status', '').lower()
                    
                    if status == 'completed':
                        # Task completed successfully
                        self._show_message("✅ SeedDream processing completed!")
                        self.handle_results_ready(result)
                        return
                    elif status in ['failed', 'error']:
                        error_msg = result.get('error', 'Task failed')
                        self.handle_processing_error(error_msg)
                        return
                    else:
                        # Still processing, poll again
                        self._show_message(f"🔄 Status: {status}")
                        self.parent_layout.parent_frame.after(3000, check_results)
                else:
                    error_msg = result.get('error', 'Failed to get task status')
                    self.handle_processing_error(error_msg)
                    
            except Exception as e:
                logger.error(f"Error polling for results: {e}")
                self.handle_processing_error(str(e))
        
        # Start polling
        self.parent_layout.parent_frame.after(2000, check_results)
    
    def poll_for_multiple_results(self, task_id: str, request_num: int) -> None:
        """Poll for individual task completion in multi-request mode"""
        start_time = time.time()
        max_poll_time = 300  # 5 minutes max
        
        def check_results():
            try:
                # Check for timeout
                if time.time() - start_time > max_poll_time:
                    self._show_message(f"⏰ Request {request_num} timed out after 5 minutes")
                    if task_id in self.active_tasks:
                        self.active_tasks[task_id]['status'] = 'failed'
                        self.active_tasks[task_id]['error'] = 'Timeout'
                    self.check_all_tasks_completed()
                    return
                
                # Check if processing was cancelled
                if not self.generation_in_progress:
                    return
                
                result = self.api_client.get_seedream_v4_result(task_id)
                
                if result.get('success'):
                    status = result.get('status', '').lower()
                    
                    if status == 'completed':
                        # Task completed successfully
                        self._show_message(f"✅ Request {request_num} completed!")
                        
                        # Get result URL
                        result_url = result.get('result_url') or result.get('output_url')
                        
                        # Update task info
                        if task_id in self.active_tasks:
                            self.active_tasks[task_id]['status'] = 'completed'
                            self.active_tasks[task_id]['result_url'] = result_url
                            self.active_tasks[task_id]['result_data'] = result
                        
                        # Check if all tasks are complete
                        self.check_all_tasks_completed()
                        return
                        
                    elif status in ['failed', 'error']:
                        error_msg = result.get('error', 'Task failed')
                        self._show_message(f"❌ Request {request_num} failed: {error_msg}")
                        
                        # Update task info
                        if task_id in self.active_tasks:
                            self.active_tasks[task_id]['status'] = 'failed'
                            self.active_tasks[task_id]['error'] = error_msg
                        
                        # Check if all tasks are complete
                        self.check_all_tasks_completed()
                        return
                        
                    else:
                        # Still processing, poll again
                        self.parent_layout.parent_frame.after(3000, check_results)
                else:
                    error_msg = result.get('error', 'Failed to get task status')
                    self._show_message(f"❌ Request {request_num} polling error: {error_msg}")
                    
                    # Update task info
                    if task_id in self.active_tasks:
                        self.active_tasks[task_id]['status'] = 'failed'
                        self.active_tasks[task_id]['error'] = error_msg
                    
                    # Check if all tasks are complete
                    self.check_all_tasks_completed()
                    
            except Exception as e:
                logger.error(f"Error polling for request {request_num}: {e}")
                
                # Update task info
                if task_id in self.active_tasks:
                    self.active_tasks[task_id]['status'] = 'failed'
                    self.active_tasks[task_id]['error'] = str(e)
                
                # Check if all tasks are complete
                self.check_all_tasks_completed()
        
        # Start polling
        self.parent_layout.parent_frame.after(2000, check_results)
    
    def check_all_tasks_completed(self) -> None:
        """Check if all active tasks have completed and handle results"""
        try:
            # Count tasks by status
            total_tasks = len(self.active_tasks)
            completed_tasks = [t for t in self.active_tasks.values() if t['status'] == 'completed']
            failed_tasks = [t for t in self.active_tasks.values() if t['status'] == 'failed']
            pending_tasks = [t for t in self.active_tasks.values() if t['status'] == 'submitted']
            
            # Update status
            status_msg = f"{len(completed_tasks)}/{total_tasks} completed"
            if failed_tasks:
                status_msg += f", {len(failed_tasks)} failed"
            self.status_label.config(text=status_msg, foreground="blue")
            
            # Check if all tasks are done
            if len(pending_tasks) == 0:
                # All tasks finished
                self._stop_processing()
                
                if completed_tasks:
                    # At least some tasks succeeded
                    self._show_message(f"🎉 Processing complete! {len(completed_tasks)}/{total_tasks} successful")
                    
                    # Handle results
                    if len(completed_tasks) == 1:
                        # Single result
                        self.handle_results_ready(completed_tasks[0]['result_data'])
                    else:
                        # Multiple results
                        self.handle_multiple_results_ready(completed_tasks)
                else:
                    # All tasks failed
                    error_messages = [t.get('error', 'Unknown error') for t in failed_tasks]
                    self.handle_processing_error(f"All {total_tasks} requests failed. Errors: {', '.join(error_messages[:3])}")
                    
        except Exception as e:
            logger.error(f"Error checking task completion: {e}")
    
    def handle_results_ready(self, result_data: Dict[str, Any]) -> None:
        """Handle single result ready"""
        try:
            if self.on_results_ready_callback:
                self.on_results_ready_callback(result_data)
            else:
                self._show_message("✅ Result ready!")
                
        except Exception as e:
            logger.error(f"Error handling results ready: {e}")
    
    def handle_multiple_results_ready(self, completed_tasks: List[Dict[str, Any]]) -> None:
        """Handle multiple results ready"""
        try:
            if self.on_results_ready_callback:
                self.on_results_ready_callback(completed_tasks, multiple=True)
            else:
                self._show_message(f"✅ {len(completed_tasks)} results ready!")
                
        except Exception as e:
            logger.error(f"Error handling multiple results ready: {e}")
    
    def handle_processing_error(self, error_message: str) -> None:
        """Handle processing errors"""
        try:
            self._stop_processing()
            
            if self.on_processing_error_callback:
                self.on_processing_error_callback(error_message)
            else:
                self._show_message(f"❌ Error: {error_message}")
                messagebox.showerror("Processing Error", error_message)
                
        except Exception as e:
            logger.error(f"Error handling processing error: {e}")
    
    def cancel_processing(self) -> None:
        """Cancel current processing"""
        try:
            self.generation_in_progress = False
            self.current_task_id = None
            self.active_tasks.clear()
            
            self._stop_processing()
            self._show_message("❌ Processing cancelled")
            
        except Exception as e:
            logger.error(f"Error cancelling processing: {e}")
    
    def clear_all(self) -> None:
        """Clear all inputs and results"""
        try:
            # Cancel any ongoing processing
            self.cancel_processing()
            
            # Clear layout data
            if hasattr(self.parent_layout, 'selected_image_path'):
                self.parent_layout.selected_image_path = None
            
            if hasattr(self.parent_layout, 'result_image_path'):
                self.parent_layout.result_image_path = None
            
            # Clear prompt
            if hasattr(self.parent_layout, 'prompt_text'):
                self.parent_layout.prompt_text.delete("1.0", tk.END)
            
            # Reset UI state
            self._show_message("🗑️ All inputs cleared")
            
        except Exception as e:
            logger.error(f"Error clearing all: {e}")
    
    def save_result(self) -> None:
        """Save current result"""
        try:
            # Check if there's a result to save
            if not hasattr(self.parent_layout, 'result_image_path') or not self.parent_layout.result_image_path:
                messagebox.showwarning("No Result", "No result image to save.")
                return
            
            from tkinter import filedialog
            
            # Get save location
            file_path = filedialog.asksaveasfilename(
                title="Save Result Image",
                defaultextension=".png",
                filetypes=[
                    ("PNG files", "*.png"),
                    ("JPEG files", "*.jpg"),
                    ("WebP files", "*.webp"),
                    ("All files", "*.*")
                ]
            )
            
            if file_path:
                # Copy result to save location
                import shutil
                shutil.copy2(self.parent_layout.result_image_path, file_path)
                self._show_message(f"💾 Result saved to: {file_path}")
                
        except Exception as e:
            logger.error(f"Error saving result: {e}")
            messagebox.showerror("Save Error", f"Failed to save result: {str(e)}")
    
    def _start_processing(self, multiple: bool = False) -> None:
        """Start processing state"""
        try:
            self.generation_in_progress = True
            
            # Update UI
            self.generate_btn.config(state='disabled')
            self.cancel_btn.config(state='normal')
            
            # Show progress bar
            self.progress_bar.grid(row=1, column=0, sticky="ew", pady=(4, 0))
            self.progress_bar.start(10)
            
            # Update status
            status_text = "Processing multiple requests..." if multiple else "Processing request..."
            self.status_label.config(text=status_text, foreground="blue")
            
        except Exception as e:
            logger.error(f"Error starting processing: {e}")
    
    def _stop_processing(self) -> None:
        """Stop processing state"""
        try:
            self.generation_in_progress = False
            
            # Update UI
            self.generate_btn.config(state='normal')
            self.cancel_btn.config(state='disabled')
            
            # Hide progress bar
            self.progress_bar.stop()
            self.progress_bar.grid_remove()
            
            # Update status
            self.status_label.config(text="Ready to process", foreground="gray")
            
        except Exception as e:
            logger.error(f"Error stopping processing: {e}")
    
    def _show_message(self, message: str) -> None:
        """Show message"""
        try:
            if hasattr(self.parent_layout, 'log_message'):
                self.parent_layout.log_message(message)
            else:
                logger.info(f"Actions: {message}")
        except Exception as e:
            logger.error(f"Error showing message: {e}")
    
    def set_results_ready_callback(self, callback: Callable) -> None:
        """Set callback for when results are ready"""
        self.on_results_ready_callback = callback
    
    def set_processing_error_callback(self, callback: Callable) -> None:
        """Set callback for processing errors"""
        self.on_processing_error_callback = callback
    
    def get_processing_status(self) -> Dict[str, Any]:
        """Get current processing status"""
        return {
            "generation_in_progress": self.generation_in_progress,
            "current_task_id": self.current_task_id,
            "active_tasks_count": len(self.active_tasks),
            "num_requests": self.num_requests_var.get(),
            "completed_results_count": len(self.completed_results)
        }
    
    def is_processing(self) -> bool:
        """Check if currently processing"""
        return self.generation_in_progress