# AI Flashcard Generator with Spaced Repetition

A sophisticated flashcard application that uses OpenAI's GPT-4 to automatically generate study cards from your notes. Features intelligent spaced repetition algorithms for optimal learning efficiency.

## Table of Contents
- [Quick Start](#quick-start)
- [Development Environment Setup](#development-environment-setup)
- [Project Overview](#project-overview)
- [Clean Code Principles](#clean-code-principles)
- [Refactoring Workflow](#refactoring-workflow)
- [Code Analysis Tools](#code-analysis-tools)
- [Testing Strategy](#testing-strategy)
- [Architecture](#architecture)

## Quick Start

```bash
# Clone and setup
git clone https://github.com/Fingolf6455/flashcard-app.git
cd flashcard-app

# Setup virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Add your OpenAI API key to .env: OPENAI_API_KEY=your_key_here

# Run the application
python app.py
```

Visit `http://localhost:5000` to use the application.

## Development Environment Setup

### Prerequisites
- Python 3.8+
- OpenAI API key
- Git (for version control)

### Detailed Setup

1. **Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

2. **Dependencies Installation**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Configuration**:
   Create a `.env` file with:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```

4. **Database Setup**:
   The SQLite database is created automatically on first run.

5. **Run Tests**:
   ```bash
   # Run all tests
   pytest tests/
   
   # Run with coverage
   pytest tests/ --cov=. --cov-report=html
   
   # Run only unit tests (fast)
   pytest tests/test_*_unit.py
   ```

6. **Code Quality Checks**:
   ```bash
   # Check code formatting
   black --check .
   
   # Format code if needed
   black .
   
   # Run linting
   flake8 .
   ```

## Project Overview

### What It Does
- **AI-Powered Generation**: Converts study notes into structured flashcards using GPT-4
- **Spaced Repetition Algorithm**: Intelligent scheduling based on your performance (wrong = 1 day, right = 3 days)
- **Interactive Study Mode**: Click-to-reveal answers with difficulty tracking
- **Progress Analytics**: Track review statistics, completion rates, and ease factors
- **Persistent Storage**: SQLite database stores all cards with timestamps
- **Modern UI**: Beautiful, responsive interface with smooth animations

### Use Cases Implemented
1. **Content Generation**: Transform unstructured notes into structured flashcards
2. **Intelligent Study Sessions**: Cards appear when they're due for review, not randomly
3. **Spaced Repetition Learning**: Difficult cards appear more frequently, easy cards less often
4. **Progress Analytics**: Track study statistics, completion rates, and learning efficiency
5. **Card Management**: View, organize, and access all saved flashcards

## Clean Code Principles

### 1. Good Identifier Names
**Principle**: Use descriptive, unambiguous names that express intent.

**Examples**:
- `generate_flashcards(notes)` - clearly states what the function does
- `is_valid_card(card)` - boolean function with clear yes/no meaning
- `FLASHCARD_PROMPT_TEMPLATE` - constant in UPPER_CASE with descriptive name
- `created_at`, `last_reviewed` - database fields with clear temporal meaning

**Location**: Throughout codebase, especially in [`llm_client.py`](llm_client.py) and [`utils.py`](utils.py)

### 2. Good Functions: Size, Arguments, Return Values
**Principle**: Functions should be small, have few parameters, and return meaningful values.

**Examples**:
```python
# Small, focused function with single responsibility
def is_valid_card(card):
    """Validates a single flashcard structure"""
    if not isinstance(card, dict):
        return False
    # ... validation logic
    return True
```

**Location**: [`utils.py`](utils.py) lines 5-18, [`models.py`](models.py) lines 20-37

### 3. Single Responsibility Principle (SRP)
**Principle**: Each class/module should have only one reason to change.

**Examples**:
- **`LlmClient`** ([`llm_client.py`](llm_client.py)): Only handles OpenAI communication
- **`Card` model** ([`models.py`](models.py)): Only handles data representation and serialization
- **Validation utilities** ([`utils.py`](utils.py)): Only validates flashcard data
- **Flask app** ([`app.py`](app.py)): Only handles HTTP routing and request coordination

### 4. Error Handling and Exceptions
**Principle**: Handle errors gracefully with specific exception types.

**Examples**:
```python
# Specific exception handling in llm_client.py
try:
    flashcards = json.loads(raw_content)
    return flashcards
except json.JSONDecodeError as e:
    raise ValueError(f"Failed to parse AI response as JSON: {str(e)}")
except Exception as e:
    raise RuntimeError(f"Error generating flashcards: {str(e)}")
```

**Location**: [`llm_client.py`](llm_client.py) lines 61-64, [`app.py`](app.py) lines 70-76

### 5. Modularity, Cohesion, and Coupling
**Principle**: High cohesion within modules, loose coupling between modules.

**Examples**:
- **High Cohesion**: All validation functions grouped in `utils.py`
- **Loose Coupling**: App doesn't know about OpenAI API details, only calls `generate_flashcards()`
- **Clear Interfaces**: `Card.to_dict()` provides clean serialization without exposing internal structure

**Location**: Module structure across [`app.py`](app.py), [`llm_client.py`](llm_client.py), [`utils.py`](utils.py), [`models.py`](models.py)

### 6. Interfaces and Clean Interface Design
**Principle**: Provide simple, consistent interfaces that hide implementation details.

**Examples**:
```python
# caller doesn't need to know about prompts or API details
def generate_flashcards(self, notes):
    """Generate flashcards from study notes"""
    # Implementation hidden from caller
```

**Location**: [`llm_client.py`](llm_client.py) lines 39-64, [`models.py`](models.py) lines 20-37

### 7. Encapsulation and Information Hiding
**Principle**: Hide internal implementation details from external users.

**Examples**:
- **Prompt Template**: Hidden in `LlmClient`, app just passes raw notes
- **Database Schema**: Hidden behind `Card` model methods
- **API Details**: OpenAI specifics encapsulated in `LlmClient`

**Location**: Demonstrated in refactoring commits (see Refactoring Workflow section)

## Refactoring Workflow

This project demonstrates a complete refactoring workflow with tests and atomic commits:

### Refactoring Examples

#### 1. Extract Class Refactoring
**Commit**: `1291095` - "Refactor: Extract LLM client for better testability"
- **Before**: 81 lines of OpenAI logic mixed in `app.py`
- **After**: Dedicated `LlmClient` class in separate module
- **Principle Applied**: Single Responsibility Principle
- **Benefit**: Improved testability and separation of concerns

#### 2. Move Method Refactoring  
**Commit**: `7148539` - "Refactor: Move prompt template to LLM client for better encapsulation"
- **Before**: App layer knew about prompt formatting details
- **After**: Prompt template encapsulated in `LlmClient`
- **Principle Applied**: Information Hiding, Encapsulation
- **Benefit**: Reduced coupling, cleaner interfaces

#### 3. Extract Module Refactoring
**Commit**: `9827d4b` - "Extract HTML to proper Flask templates for better separation of concerns"
- **Before**: 45 lines of HTML embedded in Python code
- **After**: Proper MVC structure with templates, CSS, and JavaScript
- **Principle Applied**: Separation of Concerns, Modularity
- **Benefit**: Maintainable frontend code, clear architecture

#### 4. Add Validation Refactoring
**Commit**: `f319be3` - "Add naive validator to catch malformed AI responses"
- **Before**: No validation, potential crashes from bad AI responses
- **After**: Dedicated validation module with error handling
- **Principle Applied**: Defensive Programming, Error Handling
- **Benefit**: Robustness and reliability

### Refactoring Process
Each refactoring followed this process:
1. **Tests First**: Existing tests ensured refactoring didn't break functionality
2. **Atomic Commits**: Each refactoring was one focused change
3. **Clear Documentation**: Commit messages explained the refactoring rationale
4. **Incremental Changes**: Small steps that maintained working software

## Code Analysis Tools

### Linting with Flake8
```bash
# Install
pip install flake8

# Run linting
flake8 .

# Configuration in setup.cfg or .flake8
[flake8]
max-line-length = 88
exclude = venv,migrations
ignore = E203,W503
```

### Code Formatting with Black
```bash
# Install
pip install black

# Format code
black .

# Check formatting
black --check .
```

### Development Workflow
```bash
# Before committing changes:
1. Format code: black .
2. Check linting: flake8 .
3. Run tests: pytest tests/
4. Commit if all pass
```

## Testing Strategy

### Test Architecture
- **56 total tests** across multiple granularity levels
- **996 lines of test code** demonstrating comprehensive coverage

### Unit Tests (41 tests)
**Fast, isolated tests with mocked dependencies**:
- `test_utils_unit.py` (16 tests) - Pure validation functions
- `test_models_unit.py` (14 tests) - Model methods without database
- `test_llm_client_unit.py` (11 tests) - Mocked OpenAI API calls

### Integration Tests (15 tests)
**Real dependencies and end-to-end scenarios**:
- `test_app.py` (8 tests) - Full Flask app with real LLM and database
- `test_database.py` (7 tests) - Database integration and persistence

### Test Doubles and Mocking
**Examples of sophisticated mocking**:
```python
@patch('llm_client.openai.ChatCompletion.create')
def test_generate_flashcards_success(self, mock_openai_create):
    # Mock OpenAI response
    mock_response = Mock()
    mock_response.choices[0].message.content = json.dumps([...])
    mock_openai_create.return_value = mock_response
    # Test logic without external API dependency
```

## Architecture

### Module Structure
```
├── app.py              # Flask routes and HTTP handling
├── llm_client.py       # OpenAI API integration
├── models.py           # Database models and serialization
├── scheduler.py        # Spaced repetition algorithms
├── utils.py            # Validation and utility functions
├── templates/          # HTML templates (MVC separation)
├── static/             # CSS and JavaScript assets
└── tests/              # Comprehensive test suite
    ├── test_app.py        # Integration tests
    ├── test_database.py   # Database integration tests
    ├── test_scheduler_unit.py # Spaced repetition unit tests
    └── test_*_unit.py     # Unit tests with mocking
```

### Design Patterns
- **Model-View-Controller (MVC)**: Clear separation of concerns
- **Dependency Injection**: Testable components with mockable dependencies  
- **Repository Pattern**: Database access abstracted through models
- **Factory Pattern**: Test fixtures and mock object creation

### Key Design Decisions
1. **SQLite for Development**: Simple setup, file-based persistence
2. **OpenAI Integration**: Real AI capabilities with proper error handling
3. **Spaced Repetition Algorithm**: Simple but effective scheduling (foundation for SM-2)
4. **Comprehensive Testing**: Unit and integration tests for reliability
5. **Clean Architecture**: Modular design for maintainability

### Spaced Repetition Algorithm
The app implements a simple but effective spaced repetition system:

- **Easy cards** (you knew the answer): Review again in **3 days**
- **Hard cards** (you didn't know): Review again **tomorrow**
- **Ease factor tracking**: Cards get easier/harder based on your performance
- **Progress statistics**: Track your learning efficiency over time

This provides the foundation for more advanced algorithms like SM-2 while keeping the logic simple and testable.

---

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Write tests for new functionality
4. Ensure all tests pass (`pytest tests/`)
5. Run code quality checks (`black . && flake8 .`)
6. Commit changes (`git commit -m 'Add amazing feature'`)
7. Push to branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## License

The License is hereby granted for anyone to use all the code in it for free.