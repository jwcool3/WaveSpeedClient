"""
Learning Integration Manager
Integrates the Adaptive Filter Learning System with existing components for seamless learning workflow
"""

import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

from core.adaptive_filter_learning_system import adaptive_learning_system, analyze_and_improve_patterns
from core.enhanced_prompt_tracker import enhanced_prompt_tracker, PromptQuality, FailureReason
from core.enhanced_filter_training_system import enhanced_filter_analyzer
from core.ai_prompt_advisor import AIPromptAdvisor
from core.logger import get_logger

logger = get_logger()

class LearningIntegrationManager:
    """Manages integration between adaptive learning and existing filter training systems"""
    
    def __init__(self):
        self.learning_active = True
        self.auto_improvement_enabled = True
        self.analysis_cache = {}
        self.last_analysis_time = None
        
    async def integrate_with_prompt_tracking(self, prompt_data: Dict) -> Dict:
        """
        Integration point when prompts are saved/tracked
        Automatically feeds data to learning system and generates insights
        """
        try:
            # Extract data for learning system
            quality = prompt_data.get("quality", PromptQuality.AVERAGE)
            failure_reason = prompt_data.get("failure_reason")
            prompt_text = prompt_data.get("prompt", "")
            image_analysis = prompt_data.get("image_analysis", {})
            
            # Determine if this was successful or failed
            is_successful = quality in [PromptQuality.EXCELLENT, PromptQuality.GOOD]
            
            # Feed to adaptive learning system
            learning_entry = {
                "prompt": prompt_text,
                "timestamp": datetime.now().isoformat(),
                "successful": is_successful,
                "quality_rating": quality.value if hasattr(quality, 'value') else quality,
                "failure_reason": failure_reason.value if failure_reason and hasattr(failure_reason, 'value') else failure_reason,
                "image_analysis": image_analysis,
                "detected_techniques": self._extract_techniques_from_prompt(prompt_text)
            }
            
            # Store in enhanced filter analyzer for pattern analysis
            if is_successful:
                enhanced_filter_analyzer._store_successful_bypass(learning_entry)
            else:
                enhanced_filter_analyzer._store_caught_attempt(learning_entry)
            
            # Generate immediate insights if enough data available
            insights = await self._generate_immediate_insights(learning_entry)
            
            return {
                "learning_integrated": True,
                "immediate_insights": insights,
                "suggestions": await self._generate_improvement_suggestions(prompt_text, is_successful)
            }
            
        except Exception as e:
            logger.error(f"Error in learning integration: {e}")
            return {"learning_integrated": False, "error": str(e)}
    
    async def trigger_comprehensive_analysis(self, force_refresh: bool = False) -> Dict:
        """
        Trigger a comprehensive analysis of all collected data
        Returns insights and improved prompt suggestions
        """
        try:
            # Check if we need to refresh analysis
            if not force_refresh and self._is_analysis_cache_valid():
                return self.analysis_cache
            
            logger.info("Starting comprehensive learning analysis...")
            
            # Run the adaptive learning analysis
            analysis_results = await analyze_and_improve_patterns()
            
            # Generate actionable recommendations
            recommendations = await self._generate_actionable_recommendations(analysis_results)
            
            # Cache results
            self.analysis_cache = {
                "timestamp": datetime.now().isoformat(),
                "analysis_results": analysis_results,
                "recommendations": recommendations,
                "summary": self._generate_analysis_summary(analysis_results)
            }
            self.last_analysis_time = datetime.now()
            
            return self.analysis_cache
            
        except Exception as e:
            logger.error(f"Error in comprehensive analysis: {e}")
            return {"error": str(e)}
    
    async def get_smart_prompt_improvements(self, base_prompt: str, context: Dict = None) -> List[str]:
        """
        Get smart improvements for a given prompt based on learned patterns
        """
        try:
            # Get latest analysis data
            if not self.analysis_cache or not self._is_analysis_cache_valid():
                await self.trigger_comprehensive_analysis()
            
            # Generate improved versions
            analysis_data = self.analysis_cache.get("analysis_results", {})
            improved_prompts = adaptive_learning_system.generate_improved_prompts(base_prompt, analysis_data)
            
            # Add context-aware improvements if context provided
            if context:
                contextual_improvements = await self._generate_contextual_improvements(base_prompt, context, analysis_data)
                improved_prompts.extend(contextual_improvements)
            
            # Remove duplicates and return top 5
            unique_improvements = list(dict.fromkeys(improved_prompts))
            return unique_improvements[:5]
            
        except Exception as e:
            logger.error(f"Error generating smart improvements: {e}")
            return [base_prompt]  # Return original if error
    
    async def get_real_time_feedback(self, prompt: str) -> Dict:
        """
        Provide real-time feedback on a prompt before it's used
        """
        try:
            feedback = {
                "risk_assessment": "medium",
                "success_probability": 0.5,
                "suggestions": [],
                "detected_patterns": [],
                "recommended_changes": []
            }
            
            # Analyze prompt against known patterns
            if self.analysis_cache:
                word_patterns = self.analysis_cache.get("analysis_results", {}).get("word_patterns", {})
                
                # Check for low-success words
                prompt_words = adaptive_learning_system._extract_key_words(prompt.lower())
                risky_words = []
                good_words = []
                
                for word in prompt_words:
                    if word in word_patterns:
                        analysis = word_patterns[word]
                        if analysis.success_rate < 0.3:
                            risky_words.append({
                                "word": word,
                                "success_rate": analysis.success_rate,
                                "alternatives": analysis.synonyms[:3]
                            })
                        elif analysis.success_rate > 0.7:
                            good_words.append(word)
                
                # Calculate success probability
                if prompt_words:
                    avg_success_rate = sum(
                        word_patterns.get(word, type('', (), {'success_rate': 0.5})).success_rate 
                        for word in prompt_words
                    ) / len(prompt_words)
                    feedback["success_probability"] = avg_success_rate
                
                # Generate suggestions
                if risky_words:
                    feedback["suggestions"].append(f"Consider replacing risky words: {[w['word'] for w in risky_words[:3]]}")
                    feedback["recommended_changes"] = risky_words
                
                if good_words:
                    feedback["suggestions"].append(f"Good high-success words detected: {good_words[:3]}")
                
                feedback["detected_patterns"] = prompt_words
                feedback["risk_assessment"] = "high" if len(risky_words) > 2 else "low" if not risky_words else "medium"
            
            return feedback
            
        except Exception as e:
            logger.error(f"Error in real-time feedback: {e}")
            return {"error": str(e)}
    
    def _extract_techniques_from_prompt(self, prompt: str) -> List[str]:
        """Extract bypass techniques from a prompt"""
        techniques = []
        prompt_lower = prompt.lower()
        
        # Define technique patterns
        technique_patterns = {
            "euphemism_use": ["intimate", "delicate", "barely-there", "minimal coverage"],
            "technical_language": ["remove upper garment", "unclothed torso", "sans attire"],
            "identity_preservation": ["keep face", "preserve expression", "maintain hairstyle", "identical"],
            "realism_emphasis": ["seamless", "natural", "realistic", "blend", "smooth"],
            "specific_targeting": ["blonde", "brunette", "specific clothing", "blue dress"],
            "gradual_modification": ["step by step", "gradually", "slowly remove"],
            "context_framing": ["for art purposes", "fashion design", "medical illustration"]
        }
        
        for technique, patterns in technique_patterns.items():
            if any(pattern in prompt_lower for pattern in patterns):
                techniques.append(technique)
        
        return techniques
    
    async def _generate_immediate_insights(self, learning_entry: Dict) -> List[str]:
        """Generate immediate insights from a single prompt entry"""
        insights = []
        
        try:
            prompt = learning_entry.get("prompt", "")
            successful = learning_entry.get("successful", False)
            techniques = learning_entry.get("detected_techniques", [])
            
            # Quick pattern analysis
            if successful and techniques:
                insights.append(f"✅ Successful techniques used: {', '.join(techniques[:3])}")
            elif not successful and techniques:
                insights.append(f"❌ Failed despite using: {', '.join(techniques[:3])}")
            
            # Word analysis
            key_words = adaptive_learning_system._extract_key_words(prompt.lower())
            if key_words:
                if successful:
                    insights.append(f"🎯 Effective words: {', '.join(key_words[:3])}")
                else:
                    insights.append(f"⚠️ Potentially problematic words: {', '.join(key_words[:3])}")
            
        except Exception as e:
            logger.error(f"Error generating immediate insights: {e}")
        
        return insights
    
    async def _generate_improvement_suggestions(self, prompt: str, successful: bool) -> List[str]:
        """Generate immediate improvement suggestions for a prompt"""
        suggestions = []
        
        try:
            if not successful:
                # Suggest alternatives for failed prompts
                key_words = adaptive_learning_system._extract_key_words(prompt.lower())
                
                for word in key_words[:3]:
                    synonyms = adaptive_learning_system._generate_synonyms(word)
                    euphemisms = adaptive_learning_system._generate_euphemisms(word)
                    
                    if synonyms or euphemisms:
                        alternatives = (synonyms + euphemisms)[:3]
                        suggestions.append(f"Try alternatives to '{word}': {', '.join(alternatives)}")
                
                # Suggest technique additions
                techniques = self._extract_techniques_from_prompt(prompt)
                missing_techniques = [
                    "identity_preservation", "realism_emphasis", "euphemism_use"
                ]
                missing = [t for t in missing_techniques if t not in techniques]
                if missing:
                    suggestions.append(f"Consider adding techniques: {', '.join(missing[:2])}")
            
        except Exception as e:
            logger.error(f"Error generating improvement suggestions: {e}")
        
        return suggestions
    
    async def _generate_actionable_recommendations(self, analysis_results: Dict) -> List[Dict]:
        """Generate actionable recommendations from comprehensive analysis"""
        recommendations = []
        
        try:
            # Word-based recommendations
            word_patterns = analysis_results.get("word_patterns", {})
            for word, analysis in word_patterns.items():
                if analysis.success_rate < 0.3 and analysis.synonyms:
                    recommendations.append({
                        "type": "word_substitution",
                        "priority": "high",
                        "action": f"Replace '{word}' with alternatives: {', '.join(analysis.synonyms[:3])}",
                        "success_rate": analysis.success_rate,
                        "alternatives": analysis.synonyms
                    })
            
            # Technique recommendations
            technique_patterns = analysis_results.get("technique_patterns", {})
            for combo, data in technique_patterns.items():
                if data["success_rate"] > 0.7:
                    recommendations.append({
                        "type": "technique_combination",
                        "priority": "medium", 
                        "action": f"Use effective technique combination: {', '.join(combo)}",
                        "success_rate": data["success_rate"]
                    })
            
            # Context recommendations
            context_patterns = analysis_results.get("context_patterns", {})
            for context_type, contexts in context_patterns.items():
                high_success = [
                    context for context, data in contexts.items()
                    if data["success_rate"] > 0.6
                ]
                if high_success:
                    recommendations.append({
                        "type": "context_targeting",
                        "priority": "medium",
                        "action": f"Target {context_type}: {', '.join(high_success[:2])}"
                    })
        
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
        
        return recommendations
    
    async def _generate_contextual_improvements(self, base_prompt: str, context: Dict, analysis_data: Dict) -> List[str]:
        """Generate improvements based on specific context (image analysis, etc.)"""
        improvements = []
        
        try:
            # Use image analysis context
            image_analysis = context.get("image_analysis", {})
            if image_analysis:
                subjects = image_analysis.get("subjects", {})
                if subjects:
                    # Generate subject-specific improvements
                    subject_type = subjects.get("subject_type", "")
                    if subject_type:
                        context_specific = base_prompt.replace("the person", f"the {subject_type}")
                        context_specific = context_specific.replace("subject", subject_type)
                        improvements.append(context_specific)
            
            # Use successful patterns from analysis
            word_patterns = analysis_data.get("word_patterns", {})
            successful_words = [
                word for word, analysis in word_patterns.items()
                if analysis.success_rate > 0.7
            ]
            
            if successful_words:
                # Create version using high-success words
                enhanced_prompt = base_prompt
                for word in successful_words[:3]:
                    if word not in base_prompt.lower():
                        enhanced_prompt += f" {word}"
                improvements.append(enhanced_prompt)
        
        except Exception as e:
            logger.error(f"Error generating contextual improvements: {e}")
        
        return improvements
    
    def _generate_analysis_summary(self, analysis_results: Dict) -> Dict:
        """Generate a concise summary of analysis results"""
        try:
            word_patterns = analysis_results.get("word_patterns", {})
            technique_patterns = analysis_results.get("technique_patterns", {})
            insights = analysis_results.get("generated_insights", [])
            
            return {
                "total_words_analyzed": len(word_patterns),
                "high_success_words": len([
                    w for w, a in word_patterns.items() if a.success_rate > 0.7
                ]),
                "low_success_words": len([
                    w for w, a in word_patterns.items() if a.success_rate < 0.3
                ]),
                "technique_combinations": len(technique_patterns),
                "key_insights": insights[:5],
                "analysis_timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return {"error": str(e)}
    
    def _is_analysis_cache_valid(self) -> bool:
        """Check if analysis cache is still valid (not older than 1 hour)"""
        if not self.last_analysis_time:
            return False
        
        time_diff = datetime.now() - self.last_analysis_time
        return time_diff.total_seconds() < 3600  # 1 hour

# Global integration manager
learning_integration_manager = LearningIntegrationManager()

# Convenience functions for easy integration
async def integrate_prompt_save(prompt_data: Dict) -> Dict:
    """Integrate with prompt saving workflow"""
    return await learning_integration_manager.integrate_with_prompt_tracking(prompt_data)

async def get_learning_analysis() -> Dict:
    """Get comprehensive learning analysis"""
    return await learning_integration_manager.trigger_comprehensive_analysis()

async def get_prompt_improvements(base_prompt: str, context: Dict = None) -> List[str]:
    """Get smart prompt improvements"""
    return await learning_integration_manager.get_smart_prompt_improvements(base_prompt, context)

async def get_prompt_feedback(prompt: str) -> Dict:
    """Get real-time prompt feedback"""
    return await learning_integration_manager.get_real_time_feedback(prompt)