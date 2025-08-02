"""
Integration tests for error handling scenarios.
"""

import pytest
import tempfile
import os
from unittest.mock import patch

from sparkgrep.cli import main


def test_nonexistent_file_handling():
    """Test handling of nonexistent files."""
    test_argv = ["check-spark-actions", "nonexistent.py"]

    with patch("sys.argv", test_argv):
        result = main()
        assert result == 0  # Should succeed (no files processed)


def test_mixed_existent_nonexistent_files():
    """Test handling of mix of existent and nonexistent files."""
    python_code = """
def test_function():
    display(df)
    print("hello")
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(python_code)
        temp_path = f.name

    try:
        test_argv = ["check-spark-actions", temp_path, "nonexistent.py"]

        with patch("sys.argv", test_argv):
            result = main()
            assert result == 1  # Should fail due to issues in existing file

    finally:
        os.unlink(temp_path)


def test_empty_files_handling():
    """Test handling of empty files."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write("")  # Empty file
        temp_path = f.name

    try:
        test_argv = ["check-spark-actions", temp_path]

        with patch("sys.argv", test_argv):
            result = main()
            assert result == 0  # Should succeed (no issues in empty file)

    finally:
        os.unlink(temp_path)


def test_invalid_notebook_handling():
    """Test handling of invalid notebook files."""
    # Create invalid notebook
    invalid_notebook = "This is not valid JSON"

    with tempfile.NamedTemporaryFile(mode="w", suffix=".ipynb", delete=False) as f:
        f.write(invalid_notebook)
        temp_path = f.name

    try:
        test_argv = ["check-spark-actions", temp_path]

        with patch("sys.argv", test_argv):
            result = main()
            assert result == 0  # Should succeed (no files processed due to error)

    finally:
        os.unlink(temp_path)
