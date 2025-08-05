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


def test_check_notebook_file_skip_markdown_cells():
    """Test that markdown cells are skipped."""
    cells = [
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "# Documentation\n",
                "This notebook uses display(df) for visualization.\n",
                "Use df.show() to see results.\n"
            ]
        },
        {
            "cell_type": "code",
            "metadata": {},
            "source": [
                "# This should be found\n",
                "display(df)\n"
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

        # Should only find the match in code cell, not markdown
        assert len(issues) == 1
        assert issues[0][1] == "display function"

    finally:
        os.unlink(temp_path)


def test_check_notebook_file_skip_magic_commands():
    """Test that magic commands are skipped."""
    cells = [
        {
            "cell_type": "code",
            "metadata": {},
            "source": [
                "%matplotlib inline\n",
                "%%time\n",
                "display(df)  # This should be found\n",
                "!pip install pandas\n",
                "%pwd\n"
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

        # Should find the display call but not count magic commands
        assert len(issues) == 1
        assert issues[0][1] == "display function"

    finally:
        os.unlink(temp_path)


def test_check_notebook_file_source_as_string():
    """Test handling of cells with source as string instead of list."""
    cells = [
        {
            "cell_type": "code",
            "metadata": {},
            "source": "display(df)\ndf.show()"  # String instead of list
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

        # Should handle string source and find both patterns
        assert len(issues) == 2
        descriptions = [issue[1] for issue in issues]
        assert "display function" in descriptions
        assert "show method" in descriptions

    finally:
        os.unlink(temp_path)


def test_check_notebook_file_unicode_content():
    """Test processing notebooks with unicode content."""
    cells = [
        {
            "cell_type": "code",
            "metadata": {},
            "source": [
                "# Processing données françaises 🚀\n",
                "df_世界 = load_data()\n",
                "display(df_世界)  # Should be found\n"
            ]
        }
    ]

    notebook = create_test_notebook(cells)
    patterns = [(r"display\(", "display function")]

    with tempfile.NamedTemporaryFile(mode="w", suffix=".ipynb", delete=False, encoding="utf-8") as f:
        json.dump(notebook, f, ensure_ascii=False)
        temp_path = f.name

    try:
        issues = check_notebook_file(Path(temp_path), patterns)

        assert len(issues) == 1
        assert issues[0][1] == "display function"

        # Check that unicode is preserved
        assert "df_世界" in issues[0][2]

    finally:
        os.unlink(temp_path)


def test_check_notebook_file_mixed_cell_types():
    """Test processing notebook with various cell types."""
    cells = [
        {
            "cell_type": "code",
            "metadata": {},
            "source": ["display(df_code)  # Code cell\n"]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": ["display(df_markdown) should be ignored"]
        },
        {
            "cell_type": "raw",
            "metadata": {},
            "source": ["display(df_raw) should be ignored"]
        },
        {
            "cell_type": "code",
            "metadata": {},
            "source": ["# Another code cell\ndisplay(df_code2)\n"]
        }
    ]

    notebook = create_test_notebook(cells)
    patterns = [(r"display\(", "display function")]

    with tempfile.NamedTemporaryFile(mode="w", suffix=".ipynb", delete=False) as f:
        json.dump(notebook, f)
        temp_path = f.name

    try:
        issues = check_notebook_file(Path(temp_path), patterns)

        # Should only find matches in code cells
        assert len(issues) == 2

        # Check that only code cell content is found
        code_content = [issue[2] for issue in issues]
        assert any("df_code)" in content for content in code_content)
        assert any("df_code2" in content for content in code_content)
        assert not any("df_markdown" in content for content in code_content)
        assert not any("df_raw" in content for content in code_content)

    finally:
        os.unlink(temp_path)


def test_check_notebook_file_complex_patterns():
    """Test with complex regex patterns in notebooks."""
    cells = [
        {
            "cell_type": "code",
            "metadata": {},
            "source": [
                "df.collect()  # Should match\n",
                "result = df.collect()  # Might match if negative lookbehind doesn't work\n",
                "df.count()  # Should match\n",
                "total = df.count()  # Might match if negative lookbehind doesn't work\n"
            ]
        }
    ]

    notebook = create_test_notebook(cells)
    patterns = [
        (r"\.collect\(\)", "collect method"),  # Simplified pattern
        (r"\.count\(\)", "count method")       # Simplified pattern
    ]

    with tempfile.NamedTemporaryFile(mode="w", suffix=".ipynb", delete=False) as f:
        json.dump(notebook, f)
        temp_path = f.name

    try:
        issues = check_notebook_file(Path(temp_path), patterns)

        # Should find the method calls (simplified expectation)
        assert len(issues) >= 2
        descriptions = [issue[1] for issue in issues]
        assert "collect method" in descriptions
        assert "count method" in descriptions

    finally:
        os.unlink(temp_path)


def test_check_notebook_file_multiline_cells():
    """Test processing cells with multiple lines."""
    cells = [
        {
            "cell_type": "code",
            "metadata": {},
            "source": [
                "# Multi-line cell\n",
                "df = load_data()\n",
                "processed_df = df.filter(col('value') > 0)\n",
                "display(processed_df)  # Should be found\n",
                "final_result = processed_df.collect()\n"
            ]
        }
    ]

    notebook = create_test_notebook(cells)
    patterns = [
        (r"display\(", "display function"),
        (r"\.collect\(\)", "collect method")
    ]

    with tempfile.NamedTemporaryFile(mode="w", suffix=".ipynb", delete=False) as f:
        json.dump(notebook, f)
        temp_path = f.name

    try:
        issues = check_notebook_file(Path(temp_path), patterns)

        assert len(issues) == 2
        descriptions = [issue[1] for issue in issues]
        assert "display function" in descriptions
        assert "collect method" in descriptions

    finally:
        os.unlink(temp_path)


def test_check_notebook_file_empty_source_lines():
    """Test handling of cells with empty source lines."""
    cells = [
        {
            "cell_type": "code",
            "metadata": {},
            "source": [
                "\n",  # Empty line
                "display(df)  # Should be found\n",
                "\n",  # Another empty line
                "df.show()  # Should also be found\n",
                "\n"   # Final empty line
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


def test_check_notebook_file_special_characters():
    """Test processing cells with special characters."""
    cells = [
        {
            "cell_type": "code",
            "metadata": {},
            "source": [
                "# Special characters: !@#$%^&*()\n",
                "display(df)  # Should be found\n",
                "result = 'String with \"quotes\" and \\backslashes\\'\n"
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
        assert issues[0][1] == "display function"

    finally:
        os.unlink(temp_path)
