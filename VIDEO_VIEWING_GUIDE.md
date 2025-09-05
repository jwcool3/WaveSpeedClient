# 🎬 Video Viewing Guide

## Overview

WaveSpeed AI now supports embedded video playback directly in the GUI! You can view generated videos without leaving the application and easily browse your saved video results.

## Features

### ✅ Embedded Video Player
- **In-app playback**: Watch videos directly in the GUI
- **Full controls**: Play, pause, stop, and scrub through videos
- **Auto-scaling**: Videos automatically fit the display area
- **High quality**: Support for multiple video formats

### 📁 Local File Management
- **Browse videos**: Select any video file from your computer
- **Recent videos**: Quick access to recently generated videos
- **Results folder**: Direct access to your saved video results
- **Auto-save integration**: Seamlessly view auto-saved videos

### 🎮 Enhanced Controls
- **Playback controls**: Standard play/pause/stop buttons
- **File browser**: Browse and select local video files
- **Recent videos**: Quick access to your latest creations
- **Results folder**: Open the results directory in file explorer
- **Download**: Save videos from URLs to your local storage

## How to Use

### 1. Setup (One-time)
If you haven't already, install the video player library:
```bash
python scripts/install_video_player.py
```

### 2. Viewing Generated Videos
When you generate a video using Image-to-Video or SeedDance:
1. The video will automatically appear in the video player area
2. Use the play controls to watch your video
3. Videos are automatically saved to the `WaveSpeed_Results` folder

### 3. Browsing Local Videos
- Click **"📁 Browse Local Videos"** to select any video file
- The browser will start in your `WaveSpeed_Results` folder
- Supports: MP4, AVI, MOV, MKV, WMV, FLV, WebM formats

### 4. Quick Access to Recent Videos
- Click **"🕒 Recent Videos"** for a list of your latest videos
- Double-click any video to load it instantly
- Shows creation time for easy identification

### 5. Managing Video Files
- Click **"📂 Results Folder"** to open the results directory
- Organize your videos in the file explorer
- Videos are automatically organized by AI model type

## Video Formats Supported

| Format | Extension | Notes |
|--------|-----------|--------|
| MP4 | `.mp4` | Recommended format |
| AVI | `.avi` | High compatibility |
| MOV | `.mov` | Apple QuickTime |
| MKV | `.mkv` | Open source format |
| WMV | `.wmv` | Windows Media |
| FLV | `.flv` | Flash Video |
| WebM | `.webm` | Web optimized |

## Troubleshooting

### Video Player Not Available
If you see "Video player not available":
1. Run: `python scripts/install_video_player.py`
2. Restart the WaveSpeed AI application
3. The video player should now be available

### AttributeError: 'fast_seek' Not Found
If you encounter an error about `fast_seek` attribute:
1. This is a compatibility issue with newer versions of the `av` library
2. Run: `pip install av==10.0.0` to downgrade to a compatible version
3. Restart the application
4. The error should be resolved

### Video Won't Load
- Check that the video file exists and isn't corrupted
- Ensure the video format is supported
- Try using a different video file to test

### Performance Issues
- Close other applications to free up system resources
- Use MP4 format for best performance
- Ensure your video files aren't excessively large

### Controls Not Working
- Make sure the video has fully loaded before using controls
- Try stopping and restarting the video
- Check that the video file is accessible

## Technical Details

### Dependencies
- **tkVideoPlayer**: Provides the embedded video playback functionality
- **av**: Audio/video processing library (automatically installed)
- **PIL/Pillow**: Image processing (already included)

### File Organization
Videos are automatically saved to:
```
WaveSpeed_Results/
├── Image_to_Video/     # Image-to-video results
├── SeedDance/          # SeedDance results
└── Other/              # Other video types
```

### Metadata
Each video is accompanied by a JSON metadata file containing:
- Generation parameters
- Creation timestamp
- Prompt information
- File details

## Tips for Best Experience

1. **Use MP4 format** for best compatibility and performance
2. **Keep videos under 100MB** for smooth playback
3. **Use the Recent Videos feature** for quick access to your latest creations
4. **Organize your results folder** to keep videos easy to find
5. **Close the video player** when not in use to save system resources

## Support

If you encounter issues with video playback:
1. Check the console output for error messages
2. Verify your video files are not corrupted
3. Ensure you have sufficient system resources
4. Try reinstalling the video player: `python scripts/install_video_player.py`

Enjoy creating and viewing your AI-generated videos! 🎬✨
