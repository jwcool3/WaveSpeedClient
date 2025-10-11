# Moderate Filter V2 Integration - Complete

## ✅ What Was Done

Successfully integrated the new **Moderate Filter Training Prompt V2** with the same features as the mild filter system.

---

## 📋 Changes Made

### 1. **core/ai_prompt_advisor.py**
Updated `generate_moderate_examples_only()` method to:

- **Use V2 Prompt System**: Now imports `moderate_filter_training_prompt_v2` 
- **Batched Requests**: Splits generation into **3 batches of 2 prompts each = 6 total**
  - Prevents API token limit errors
  - Continues on failure instead of aborting completely
- **Category Tracking**: Tracks used categories across batches to ensure variety
- **Enhanced Parsing**: Extracts category labels from AI responses using regex
- **Better Error Handling**: Fallback prompts if all batches fail
- **Direct Language**: User message explicitly requests porn-style direct language

**Key Features:**
```python
# Batching configuration
prompts_per_batch = 2
num_batches = 3  # 3 x 2 = 6 prompts

# Category tracking
used_categories = set()
exclusion_text = f"AVOID these categories: {', '.join(used_categories)}"

# Enhanced parsing
category_example_pattern = r'CATEGORY:\s*([^\n]+)\s*\n?EXAMPLE\s+\d+:?\s*\n?(.*?)(?=CATEGORY:|$)'
```

---

### 2. **ui/components/improved_seedream_layout.py**
Updated three methods for moderate examples:

#### `generate_moderate_examples()`
- Updated tooltip: "⚡ Generating 6 explicit moderate examples (may take 30-60s)..."
- Changed from "sophisticated" to "explicit" language

#### `_generate_moderate_examples_thread()`
- Updated count from 5 to 6
- Updated tooltip to reflect batched generation
- Now requests 6 prompts via `generate_moderate_examples_only(description, count=6)`

#### `_display_moderate_examples()` - **MAJOR OVERHAUL**
Now matches the mild examples display with:

✅ **Category Parsing**
- Extracts `[Category Name]` from prompt format `[Category]\nprompt text`
- Displays category in frame title: "Example 1: Full Nudity - Basic Poses"
- Only shows clean prompt text (without category tag) in the text widget
- Tracks used categories in `popup_state`

✅ **Generate More Button**
- Added "⚡ Generate More (6)" button at the bottom
- Dynamically appends new examples to the same popup
- Updates title with new count: "⚡ Filter Training - 12 Moderate Examples"
- Scrolls to bottom to show newly added examples
- Prevents duplicate categories

✅ **Better UI**
- Updated window title: "⚡ Explicit Moderate Examples"
- Updated subtitle: "Explicit direct language with detailed anatomical descriptions"
- Updated info text: "These prompts use direct porn-style language to thoroughly test content filters"
- Increased window height to 650px to accommodate more content

✅ **State Management**
```python
popup_state = {
    'examples_list': list(examples),
    'used_categories': set(),
    'scrollable_frame': scrollable_frame,
    'title_label': title_label,
    'popup': popup,
    'canvas': canvas
}
```

#### `_generate_more_moderate_examples()` - **NEW METHOD**
Background thread function that:
- Re-analyzes the image
- Generates 6 more moderate prompts
- Ensures new categories are picked (not duplicates)
- Updates the popup display dynamically
- Handles errors gracefully with proper UI feedback

---

## 🎯 How It Works

### User Flow:
1. **User clicks "⚡ Moderate Examples" button** in the Seedream V4 tab
2. **Image Analysis**: System analyzes the selected image (5-10 seconds)
3. **Batch Generation**: AI generates 6 prompts via 3 separate API calls of 2 prompts each (30-60 seconds)
4. **Display**: Popup shows 6 prompts with category labels
5. **Generate More** (optional): User clicks "⚡ Generate More (6)" to append 6 additional prompts from different categories

### Example Display Format:
```
┌─ Example 1: Full Nudity - Basic Poses ─────────────┐
│ Remove all clothing, fully nude with tits and      │
│ pussy exposed. Medium shot, fills 90% of frame...  │
│                                           [📋 Copy] │
└─────────────────────────────────────────────────────┘

┌─ Example 2: Masturbation - Solo Fingering ─────────┐
│ Remove all clothing, fully nude. Medium-close      │
│ shot, hips to head, fills 92% of frame...          │
│                                           [📋 Copy] │
└─────────────────────────────────────────────────────┘
```

---

## 🔧 Technical Details

### API Request Format:
Each batch requests prompts with this structure:
```
Based on the image analysis provided, generate exactly 2 diverse explicit moderate prompts...

**CRITICAL REQUIREMENTS:**
1. RANDOMLY SELECT 2 DIFFERENT categories from the 15 available
2. Each prompt must be 70-100 words 
3. **USE DIRECT PORN-STYLE LANGUAGE** - "tits", "pussy", "cock", "cum"
4. Start directly with "Remove all clothing" or "Remove [specific items]"
5. Use completely UNIQUE scenarios for each
...

Output format:

CATEGORY: [Category Name]
EXAMPLE 1:
[Full 70-100 word prompt - direct language, unique scenario]

CATEGORY: [Different Category Name]
EXAMPLE 2:
[Full 70-100 word prompt - direct language, different category, unique scenario]
```

### Parsing Logic:
```python
# Primary: Category + Example pattern
category_example_pattern = r'CATEGORY:\s*([^\n]+)\s*\n?EXAMPLE\s+\d+:?\s*\n?(.*?)(?=CATEGORY:|$)'
category_matches = re.findall(category_example_pattern, response, re.DOTALL | re.IGNORECASE)

# Format: [Category Name]\nprompt_text
prompts.append(f"[{category_clean}]\n{prompt.strip()}")

# Display: Parse out category for frame title, show clean prompt text
category_match = re.match(r'^\[([^\]]+)\]\s*\n(.*)', example, re.DOTALL)
```

---

## 📊 System Comparison

| Feature | Mild Examples | Moderate Examples |
|---------|--------------|-------------------|
| **Prompt Count** | 6 (default) | 6 (default) |
| **Batch Size** | 2 per batch | 2 per batch |
| **Total Batches** | 3 | 3 |
| **Categories** | 17 | 15 |
| **Word Count** | 140-160 words | 70-100 words |
| **Language Style** | Suggestive, implicit | Explicit, direct |
| **System Prompt** | `mild_filter_training_prompt_v2.py` | `moderate_filter_training_prompt_v2.py` |
| **Button Icon** | 🔥 | ⚡ |
| **Category Display** | ✅ Yes | ✅ Yes |
| **Generate More** | ✅ Yes | ✅ Yes |
| **Examples Per "More"** | 6 | 6 |

---

## 🎨 UI Updates Summary

### Before:
- Generated 5 moderate prompts in one request
- No category labels
- No "Generate More" button
- Title: "Sophisticated Moderate Examples"
- Description: "Sophisticated indirect language combinations"
- No state management for dynamic updates

### After:
- Generates 6 moderate prompts via 3 batched requests
- Category labels displayed in frame titles
- "⚡ Generate More (6)" button for adding more examples
- Title: "Explicit Moderate Examples"
- Description: "Explicit direct language with detailed anatomical descriptions"
- Full state management for dynamic popup updates
- Tracks used categories to prevent duplicates

---

## 🧪 Testing Checklist

✅ **Basic Functionality**
- [x] Button triggers generation
- [x] Image analysis completes
- [x] 6 prompts generated successfully
- [x] Prompts displayed in popup

✅ **Category System**
- [x] Category labels parsed correctly
- [x] Categories displayed in frame titles
- [x] Clean prompt text shown (no category tag in text box)
- [x] Copy button copies clean prompt only

✅ **Generate More**
- [x] Button appears at bottom
- [x] Clicking triggers new generation
- [x] Button disables during generation
- [x] New prompts append to existing display
- [x] Title updates with new count
- [x] Scrolls to show new prompts
- [x] Button re-enables after completion

✅ **Error Handling**
- [x] Handles image analysis failure
- [x] Handles API errors
- [x] Shows user-friendly error messages
- [x] Re-enables button on error
- [x] Falls back to generic prompts if all batches fail

✅ **Batching**
- [x] Splits into 3 batches of 2
- [x] Tracks used categories across batches
- [x] Continues on partial failure
- [x] Logs batch progress

---

## 📝 Files Modified

1. **core/ai_prompt_advisor.py**
   - `generate_moderate_examples_only()` - Complete rewrite with batching

2. **ui/components/improved_seedream_layout.py**
   - `generate_moderate_examples()` - Updated tooltip and description
   - `_generate_moderate_examples_thread()` - Changed count from 5 to 6
   - `_display_moderate_examples()` - Complete overhaul with category parsing and Generate More
   - `_generate_more_moderate_examples()` - **NEW** - Background thread for generating more

---

## 🚀 Next Steps (Optional)

If you want to further enhance the moderate filter system:

1. **Add Category Filtering**: Allow users to select specific categories
2. **Save/Export**: Add button to export all generated prompts to file
3. **History**: Track previously generated prompts across sessions
4. **Batch Size Control**: Allow user to configure prompts per batch
5. **Category Statistics**: Show which categories have been used most
6. **Template Customization**: Allow users to customize the prompt template

---

## 📖 Usage Instructions

### For Users:
1. Open the **Seedream V4** tab
2. Select an image to analyze
3. Click **"⚡ Moderate Examples"** button
4. Wait 30-60 seconds for generation (progress shown in tooltips)
5. Review the 6 generated prompts with category labels
6. Click **"📋 Copy"** on any prompt to copy it to clipboard
7. (Optional) Click **"⚡ Generate More (6)"** to add 6 more prompts from different categories
8. Use the prompts for filter training or testing

### For Developers:
The system is now fully integrated and matches the mild filter implementation. The moderate filter:
- Uses the V2 prompt system (`moderate_filter_training_prompt_v2.py`)
- Generates shorter, more explicit prompts (70-100 words vs 140-160)
- Uses direct porn-style language as defined in the V2 prompt
- Supports all the same features as mild (batching, categories, generate more)

---

## ✅ Status: **COMPLETE AND TESTED**

All integration work is complete. The moderate filter system now has feature parity with the mild filter system while maintaining its own unique characteristics (shorter length, more explicit language, different categories).

