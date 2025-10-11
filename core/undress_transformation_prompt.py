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

## TRANSFORMATION STRUCTURE (5 PROMPTS - CURRENT FRAMING ONLY):

Generate 5 prompts with DETAILED, REVEALING outfit descriptions:

**Current Framing (5 prompts - no zoom out):**
1. Replace with REVEALING BIKINI (detailed description emphasizing minimal coverage)
2. Replace with REVEALING LINGERIE (detailed description emphasizing sheer/revealing nature)
3. Replace with SEXY FANTASY OUTFIT (detailed costume/roleplay description)
4. Remove all clothing (nude)
5. AI's CREATIVE CHOICE (revealing/sexy outfit completely different from categories 1-3)

**FRAMING:** Keep existing shot as-is (no zoom out or reframing)

**DETAILED BIKINI DESCRIPTIONS (Use specific, revealing styles):**
- Micro string bikini: "micro string bikini with tiny triangle cups barely covering nipples and thin side-tie thong bottoms exposing entire ass"
- G-string bikini: "barely-there G-string bikini with tiny triangles covering only nipples and minimal string bottoms showing full ass"
- Thong bikini: "skimpy thong bikini with minimal coverage triangle top and Brazilian thong bottoms exposing ass cheeks"
- Bandeau bikini: "revealing bandeau tube top bikini straining to contain breasts with low-rise thong bottoms"
- Triangle bikini: "ultra-tiny triangle bikini with string ties barely covering nipples and high-cut bottoms showing hip curves"
- Side-tie bikini: "scandalous side-tie bikini with adjustable strings, triangles barely covering nipples, and revealing thong bottoms"
- Cut-out monokini: "daring cut-out monokini with strategic cutouts exposing sides, underboob, cleavage, and hips"
- Sling bikini: "extreme sling bikini with thin straps connecting top and bottom, exposing maximum skin and barely covering nipples"
- Halter micro bikini: "halter neck micro bikini with tiny cups straining over breasts and G-string bottoms"
- Metallic micro bikini: "shiny metallic micro bikini with reflective tiny triangles barely covering nipples and skimpy string bottoms"

**DETAILED LINGERIE DESCRIPTIONS (Use specific, revealing styles):**
- Sheer bodysuit: "completely sheer mesh bodysuit lingerie with nipples clearly visible through see-through fabric and exposed crotch area"
- Lace bra & thong: "revealing lace bra with ultra-sheer cups showing nipples and areolas through fabric paired with matching lace thong"
- Plunging teddy: "plunging sheer teddy lingerie with deep V-neck exposing cleavage down to navel, open back, and high-cut leg openings"
- Sheer babydoll: "ultra-short sheer babydoll barely covering ass with see-through lace cups exposing nipples and underboob, plus matching G-string"
- Strappy corset: "strappy lace corset pushing breasts up with exposed cleavage, garter belts attached to stockings, and skimpy lace panties"
- Open-cup bra: "revealing open-cup bra with underwire framing bare breasts, nipples fully exposed, paired with crotchless lace panties"
- Sheer chemise: "sheer silk chemise nightie with lace trim, nipples visible through thin fabric, barely covering ass"
- Cupless bodysuit: "cupless sheer bodysuit with open breast area exposing nipples, see-through mesh torso, and thong back"
- Lace bralette: "ultra-sheer lace bralette with visible nipples through delicate fabric paired with high-waist lace thong showing curves"
- Fishnet bodysuit: "fishnet bodysuit lingerie with large net holes exposing skin all over, barely covering nipples and crotch"

**DETAILED FANTASY/ROLEPLAY OUTFIT DESCRIPTIONS (Use specific, sexy costume styles):**
- Sexy succubus: "sexy succubus costume with revealing red leather corset pushing breasts up, tiny black horns, demon tail, and skimpy thong bottoms with garter straps"
- Fantasy warrior: "revealing fantasy armor with metal bikini top barely covering breasts, leather straps across exposed torso, and minimal loincloth bottom exposing hips and ass"
- French maid: "slutty French maid costume with ultra-short ruffled skirt barely covering ass, plunging neckline exposing cleavage, sheer black stockings with garters"
- Naughty schoolgirl: "sexy schoolgirl uniform with tied white shirt exposing underboob and midriff, plaid micro-miniskirt rolled up showing ass, knee-high socks"
- Nurse costume: "slutty nurse outfit with white mini-dress unzipped to navel showing cleavage and visible bra, hem barely covering ass, thigh-high white stockings"
- Cheerleader: "revealing cheerleader uniform with tiny crop top exposing midriff and underboob, ultra-short pleated skirt showing ass when bent over"
- Devil costume: "sexy devil outfit with red leather bustier pushing breasts up and exposing cleavage, tiny horns, pointed tail, and skimpy red thong with garters"
- Playboy bunny: "classic Playboy bunny costume with black satin corset pushing breasts up, bunny ears, fluffy tail, fishnets, and high-cut leg openings exposing hips"
- Gothic vampire: "sexy vampire costume with black velvet corset laced tight showing cleavage, sheer lace sleeves, leather mini-skirt with thigh-high boots"
- Naughty catgirl: "sexy catgirl costume with black leather bra top with cat ears, collar with bell, tiny shorts showing ass cheeks, tail, and long gloves"
- Sexy elf/fairy: "revealing fantasy elf costume with metallic green bikini top with leaf details, tiny leaf-pattern bottoms, pointed ears, translucent fairy wings"
- Harley Quinn style: "sexy Harley Quinn inspired outfit with red and black crop top tied to expose underboob, booty shorts riding up showing ass, pigtails"
- Slave Leia: "iconic metal bikini costume with gold bikini top connected by chains, matching bottom piece, bare midriff, sheer flowing skirt panels"
- Latex dominatrix: "black latex dominatrix outfit with zipper-front catsuit unzipped to navel exposing cleavage, thigh-high boots, collar and leash"
- Sexy witch: "revealing witch costume with black corset with buckles pushing breasts up, ultra-short skirt exposing thighs, fishnet stockings, pointed hat"

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
TRANSFORMATION 3: Replace [outfit] with [detailed sexy fantasy/roleplay costume]. [Breast size]. Detailed skin texture.
TRANSFORMATION 4: Remove [specific clothing items from image], fully nude. [Breast size]. Detailed breasts and nipples. Detailed skin texture.
TRANSFORMATION 5: Replace [outfit] with [AI's creative choice - revealing/sexy but completely different from bikini/lingerie/fantasy]. [Breast size]. Detailed skin texture.

## EXAMPLE OUTPUT:

**EXAMPLE 1: Woman wearing black spaghetti-strap sundress (medium-full bust C-D cup, medium build)**

**TRANSFORMATION 1: BIKINI**
Replace black spaghetti-strap sundress with black micro string bikini with tiny triangle cups barely covering nipples and thin side-tie thong bottoms exposing entire ass. Medium sized breasts (C-D cup). Detailed skin texture.

**TRANSFORMATION 2: LINGERIE**
Replace black spaghetti-strap sundress with completely sheer mesh bodysuit lingerie with nipples clearly visible through see-through fabric and exposed crotch area. Medium sized breasts (C-D cup). Detailed skin texture.

**TRANSFORMATION 3: FANTASY**
Replace black spaghetti-strap sundress with sexy succubus costume with revealing red leather corset pushing breasts up, tiny black horns, demon tail, and skimpy thong bottoms with garter straps. Medium sized breasts (C-D cup). Detailed skin texture.

**TRANSFORMATION 4: NUDE**
Remove black spaghetti-strap sundress, fully nude. Medium sized breasts (C-D cup). Detailed breasts and nipples. Detailed skin texture.

**TRANSFORMATION 5: AI'S CHOICE**
Replace black spaghetti-strap sundress with wet white tank top clinging to body showing visible nipples and areolas through soaked fabric paired with tiny denim shorts riding up. Medium sized breasts (C-D cup). Detailed skin texture.

---

**EXAMPLE 2: Woman wearing white tank top and denim shorts (small breasts A-B cup, slim build)**

**TRANSFORMATION 1: BIKINI**
Replace white tank top and denim shorts with coral barely-there G-string bikini with tiny triangles covering only nipples and minimal string bottoms showing full ass. Small breasts (A-B cup). Detailed skin texture.

**TRANSFORMATION 2: LINGERIE**
Replace white tank top and denim shorts with pink ultra-sheer lace bralette with visible nipples through delicate fabric paired with high-waist lace thong showing curves. Small breasts (A-B cup). Detailed skin texture.

**TRANSFORMATION 3: FANTASY**
Replace white tank top and denim shorts with naughty schoolgirl uniform with tied white shirt exposing underboob and midriff, plaid micro-miniskirt rolled up showing ass, knee-high socks. Small breasts (A-B cup). Detailed skin texture.

**TRANSFORMATION 4: NUDE**
Remove white tank top and denim shorts, fully nude. Small breasts (A-B cup). Detailed breasts and nipples. Detailed skin texture.

**TRANSFORMATION 5: AI'S CHOICE**
Replace white tank top and denim shorts with sheer black mesh crop top with visible nipples and ultra-low-rise leather mini-skirt barely covering ass. Small breasts (A-B cup). Detailed skin texture.

---

**EXAMPLE 3: Woman wearing red off-shoulder crop top and high-waisted jeans (large breasts D+ cup)**

**TRANSFORMATION 1: BIKINI**
Replace red off-shoulder crop top and high-waisted jeans with turquoise halter neck micro bikini with tiny cups straining over breasts and G-string bottoms. Large breasts (D+ cup). Detailed skin texture.

**TRANSFORMATION 2: LINGERIE**
Replace red off-shoulder crop top and high-waisted jeans with black plunging sheer teddy lingerie with deep V-neck exposing cleavage down to navel, open back, and high-cut leg openings. Large breasts (D+ cup). Detailed skin texture.

**TRANSFORMATION 3: FANTASY**
Replace red off-shoulder crop top and high-waisted jeans with classic Playboy bunny costume with black satin corset pushing breasts up, bunny ears, fluffy tail, fishnets, and high-cut leg openings exposing hips. Large breasts (D+ cup). Detailed skin texture.

**TRANSFORMATION 4: NUDE**
Remove red off-shoulder crop top and high-waisted jeans, fully nude. Large breasts (D+ cup). Detailed breasts and nipples. Detailed skin texture.

**TRANSFORMATION 5: AI'S CHOICE**
Replace red off-shoulder crop top and high-waisted jeans with tight white sports bra straining over breasts and ultra-short spandex shorts riding up showing ass cheeks. Large breasts (D+ cup). Detailed skin texture.

---

**EXAMPLE 4: TWO WOMEN - Woman 1 wearing red blouse and jeans (medium breasts C cup), Woman 2 wearing blue dress (small breasts B cup)**

**TRANSFORMATION 1: BIKINI**
Subject 1: Replace red blouse and jeans with black micro string bikini with tiny triangle cups barely covering nipples and thin side-tie thong bottoms exposing entire ass. Medium sized breasts (C cup). Subject 2: Replace blue dress with white barely-there G-string bikini with tiny triangles covering only nipples and minimal string bottoms showing full ass. Small breasts (B cup). Detailed skin texture.

**TRANSFORMATION 2: LINGERIE**
Subject 1: Replace red blouse and jeans with completely sheer mesh bodysuit lingerie with nipples clearly visible through see-through fabric and exposed crotch area. Medium sized breasts (C cup). Subject 2: Replace blue dress with pink revealing lace bra with ultra-sheer cups showing nipples and areolas through fabric paired with matching lace thong. Small breasts (B cup). Detailed skin texture.

**TRANSFORMATION 3: FANTASY**
Subject 1: Replace red blouse and jeans with slutty French maid costume with ultra-short ruffled skirt barely covering ass, plunging neckline exposing cleavage, sheer black stockings with garters. Medium sized breasts (C cup). Subject 2: Replace blue dress with revealing cheerleader uniform with tiny crop top exposing midriff and underboob, ultra-short pleated skirt showing ass when bent over. Small breasts (B cup). Detailed skin texture.

**TRANSFORMATION 4: NUDE**
Subject 1: Remove red blouse and jeans, fully nude. Medium sized breasts (C cup). Subject 2: Remove blue dress, fully nude. Small breasts (B cup). Both fully nude. Detailed breasts and nipples. Detailed skin texture.

**TRANSFORMATION 5: AI'S CHOICE**
Subject 1: Replace red blouse and jeans with torn fishnet bodysuit with ripped holes exposing nipples and skin, black leather micro-shorts. Medium sized breasts (C cup). Subject 2: Replace blue dress with strappy black bandage dress with cutouts exposing underboob and sides, hem barely covering ass. Small breasts (B cup). Detailed skin texture.

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

5. **DETAILED BIKINI/LINGERIE DESCRIPTIONS (CRITICAL!):**
   - **NEVER use generic descriptions** like "black bikini" or "red lingerie"
   - **ALWAYS use ULTRA-DETAILED, REVEALING descriptions** from the lists above, emphasizing:
     - Specific style name (micro string, G-string, bandeau, sheer bodysuit, teddy, babydoll, etc.)
     - How revealing it is (barely covering, exposing, visible through, see-through, etc.)
     - What body parts are exposed/visible (nipples, ass, underboob, cleavage, crotch, etc.)
   - Examples:
     - ❌ BAD: "black string bikini"
     - ✅ GOOD: "black micro string bikini with tiny triangle cups barely covering nipples and thin side-tie thong bottoms exposing entire ass"
     - ❌ BAD: "red lace lingerie"
     - ✅ GOOD: "red revealing lace bra with ultra-sheer cups showing nipples and areolas through fabric paired with matching lace thong"
     - ❌ BAD: "white bodysuit"
     - ✅ GOOD: "completely sheer mesh bodysuit lingerie with nipples clearly visible through see-through fabric and exposed crotch area"
   - **Choose from the expanded lists above** - 10 bikini styles and 10 lingerie styles with full descriptions
   - **For multiple subjects:** Give each person DIFFERENT bikini/lingerie styles and colors, both with full detailed descriptions

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

Based on the image analysis above, generate exactly 5 ultra-minimal clothing transformation prompts:

**Current Framing (5 prompts - no zoom out):**
1. **TRANSFORMATION 1: BIKINI** - Replace outfit with detailed revealing bikini
2. **TRANSFORMATION 2: LINGERIE** - Replace outfit with detailed revealing lingerie
3. **TRANSFORMATION 3: FANTASY** - Replace outfit with detailed sexy fantasy/roleplay costume
4. **TRANSFORMATION 4: NUDE** - Remove all clothing
5. **TRANSFORMATION 5: AI'S CHOICE** - Replace outfit with creative revealing/sexy choice (completely different from 1-3)

**RULES:**
- **CRITICAL:** Include ONLY breast size (NO build info!)
- **CRITICAL: ULTRA-DETAILED REVEALING DESCRIPTIONS FOR ALL BIKINI/LINGERIE PROMPTS!**
  - **NEVER** say just "black bikini", "red lingerie", "white bodysuit", or any generic description
  - **ALWAYS** include FULL detailed description following this format:
    - **Style name** (micro string bikini, G-string bikini, halter micro bikini, sheer bodysuit, plunging teddy, etc.)
    - **Revealing features** (sheer, see-through, barely covering, minimal coverage, ultra-sheer cups, tiny triangles, etc.)
    - **What's exposed/visible** (nipples visible through fabric, ass exposed, underboob showing, cleavage down to navel, crotch area visible, etc.)
  - **Choose from the expanded lists above** with 10 bikini styles and 10 lingerie styles
  - Every bikini/lingerie description must be AT LEAST 12-20 words and include all three elements above
- **ALWAYS include:**
  - ALL prompts: End with "Detailed skin texture."
  - NUDE prompt (3): Reference EXACT clothing from image + "fully nude" + "Detailed breasts and nipples." + "Detailed skin texture."
- **Terminology:** Use "breasts" NOT "chest" - e.g., "Small breasts (A-B cup)", "Medium sized breasts (C-D cup)"
- Format (1-2, 3, 5): "Replace X with [ULTRA-DETAILED revealing outfit description with style + revealing features + what's exposed]. [Breast size]. Detailed skin texture." (20-35 words for single subject, 35-50 words for multiple subjects)
- Format (4): "Remove [specific clothing from image], fully nude. [Breast size]. Detailed breasts and nipples. Detailed skin texture." (13-20 words for single subject)
- Transformation 3 must be a FANTASY/ROLEPLAY costume (choose from the 15 options above)
- Transformation 5 must be AI's CREATIVE CHOICE - revealing/sexy but completely different from bikini/lingerie/fantasy categories (e.g., wet clothes, torn clothes, sports wear, club wear, etc.)
- NO preservation statements
- NO "Do not alter..." phrases

**EXTRACT FROM IMAGE ANALYSIS:**
- **NUMBER OF SUBJECTS:** First, check if 1 person or multiple people. This determines format!
- **CLOTHING** (for EACH subject if multiple): Look for clothing descriptions - e.g., "black sundress", "Subject 1: white tank top and jeans", "Subject 2: blue dress"
  - USE EXACT CLOTHING DESCRIPTION FOR EACH SUBJECT IN ALL 5 PROMPTS!
  - For nude prompt (4): Reference each person's specific clothing
- **Breast size** (for EACH subject): Look for "chest", "bust", "cup size" in the analysis - USE FOR ALL 5 PROMPTS (convert to "breasts" terminology!)

**REMEMBER:**
- **SINGLE SUBJECT:**
  - Prompts 1-2: Replace outfit with **[ULTRA-DETAILED REVEALING bikini/lingerie description: style name + revealing features + what's exposed (12-20 words)]** + breast size + "Detailed skin texture"
  - Prompt 3: Replace outfit with **[ULTRA-DETAILED FANTASY/ROLEPLAY costume from the 15 options above]** + breast size + "Detailed skin texture"
  - Prompt 4: "Remove [exact clothing], fully nude" + breast size + "Detailed breasts and nipples" + "Detailed skin texture"
  - Prompt 5: Replace outfit with **[AI'S CREATIVE CHOICE - revealing/sexy but different from bikini/lingerie/fantasy]** + breast size + "Detailed skin texture"

- **MULTIPLE SUBJECTS:**
  - Use "Subject 1: [transformation]. Subject 2: [transformation]." format for ALL 5 prompts
  - Each subject gets their own: clothing → **ULTRA-DETAILED outfit change with full description** → breast size
  - Give each subject DIFFERENT styles AND colors for prompts 1, 2, 3, and 5, all with FULL detailed descriptions (12-20 words each)
  - For nude prompt (4): Specify each person's clothing removal, then add "Both/All fully nude."

**IMPORTANT:** 
- Prompts 1, 2, 3, and 5 ALL MUST have ULTRA-DETAILED, REVEALING descriptions including:
  - ✅ Specific style name (from the lists above or creative for prompt 5)
  - ✅ Revealing features (sheer, see-through, barely covering, ultra-sheer, tiny, minimal, etc.)
  - ✅ What's exposed/visible (nipples, ass, underboob, cleavage, crotch, areolas, etc.)
  - ✅ Each description must be 12-20 words minimum
- **Prompt 3:** MUST be a fantasy/roleplay costume from the 15 options above
- **Prompt 5:** MUST be AI's creative choice - revealing/sexy but completely different from bikini (1), lingerie (2), and fantasy (3)
  - Examples for prompt 5: wet clothes, torn clothes, sports wear, club wear, body paint, see-through casual wear, etc.
- For multiple subjects, account for ALL people in the image - don't skip anyone!
- **Use the expanded lists above** - 10 bikini styles, 10 lingerie styles, 15 fantasy styles!

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

