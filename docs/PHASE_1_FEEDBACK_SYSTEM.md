# Phase 1: Feedback Tracking System

## 🎯 Overview
The feedback tracking system allows WaveSpeed to learn which prompts produce good results and which don't, making the AI prompt generation smarter over time.

## ✅ What's Been Implemented

### 1. **PromptResultTracker** (`core/prompt_result_tracker.py`)
- Tracks prompt success/failure rates
- Stores data in `data/adaptive_learning/prompt_results.jsonl` (JSONL format for incremental writes)
- Generates statistics in `data/adaptive_learning/prompt_stats.json`
- **Key Methods:**
  - `track_generation()` - Track when a prompt is used
  - `track_result_saved()` - Track successful prompt (user explicitly saved it)
  - `track_result_deleted()` - Track failed prompt (user deleted the result)
  - `track_feedback()` - Track explicit user feedback (👍/👎 buttons)
  - `get_successful_prompts()` - Get prompts with high success rates
  - `get_failed_prompts()` - Get prompts with low success rates

### 2. **Feedback Buttons in Recent Results** (`ui/components/recent_results_panel.py`)
- Added 👍 (thumbs up) and 👎 (thumbs down) buttons to each result thumbnail
- Buttons change color when clicked:
  - 👍 turns green background when marked good
  - 👎 turns red background when marked bad
- Feedback is saved to:
  - Memory (immediate UI update)
  - Metadata JSON file (persistent storage)
  - Prompt tracker (for learning)

### 3. **Automatic Tracking Hooks**
- **Prompt saves** (`ui/components/seedream/prompt_section.py`):
  - When user clicks "💾 Save Prompt" button
  - Prompt is saved to `data/seedream_v4_prompts.json`
  - **Tracked as SUCCESSFUL** (user explicitly chose to save it)
  
- **Result deletion** (`ui/components/recent_results_panel.py`):
  - When user deletes a result from Recent Results panel
  - **Tracked as FAILED** (user didn't like it)

- **Note:** Auto-save does NOT track as successful
  - Auto-save happens for ALL generated images
  - Only explicit prompt saves indicate user approval

### 4. **Enhanced AI Analysis with Image Context** (`core/prompt_learning_analyzer.py`)
- AI now receives success rate data when analyzing prompts
- **NEW: Image descriptions included for context**
  - Stores AI description of input image with each tracked prompt
  - Shows what was in the original photo (e.g., "woman holding soda can")
  - Helps AI understand why certain prompts worked (e.g., prompt removes soda can)
- Analysis includes:
  - High success prompts (>70% success rate) with image context
  - Low success prompts (<30% success rate)
  - Overall statistics (average success rate, total feedback count)
- AI uses this to identify patterns that work vs. don't work
- **Context-aware learning:** AI can now understand that successful prompts match the image content

## 📊 How It Works

### User Journey:
1. **Generate Images:**
   - User generates images with Mild/Moderate/Undress buttons
   - Images auto-save to `WaveSpeed_Results/Seedream_V4/`
   
2. **Give Feedback:**
   - **Option A:** Click 👍/👎 on results in Recent Results panel
   - **Option B:** Delete unwanted results (counts as 👎)
   - **Option C:** Save good prompts with "💾 Save Prompt" button (counts as 👍👍)

3. **AI Learns:**
   - Run: `python scripts/analyze_saved_prompts.py`
   - AI analyzes all saved prompts + feedback data
   - Extracts patterns from successful vs. failed prompts
   - Caches insights to `data/adaptive_learning/ai_learning_insights.json`

4. **Better Prompts:**
   - Next time you click Mild/Moderate/Undress buttons
   - AI uses learned insights to generate better prompts
   - Prompts now favor patterns that worked well

## 📁 Data Files

### Input Files:
- `data/seedream_v4_prompts.json` - User's explicitly saved prompts (SUCCESS indicators)

### Output Files:
- `data/adaptive_learning/prompt_results.jsonl` - All tracked events (JSONL format)
  - **Now includes `image_description` field** for context
- `data/adaptive_learning/prompt_stats.json` - Aggregated statistics
- `data/adaptive_learning/ai_learning_insights.json` - AI-extracted patterns

### Metadata Files:
- `WaveSpeed_Results/Seedream_V4/*.json` - Per-image metadata
  - Includes `feedback` field (good/bad/saved/deleted)
  - **Includes `image_description` field** (AI description of input image)

## 🚀 Usage

### For Users:
1. Generate images normally
2. Give feedback on results:
   - 👍 = good result
   - 👎 = bad result  
   - 💾 Save Prompt = really good result
   - 🗑️ Delete = really bad result
3. Periodically run: `python scripts/analyze_saved_prompts.py`
4. Enjoy smarter prompt generation!

### For Developers:
```python
from core.prompt_result_tracker import get_prompt_tracker

tracker = get_prompt_tracker()

# Track a successful result with image context
tracker.track_result_saved(
    prompt="Replace top with red bikini, remove soda can from hand",
    result_path="path/to/image.png",
    metadata={"source": "mild_button"},
    image_description="Young woman in white t-shirt holding a soda can, standing outdoors"
)

# Track explicit feedback with context
tracker.track_feedback(
    prompt="Replace top with red bikini, remove soda can from hand",
    feedback="good",  # or "bad"
    result_path="path/to/image.png",
    image_description="Young woman in white t-shirt holding a soda can, standing outdoors"
)

# Get statistics
stats = tracker.get_prompt_stats("Replace top with red bikini, remove soda can from hand")
print(f"Success rate: {stats['success_rate']:.1%}")

# Get successful prompts (AI will now see the image context)
successful = tracker.get_successful_prompts(min_success_rate=0.7)
```

## 🧪 Testing

Run the test suite:
```bash
python scripts/test_feedback_system.py
```

This tests:
- Basic tracking functionality
- Feedback button tracking
- Success/failure detection
- Summary statistics generation
- AI integration readiness
- Data file creation

## 📈 Success Metrics

### What Gets Tracked as SUCCESS:
- ✅ User clicks 👍 on a result
- ✅ User saves prompt with "💾 Save Prompt" button
- ✅ (Future) User keeps result for 7+ days without deleting

### What Gets Tracked as FAILURE:
- ❌ User clicks 👎 on a result
- ❌ User deletes a result
- ❌ (Future) User immediately deletes result after generation

### What Does NOT Get Tracked:
- 🚫 Auto-save (happens for all results, not an indicator of quality)
- 🚫 Viewing a result (doesn't indicate satisfaction)
- 🚫 Generating a prompt (success unknown until feedback given)

## 🔮 Future Enhancements (Phase 2 & 3)

### Phase 2: Real-time Adaptation
- Auto-refresh insights every 50 new feedback events
- Show success rate in Recent Results panel
- Suggest improvements for low-performing prompts

### Phase 3: Advanced Learning
- A/B testing of prompt variations
- Automatic prompt refinement suggestions
- Context-aware learning (different patterns for different image types)
- Export/import learning profiles

## 🐛 Troubleshooting

### No feedback data appearing?
- Make sure you're clicking 👍/👎 buttons or saving prompts
- Check `data/adaptive_learning/prompt_results.jsonl` exists
- Run: `python scripts/test_feedback_system.py`

### AI analysis not improving prompts?
- Run: `python scripts/analyze_saved_prompts.py` after giving feedback
- Check `data/adaptive_learning/ai_learning_insights.json` exists
- Verify your AI API keys are configured

### Feedback buttons not showing?
- Refresh the Recent Results panel (click 🔄)
- Check that metadata JSON files exist alongside images

## 📝 Version History

- **v1.1** (2025-10-20): Added image context tracking
  - AI image descriptions now stored with each prompt
  - AI analysis includes image context for better learning
  - Metadata files include `image_description` field
  - Helps AI understand why prompts work in specific contexts
  
- **v1.0** (2025-10-20): Initial Phase 1 implementation
  - Basic tracking system
  - Feedback buttons
  - AI analysis integration
  - Auto-save clarification (not tracked as success)

---

**Built with ❤️ for smarter AI prompt generation!**

