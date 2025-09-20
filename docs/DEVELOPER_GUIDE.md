# 🛠️ Developer Guide - WaveSpeed AI Application

This guide provides comprehensive information for developers working on the WaveSpeed AI application, including architecture, development practices, and contribution guidelines.

## 📋 Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Project Structure](#project-structure)
3. [Development Setup](#development-setup)
4. [Adding New AI Models](#adding-new-ai-models)
5. [Code Quality Standards](#code-quality-standards)
6. [Testing Guidelines](#testing-guidelines)
7. [Error Handling](#error-handling)
8. [Configuration Management](#configuration-management)
9. [API Integration](#api-integration)
10. [Performance Optimization](#performance-optimization)
11. [Contributing](#contributing)

## 🏗️ Architecture Overview

The WaveSpeed AI application follows a modular architecture with clear separation of concerns:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   UI Layer      │    │  Business Logic │    │   Data Layer    │
│                 │    │                 │    │                 │
│ • Tabs          │◄──►│ • API Client    │◄──►│ • Configuration │
│ • Components    │    │ • Validation    │    │ • File System   │
│ • Layouts       │    │ • Error Handling│    │ • Logging       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Key Components

- **UI Layer**: Tkinter-based interface with modular tab system
- **Business Logic**: Core functionality, API interactions, validation
- **Data Layer**: Configuration, file management, logging
- **Error Handling**: Comprehensive exception system with user-friendly messages
- **Validation**: Input validation and sanitization
- **Configuration**: Type-safe configuration management with dataclasses

## 📁 Project Structure

```
waveapi/
├── app/                    # Application configuration and main app
│   ├── config.py          # Legacy configuration
│   ├── config_enhanced.py # Enhanced configuration with dataclasses
│   ├── constants.py       # Centralized constants and enums
│   └── main_app.py        # Main application class
├── core/                  # Core business logic
│   ├── api_client.py      # WaveSpeed AI API client
│   ├── exceptions.py      # Custom exception classes
│   ├── logger.py          # Logging configuration
│   ├── resource_manager.py # Resource management
│   └── validation.py      # Input validation functions
├── ui/                    # User interface components
│   ├── components/        # Reusable UI components
│   └── tabs/             # Tab implementations
├── tests/                 # Unit tests
│   ├── test_config.py     # Configuration tests
│   ├── test_validation.py # Validation tests
│   ├── test_exceptions.py # Exception tests
│   └── run_tests.py      # Test runner
├── docs/                  # Documentation
└── requirements-dev.txt   # Development dependencies
```

## 🚀 Development Setup

### Prerequisites

- Python 3.8 or higher
- pip package manager
- Git

### Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd waveapi
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   # Install core dependencies
   pip install -r requirements.txt
   
   # Install development dependencies
   pip install -r requirements-dev.txt
   ```

4. **Set up environment variables**:
   ```bash
   cp docs/env_example.txt .env
   # Edit .env with your API keys
   ```

5. **Run tests**:
   ```bash
   python tests/run_tests.py
   ```

### IDE Setup

#### VS Code
Install these extensions:
- Python
- Pylance
- Python Docstring Generator
- GitLens

#### PyCharm
- Enable type checking
- Configure code style (Black formatter)
- Set up run configurations for tests

## 🤖 Adding New AI Models

### Step 1: Create Tab Implementation

Create a new file in `ui/tabs/` following the pattern:

```python
# ui/tabs/new_model_tab.py
from ui.tabs.base_tab import BaseTab
from app.constants import ModelNames

class NewModelTab(BaseTab):
    """Tab for new AI model"""
    
    def __init__(self, parent, api_client, **kwargs):
        super().__init__(parent, api_client, **kwargs)
        self.model_name = ModelNames.NEW_MODEL
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the UI components"""
        # Implementation here
        pass
    
    def submit_task(self):
        """Submit task to the new model"""
        # Implementation here
        pass
```

### Step 2: Update Configuration

Add the new model to `app/constants.py`:

```python
class ModelNames:
    # ... existing models ...
    NEW_MODEL = "new-model"
```

Update `app/config_enhanced.py`:

```python
# Add endpoint
endpoints = {
    # ... existing endpoints ...
    'new_model': f"{self.api.base_url}/path/to/new-model"
}

# Add auto-save folder
subfolders = {
    # ... existing folders ...
    'new_model': 'New_Model'
}
```

### Step 3: Add API Client Method

Add method to `core/api_client.py`:

```python
def submit_new_model_task(self, image_path: Union[str, Path], prompt: str, **kwargs) -> Tuple[Optional[RequestId], Optional[str]]:
    """Submit task to new model"""
    try:
        # Validate inputs
        is_valid, error = validate_prompt(prompt)
        if not is_valid:
            raise handle_validation_error("prompt", prompt, error)
        
        # Implementation here
        pass
        
    except (ValidationError, APIError):
        raise
    except Exception as e:
        raise APIError(f"Error submitting new model task: {str(e)}")
```

### Step 4: Register Tab

Update `app/main_app.py`:

```python
from ui.tabs.new_model_tab import NewModelTab

# In setup_ui method:
self.new_model_tab = NewModelTab(self.notebook, self.api_client)
self.notebook.add(self.new_model_tab, text="🤖 New Model")
```

### Step 5: Update Cross-Tab Navigation

Update `ui/components/cross_tab_navigator.py`:

```python
TAB_MAPPING = {
    # ... existing mappings ...
    'new_model': 'New Model'
}
```

## 📏 Code Quality Standards

### Type Hints

All functions must include type hints:

```python
def process_image(image_path: Union[str, Path], output_format: str = "png") -> Tuple[bool, Optional[str]]:
    """Process image with type hints"""
    pass
```

### Documentation

Use docstrings for all classes and functions:

```python
def validate_input(value: str) -> Tuple[bool, Optional[str]]:
    """
    Validate input value
    
    Args:
        value: The value to validate
        
    Returns:
        Tuple of (is_valid, error_message)
        
    Raises:
        ValidationError: If validation fails
    """
    pass
```

### Error Handling

Use custom exceptions with context:

```python
try:
    result = api_call()
except requests.exceptions.RequestException as e:
    raise handle_network_error(url, f"API call failed: {str(e)}")
```

### Code Formatting

Use Black for code formatting:

```bash
black --line-length 88 .
```

Use isort for import sorting:

```bash
isort .
```

## 🧪 Testing Guidelines

### Unit Tests

Create tests for all new functionality:

```python
# tests/test_new_feature.py
import unittest
from unittest.mock import Mock, patch

class TestNewFeature(unittest.TestCase):
    """Test cases for new feature"""
    
    def test_valid_input(self):
        """Test with valid input"""
        result = new_function("valid_input")
        self.assertTrue(result)
    
    def test_invalid_input(self):
        """Test with invalid input"""
        with self.assertRaises(ValidationError):
            new_function("invalid_input")
```

### Running Tests

```bash
# Run all tests
python tests/run_tests.py

# Run specific test file
python -m pytest tests/test_validation.py -v

# Run with coverage
python -m pytest tests/ --cov=core --cov=app
```

### Test Coverage

Maintain at least 80% test coverage for core modules:
- `core/validation.py`
- `core/exceptions.py`
- `core/api_client.py`
- `app/config_enhanced.py`

## ⚠️ Error Handling

### Exception Hierarchy

```
WaveSpeedAIError (base)
├── APIError
│   ├── AuthenticationError
│   ├── RateLimitError
│   └── InsufficientBalanceError
├── ValidationError
├── FileError
│   ├── ImageProcessingError
│   └── VideoProcessingError
├── ConfigurationError
├── NetworkError
├── TimeoutError
└── TaskError
    ├── TaskFailedError
    └── TaskTimeoutError
```

### Best Practices

1. **Use specific exceptions**: Don't catch generic `Exception`
2. **Provide context**: Include relevant information in error messages
3. **Log errors**: Use the logger for debugging information
4. **User-friendly messages**: Convert technical errors to user-friendly messages

```python
try:
    result = risky_operation()
except SpecificError as e:
    logger.error(f"Operation failed: {str(e)}", exc_info=True)
    raise UserFriendlyError("Operation could not be completed. Please try again.")
```

## ⚙️ Configuration Management

### Using Enhanced Configuration

```python
from app.config_enhanced import get_config

config = get_config()

# Access configuration
api_key = config.api.api_key
window_size = config.ui.window_size
max_file_size = config.file.max_file_size
```

### Adding New Configuration

1. **Add to appropriate dataclass** in `app/config_enhanced.py`
2. **Add validation** in `__post_init__` method
3. **Add to environment variables** in `.env` file
4. **Update tests** in `tests/test_config.py`

### Environment Variables

```bash
# Required
WAVESPEED_API_KEY=your_api_key_here

# Optional
CLAUDE_API_KEY=your_claude_key_here
OPENAI_API_KEY=your_openai_key_here
AI_ADVISOR_PROVIDER=claude
```

## 🔌 API Integration

### API Client Usage

```python
from core.api_client import WaveSpeedAPIClient

client = WaveSpeedAPIClient()

# Submit task
request_id, error = client.submit_image_edit_task(
    image_path="path/to/image.png",
    prompt="Make it more artistic"
)

if error:
    print(f"Error: {error}")
else:
    print(f"Task submitted: {request_id}")
```

### Error Handling

```python
try:
    result = client.get_balance()
except AuthenticationError:
    print("Invalid API key")
except RateLimitError as e:
    print(f"Rate limited. Retry after {e.retry_after} seconds")
except APIError as e:
    print(f"API error: {e}")
```

## 🚀 Performance Optimization

### Async Operations

For long-running operations, consider using async:

```python
import asyncio
import aiohttp

async def async_api_call(self, endpoint: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Async API call for better responsiveness"""
    async with aiohttp.ClientSession() as session:
        async with session.post(endpoint, json=payload) as response:
            return await response.json()
```

### Memory Management

- Use context managers for file operations
- Clean up temporary files
- Monitor memory usage with large images

### Caching

Consider caching for:
- API responses
- Image thumbnails
- Configuration values

## 🤝 Contributing

### Pull Request Process

1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature/new-feature`
3. **Make changes** following code quality standards
4. **Add tests** for new functionality
5. **Run tests**: `python tests/run_tests.py`
6. **Commit changes**: `git commit -m "Add new feature"`
7. **Push to branch**: `git push origin feature/new-feature`
8. **Create Pull Request**

### Commit Message Format

```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance tasks

### Code Review Checklist

- [ ] Code follows style guidelines
- [ ] Tests pass
- [ ] Documentation updated
- [ ] Error handling implemented
- [ ] Type hints added
- [ ] No hardcoded values
- [ ] Security considerations addressed

## 📚 Additional Resources

- [Python Type Hints](https://docs.python.org/3/library/typing.html)
- [Tkinter Documentation](https://docs.python.org/3/library/tkinter.html)
- [Pytest Documentation](https://docs.pytest.org/)
- [Black Code Formatter](https://black.readthedocs.io/)
- [MyPy Type Checker](https://mypy.readthedocs.io/)

## 🆘 Getting Help

- **Issues**: Create GitHub issues for bugs or feature requests
- **Discussions**: Use GitHub Discussions for questions
- **Documentation**: Check existing documentation first
- **Code Review**: Request code review for complex changes

---

**Happy Coding! 🎉**

Remember: Good code is not just working code, but maintainable, testable, and well-documented code.
