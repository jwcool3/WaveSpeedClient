"""
Seedream V4 Layout Components - Modular Architecture

This package contains the refactored Seedream V4 layout split into manageable modules.
Each module handles a specific aspect of the UI functionality.

Modules:
- image_section: Image loading, display, caching, zoom/pan, canvas interactions
- settings_panel: Settings controls and configuration (TODO)
- prompt_section: Prompt editor and AI integration (TODO)
- filter_training: Filter training features (TODO)
- actions_handler: Action buttons and processing (TODO)
- results_display: Results display and history (TODO)
- layout_base: Main coordinator bringing everything together (TODO)
"""

__version__ = "2.0.0"
__author__ = "WaveSpeed Team"

# Import image section components
from .image_section import (
    SynchronizedImagePanels,
    EnhancedSyncManager,
    ImageSectionManager
)

__all__ = [
    # Image Section
    'SynchronizedImagePanels',
    'EnhancedSyncManager',
    'ImageSectionManager',
]

