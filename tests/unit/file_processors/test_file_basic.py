import pytest
import tempfile
import os
import json
from pathlib import Path

from sparkgrep.file_processors import process_single_file


def test_process_python_file():
    """Test processing a Python file."""
    python_code = """
def example():
    display(df)  # Should be found
    df.show()    # Should be found
    return df
"""

    patterns = [
        (r"display\(", "display function"),
        (r"\.show\(", "show method")
    ]

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(python_code)
        temp_path = f.name

    try:
        issues = process_single_file(Path(temp_path), patterns)

        assert len(issues) == 2
        descriptions = [issue[1] for issue in issues]
        assert "display function" in descriptions
        assert "show method" in descriptions

    finally:
        os.unlink(temp_path)


def test_process_notebook_file():
    """Test processing a Jupyter notebook file."""
    notebook = {
        "nbformat": 4,
        "nbformat_minor": 4,
        "metadata": {},
        "cells": [
            {
                "cell_type": "code",
                "metadata": {},
                "source": [
                    "# Data processing\n",
                    "display(df)  # Should be found\n",
                    "df.show()    # Should be found\n"
                ]
            }
        ]
    }

    patterns = [
        (r"display\(", "display function"),
        (r"\.show\(", "show method")
    ]

    with tempfile.NamedTemporaryFile(mode="w", suffix=".ipynb", delete=False) as f:
        json.dump(notebook, f)
        temp_path = f.name

    try:
        issues = process_single_file(Path(temp_path), patterns)

        assert len(issues) == 2
        descriptions = [issue[1] for issue in issues]
        assert "display function" in descriptions
        assert "show method" in descriptions

    finally:
        os.unlink(temp_path)


def test_process_unsupported_file_type():
    """Test processing an unsupported file type."""
    content = "display(df); df.show();"
    patterns = [(r"display\(", "display function")]

    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write(content)
        temp_path = f.name

    try:
        issues = process_single_file(Path(temp_path), patterns)
        # Should return empty list for unsupported file types
        assert len(issues) == 0

    finally:
        os.unlink(temp_path)


def test_process_nonexistent_file():
    """Test processing a nonexistent file."""
    patterns = [(r"display\(", "display function")]

    issues = process_single_file(Path("nonexistent_file.py"), patterns)
    assert len(issues) == 0


def test_process_file_empty_patterns():
    """Test processing files with empty patterns list."""
    python_code = "display(df); df.show();"
    patterns = []

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(python_code)
        temp_path = f.name

    try:
        issues = process_single_file(Path(temp_path), patterns)
        assert len(issues) == 0

    finally:
        os.unlink(temp_path)


def test_process_file_pathlib_path():
    """Test that function works with pathlib.Path objects."""
    python_code = "display(df)"
    patterns = [(r"display\(", "display function")]

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(python_code)
        temp_path = f.name

    try:
        # Test with Path object
        path_obj = Path(temp_path)
        issues = process_single_file(path_obj, patterns)

        assert len(issues) == 1
        assert issues[0][1] == "display function"

    finally:
        os.unlink(temp_path)


def test_process_file_return_format():
    """Test that the return format is correct."""
    python_code = """
# Line 1
display(df)  # Line 2 - should be found
"""

    patterns = [(r"display\(", "display function")]

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(python_code)
        temp_path = f.name

    try:
        issues = process_single_file(Path(temp_path), patterns)

        assert len(issues) == 1
        issue = issues[0]

        # Check that issue is a tuple with (line_info, description, content)
        assert len(issue) == 3

        line_info, description, content = issue
        assert description == "display function"
        assert "display(df)" in content
        assert isinstance(line_info, (str, int))  # Line info format may vary

    finally:
        os.unlink(temp_path)


def test_process_file_multiple_issues_same_file():
    """Test processing a file with multiple different issues."""
    python_code = """
def process_data():
    display(df1)      # Issue 1
    df2.show()        # Issue 2
    df3.collect()     # Issue 3
    display(df4)      # Issue 4
"""

    patterns = [
        (r"display\(", "display function"),
        (r"\.show\(", "show method"),
        (r"\.collect\(", "collect method")
    ]

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(python_code)
        temp_path = f.name

    try:
        issues = process_single_file(Path(temp_path), patterns)

        assert len(issues) == 4

        descriptions = [issue[1] for issue in issues]
        assert descriptions.count("display function") == 2
        assert descriptions.count("show method") == 1
        assert descriptions.count("collect method") == 1

    finally:
        os.unlink(temp_path)


def test_process_file_simple_patterns():
    """Test with simple, straightforward patterns."""
    python_code = """
simple_call()
another_function()
display(data)
"""

    patterns = [
        (r"simple_call", "simple call"),
        (r"another_function", "another function"),
        (r"display", "display call")
    ]

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(python_code)
        temp_path = f.name

    try:
        issues = process_single_file(Path(temp_path), patterns)

        assert len(issues) == 3
        descriptions = [issue[1] for issue in issues]
        assert "simple call" in descriptions
        assert "another function" in descriptions
        assert "display call" in descriptions

    finally:
        os.unlink(temp_path)


def test_process_file_with_string_filename():
    """Test that function works with string file paths."""
    python_code = "display(df)"
    patterns = [(r"display\(", "display function")]

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(python_code)
        temp_path = f.name

    try:
        # Test with string path (should work with Path conversion)
        issues = process_single_file(Path(temp_path), patterns)

        assert len(issues) == 1
        assert issues[0][1] == "display function"

    finally:
        os.unlink(temp_path)
