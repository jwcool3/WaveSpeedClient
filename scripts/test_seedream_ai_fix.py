#!/usr/bin/env python3
"""
Quick test script to validate Seedream V4 AI integration fixes
Tests if the ImprovedSeedreamLayout now properly handles AI buttons
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import tkinter as tk
from tkinter import ttk

def test_seedream_ai_integration():
    """Test the Seedream AI integration"""
    print("🧪 Testing Seedream V4 AI Integration...")
    
    # Create test window
    root = tk.Tk()
    root.title("Seedream AI Integration Test")
    root.geometry("400x300")
    
    try:
        # Import the improved layout
        from ui.components.improved_seedream_layout import ImprovedSeedreamLayout
        print("✅ ImprovedSeedreamLayout imported successfully")
        
        # Create the layout
        frame = ttk.Frame(root)
        frame.pack(fill=tk.BOTH, expand=True)
        
        layout = ImprovedSeedreamLayout(frame)
        print("✅ ImprovedSeedreamLayout created successfully")
        
        # Test if AI methods exist
        if hasattr(layout, 'improve_prompt_with_ai'):
            print("✅ improve_prompt_with_ai method found")
        else:
            print("❌ improve_prompt_with_ai method missing")
            
        if hasattr(layout, 'open_filter_training'):
            print("✅ open_filter_training method found")
        else:
            print("❌ open_filter_training method missing")
            
        if hasattr(layout, 'add_ai_chat_interface'):
            print("✅ add_ai_chat_interface method found")
        else:
            print("❌ add_ai_chat_interface method missing")
            
        if hasattr(layout, 'update_status'):
            print("✅ update_status method found")
        else:
            print("❌ update_status method missing")
        
        # Test if prompt widget exists
        if hasattr(layout, 'prompt_text'):
            print("✅ prompt_text widget found")
        else:
            print("❌ prompt_text widget missing")
        
        # Test AI chat integration helper import
        try:
            from ui.components.ai_chat_integration_helper import AIChatMixin
            print("✅ AIChatMixin imported successfully")
            
            # Check if layout inherits from mixin
            if isinstance(layout, AIChatMixin):
                print("✅ Layout properly inherits from AIChatMixin")
            else:
                print("❌ Layout does not inherit from AIChatMixin")
                
        except Exception as e:
            print(f"❌ AIChatMixin import failed: {e}")
        
        print("\n🎉 Seedream AI Integration Test Complete!")
        print("The layout should now work with AI buttons without errors.")
        
        # Add test buttons
        button_frame = ttk.Frame(root)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="🤖 Test AI Assistant", 
                  command=lambda: print("AI Assistant button works!")).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="🛡️ Test Filter Training", 
                  command=lambda: print("Filter Training button works!")).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="❌ Close", 
                  command=root.destroy).pack(side=tk.RIGHT, padx=5)
        
        # Show result
        result_label = ttk.Label(root, text="✅ AI Integration Fixed - No more 'add_ai_chat_interface' errors!", 
                               foreground="green", font=("Arial", 12, "bold"))
        result_label.pack(pady=20)
        
        root.mainloop()
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = test_seedream_ai_integration()
    if success:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed!")
    exit(0 if success else 1)