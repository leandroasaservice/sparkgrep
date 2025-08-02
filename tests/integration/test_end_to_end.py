"""
End-to-end integration tests for the complete sparkgrep workflow.
"""

import pytest
import tempfile
import os
import json

from sparkgrep.patterns import build_patterns_list
from sparkgrep.file_processors import process_single_file


def test_full_workflow_python_file_with_issues():
    """Test complete workflow with Python file containing issues."""
    python_code = """
def test_function():
    display(df)  # Should be caught
    df.show()  # Should be caught
    df.collect()
    df.count()
    df.toPandas()
    print("This is fine")
    return result
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(python_code)
        temp_path = f.name

    try:
        # Test using the complete workflow
        patterns = build_patterns_list()
        issues = process_single_file(temp_path, patterns)

        # Should find multiple issues
        assert len(issues) >= 4  # At least display, show, collect, count, toPandas

        # Check specific issues
        issue_descriptions = [issue[1] for issue in issues]
        assert any("display" in desc for desc in issue_descriptions)
        assert any("show" in desc for desc in issue_descriptions)

    finally:
        os.unlink(temp_path)


def test_full_workflow_notebook_with_issues():
    """Test complete workflow with Jupyter notebook containing issues."""
    notebook_content = {
        "cells": [
            {
                "cell_type": "code",
                "source": "# Setup\nimport pandas as pd\nfrom pyspark.sql import SparkSession",
                "metadata": {},
                "outputs": [],
            },
            {
                "cell_type": "code",
                "source": "display(df)  # Should be caught",
                "metadata": {},
                "outputs": [],
            },
            {
                "cell_type": "code",
                "source": "df.show()  # Should be caught\nresult = df.collect()  # Should NOT be caught (assignment)",
                "metadata": {},
                "outputs": [],
            },
            {
                "cell_type": "markdown",
                "source": "This is markdown with display(df) - should be ignored",
            },
        ],
        "metadata": {},
        "nbformat": 4,
        "nbformat_minor": 2,
    }

    with tempfile.NamedTemporaryFile(mode="w", suffix=".ipynb", delete=False) as f:
        json.dump(notebook_content, f)
        temp_path = f.name

    try:
        patterns = build_patterns_list()
        issues = process_single_file(temp_path, patterns)

        # Should find 2 issues (display and show)
        assert len(issues) == 2

        # Check specific issues
        issue_descriptions = [issue[1] for issue in issues]
        assert any("display" in desc for desc in issue_descriptions)
        assert any("show" in desc for desc in issue_descriptions)

        # Check cell locations
        locations = [issue[0] for issue in issues]
        assert "Cell 2, Line 1" in locations
        assert "Cell 3, Line 1" in locations

    finally:
        os.unlink(temp_path)


def test_full_workflow_no_issues():
    """Test complete workflow with clean files."""
    python_code = '''
def test_function():
    """
    This function has display(df) in docstring but it's ignored.
    """
    # Also has display(df) in comment but it's ignored
    result = df.collect()  # This is assigned, so it's OK
    pandas_df = df.toPandas()  # This is assigned, so it's OK
    print("All good")
    return result
'''

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(python_code)
        temp_path = f.name

    try:
        patterns = build_patterns_list()
        issues = process_single_file(temp_path, patterns)

        # Should find no issues
        assert len(issues) == 0

    finally:
        os.unlink(temp_path)


def test_custom_patterns_integration():
    """Test integration with custom patterns."""
    python_code = """
def test_function():
    display(df)  # Default pattern
    custom_debug_function()  # Custom pattern
    print("hello")
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(python_code)
        temp_path = f.name

    try:
        # Test with custom patterns
        patterns = build_patterns_list(
            disable_default_patterns=False,
            additional_patterns=[
                "custom_debug_function:Custom debug function",
            ],
        )

        issues = process_single_file(temp_path, patterns)

        # Should find multiple issues (default + custom)
        assert len(issues) >= 2

        issue_descriptions = [issue[1] for issue in issues]
        assert any("display" in desc for desc in issue_descriptions)

    finally:
        os.unlink(temp_path)
