# SparkGrep - Debugging Leftovers Detector for Apache Spark Application Developers

A pre-commit hook that detects and prevents common debugging leftovers in Apache Spark applications from being committed to your repository and reaching Production environments. Works with any Spark environment including Databricks, EMR, Dataproc, and local development.

## Features

- Detects commondebugging leftovers:
  - `display()` function calls.
  - `.display()` method calls.
  - `.show()` method calls.
  - `.collect()` calls without assignment.
  - `.count()` calls without assignment.
  - `.toPandas()` calls without assignment.
  - `dbutils.notebook.exit()` calls.

- Supports both Python (.py) and Jupyter notebook (.ipynb) files.
- Respects docstrings and comments (skips them).
- Configurable with custom patterns.
- Works with any Spark environment (Databricks, EMR, Dataproc, local).

## Quick Start

### Installation

```bash
pip install -e .
```

### As a Pre-commit Hook

Add to your `.pre-commit-config.yaml`:

```yaml
repos:
 - repo: https://github.com/leandroasaservice/sparkgrep
   rev: v0.1.0a0
   hooks:
   - id: sparkgrep
     name: Check for debugging leftovers.
     files: \.(py|ipynb)$

```

### Standalone Usage

```bash
# Check single file
sparkgrep my_notebook.py

# Check multiple files
sparkgrep file1.py file2.ipynb

# With custom patterns
sparkgrep --additional-patterns "custom_debug():Custom debug function" file.py

# Disable default patterns
sparkgrep --disable-default-patterns --additional-patterns "pattern:desc" file.py
```

## Configuration

### Default Patterns

The tool detects these patterns by default:

1. `display()` function calls
2. `.display()` method calls
3. `.show()` method calls
4. `.collect()` without assignment
5. `.count()` without assignment
6. `.toPandas()` without assignment
7. `dbutils.notebook.exit()` calls

### Custom Patterns

You can add custom patterns using the `--additional-patterns` option:

```bash
sparkgrep --additional-patterns "spark\.sql.*\.show():SQL show without assignment" file.py
```

### Disable Default Patterns

Use `--disable-default-patterns` to use only custom patterns:

```bash
sparkgrep --disable-default-patterns --additional-patterns "custom:Custom pattern" file.py
```

## Examples

### What Gets Caught

```python
# ❌ These will be flagged
display(df)  # Spark display function
df.display()  # DataFrame display method
df.show()  # DataFrame show method
df.collect()  # without assignment
df.count()  # without assignment
df.toPandas()  # without assignment
dbutils.notebook.exit()  # Databricks-specific

# ✅ These are OK
result = df.collect()  # assigned
row_count = df.count()  # assigned
pandas_df = df.toPandas()  # assigned
df.show(10)  # This will still be flagged - all show() calls are detected

# ✅ These are ignored (in comments/docstrings)
# display(df)  # This is ignored
```

### Jupyter Notebook Support

The tool processes Jupyter notebooks and reports issues with cell locations:

```shell
notebook.ipynb:
  Cell 2, Line 3: display() function call
    > display(df)
  Cell 5, Line 1: .show() method call
    > df.show()
```

## Exit Codes

- **0**: No issues found (success)
- **1**: Issues found (failure - will block commit)

## Contributing

We welcome contributions! Please see our [Contributing Guide](doc/CONTRIBUTING.md) for detailed information on how to contribute to SparkGrep.

### Using Task (Optional)

We provide a [taskfile.dist.yaml](https://taskfile.dev/) for easier development workflows. Copy it to `Taskfile.yml` or `taskfile.yaml` and customize as needed. If you have Task installed, you can use commands like:

```bash
task setup          # Set up development environment
task test           # Run tests
task fix            # Auto-fix linting and formatting
task quality        # Run all quality checks
task --list         # See all available commands
```

To install Task, see: [https://taskfile.dev/installation/](https://taskfile.dev/installation/)

## License

This project is licensed under the MIT License.
