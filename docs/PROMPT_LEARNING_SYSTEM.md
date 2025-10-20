# 🧠 AI Prompt Learning System

## Overview

Your app now learns from your saved prompts! When you save prompts you like, the system uses AI to analyze them and extract patterns. These learned patterns are then automatically used to improve future prompt generation.

---

## How It Works

```
You save prompts you like
   ↓
Run AI analysis (one time)
   ↓
AI extracts patterns, vocabulary, structures
   ↓
Insights cached for future use
   ↓
When you click Mild/Moderate/Undress buttons
   ↓
Generated prompts incorporate learned patterns
   ↓
Results get better over time!
```

---

## Setup (First Time)

### Step 1: Analyze Your Saved Prompts

Run this command once to analyze your saved prompts:

```bash
python scripts/analyze_saved_prompts.py
```

This will:
- Load your last 100 saved prompts from `data/seedream_v4_prompts.json`
- Send them to Claude/OpenAI for AI analysis
- Extract patterns, vocabulary, and structures
- Cache the insights for future use

**Time:** Takes about 30-60 seconds

**Cost:** One API call to analyze all prompts

---

## What Gets Learned

The AI analyzes your prompts and extracts:

### 1. **Key Patterns**
Example patterns it might find:
- "Prompts starting with 'Remove... replace with...' are most effective"
- "Including frame fill percentage (85-95%) produces better results"
- "Direct language works better than flowery descriptions"

### 2. **Successful Vocabulary**
High-frequency words/phrases that appear in your saved prompts:
- "fully nude", "exposed", "medium shot", "looking at camera"
- "detailed skin texture", "natural lighting"
- "do not alter facial identity"

### 3. **Structural Recommendations**
Common structural patterns:
- Opening with clothing removal instructions
- Including specific shot framing
- Ending with preservation directives

### 4. **Style Guidance**
Overall tone and approach:
- Direct vs. poetic language
- Level of detail
- Technical terminology usage

---

## Usage

Once you've run the initial analysis, **it happens automatically**:

1. **Save prompts you like** (use the 💾 Save button)
2. **Click Mild/Moderate/Undress buttons**
3. Generated prompts will incorporate your learned patterns
4. **No additional steps needed!**

---

## Refresh Analysis

As you save more prompts, refresh the learning:

```bash
python scripts/analyze_saved_prompts.py
```

When prompted, type `y` to run fresh analysis.

**Recommended:** Refresh after saving 20-30 new prompts.

---

## Example Output

When you run the analyzer:

```
=====================================
🧠 AI PROMPT LEARNING ANALYZER
=====================================

📂 Loading saved prompts...
✅ Loaded 146 saved prompts

🧠 Analyzing with AI...
   Sending prompts to Claude for pattern analysis...

====================================
✅ ANALYSIS COMPLETE!
====================================

📊 Insights extracted:
   • Key Patterns: 8
   • Successful Vocabulary: 45
   • Structural Recommendations: 7

====================================
KEY PATTERNS IDENTIFIED:
====================================
1. Prompts use direct, technical language
2. Frame composition specified (85-95% fill)
3. Explicit "looking at camera" directions
4. Detailed anatomical descriptions
5. Consistent closing with "Do not alter..."
...

====================================
SUCCESSFUL VOCABULARY:
====================================
"remove", "replace", "fully nude", "exposed", 
"medium shot", "detailed", "natural lighting"...

====================================
✅ INSIGHTS CACHED!
====================================
📁 Saved to: data/adaptive_learning/ai_learning_insights.json

💡 These insights will now be automatically used 
   to enhance future prompt generation!
```

---

## Technical Details

### Files Created

- **`core/prompt_learning_analyzer.py`** - AI analysis engine
- **`scripts/analyze_saved_prompts.py`** - Analysis command
- **`data/adaptive_learning/ai_learning_insights.json`** - Cached insights

### Integration Points

The learning system enhances these methods in `ai_prompt_advisor.py`:
- `generate_mild_examples_only()`
- `generate_moderate_examples_only()`
- `generate_undress_transformations()`

### How Insights Are Applied

When generating prompts, the system:
1. Loads cached insights
2. Formats them as an enhancement section
3. Appends to the base system prompt
4. AI sees both the template AND your learned patterns
5. Generated prompts naturally incorporate your style

---

## Benefits

### Immediate Benefits:
- ✅ Prompts match your preferred style
- ✅ Generated prompts feel more "like yours"
- ✅ Better consistency across generations

### Long-Term Benefits:
- ✅ System improves as you save more prompts
- ✅ Learns your specific preferences
- ✅ Adapts to changing styles over time

---

## FAQ

**Q: Do I need to run the analysis every time?**  
A: No! Run it once, then it uses cached insights automatically. Refresh when you have ~20 new saved prompts.

**Q: Does this cost extra API calls?**  
A: Only when you run `analyze_saved_prompts.py`. Normal generation doesn't add API calls - it just enhances the prompt sent to the AI.

**Q: What if I don't like the learned patterns?**  
A: Just delete unwanted saved prompts from `data/seedream_v4_prompts.json` and re-run the analysis.

**Q: Can I see what patterns it learned?**  
A: Yes! Check `data/adaptive_learning/ai_learning_insights.json` or re-run the analysis script to see the output.

**Q: Will this work with both Claude and OpenAI?**  
A: Yes! Whichever API you have configured will be used for both analysis and generation.

---

## Next Steps

1. **Run the initial analysis:**
   ```bash
   python scripts/analyze_saved_prompts.py
   ```

2. **Test it out:**
   - Select an image
   - Click "🔥 Mild" or "⚡ Moderate" button
   - Notice generated prompts match your style!

3. **Keep improving:**
   - Save more prompts you like
   - Periodically refresh the analysis
   - Watch the system get better over time

---

## Future Enhancements (Planned)

- **Live learning:** Auto-refresh insights when you save prompts
- **Feedback buttons:** "👍 Good" / "👎 Bad" on results
- **Per-category learning:** Separate insights for mild/moderate/undress
- **Trend detection:** Notice when your style changes over time

---

**The system is now learning from your preferences automatically!** 🎉

