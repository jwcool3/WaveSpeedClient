"""
Prompt Analytics Component
Provides a GUI interface for viewing prompt tracking statistics
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import sys
import os
from datetime import datetime

# Add project root to path for imports
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from core.prompt_tracker import prompt_tracker
from core.logger import get_logger

logger = get_logger()

class PromptAnalyticsWindow:
    """Window for viewing prompt analytics and statistics"""
    
    def __init__(self, parent=None):
        self.parent = parent
        self.window = None
        self.create_window()
    
    def create_window(self):
        """Create the analytics window"""
        self.window = tk.Toplevel(self.parent) if self.parent else tk.Tk()
        self.window.title("Prompt Analytics")
        self.window.geometry("800x600")
        self.window.resizable(True, True)
        
        # Create main frame
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Prompt Analytics Dashboard", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, pady=(0, 10))
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create tabs
        self.create_overview_tab()
        self.create_failed_prompts_tab()
        self.create_successful_prompts_tab()
        self.create_analysis_tab()
        
        # Refresh button
        refresh_btn = ttk.Button(main_frame, text="Refresh Data", 
                                command=self.refresh_all_data)
        refresh_btn.grid(row=2, column=0, pady=(10, 0))
        
        # Load initial data
        self.refresh_all_data()
    
    def create_overview_tab(self):
        """Create the overview statistics tab"""
        overview_frame = ttk.Frame(self.notebook)
        self.notebook.add(overview_frame, text="Overview")
        
        # Statistics display
        self.stats_text = tk.Text(overview_frame, wrap=tk.WORD, height=20, width=80)
        stats_scrollbar = ttk.Scrollbar(overview_frame, orient=tk.VERTICAL, 
                                       command=self.stats_text.yview)
        self.stats_text.configure(yscrollcommand=stats_scrollbar.set)
        
        self.stats_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        stats_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        overview_frame.columnconfigure(0, weight=1)
        overview_frame.rowconfigure(0, weight=1)
    
    def create_failed_prompts_tab(self):
        """Create the failed prompts tab"""
        failed_frame = ttk.Frame(self.notebook)
        self.notebook.add(failed_frame, text="Failed Prompts")
        
        # Treeview for failed prompts
        columns = ("Timestamp", "Error Type", "Prompt", "Model")
        self.failed_tree = ttk.Treeview(failed_frame, columns=columns, show="headings", height=15)
        
        # Configure columns
        self.failed_tree.heading("Timestamp", text="Timestamp")
        self.failed_tree.heading("Error Type", text="Error Type")
        self.failed_tree.heading("Prompt", text="Prompt (first 50 chars)")
        self.failed_tree.heading("Model", text="Model")
        
        self.failed_tree.column("Timestamp", width=150)
        self.failed_tree.column("Error Type", width=120)
        self.failed_tree.column("Prompt", width=300)
        self.failed_tree.column("Model", width=100)
        
        # Scrollbars
        failed_scrollbar_y = ttk.Scrollbar(failed_frame, orient=tk.VERTICAL, 
                                          command=self.failed_tree.yview)
        failed_scrollbar_x = ttk.Scrollbar(failed_frame, orient=tk.HORIZONTAL, 
                                          command=self.failed_tree.xview)
        self.failed_tree.configure(yscrollcommand=failed_scrollbar_y.set,
                                  xscrollcommand=failed_scrollbar_x.set)
        
        self.failed_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        failed_scrollbar_y.grid(row=0, column=1, sticky=(tk.N, tk.S))
        failed_scrollbar_x.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        failed_frame.columnconfigure(0, weight=1)
        failed_frame.rowconfigure(0, weight=1)
    
    def create_successful_prompts_tab(self):
        """Create the successful prompts tab"""
        success_frame = ttk.Frame(self.notebook)
        self.notebook.add(success_frame, text="Successful Prompts")
        
        # Treeview for successful prompts
        columns = ("Timestamp", "Save Method", "Prompt", "Model")
        self.success_tree = ttk.Treeview(success_frame, columns=columns, show="headings", height=15)
        
        # Configure columns
        self.success_tree.heading("Timestamp", text="Timestamp")
        self.success_tree.heading("Save Method", text="Save Method")
        self.success_tree.heading("Prompt", text="Prompt (first 50 chars)")
        self.success_tree.heading("Model", text="Model")
        
        self.success_tree.column("Timestamp", width=150)
        self.success_tree.column("Save Method", width=100)
        self.success_tree.column("Prompt", width=300)
        self.success_tree.column("Model", width=100)
        
        # Scrollbars
        success_scrollbar_y = ttk.Scrollbar(success_frame, orient=tk.VERTICAL, 
                                           command=self.success_tree.yview)
        success_scrollbar_x = ttk.Scrollbar(success_frame, orient=tk.HORIZONTAL, 
                                           command=self.success_tree.xview)
        self.success_tree.configure(yscrollcommand=success_scrollbar_y.set,
                                   xscrollcommand=success_scrollbar_x.set)
        
        self.success_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        success_scrollbar_y.grid(row=0, column=1, sticky=(tk.N, tk.S))
        success_scrollbar_x.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        success_frame.columnconfigure(0, weight=1)
        success_frame.rowconfigure(0, weight=1)
    
    def create_analysis_tab(self):
        """Create the analysis tab"""
        analysis_frame = ttk.Frame(self.notebook)
        self.notebook.add(analysis_frame, text="Analysis")
        
        # Analysis display
        self.analysis_text = tk.Text(analysis_frame, wrap=tk.WORD, height=20, width=80)
        analysis_scrollbar = ttk.Scrollbar(analysis_frame, orient=tk.VERTICAL, 
                                          command=self.analysis_text.yview)
        self.analysis_text.configure(yscrollcommand=analysis_scrollbar.set)
        
        self.analysis_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        analysis_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Export button
        export_btn = ttk.Button(analysis_frame, text="Export Data", 
                               command=self.export_data)
        export_btn.grid(row=1, column=0, pady=(10, 0))
        
        analysis_frame.columnconfigure(0, weight=1)
        analysis_frame.rowconfigure(0, weight=1)
    
    def refresh_all_data(self):
        """Refresh all data in background thread"""
        def refresh_worker():
            try:
                # Update overview
                self.update_overview()
                
                # Update failed prompts
                self.update_failed_prompts()
                
                # Update successful prompts
                self.update_successful_prompts()
                
                # Update analysis
                self.update_analysis()
                
            except Exception as e:
                logger.error(f"Error refreshing analytics data: {e}")
                messagebox.showerror("Error", f"Failed to refresh data: {e}")
        
        # Run in background thread to avoid blocking UI
        threading.Thread(target=refresh_worker, daemon=True).start()
    
    def update_overview(self):
        """Update the overview statistics"""
        try:
            stats = prompt_tracker.get_statistics()
            
            overview_text = f"""
PROMPT ANALYTICS OVERVIEW
{'='*50}

Overall Statistics:
• Total Attempts: {stats.get('total_attempts', 0)}
• Successful Attempts: {stats.get('successful_attempts', 0)}
• Failed Attempts: {stats.get('failed_attempts', 0)}
• Success Rate: {stats.get('success_rate', 0):.1f}%

Recent Activity:
• Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Tips for Improvement:
• Review failed prompts to identify common issues
• Analyze successful prompts to understand what works
• Track your success rate over time
• Export data for detailed analysis
"""
            
            self.stats_text.delete(1.0, tk.END)
            self.stats_text.insert(1.0, overview_text)
            
        except Exception as e:
            logger.error(f"Error updating overview: {e}")
    
    def update_failed_prompts(self):
        """Update the failed prompts list"""
        try:
            # Clear existing items
            for item in self.failed_tree.get_children():
                self.failed_tree.delete(item)
            
            # Get failed prompts
            failed_prompts = prompt_tracker.get_failed_prompts(limit=100)
            
            for prompt_data in failed_prompts:
                timestamp = prompt_data.get('timestamp', 'Unknown')
                error_type = prompt_data.get('error_type', 'unknown')
                prompt = prompt_data.get('prompt', 'N/A')[:50] + "..." if len(prompt_data.get('prompt', '')) > 50 else prompt_data.get('prompt', 'N/A')
                model = prompt_data.get('ai_model', 'unknown')
                
                self.failed_tree.insert("", "end", values=(timestamp, error_type, prompt, model))
                
        except Exception as e:
            logger.error(f"Error updating failed prompts: {e}")
    
    def update_successful_prompts(self):
        """Update the successful prompts list"""
        try:
            # Clear existing items
            for item in self.success_tree.get_children():
                self.success_tree.delete(item)
            
            # Get successful prompts
            successful_prompts = prompt_tracker.get_successful_prompts(limit=100)
            
            for prompt_data in successful_prompts:
                timestamp = prompt_data.get('timestamp', 'Unknown')
                context = prompt_data.get('additional_context', {})
                save_method = "Auto" if context.get('auto_saved') else "Manual"
                prompt = prompt_data.get('prompt', 'N/A')[:50] + "..." if len(prompt_data.get('prompt', '')) > 50 else prompt_data.get('prompt', 'N/A')
                model = prompt_data.get('ai_model', 'unknown')
                
                self.success_tree.insert("", "end", values=(timestamp, save_method, prompt, model))
                
        except Exception as e:
            logger.error(f"Error updating successful prompts: {e}")
    
    def update_analysis(self):
        """Update the analysis text"""
        try:
            analysis = prompt_tracker.analyze_prompt_patterns()
            
            analysis_text = f"""
PROMPT PATTERN ANALYSIS
{'='*50}

Failed Prompts Analysis:
• Count: {analysis.get('failed_prompts', {}).get('count', 0)}
• Average Length: {analysis.get('failed_prompts', {}).get('avg_length', 0):.1f} characters
• Average Words: {analysis.get('failed_prompts', {}).get('avg_word_count', 0):.1f}

Successful Prompts Analysis:
• Count: {analysis.get('successful_prompts', {}).get('count', 0)}
• Average Length: {analysis.get('successful_prompts', {}).get('avg_length', 0):.1f} characters
• Average Words: {analysis.get('successful_prompts', {}).get('avg_word_count', 0):.1f}

Common Error Types:
"""
            
            error_types = analysis.get('failed_prompts', {}).get('common_error_types', {})
            for error_type, count in error_types.items():
                analysis_text += f"• {error_type}: {count}\n"
            
            analysis_text += f"""
Recommendations:
• Focus on prompts that are {analysis.get('successful_prompts', {}).get('avg_length', 0):.0f} characters or less
• Avoid common error patterns shown above
• Use successful prompts as templates for new ones
• Track your improvement over time

Data Export:
• Use the Export Data button to save all data for external analysis
• Export includes detailed prompt data and statistics
"""
            
            self.analysis_text.delete(1.0, tk.END)
            self.analysis_text.insert(1.0, analysis_text)
            
        except Exception as e:
            logger.error(f"Error updating analysis: {e}")
    
    def export_data(self):
        """Export prompt data"""
        try:
            export_file = prompt_tracker.export_prompts()
            if export_file:
                messagebox.showinfo("Export Complete", 
                                  f"Data exported to:\n{export_file}")
            else:
                messagebox.showerror("Export Failed", "Failed to export data")
        except Exception as e:
            logger.error(f"Error exporting data: {e}")
            messagebox.showerror("Export Error", f"Failed to export data: {e}")
    
    def show(self):
        """Show the analytics window"""
        if self.window:
            self.window.deiconify()
            self.window.lift()
            self.window.focus_force()

def show_prompt_analytics(parent=None):
    """Show the prompt analytics window"""
    try:
        analytics_window = PromptAnalyticsWindow(parent)
        analytics_window.show()
        return analytics_window
    except Exception as e:
        logger.error(f"Error showing prompt analytics: {e}")
        messagebox.showerror("Error", f"Failed to open analytics: {e}")
        return None
