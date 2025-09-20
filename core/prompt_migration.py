"""
Prompt Migration Helper
For WaveSpeed AI Creative Suite

Migrates existing JSON prompt files to the enhanced prompt management system.
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Optional
from core.prompt_manager_core import EnhancedPromptManager, PromptData
from core.logger import get_logger

logger = get_logger()

class PromptMigrationHelper:
    """Helper class for migrating existing prompts to the enhanced system"""
    
    def __init__(self):
        self.manager = EnhancedPromptManager()
        self.migration_stats = {
            "total_migrated": 0,
            "errors": 0,
            "files_processed": 0
        }
    
    def migrate_all_existing_prompts(self) -> Dict[str, int]:
        """Migrate all existing prompt files to the enhanced system"""
        logger.info("Starting migration of existing prompt files...")
        
        # Define migration mapping
        migration_files = [
            ("data/saved_prompts.json", "nano_banana", "Nano Banana Editor"),
            ("data/seededit_prompts.json", "seededit", "SeedEdit"),
            ("data/seedream_v4_prompts.json", "seedream_v4", "Seedream V4"),
            ("data/video_prompts.json", "wan_22", "Wan 2.2"),
            ("data/seeddance_prompts.json", "seeddance", "SeedDance Pro")
        ]
        
        for file_path, model_type, model_name in migration_files:
            if os.path.exists(file_path):
                logger.info(f"Migrating {file_path} for {model_name}...")
                self.migrate_file(file_path, model_type, model_name)
            else:
                logger.info(f"File not found: {file_path}")
        
        logger.info(f"Migration completed. Stats: {self.migration_stats}")
        return self.migration_stats
    
    def migrate_file(self, file_path: str, model_type: str, model_name: str) -> int:
        """Migrate a single prompt file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.migration_stats["files_processed"] += 1
            migrated_count = 0
            
            if isinstance(data, list):
                # Handle list of prompts
                for prompt_text in data:
                    if self.migrate_single_prompt(prompt_text, model_type, model_name):
                        migrated_count += 1
            elif isinstance(data, dict):
                # Handle dictionary format (if prompts are stored as key-value pairs)
                for name, prompt_text in data.items():
                    if self.migrate_single_prompt(prompt_text, model_type, model_name, name):
                        migrated_count += 1
            else:
                logger.warning(f"Unexpected data format in {file_path}")
                self.migration_stats["errors"] += 1
            
            self.migration_stats["total_migrated"] += migrated_count
            logger.info(f"Migrated {migrated_count} prompts from {file_path}")
            return migrated_count
            
        except Exception as e:
            logger.error(f"Error migrating {file_path}: {e}")
            self.migration_stats["errors"] += 1
            return 0
    
    def migrate_single_prompt(self, prompt_text: str, model_type: str, model_name: str, custom_name: Optional[str] = None) -> bool:
        """Migrate a single prompt"""
        try:
            if not prompt_text or not prompt_text.strip():
                return False
            
            # Clean up the prompt text
            prompt_text = prompt_text.strip()
            
            # Generate a name if not provided
            if not custom_name:
                name = prompt_text[:50] + "..." if len(prompt_text) > 50 else prompt_text
            else:
                name = custom_name
            
            # Create enhanced prompt
            prompt = self.manager.create_prompt(
                name=name,
                content=prompt_text,
                model_type=model_type,
                auto_categorize=True
            )
            
            # Add some metadata
            prompt.description = f"Migrated from {model_name} prompt library"
            
            # Save the prompt
            success = self.manager.db.save_prompt(prompt)
            if success:
                logger.debug(f"Migrated prompt: {name}")
                return True
            else:
                logger.warning(f"Failed to save prompt: {name}")
                return False
                
        except Exception as e:
            logger.error(f"Error migrating single prompt: {e}")
            self.migration_stats["errors"] += 1
            return False
    
    def create_sample_prompts(self) -> int:
        """Create sample prompts for demonstration"""
        logger.info("Creating sample prompts...")
        
        sample_prompts = [
            {
                "name": "Watercolor Portrait",
                "content": "beautiful watercolor portrait of a young woman with flowing hair, soft lighting, artistic style",
                "model_type": "nano_banana",
                "category": "🎨 Artistic Styles",
                "subcategory": "Watercolor",
                "tags": ["portrait", "watercolor", "artistic", "soft"]
            },
            {
                "name": "Cinematic Landscape",
                "content": "dramatic mountain landscape at sunset, cinematic lighting, epic composition, high detail",
                "model_type": "seedream_v4",
                "category": "🌍 Environments",
                "subcategory": "Landscapes",
                "tags": ["landscape", "cinematic", "dramatic", "detailed"]
            },
            {
                "name": "Professional Headshot",
                "content": "professional headshot of a business person, clean background, corporate style, high quality",
                "model_type": "universal",
                "category": "💼 Professional",
                "subcategory": "Business",
                "tags": ["professional", "business", "clean", "corporate"]
            },
            {
                "name": "Fantasy Character",
                "content": "fantasy warrior character, detailed armor, magical effects, concept art style",
                "model_type": "seedream_v4",
                "category": "🎪 Creative",
                "subcategory": "Fantasy",
                "tags": ["fantasy", "character", "detailed", "magical"]
            },
            {
                "name": "Social Media Post",
                "content": "vibrant social media post design, trendy colors, modern typography, Instagram style",
                "model_type": "nano_banana",
                "category": "📱 Social Media",
                "subcategory": "Instagram",
                "tags": ["social", "vibrant", "trendy", "modern"]
            }
        ]
        
        created_count = 0
        for prompt_data in sample_prompts:
            try:
                prompt = PromptData(
                    id="",  # Will be auto-generated
                    name=prompt_data["name"],
                    content=prompt_data["content"],
                    category=prompt_data["category"],
                    subcategory=prompt_data["subcategory"],
                    tags=prompt_data["tags"],
                    model_type=prompt_data["model_type"],
                    description="Sample prompt for demonstration"
                )
                
                if self.manager.db.save_prompt(prompt):
                    created_count += 1
                    logger.debug(f"Created sample prompt: {prompt_data['name']}")
                    
            except Exception as e:
                logger.error(f"Error creating sample prompt {prompt_data['name']}: {e}")
        
        logger.info(f"Created {created_count} sample prompts")
        return created_count
    
    def backup_existing_files(self) -> bool:
        """Create backup of existing prompt files before migration"""
        try:
            backup_dir = Path("data/backup")
            backup_dir.mkdir(exist_ok=True)
            
            files_to_backup = [
                "data/saved_prompts.json",
                "data/seededit_prompts.json", 
                "data/seedream_v4_prompts.json",
                "data/video_prompts.json",
                "data/seeddance_prompts.json"
            ]
            
            backed_up = 0
            for file_path in files_to_backup:
                if os.path.exists(file_path):
                    backup_path = backup_dir / Path(file_path).name
                    import shutil
                    shutil.copy2(file_path, backup_path)
                    backed_up += 1
                    logger.info(f"Backed up {file_path} to {backup_path}")
            
            logger.info(f"Backed up {backed_up} files to {backup_dir}")
            return backed_up > 0
            
        except Exception as e:
            logger.error(f"Error creating backup: {e}")
            return False
    
    def get_migration_report(self) -> str:
        """Generate a migration report"""
        report = f"""
📊 Prompt Migration Report
========================

Files Processed: {self.migration_stats['files_processed']}
Total Prompts Migrated: {self.migration_stats['total_migrated']}
Errors: {self.migration_stats['errors']}

Migration Status: {'✅ Success' if self.migration_stats['errors'] == 0 else '⚠️ Completed with errors'}

Next Steps:
1. Test the enhanced prompt browser
2. Verify all prompts are accessible
3. Remove old JSON files if migration was successful
4. Train users on the new system
        """
        return report.strip()


def run_migration():
    """Run the complete migration process"""
    logger.info("Starting prompt migration process...")
    
    migration_helper = PromptMigrationHelper()
    
    # Step 1: Create backup
    logger.info("Step 1: Creating backup of existing files...")
    migration_helper.backup_existing_files()
    
    # Step 2: Migrate existing prompts
    logger.info("Step 2: Migrating existing prompts...")
    migration_helper.migrate_all_existing_prompts()
    
    # Step 3: Create sample prompts if no prompts exist
    if migration_helper.migration_stats["total_migrated"] == 0:
        logger.info("Step 3: No existing prompts found, creating sample prompts...")
        migration_helper.create_sample_prompts()
    
    # Step 4: Generate report
    logger.info("Step 4: Generating migration report...")
    report = migration_helper.get_migration_report()
    logger.info(f"Migration Report:\n{report}")
    
    return migration_helper.migration_stats


if __name__ == "__main__":
    # Run migration when script is executed directly
    stats = run_migration()
    print(f"Migration completed with stats: {stats}")
