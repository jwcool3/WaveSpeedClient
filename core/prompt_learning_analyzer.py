"""
AI-Powered Prompt Learning Analyzer
Uses Claude/OpenAI to analyze saved prompts and extract learning patterns
"""

import json
import re
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass
import asyncio


@dataclass
class LearningInsights:
    """AI-generated learning insights from saved prompts"""
    analysis_text: str  # Full AI analysis
    key_patterns: List[str]  # Key patterns identified
    successful_vocabulary: List[str]  # High-success words/phrases
    structural_recommendations: List[str]  # Structure advice
    style_guidance: str  # Style recommendations
    raw_response: str  # Full AI response


class AIPromptLearningAnalyzer:
    """Uses AI to analyze saved prompts and extract patterns"""
    
    def __init__(self):
        self.prompts_file = Path("data/seedream_v4_prompts.json")
        self.cache_file = Path("data/adaptive_learning/ai_learning_insights.json")
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)
    
    def load_saved_prompts(self, limit: int = 100) -> List[str]:
        """Load the last N saved prompts"""
        try:
            if not self.prompts_file.exists():
                print(f"⚠️ Prompts file not found: {self.prompts_file}")
                return []
            
            with open(self.prompts_file, 'r', encoding='utf-8') as f:
                prompts = json.load(f)
            
            # Get last N prompts (most recent)
            if len(prompts) > limit:
                prompts = prompts[-limit:]
            
            print(f"✅ Loaded {len(prompts)} saved prompts for AI analysis")
            return prompts
            
        except Exception as e:
            print(f"❌ Error loading saved prompts: {e}")
            return []
    
    async def analyze_with_ai(self, prompts: List[str], include_feedback: bool = True) -> LearningInsights:
        """Use AI to analyze prompts and extract patterns (optionally with success rate data)"""
        from core.ai_prompt_advisor import get_ai_advisor
        from core.prompt_result_tracker import get_prompt_tracker
        
        if not prompts:
            return self._empty_insights()
        
        print(f"🧠 Sending {len(prompts)} prompts to AI for pattern analysis...")
        
        # Get success rate data if requested
        feedback_data = None
        if include_feedback:
            try:
                tracker = get_prompt_tracker()
                stats = tracker.get_all_stats()
                if stats:
                    # Get prompts with their image descriptions
                    results = tracker._load_all_results()
                    prompt_contexts = {}  # Map prompts to their image descriptions
                    
                    for result in results:
                        if result.feedback in ['saved', 'good'] and result.image_description:
                            if result.prompt not in prompt_contexts:
                                prompt_contexts[result.prompt] = result.image_description
                    
                    feedback_data = {
                        'total_prompts_with_feedback': sum(1 for s in stats.values() if s['successes'] + s['failures'] > 0),
                        'successful_prompts': tracker.get_successful_prompts(min_success_rate=0.7, min_uses=1),
                        'failed_prompts': tracker.get_failed_prompts(max_success_rate=0.3, min_uses=1),
                        'prompt_contexts': prompt_contexts,  # Map of prompt -> image description
                        'summary': tracker.get_summary()
                    }
                    print(f"📊 Including feedback data: {feedback_data['total_prompts_with_feedback']} prompts with user feedback")
                    if prompt_contexts:
                        print(f"🖼️  Including image context for {len(prompt_contexts)} prompts")
            except Exception as e:
                print(f"⚠️ Could not load feedback data: {e}")
        
        # Create analysis prompt
        system_prompt = self._create_analysis_system_prompt()
        user_message = self._create_analysis_user_message(prompts, feedback_data)
        
        # Get AI advisor
        advisor = get_ai_advisor()
        if not advisor.is_available():
            print("❌ AI service not available")
            return self._empty_insights()
        
        # Get AI analysis
        try:
            if advisor.api_provider == "claude" and advisor.claude_api:
                response = await advisor.claude_api.generate_response(system_prompt + "\n\n" + user_message)
            elif advisor.api_provider == "openai" and advisor.openai_api:
                response = await advisor.openai_api.generate_response(system_prompt + "\n\n" + user_message)
            else:
                print("❌ No AI API available")
                return self._empty_insights()
            
            print(f"✅ AI analysis complete ({len(response)} chars)")
            
            # Parse AI response into structured insights
            insights = self._parse_ai_response(response, prompts)
            
            # Cache the insights
            self._cache_insights(insights)
            
            return insights
            
        except Exception as e:
            print(f"❌ Error during AI analysis: {e}")
            return self._empty_insights()
    
    def _create_analysis_system_prompt(self) -> str:
        """Create system prompt for AI analysis"""
        return """You are an expert at analyzing AI image generation prompts to identify successful patterns and best practices.

Your task is to analyze a collection of saved "good" prompts (prompts the user liked enough to save) and extract:
1. Common vocabulary and phrasing that appears frequently
2. Structural patterns (how prompts are organized)
3. Style patterns (direct vs flowery language, technical terms, etc.)
4. Successful techniques for achieving specific results

Focus on ACTIONABLE insights that can be used to generate better prompts in the future.

Output format:

**KEY PATTERNS:**
- [List 5-10 major patterns you notice]

**SUCCESSFUL VOCABULARY:**
- [List 15-20 words/phrases that appear frequently and seem effective]

**STRUCTURAL RECOMMENDATIONS:**
- [List 5-7 structural patterns that work well]

**STYLE GUIDANCE:**
[2-3 paragraphs describing the overall style, tone, and approach of successful prompts]

**SUMMARY:**
[1 paragraph summarizing the most important learnings]

Be specific and actionable. These insights will be used to enhance future AI prompt generation."""
    
    def _create_analysis_user_message(self, prompts: List[str], feedback_data: Optional[Dict] = None) -> str:
        """Create user message with prompts to analyze (optionally with feedback data)"""
        # Sample prompts if too many
        if len(prompts) > 50:
            # Take a diverse sample
            step = len(prompts) // 50
            sample = prompts[::step][:50]
            message = f"Analyze these {len(sample)} representative prompts (sampled from {len(prompts)} total saved prompts):\n\n"
        else:
            sample = prompts
            message = f"Analyze all {len(sample)} saved prompts:\n\n"
        
        # Add prompts with numbering
        for i, prompt in enumerate(sample, 1):
            # Truncate very long prompts
            display_prompt = prompt[:500] + "..." if len(prompt) > 500 else prompt
            message += f"{i}. {display_prompt}\n\n"
        
        # Add feedback data if available
        if feedback_data:
            message += "\n\n--- USER FEEDBACK DATA ---\n"
            message += f"Total prompts with user feedback (👍/👎 or save/delete): {feedback_data['total_prompts_with_feedback']}\n\n"
            
            if feedback_data['successful_prompts']:
                message += f"HIGH SUCCESS PROMPTS ({len(feedback_data['successful_prompts'])} prompts with >70% success rate):\n"
                prompt_contexts = feedback_data.get('prompt_contexts', {})
                for i, prompt in enumerate(feedback_data['successful_prompts'][:10], 1):
                    display = prompt[:200] + "..." if len(prompt) > 200 else prompt
                    message += f"  ✅ Prompt: {display}\n"
                    # Add image context if available
                    if prompt in prompt_contexts:
                        context = prompt_contexts[prompt]
                        context_display = context[:150] + "..." if len(context) > 150 else context
                        message += f"     📸 Image Context: {context_display}\n"
                    message += "\n"
                message += "\n"
            
            if feedback_data['failed_prompts']:
                message += f"LOW SUCCESS PROMPTS ({len(feedback_data['failed_prompts'])} prompts with <30% success rate):\n"
                for i, prompt in enumerate(feedback_data['failed_prompts'][:10], 1):
                    display = prompt[:200] + "..." if len(prompt) > 200 else prompt
                    message += f"  ❌ {display}\n"
                message += "\n"
            
            summary = feedback_data.get('summary', {})
            if summary:
                message += f"Overall Statistics:\n"
                message += f"  • Average success rate: {summary.get('average_success_rate', 0):.1%}\n"
                message += f"  • Total tracked prompts: {summary.get('total_tracked_prompts', 0)}\n\n"
        
        message += "\nExtract the key patterns, vocabulary, structures, and style guidance that make these prompts successful."
        if feedback_data:
            message += " Pay special attention to what differentiates high-success prompts from low-success ones."
            if feedback_data.get('prompt_contexts'):
                message += " The image context shows what was in the original photo - use this to understand why certain prompts worked well (e.g., if the image has 'woman holding phone', successful prompts might mention removing the phone)."
        
        return message
    
    def _parse_ai_response(self, response: str, prompts: List[str]) -> LearningInsights:
        """Parse AI response into structured insights"""
        import re
        
        # Extract sections
        key_patterns = self._extract_section(response, r"\*\*KEY PATTERNS:\*\*", r"\*\*SUCCESSFUL VOCABULARY:\*\*")
        vocabulary = self._extract_section(response, r"\*\*SUCCESSFUL VOCABULARY:\*\*", r"\*\*STRUCTURAL RECOMMENDATIONS:\*\*")
        structural = self._extract_section(response, r"\*\*STRUCTURAL RECOMMENDATIONS:\*\*", r"\*\*STYLE GUIDANCE:\*\*")
        style = self._extract_section(response, r"\*\*STYLE GUIDANCE:\*\*", r"\*\*SUMMARY:\*\*")
        
        # Convert to lists
        key_patterns_list = self._extract_list_items(key_patterns)
        vocabulary_list = self._extract_list_items(vocabulary)
        structural_list = self._extract_list_items(structural)
        
        return LearningInsights(
            analysis_text=response,
            key_patterns=key_patterns_list,
            successful_vocabulary=vocabulary_list,
            structural_recommendations=structural_list,
            style_guidance=style.strip(),
            raw_response=response
        )
    
    def _extract_section(self, text: str, start_pattern: str, end_pattern: str) -> str:
        """Extract text between two patterns"""
        try:
            start_match = re.search(start_pattern, text, re.IGNORECASE)
            end_match = re.search(end_pattern, text, re.IGNORECASE)
            
            if start_match and end_match:
                return text[start_match.end():end_match.start()].strip()
            elif start_match:
                return text[start_match.end():].strip()
            else:
                return ""
        except:
            return ""
    
    def _extract_list_items(self, text: str) -> List[str]:
        """Extract list items (lines starting with - or numbers)"""
        items = []
        for line in text.split('\n'):
            line = line.strip()
            if line.startswith('-') or line.startswith('•'):
                items.append(line[1:].strip())
            elif re.match(r'^\d+\.', line):
                items.append(re.sub(r'^\d+\.\s*', '', line))
        return items
    
    def _cache_insights(self, insights: LearningInsights):
        """Cache insights to file"""
        try:
            cache_data = {
                'analysis_text': insights.analysis_text,
                'key_patterns': insights.key_patterns,
                'successful_vocabulary': insights.successful_vocabulary,
                'structural_recommendations': insights.structural_recommendations,
                'style_guidance': insights.style_guidance,
                'raw_response': insights.raw_response
            }
            
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Cached AI learning insights to {self.cache_file}")
            
        except Exception as e:
            print(f"❌ Error caching insights: {e}")
    
    def load_cached_insights(self) -> Optional[LearningInsights]:
        """Load previously cached AI insights"""
        try:
            if not self.cache_file.exists():
                print("⚠️ No cached AI insights found")
                return None
            
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            insights = LearningInsights(
                analysis_text=cache_data.get('analysis_text', ''),
                key_patterns=cache_data.get('key_patterns', []),
                successful_vocabulary=cache_data.get('successful_vocabulary', []),
                structural_recommendations=cache_data.get('structural_recommendations', []),
                style_guidance=cache_data.get('style_guidance', ''),
                raw_response=cache_data.get('raw_response', '')
            )
            
            print(f"✅ Loaded cached AI insights")
            return insights
            
        except Exception as e:
            print(f"❌ Error loading cached insights: {e}")
            return None
    
    def _empty_insights(self) -> LearningInsights:
        """Return empty insights"""
        return LearningInsights(
            analysis_text="No analysis available",
            key_patterns=[],
            successful_vocabulary=[],
            structural_recommendations=[],
            style_guidance="",
            raw_response=""
        )
    
    def format_insights_for_generation(self, insights: LearningInsights) -> str:
        """Format insights as enhancement text for prompt generation"""
        if not insights.key_patterns and not insights.successful_vocabulary:
            return ""
        
        enhancement = []
        enhancement.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        enhancement.append("🧠 AI LEARNING INSIGHTS (from analyzing your saved successful prompts)")
        enhancement.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        enhancement.append("")
        
        if insights.key_patterns:
            enhancement.append("**KEY SUCCESS PATTERNS:**")
            for pattern in insights.key_patterns[:7]:
                enhancement.append(f"- {pattern}")
            enhancement.append("")
        
        if insights.successful_vocabulary:
            vocab_text = ", ".join(f'"{v}"' for v in insights.successful_vocabulary[:20])
            enhancement.append("**HIGH-SUCCESS VOCABULARY (use these frequently):**")
            enhancement.append(vocab_text)
            enhancement.append("")
        
        if insights.structural_recommendations:
            enhancement.append("**PROVEN STRUCTURAL PATTERNS:**")
            for rec in insights.structural_recommendations[:5]:
                enhancement.append(f"- {rec}")
            enhancement.append("")
        
        if insights.style_guidance:
            enhancement.append("**STYLE GUIDANCE:**")
            enhancement.append(insights.style_guidance[:500])  # Limit length
            enhancement.append("")
        
        enhancement.append("**INSTRUCTION:** Incorporate these learned patterns naturally while still following the template requirements.")
        enhancement.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        
        return "\n".join(enhancement)


# Convenience functions
async def analyze_saved_prompts(limit: int = 100, force_refresh: bool = False) -> LearningInsights:
    """Analyze saved prompts with AI and return insights"""
    analyzer = AIPromptLearningAnalyzer()
    
    # Try to load cached first unless forcing refresh
    if not force_refresh:
        cached = analyzer.load_cached_insights()
        if cached:
            return cached
    
    # Analyze with AI
    prompts = analyzer.load_saved_prompts(limit)
    return await analyzer.analyze_with_ai(prompts)


async def get_learning_insights(force_refresh: bool = False) -> Optional[LearningInsights]:
    """Get AI learning insights (cached or fresh)"""
    analyzer = AIPromptLearningAnalyzer()
    
    if not force_refresh:
        cached = analyzer.load_cached_insights()
        if cached:
            return cached
    
    # Generate new analysis
    print("🧠 Generating fresh AI analysis of saved prompts...")
    prompts = analyzer.load_saved_prompts(100)
    return await analyzer.analyze_with_ai(prompts)


def format_learning_for_generation() -> str:
    """Get formatted learning insights for enhancing prompt generation"""
    analyzer = AIPromptLearningAnalyzer()
    insights = analyzer.load_cached_insights()
    
    if not insights:
        return ""
    
    return analyzer.format_insights_for_generation(insights)


if __name__ == "__main__":
    # Test the analyzer
    print("="*70)
    print("AI PROMPT LEARNING ANALYZER TEST")
    print("="*70)
    
    async def test():
        analyzer = AIPromptLearningAnalyzer()
        
        # Load prompts
        prompts = analyzer.load_saved_prompts(100)
        print(f"\n✅ Loaded {len(prompts)} prompts")
        
        # Analyze with AI
        print("\n🧠 Analyzing with AI...")
        insights = await analyzer.analyze_with_ai(prompts)
        
        # Show results
        print("\n" + "="*70)
        print("AI ANALYSIS RESULTS:")
        print("="*70)
        print(f"\nKey Patterns: {len(insights.key_patterns)}")
        print(f"Vocabulary: {len(insights.successful_vocabulary)}")
        print(f"Structures: {len(insights.structural_recommendations)}")
        
        print("\n" + "="*70)
        print("FORMATTED FOR GENERATION:")
        print("="*70)
        print(analyzer.format_insights_for_generation(insights))
    
    asyncio.run(test())
