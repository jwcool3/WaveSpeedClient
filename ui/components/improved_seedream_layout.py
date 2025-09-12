"""
Improved Seedream V4 Tab Layout - Fixing All Issues
1. Two-column structure eliminates vertical scrolling
2. Compact horizontal settings (1/3 the height)  
3. Apply button directly under prompt
4. Collapsible advanced sections
5. Large dynamic preview with minimal margins
6. No wasted horizontal space
7. ENHANCED: Unified status console and keyboard shortcuts
"""

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os
import threading
import asyncio
from ui.components.unified_status_console import UnifiedStatusConsole
from ui.components.keyboard_manager import KeyboardManager
from ui.components.ai_chat_integration_helper import AIChatMixin
from core.logger import get_logger

logger = get_logger()


class ImprovedSeedreamLayout(AIChatMixin):
    """Improved Seedream V4 layout with efficient space usage and better UX"""
    
    def __init__(self, parent_frame, api_client=None, tab_instance=None):
        self.parent_frame = parent_frame
        self.api_client = api_client
        self.tab_instance = tab_instance
        self.selected_image_path = None
        self.result_image_path = None
        self.result_url = None
        self.current_task_id = None
        self.tab_name = "Seedream V4"  # For AI integration
        
        # Settings variables
        self.width_var = tk.IntVar(value=1024)
        self.height_var = tk.IntVar(value=1024)
        self.seed_var = tk.StringVar(value="-1")
        self.sync_mode_var = tk.BooleanVar(value=False)
        self.base64_var = tk.BooleanVar(value=False)
        
        # Aspect ratio locking
        self.aspect_lock_var = tk.BooleanVar(value=False)
        self.locked_aspect_ratio = None
        
        # Size presets
        self.size_presets = [
            ("1K", 1024, 1024),
            ("2K", 2048, 2048), 
            ("4K", 3840, 2160),
            ("Square", 1024, 1024),
            ("Portrait", 768, 1024),
            ("Landscape", 1024, 768)
        ]
        
        # Enhanced components
        self.status_console = None
        self.keyboard_manager = None
        
        self.setup_layout()
        self.setup_enhanced_features()
        self.setup_learning_components()
    
    def setup_layout(self):
        """Setup the improved 2-column layout"""
        
        # Main container
        main_container = ttk.Frame(self.parent_frame)
        main_container.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        
        # Configure grid - 2 columns with no wasted space
        main_container.columnconfigure(0, weight=1, minsize=380)  # Left: Controls (slightly wider for settings)
        main_container.columnconfigure(1, weight=2, minsize=520)  # Right: Images (2x weight)
        main_container.rowconfigure(0, weight=1)
        
        # Left Column - Compact Controls
        self.setup_left_column(main_container)
        
        # Right Column - Large Image Display  
        self.setup_right_column(main_container)
    
    def setup_left_column(self, parent):
        """Setup left column with logical flow and compact sections"""
        left_frame = ttk.Frame(parent, padding="8")
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 4))
        left_frame.columnconfigure(0, weight=1)
        
        # Configure rows to eliminate vertical scrolling
        left_frame.rowconfigure(0, weight=0)  # Image input - compact
        left_frame.rowconfigure(1, weight=0)  # Settings - MUCH more compact
        left_frame.rowconfigure(2, weight=0)  # Prompt section - compact  
        left_frame.rowconfigure(3, weight=0)  # Primary action - prominent
        left_frame.rowconfigure(4, weight=0)  # Advanced sections - collapsible
        left_frame.rowconfigure(5, weight=0)  # Status console - professional feedback
        left_frame.rowconfigure(6, weight=1)  # Spacer
        left_frame.rowconfigure(7, weight=0)  # Secondary actions - bottom
        
        # 1. COMPACT IMAGE INPUT
        self.setup_compact_image_input(left_frame)
        
        # 2. SUPER COMPACT SETTINGS (key improvement!)
        self.setup_compact_settings(left_frame)
        
        # 3. PROMPT SECTION
        self.setup_prompt_section(left_frame)
        
        # 4. PRIMARY ACTION (right under prompt!)
        self.setup_primary_action(left_frame)
        
        # 5. COLLAPSIBLE ADVANCED SECTIONS
        self.setup_advanced_sections(left_frame)
        
        # 6. STATUS CONSOLE (professional feedback)
        self.setup_status_console(left_frame)
        
        # 7. SPACER
        spacer = ttk.Frame(left_frame)
        spacer.grid(row=6, column=0, sticky="nsew")
        
        # 8. SECONDARY ACTIONS (at bottom)
        self.setup_secondary_actions(left_frame)
    
    def setup_compact_image_input(self, parent):
        """Very compact image input section"""
        input_frame = ttk.LabelFrame(parent, text="📥 Input Image", padding="6")
        input_frame.grid(row=0, column=0, sticky="ew", pady=(0, 6))
        input_frame.columnconfigure(1, weight=1)
        
        # Thumbnail + Info in one row (same as SeedEdit)
        self.thumbnail_label = tk.Label(
            input_frame,
            text="📁",
            width=8, height=4,
            bg='#f5f5f5',
            relief='solid',
            borderwidth=1,
            cursor="hand2",
            font=('Arial', 10)
        )
        self.thumbnail_label.grid(row=0, column=0, padx=(0, 8), rowspan=2)
        self.thumbnail_label.bind("<Button-1>", lambda e: self.browse_image())
        
        # Image info
        self.image_name_label = ttk.Label(
            input_frame,
            text="No image selected",
            font=('Arial', 9, 'bold'),
            foreground="gray"
        )
        self.image_name_label.grid(row=0, column=1, sticky="w")
        
        info_frame = ttk.Frame(input_frame)
        info_frame.grid(row=1, column=1, sticky="ew")
        
        self.image_size_label = ttk.Label(
            info_frame,
            text="",
            font=('Arial', 8),
            foreground="gray"
        )
        self.image_size_label.pack(side=tk.LEFT)
        
        browse_btn = ttk.Button(
            info_frame,
            text="Browse",
            command=self.browse_image,
            width=8
        )
        browse_btn.pack(side=tk.RIGHT)
    
    def setup_compact_settings(self, parent):
        """SUPER compact settings - key improvement! 1/3 the height"""
        settings_frame = ttk.LabelFrame(parent, text="⚙️ Settings", padding="6")
        settings_frame.grid(row=1, column=0, sticky="ew", pady=(0, 6))
        settings_frame.columnconfigure(1, weight=1)
        settings_frame.columnconfigure(3, weight=1)
        
        # Row 1: Width + Height (side by side with sliders)
        ttk.Label(settings_frame, text="Size:", font=('Arial', 9, 'bold')).grid(
            row=0, column=0, sticky="w", columnspan=4, pady=(0, 2)
        )
        
        # Width
        ttk.Label(settings_frame, text="W:", font=('Arial', 8)).grid(
            row=1, column=0, sticky="w"
        )
        
        width_frame = ttk.Frame(settings_frame)
        width_frame.grid(row=1, column=1, sticky="ew", padx=(2, 8))
        
        self.width_scale = ttk.Scale(
            width_frame,
            from_=256, to=4096,
            variable=self.width_var,
            orient=tk.HORIZONTAL,
            length=80,
            command=self.on_size_changed
        )
        self.width_scale.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.width_entry = ttk.Entry(
            width_frame,
            textvariable=self.width_var,
            width=5,
            font=('Arial', 8)
        )
        self.width_entry.pack(side=tk.RIGHT, padx=(2, 0))
        
        # Add validation for aspect ratio locking on entry changes
        self.width_var.trace('w', self._on_entry_change)
        
        # Height  
        ttk.Label(settings_frame, text="H:", font=('Arial', 8)).grid(
            row=1, column=2, sticky="w"
        )
        
        height_frame = ttk.Frame(settings_frame)
        height_frame.grid(row=1, column=3, sticky="ew")
        
        self.height_scale = ttk.Scale(
            height_frame,
            from_=256, to=4096,
            variable=self.height_var,
            orient=tk.HORIZONTAL,
            length=80,
            command=self.on_size_changed
        )
        self.height_scale.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.height_entry = ttk.Entry(
            height_frame,
            textvariable=self.height_var,
            width=5,
            font=('Arial', 8)
        )
        self.height_entry.pack(side=tk.RIGHT, padx=(2, 0))
        
        # Add validation for aspect ratio locking on height entry changes
        self.height_var.trace('w', self._on_entry_change)
        
        # Row 2: Size presets (grid layout - much more compact!)
        preset_frame = ttk.Frame(settings_frame)
        preset_frame.grid(row=2, column=0, columnspan=4, sticky="ew", pady=(4, 2))
        
        # Preset buttons in a 3x2 grid
        for i, (name, width, height) in enumerate(self.size_presets):
            btn = ttk.Button(
                preset_frame,
                text=name,
                command=lambda w=width, h=height: self.set_size_preset(w, h),
                width=6
            )
            btn.grid(row=i//3, column=i%3, padx=1, pady=1, sticky="ew")
        
        # Configure preset frame columns
        for i in range(3):
            preset_frame.columnconfigure(i, weight=1)
        
        # Row 3: Seed + Options (horizontal)
        ttk.Label(settings_frame, text="Seed:", font=('Arial', 8)).grid(
            row=3, column=0, sticky="w", pady=(4, 0)
        )
        
        seed_entry = ttk.Entry(
            settings_frame,
            textvariable=self.seed_var,
            width=8,
            font=('Arial', 8)
        )
        seed_entry.grid(row=3, column=1, sticky="w", pady=(4, 0))
        
        # Lock aspect ratio button (starts unlocked)
        self.lock_aspect_btn = ttk.Button(
            settings_frame,
            text="🔓",
            width=3,
            command=self.toggle_aspect_lock
        )
        self.lock_aspect_btn.grid(row=3, column=2, sticky="w", padx=(8, 0), pady=(4, 0))
        
        # Auto-resolution button
        auto_btn = ttk.Button(
            settings_frame,
            text="Auto",
            width=6,
            command=self.auto_set_resolution
        )
        auto_btn.grid(row=3, column=3, sticky="e", pady=(4, 0))
    
    def setup_prompt_section(self, parent):
        """Compact prompt section"""
        prompt_frame = ttk.LabelFrame(parent, text="✏️ Transformation Prompt", padding="6")
        prompt_frame.grid(row=2, column=0, sticky="ew", pady=(0, 6))
        prompt_frame.columnconfigure(0, weight=1)
        
        # Preset management (horizontal row)
        preset_frame = ttk.Frame(prompt_frame)
        preset_frame.grid(row=0, column=0, sticky="ew", pady=(0, 4))
        preset_frame.columnconfigure(0, weight=1)
        
        # Preset dropdown
        self.preset_var = tk.StringVar()
        self.preset_combo = ttk.Combobox(
            preset_frame,
            textvariable=self.preset_var,
            font=('Arial', 9),
            width=20
        )
        self.preset_combo.grid(row=0, column=0, sticky="ew", padx=(0, 4))
        self.preset_combo.bind('<<ComboboxSelected>>', self.load_preset)
        
        # Preset buttons (small) - AI integration target
        self.ai_chat_container = ttk.Frame(preset_frame)
        self.ai_chat_container.grid(row=0, column=1)
        
        ttk.Button(self.ai_chat_container, text="💾", width=3, command=self.save_preset).pack(side=tk.LEFT, padx=1)
        ttk.Button(self.ai_chat_container, text="🎲", width=3, command=self.load_sample).pack(side=tk.LEFT, padx=1)
        ttk.Button(self.ai_chat_container, text="🤖", width=3, command=self.improve_with_ai).pack(side=tk.LEFT, padx=1)
        mild_btn = ttk.Button(self.ai_chat_container, text="🔥", width=3, command=self.generate_mild_examples)
        mild_btn.pack(side=tk.LEFT, padx=1)
        # Add tooltip for the mild examples button
        self.create_tooltip(mild_btn, "Generate 5 mild filter training examples\nAutomatically analyzes image first")
        
        moderate_btn = ttk.Button(self.ai_chat_container, text="⚡", width=3, command=self.generate_moderate_examples)
        moderate_btn.pack(side=tk.LEFT, padx=1)
        # Add tooltip for the moderate examples button
        self.create_tooltip(moderate_btn, "Generate 5 sophisticated moderate examples\nUses indirect language combinations")
    
    def generate_mild_examples(self):
        """Generate 5 mild filter training examples with automatic image analysis"""
        if not self.selected_image_path:
            self.show_tooltip("❌ Please select an image first")
            return
        
        self.show_tooltip("🔥 Starting mild examples generation...")
        
        # Start background thread for mild examples generation
        thread = threading.Thread(target=self._generate_mild_examples_thread, daemon=True)
        thread.start()
    
    def generate_moderate_examples(self):
        """Generate 5 sophisticated moderate examples with automatic image analysis"""
        if not self.selected_image_path:
            self.show_tooltip("❌ Please select an image first")
            return
        
        self.show_tooltip("⚡ Starting sophisticated moderate examples generation...")
        
        # Start background thread for moderate examples generation
        thread = threading.Thread(target=self._generate_moderate_examples_thread, daemon=True)
        thread.start()
    
    def _generate_mild_examples_thread(self):
        """Background thread for generating mild examples"""
        try:
            from core.ai_prompt_advisor import get_ai_advisor
            
            ai_advisor = get_ai_advisor()
            if not ai_advisor.is_available():
                self.parent_frame.after(0, lambda: self.show_tooltip("❌ AI service not available"))
                return
            
            # Step 1: Analyze image for filter training (detailed analysis)
            self.parent_frame.after(0, lambda: self.show_tooltip("🔍 Analyzing image..."))
            description = asyncio.run(ai_advisor.describe_image(self.selected_image_path, detailed_analysis=True))
            
            if not description or "error" in description.lower():
                self.parent_frame.after(0, lambda: self.show_tooltip("❌ Image analysis failed"))
                return
            
            # Step 2: Generate 5 mild examples using optimized method
            self.parent_frame.after(0, lambda: self.show_tooltip("🔥 Generating 5 mild examples..."))
            mild_examples = asyncio.run(ai_advisor.generate_mild_examples_only(description, count=5))
            
            if not mild_examples:
                # Final fallback using vocabulary bank
                from core.filter_vocabulary_bank import filter_vocab
                import re
                
                mild_examples = []
                for i in range(5):
                    # Extract subject and clothing from description
                    subject_match = re.search(r'\b(woman|man|girl|lady|gentleman)\b', description.lower())
                    clothing_match = re.search(r'\b(dress|gown|shirt|top|blouse|outfit|clothing|garment|attire)\b', description.lower())
                    
                    if subject_match and clothing_match:
                        subject = subject_match.group(1)
                        clothing = clothing_match.group(1)
                        mild_example = filter_vocab.generate_varied_mild_prompt(subject, clothing)
                        mild_examples.append(mild_example)
                    else:
                        # Use generic fallbacks with varied vocabulary
                        generic_examples = [
                            "Convert outfit to revealing swimwear; preserve identity",
                            "Transform attire to micro bikini; maintain features", 
                            "Change clothing to skimpy two-piece; keep expression",
                            "Alter garment to minimal coverage; retain appearance",
                            "Switch to tiny string bikini; hold facial features"
                        ]
                        mild_examples.append(generic_examples[i] if i < len(generic_examples) else generic_examples[0])
            
            # Show results in UI thread
            self.parent_frame.after(0, lambda: self._display_mild_examples(mild_examples))
            
        except Exception as e:
            logger.error(f"Error in mild examples thread: {e}")
            self.parent_frame.after(0, lambda: self.show_tooltip(f"❌ Generation failed: {str(e)}"))
    
    def _generate_moderate_examples_thread(self):
        """Background thread for generating sophisticated moderate examples"""
        try:
            from core.ai_prompt_advisor import get_ai_advisor
            
            ai_advisor = get_ai_advisor()
            if not ai_advisor.is_available():
                self.parent_frame.after(0, lambda: self.show_tooltip("❌ AI service not available"))
                return
            
            # Step 1: Analyze image for filter training (detailed analysis)
            self.parent_frame.after(0, lambda: self.show_tooltip("🔍 Analyzing image for moderate examples..."))
            description = asyncio.run(ai_advisor.describe_image(self.selected_image_path, detailed_analysis=True))
            
            if not description or "error" in description.lower():
                self.parent_frame.after(0, lambda: self.show_tooltip("❌ Image analysis failed"))
                return
            
            # Step 2: Generate 5 sophisticated moderate examples
            self.parent_frame.after(0, lambda: self.show_tooltip("⚡ Generating sophisticated indirect prompts..."))
            moderate_examples = asyncio.run(ai_advisor.generate_moderate_examples_only(description, count=5))
            
            # Show results in UI thread
            self.parent_frame.after(0, lambda: self._display_moderate_examples(moderate_examples))
            
        except Exception as e:
            logger.error(f"Error in moderate examples thread: {e}")
            self.parent_frame.after(0, lambda: self.show_tooltip(f"❌ Generation failed: {str(e)}"))
    
    def _display_mild_examples(self, examples):
        """Display generated mild examples in a popup window"""
        try:
            # Create popup window
            popup = tk.Toplevel(self.parent_frame)
            popup.title("🔥 Filter Training - Mild Examples")
            popup.geometry("700x500")
            popup.resizable(True, True)
            
            # Main frame with scrollbar
            main_frame = ttk.Frame(popup)
            main_frame.pack(fill="both", expand=True, padx=10, pady=10)
            
            # Title with count
            title_label = ttk.Label(main_frame, text=f"🔥 Filter Training - {len(examples)} Mild Examples", font=("Arial", 12, "bold"))
            title_label.pack(pady=(0, 5))
            
            # Subtitle
            subtitle_label = ttk.Label(main_frame, text="Generated using comprehensive vocabulary bank and varied terminology", font=("Arial", 9), foreground="gray")
            subtitle_label.pack(pady=(0, 10))
            
            # Scrollable frame for examples
            canvas = tk.Canvas(main_frame, highlightthickness=0)
            scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
            scrollable_frame = ttk.Frame(canvas)
            
            scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            # Pack scrollbar and canvas
            scrollbar.pack(side="right", fill="y")
            canvas.pack(side="left", fill="both", expand=True)
            
            # Add examples to scrollable frame
            for i, example in enumerate(examples, 1):
                # Example frame
                example_frame = ttk.LabelFrame(scrollable_frame, text=f"Example {i}", padding="8")
                example_frame.pack(fill="x", padx=5, pady=3)
                
                # Example text (selectable)
                example_text = tk.Text(example_frame, height=3, wrap=tk.WORD, font=("Arial", 10))
                example_text.pack(fill="x")
                example_text.insert("1.0", example)
                example_text.configure(state='normal')  # Allow selection but not editing
                
                # Copy button
                copy_btn = ttk.Button(example_frame, text="📋 Copy", 
                                    command=lambda ex=example: popup.clipboard_clear() or popup.clipboard_append(ex) or self.show_tooltip("📋 Copied to clipboard"))
                copy_btn.pack(anchor="e", pady=(5, 0))
            
            # Bind mousewheel to canvas
            def on_mousewheel(event):
                canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            canvas.bind_all("<MouseWheel>", on_mousewheel)
            
            # Close button
            close_btn = ttk.Button(popup, text="Close", command=popup.destroy)
            close_btn.pack(pady=5)
            
            # Focus on popup
            popup.focus_set()
            popup.grab_set()
            
        except Exception as e:
            logger.error(f"Error displaying mild examples: {e}")
            self.show_tooltip(f"❌ Error: {str(e)}")
    
    def _display_moderate_examples(self, examples):
        """Display generated moderate examples in a popup window"""
        try:
            # Create popup window
            popup = tk.Toplevel(self.parent_frame)
            popup.title("⚡ Sophisticated Moderate Examples")
            popup.geometry("800x600")
            popup.resizable(True, True)
            
            # Main frame with scrollbar
            main_frame = ttk.Frame(popup)
            main_frame.pack(fill="both", expand=True, padx=10, pady=10)
            
            # Title with count
            title_label = ttk.Label(main_frame, text=f"⚡ Filter Training - {len(examples)} Moderate Examples", font=("Arial", 12, "bold"))
            title_label.pack(pady=(0, 5))
            
            # Subtitle explaining the approach
            subtitle_label = ttk.Label(main_frame, text="Sophisticated indirect language combinations designed to confuse models", font=("Arial", 9), foreground="gray")
            subtitle_label.pack(pady=(0, 5))
            
            info_label = ttk.Label(main_frame, text="These prompts use word combinations to imply harmful content without explicit terms", font=("Arial", 8), foreground="#666")
            info_label.pack(pady=(0, 10))
            
            # Scrollable frame for examples
            canvas = tk.Canvas(main_frame, highlightthickness=0)
            scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
            scrollable_frame = ttk.Frame(canvas)
            
            scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            # Pack scrollbar and canvas
            scrollbar.pack(side="right", fill="y")
            canvas.pack(side="left", fill="both", expand=True)
            
            # Add examples to scrollable frame
            for i, example in enumerate(examples, 1):
                # Example frame with more space for longer prompts
                example_frame = ttk.LabelFrame(scrollable_frame, text=f"Moderate Example {i}", padding="8")
                example_frame.pack(fill="x", padx=5, pady=4)
                
                # Example text (larger for longer moderate prompts)
                example_text = tk.Text(example_frame, height=4, wrap=tk.WORD, font=("Arial", 10))
                example_text.pack(fill="x")
                example_text.insert("1.0", example)
                example_text.configure(state='normal')  # Allow selection
                
                # Buttons frame
                buttons_frame = ttk.Frame(example_frame)
                buttons_frame.pack(fill="x", pady=(5, 0))
                
                # Copy button
                copy_btn = ttk.Button(buttons_frame, text="📋 Copy", 
                                    command=lambda ex=example: popup.clipboard_clear() or popup.clipboard_append(ex) or self.show_tooltip("📋 Copied to clipboard"))
                copy_btn.pack(side="left")
                
                # Analysis button (shows breakdown of indirect techniques)
                analysis_btn = ttk.Button(buttons_frame, text="🔍 Analyze", 
                                        command=lambda ex=example: self._show_moderate_analysis(ex))
                analysis_btn.pack(side="left", padx=(5, 0))
            
            # Bind mousewheel to canvas
            def on_mousewheel(event):
                canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            canvas.bind_all("<MouseWheel>", on_mousewheel)
            
            # Close button
            close_btn = ttk.Button(popup, text="Close", command=popup.destroy)
            close_btn.pack(pady=5)
            
            # Focus on popup
            popup.focus_set()
            popup.grab_set()
            
        except Exception as e:
            logger.error(f"Error displaying moderate examples: {e}")
            self.show_tooltip(f"❌ Error: {str(e)}")
    
    def _show_moderate_analysis(self, example):
        """Show analysis of indirect techniques used in moderate example"""
        try:
            analysis_popup = tk.Toplevel(self.parent_frame)
            analysis_popup.title("🔍 Moderate Example Analysis")
            analysis_popup.geometry("600x400")
            
            frame = ttk.Frame(analysis_popup, padding="10")
            frame.pack(fill="both", expand=True)
            
            # Title
            ttk.Label(frame, text="Indirect Language Techniques Analysis", font=("Arial", 12, "bold")).pack(pady=(0, 10))
            
            # Example text
            ttk.Label(frame, text="Example:", font=("Arial", 10, "bold")).pack(anchor="w")
            example_text = tk.Text(frame, height=3, wrap=tk.WORD, font=("Arial", 10))
            example_text.pack(fill="x", pady=(2, 10))
            example_text.insert("1.0", example)
            example_text.configure(state='disabled')
            
            # Analysis
            ttk.Label(frame, text="Techniques Identified:", font=("Arial", 10, "bold")).pack(anchor="w")
            
            analysis_text = tk.Text(frame, wrap=tk.WORD, font=("Arial", 9))
            analysis_text.pack(fill="both", expand=True, pady=(2, 10))
            
            # Simple keyword-based analysis
            techniques = []
            if "artistic" in example.lower() or "art" in example.lower():
                techniques.append("• Artistic Justification: Uses art context to legitimize request")
            if "professional" in example.lower() or "gallery" in example.lower():
                techniques.append("• Professional Context: Claims professional/academic purpose")
            if any(word in example.lower() for word in ["absence", "without", "free", "liberated"]):
                techniques.append("• Removal Implication: Implies removal without explicit terms")
            if any(word in example.lower() for word in ["transparency", "clear", "minimal", "reduced"]):
                techniques.append("• Coverage Reduction: Suggests minimal coverage indirectly")
            if any(word in example.lower() for word in ["maintaining", "preserving", "keeping"]):
                techniques.append("• Identity Preservation: Maintains specific appearance features")
            
            if not techniques:
                techniques.append("• Complex Language Combination: Uses sophisticated vocabulary to confuse filters")
            
            analysis_content = "This moderate example uses the following indirect techniques:\n\n" + "\n".join(techniques)
            analysis_content += "\n\nThese techniques are designed to bypass content filters by avoiding explicit harmful terms while still communicating the intended meaning through implication and context."
            
            analysis_text.insert("1.0", analysis_content)
            analysis_text.configure(state='disabled')
            
            # Close button
            ttk.Button(analysis_popup, text="Close", command=analysis_popup.destroy).pack(pady=5)
            
            # Focus
            analysis_popup.focus_set()
            analysis_popup.grab_set()
            
        except Exception as e:
            logger.error(f"Error showing analysis: {e}")
            self.show_tooltip(f"❌ Analysis error: {str(e)}")
        
        # Prompt text (compact)
        self.prompt_text = tk.Text(
            prompt_frame,
            height=4,  # Compact height
            wrap=tk.WORD,
            font=('Arial', 10),
            relief='solid',
            borderwidth=1
        )
        self.prompt_text.grid(row=1, column=0, sticky="ew", pady=(4, 0))
        
        # Placeholder text
        self.prompt_text.insert("1.0", "Describe the transformation you want to apply to the image...")
        self.prompt_text.bind("<FocusIn>", self.clear_placeholder)
        self.prompt_text.bind("<FocusOut>", self.add_placeholder)
    
    def setup_primary_action(self, parent):
        """Primary action button RIGHT under prompt - key UX improvement!"""
        action_frame = ttk.Frame(parent)
        action_frame.grid(row=3, column=0, sticky="ew", pady=6)
        action_frame.columnconfigure(0, weight=1)
        
        # PROMINENT primary action button
        self.primary_btn = ttk.Button(
            action_frame,
            text="🌟 Apply Seedream V4",
            command=self.process_seedream,
            style='Accent.TButton'
        )
        self.primary_btn.grid(row=0, column=0, sticky="ew")
        
        # Status indicator right below
        self.status_label = ttk.Label(
            action_frame,
            text="Ready for transformation",
            font=('Arial', 9),
            foreground="green"
        )
        self.status_label.grid(row=1, column=0, pady=(4, 0))
        
        # Progress bar (hidden by default)
        self.progress_bar = ttk.Progressbar(
            action_frame,
            mode='indeterminate'
        )
        # Don't grid it yet - only show when processing
    
    def setup_advanced_sections(self, parent):
        """Collapsible advanced sections - saves lots of space!"""
        advanced_frame = ttk.Frame(parent)
        advanced_frame.grid(row=4, column=0, sticky="ew", pady=(0, 6))
        advanced_frame.columnconfigure(0, weight=1)
        
        # AI Assistant (collapsible)
        self.ai_section = self.create_collapsible_section(
            advanced_frame, 
            "🤖 AI Assistant", 
            row=0
        )
        
        # Add AI assistant content
        ai_btn = ttk.Button(
            self.ai_section['content'],
            text="✨ Improve Prompt with AI",
            command=self.improve_with_ai,
            width=20
        )
        ai_btn.pack(pady=2)
        
        filter_btn = ttk.Button(
            self.ai_section['content'],
            text="🛡️ Filter Training Mode",
            command=self.filter_training,
            width=20
        )
        filter_btn.pack(pady=2)
        
        # Learning insights button
        learning_btn = ttk.Button(
            self.ai_section['content'],
            text="🧠 Learning Insights",
            command=self.show_learning_panel,
            width=20
        )
        learning_btn.pack(pady=2)
        
        # Quality rating button (enabled after generation)
        self.rating_btn = ttk.Button(
            self.ai_section['content'],
            text="⭐ Rate Last Result",
            command=self.show_quality_rating,
            width=20,
            state="disabled"
        )
        self.rating_btn.pack(pady=2)
        
        # Advanced Options (collapsible)
        self.options_section = self.create_collapsible_section(
            advanced_frame,
            "🔧 Advanced Options",
            row=1
        )
        
        # Add advanced options content
        options_content = ttk.Frame(self.options_section['content'])
        options_content.pack(fill=tk.X, pady=2)
        options_content.columnconfigure(1, weight=1)
        
        ttk.Checkbutton(
            options_content,
            text="Sync Mode",
            variable=self.sync_mode_var
        ).grid(row=0, column=0, sticky="w")
        
        ttk.Checkbutton(
            options_content,
            text="Base64 Output",
            variable=self.base64_var
        ).grid(row=0, column=1, sticky="w", padx=(10, 0))
        
        # Progress Log (collapsible)
        self.log_section = self.create_collapsible_section(
            advanced_frame,
            "📊 Progress Log",
            row=2
        )
        
        # Add log content
        self.log_text = tk.Text(
            self.log_section['content'],
            height=4,
            width=1,
            font=('Courier', 8),
            bg='#f8f8f8',
            state=tk.DISABLED
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, pady=2)
    
    def create_collapsible_section(self, parent, title, row):
        """Create a collapsible section"""
        section_frame = ttk.Frame(parent)
        section_frame.grid(row=row, column=0, sticky="ew", pady=1)
        section_frame.columnconfigure(1, weight=1)
        
        # Header with toggle button
        toggle_btn = ttk.Button(
            section_frame,
            text="▶",
            width=3,
            command=lambda: self.toggle_section(section_frame, toggle_btn)
        )
        toggle_btn.grid(row=0, column=0, sticky="w")
        
        title_label = ttk.Label(
            section_frame,
            text=title,
            font=('Arial', 9, 'bold')
        )
        title_label.grid(row=0, column=1, sticky="w", padx=(4, 0))
        
        # Content frame (initially hidden)
        content_frame = ttk.Frame(section_frame)
        # Don't grid it yet - will be shown/hidden by toggle
        
        return {
            'frame': section_frame,
            'toggle': toggle_btn,
            'content': content_frame,
            'expanded': False
        }
    
    def toggle_section(self, section_frame, toggle_btn):
        """Toggle collapsible section"""
        # Find the section data
        section_data = None
        for section in [self.ai_section, self.options_section, self.log_section]:
            if section['toggle'] == toggle_btn:
                section_data = section
                break
        
        if not section_data:
            return
        
        if section_data['expanded']:
            # Collapse
            section_data['content'].grid_remove()
            toggle_btn.config(text="▶")
            section_data['expanded'] = False
        else:
            # Expand
            section_data['content'].grid(row=1, column=0, columnspan=2, sticky="ew", padx=(20, 0), pady=(2, 0))
            toggle_btn.config(text="▼")
            section_data['expanded'] = True
    
    def setup_secondary_actions(self, parent):
        """Compact secondary actions at bottom"""
        secondary_frame = ttk.LabelFrame(parent, text="🔧 Tools", padding="4")
        secondary_frame.grid(row=7, column=0, sticky="ew")
        secondary_frame.columnconfigure(0, weight=1)
        secondary_frame.columnconfigure(1, weight=1)
        
        # Row 1: Clear and Sample
        ttk.Button(
            secondary_frame,
            text="🧹 Clear",
            command=self.clear_all,
            width=10
        ).grid(row=0, column=0, sticky="ew", padx=(0, 1), pady=1)
        
        ttk.Button(
            secondary_frame,
            text="🎲 Sample",
            command=self.load_sample,
            width=10
        ).grid(row=0, column=1, sticky="ew", padx=(1, 0), pady=1)
        
        # Row 2: Save and Load
        ttk.Button(
            secondary_frame,
            text="💾 Save",
            command=self.save_result,
            width=10
        ).grid(row=1, column=0, sticky="ew", padx=(0, 1), pady=1)
        
        ttk.Button(
            secondary_frame,
            text="📂 Load",
            command=self.load_result,
            width=10
        ).grid(row=1, column=1, sticky="ew", padx=(1, 0), pady=1)
    
    def setup_status_console(self, parent):
        """Setup unified status console for professional feedback"""
        self.status_console = UnifiedStatusConsole(
            parent, 
            title="📊 Status", 
            height=3  # Compact height for Seedream V4
        )
        self.status_console.grid(row=5, column=0, sticky="ew", pady=(0, 4))
        self.status_console.log_ready("Seedream V4")
    
    def setup_enhanced_features(self):
        """Setup keyboard manager and enhanced functionality"""
        # Setup keyboard manager
        self.keyboard_manager = KeyboardManager(self.parent_frame, "Seedream V4")
        
        # Register primary action (will be connected by tab)
        # self.keyboard_manager.register_primary_action(self.process_seedream, self.apply_btn)
        
        # Register file operations (will be connected by tab)
        # self.keyboard_manager.register_file_actions(
        #     open_file=self.browse_image,
        #     save_result=self.save_result,
        #     clear_all=self.clear_all
        # )
        
        # Register AI actions (will be connected by tab)
        # self.keyboard_manager.register_ai_actions(
        #     improve_callback=self.improve_with_ai,
        #     filter_callback=self.filter_training,
        #     chat_callback=self.ai_chat
        # )
    
    def setup_right_column(self, parent):
        """Setup right column with large dynamic image display"""
        right_frame = ttk.Frame(parent, padding="4")
        right_frame.grid(row=0, column=1, sticky="nsew", padx=(4, 0))
        right_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(1, weight=1)
        
        # Image viewing controls
        self.setup_image_controls(right_frame)
        
        # Large image display
        self.setup_image_display(right_frame)
    
    def setup_image_controls(self, parent):
        """Setup image viewing controls"""
        controls_frame = ttk.Frame(parent)
        controls_frame.grid(row=0, column=0, sticky="ew", pady=(0, 4))
        controls_frame.columnconfigure(2, weight=1)
        
        # View mode buttons
        self.view_original_btn = ttk.Button(
            controls_frame,
            text="📥 Original",
            command=lambda: self.set_view_mode("original"),
            width=10
        )
        self.view_original_btn.grid(row=0, column=0, padx=(0, 2))
        
        self.view_result_btn = ttk.Button(
            controls_frame,
            text="🌟 Result",
            command=lambda: self.set_view_mode("result"),
            width=10
        )
        self.view_result_btn.grid(row=0, column=1, padx=(0, 8))
        
        # Comparison and zoom controls (same as SeedEdit)
        self.comparison_btn = ttk.Button(
            controls_frame,
            text="⚖️ Compare",
            command=self.toggle_comparison_mode,
            width=10
        )
        self.comparison_btn.grid(row=0, column=3, padx=(8, 0))
        
        zoom_frame = ttk.Frame(controls_frame)
        zoom_frame.grid(row=0, column=4, padx=(8, 0))
        
        ttk.Label(zoom_frame, text="Zoom:", font=('Arial', 9)).pack(side=tk.LEFT)
        
        self.zoom_var = tk.StringVar(value="Fit")
        zoom_combo = ttk.Combobox(
            zoom_frame,
            textvariable=self.zoom_var,
            values=["Fit", "50%", "100%", "150%", "200%"],
            state="readonly",
            width=6,
            font=('Arial', 9)
        )
        zoom_combo.pack(side=tk.LEFT, padx=(2, 0))
        zoom_combo.bind('<<ComboboxSelected>>', self.on_zoom_changed)
    
    def setup_image_display(self, parent):
        """Setup large image display with minimal margins"""
        display_frame = ttk.Frame(parent)
        display_frame.grid(row=1, column=0, sticky="nsew")
        display_frame.columnconfigure(0, weight=1)
        display_frame.rowconfigure(0, weight=1)
        
        # Canvas with minimal padding
        self.image_canvas = tk.Canvas(
            display_frame,
            bg='white',
            highlightthickness=0,
            relief='flat'
        )
        self.image_canvas.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(display_frame, orient=tk.VERTICAL, command=self.image_canvas.yview)
        h_scrollbar = ttk.Scrollbar(display_frame, orient=tk.HORIZONTAL, command=self.image_canvas.xview)
        
        self.image_canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        # Bind events
        self.image_canvas.bind('<Configure>', self.on_canvas_configure)
        self.image_canvas.bind('<Button-1>', self.on_canvas_click)
        self.image_canvas.bind('<MouseWheel>', self.on_mouse_wheel)
        
        # Default message
        self.show_default_message()
    
    def show_default_message(self):
        """Show default message"""
        self.image_canvas.delete("all")
        self.image_canvas.create_text(
            260, 200,
            text="Select an image to transform\n\nDrag & drop supported",
            font=('Arial', 14),
            fill='#888',
            justify=tk.CENTER
        )
    
    # Event handlers and utility methods
    def browse_image(self):
        """Browse for image file"""
        from tkinter import filedialog
        file_path = filedialog.askopenfilename(
            title="Select Image for Seedream V4",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.gif *.bmp *.webp"),
                ("PNG files", "*.png"),
                ("JPEG files", "*.jpg *.jpeg"),
                ("All files", "*.*")
            ]
        )
        if file_path:
            # If we have a connected tab instance, use its image selection handler
            if self.tab_instance and hasattr(self.tab_instance, 'on_image_selected'):
                self.tab_instance.on_image_selected(file_path)
            else:
                # Fallback to direct loading
                self.load_image(file_path)
    
    def load_image(self, image_path):
        """Load and display input image"""
        self.selected_image_path = image_path
        
        try:
            # Update thumbnail
            img = Image.open(image_path)
            img.thumbnail((50, 50), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            
            self.thumbnail_label.config(image=photo, text="")
            self.thumbnail_label.image = photo
            
            # Update info
            filename = os.path.basename(image_path)
            if len(filename) > 25:
                filename = filename[:22] + "..."
            self.image_name_label.config(text=filename, foreground="black")
            
            # Get image size
            original = Image.open(image_path)
            self.image_size_label.config(text=f"{original.width}×{original.height}")
            
            # Auto-set resolution if enabled
            self.auto_set_resolution()
            
            # Display in main canvas
            self.set_view_mode("original")
            
        except Exception as e:
            self.status_label.config(text=f"Error loading image: {str(e)}", foreground="red")
    
    def set_size_preset(self, width, height):
        """Set size preset"""
        self.width_var.set(width)
        self.height_var.set(height)
        self.log_message(f"Size preset set to {width}×{height}")
    
    def auto_set_resolution(self):
        """Auto-set resolution based on input image"""
        if not self.selected_image_path:
            return
        
        try:
            img = Image.open(self.selected_image_path)
            # Set to input image size or closest preset
            self.width_var.set(img.width)
            self.height_var.set(img.height)
            self.log_message(f"Auto-set resolution to {img.width}×{img.height}")
        except:
            pass
    
    def toggle_aspect_lock(self):
        """Toggle aspect ratio lock"""
        try:
            # Toggle the lock state
            current_state = self.aspect_lock_var.get()
            self.aspect_lock_var.set(not current_state)
            new_state = self.aspect_lock_var.get()
            
            if new_state:
                # Locking - calculate and store current aspect ratio
                current_width = self.width_var.get()
                current_height = self.height_var.get()
                if current_height > 0:
                    self.locked_aspect_ratio = current_width / current_height
                    self.lock_aspect_btn.config(text="🔒", style="Accent.TButton")
                    self.log_message(f"🔒 Aspect ratio locked: {current_width}:{current_height} (ratio: {self.locked_aspect_ratio:.3f})")
                else:
                    # Can't lock with zero height
                    self.aspect_lock_var.set(False)
                    self.log_message("❌ Cannot lock aspect ratio with zero height")
            else:
                # Unlocking
                self.locked_aspect_ratio = None
                self.lock_aspect_btn.config(text="🔓", style="")
                self.log_message("🔓 Aspect ratio unlocked")
                
        except Exception as e:
            logger.error(f"Error toggling aspect lock: {e}")
            self.aspect_lock_var.set(False)
            self.locked_aspect_ratio = None
    
    def on_size_changed(self, value):
        """Handle size slider changes with aspect ratio locking"""
        if not hasattr(self, 'locked_aspect_ratio') or not self.locked_aspect_ratio:
            return  # No aspect ratio lock active
            
        # If aspect ratio is locked, adjust the other dimension
        try:
            if hasattr(self, '_updating_size') and self._updating_size:
                return  # Prevent recursion
            
            self._updating_size = True
            
            # Get current values
            current_width = self.width_var.get()
            current_height = self.height_var.get()
            
            # Determine which dimension to adjust based on the locked ratio
            # We need to figure out which slider was moved by comparing to expected values
            expected_height = int(current_width / self.locked_aspect_ratio)
            expected_width = int(current_height * self.locked_aspect_ratio)
            
            # If height doesn't match the expected ratio, adjust it (width was changed)
            if abs(current_height - expected_height) > abs(current_width - expected_width):
                new_height = max(256, min(4096, expected_height))
                if new_height != current_height:
                    self.height_var.set(new_height)
                    self.log_message(f"🔒 Adjusted height to {new_height} (maintaining ratio {self.locked_aspect_ratio:.3f})")
            
            # If width doesn't match the expected ratio, adjust it (height was changed)  
            else:
                new_width = max(256, min(4096, expected_width))
                if new_width != current_width:
                    self.width_var.set(new_width)
                    self.log_message(f"🔒 Adjusted width to {new_width} (maintaining ratio {self.locked_aspect_ratio:.3f})")
            
            self._updating_size = False
            
        except Exception as e:
            logger.error(f"Error in aspect ratio adjustment: {e}")
            self.log_message(f"❌ Aspect ratio adjustment failed: {str(e)}")
            if hasattr(self, '_updating_size'):
                self._updating_size = False
    
    def _on_entry_change(self, *args):
        """Handle entry field changes for aspect ratio locking"""
        # Add a small delay to avoid too frequent updates
        if hasattr(self, '_entry_update_id'):
            self.parent_frame.after_cancel(self._entry_update_id)
        
        self._entry_update_id = self.parent_frame.after(100, self._process_entry_change)
    
    def _process_entry_change(self):
        """Process entry changes with aspect ratio locking"""
        try:
            # Clear the update ID
            if hasattr(self, '_entry_update_id'):
                delattr(self, '_entry_update_id')
                
            # Only apply aspect ratio if locked
            if self.locked_aspect_ratio:
                self.on_size_changed(None)  # Trigger aspect ratio adjustment
        except Exception as e:
            logger.error(f"Error processing entry change: {e}")
    
    def process_seedream(self):
        """Process with Seedream V4 API"""
        if not self.api_client:
            self.status_label.config(text="API client not available", foreground="red")
            self.log_message("❌ Error: API client not configured")
            return
            
        if not self.selected_image_path:
            self.status_label.config(text="Please select an image first", foreground="red")
            self.log_message("❌ Error: No image selected")
            return
        
        prompt = self.prompt_text.get("1.0", tk.END).strip()
        if not prompt or prompt == "Describe the transformation you want to apply to the image...":
            self.status_label.config(text="Please enter transformation instructions", foreground="red")
            self.log_message("❌ Error: No prompt provided")
            return
        
        # Show processing state
        self.status_label.config(text="Processing with Seedream V4...", foreground="blue")
        self.progress_bar.grid(row=2, column=0, sticky="ew", pady=(4, 0))
        self.progress_bar.start()
        self.primary_btn.config(state='disabled', text="Processing...")
        
        # Log the start
        self.log_message(f"🚀 Starting Seedream V4 processing...")
        self.log_message(f"📐 Size: {self.width_var.get()}×{self.height_var.get()}")
        self.log_message(f"🎲 Seed: {self.seed_var.get()}")
        self.log_message(f"📝 Prompt: {prompt[:100]}{'...' if len(prompt) > 100 else ''}")
        
        # Process in background thread
        def process_in_background():
            try:
                # Upload image and get URL using privacy uploader
                self.log_message("📤 Uploading image...")
                from core.secure_upload import privacy_uploader
                success, image_url, privacy_info = privacy_uploader.upload_with_privacy_warning(
                    self.selected_image_path, 'seedream_v4'
                )
                
                if not success or not image_url:
                    error_msg = privacy_info or "Failed to upload image"
                
                if not image_url:
                    self.parent_frame.after(0, lambda: self.handle_processing_error(f"Failed to upload image: {error_msg}"))
                    return
                
                self.log_message("✅ Image uploaded successfully")
                
                # Prepare parameters
                size_str = f"{self.width_var.get()}*{self.height_var.get()}"
                seed = int(self.seed_var.get()) if self.seed_var.get() != "-1" else -1
                sync_mode = self.sync_mode_var.get()
                base64_output = self.base64_var.get()
                
                self.log_message(f"🔧 Submitting task with size: {size_str}, sync: {sync_mode}")
                
                # Submit task
                result = self.api_client.submit_seedream_v4_task(
                    prompt=prompt,
                    images=[image_url],
                    size=size_str,
                    seed=seed,
                    enable_sync_mode=sync_mode,
                    enable_base64_output=base64_output
                )
                
                if result.get('success'):
                    task_id = result.get('task_id') or result.get('data', {}).get('id')
                    if task_id:
                        self.current_task_id = task_id
                        self.parent_frame.after(0, lambda: self.handle_task_submitted(task_id))
                    else:
                        self.parent_frame.after(0, lambda: self.handle_processing_error("No task ID received"))
                else:
                    error_msg = result.get('error', 'Unknown error')
                    self.parent_frame.after(0, lambda: self.handle_processing_error(error_msg))
                    
            except Exception as e:
                logger.error(f"Error in Seedream V4 processing: {e}")
                self.parent_frame.after(0, lambda: self.handle_processing_error(str(e)))
        
        # Start processing thread
        thread = threading.Thread(target=process_in_background)
        thread.daemon = True
        thread.start()
    
    def handle_task_submitted(self, task_id):
        """Handle successful task submission"""
        self.log_message(f"✅ Task submitted successfully: {task_id}")
        self.log_message("⏳ Waiting for processing to complete...")
        
        # Start polling for results
        self.poll_for_results(task_id)
    
    def handle_processing_error(self, error_msg):
        """Handle processing error with enhanced logging"""
        self.progress_bar.stop()
        self.progress_bar.grid_remove()
        self.primary_btn.config(state='normal', text="🌟 Apply Seedream V4")
        self.status_label.config(text=f"Error: {error_msg}", foreground="red")
        self.log_message(f"❌ Processing failed: {error_msg}")
        
        # Enhanced logging integration
        try:
            prompt = self.prompt_text.get("1.0", tk.END).strip() if hasattr(self, 'prompt_text') else ""
            
            # Import enhanced systems
            from core.enhanced_prompt_tracker import enhanced_prompt_tracker, FailureReason
            from core.enhanced_filter_training_system import EnhancedFilterTrainingAnalyzer, FilterBypassType
            
            # Determine failure reason from error message
            failure_reason = self._categorize_error(error_msg)
            
            # Collect processing context
            processing_context = {
                "image_path": self.selected_image_path,
                "width": self.width_var.get() if hasattr(self, 'width_var') else None,
                "height": self.height_var.get() if hasattr(self, 'height_var') else None,
                "seed": self.seed_var.get() if hasattr(self, 'seed_var') else None,
                "sync_mode": self.sync_mode_var.get() if hasattr(self, 'sync_mode_var') else None,
                "base64_output": self.base64_var.get() if hasattr(self, 'base64_var') else None,
                "current_task_id": getattr(self, 'current_task_id', None),
                "error_source": "improved_seedream_layout"
            }
            
            # Log to enhanced prompt tracker
            enhanced_prompt_tracker.log_failed_prompt(
                prompt=prompt,
                ai_model="seedream_v4",
                error_message=error_msg,
                failure_reason=failure_reason,
                additional_context=processing_context
            )
            
            # Analyze for potential bypass attempts (for filter training research)
            bypass_techniques = self._analyze_potential_bypass_techniques(prompt)
            
            if bypass_techniques:
                # Log as filter research data (prompt that failed to execute)
                filter_analyzer = EnhancedFilterTrainingAnalyzer()
                filter_analyzer.log_filter_bypass_attempt(
                    prompt=prompt,
                    ai_model="seedream_v4", 
                    success=False,  # Failed to execute (caught by filter or API error)
                    bypass_techniques=bypass_techniques,
                    filter_response=error_msg
                )
                
                self.log_message(f"🛡️ Detected {len(bypass_techniques)} potential bypass techniques in failed prompt")
            
        except Exception as logging_error:
            logger.error(f"Enhanced logging failed: {logging_error}")
            # Don't let logging errors break the main error handling
    
    def _categorize_error(self, error_msg):
        """Categorize error message for enhanced tracking"""
        from core.enhanced_prompt_tracker import FailureReason
        
        error_lower = error_msg.lower()
        
        if any(term in error_lower for term in ["content policy", "inappropriate", "harmful", "nsfw", "violation"]):
            return FailureReason.CONTENT_FILTER
        elif any(term in error_lower for term in ["api key", "authentication", "unauthorized", "forbidden"]):
            return FailureReason.API_ERROR
        elif any(term in error_lower for term in ["timeout", "timed out", "connection"]):
            return FailureReason.TIMEOUT_ERROR
        elif any(term in error_lower for term in ["quota", "limit", "rate limit", "billing"]):
            return FailureReason.QUOTA_EXCEEDED
        elif any(term in error_lower for term in ["invalid", "malformed", "bad request", "format"]):
            return FailureReason.MALFORMED_PROMPT
        else:
            return FailureReason.OTHER
    
    def _analyze_potential_bypass_techniques(self, prompt):
        """Analyze prompt for potential filter bypass techniques"""
        if not prompt:
            return []
            
        from core.enhanced_filter_training_system import FilterBypassType
        
        techniques = []
        prompt_lower = prompt.lower()
        
        # Euphemism detection
        euphemisms = [
            "intimate wear", "barely there", "minimal coverage", "delicate", "sheer", 
            "transparent", "revealing", "skimpy", "tight", "form-fitting"
        ]
        if any(euphem in prompt_lower for euphem in euphemisms):
            techniques.append(FilterBypassType.EUPHEMISM_USE)
        
        # Technical language detection
        technical_terms = [
            "remove upper garment", "unclothed torso", "modify clothing", "alter attire",
            "adjust garments", "change outfit", "wardrobe modification"
        ]
        if any(tech in prompt_lower for tech in technical_terms):
            techniques.append(FilterBypassType.TECHNICAL_LANGUAGE)
        
        # Context framing detection  
        context_frames = [
            "artistic study", "fashion design", "anatomy reference", "educational purpose",
            "medical illustration", "scientific research", "artistic expression"
        ]
        if any(context in prompt_lower for context in context_frames):
            techniques.append(FilterBypassType.CONTEXT_FRAMING)
        
        # Identity preservation detection
        identity_terms = [
            "keep face identical", "preserve expression", "maintain hairstyle", "same face",
            "identical features", "preserve identity", "keep person recognizable"
        ]
        if any(identity in prompt_lower for identity in identity_terms):
            techniques.append(FilterBypassType.IDENTITY_PRESERVATION)
        
        # Background manipulation detection
        background_terms = [
            "seamless edit", "natural lighting", "realistic blend", "perfect integration",
            "professional edit", "high quality result", "photorealistic"
        ]
        if any(bg in prompt_lower for bg in background_terms):
            techniques.append(FilterBypassType.BACKGROUND_MANIPULATION)
        
        return techniques
    
    def poll_for_results(self, task_id):
        """Poll for task completion results"""
        import time
        start_time = time.time()
        max_poll_time = 300  # 5 minutes max
        
        def check_results():
            try:
                # Check for timeout
                if time.time() - start_time > max_poll_time:
                    self.log_message("⏰ Polling timeout - stopping after 5 minutes")
                    self.parent_frame.after(0, lambda: self.handle_processing_error("Task timed out after 5 minutes"))
                    return
                
                result = self.api_client.get_seedream_v4_result(task_id)
                
                if result.get('success'):
                    status = result.get('status', '').lower()
                    
                    if status == 'completed':
                        # Task completed successfully - stop polling and handle result
                        self.log_message("✅ SeedDream processing completed!")
                        self.parent_frame.after(0, lambda: self.handle_results_ready(result))
                        return  # Stop the polling loop
                    elif status in ['failed', 'error']:
                        error_msg = result.get('error', 'Task failed')
                        self.parent_frame.after(0, lambda: self.handle_processing_error(error_msg))
                        return  # Stop the polling loop
                    else:
                        # Still processing, poll again
                        self.log_message(f"🔄 Status: {status}")
                        self.parent_frame.after(3000, check_results)  # Check again in 3 seconds
                else:
                    error_msg = result.get('error', 'Failed to get task status')
                    self.parent_frame.after(0, lambda: self.handle_processing_error(error_msg))
                    
            except Exception as e:
                logger.error(f"Error polling for results: {e}")
                self.parent_frame.after(0, lambda: self.handle_processing_error(str(e)))
        
        # Start polling
        self.parent_frame.after(2000, check_results)  # Initial check after 2 seconds
    
    def handle_results_ready(self, data):
        """Handle completed results"""
        try:
            # Get the result image URL
            result_url = data.get('result_url') or data.get('output_url')
            if not result_url:
                self.handle_processing_error("No result image URL received")
                return
            
            self.result_url = result_url
            self.log_message(f"🎉 Processing completed! Result URL: {result_url}")
            
            # Download and display the result
            self.download_and_display_result(result_url)
            
        except Exception as e:
            logger.error(f"Error handling results: {e}")
            self.handle_processing_error(str(e))
    
    def download_and_display_result(self, result_url):
        """Download and display the result image"""
        def download_in_background():
            try:
                self.log_message("📥 Downloading result image...")
                
                # Download the image
                import requests
                response = requests.get(result_url, timeout=60)
                response.raise_for_status()
                
                # Save to temporary file
                import tempfile
                with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
                    temp_file.write(response.content)
                    temp_path = temp_file.name
                
                self.result_image_path = temp_path
                
                # Update UI in main thread
                self.parent_frame.after(0, lambda: self.handle_download_complete(temp_path))
                
            except Exception as e:
                logger.error(f"Error downloading result: {e}")
                self.parent_frame.after(0, lambda: self.handle_processing_error(f"Failed to download result: {str(e)}"))
        
        # Start download thread
        thread = threading.Thread(target=download_in_background)
        thread.daemon = True
        thread.start()
    
    def handle_download_complete(self, result_path):
        """Handle successful download completion"""
        # Update UI state
        self.progress_bar.stop()
        self.progress_bar.grid_remove()
        self.primary_btn.config(state='normal', text="🌟 Apply Seedream V4")
        self.status_label.config(text="✅ Transformation complete!", foreground="green")
        
        # Log completion
        self.log_message("✅ Processing completed successfully!")
        self.log_message(f"💾 Result saved to: {result_path}")
        
        # Enable result view buttons
        if hasattr(self, 'view_result_btn'):
            self.view_result_btn.config(state='normal')
        if hasattr(self, 'comparison_btn'):
            self.comparison_btn.config(state='normal')
        
        # Enhanced logging for successful completion
        try:
            prompt = self.prompt_text.get("1.0", tk.END).strip() if hasattr(self, 'prompt_text') else ""
            
            # Import enhanced systems
            from core.enhanced_prompt_tracker import enhanced_prompt_tracker
            from core.enhanced_filter_training_system import EnhancedFilterTrainingAnalyzer
            
            # Collect success context
            success_context = {
                "image_path": self.selected_image_path,
                "result_path": result_path,
                "result_url": self.result_url,
                "width": self.width_var.get() if hasattr(self, 'width_var') else None,
                "height": self.height_var.get() if hasattr(self, 'height_var') else None,
                "seed": self.seed_var.get() if hasattr(self, 'seed_var') else None,
                "sync_mode": self.sync_mode_var.get() if hasattr(self, 'sync_mode_var') else None,
                "base64_output": self.base64_var.get() if hasattr(self, 'base64_var') else None,
                "current_task_id": getattr(self, 'current_task_id', None),
                "processing_source": "improved_seedream_layout"
            }
            
            # Log successful completion
            enhanced_prompt_tracker.log_successful_prompt(
                prompt=prompt,
                ai_model="seedream_v4",
                result_url=self.result_url,
                result_path=result_path,
                additional_context=success_context
            )
            
            # Analyze for bypass techniques that succeeded (for filter training research)
            bypass_techniques = self._analyze_potential_bypass_techniques(prompt)
            
            if bypass_techniques:
                # Log as successful bypass attempt (prompt that worked despite potential issues)
                filter_analyzer = EnhancedFilterTrainingAnalyzer()
                filter_analyzer.log_filter_bypass_attempt(
                    prompt=prompt,
                    ai_model="seedream_v4",
                    success=True,  # Successfully generated content
                    bypass_techniques=bypass_techniques,
                    filter_response=f"Content generated successfully with {len(bypass_techniques)} potential techniques"
                )
                
                self.log_message(f"🛡️ Logged {len(bypass_techniques)} successful bypass techniques for filter research")
            
            self.log_message("📊 Enhanced logging completed for successful generation")
            
        except Exception as logging_error:
            logger.error(f"Enhanced success logging failed: {logging_error}")
            # Don't let logging errors break the success flow
        
        # Auto-save if enabled and integrate with tab
        if self.tab_instance and hasattr(self.tab_instance, 'handle_result_ready'):
            self.tab_instance.handle_result_ready(result_path, self.result_url)
        
        # Enable quality rating button after successful generation
        if hasattr(self, 'rating_btn'):
            self.rating_btn.config(state="normal")
            
        # Store last result for rating
        self.last_result_path = result_path
        self.last_prompt = self.prompt_text.get("1.0", tk.END).strip()
        
        # Auto-save the result
        self.auto_save_result(result_path)
    
    def auto_save_result(self, result_path):
        """Auto-save the result to the organized folder structure"""
        try:
            from core.auto_save import auto_save_manager
            from app.config import Config
            
            if not Config.AUTO_SAVE_ENABLED:
                return
            
            # Get prompt and settings for filename
            prompt = self.prompt_text.get("1.0", tk.END).strip() if hasattr(self, 'prompt_text') else ""
            
            # Get size settings if available
            if hasattr(self, 'width_var') and hasattr(self, 'height_var'):
                width = int(self.width_var.get())
                height = int(self.height_var.get())
                size = f"{width}x{height}"
            else:
                size = "unknown"
            
            # Get seed if available
            if hasattr(self, 'seed_var'):
                seed = self.seed_var.get()
                extra_info = f"{size}_seed{seed}"
            else:
                extra_info = size
            
            # Save the result (using local file method since result_path is a local file)
            success, saved_path, error = auto_save_manager.save_local_file(
                'seedream_v4',
                result_path,  # This is a local file path
                prompt=prompt,
                extra_info=extra_info
            )
            
            if success:
                self.log_message(f"💾 Auto-saved to: {saved_path}")
            else:
                self.log_message(f"⚠️ Auto-save failed: {error}")
                
        except Exception as e:
            logger.error(f"Error in auto-save: {e}")
            self.log_message(f"⚠️ Auto-save error: {str(e)}")
    
    def after_processing(self):
        """Called after processing completes"""
        # Hide progress
        self.progress_bar.stop()
        self.progress_bar.grid_remove()
        self.primary_btn.config(state='normal', text="🌟 Apply Seedream V4")
        self.status_label.config(text="✅ Transformation complete!", foreground="green")
        
        # Log completion
        self.log_message("✅ Processing completed successfully!")
        
        # Enable result view
        self.view_result_btn.config(state='normal')
        self.comparison_btn.config(state='normal')
    
    def log_message(self, message):
        """Add message to progress log"""
        if hasattr(self, 'log_text'):
            self.log_text.config(state=tk.NORMAL)
            self.log_text.insert(tk.END, f"{message}\n")
            self.log_text.see(tk.END)
            self.log_text.config(state=tk.DISABLED)
    
    # Image display methods (same as SeedEdit)
    def set_view_mode(self, mode):
        """Set image viewing mode"""
        self.current_view_mode = mode
        
        if mode == "original":
            # ttk.Button doesn't support relief, use state instead
            self.view_original_btn.state(['pressed'])
            self.view_result_btn.state(['!pressed'])
            if self.selected_image_path:
                self.display_image(self.selected_image_path)
        elif mode == "result":
            self.view_result_btn.state(['pressed'])
            self.view_original_btn.state(['!pressed'])
            if self.result_image_path:
                self.display_image(self.result_image_path)
        
        self.comparison_btn.state(['!pressed'])
    
    def toggle_comparison_mode(self):
        """Toggle comparison mode"""
        if not self.selected_image_path or not self.result_image_path:
            self.status_label.config(text="Need both images for comparison", foreground="orange")
            return
        
        self.comparison_btn.state(['pressed'])
        self.view_original_btn.state(['!pressed'])
        self.view_result_btn.state(['!pressed'])
        
        self.display_comparison()
    
    def display_image(self, image_path, position="center"):
        """Display image with dynamic scaling"""
        # Same implementation as SeedEdit layout
        try:
            self.image_canvas.delete("all")
            
            img = Image.open(image_path)
            canvas_width = self.image_canvas.winfo_width()
            canvas_height = self.image_canvas.winfo_height()
            
            if canvas_width <= 1:
                canvas_width = 520
                canvas_height = 400
            
            zoom_value = self.zoom_var.get()
            if zoom_value == "Fit":
                scale_factor = min(
                    (canvas_width - 10) / img.width,
                    (canvas_height - 10) / img.height
                )
            else:
                scale_factor = float(zoom_value.rstrip('%')) / 100
            
            new_width = int(img.width * scale_factor)
            new_height = int(img.height * scale_factor)
            img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            photo = ImageTk.PhotoImage(img_resized)
            
            x = max(5, (canvas_width - new_width) // 2)
            y = max(5, (canvas_height - new_height) // 2)
            
            self.image_canvas.create_image(x, y, anchor=tk.NW, image=photo)
            self.image_canvas.image = photo
            
            self.image_canvas.configure(scrollregion=self.image_canvas.bbox("all"))
            
        except Exception as e:
            self.image_canvas.delete("all")
            self.image_canvas.create_text(
                260, 200,
                text=f"Error loading image:\n{str(e)}",
                font=('Arial', 12),
                fill='red',
                justify=tk.CENTER
            )
    
    def display_comparison(self):
        """Display side-by-side comparison"""
        if not self.selected_image_path or not self.result_image_path:
            self.log_message("❌ Need both original and result images for comparison")
            return
        
        try:
            # Create comparison window
            comparison_window = tk.Toplevel(self.parent_frame)
            comparison_window.title("Image Comparison - Seedream V4")
            comparison_window.geometry("1200x600")
            
            # Left side - Original
            left_frame = ttk.LabelFrame(comparison_window, text="Original", padding="10")
            left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 5), pady=10)
            
            # Right side - Result
            right_frame = ttk.LabelFrame(comparison_window, text="Result", padding="10")
            right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 10), pady=10)
            
            # Load and display images
            original_img = Image.open(self.selected_image_path)
            result_img = Image.open(self.result_image_path)
            
            # Resize for display
            display_size = (500, 400)
            original_img.thumbnail(display_size, Image.Resampling.LANCZOS)
            result_img.thumbnail(display_size, Image.Resampling.LANCZOS)
            
            # Convert to PhotoImage
            original_photo = ImageTk.PhotoImage(original_img)
            result_photo = ImageTk.PhotoImage(result_img)
            
            # Display in labels
            original_label = tk.Label(left_frame, image=original_photo)
            original_label.image = original_photo  # Keep reference
            original_label.pack(expand=True)
            
            result_label = tk.Label(right_frame, image=result_photo)
            result_label.image = result_photo  # Keep reference
            result_label.pack(expand=True)
            
            self.log_message("📊 Comparison window opened")
            
        except Exception as e:
            logger.error(f"Error displaying comparison: {e}")
            self.log_message(f"❌ Error displaying comparison: {str(e)}")
    
    # Utility methods
    def clear_placeholder(self, event):
        current_text = self.prompt_text.get("1.0", tk.END).strip()
        if current_text == "Describe the transformation you want to apply to the image...":
            self.prompt_text.delete("1.0", tk.END)
    
    def add_placeholder(self, event):
        current_text = self.prompt_text.get("1.0", tk.END).strip()
        if not current_text:
            self.prompt_text.insert("1.0", "Describe the transformation you want to apply to the image...")
    
    def on_canvas_configure(self, event):
        """Handle canvas resize"""
        # Update scroll region if we have a canvas
        if hasattr(self, 'image_canvas') and hasattr(event, 'width') and hasattr(event, 'height'):
            try:
                self.image_canvas.configure(scrollregion=self.image_canvas.bbox("all"))
            except:
                pass
    
    def on_canvas_click(self, event):
        """Handle canvas click"""
        # Could be used for image interaction in the future
        if hasattr(self, 'selected_image_path') and self.selected_image_path:
            self.log_message("📍 Image clicked - feature could be expanded for interactive editing")
    
    def on_mouse_wheel(self, event):
        """Handle mouse wheel for zooming"""
        # Basic mouse wheel support for image viewing
        if hasattr(self, 'image_canvas') and hasattr(event, 'delta'):
            try:
                # Scroll the canvas
                self.image_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            except:
                pass
    
    def on_zoom_changed(self, event):
        """Handle zoom change"""
        # Could implement image zoom functionality
        if hasattr(self, 'current_zoom'):
            self.log_message(f"🔍 Zoom changed: {self.current_zoom}%")
    
    # Preset and sample methods
    def load_preset(self, event=None): 
        """Load preset settings"""
        if self.tab_instance and hasattr(self.tab_instance, 'load_saved_prompt'):
            self.tab_instance.load_saved_prompt()
    
    def save_preset(self): 
        """Save current settings as preset"""
        if self.tab_instance and hasattr(self.tab_instance, 'save_current_prompt'):
            self.tab_instance.save_current_prompt()
    
    def load_sample(self): 
        """Load sample prompt"""
        if self.tab_instance and hasattr(self.tab_instance, 'load_sample_prompt'):
            self.tab_instance.load_sample_prompt()
    # AI integration methods inherited from AIChatMixin
    # improve_prompt_with_ai() and open_filter_training() are provided by the mixin
    
    def improve_with_ai(self):
        """Wrapper for improve_prompt_with_ai to maintain backwards compatibility"""
        self.improve_prompt_with_ai()
    
    def filter_training(self):
        """Wrapper for open_filter_training to maintain backwards compatibility"""  
        self.open_filter_training()
    
    def generate_mild_examples(self):
        """Generate 5 mild filter training examples based on current image"""
        try:
            if not self.selected_image_path:
                # Show tooltip message
                self.show_tooltip("🖼️ Please select an image first")
                return
            
            # Show loading state
            self.show_tooltip("🔥 Generating mild examples...")
            
            # Run generation in background thread to avoid UI freezing
            threading.Thread(
                target=self._generate_mild_examples_thread,
                daemon=True
            ).start()
            
        except Exception as e:
            logger.error(f"Error generating mild examples: {e}")
            self.show_tooltip(f"❌ Error: {str(e)}")
    
    def generate_moderate_examples(self):
        """Generate 5 sophisticated moderate filter training examples using indirect language"""
        try:
            if not self.selected_image_path:
                # Show tooltip message
                self.show_tooltip("🖼️ Please select an image first")
                return
            
            # Show loading state
            self.show_tooltip("⚡ Generating sophisticated moderate examples...")
            
            # Run generation in background thread to avoid UI freezing
            threading.Thread(
                target=self._generate_moderate_examples_thread,
                daemon=True
            ).start()
            
        except Exception as e:
            logger.error(f"Error generating moderate examples: {e}")
            self.show_tooltip(f"❌ Error: {str(e)}")
    
    def _generate_mild_examples_thread(self):
        """Background thread for generating mild examples"""
        try:
            from core.ai_prompt_advisor import get_ai_advisor
            
            ai_advisor = get_ai_advisor()
            if not ai_advisor.is_available():
                self.parent_frame.after(0, lambda: self.show_tooltip("❌ AI service not available"))
                return
            
            # Step 1: Analyze image for filter training (detailed analysis)
            self.parent_frame.after(0, lambda: self.show_tooltip("🔍 Analyzing image..."))
            description = asyncio.run(ai_advisor.describe_image(self.selected_image_path, detailed_analysis=True))
            
            if not description or "error" in description.lower():
                self.parent_frame.after(0, lambda: self.show_tooltip("❌ Image analysis failed"))
                return
            
            # Step 2: Generate 5 mild examples using optimized method
            self.parent_frame.after(0, lambda: self.show_tooltip("🔥 Generating 5 mild examples..."))
            mild_examples = asyncio.run(ai_advisor.generate_mild_examples_only(description, count=5))
            
            if not mild_examples:
                # Final fallback using vocabulary bank
                from core.filter_vocabulary_bank import filter_vocab
                import re
                
                mild_examples = []
                for i in range(5):
                    # Extract subject and clothing from description
                    subject_match = re.search(r'\b(woman|man|girl|lady|gentleman)\b', description.lower())
                    clothing_match = re.search(r'\b(dress|gown|shirt|top|blouse|outfit|clothing|garment|attire)\b', description.lower())
                    
                    if subject_match and clothing_match:
                        subject = subject_match.group(1)
                        clothing = clothing_match.group(1)
                        mild_example = filter_vocab.generate_varied_mild_prompt(subject, clothing)
                        mild_examples.append(mild_example)
                    else:
                        # Use generic fallbacks with varied vocabulary
                        generic_examples = [
                            "Convert outfit to revealing swimwear; preserve identity",
                            "Transform attire to micro bikini; maintain features", 
                            "Change clothing to skimpy two-piece; keep expression",
                            "Alter garment to minimal coverage; retain appearance",
                            "Switch to tiny string bikini; hold facial features"
                        ]
                        mild_examples.append(generic_examples[i] if i < len(generic_examples) else generic_examples[0])
            
            # Show results in UI thread
            self.parent_frame.after(0, lambda: self._display_mild_examples(mild_examples))
            
        except Exception as e:
            logger.error(f"Error in mild examples thread: {e}")
            self.parent_frame.after(0, lambda: self.show_tooltip(f"❌ Generation failed: {str(e)}"))
    
    def _generate_moderate_examples_thread(self):
        """Background thread for generating sophisticated moderate examples"""
        try:
            from core.ai_prompt_advisor import get_ai_advisor
            
            ai_advisor = get_ai_advisor()
            if not ai_advisor.is_available():
                self.parent_frame.after(0, lambda: self.show_tooltip("❌ AI service not available"))
                return
            
            # Step 1: Analyze image for filter training (detailed analysis)
            self.parent_frame.after(0, lambda: self.show_tooltip("🔍 Analyzing image for moderate examples..."))
            description = asyncio.run(ai_advisor.describe_image(self.selected_image_path, detailed_analysis=True))
            
            if not description or "error" in description.lower():
                self.parent_frame.after(0, lambda: self.show_tooltip("❌ Image analysis failed"))
                return
            
            # Step 2: Generate 5 sophisticated moderate examples
            self.parent_frame.after(0, lambda: self.show_tooltip("⚡ Generating sophisticated indirect prompts..."))
            moderate_examples = asyncio.run(ai_advisor.generate_moderate_examples_only(description, count=5))
            
            # Show results in UI thread
            self.parent_frame.after(0, lambda: self._display_moderate_examples(moderate_examples))
            
        except Exception as e:
            logger.error(f"Error in moderate examples thread: {e}")
            self.parent_frame.after(0, lambda: self.show_tooltip(f"❌ Generation failed: {str(e)}"))
    
    def _display_moderate_examples(self, examples):
        """Display generated moderate examples in a popup window"""
        try:
            # Create popup window
            popup = tk.Toplevel(self.parent_frame)
            popup.title("⚡ Sophisticated Moderate Examples")
            popup.geometry("800x600")
            popup.resizable(True, True)
            
            # Main frame with scrollbar
            main_frame = ttk.Frame(popup)
            main_frame.pack(fill="both", expand=True, padx=10, pady=10)
            
            # Title with count
            title_label = ttk.Label(main_frame, text=f"⚡ Filter Training - {len(examples)} Moderate Examples", font=("Arial", 12, "bold"))
            title_label.pack(pady=(0, 5))
            
            # Info label
            info_label = ttk.Label(main_frame, text="🎯 Uses sophisticated indirect language combinations to achieve harmful goals without explicit terms", font=("Arial", 9), foreground="gray")
            info_label.pack(pady=(0, 10))
            
            # Examples frame with scrollbar
            canvas = tk.Canvas(main_frame)
            scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
            scrollable_frame = ttk.Frame(canvas)
            
            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )
            
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            
            # Add examples with copy buttons
            for i, example in enumerate(examples, 1):
                example_frame = ttk.LabelFrame(scrollable_frame, text=f"Moderate Example {i}", padding="8")
                example_frame.pack(fill="x", pady=5, padx=5)
                example_frame.columnconfigure(0, weight=1)
                
                # Example text (larger for longer prompts)
                text_widget = tk.Text(example_frame, height=4, wrap=tk.WORD, font=("Arial", 10))
                text_widget.insert("1.0", example)
                text_widget.config(state="readonly")
                text_widget.grid(row=0, column=0, sticky="ew", pady=(0, 5))
                
                # Word count label
                word_count = len(example.split())
                word_label = ttk.Label(example_frame, text=f"({word_count} words)", font=("Arial", 8), foreground="gray")
                word_label.grid(row=1, column=0, sticky="w", pady=(0, 5))
                
                # Buttons frame
                btn_frame = ttk.Frame(example_frame)
                btn_frame.grid(row=2, column=0, sticky="ew")
                
                # Copy button
                copy_btn = ttk.Button(
                    btn_frame, 
                    text="📋 Copy", 
                    command=lambda ex=example: self._copy_to_clipboard(ex, popup)
                )
                copy_btn.pack(side="left", padx=(0, 5))
                
                # Use button
                use_btn = ttk.Button(
                    btn_frame,
                    text="✅ Use This",
                    command=lambda ex=example: self._use_example(ex, popup)
                )
                use_btn.pack(side="left")
                
                # Analyze button (shows breakdown)
                analyze_btn = ttk.Button(
                    btn_frame,
                    text="🔍 Analyze",
                    command=lambda ex=example: self._show_example_analysis(ex)
                )
                analyze_btn.pack(side="right")
            
            # Bottom buttons
            bottom_frame = ttk.Frame(main_frame)
            bottom_frame.pack(fill="x", pady=(10, 0))
            
            ttk.Button(bottom_frame, text="🔄 Generate New", command=lambda: [popup.destroy(), self.generate_moderate_examples()]).pack(side="left")
            ttk.Button(bottom_frame, text="❌ Close", command=popup.destroy).pack(side="right")
            
            # Center window
            popup.transient(self.parent_frame.winfo_toplevel())
            popup.grab_set()
            
        except Exception as e:
            logger.error(f"Error displaying moderate examples: {e}")
            self.show_tooltip(f"❌ Display error: {str(e)}")
    
    def _show_example_analysis(self, example):
        """Show analysis of how the example works indirectly"""
        try:
            # Create analysis popup
            analysis_popup = tk.Toplevel(self.parent_frame)
            analysis_popup.title("🔍 Example Analysis")
            analysis_popup.geometry("600x400")
            analysis_popup.resizable(True, True)
            
            main_frame = ttk.Frame(analysis_popup)
            main_frame.pack(fill="both", expand=True, padx=10, pady=10)
            
            # Title
            title_label = ttk.Label(main_frame, text="🔍 Indirect Language Analysis", font=("Arial", 12, "bold"))
            title_label.pack(pady=(0, 10))
            
            # Original example
            example_frame = ttk.LabelFrame(main_frame, text="Example", padding="8")
            example_frame.pack(fill="x", pady=(0, 10))
            
            example_text = tk.Text(example_frame, height=3, wrap=tk.WORD, font=("Arial", 10))
            example_text.insert("1.0", example)
            example_text.config(state="readonly", background="#f0f0f0")
            example_text.pack(fill="x")
            
            # Analysis
            analysis_frame = ttk.LabelFrame(main_frame, text="How This Works", padding="8")
            analysis_frame.pack(fill="both", expand=True, pady=(0, 10))
            
            analysis_text = tk.Text(analysis_frame, wrap=tk.WORD, font=("Arial", 10))
            
            # Simple analysis based on keywords found
            analysis_content = "This example uses indirect language techniques:\n\n"
            
            if "artistic" in example.lower() or "study" in example.lower():
                analysis_content += "✓ ARTISTIC JUSTIFICATION: Uses legitimate art/study context as cover\n"
            if "anatomical" in example.lower() or "medical" in example.lower():
                analysis_content += "✓ CLINICAL FRAMING: Medical/educational terminology to appear legitimate\n"
            if "visualization" in example.lower() or "reference" in example.lower():
                analysis_content += "✓ PROFESSIONAL PURPOSE: Claims professional/educational intent\n"
            if "absence" in example.lower() or "without" in example.lower():
                analysis_content += "✓ INDIRECT REMOVAL: Implies nudity without using explicit terms\n"
            if "preserving" in example.lower() or "maintaining" in example.lower():
                analysis_content += "✓ IDENTITY PRESERVATION: Ensures recognizable result\n"
            
            analysis_content += "\nThis combination of techniques makes the harmful intent less obvious to filters while still achieving the desired result through implication and context manipulation."
            
            analysis_text.insert("1.0", analysis_content)
            analysis_text.config(state="readonly")
            analysis_text.pack(fill="both", expand=True)
            
            # Close button
            ttk.Button(main_frame, text="Close", command=analysis_popup.destroy).pack(pady=(10, 0))
            
            # Center window
            analysis_popup.transient(analysis_popup.winfo_toplevel())
            
        except Exception as e:
            logger.error(f"Error showing example analysis: {e}")
    
    def _display_mild_examples(self, examples):
        """Display generated mild examples in a popup window"""
        try:
            # Create popup window
            popup = tk.Toplevel(self.parent_frame)
            popup.title("🔥 Generated Mild Examples")
            popup.geometry("600x500")
            popup.resizable(True, True)
            
            # Main frame with scrollbar
            main_frame = ttk.Frame(popup)
            main_frame.pack(fill="both", expand=True, padx=10, pady=10)
            
            # Title with count
            title_label = ttk.Label(main_frame, text=f"🔥 Filter Training - {len(examples)} Mild Examples", font=("Arial", 12, "bold"))
            title_label.pack(pady=(0, 5))
            
            # Info label
            info_label = ttk.Label(main_frame, text="✨ Generated with improved vocabulary variety and shorter format", font=("Arial", 9), foreground="gray")
            info_label.pack(pady=(0, 10))
            
            # Examples frame with scrollbar
            canvas = tk.Canvas(main_frame)
            scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
            scrollable_frame = ttk.Frame(canvas)
            
            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )
            
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            
            # Add examples with copy buttons
            for i, example in enumerate(examples, 1):
                example_frame = ttk.LabelFrame(scrollable_frame, text=f"Example {i}", padding="8")
                example_frame.pack(fill="x", pady=5, padx=5)
                example_frame.columnconfigure(0, weight=1)
                
                # Example text
                text_widget = tk.Text(example_frame, height=3, wrap=tk.WORD, font=("Arial", 10))
                text_widget.insert("1.0", example)
                text_widget.config(state="readonly")
                text_widget.grid(row=0, column=0, sticky="ew", pady=(0, 5))
                
                # Buttons frame
                btn_frame = ttk.Frame(example_frame)
                btn_frame.grid(row=1, column=0, sticky="ew")
                
                # Copy button
                copy_btn = ttk.Button(
                    btn_frame, 
                    text="📋 Copy", 
                    command=lambda ex=example: self._copy_to_clipboard(ex, popup)
                )
                copy_btn.pack(side="left", padx=(0, 5))
                
                # Use button
                use_btn = ttk.Button(
                    btn_frame,
                    text="✅ Use This",
                    command=lambda ex=example: self._use_example(ex, popup)
                )
                use_btn.pack(side="left")
            
            # Bottom buttons
            bottom_frame = ttk.Frame(main_frame)
            bottom_frame.pack(fill="x", pady=(10, 0))
            
            ttk.Button(bottom_frame, text="🔄 Generate New", command=lambda: [popup.destroy(), self.generate_mild_examples()]).pack(side="left")
            ttk.Button(bottom_frame, text="❌ Close", command=popup.destroy).pack(side="right")
            
            # Center window
            popup.transient(self.parent_frame.winfo_toplevel())
            popup.grab_set()
            
        except Exception as e:
            logger.error(f"Error displaying mild examples: {e}")
            self.show_tooltip(f"❌ Display error: {str(e)}")
    
    def _copy_to_clipboard(self, text, popup_window):
        """Copy text to clipboard and show feedback"""
        try:
            popup_window.clipboard_clear()
            popup_window.clipboard_append(text)
            self.show_tooltip("📋 Copied to clipboard!")
        except Exception as e:
            logger.error(f"Error copying to clipboard: {e}")
    
    def _use_example(self, example, popup_window):
        """Use example in the prompt text field"""
        try:
            # Clear current prompt and insert example
            self.prompt_text.delete("1.0", tk.END)
            self.prompt_text.insert("1.0", example)
            
            # Close popup
            popup_window.destroy()
            
            # Show feedback
            self.show_tooltip("✅ Example loaded into prompt!")
            
        except Exception as e:
            logger.error(f"Error using example: {e}")
    
    def show_tooltip(self, message):
        """Show temporary tooltip message"""
        try:
            # Update status label temporarily
            original_text = self.status_label.cget("text")
            original_color = self.status_label.cget("foreground")
            
            self.status_label.config(text=message, foreground="blue")
            
            # Restore original text after 3 seconds
            self.parent_frame.after(3000, lambda: self.status_label.config(text=original_text, foreground=original_color))
            
        except Exception as e:
            logger.error(f"Error showing tooltip: {e}")
    
    def create_tooltip(self, widget, text):
        """Create a hover tooltip for a widget"""
        def on_enter(event):
            # Create tooltip window
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_attributes("-topmost", True)
            
            # Position tooltip near widget
            x = widget.winfo_rootx() + 25
            y = widget.winfo_rooty() - 25
            tooltip.wm_geometry(f"+{x}+{y}")
            
            # Add text
            label = ttk.Label(tooltip, text=text, background="lightyellow", 
                            relief="solid", borderwidth=1, font=("Arial", 9))
            label.pack()
            
            # Store tooltip reference
            widget.tooltip = tooltip
        
        def on_leave(event):
            # Destroy tooltip
            if hasattr(widget, 'tooltip'):
                widget.tooltip.destroy()
                delattr(widget, 'tooltip')
        
        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)
    
    def add_ai_chat_interface(self, prompt_widget, model_type, tab_instance):
        """Add AI chat interface for universal AI integration system"""
        try:
            # Store prompt widget reference
            self.prompt_widget = prompt_widget
            
            # Find or create AI container
            if hasattr(self, 'ai_chat_container'):
                container = self.ai_chat_container
            else:
                # Create a fallback container if needed
                container = ttk.Frame(self.parent_frame)
                container.pack(fill=tk.X, pady=2)
                self.ai_chat_container = container
            
            # Clear existing buttons
            for widget in container.winfo_children():
                widget.destroy()
            
            # Add AI buttons
            ttk.Button(container, text="🤖", width=3, 
                      command=self.improve_with_ai).pack(side=tk.LEFT, padx=1)
            ttk.Button(container, text="🛡️", width=3, 
                      command=self.filter_training).pack(side=tk.LEFT, padx=1)
            ttk.Button(container, text="💾", width=3, 
                      command=self.save_preset).pack(side=tk.LEFT, padx=1)
            ttk.Button(container, text="🎲", width=3, 
                      command=self.load_sample).pack(side=tk.LEFT, padx=1)
            
            return True
            
        except Exception as e:
            logger.error(f"Error adding AI chat interface to Seedream layout: {e}")
            return False
    
    def update_status(self, message: str, status_type: str = "info"):
        """Update status for AI integration"""
        try:
            if hasattr(self, 'status_console') and self.status_console:
                if status_type == "success":
                    self.status_console.log_status(message, "success")
                elif status_type == "error":
                    self.status_console.log_error(message, "AI")
                elif status_type == "warning":
                    self.status_console.log_status(message, "warning")
                else:
                    self.status_console.log_status(message, "info")
            else:
                print(f"[{status_type.upper()}] {message}")
        except Exception as e:
            print(f"Status update error: {e}")
            print(f"[{status_type.upper()}] {message}")
    def clear_all(self): 
        """Clear all inputs and reset to defaults"""
        if self.tab_instance and hasattr(self.tab_instance, 'clear_all'):
            self.tab_instance.clear_all()
        else:
            # Fallback implementation
            try:
                self.prompt_text.delete("1.0", tk.END)
                self.prompt_text.insert("1.0", "Describe the transformation you want to apply to the image...")
                self.width_var.set(1024)
                self.height_var.set(1024)
                self.seed_var.set("-1")
                self.sync_mode_var.set(False)
                self.base64_var.set(False)
                self.log_message("🧹 All inputs cleared")
            except Exception as e:
                logger.error(f"Error clearing inputs: {e}")
                
    def load_result(self): 
        """Load a previously saved result"""
        if self.tab_instance and hasattr(self.tab_instance, 'load_result'):
            self.tab_instance.load_result()
        else:
            self.log_message("💡 Load result feature - connect to result browser")
            
    def save_result(self): 
        """Save the current result"""
        if self.tab_instance and hasattr(self.tab_instance, 'save_result_image'):
            self.tab_instance.save_result_image()
        else:
            self.log_message("💡 Save result feature - implement result saving")

    def setup_learning_components(self):
        """Setup AI learning components and widgets"""
        try:
            # Import learning components
            from ui.components.smart_learning_panel import SmartLearningPanel
            from core.quality_rating_widget import QualityRatingDialog
            
            # Create learning panel reference for later use
            self.learning_panel = None
            self.quality_dialog = None
            
            logger.info("Learning components initialized successfully")
            
        except ImportError as e:
            logger.warning(f"Learning components not available: {e}")
            self.learning_panel = None
            self.quality_dialog = None
        except Exception as e:
            logger.error(f"Error initializing learning components: {e}")
            self.learning_panel = None
            self.quality_dialog = None
    
    def show_learning_panel(self):
        """Show the Smart Learning Panel with current insights"""
        try:
            if not hasattr(self, 'learning_panel') or self.learning_panel is None:
                from ui.components.smart_learning_panel import create_smart_learning_panel
                
                # Create learning panel window
                learning_window = tk.Toplevel(self.parent_frame)
                learning_window.title("🧠 AI Learning Insights - Seedream V4")
                learning_window.geometry("800x600")
                learning_window.resizable(True, True)
                
                # Create and add learning panel
                self.learning_panel = create_smart_learning_panel(learning_window)
                self.learning_panel.grid(sticky="nsew", padx=10, pady=10)
                
                # Configure window grid
                learning_window.columnconfigure(0, weight=1)
                learning_window.rowconfigure(0, weight=1)
                
                # Update with current context
                current_prompt = self.prompt_text.get("1.0", tk.END).strip() if hasattr(self, 'prompt_text') else ""
                if current_prompt:
                    self.learning_panel.analyze_prompt(current_prompt, "seedream_v4")
                
                self.log_message("🧠 AI Learning Panel opened")
            else:
                self.log_message("🧠 Learning panel already open")
                
        except Exception as e:
            logger.error(f"Error showing learning panel: {e}")
            self.log_message(f"❌ Failed to open learning panel: {str(e)}")
    
    def show_quality_rating(self, prompt: str = None, result_path: str = None):
        """Show quality rating dialog for user feedback"""
        try:
            from core.quality_rating_widget import QualityRatingDialog
            
            # Use stored values if called from button
            if prompt is None and hasattr(self, 'last_prompt'):
                prompt = self.last_prompt
            if result_path is None and hasattr(self, 'last_result_path'):
                result_path = self.last_result_path
                
            if not prompt:
                self.log_message("❌ No prompt available for rating")
                return
            
            def on_rating_complete(quality, feedback):
                self.log_message(f"📊 Quality rated: {quality}")
                if feedback:
                    self.log_message(f"📝 User feedback: {feedback[:50]}...")
            
            self.quality_dialog = QualityRatingDialog(
                parent=self.parent_frame,
                prompt=prompt,
                result_path=result_path,
                callback=on_rating_complete
            )
            
        except Exception as e:
            logger.error(f"Error showing quality rating: {e}")
            self.log_message(f"❌ Failed to open quality rating: {str(e)}")
    
    def update_learning_insights(self, prompt: str, success: bool, result_data: dict = None):
        """Update learning insights with new data"""
        try:
            # Update learning panel if it exists
            if hasattr(self, 'learning_panel') and self.learning_panel is not None:
                self.learning_panel.update_insights(prompt, success, result_data)
            
            # Log learning update
            status = "successful" if success else "failed"
            self.log_message(f"🧠 Learning updated: {status} generation")
            
        except Exception as e:
            logger.error(f"Error updating learning insights: {e}")
    
    # Helper methods for tab integration
    
    def log_status(self, message: str, status_type: str = "info"):
        """Log status message to console"""
        if self.status_console:
            self.status_console.log_status(message, status_type)
    
    def log_processing_start(self, operation: str, details: str = ""):
        """Log start of processing with timing"""
        if self.status_console:
            self.status_console.log_processing_start(operation, details)
    
    def log_processing_complete(self, operation: str, success: bool = True, details: str = ""):
        """Log completion of processing with timing"""
        if self.status_console:
            self.status_console.log_processing_complete(operation, success, details)
    
    def log_file_operation(self, operation: str, filename: str, success: bool = True):
        """Log file operations"""
        if self.status_console:
            self.status_console.log_file_operation(operation, filename, success)
    
    def log_error(self, error_message: str, context: str = ""):
        """Log error message"""
        if self.status_console:
            self.status_console.log_error(error_message, context)
    
    def show_progress(self):
        """Show progress bar"""
        if self.status_console:
            self.status_console.show_progress()
    
    def hide_progress(self):
        """Hide progress bar"""
        if self.status_console:
            self.status_console.hide_progress()
    
    def setup_keyboard_callbacks(self, primary_action=None, primary_widget=None, 
                                browse_image=None, save_result=None, clear_all=None,
                                improve_ai=None, filter_training=None, ai_chat=None):
        """Setup keyboard callbacks from the parent tab"""
        if self.keyboard_manager:
            if primary_action and primary_widget:
                self.keyboard_manager.register_primary_action(primary_action, primary_widget)
            
            if browse_image or save_result or clear_all:
                self.keyboard_manager.register_file_actions(
                    open_file=browse_image,
                    save_result=save_result,
                    new_operation=clear_all
                )
            
            if improve_ai or filter_training or ai_chat:
                self.keyboard_manager.register_ai_actions(
                    improve_callback=improve_ai,
                    filter_callback=filter_training,
                    chat_callback=ai_chat
                )
    
    def set_operation_in_progress(self, in_progress: bool):
        """Update operation status for keyboard manager"""
        if self.keyboard_manager:
            self.keyboard_manager.set_operation_in_progress(in_progress)
