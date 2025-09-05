#!/usr/bin/env python3
"""
Installation script for WaveSpeed AI video player functionality

This script installs the required video player library for embedded video playback.
"""

import subprocess
import sys
import os

def install_package(package):
    """Install a Python package using pip"""
    try:
        print(f"Installing {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ {package} installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install {package}: {e}")
        return False

def check_installation():
    """Check if video player is installed and working"""
    try:
        import tkVideoPlayer
        print("✅ tkVideoPlayer is installed and available!")
        return True
    except ImportError:
        print("❌ tkVideoPlayer is not available")
        return False

def main():
    """Main installation function"""
    print("🎬 WaveSpeed AI Video Player Setup")
    print("=" * 40)
    
    # Check if already installed
    if check_installation():
        print("\n✅ Video player is already installed and ready to use!")
        return
    
    print("\n📦 Installing video player library...")
    
    # Install tkvideoplayer
    if install_package("tkvideoplayer==2.3"):
        print("\n🎉 Installation completed successfully!")
        print("\n📋 Next steps:")
        print("1. Restart the WaveSpeed AI application")
        print("2. Generate a video using Image to Video or SeedDance tabs")
        print("3. The video will now play directly in the application!")
        
        # Verify installation
        print("\n🔍 Verifying installation...")
        if check_installation():
            print("✅ All good! Video player is ready to use.")
        else:
            print("⚠️  Installation completed but verification failed.")
            print("   You may need to restart your Python environment.")
    else:
        print("\n❌ Installation failed!")
        print("\n🔧 Troubleshooting:")
        print("1. Make sure you have an active internet connection")
        print("2. Try running: pip install tkvideoplayer==2.3")
        print("3. Check if you have the required permissions")

if __name__ == "__main__":
    main()
