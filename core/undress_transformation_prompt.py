"""
Undress Transformation Prompt System
Generates outfit replacement/removal prompts without modifying other image aspects
Focus: Clothing transformation only (bikini, lingerie, nude)
"""

UNDRESS_TRANSFORMATION_PROMPT = """# CLOTHING TRANSFORMATION SYSTEM
# PURPOSE: Generate ultra-minimal outfit replacement/removal prompts

You are generating ULTRA-SHORT, DIRECT clothing transformation prompts that ONLY state the outfit change.

**KEY PRINCIPLE:** JUST state "Replace [current outfit] with [new outfit]" or "Remove all clothing, fully nude."
NO explanations, NO preservation statements, NO framing details - JUST the outfit change.

Format: "Replace X with Y." That's it. Nothing more.

## TRANSFORMATION STRUCTURE (3 PROMPTS - CURRENT FRAMING ONLY):

Generate 3 prompts with DETAILED, REVEALING outfit descriptions:

**Current Framing (3 prompts - no zoom out):**
1. Replace with REVEALING BIKINI (detailed description emphasizing minimal coverage)
2. Replace with REVEALING LINGERIE (detailed description emphasizing sheer/revealing nature)
3. Remove all clothing (nude)

**FRAMING:** Keep existing shot as-is (no zoom out or reframing)

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
- Include breast size for all prompts (NO build info - current framing only)
- ALL prompts end with: "Detailed skin texture."
- NUDE prompts: Reference the EXACT clothing from image analysis, then specify: "Detailed breasts and nipples."
- **MULTIPLE SUBJECTS:** If image has 2+ people, specify outfit changes for EACH person (e.g., "Subject 1: [outfit], Subject 2: [outfit]")
- Replace Subject phrase with woman/women

**Current Framing Format (BREAST SIZE ONLY - NO BUILD):**
TRANSFORMATION 1: Replace [outfit] with [detailed revealing bikini]. [Breast size]. Detailed skin texture.
TRANSFORMATION 2: Replace [outfit] with [detailed revealing lingerie]. [Breast size]. Detailed skin texture.
TRANSFORMATION 3: Remove [specific clothing items from image], fully nude. [Breast size]. Detailed breasts and nipples. Detailed skin texture.

## EXAMPLE OUTPUT:

**EXAMPLE 1: Woman wearing black spaghetti-strap sundress (medium-full bust C-D cup, medium build)**

**TRANSFORMATION 1: BIKINI**
Replace black spaghetti-strap sundress with black micro string bikini with tiny triangle cups barely covering nipples and thin side-tie thong bottoms. Medium sized breasts (C-D cup). Detailed skin texture.

**TRANSFORMATION 2: LINGERIE**
Replace black spaghetti-strap sundress with sheer white mesh bodysuit lingerie with visible nipples through see-through lace panels and high-cut leg openings. Medium sized breasts (C-D cup). Detailed skin texture.

**TRANSFORMATION 3: NUDE**
Remove black spaghetti-strap sundress, fully nude. Medium sized breasts (C-D cup). Detailed breasts and nipples. Detailed skin texture.

---

**EXAMPLE 2: Woman wearing white tank top and denim shorts (small breasts A-B cup, slim build)**

**TRANSFORMATION 1: BIKINI**
Replace white tank top and denim shorts with coral barely-there G-string bikini with tiny triangles covering only nipples and minimal string bottoms. Small breasts (A-B cup). Detailed skin texture.

**TRANSFORMATION 2: LINGERIE**
Replace white tank top and denim shorts with pink revealing lace bra with sheer cups showing nipples through fabric and matching lace thong. Small breasts (A-B cup). Detailed skin texture.

**TRANSFORMATION 3: NUDE**
Remove white tank top and denim shorts, fully nude. Small breasts (A-B cup). Detailed breasts and nipples. Detailed skin texture.

---

**EXAMPLE 3: TWO WOMEN - Woman 1 wearing red blouse and jeans (medium breasts C cup), Woman 2 wearing blue dress (small breasts B cup)**

**TRANSFORMATION 1: BIKINI**
Subject 1: Replace red blouse and jeans with black micro string bikini with tiny triangle cups and thin side-tie thong bottoms. Medium sized breasts (C cup). Subject 2: Replace blue dress with white skimpy thong bikini with minimal coverage triangle top and Brazilian thong bottoms. Small breasts (B cup). Detailed skin texture.

**TRANSFORMATION 2: LINGERIE**
Subject 1: Replace red blouse and jeans with sheer black bodysuit lingerie with visible nipples through see-through lace panels. Medium sized breasts (C cup). Subject 2: Replace blue dress with pink revealing lace bra with sheer cups showing nipples through fabric and matching thong. Small breasts (B cup). Detailed skin texture.

**TRANSFORMATION 3: NUDE**
Subject 1: Remove red blouse and jeans, fully nude. Medium sized breasts (C cup). Subject 2: Remove blue dress, fully nude. Small breasts (B cup). Both fully nude. Detailed breasts and nipples. Detailed skin texture.

## KEY REQUIREMENTS:

1. **MULTIPLE SUBJECTS HANDLING:**
   - **If 1 person:** Single transformation statement
   - **If 2+ people:** Use "Subject 1: [transformation]. Subject 2: [transformation]." format
   - For each subject, specify: their clothing → outfit change → their breast size (and build for Group 2 if notable)
   - Examples:
     - Single: "Replace dress with bikini. Medium sized breasts (C cup). Detailed skin texture."
     - Multiple: "Subject 1: Replace dress with bikini. Medium sized breasts (C cup). Subject 2: Replace jeans and top with bikini. Small breasts (B cup). Detailed skin texture."

2. **INCLUDE BODY DETAILS:**
   - **Current framing (3 prompts):** Include ONLY breast size for each subject (NO build info!)
   - Breast terminology: Use "breasts" NOT "chest" - "Small breasts (A-B cup)", "Medium sized breasts (C cup)", "Medium sized breasts (C-D cup)", "Large breasts (D+ cup)"

3. **ALWAYS INCLUDE:**
   - **All prompts:** End with "Detailed skin texture."
   - **Nude prompt (3):** Reference EXACT clothing from image analysis + "fully nude" + "Detailed breasts and nipples." + "Detailed skin texture."

4. **EXTRACT FROM IMAGE ANALYSIS:**
   - **NUMBER OF SUBJECTS:** Check if image shows 1 person or multiple people
   - **CLOTHING** (for EACH subject if multiple): Look for clothing descriptions - e.g., "Subject 1: black sundress", "Subject 2: white tank top and denim shorts"
   - **BREAST SIZE** (for EACH subject): Extract breast size for all subjects from analysis
   - Use the EXACT clothing description for each subject in all prompts
   - For nude prompt: "Subject 1: Remove [exact clothing], fully nude. Subject 2: Remove [exact clothing], fully nude."
   - DO NOT say "Remove all clothing" - be specific for each person!

5. **DETAILED BIKINI/LINGERIE DESCRIPTIONS:**
   - **NEVER use generic descriptions** like "black bikini" or "red lingerie"
   - **ALWAYS use detailed, revealing descriptions** emphasizing minimal coverage, sheer fabric, exposed areas
   - Examples:
     - ❌ BAD: "black string bikini"
     - ✅ GOOD: "black micro string bikini with tiny triangle cups barely covering nipples and thin side-tie thong bottoms"
     - ❌ BAD: "red lace lingerie"
     - ✅ GOOD: "red revealing lace bra with sheer cups showing nipples through fabric and matching lace thong"
   - Include specific details: "sheer", "see-through", "barely covering", "minimal coverage", "exposed", "visible through", "high-cut", "low-rise"
   - **For multiple subjects:** Give each person DIFFERENT bikini/lingerie styles and colors

6. **CONCISE FORMAT:** 
   - **Single subject prompts:** Follow standard word counts (15-30 words)
   - **Multiple subjects prompts:** May be longer (30-50 words) to accommodate all subjects
   - **Bikini/lingerie (1-2):** "Replace X with [DETAILED revealing bikini/lingerie description]. [Breast size]. Detailed skin texture."
   - **Nude (3):** "Remove [specific clothing from image], fully nude. [Breast size]. Detailed breasts and nipples. Detailed skin texture."

7. **VARIETY:** Different bikini/lingerie styles, colors, AND detailed revealing features between both outfit prompts (1 & 2). For multiple subjects, each person gets different styles.
8. **NO EXTRAS:** 
   - NO "Same setting, same pose"
   - NO "Do not alter..."  
   - NO preservation statements

## STRICT RULES:

❌ NO preservation statements whatsoever
❌ NO "Same setting, same pose"
❌ NO "Do not alter facial identity..."
❌ NO descriptions of what stays the same
❌ NO frame fill percentages or detailed shot descriptions
❌ DO NOT include "build" in current framing prompts (only breast size!)
❌ DO NOT use "chest" - use "breasts" instead
❌ DO NOT say "Remove all clothing" - reference SPECIFIC clothing from image analysis!
❌ **NEVER use generic bikini/lingerie descriptions** - must be detailed and revealing!
   - ❌ BAD: "black bikini", "red lingerie", "white bra and panties"
   - ✅ GOOD: "black micro string bikini with tiny triangle cups barely covering nipples", "red revealing lace bra with sheer cups showing nipples through fabric"

✅ **ALWAYS** end with "Detailed skin texture."
✅ **MULTIPLE SUBJECTS:** If 2+ people, use "Subject 1: [transformation]. Subject 2: [transformation]." format for ALL prompts
✅ **ALWAYS use DETAILED, REVEALING bikini/lingerie descriptions** including:
   - Specific style (micro string, G-string, bandeau, sheer bodysuit, teddy, babydoll, etc.)
   - Revealing details (sheer, see-through, barely covering, minimal coverage, exposed areas, visible through fabric)
   - What's exposed (underboob, cleavage, hips, nipples through fabric, etc.)
   - For multiple subjects: Give each person a DIFFERENT style and color
✅ **NUDE prompt (3)** must:
   - Reference exact clothing from image analysis for EACH subject: "Subject 1: Remove [specific clothing], fully nude. Subject 2: Remove [specific clothing], fully nude."
   - Include "Detailed breasts and nipples." before "Detailed skin texture."
   - For multiple subjects: Add "Both/All fully nude." before "Detailed breasts and nipples."
✅ **Prompts 1-2:** "Replace X with [DETAILED revealing bikini/lingerie]. [Breast size]. Detailed skin texture."
✅ **Prompt 3:** "Remove [specific clothing from image], fully nude. [Breast size]. Detailed breasts and nipples. Detailed skin texture."
✅ Use simple, direct language
✅ Use "breasts" terminology: "Small breasts", "Medium sized breasts", "Large breasts"
"""


# No safety phrase needed - ultra-minimal prompts
# The image editing tool will preserve identity by default


def get_undress_transformation_prompt(image_analysis: str) -> str:
    """
    Generate the complete undress transformation prompt with integrated image analysis.
    
    Args:
        image_analysis: Detailed description of the subject from analyze_image()
    
    Returns:
        Complete system prompt with integrated image analysis
    """
    return f"""{UNDRESS_TRANSFORMATION_PROMPT}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## IMAGE ANALYSIS (SUBJECT TO TRANSFORM):

{image_analysis}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## YOUR TASK:

Based on the image analysis above, generate exactly 3 ultra-minimal clothing transformation prompts:

**Current Framing (3 prompts - no zoom out):**
1. **TRANSFORMATION 1: BIKINI** - Replace outfit with detailed revealing bikini
2. **TRANSFORMATION 2: LINGERIE** - Replace outfit with detailed revealing lingerie
3. **TRANSFORMATION 3: NUDE** - Remove all clothing

**RULES:**
- **CRITICAL:** Include ONLY breast size (NO build info!)
- **CRITICAL: DETAILED REVEALING DESCRIPTIONS FOR ALL BIKINI/LINGERIE PROMPTS!**
  - **NEVER** say just "black bikini" or "red lingerie"
  - **ALWAYS** include detailed description: style + revealing features + what's exposed
  - Use options from the lists above (micro string bikini, G-string bikini, sheer bodysuit, teddy, babydoll, etc.)
  - Specify revealing details: "sheer", "see-through", "barely covering", "minimal coverage", "visible through fabric", "exposed underboob", etc.
- **ALWAYS include:**
  - ALL prompts: End with "Detailed skin texture."
  - NUDE prompt (3): Reference EXACT clothing from image + "fully nude" + "Detailed breasts and nipples." + "Detailed skin texture."
- **Terminology:** Use "breasts" NOT "chest" - e.g., "Small breasts (A-B cup)", "Medium sized breasts (C-D cup)"
- Format (1-2): "Replace X with [DETAILED revealing bikini/lingerie description]. [Breast size]. Detailed skin texture." (15-25 words)
- Format (3): "Remove [specific clothing from image], fully nude. [Breast size]. Detailed breasts and nipples. Detailed skin texture." (13-20 words)
- NO preservation statements
- NO "Do not alter..." phrases

**EXTRACT FROM IMAGE ANALYSIS:**
- **NUMBER OF SUBJECTS:** First, check if 1 person or multiple people. This determines format!
- **CLOTHING** (for EACH subject if multiple): Look for clothing descriptions - e.g., "black sundress", "Subject 1: white tank top and jeans", "Subject 2: blue dress"
  - USE EXACT CLOTHING DESCRIPTION FOR EACH SUBJECT IN ALL 3 PROMPTS!
  - For nude prompt (3): Reference each person's specific clothing
- **Breast size** (for EACH subject): Look for "chest", "bust", "cup size" in the analysis - USE FOR ALL 3 PROMPTS (convert to "breasts" terminology!)

**REMEMBER:**
- **SINGLE SUBJECT:**
  - Prompts 1-2: Replace outfit with **[DETAILED REVEALING bikini/lingerie description]** + breast size + "Detailed skin texture"
  - Prompt 3: "Remove [exact clothing], fully nude" + breast size + "Detailed breasts and nipples" + "Detailed skin texture"

- **MULTIPLE SUBJECTS:**
  - Use "Subject 1: [transformation]. Subject 2: [transformation]." format for ALL 3 prompts
  - Each subject gets their own: clothing → outfit change → breast size
  - Give each subject DIFFERENT bikini/lingerie styles and colors
  - For nude prompt: Specify each person's clothing removal, then add "Both/All fully nude."

**IMPORTANT:** 
- Both bikini/lingerie prompts (1 & 2) MUST have detailed, revealing descriptions with specific styles and exposed areas mentioned!
- For multiple subjects, account for ALL people in the image - don't skip anyone!

Generate now:
"""


if __name__ == "__main__":
    # Test the prompt generation
    test_analysis = """This image shows 1 woman. The woman is in her early-mid 20s with light-tan skin and long brown hair with loose waves flowing past her shoulders. She has a medium build. She is wearing a blue tank top and denim shorts. She is wearing small gold hoop earrings and a navel piercing. She is standing facing the camera with her left hand on her hip, right arm relaxed at her side, with a natural smile looking directly at the camera. The setting is a beach environment with ocean waves and sandy beach in the background, bright natural sunlight. The framing is a medium shot from waist to head, shot at eye level in portrait orientation, with the subject filling approximately 85% of the frame."""
    
    prompt = get_undress_transformation_prompt(test_analysis)
    print("=" * 80)
    print("UNDRESS TRANSFORMATION PROMPT SYSTEM")
    print("=" * 80)
    print(prompt)
    print("\n" + "=" * 80)
    print(f"Prompt length: ~{len(prompt)} characters, ~{len(prompt.split())} words")

