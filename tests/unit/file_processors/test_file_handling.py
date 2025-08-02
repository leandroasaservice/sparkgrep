"""
Unit tests for general file handling functionality.
"""

import pytest
from pathlib import Path
import tempfile
import os
import json

from sparkgrep.file_processors import process_single_file


def test_process_python_file():
    """Test processing a Python file."""
    patterns = [(r"display\s*\(", "display function")]

    python_code = """
def test_function():
    display(df)
    print("hello")
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(python_code)
        temp_path = f.name

    try:
        issues = process_single_file(temp_path, patterns)

        assert len(issues) == 1
        assert issues[0][1] == "display function"
    finally:
        os.unlink(temp_path)


def test_process_notebook_file():
    """Test processing a Jupyter notebook file."""
    patterns = [(r"display\s*\(", "display function")]

    notebook_content = {
        "cells": [
            {
                "cell_type": "code",
                "source": "display(df)",
                "metadata": {},
                "outputs": [],
            }
        ],
        "metadata": {},
        "nbformat": 4,
        "nbformat_minor": 2,
    }

    with tempfile.NamedTemporaryFile(mode="w", suffix=".ipynb", delete=False) as f:
        json.dump(notebook_content, f)
        temp_path = f.name

    try:
        issues = process_single_file(temp_path, patterns)

        assert len(issues) == 1
        assert issues[0][1] == "display function"
    finally:
        os.unlink(temp_path)


def test_process_unsupported_file_type():
    """Test processing unsupported file type."""
    patterns = [(r"display\s*\(", "display function")]

    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("display(df)")
        temp_path = f.name

    try:
        issues = process_single_file(temp_path, patterns)
        assert len(issues) == 0
    finally:
        os.unlink(temp_path)


def test_process_nonexistent_file():
    """Test processing nonexistent file."""
    patterns = [(r"display\s*\(", "display function")]

    issues = process_single_file("nonexistent.py", patterns)
    assert len(issues) == 0


def test_process_file_path_handling():
    """Test that file path handling works correctly."""
    patterns = [(r"display\s*\(", "display function")]

    python_code = """
def test_function():
    display(df)
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(python_code)
        temp_path = f.name

    try:
        # Test with string path
        issues = process_single_file(temp_path, patterns)
        assert len(issues) == 1

        # Test with Path object
        issues = process_single_file(Path(temp_path), patterns)
        assert len(issues) == 1
    finally:
        os.unlink(temp_path)
