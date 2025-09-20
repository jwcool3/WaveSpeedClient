"""
Prompt Tracking System
Tracks successful and failed prompts for analysis and improvement
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

# Add project root to path for imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from core.logger import get_logger

logger = get_logger()

class PromptTracker:
    """Tracks prompts and their outcomes for analysis"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        # File paths for different types of tracking
        self.failed_prompts_file = self.data_dir / "failed_prompts.json"
        self.successful_prompts_file = self.data_dir / "successful_prompts.json"
        self.prompt_stats_file = self.data_dir / "prompt_statistics.json"
        
        # Initialize files if they don't exist
        self._initialize_files()
    
    def _initialize_files(self):
        """Initialize tracking files with empty structure"""
        if not self.failed_prompts_file.exists():
            self._write_json(self.failed_prompts_file, {
                "metadata": {
                    "created": datetime.now().isoformat(),
                    "description": "Failed prompt attempts with error details"
                },
                "prompts": []
            })
        
        if not self.successful_prompts_file.exists():
            self._write_json(self.successful_prompts_file, {
                "metadata": {
                    "created": datetime.now().isoformat(),
                    "description": "Successful prompts that user saved"
                },
                "prompts": []
            })
        
        if not self.prompt_stats_file.exists():
            self._write_json(self.prompt_stats_file, {
                "metadata": {
                    "created": datetime.now().isoformat(),
                    "description": "Aggregated prompt statistics"
                },
                "statistics": {
                    "total_attempts": 0,
                    "successful_attempts": 0,
                    "failed_attempts": 0,
                    "success_rate": 0.0,
                    "common_failure_reasons": {},
                    "successful_prompt_patterns": {}
                }
            })
    
    def _write_json(self, file_path: Path, data: Dict):
        """Safely write JSON data to file"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to write to {file_path}: {e}")
    
    def _read_json(self, file_path: Path) -> Dict:
        """Safely read JSON data from file"""
        try:
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.error(f"Failed to read from {file_path}: {e}")
            return {}
    
    def log_failed_prompt(self, 
                         prompt: str,
                         ai_model: str,
                         error_message: str,
                         error_type: str = "unknown",
                         additional_context: Optional[Dict] = None):
        """Log a failed prompt attempt with detailed context"""
        try:
            # Read existing data
            data = self._read_json(self.failed_prompts_file)
            if not data:
                data = {"metadata": {}, "prompts": []}
            
            # Create failure record
            failure_record = {
                "timestamp": datetime.now().isoformat(),
                "prompt": prompt,
                "ai_model": ai_model,
                "error_message": error_message,
                "error_type": error_type,
                "additional_context": additional_context or {},
                "prompt_length": len(prompt),
                "word_count": len(prompt.split()) if prompt else 0
            }
            
            # Add to prompts list
            data["prompts"].append(failure_record)
            
            # Keep only last 1000 failed prompts to prevent file from growing too large
            if len(data["prompts"]) > 1000:
                data["prompts"] = data["prompts"][-1000:]
            
            # Update metadata
            data["metadata"]["last_updated"] = datetime.now().isoformat()
            data["metadata"]["total_failures"] = len(data["prompts"])
            
            # Write back to file
            self._write_json(self.failed_prompts_file, data)
            
            # Update statistics
            self._update_statistics("failed")
            
            logger.info(f"Logged failed prompt for {ai_model}: {error_type}")
            
        except Exception as e:
            logger.error(f"Failed to log failed prompt: {e}")
    
    def log_successful_prompt(self,
                             prompt: str,
                             ai_model: str,
                             result_url: Optional[str] = None,
                             save_path: Optional[str] = None,
                             additional_context: Optional[Dict] = None):
        """Log a successful prompt that the user saved"""
        try:
            # Read existing data
            data = self._read_json(self.successful_prompts_file)
            if not data:
                data = {"metadata": {}, "prompts": []}
            
            # Create success record
            success_record = {
                "timestamp": datetime.now().isoformat(),
                "prompt": prompt,
                "ai_model": ai_model,
                "result_url": result_url,
                "save_path": save_path,
                "additional_context": additional_context or {},
                "prompt_length": len(prompt),
                "word_count": len(prompt.split()) if prompt else 0
            }
            
            # Add to prompts list
            data["prompts"].append(success_record)
            
            # Keep only last 1000 successful prompts
            if len(data["prompts"]) > 1000:
                data["prompts"] = data["prompts"][-1000:]
            
            # Update metadata
            data["metadata"]["last_updated"] = datetime.now().isoformat()
            data["metadata"]["total_successes"] = len(data["prompts"])
            
            # Write back to file
            self._write_json(self.successful_prompts_file, data)
            
            # Update statistics
            self._update_statistics("successful")
            
            logger.info(f"Logged successful prompt for {ai_model}")
            
        except Exception as e:
            logger.error(f"Failed to log successful prompt: {e}")
    
    def _update_statistics(self, outcome: str):
        """Update aggregated statistics"""
        try:
            stats_data = self._read_json(self.prompt_stats_file)
            if not stats_data:
                stats_data = {"metadata": {}, "statistics": {}}
            
            stats = stats_data.get("statistics", {})
            
            # Update counters
            stats["total_attempts"] = stats.get("total_attempts", 0) + 1
            if outcome == "successful":
                stats["successful_attempts"] = stats.get("successful_attempts", 0) + 1
            elif outcome == "failed":
                stats["failed_attempts"] = stats.get("failed_attempts", 0) + 1
            
            # Calculate success rate
            total = stats.get("total_attempts", 0)
            successful = stats.get("successful_attempts", 0)
            stats["success_rate"] = (successful / total * 100) if total > 0 else 0.0
            
            # Update metadata
            stats_data["metadata"]["last_updated"] = datetime.now().isoformat()
            stats_data["statistics"] = stats
            
            # Write back
            self._write_json(self.prompt_stats_file, stats_data)
            
        except Exception as e:
            logger.error(f"Failed to update statistics: {e}")
    
    def get_failed_prompts(self, limit: int = 50) -> List[Dict]:
        """Get recent failed prompts"""
        try:
            data = self._read_json(self.failed_prompts_file)
            prompts = data.get("prompts", [])
            return prompts[-limit:] if limit else prompts
        except Exception as e:
            logger.error(f"Failed to get failed prompts: {e}")
            return []
    
    def get_successful_prompts(self, limit: int = 50) -> List[Dict]:
        """Get recent successful prompts"""
        try:
            data = self._read_json(self.successful_prompts_file)
            prompts = data.get("prompts", [])
            return prompts[-limit:] if limit else prompts
        except Exception as e:
            logger.error(f"Failed to get successful prompts: {e}")
            return []
    
    def get_statistics(self) -> Dict:
        """Get aggregated prompt statistics"""
        try:
            data = self._read_json(self.prompt_stats_file)
            return data.get("statistics", {})
        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            return {}
    
    def analyze_prompt_patterns(self) -> Dict:
        """Analyze patterns in successful vs failed prompts"""
        try:
            failed_prompts = self.get_failed_prompts(limit=200)
            successful_prompts = self.get_successful_prompts(limit=200)
            
            analysis = {
                "failed_prompts": {
                    "count": len(failed_prompts),
                    "avg_length": sum(p.get("prompt_length", 0) for p in failed_prompts) / len(failed_prompts) if failed_prompts else 0,
                    "avg_word_count": sum(p.get("word_count", 0) for p in failed_prompts) / len(failed_prompts) if failed_prompts else 0,
                    "common_error_types": {}
                },
                "successful_prompts": {
                    "count": len(successful_prompts),
                    "avg_length": sum(p.get("prompt_length", 0) for p in successful_prompts) / len(successful_prompts) if successful_prompts else 0,
                    "avg_word_count": sum(p.get("word_count", 0) for p in successful_prompts) / len(successful_prompts) if successful_prompts else 0
                }
            }
            
            # Count error types
            for prompt in failed_prompts:
                error_type = prompt.get("error_type", "unknown")
                analysis["failed_prompts"]["common_error_types"][error_type] = \
                    analysis["failed_prompts"]["common_error_types"].get(error_type, 0) + 1
            
            return analysis
            
        except Exception as e:
            logger.error(f"Failed to analyze prompt patterns: {e}")
            return {}
    
    def export_prompts(self, output_file: str = None) -> str:
        """Export all prompt data to a single file for analysis"""
        try:
            if not output_file:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_file = self.data_dir / f"prompt_export_{timestamp}.json"
            
            export_data = {
                "export_timestamp": datetime.now().isoformat(),
                "failed_prompts": self._read_json(self.failed_prompts_file),
                "successful_prompts": self._read_json(self.successful_prompts_file),
                "statistics": self._read_json(self.prompt_stats_file),
                "analysis": self.analyze_prompt_patterns()
            }
            
            self._write_json(Path(output_file), export_data)
            logger.info(f"Exported prompt data to {output_file}")
            return str(output_file)
            
        except Exception as e:
            logger.error(f"Failed to export prompts: {e}")
            return ""

# Global instance
prompt_tracker = PromptTracker()
