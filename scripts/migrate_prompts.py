#!/usr/bin/env python3
"""
Prompt Migration Script
For WaveSpeed AI Creative Suite

This script migrates existing JSON prompt files to the enhanced prompt management system.
Run this script once to upgrade your prompt management to the new enhanced system.
"""

import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.prompt_migration import run_migration
from core.logger import get_logger

logger = get_logger()

def main():
    """Main migration function"""
    print("🚀 WaveSpeed AI - Enhanced Prompt Management Migration")
    print("=" * 60)
    print()
    
    # Check if we're in the right directory
    if not os.path.exists("core/prompt_manager_core.py"):
        print("❌ Error: Please run this script from the WaveSpeed AI project root directory")
        print("   Expected to find: core/prompt_manager_core.py")
        sys.exit(1)
    
    print("📋 This script will:")
    print("   1. Create a backup of your existing prompt files")
    print("   2. Migrate all prompts to the enhanced database system")
    print("   3. Create sample prompts if no existing prompts are found")
    print("   4. Generate a migration report")
    print()
    
    # Ask for confirmation
    response = input("🤔 Do you want to proceed with the migration? (y/N): ").strip().lower()
    if response not in ['y', 'yes']:
        print("❌ Migration cancelled by user")
        sys.exit(0)
    
    print()
    print("🔄 Starting migration process...")
    print()
    
    try:
        # Run the migration
        stats = run_migration()
        
        print()
        print("✅ Migration completed successfully!")
        print()
        print("📊 Migration Statistics:")
        print(f"   • Files processed: {stats['files_processed']}")
        print(f"   • Prompts migrated: {stats['total_migrated']}")
        print(f"   • Errors: {stats['errors']}")
        print()
        
        if stats['total_migrated'] > 0:
            print("🎉 Your prompts have been successfully migrated to the enhanced system!")
            print("   You can now use the new Enhanced Prompt Library in your tabs.")
        else:
            print("📝 No existing prompts were found, but sample prompts have been created.")
            print("   You can start using the Enhanced Prompt Library right away!")
        
        print()
        print("🚀 Next Steps:")
        print("   1. Restart your WaveSpeed AI application")
        print("   2. Look for the '📚 Enhanced Library' button in your tabs")
        print("   3. Explore the new categorized prompt system")
        print("   4. Your old prompt files are backed up in data/backup/")
        print()
        
    except Exception as e:
        print(f"❌ Migration failed with error: {e}")
        logger.error(f"Migration failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
