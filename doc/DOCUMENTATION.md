# SparkGrep - Apache Spark Pre-commit Hooks - Comprehensive Documentation

## Table of Contents

1. [Overview](#overview)
2. [Installation Guide](#installation-guide)
3. [Default Patterns](#default-patterns)
4. [Configuration Options](#configuration-options)
5. [Usage Examples](#usage-examples)
6. [Testing Guide](#testing-guide)
7. [Advanced Configuration](#advanced-configuration)
8. [Troubleshooting](#troubleshooting)

## Overview

This pre-commit hook is designed for Apache Spark development environments to automatically detect and prevent common debugging leftovers before they reach your repository. Works with any Spark platform including Azure Databricks, AWS EMR, Google Dataproc, and local Spark development.

### Key Features

- **Automatic Detection**: Identifies problematic patterns in Python files and Jupyter notebooks
- **Configurable Patterns**: Supports both default patterns and custom user-defined patterns
- **Multi-file Support**: Works with `.py` and `.ipynb` files
- **Flexible Configuration**: Configure via command line or `.pre-commit-config.yaml`
- **Comprehensive Reporting**: Detailed output showing exact locations and descriptions of issues

### Supported File Types

- **Python Files (`.py`)**: Full pattern matching support
- **Jupyter Notebooks (`.ipynb`)**: Checks code cells, ignores magic commands and markdown

## Installation Guide

### Prerequisites

- Python 3.12 or higher (3.12 is used in CI)
- Git repository initialized
- pip package manager
- [Task](https://taskfile.dev/) (recommended for development)

### Step-by-Step Installation

1. **Install pre-commit framework**:

    ```bash
    pip install pre-commit
    ```

2. **Set up development environment**:

    ```bash
    # Using Task (recommended)
    task venv
    task build:install

    # Or manually
    python3 -m venv .venv
    .venv/bin/pip install -r requirements.txt
    .venv/bin/python -m build
    .venv/bin/pip install dist/*.whl
    ```

3. **Verify installation**:

    ```bash
    # Test the package
    sparkgrep --help

    # Run sample command
    task run:sample  # or sparkgrep sample.py
    ```

## Default Patterns

The system includes seven default patterns that catch common Spark debugging leftovers:

### 1. `display` Function Or Method Calls

**Pattern**: `\s*display\s*\(`
**Description**: Catches standalone `display()` function calls
**Example**:

```python
display(df)  # ❌ Caught
result = display(df)  # ❌ Caught

df.display()  # ❌ Caught
result = df.display()  # ❌ Caught

```

### 2. `show` Method Calls

**Pattern**: `^\s*\w+\.show\s*\(`
**Description**: Catches all `.show()` method calls (with or without parameters)
**Example**:

```python
df.show()      # ❌ Caught
df.show(10)    # ❌ Caught
df.show(20, False)  # ❌ Caught
```

### 3. `collect` Without Assignment

**Pattern**: `^\s*\w+\.collect\s*\(\s*\)\s*$`
**Description**: Catches `.collect()` calls not assigned to variables
**Example**:

```python
df.collect()  # ❌ Caught
result = df.collect()  # ✅ Not caught (assigned)
```

### 4. `count` Without Assignment

**Pattern**: `^\s*\w+\.count\s*\(\s*\)\s*$`
**Description**: Catches `.count()` calls not assigned to variables
**Example**:

```python
df.count()  # ❌ Caught
row_count = df.count()  # ✅ Not caught (assigned)
```

### 5. `toPandas` Without Assignment

**Pattern**: `^\s*\w+\.toPandas\s*\(\s*\)\s*$`
**Description**: Catches `.toPandas()` calls not assigned to variables
**Example**:

```python
df.toPandas()  # ❌ Caught
pandas_df = df.toPandas()  # ✅ Not caught (assigned)
```

### 7. DBUtils Notebook Exit (Databricks-specific)

**Pattern**: `dbutils\.notebook\.exit\s*\(\s*\)`
**Description**: Catches Databricks debugging exit calls
**Example**:

```python
dbutils.notebook.exit()  # ❌ Caught
```

## Configuration Options

### Basic Configuration (Default Patterns Only)

```yaml
# .pre-commit-config.yaml
- repo: local
  hooks:
    - id: sparkgrep
      name: Check for useless Databricks actions
      entry: sparkgrep
      language: python
      files: \.(py|ipynb)$
      additional_dependencies: [nbformat]
```

### Adding Custom Patterns

```yaml
- repo: local
  hooks:
    - id: sparkgrep
      name: Check for useless Databricks actions
      entry: sparkgrep
      language: python
      files: \.(py|ipynb)$
      additional_dependencies: [nbformat]
      args: [
        "--additional-patterns",
        "print.*debug:Debug print statement",
        "createDataFrame.*test:Test DataFrame creation",
        "spark\.sql.*select \*:Select all from table",
        "\.head\s*\(\s*\):DataFrame head() call",
        "\.count\s*\(\s*\)\s*>:DataFrame count() in comparison"
      ]
```

### Using Only Custom Patterns

```yaml
args: [
  "--disable-default-patterns",
  "--additional-patterns",
  "your_pattern_1:Description 1",
  "your_pattern_2:Description 2"
]
```

### Pattern Format

All patterns must follow the format: `"regex_pattern:description"`

- **regex_pattern**: Valid Python regex pattern
- **description**: Human-readable description of what the pattern catches
- **Separator**: Use colon `:` to separate pattern from description

## Usage Examples

### Command Line Usage

#### Basic Usage

```bash
# Check single file with default patterns
sparkgrep my_notebook.py

# Check multiple files
sparkgrep file1.py file2.ipynb file3.py
```

#### With Additional Patterns

```bash
# Add custom patterns to defaults
sparkgrep file.py \
  --additional-patterns \
  "print.*debug:Debug print statement" \
  "\.head\(\):DataFrame head() call"
```

#### Custom Patterns Only

```bash
# Use only custom patterns
sparkgrep file.py \
  --disable-default-patterns \
  --additional-patterns \
  "custom_pattern:Custom description"
```

### Pre-commit Integration

#### Automatic on Commit

```bash
git add my_changes.py
git commit -m "Add new feature"
# Hook runs automatically and blocks commit if issues found
```

#### Manual Execution

```bash
# Run on all files
pre-commit run --all-files

# Run on specific files
pre-commit run --files path/to/file.py

# Run only this specific hook
pre-commit run sparkgrep
```

## Testing Guide

### Setting Up Test Environment

1. **Create test files** to verify the hook works correctly:

    ```bash
    # Create a test directory
    mkdir tests
    cd tests
    ```

2. **Create test files with various patterns**:

    ```python
    # tests/test_positive_cases.py
    # File with issues that SHOULD be caught

    import pandas as pd
    from pyspark.sql import SparkSession

    spark = SparkSession.builder.appName("test").getOrCreate()
    df = spark.createDataFrame([(1, "test")], ["id", "name"])

    # These should be caught by default patterns
    display(df)  # Spark display function
    df.display()  # DataFrame display method
    df.show()  # DataFrame show method
    df.show(10)  # DataFrame show with parameters
    df.collect()  # DataFrame collect without assignment
    df.count()  # DataFrame count without assignment
    df.toPandas()  # DataFrame conversion without assignment
    dbutils.notebook.exit()  # Databricks-specific exit

    # These should be caught by custom patterns (if enabled)
    print("Debug: processing started")
    test_df = spark.createDataFrame([(1, "test")], ["id", "name"])
    df.head()
    ```

```python
# File with code that should NOT be caught

import pandas as pd
from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("test").getOrCreate()
df = spark.createDataFrame([(1, "test")], ["id", "name"])

# These should NOT be caught (legitimate uses)
result = df.collect()
pandas_df = df.toPandas()
output = display(df)  # Assignment
print("Processing complete")  # Not debug print
users_df = spark.sql("SELECT id, name FROM users")  # Specific query

# Comments should be ignored
# display(df) - this is just a comment
"""
This docstring mentions df.show() but should be ignored
"""
```

### Test Scenarios

#### Test 1: Default Patterns Only

```bash
# Should find 7 issues in test_positive_cases.py
sparkgrep tests/test_positive_cases.py

# Should find 0 issues in test_negative_cases.py
sparkgrep tests/test_negative_cases.py
```

**Expected Output**:

```bash
tests/test_positive_cases.py:
  Line 9: display() function call
    > display(df)
  Line 10: .display() method call
    > df.display()
  Line 11: .show() method call
    > df.show()
  Line 12: .show() method call
    > df.show(10)
  Line 13: .collect() call without assignment
    > df.collect()
  Line 14: .count() call without assignment
    > df.count()
  Line 15: .toPandas() without assignment
    > df.toPandas()
  Line 16: dbutils.notebook.exit() call
    > dbutils.notebook.exit()

Found 8 useless Databricks action(s)
Please remove these before committing.
```

#### Test 2: Additional Patterns

```bash
# Test with additional patterns
sparkgrep tests/test_positive_cases.py \
  --additional-patterns \
  "print.*Debug:Debug print statement" \
  "createDataFrame.*test:Test DataFrame creation" \
  "\.head\s*\(\s*\):DataFrame head() call"
```

**Expected Output**: Should find 10 issues (7 default + 3 custom)

#### Test 3: Custom Patterns Only

```bash
# Test with only custom patterns
sparkgrep tests/test_positive_cases.py \
  --disable-default-patterns \
  --additional-patterns \
  "print.*Debug:Debug print statement" \
  "\.head\s*\(\s*\):DataFrame head() call"
```

**Expected Output**: Should find 2 issues (only custom patterns)

#### Test 4: Notebook Files

Create a test notebook:

```python
{
  "cells": [
    {
      "cell_type": "code",
      "source": [
        "import pandas as pd\n",
        "from pyspark.sql import SparkSession\n",
        "\n",
        "spark = SparkSession.builder.appName(\"test\").getOrCreate()\n",
        "df = spark.createDataFrame([(1, \"test\")], [\"id\", \"name\"])\n",
        "\n",
        "# This should be caught\n",
        "display(df)\n",
        "df.show()"
      ]
    }
  ]
}
```

```bash
# Test notebook processing
sparkgrep tests/test_notebook.ipynb
```

#### Test 5: Quality Integration

```bash
# Test quality checks
echo "display(df)" > test_file.py
sparkgrep test_file.py  # Should find issues

# Test with Task
task quality  # Should run all quality checks
```

### Performance Testing

#### Large File Testing

```bash
# Create a large test file
python -c "
with open('large_test.py', 'w') as f:
    f.write('# Large file test\n')
    for i in range(1000):
        f.write(f'df_{i} = spark.table(\"table_{i}\")\n')
        f.write(f'display(df_{i})\n')
"

# Time the execution
time sparkgrep large_test.py
```

#### Batch Testing

```bash
# Test multiple files at once
sparkgrep tests/*.py tests/*.ipynb
```

### Automated Testing Script

Create a comprehensive test runner:

```python
# tests/run_tests.py
#!/usr/bin/env python3
"""
Comprehensive test runner for SparkGrep.
Tests all functionality including patterns, CLI, and quality checks.
"""

import subprocess
import sys
from pathlib import Path

def run_test(description, command, expected_exit_code=0):
    """Run a test and report results."""
    print(f"\n{'='*60}")
    print(f"TEST: {description}")
    print(f"COMMAND: {command}")
    print(f"{'='*60}")

    result = subprocess.run(command, shell=True, capture_output=True, text=True)

    if result.returncode == expected_exit_code:
        print("✅ PASSED")
    else:
        print("❌ FAILED")
        print(f"Expected exit code: {expected_exit_code}")
        print(f"Actual exit code: {result.returncode}")
        print(f"STDOUT:\n{result.stdout}")
        print(f"STDERR:\n{result.stderr}")
        return False

    print(f"STDOUT:\n{result.stdout}")
    if result.stderr:
        print(f"STDERR:\n{result.stderr}")

    return True

def main():
    tests = [
        ("Default patterns with issues",
         "sparkgrep tests/test_positive_cases.py", 1),

        ("Default patterns without issues",
         "sparkgrep tests/test_negative_cases.py", 0),

        ("Additional patterns",
         "sparkgrep tests/test_positive_cases.py --additional-patterns 'print.*Debug:Debug print'", 1),

        ("Custom patterns only",
         "sparkgrep tests/test_positive_cases.py --disable-default-patterns --additional-patterns 'print.*Debug:Debug print'", 1),

        ("No files provided",
         "sparkgrep", 0),

        ("Invalid pattern format",
         "sparkgrep tests/test_positive_cases.py --additional-patterns 'invalid_format'", 1),
    ]

    passed = 0
    total = len(tests)

    for description, command, expected_exit_code in tests:
        if run_test(description, command, expected_exit_code):
            passed += 1

    print(f"\n{'='*60}")
    print(f"TEST SUMMARY: {passed}/{total} tests passed")
    print(f"{'='*60}")

    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(main())
```

Run the automated tests:

```bash
chmod +x tests/run_tests.py
python tests/run_tests.py
```

## Advanced Configuration

### Creating Custom Pattern Libraries

Create reusable pattern sets for different teams or projects:

```python
# patterns/databricks_patterns.py
PERFORMANCE_PATTERNS = [
    (r'\.collect\s*\(\s*\)\.', 'Collect followed by operation (inefficient)'),
    (r'\.count\s*\(\s*\)\s*>', 'Count in comparison (consider caching)'),
    (r'\.toPandas\s*\(\s*\)\.', 'toPandas followed by operation (consider alternatives)'),
]

DEBUGGING_PATTERNS = [
    (r'print\s*\(.*debug', 'Debug print statement'),
    (r'print\s*\(.*TODO', 'TODO print statement'),
    (r'\.head\s*\(\s*\)', 'DataFrame head() call'),
]

SECURITY_PATTERNS = [
    (r'spark\.sql\s*\(.*password', 'Potential password in SQL'),
    (r'dbutils\.secrets\.get\s*\(.*print', 'Secret value being printed'),
]
```

### Environment-Specific Configurations

```yaml
# .pre-commit-config.yaml for development
- repo: local
  hooks:
    - id: databricks-useless-actions
      name: Check for useless Databricks actions (Dev)
      entry: python scripts/check_spark_actions.py
      language: python
      files: \.(py|ipynb)$
      additional_dependencies: [nbformat]
      args: [
        "--additional-patterns",
        "print.*debug:Debug print statement",
        "\.head\(\):DataFrame head() call"
      ]
```

```yaml
# .pre-commit-config.yaml for production
- repo: local
  hooks:
    - id: databricks-useless-actions
      name: Check for useless Databricks actions (Prod)
      entry: python scripts/check_spark_actions.py
      language: python
      files: \.(py|ipynb)$
      additional_dependencies: [nbformat]
      args: [
        "--additional-patterns",
        "print.*debug:Debug print statement",
        "\.head\(\):DataFrame head() call",
        "createDataFrame.*test:Test DataFrame creation",
        "dbutils\.fs\.rm.*tmp:Temporary file operations"
      ]
```

### Configuration File Support

For complex pattern sets, you can extend the script to support configuration files:

```python
# config/databricks_patterns.yaml
default_patterns:
  - pattern: "^\s*display\s*\("
    description: "display() function call"
  - pattern: "^\s*\w+\.display\s*\("
    description: ".display() method call"

custom_patterns:
  performance:
    - pattern: "\.collect\s*\(\s*\)\."
      description: "Collect followed by operation"
  debugging:
    - pattern: "print\s*\(.*debug"
      description: "Debug print statement"
```

## Troubleshooting

### Common Issues

#### 1. Hook Not Running

**Symptom**: Pre-commit hook doesn't execute on commit
**Solution**:

```bash
# Reinstall hooks
pre-commit uninstall
pre-commit install

# Check hook configuration
pre-commit run --all-files
```

#### 2. Script Not Executable

**Symptom**: Permission denied error
**Solution**:

```bash
chmod +x scripts/check_spark_actions.py
```

#### 3. Notebook Processing Fails

**Symptom**: "nbformat not installed" warning
**Solution**:

```bash
pip install nbformat
```

#### 4. Pattern Not Matching

**Symptom**: Expected pattern not caught
**Solution**:

```bash
# Test pattern interactively
python -c "
import re
pattern = r'your_pattern_here'
test_string = 'your_test_string'
print(re.search(pattern, test_string))
"
```

#### 5. False Positives

**Symptom**: Legitimate code flagged as problematic
**Solutions**:

- Refine regex patterns to be more specific
- Use negative lookahead/lookbehind assertions
- Add context-aware filtering

### Debug Mode

Add debug output to the script for troubleshooting:

```python
# Add to cli.py
import os

DEBUG = os.getenv('DEBUG', 'false').lower() == 'true'

def debug_print(msg):
    if DEBUG:
        print(f"DEBUG: {msg}")

# Usage
debug_print(f"Checking pattern: {pattern}")
debug_print(f"Against line: {line.strip()}")
```

```bash
# Run with debug output
DEBUG=true sparkgrep file.py
```

### Performance Optimization

For large codebases:

```python
# Optimize pattern compilation
import re

# Compile patterns once
compiled_patterns = [(re.compile(pattern), desc) for pattern, desc in patterns]

# Use compiled patterns
for compiled_pattern, description in compiled_patterns:
    if compiled_pattern.search(line):
        issues.append((line_num, description, line.strip()))
```

## Contributing

For detailed information on contributing to SparkGrep, including development setup, coding standards, and submission guidelines, please see our [Contributing Guide](CONTRIBUTING.md).
