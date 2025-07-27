"""
Unit tests for the file_processors module.
"""

import pytest
from pathlib import Path
from unittest.mock import patch, mock_open, MagicMock
import tempfile
import os
import json

from src.file_processors import (
    check_python_file,
    check_notebook_file,
    process_single_file,
    _read_notebook_safely,
    _process_notebook_cell,
)


class TestCheckPythonFile:
    """Test the check_python_file function."""

    def test_check_python_file_with_matches(self):
        """Test checking Python file with pattern matches."""
        patterns = [
            (r"display\s*\(", "display function"),
            (r"\.show\s*\(", "show method"),
        ]

        python_code = """
def test_function():
    display(df)  # This should match
    result = df.show()  # This should match
    print("hello")  # This should not match
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(python_code)
            temp_path = f.name

        try:
            issues = check_python_file(Path(temp_path), patterns)

            assert len(issues) == 2
            assert any(issue[1] == "display function" for issue in issues)
            assert any(issue[1] == "show method" for issue in issues)

            # Check line numbers
            display_issue = next(
                issue for issue in issues if issue[1] == "display function"
            )
            show_issue = next(issue for issue in issues if issue[1] == "show method")

            assert display_issue[0] == 3  # Line number
            assert show_issue[0] == 4  # Line number
        finally:
            os.unlink(temp_path)

    def test_check_python_file_no_matches(self):
        """Test checking Python file with no pattern matches."""
        patterns = [(r"display\s*\(", "display function")]

        python_code = """
def test_function():
    print("hello")
    result = df.collect()
    return result
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(python_code)
            temp_path = f.name

        try:
            issues = check_python_file(Path(temp_path), patterns)
            assert len(issues) == 0
        finally:
            os.unlink(temp_path)

    def test_check_python_file_skip_comments(self):
        """Test that comments are skipped."""
        patterns = [(r"display\s*\(", "display function")]

        python_code = """
def test_function():
    # display(df)  # This should be skipped
    # TODO: Add display(df) later
    print("hello")
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(python_code)
            temp_path = f.name

        try:
            issues = check_python_file(Path(temp_path), patterns)
            assert len(issues) == 0
        finally:
            os.unlink(temp_path)

    def test_check_python_file_skip_docstrings(self):
        """Test that docstrings are skipped."""
        patterns = [(r"display\s*\(", "display function")]

        python_code = '''
def test_function():
    """
    This function demonstrates display(df) usage
    but this should be skipped
    """
    actual_display(df)  # This should NOT match our pattern
'''

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(python_code)
            temp_path = f.name

        try:
            issues = check_python_file(Path(temp_path), patterns)
            assert len(issues) == 0
        finally:
            os.unlink(temp_path)

    def test_check_python_file_single_quote_docstring(self):
        """Test handling of single quote docstrings."""
        patterns = [(r"display\s*\(", "display function")]

        python_code = """
def test_function():
    '''
    This function demonstrates display(df) usage
    but this should be skipped
    '''
    print("hello")
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(python_code)
            temp_path = f.name

        try:
            issues = check_python_file(Path(temp_path), patterns)
            assert len(issues) == 0
        finally:
            os.unlink(temp_path)

    def test_check_python_file_nonexistent(self):
        """Test checking nonexistent Python file."""
        patterns = [(r"display\s*\(", "display function")]

        issues = check_python_file(Path("nonexistent.py"), patterns)
        assert len(issues) == 0

    def test_check_python_file_empty_patterns(self):
        """Test checking Python file with empty patterns."""
        python_code = """
def test_function():
    display(df)
    df.show()
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(python_code)
            temp_path = f.name

        try:
            issues = check_python_file(Path(temp_path), [])
            assert len(issues) == 0
        finally:
            os.unlink(temp_path)


class TestReadNotebookSafely:
    """Test the _read_notebook_safely function."""

    def test_read_notebook_success(self):
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

    def test_read_notebook_missing_nbformat(self, capsys):
        """Test reading notebook when nbformat is not available."""
        # Mock the import to raise ImportError
        import sys

        original_modules = sys.modules.copy()

        try:
            # Remove nbformat from sys.modules if it exists
            if "nbformat" in sys.modules:
                del sys.modules["nbformat"]

            # Mock the import to raise ImportError
            from unittest.mock import patch

            with patch.dict("sys.modules", {"nbformat": None}):
                # Reimport the function to get the patched version
                from src.file_processors import _read_notebook_safely

                # This should trigger the ImportError path
                with patch(
                    "scripts.file_processors.nbformat",
                    side_effect=ImportError("No module named 'nbformat'"),
                ):
                    result = _read_notebook_safely(Path("test.ipynb"))

                    assert result is None
                    captured = capsys.readouterr()
                    assert "nbformat not installed" in captured.out

        finally:
            # Restore original modules
            sys.modules.clear()
            sys.modules.update(original_modules)

    def test_read_notebook_file_error(self, capsys):
        """Test reading notebook with file error."""
        result = _read_notebook_safely(Path("nonexistent.ipynb"))

        assert result is None
        captured = capsys.readouterr()
        assert "Could not read notebook" in captured.out

    def test_read_notebook_parse_error(self, capsys):
        """Test reading notebook with parse error."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".ipynb", delete=False) as f:
            f.write("invalid json content")
            temp_path = f.name

        try:
            result = _read_notebook_safely(Path(temp_path))

            assert result is None
            captured = capsys.readouterr()
            assert "Could not read notebook" in captured.out
        finally:
            os.unlink(temp_path)


class TestProcessNotebookCell:
    """Test the _process_notebook_cell function."""

    def test_process_code_cell_with_matches(self):
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

    def test_process_code_cell_no_matches(self):
        """Test processing code cell with no pattern matches."""
        patterns = [(r"display\s*\(", "display function")]

        cell = MagicMock()
        cell.cell_type = "code"
        cell.source = 'print("hello")\nresult = df.collect()'

        issues = _process_notebook_cell(cell, 0, patterns)

        assert len(issues) == 0

    def test_process_markdown_cell(self):
        """Test processing markdown cell (should be skipped)."""
        patterns = [(r"display\s*\(", "display function")]

        cell = MagicMock()
        cell.cell_type = "markdown"
        cell.source = "display(df)"

        issues = _process_notebook_cell(cell, 0, patterns)

        assert len(issues) == 0

    def test_process_code_cell_skip_comments(self):
        """Test processing code cell skipping comments."""
        patterns = [(r"display\s*\(", "display function")]

        cell = MagicMock()
        cell.cell_type = "code"
        cell.source = '# display(df)\nprint("hello")'

        issues = _process_notebook_cell(cell, 0, patterns)

        assert len(issues) == 0

    def test_process_code_cell_skip_magic_commands(self):
        """Test processing code cell skipping magic commands."""
        patterns = [(r"display\s*\(", "display function")]

        cell = MagicMock()
        cell.cell_type = "code"
        cell.source = "%matplotlib inline\n%%sql\nSELECT * FROM table"

        issues = _process_notebook_cell(cell, 0, patterns)

        assert len(issues) == 0

    def test_process_code_cell_empty_source(self):
        """Test processing code cell with empty source."""
        patterns = [(r"display\s*\(", "display function")]

        cell = MagicMock()
        cell.cell_type = "code"
        cell.source = ""

        issues = _process_notebook_cell(cell, 0, patterns)

        assert len(issues) == 0

    def test_process_code_cell_multiline_patterns(self):
        """Test processing code cell with multiline patterns."""
        patterns = [(r"df\.collect\s*\(\s*\)", "collect method")]

        cell = MagicMock()
        cell.cell_type = "code"
        cell.source = 'df.collect()\nresult = df.collect(   )\nprint("hello")'

        issues = _process_notebook_cell(cell, 0, patterns)

        assert len(issues) == 2
        assert ("Cell 1, Line 1", "collect method", "df.collect()") in issues
        assert (
            "Cell 1, Line 2",
            "collect method",
            "result = df.collect(   )",
        ) in issues


class TestCheckNotebookFile:
    """Test the check_notebook_file function."""

    def test_check_notebook_file_with_matches(self):
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

    def test_check_notebook_file_no_matches(self):
        """Test checking notebook file with no pattern matches."""
        patterns = [(r"display\s*\(", "display function")]

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
            issues = check_notebook_file(Path(temp_path), patterns)
            assert len(issues) == 0
        finally:
            os.unlink(temp_path)

    def test_check_notebook_file_read_error(self):
        """Test checking notebook file with read error."""
        patterns = [(r"display\s*\(", "display function")]

        issues = check_notebook_file(Path("nonexistent.ipynb"), patterns)
        assert len(issues) == 0

    def test_check_notebook_file_empty_notebook(self):
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


class TestProcessSingleFile:
    """Test the process_single_file function."""

    def test_process_python_file(self):
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

    def test_process_notebook_file(self):
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

    def test_process_unsupported_file_type(self):
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

    def test_process_nonexistent_file(self):
        """Test processing nonexistent file."""
        patterns = [(r"display\s*\(", "display function")]

        issues = process_single_file("nonexistent.py", patterns)
        assert len(issues) == 0

    def test_process_file_empty_patterns(self):
        """Test processing file with empty patterns."""
        python_code = """
def test_function():
    display(df)
    df.show()
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(python_code)
            temp_path = f.name

        try:
            issues = process_single_file(temp_path, [])
            assert len(issues) == 0
        finally:
            os.unlink(temp_path)

    def test_process_file_path_handling(self):
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
