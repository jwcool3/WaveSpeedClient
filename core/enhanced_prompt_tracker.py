"""
Enhanced Prompt Tracking System
Improved version with better failure tracking and user quality ratings
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from enum import Enum

# Add project root to path for imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from core.logger import get_logger

logger = get_logger()

class PromptQuality(Enum):
    """User quality ratings for prompts"""
    EXCELLENT = 5
    GOOD = 4
    AVERAGE = 3
    POOR = 2
    TERRIBLE = 1
    UNRATED = 0

class FailureReason(Enum):
    """Categorized failure reasons"""
    API_ERROR = "api_error"
    CONTENT_FILTER = "content_filter"
    INVALID_PARAMETERS = "invalid_parameters"
    TIMEOUT = "timeout"
    NETWORK_ERROR = "network_error"
    SERVER_ERROR = "server_error"
    QUOTA_EXCEEDED = "quota_exceeded"
    MALFORMED_PROMPT = "malformed_prompt"
    NSFW_CONTENT = "nsfw_content"
    OTHER = "other"

class EnhancedPromptTracker:
    """Enhanced prompt tracking with quality ratings and failure analysis"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        # Enhanced file structure
        self.failed_prompts_file = self.data_dir / "failed_prompts_enhanced.json"
        self.successful_prompts_file = self.data_dir / "successful_prompts_enhanced.json"
        self.user_ratings_file = self.data_dir / "user_quality_ratings.json"
        self.prompt_stats_file = self.data_dir / "prompt_statistics_enhanced.json"
        self.training_export_file = self.data_dir / "ai_training_export.json"
        
        self._initialize_files()
    
    def _initialize_files(self):
        """Initialize enhanced tracking files"""
        if not self.failed_prompts_file.exists():
            self._write_json(self.failed_prompts_file, {
                "metadata": {
                    "created": datetime.now().isoformat(),
                    "description": "Enhanced failed prompt tracking with categorized errors",
                    "version": "2.0"
                },
                "prompts": []
            })
        
        if not self.successful_prompts_file.exists():
            self._write_json(self.successful_prompts_file, {
                "metadata": {
                    "created": datetime.now().isoformat(),
                    "description": "Enhanced successful prompt tracking with quality ratings",
                    "version": "2.0"
                },
                "prompts": []
            })
        
        if not self.user_ratings_file.exists():
            self._write_json(self.user_ratings_file, {
                "metadata": {
                    "created": datetime.now().isoformat(),
                    "description": "User quality ratings for generated results"
                },
                "ratings": []
            })
    
    def log_failed_prompt(self,
                         prompt: str,
                         ai_model: str,
                         error_message: str,
                         failure_reason: FailureReason = FailureReason.OTHER,
                         http_status: Optional[int] = None,
                         api_response: Optional[str] = None,
                         model_parameters: Optional[Dict] = None,
                         additional_context: Optional[Dict] = None):
        """Enhanced failed prompt logging with categorization"""
        try:
            data = self._read_json(self.failed_prompts_file)
            if not data:
                data = {"metadata": {}, "prompts": []}
            
            failure_record = {
                "timestamp": datetime.now().isoformat(),
                "prompt": prompt,
                "ai_model": ai_model,
                "error_message": error_message,
                "failure_reason": failure_reason.value,
                "http_status": http_status,
                "api_response": api_response,
                "model_parameters": model_parameters or {},
                "additional_context": additional_context or {},
                "prompt_length": len(prompt),
                "word_count": len(prompt.split()) if prompt else 0,
                "prompt_hash": hash(prompt),  # For deduplication
                
                # Enhanced analysis fields
                "contains_special_chars": any(c in prompt for c in "!@#$%^&*()"),
                "contains_numbers": any(c.isdigit() for c in prompt),
                "all_caps_ratio": sum(1 for c in prompt if c.isupper()) / len(prompt) if prompt else 0,
                "has_multiple_sentences": len([s for s in prompt.split('.') if s.strip()]) > 1,
                "avg_word_length": sum(len(word) for word in prompt.split()) / len(prompt.split()) if prompt.split() else 0
            }
            
            data["prompts"].append(failure_record)
            
            # Keep only last 2000 failed prompts
            if len(data["prompts"]) > 2000:
                data["prompts"] = data["prompts"][-2000:]
            
            data["metadata"]["last_updated"] = datetime.now().isoformat()
            data["metadata"]["total_failures"] = len(data["prompts"])
            
            self._write_json(self.failed_prompts_file, data)
            self._update_statistics("failed", failure_reason)
            
            logger.info(f"Enhanced logging: Failed prompt for {ai_model} - {failure_reason.value}")
            
        except Exception as e:
            logger.error(f"Failed to log enhanced failed prompt: {e}")
    
    def log_successful_prompt(self,
                             prompt: str,
                             ai_model: str,
                             result_url: Optional[str] = None,
                             save_path: Optional[str] = None,
                             save_method: str = "auto",  # auto, manual, user_save
                             model_parameters: Optional[Dict] = None,
                             additional_context: Optional[Dict] = None):
        """Enhanced successful prompt logging"""
        try:
            data = self._read_json(self.successful_prompts_file)
            if not data:
                data = {"metadata": {}, "prompts": []}
            
            success_record = {
                "timestamp": datetime.now().isoformat(),
                "prompt": prompt,
                "ai_model": ai_model,
                "result_url": result_url,
                "save_path": save_path,
                "save_method": save_method,
                "model_parameters": model_parameters or {},
                "additional_context": additional_context or {},
                "prompt_length": len(prompt),
                "word_count": len(prompt.split()) if prompt else 0,
                "prompt_hash": hash(prompt),
                
                # Enhanced analysis fields (same as failed prompts)
                "contains_special_chars": any(c in prompt for c in "!@#$%^&*()"),
                "contains_numbers": any(c.isdigit() for c in prompt),
                "all_caps_ratio": sum(1 for c in prompt if c.isupper()) / len(prompt) if prompt else 0,
                "has_multiple_sentences": len([s for s in prompt.split('.') if s.strip()]) > 1,
                "avg_word_length": sum(len(word) for word in prompt.split()) / len(prompt.split()) if prompt.split() else 0,
                
                # Success-specific fields
                "user_quality_rating": PromptQuality.UNRATED.value,
                "user_feedback": "",
                "result_kept": save_method != "auto",  # User explicitly saved
                "processing_time": additional_context.get("processing_time") if additional_context else None
            }
            
            data["prompts"].append(success_record)
            
            # Keep only last 2000 successful prompts
            if len(data["prompts"]) > 2000:
                data["prompts"] = data["prompts"][-2000:]
            
            data["metadata"]["last_updated"] = datetime.now().isoformat()
            data["metadata"]["total_successes"] = len(data["prompts"])
            
            self._write_json(self.successful_prompts_file, data)
            self._update_statistics("successful", save_method)
            
            logger.info(f"Enhanced logging: Successful prompt for {ai_model} - {save_method}")
            
        except Exception as e:
            logger.error(f"Failed to log enhanced successful prompt: {e}")
    
    def rate_prompt_quality(self, 
                           prompt_hash: int, 
                           quality_rating: PromptQuality,
                           user_feedback: str = "",
                           result_path: Optional[str] = None):
        """Allow users to rate the quality of generated results"""
        try:
            # Update the successful prompt record
            data = self._read_json(self.successful_prompts_file)
            for prompt_record in data.get("prompts", []):
                if prompt_record.get("prompt_hash") == prompt_hash:
                    prompt_record["user_quality_rating"] = quality_rating.value
                    prompt_record["user_feedback"] = user_feedback
                    prompt_record["rating_timestamp"] = datetime.now().isoformat()
                    break
            
            self._write_json(self.successful_prompts_file, data)
            
            # Also log in separate ratings file
            ratings_data = self._read_json(self.user_ratings_file)
            rating_record = {
                "timestamp": datetime.now().isoformat(),
                "prompt_hash": prompt_hash,
                "quality_rating": quality_rating.value,
                "user_feedback": user_feedback,
                "result_path": result_path
            }
            
            ratings_data["ratings"].append(rating_record)
            self._write_json(self.user_ratings_file, ratings_data)
            
            logger.info(f"User rated prompt quality: {quality_rating.value}/5")
            
        except Exception as e:
            logger.error(f"Failed to log quality rating: {e}")
    
    def get_prompts_for_ai_training(self, 
                                   min_quality_rating: int = 4,
                                   max_failed_examples: int = 200,
                                   max_successful_examples: int = 200) -> Dict:
        """Export high-quality prompts for AI training"""
        try:
            # Get highly rated successful prompts
            successful_data = self._read_json(self.successful_prompts_file)
            high_quality_prompts = [
                p for p in successful_data.get("prompts", [])
                if p.get("user_quality_rating", 0) >= min_quality_rating
                or p.get("save_method") == "manual"  # User manually saved
            ]
            
            # Get categorized failed prompts
            failed_data = self._read_json(self.failed_prompts_file)
            failed_prompts = failed_data.get("prompts", [])
            
            # Categorize failures by reason
            categorized_failures = {}
            for failure in failed_prompts[-max_failed_examples:]:
                reason = failure.get("failure_reason", "other")
                if reason not in categorized_failures:
                    categorized_failures[reason] = []
                categorized_failures[reason].append(failure)
            
            training_data = {
                "export_timestamp": datetime.now().isoformat(),
                "metadata": {
                    "description": "Curated prompt data for AI training",
                    "good_prompts_count": len(high_quality_prompts[-max_successful_examples:]),
                    "failed_prompts_count": len(failed_prompts[-max_failed_examples:]),
                    "quality_threshold": min_quality_rating
                },
                "good_prompts": high_quality_prompts[-max_successful_examples:],
                "failed_prompts_by_category": categorized_failures,
                "analysis": self.analyze_prompt_patterns_enhanced()
            }
            
            # Save training export
            self._write_json(self.training_export_file, training_data)
            
            return training_data
            
        except Exception as e:
            logger.error(f"Failed to export training data: {e}")
            return {}
    
    def analyze_prompt_patterns_enhanced(self) -> Dict:
        """Enhanced pattern analysis for AI learning"""
        try:
            successful_data = self._read_json(self.successful_prompts_file)
            failed_data = self._read_json(self.failed_prompts_file)
            
            successful_prompts = successful_data.get("prompts", [])
            failed_prompts = failed_data.get("prompts", [])
            
            # Separate high-quality vs low-quality successful prompts
            high_quality = [p for p in successful_prompts if p.get("user_quality_rating", 0) >= 4]
            low_quality = [p for p in successful_prompts if 0 < p.get("user_quality_rating", 0) < 4]
            unrated = [p for p in successful_prompts if p.get("user_quality_rating", 0) == 0]
            
            analysis = {
                "timestamp": datetime.now().isoformat(),
                "high_quality_prompts": {
                    "count": len(high_quality),
                    "avg_length": self._avg_field(high_quality, "prompt_length"),
                    "avg_word_count": self._avg_field(high_quality, "word_count"),
                    "avg_word_length": self._avg_field(high_quality, "avg_word_length"),
                    "special_chars_ratio": self._ratio_field(high_quality, "contains_special_chars"),
                    "multi_sentence_ratio": self._ratio_field(high_quality, "has_multiple_sentences")
                },
                "low_quality_prompts": {
                    "count": len(low_quality),
                    "avg_length": self._avg_field(low_quality, "prompt_length"),
                    "avg_word_count": self._avg_field(low_quality, "word_count"),
                    "avg_word_length": self._avg_field(low_quality, "avg_word_length"),
                    "special_chars_ratio": self._ratio_field(low_quality, "contains_special_chars"),
                    "multi_sentence_ratio": self._ratio_field(low_quality, "has_multiple_sentences")
                },
                "failed_prompts": {
                    "count": len(failed_prompts),
                    "avg_length": self._avg_field(failed_prompts, "prompt_length"),
                    "avg_word_count": self._avg_field(failed_prompts, "word_count"),
                    "failure_reasons": self._count_field(failed_prompts, "failure_reason"),
                    "special_chars_ratio": self._ratio_field(failed_prompts, "contains_special_chars"),
                    "multi_sentence_ratio": self._ratio_field(failed_prompts, "has_multiple_sentences")
                },
                "save_method_analysis": {
                    "manual_saves": len([p for p in successful_prompts if p.get("save_method") == "manual"]),
                    "auto_saves": len([p for p in successful_prompts if p.get("save_method") == "auto"]),
                    "user_saves": len([p for p in successful_prompts if p.get("save_method") == "user_save"])
                }
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Failed enhanced pattern analysis: {e}")
            return {}
    
    def _avg_field(self, data_list: List[Dict], field: str) -> float:
        """Calculate average of a field"""
        values = [item.get(field, 0) for item in data_list if item.get(field) is not None]
        return sum(values) / len(values) if values else 0
    
    def _ratio_field(self, data_list: List[Dict], field: str) -> float:
        """Calculate ratio of True values for boolean field"""
        true_count = sum(1 for item in data_list if item.get(field, False))
        return true_count / len(data_list) if data_list else 0
    
    def _count_field(self, data_list: List[Dict], field: str) -> Dict:
        """Count occurrences of field values"""
        counts = {}
        for item in data_list:
            value = item.get(field, "unknown")
            counts[value] = counts.get(value, 0) + 1
        return counts
    
    def _read_json(self, file_path: Path) -> Dict:
        """Read JSON file safely"""
        try:
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error reading {file_path}: {e}")
        return {}
    
    def _write_json(self, file_path: Path, data: Dict):
        """Write JSON file safely"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error writing {file_path}: {e}")
    
    def _update_statistics(self, result_type: str, category: str = None):
        """Update aggregated statistics"""
        try:
            stats_data = self._read_json(self.prompt_stats_file)
            if not stats_data:
                stats_data = {"statistics": {}, "metadata": {"created": datetime.now().isoformat()}}
            
            stats = stats_data.get("statistics", {})
            today = datetime.now().strftime("%Y-%m-%d")
            
            if today not in stats:
                stats[today] = {"successful": 0, "failed": 0, "categories": {}}
            
            stats[today][result_type] += 1
            
            if category:
                if category not in stats[today]["categories"]:
                    stats[today]["categories"][category] = 0
                stats[today]["categories"][category] += 1
            
            stats_data["statistics"] = stats
            stats_data["metadata"]["last_updated"] = datetime.now().isoformat()
            
            self._write_json(self.prompt_stats_file, stats_data)
            
        except Exception as e:
            logger.error(f"Failed to update statistics: {e}")

# Global enhanced instance
enhanced_prompt_tracker = EnhancedPromptTracker()