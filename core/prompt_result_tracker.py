"""
Prompt Result Tracker
Tracks which prompts produce good/bad results based on user feedback
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict


@dataclass
class PromptResult:
    """Single prompt result with feedback"""
    prompt: str
    timestamp: str
    source: str  # "mild_button", "moderate_button", "undress_button", "manual"
    result_path: Optional[str] = None
    feedback: Optional[str] = None  # "good", "bad", "saved", "deleted", None
    image_description: Optional[str] = None  # AI description of the input image
    metadata: Optional[Dict] = None


class PromptResultTracker:
    """Tracks prompt results and user feedback for learning"""
    
    def __init__(self):
        self.data_dir = Path("data/adaptive_learning")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.results_file = self.data_dir / "prompt_results.jsonl"
        self.stats_file = self.data_dir / "prompt_stats.json"
    
    def track_generation(self, prompt: str, source: str = "manual", metadata: Optional[Dict] = None):
        """Track that a prompt was generated/used"""
        result = PromptResult(
            prompt=prompt,
            timestamp=datetime.now().isoformat(),
            source=source,
            metadata=metadata
        )
        
        self._append_result(result)
        print(f"📊 Tracked prompt generation from {source}")
    
    def track_result_saved(self, prompt: str, result_path: str, metadata: Optional[Dict] = None, image_description: Optional[str] = None):
        """Track that a result was explicitly saved (indicates success)"""
        result = PromptResult(
            prompt=prompt,
            timestamp=datetime.now().isoformat(),
            source=metadata.get('source', 'manual') if metadata else 'manual',
            result_path=result_path,
            feedback="saved",
            image_description=image_description or (metadata.get('image_description') if metadata else None),
            metadata=metadata
        )
        
        self._append_result(result)
        self._update_stats()
        print(f"✅ Tracked prompt success (result saved)")
    
    def track_result_deleted(self, prompt: str, result_path: str, metadata: Optional[Dict] = None, image_description: Optional[str] = None):
        """Track that a result was deleted (indicates failure)"""
        result = PromptResult(
            prompt=prompt,
            timestamp=datetime.now().isoformat(),
            source=metadata.get('source', 'manual') if metadata else 'manual',
            result_path=result_path,
            feedback="deleted",
            image_description=image_description or (metadata.get('image_description') if metadata else None),
            metadata=metadata
        )
        
        self._append_result(result)
        self._update_stats()
        print(f"❌ Tracked prompt failure (result deleted)")
    
    def track_feedback(self, prompt: str, feedback: str, result_path: Optional[str] = None, metadata: Optional[Dict] = None, image_description: Optional[str] = None):
        """Track explicit user feedback (good/bad button click)"""
        result = PromptResult(
            prompt=prompt,
            timestamp=datetime.now().isoformat(),
            source=metadata.get('source', 'manual') if metadata else 'manual',
            result_path=result_path,
            feedback=feedback,
            image_description=image_description or (metadata.get('image_description') if metadata else None),
            metadata=metadata
        )
        
        self._append_result(result)
        self._update_stats()
        print(f"👍/👎 Tracked user feedback: {feedback}")
    
    def get_prompt_stats(self, prompt: str) -> Dict:
        """Get statistics for a specific prompt"""
        results = self._load_all_results()
        
        # Find all results for this prompt (or very similar prompts)
        matching = [r for r in results if self._prompts_match(r.prompt, prompt)]
        
        if not matching:
            return {
                'prompt': prompt,
                'total_uses': 0,
                'successes': 0,
                'failures': 0,
                'success_rate': 0.0
            }
        
        successes = sum(1 for r in matching if r.feedback in ['saved', 'good'])
        failures = sum(1 for r in matching if r.feedback in ['deleted', 'bad'])
        total_feedback = successes + failures
        
        return {
            'prompt': prompt,
            'total_uses': len(matching),
            'successes': successes,
            'failures': failures,
            'success_rate': successes / total_feedback if total_feedback > 0 else 0.0
        }
    
    def get_all_stats(self) -> Dict[str, Dict]:
        """Get statistics for all tracked prompts"""
        results = self._load_all_results()
        
        # Group by prompt (similar prompts grouped together)
        prompt_groups = {}
        
        for result in results:
            # Find matching group
            matched = False
            for base_prompt in prompt_groups.keys():
                if self._prompts_match(result.prompt, base_prompt):
                    prompt_groups[base_prompt].append(result)
                    matched = True
                    break
            
            if not matched:
                prompt_groups[result.prompt] = [result]
        
        # Calculate stats for each group
        stats = {}
        for base_prompt, group_results in prompt_groups.items():
            successes = sum(1 for r in group_results if r.feedback in ['saved', 'good'])
            failures = sum(1 for r in group_results if r.feedback in ['deleted', 'bad'])
            total_feedback = successes + failures
            
            stats[base_prompt] = {
                'prompt': base_prompt,
                'total_uses': len(group_results),
                'successes': successes,
                'failures': failures,
                'success_rate': successes / total_feedback if total_feedback > 0 else 0.0
            }
        
        return stats
    
    def get_successful_prompts(self, min_success_rate: float = 0.7, min_uses: int = 2) -> List[str]:
        """Get prompts with high success rates"""
        stats = self.get_all_stats()
        
        successful = [
            prompt for prompt, data in stats.items()
            if data['success_rate'] >= min_success_rate and data['total_uses'] >= min_uses
        ]
        
        return successful
    
    def get_failed_prompts(self, max_success_rate: float = 0.3, min_uses: int = 2) -> List[str]:
        """Get prompts with low success rates"""
        stats = self.get_all_stats()
        
        failed = [
            prompt for prompt, data in stats.items()
            if data['success_rate'] <= max_success_rate and data['total_uses'] >= min_uses
        ]
        
        return failed
    
    def _append_result(self, result: PromptResult):
        """Append result to JSONL file"""
        try:
            with open(self.results_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(asdict(result), ensure_ascii=False) + '\n')
        except Exception as e:
            print(f"❌ Error appending result: {e}")
    
    def _load_all_results(self) -> List[PromptResult]:
        """Load all results from JSONL file"""
        if not self.results_file.exists():
            return []
        
        results = []
        try:
            with open(self.results_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        results.append(PromptResult(**data))
        except Exception as e:
            print(f"❌ Error loading results: {e}")
        
        return results
    
    def _prompts_match(self, prompt1: str, prompt2: str, threshold: float = 0.9) -> bool:
        """Check if two prompts are similar enough to be considered the same"""
        from difflib import SequenceMatcher
        ratio = SequenceMatcher(None, prompt1.lower(), prompt2.lower()).ratio()
        return ratio >= threshold
    
    def _update_stats(self):
        """Update aggregate statistics file"""
        try:
            stats = self.get_all_stats()
            
            # Calculate overall metrics
            total_prompts = len(stats)
            prompts_with_feedback = sum(1 for s in stats.values() if s['successes'] + s['failures'] > 0)
            avg_success_rate = sum(s['success_rate'] for s in stats.values()) / total_prompts if total_prompts > 0 else 0
            
            summary = {
                'last_updated': datetime.now().isoformat(),
                'total_tracked_prompts': total_prompts,
                'prompts_with_feedback': prompts_with_feedback,
                'average_success_rate': avg_success_rate,
                'top_successful_prompts': sorted(
                    [(p, d['success_rate'], d['total_uses']) for p, d in stats.items() if d['success_rate'] > 0.7],
                    key=lambda x: (x[1], x[2]),
                    reverse=True
                )[:10],
                'top_failed_prompts': sorted(
                    [(p, d['success_rate'], d['total_uses']) for p, d in stats.items() if d['success_rate'] < 0.3],
                    key=lambda x: (x[1], x[2])
                )[:10]
            }
            
            with open(self.stats_file, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"❌ Error updating stats: {e}")
    
    def get_summary(self) -> Dict:
        """Get summary statistics"""
        if not self.stats_file.exists():
            self._update_stats()
        
        try:
            with open(self.stats_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}


# Global instance
_tracker_instance = None

def get_prompt_tracker() -> PromptResultTracker:
    """Get global tracker instance"""
    global _tracker_instance
    if _tracker_instance is None:
        _tracker_instance = PromptResultTracker()
    return _tracker_instance


if __name__ == "__main__":
    # Test the tracker
    print("="*70)
    print("PROMPT RESULT TRACKER TEST")
    print("="*70)
    
    tracker = PromptResultTracker()
    
    # Simulate some tracking
    test_prompt = "Remove white top, replace with red bikini"
    
    tracker.track_generation(test_prompt, source="mild_button")
    tracker.track_result_saved(test_prompt, "result1.png")
    
    tracker.track_generation(test_prompt, source="mild_button")
    tracker.track_result_deleted(test_prompt, "result2.png")
    
    # Get stats
    stats = tracker.get_prompt_stats(test_prompt)
    print(f"\nStats for test prompt:")
    print(f"  Total uses: {stats['total_uses']}")
    print(f"  Successes: {stats['successes']}")
    print(f"  Failures: {stats['failures']}")
    print(f"  Success rate: {stats['success_rate']:.1%}")
    
    # Get summary
    summary = tracker.get_summary()
    print(f"\nOverall summary:")
    print(f"  Total tracked prompts: {summary.get('total_tracked_prompts', 0)}")
    print(f"  Average success rate: {summary.get('average_success_rate', 0):.1%}")
    
    print("\n" + "="*70)

