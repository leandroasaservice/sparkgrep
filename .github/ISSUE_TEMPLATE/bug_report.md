---
name: Bug Report
about: Report a bug or unexpected behavior in SparkGrep CLI
title: '[BUG] '
labels: bug, needs-triage
assignees: ''

---

## 🐛 Bug Description

**Brief summary:**
<!-- A clear and concise description of what the bug is -->

**Expected behavior:**
<!-- What you expected to happen -->

**Actual behavior:**
<!-- What actually happened -->

## 🔄 Steps to Reproduce

1. <!-- First step -->
2. <!-- Second step -->
3. <!-- Third step -->
4. <!-- See error -->

**Minimal reproducible example:**

```bash
# Command that causes the issue
sparkgrep [your command here]
```

## 📋 Environment Information

**SparkGrep version:**
<!-- Run: sparkgrep --version -->

**Python version:**
<!-- Run: python --version -->

**Operating System:**
<!-- e.g., Ubuntu 20.04, macOS 13.1, Windows 11 -->

**Installation method:**

- [ ] pip install sparkgrep
- [ ] pip install -e . (development)
- [ ] Other: <!-- specify -->

## 📁 Sample Files (if applicable)

**File type causing issue:**

- [ ] Python (.py) files
- [ ] Jupyter Notebook (.ipynb) files
- [ ] Both
- [ ] Configuration files

**Sample content:** (if you can share)

```python
# Paste problematic code snippet here
# Remove any sensitive information
```

## 📊 Command Output

**Command run:**
```bash
sparkgrep [your full command]
```

**Output/Error message:**
```
Paste the full output or error message here
```

**Verbose output:** (if available)
```bash
# Run with -v or --verbose flag
sparkgrep -v [your command]
```

## 🔍 Additional Context

**Pattern matching details:**
- [ ] Issue with default patterns
- [ ] Issue with custom patterns
- [ ] Issue with pattern file/config
- [ ] Pattern: <!-- specify the problematic pattern -->

**File processing:**
- [ ] Single file processing
- [ ] Multiple file processing
- [ ] Directory scanning
- [ ] Large file handling

**Pre-commit hook context:**
- [ ] Used as pre-commit hook
- [ ] Standalone CLI usage
- [ ] CI/CD integration

## 🤔 Possible Solution

<!-- If you have ideas on how to fix this bug, please describe them -->

## 📎 Attachments

<!--
Attach any relevant files:
- Sample files that trigger the bug
- Full error logs
- Screenshots (if UI-related)
- Configuration files
-->

---

**Checklist before submitting:**
- [ ] I have searched existing issues to avoid duplicates
- [ ] I have provided all requested information
- [ ] I have tested with the latest version of SparkGrep
- [ ] I have included a minimal reproducible example
