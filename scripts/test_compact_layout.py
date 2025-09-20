#!/usr/bin/env python3
"""
Test script for the new compact layout
Demonstrates the improved UI design
"""

import sys
import os
import tkinter as tk
from tkinter import ttk

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from ui.components.enhanced_compact_layout import EnhancedCompactLayout
from core.logger import get_logger

logger = get_logger()


class MockTab:
    """Mock tab instance for testing"""
    def __init__(self):
        self.frame = None


class CompactLayoutTestApp:
    """Test application for the compact layout"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Compact Layout Test - WaveSpeed AI")
        self.root.geometry("1400x900")
        self.root.configure(bg='#f8f9fa')
        
        # Create main frame
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create mock tab
        self.mock_tab = MockTab()
        self.mock_tab.frame = self.main_frame
        
        # Create compact layout
        self.layout = EnhancedCompactLayout(
            parent_frame=self.main_frame,
            tab_instance=self.mock_tab,
            model_type="seedream_v4",
            title="Seedream V4 - Compact Layout Test"
        )
        
        # Set up callbacks
        self.layout.on_image_selected = self.on_image_selected
        self.layout.on_process_requested = self.on_process_requested
        self.layout.on_status_update = self.on_status_update
        
        # Add some test data
        self.setup_test_data()
    
    def setup_test_data(self):
        """Add some test data to the layout"""
        # Add sample prompts
        sample_prompts = [
            "Transform the subject into a cyberpunk character with neon lights",
            "Change the background to a beautiful sunset landscape",
            "Make the person smile and add a warm glow effect",
            "Create a fantasy portrait with magical elements",
            "Convert to black and white with dramatic lighting"
        ]
        
        self.layout.prompts_combo['values'] = sample_prompts
        
        # Add some recent results
        recent_results = [
            "seedream_v4_20250911_120000_cyberpunk_character.png",
            "seedream_v4_20250911_115500_sunset_landscape.png",
            "seedream_v4_20250911_115000_smiling_portrait.png",
            "seedream_v4_20250911_114500_fantasy_portrait.png",
            "seedream_v4_20250911_114000_dramatic_bw.png"
        ]
        
        for result in recent_results:
            self.layout.results_listbox.insert(tk.END, result)
    
    def on_image_selected(self, image_path):
        """Handle image selection"""
        logger.info(f"Image selected: {image_path}")
        self.layout.update_status(f"Image loaded: {os.path.basename(image_path)}", "success")
    
    def on_process_requested(self):
        """Handle process request"""
        logger.info("Process requested")
        
        # Simulate processing
        import threading
        import time
        
        def simulate_processing():
            self.layout.update_status("Processing...", "info")
            time.sleep(3)  # Simulate processing time
            
            # Simulate success
            self.layout.after_processing(
                success=True,
                result_url="https://example.com/result.png"
            )
        
        threading.Thread(target=simulate_processing, daemon=True).start()
    
    def on_status_update(self, message, status_type):
        """Handle status updates"""
        logger.info(f"Status: {message} ({status_type})")
    
    def run(self):
        """Run the test application"""
        # Add some instructions
        instructions = ttk.Label(
            self.main_frame,
            text="🎯 Compact Layout Test - Try selecting an image, entering a prompt, and clicking the process button!",
            font=('Arial', 10, 'bold'),
            foreground='#495057'
        )
        instructions.pack(pady=(0, 10))
        
        self.root.mainloop()


def main():
    """Main function"""
    try:
        app = CompactLayoutTestApp()
        app.run()
    except Exception as e:
        logger.error(f"Error running test app: {e}")
        print(f"Error: {e}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
