"""
Unit tests for notebook file processing functionality.
"""

import pytest
from pathlib import Path
from unittest.mock import MagicMock
import tempfile
import os
import json

from sparkgrep.file_processors import (
    check_notebook_file,
    _read_notebook_safely,
    _process_notebook_cell,
)


def test_read_notebook_success():
    """Test successfully reading a notebook."""
    notebook_content = {
        "cells": [
            {
                "cell_type": "code",
                "source": "print('hello')",
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
        result = _read_notebook_safely(Path(temp_path))
        assert result is not None
        assert len(result.cells) == 1
        assert result.cells[0].cell_type == "code"
    finally:
        os.unlink(temp_path)


def test_read_notebook_file_error(capsys):
    """Test reading notebook with file error."""
    result = _read_notebook_safely(Path("nonexistent.ipynb"))

    assert result is None
    captured = capsys.readouterr()
    assert "Could not read notebook" in captured.out


def test_process_code_cell_with_matches():
    """Test processing code cell with pattern matches."""
    patterns = [
        (r"display\s*\(", "display function"),
        (r"\.show\s*\(", "show method"),
    ]

    cell = MagicMock()
    cell.cell_type = "code"
    cell.source = 'display(df)\nresult = df.show()\nprint("hello")'

    issues = _process_notebook_cell(cell, 0, patterns)

    assert len(issues) == 2
    assert ("Cell 1, Line 1", "display function", "display(df)") in issues
    assert ("Cell 1, Line 2", "show method", "result = df.show()") in issues


def test_process_markdown_cell():
    """Test processing markdown cell (should be skipped)."""
    patterns = [(r"display\s*\(", "display function")]

    cell = MagicMock()
    cell.cell_type = "markdown"
    cell.source = "display(df)"

    issues = _process_notebook_cell(cell, 0, patterns)

    assert len(issues) == 0


def test_check_notebook_file_with_matches():
    """Test checking notebook file with pattern matches."""
    patterns = [
        (r"display\s*\(", "display function"),
        (r"\.show\s*\(", "show method"),
    ]

    notebook_content = {
        "cells": [
            {
                "cell_type": "code",
                "source": "display(df)",
                "metadata": {},
                "outputs": [],
            },
            {
                "cell_type": "code",
                "source": "result = df.show()",
                "metadata": {},
                "outputs": [],
            },
            {
                "cell_type": "markdown",
                "source": "display(df) in markdown should be ignored",
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
        issues = check_notebook_file(Path(temp_path), patterns)

        assert len(issues) == 2
        assert ("Cell 1, Line 1", "display function", "display(df)") in issues
        assert ("Cell 2, Line 1", "show method", "result = df.show()") in issues
    finally:
        os.unlink(temp_path)


def test_check_notebook_file_empty_notebook():
    """Test checking empty notebook file."""
    patterns = [(r"display\s*\(", "display function")]

    notebook_content = {
        "cells": [],
        "metadata": {},
        "nbformat": 4,
        "nbformat_minor": 2,
    }

    with tempfile.NamedTemporaryFile(mode="w", suffix=".ipynb", delete=False) as f:
        json.dump(notebook_content, f)
        temp_path = f.name

    try:
        issues = check_notebook_file(Path(temp_path), patterns)
        assert len(issues) == 0
    finally:
        os.unlink(temp_path)
