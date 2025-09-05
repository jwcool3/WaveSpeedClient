# WaveSpeed AI Complete Creative Suite

A comprehensive GUI application for AI-powered image editing, upscaling, and video generation using the WaveSpeed AI APIs. Features a modern, responsive interface with professional workflow capabilities.

## 🆕 Latest Features (2024)

### 💰 **Real-Time Balance Indicator**
- **Live Balance Display**: Shows your current WaveSpeed AI account balance in the top-right corner
- **Auto-Refresh**: Updates every 5 minutes with manual refresh option
- **Visual Status**: Color-coded balance indicator (green for healthy, red for low balance)
- **Smart Icons**: Dynamic icons based on balance level (💰 full, 🪙 low, ⚠️ very low)

### 📂 **Recent Results Panel**
- **Visual Gallery**: Thumbnail grid of your last 50 generated results
- **Smart Filtering**: Filter results by AI model (Nano Banana, SeedEdit, Upscaler, Wan 2.2, SeedDance)
- **One-Click Reuse**: Click any result to send it to any compatible tab instantly
- **Cross-Tab Workflow**: Seamlessly chain different AI models together
- **File Management**: Right-click for "Show in Folder" and "Delete" options
- **Metadata Tooltips**: Hover for generation details and prompts

### 📤 **Cross-Tab Result Sharing**
- **Send To Dropdown**: Every result includes a "📤 Send To..." button
- **Auto-Navigation**: Automatically switches tabs and loads images
- **Smart Routing**: Only shows compatible destination tabs
- **Professional Workflow**: Chain Nano Banana → Upscaler → SeedEdit → Wan 2.2
- **Success Feedback**: Clear confirmation when transfers complete

### 🎛️ **Resizable UI Sections**
- **Draggable Splitter**: Resize the recent results panel and main content area
- **Keyboard Shortcuts**: 
  - `Ctrl + [` - Collapse sidebar
  - `Ctrl + ]` - Expand sidebar  
  - `Ctrl + =` - Reset to default
- **Position Memory**: Remembers your preferred layout between sessions
- **Smart Constraints**: Prevents panels from becoming too small to use

### 🎨 **Optimized Layouts**
- **30/70 Split Design**: Efficient space utilization across all tabs
- **Tabbed Image Display**: "Input Image" and "Edited Result" tabs for better organization
- **Responsive Design**: Adapts to any window size, both horizontal and vertical
- **Professional UI**: Clean, modern interface inspired by professional creative software

### 🎬 **Enhanced Video Player**
- **YouTube-Like Experience**: Large, interactive video player with auto-hide controls
- **Interactive Progress Bar**: Click to seek, real-time position display
- **Volume Control**: Adjustable volume slider
- **Fullscreen Mode**: Immersive video viewing experience
- **Mouse & Keyboard**: Click to play/pause, spacebar controls, escape to exit fullscreen
- **File Management**: Browse local videos, recent videos menu, open results folder

## Core Features

### 🤖 **Auto-Save System**
- **Automatic Saving**: All AI results are automatically saved to organized folders
- **Smart Naming**: Files named with timestamps, AI model, prompt info, and settings
- **Organized Structure**: Separate folders for each AI model type
- **Metadata Tracking**: JSON files store generation details alongside results
- **Easy Access**: "Open Results Folder" menu option for quick file access
- **Cross-Platform**: Works on Windows, macOS, and Linux

### 🔒 **Privacy & Security**
- **Privacy Modes**: Choose from High, Medium, or Demo privacy levels
- **High Privacy**: Base64 data URLs (no external hosting, most secure)
- **Medium Privacy**: Temporary hosting with 1-hour auto-delete
- **Demo Mode**: Uses sample images (your images never uploaded)
- **Privacy Settings**: Easy-to-use privacy configuration dialog
- **Secure Upload**: Automatic privacy-aware image handling

### 📱 **Responsive Design**
- **Adaptive Layout**: GUI automatically adapts to different window sizes
- **Scrollable Content**: All tabs have scrollable content areas
- **Sticky Buttons**: Critical action buttons always remain visible at bottom
- **Minimum Window Size**: Prevents interface from becoming unusable
- **Mouse Wheel Support**: Scroll through content with mouse wheel
- **Resizable Sections**: All UI elements properly resize with window

## AI Models & Tabs

### 🍌 **Nano Banana Editor** (formerly Image Editor)
- **Google's Nano Banana**: State-of-the-art image editing AI
- **Drag & Drop Support**: Simply drag images from your file explorer into the app
- **Optimized Layout**: 30/70 split with tabbed image display
- **Cross-Tab Sharing**: Send results to any other tab with one click
- **Prompt Management**: Save, reuse, and manage your editing prompts
- **Chain Editing**: Use result images as input for the next edit
- **Format Selection**: Choose output format (PNG, JPG, WebP)
- **Auto-Save**: Results automatically saved with prompt and timestamp info

### ✨ **SeedEdit**
- **ByteDance SeedEdit-v3**: Precise image modifications with fine control
- **Optimized Layout**: Professional 30/70 split interface
- **Guidance Control**: Adjustable guidance scale (0.0-1.0) for editing strength
- **Seed Control**: Reproducible results with custom seeds
- **Cross-Tab Integration**: Send results to other tabs for complex workflows
- **Sample Prompts**: Built-in examples for common editing tasks
- **Auto-Save**: Results automatically saved with prompt and settings info

### 🔍 **Image Upscaler**
- **WaveSpeed AI Upscaler**: Enhance image resolution using advanced AI
- **Optimized Layout**: Streamlined interface for upscaling workflow
- **Multiple Resolutions**: Choose from 2K, 4K, or 8K target resolutions
- **Creativity Control**: Adjust creativity level (-2 to +2) for enhancement
- **Format Options**: Output in PNG, JPEG, or WebP formats
- **Cross-Tab Integration**: Send upscaled images directly to other tabs
- **Auto-Save**: Results automatically saved with resolution and creativity settings

### 🎬 **Wan 2.2** (formerly Image to Video)
- **WaveSpeed WAN-2.2**: Convert static images into dynamic videos
- **Enhanced Video Player**: Large, YouTube-like player with full controls
- **Optimized Layout**: 30/70 split with large video display area
- **Customizable Duration**: Generate 5 or 8-second videos
- **Prompt Control**: Detailed prompts for video content and movement
- **Negative Prompts**: Specify what to avoid in video generation
- **Seed Control**: Reproducible results with custom seeds
- **Auto-Save**: Videos automatically saved with duration and seed info

### 🕺 **SeedDance**
- **ByteDance SeedDance-v1-Pro**: Professional-grade video generation
- **Enhanced Video Player**: Full-featured playback with interactive controls
- **Optimized Layout**: Efficient space usage with large video display
- **Extended Duration**: Generate videos from 5 to 10 seconds
- **Camera Control**: Fixed or dynamic camera positioning
- **Optional Prompts**: Text prompts for enhanced video generation
- **High Quality**: Professional-grade video output
- **Auto-Save**: Videos automatically saved with duration, camera, and seed settings

## Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Install Video Player (Recommended)**:
   ```bash
   # For enhanced video playback experience
   python scripts/install_video_player.py
   
   # Or manually install
   pip install av==10.0.0
   pip install tkvideoplayer==2.3
   ```

3. **Set up API Key**:
   - Copy `docs/env_example.txt` to `.env` in the root directory
   - Add your WaveSpeed API key to the `.env` file:
     ```
     WAVESPEED_API_KEY=your_actual_api_key_here
     ```

4. **Run the Application**:
   ```bash
   # Main application
   python main.py
   ```

## Usage

### Professional Workflow Examples

#### **🔄 Cross-Tab Creative Pipeline**
1. **Nano Banana Editor**: Apply creative edits to your image
2. **📤 Send To Upscaler**: Click "Send To..." → "🔍 Image Upscaler"  
3. **Upscale**: Enhance to 4K resolution
4. **📤 Send To SeedEdit**: Fine-tune specific details
5. **📤 Send To Wan 2.2**: Create stunning video from final image

#### **🎨 Advanced Editing Workflow**
1. **Recent Results Panel**: Browse your previous generations
2. **One-Click Reuse**: Click any result to load in current tab
3. **Iterative Editing**: Apply multiple AI models in sequence
4. **Quality Enhancement**: Upscale → Edit → Upscale for maximum quality

### Basic Usage

#### **Nano Banana Editor Tab**
1. **Select Image**: Drag & drop or click "Browse Image"
2. **Enter Prompt**: Describe your desired edits
3. **Choose Settings**: Select output format and other options
4. **Generate**: Click "🍌 Edit with Nano Banana"
5. **View Results**: See before/after in tabbed display
6. **Share Results**: Use "📤 Send To..." to continue in other tabs

#### **Recent Results Panel**
1. **Browse Results**: See thumbnails of your last 50 generations
2. **Filter by Model**: Use dropdown to show specific AI model results
3. **Quick Reuse**: Click any thumbnail to open action menu
4. **Send to Tab**: Choose destination tab from "📤 Send To" menu
5. **File Management**: Right-click for folder access and deletion

#### **Resizable Layout**
1. **Drag Splitter**: Grab the bar between panels and drag to resize
2. **Keyboard Shortcuts**: Use Ctrl+[ to collapse, Ctrl+] to expand
3. **Reset Layout**: Press Ctrl+= to return to default sizes
4. **Auto-Save**: Your layout preferences are remembered

### Enhanced Video Experience

#### **YouTube-Like Video Player**
1. **Large Display**: Videos play in spacious, responsive player
2. **Interactive Controls**: Click progress bar to seek, adjust volume
3. **Auto-Hide Interface**: Controls fade when not in use
4. **Fullscreen Mode**: Click fullscreen button for immersive viewing
5. **File Management**: Access recent videos and results folder directly

## Requirements

- Python 3.7+
- tkinter (usually included with Python)
- requests
- python-dotenv
- Pillow (PIL)
- tkinterdnd2 (for drag & drop functionality)
- av==10.0.0 (for video playback)
- tkvideoplayer==2.3 (for enhanced video player)

## API Integration

This application integrates with the WaveSpeed AI API endpoints:
- **Balance**: `https://api.wavespeed.ai/api/v3/balance`
- **Nano Banana editing**: `https://api.wavespeed.ai/api/v3/google/nano-banana/edit`
- **SeedEdit**: `https://api.wavespeed.ai/api/v3/bytedance/seededit-v3`
- **Image upscaling**: `https://api.wavespeed.ai/api/v3/wavespeed-ai/image-upscaler`
- **Wan 2.2 video**: `https://api.wavespeed.ai/api/v3/wavespeed-ai/wan-2.2/i2v-480p`
- **SeedDance video**: `https://api.wavespeed.ai/api/v3/bytedance/seedance-v1-pro-i2v-480p`
- **Result polling**: `https://api.wavespeed.ai/api/v3/predictions/{request_id}/result`

## Auto-Save File Organization

### 📁 **Automatic Folder Structure**
All AI results are automatically saved to organized folders:

```
WaveSpeed_Results/
├── Nano_Banana_Editor/    # Nano Banana Editor results
├── SeedEdit/              # SeedEdit results  
├── Image_Upscaler/        # Upscaler results
├── Wan_2.2/               # Wan 2.2 video results
└── SeedDance/             # SeedDance video results
```

### 📝 **File Naming Convention**
Files are automatically named with detailed information:

**Images**: `{model}_{timestamp}_{prompt}_{settings}.png`
- Example: `seededit_20240904_143052_add_sunglasses_gs0.7_seed42.png`

**Videos**: `{model}_{timestamp}_{prompt}_{settings}.mp4`
- Example: `video_20240904_143052_dancing_cat_5s_seed123.mp4`

### 📋 **Metadata Files**
Each result includes a JSON metadata file with:
- Generation timestamp
- AI model used
- Full prompt text
- All settings and parameters
- Original result URL

## Keyboard Shortcuts

### Global Shortcuts
- `Ctrl + [` - Collapse recent results sidebar
- `Ctrl + ]` - Expand recent results sidebar  
- `Ctrl + =` - Reset splitter to default position

### Video Player Shortcuts
- `Space` - Play/pause video
- `Escape` - Exit fullscreen mode
- `F` - Toggle fullscreen
- `↑/↓` - Adjust volume
- `←/→` - Seek backward/forward

## Configuration Files

The application creates these files in your working directory:
- `ui_layout.conf` - Stores your preferred UI layout and splitter positions
- `data/saved_prompts.json` - Stores your saved Nano Banana Editor prompts
- `data/seededit_prompts.json` - Stores your saved SeedEdit prompts
- `WaveSpeed_Results/` - Auto-save directory for all generated content

## Advanced Features

### 🎯 **Professional Workflow Tools**
- **Result History**: Visual browser of all your AI generations
- **Cross-Model Chaining**: Seamlessly combine different AI models
- **Layout Customization**: Resize panels to match your workflow
- **Batch Processing**: Process multiple images through different models
- **Quality Pipeline**: Upscale → Edit → Refine → Animate workflows

### 🔧 **Developer-Friendly**
- **Modular Architecture**: Clean separation of concerns across files
- **Extensible Design**: Easy to add new AI models and features
- **Error Handling**: Comprehensive error handling with user feedback
- **Logging**: Detailed logging for debugging and monitoring
- **Cross-Platform**: Works on Windows, macOS, and Linux

### 🎨 **UI/UX Excellence**
- **Modern Design**: Professional interface with intuitive controls
- **Responsive Layout**: Adapts to any screen size or window configuration
- **Visual Feedback**: Clear progress indicators and status updates
- **Accessibility**: Keyboard shortcuts and clear visual hierarchy
- **Performance**: Optimized for smooth operation with large images and videos

## Troubleshooting

### Video Player Issues
If you encounter video playback problems:
```bash
# Install specific compatible versions
pip install av==10.0.0
pip install tkvideoplayer==2.3
```

### Balance API Issues
If the balance indicator shows errors:
- Check your API key in the `.env` file
- Verify internet connection
- The application will continue to work without balance display

### Layout Issues
If the UI layout appears broken:
- Delete `ui_layout.conf` to reset to defaults
- Restart the application
- Use keyboard shortcuts to reset splitter positions

## Contributing

This application is built with a modular architecture that makes it easy to:
- Add new AI model integrations
- Enhance existing UI components
- Implement additional workflow features
- Improve cross-platform compatibility

## License

This project integrates with WaveSpeed AI services. Please ensure you have appropriate API access and follow WaveSpeed AI's terms of service.

---

**WaveSpeed AI Complete Creative Suite** - Transform your creative workflow with professional AI-powered tools and an intuitive, customizable interface.