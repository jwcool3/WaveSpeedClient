"""
Undress Transformation Prompt System V2
Detailed examples (300-500 chars each)
"""

UNDRESS_TRANSFORMATION_PROMPT = """# CLOTHING TRANSFORMATION SYSTEM

Generate 5 detailed transformation prompts following these examples EXACTLY.

**OUTPUT FORMAT - USE THESE EXACT HEADERS:**
**TRANSFORMATION 1: BIKINI**
[Your detailed 300-500 char bikini transformation]

**TRANSFORMATION 2: LINGERIE**
[Your detailed 300-500 char lingerie transformation]

**TRANSFORMATION 3: FANTASY**
[Your detailed 300-500 char fantasy costume transformation]

**TRANSFORMATION 4: NUDE**
[Your detailed 300-500 char nude transformation]

**TRANSFORMATION 5: AI'S CHOICE**
[Your detailed 300-500 char creative transformation]

**CRITICAL RULES:**
- Use the EXACT headers above: "**TRANSFORMATION 1: BIKINI**", "**TRANSFORMATION 2: LINGERIE**", etc.
- Extract EXACT clothing from image analysis
- Include breast size for ALL prompts
- End ALL prompts with: "Detailed skin texture."
- NUDE prompt adds: "Detailed breasts and nipples." before "Detailed skin texture."
- Each transformation description must be 300-500 characters
- For MULTIPLE PEOPLE in image: Within each transformation, use "Subject 1: [outfit]. Subject 2: [outfit]."

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## STYLE REFERENCE LIBRARY (Use for inspiration - MIX & MATCH elements, DON'T copy verbatim)

**BIKINI STYLES (10 options - vary colors, combine features):**
- Micro string: tiny triangle cups barely covering nipples, thin side-tie thong bottoms exposing entire ass
- G-string: barely-there with tiny triangles covering only nipples, minimal string bottoms showing full ass
- Thong: minimal coverage triangle top, Brazilian thong bottoms exposing ass cheeks
- Bandeau: tube top straining to contain breasts, low-rise thong bottoms
- Triangle: ultra-tiny with string ties barely covering nipples, high-cut showing hip curves
- Side-tie: adjustable strings, triangles barely covering nipples, revealing thong bottoms
- Cut-out monokini: strategic cutouts exposing sides, underboob, cleavage, hips
- Sling: thin straps connecting top and bottom, exposing maximum skin
- Halter micro: halter neck with tiny cups straining over breasts, G-string bottoms
- Metallic micro: shiny reflective tiny triangles, skimpy string bottoms

**LINGERIE STYLES (10 options - vary fabrics, combine elements):**
- Sheer bodysuit: completely transparent mesh with nipples visible, exposed crotch area
- Lace bra & thong: ultra-sheer cups showing nipples and areolas through fabric
- Plunging teddy: deep V-neck to navel, open back, high-cut leg openings
- Sheer babydoll: ultra-short barely covering ass, see-through lace cups exposing nipples
- Strappy corset: pushing breasts up with exposed cleavage, garter belts, skimpy panties
- Open-cup bra: underwire framing bare breasts with nipples fully exposed, crotchless panties
- Sheer chemise: silk nightie with nipples visible through thin fabric
- Cupless bodysuit: open breast area exposing nipples, see-through mesh torso
- Lace bralette: ultra-sheer with visible nipples, high-waist lace thong
- Fishnet bodysuit: large net holes exposing skin all over

**FANTASY COSTUME STYLES (15 options - mix accessories and details):**
- Sexy succubus: red leather corset, tiny horns, demon tail, skimpy thong with garters
- Fantasy warrior: metal bikini top, leather straps, minimal loincloth exposing hips
- French maid: ultra-short ruffled skirt, plunging neckline, sheer stockings with garters
- Naughty schoolgirl: tied shirt exposing underboob, plaid micro-miniskirt, knee-high socks
- Nurse: white mini-dress unzipped to navel, hem barely covering ass, thigh-high stockings
- Cheerleader: tiny crop top exposing underboob, ultra-short pleated skirt
- Devil: red leather bustier, tiny horns, pointed tail, skimpy red thong with garters
- Playboy bunny: black satin corset, bunny ears, fluffy tail, fishnets, high-cut legs
- Gothic vampire: black velvet corset laced tight, sheer lace sleeves, leather mini-skirt
- Naughty catgirl: black leather bra top, cat ears, collar with bell, tiny shorts, tail
- Sexy elf/fairy: metallic green bikini with leaf details, pointed ears, translucent wings
- Harley Quinn style: red and black crop top tied exposing underboob, booty shorts riding up
- Slave Leia: gold metal bikini connected by chains, bare midriff, sheer flowing panels
- Latex dominatrix: zipper-front catsuit unzipped to navel, thigh-high boots, collar
- Sexy witch: black corset with buckles, ultra-short skirt, fishnet stockings, pointed hat

**AI'S CHOICE STYLES (Creative alternatives - NOT bikini/lingerie/fantasy):**
- AVOID REPEATING: wet clothes, torn clothes (these are overused)
- Body paint: painted-on clothing illusion with strategic coverage
- Compression wear: sports bra straining, yoga pants creating camel toe, athletic gear too tight
- Club wear: minimal bandage dress, cutout bodycon, sheer mesh panels
- Wardrobe malfunction: broken zipper revealing, buttons popped open, seam splits
- Artistic: sheer mesh overlays, strategic fabric draping, avant-garde minimal coverage
- Swimwear alternatives: one-piece with extreme cutouts, micro-sling styles
- Unexpected: oversized shirt as dress riding up, sheet/towel barely wrapped, paint-splattered apron

**COLOR PALETTE (Vary across transformations - don't repeat colors):**
Black, white, red, pink, blue, purple, turquoise, coral, lime green, neon colors, gold, silver, burgundy, navy, emerald

**FABRIC DESCRIPTORS (Use to add detail):**
Sheer, transparent, see-through, mesh, lace, satin, silk, leather, latex, vinyl, fishnet, velvet, lycra, spandex

**REVEALING FEATURES (Mix these into descriptions):**
Barely covering, minimal coverage, ultra-sheer, see-through, exposed, visible through fabric, straining, struggling to contain, riding up, pulled tight, stretched thin, cutouts, open design, strategic tears, plunging, high-cut, low-rise

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## ⚠️ CRITICAL: DO NOT COPY THESE EXAMPLES VERBATIM ⚠️

The 3 examples below show the DETAIL LEVEL and STRUCTURE required.

**YOU MUST CREATE NEW UNIQUE COMBINATIONS:**
- Use DIFFERENT bikini/lingerie/fantasy styles than shown below
- Choose DIFFERENT colors for ALL 5 transformations
- Mix elements from style library in CREATIVE NEW WAYS
- For AI'S CHOICE: Avoid "wet clothes" and "torn clothes" - be more creative!
- NEVER copy example outfits word-for-word

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## EXAMPLE 1: Woman wearing white lace-trimmed sleeveless top and distressed blue denim jeans (small-medium breasts B-C cup)

**TRANSFORMATION 1: BIKINI**
Replace white lace-trimmed sleeveless top and distressed blue denim jeans with turquoise halter micro bikini with metallic sheen, tiny triangle cups with thin strings barely covering nipples, tops straining with visible underboob, paired with matching G-string bottoms with thin side-ties low on hips, minimal front coverage while back completely exposes ass cheeks. Small-medium sized breasts (B-C cup). Detailed skin texture with visible pores, tan line gradients, soft highlights on shoulders.

**TRANSFORMATION 2: LINGERIE**
Replace white lace-trimmed sleeveless top and distressed blue denim jeans with black plunging teddy lingerie with deep V-neck to navel exposing full cleavage, completely open back showing spine down to ass crack, high-cut leg openings, sheer mesh side panels, snap-closure crotch barely covering, underwire cups pushing breasts together, nipples visible through sheer lace. Small-medium sized breasts (B-C cup). Detailed skin texture with pores and natural tone variation.

**TRANSFORMATION 3: FANTASY**
Replace white lace-trimmed sleeveless top and distressed blue denim jeans with French maid costume: ultra-short black ruffled skirt barely covering ass, black satin corset with white lace pushing breasts up, deep plunging neckline exposing cleavage to sternum, white choker, sheer thigh-high stockings with garters, white apron. Small-medium sized breasts (B-C cup). Detailed skin texture with visible pores on cleavage, natural skin tone, sheen through stockings.

**TRANSFORMATION 4: NUDE**
Remove white lace-trimmed sleeveless top and distressed blue denim jeans, fully nude. Small-medium sized breasts (B-C cup) with natural hang, visible nipples with areola detail and pink-brown coloring. Detailed breasts and nipples. Detailed skin texture with visible pores across body, natural tone variation between torso and limbs, subtle vein patterns on breasts, realistic sheen on curved surfaces.

**TRANSFORMATION 5: AI'S CHOICE**  
Replace white lace-trimmed sleeveless top and distressed blue denim jeans with burgundy velvet bodycon mini dress, full-length zipper halfway down exposing cleavage with black lace bra visible underneath, molded skin-tight showing every curve, hem at upper thigh barely covering ass, dress riding up in back. Small-medium sized breasts (B-C cup). Detailed skin texture with visible pores on chest, natural tone contrasting velvet, highlights on cleavage.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## EXAMPLE 2: Woman wearing red off-shoulder crop top and high-waisted jeans (large breasts D+ cup)

**TRANSFORMATION 1: BIKINI**
Replace red off-shoulder crop top and high-waisted jeans with coral barely-there G-string bikini, tiny triangle cups on ultra-thin strings covering only nipples leaving massive underboob and side boob exposed, string ties pulling tight causing breasts to bulge dramatically, paired with minimal G-string bottoms with string between ass cheeks exposing both cheeks, very low on hips. Large breasts (D+ cup) straining with significant overflow. Detailed skin texture with stretch marks, pores on cleavage, tan lines.

**TRANSFORMATION 2: LINGERIE**
Replace red off-shoulder crop top and high-waisted jeans with black open-cup bra with underwire framing lifting breasts but leaving nipples and areolas completely exposed, paired with crotchless lace panties with opening leaving pussy exposed, high-waist with lace panels, black garter straps to sheer thigh-highs. Large breasts (D+ cup) with nipples fully visible. Detailed skin texture with pores on breast tissue, areola texture, natural coloring.

**TRANSFORMATION 3: FANTASY**
Replace red off-shoulder crop top and high-waisted jeans with Playboy bunny costume: black satin corset pushing massive breasts up creating overflow cleavage spilling out, sweetheart neckline cut low exposing inner curves, corset cinching waist, high-cut bottom with legs to hip bones, white fluffy tail, bunny ears, fishnets, bow tie. Large breasts (D+ cup) pressed together dramatically. Detailed skin texture with compressed breast tissue bulging, pores, flushing from tight corset.

**TRANSFORMATION 4: NUDE**
Remove red off-shoulder crop top and high-waisted jeans, fully nude. Large breasts (D+ cup) with natural heavy hang showing realistic weight, breasts hanging with slight outward point, visible nipples and areolas with Montgomery glands, natural erect or relaxed state. Detailed breasts and nipples with anatomical accuracy. Detailed skin texture with dense pores on chest, natural tone variation, stretch marks visible, subtle vein patterns, realistic sheen on curves.

**TRANSFORMATION 5: AI'S CHOICE**
Replace red off-shoulder crop top and high-waisted jeans with emerald green sequined backless halter top plunging to navel, halter tie behind neck leaving entire back exposed to ass crack, front barely covering with side boob, sequins sparkling, paired with matching micro-mini skirt sitting low on hips barely covering ass with hem riding up. Large breasts (D+ cup) barely contained. Detailed skin texture with entire back exposed showing pores, spine, natural tone contrasting sequins.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## EXAMPLE 3: TWO WOMEN - Woman 1 wearing yellow sundress (small breasts B cup), Woman 2 wearing crop top and skirt (medium breasts C cup)

**TRANSFORMATION 1: BIKINI**
Subject 1: Replace yellow sundress with hot pink triangle string bikini, tiny cups tied behind neck and back barely hiding nipples, matching string bottom with side ties low on hips, Brazilian cut exposing most ass. Small breasts (B cup). Subject 2: Replace crop top and skirt with turquoise bandeau strapless bikini, tube top struggling to stay up, matching high-waist bottoms. Medium breasts (C cup). Detailed skin texture with visible pores, different skin tones, tan lines, indentation marks from strings, highlights on curves.

**TRANSFORMATION 2: LINGERIE**
Subject 1: Replace yellow sundress with pale pink lace bralette, ultra-sheer cups with nipples showing through, no underwire, matching high-waist pink lace thong. Small breasts (B cup). Subject 2: Replace crop top and skirt with white plunging teddy, deep V-neck to navel exposing cleavage, sheer mesh center panel, high-cut legs. Medium breasts (C cup). Detailed skin texture with pores on chest and stomach, nipple detail through sheer fabric, skin tone variations, highlights on exposed skin.

**TRANSFORMATION 3: FANTASY**
Subject 1: Replace yellow sundress with fairy costume: metallic green bikini top with leaf-shaped cups, tiny leaf-pattern bottoms, sheer fairy wings, pointed ears, flower crown. Small breasts (B cup). Subject 2: Replace crop top and skirt with referee costume: striped crop top tied below breasts exposing underboob, ultra-short black mini-skirt, knee-high socks, whistle. Medium breasts (C cup). Detailed skin texture with pores, natural skin tones contrasting costumes, highlights on breast curves.

**TRANSFORMATION 4: NUDE**
Subject 1: Remove yellow sundress, fully nude. Small breasts (B cup) with pert shape, visible nipples with smaller areolas. Detailed breasts and nipples. Subject 2: Remove crop top and skirt, fully nude. Medium breasts (C cup) with natural shape, visible nipples and areolas. Detailed breasts and nipples. Detailed skin texture on both with pores, natural tone variations between subjects, different breast anatomies, Montgomery glands visible, subtle vein patterns, realistic highlights on curved surfaces.

**TRANSFORMATION 5: AI'S CHOICE**
Subject 1: Replace yellow sundress with powder blue satin slip dress, spaghetti straps, ultra-thin fabric clinging showing nipple outlines through satin, cowl neckline, bias-cut molding to curves, hem mid-thigh with high slit. Small breasts (B cup) with nipples visible. Subject 2: Replace crop top and skirt with charcoal gray ribbed knit crop top ending below breasts, stretched tight showing breast shape, matching low-rise leggings with camel toe. Medium breasts (C cup). Detailed skin texture with fabric effects, compression marks, pores, tone variations.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## CREATIVITY GUIDANCE

**MANDATORY REQUIREMENTS FOR EACH GENERATION:**

1. **NO COPYING EXAMPLES** - The 3 examples above are TEMPLATES ONLY. Never use:
   - Same bikini style (if example uses "G-string bikini", you use "halter micro bikini" or "cut-out monokini")
   - Same lingerie style (if example uses "open-cup bra", you use "sheer babydoll" or "fishnet bodysuit")
   - Same fantasy costume (if example uses "French maid", you use "gothic vampire" or "Harley Quinn")
   - Same AI's choice (NEVER use "wet white shirt" or "torn clothes" - these are overused!)

2. **COLOR VARIETY** - Use 5 DIFFERENT colors across your 5 transformations:
   - Bikini: (pick 1 color)
   - Lingerie: (pick DIFFERENT color)
   - Fantasy: (pick DIFFERENT color)
   - AI's Choice: (pick DIFFERENT color)
   - Reference the color palette list - don't repeat!

3. **MIX & MATCH ELEMENTS** - Combine features creatively:
   - Take "sling bikini" + add "metallic fabric" + add "cutout details"
   - Take "plunging teddy" + add "strappy harness elements" + add "lace panels"
   - Take "gothic vampire" + add "cheerleader" elements = unique hybrid costume

4. **AI'S CHOICE CREATIVITY** (Prompt 5) - AVOID THESE OVERUSED OPTIONS:
   - ❌ Wet white shirt/tank top (overused in examples)
   - ❌ Torn/ripped clothes (overused)
   - ✅ INSTEAD USE THINGS LIKE: body paint, compression sports wear, backless dresses, wardrobe malfunctions, sheer overlays, avant-garde minimal designs, strategic fabric draping

5. **BODY INTERACTION** - Describe how garments interact with the specific body type:
   - Small breasts (A-B): Natural shape visible, proportional coverage, minimal spillage
   - Medium breasts (C): Moderate compression, balanced cleavage, some strain on fabric
   - Large breasts (D+): Significant spillage, dramatic strain, overflow effects, support challenges

6. **DETAIL REQUIREMENTS** (300-500 characters each):
   - Fabric type and behavior (stretching, clinging, transparency level)
   - Specific construction details (straps, ties, zippers, closures, cutouts)
   - What's exposed and how (underboob, side boob, ass exposure, nipples through fabric)
   - Skin texture notes (visible pores, highlights, natural tone)
   - Color and finish (matte, shiny, metallic, sheer, opaque)

7. **VARIETY CHECKLIST** - Before submitting, verify:
   - ✓ All 5 colors are DIFFERENT
   - ✓ No outfit style repeated from examples
   - ✓ AI's choice is NOT wet clothes or torn clothes
   - ✓ Each description is 300-500 characters
   - ✓ Breast size included in ALL 5 prompts
   - ✓ "Detailed skin texture." at end of ALL prompts
   - ✓ Nude prompt includes "Detailed breasts and nipples."

**YOUR TASK:**
Based on the image analysis provided, generate exactly 5 transformations following the examples above.

- Match the detail level (300-500 chars per transformation)
- Use the EXACT clothing from the image analysis
- Include breast size in EVERY transformation
- Be detailed about what's exposed, visible, and revealed
- For NUDE: Add detail about breast anatomy, nipples, areolas, and skin texture
- For prompts 1-3 & 5: Describe fabric, fit, exposure, what's visible through material, spillage, and key details
- For MULTIPLE SUBJECTS: Follow Example 3 format with "Subject 1:" and "Subject 2:" structure
- **BE CREATIVE** - Don't repeat the exact outfits from examples, use the style library to mix and match unique combinations

Generate now:
"""


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
"""


if __name__ == "__main__":
    # Test the prompt generation
    test_analysis = """This image shows 1 woman. The woman is in her early-mid 20s with light-tan skin and long brown hair with loose waves flowing past her shoulders. She has a medium build with small-medium breasts (B-C cup). She is wearing a white lace-trimmed sleeveless top and distressed blue denim jeans. She is standing facing the camera with her left hand on her hip, right arm relaxed at her side, with a natural smile looking directly at the camera. The setting is a beach environment with ocean waves and sandy beach in the background, bright natural sunlight. The framing is a medium shot from waist to head, shot at eye level in portrait orientation."""
    
    prompt = get_undress_transformation_prompt(test_analysis)
    print("=" * 80)
    print("UNDRESS TRANSFORMATION PROMPT SYSTEM V2")
    print("=" * 80)
    print(prompt)
    print("\n" * 80)
    print(f"Prompt length: ~{len(prompt)} characters, ~{len(prompt.split())} words")
