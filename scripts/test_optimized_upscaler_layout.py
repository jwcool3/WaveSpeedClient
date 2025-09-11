#!/usr/bin/env python3
"""
Test script for the optimized Image Upscaler layout
Demonstrates the new streamlined upscaling workflow
"""

import sys
import os
import tkinter as tk
from tkinter import ttk

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from ui.components.optimized_upscaler_layout import OptimizedUpscalerLayout
from core.logger import get_logger

logger = get_logger()


class OptimizedUpscalerTestApp:
    """Test application for the optimized Image Upscaler layout"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Optimized Image Upscaler Layout Test - WaveSpeed AI")
        self.root.geometry("1400x900")
        self.root.configure(bg='#f8f9fa')
        
        # Create main frame
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create optimized layout
        self.layout = OptimizedUpscalerLayout(self.main_frame)
        
        # Set up callbacks
        self.layout.browse_image = self.on_browse_image
        self.layout.process_upscale = self.on_process_upscale
        self.layout.save_result = self.on_save_result
        self.layout.load_image_dialog = self.on_load_image
        self.layout.clear_all = self.on_clear_all
        
        # Add some test data
        self.setup_test_data()
    
    def setup_test_data(self):
        """Add some test data to the layout"""
        # The layout is already set up with default values
        # We can add some sample images or test data here if needed
        pass
    
    def on_browse_image(self):
        """Handle image browsing"""
        from tkinter import filedialog
        file_path = filedialog.askopenfilename(
            title="Select Test Image to Upscale",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.gif *.bmp *.webp"),
                ("PNG files", "*.png"),
                ("JPEG files", "*.jpg *.jpeg"),
                ("WebP files", "*.webp"),
                ("All files", "*.*")
            ]
        )
        if file_path:
            self.layout.load_image(file_path)
            logger.info(f"Test image loaded: {file_path}")
    
    def on_process_upscale(self):
        """Handle upscale process request"""
        logger.info("Upscale process requested from optimized layout")
        
        # Simulate processing
        import threading
        import time
        
        def simulate_processing():
            self.layout.log_status("🔍 Starting upscale process...")
            self.layout.upscale_btn.config(state='disabled', text="Upscaling...")
            self.layout.progress_bar.grid(row=1, column=0, sticky="ew", pady=(4, 0))
            self.layout.progress_bar.start()
            
            time.sleep(3)  # Simulate processing time
            
            # Simulate success
            self.layout.after_upscaling()
        
        threading.Thread(target=simulate_processing, daemon=True).start()
    
    def on_save_result(self):
        """Handle save result"""
        logger.info("Save result requested")
        self.layout.log_status("💾 Save result clicked")
    
    def on_load_image(self):
        """Handle load image"""
        logger.info("Load image requested")
        self.layout.log_status("📂 Load image clicked")
        self.on_browse_image()
    
    def on_clear_all(self):
        """Handle clear all"""
        logger.info("Clear all requested")
        self.layout.log_status("🧹 Clear all clicked")
    
    def run(self):
        """Run the test application"""
        # Add some instructions
        instructions = ttk.Label(
            self.main_frame,
            text="🎯 Optimized Image Upscaler Layout Test - Try the streamlined upscaling workflow!",
            font=('Arial', 10, 'bold'),
            foreground='#495057'
        )
        instructions.pack(pady=(0, 10))
        
        self.root.mainloop()


def main():
    """Main function"""
    try:
        app = OptimizedUpscalerTestApp()
        app.run()
    except Exception as e:
        logger.error(f"Error running test app: {e}")
        print(f"Error: {e}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
