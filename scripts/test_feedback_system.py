"""
Test Script for Phase 1 Feedback Tracking System
Tests the complete feedback loop: tracking, storage, and AI learning
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.prompt_result_tracker import PromptResultTracker, get_prompt_tracker


def test_basic_tracking():
    """Test basic prompt tracking"""
    print("\n" + "="*70)
    print("TEST 1: Basic Prompt Tracking")
    print("="*70)
    
    tracker = PromptResultTracker()
    
    # Test tracking generation
    test_prompt = "Remove white shirt, replace with red bikini top, maintain exact pose and body"
    tracker.track_generation(test_prompt, source="mild_button")
    print(f"✅ Tracked generation")
    
    # Test tracking success
    tracker.track_result_saved(test_prompt, "test_result_1.png", {"source": "mild_button"})
    print(f"✅ Tracked successful save")
    
    # Test tracking failure
    tracker.track_result_deleted(test_prompt, "test_result_2.png", {"source": "mild_button"})
    print(f"✅ Tracked deletion (failure)")
    
    # Get stats
    stats = tracker.get_prompt_stats(test_prompt)
    print(f"\n📊 Stats for test prompt:")
    print(f"   Total uses: {stats['total_uses']}")
    print(f"   Successes: {stats['successes']}")
    print(f"   Failures: {stats['failures']}")
    print(f"   Success rate: {stats['success_rate']:.1%}")


def test_feedback_buttons():
    """Test feedback button tracking (good/bad)"""
    print("\n" + "="*70)
    print("TEST 2: Feedback Button Tracking")
    print("="*70)
    
    tracker = get_prompt_tracker()
    
    # Test good feedback
    prompt1 = "Replace outfit with sexy black dress"
    tracker.track_feedback(prompt1, 'good', 'result_good.png')
    print(f"✅ Tracked 👍 feedback")
    
    # Test bad feedback
    prompt2 = "Change to red bikini"
    tracker.track_feedback(prompt2, 'bad', 'result_bad.png')
    print(f"✅ Tracked 👎 feedback")
    
    # Get overall stats
    all_stats = tracker.get_all_stats()
    print(f"\n📊 Total tracked prompts: {len(all_stats)}")


def test_success_detection():
    """Test successful/failed prompt detection"""
    print("\n" + "="*70)
    print("TEST 3: Success Detection")
    print("="*70)
    
    tracker = get_prompt_tracker()
    
    # Create some test data
    good_prompt = "Professional bikini photoshoot style"
    for i in range(3):
        tracker.track_result_saved(good_prompt, f"good_{i}.png")
    
    bad_prompt = "Poorly written test prompt"
    for i in range(3):
        tracker.track_result_deleted(bad_prompt, f"bad_{i}.png")
    
    # Test detection
    successful = tracker.get_successful_prompts(min_success_rate=0.7, min_uses=2)
    failed = tracker.get_failed_prompts(max_success_rate=0.3, min_uses=2)
    
    print(f"✅ High success prompts: {len(successful)}")
    if successful:
        print(f"   Example: {successful[0][:60]}...")
    
    print(f"✅ Low success prompts: {len(failed)}")
    if failed:
        print(f"   Example: {failed[0][:60]}...")


def test_summary_stats():
    """Test summary statistics"""
    print("\n" + "="*70)
    print("TEST 4: Summary Statistics")
    print("="*70)
    
    tracker = get_prompt_tracker()
    summary = tracker.get_summary()
    
    if summary:
        print(f"✅ Summary statistics generated:")
        print(f"   Total tracked prompts: {summary.get('total_tracked_prompts', 0)}")
        print(f"   Prompts with feedback: {summary.get('prompts_with_feedback', 0)}")
        print(f"   Average success rate: {summary.get('average_success_rate', 0):.1%}")
        
        top_successful = summary.get('top_successful_prompts', [])
        if top_successful:
            print(f"\n   Top successful prompt:")
            prompt, rate, uses = top_successful[0]
            print(f"   • {prompt[:60]}...")
            print(f"     Success rate: {rate:.1%}, Uses: {uses}")
    else:
        print(f"⚠️ No summary data yet (need more tracked prompts)")


def test_ai_integration():
    """Test AI learning integration"""
    print("\n" + "="*70)
    print("TEST 5: AI Learning Integration Check")
    print("="*70)
    
    try:
        from core.prompt_learning_analyzer import AIPromptLearningAnalyzer
        from core.prompt_result_tracker import get_prompt_tracker
        
        analyzer = AIPromptLearningAnalyzer()
        tracker = get_prompt_tracker()
        
        # Check if feedback data is available
        stats = tracker.get_all_stats()
        successful = tracker.get_successful_prompts()
        failed = tracker.get_failed_prompts()
        
        print(f"✅ AI Analyzer initialized")
        print(f"✅ Feedback data available:")
        print(f"   • Total prompts tracked: {len(stats)}")
        print(f"   • Successful prompts: {len(successful)}")
        print(f"   • Failed prompts: {len(failed)}")
        
        if len(stats) > 0:
            print(f"\n✅ Ready for AI analysis with feedback data!")
            print(f"   Run: python scripts/analyze_saved_prompts.py")
        else:
            print(f"\n⚠️ No feedback data yet. Use the app to:")
            print(f"   • Generate some images")
            print(f"   • Click 👍/👎 on results")
            print(f"   • Delete unwanted results")
        
    except Exception as e:
        print(f"❌ Error checking AI integration: {e}")


def test_file_creation():
    """Test that data files are created correctly"""
    print("\n" + "="*70)
    print("TEST 6: Data File Creation")
    print("="*70)
    
    from pathlib import Path
    
    tracker = get_prompt_tracker()
    
    # Track something to ensure files are created
    tracker.track_generation("Test prompt for file creation", "test")
    
    data_dir = Path("data/adaptive_learning")
    results_file = data_dir / "prompt_results.jsonl"
    stats_file = data_dir / "prompt_stats.json"
    
    if data_dir.exists():
        print(f"✅ Data directory exists: {data_dir}")
    else:
        print(f"❌ Data directory missing: {data_dir}")
    
    if results_file.exists():
        print(f"✅ Results file exists: {results_file}")
        # Check file size
        size = results_file.stat().st_size
        print(f"   File size: {size} bytes")
    else:
        print(f"❌ Results file missing: {results_file}")
    
    if stats_file.exists():
        print(f"✅ Stats file exists: {stats_file}")
    else:
        print(f"⚠️ Stats file not yet created (will be created after first feedback)")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("PHASE 1 FEEDBACK TRACKING SYSTEM - TEST SUITE")
    print("="*70)
    
    try:
        test_basic_tracking()
        test_feedback_buttons()
        test_success_detection()
        test_summary_stats()
        test_ai_integration()
        test_file_creation()
        
        print("\n" + "="*70)
        print("✅ ALL TESTS COMPLETED!")
        print("="*70)
        print("\nNext steps:")
        print("1. Launch the app: python main.py")
        print("2. Generate some images using the Mild/Moderate/Undress buttons")
        print("3. Click 👍/👎 on results in the Recent Results panel")
        print("4. Run AI analysis: python scripts/analyze_saved_prompts.py")
        print("5. Generate new prompts - they'll be enhanced with learning!")
        print("\n" + "="*70)
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()

