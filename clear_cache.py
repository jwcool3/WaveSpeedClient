"""
Clear all Python bytecode cache to force reload of updated modules
"""
import os
import shutil
import sys

def clear_pycache(root_dir="."):
    """Remove all __pycache__ directories recursively"""
    removed_count = 0
    
    for dirpath, dirnames, filenames in os.walk(root_dir):
        if '__pycache__' in dirnames:
            pycache_path = os.path.join(dirpath, '__pycache__')
            try:
                shutil.rmtree(pycache_path)
                print(f"✓ Removed: {pycache_path}")
                removed_count += 1
            except Exception as e:
                print(f"✗ Failed to remove {pycache_path}: {e}")
    
    # Also remove .pyc files
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith('.pyc'):
                pyc_path = os.path.join(dirpath, filename)
                try:
                    os.remove(pyc_path)
                    print(f"✓ Removed: {pyc_path}")
                    removed_count += 1
                except Exception as e:
                    print(f"✗ Failed to remove {pyc_path}: {e}")
    
    print(f"\n✅ Cleared {removed_count} cache files/directories")
    print("🔄 Python will now reload all modules from source")
    print("\n⚠️  Please restart your application for changes to take effect")

if __name__ == "__main__":
    print("🧹 Clearing Python bytecode cache...\n")
    clear_pycache()

