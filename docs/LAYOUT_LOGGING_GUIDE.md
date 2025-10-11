# Layout Logging & Manual Save Guide

## 🎯 Overview

Auto-save has been **disabled** for Seedream V4 layout. Instead, you now have:
1. ✅ **Detailed console logging** when you drag splitters
2. ✅ **Manual save option** in the Tools menu

## 📊 How to Find Your Preferred Layout

### Step 1: Open Seedream V4
Switch to the Seedream V4 tab in the application.

### Step 2: Drag the Splitter
Drag the vertical splitter (divider between left panel and image display) to your preferred position.

### Step 3: Check the Console
Every time you release any splitter, you'll see detailed logging like this:

```
================================================================================
📐 LAYOUT CHANGED
================================================================================
🖥️  WINDOW STATE:
   State: zoomed
   Size: 1920x1080px
--------------------------------------------------------------------------------
📏 MAIN SPLITTER (Left Panel | Right Panel):
   Left Panel Width: 320px
   Total Width: 1920px
   Percentage: 16.7%
   Right Panel Width: 1600px
--------------------------------------------------------------------------------
📏 SIDE PANEL SPLITTER (Main | Side Panel):
   Main Content Width: 1440px
   Total Width: 1920px
   Percentage: 75.0%
   Side Panel Width: 480px
================================================================================
💡 To set this as default, add to your settings:
   'splitter_position': 320
   'side_panel_position': 1440
================================================================================
```

**Note**: The Side Panel Splitter only appears when you have AI-generated prompts open (Mild/Moderate/Undress examples).

### Step 4: Try Different Positions
Keep dragging until you find the perfect layout. The console will show you the exact values each time.

### Step 5: Save Your Layout
Once you're happy with the layout:
1. Go to **Tools** menu → **💾 Save Seedream Layout**
2. A popup will show your saved settings
3. The layout is now saved and will be restored on next startup!

## 📝 Understanding the Values

### Window State
- **normal**: Regular windowed mode
- **zoomed**: Maximized/fullscreen mode
- **Size**: Your current window dimensions

### Main Splitter (Left Panel Width)
- **Too narrow** (< 280px): Controls might be cramped
- **Recommended**: 300-350px for most screens
- **Too wide** (> 400px): Less space for image display
- **Percentage**: What % of screen width the left panel takes
  - **Typical range**: 15-25%
  - Lower % = more space for images

### Side Panel Splitter (if visible)
- Only appears when AI-generated prompts are open
- Controls how much space the prompt examples take
- **Recommended**: 30-40% of total width for side panel

### Right Panel Width
- Remaining space for image display
- **More is better** for viewing your results!

## 🎨 Example Layouts

### Compact Layout (More Image Space)
```
Left Panel Width: 300px
Percentage: 15.6%
Right Panel Width: 1620px
```

### Balanced Layout
```
Left Panel Width: 350px
Percentage: 18.2%
Right Panel Width: 1570px
```

### Wide Controls Layout
```
Left Panel Width: 400px
Percentage: 20.8%
Right Panel Width: 1520px
```

## 💾 Saved Settings Location

All settings are saved to:
```
data/seedream_settings.json
```

The file will look like this:
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

## 🔧 Manual Editing (Advanced)

You can manually edit `data/seedream_settings.json` when the app is closed:

1. Close the application
2. Open `data/seedream_settings.json` in a text editor
3. Find `"ui_preferences"` section
4. Change `"splitter_position"` to your preferred value
5. Save and restart the app

## 🎯 Tips

1. **Try fullscreen first** - Your preferred layout might differ in fullscreen vs windowed mode
   - If you save while maximized, the app will open maximized next time!
2. **Check on different screens** - If you use multiple monitors, test on each
3. **Save multiple times** - You can adjust and re-save as often as you like
4. **Console is your friend** - Watch the console logs to fine-tune exact pixel values
5. **Multiple splitters** - The console tracks ALL splitters (main + side panel)
6. **Window state matters** - The save includes window size, position, and maximized state

## ⚠️ Troubleshooting

### "Not Available" Error
- Make sure you're on the Seedream V4 tab when saving
- If the tab hasn't been opened yet, open it first

### Layout Not Restoring
- Check that `data/seedream_settings.json` exists
- Verify the JSON is valid (no syntax errors)
- Check console for "Invalid saved settings" warnings

### Splitter Resets on Restart
- Make sure you **saved** after dragging (Tools → Save Seedream Layout)
- Check that the file wasn't reverted or deleted

---

**Remember**: Layout is now **manual save only**. Drag the splitter, check the console for values, and save when you're happy! 🎉

