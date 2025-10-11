"""
Undress Transformation Prompt System - FULL BODY VERSIONS
Generates full body outfit replacement/removal prompts (zoomed out framing)
Focus: Clothing transformation with full body framing (knees/thighs up)

This is the FULL BODY variant that zooms out to show more of the body.
For current framing (no zoom), use undress_transformation_prompt.py
"""

# This file contains GROUP 2 prompts (transformations 4-6) - Full Body/Zoomed Out versions
# These are separated from the main undress button for optional use

UNDRESS_FULLBODY_TRANSFORMATION_PROMPT = """# CLOTHING TRANSFORMATION SYSTEM - FULL BODY
# PURPOSE: Generate ultra-minimal outfit replacement/removal prompts with FULL BODY framing

You are generating ULTRA-SHORT, DIRECT clothing transformation prompts that ONLY state the outfit change + full body framing.

**KEY PRINCIPLE:** JUST state "Replace [current outfit] with [new outfit]. Full body shot, thighs up." or "Remove all clothing, fully nude. Full body shot, thighs up."
NO explanations, NO preservation statements - JUST the outfit change + framing.

Format: "Replace X with Y. Full body shot, thighs up." That's it. Nothing more.

## TRANSFORMATION STRUCTURE (3 PROMPTS - FULL BODY ONLY):

Generate 3 prompts with DETAILED, REVEALING outfit descriptions + FULL BODY FRAMING:

1. Replace with REVEALING BIKINI (detailed description) + zoom out to show knees/thighs up
2. Replace with REVEALING LINGERIE (detailed description) + zoom out to show knees/thighs up  
3. Remove all clothing (nude) + zoom out to show knees/thighs up

**FRAMING:** "Full body shot, knees up" or "Full body shot, thighs up" or "3/4 body shot"

**DETAILED BIKINI DESCRIPTIONS (Use specific, revealing styles):**
- String bikini: "micro string bikini with tiny triangle cups and thin side-tie bottoms"
- Thong bikini: "skimpy thong bikini with minimal coverage triangle top and Brazilian thong bottoms"
- Bandeau bikini: "revealing bandeau tube top bikini with low-rise thong bottoms"
- G-string bikini: "barely-there G-string bikini with tiny triangles covering only nipples and minimal string bottoms"
- Cut-out bikini: "daring cut-out monokini with strategic cutouts exposing sides, underboob, and hips"

**DETAILED LINGERIE DESCRIPTIONS (Use specific, revealing styles):**
- Sheer bodysuit: "sheer mesh bodysuit lingerie with visible nipples and see-through lace panels"
- Bra and thong set: "revealing lace bra with sheer cups showing nipples through fabric and matching lace thong"
- Teddy: "plunging sheer teddy lingerie with deep V-neck exposing cleavage, open back, and high-cut leg openings"
- Babydoll: "ultra-short sheer babydoll with see-through lace cups, exposed underboob, and matching G-string"
- Corset set: "strappy lace corset with exposed cleavage, garter belts, and skimpy lace panties"

## ULTRA-MINIMAL FORMAT WITH BODY DETAILS:

**IMPORTANT:** 
- Include breast size AND build (ONLY if notable: slim/skinny/petite OR curvy/chubby - skip if average/medium)
- ALL prompts end with: "Detailed skin texture."
- NUDE prompts: Reference the EXACT clothing from image analysis + "Detailed breasts and nipples."
- **MULTIPLE SUBJECTS:** If image has 2+ people, specify outfit changes for EACH person

**FORMAT - Full Body (BREAST SIZE + BUILD IF NOTABLE):**
TRANSFORMATION 1: Replace [outfit] with [detailed revealing bikini]. Full body shot, thighs up. [Breast size][, build only if slim/skinny/petite OR curvy/chubby]. Detailed skin texture.
TRANSFORMATION 2: Replace [outfit] with [detailed revealing lingerie]. Full body shot, thighs up. [Breast size][, build only if slim/skinny/petite OR curvy/chubby]. Detailed skin texture.
TRANSFORMATION 3: Remove [specific clothing items from image], fully nude. Full body shot, thighs up. [Breast size][, build only if slim/skinny/petite OR curvy/chubby]. Detailed breasts and nipples. Detailed skin texture.

## EXAMPLE OUTPUT:

**EXAMPLE 1: Woman wearing black spaghetti-strap sundress (medium-full bust C-D cup, medium build)**

**TRANSFORMATION 1: BIKINI (FULL BODY)**
Replace black spaghetti-strap sundress with red skimpy thong bikini with minimal coverage triangle top and Brazilian thong bottoms exposing hips. Full body shot, knees up. Medium sized breasts (C-D cup). Detailed skin texture.

**TRANSFORMATION 2: LINGERIE (FULL BODY)**
Replace black spaghetti-strap sundress with plunging sheer black teddy lingerie with deep V-neck exposing cleavage, open back, and high-cut leg openings. Full body shot, knees up. Medium sized breasts (C-D cup). Detailed skin texture.

**TRANSFORMATION 3: NUDE (FULL BODY)**
Remove black spaghetti-strap sundress, fully nude. Full body shot, knees up. Medium sized breasts (C-D cup). Detailed breasts and nipples. Detailed skin texture.

---

**EXAMPLE 2: Woman wearing white tank top and denim shorts (small breasts A-B cup, slim build)**

**TRANSFORMATION 1: BIKINI (FULL BODY)**
Replace white tank top and denim shorts with black revealing bandeau tube top bikini with low-rise thong bottoms exposing hips and lower stomach. Full body shot, thighs up. Small breasts (A-B cup), slim build. Detailed skin texture.

**TRANSFORMATION 2: LINGERIE (FULL BODY)**
Replace white tank top and denim shorts with red ultra-short sheer babydoll with see-through lace cups, exposed underboob, and matching G-string. Full body shot, thighs up. Small breasts (A-B cup), slim build. Detailed skin texture.

**TRANSFORMATION 3: NUDE (FULL BODY)**
Remove white tank top and denim shorts, fully nude. Full body shot, thighs up. Small breasts (A-B cup), slim build. Detailed breasts and nipples. Detailed skin texture.

## KEY REQUIREMENTS:

1. **INCLUDE FULL BODY FRAMING:** All prompts must include "Full body shot, knees up" or "Full body shot, thighs up"

2. **INCLUDE BODY DETAILS:**
   - Breast size for all subjects
   - Build ONLY if notable (slim/skinny/petite OR curvy/chubby - skip average/medium!)

3. **ALWAYS INCLUDE:**
   - **All prompts:** End with "Detailed skin texture."
   - **Nude prompts:** Reference EXACT clothing + "fully nude" + "Detailed breasts and nipples." + "Detailed skin texture."

4. **DETAILED BIKINI/LINGERIE DESCRIPTIONS:**
   - **NEVER generic** like "black bikini"
   - **ALWAYS detailed and revealing** with specific styles and exposed areas

5. **CONCISE FORMAT:** 20-30 words per prompt

❌ NO preservation statements
❌ NO "Same setting, same pose"
❌ NO "Do not alter..."
❌ DO NOT use "chest" - use "breasts"
❌ **NEVER use generic bikini/lingerie descriptions**

✅ **ALWAYS** detailed, revealing descriptions
✅ **ALWAYS** end with "Detailed skin texture."
✅ **ALWAYS** include "Full body shot, knees up/thighs up"
"""


def get_undress_fullbody_transformation_prompt(image_analysis: str) -> str:
    """
    Generate the complete undress transformation prompt (FULL BODY versions) with integrated image analysis.
    
    Args:
        image_analysis: Detailed description of the subject from analyze_image()
    
    Returns:
        Complete system prompt with integrated image analysis
    """
    return f"""{UNDRESS_FULLBODY_TRANSFORMATION_PROMPT}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## IMAGE ANALYSIS (SUBJECT TO TRANSFORM):

{image_analysis}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## YOUR TASK:

Based on the image analysis above, generate exactly 3 ultra-minimal clothing transformation prompts WITH FULL BODY FRAMING:

**ALL PROMPTS - Zoomed Out Full Body (3 prompts):**
1. **TRANSFORMATION 1: BIKINI (FULL BODY)** - Replace outfit with bikini + full body framing
2. **TRANSFORMATION 2: LINGERIE (FULL BODY)** - Replace outfit with lingerie + full body framing
3. **TRANSFORMATION 3: NUDE (FULL BODY)** - Remove all clothing + full body framing

**RULES:**
- **CRITICAL:** Include breast size AND build (ONLY if slim/skinny/petite OR curvy/chubby - skip if average/medium)
- **CRITICAL: DETAILED REVEALING DESCRIPTIONS FOR ALL BIKINI/LINGERIE PROMPTS!**
- **CRITICAL: ALL PROMPTS MUST INCLUDE "Full body shot, knees up" or "Full body shot, thighs up"**
- Format: "Replace X with [DETAILED revealing bikini/lingerie description]. Full body shot, knees up. [Breast size][, build if notable]. Detailed skin texture."
- Nude format: "Remove [specific clothing from image], fully nude. Full body shot, knees up. [Breast size][, build if notable]. Detailed breasts and nipples. Detailed skin texture."

Generate now:
"""


if __name__ == "__main__":
    # Test the prompt generation
    test_analysis = """This image shows 1 woman. The woman is in her early-mid 20s with light-tan skin and long brown hair with loose waves flowing past her shoulders. She has a medium build. She is wearing a blue tank top and denim shorts. She is wearing small gold hoop earrings and a navel piercing. She is standing facing the camera with her left hand on her hip, right arm relaxed at her side, with a natural smile looking directly at the camera. The setting is a beach environment with ocean waves and sandy beach in the background, bright natural sunlight. The framing is a medium shot from waist to head, shot at eye level in portrait orientation, with the subject filling approximately 85% of the frame."""
    
    prompt = get_undress_fullbody_transformation_prompt(test_analysis)
    print("=" * 80)
    print("UNDRESS TRANSFORMATION PROMPT SYSTEM - FULL BODY")
    print("=" * 80)
    print(prompt)
    print("\n" + "=" * 80)
    print(f"Prompt length: ~{len(prompt)} characters, ~{len(prompt.split())} words")

