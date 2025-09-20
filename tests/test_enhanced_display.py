#!/usr/bin/env python3
"""
Test script for Enhanced Image Display Components

This script tests the new enhanced image display functionality.
"""

import tkinter as tk
from tkinter import ttk
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from ui.components.enhanced_image_display import EnhancedImageSelector, EnhancedImagePreview, ExpandableImageViewer
    from PIL import Image, ImageDraw
    print("✅ Enhanced image display components imported successfully!")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

def create_test_image():
    """Create a test image for demonstration"""
    img = Image.new('RGB', (800, 600), color='lightblue')
    draw = ImageDraw.Draw(img)
    
    # Draw some test content
    draw.rectangle([50, 50, 750, 550], outline='navy', width=5)
    draw.text((100, 100), "Enhanced Image Display Test", fill='navy')
    draw.text((100, 150), "This is a larger result display", fill='darkblue')
    draw.text((100, 200), "Double-click to expand to full size", fill='darkblue')
    draw.text((100, 250), "Right-click for context menu", fill='darkblue')
    
    # Save test image
    test_path = "test_image.png"
    img.save(test_path)
    return test_path, img

def test_enhanced_display():
    """Test the enhanced display components"""
    root = tk.Tk()
    root.title("Enhanced Image Display Test")
    root.geometry("900x700")
    
    # Create test image
    test_path, test_img = create_test_image()
    
    # Create main frame
    main_frame = ttk.Frame(root, padding="10")
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    # Test enhanced image selector
    def on_image_selected(path):
        print(f"Image selected: {path}")
        # Update the preview with the selected image
        preview.update_original_image(path)
        # Simulate a result by using the same image
        preview.update_result_image(image=test_img)
    
    selector = EnhancedImageSelector(
        main_frame, 0, on_image_selected, 
        "Test Enhanced Image Selector:", show_preview=True
    )
    
    # Test enhanced image preview
    preview = EnhancedImagePreview(
        main_frame, 3, "Enhanced Image Preview Test", 
        result_size=(600, 400)
    )
    
    # Add some instructions
    instructions = ttk.Label(
        main_frame,
        text="Instructions:\n"
             "1. Click 'Browse Image' to select an image\n"
             "2. Or drag & drop an image onto the small preview\n"
             "3. Result will show in large preview on right\n"
             "4. Double-click result to expand full-screen\n"
             "5. Right-click result for context menu",
        font=('Arial', 10),
        justify='left'
    )
    instructions.grid(row=5, column=0, columnspan=2, sticky=tk.W, pady=20)
    
    # Auto-load test image
    root.after(1000, lambda: on_image_selected(test_path))
    
    # Cleanup function
    def on_closing():
        try:
            os.remove(test_path)
        except:
            pass
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    print("🚀 Enhanced Image Display test window opened!")
    print("📋 Features to test:")
    print("   • Larger result display")
    print("   • Double-click to expand")
    print("   • Right-click context menu")
    print("   • Drag & drop support")
    print("   • Smaller input preview")
    
    root.mainloop()

if __name__ == "__main__":
    print("🧪 Testing Enhanced Image Display Components")
    print("=" * 50)
    
    try:
        test_enhanced_display()
        print("✅ Test completed successfully!")
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
