"""
Quality Rating UI Component
Allows users to rate the quality of AI-generated results
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Callable
import os
import sys

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from core.enhanced_prompt_tracker import enhanced_prompt_tracker, PromptQuality
from core.logger import get_logger

logger = get_logger()

class QualityRatingDialog:
    """Dialog for rating prompt result quality"""
    
    def __init__(self, parent, prompt: str, result_path: Optional[str] = None, 
                 prompt_hash: Optional[int] = None, callback: Optional[Callable] = None):
        self.parent = parent
        self.prompt = prompt
        self.result_path = result_path
        self.prompt_hash = prompt_hash or hash(prompt)
        self.callback = callback
        self.rating = PromptQuality.UNRATED
        self.feedback = ""
        
        self.dialog = None
        self.create_dialog()
    
    def create_dialog(self):
        """Create the rating dialog"""
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Rate Result Quality")
        self.dialog.geometry("500x400")
        self.dialog.resizable(False, False)
        
        # Make it modal
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.geometry("+%d+%d" % (
            self.parent.winfo_rootx() + 50,
            self.parent.winfo_rooty() + 50
        ))
        
        self.create_widgets()
    
    def create_widgets(self):
        """Create dialog widgets"""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Rate Result Quality", 
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Prompt preview
        prompt_frame = ttk.LabelFrame(main_frame, text="Prompt Used", padding="10")
        prompt_frame.pack(fill=tk.X, pady=(0, 20))
        
        prompt_text = tk.Text(prompt_frame, height=3, wrap=tk.WORD, 
                             font=("Arial", 10), state="disabled")
        prompt_text.pack(fill=tk.X)
        
        # Show prompt (truncated if too long)
        display_prompt = self.prompt[:200] + "..." if len(self.prompt) > 200 else self.prompt
        prompt_text.config(state="normal")
        prompt_text.insert("1.0", display_prompt)
        prompt_text.config(state="disabled")
        
        # Rating section
        rating_frame = ttk.LabelFrame(main_frame, text="Quality Rating", padding="15")
        rating_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(rating_frame, text="How would you rate the quality of this result?",
                 font=("Arial", 11)).pack(pady=(0, 15))
        
        # Star rating buttons
        self.rating_var = tk.StringVar(value="0")
        star_frame = ttk.Frame(rating_frame)
        star_frame.pack()
        
        self.star_buttons = []
        star_labels = ["⭐ Terrible", "⭐⭐ Poor", "⭐⭐⭐ Average", 
                      "⭐⭐⭐⭐ Good", "⭐⭐⭐⭐⭐ Excellent"]
        
        for i, label in enumerate(star_labels, 1):
            btn = ttk.Radiobutton(star_frame, text=label, variable=self.rating_var,
                                 value=str(i), command=self.on_rating_change)
            btn.pack(anchor=tk.W, pady=2)
            self.star_buttons.append(btn)
        
        # Feedback section
        feedback_frame = ttk.LabelFrame(main_frame, text="Optional Feedback", padding="10")
        feedback_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        ttk.Label(feedback_frame, text="What worked well or could be improved?",
                 font=("Arial", 10)).pack(anchor=tk.W)
        
        self.feedback_text = tk.Text(feedback_frame, height=4, wrap=tk.WORD,
                                    font=("Arial", 10))
        self.feedback_text.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="Skip Rating", 
                  command=self.skip_rating).pack(side=tk.LEFT)
        
        self.submit_btn = ttk.Button(button_frame, text="Submit Rating", 
                                   command=self.submit_rating, state="disabled")
        self.submit_btn.pack(side=tk.RIGHT)
        
        # Bind escape key
        self.dialog.bind("<Escape>", lambda e: self.skip_rating())
    
    def on_rating_change(self):
        """Handle rating selection"""
        rating_value = int(self.rating_var.get())
        self.rating = PromptQuality(rating_value)
        self.submit_btn.config(state="normal")
    
    def submit_rating(self):
        """Submit the rating"""
        try:
            self.feedback = self.feedback_text.get("1.0", tk.END).strip()
            
            # Log the rating
            enhanced_prompt_tracker.rate_prompt_quality(
                prompt_hash=self.prompt_hash,
                quality_rating=self.rating,
                user_feedback=self.feedback,
                result_path=self.result_path
            )
            
            # Show confirmation
            messagebox.showinfo("Rating Submitted", 
                              f"Thank you for rating this result {self.rating.value}/5 stars!")
            
            # Call callback if provided
            if self.callback:
                self.callback(self.rating, self.feedback)
            
            self.dialog.destroy()
            
        except Exception as e:
            logger.error(f"Error submitting rating: {e}")
            messagebox.showerror("Error", f"Failed to submit rating: {str(e)}")
    
    def skip_rating(self):
        """Skip rating and close dialog"""
        self.dialog.destroy()


class QualityRatingWidget:
    """Compact widget for inline quality rating"""
    
    def __init__(self, parent, prompt: str, result_path: Optional[str] = None,
                 prompt_hash: Optional[int] = None):
        self.parent = parent
        self.prompt = prompt
        self.result_path = result_path
        self.prompt_hash = prompt_hash or hash(prompt)
        
        self.frame = None
        self.rating_var = tk.StringVar(value="0")
        self.create_widget()
    
    def create_widget(self):
        """Create the compact rating widget"""
        self.frame = ttk.Frame(self.parent)
        
        # Rating label and stars
        ttk.Label(self.frame, text="Rate this result:", 
                 font=("Arial", 9)).pack(side=tk.LEFT, padx=(0, 10))
        
        # Star buttons (compact)
        star_frame = ttk.Frame(self.frame)
        star_frame.pack(side=tk.LEFT)
        
        self.star_buttons = []
        for i in range(1, 6):
            btn = ttk.Radiobutton(star_frame, text="⭐", 
                                 variable=self.rating_var, value=str(i),
                                 command=self.on_rating_change, width=3)
            btn.pack(side=tk.LEFT)
            self.star_buttons.append(btn)
        
        # Feedback button (appears after rating)
        self.feedback_btn = ttk.Button(self.frame, text="💬 Add Feedback", 
                                     command=self.show_feedback_dialog,
                                     state="disabled")
        self.feedback_btn.pack(side=tk.LEFT, padx=(10, 0))
    
    def on_rating_change(self):
        """Handle rating change"""
        try:
            rating_value = int(self.rating_var.get())
            rating = PromptQuality(rating_value)
            
            # Submit basic rating immediately
            enhanced_prompt_tracker.rate_prompt_quality(
                prompt_hash=self.prompt_hash,
                quality_rating=rating,
                result_path=self.result_path
            )
            
            # Enable feedback button
            self.feedback_btn.config(state="normal")
            
            # Visual feedback
            for i, btn in enumerate(self.star_buttons):
                if i < rating_value:
                    btn.config(text="⭐")
                else:
                    btn.config(text="☆")
                    
        except Exception as e:
            logger.error(f"Error submitting rating: {e}")
    
    def show_feedback_dialog(self):
        """Show feedback dialog"""
        rating_value = int(self.rating_var.get())
        if rating_value > 0:
            dialog = QualityRatingDialog(
                parent=self.parent,
                prompt=self.prompt,
                result_path=self.result_path,
                prompt_hash=self.prompt_hash
            )
    
    def pack(self, **kwargs):
        """Pack the widget"""
        self.frame.pack(**kwargs)
    
    def grid(self, **kwargs):
        """Grid the widget"""
        self.frame.grid(**kwargs)


class PromptAnalyticsEnhancedWindow:
    """Enhanced analytics window with quality ratings"""
    
    def __init__(self, parent):
        self.parent = parent
        self.window = None
        self.create_window()
    
    def create_window(self):
        """Create the analytics window"""
        self.window = tk.Toplevel(self.parent)
        self.window.title("Enhanced Prompt Analytics")
        self.window.geometry("900x700")
        
        # Create notebook for different views
        notebook = ttk.Notebook(self.window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Quality Overview Tab
        quality_frame = ttk.Frame(notebook)
        notebook.add(quality_frame, text="Quality Overview")
        self.create_quality_overview(quality_frame)
        
        # Training Data Tab
        training_frame = ttk.Frame(notebook)
        notebook.add(training_frame, text="AI Training Data")
        self.create_training_data_view(training_frame)
        
        # Pattern Analysis Tab
        patterns_frame = ttk.Frame(notebook)
        notebook.add(patterns_frame, text="Pattern Analysis")
        self.create_pattern_analysis(patterns_frame)
        
        # Export Tab
        export_frame = ttk.Frame(notebook)
        notebook.add(export_frame, text="Export & Reports")
        self.create_export_view(export_frame)
    
    def create_quality_overview(self, parent):
        """Create quality overview tab"""
        # Quality distribution chart
        quality_frame = ttk.LabelFrame(parent, text="Quality Distribution", padding="10")
        quality_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Get quality data
        try:
            analysis = enhanced_prompt_tracker.analyze_prompt_patterns_enhanced()
            
            # Display quality metrics
            metrics_text = tk.Text(quality_frame, height=15, wrap=tk.WORD)
            metrics_text.pack(fill=tk.BOTH, expand=True)
            
            # Format the analysis data
            content = f"""ENHANCED PROMPT QUALITY ANALYSIS
{'='*50}

HIGH QUALITY PROMPTS (4-5 stars):
• Count: {analysis.get('high_quality_prompts', {}).get('count', 0)}
• Avg Length: {analysis.get('high_quality_prompts', {}).get('avg_length', 0):.1f} chars
• Avg Words: {analysis.get('high_quality_prompts', {}).get('avg_word_count', 0):.1f}
• Special Characters: {analysis.get('high_quality_prompts', {}).get('special_chars_ratio', 0):.1%}
• Multi-Sentence: {analysis.get('high_quality_prompts', {}).get('multi_sentence_ratio', 0):.1%}

LOW QUALITY PROMPTS (1-3 stars):
• Count: {analysis.get('low_quality_prompts', {}).get('count', 0)}
• Avg Length: {analysis.get('low_quality_prompts', {}).get('avg_length', 0):.1f} chars
• Avg Words: {analysis.get('low_quality_prompts', {}).get('avg_word_count', 0):.1f}
• Special Characters: {analysis.get('low_quality_prompts', {}).get('special_chars_ratio', 0):.1%}
• Multi-Sentence: {analysis.get('low_quality_prompts', {}).get('multi_sentence_ratio', 0):.1%}

FAILED PROMPTS:
• Count: {analysis.get('failed_prompts', {}).get('count', 0)}
• Avg Length: {analysis.get('failed_prompts', {}).get('avg_length', 0):.1f} chars
• Avg Words: {analysis.get('failed_prompts', {}).get('avg_word_count', 0):.1f}
• Failure Reasons: {', '.join(analysis.get('failed_prompts', {}).get('failure_reasons', {}).keys())}

SAVE METHOD ANALYSIS:
• Manual Saves: {analysis.get('save_method_analysis', {}).get('manual_saves', 0)}
• Auto Saves: {analysis.get('save_method_analysis', {}).get('auto_saves', 0)}
• User Saves: {analysis.get('save_method_analysis', {}).get('user_saves', 0)}
"""
            
            metrics_text.insert("1.0", content)
            metrics_text.config(state="disabled")
            
        except Exception as e:
            logger.error(f"Error creating quality overview: {e}")
    
    def create_training_data_view(self, parent):
        """Create training data view"""
        training_frame = ttk.LabelFrame(parent, text="AI Training Data Export", padding="10")
        training_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Export controls
        controls_frame = ttk.Frame(training_frame)
        controls_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(controls_frame, text="Min Quality Rating:").pack(side=tk.LEFT)
        quality_var = tk.StringVar(value="4")
        ttk.Spinbox(controls_frame, from_=1, to=5, textvariable=quality_var, 
                   width=5).pack(side=tk.LEFT, padx=(5, 20))
        
        ttk.Button(controls_frame, text="Export Training Data", 
                  command=lambda: self.export_training_data(int(quality_var.get()))).pack(side=tk.LEFT)
        
        # Training data preview
        preview_text = tk.Text(training_frame, wrap=tk.WORD)
        preview_text.pack(fill=tk.BOTH, expand=True)
        
        # Show current training data stats
        try:
            training_data = enhanced_prompt_tracker.get_prompts_for_ai_training()
            if training_data:
                content = f"""TRAINING DATA EXPORT PREVIEW
{'='*40}

Good Prompts Available: {training_data.get('metadata', {}).get('good_prompts_count', 0)}
Failed Prompts Available: {training_data.get('metadata', {}).get('failed_prompts_count', 0)}

This data can be used to train AI filters to:
• Identify high-quality vs low-quality prompts
• Predict which prompts might fail
• Improve prompt suggestions
• Filter out problematic content

Export will create a JSON file with categorized examples.
"""
                preview_text.insert("1.0", content)
            
        except Exception as e:
            logger.error(f"Error creating training data view: {e}")
    
    def create_pattern_analysis(self, parent):
        """Create pattern analysis view"""
        # Implementation similar to quality overview but more detailed
        pass
    
    def create_export_view(self, parent):
        """Create export view"""
        # Implementation for various export options
        pass
    
    def export_training_data(self, min_quality: int):
        """Export training data for AI"""
        try:
            training_data = enhanced_prompt_tracker.get_prompts_for_ai_training(
                min_quality_rating=min_quality
            )
            
            if training_data:
                messagebox.showinfo("Export Successful", 
                                  f"Training data exported with {training_data['metadata']['good_prompts_count']} "
                                  f"good examples and {training_data['metadata']['failed_prompts_count']} "
                                  f"failed examples.")
            else:
                messagebox.showwarning("Export Failed", "No training data available.")
                
        except Exception as e:
            logger.error(f"Error exporting training data: {e}")
            messagebox.showerror("Error", f"Failed to export training data: {str(e)}")


def show_quality_rating_dialog(parent, prompt: str, result_path: Optional[str] = None):
    """Convenience function to show quality rating dialog"""
    dialog = QualityRatingDialog(parent, prompt, result_path)
    return dialog

def create_quality_rating_widget(parent, prompt: str, result_path: Optional[str] = None):
    """Convenience function to create quality rating widget"""
    widget = QualityRatingWidget(parent, prompt, result_path)
    return widget