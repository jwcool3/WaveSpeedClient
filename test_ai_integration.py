"""
Test AI Integration System
For WaveSpeed AI Creative Suite

This script tests the AI integration components to ensure they work correctly.
"""

import os
import sys
import tkinter as tk
from pathlib import Path

def test_ai_components():
    """Test AI component imports and basic functionality"""
    
    print("🧪 Testing AI Integration Components")
    print("=" * 50)
    
    # Test 1: Check if AI components can be imported
    print("\n1. 📦 Testing Component Imports...")
    
    try:
        from ui.components.fixed_ai_settings import AIAssistantManager, show_ai_settings, get_ai_status
        print("   ✅ fixed_ai_settings.py: Import successful")
    except Exception as e:
        print(f"   ❌ fixed_ai_settings.py: Import failed - {e}")
        return False
    
    try:
        from ui.components.universal_ai_integration import UniversalAIIntegrator, integrate_ai_with_tab
        print("   ✅ universal_ai_integration.py: Import successful")
    except Exception as e:
        print(f"   ❌ universal_ai_integration.py: Import failed - {e}")
        return False
    
    try:
        from core.ai_prompt_advisor import get_ai_advisor
        print("   ✅ ai_prompt_advisor.py: Import successful")
    except Exception as e:
        print(f"   ❌ ai_prompt_advisor.py: Import failed - {e}")
        return False
    
    # Test 2: Check AI status functionality
    print("\n2. 🔍 Testing AI Status Detection...")
    
    try:
        ai_manager = AIAssistantManager()
        status = ai_manager.get_api_status()
        
        print(f"   • Claude Available: {'✅' if status['claude_available'] else '❌'}")
        print(f"   • OpenAI Available: {'✅' if status['openai_available'] else '❌'}")
        print(f"   • Any Available: {'✅' if status['any_available'] else '❌'}")
        print(f"   • Preferred Provider: {status['preferred_provider']}")
        
    except Exception as e:
        print(f"   ❌ AI Status Detection failed: {e}")
        return False
    
    # Test 3: Check .env configuration
    print("\n3. ⚙️ Testing .env Configuration...")
    
    if os.path.exists('.env'):
        print("   ✅ .env file found")
        
        try:
            with open('.env', 'r') as f:
                env_content = f.read()
            
            has_claude = 'CLAUDE_API_KEY' in env_content
            has_openai = 'OPENAI_API_KEY' in env_content
            has_provider = 'AI_ADVISOR_PROVIDER' in env_content
            
            print(f"   • Claude API Key: {'✅' if has_claude else '❌'}")
            print(f"   • OpenAI API Key: {'✅' if has_openai else '❌'}")
            print(f"   • Provider Setting: {'✅' if has_provider else '❌'}")
            
        except Exception as e:
            print(f"   ❌ Error reading .env: {e}")
    else:
        print("   ❌ .env file not found")
        print("   💡 Create .env file with your API keys")
    
    # Test 4: Test AI Advisor initialization
    print("\n4. 🤖 Testing AI Advisor Initialization...")
    
    try:
        advisor = get_ai_advisor()
        print("   ✅ AI Advisor initialized successfully")
        print(f"   • Claude Available: {'✅' if advisor.claude_available else '❌'}")
        print(f"   • OpenAI Available: {'✅' if advisor.openai_available else '❌'}")
        
    except Exception as e:
        print(f"   ❌ AI Advisor initialization failed: {e}")
        return False
    
    # Test 5: Test Universal Integrator
    print("\n5. 🔧 Testing Universal AI Integrator...")
    
    try:
        integrator = UniversalAIIntegrator()
        print("   ✅ Universal AI Integrator initialized")
        print(f"   • AI Available: {'✅' if integrator.ai_available else '❌'}")
        print(f"   • Integrated Tabs: {len(integrator.integrated_tabs)}")
        
    except Exception as e:
        print(f"   ❌ Universal AI Integrator failed: {e}")
        return False
    
    print("\n🎉 All AI Integration Tests Passed!")
    return True

def test_ui_components():
    """Test UI components in a simple window"""
    
    print("\n🖥️ Testing UI Components...")
    
    try:
        # Create a simple test window
        root = tk.Tk()
        root.title("AI Integration Test")
        root.geometry("400x300")
        
        # Test AI settings dialog
        def test_settings():
            try:
                from ui.components.fixed_ai_settings import show_ai_settings
                show_ai_settings(root)
                print("   ✅ AI Settings Dialog: Opened successfully")
            except Exception as e:
                print(f"   ❌ AI Settings Dialog: Failed - {e}")
        
        # Test button
        test_btn = tk.Button(
            root,
            text="🧪 Test AI Settings",
            command=test_settings,
            bg='#3498db',
            fg='white',
            font=('Arial', 12),
            padx=20,
            pady=10
        )
        test_btn.pack(pady=50)
        
        # Status label
        status_label = tk.Label(
            root,
            text="Click the button to test AI settings dialog",
            font=('Arial', 10),
            fg='#666666'
        )
        status_label.pack(pady=10)
        
        # Auto-close after 5 seconds
        def auto_close():
            root.quit()
            root.destroy()
        
        root.after(5000, auto_close)
        
        print("   ✅ Test window created successfully")
        print("   💡 Test window will auto-close in 5 seconds")
        
        root.mainloop()
        
    except Exception as e:
        print(f"   ❌ UI Component Test failed: {e}")
        return False
    
    return True

def show_integration_guide():
    """Show integration guide"""
    
    print("\n📋 AI Integration Guide")
    print("=" * 30)
    
    print("""
🚀 QUICK START:

1. 📁 Ensure these files exist:
   • ui/components/fixed_ai_settings.py
   • ui/components/universal_ai_integration.py
   • core/ai_prompt_advisor.py

2. ⚙️ Configure API keys in .env:
   CLAUDE_API_KEY=your_claude_key_here
   OPENAI_API_KEY=your_openai_key_here
   AI_ADVISOR_PROVIDER=claude

3. 🔄 Restart your application

4. 🎯 Look for these features:
   • "✨ Improve with AI" buttons in all tabs
   • "🛡️ Filter Training" buttons for safety research
   • "🤖 AI Assistant" menu with settings
   • Right-click context menus in prompt fields

🔧 TROUBLESHOOTING:

• Buttons not appearing?
  → Check that API keys are configured
  → Restart the application
  → Use "AI Assistant → Refresh AI Features"

• Settings dialog not working?
  → Verify fixed_ai_settings.py is in place
  → Check for import errors in logs

• API errors?
  → Verify your API keys are valid
  → Check your internet connection
  → Test connections in AI Assistant → Settings

💡 FEATURES:

• Smart prompt enhancement for all AI models
• Model-specific optimization
• Filter training for safety research
• Real-time API status detection
• Automatic button state management
• Right-click context menus
• Comprehensive help documentation
""")

def main():
    """Main test function"""
    
    print("🤖 WaveSpeed AI - Integration Test Suite")
    print("=" * 50)
    
    # Run component tests
    success = test_ai_components()
    
    if success:
        # Run UI tests
        test_ui_components()
        
        # Show integration guide
        show_integration_guide()
        
        print("\n✅ Integration Test Complete!")
        print("Your AI integration system is ready to use.")
        
    else:
        print("\n❌ Integration Test Failed!")
        print("Please fix the issues above before proceeding.")
    
    return success

if __name__ == "__main__":
    main()
