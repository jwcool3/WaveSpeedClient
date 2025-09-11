#!/usr/bin/env python3
"""
Prompt Analysis Utility
Analyzes tracked prompts to identify patterns and insights
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime
from collections import Counter

# Add the project root to the path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from core.prompt_tracker import prompt_tracker

def print_separator(title=""):
    """Print a visual separator"""
    if title:
        print(f"\n{'='*60}")
        print(f" {title}")
        print(f"{'='*60}")
    else:
        print("-" * 60)

def analyze_prompt_statistics():
    """Display overall prompt statistics"""
    print_separator("PROMPT STATISTICS")
    
    stats = prompt_tracker.get_statistics()
    
    if not stats:
        print("No statistics available yet.")
        return
    
    print(f"Total Attempts: {stats.get('total_attempts', 0)}")
    print(f"Successful Attempts: {stats.get('successful_attempts', 0)}")
    print(f"Failed Attempts: {stats.get('failed_attempts', 0)}")
    print(f"Success Rate: {stats.get('success_rate', 0):.1f}%")
    
    if stats.get('common_failure_reasons'):
        print("\nCommon Failure Reasons:")
        for reason, count in stats['common_failure_reasons'].items():
            print(f"  {reason}: {count}")

def analyze_failed_prompts():
    """Analyze failed prompts for patterns"""
    print_separator("FAILED PROMPTS ANALYSIS")
    
    failed_prompts = prompt_tracker.get_failed_prompts(limit=100)
    
    if not failed_prompts:
        print("No failed prompts to analyze.")
        return
    
    print(f"Analyzing {len(failed_prompts)} recent failed prompts...")
    
    # Group by error type
    error_types = Counter()
    prompt_lengths = []
    word_counts = []
    
    for prompt_data in failed_prompts:
        error_type = prompt_data.get('error_type', 'unknown')
        error_types[error_type] += 1
        
        prompt_lengths.append(prompt_data.get('prompt_length', 0))
        word_counts.append(prompt_data.get('word_count', 0))
    
    print(f"\nError Type Distribution:")
    for error_type, count in error_types.most_common():
        print(f"  {error_type}: {count} ({count/len(failed_prompts)*100:.1f}%)")
    
    if prompt_lengths:
        avg_length = sum(prompt_lengths) / len(prompt_lengths)
        print(f"\nAverage Prompt Length: {avg_length:.1f} characters")
    
    if word_counts:
        avg_words = sum(word_counts) / len(word_counts)
        print(f"Average Word Count: {avg_words:.1f} words")
    
    # Show recent failed prompts
    print(f"\nRecent Failed Prompts (last 5):")
    for i, prompt_data in enumerate(failed_prompts[-5:], 1):
        timestamp = prompt_data.get('timestamp', 'Unknown')
        prompt = prompt_data.get('prompt', 'N/A')[:100]
        error_type = prompt_data.get('error_type', 'unknown')
        print(f"  {i}. [{error_type}] {prompt}...")
        print(f"     Time: {timestamp}")

def analyze_successful_prompts():
    """Analyze successful prompts for patterns"""
    print_separator("SUCCESSFUL PROMPTS ANALYSIS")
    
    successful_prompts = prompt_tracker.get_successful_prompts(limit=100)
    
    if not successful_prompts:
        print("No successful prompts to analyze.")
        return
    
    print(f"Analyzing {len(successful_prompts)} recent successful prompts...")
    
    prompt_lengths = []
    word_counts = []
    auto_saved_count = 0
    manual_saved_count = 0
    
    for prompt_data in successful_prompts:
        prompt_lengths.append(prompt_data.get('prompt_length', 0))
        word_counts.append(prompt_data.get('word_count', 0))
        
        context = prompt_data.get('additional_context', {})
        if context.get('auto_saved'):
            auto_saved_count += 1
        elif context.get('manual_save'):
            manual_saved_count += 1
    
    if prompt_lengths:
        avg_length = sum(prompt_lengths) / len(prompt_lengths)
        print(f"Average Prompt Length: {avg_length:.1f} characters")
    
    if word_counts:
        avg_words = sum(word_counts) / len(word_counts)
        print(f"Average Word Count: {avg_words:.1f} words")
    
    print(f"\nSave Method Distribution:")
    print(f"  Auto-saved: {auto_saved_count} ({auto_saved_count/len(successful_prompts)*100:.1f}%)")
    print(f"  Manual save: {manual_saved_count} ({manual_saved_count/len(successful_prompts)*100:.1f}%)")
    
    # Show recent successful prompts
    print(f"\nRecent Successful Prompts (last 5):")
    for i, prompt_data in enumerate(successful_prompts[-5:], 1):
        timestamp = prompt_data.get('timestamp', 'Unknown')
        prompt = prompt_data.get('prompt', 'N/A')[:100]
        context = prompt_data.get('additional_context', {})
        save_method = "Auto" if context.get('auto_saved') else "Manual"
        print(f"  {i}. [{save_method}] {prompt}...")
        print(f"     Time: {timestamp}")

def compare_prompt_patterns():
    """Compare patterns between successful and failed prompts"""
    print_separator("SUCCESSFUL vs FAILED PROMPT COMPARISON")
    
    analysis = prompt_tracker.analyze_prompt_patterns()
    
    if not analysis:
        print("No data available for comparison.")
        return
    
    failed = analysis.get('failed_prompts', {})
    successful = analysis.get('successful_prompts', {})
    
    print(f"Failed Prompts:")
    print(f"  Count: {failed.get('count', 0)}")
    print(f"  Avg Length: {failed.get('avg_length', 0):.1f} chars")
    print(f"  Avg Words: {failed.get('avg_word_count', 0):.1f}")
    
    print(f"\nSuccessful Prompts:")
    print(f"  Count: {successful.get('count', 0)}")
    print(f"  Avg Length: {successful.get('avg_length', 0):.1f} chars")
    print(f"  Avg Words: {successful.get('avg_word_count', 0):.1f}")
    
    if failed.get('common_error_types'):
        print(f"\nMost Common Error Types:")
        for error_type, count in failed['common_error_types'].items():
            print(f"  {error_type}: {count}")

def export_prompt_data():
    """Export all prompt data for external analysis"""
    print_separator("EXPORTING PROMPT DATA")
    
    export_file = prompt_tracker.export_prompts()
    
    if export_file:
        print(f"Prompt data exported to: {export_file}")
        print("You can use this file for further analysis or share it for review.")
    else:
        print("Failed to export prompt data.")

def main():
    """Main analysis function"""
    print("Prompt Analysis Tool")
    print("Analyzing your AI prompt patterns...")
    
    try:
        # Run all analyses
        analyze_prompt_statistics()
        analyze_failed_prompts()
        analyze_successful_prompts()
        compare_prompt_patterns()
        export_prompt_data()
        
        print_separator("ANALYSIS COMPLETE")
        print("Use this information to:")
        print("• Identify what types of prompts work best")
        print("• Avoid common failure patterns")
        print("• Optimize your prompt writing")
        print("• Track your improvement over time")
        
    except Exception as e:
        print(f"Error during analysis: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
