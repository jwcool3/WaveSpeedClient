#!/usr/bin/env python3
"""
Test script for the improved SeedEdit layout
Demonstrates the enhanced 2-column design with all improvements
"""

import sys
import os
import tkinter as tk
from tkinter import ttk

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from ui.components.improved_seededit_layout import ImprovedSeedEditLayout
from core.logger import get_logger

logger = get_logger()


class MockTab:
    """Mock tab instance for testing"""
    def __init__(self):
        self.frame = None


class ImprovedSeedEditTestApp:
    """Test application for the improved SeedEdit layout"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Improved SeedEdit Layout Test - WaveSpeed AI")
        self.root.geometry("1600x1000")
        self.root.configure(bg='#f8f9fa')
        
        # Create main frame
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create the improved SeedEdit layout
        self.layout = ImprovedSeedEditLayout(self.main_frame)
        
        # Add some test data
        self.setup_test_data()
        
        # Add instructions
        self.add_instructions()
    
    def setup_test_data(self):
        """Add some test data to the layout"""
        # Add sample prompts to the preset dropdown
        sample_prompts = [
            "Change the background to a beautiful sunset landscape",
            "Make the person smile and add a warm glow effect",
            "Convert to black and white with dramatic lighting",
            "Add a vintage film effect with grain and color grading",
            "Change the clothing to a formal business suit",
            "Add a magical sparkle effect around the subject",
            "Transform into a watercolor painting style",
            "Add a neon cyberpunk aesthetic with glowing elements"
        ]
        
        self.layout.preset_combo['values'] = sample_prompts
        
        # Set a sample prompt
        self.layout.prompt_text.delete("1.0", tk.END)
        self.layout.prompt_text.insert("1.0", "Change the background to a beautiful sunset landscape with warm golden light")
    
    def add_instructions(self):
        """Add instructions for testing"""
        instructions_frame = ttk.Frame(self.main_frame)
        instructions_frame.pack(fill=tk.X, pady=(0, 10))
        
        instructions = ttk.Label(
            instructions_frame,
            text="🎯 Improved SeedEdit Layout Test - Key Features:\n"
                 "✅ Two balanced columns (controls | images)\n"
                 "✅ Primary action button right under prompt\n"
                 "✅ Dynamic image scaling with minimal margins\n"
                 "✅ Side-by-side comparison instead of tabs\n"
                 "✅ Horizontal settings layout to save space\n"
                 "✅ No wasted space between columns",
            font=('Arial', 10),
            foreground='#495057',
            justify=tk.LEFT
        )
        instructions.pack(anchor=tk.W)
        
        # Add test buttons
        test_frame = ttk.Frame(instructions_frame)
        test_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Button(
            test_frame,
            text="📁 Load Test Image",
            command=self.load_test_image,
            width=15
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(
            test_frame,
            text="🎲 Randomize Settings",
            command=self.randomize_settings,
            width=18
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(
            test_frame,
            text="⚖️ Test Comparison",
            command=self.test_comparison,
            width=15
        ).pack(side=tk.LEFT)
    
    def load_test_image(self):
        """Load a test image"""
        # Try to find a sample image in the project
        sample_paths = [
            "docs/sample_image.png",
            "data/sample.png",
            "WaveSpeed_Results/Image_Editor/sample.png"
        ]
        
        for path in sample_paths:
            if os.path.exists(path):
                self.layout.load_image(path)
                return
        
        # If no sample image found, open file dialog
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
    
    def randomize_settings(self):
        """Randomize settings for testing"""
        import random
        
        # Randomize guidance scale
        guidance_values = ["0.1", "0.2", "0.3", "0.4", "0.5", "0.6", "0.7", "0.8", "0.9", "1.0"]
        self.layout.guidance_var.set(random.choice(guidance_values))
        
        # Randomize seed
        self.layout.seed_var.set(str(random.randint(1, 999999)))
        
        # Randomize format
        formats = ["png", "jpg", "webp"]
        self.layout.format_var.set(random.choice(formats))
        
        # Load random sample prompt
        sample_prompts = [
            "Change the background to a beautiful sunset landscape",
            "Make the person smile and add a warm glow effect",
            "Convert to black and white with dramatic lighting",
            "Add a vintage film effect with grain and color grading",
            "Change the clothing to a formal business suit",
            "Add a magical sparkle effect around the subject",
            "Transform into a watercolor painting style",
            "Add a neon cyberpunk aesthetic with glowing elements"
        ]
        
        sample = random.choice(sample_prompts)
        self.layout.prompt_text.delete("1.0", tk.END)
        self.layout.prompt_text.insert("1.0", sample)
        
        print("Settings randomized!")
    
    def test_comparison(self):
        """Test the comparison feature"""
        if not self.layout.selected_image_path:
            print("Please load an image first to test comparison")
            return
        
        # Simulate having a result image
        self.layout.result_image_path = self.layout.selected_image_path
        self.layout.toggle_comparison_mode()
        print("Comparison mode activated!")
    
    def run(self):
        """Run the test application"""
        self.root.mainloop()


def main():
    """Main function"""
    try:
        app = ImprovedSeedEditTestApp()
        app.run()
    except Exception as e:
        logger.error(f"Error running test app: {e}")
        print(f"Error: {e}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
