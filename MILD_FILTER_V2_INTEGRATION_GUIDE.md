# Mild Filter Training Prompt V2 - Integration Guide

## Overview

`mild_filter_training_prompt_v2.py` is an enhanced version of the mild filter training system with:
- **12 categories** (up from 6)
- **24 detailed examples** (2 per category)
- **Generates 10 prompts** instead of 5
- **140-160 word optimal formula** based on successful testing
- **Strong creativity instructions** to prevent example copying
- **Full backward compatibility** with existing code

## What's New in V2

### 📦 **12 Categories** (Original had ~6)

1. Micro Bikinis & Revealing Swimwear
2. Lingerie & Intimate Wear
3. Costume/Roleplay
4. Partial Exposure (Pulling Aside/Down)
5. Downblouse/Accidental Exposure
6. Fantasy/Themed Revealing Outfits
7. **NEW: Wet/Water Revealing**
8. **NEW: Latex/Leather/Tight Materials**
9. **NEW: Workout/Athletic Revealing**
10. **NEW: Office/Professional Revealing**
11. **NEW: Public/Outdoor Risky**
12. **NEW: Club/Party/Night Wear**

### ✨ **Key Improvements**

1. **Optimal Prompt Structure (140-160 words)**
   - Based on extensive testing with successful prompts
   - 7-part formula for consistency
   - Frame fill percentages (85-95%)
   - "Looking at camera/viewer" emphasis

2. **Porn-Style Language**
   - Uses natural language: "tits", "pussy", "camel toe"
   - Explicit visibility descriptions
   - Direct, effective terminology

3. **Strong Creativity Instructions**
   - ⚠️ Major addition: "DO NOT COPY THE EXAMPLES" section
   - Examples are templates, not scripts
   - Forces unique garments, poses, settings, combinations
   - Prevents AI from regurgitating examples

4. **Enhanced Quality Checklist**
   - 10-point checklist per prompt
   - Ensures variety across all 10 generated prompts
   - Validates category diversity

## Integration Options

### **Option 1: Change Import (Recommended for Testing)**

In `core/ai_prompt_advisor.py`, line 1371:

```python
# OLD:
from core.mild_filter_training_prompt import get_mild_filter_prompt_with_analysis

# NEW:
from core.mild_filter_training_prompt_v2 import get_mild_filter_prompt_with_analysis
```

**Pros:**
- Easy to test
- Can switch back quickly
- Original file preserved
- No risk

**Cons:**
- Need to remember which version is active
- One code change required

### **Option 2: File Rename (Recommended for Production)**

```bash
# Backup original
mv core/mild_filter_training_prompt.py core/mild_filter_training_prompt_old.py

# Activate V2
mv core/mild_filter_training_prompt_v2.py core/mild_filter_training_prompt.py
```

**Pros:**
- ✅ Zero code changes needed
- ✅ Drop-in replacement
- ✅ All existing imports work unchanged
- ✅ Original safely backed up

**Cons:**
- Need to rename files

## Available Functions

All functions from the original are implemented for full compatibility:

```python
# Main V2 function
get_mild_v2_prompt(analysis=None)

# Compatibility wrappers (same as original)
get_mild_filter_prompt_with_analysis(image_analysis=None)
get_mild_prompt(analysis=None)

# Helper function
format_analysis_for_prompt(analysis)
```

## Testing the V2 File

```bash
cd C:\Users\itssa\Downloads\wave2\WaveSpeedClient
python core/mild_filter_training_prompt_v2.py
```

Expected output:
```
======================================================================
Mild Filter Training Prompt V2 - Loaded Successfully
======================================================================

Prompt length: 30173 characters
Total categories: 12
Examples per category: 2 (24 total examples)
Prompts generated per request: 10
```

## Category Selection

The system will:
1. Select 10 different categories from the 12 available
2. Generate one prompt per selected category
3. Ensure no category repeats in a single generation
4. Maximize diversity across garments, colors, materials, poses, settings

## Creativity Enforcement

The V2 includes a dedicated "CRITICAL CREATIVITY INSTRUCTIONS" section that:

- ⚠️ Explicitly warns: "DO NOT COPY THE EXAMPLES!"
- Provides specific guidance on making prompts different
- Shows comparison examples (Example uses X → You should use Y)
- Covers 5 areas: garments, poses, settings, combinations, details
- Emphasizes examples are TEMPLATES, not scripts to copy

This prevents the AI from lazily copying example prompts and ensures fresh, varied outputs.

## Word Count & Structure

**Original:** 60-100 words per prompt
**V2:** 140-160 words per prompt

V2 uses the proven optimal formula:
1. CLOTHING CHANGE (25-30 words)
2. SHOT & FRAME (10 words)
3. SETTING (10-15 words)
4. MAIN POSE (30-40 words)
5. FACIAL & EXPRESSION (15-20 words)
6. KEY DETAILS (20-25 words)
7. FINAL DIRECTIVE (15-20 words)

## Backward Compatibility

✅ **100% backward compatible**

All function names and signatures match the original exactly:
- `get_mild_filter_prompt_with_analysis()` - Main function used by ai_prompt_advisor
- `get_mild_prompt()` - Legacy wrapper
- `format_analysis_for_prompt()` - Helper function

No changes needed to calling code.

## Prompt Output Changes

### Original System:
- Generates 5 prompts
- Each 60-100 words
- Fewer categories to choose from

### V2 System:
- Generates 10 prompts
- Each 140-160 words
- 12 categories with 24 examples
- Stronger creativity enforcement
- More detailed and specific

## Benefits

1. ✅ **More Variety** - 12 categories vs 6, 10 prompts vs 5
2. ✅ **Better Quality** - 140-160 word optimal formula tested and proven
3. ✅ **Prevents Copying** - Strong creativity instructions
4. ✅ **More Examples** - 24 detailed examples vs fewer
5. ✅ **Modern Language** - Uses effective porn terminology
6. ✅ **Drop-in Compatible** - Zero breaking changes
7. ✅ **Well Documented** - Clear structure and instructions

## Migration Path

### Phase 1: Test (Now)
```python
# In ai_prompt_advisor.py
from core.mild_filter_training_prompt_v2 import get_mild_filter_prompt_with_analysis
```

### Phase 2: Validate
- Generate prompts with V2
- Compare quality to original
- Verify 10 prompts are generated
- Check category diversity

### Phase 3: Production
```bash
# Backup and switch
mv core/mild_filter_training_prompt.py core/mild_filter_training_prompt_old.py
mv core/mild_filter_training_prompt_v2.py core/mild_filter_training_prompt.py
```

### Phase 4: Cleanup (Optional)
- After confirming V2 works well
- Can delete or archive the old version

## File Size Comparison

- **Original:** ~368 lines
- **V2:** ~549 lines
- **Increase:** +181 lines (+49%)

Extra content:
- 6 additional categories (12 vs 6)
- 2 examples per category (24 total)
- Creativity instructions section
- Enhanced documentation

## Questions?

The V2 file includes comprehensive inline documentation. Run it standalone to see all integration instructions:

```bash
python core/mild_filter_training_prompt_v2.py
```

