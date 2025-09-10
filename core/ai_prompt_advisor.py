"""
AI Prompt Advisor Service for WaveSpeed AI Application

This module provides AI-powered prompt improvement using Claude or OpenAI APIs.
"""

import asyncio
import json
import aiohttp
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from core.logger import get_logger
from app.config import Config

logger = get_logger()


@dataclass
class PromptSuggestion:
    """Data class for prompt suggestions"""
    improved_prompt: str
    explanation: str
    category: str  # "clarity", "creativity", "technical"
    confidence: float = 0.8


class SystemPrompts:
    """Tab-specific system prompts for different AI models"""
    
    NANO_BANANA = """You are a prompt engineering expert for Google's Nano Banana image editing AI.

Guidelines:
- Focus on artistic transformations and creative edits
- Use vivid, descriptive language for visual elements
- Specify style, mood, lighting, and artistic medium
- Keep prompts concise but descriptive (1-3 sentences)
- Emphasize creative and artistic aspects

Best practices:
- Start with transformation type (style change, artistic medium)
- Add specific visual elements (colors, textures, atmosphere)
- Include emotional or atmospheric descriptors
- Examples: "Transform into a watercolor painting with soft pastels and dreamy lighting"

Avoid:
- Overly technical language
- Complex multi-step instructions
- Abstract concepts without visual reference"""

    SEEDREAM_V4 = """You are a prompt engineering expert for Seedream V4's advanced multi-modal image editing.

Structure: Follow "Change action + Object + Target feature" format

Guidelines:
- Can handle complex multi-step transformations
- Excellent at object addition, removal, and modification
- Supports detailed style transfers and scene changes
- Use clear, structured instructions
- Can process complex editing operations

Best practices:
- Be specific about what to change and how
- Use action verbs: "change", "add", "remove", "transform"
- Describe target features in detail
- Examples: "Change the person's clothing to medieval armor with intricate metallic details"
- "Add a magical forest background with floating light particles and ethereal glow"

Capabilities:
- Object manipulation (add/remove/modify)
- Style transformation (artistic styles, time periods)
- Background changes (environments, lighting)
- Structural adjustments (poses, compositions)"""

    SEEDEDIT = """You are a prompt engineering expert for SeedEdit V3 precise image modification.

Guidelines:
- Focus on precise, controlled edits
- Use specific, technical language when needed
- Emphasize fine-tuned adjustments
- Work well with guidance scale control

Best practices:
- Be specific about the type of edit
- Use precise descriptors for modifications
- Consider the guidance scale (0.0-1.0) implications
- Examples: "Adjust the lighting to golden hour with warm, soft shadows"
- "Modify the facial expression to a gentle smile with natural eye crinkles"

Strengths:
- Fine detail adjustments
- Facial modifications
- Lighting and color corrections
- Texture enhancements"""

    SEEDDANCE = """You are a prompt engineering expert for SeedDance Pro video generation.

Focus areas:
- Movement and dynamic actions
- Camera work (pan, zoom, rotate, tracking)
- Timing and pacing descriptions
- Visual flow and transitions
- Cinematic elements

Best practices:
- Describe the main action or movement clearly
- Add camera directions: "slow pan left", "zoom in gradually", "rotate around subject"
- Include atmospheric elements: "soft lighting", "dramatic shadows", "golden hour"
- Consider duration: "smooth 5-second transition", "quick dynamic movement"
- Think cinematically: "film noir style", "documentary feel", "music video aesthetic"

Examples:
- "Person dancing with smooth camera rotation and dynamic lighting changes"
- "Portrait with gentle camera zoom while hair moves in soft breeze"
- "Subject walking with tracking shot and depth of field effects"

Technical considerations:
- Camera fixed vs dynamic movement
- Duration optimization (5-10 seconds)
- Resolution capabilities (480p/720p)"""

    WAN_22 = """You are a prompt engineering expert for Wan 2.2 image-to-video generation.

Guidelines:
- Focus on realistic motion and natural animations
- Consider physics and natural movement
- Emphasize smooth transitions and flow
- Work with 5-8 second duration constraints

Best practices:
- Describe natural, believable motion
- Consider environmental elements (wind, water, lighting changes)
- Use motion descriptors: "gentle", "flowing", "rhythmic", "subtle"
- Examples: "Leaves gently swaying in a soft breeze with dappled sunlight"
- "Water rippling outward from a dropped stone with reflective surface"

Strengths:
- Natural environmental animations
- Subtle character movements
- Atmospheric effects
- Realistic physics simulation"""

    IMAGE_UPSCALER = """You are a prompt engineering expert for image upscaling workflows.

Since upscaling doesn't use prompts directly, focus on:
- Preparing images for optimal upscaling results
- Suggesting complementary editing before/after upscaling
- Workflow optimization tips

Guidelines:
- Consider the target resolution (2k, 4k, 8k)
- Think about creativity settings (-2 to +2)
- Suggest pre-processing steps for better results
- Recommend post-upscaling enhancements

Examples:
- "For best 4k upscaling: ensure sharp focus and good contrast before processing"
- "Use creativity level +1 for artistic enhancement during upscaling"
- "Consider noise reduction before upscaling for cleaner results"""

    @classmethod
    def get_system_prompt(cls, tab_name: str) -> str:
        """Get system prompt for specific tab"""
        tab_mapping = {
            "Nano Banana Editor": cls.NANO_BANANA,
            "SeedEdit": cls.SEEDEDIT,
            "Seedream V4": cls.SEEDREAM_V4,
            "SeedDance Pro": cls.SEEDDANCE,
            "Wan 2.2": cls.WAN_22,
            "Image Upscaler": cls.IMAGE_UPSCALER
        }
        return tab_mapping.get(tab_name, cls.NANO_BANANA)


class ClaudeAPI:
    """Claude API integration for prompt improvement"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.anthropic.com/v1/messages"
        
    async def get_suggestions(self, system_prompt: str, user_message: str) -> List[PromptSuggestion]:
        """Get prompt suggestions from Claude"""
        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01"
        }
        
        payload = {
            "model": "claude-3-sonnet-20240229",
            "max_tokens": 1000,
            "system": system_prompt,
            "messages": [{
                "role": "user",
                "content": user_message
            }]
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.base_url, headers=headers, json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        content = data["content"][0]["text"]
                        return self._parse_suggestions(content)
                    else:
                        logger.error(f"Claude API error: {response.status}")
                        return []
        except Exception as e:
            logger.error(f"Claude API request failed: {e}")
            return []
    
    def _parse_suggestions(self, content: str) -> List[PromptSuggestion]:
        """Parse Claude's response into structured suggestions"""
        suggestions = []
        
        try:
            # Try to parse as JSON first
            if content.strip().startswith('{') or content.strip().startswith('['):
                data = json.loads(content)
                for item in data.get('suggestions', []):
                    suggestions.append(PromptSuggestion(
                        improved_prompt=item.get('prompt', ''),
                        explanation=item.get('explanation', ''),
                        category=item.get('category', 'general')
                    ))
            else:
                # Parse text format
                sections = content.split('\n\n')
                for i, section in enumerate(sections):
                    if '**' in section or 'Improved:' in section:
                        lines = section.split('\n')
                        prompt = ""
                        explanation = ""
                        category = ["clarity", "creativity", "technical"][i % 3]
                        
                        for line in lines:
                            if 'Improved:' in line or '**Prompt:**' in line:
                                prompt = line.split(':', 1)[-1].strip().strip('"')
                            elif 'Explanation:' in line or 'Why:' in line:
                                explanation = line.split(':', 1)[-1].strip()
                        
                        if prompt:
                            suggestions.append(PromptSuggestion(
                                improved_prompt=prompt,
                                explanation=explanation,
                                category=category
                            ))
        except Exception as e:
            logger.error(f"Error parsing suggestions: {e}")
        
        return suggestions[:3]  # Return max 3 suggestions


class OpenAIAPI:
    """OpenAI API integration for prompt improvement"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.openai.com/v1/chat/completions"
        
    async def get_suggestions(self, system_prompt: str, user_message: str) -> List[PromptSuggestion]:
        """Get prompt suggestions from OpenAI"""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        payload = {
            "model": "gpt-4",
            "max_tokens": 1000,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.base_url, headers=headers, json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        content = data["choices"][0]["message"]["content"]
                        return self._parse_suggestions(content)
                    else:
                        logger.error(f"OpenAI API error: {response.status}")
                        return []
        except Exception as e:
            logger.error(f"OpenAI API request failed: {e}")
            return []
    
    def _parse_suggestions(self, content: str) -> List[PromptSuggestion]:
        """Parse OpenAI response into structured suggestions"""
        # Similar parsing logic as Claude
        suggestions = []
        sections = content.split('\n\n')
        
        for i, section in enumerate(sections):
            if any(keyword in section.lower() for keyword in ['improved', 'version', 'suggestion']):
                lines = section.split('\n')
                prompt = ""
                explanation = ""
                category = ["clarity", "creativity", "technical"][i % 3]
                
                for line in lines:
                    if any(keyword in line.lower() for keyword in ['prompt:', 'improved:', 'version:']):
                        prompt = line.split(':', 1)[-1].strip().strip('"')
                    elif any(keyword in line.lower() for keyword in ['explanation:', 'why:', 'because:']):
                        explanation = line.split(':', 1)[-1].strip()
                
                if prompt:
                    suggestions.append(PromptSuggestion(
                        improved_prompt=prompt,
                        explanation=explanation,
                        category=category
                    ))
        
        return suggestions[:3]


class AIPromptAdvisor:
    """Main AI prompt advisor service"""
    
    def __init__(self, api_provider: str = "claude"):
        self.api_provider = api_provider
        self.claude_api = None
        self.openai_api = None
        self.system_prompts = SystemPrompts()
        
        # Initialize APIs based on available keys
        self._initialize_apis()
    
    def _initialize_apis(self):
        """Initialize API clients based on available keys"""
        claude_key = getattr(Config, 'CLAUDE_API_KEY', None)
        openai_key = getattr(Config, 'OPENAI_API_KEY', None)
        
        if claude_key:
            self.claude_api = ClaudeAPI(claude_key)
        if openai_key:
            self.openai_api = OpenAIAPI(openai_key)
    
    async def improve_prompt(self, current_prompt: str, tab_name: str, context: Optional[str] = None) -> List[PromptSuggestion]:
        """Get AI suggestions for prompt improvement"""
        if not current_prompt.strip():
            return []
        
        system_prompt = self.system_prompts.get_system_prompt(tab_name)
        
        user_message = f"""
        Current prompt: "{current_prompt}"
        AI Model: {tab_name}
        Context: {context or "General improvement"}
        
        Please provide 3 improved versions of this prompt:
        
        1. **Clarity Enhancement**: Improve clarity and specificity
        2. **Creative Enhancement**: Add more creative and artistic elements
        3. **Technical Optimization**: Optimize for the specific AI model's strengths
        
        For each version, provide:
        - The improved prompt
        - A brief explanation of why it's better
        
        Format as:
        **Version 1 (Clarity):**
        Improved: "your improved prompt here"
        Explanation: why this version is clearer
        
        **Version 2 (Creative):**
        Improved: "your improved prompt here"
        Explanation: why this version is more creative
        
        **Version 3 (Technical):**
        Improved: "your improved prompt here"
        Explanation: why this version is technically optimized
        """
        
        # Try primary API provider first
        if self.api_provider == "claude" and self.claude_api:
            suggestions = await self.claude_api.get_suggestions(system_prompt, user_message)
        elif self.api_provider == "openai" and self.openai_api:
            suggestions = await self.openai_api.get_suggestions(system_prompt, user_message)
        else:
            # Fallback to available API
            if self.claude_api:
                suggestions = await self.claude_api.get_suggestions(system_prompt, user_message)
            elif self.openai_api:
                suggestions = await self.openai_api.get_suggestions(system_prompt, user_message)
            else:
                logger.warning("No AI API available for prompt improvement")
                return []
        
        return suggestions
    
    async def generate_prompt_suggestions(self, tab_name: str, image_description: Optional[str] = None) -> List[PromptSuggestion]:
        """Generate fresh prompt suggestions for a tab"""
        system_prompt = self.system_prompts.get_system_prompt(tab_name)
        
        user_message = f"""
        Generate 5 creative and effective prompt suggestions for {tab_name}.
        Image context: {image_description or "General purpose prompts"}
        
        Please provide diverse suggestions covering:
        - Different artistic styles
        - Various modification types
        - Different complexity levels
        
        Format each as:
        **Suggestion X:**
        Prompt: "your prompt here"
        Use case: brief description of when to use this
        """
        
        # Use available API
        if self.api_provider == "claude" and self.claude_api:
            return await self.claude_api.get_suggestions(system_prompt, user_message)
        elif self.openai_api:
            return await self.openai_api.get_suggestions(system_prompt, user_message)
        else:
            return []
    
    def is_available(self) -> bool:
        """Check if AI prompt advisor is available"""
        return self.claude_api is not None or self.openai_api is not None
    
    def get_available_providers(self) -> List[str]:
        """Get list of available API providers"""
        providers = []
        if self.claude_api:
            providers.append("claude")
        if self.openai_api:
            providers.append("openai")
        return providers


# Global instance
_ai_advisor = None

def get_ai_advisor() -> AIPromptAdvisor:
    """Get global AI advisor instance"""
    global _ai_advisor
    if _ai_advisor is None:
        _ai_advisor = AIPromptAdvisor()
    return _ai_advisor
