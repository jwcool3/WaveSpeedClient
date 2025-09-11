# 🖼️ AI Image Analysis Integration Guide

## Overview
This guide outlines how to integrate image analysis capabilities into the AI chat system to automatically improve prompts based on visual content analysis. The AI will be able to "see" the input image and provide context-aware suggestions.

## 🎯 Goals
- **Visual Context Understanding**: AI analyzes the input image to understand what's in it
- **Automatic Prompt Enhancement**: Suggests improvements based on visual content
- **Smart Recommendations**: Provides specific suggestions based on what it sees
- **Seamless Integration**: Works with existing AI chat system

## 🏗️ Architecture Overview

### 1. Image Analysis Pipeline
```
Input Image → Image Processing → AI Vision Analysis → Context Extraction → Prompt Enhancement
```

### 2. Integration Points
- **AI Chat Component**: Enhanced to accept and analyze images
- **Image Display System**: Pass image data to AI chat
- **AI Advisor**: Extended with vision capabilities
- **Prompt Enhancement**: Context-aware suggestions

## 📋 Implementation Plan

### Phase 1: Image Data Integration
**Goal**: Pass image data to AI chat system

#### 1.1 Modify AI Chat Component
**File**: `ui/components/ai_prompt_chat.py`

**Changes Needed**:
```python
class AIPromptChat:
    def __init__(self, parent, on_prompt_updated: Optional[Callable] = None):
        # Add image analysis capabilities
        self.current_image = None
        self.image_analysis_available = False
        self.vision_model = None
        
    def set_current_image(self, image_path: str):
        """Set the current image for analysis"""
        self.current_image = image_path
        self.image_analysis_available = bool(image_path)
        
    def get_image_analysis_context(self) -> str:
        """Get image analysis context for AI"""
        if not self.image_analysis_available:
            return ""
        
        # This will be implemented in Phase 2
        return f"Current image: {self.current_image}"
```

#### 1.2 Update Optimized Layout
**File**: `ui/components/optimized_image_layout.py`

**Changes Needed**:
```python
def add_ai_chat_interface(self, prompt_widget, model_type, tab_instance):
    # ... existing code ...
    
    # Pass image reference to AI chat
    def apply_prompt_callback(improved_prompt: str):
        prompt_widget.delete("1.0", tk.END)
        prompt_widget.insert("1.0", improved_prompt)
        logger.info("Applied improved prompt from AI chat")
    
    # Create AI chat with image awareness
    self.ai_model_chat = AIPromptChat(
        parent=self.ai_chat_container,
        on_prompt_updated=apply_prompt_callback
    )
    
    # Set up image reference
    self.ai_model_chat.set_image_reference(self)
    
    # ... rest of existing code ...
```

#### 1.3 Image Reference System
**File**: `ui/components/optimized_image_layout.py`

**New Methods**:
```python
def get_current_image_path(self) -> Optional[str]:
    """Get the current input image path"""
    return self.selected_image_path

def update_ai_chat_image(self):
    """Update AI chat with current image"""
    if hasattr(self, 'ai_model_chat'):
        image_path = self.get_current_image_path()
        self.ai_model_chat.set_current_image(image_path)
        
    if hasattr(self, 'filter_training_chat'):
        image_path = self.get_current_image_path()
        self.filter_training_chat.set_current_image(image_path)
```

### Phase 2: Vision Model Integration
**Goal**: Integrate AI vision capabilities

#### 2.1 Extend AI Advisor
**File**: `core/ai_prompt_advisor.py`

**New Methods**:
```python
class AIPromptAdvisor:
    def __init__(self):
        # ... existing code ...
        self.vision_available = self._check_vision_availability()
        
    def _check_vision_availability(self) -> bool:
        """Check if vision models are available"""
        try:
            # Check for OpenAI GPT-4V or Claude 3.5 Sonnet with vision
            return bool(os.getenv('OPENAI_API_KEY') or os.getenv('CLAUDE_API_KEY'))
        except:
            return False
    
    async def analyze_image(self, image_path: str, context: str = "") -> dict:
        """Analyze image and return structured analysis"""
        if not self.vision_available:
            return {"error": "Vision capabilities not available"}
        
        try:
            # Choose the best available vision model
            if os.getenv('OPENAI_API_KEY'):
                return await self._analyze_with_openai_vision(image_path, context)
            elif os.getenv('CLAUDE_API_KEY'):
                return await self._analyze_with_claude_vision(image_path, context)
        except Exception as e:
            logger.error(f"Error analyzing image: {e}")
            return {"error": str(e)}
    
    async def _analyze_with_openai_vision(self, image_path: str, context: str) -> dict:
        """Analyze image using OpenAI GPT-4V"""
        # Implementation for OpenAI vision
        pass
    
    async def _analyze_with_claude_vision(self, image_path: str, context: str) -> dict:
        """Analyze image using Claude 3.5 Sonnet with vision"""
        # Implementation for Claude vision
        pass
```

#### 2.2 Vision Analysis Prompts
**File**: `core/ai_prompt_advisor.py`

**New System Prompts**:
```python
class SystemPrompts:
    # ... existing prompts ...
    
    IMAGE_ANALYSIS = """You are an expert image analyst specializing in AI prompt optimization. 

Your task is to analyze the provided image and generate context-aware prompt suggestions for AI image editing/generation models.

## Analysis Framework:
1. **Visual Content**: Describe what you see in the image
2. **Technical Details**: Note composition, lighting, colors, style
3. **Potential Edits**: Identify what could be modified, added, or removed
4. **Prompt Opportunities**: Suggest specific prompt improvements

## Output Format:
Return a JSON object with:
```json
{
  "visual_description": "Detailed description of what's in the image",
  "technical_analysis": {
    "composition": "Analysis of composition and framing",
    "lighting": "Lighting conditions and mood",
    "colors": "Color palette and style",
    "quality": "Image quality and technical aspects"
  },
  "edit_suggestions": [
    {
      "type": "removal|addition|modification|style_change",
      "description": "What could be changed",
      "prompt_suggestion": "Specific prompt for this edit",
      "confidence": 0.8
    }
  ],
  "prompt_improvements": [
    {
      "current_issue": "What's unclear or could be better",
      "suggestion": "How to improve the prompt",
      "example": "Improved prompt example"
    }
  ]
}
```

Focus on practical, actionable suggestions that would help users create better prompts for AI image editing."""

    IMAGE_CONTEXT_PROMPT = """Based on the image analysis, provide context-aware prompt suggestions.

Current prompt: {current_prompt}
Image analysis: {image_analysis}
Model: {model_type}

Provide specific suggestions for improving the prompt based on what you see in the image."""
```

### Phase 3: Smart Prompt Enhancement
**Goal**: Use image analysis to enhance prompts automatically

#### 3.1 Enhanced AI Chat Response
**File**: `ui/components/ai_prompt_chat.py`

**New Methods**:
```python
async def get_ai_response_with_image(self, user_message: str) -> str:
    """Get AI response with image analysis context"""
    try:
        advisor = get_ai_advisor()
        
        # Get image analysis if available
        image_context = ""
        if self.current_image and os.path.exists(self.current_image):
            image_analysis = await advisor.analyze_image(self.current_image, user_message)
            if "error" not in image_analysis:
                image_context = f"\n\nImage Analysis Context:\n{json.dumps(image_analysis, indent=2)}"
        
        # Enhanced context with image information
        context = f"""
Current prompt: {self.current_prompt}
Tab: {self.current_tab_name}
Chat history: {self.chat_history[-3:] if len(self.chat_history) > 3 else self.chat_history}
User message: {user_message}
{image_context}

Please respond as a helpful AI assistant that specializes in prompt improvement. Use the image analysis to provide more specific and accurate suggestions.
"""
        
        # Use enhanced context for AI response
        if self.filter_training:
            return await self.get_smart_filter_training_response(user_message, advisor, image_context)
        else:
            return await self.get_enhanced_prompt_response(user_message, advisor, image_context)
            
    except Exception as e:
        logger.error(f"Error getting AI response with image: {e}")
        return f"I encountered an error: {str(e)}. Please try again."

async def get_enhanced_prompt_response(self, user_message: str, advisor, image_context: str) -> str:
    """Get enhanced prompt response with image context"""
    # Implementation for image-aware prompt improvement
    pass
```

#### 3.2 Automatic Prompt Suggestions
**File**: `ui/components/ai_prompt_chat.py`

**New Methods**:
```python
async def get_automatic_image_suggestions(self, advisor) -> str:
    """Get automatic suggestions based on image analysis"""
    if not self.current_image or not os.path.exists(self.current_image):
        return "No image available for analysis."
    
    try:
        # Analyze the image
        image_analysis = await advisor.analyze_image(self.current_image, "automatic prompt suggestions")
        
        if "error" in image_analysis:
            return f"Could not analyze image: {image_analysis['error']}"
        
        # Generate suggestions based on analysis
        suggestions = []
        
        # Visual content suggestions
        if "visual_description" in image_analysis:
            suggestions.append(f"**What I see:** {image_analysis['visual_description']}")
        
        # Edit suggestions
        if "edit_suggestions" in image_analysis:
            suggestions.append("**Potential edits I can suggest:**")
            for edit in image_analysis["edit_suggestions"][:3]:  # Top 3 suggestions
                suggestions.append(f"• {edit['description']} - \"{edit['prompt_suggestion']}\"")
        
        # Prompt improvements
        if "prompt_improvements" in image_analysis:
            suggestions.append("**Prompt improvements:**")
            for improvement in image_analysis["prompt_improvements"][:2]:  # Top 2 improvements
                suggestions.append(f"• {improvement['suggestion']}")
                suggestions.append(f"  Example: \"{improvement['example']}\"")
        
        return "\n".join(suggestions) if suggestions else "I can see the image but don't have specific suggestions at the moment."
        
    except Exception as e:
        logger.error(f"Error getting automatic suggestions: {e}")
        return f"Error analyzing image: {str(e)}"
```

### Phase 4: UI Enhancements
**Goal**: Update UI to show image analysis and suggestions

#### 4.1 Image Analysis Display
**File**: `ui/components/ai_prompt_chat.py`

**New UI Elements**:
```python
def setup_ui(self):
    # ... existing UI setup ...
    
    # Add image analysis section
    if self.filter_training:
        # Filter training mode - no image analysis
        pass
    else:
        # Normal mode - add image analysis
        self.setup_image_analysis_section()

def setup_image_analysis_section(self):
    """Setup image analysis display section"""
    # Image analysis frame
    self.image_analysis_frame = ttk.LabelFrame(self.container, text="🖼️ Image Analysis", padding="5")
    self.image_analysis_frame.pack(fill=tk.X, pady=(0, 10))
    
    # Image analysis display
    self.image_analysis_display = tk.Text(
        self.image_analysis_frame,
        height=4,
        wrap=tk.WORD,
        font=('Arial', 9),
        bg='#f8f9fa',
        state=tk.DISABLED
    )
    self.image_analysis_display.pack(fill=tk.X)
    
    # Auto-analyze button
    self.auto_analyze_btn = ttk.Button(
        self.image_analysis_frame,
        text="🔍 Analyze Image & Suggest",
        command=self.auto_analyze_image
    )
    self.auto_analyze_btn.pack(pady=(5, 0))
    
    # Initially hide if no image
    self.update_image_analysis_visibility()

def update_image_analysis_visibility(self):
    """Update visibility of image analysis section"""
    if self.current_image and os.path.exists(self.current_image):
        self.image_analysis_frame.pack(fill=tk.X, pady=(0, 10))
        self.auto_analyze_btn.config(state="normal")
    else:
        self.image_analysis_frame.pack_forget()
        self.auto_analyze_btn.config(state="disabled")

async def auto_analyze_image(self):
    """Automatically analyze image and show suggestions"""
    if not self.current_image:
        return
    
    # Show loading state
    self.auto_analyze_btn.config(text="🔄 Analyzing...", state="disabled")
    
    try:
        advisor = get_ai_advisor()
        suggestions = await self.get_automatic_image_suggestions(advisor)
        
        # Display suggestions
        self.image_analysis_display.config(state=tk.NORMAL)
        self.image_analysis_display.delete("1.0", tk.END)
        self.image_analysis_display.insert("1.0", suggestions)
        self.image_analysis_display.config(state=tk.DISABLED)
        
    except Exception as e:
        logger.error(f"Error in auto-analyze: {e}")
        self.image_analysis_display.config(state=tk.NORMAL)
        self.image_analysis_display.delete("1.0", tk.END)
        self.image_analysis_display.insert("1.0", f"Error analyzing image: {str(e)}")
        self.image_analysis_display.config(state=tk.DISABLED)
    
    finally:
        self.auto_analyze_btn.config(text="🔍 Analyze Image & Suggest", state="normal")
```

#### 4.2 Enhanced Button Actions
**File**: `ui/components/ai_prompt_chat.py`

**Updated Methods**:
```python
def quick_improve(self):
    """Quick improve prompt action with image context"""
    if self.current_image and os.path.exists(self.current_image):
        self.message_entry.delete("1.0", tk.END)
        self.message_entry.insert("1.0", "Analyze the image and improve this prompt based on what you see")
    else:
        self.message_entry.delete("1.0", tk.END)
        self.message_entry.insert("1.0", "Can you improve this prompt and explain what changes you made?")
    self.send_message()

def quick_explain(self):
    """Quick explain prompt action with image context"""
    if self.current_image and os.path.exists(self.current_image):
        self.message_entry.delete("1.0", tk.END)
        self.message_entry.insert("1.0", "Look at the image and explain what this prompt does and how it could be better")
    else:
        self.message_entry.delete("1.0", tk.END)
        self.message_entry.insert("1.0", "Can you explain what this prompt does and how it could be better?")
    self.send_message()
```

### Phase 5: Integration with Existing Systems
**Goal**: Seamlessly integrate with current workflow

#### 5.1 Image Update Triggers
**File**: `ui/components/optimized_image_layout.py`

**Enhanced Methods**:
```python
def update_input_image(self, image_path: str) -> bool:
    """Update input image and notify AI chat"""
    # ... existing image update code ...
    
    # Notify AI chat of image change
    self.update_ai_chat_image()
    
    return True

def on_image_selected(self, file_path, replacing_image=False):
    """Handle image selection and update AI chat"""
    # ... existing image selection code ...
    
    # Update AI chat with new image
    self.update_ai_chat_image()
```

#### 5.2 Cross-Tab Integration
**File**: `ui/components/optimized_image_layout.py`

**New Methods**:
```python
def sync_image_with_ai_chat(self):
    """Sync current image with AI chat across all instances"""
    if hasattr(self, 'ai_model_chat'):
        self.ai_model_chat.set_current_image(self.get_current_image_path())
        self.ai_model_chat.update_image_analysis_visibility()
        
    if hasattr(self, 'filter_training_chat'):
        # Filter training doesn't use image analysis
        pass
```

## 🔧 Technical Implementation Details

### Image Processing Pipeline
1. **Image Validation**: Check if image exists and is readable
2. **Format Conversion**: Convert to format suitable for AI vision models
3. **Size Optimization**: Resize if too large for API limits
4. **Base64 Encoding**: Encode for API transmission
5. **Analysis Request**: Send to vision model
6. **Response Processing**: Parse and structure results

### API Integration
- **OpenAI GPT-4V**: For detailed image analysis
- **Claude 3.5 Sonnet**: Alternative vision model
- **Fallback Handling**: Graceful degradation when vision unavailable

### Performance Considerations
- **Caching**: Cache image analysis results
- **Async Processing**: Non-blocking image analysis
- **Error Handling**: Robust error handling and fallbacks
- **Rate Limiting**: Respect API rate limits

## 🎯 User Experience Flow

### 1. Image Loading
1. User loads image into tab
2. AI chat automatically detects image
3. Image analysis section becomes visible
4. "Analyze Image & Suggest" button becomes active

### 2. Automatic Analysis
1. User clicks "Analyze Image & Suggest"
2. AI analyzes image content
3. Suggestions appear in image analysis section
4. User can use suggestions or ask for more specific help

### 3. Context-Aware Chat
1. User asks questions about prompt improvement
2. AI considers both prompt and image context
3. Provides more accurate and specific suggestions
4. Can reference specific elements in the image

### 4. Smart Suggestions
1. AI identifies potential edits based on image content
2. Suggests specific prompt improvements
3. Provides examples of better prompts
4. Explains reasoning based on visual analysis

## 🚀 Future Enhancements

### Advanced Features
- **Object Detection**: Identify specific objects for targeted editing
- **Style Analysis**: Analyze artistic style for style transfer suggestions
- **Composition Analysis**: Suggest composition improvements
- **Color Analysis**: Provide color palette suggestions
- **Quality Assessment**: Identify areas for quality improvement

### Integration Opportunities
- **Batch Processing**: Analyze multiple images
- **Comparison Mode**: Compare before/after images
- **Template Matching**: Match images to prompt templates
- **Learning System**: Learn from user preferences

## 📝 Implementation Checklist

### Phase 1: Foundation
- [ ] Add image reference to AI chat component
- [ ] Update optimized layout to pass image data
- [ ] Create image reference system
- [ ] Test basic image data flow

### Phase 2: Vision Integration
- [ ] Extend AI advisor with vision capabilities
- [ ] Implement OpenAI GPT-4V integration
- [ ] Implement Claude 3.5 Sonnet integration
- [ ] Create vision analysis prompts
- [ ] Test vision model responses

### Phase 3: Smart Enhancement
- [ ] Implement image-aware prompt responses
- [ ] Create automatic suggestion system
- [ ] Add image context to chat responses
- [ ] Test enhanced prompt suggestions

### Phase 4: UI Updates
- [ ] Add image analysis display section
- [ ] Create auto-analyze functionality
- [ ] Update button actions for image context
- [ ] Test UI integration

### Phase 5: System Integration
- [ ] Integrate with image update triggers
- [ ] Add cross-tab synchronization
- [ ] Implement error handling and fallbacks
- [ ] Test complete workflow

## 🎉 Expected Benefits

### For Users
- **More Accurate Suggestions**: AI sees what you're working with
- **Context-Aware Help**: Suggestions based on actual image content
- **Faster Workflow**: Automatic analysis and suggestions
- **Better Results**: More targeted prompt improvements

### For Developers
- **Enhanced AI Capabilities**: Vision-powered prompt optimization
- **Better User Experience**: More intelligent and helpful AI
- **Competitive Advantage**: Advanced image analysis features
- **Extensible Architecture**: Foundation for future enhancements

This guide provides a comprehensive roadmap for implementing image analysis in the AI chat system, making it much more powerful and context-aware!
