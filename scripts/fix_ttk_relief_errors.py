#!/usr/bin/env python3
"""
Script to fix all ttk.Frame relief errors in the codebase
ttk widgets don't support relief parameter - this removes them
"""

import os
import re
from pathlib import Path

def fix_ttk_relief_in_file(file_path):
    """Fix ttk relief issues in a single file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Pattern to match ttk.Frame with relief parameter
        # Matches: ttk.Frame(parent, relief='groove', borderwidth=1, padding="8")
        # Replaces with: ttk.Frame(parent, padding="8")
        pattern = r'(ttk\.Frame\([^)]*?)(?:,\s*)?relief\s*=\s*[\'"][^\'\"]*[\'"](?:,\s*)?(?:borderwidth\s*=\s*\d+(?:,\s*)?)?'
        
        def clean_args(match):
            args = match.group(1)
            # Clean up double commas and trailing commas
            args = re.sub(r',\s*,', ',', args)
            args = re.sub(r',\s*\)', ')', args)
            return args
        
        content = re.sub(pattern, clean_args, content)
        
        # Additional cleanup for any remaining borderwidth without relief
        pattern2 = r'(ttk\.Frame\([^)]*?)(?:,\s*)?borderwidth\s*=\s*\d+(?:,\s*)?'
        content = re.sub(pattern2, clean_args, content)
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Fixed ttk relief errors in {file_path}")
            return True
        else:
            print(f"No ttk relief errors found in {file_path}")
            return False
            
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """Fix all ttk relief errors in the project"""
    print("Fixing TTK Relief Errors in WaveSpeed AI...")
    
    # List of files that need fixing
    files_to_fix = [
        "ui/components/compact_image_layout.py",
        "ui/components/optimized_image_layout.py", 
        "ui/components/optimized_seeddance_layout.py",
        "ui/components/optimized_upscaler_layout.py",
        "ui/components/optimized_wan22_layout.py"
    ]
    
    project_root = Path(__file__).parent.parent
    fixed_count = 0
    
    for file_path in files_to_fix:
        full_path = project_root / file_path
        if full_path.exists():
            if fix_ttk_relief_in_file(full_path):
                fixed_count += 1
        else:
            print(f"File not found: {full_path}")
    
    print(f"\nFixed ttk relief errors in {fixed_count} files!")
    print("The 'unknown option -relief' error should now be resolved.")

if __name__ == "__main__":
    main()