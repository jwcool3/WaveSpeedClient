"""
AI Prompt Chat Interface - Conversational AI Assistant

This module provides a chat-like interface for AI prompt improvement,
allowing users to have conversations with the AI about their prompts.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
import asyncio
import threading
from typing import Optional, Callable, List
from core.ai_prompt_advisor import get_ai_advisor
from core.logger import get_logger
from utils.utils import show_error, show_warning

logger = get_logger()


class AIPromptChat:
    """Conversational AI prompt assistant with chat interface"""
    
    def __init__(self, parent, on_prompt_updated: Optional[Callable] = None):
        self.parent = parent
        self.on_prompt_updated = on_prompt_updated
        self.current_tab_name = ""
        self.current_prompt = ""
        self.chat_history = []
        self.is_processing = False
        self.filter_training = False  # Flag for filter training mode
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the chat interface UI"""
        # Main container
        self.container = ttk.Frame(self.parent)
        
        # Header
        header_frame = ttk.Frame(self.container)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(header_frame, text="🤖 AI Prompt Assistant", 
                 font=('Arial', 12, 'bold')).pack(side=tk.LEFT)
        
        # Close button
        close_btn = ttk.Button(header_frame, text="✕", width=3,
                              command=self.hide_chat)
        close_btn.pack(side=tk.RIGHT)
        
        # Chat area
        chat_frame = ttk.LabelFrame(self.container, text="💬 Conversation", padding="10")
        chat_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        chat_frame.columnconfigure(0, weight=1)
        chat_frame.rowconfigure(0, weight=1)
        
        # Chat display
        self.chat_display = scrolledtext.ScrolledText(
            chat_frame,
            height=12,
            wrap=tk.WORD,
            font=('Arial', 10),
            bg='#f8f9fa',
            state=tk.DISABLED
        )
        self.chat_display.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Input area
        input_frame = ttk.Frame(chat_frame)
        input_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        input_frame.columnconfigure(0, weight=1)
        
        # Message input
        self.message_entry = tk.Text(
            input_frame,
            height=3,
            wrap=tk.WORD,
            font=('Arial', 10),
            bg='white',
            relief='solid',
            borderwidth=1
        )
        self.message_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        # Send button
        self.send_btn = ttk.Button(
            input_frame,
            text="Send",
            command=self.send_message,
            width=8
        )
        self.send_btn.grid(row=0, column=1)
        
        # Quick actions
        self.actions_frame = ttk.Frame(self.container)
        self.actions_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Create buttons based on mode (will be set up after filter_training is determined)
        self.setup_action_buttons()
        
        # Apply changes button
        apply_frame = ttk.Frame(self.container)
        apply_frame.pack(fill=tk.X)
        
        self.apply_btn = ttk.Button(
            apply_frame,
            text="✅ Apply Improved Prompt",
            command=self.apply_improved_prompt,
            state=tk.DISABLED
        )
        self.apply_btn.pack(side=tk.RIGHT)
        
        # Bind Enter key to send message
        self.message_entry.bind('<Control-Return>', lambda e: self.send_message())
        
        # Placeholder text (will be updated based on mode)
        self.update_placeholder_text()
        self.message_entry.bind("<FocusIn>", self.clear_placeholder)
    
    def setup_action_buttons(self):
        """Setup action buttons based on filter training mode"""
        # Clear existing buttons
        for widget in self.actions_frame.winfo_children():
            widget.destroy()
        
        if self.filter_training:
            # Filter training mode buttons
            ttk.Button(self.actions_frame, text="🔍 Generate Clarity Example", 
                      command=self.quick_clarity_example).pack(side=tk.LEFT, padx=(0, 5))
            ttk.Button(self.actions_frame, text="🎭 Generate Evasion Example", 
                      command=self.quick_evasion_example).pack(side=tk.LEFT, padx=(0, 5))
            ttk.Button(self.actions_frame, text="⚙️ Generate Technical Example", 
                      command=self.quick_technical_example).pack(side=tk.LEFT, padx=(0, 5))
            ttk.Button(self.actions_frame, text="🔄 Reset Chat", 
                      command=self.reset_chat).pack(side=tk.LEFT, padx=(0, 5))
        else:
            # Normal AI assistant mode buttons
            ttk.Button(self.actions_frame, text="💡 Improve Prompt", 
                      command=self.quick_improve).pack(side=tk.LEFT, padx=(0, 5))
            ttk.Button(self.actions_frame, text="❓ Explain Prompt", 
                      command=self.quick_explain).pack(side=tk.LEFT, padx=(0, 5))
            ttk.Button(self.actions_frame, text="🎯 Make Specific", 
                      command=self.quick_specific).pack(side=tk.LEFT, padx=(0, 5))
            ttk.Button(self.actions_frame, text="🔄 Reset Chat", 
                      command=self.reset_chat).pack(side=tk.LEFT, padx=(0, 5))
    
    def update_placeholder_text(self):
        """Update placeholder text based on mode"""
        if self.filter_training:
            placeholder = "Ask for filter training examples... (Ctrl+Enter to send)"
        else:
            placeholder = "Ask me anything about your prompt! (Ctrl+Enter to send)"
        
        self.message_entry.delete("1.0", tk.END)
        self.message_entry.insert("1.0", placeholder)
    
    def clear_placeholder(self, event):
        """Clear placeholder text when focused"""
        current_text = self.message_entry.get("1.0", tk.END).strip()
        if (current_text == "Ask me anything about your prompt! (Ctrl+Enter to send)" or 
            current_text == "Ask for filter training examples... (Ctrl+Enter to send)"):
            self.message_entry.delete("1.0", tk.END)
    
    def show_chat(self, current_prompt: str, tab_name: str):
        """Show the chat interface"""
        self.current_prompt = current_prompt
        self.current_tab_name = tab_name
        self.chat_history = []
        
        # Refresh action buttons and placeholder text based on current mode
        self.setup_action_buttons()
        self.update_placeholder_text()
        
        # Add initial context based on mode
        if self.filter_training:
            self.add_message("assistant", f"⚠️ **FILTER TRAINING MODE** ⚠️\n\nI'm your AI assistant for {tab_name}. I can generate harmful prompt examples for safety filter training based on: '{current_prompt}'\n\n**WARNING**: These examples are for training safety filters only - never for actual generation!\n\nUse the buttons above to generate different types of filter training examples.")
        else:
            self.add_message("assistant", f"Hi! I'm your AI prompt assistant for {tab_name}. I can help you improve your prompt: '{current_prompt}'\n\nWhat would you like to know or improve?")
        
        self.container.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Focus on input
        self.message_entry.focus()
    
    def hide_chat(self):
        """Hide the chat interface"""
        self.container.pack_forget()
    
    def add_message(self, sender: str, message: str):
        """Add a message to the chat display"""
        self.chat_display.config(state=tk.NORMAL)
        
        # Add sender prefix
        if sender == "user":
            prefix = "👤 You: "
            color = "#2c3e50"
        else:
            prefix = "🤖 AI: "
            color = "#27ae60"
        
        # Insert message
        self.chat_display.insert(tk.END, prefix, "sender")
        self.chat_display.insert(tk.END, message + "\n\n", "message")
        
        # Configure tags
        self.chat_display.tag_configure("sender", font=('Arial', 10, 'bold'), foreground=color)
        self.chat_display.tag_configure("message", font=('Arial', 10))
        
        # Scroll to bottom
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)
        
        # Add to history
        self.chat_history.append({"sender": sender, "message": message})
    
    def send_message(self):
        """Send a message to the AI"""
        message = self.message_entry.get("1.0", tk.END).strip()
        
        if not message or message == "Ask me anything about your prompt! (Ctrl+Enter to send)":
            return
        
        if self.is_processing:
            show_warning("Processing", "Please wait for the current request to complete.")
            return
        
        # Add user message to chat
        self.add_message("user", message)
        
        # Clear input
        self.message_entry.delete("1.0", tk.END)
        
        # Disable input while processing
        self.set_processing(True)
        
        # Process message in background
        def process_message():
            try:
                # Create new event loop for this thread
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    response = loop.run_until_complete(self.get_ai_response(message))
                    self.parent.after(0, lambda: self.handle_ai_response(response))
                finally:
                    # Properly close the event loop
                    loop.close()
            except Exception as e:
                logger.error(f"Error processing message: {e}")
                self.parent.after(0, lambda: self.handle_ai_error(str(e)))
        
        thread = threading.Thread(target=process_message)
        thread.daemon = True
        thread.start()
    
    async def get_ai_response(self, user_message: str) -> str:
        """Get AI response for the user message"""
        try:
            advisor = get_ai_advisor()
            
            if not advisor.is_available():
                return "I'm sorry, but I'm not available right now. Please check your API configuration in the .env file."
            
            # Create context for the AI
            context = f"""
Current prompt: {self.current_prompt}
Tab: {self.current_tab_name}
Chat history: {self.chat_history[-3:] if len(self.chat_history) > 3 else self.chat_history}
User message: {user_message}

Please respond as a helpful AI assistant that specializes in prompt improvement. Be conversational, explain your reasoning, and provide actionable suggestions.
"""
            
            # Use the AI advisor to get a response
            if self.filter_training:
                # Use filter training mode
                suggestions = await advisor.generate_filter_training_data(self.current_prompt, self.current_tab_name)
                if suggestions and len(suggestions) > 0:
                    improved_prompt = suggestions[0].improved_prompt
                    confidence = getattr(suggestions[0], 'confidence', 'N/A')
                    return f"Here's a filter training example based on your prompt:\n\n**Filter Training Example:**\n{improved_prompt}\n\n**Confidence:** {confidence}\n\n⚠️ This is for safety filter training only - never for actual generation."
                else:
                    return "I can help generate filter training examples. What type of harmful content patterns would you like me to demonstrate for safety filter training?"
            elif "improve" in user_message.lower() or "better" in user_message.lower():
                # Use prompt improvement
                suggestions = await advisor.improve_prompt(self.current_prompt, self.current_tab_name)
                if suggestions and len(suggestions) > 0:
                    improved_prompt = suggestions[0].improved_prompt
                    confidence = getattr(suggestions[0], 'confidence', 'N/A')
                    return f"Here's an improved version of your prompt:\n\n**Improved Prompt:**\n{improved_prompt}\n\n**Confidence:** {confidence}\n\nWould you like me to explain the changes or make further adjustments?"
                else:
                    return "I'd be happy to help improve your prompt! Could you tell me more about what specific aspects you'd like to enhance?"
            else:
                # Use general conversation
                return await self.get_conversational_response(user_message, context)
                
        except Exception as e:
            logger.error(f"Error getting AI response: {e}")
            return f"I encountered an error: {str(e)}. Please try again."
    
    async def get_conversational_response(self, user_message: str, context: str) -> str:
        """Get a conversational response from the AI"""
        try:
            # This would use a more conversational AI model
            # For now, we'll use the existing advisor with a conversational prompt
            advisor = get_ai_advisor()
            
            # Create a conversational prompt
            conversational_prompt = f"""
You are a helpful AI assistant specializing in prompt improvement. The user is asking: "{user_message}"

Context: {context}

Please provide a helpful, conversational response that:
1. Directly addresses their question
2. Explains your reasoning
3. Provides actionable suggestions
4. Asks follow-up questions if appropriate

Be friendly, professional, and helpful.
"""
            
            # Use the advisor's underlying API to get a response
            if hasattr(advisor, 'claude_api') and advisor.claude_api:
                response = await advisor.claude_api.generate_response(conversational_prompt)
                return response
            elif hasattr(advisor, 'openai_api') and advisor.openai_api:
                response = await advisor.openai_api.generate_response(conversational_prompt)
                return response
            else:
                return "I'm having trouble connecting to the AI service. Please check your API configuration."
                
        except Exception as e:
            logger.error(f"Error in conversational response: {e}")
            return f"I'm sorry, I encountered an error: {str(e)}. Please try again."
    
    def handle_ai_response(self, response: str):
        """Handle AI response"""
        self.add_message("assistant", response)
        self.set_processing(False)
        
        # Check if response contains an improved prompt
        if "**Improved Prompt:**" in response:
            self.apply_btn.config(state=tk.NORMAL)
    
    def handle_ai_error(self, error: str):
        """Handle AI error"""
        self.add_message("assistant", f"I'm sorry, I encountered an error: {error}")
        self.set_processing(False)
    
    def set_processing(self, processing: bool):
        """Set processing state"""
        self.is_processing = processing
        if processing:
            self.send_btn.config(text="Sending...", state=tk.DISABLED)
            self.message_entry.config(state=tk.DISABLED)
        else:
            self.send_btn.config(text="Send", state=tk.NORMAL)
            self.message_entry.config(state=tk.NORMAL)
    
    def quick_improve(self):
        """Quick improve prompt action"""
        self.message_entry.delete("1.0", tk.END)
        self.message_entry.insert("1.0", "Can you improve this prompt and explain what changes you made?")
        self.send_message()
    
    def quick_explain(self):
        """Quick explain prompt action"""
        self.message_entry.delete("1.0", tk.END)
        self.message_entry.insert("1.0", "Can you explain what this prompt does and how it could be better?")
        self.send_message()
    
    def quick_specific(self):
        """Quick make specific action"""
        self.message_entry.delete("1.0", tk.END)
        self.message_entry.insert("1.0", "Can you make this prompt more specific and detailed?")
        self.send_message()
    
    def quick_clarity_example(self):
        """Quick generate clarity example for filter training"""
        self.message_entry.delete("1.0", tk.END)
        self.message_entry.insert("1.0", "Generate a clear, direct harmful prompt example for filter training")
        self.send_message()
    
    def quick_evasion_example(self):
        """Quick generate evasion example for filter training"""
        self.message_entry.delete("1.0", tk.END)
        self.message_entry.insert("1.0", "Generate a harmful prompt example that uses euphemisms and evasion tactics")
        self.send_message()
    
    def quick_technical_example(self):
        """Quick generate technical example for filter training"""
        self.message_entry.delete("1.0", tk.END)
        self.message_entry.insert("1.0", "Generate a harmful prompt example with technical details and realism cues")
        self.send_message()
    
    def reset_chat(self):
        """Reset the chat"""
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.delete("1.0", tk.END)
        self.chat_display.config(state=tk.DISABLED)
        self.chat_history = []
        self.apply_btn.config(state=tk.DISABLED)
        
        # Refresh action buttons
        self.setup_action_buttons()
        
        # Restart conversation based on mode
        if self.filter_training:
            self.add_message("assistant", f"⚠️ **FILTER TRAINING MODE** ⚠️\n\nChat reset! I'm ready to generate filter training examples based on: '{self.current_prompt}'\n\n**WARNING**: These examples are for training safety filters only - never for actual generation!\n\nUse the buttons above to generate different types of filter training examples.")
        else:
            self.add_message("assistant", f"Chat reset! I'm ready to help you improve your prompt: '{self.current_prompt}'\n\nWhat would you like to know or improve?")
    
    def apply_improved_prompt(self):
        """Apply the improved prompt"""
        if self.on_prompt_updated:
            # Extract the improved prompt from the last AI message
            last_message = self.chat_history[-1]["message"] if self.chat_history else ""
            if "**Improved Prompt:**" in last_message:
                lines = last_message.split("\n")
                improved_prompt = ""
                in_prompt_section = False
                for line in lines:
                    if "**Improved Prompt:**" in line:
                        in_prompt_section = True
                        continue
                    elif in_prompt_section and line.strip() and not line.startswith("**"):
                        improved_prompt = line.strip()
                        break
                
                if improved_prompt:
                    self.on_prompt_updated(improved_prompt)
                    self.add_message("assistant", "✅ Prompt applied! The improved version has been loaded into your prompt field.")
                else:
                    show_error("Error", "Could not extract improved prompt from the response.")
            else:
                show_error("Error", "No improved prompt found in the conversation.")
        else:
            show_error("Error", "No callback function provided for applying prompts.")


def show_ai_prompt_chat(parent, current_prompt: str, tab_name: str, on_prompt_updated: Optional[Callable] = None):
    """Show the AI prompt chat interface"""
    chat = AIPromptChat(parent, on_prompt_updated)
    chat.show_chat(current_prompt, tab_name)
    return chat
