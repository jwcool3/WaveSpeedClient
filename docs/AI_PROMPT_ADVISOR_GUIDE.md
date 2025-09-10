# 🤖 AI Prompt Advisor Integration Guide

## Overview

The AI Prompt Advisor is a powerful new feature that provides intelligent prompt suggestions using Claude or OpenAI APIs. This feature helps users create better prompts for all AI models in the WaveSpeed AI Creative Suite.

## ✨ Features

### 🎯 **Smart Prompt Improvement**
- **3 Enhancement Types**: Clarity, Creativity, and Technical optimization
- **Model-Specific Guidance**: Tailored suggestions for each AI model's strengths
- **Context-Aware**: Understands the current prompt and suggests improvements

### 🎨 **Seamless Integration**
- **✨ Improve with AI Button**: Added to all prompt sections
- **Right-Click Context Menu**: Quick access from any prompt text field
- **Visual Suggestion Panel**: Clean, organized display of AI suggestions
- **One-Click Application**: Apply suggestions directly to your prompt

### 🔧 **Multiple AI Providers**
- **Claude API**: Anthropic's Claude-3-Sonnet for advanced reasoning
- **OpenAI API**: GPT-4 for comprehensive prompt optimization
- **Automatic Fallback**: Uses available API if primary provider fails

## 🚀 Setup Instructions

### 1. **Install Dependencies**
```bash
pip install aiohttp==3.9.1
```

### 2. **Configure API Keys**
Add to your `.env` file:
```env
# AI Prompt Advisor Configuration (Optional)
CLAUDE_API_KEY=your_claude_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
AI_ADVISOR_PROVIDER=claude
```

### 3. **Get API Keys**

#### **Claude API Key**
1. Visit [Anthropic Console](https://console.anthropic.com/)
2. Create an account and navigate to API Keys
3. Generate a new API key
4. Copy the key to your `.env` file

#### **OpenAI API Key**
1. Visit [OpenAI Platform](https://platform.openai.com/api-keys)
2. Create an account and navigate to API Keys
3. Generate a new API key
4. Copy the key to your `.env` file

## 🎯 How to Use

### **Method 1: AI Improve Button**
1. **Enter your prompt** in any tab's prompt field
2. **Click "✨ Improve with AI"** button
3. **Review suggestions** in the popup panel
4. **Click "Use This Prompt"** to apply your favorite suggestion

### **Method 2: Right-Click Context Menu**
1. **Right-click** in any prompt text field
2. **Select "✨ Improve with AI"** from the context menu
3. **Choose from suggestions** and apply as needed

### **Method 3: Copy to Clipboard**
1. **Generate suggestions** using either method above
2. **Click "Copy"** on any suggestion
3. **Paste** into your prompt field manually

## 🎨 Model-Specific Guidance

### **🍌 Nano Banana Editor**
- **Focus**: Artistic transformations and creative edits
- **Style**: Vivid, descriptive language for visual elements
- **Examples**: "Transform into a watercolor painting with soft pastels and dreamy lighting"

### **✨ SeedEdit**
- **Focus**: Precise, controlled edits with fine-tuned adjustments
- **Style**: Specific, technical language when needed
- **Examples**: "Adjust the lighting to golden hour with warm, soft shadows"

### **🌟 Seedream V4**
- **Focus**: Complex multi-step transformations
- **Style**: "Change action + Object + Target feature" format
- **Examples**: "Change the person's clothing to medieval armor with intricate metallic details"

### **🎬 Wan 2.2 (Image to Video)**
- **Focus**: Realistic motion and natural animations
- **Style**: Natural, believable motion descriptions
- **Examples**: "Leaves gently swaying in a soft breeze with dappled sunlight"

### **🕺 SeedDance Pro**
- **Focus**: Movement, camera work, and cinematic elements
- **Style**: Dynamic actions with camera directions
- **Examples**: "Person dancing with smooth camera rotation and dynamic lighting changes"

## 🔧 Technical Details

### **Architecture**
```
core/ai_prompt_advisor.py          # Main AI advisor service
ui/components/ai_prompt_suggestions.py  # UI components
app/config.py                      # Configuration management
```

### **Key Components**

#### **AIPromptAdvisor Class**
- Manages API connections and prompt improvement logic
- Handles both Claude and OpenAI integrations
- Provides model-specific system prompts

#### **PromptSuggestionPanel Class**
- Displays AI suggestions in organized panels
- Handles user interactions (use, copy, close)
- Shows loading states and error messages

#### **AIImproveButton Class**
- Adds "✨ Improve with AI" buttons to prompt sections
- Manages button state based on API availability
- Provides tooltips for user guidance

#### **PromptContextMenu Class**
- Adds right-click context menu to prompt text fields
- Includes standard text operations (cut, copy, paste)
- Integrates AI improvement functionality

### **API Integration**

#### **Claude API**
- **Model**: claude-3-sonnet-20240229
- **Endpoint**: https://api.anthropic.com/v1/messages
- **Features**: Advanced reasoning, creative suggestions

#### **OpenAI API**
- **Model**: gpt-4
- **Endpoint**: https://api.openai.com/v1/chat/completions
- **Features**: Comprehensive prompt optimization

## 🎯 User Experience Features

### **Smart Availability Detection**
- **Automatic Detection**: Checks for available API keys on startup
- **Graceful Degradation**: Disables features if no APIs are configured
- **User Feedback**: Clear tooltips and error messages

### **Professional UI Design**
- **Consistent Integration**: Matches existing WaveSpeed AI design
- **Loading States**: Shows progress during AI processing
- **Error Handling**: Graceful error messages with helpful guidance

### **Performance Optimization**
- **Async Processing**: Non-blocking AI requests
- **Background Threading**: UI remains responsive during processing
- **Caching**: Efficient API usage and response handling

## 🔒 Privacy & Security

### **API Key Management**
- **Environment Variables**: Secure storage in `.env` file
- **No Hardcoding**: Keys never stored in source code
- **Optional Feature**: Works without AI advisor if keys not provided

### **Data Handling**
- **Prompt Privacy**: Only current prompt sent to AI APIs
- **No Storage**: AI suggestions not permanently stored
- **User Control**: Users choose which suggestions to apply

## 🚀 Advanced Features

### **Context-Aware Suggestions**
- **Model Understanding**: AI knows which model will process the prompt
- **Style Optimization**: Suggestions tailored to each AI's strengths
- **Best Practices**: Incorporates prompt engineering expertise

### **Multi-Provider Support**
- **Primary/Secondary**: Configurable API provider preference
- **Automatic Fallback**: Switches to available provider if needed
- **Provider Comparison**: Different AI models provide varied perspectives

### **Extensible Design**
- **Easy Integration**: Simple function calls to add AI features
- **Modular Architecture**: Components can be used independently
- **Future-Proof**: Ready for additional AI providers

## 🎯 Best Practices

### **For Users**
1. **Start Simple**: Begin with basic prompts, then use AI to enhance
2. **Experiment**: Try different suggestion types (clarity, creativity, technical)
3. **Iterate**: Use AI suggestions as starting points for further refinement
4. **Save Favorites**: Use the existing prompt saving system for successful combinations

### **For Developers**
1. **Error Handling**: Always check API availability before showing AI features
2. **User Feedback**: Provide clear status messages and loading indicators
3. **Performance**: Use async processing to maintain UI responsiveness
4. **Extensibility**: Design components to be easily integrated into new tabs

## 🔧 Troubleshooting

### **Common Issues**

#### **"AI Advisor Unavailable" Message**
- **Cause**: No API keys configured
- **Solution**: Add Claude or OpenAI API keys to `.env` file

#### **"Failed to Generate Suggestions" Error**
- **Cause**: API request failed or network issue
- **Solution**: Check internet connection and API key validity

#### **Button Disabled**
- **Cause**: No AI APIs available
- **Solution**: Configure at least one API key in `.env` file

#### **Slow Response Times**
- **Cause**: API rate limits or network latency
- **Solution**: Wait a moment and try again, or check API usage limits

### **Debug Information**
- **Logs**: Check application logs for detailed error information
- **API Status**: Verify API keys are valid and have sufficient credits
- **Network**: Ensure stable internet connection for API requests

## 🎉 Success Stories

### **Enhanced Creative Workflows**
- **Artistic Prompts**: Users create more vivid, descriptive prompts for Nano Banana
- **Technical Precision**: SeedEdit users get better guidance for fine-tuned edits
- **Video Descriptions**: Wan 2.2 and SeedDance users create more cinematic prompts

### **Improved Results**
- **Better AI Output**: Enhanced prompts lead to higher quality AI generations
- **Reduced Iterations**: Users get better results on first attempts
- **Creative Exploration**: AI suggestions inspire new creative directions

## 🔮 Future Enhancements

### **Planned Features**
- **Image Analysis**: Analyze uploaded images to suggest relevant prompts
- **Learning System**: Remember user preferences and improve suggestions over time
- **Batch Processing**: Improve multiple prompts simultaneously
- **Custom Templates**: User-defined prompt templates and styles

### **Advanced Integrations**
- **Workflow Suggestions**: Recommend next steps in cross-tab workflows
- **Style Transfer**: Suggest prompts based on successful previous generations
- **Community Sharing**: Share and discover effective prompt patterns

---

## 🎯 Quick Start Checklist

- [ ] Install `aiohttp==3.9.1` dependency
- [ ] Add API keys to `.env` file (Claude or OpenAI)
- [ ] Restart the application
- [ ] Enter a prompt in any tab
- [ ] Click "✨ Improve with AI" button
- [ ] Review and apply suggestions
- [ ] Enjoy enhanced AI generations!

**The AI Prompt Advisor transforms your creative workflow by providing intelligent, model-specific prompt suggestions that help you achieve better results with every AI generation.**
