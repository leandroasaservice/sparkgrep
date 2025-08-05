import pytest
import tempfile
import os
import json
from pathlib import Path

from sparkgrep.file_processors import check_notebook_file


def create_test_notebook(cells):
    """Helper function to create a test notebook with given cells."""
    notebook = {
        "nbformat": 4,
        "nbformat_minor": 4,
        "metadata": {},
        "cells": cells
    }
    return notebook


def test_check_notebook_file_with_matches():
    """Test checking a notebook that contains pattern matches."""
    cells = [
        {
            "cell_type": "code",
            "metadata": {},
            "source": [
                "# Load data\n",
                "df = spark.read.parquet('data.parquet')\n",
                "display(df)  # This should match\n"
            ]
        },
        {
            "cell_type": "code",
            "metadata": {},
            "source": [
                "# Process data\n",
                "df.show()  # This should also match\n"
            ]
        }
    ]

    notebook = create_test_notebook(cells)
    patterns = [
        (r"display\(", "display function"),
        (r"\.show\(", "show method")
    ]

    with tempfile.NamedTemporaryFile(mode="w", suffix=".ipynb", delete=False) as f:
        json.dump(notebook, f)
        temp_path = f.name

    try:
        issues = check_notebook_file(Path(temp_path), patterns)

        assert len(issues) == 2

        descriptions = [issue[1] for issue in issues]
        assert "display function" in descriptions
        assert "show method" in descriptions

    finally:
        os.unlink(temp_path)


def test_check_notebook_file_no_matches():
    """Test checking a notebook with no pattern matches."""
    cells = [
        {
            "cell_type": "code",
            "metadata": {},
            "source": [
                "import pandas as pd\n",
                "data = [1, 2, 3, 4, 5]\n",
                "print(f'Data: {data}')\n"
            ]
        },
        {
            "cell_type": "code",
            "metadata": {},
            "source": [
                "result = sum(data)\n",
                "print(f'Sum: {result}')\n"
            ]
        }
    ]

    notebook = create_test_notebook(cells)
    patterns = [
        (r"display\(", "display function"),
        (r"\.show\(", "show method")
    ]

    with tempfile.NamedTemporaryFile(mode="w", suffix=".ipynb", delete=False) as f:
        json.dump(notebook, f)
        temp_path = f.name

    try:
        issues = check_notebook_file(Path(temp_path), patterns)
        assert len(issues) == 0

    finally:
        os.unlink(temp_path)


def test_check_notebook_file_multiple_code_cells():
    """Test checking notebook with multiple code cells."""
    cells = [
        {
            "cell_type": "code",
            "metadata": {},
            "source": [
                "# Cell 1\n",
                "df1 = load_data()\n",
                "display(df1)\n"
            ]
        },
        {
            "cell_type": "code",
            "metadata": {},
            "source": [
                "# Cell 2\n",
                "df2 = transform_data(df1)\n",
                "df2.show()\n"
            ]
        },
        {
            "cell_type": "code",
            "metadata": {},
            "source": [
                "# Cell 3\n",
                "final_result = df2.collect()\n",
                "print('Done')\n"
            ]
        }
    ]

    notebook = create_test_notebook(cells)
    patterns = [
        (r"display\(", "display function"),
        (r"\.show\(", "show method"),
        (r"\.collect\(", "collect method")
    ]

    with tempfile.NamedTemporaryFile(mode="w", suffix=".ipynb", delete=False) as f:
        json.dump(notebook, f)
        temp_path = f.name

    try:
        issues = check_notebook_file(Path(temp_path), patterns)

        assert len(issues) == 3

        descriptions = [issue[1] for issue in issues]
        assert "display function" in descriptions
        assert "show method" in descriptions
        assert "collect method" in descriptions

    finally:
        os.unlink(temp_path)


def test_check_notebook_file_empty_notebook():
    """Test checking an empty notebook."""
    cells = []

    notebook = create_test_notebook(cells)
    patterns = [(r"display\(", "display function")]

    with tempfile.NamedTemporaryFile(mode="w", suffix=".ipynb", delete=False) as f:
        json.dump(notebook, f)
        temp_path = f.name

    try:
        issues = check_notebook_file(Path(temp_path), patterns)
        assert len(issues) == 0

    finally:
        os.unlink(temp_path)


def test_check_notebook_file_nonexistent():
    """Test handling of nonexistent notebook files."""
    patterns = [(r"display\(", "display function")]

    issues = check_notebook_file(Path("nonexistent_notebook.ipynb"), patterns)
    assert len(issues) == 0


def test_check_notebook_file_empty_patterns():
    """Test checking notebook with empty patterns list."""
    cells = [
        {
            "cell_type": "code",
            "metadata": {},
            "source": [
                "display(df)\n",
                "df.show()\n"
            ]
        }
    ]

    notebook = create_test_notebook(cells)
    patterns = []  # Empty patterns list

    with tempfile.NamedTemporaryFile(mode="w", suffix=".ipynb", delete=False) as f:
        json.dump(notebook, f)
        temp_path = f.name

    try:
        issues = check_notebook_file(Path(temp_path), patterns)
        assert len(issues) == 0  # No patterns to match

    finally:
        os.unlink(temp_path)


def test_check_notebook_file_simple_patterns():
    """Test notebook checking with simple regex patterns."""
    cells = [
        {
            "cell_type": "code",
            "metadata": {},
            "source": [
                "simple_function()\n",
                "another_call()\n"
            ]
        }
    ]

    notebook = create_test_notebook(cells)
    patterns = [
        (r"simple_function", "simple function call"),
        (r"another_call", "another function call")
    ]

    with tempfile.NamedTemporaryFile(mode="w", suffix=".ipynb", delete=False) as f:
        json.dump(notebook, f)
        temp_path = f.name

    try:
        issues = check_notebook_file(Path(temp_path), patterns)

        assert len(issues) == 2
        descriptions = [issue[1] for issue in issues]
        assert "simple function call" in descriptions
        assert "another function call" in descriptions

    finally:
        os.unlink(temp_path)


def test_check_notebook_file_line_numbers():
    """Test that line numbers are reported correctly."""
    cells = [
        {
            "cell_type": "code",
            "metadata": {},
            "source": [
                "# First line\n",
                "display(df)  # Second line\n",
                "# Third line\n"
            ]
        }
    ]

    notebook = create_test_notebook(cells)
    patterns = [(r"display\(", "display function")]

    with tempfile.NamedTemporaryFile(mode="w", suffix=".ipynb", delete=False) as f:
        json.dump(notebook, f)
        temp_path = f.name

    try:
        issues = check_notebook_file(Path(temp_path), patterns)

        assert len(issues) == 1
        # Check that line number is correctly reported
        line_info = issues[0][0]
        assert "2" in str(line_info)  # Should be line 2

    finally:
        os.unlink(temp_path)
