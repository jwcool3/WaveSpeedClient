#!/usr/bin/env python3
"""
Test script for the optimized Wan 2.2 Video Generation layout
Demonstrates the new streamlined video generation workflow
"""

import sys
import os
import tkinter as tk
from tkinter import ttk

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from ui.components.optimized_wan22_layout import OptimizedWan22Layout
from core.logger import get_logger

logger = get_logger()


class OptimizedWan22TestApp:
    """Test application for the optimized Wan 2.2 layout"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Optimized Wan 2.2 Layout Test - WaveSpeed AI")
        self.root.geometry("1400x900")
        self.root.configure(bg='#f8f9fa')
        
        # Create main frame
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create optimized layout
        self.layout = OptimizedWan22Layout(self.main_frame)
        
        # Set up callbacks
        self.layout.browse_image = self.on_browse_image
        self.layout.process_video_generation = self.on_process_video_generation
        self.layout.open_in_browser = self.on_open_in_browser
        self.layout.play_in_system = self.on_play_in_system
        self.layout.download_video = self.on_download_video
        self.layout.clear_all = self.on_clear_all
        self.layout.load_sample = self.on_load_sample
        self.layout.improve_with_ai = self.on_improve_with_ai
        self.layout.save_current_prompt = self.on_save_current_prompt
        self.layout.delete_saved_prompt = self.on_delete_saved_prompt
        self.layout.on_saved_prompt_selected = self.on_saved_prompt_selected
        
        # Add some test data
        self.setup_test_data()
    
    def setup_test_data(self):
        """Add some test data to the layout"""
        # Set some initial values for testing
        self.layout.video_prompt_text.delete("1.0", tk.END)
        self.layout.video_prompt_text.insert("1.0", "A beautiful woman walking through a garden, gentle breeze, natural lighting, cinematic movement")
        
        self.layout.negative_prompt_text.delete("1.0", tk.END)
        self.layout.negative_prompt_text.insert("1.0", "blurry, low quality, static, no movement")
        
        self.layout.duration_var.set("5s")
        self.layout.seed_var.set("12345")
        self.layout.last_image_url_var.set("")
        
        # Add some sample saved prompts
        self.layout.saved_prompts_listbox.insert(tk.END, "Sample Video Prompt 1")
        self.layout.saved_prompts_listbox.insert(tk.END, "Sample Video Prompt 2")
        self.layout.saved_prompts_listbox.insert(tk.END, "Sample Video Prompt 3")
    
    def on_browse_image(self):
        """Handle image browsing"""
        from tkinter import filedialog
        file_path = filedialog.askopenfilename(
            title="Select Test Image for Video Generation",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.gif *.bmp *.webp"),
                ("All files", "*.*")
            ]
        )
        if file_path:
            self.layout.load_image(file_path)
            logger.info(f"Test image loaded: {file_path}")
    
    def on_process_video_generation(self):
        """Handle video generation process request"""
        logger.info("Video generation process requested from optimized layout")
        
        # Simulate processing
        import threading
        import time
        
        def simulate_processing():
            self.layout.status_label.config(text="🎬 Generating video with Wan 2.2...", foreground="blue")
            self.layout.generate_btn.config(state='disabled', text="Generating Video...")
            self.layout.progress_bar.grid(row=1, column=0, sticky="ew", pady=(4, 0))
            self.layout.progress_bar.start()
            
            time.sleep(5)  # Simulate processing time
            
            # Simulate success
            self.layout.after_video_generation()
        
        threading.Thread(target=simulate_processing, daemon=True).start()
    
    def on_open_in_browser(self):
        """Handle open in browser"""
        logger.info("Open in browser requested")
        self.layout.status_label.config(text="🌐 Opening in browser...", foreground="blue")
    
    def on_play_in_system(self):
        """Handle play in system"""
        logger.info("Play in system requested")
        self.layout.status_label.config(text="📱 Opening in system player...", foreground="blue")
    
    def on_download_video(self):
        """Handle download video"""
        logger.info("Download video requested")
        self.layout.status_label.config(text="💾 Video downloaded", foreground="green")
    
    def on_clear_all(self):
        """Handle clear all"""
        logger.info("Clear all requested")
        self.layout.status_label.config(text="🧹 Cleared all data", foreground="gray")
    
    def on_load_sample(self):
        """Handle load sample"""
        logger.info("Load sample requested")
        self.layout.video_prompt_text.delete("1.0", tk.END)
        self.layout.video_prompt_text.insert("1.0", "A beautiful woman walking through a garden, gentle breeze, natural lighting, cinematic movement")
        self.layout.status_label.config(text="🎲 Sample prompt loaded", foreground="blue")
    
    def on_improve_with_ai(self):
        """Handle improve with AI"""
        logger.info("Improve with AI requested")
        self.layout.status_label.config(text="🤖 AI improvement requested", foreground="blue")
    
    def on_save_current_prompt(self):
        """Handle save current prompt"""
        logger.info("Save current prompt requested")
        self.layout.status_label.config(text="💾 Prompt saved", foreground="green")
    
    def on_delete_saved_prompt(self):
        """Handle delete saved prompt"""
        logger.info("Delete saved prompt requested")
        self.layout.status_label.config(text="🗑️ Prompt deleted", foreground="red")
    
    def on_saved_prompt_selected(self, event):
        """Handle saved prompt selection"""
        selection = self.layout.saved_prompts_listbox.curselection()
        if selection:
            selected_prompt = self.layout.saved_prompts_listbox.get(selection[0])
            logger.info(f"Saved prompt selected: {selected_prompt}")
            self.layout.status_label.config(text=f"📋 Selected: {selected_prompt}", foreground="blue")
    
    def run(self):
        """Run the test application"""
        # Add some instructions
        instructions = ttk.Label(
            self.main_frame,
            text="🎬 Optimized Wan 2.2 Layout Test - Try the streamlined video generation workflow!",
            font=('Arial', 10, 'bold'),
            foreground='#495057'
        )
        instructions.pack(pady=(0, 10))
        
        self.root.mainloop()


def main():
    """Main function"""
    try:
        app = OptimizedWan22TestApp()
        app.run()
    except Exception as e:
        logger.error(f"Error running test app: {e}")
        print(f"Error: {e}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
