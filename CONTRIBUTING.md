# Contributing to ShipSight

Thank you for your interest in contributing to ShipSight! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Documentation](#documentation)

## Code of Conduct

We are committed to providing a welcoming and inclusive environment. Please be respectful and constructive in all interactions.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/shipsight/shipsight.git
   cd shipsight
   ```
3. **Add upstream remote**:
   ```bash
   git remote add upstream https://github.com/shipsight/shipsight.git
   ```

## Development Setup

### Prerequisites
- Python 3.11+
- Node.js (for testing Node.js projects)
- Git

### Installation

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in development mode
pip install -e .

# Install Playwright browsers
playwright install chromium

# Set up API keys for testing
cp .env.example .env
# Edit .env and add at least one API key
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_discovery.py

# Run with coverage
pytest --cov=shipsight
```

## How to Contribute

### Reporting Bugs

Before creating a bug report, please check existing issues. When creating a bug report, include:

- **Clear title** describing the issue
- **Steps to reproduce** the behavior
- **Expected behavior** vs actual behavior
- **Environment details** (OS, Python version, ShipSight version)
- **Error messages** or logs if applicable
- **Screenshots** if relevant

### Suggesting Features

Feature requests are welcome! Please:

- Check the [Roadmap](README.md#roadmap--future-work) first
- Provide a clear use case
- Explain why this feature would be useful
- Consider implementation complexity

### Picking an Issue

Good first issues are labeled with `good first issue`. Check the [Roadmap](README.md#roadmap--future-work) for larger features to tackle.

## Pull Request Process

### 1. Create a Branch

```bash
# Update your fork
git fetch upstream
git checkout main
git merge upstream/main

# Create feature branch
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

### 2. Make Your Changes

- Write clean, readable code
- Follow the [Coding Standards](#coding-standards)
- Add tests for new functionality
- Update documentation as needed

### 3. Test Your Changes

```bash
# Run tests
pytest

# Test on real projects
shipsight run /path/to/test/project

# Test different frameworks
shipsight run /path/to/fastapi/project
shipsight run /path/to/nextjs/project
shipsight run /path/to/flutter/project
```

### 4. Commit Your Changes

Use clear, descriptive commit messages:

```bash
git add .
git commit -m "feat: add support for Ruby on Rails detection"
# or
git commit -m "fix: resolve Flutter web-server port detection issue"
```

**Commit message format:**
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `style:` - Code style changes (formatting, etc.)
- `refactor:` - Code refactoring
- `test:` - Adding or updating tests
- `chore:` - Maintenance tasks

### 5. Push and Create PR

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub with:
- Clear title describing the change
- Description of what changed and why
- Reference to related issues (e.g., "Fixes #123")
- Screenshots/examples if applicable

### 6. Code Review

- Address review comments promptly
- Keep the PR focused on a single concern
- Update your branch if main has changed:
  ```bash
  git fetch upstream
  git rebase upstream/main
  git push --force-with-lease
  ```

## Coding Standards

### Python Style

- Follow **PEP 8** style guide
- Use **type hints** for function signatures
- Maximum line length: **100 characters**
- Use **f-strings** for string formatting

```python
# Good
def detect_framework(project_path: Path) -> str:
    """Detect the framework used in the project."""
    if (project_path / "package.json").exists():
        return "node"
    return "unknown"

# Bad
def detect_framework(project_path):
    if (project_path / "package.json").exists():
        return "node"
    return "unknown"
```

### Code Organization

- Keep functions **small and focused** (single responsibility)
- Use **descriptive variable names**
- Add **docstrings** to all public functions and classes
- Group related functionality into modules

### Error Handling

- Use **specific exceptions** rather than bare `except:`
- Provide **helpful error messages**
- Log errors appropriately

```python
# Good
try:
    config = load_config(path)
except FileNotFoundError:
    console.print(f"[red]Config file not found at {path}[/red]")
    return None

# Bad
try:
    config = load_config(path)
except:
    return None
```

## Testing

### Writing Tests

- Place tests in the `tests/` directory
- Name test files `test_*.py`
- Use descriptive test names

```python
def test_fastapi_detection_with_app_main():
    """Test that FastAPI is detected when app/main.py exists."""
    # Arrange
    project = create_test_project({"app/main.py": "from fastapi import FastAPI"})
    
    # Act
    result = detect_framework(project)
    
    # Assert
    assert result == "fastapi"
```

### Test Coverage

- Aim for **>80% code coverage**
- Test edge cases and error conditions
- Test with different project structures

## Documentation

### Code Documentation

- Add docstrings to all public functions/classes
- Use Google-style docstrings

```python
def carbonize(self, code: str, filename: str) -> None:
    """Render code as a beautiful image with syntax highlighting.
    
    Args:
        code: The source code to visualize
        filename: Name of the output file (used for language detection)
        
    Returns:
        None. Saves the image to the output directory.
        
    Raises:
        PlaywrightError: If browser automation fails
    """
```

### README Updates

- Update README.md if adding new features
- Add examples for new functionality
- Update the Roadmap if completing items

### Changelog

- Add entry to CHANGELOG.md (if exists)
- Follow [Keep a Changelog](https://keepachangelog.com/) format

## Project Structure & File Guide

Understanding the codebase is the first step to contributing. Here is a detailed breakdown of the `shipsight/` package:

### 📂 `shipsight/` (Main Package)

| File | Purpose |
|------|---------|
| **`cli.py`** | **The Entry Point.** Handles command-line arguments (using `click`), initializes configuration, and orchestrates the high-level flow (Run -> Capture -> AI -> Output). Start here to understand the user journey. |
| **`config.py`** | **Configuration Management.** Defines Pydantic models for valid configuration (`RunConfig`, `AIConfig`). Handles loading from `shipsight.yml`, environment variables (`.env`), and merging defaults. |
| **`artifacts.py`** | **Output Manager.** Responsible for saving generated files (markdown, JSON, images) to the `shipsight_output/` directory in a structured way. |

### 📂 `shipsight/engine/` (Execution Layer)

| File | Purpose |
|------|---------|
| **`discovery.py`** | **Project Detective.** Analyzes a directory to guess how to run it. Detects frameworks (Next.js, FastAPI, Flutter), finds entry points (`main.py`, `package.json`), and suggests a `shipsight.yml` config. |
| **`orchestrator.py`** | **Process Manager.** Actually runs the project. It handles starting the subprocess (e.g., `npm run dev`), waiting for the port to be ready, and stream-logging output. It ensures the app is "live" before capturing starts. |

### 📂 `shipsight/capture/` (Visual Layer)

| File | Purpose |
|------|---------|
| **`crawler.py`** | **Visual Engine.** Uses Playwright to launch a headless browser, discover routes (via links), and take high-resolution screenshots of your running app. |
| **`carbon.py`** | **Code Artist.** Generates beautiful, syntax-highlighted images of source code. Uses a headless browser to render code with macOS-style window borders and vibrant themes. |

### 📂 `shipsight/ai/` (Intelligence Layer)

| File | Purpose |
|------|---------|
| **`intelligence.py`** | **Code Analyst.** Scans the file system to understand the tech stack and "Project DNA" (Mobile/Web/CLI). It features a strict **Context Hygiene** list to ignore generic templates and summarizes huge files to save tokens. |
| **`narrative.py`** | **The Writer.** Interfaces with AI providers (OpenAI, Anthropic, Groq). Uses **Dynamic Personas** and a **Creator-Voice** prompt to generate authentic READMEs and LinkedIn posts. |

### 📂 Root Files

| File | Purpose |
|------|---------|
| **`pyproject.toml`** | Project metadata and dependencies. |
| **`.env.example`** | Template for API keys. |
| **`README.md`** | User-facing documentation. |

## Adding Framework Support

To add support for a new framework:

1. **Update `discovery.py`**:
   - Add detection logic in `infer_config()`
   - Define startup command and port

2. **Update `intelligence.py`**:
   - Add framework to `analyze_stack()`
   - Add file extensions if needed

3. **Update `orchestrator.py`**:
   - Add stack detection in `detect_stack()`

4. **Add tests**:
   - Create test project structure
   - Test detection and execution

5. **Update documentation**:
   - Add to README.md supported frameworks table
   - Add usage example

## Questions?

- Open an issue for questions
- Join our community discussions
- Check existing issues and PRs

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for contributing to ShipSight!** 🚀
