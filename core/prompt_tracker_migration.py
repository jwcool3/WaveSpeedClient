"""
Prompt Tracker Migration Utility
Migrates from old prompt_tracker to enhanced_prompt_tracker
"""

import json
from pathlib import Path
from datetime import datetime
from core.logger import get_logger
from core.prompt_tracker import prompt_tracker
from core.enhanced_prompt_tracker import enhanced_prompt_tracker, PromptQuality, FailureReason

logger = get_logger()

class PromptTrackerMigration:
    """Handles migration from old to new prompt tracking system"""
    
    def __init__(self):
        self.old_tracker = prompt_tracker
        self.new_tracker = enhanced_prompt_tracker
    
    def migrate_existing_data(self):
        """Migrate existing prompt data to enhanced format"""
        logger.info("Starting prompt tracker data migration...")
        
        try:
            # Migrate successful prompts
            self._migrate_successful_prompts()
            
            # Migrate failed prompts
            self._migrate_failed_prompts()
            
            # Create backup of old files
            self._backup_old_files()
            
            logger.info("✅ Prompt tracker migration completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Migration failed: {e}")
            return False
    
    def _migrate_successful_prompts(self):
        """Migrate successful prompts to enhanced format"""
        old_file = Path("data/successful_prompts.json")
        if not old_file.exists():
            logger.info("No old successful prompts to migrate")
            return
        
        with open(old_file, 'r', encoding='utf-8') as f:
            old_data = json.load(f)
        
        migrated_count = 0
        for old_prompt in old_data.get("prompts", []):
            try:
                # Convert to enhanced format
                self.new_tracker.log_successful_prompt(
                    prompt=old_prompt.get("prompt", ""),
                    ai_model=old_prompt.get("ai_model", "unknown"),
                    result_url=old_prompt.get("result_url"),
                    save_path=old_prompt.get("save_path"),
                    save_method="auto",  # Assume auto for old data
                    model_parameters=old_prompt.get("additional_context", {}),
                    additional_context={
                        "migrated_from_old_tracker": True,
                        "original_timestamp": old_prompt.get("timestamp")
                    }
                )
                migrated_count += 1
                
            except Exception as e:
                logger.warning(f"Failed to migrate successful prompt: {e}")
        
        logger.info(f"Migrated {migrated_count} successful prompts")
    
    def _migrate_failed_prompts(self):
        """Migrate failed prompts to enhanced format"""
        old_file = Path("data/failed_prompts.json")
        if not old_file.exists():
            logger.info("No old failed prompts to migrate")
            return
        
        with open(old_file, 'r', encoding='utf-8') as f:
            old_data = json.load(f)
        
        migrated_count = 0
        for old_prompt in old_data.get("prompts", []):
            try:
                # Determine failure reason from error message
                error_msg = old_prompt.get("error_message", "").lower()
                failure_reason = self._categorize_failure_reason(error_msg)
                
                # Convert to enhanced format
                self.new_tracker.log_failed_prompt(
                    prompt=old_prompt.get("prompt", ""),
                    ai_model=old_prompt.get("ai_model", "unknown"),
                    error_message=old_prompt.get("error_message", ""),
                    failure_reason=failure_reason,
                    http_status=old_prompt.get("http_status"),
                    model_parameters=old_prompt.get("additional_context", {}),
                    additional_context={
                        "migrated_from_old_tracker": True,
                        "original_timestamp": old_prompt.get("timestamp")
                    }
                )
                migrated_count += 1
                
            except Exception as e:
                logger.warning(f"Failed to migrate failed prompt: {e}")
        
        logger.info(f"Migrated {migrated_count} failed prompts")
    
    def _categorize_failure_reason(self, error_message: str) -> FailureReason:
        """Categorize old error messages into new failure reasons"""
        error_lower = error_message.lower()
        
        if "filter" in error_lower or "content" in error_lower:
            return FailureReason.CONTENT_FILTER
        elif "timeout" in error_lower:
            return FailureReason.TIMEOUT
        elif "network" in error_lower or "connection" in error_lower:
            return FailureReason.NETWORK_ERROR
        elif "server" in error_lower or "500" in error_lower:
            return FailureReason.SERVER_ERROR
        elif "quota" in error_lower or "limit" in error_lower:
            return FailureReason.QUOTA_EXCEEDED
        elif "parameter" in error_lower or "invalid" in error_lower:
            return FailureReason.INVALID_PARAMETERS
        elif "nsfw" in error_lower:
            return FailureReason.NSFW_CONTENT
        else:
            return FailureReason.OTHER
    
    def _backup_old_files(self):
        """Create backup of old tracking files"""
        backup_dir = Path("data/backup_old_tracker")
        backup_dir.mkdir(exist_ok=True)
        
        old_files = [
            "data/successful_prompts.json",
            "data/failed_prompts.json",
            "data/prompt_statistics.json"
        ]
        
        for old_file in old_files:
            old_path = Path(old_file)
            if old_path.exists():
                backup_path = backup_dir / f"{old_path.name}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                old_path.rename(backup_path)
                logger.info(f"Backed up {old_file} to {backup_path}")

# Global migration instance
tracker_migration = PromptTrackerMigration()

def run_migration():
    """Run the migration process"""
    return tracker_migration.migrate_existing_data()