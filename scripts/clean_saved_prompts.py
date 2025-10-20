"""
Clean Saved Prompts - Remove Duplicates and Similar Prompts
Keeps the most recent version of similar prompts
"""

import json
import shutil
from pathlib import Path
from datetime import datetime
from difflib import SequenceMatcher


def similarity_ratio(str1: str, str2: str) -> float:
    """Calculate similarity ratio between two strings (0.0 to 1.0)"""
    return SequenceMatcher(None, str1.lower(), str2.lower()).ratio()


def are_similar(prompt1: str, prompt2: str, threshold: float = 0.85) -> bool:
    """Check if two prompts are similar (default 85% similar)"""
    return similarity_ratio(prompt1, prompt2) >= threshold


def clean_prompts(prompts: list, similarity_threshold: float = 0.85) -> list:
    """Remove duplicate and very similar prompts, keeping most recent"""
    if not prompts:
        return []
    
    # Work backwards (most recent first) to keep newer versions
    cleaned = []
    seen_prompts = []
    
    for prompt in reversed(prompts):
        # Check if this prompt is similar to any we've already kept
        is_duplicate = False
        for seen in seen_prompts:
            if are_similar(prompt, seen, similarity_threshold):
                is_duplicate = True
                break
        
        if not is_duplicate:
            cleaned.append(prompt)
            seen_prompts.append(prompt)
    
    # Reverse back to original order
    return list(reversed(cleaned))


def main():
    print("="*70)
    print("🧹 CLEANING SAVED PROMPTS")
    print("="*70)
    print()
    
    prompts_file = Path("data/seedream_v4_prompts.json")
    
    if not prompts_file.exists():
        print("❌ Prompts file not found!")
        return
    
    # 1. Create backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = Path(f"data/seedream_v4_prompts_backup_{timestamp}.json")
    
    print(f"📦 Creating backup...")
    shutil.copy(prompts_file, backup_file)
    print(f"✅ Backup saved: {backup_file.name}")
    print()
    
    # 2. Load prompts
    with open(prompts_file, 'r', encoding='utf-8') as f:
        prompts = json.load(f)
    
    original_count = len(prompts)
    print(f"📊 Original prompts: {original_count}")
    print()
    
    # 3. Show similarity threshold options
    print("🎯 Similarity threshold (how similar = duplicate):")
    print("   0.90 = Very strict (only almost identical prompts)")
    print("   0.85 = Recommended (catches minor edits)")
    print("   0.80 = More aggressive (catches similar variations)")
    print()
    
    threshold_input = input("Enter threshold (0.80-0.95) or press Enter for 0.85: ").strip()
    if threshold_input:
        try:
            threshold = float(threshold_input)
            if not 0.5 <= threshold <= 1.0:
                print("⚠️ Using default 0.85")
                threshold = 0.85
        except:
            print("⚠️ Using default 0.85")
            threshold = 0.85
    else:
        threshold = 0.85
    
    print(f"\n🔍 Using similarity threshold: {threshold:.2f}")
    print()
    
    # 4. Clean prompts
    print("🧹 Removing duplicates and similar prompts...")
    cleaned_prompts = clean_prompts(prompts, threshold)
    
    removed_count = original_count - len(cleaned_prompts)
    print(f"✅ Removed {removed_count} duplicate/similar prompts")
    print(f"📊 Remaining prompts: {len(cleaned_prompts)}")
    print()
    
    # Show some examples of what was removed
    if removed_count > 0:
        print("📝 Examples of removed duplicates:")
        print()
        
        # Find some duplicates to show
        shown = 0
        for i, prompt1 in enumerate(prompts):
            if shown >= 3:
                break
            
            if prompt1 not in cleaned_prompts:
                # Find what it was similar to
                for prompt2 in cleaned_prompts:
                    if are_similar(prompt1, prompt2, threshold):
                        ratio = similarity_ratio(prompt1, prompt2)
                        print(f"   Removed (similarity: {ratio:.1%}):")
                        print(f"   \"{prompt1[:80]}...\"")
                        print(f"   Kept:")
                        print(f"   \"{prompt2[:80]}...\"")
                        print()
                        shown += 1
                        break
    
    # 5. Keep only most recent 100
    if len(cleaned_prompts) > 100:
        print(f"✂️ Keeping only the most recent 100 prompts...")
        cleaned_prompts = cleaned_prompts[-100:]
        print(f"✅ Trimmed to {len(cleaned_prompts)} prompts")
        print()
    
    # 6. Save cleaned version
    with open(prompts_file, 'w', encoding='utf-8') as f:
        json.dump(cleaned_prompts, f, indent=2, ensure_ascii=False)
    
    print("="*70)
    print("✅ CLEANING COMPLETE!")
    print("="*70)
    print(f"📊 Summary:")
    print(f"   • Original: {original_count} prompts")
    print(f"   • Duplicates removed: {removed_count}")
    print(f"   • Final count: {len(cleaned_prompts)} prompts")
    print(f"   • Backup: {backup_file.name}")
    print()
    
    # 7. Offer to re-run analysis
    response = input("🧠 Re-run AI analysis on cleaned prompts? (Y/n): ").lower()
    if response != 'n':
        print()
        print("="*70)
        print("🧠 RUNNING AI ANALYSIS ON CLEANED PROMPTS")
        print("="*70)
        print()
        
        import asyncio
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from core.prompt_learning_analyzer import AIPromptLearningAnalyzer
        
        async def analyze():
            analyzer = AIPromptLearningAnalyzer()
            
            # Load cleaned prompts
            prompts = analyzer.load_saved_prompts(100)
            print(f"✅ Loaded {len(prompts)} cleaned prompts")
            print()
            
            # Analyze with AI
            print("🧠 Analyzing with AI...")
            insights = await analyzer.analyze_with_ai(prompts)
            
            # Show results
            print()
            print("="*70)
            print("✅ ANALYSIS COMPLETE!")
            print("="*70)
            print(f"📊 Insights extracted:")
            print(f"   • Key Patterns: {len(insights.key_patterns)}")
            print(f"   • Successful Vocabulary: {len(insights.successful_vocabulary)}")
            print(f"   • Structural Recommendations: {len(insights.structural_recommendations)}")
            print()
            
            print("✅ Updated learning insights with cleaned prompts!")
            print("   Your Mild/Moderate/Undress buttons now use cleaner patterns!")
        
        asyncio.run(analyze())
    else:
        print()
        print("💡 Run 'python scripts/analyze_saved_prompts.py' later to update learning.")
    
    print()
    print("="*70)


if __name__ == "__main__":
    main()

