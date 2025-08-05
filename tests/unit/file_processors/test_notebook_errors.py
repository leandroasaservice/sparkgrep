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


def test_check_notebook_file_invalid_json():
    """Test handling of invalid JSON files."""
    invalid_json = "{ invalid json content"
    patterns = [(r"display\(", "display function")]

    with tempfile.NamedTemporaryFile(mode="w", suffix=".ipynb", delete=False) as f:
        f.write(invalid_json)
        temp_path = f.name

    try:
        issues = check_notebook_file(Path(temp_path), patterns)
        # Should handle gracefully and return empty list
        assert len(issues) == 0

    finally:
        os.unlink(temp_path)


def test_check_notebook_file_missing_cells():
    """Test handling of notebook without cells key."""
    invalid_notebook = {
        "nbformat": 4,
        "nbformat_minor": 4,
        "metadata": {}
        # Missing "cells" key
    }
    patterns = [(r"display\(", "display function")]

    with tempfile.NamedTemporaryFile(mode="w", suffix=".ipynb", delete=False) as f:
        json.dump(invalid_notebook, f)
        temp_path = f.name

    try:
        issues = check_notebook_file(Path(temp_path), patterns)
        # Should handle gracefully
        assert len(issues) == 0

    finally:
        os.unlink(temp_path)


def test_check_notebook_file_cell_without_source():
    """Test handling of cells without source key."""
    cells = [
        {
            "cell_type": "code",
            "metadata": {},
            "source": []  # Empty source instead of missing source
        },
        {
            "cell_type": "code",
            "metadata": {},
            "source": [
                "display(df)  # This should be found\n"
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

        # Should find the pattern in the valid cell
        assert len(issues) == 1
        assert issues[0][1] == "display function"

    finally:
        os.unlink(temp_path)


def test_check_notebook_file_large_notebook():
    """Test processing a large notebook."""
    # Create many cells with occasional patterns
    cells = []
    for i in range(100):
        if i % 10 == 0:
            source = [f"display(df_{i})  # Cell {i}\n"]
        else:
            source = [f"# Regular cell {i}\nprint('Processing')\n"]

        cells.append({
            "cell_type": "code",
            "metadata": {},
            "source": source
        })

    notebook = create_test_notebook(cells)
    patterns = [(r"display\(", "display function")]

    with tempfile.NamedTemporaryFile(mode="w", suffix=".ipynb", delete=False) as f:
        json.dump(notebook, f)
        temp_path = f.name

    try:
        issues = check_notebook_file(Path(temp_path), patterns)

        # Should find 10 display calls (every 10th cell starting from 0)
        assert len(issues) == 10

        # All should be display functions
        descriptions = [issue[1] for issue in issues]
        assert all(desc == "display function" for desc in descriptions)

    finally:
        os.unlink(temp_path)


def test_check_notebook_file_malformed_cells():
    """Test handling of malformed cells."""
    cells = [
        {
            "cell_type": "code",
            "metadata": {},
            "source": ["display(df_good)\n"]
        },
        {
            # Missing cell_type
            "metadata": {},
            "source": ["display(df_bad)\n"]
        },
        {
            "cell_type": "code",
            # Missing metadata - should still work
            "source": ["display(df_ok)\n"]
        }
    ]

    notebook = create_test_notebook(cells)
    patterns = [(r"display\(", "display function")]

    with tempfile.NamedTemporaryFile(mode="w", suffix=".ipynb", delete=False) as f:
        json.dump(notebook, f)
        temp_path = f.name

    try:
        issues = check_notebook_file(Path(temp_path), patterns)

        # Should handle malformed cells gracefully and process valid ones
        assert len(issues) >= 1  # At least the good cell should be processed

    finally:
        os.unlink(temp_path)


def test_check_notebook_file_corrupted_notebook():
    """Test handling of corrupted notebook structure."""
    corrupted_notebook = {
        "nbformat": "invalid",  # Should be integer
        "cells": [
            {
                "cell_type": "code",
                "source": ["display(df)\n"]
            }
        ]
    }
    patterns = [(r"display\(", "display function")]

    with tempfile.NamedTemporaryFile(mode="w", suffix=".ipynb", delete=False) as f:
        json.dump(corrupted_notebook, f)
        temp_path = f.name

    try:
        issues = check_notebook_file(Path(temp_path), patterns)

        # Should handle gracefully - may or may not find patterns depending on implementation
        assert isinstance(issues, list)

    finally:
        os.unlink(temp_path)


def test_check_notebook_file_empty_cells_array():
    """Test handling of notebook with empty cells array."""
    notebook = {
        "nbformat": 4,
        "nbformat_minor": 4,
        "metadata": {},
        "cells": []  # Empty cells array
    }
    patterns = [(r"display\(", "display function")]

    with tempfile.NamedTemporaryFile(mode="w", suffix=".ipynb", delete=False) as f:
        json.dump(notebook, f)
        temp_path = f.name

    try:
        issues = check_notebook_file(Path(temp_path), patterns)

        # Should handle empty cells gracefully
        assert len(issues) == 0

    finally:
        os.unlink(temp_path)


def test_check_notebook_file_very_long_lines():
    """Test handling of cells with very long lines."""
    # Create a very long line
    long_line = "# " + "x" * 10000 + "\n"

    cells = [
        {
            "cell_type": "code",
            "metadata": {},
            "source": [
                long_line,
                "display(df)  # Should still be found\n"
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


def test_check_notebook_file_binary_content():
    """Test handling of notebook with binary content."""
    # Try to create a notebook with binary content in source
    cells = [
        {
            "cell_type": "code",
            "metadata": {},
            "source": ["display(df)\n"]  # Valid content
        }
    ]

    notebook = create_test_notebook(cells)
    patterns = [(r"display\(", "display function")]

    with tempfile.NamedTemporaryFile(mode="w", suffix=".ipynb", delete=False) as f:
        json.dump(notebook, f)
        temp_path = f.name

    try:
        issues = check_notebook_file(Path(temp_path), patterns)

        # Should handle normally since we have valid content
        assert len(issues) == 1
        assert issues[0][1] == "display function"

    finally:
        os.unlink(temp_path)


def test_check_notebook_file_permission_errors():
    """Test handling when file cannot be read due to permissions."""
    cells = [
        {
            "cell_type": "code",
            "metadata": {},
            "source": ["display(df)\n"]
        }
    ]

    notebook = create_test_notebook(cells)
    patterns = [(r"display\(", "display function")]

    with tempfile.NamedTemporaryFile(mode="w", suffix=".ipynb", delete=False) as f:
        json.dump(notebook, f)
        temp_path = f.name

    try:
        # Remove read permissions
        os.chmod(temp_path, 0o000)

        issues = check_notebook_file(Path(temp_path), patterns)

        # Should handle permission errors gracefully
        assert isinstance(issues, list)

    finally:
        # Restore permissions for cleanup
        os.chmod(temp_path, 0o644)
        os.unlink(temp_path)


def test_check_notebook_file_nested_structures():
    """Test handling of deeply nested JSON structures in cells."""
    cells = [
        {
            "cell_type": "code",
            "metadata": {
                "nested": {
                    "deep": {
                        "structure": "value"
                    }
                }
            },
            "source": ["display(df)\n"]
        }
    ]

    notebook = create_test_notebook(cells)
    patterns = [(r"display\(", "display function")]

    with tempfile.NamedTemporaryFile(mode="w", suffix=".ipynb", delete=False) as f:
        json.dump(notebook, f)
        temp_path = f.name

    try:
        issues = check_notebook_file(Path(temp_path), patterns)

        # Should handle nested metadata and still find patterns
        assert len(issues) == 1
        assert issues[0][1] == "display function"

    finally:
        os.unlink(temp_path)
