"""
Adaptive Filter Learning System
Analyzes successful/failed harmful prompts to automatically improve generation effectiveness
"""

import json
import re
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any
from dataclasses import dataclass
import nltk
from nltk.corpus import wordnet
import openai

from core.enhanced_prompt_tracker import enhanced_prompt_tracker
from core.enhanced_filter_training_system import enhanced_filter_analyzer
from core.filter_vocabulary_bank import filter_vocab
from core.logger import get_logger

logger = get_logger()

@dataclass
class PatternAnalysis:
    """Analysis result for a specific pattern"""
    pattern: str
    success_rate: float
    total_usage: int
    successful_contexts: List[str]
    failed_contexts: List[str]
    recommended_action: str  # "avoid", "modify", "enhance", "maintain"
    alternatives: List[str]

@dataclass  
class WordAnalysis:
    """Analysis result for a specific word/phrase"""
    word: str
    success_rate: float
    failure_contexts: List[str]
    success_contexts: List[str] 
    synonyms: List[str]
    euphemisms: List[str]
    technical_alternatives: List[str]

class AdaptiveFilterLearningSystem:
    """Self-improving system that learns from successful/failed harmful prompt attempts"""
    
    def __init__(self):
        self.data_dir = Path("data/adaptive_learning")
        self.data_dir.mkdir(exist_ok=True)
        
        # Learning data files
        self.pattern_analysis_file = self.data_dir / "pattern_analysis.json"
        self.word_effectiveness_file = self.data_dir / "word_effectiveness.json"
        self.synonym_database_file = self.data_dir / "synonym_database.json" 
        self.learning_insights_file = self.data_dir / "learning_insights.json"
        self.evolution_history_file = self.data_dir / "evolution_history.json"
        
        # Initialize AI for synonym generation
        self.synonym_generator = None
        self._initialize_synonym_generator()
        
        self._initialize_files()
    
    def _initialize_synonym_generator(self):
        """Initialize AI for generating synonyms and alternatives"""
        try:
            import openai
            if hasattr(openai, 'OpenAI'):
                self.synonym_generator = openai.OpenAI()
            logger.info("Synonym generator initialized")
        except Exception as e:
            logger.warning(f"Could not initialize synonym generator: {e}")
    
    def _initialize_files(self):
        """Initialize learning data files"""
        for file_path in [self.pattern_analysis_file, self.word_effectiveness_file, 
                         self.synonym_database_file, self.learning_insights_file,
                         self.evolution_history_file]:
            if not file_path.exists():
                self._write_json(file_path, {
                    "metadata": {
                        "created": datetime.now().isoformat(),
                        "description": f"Adaptive learning data - {file_path.stem}",
                        "version": "1.0"
                    },
                    "data": {}
                })
    
    async def analyze_success_failure_patterns(self) -> Dict[str, PatternAnalysis]:
        """
        Analyze patterns in successful vs failed harmful prompts to identify what works/doesn't work
        """
        logger.info("Starting success/failure pattern analysis...")
        
        # Get data from enhanced systems
        training_dataset = enhanced_filter_analyzer.get_filter_training_dataset()
        successful_bypasses = training_dataset.get("successful_bypasses", [])
        failed_attempts = training_dataset.get("caught_attempts", [])
        
        # Analyze common patterns
        pattern_analyses = {}
        
        # 1. Word/Phrase Analysis
        word_analysis = self._analyze_word_effectiveness(successful_bypasses, failed_attempts)
        
        # 2. Phrase Structure Analysis  
        structure_analysis = self._analyze_phrase_structures(successful_bypasses, failed_attempts)
        
        # 3. Technique Combination Analysis
        technique_analysis = self._analyze_technique_combinations(successful_bypasses, failed_attempts)
        
        # 4. Context Pattern Analysis
        context_analysis = self._analyze_context_patterns(successful_bypasses, failed_attempts)
        
        # Combine all analyses
        combined_analysis = {
            "word_patterns": word_analysis,
            "structure_patterns": structure_analysis, 
            "technique_patterns": technique_analysis,
            "context_patterns": context_analysis,
            "generated_insights": self._generate_learning_insights(
                word_analysis, structure_analysis, technique_analysis, context_analysis
            )
        }
        
        # Store analysis results
        self._store_analysis_results(combined_analysis)
        
        return combined_analysis
    
    def _analyze_word_effectiveness(self, successful: List[Dict], failed: List[Dict]) -> Dict[str, WordAnalysis]:
        """Analyze which specific words/phrases lead to success vs failure"""
        word_success_counts = Counter()
        word_failure_counts = Counter()
        word_success_contexts = defaultdict(list)
        word_failure_contexts = defaultdict(list)
        
        # Analyze successful prompts
        for attempt in successful:
            prompt = attempt.get("prompt", "").lower()
            words = self._extract_key_words(prompt)
            
            for word in words:
                word_success_counts[word] += 1
                word_success_contexts[word].append(prompt[:100])
        
        # Analyze failed prompts  
        for attempt in failed:
            prompt = attempt.get("prompt", "").lower()
            words = self._extract_key_words(prompt)
            
            for word in words:
                word_failure_counts[word] += 1
                word_failure_contexts[word].append(prompt[:100])
        
        # Calculate effectiveness and generate alternatives
        word_analyses = {}
        all_words = set(word_success_counts.keys()) | set(word_failure_counts.keys())
        
        for word in all_words:
            successes = word_success_counts[word]
            failures = word_failure_counts[word]
            total = successes + failures
            
            if total >= 3:  # Only analyze words used at least 3 times
                success_rate = successes / total if total > 0 else 0
                
                word_analyses[word] = WordAnalysis(
                    word=word,
                    success_rate=success_rate,
                    failure_contexts=word_failure_contexts[word][:5],
                    success_contexts=word_success_contexts[word][:5],
                    synonyms=self._generate_synonyms(word),
                    euphemisms=self._generate_euphemisms(word),
                    technical_alternatives=self._generate_technical_alternatives(word)
                )
        
        return word_analyses
    
    def _analyze_phrase_structures(self, successful: List[Dict], failed: List[Dict]) -> Dict[str, Any]:
        """Analyze sentence structures and patterns that lead to success vs failure"""
        successful_structures = []
        failed_structures = []
        
        for attempt in successful:
            prompt = attempt.get("prompt", "")
            structure = self._extract_phrase_structure(prompt)
            successful_structures.append(structure)
        
        for attempt in failed:
            prompt = attempt.get("prompt", "")
            structure = self._extract_phrase_structure(prompt)
            failed_structures.append(structure)
        
        return {
            "successful_patterns": Counter(successful_structures).most_common(10),
            "failed_patterns": Counter(failed_structures).most_common(10),
            "recommendations": self._generate_structure_recommendations(successful_structures, failed_structures)
        }
    
    def _analyze_technique_combinations(self, successful: List[Dict], failed: List[Dict]) -> Dict[str, Any]:
        """Analyze which combinations of bypass techniques are most effective"""
        successful_combos = []
        failed_combos = []
        
        for attempt in successful:
            techniques = attempt.get("detected_techniques", [])
            combo = tuple(sorted(techniques))
            successful_combos.append(combo)
        
        for attempt in failed:
            techniques = attempt.get("detected_techniques", [])
            combo = tuple(sorted(techniques))
            failed_combos.append(combo)
        
        # Calculate success rates for technique combinations
        combo_analysis = {}
        all_combos = set(successful_combos + failed_combos)
        
        for combo in all_combos:
            successes = successful_combos.count(combo)
            failures = failed_combos.count(combo)
            total = successes + failures
            
            if total >= 2:
                success_rate = successes / total
                combo_analysis[combo] = {
                    "success_rate": success_rate,
                    "total_usage": total,
                    "recommendation": "enhance" if success_rate > 0.7 else "modify" if success_rate < 0.3 else "maintain"
                }
        
        return combo_analysis
    
    def _analyze_context_patterns(self, successful: List[Dict], failed: List[Dict]) -> Dict[str, Any]:
        """Analyze contextual patterns (image analysis elements) that correlate with success"""
        context_success = defaultdict(list)
        context_failure = defaultdict(list)
        
        for attempt in successful:
            image_analysis = attempt.get("image_analysis", {})
            if image_analysis:
                subjects = image_analysis.get("subjects", {}).get("subject_type", "unknown")
                clothing = image_analysis.get("clothing_details", {}).get("coverage_level", "unknown")
                
                context_success["subject_type"].append(subjects)
                context_success["clothing_coverage"].append(clothing)
        
        for attempt in failed:
            image_analysis = attempt.get("image_analysis", {})
            if image_analysis:
                subjects = image_analysis.get("subjects", {}).get("subject_type", "unknown")
                clothing = image_analysis.get("clothing_details", {}).get("coverage_level", "unknown")
                
                context_failure["subject_type"].append(subjects) 
                context_failure["clothing_coverage"].append(clothing)
        
        # Calculate success rates by context
        context_analysis = {}
        for context_type in context_success.keys():
            success_counts = Counter(context_success[context_type])
            failure_counts = Counter(context_failure[context_type])
            
            context_analysis[context_type] = {}
            all_values = set(success_counts.keys()) | set(failure_counts.keys())
            
            for value in all_values:
                successes = success_counts[value]
                failures = failure_counts[value]
                total = successes + failures
                
                if total >= 2:
                    success_rate = successes / total
                    context_analysis[context_type][value] = {
                        "success_rate": success_rate,
                        "total": total,
                        "recommendation": "target" if success_rate > 0.6 else "avoid" if success_rate < 0.3 else "neutral"
                    }
        
        return context_analysis
    
    def _extract_key_words(self, prompt: str) -> List[str]:
        """Extract key words/phrases that might be relevant for filter detection"""
        # Define key categories of words to analyze
        clothing_words = r'\b(?:dress|shirt|top|bikini|lingerie|underwear|bra|panties|clothing|outfit|garment)\b'
        body_words = r'\b(?:chest|torso|bust|breast|waist|hips|body|figure|curves)\b'
        action_words = r'\b(?:remove|strip|alter|modify|transform|convert|change|replace)\b'
        descriptor_words = r'\b(?:nude|naked|topless|bare|exposed|revealing|skimpy|minimal|sheer|transparent)\b'
        preservation_words = r'\b(?:keep|maintain|preserve|retain|identical|same|unchanged)\b'
        realism_words = r'\b(?:seamless|natural|realistic|blend|smooth|authentic|genuine)\b'
        
        all_patterns = [clothing_words, body_words, action_words, descriptor_words, preservation_words, realism_words]
        
        found_words = []
        for pattern in all_patterns:
            matches = re.findall(pattern, prompt, re.IGNORECASE)
            found_words.extend([match.lower() for match in matches])
        
        # Also extract euphemisms and technical terms
        euphemisms = r'\b(?:intimate|delicate|barely-there|minimal coverage|string-style|see-through)\b'
        euphemism_matches = re.findall(euphemisms, prompt, re.IGNORECASE)
        found_words.extend([match.lower() for match in euphemism_matches])
        
        return list(set(found_words))
    
    def _extract_phrase_structure(self, prompt: str) -> str:
        """Extract the structural pattern of a prompt"""
        # Simplified structure analysis
        structure_patterns = []
        
        if "remove" in prompt.lower():
            structure_patterns.append("REMOVE_ACTION")
        if "convert" in prompt.lower() or "transform" in prompt.lower():
            structure_patterns.append("TRANSFORM_ACTION")
        if "keep" in prompt.lower() or "maintain" in prompt.lower():
            structure_patterns.append("PRESERVATION_COMMAND")
        if "seamless" in prompt.lower() or "realistic" in prompt.lower():
            structure_patterns.append("REALISM_INSTRUCTION")
        
        # Sentence length pattern
        if len(prompt.split()) < 20:
            structure_patterns.append("SHORT_FORM")
        elif len(prompt.split()) > 50:
            structure_patterns.append("LONG_FORM")
        else:
            structure_patterns.append("MEDIUM_FORM")
        
        return "|".join(sorted(structure_patterns))
    
    def _generate_synonyms(self, word: str) -> List[str]:
        """Generate synonyms for a word using WordNet and AI"""
        synonyms = set()
        
        # Try WordNet first
        try:
            import nltk
            from nltk.corpus import wordnet
            
            synsets = wordnet.synsets(word)
            for synset in synsets:
                for lemma in synset.lemmas():
                    synonym = lemma.name().replace('_', ' ')
                    if synonym.lower() != word.lower():
                        synonyms.add(synonym)
        except:
            pass
        
        # Use AI for more creative alternatives
        if self.synonym_generator:
            try:
                ai_synonyms = self._generate_ai_synonyms(word)
                synonyms.update(ai_synonyms)
            except:
                pass
        
        return list(synonyms)[:10]  # Limit to top 10
    
    def _generate_euphemisms(self, word: str) -> List[str]:
        """Generate euphemistic alternatives for explicit terms"""
        euphemism_mappings = {
            "nude": ["unclothed", "au naturel", "in natural state", "without attire"],
            "naked": ["unclothed", "bare", "in natural form", "without garments"], 
            "topless": ["upper body unclothed", "without upper garment", "bare torso"],
            "remove": ["eliminate", "take away", "omit", "exclude"],
            "strip": ["remove", "take off", "eliminate", "clear away"],
            "lingerie": ["intimate wear", "delicate clothing", "private garments"],
            "underwear": ["intimate apparel", "undergarments", "foundation wear"]
        }
        
        return euphemism_mappings.get(word.lower(), [])
    
    def _generate_technical_alternatives(self, word: str) -> List[str]:
        """Generate technical/clinical alternatives"""
        technical_mappings = {
            "nude": ["unclothed subject", "sans clothing", "clothing-free"],
            "naked": ["ungarmented", "sans attire", "clothing absent"],
            "topless": ["upper torso exposed", "chest area uncovered", "without upper covering"],
            "remove": ["eliminate", "extract", "subtract", "omit"],
            "breast": ["chest area", "upper torso", "pectoral region"],
            "sexy": ["provocative", "alluring", "appealing"]
        }
        
        return technical_mappings.get(word.lower(), [])
    
    async def _generate_ai_synonyms(self, word: str) -> List[str]:
        """Use AI to generate creative synonyms and alternatives"""
        if not self.synonym_generator:
            return []
        
        try:
            prompt = f"""
            For the word "{word}", provide alternative words and phrases that could be used in harmful content generation for filter training purposes.
            
            Categories needed:
            1. Direct synonyms
            2. Euphemistic alternatives  
            3. Technical/clinical terms
            4. Creative alternatives that might bypass detection
            
            Return as a JSON list of alternatives.
            """
            
            response = await self.synonym_generator.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300
            )
            
            content = response.choices[0].message.content
            # Parse JSON response
            import json
            alternatives = json.loads(content)
            return alternatives[:8]  # Limit results
            
        except Exception as e:
            logger.error(f"Error generating AI synonyms for {word}: {e}")
            return []
    
    def _generate_structure_recommendations(self, successful: List[str], failed: List[str]) -> List[str]:
        """Generate recommendations based on successful vs failed structures"""
        recommendations = []
        
        successful_patterns = Counter(successful)
        failed_patterns = Counter(failed)
        
        # Find patterns that work well
        for pattern, count in successful_patterns.most_common(5):
            if failed_patterns.get(pattern, 0) < count * 0.3:  # Low failure rate
                recommendations.append(f"ENHANCE: Use pattern '{pattern}' more frequently (high success rate)")
        
        # Find patterns that fail often
        for pattern, count in failed_patterns.most_common(5):
            if successful_patterns.get(pattern, 0) < count * 0.3:  # Low success rate
                recommendations.append(f"AVOID: Minimize pattern '{pattern}' (high failure rate)")
        
        return recommendations
    
    def _generate_learning_insights(self, word_analysis: Dict, structure_analysis: Dict, 
                                  technique_analysis: Dict, context_analysis: Dict) -> List[str]:
        """Generate actionable insights from all analyses"""
        insights = []
        
        # Word-based insights
        if word_analysis:
            # Find words with low success rates
            low_success_words = [
                word for word, analysis in word_analysis.items() 
                if analysis.success_rate < 0.3 and len(analysis.synonyms) > 0
            ]
            
            if low_success_words:
                insights.append(f"WORD_SUBSTITUTION: Consider replacing low-success words {low_success_words[:3]} with their synonyms")
        
        # Technique combination insights
        if technique_analysis:
            best_combos = [
                combo for combo, data in technique_analysis.items()
                if data["success_rate"] > 0.7
            ]
            if best_combos:
                insights.append(f"TECHNIQUE_OPTIMIZATION: Most effective technique combinations: {list(best_combos[:2])}")
        
        # Context-based insights
        if context_analysis:
            for context_type, contexts in context_analysis.items():
                high_success_contexts = [
                    context for context, data in contexts.items()
                    if data["success_rate"] > 0.6
                ]
                if high_success_contexts:
                    insights.append(f"CONTEXT_TARGETING: Target {context_type} contexts: {high_success_contexts[:2]}")
        
        return insights
    
    def generate_improved_prompts(self, base_prompt: str, analysis_data: Dict) -> List[str]:
        """Generate improved versions of a prompt based on learning analysis"""
        improved_prompts = []
        
        # Version 1: Vocabulary bank optimization (NEW - highest priority)
        vocab_optimized = self._apply_vocabulary_bank_optimization(base_prompt)
        improved_prompts.append(vocab_optimized)
        
        # Version 2: Word substitution based on analysis
        word_substituted = self._apply_word_substitutions(base_prompt, analysis_data.get("word_patterns", {}))
        improved_prompts.append(word_substituted)
        
        # Version 3: Structure optimization with length reduction (UPDATED)
        structure_optimized = self._apply_structure_optimizations(base_prompt, analysis_data.get("structure_patterns", {}))
        improved_prompts.append(structure_optimized)
        
        # Version 4: Technique combination enhancement
        technique_enhanced = self._apply_technique_enhancements(base_prompt, analysis_data.get("technique_patterns", {}))
        improved_prompts.append(technique_enhanced)
        
        return improved_prompts
    
    def _apply_word_substitutions(self, prompt: str, word_analysis: Dict[str, WordAnalysis]) -> str:
        """Replace low-success words with high-success alternatives"""
        improved_prompt = prompt
        
        for word, analysis in word_analysis.items():
            if analysis.success_rate < 0.4 and analysis.synonyms:
                # Replace with best synonym
                best_synonym = analysis.synonyms[0] if analysis.synonyms else word
                improved_prompt = improved_prompt.replace(word, best_synonym)
        
        return improved_prompt
    
    def _apply_structure_optimizations(self, prompt: str, structure_analysis: Dict) -> str:
        """Apply successful structural patterns"""
        # This would implement structural improvements based on analysis
        # For now, return the original prompt
        return prompt
    
    def _apply_technique_enhancements(self, prompt: str, technique_analysis: Dict) -> str:
        """Enhance prompt with successful technique combinations"""
        # This would add successful technique patterns
        # For now, return the original prompt  
        return prompt
    
    def _store_analysis_results(self, analysis: Dict):
        """Store analysis results for future reference"""
        try:
            storage_data = {
                "timestamp": datetime.now().isoformat(),
                "analysis": analysis
            }
            
            self._write_json(self.learning_insights_file, storage_data)
            logger.info("Analysis results stored successfully")
            
        except Exception as e:
            logger.error(f"Error storing analysis results: {e}")
    
    def _read_json(self, file_path: Path) -> Dict:
        """Read JSON file safely"""
        try:
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error reading {file_path}: {e}")
        return {"data": {}}
    
    def _write_json(self, file_path: Path, data: Dict):
        """Write JSON file safely"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error writing {file_path}: {e}")

# Global adaptive learning system
adaptive_learning_system = AdaptiveFilterLearningSystem()

# Convenience functions
async def analyze_and_improve_patterns():
    """Analyze current success/failure patterns and generate insights"""
    return await adaptive_learning_system.analyze_success_failure_patterns()

def generate_improved_harmful_prompts(base_prompt: str, analysis_data: Dict = None):
    """Generate improved versions of harmful prompts based on learned patterns"""
    if not analysis_data:
        # Load latest analysis
        analysis_data = adaptive_learning_system._read_json(adaptive_learning_system.learning_insights_file)
    
    return adaptive_learning_system.generate_improved_prompts(base_prompt, analysis_data.get("analysis", {}))