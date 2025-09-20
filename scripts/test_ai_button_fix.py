#!/usr/bin/env python3
"""
Test script to validate AI button functionality after fixes
Tests both regular AI assistance and filter training buttons
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import tkinter as tk
from tkinter import ttk, messagebox
from ui.components.enhanced_seededit_layout import EnhancedSeedEditLayout
from ui.components.enhanced_compact_layout import EnhancedCompactLayout
from core.logger import get_logger

logger = get_logger()

class AIButtonTestApp:
    """Test application to validate AI button functionality"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("AI Button Functionality Test")
        self.root.geometry("1000x800")
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the test UI"""
        # Create notebook for different layout tests
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Test 1: Enhanced SeedEdit Layout
        self.test_enhanced_seededit(notebook)
        
        # Test 2: Enhanced Compact Layout
        self.test_enhanced_compact(notebook)
        
        # Status area
        self.setup_status_area()
    
    def test_enhanced_seededit(self, parent):
        """Test enhanced SeedEdit layout with AI buttons"""
        frame = ttk.Frame(parent)
        parent.add(frame, text="Enhanced SeedEdit Test")
        
        # Create a mock tab instance
        class MockTab:
            pass
        
        mock_tab = MockTab()
        
        try:
            # Create the layout
            layout = EnhancedSeedEditLayout(frame, mock_tab, None)
            
            # Add some test text to the prompt
            layout.prompt_text.insert("1.0", "Test prompt for SeedEdit")
            
            self.log_status("✅ Enhanced SeedEdit layout created successfully")
            
        except Exception as e:
            self.log_status(f"❌ Enhanced SeedEdit layout failed: {str(e)}")
            logger.error(f"Enhanced SeedEdit test error: {e}")
    
    def test_enhanced_compact(self, parent):
        """Test enhanced compact layout with AI buttons"""
        frame = ttk.Frame(parent)
        parent.add(frame, text="Enhanced Compact Test")
        
        # Create a mock tab instance
        class MockTab:
            pass
        
        mock_tab = MockTab()
        
        try:
            # Create the layout
            layout = EnhancedCompactLayout(frame, mock_tab, "TestModel", "Test Layout")
            
            # Add some test text to the prompt
            layout.prompt_text.insert("1.0", "Test prompt for compact layout")
            
            self.log_status("✅ Enhanced Compact layout created successfully")
            
        except Exception as e:
            self.log_status(f"❌ Enhanced Compact layout failed: {str(e)}")
            logger.error(f"Enhanced Compact test error: {e}")
    
    def setup_status_area(self):
        """Setup status logging area"""
        status_frame = ttk.LabelFrame(self.root, text="Test Status Log", padding=10)
        status_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # Status text area
        self.status_text = tk.Text(status_frame, height=8, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(status_frame, orient=tk.VERTICAL, command=self.status_text.yview)
        self.status_text.configure(yscrollcommand=scrollbar.set)
        
        self.status_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Test buttons
        button_frame = ttk.Frame(status_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(button_frame, text="🤖 Test AI Buttons", 
                  command=self.test_ai_buttons).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="🛡️ Test Filter Training", 
                  command=self.test_filter_training).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="🧪 Run All Tests", 
                  command=self.run_all_tests).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="🗑️ Clear Log", 
                  command=self.clear_log).pack(side=tk.RIGHT, padx=5)
        
        # Initial status
        self.log_status("🚀 AI Button Test Application Started")
        self.log_status("📝 Click buttons above to test AI functionality")
    
    def test_ai_buttons(self):
        """Test regular AI assistance buttons"""
        try:
            self.log_status("\n🤖 Testing Regular AI Assistance...")
            
            # Try to find layouts in the notebook
            notebook_children = self.root.winfo_children()[0].winfo_children()
            
            for i, child in enumerate(notebook_children):
                try:
                    # Look for layout objects
                    for widget in child.winfo_children():
                        if hasattr(widget, 'improve_prompt_with_ai'):
                            self.log_status(f"✅ Tab {i+1}: AI button method found")
                            # Don't actually call it in test mode
                            return
                except:
                    continue
            
            self.log_status("⚠️ No AI button methods found")
            
        except Exception as e:
            self.log_status(f"❌ AI button test failed: {str(e)}")
    
    def test_filter_training(self):
        """Test filter training buttons"""
        try:
            self.log_status("\n🛡️ Testing Filter Training...")
            
            # Try to find layouts in the notebook
            notebook_children = self.root.winfo_children()[0].winfo_children()
            
            for i, child in enumerate(notebook_children):
                try:
                    # Look for layout objects
                    for widget in child.winfo_children():
                        if hasattr(widget, 'open_filter_training'):
                            self.log_status(f"✅ Tab {i+1}: Filter training method found")
                            # Don't actually call it in test mode
                            return
                except:
                    continue
            
            self.log_status("⚠️ No filter training methods found")
            
        except Exception as e:
            self.log_status(f"❌ Filter training test failed: {str(e)}")
    
    def run_all_tests(self):
        """Run comprehensive tests"""
        self.log_status("\n🧪 Running Comprehensive AI Button Tests...\n")
        
        # Test imports
        self.test_imports()
        
        # Test AI integration
        self.test_ai_integration()
        
        # Test learning system
        self.test_learning_system()
        
        self.log_status("\n✅ All tests completed!")
    
    def test_imports(self):
        """Test if all required modules can be imported"""
        try:
            from ui.components.ai_prompt_chat import show_ai_prompt_chat
            self.log_status("✅ AI chat module imported successfully")
        except Exception as e:
            self.log_status(f"❌ AI chat import failed: {str(e)}")
        
        try:
            from ui.components.ai_chat_integration_helper import AIChatMixin
            self.log_status("✅ AI integration helper imported successfully")
        except Exception as e:
            self.log_status(f"❌ AI integration helper import failed: {str(e)}")
        
        try:
            from core.learning_integration_manager import learning_integration_manager
            self.log_status("✅ Learning integration manager imported successfully")
        except Exception as e:
            self.log_status(f"❌ Learning integration manager import failed: {str(e)}")
    
    def test_ai_integration(self):
        """Test AI integration functionality"""
        try:
            from ui.components.ai_chat_integration_helper import AIChatIntegrationHelper
            
            # Test if helper class has required methods
            if hasattr(AIChatIntegrationHelper, 'open_ai_prompt_assistant'):
                self.log_status("✅ AI prompt assistant method available")
            else:
                self.log_status("❌ AI prompt assistant method missing")
                
            if hasattr(AIChatIntegrationHelper, 'open_filter_training_assistant'):
                self.log_status("✅ Filter training assistant method available")
            else:
                self.log_status("❌ Filter training assistant method missing")
                
        except Exception as e:
            self.log_status(f"❌ AI integration test failed: {str(e)}")
    
    def test_learning_system(self):
        """Test learning system integration"""
        try:
            from core.adaptive_filter_learning_system import adaptive_learning_system
            self.log_status("✅ Adaptive learning system available")
            
            from ui.components.smart_learning_panel import create_smart_learning_panel
            self.log_status("✅ Smart learning panel available")
            
        except Exception as e:
            self.log_status(f"❌ Learning system test failed: {str(e)}")
    
    def log_status(self, message: str):
        """Log status message to the text area"""
        self.status_text.insert(tk.END, f"{message}\n")
        self.status_text.see(tk.END)
        self.root.update_idletasks()
    
    def clear_log(self):
        """Clear the status log"""
        self.status_text.delete(1.0, tk.END)
        self.log_status("🗑️ Log cleared")
    
    def run(self):
        """Run the test application"""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self.log_status("🛑 Test interrupted by user")
        except Exception as e:
            self.log_status(f"💥 Unexpected error: {str(e)}")

def main():
    """Main entry point"""
    print("🧪 Starting AI Button Functionality Test...")
    
    try:
        app = AIButtonTestApp()
        app.run()
    except Exception as e:
        print(f"💥 Test application failed to start: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())