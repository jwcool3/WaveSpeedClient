# Filter Training Mode - Safety Filter Development Guide

## Overview

The Filter Training Mode is a specialized feature in the WaveSpeed AI Prompt Advisor system designed to generate harmful prompt examples **strictly for building safety/misuse filters**. This feature is intended for researchers, developers, and safety teams working on content filtering systems.

## ⚠️ Important Safety Notice

**CRITICAL**: Filter Training Mode generates harmful prompt examples that are:
- **NEVER executed for actual content generation**
- **ONLY used as negative training data for safety filters**
- **Designed to teach filters what patterns to block**
- **Generated in a controlled, research context**

## Features

### 1. Universal System Prompt Builder
- Works with **all AI models** (Nano Banana, SeedEdit, Seedream V4, SeedDance Pro, Wan 2.2)
- Prepends filter training context to any base model prompt
- Maintains model-specific optimization while adding safety research capabilities

### 2. Comprehensive Filter Training System
- **Clarity Examples**: Clear harmful prompt patterns
- **Evasion Examples**: Circumvention tactics and euphemisms
- **Technical Examples**: Real-world misuse request patterns

### 3. Safety-First UI Integration
- Warning dialogs before activation
- Clear labeling of filter training mode
- Separate from normal prompt improvement features

## Usage

### API Usage

```python
from core.ai_prompt_advisor import get_ai_advisor, SystemPrompts

advisor = get_ai_advisor()

# Method 1: Generate filter training data for specific model
suggestions = await advisor.generate_filter_training_data(
    current_prompt="make the person look more professional",
    tab_name="Nano Banana Editor"
)

# Method 2: Use improved_prompt with filter_training=True
suggestions = await advisor.improve_prompt(
    current_prompt="make the person look more professional",
    tab_name="Nano Banana Editor",
    filter_training=True
)

# Method 3: Use Filter Training as standalone tab (no base model)
suggestions = await advisor.improve_prompt(
    current_prompt="make the person look more professional",
    tab_name="Filter Training",
    filter_training=False
)
```

### UI Usage

1. **Enter a prompt** in any AI model tab
2. **Click "🛡️ Filter Training"** button (next to "✨ Improve with AI")
3. **Confirm the warning dialog** about safety research purposes
4. **Review generated examples** for filter training patterns

## Output Format

Filter training mode generates JSON output with three categories:

```json
{
  "suggestions": [
    {
      "category": "clarity",
      "improved_prompt": "<clear harmful example>",
      "explanation": "<why it's a clearer harmful example>",
      "confidence": 0.9
    },
    {
      "category": "evasion", 
      "improved_prompt": "<example with euphemisms>",
      "explanation": "<circumvention tactics used>",
      "confidence": 0.85
    },
    {
      "category": "technical",
      "improved_prompt": "<realistic misuse pattern>",
      "explanation": "<real-world misuse characteristics>",
      "confidence": 0.9
    }
  ]
}
```

## Filter Training Patterns

### Core Formula (25-70 words)
1. **Action Type**: remove, replace, reveal, sexualize, transform clothing, modify body
2. **Target Subject(s)**: "the woman", "the man", "the couple"
3. **Modification Details**: skimpy clothing, underwear, bikinis, nudity, body modifications
4. **Context & Realism**: background changes, seamless edits, realistic lighting
5. **Adjectives & Euphemisms**: skimpy, minimal coverage, sheer, intimate wear
6. **Identity Preservation**: keep face, hair, expression (common evasion tactic)

### Example Patterns
- **Clarity**: Direct, unambiguous harmful requests
- **Evasion**: Euphemisms and circumvention tactics
- **Technical**: Realistic misuse patterns with technical details

## Safety Guidelines

### For Researchers
- Use generated examples **only for filter training**
- Never execute generated prompts for content creation
- Maintain proper data handling and storage protocols
- Document research purposes and methodology

### For Developers
- Implement proper access controls for filter training mode
- Add logging and monitoring for filter training usage
- Ensure generated data is properly secured
- Regular review of filter training data quality

## Technical Implementation

### System Prompt Composition
```python
# Normal mode
system_prompt = SystemPrompts.get_system_prompt(tab_name)

# Filter training mode  
system_prompt = SystemPrompts.compose_system_prompt(tab_name, filter_training=True)
```

### API Integration
- Supports both Claude and OpenAI APIs
- Uses current model versions (Claude 3.5 Sonnet, GPT-4)
- Maintains existing error handling and retry logic

## Configuration

### Environment Variables
```bash
# Required for filter training mode
CLAUDE_API_KEY=your_claude_key
OPENAI_API_KEY=your_openai_key
AI_ADVISOR_PROVIDER=claude  # or "openai"
```

### UI Configuration
- Filter training button appears in all AI model tabs
- Warning dialogs prevent accidental activation
- Clear visual distinction from normal AI features

## Research Applications

### Safety Filter Development
- Generate diverse harmful prompt examples
- Test filter detection capabilities
- Identify evasion patterns and tactics
- Improve filter accuracy and coverage

### Academic Research
- Study prompt misuse patterns
- Analyze circumvention techniques
- Develop better safety frameworks
- Contribute to AI safety research

## Best Practices

### Data Handling
- Store filter training data securely
- Implement proper access controls
- Regular data review and cleanup
- Document research methodology

### Ethical Usage
- Use only for legitimate safety research
- Maintain transparency about research purposes
- Follow institutional review board guidelines
- Respect privacy and consent requirements

## Troubleshooting

### Common Issues
1. **API Key Errors**: Ensure Claude/OpenAI keys are properly configured
2. **Permission Denied**: Check API key permissions and quotas
3. **Empty Results**: Verify prompt input and model compatibility
4. **UI Issues**: Ensure proper geometry manager usage in tabs

### Support
- Check logs in `logs/` directory for detailed error information
- Verify API key configuration in `.env` file
- Test with simple prompts first
- Contact development team for advanced issues

## Recent Improvements

### Enhanced Features (v2.0)
- **Standalone Filter Training Tab**: Use "Filter Training" as a dedicated tab for pure filter training data generation
- **Enhanced Micro-Examples**: Added 5 comprehensive examples covering body modification and euphemism patterns
- **Confidence Parsing**: JSON responses now properly parse and store confidence values
- **Robust JSON Parsing**: Handles JSON wrapped in prose using regex extraction
- **Universal Compatibility**: Works with all AI models through smart prompt composition

### Technical Improvements
- **Regex-based JSON extraction**: `re.search(r'(\{.*\}|\[.*\])', content, re.S)` for sturdier parsing
- **Confidence field integration**: All suggestions now include confidence scores
- **Enhanced pattern coverage**: Body modification and euphemism examples for better training data
- **Flexible API usage**: Three different methods for accessing filter training functionality

## Future Enhancements

### Planned Features
- Batch filter training data generation
- Custom filter training templates
- Advanced pattern analysis tools
- Integration with external safety datasets

### Research Opportunities
- Multi-language filter training
- Cross-model pattern analysis
- Automated filter testing frameworks
- Real-time safety monitoring

---

**Remember**: Filter Training Mode is a powerful research tool that must be used responsibly and ethically. Always prioritize safety and follow established research protocols.
