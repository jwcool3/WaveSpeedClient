#!/usr/bin/env python3
"""
WaveSpeed AI Application Launcher

Main entry point for the WaveSpeed AI GUI application.
This launcher handles the new organized folder structure.
"""

import sys
import os

# Add the current directory to Python path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """Main entry point"""
    try:
        from app.main_app import WaveSpeedAIApp
        
        print("Starting WaveSpeed AI Application...")
        app = WaveSpeedAIApp()
        app.run()
        
    except ImportError as e:
        print(f"Import Error: {e}")
        print("Please ensure all dependencies are installed:")
        print("pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"Error starting application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
