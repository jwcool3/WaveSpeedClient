# WaveSpeed AI Complete Suite

A comprehensive GUI application for AI-powered image editing, upscaling, and video generation using the WaveSpeed AI APIs.

## Features

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

### Image Editor Tab
- **Drag & Drop Support**: Simply drag images from your file explorer into the app
- **Image Selection**: Browse and select images from your computer with preview
- **Before/After Comparison**: Side-by-side view of original and edited images
- **Prompt Management**: Save, reuse, and manage your editing prompts
- **Persistent Storage**: Prompts are saved between app sessions
- **Chain Editing**: Use result images as input for the next edit
- **Format Selection**: Choose output format (PNG, JPG, WebP)
- **Progress Tracking**: Real-time status updates and progress indication
- **Result Display**: View processed images directly in the GUI
- **Image Saving**: Save edited images to your computer in various formats
- **Full Resolution**: Download and work with full-resolution images
- **Visual Feedback**: Interactive drop zones with hover and drag effects
- **Base64 Processing**: Actual image files are sent to the API (no placeholder URLs)
- **Auto-Save**: Results automatically saved with prompt and timestamp info

### SeedEdit Tab
- **Precise Modifications**: ByteDance SeedEdit-v3 for accurate image editing
- **Guidance Control**: Adjustable guidance scale (0.0-1.0) for editing strength
- **Seed Control**: Reproducible results with custom seeds
- **Fast Processing**: Optimized for quick image modifications
- **Sample Prompts**: Built-in examples for common editing tasks
- **Prompt Management**: Save, reuse, and manage your SeedEdit prompts
- **Cross-Tab Integration**: Use results in other tabs for complex workflows
- **URL-Based Processing**: Handles image uploads for API compatibility
- **Auto-Save**: Results automatically saved with prompt and settings info

### Image Upscaler Tab
- **AI Upscaling**: Enhance image resolution using WaveSpeed AI upscaler
- **Multiple Resolutions**: Choose from 2K, 4K, or 8K target resolutions
- **Creativity Control**: Adjust creativity level (-2 to +2) for upscaling enhancement
- **Format Options**: Output in PNG, JPEG, or WebP formats
- **Cross-Tab Integration**: Use upscaled images directly in the editor tab
- **Independent Processing**: Separate interface for dedicated upscaling tasks
- **Same UI Experience**: Consistent drag & drop and progress tracking
- **Auto-Save**: Results automatically saved with resolution and creativity settings

### Image to Video Tab (WAN-2.2)
- **AI Video Generation**: Convert static images into dynamic videos
- **Embedded Video Player**: Watch videos directly in the application
- **Playback Controls**: Play, pause, stop, and seek functionality
- **Customizable Duration**: Generate 5 or 8-second videos
- **Prompt Control**: Detailed prompts for video content and movement
- **Negative Prompts**: Specify what to avoid in video generation
- **Seed Control**: Reproducible results with custom seeds
- **Last Frame Control**: Optional last frame specification for video ending
- **Download Integration**: Save videos directly to your computer
- **Browser Fallback**: Open videos in browser when needed
- **URL Management**: Copy video URLs to clipboard for easy sharing
- **Auto-Save**: Videos automatically saved with duration and seed info

### SeedDance Tab (Pro Video)
- **Professional Video Generation**: ByteDance SeedDance-v1-Pro for high-quality videos
- **Embedded Video Player**: Watch videos directly in the application
- **Playback Controls**: Play, pause, stop, and seek functionality
- **Extended Duration**: Generate videos from 5 to 10 seconds
- **Camera Control**: Fixed or dynamic camera positioning
- **Optional Prompts**: Text prompts for enhanced video generation
- **Seed Control**: Reproducible results with custom seeds
- **High Quality**: Professional-grade video output
- **Fast Processing**: Optimized for quick video generation
- **Download Integration**: Save videos directly to your computer
- **Auto-Save**: Videos automatically saved with duration, camera, and seed settings

## Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Install Video Player (Optional but Recommended)**:
   ```bash
   # For embedded video playback
   python install_video_player.py
   
   # Or manually install
   pip install tkvideoplayer==2.3
   ```

3. **Set up API Key**:
   - Copy `env_example.txt` to `.env`
   - Add your WaveSpeed API key to the `.env` file:
     ```
     WAVESPEED_API_KEY=your_actual_api_key_here
     ```

4. **Run the Application**:
   ```bash
   # New modular version (recommended)
   python gui_app_new.py
   
   # Or run the main app directly
   python main_app.py
   
   # Original version (still available)
   python gui_app.py
   ```

## Usage

### Image Editor Tab

1. **Select an Image**: 
   - **Drag & Drop**: Simply drag an image file from your file explorer into the drop zone
   - **Browse**: Click "Browse Image" to select an image file using the file dialog
2. **Preview**: View your selected image in the "Original Image" panel
3. **Enter/Select Prompt**: 
   - Type your editing instructions in the current prompt area
   - **OR** select a saved prompt from the "Saved Prompts" list
   - Use "Save Prompt" to save frequently used prompts
4. **Choose Format**: Select your preferred output format (PNG, JPG, WebP)
5. **Process**: Click "Process Image" to start the editing process
6. **View Results**: Watch the progress and see the edited image appear in the "Edited Result" panel
7. **Save or Continue**: 
   - Use "Save Result Image" to download the edited image
   - **OR** use "Use as Next Input" to chain edits together

### SeedEdit Tab

1. **Select an Image**: 
   - Switch to the "SeedEdit" tab
   - **Drag & Drop**: Drag an image file into the drop zone
   - **Browse**: Click "Browse Image" to select an image file
2. **Configure Edit Settings**:
   - **Edit Instruction**: Describe the specific changes you want to make
   - **Save/Use Prompts**: Save frequently used prompts or select from saved ones
   - **Guidance Scale**: Adjust from 0.1 (subtle) to 1.0 (strong) editing
   - **Seed**: Use -1 for random or specify a number for reproducible results
3. **Process**: Click "Apply SeedEdit" to start the editing process
4. **View Results**: See the precisely edited image in the "SeedEdit Result" panel
5. **Save or Transfer**: 
   - Use "Save Result Image" to download the edited image
   - **OR** use "Use as Editor Input" to transfer to other tabs for further processing

### Image Upscaler Tab

1. **Select an Image**: 
   - Switch to the "Image Upscaler" tab
   - **Drag & Drop**: Drag an image file into the upscaler drop zone
   - **Browse**: Click "Browse Image" to select an image file
2. **Configure Settings**:
   - **Target Resolution**: Choose from 2K, 4K, or 8K
   - **Creativity Level**: Adjust from -2 (conservative) to +2 (creative)
   - **Output Format**: Select PNG, JPEG, or WebP
3. **Process**: Click "Upscale Image" to start the upscaling process
4. **View Results**: See the upscaled image in the "Upscaled Result" panel
5. **Save or Transfer**: 
   - Use "Save Result Image" to download the upscaled image
   - **OR** use "Use as Editor Input" to transfer to the editor tab for further processing

### Image to Video Tab

1. **Select an Image**: 
   - Switch to the "Image to Video" tab
   - **Drag & Drop**: Drag an image file into the drop zone
   - **Browse**: Click "Browse Image" to select an image file
2. **Configure Video Settings**:
   - **Video Prompt**: Describe the desired video content and movement
   - **Negative Prompt**: Specify what to avoid (optional)
   - **Duration**: Choose 5 or 8 seconds
   - **Seed**: Use -1 for random or specify a number for reproducible results
   - **Last Image**: Optional URL for video ending frame
3. **Generate**: Click "Generate Video" to start the video creation process
4. **View Results**: 
   - Click "Open Video in Browser" to view and download the video
   - Use "Copy Video URL" to share the video link

### SeedDance Tab

1. **Select an Image**: 
   - Switch to the "SeedDance" tab
   - **Drag & Drop**: Drag an image file into the drop zone
   - **Browse**: Click "Browse Image" to select an image file
2. **Configure Video Settings**:
   - **Video Prompt**: Optional text prompt for enhanced video generation
   - **Duration**: Choose from 5 to 10 seconds
   - **Camera Position**: Fixed (stable) or dynamic (moving) camera
   - **Seed**: Use -1 for random or specify a number for reproducible results
3. **Generate**: Click "Generate SeedDance Video" to start the video creation process
4. **View Results**: 
   - Click "Open Video in Browser" to view and download the video
   - Use "Copy Video URL" to share the video link

### New Workflow Features

**Prompt Management:**
- **Save Prompts**: Click "Save Prompt" to store frequently used prompts
- **Reuse Prompts**: Select from saved prompts and click "Use Selected"
- **Delete Prompts**: Remove unwanted prompts from your collection
- **Persistent Storage**: All prompts are saved in `saved_prompts.json`

**Chain Editing:**
- After getting a result, click "Use as Next Input" 
- The result becomes your new input image
- Apply additional edits iteratively
- Perfect for multi-step transformations

### Drag & Drop Tips
- The drop zone will highlight when you hover over it
- You can drag images directly from Windows Explorer, Mac Finder, or any file manager
- Supported formats: PNG, JPG, JPEG, GIF, BMP, WebP
- If drag & drop doesn't work, use the "Browse Image" button as a fallback

## Requirements

- Python 3.7+
- tkinter (usually included with Python)
- requests
- python-dotenv
- Pillow (PIL)
- tkinterdnd2 (for drag & drop functionality)
- tkvideoplayer (optional, for embedded video playback)

## Video Player Features

### 🎬 **Embedded Video Playback**
- **Direct Viewing**: Watch generated videos directly in the application
- **No External Dependencies**: Videos play without needing external media players
- **Automatic Download**: Videos are automatically downloaded for local playback
- **Seamless Integration**: Video player is integrated into the existing UI

### 🎮 **Playback Controls**
- **Play/Pause/Stop**: Standard video playback controls
- **Progress Tracking**: Visual feedback during video loading
- **Responsive UI**: Controls adapt to video status
- **Error Handling**: Graceful fallback if video player is unavailable

### 💾 **Download & Save Options**
- **Direct Download**: Save videos to your chosen location
- **Browser Fallback**: Open videos in browser when needed
- **URL Copying**: Copy video URLs to clipboard for sharing
- **Auto-Save Integration**: Videos automatically saved to organized folders

### 🔧 **Installation Options**
- **Easy Setup**: Run `python install_video_player.py` for guided installation
- **Manual Install**: `pip install tkvideoplayer==2.3`
- **Graceful Fallback**: Application works without video player (browser-only mode)
- **No Breaking Changes**: Existing functionality remains unchanged

## Enhanced Image Display

### 🖼️ **Large Result Previews**
- **Bigger Display**: Result images shown at 600x450+ pixels (vs previous 350x250)
- **Better Detail**: See fine details and quality of AI-generated results
- **Aspect Ratio**: Maintains original image proportions
- **Quality Preview**: High-quality thumbnails for accurate representation

### 🔍 **Full-Screen Image Viewer**
- **Double-Click Expansion**: Double-click any result image to view full-screen
- **Scrollable Zoom**: Navigate large images with mouse wheel scrolling
- **Original Resolution**: View images at their actual generated resolution
- **Keyboard Shortcuts**: Press ESC, Enter, or Space to close viewer
- **Save Integration**: Direct save option from full-screen viewer

### 🎯 **Optimized Input Display**
- **Compact Input**: Smaller input image preview (150x120) to save screen space
- **Optional Preview**: Can be disabled for video tabs to maximize workspace
- **Drag & Drop**: Still supports drag & drop on compact input preview
- **Smart Layout**: More space allocated to result display

### 🖱️ **Interactive Features**
- **Right-Click Menu**: Context menu with "View Full Size" and "Save Image" options
- **Visual Feedback**: Hover effects and cursor changes indicate interactive elements
- **Status Updates**: Brief success messages when saving images
- **Error Handling**: Clear error messages with fallback display options

## API Integration

This application integrates with the WaveSpeed AI API endpoints:
- **Image editing**: `https://api.wavespeed.ai/api/v3/google/nano-banana/edit`
- **SeedEdit**: `https://api.wavespeed.ai/api/v3/bytedance/seededit-v3`
- **Image upscaling**: `https://api.wavespeed.ai/api/v3/wavespeed-ai/image-upscaler`
- **Image to video (WAN-2.2)**: `https://api.wavespeed.ai/api/v3/wavespeed-ai/wan-2.2/i2v-480p`
- **SeedDance video**: `https://api.wavespeed.ai/api/v3/bytedance/seedance-v1-pro-i2v-480p`
- **Result polling**: `https://api.wavespeed.ai/api/v3/predictions/{request_id}/result`

The application handles:
- Asynchronous processing with polling
- Error handling and user feedback
- Progress indication during processing
- Automatic result image downloading and display
- Full-resolution image saving with format conversion
- Side-by-side before/after comparison

## Enhanced Features

- **Large Result Display**: Bigger image previews (600x450+) for better detail viewing
- **Expandable Image Viewer**: Double-click images to view full-screen with scrollable zoom
- **Context Menu**: Right-click images for quick save and view options
- **Optimized Input Preview**: Smaller, optional input image preview to save space
- **Drag & Drop Interface**: Intuitive file selection with visual feedback
- **Visual Comparison**: See your original and edited images side by side
- **Automatic Download**: Result images are automatically downloaded and displayed
- **High Quality**: Full-resolution images are preserved for saving
- **Multiple Formats**: Save results in PNG, JPEG, or WebP formats
- **Interactive UI**: Hover effects, drag indicators, and responsive design
- **Cross-Platform**: Works on Windows, Mac, and Linux with drag & drop support
- **User-Friendly**: No need to manually copy URLs - everything is handled in the GUI
- **Workflow Optimization**: Chain edits together for complex transformations
- **Prompt Library**: Build and manage your collection of editing prompts
- **Session Persistence**: Your prompts are automatically saved and restored

## Auto-Save File Organization

### 📁 **Automatic Folder Structure**
All AI results are automatically saved to organized folders:

```
WaveSpeed_Results/
├── Image_Editor/           # Image Editor results
├── SeedEdit/              # SeedEdit results  
├── Image_Upscaler/        # Upscaler results
├── Image_to_Video/        # Video generation results
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

### 🎯 **Easy Access**
- **Menu**: File → "Open Results Folder" to browse all results
- **Auto-Creation**: Folders created automatically when first result is saved
- **Cross-Platform**: Works on Windows, macOS, and Linux

## Privacy & Security Settings

### 🔒 **Privacy Modes**

The application offers three privacy levels to protect your images:

#### **🔒 HIGH PRIVACY (Recommended)**
- **How it works**: Uses base64 data URLs - your images are converted to text data
- **Privacy**: Your images **never leave your computer** or get uploaded anywhere
- **Compatibility**: May not work with all APIs (some require external URLs)
- **Best for**: Maximum privacy when APIs support base64 data

#### **⚠️ MEDIUM PRIVACY (Balanced)**
- **How it works**: Temporary hosting with automatic 1-hour deletion
- **Privacy**: Images uploaded temporarily but automatically deleted
- **Compatibility**: Works with all APIs that require public URLs
- **Best for**: Good balance of privacy and functionality

#### **🔓 DEMO MODE (Testing)**
- **How it works**: Uses built-in sample images for demonstration
- **Privacy**: Your images are **never uploaded** - only sample images processed
- **Compatibility**: Works with all APIs
- **Best for**: Testing the application without uploading personal images

### ⚙️ **Changing Privacy Settings**
1. Go to **File → Privacy Settings** in the menu
2. Select your preferred privacy level
3. Click **Save Settings**
4. Your choice applies to all future image processing

## Files Created

The application creates these files in your working directory:
- `saved_prompts.json` - Stores your saved Image Editor prompts (automatically created)
- `seededit_prompts.json` - Stores your saved SeedEdit prompts (automatically created)
- `temp_result_image.png` - Temporary file when using "Use as Next Input" (auto-managed)
- `temp_upscaled_image.png` - Temporary file when transferring upscaled images to editor (auto-managed)

## New Modular Architecture

The application has been restructured into multiple files for better organization:

### Core Files
- `main_app.py` - Main application and window management
- `api_client.py` - All WaveSpeed AI API interactions
- `utils.py` - Utility functions and common operations
- `ui_components.py` - Reusable UI components and base classes

### Tab Modules
- `image_editor_tab.py` - Image editing functionality
- `seededit_tab.py` - SeedEdit precise image modifications
- `image_upscaler_tab.py` - Image upscaling functionality  
- `image_to_video_tab.py` - Image-to-video generation (WAN-2.2)
- `seeddance_tab.py` - SeedDance professional video generation

### Launchers
- `gui_app_new.py` - New modular version launcher
- `gui_app.py` - Original single-file version (still functional)

## Workflow Examples

### Basic Upscaling
1. Go to "Image Upscaler" tab
2. Select an image (drag & drop or browse)
3. Choose target resolution (2K, 4K, or 8K)
4. Set creativity level (0 for balanced results)
5. Click "Upscale Image"
6. Save the result

### Upscale + Edit Workflow
1. **Upscale**: Use the upscaler tab to enhance resolution
2. **Transfer**: Click "Use as Editor Input" to move to editor tab
3. **Edit**: Apply prompt-based edits to the upscaled image
4. **Chain**: Continue editing or save the final result

### Edit + Upscale Workflow
1. **Edit**: Use the editor tab to apply creative edits
2. **Save**: Save the edited image to your computer
3. **Upscale**: Load the edited image in the upscaler tab
4. **Enhance**: Upscale to higher resolution

### Image to Video Workflow
1. **Prepare**: Start with a high-quality image (optionally upscaled)
2. **Generate**: Use the video tab to create animated content
3. **Customize**: Adjust duration, prompts, and creative parameters
4. **Share**: Download or share the generated video

### Complete Creative Pipeline
1. **Edit**: Enhance and modify your image with AI prompts
2. **Upscale**: Increase resolution for better video quality
3. **Animate**: Convert the final image into a dynamic video
4. **Export**: Save or share your complete creation

## Important Notes

### Image Editor
The editor tab properly sends your actual image files to the API using base64 encoding, so the drag & drop functionality will process the exact image you select!

### Image Upscaler, Video Generator, SeedEdit & SeedDance
The upscaler, video generator, SeedEdit, and SeedDance APIs require images to be provided as public URLs. Currently, these tabs use sample URLs for demonstration purposes. For production use, you'll need to implement image upload functionality to a service like:
- Imgur API
- Cloudinary
- AWS S3
- Your own image hosting service

The `upload_image_for_upscaler()`, `upload_image_for_video()`, `upload_image_for_seededit()`, and `upload_image_for_seeddance()` methods contain placeholder logic that you can replace with your preferred image hosting solution.

**Important**: When you drag & drop an image in these tabs, the application will show a warning dialog explaining that it's using a sample image for demonstration, while your actual image path is noted for future implementation.

### Video Generation
The video generator creates MP4 files that can be viewed in any modern web browser. Videos are delivered as download URLs and can be shared or embedded as needed.
