"""
Seedream Components Package
Modular components for the Seedream V4 tab refactoring

This package contains the refactored modules from the original
improved_seedream_layout.py file (5,645 lines) split into 
maintainable, testable components.

Progress:
- ✅ Phase 1: Image Section (image_section.py) - 827 lines
- ✅ Phase 2: Settings Panel (settings_panel.py) - 715 lines
- 🔄 Phase 3: Prompt Section (prompt_section.py) - TODO
- 🔄 Phase 4: Filter Training (filter_training.py) - TODO  
- 🔄 Phase 5: Actions Handler (actions_handler.py) - TODO
- 🔄 Phase 6: Results Display (results_display.py) - TODO
- 🔄 Phase 7: Layout Base Coordinator (layout_base.py) - TODO
"""

# Phase 1: Image Section Module (COMPLETE)
try:
    from .image_section import (
        SynchronizedImagePanels,
        EnhancedSyncManager,
        ImageSectionManager
    )
    _IMAGE_SECTION_AVAILABLE = True
except ImportError as e:
    _IMAGE_SECTION_AVAILABLE = False
    print(f"Warning: Image section module not available: {e}")

# Phase 2: Settings Panel Module (COMPLETE)
try:
    from .settings_panel import (
        SettingsPanelManager
    )
    _SETTINGS_PANEL_AVAILABLE = True
except ImportError as e:
    _SETTINGS_PANEL_AVAILABLE = False
    print(f"Warning: Settings panel module not available: {e}")

# Phase 3: Prompt Section Module (TODO)
try:
    from .prompt_section import (
        PromptSectionManager
    )
    _PROMPT_SECTION_AVAILABLE = True
except ImportError:
    _PROMPT_SECTION_AVAILABLE = False

# Phase 4: Filter Training Module (TODO)
try:
    from .filter_training import (
        FilterTrainingManager
    )
    _FILTER_TRAINING_AVAILABLE = True
except ImportError:
    _FILTER_TRAINING_AVAILABLE = False

# Phase 5: Actions Handler Module (TODO)
try:
    from .actions_handler import (
        ActionsHandlerManager
    )
    _ACTIONS_HANDLER_AVAILABLE = True
except ImportError:
    _ACTIONS_HANDLER_AVAILABLE = False

# Phase 6: Results Display Module (TODO)
try:
    from .results_display import (
        ResultsDisplayManager
    )
    _RESULTS_DISPLAY_AVAILABLE = True
except ImportError:
    _RESULTS_DISPLAY_AVAILABLE = False

# Phase 7: Layout Base Coordinator (TODO)
try:
    from .layout_base import (
        SeedreamLayoutV2
    )
    _LAYOUT_BASE_AVAILABLE = True
except ImportError:
    _LAYOUT_BASE_AVAILABLE = False

# Export completed modules
__all__ = []

if _IMAGE_SECTION_AVAILABLE:
    __all__.extend([
        'SynchronizedImagePanels',
        'EnhancedSyncManager', 
        'ImageSectionManager'
    ])

if _SETTINGS_PANEL_AVAILABLE:
    __all__.extend([
        'SettingsPanelManager'
    ])

if _PROMPT_SECTION_AVAILABLE:
    __all__.extend([
        'PromptSectionManager'
    ])

if _FILTER_TRAINING_AVAILABLE:
    __all__.extend([
        'FilterTrainingManager'
    ])

if _ACTIONS_HANDLER_AVAILABLE:
    __all__.extend([
        'ActionsHandlerManager'
    ])

if _RESULTS_DISPLAY_AVAILABLE:
    __all__.extend([
        'ResultsDisplayManager'
    ])

if _LAYOUT_BASE_AVAILABLE:
    __all__.extend([
        'SeedreamLayoutV2'
    ])

# Module status information
MODULE_STATUS = {
    'image_section': _IMAGE_SECTION_AVAILABLE,
    'settings_panel': _SETTINGS_PANEL_AVAILABLE,
    'prompt_section': _PROMPT_SECTION_AVAILABLE,
    'filter_training': _FILTER_TRAINING_AVAILABLE,
    'actions_handler': _ACTIONS_HANDLER_AVAILABLE,
    'results_display': _RESULTS_DISPLAY_AVAILABLE,
    'layout_base': _LAYOUT_BASE_AVAILABLE
}

def get_module_status():
    """Get status of all modules in the package"""
    return MODULE_STATUS.copy()

def get_completed_modules():
    """Get list of completed module names"""
    return [name for name, available in MODULE_STATUS.items() if available]

def get_pending_modules():
    """Get list of pending module names"""
    return [name for name, available in MODULE_STATUS.items() if not available]

def get_refactoring_progress():
    """Get refactoring progress information"""
    completed = len(get_completed_modules())
    total = len(MODULE_STATUS)
    
    return {
        'completed_modules': completed,
        'total_modules': total,
        'progress_percentage': (completed / total) * 100,
        'completed_names': get_completed_modules(),
        'pending_names': get_pending_modules()
    }

# Version info
__version__ = "0.2.0"  # Phase 2 complete
__author__ = "Seedream Refactoring Team"
__description__ = "Modular components for Seedream V4 tab"

# Usage example for completed modules
"""
Example usage of completed modules:

# Phase 1: Image Section
from ui.components.seedream import ImageSectionManager

image_manager = ImageSectionManager(layout)
image_manager.setup_image_section(parent_frame)

# Phase 2: Settings Panel  
from ui.components.seedream import SettingsPanelManager

settings_manager = SettingsPanelManager(layout)
settings_manager.setup_settings_panel(parent_frame)
current_settings = settings_manager.get_current_settings()
is_valid, error = settings_manager.validate_settings()

# Check module availability
from ui.components.seedream import get_refactoring_progress
progress = get_refactoring_progress()
print(f"Refactoring progress: {progress['progress_percentage']:.1f}%")
"""