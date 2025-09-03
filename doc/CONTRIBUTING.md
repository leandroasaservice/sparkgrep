# Contributing to SparkGrep

Thank you for your interest in contributing to SparkGrep! This document provides guidelines for contributing to the project.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Development Setup](#development-setup)
3. [Project Structure](#project-structure)
4. [Making Changes](#making-changes)
5. [Adding New Patterns](#adding-new-patterns)
6. [Testing](#testing)
7. [Code Style](#code-style)
8. [Pull Request Process](#pull-request-process)
9. [Pattern Development Guidelines](#pattern-development-guidelines)

## Getting Started

### Prerequisites

- Python 3.12 or higher (3.12 is used in CI)
- Git
- Virtual environment (recommended)
- [Task](https://taskfile.dev/) (recommended for development commands)

### Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork locally:

   ```bash
   git clone https://github.com/your-username/sparkgrep.git
   cd sparkgrep
   ```

## Development Setup

### Option 1: Using Task (Recommended)

If you have [Task](https://taskfile.dev/) installed:

```bash
# Create virtual environment
task venv

# Build and install package in development mode
task build:install

# Verify installation
task run:sample
```

### Option 2: Manual Setup

### 1. Create Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 2. Install Dependencies

```bash
# Install package dependencies
pip install -r requirements.txt

# Build and install package
python -m build
pip install dist/*.whl
```

### 3. Verify Installation

```bash
# Test the installation
sparkgrep --help
```

## Project Structure

```bash
sparkgrep/
├── src/
│   ├── __init__.py           # Package initialization
│   ├── cli.py                # Command-line interface (60 lines)
│   ├── patterns.py           # Pattern definitions (54 lines)
│   ├── utils.py              # Utility functions (66 lines)
│   └── file_processors.py    # File processing logic (110 lines)
├── tests/
│   ├── test_patterns.py      # Pattern tests
│   ├── test_utils.py         # Utility tests
│   ├── test_file_processors.py  # File processor tests
│   ├── test_cli.py           # CLI tests
│   └── test_integration.py   # Integration tests
├── doc/
│   └── CONTRIBUTING.md       # This file
├── .pre-commit-hooks.yaml    # Pre-commit hook definition
├── .pre-commit-config.yaml.sample  # Sample configuration
└── pyproject.toml            # Project configuration
```

### Modular Design Principles

The project maintains **cyclomatic complexity ≤ 5** for better maintainability:

- **`patterns.py`** - Contains pattern definitions and pattern building logic
- **`utils.py`** - File reading, line processing, and reporting utilities
- **`file_processors.py`** - Python and Jupyter notebook processing logic
- **`cli.py`** - Command-line interface and argument parsing

## Making Changes

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b bugfix/issue-description
```

### 2. Make Your Changes

- Follow the existing code style
- Add tests for new functionality
- Update documentation as needed

### 3. Test Your Changes

**Using Task:**

```bash
# Run all tests
task test

# Run all quality checks (security, lint, format, test)
task quality

# Run security scan only
task security
```

**Manual commands:**

```bash
# Run all tests
.venv/bin/python -m pytest

# Run with coverage
.venv/bin/python -m pytest --cov=sparkgrep --cov-report=html

# Run specific test modules
.venv/bin/python -m pytest tests/unit/patterns/test_pattern_definitions.py -v
```

## Adding New Patterns

### Default Patterns

To add a new default pattern, edit `src/patterns.py`:

```python
USELESS_PATTERNS = [
    # ... existing patterns ...
    (r'your_new_pattern_regex', 'Description of what it catches'),
]
```

### Pattern Format

- **Regex pattern**: Valid Python regex pattern
- **Description**: Human-readable description of what the pattern catches
- **Separator**: Use colon `:` to separate pattern from description in CLI

### Example Pattern Addition

```python
# In src/patterns.py
(r'^\s*df\.cache\s*\(\s*\)\s*$', '.cache() call without assignment'),
```

### Testing New Patterns

1. **Add test cases** in `tests/test_patterns.py`:

    ```python
    def test_cache_without_assignment():
        """Test detection of cache() calls without assignment."""
        patterns = [USELESS_PATTERNS[x]]  # Replace x with your pattern index

        # Should be caught
        assert check_line_for_patterns("df.cache()", patterns)

        # Should NOT be caught
        assert not check_line_for_patterns("cached_df = df.cache()", patterns)
    ```

2. **Add integration tests** in `tests/test_integration.py`
3. **Update examples** in documentation

## Testing

### Test Structure

- **Unit tests** for all modules with 80%+ coverage
- **Integration tests** for end-to-end workflows
- **Pre-commit hook tests** for real-world scenarios
- **Error handling tests** for edge cases

### Running Tests

```bash
# All tests
pytest tests/

# Specific test file
pytest tests/test_patterns.py

# With verbose output
pytest tests/ -v

# With coverage report
pytest tests/ --cov=src --cov-report=term-missing

# Coverage HTML report
pytest tests/ --cov=src --cov-report=html
open htmlcov/index.html  # View coverage report
```

### Test Categories

Mark tests appropriately:

```python
import pytest

@pytest.mark.slow
def test_large_file_processing():
    """Test processing of large files."""
    pass

@pytest.mark.integration
def test_end_to_end_workflow():
    """Test complete workflow."""
    pass
```

Run specific test categories:

```bash
pytest tests/ -m "not slow"  # Skip slow tests
pytest tests/ -m integration  # Only integration tests
```

## Code Style

### Formatting and Linting

We use `ruff` for both code formatting and linting:

**Using Task:**

```bash
# Auto-fix linting and formatting
task fix

# Check linting only
task lint

# Generate linting report for SonarCloud
task lint:report

# Format code only
task format

# Check formatting only
task format:check
```

**Manual commands:**

```bash
# Format all code
.venv/bin/ruff format src/

# Check and fix linting issues
.venv/bin/ruff check src/ --fix

# Check only (no fixes)
.venv/bin/ruff check src/

# Security scan
.venv/bin/bandit -r src/
```

### Code Quality Standards

- **Cyclomatic complexity**: ≤ 5 for all functions
- **Line length**: 88 characters (ruff default)
- **Type hints**: Use where appropriate
- **Docstrings**: Required for all public functions (Google style)
- **Comments**: Explain complex regex patterns
- **Configuration**: All rules configured in `ruff.toml`

### Example Function

```python
def check_line_for_patterns(line: str, patterns: List[Tuple[str, str]]) -> List[Tuple[str, str]]:
    """
    Check a single line against all patterns and return matches.

    Args:
        line: The line of code to check
        patterns: List of (pattern, description) tuples

    Returns:
        List of (description, line) tuples for matches found
    """
    matches = []
    for pattern, description in patterns:
        if re.search(pattern, line, re.IGNORECASE):
            matches.append((description, line.strip()))
    return matches
```

## Pull Request Process

### 1. Before Submitting

- [ ] All quality checks pass: `task quality`
- [ ] Tests pass: `task test`
- [ ] Code formatted and linted: `task fix`
- [ ] Security scan passes: `task security`
- [ ] Documentation updated (if needed)
- [ ] Package builds successfully: `task build:install`

### 2. Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing
- [ ] Tests added/updated
- [ ] All tests pass
- [ ] Coverage maintained

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes (or clearly documented)
```

### 3. Review Process

1. **Automated checks** run via GitHub Actions (when available)
2. **Code review** by maintainers
3. **Testing** in different environments
4. **Merge** after approval

## Pattern Development Guidelines

### 1. Make Patterns Specific

Avoid overly broad patterns that catch legitimate code:

```python
# ❌ Too broad
r'display'  # Matches comments, strings, etc.

# ✅ Specific
r'^\s*display\s*\('  # Only matches function calls at line start
```

### 2. Test Extensively

Include both positive and negative test cases:

```python
# Positive cases (should be caught)
test_cases_positive = [
    "display(df)",
    "  display(data_frame)",
    "display(result)",
]

# Negative cases (should NOT be caught)
test_cases_negative = [
    "# display(df)  # comment",
    'result = display(df)',
    '"display function"',
    '"""display(df) in docstring"""',
]
```

### 3. Consider Context

Account for different coding styles and use cases:

```python
# Consider whitespace variations
r'^\s*\w+\.collect\s*\(\s*\)\s*$'

# Consider method chaining
r'^\s*\w+\.show\s*\('  # Catches df.show() but not df.show().collect()
```

### 4. Document Clearly

Explain what the pattern catches and why:

```python
(r'^\s*\w+\.collect\s*\(\s*\)\s*$', '.collect() call without assignment'),
#   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#   Regex pattern                     Clear description
```

### 5. Performance Considerations

- Use anchors (`^`, `$`) when appropriate.
- Compile patterns if used frequently.
- Test with large files.

## Getting Help

- **Issues**: Report bugs or request features via [GitHub Issues](https://github.com/leandroasaservice/sparkgrep/issues).
- **Discussions**: Ask questions in [GitHub Discussions](https://github.com/leandroasaservice/sparkgrep/discussions).
- **Email**: Contact maintainer at [lkellermann@leandroasaservice.com](mailto:lkellermann@leandroasaservice.com)

## Code of Conduct

- Be respectful and inclusive.
- Focus on constructive feedback.
- Help others learn and improve.
- Follow the golden rule.

## Recognition

Contributors will be recognized in:

- Release notes.
- Contributors list.
- Project documentation.

Thank you for contributing to SparkGrep! 🚀
