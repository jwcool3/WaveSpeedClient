"""
Enhanced Prompt Management System - Core Implementation
For WaveSpeed AI Creative Suite

This module provides the foundation for the enhanced prompt management system
with categories, tags, search, and cross-tab functionality.
"""

import json
import sqlite3
import uuid
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import re

@dataclass
class PromptData:
    """Enhanced prompt data structure"""
    id: str
    name: str
    content: str
    category: str = "General"
    subcategory: str = ""
    tags: List[str] = None
    model_type: str = "universal"
    created_date: str = ""
    last_used: str = ""
    usage_count: int = 0
    rating: float = 0.0
    description: str = ""
    preview_image: str = ""
    settings: Dict = None
    ai_enhanced: bool = False
    original_prompt: str = ""
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.settings is None:
            self.settings = {}
        if not self.created_date:
            self.created_date = datetime.now().isoformat()
        if not self.id:
            self.id = str(uuid.uuid4())

class CategoryManager:
    """Manages prompt categories and hierarchies"""
    
    DEFAULT_CATEGORIES = {
        "🎨 Artistic Styles": ["Watercolor", "Oil Painting", "Digital Art", "Sketch", "Pop Art"],
        "👤 Portrait & People": ["Faces", "Expressions", "Poses", "Groups", "Emotions"],
        "🌍 Environments": ["Landscapes", "Interiors", "Cities", "Nature", "Architecture"],
        "🎬 Cinematic": ["Movie Styles", "Lighting", "Moods", "Drama", "Action"],
        "🔧 Technical": ["Upscaling", "Enhancement", "Correction", "Restoration"],
        "🎪 Creative": ["Fantasy", "Sci-Fi", "Abstract", "Surreal", "Conceptual"],
        "📱 Social Media": ["Instagram", "TikTok", "Profile Pics", "Stories", "Posts"],
        "💼 Professional": ["Business", "Corporate", "Marketing", "Logos", "Presentations"]
    }
    
    @classmethod
    def get_categories(cls) -> Dict[str, List[str]]:
        return cls.DEFAULT_CATEGORIES.copy()
    
    @classmethod
    def suggest_category(cls, prompt_text: str) -> Tuple[str, str]:
        """AI-powered category suggestion based on prompt content"""
        prompt_lower = prompt_text.lower()
        
        # Simple keyword-based categorization (can be enhanced with actual AI)
        category_keywords = {
            "🎨 Artistic Styles": ["watercolor", "oil painting", "digital art", "sketch", "artistic"],
            "👤 Portrait & People": ["portrait", "face", "person", "people", "expression"],
            "🌍 Environments": ["landscape", "building", "city", "nature", "environment"],
            "🎬 Cinematic": ["cinematic", "movie", "dramatic", "lighting", "film"],
            "🔧 Technical": ["upscale", "enhance", "fix", "restore", "quality"],
            "🎪 Creative": ["fantasy", "sci-fi", "abstract", "surreal", "magic"],
            "📱 Social Media": ["instagram", "social", "profile", "avatar", "trendy"],
            "💼 Professional": ["business", "corporate", "professional", "logo", "clean"]
        }
        
        for category, keywords in category_keywords.items():
            if any(keyword in prompt_lower for keyword in keywords):
                # Find best subcategory
                subcategories = cls.DEFAULT_CATEGORIES.get(category, [])
                for subcat in subcategories:
                    if subcat.lower() in prompt_lower:
                        return category, subcat
                return category, subcategories[0] if subcategories else ""
        
        return "General", ""

class PromptDatabase:
    """SQLite database manager for prompts"""
    
    def __init__(self, db_path: str = "data/prompts.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        self.init_database()
    
    def init_database(self):
        """Initialize database tables"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS prompts (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    content TEXT NOT NULL,
                    category TEXT DEFAULT 'General',
                    subcategory TEXT DEFAULT '',
                    tags TEXT DEFAULT '[]',
                    model_type TEXT DEFAULT 'universal',
                    created_date TEXT,
                    last_used TEXT,
                    usage_count INTEGER DEFAULT 0,
                    rating REAL DEFAULT 0.0,
                    description TEXT DEFAULT '',
                    preview_image TEXT DEFAULT '',
                    settings TEXT DEFAULT '{}',
                    ai_enhanced BOOLEAN DEFAULT FALSE,
                    original_prompt TEXT DEFAULT ''
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    parent_id INTEGER,
                    display_order INTEGER DEFAULT 0,
                    FOREIGN KEY (parent_id) REFERENCES categories (id)
                )
            ''')
            
            conn.execute('''
                CREATE TABLE IF NOT EXISTS usage_stats (
                    prompt_id TEXT,
                    used_date TEXT,
                    model_type TEXT,
                    success_rating REAL,
                    FOREIGN KEY (prompt_id) REFERENCES prompts (id)
                )
            ''')
            
            # Create indexes for better search performance
            conn.execute('CREATE INDEX IF NOT EXISTS idx_prompts_category ON prompts(category)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_prompts_model_type ON prompts(model_type)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_prompts_usage_count ON prompts(usage_count)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_prompts_rating ON prompts(rating)')
    
    def save_prompt(self, prompt: PromptData) -> bool:
        """Save or update a prompt"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT OR REPLACE INTO prompts VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    prompt.id, prompt.name, prompt.content, prompt.category,
                    prompt.subcategory, json.dumps(prompt.tags), prompt.model_type,
                    prompt.created_date, prompt.last_used, prompt.usage_count,
                    prompt.rating, prompt.description, prompt.preview_image,
                    json.dumps(prompt.settings), prompt.ai_enhanced, prompt.original_prompt
                ))
            return True
        except Exception as e:
            print(f"Error saving prompt: {e}")
            return False
    
    def load_prompt(self, prompt_id: str) -> Optional[PromptData]:
        """Load a specific prompt by ID"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('SELECT * FROM prompts WHERE id = ?', (prompt_id,))
                row = cursor.fetchone()
                if row:
                    return self._row_to_prompt(row)
            return None
        except Exception as e:
            print(f"Error loading prompt: {e}")
            return None
    
    def search_prompts(self, 
                      query: str = "",
                      category: str = "",
                      tags: List[str] = None,
                      model_type: str = "",
                      min_rating: float = 0.0,
                      limit: int = 100) -> List[PromptData]:
        """Advanced prompt search"""
        try:
            sql = "SELECT * FROM prompts WHERE 1=1"
            params = []
            
            if query:
                sql += " AND (content LIKE ? OR name LIKE ? OR description LIKE ?)"
                search_term = f"%{query}%"
                params.extend([search_term, search_term, search_term])
            
            if category:
                sql += " AND category = ?"
                params.append(category)
            
            if model_type:
                sql += " AND (model_type = ? OR model_type = 'universal')"
                params.append(model_type)
            
            if min_rating > 0:
                sql += " AND rating >= ?"
                params.append(min_rating)
            
            if tags:
                # Simple tag search - can be enhanced
                for tag in tags:
                    sql += " AND tags LIKE ?"
                    params.append(f"%{tag}%")
            
            sql += " ORDER BY usage_count DESC, rating DESC LIMIT ?"
            params.append(limit)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(sql, params)
                return [self._row_to_prompt(row) for row in cursor.fetchall()]
                
        except Exception as e:
            print(f"Error searching prompts: {e}")
            return []
    
    def get_popular_prompts(self, model_type: str = "", limit: int = 10) -> List[PromptData]:
        """Get most popular prompts"""
        return self.search_prompts(model_type=model_type, limit=limit)
    
    def get_recent_prompts(self, model_type: str = "", limit: int = 10) -> List[PromptData]:
        """Get recently used prompts"""
        try:
            sql = """
                SELECT * FROM prompts 
                WHERE last_used != '' 
                AND (model_type = ? OR model_type = 'universal' OR ? = '')
                ORDER BY last_used DESC 
                LIMIT ?
            """
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(sql, (model_type, model_type, limit))
                return [self._row_to_prompt(row) for row in cursor.fetchall()]
        except Exception as e:
            print(f"Error getting recent prompts: {e}")
            return []
    
    def record_usage(self, prompt_id: str, model_type: str, success_rating: float = 0.0):
        """Record prompt usage for analytics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Update usage count and last used
                conn.execute('''
                    UPDATE prompts 
                    SET usage_count = usage_count + 1, last_used = ? 
                    WHERE id = ?
                ''', (datetime.now().isoformat(), prompt_id))
                
                # Record usage stats
                conn.execute('''
                    INSERT INTO usage_stats (prompt_id, used_date, model_type, success_rating)
                    VALUES (?, ?, ?, ?)
                ''', (prompt_id, datetime.now().isoformat(), model_type, success_rating))
        except Exception as e:
            print(f"Error recording usage: {e}")
    
    def delete_prompt(self, prompt_id: str) -> bool:
        """Delete a prompt"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('DELETE FROM prompts WHERE id = ?', (prompt_id,))
                conn.execute('DELETE FROM usage_stats WHERE prompt_id = ?', (prompt_id,))
            return True
        except Exception as e:
            print(f"Error deleting prompt: {e}")
            return False
    
    def _row_to_prompt(self, row) -> PromptData:
        """Convert database row to PromptData object"""
        return PromptData(
            id=row[0], name=row[1], content=row[2], category=row[3],
            subcategory=row[4], tags=json.loads(row[5]), model_type=row[6],
            created_date=row[7], last_used=row[8], usage_count=row[9],
            rating=row[10], description=row[11], preview_image=row[12],
            settings=json.loads(row[13]), ai_enhanced=bool(row[14]),
            original_prompt=row[15]
        )

class EnhancedPromptManager:
    """Main prompt management interface"""
    
    def __init__(self):
        self.db = PromptDatabase()
        self.category_manager = CategoryManager()
    
    def create_prompt(self, 
                     name: str,
                     content: str,
                     model_type: str = "universal",
                     auto_categorize: bool = True) -> PromptData:
        """Create a new prompt with automatic categorization"""
        
        prompt = PromptData(
            id=str(uuid.uuid4()),
            name=name,
            content=content,
            model_type=model_type
        )
        
        if auto_categorize:
            category, subcategory = self.category_manager.suggest_category(content)
            prompt.category = category
            prompt.subcategory = subcategory
            prompt.tags = self._extract_tags(content)
        
        self.db.save_prompt(prompt)
        return prompt
    
    def _extract_tags(self, content: str) -> List[str]:
        """Extract relevant tags from prompt content"""
        # Simple tag extraction - can be enhanced with NLP
        common_tags = [
            "portrait", "landscape", "artistic", "realistic", "colorful",
            "dramatic", "soft", "detailed", "professional", "creative",
            "modern", "vintage", "minimalist", "vibrant", "dark", "bright"
        ]
        
        content_lower = content.lower()
        extracted_tags = []
        
        for tag in common_tags:
            if tag in content_lower:
                extracted_tags.append(tag)
        
        return extracted_tags[:5]  # Limit to 5 tags
    
    def migrate_existing_prompts(self, existing_prompts: List[str], model_type: str):
        """Migrate existing simple prompt lists to enhanced system"""
        for prompt_text in existing_prompts:
            if prompt_text.strip():
                self.create_prompt(
                    name=prompt_text[:50] + "..." if len(prompt_text) > 50 else prompt_text,
                    content=prompt_text,
                    model_type=model_type
                )
    
    def get_prompts_for_model(self, model_type: str) -> List[PromptData]:
        """Get all prompts compatible with a specific model"""
        return self.db.search_prompts(model_type=model_type)
    
    def search(self, query: str, **kwargs) -> List[PromptData]:
        """Search prompts with various filters"""
        return self.db.search_prompts(query=query, **kwargs)

# Usage Example
if __name__ == "__main__":
    # Example usage
    manager = EnhancedPromptManager()
    
    # Create a new prompt
    prompt = manager.create_prompt(
        name="Watercolor Portrait",
        content="beautiful watercolor portrait of a young woman with flowing hair",
        model_type="nano_banana"
    )
    
    print(f"Created prompt: {prompt.name}")
    print(f"Auto-categorized as: {prompt.category} > {prompt.subcategory}")
    print(f"Auto-tagged with: {prompt.tags}")
    
    # Search prompts
    results = manager.search("watercolor")
    print(f"Found {len(results)} watercolor prompts")