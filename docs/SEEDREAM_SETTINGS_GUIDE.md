# Seedream V4 Settings Guide

## 📁 Settings File Location

All Seedream V4 settings are saved in:
```
data/seedream_settings.json
```

## 🎛️ What Gets Saved

### Generation Settings (saved immediately)
- `width` - Output image width (256-4096)
- `height` - Output image height (256-4096)
- `seed` - Random seed for reproducibility (-1 for random)
- `sync_mode` - Enable sync mode (true/false)
- `base64_output` - Use base64 output (true/false)
- `aspect_locked` - Lock aspect ratio (true/false)
- `locked_aspect_ratio` - Current locked ratio value

### UI Preferences (saved manually via Tools menu)
- `splitter_position` - Main left panel width in pixels
- `side_panel_position` - Side panel position (when AI prompts are open)
- `zoom_level` - Zoom setting ("Fit", "100%", "150%", etc.)
- `comparison_mode` - View mode ("side_by_side", "overlay", "original_only", "result_only")
- `overlay_opacity` - Blend opacity for overlay mode (0.0-1.0)
- `sync_zoom` - Sync zoom between panels (true/false)
- `sync_drag` - Sync panning between panels (true/false)
- `window_state` - Window state ("normal", "zoomed", "iconic")
- `window_width` - Window width in pixels
- `window_height` - Window height in pixels
- `window_x` - Window X position
- `window_y` - Window Y position

## 📝 Example Settings File

```json
{
  "width": 2550,
  "height": 3279,
  "seed": -1,
  "sync_mode": false,
  "base64_output": true,
  "aspect_locked": true,
  "locked_aspect_ratio": 0.777777,
  "ui_preferences": {
    "splitter_position": 320,
    "side_panel_position": 1440,
    "zoom_level": "Fit",
    "comparison_mode": "side_by_side",
    "overlay_opacity": 0.5,
    "sync_zoom": true,
    "sync_drag": true,
    "window_state": "zoomed",
    "window_width": 1920,
    "window_height": 1080,
    "window_x": 0,
    "window_y": 0
  }
}
```

## 🔄 How Saving Works

### Generation Settings
- Saved **500ms** after you stop changing them (debounced, automatic)
- Applied to UI when app starts

### UI Preferences
- **Manual save only** - Use **Tools → 💾 Save Seedream Layout**
- Tracks splitter positions, zoom, comparison mode, sync settings, and window state
- Applied to UI when app starts
- Includes window size, position, and maximized state

## 🛠️ Manual Editing

You can manually edit `data/seedream_settings.json` when the app is closed.

### Validation Rules:
- **Width/Height**: Must be integers between 256-4096
- **Seed**: Must be integer between -1 and 2147483647 (or -1 for random)
- **Booleans**: Must be `true` or `false` (lowercase)
- **Zoom**: Must be "Fit", "50%", "75%", "100%", "125%", "150%", "200%", "300%", or "400%"
- **Comparison Mode**: Must be "side_by_side", "overlay", "original_only", or "result_only"
- **Window State**: Must be "normal", "zoomed", "iconic", or "withdrawn"
- **Splitter Positions**: Must be positive integers (in pixels)

## ⚠️ Troubleshooting

### "Invalid saved settings, using defaults"

This warning means the settings file failed validation. Check the console for specific error:

```
Settings validation failed: width/height out of range (5000, 6000)
Settings validation failed: invalid seed type (abc)
Settings validation failed: not a dictionary
```

### Reset to Defaults

Simply delete `data/seedream_settings.json` and restart the app.

### Legacy Compatibility

The old splitter position file (`data/seedream_splitter_position.txt`) is still supported as a fallback if the unified settings file doesn't contain a splitter position.

## 🎨 Customizing Your Layout

1. **Adjust the UI** to your liking:
   - Drag the splitter to your preferred position
   - Set your preferred zoom level
   - Choose your comparison mode
   - Enable/disable sync zoom and sync drag

2. **Wait 1 second** - settings auto-save

3. **Restart the app** - your layout is restored!

## 💡 Tips

- **UI layout persists** across sessions when you save it
- **Manual save required** - Use Tools → 💾 Save Seedream Layout
- **Window state saves** - If you save while maximized, it opens maximized next time!
- **Multiple splitters tracked** - Main splitter + side panel splitter (when visible)
- **Console logging** - Every splitter drag shows detailed layout info in console
- **Generation settings auto-save** - Width, height, seed, etc. save automatically (not UI layout)

---

**Note**: This is the **unified settings system** introduced in the refactored Seedream V4. All UI preferences are now in one place for easier backup and management!

