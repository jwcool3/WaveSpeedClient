"""
Enhanced Prompt Browser UI Component
For WaveSpeed AI Creative Suite

Modern prompt management interface with categories, search, and visual browsing.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Optional, Callable
from PIL import Image, ImageTk
import os
from core.prompt_manager_core import EnhancedPromptManager, PromptData, CategoryManager
from core.logger import get_logger

logger = get_logger()

class EnhancedPromptBrowser:
    """Modern prompt browser with categories, search, and visual browsing"""
    
    def __init__(self, parent, model_type: str = "universal", on_select: Optional[Callable] = None):
        self.parent = parent
        self.model_type = model_type
        self.on_select = on_select
        self.manager = EnhancedPromptManager()
        self.current_prompts = []
        self.selected_prompt = None
        
        # Create main window
        self.window = tk.Toplevel(parent)
        self.window.title(f"📚 Enhanced Prompt Library - {model_type.title()}")
        self.window.geometry("1000x700")
        self.window.configure(bg='#f8f9fa')
        
        # Make window modal
        self.window.transient(parent)
        self.window.grab_set()
        
        # Center window
        self.center_window()
        
        self.setup_ui()
        self.load_prompts()
        
        # Bind close event
        self.window.protocol("WM_DELETE_WINDOW", self.close)
    
    def center_window(self):
        """Center the window on screen"""
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f"{width}x{height}+{x}+{y}")
    
    def setup_ui(self):
        """Setup the main UI layout"""
        # Main container
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Header section
        self.setup_header(main_frame)
        
        # Content area with sidebar and main view
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True, pady=(15, 0))
        content_frame.columnconfigure(1, weight=1)
        content_frame.rowconfigure(0, weight=1)
        
        # Left sidebar - Categories and filters
        self.setup_sidebar(content_frame)
        
        # Right main area - Prompt list and details
        self.setup_main_area(content_frame)
        
        # Bottom action bar
        self.setup_action_bar(main_frame)
    
    def setup_header(self, parent):
        """Setup header with search and controls"""
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Title
        title_label = ttk.Label(
            header_frame, 
            text="📚 Enhanced Prompt Library", 
            font=('Arial', 16, 'bold')
        )
        title_label.pack(side=tk.LEFT)
        
        # Search frame
        search_frame = ttk.Frame(header_frame)
        search_frame.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(20, 0))
        
        # Search entry
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.on_search_change)
        search_entry = ttk.Entry(
            search_frame, 
            textvariable=self.search_var,
            font=('Arial', 11),
            width=30
        )
        search_entry.pack(side=tk.LEFT, padx=(0, 10))
        
        # Search button
        search_btn = ttk.Button(
            search_frame, 
            text="🔍 Search",
            command=self.perform_search
        )
        search_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Clear search
        clear_btn = ttk.Button(
            search_frame, 
            text="✕ Clear",
            command=self.clear_search
        )
        clear_btn.pack(side=tk.LEFT)
    
    def setup_sidebar(self, parent):
        """Setup left sidebar with categories and filters"""
        sidebar_frame = ttk.LabelFrame(parent, text="📂 Categories & Filters", padding="10")
        sidebar_frame.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.W), padx=(0, 10))
        sidebar_frame.configure(width=250)
        
        # Categories tree
        self.setup_categories_tree(sidebar_frame)
        
        # Filters section
        self.setup_filters(sidebar_frame)
    
    def setup_categories_tree(self, parent):
        """Setup categories tree view"""
        # Categories label
        ttk.Label(parent, text="Categories:", font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=(0, 5))
        
        # Categories tree
        tree_frame = ttk.Frame(parent)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        self.categories_tree = ttk.Treeview(tree_frame, height=8)
        self.categories_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Scrollbar for categories
        cat_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.categories_tree.yview)
        cat_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.categories_tree.configure(yscrollcommand=cat_scrollbar.set)
        
        # Bind selection event
        self.categories_tree.bind('<<TreeviewSelect>>', self.on_category_select)
        
        # Populate categories
        self.populate_categories()
    
    def populate_categories(self):
        """Populate the categories tree"""
        categories = CategoryManager.get_categories()
        
        # Add "All" category
        self.categories_tree.insert('', 'end', 'all', text='📁 All Prompts', tags=('all',))
        
        # Add each category with subcategories
        for category, subcategories in categories.items():
            cat_id = self.categories_tree.insert('', 'end', text=category, tags=(category,))
            
            for subcategory in subcategories:
                self.categories_tree.insert(cat_id, 'end', text=f"  {subcategory}", tags=(category, subcategory))
        
        # Expand all categories
        for item in self.categories_tree.get_children():
            self.categories_tree.see(item)
    
    def setup_filters(self, parent):
        """Setup filter controls"""
        # Filters label
        ttk.Label(parent, text="Filters:", font=('Arial', 10, 'bold')).pack(anchor=tk.W, pady=(0, 5))
        
        # Model type filter
        model_frame = ttk.Frame(parent)
        model_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(model_frame, text="Model:").pack(side=tk.LEFT)
        self.model_var = tk.StringVar(value=self.model_type)
        model_combo = ttk.Combobox(
            model_frame, 
            textvariable=self.model_var,
            values=["universal", "nano_banana", "seededit", "seedream_v4", "wan_22", "seeddance"],
            state="readonly",
            width=15
        )
        model_combo.pack(side=tk.RIGHT)
        model_combo.bind('<<ComboboxSelected>>', self.on_filter_change)
        
        # Rating filter
        rating_frame = ttk.Frame(parent)
        rating_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(rating_frame, text="Min Rating:").pack(side=tk.LEFT)
        self.rating_var = tk.DoubleVar(value=0.0)
        rating_scale = ttk.Scale(
            rating_frame,
            from_=0.0,
            to=5.0,
            variable=self.rating_var,
            orient=tk.HORIZONTAL,
            command=self.on_filter_change
        )
        rating_scale.pack(side=tk.RIGHT, fill=tk.X, expand=True)
        
        # Usage filter
        usage_frame = ttk.Frame(parent)
        usage_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.usage_var = tk.BooleanVar()
        usage_check = ttk.Checkbutton(
            usage_frame,
            text="Recently Used",
            variable=self.usage_var,
            command=self.on_filter_change
        )
        usage_check.pack(anchor=tk.W)
    
    def setup_main_area(self, parent):
        """Setup main area with prompt list and details"""
        main_area_frame = ttk.Frame(parent)
        main_area_frame.grid(row=0, column=1, sticky=(tk.N, tk.S, tk.E, tk.W))
        
        # Prompt list
        self.setup_prompt_list(main_area_frame)
        
        # Prompt details
        self.setup_prompt_details(main_area_frame)
    
    def setup_prompt_list(self, parent):
        """Setup the prompt list view"""
        list_frame = ttk.LabelFrame(parent, text="📝 Prompts", padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Listbox with scrollbar
        list_container = ttk.Frame(list_frame)
        list_container.pack(fill=tk.BOTH, expand=True)
        
        self.prompt_listbox = tk.Listbox(
            list_container,
            font=('Arial', 10),
            selectmode=tk.SINGLE,
            height=12
        )
        self.prompt_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Scrollbar
        list_scrollbar = ttk.Scrollbar(list_container, orient=tk.VERTICAL, command=self.prompt_listbox.yview)
        list_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.prompt_listbox.configure(yscrollcommand=list_scrollbar.set)
        
        # Bind selection
        self.prompt_listbox.bind('<<ListboxSelect>>', self.on_prompt_select)
        self.prompt_listbox.bind('<Double-Button-1>', self.on_prompt_double_click)
    
    def setup_prompt_details(self, parent):
        """Setup prompt details view"""
        details_frame = ttk.LabelFrame(parent, text="📋 Prompt Details", padding="10")
        details_frame.pack(fill=tk.X)
        
        # Details text area
        self.details_text = tk.Text(
            details_frame,
            height=6,
            font=('Arial', 10),
            wrap=tk.WORD,
            state=tk.DISABLED,
            bg='#f8f9fa'
        )
        self.details_text.pack(fill=tk.X, pady=(0, 10))
        
        # Metadata frame
        metadata_frame = ttk.Frame(details_frame)
        metadata_frame.pack(fill=tk.X)
        
        # Metadata labels
        self.metadata_labels = {}
        metadata_items = [
            ("Category:", "category"),
            ("Tags:", "tags"),
            ("Usage:", "usage"),
            ("Rating:", "rating"),
            ("Created:", "created")
        ]
        
        for i, (label_text, key) in enumerate(metadata_items):
            row = i // 2
            col = (i % 2) * 2
            
            ttk.Label(metadata_frame, text=label_text, font=('Arial', 9, 'bold')).grid(
                row=row, column=col, sticky=tk.W, padx=(0, 5), pady=2
            )
            
            self.metadata_labels[key] = ttk.Label(
                metadata_frame, 
                text="", 
                font=('Arial', 9),
                foreground='#666666'
            )
            self.metadata_labels[key].grid(
                row=row, column=col+1, sticky=tk.W, padx=(0, 20), pady=2
            )
    
    def setup_action_bar(self, parent):
        """Setup bottom action bar"""
        action_frame = ttk.Frame(parent)
        action_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Left side - Info
        info_label = ttk.Label(
            action_frame, 
            text="💡 Double-click a prompt to use it, or select and click 'Use Prompt'",
            font=('Arial', 9),
            foreground='#666666'
        )
        info_label.pack(side=tk.LEFT)
        
        # Right side - Buttons
        button_frame = ttk.Frame(action_frame)
        button_frame.pack(side=tk.RIGHT)
        
        # Use prompt button
        self.use_btn = ttk.Button(
            button_frame,
            text="✅ Use Prompt",
            command=self.use_selected_prompt,
            state=tk.DISABLED
        )
        self.use_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Close button
        close_btn = ttk.Button(
            button_frame,
            text="❌ Close",
            command=self.close
        )
        close_btn.pack(side=tk.LEFT)
    
    def load_prompts(self, category: str = "", search_query: str = ""):
        """Load prompts based on current filters"""
        try:
            # Get current filter values
            model_type = self.model_var.get()
            min_rating = self.rating_var.get()
            recent_only = self.usage_var.get()
            
            # Search prompts
            if recent_only:
                self.current_prompts = self.manager.db.get_recent_prompts(model_type=model_type, limit=50)
            else:
                self.current_prompts = self.manager.db.search_prompts(
                    query=search_query,
                    category=category,
                    model_type=model_type,
                    min_rating=min_rating,
                    limit=100
                )
            
            # Update listbox
            self.update_prompt_list()
            
        except Exception as e:
            logger.error(f"Error loading prompts: {e}")
            messagebox.showerror("Error", f"Failed to load prompts: {e}")
    
    def update_prompt_list(self):
        """Update the prompt listbox with current prompts"""
        self.prompt_listbox.delete(0, tk.END)
        
        for prompt in self.current_prompts:
            # Format display text
            display_text = f"{prompt.name}"
            if prompt.category != "General":
                display_text += f" [{prompt.category}]"
            if prompt.usage_count > 0:
                display_text += f" (Used {prompt.usage_count}x)"
            
            self.prompt_listbox.insert(tk.END, display_text)
    
    def on_category_select(self, event):
        """Handle category selection"""
        selection = self.categories_tree.selection()
        if selection:
            item = selection[0]
            tags = self.categories_tree.item(item, 'tags')
            
            if tags and tags[0] == 'all':
                self.load_prompts()
            elif len(tags) >= 1:
                category = tags[0]
                self.load_prompts(category=category)
    
    def on_filter_change(self, *args):
        """Handle filter changes"""
        self.load_prompts()
    
    def on_search_change(self, *args):
        """Handle search text changes"""
        # Debounce search - could be enhanced with actual debouncing
        pass
    
    def perform_search(self):
        """Perform search with current query"""
        query = self.search_var.get().strip()
        self.load_prompts(search_query=query)
    
    def clear_search(self):
        """Clear search and reload all prompts"""
        self.search_var.set("")
        self.load_prompts()
    
    def on_prompt_select(self, event):
        """Handle prompt selection"""
        selection = self.prompt_listbox.curselection()
        if selection:
            index = selection[0]
            if 0 <= index < len(self.current_prompts):
                self.selected_prompt = self.current_prompts[index]
                self.update_prompt_details()
                self.use_btn.config(state=tk.NORMAL)
    
    def on_prompt_double_click(self, event):
        """Handle prompt double-click"""
        self.use_selected_prompt()
    
    def update_prompt_details(self):
        """Update prompt details display"""
        if not self.selected_prompt:
            return
        
        prompt = self.selected_prompt
        
        # Update details text
        self.details_text.config(state=tk.NORMAL)
        self.details_text.delete(1.0, tk.END)
        self.details_text.insert(1.0, prompt.content)
        self.details_text.config(state=tk.DISABLED)
        
        # Update metadata
        self.metadata_labels["category"].config(text=f"{prompt.category} > {prompt.subcategory}")
        self.metadata_labels["tags"].config(text=", ".join(prompt.tags) if prompt.tags else "None")
        self.metadata_labels["usage"].config(text=f"{prompt.usage_count} times")
        self.metadata_labels["rating"].config(text=f"{prompt.rating:.1f}/5.0")
        
        # Format created date
        if prompt.created_date:
            try:
                from datetime import datetime
                created_dt = datetime.fromisoformat(prompt.created_date)
                formatted_date = created_dt.strftime("%Y-%m-%d %H:%M")
                self.metadata_labels["created"].config(text=formatted_date)
            except:
                self.metadata_labels["created"].config(text=prompt.created_date)
        else:
            self.metadata_labels["created"].config(text="Unknown")
    
    def use_selected_prompt(self):
        """Use the selected prompt"""
        if self.selected_prompt and self.on_select:
            # Record usage
            self.manager.db.record_usage(
                self.selected_prompt.id, 
                self.model_type
            )
            
            # Call the callback
            self.on_select(self.selected_prompt.content)
            
            # Close the browser
            self.close()
    
    def close(self):
        """Close the browser"""
        self.window.destroy()


def show_enhanced_prompt_browser(parent, model_type: str = "universal", on_select: Optional[Callable] = None):
    """Show the enhanced prompt browser dialog"""
    browser = EnhancedPromptBrowser(parent, model_type, on_select)
    return browser


# Example usage and testing
if __name__ == "__main__":
    # Test the browser
    root = tk.Tk()
    root.title("Test Enhanced Prompt Browser")
    
    def on_prompt_selected(prompt_content):
        print(f"Selected prompt: {prompt_content[:100]}...")
    
    def show_browser():
        show_enhanced_prompt_browser(root, "nano_banana", on_prompt_selected)
    
    ttk.Button(root, text="Show Enhanced Prompt Browser", command=show_browser).pack(pady=20)
    
    root.mainloop()
