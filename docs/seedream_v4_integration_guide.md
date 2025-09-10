# 🌟 Seedream V4 Integration Guide

## Overview
This guide shows how to integrate the new **Bytedance Seedream V4** model into your WaveSpeed AI application. Seedream V4 is described as "surpassing nano banana in every aspect" with multi-modal image generation support.

## 🆕 Key Features of Seedream V4
- **Multi-modal image generation**: Text-to-image, image-editing, and group image generation
- **Outstanding advantages**: Precise instruction editing, high feature retention, deep understanding
- **Ultra-fast inference**: As little as 1.8 seconds to generate a 2K image
- **Ultra-high-resolution**: Support for resolutions up to 4096×4096 pixels
- **Complex editing operations**: Object addition/deletion, attribute changes, style transformations, structural adjustments

## 📁 Files to Create/Update

### 1. Create New Tab File
**File**: `ui/tabs/seedream_v4_tab.py`
- Complete implementation of Seedream V4 tab
- Uses optimized image layout like other tabs
- Includes prompt management and cross-tab sharing
- Supports all Seedream V4 features and settings

### 2. Update Configuration
**File**: `app/config.py`
- Add new endpoint: `'seedream_v4': f"{BASE_URL}/bytedance/seedream-v4/edit"`
- Add auto-save folder: `'seedream_v4': 'Seedream_V4'`
- Add sample URL for fallback
- Add size options: `SEEDREAM_V4_SIZES` array
- Update version to 2.6

### 3. Update API Client
**File**: `core/api_client.py`
- Add new method: `submit_seedream_v4_task()`
- Handles image array format (images field is an array)
- Supports size, seed, and prompt parameters
- Includes proper error handling and logging

### 4. Update Main Application
**File**: `app/main_app.py`
- Import `SeedreamV4Tab`
- Add tab to notebook: `🌟 Seedream V4`
- Update menu items with correct tab indices
- Update about dialog with Seedream V4 info

### 5. Update Cross-Tab Navigation
**File**: `ui/components/cross_tab_navigator.py`
- Add `seedream_v4` to tab mapping
- Update tab indices (shifts existing tabs)
- Add to available targets list

### 6. Update Recent Results Panel
**File**: `ui/components/recent_results_panel.py`
- Add "Seedream V4" to tab names array
- Update tab index mapping

### 7. Create Data Directory
**Directory**: `data/`
- Create `seedream_v4_prompts.json` for prompt storage

## 🎯 API Parameters

### Request Parameters
```json
{
  "prompt": "string - The editing instruction",
  "images": ["array - Image URLs or base64"],
  "size": "string - Format: width*height (1024*1024 to 4096*4096)",
  "seed": "integer - Random seed (-1 to 2147483647)",
  "enable_sync_mode": false,
  "enable_base64_output": false
}
```

### Supported Sizes
- `1024*1024`
- `1024*2048` 
- `2048*1024`
- `2048*2048`
- `2048*4096`
- `4096*2048`

## 🚀 Installation Steps

1. **Add the new tab file** (`seedream_v4_tab.py`) to `ui/tabs/`
2. **Update configuration** in `app/config.py`
3. **Add API method** in `core/api_client.py`
4. **Update main app** in `app/main_app.py`
5. **Update cross-tab navigation** components
6. **Test the integration** with sample prompts

## 🎨 UI Features

### New Tab Interface
- **🌟 Seedream V4** tab with state-of-the-art icon
- **Optimized layout** matching other tabs (30/70 split)
- **Multi-line prompt editor** with guidance text
- **Size selector** for different output resolutions
- **Seed control** for reproducible results
- **Prompt management** (save/load/delete)
- **Cross-tab sharing** to send results to other models
- **Auto-save integration** with organized folder structure

### Sample Prompts
The tab includes helpful sample prompts like:
- "Transform the person into a Renaissance-style painting with oil paint texture"
- "Change the background to a futuristic cyberpunk cityscape with neon lights"
- "Convert this image to anime style with vibrant colors"
- "Add magical elements like floating particles and glowing effects"

## 🔄 Cross-Tab Workflow
Users can now:
1. Edit images with **Nano Banana Editor**
2. Refine with **SeedEdit V3**
3. **Enhance with Seedream V4** (NEW!)
4. Upscale with **Image Upscaler**
5. Convert to video with **Wan 2.2** or **SeedDance**

## 📊 Updated Tab Order
1. 🍌 **Nano Banana Editor** (index 0)
2. ✨ **SeedEdit** (index 1) 
3. 🌟 **Seedream V4** (index 2) - **NEW**
4. 🔍 **Image Upscaler** (index 3)
5. 🎬 **Wan 2.2** (index 4)
6. 🕺 **SeedDance** (index 5)

## 🎯 Benefits for Users
- **Latest AI technology** with state-of-the-art results
- **Faster processing** (1.8s for 2K images)
- **Higher quality output** with better feature retention
- **More precise control** over editing operations
- **Seamless integration** with existing workflow
- **Professional UI** matching the app's design standards

This integration maintains your application's high-quality user experience while adding cutting-edge AI capabilities!