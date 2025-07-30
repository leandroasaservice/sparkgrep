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

### Setup and Installation

| Command | Description |
|---------|-------------|
| `task setup` | Set up complete development environment |
| `task install` | Install package in development mode |
| `task install:dev` | Install development dependencies |

### Testing

| Command | Description |
|---------|-------------|
| `task test` | Run all tests |
| `task test:cov` | Run tests with coverage report |

### Code Quality

| Command | Description |
|---------|-------------|
| `task lint` | Run ruff linting (check only) |
| `task lint:fix` | Run ruff linting with auto-fix |
| `task format` | Format code with ruff |
| `task format:check` | Check code formatting without changes |
| `task quality` | Run all code quality checks |
| `task fix` | Auto-fix linting and formatting issues |

### Pre-commit

| Command | Description |
|---------|-------------|
| `task pre-commit:install` | Install pre-commit hooks |
| `task pre-commit:run` | Run pre-commit on all files |
| `task pre-commit:update` | Update pre-commit hook versions |

### Build and Package

| Command | Description |
|---------|-------------|
| `task build` | Build package distribution |
| `task build:clean` | Clean and rebuild package |

### Cleanup

| Command | Description |
|---------|-------------|
| `task clean` | Clean build artifacts and cache files |
| `task clean:all` | Clean everything including virtual environment |

### Development Helpers

| Command | Description |
|---------|-------------|
| `task run:sample` | Run sparkgrep on sample.py |
| `task shell` | Show command to activate virtual environment |
| `task deps:update` | Update all dependencies |

### CI/CD and Release

| Command | Description |
|---------|-------------|
| `task ci` | Simulate CI pipeline |
| `task release:check` | Check if project is ready for release |

### Information

| Command | Description |
|---------|-------------|
| `task info` | Show project information |
| `task env` | Show environment information |
| `task --list` | List all available tasks |

## Common Workflows

### New Contributor Setup

```bash
cp taskfile.dist.yaml Taskfile.yml
task setup
```

### Before Committing

```bash
task fix
task test
```

### Full Quality Check

```bash
task quality
```

### Prepare for Release

```bash
task release:check
```

### Clean Start

```bash
task clean:all
cp taskfile.dist.yaml Taskfile.yml  # if needed
task setup
```

## Manual Equivalents

If you prefer not to use Task, here are the manual command equivalents:

| Task Command | Manual Equivalent |
|-------------|-------------------|
| `task setup` | `python3 -m venv .venv && .venv/bin/pip install -e .[dev] && .venv/bin/pre-commit install` |
| `task test` | `.venv/bin/pytest tests/` |
| `task fix` | `.venv/bin/ruff check src/ --fix && .venv/bin/ruff format src/` |
| `task quality` | `.venv/bin/ruff check src/ && .venv/bin/ruff format src/ --check && .venv/bin/pytest tests/` |
| `task clean` | `rm -rf build/ dist/ *.egg-info/ .pytest_cache/ htmlcov/ .coverage .ruff_cache/` |

## Benefits of Using Task

- **Consistency**: Same commands work across different environments.
- **Simplicity**: No need to remember complex command combinations.
- **Documentation**: Self-documenting with `task --list`.
- **Dependency management**: Tasks can depend on other tasks.
- **Cross-platform**: Works on macOS, Linux, and Windows.
