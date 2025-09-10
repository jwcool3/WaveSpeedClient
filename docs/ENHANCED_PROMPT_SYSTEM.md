# 📚 Enhanced Prompt Management System

## Overview

The Enhanced Prompt Management System is a comprehensive upgrade to WaveSpeed AI's prompt management capabilities. It replaces the simple JSON-based prompt lists with a modern, database-driven system featuring categories, tags, search, and cross-tab functionality.

## 🚀 Key Features

### ✨ Modern Database System
- **SQLite Database**: Efficient storage and retrieval of hundreds of prompts
- **Structured Data**: Rich metadata including categories, tags, ratings, and usage statistics
- **Performance**: Fast search and filtering even with large prompt libraries

### 🏷️ Smart Categorization
- **Hierarchical Categories**: Main categories with subcategories
- **Auto-Categorization**: AI-powered category suggestions based on prompt content
- **Custom Tags**: Flexible tagging system for detailed organization

### 🔍 Advanced Search & Discovery
- **Full-Text Search**: Search across prompt names, content, and descriptions
- **Filter by Category**: Browse prompts by artistic style, use case, or model type
- **Rating System**: Find high-quality prompts based on user ratings
- **Usage Analytics**: Discover popular and recently used prompts

### 🔄 Cross-Tab Integration
- **Universal Prompts**: Use prompts across different AI models
- **Model-Specific Prompts**: Prompts optimized for specific models
- **Seamless Integration**: Works with existing tab interfaces

### 📊 Analytics & Insights
- **Usage Tracking**: Monitor which prompts are used most frequently
- **Success Ratings**: Rate prompts based on results quality
- **Recent Activity**: Quick access to recently used prompts

## 📁 System Architecture

```
core/
├── prompt_manager_core.py      # Core database and management logic
├── prompt_migration.py         # Migration helper for existing prompts
└── enhanced_prompt_browser.py  # Modern UI browser component

ui/components/
├── enhanced_prompt_browser.py  # Main browser interface
└── prompt_integration.py       # Integration helpers for tabs

scripts/
└── migrate_prompts.py          # Migration script
```

## 🛠️ Installation & Setup

### Step 1: Run Migration Script

```bash
# From the WaveSpeed AI project root
python scripts/migrate_prompts.py
```

This script will:
- Create backups of existing prompt files
- Migrate all prompts to the new database system
- Create sample prompts if none exist
- Generate a migration report

### Step 2: Integration with Tabs

The enhanced prompt system can be integrated with existing tabs in two ways:

#### Option A: Quick Integration (Recommended)
Add the enhanced prompt browser button to existing prompt sections:

```python
from ui.components.enhanced_prompt_browser import show_enhanced_prompt_browser

# In your tab's prompt actions section
ttk.Button(prompt_actions, text="📚 Enhanced Library", 
          command=self.show_enhanced_prompt_browser).pack(side=tk.LEFT, padx=(0, 5))

def show_enhanced_prompt_browser(self):
    show_enhanced_prompt_browser(
        parent=self.root,
        model_type="your_model_type",  # e.g., "nano_banana", "seededit"
        on_select=self.apply_enhanced_prompt
    )

def apply_enhanced_prompt(self, prompt_content: str):
    self.prompt_text.delete("1.0", tk.END)
    self.prompt_text.insert("1.0", prompt_content)
```

#### Option B: Complete Replacement
Replace existing prompt management with the enhanced system:

```python
from ui.components.prompt_integration import create_prompt_management_section

# Replace existing prompt section
prompt_frame = create_prompt_management_section(
    parent_frame=your_parent_frame,
    prompt_text_widget=self.prompt_text,
    model_type="your_model_type",
    on_save=self.save_current_prompt,
    on_load=self.load_saved_prompts
)
```

## 📊 Database Schema

### Prompts Table
```sql
CREATE TABLE prompts (
    id TEXT PRIMARY KEY,           -- Unique identifier
    name TEXT NOT NULL,            -- Display name
    content TEXT NOT NULL,         -- Prompt text
    category TEXT DEFAULT 'General', -- Main category
    subcategory TEXT DEFAULT '',   -- Subcategory
    tags TEXT DEFAULT '[]',        -- JSON array of tags
    model_type TEXT DEFAULT 'universal', -- Compatible models
    created_date TEXT,             -- Creation timestamp
    last_used TEXT,                -- Last usage timestamp
    usage_count INTEGER DEFAULT 0, -- Usage frequency
    rating REAL DEFAULT 0.0,       -- User rating (0-5)
    description TEXT DEFAULT '',   -- Optional description
    preview_image TEXT DEFAULT '', -- Optional preview image
    settings TEXT DEFAULT '{}',    -- JSON settings
    ai_enhanced BOOLEAN DEFAULT FALSE, -- AI-enhanced flag
    original_prompt TEXT DEFAULT '' -- Original prompt if enhanced
);
```

## 🎨 Default Categories

The system comes with pre-defined categories:

- **🎨 Artistic Styles**: Watercolor, Oil Painting, Digital Art, Sketch, Pop Art
- **👤 Portrait & People**: Faces, Expressions, Poses, Groups, Emotions
- **🌍 Environments**: Landscapes, Interiors, Cities, Nature, Architecture
- **🎬 Cinematic**: Movie Styles, Lighting, Moods, Drama, Action
- **🔧 Technical**: Upscaling, Enhancement, Correction, Restoration
- **🎪 Creative**: Fantasy, Sci-Fi, Abstract, Surreal, Conceptual
- **📱 Social Media**: Instagram, TikTok, Profile Pics, Stories, Posts
- **💼 Professional**: Business, Corporate, Marketing, Logos, Presentations

## 🔧 API Reference

### EnhancedPromptManager

```python
from core.prompt_manager_core import EnhancedPromptManager

manager = EnhancedPromptManager()

# Create a new prompt
prompt = manager.create_prompt(
    name="My Prompt",
    content="beautiful landscape painting",
    model_type="nano_banana",
    auto_categorize=True
)

# Search prompts
results = manager.search(
    query="landscape",
    category="🌍 Environments",
    model_type="nano_banana",
    min_rating=3.0
)

# Get popular prompts
popular = manager.db.get_popular_prompts(model_type="nano_banana", limit=10)

# Record usage
manager.db.record_usage(prompt.id, "nano_banana", success_rating=4.5)
```

### Enhanced Prompt Browser

```python
from ui.components.enhanced_prompt_browser import show_enhanced_prompt_browser

def on_prompt_selected(prompt_content):
    print(f"Selected: {prompt_content}")

show_enhanced_prompt_browser(
    parent=root_window,
    model_type="nano_banana",
    on_select=on_prompt_selected
)
```

## 🚀 Advanced Features

### Custom Categories
Add your own categories to the system:

```python
from core.prompt_manager_core import CategoryManager

# Categories are defined in CategoryManager.DEFAULT_CATEGORIES
# You can extend this or create custom categorization logic
```

### AI-Enhanced Prompts
Track prompts that have been improved by AI:

```python
prompt = PromptData(
    name="Enhanced Portrait",
    content="improved prompt text",
    ai_enhanced=True,
    original_prompt="original prompt text"
)
```

### Usage Analytics
Monitor prompt performance:

```python
# Get usage statistics
recent_prompts = manager.db.get_recent_prompts(model_type="nano_banana", limit=20)
popular_prompts = manager.db.get_popular_prompts(model_type="nano_banana", limit=10)
```

## 🔄 Migration from Old System

### Automatic Migration
The migration script handles most scenarios automatically:

1. **JSON Lists**: `["prompt1", "prompt2", ...]`
2. **JSON Objects**: `{"name1": "prompt1", "name2": "prompt2"}`
3. **Mixed Formats**: Handles various existing formats

### Manual Migration
For custom formats, use the migration helper:

```python
from core.prompt_migration import PromptMigrationHelper

helper = PromptMigrationHelper()

# Migrate custom data
for custom_prompt in your_custom_data:
    helper.migrate_single_prompt(
        prompt_text=custom_prompt["text"],
        model_type="your_model",
        model_name="Your Model Name",
        custom_name=custom_prompt.get("name")
    )
```

## 🐛 Troubleshooting

### Common Issues

1. **Database Locked**: Ensure no other instances of the app are running
2. **Migration Fails**: Check file permissions and disk space
3. **UI Not Loading**: Verify all dependencies are installed

### Debug Mode
Enable debug logging:

```python
from core.logger import get_logger
logger = get_logger()
logger.setLevel(logging.DEBUG)
```

### Reset Database
If you need to start fresh:

```bash
# Remove the database file
rm data/prompts.db

# Run migration again
python scripts/migrate_prompts.py
```

## 🔮 Future Enhancements

### Planned Features
- **Cloud Sync**: Backup and sync prompts across devices
- **AI Categorization**: Machine learning-based category suggestions
- **Prompt Templates**: Reusable prompt templates with variables
- **Collaborative Features**: Share prompts with other users
- **Advanced Analytics**: Detailed usage reports and insights

### Extensibility
The system is designed to be easily extensible:

- Add new model types
- Create custom categorization logic
- Implement additional search filters
- Add new metadata fields

## 📝 Contributing

To contribute to the enhanced prompt system:

1. Follow the existing code structure
2. Add appropriate error handling
3. Include logging for debugging
4. Update documentation
5. Test with various prompt formats

## 📄 License

This enhanced prompt management system is part of the WaveSpeed AI Creative Suite and follows the same licensing terms.
