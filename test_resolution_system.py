#!/usr/bin/env python3
"""
Test script for the new resolution multiplier system in Seedream tab
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ui.components.improved_seedream_layout import ImprovedSeedreamLayout
import tkinter as tk
from PIL import Image
import tempfile

def test_resolution_multipliers():
    """Test the new resolution multiplier system"""
    print("Testing resolution multiplier system...")
    
    # Create a test image
    test_image = Image.new('RGB', (800, 600), color='red')
    
    # Save to temporary file
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
        temp_path = temp_file.name
        test_image.save(temp_path, 'PNG')
    
    try:
        # Create root window
        root = tk.Tk()
        root.withdraw()  # Hide the window
        
        # Create the improved layout
        layout = ImprovedSeedreamLayout(root, None, None)
        
        # Load the test image
        layout.load_image(temp_path)
        
        print(f"Original image dimensions: {layout.original_image_width}x{layout.original_image_height}")
        
        # Test each multiplier
        multipliers = [1.5, 2.0, 2.5]
        for multiplier in multipliers:
            layout.set_size_multiplier(multiplier)
            width = layout.width_var.get()
            height = layout.height_var.get()
            expected_width = int(800 * multiplier)
            expected_height = int(600 * multiplier)
            
            print(f"Multiplier {multiplier}x:")
            print(f"  Expected: {expected_width}x{expected_height}")
            print(f"  Actual: {width}x{height}")
            print(f"  Match: {width == expected_width and height == expected_height}")
            print()
        
        # Test validation
        print("Testing integer validation:")
        test_values = ["100", "1.5", "abc", "0", "5000", ""]
        for value in test_values:
            is_valid = layout.validate_integer(value)
            print(f"  '{value}' -> {is_valid}")
        
        # Test custom scale functionality (without showing dialog)
        print("\nTesting custom scale functionality:")
        print("  Custom scale dialog method available:", hasattr(layout, 'show_custom_scale_dialog'))
        
        # Test multiple image functionality
        print("\nTesting multiple image functionality:")
        print("  Multiple image support available:", hasattr(layout, 'load_images'))
        print("  Image count display method available:", hasattr(layout, 'update_image_count_display'))
        
        # Test with multiple images
        test_images = [temp_path] * 3  # Create 3 copies of the same image for testing
        layout.load_images(test_images)
        print(f"  Loaded {len(layout.selected_image_paths)} images")
        print(f"  First image path: {layout.selected_image_path}")
        print(f"  Image count display updated: {hasattr(layout, 'image_name_label')}")
        
        # Test edge cases for multipliers
        print("\nTesting edge cases:")
        edge_multipliers = [0.1, 0.5, 1.0, 3.0, 5.0]
        for multiplier in edge_multipliers:
            layout.set_size_multiplier(multiplier)
            width = layout.width_var.get()
            height = layout.height_var.get()
            print(f"  {multiplier}x -> {width}x{height}")
        
        print("\nAll tests completed!")
        
    finally:
        # Clean up
        try:
            os.unlink(temp_path)
        except:
            pass
        root.destroy()

if __name__ == "__main__":
    test_resolution_multipliers()
