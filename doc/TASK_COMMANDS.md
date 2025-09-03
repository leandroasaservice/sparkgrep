# Task Commands Reference

This document lists all available Task commands for SparkGrep development. [Task](https://taskfile.dev/) is an optional build tool that simplifies common development workflows.

## Setup

First, copy the task configuration file:

```bash
cp taskfile.dist.yaml Taskfile.yml
```

## Installation

To install Task, follow the instructions at: [https://taskfile.dev/installation/](https://taskfile.dev/installation/)

Quick install options:

```bash
# macOS (via Homebrew)
brew install go-task/tap/go-task

# Go users
go install github.com/go-task/task/v3/cmd/task@latest

# NPM users
npm install -g @go-task/cli
```

## Available Commands

### Environment Setup

| Command | Description |
|---------|-------------|
| `task venv` | Create Python virtual environment |
| `task venv:recreate` | Recreate Python virtual environment |
| `task env` | Show environment information |

### Testing

| Command | Description |
|---------|-------------|
| `task test` | Run all tests with pytest |

### Code Quality

| Command | Description |
|---------|-------------|
| `task lint` | Run ruff linting (check only) |
| `task lint:report` | Run ruff linting and generate JSON report |
| `task lint:fix` | Run ruff linting with auto-fix |
| `task format` | Format code with ruff |
| `task format:check` | Check code formatting without changes |
| `task security` | Run security scan with Bandit |
| `task quality` | Run all code quality checks (security, lint, format:check, test) |
| `task fix` | Auto-fix linting and formatting issues |

### Build and Package

| Command | Description |
|---------|-------------|
| `task build` | Build package distribution |
| `task build:clean` | Clean build artifacts and rebuild |
| `task build:install` | Clean build artifacts, rebuild and install in virtual environment |
| `task build:recreate` | Clean cache, recreate environment, and build |

### Cleanup

| Command | Description |
|---------|-------------|
| `task clean` | Clean up build artifacts, cache files, and temporary files |
| `task clean:all` | Clean everything including virtual environment |

### Development Helpers

| Command | Description |
|---------|-------------|
| `task run:sample` | Run sparkgrep on sample.py |
| `task env` | Show environment information |

### Release Management

| Command | Description |
|---------|-------------|
| `task release:check` | Check if project is ready for release (runs clean:all, venv, build:install, quality) |

### Information

| Command | Description |
|---------|-------------|
| `task` (or `task default`) | Show available tasks |
| `task env` | Show environment information |
| `task --list` | List all available tasks |

## Common Workflows

### New Contributor Setup

```bash
# Copy task configuration
cp taskfile.dist.yaml Taskfile.yml

# Create virtual environment and install dependencies
task venv

# Build and install package
task build:install
```

### Before Committing

```bash
# Auto-fix code issues
task fix

# Run all quality checks
task quality
```

### Full Quality Check

```bash
# Run comprehensive quality checks (security, lint, format, test)
task quality
```

### Prepare for Release

```bash
task release:check
```

### Clean Start

```bash
# Clean everything and start fresh
task clean:all

# Copy configuration (if needed)
cp taskfile.dist.yaml Taskfile.yml

# Set up environment
task venv
task build:install
```

## Manual Equivalents

If you prefer not to use Task, here are the manual command equivalents:

| Task Command | Manual Equivalent |
|-------------|-------------------|
| `task venv` | `python3 -m venv .venv && .venv/bin/python -m pip install --upgrade pip && .venv/bin/python -m pip install -r requirements.txt` |
| `task build` | `.venv/bin/python -m build` |
| `task build:install` | `task build:clean && .venv/bin/python -m pip install dist/*.whl` |
| `task test` | `.venv/bin/python -m pytest` |
| `task lint` | `.venv/bin/ruff check src/` |
| `task format` | `.venv/bin/ruff format src/` |
| `task security` | `.venv/bin/bandit -r src/ -f json -o bandit-report.json \|\| true && .venv/bin/bandit -r src/` |
| `task fix` | `.venv/bin/ruff check src/ --fix && .venv/bin/ruff format src/` |
| `task quality` | `task security && task lint && task format:check && task test` |
| `task clean` | `rm -rf build/ dist/ *.egg-info/ .pytest_cache/ htmlcov/ .coverage .ruff-report.json coverage.xml .ruff_cache/ src/__pycache__/ tests/__pycache__/` |

## Benefits of Using Task

- **Consistency**: Same commands work across different environments.
- **Simplicity**: No need to remember complex command combinations.
- **Documentation**: Self-documenting with `task --list`.
- **Dependency management**: Tasks can depend on other tasks.
- **Cross-platform**: Works on macOS, Linux, and Windows.
