"""
Migrate Seedream V4 saved prompts to Enhanced Prompt Library
"""

import json
import sys
import os
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.prompt_manager_core import EnhancedPromptManager, PromptData, CategoryManager
from core.logger import get_logger

logger = get_logger()

def migrate_seedream_prompts():
    """Migrate existing Seedream V4 prompts to Enhanced Prompt Library"""
    try:
        # Initialize the prompt manager
        manager = EnhancedPromptManager()
        
        # Load existing Seedream V4 prompts
        seedream_prompts_file = project_root / "data" / "seedream_v4_prompts.json"
        
        if not seedream_prompts_file.exists():
            logger.info("No Seedream V4 prompts file found")
            return
        
        with open(seedream_prompts_file, 'r', encoding='utf-8') as f:
            seedream_prompts = json.load(f)
        
        logger.info(f"Found {len(seedream_prompts)} Seedream V4 prompts to migrate")
        
        # Process each prompt
        migrated_count = 0
        skipped_count = 0
        
        for i, prompt_content in enumerate(seedream_prompts):
            if not prompt_content or not prompt_content.strip():
                skipped_count += 1
                continue
            
            # Generate a meaningful name from the prompt
            prompt_name = generate_prompt_name(prompt_content)
            
            # Suggest category based on content
            category, subcategory = CategoryManager.suggest_category(prompt_content)
            
            # Create PromptData object
            prompt_data = PromptData(
                id="",  # Will be auto-generated
                name=prompt_name,
                content=prompt_content.strip(),
                category=category,
                subcategory=subcategory,
                model_type="seedream_v4",
                tags=extract_tags_from_content(prompt_content),
                description=f"Migrated from Seedream V4 saved prompts"
            )
            
            # Check if prompt already exists
            existing_prompts = manager.db.search_prompts(
                query=prompt_content[:50],  # Search by first 50 chars
                model_type="seedream_v4"
            )
            
            # Skip if exact content already exists
            if any(p.content.strip() == prompt_content.strip() for p in existing_prompts):
                logger.info(f"Skipping duplicate prompt: {prompt_name}")
                skipped_count += 1
                continue
            
            # Save the prompt
            if manager.db.save_prompt(prompt_data):
                migrated_count += 1
                logger.info(f"Migrated prompt {i+1}: {prompt_name}")
            else:
                logger.error(f"Failed to migrate prompt {i+1}: {prompt_name}")
                skipped_count += 1
        
        logger.info(f"Migration complete: {migrated_count} prompts migrated, {skipped_count} skipped")
        print(f"✅ Successfully migrated {migrated_count} Seedream V4 prompts to Enhanced Prompt Library")
        print(f"⚠️ Skipped {skipped_count} prompts (duplicates or empty)")
        
    except Exception as e:
        logger.error(f"Error during migration: {e}")
        print(f"❌ Migration failed: {e}")

def generate_prompt_name(prompt_content: str) -> str:
    """Generate a meaningful name from prompt content"""
    # Clean and truncate the prompt for naming
    content = prompt_content.strip()
    
    # Take first meaningful part (up to first comma or period, max 50 chars)
    parts = content.replace('\n', ' ').split(',')
    if len(parts) > 1:
        name = parts[0].strip()
    else:
        name = content.split('.')[0].strip()
    
    # Limit length and clean up
    if len(name) > 50:
        name = name[:47] + "..."
    
    # Capitalize first word
    if name:
        name = name[0].upper() + name[1:] if len(name) > 1 else name.upper()
    
    return name or "Untitled Prompt"

def extract_tags_from_content(prompt_content: str) -> list:
    """Extract relevant tags from prompt content"""
    content_lower = prompt_content.lower()
    tags = []
    
    # Common editing keywords
    editing_keywords = {
        'remove': 'removal',
        'change': 'modification', 
        'transform': 'transformation',
        'swap': 'face-swap',
        'alter': 'alteration',
        'modify': 'modification',
        'replace': 'replacement',
        'keep': 'preservation',
        'bikini': 'clothing',
        'dress': 'clothing',
        'outfit': 'clothing',
        'face': 'portrait',
        'background': 'environment',
        'lighting': 'lighting',
        'pose': 'pose',
        'winter': 'seasonal',
        'snow': 'weather',
        'vacation': 'travel',
        'outdoor': 'environment',
        'indoor': 'environment'
    }
    
    for keyword, tag in editing_keywords.items():
        if keyword in content_lower:
            if tag not in tags:
                tags.append(tag)
    
    # Add model-specific tag
    tags.append('seedream-v4')
    
    return tags

if __name__ == "__main__":
    migrate_seedream_prompts()