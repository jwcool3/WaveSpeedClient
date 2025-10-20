"""
Analyze Saved Prompts with AI
Runs AI analysis on saved prompts and caches insights for future use
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.prompt_learning_analyzer import AIPromptLearningAnalyzer


async def main():
    print("="*70)
    print("🧠 AI PROMPT LEARNING ANALYZER")
    print("="*70)
    print()
    
    analyzer = AIPromptLearningAnalyzer()
    
    # Check for existing cache
    cached = analyzer.load_cached_insights()
    if cached:
        print("📦 Found existing cached analysis!")
        print(f"   Analyzed prompts: {len(cached.key_patterns) + len(cached.successful_vocabulary)} insights")
        print()
        
        response = input("🔄 Run fresh analysis? (y/N): ").lower()
        if response != 'y':
            print("\n✅ Using cached analysis. Run with 'y' to refresh.")
            print("\n" + "="*70)
            print("CACHED INSIGHTS PREVIEW:")
            print("="*70)
            print(analyzer.format_insights_for_generation(cached)[:800] + "...")
            return
    
    # Load prompts
    print("📂 Loading saved prompts...")
    prompts = analyzer.load_saved_prompts(100)
    
    if not prompts:
        print("❌ No saved prompts found!")
        print("   Save some prompts first, then run this analysis.")
        return
    
    print(f"✅ Loaded {len(prompts)} saved prompts")
    print()
    
    # Show sample
    print("📝 Sample prompts:")
    for i, prompt in enumerate(prompts[:3], 1):
        preview = prompt[:100] + "..." if len(prompt) > 100 else prompt
        print(f"   {i}. {preview}")
    print(f"   ... and {len(prompts) - 3} more")
    print()
    
    # Analyze with AI
    print("🧠 Analyzing with AI (this may take 30-60 seconds)...")
    print("   Sending prompts to Claude/OpenAI for pattern analysis...")
    print()
    
    insights = await analyzer.analyze_with_ai(prompts)
    
    if not insights.key_patterns and not insights.successful_vocabulary:
        print("❌ Analysis failed or returned no insights")
        return
    
    # Show results
    print("="*70)
    print("✅ ANALYSIS COMPLETE!")
    print("="*70)
    print()
    print(f"📊 Insights extracted:")
    print(f"   • Key Patterns: {len(insights.key_patterns)}")
    print(f"   • Successful Vocabulary: {len(insights.successful_vocabulary)}")
    print(f"   • Structural Recommendations: {len(insights.structural_recommendations)}")
    print()
    
    print("="*70)
    print("KEY PATTERNS IDENTIFIED:")
    print("="*70)
    for i, pattern in enumerate(insights.key_patterns[:10], 1):
        print(f"{i}. {pattern}")
    print()
    
    print("="*70)
    print("SUCCESSFUL VOCABULARY:")
    print("="*70)
    vocab_preview = ", ".join(f'"{v}"' for v in insights.successful_vocabulary[:20])
    print(vocab_preview)
    print()
    
    if insights.style_guidance:
        print("="*70)
        print("STYLE GUIDANCE:")
        print("="*70)
        print(insights.style_guidance[:400] + "...")
        print()
    
    print("="*70)
    print("✅ INSIGHTS CACHED!")
    print("="*70)
    print(f"📁 Saved to: {analyzer.cache_file}")
    print()
    print("💡 These insights will now be automatically used to enhance")
    print("   future prompt generation from your Mild/Moderate/Undress buttons!")
    print()
    print("🔄 To refresh the analysis, run this script again anytime.")
    print("="*70)


if __name__ == "__main__":
    asyncio.run(main())

