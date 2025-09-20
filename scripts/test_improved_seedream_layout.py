#!/usr/bin/env python3
"""
Test script for the improved Seedream V4 layout
Demonstrates the new compact layout design
"""

import sys
import os
import tkinter as tk
from tkinter import ttk

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from ui.components.improved_seedream_layout import ImprovedSeedreamLayout
from core.logger import get_logger

logger = get_logger()


class MockTab:
    """Mock tab instance for testing"""
    def __init__(self):
        self.frame = None


class ImprovedSeedreamTestApp:
    """Test application for the improved Seedream V4 layout"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Improved Seedream V4 Layout Test - WaveSpeed AI")
        self.root.geometry("1400x900")
        self.root.configure(bg='#f8f9fa')
        
        # Create main frame
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create mock tab
        self.mock_tab = MockTab()
        self.mock_tab.frame = self.main_frame
        
        # Create improved layout
        self.layout = ImprovedSeedreamLayout(self.main_frame)
        
        # Set up callbacks
        self.layout.browse_image = self.on_browse_image
        self.layout.process_seedream = self.on_process_requested
        self.layout.save_result = self.on_save_result
        self.layout.load_result = self.on_load_result
        self.layout.clear_all = self.on_clear_all
        self.layout.load_sample = self.on_load_sample
        self.layout.improve_with_ai = self.on_improve_with_ai
        self.layout.save_preset = self.on_save_preset
        self.layout.load_preset = self.on_load_preset
        self.layout.auto_set_resolution = self.on_auto_set_resolution
        
        # Add some test data
        self.setup_test_data()
    
    def setup_test_data(self):
        """Add some test data to the layout"""
        # Add sample prompts to the preset combo
        sample_prompts = [
            "Transform the subject into a cyberpunk character with neon lights",
            "Change the background to a beautiful sunset landscape",
            "Make the person smile and add a warm glow effect",
            "Create a fantasy portrait with magical elements",
            "Convert to black and white with dramatic lighting"
        ]
        
        self.layout.preset_combo['values'] = sample_prompts
    
    def on_browse_image(self):
        """Handle image browsing"""
        from tkinter import filedialog
        file_path = filedialog.askopenfilename(
            title="Select Test Image",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.gif *.bmp *.webp"),
                ("All files", "*.*")
            ]
        )
        if file_path:
            self.layout.load_image(file_path)
            logger.info(f"Test image loaded: {file_path}")
    
    def on_process_requested(self):
        """Handle process request"""
        logger.info("Process requested from improved layout")
        
        # Simulate processing
        import threading
        import time
        
        def simulate_processing():
            self.layout.status_label.config(text="Processing...", foreground="blue")
            self.layout.progress_bar.grid(row=2, column=0, sticky="ew", pady=(4, 0))
            self.layout.progress_bar.start()
            self.layout.primary_btn.config(state='disabled', text="Processing...")
            
            time.sleep(3)  # Simulate processing time
            
            # Simulate success
            self.layout.after_processing()
        
        threading.Thread(target=simulate_processing, daemon=True).start()
    
    def on_save_result(self):
        """Handle save result"""
        logger.info("Save result requested")
        self.layout.status_label.config(text="Save result clicked", foreground="blue")
    
    def on_load_result(self):
        """Handle load result"""
        logger.info("Load result requested")
        self.layout.status_label.config(text="Load result clicked", foreground="blue")
    
    def on_clear_all(self):
        """Handle clear all"""
        logger.info("Clear all requested")
        self.layout.status_label.config(text="All cleared", foreground="green")
    
    def on_load_sample(self):
        """Handle load sample"""
        logger.info("Load sample requested")
        sample_prompts = [
            "Transform the subject into a cyberpunk character with neon lights",
            "Change the background to a beautiful sunset landscape",
            "Make the person smile and add a warm glow effect",
            "Create a fantasy portrait with magical elements",
            "Convert to black and white with dramatic lighting"
        ]
        
        import random
        sample = random.choice(sample_prompts)
        self.layout.prompt_text.delete("1.0", tk.END)
        self.layout.prompt_text.insert("1.0", sample)
        self.layout.status_label.config(text="Sample prompt loaded", foreground="green")
    
    def on_improve_with_ai(self):
        """Handle improve with AI"""
        logger.info("Improve with AI requested")
        self.layout.status_label.config(text="AI improvement clicked", foreground="blue")
    
    def on_save_preset(self):
        """Handle save preset"""
        logger.info("Save preset requested")
        self.layout.status_label.config(text="Preset saved", foreground="green")
    
    def on_load_preset(self, event=None):
        """Handle load preset"""
        logger.info("Load preset requested")
        self.layout.status_label.config(text="Preset loaded", foreground="green")
    
    def on_auto_set_resolution(self):
        """Handle auto set resolution"""
        logger.info("Auto set resolution requested")
        self.layout.status_label.config(text="Resolution auto-set", foreground="green")
    
    def run(self):
        """Run the test application"""
        # Add some instructions
        instructions = ttk.Label(
            self.main_frame,
            text="🎯 Improved Seedream V4 Layout Test - Try the new compact design with collapsible sections!",
            font=('Arial', 10, 'bold'),
            foreground='#495057'
        )
        instructions.pack(pady=(0, 10))
        
        self.root.mainloop()


def main():
    """Main function"""
    try:
        app = ImprovedSeedreamTestApp()
        app.run()
    except Exception as e:
        logger.error(f"Error running test app: {e}")
        print(f"Error: {e}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
