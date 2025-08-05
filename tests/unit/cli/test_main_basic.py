import pytest
import tempfile
import os
import json
from unittest.mock import patch

from sparkgrep.cli import main


def test_main_success_no_issues():
    """Test main function with files that have no issues."""
    python_code = """
def clean_function():
    data = [1, 2, 3, 4, 5]
    result = sum(data)
    return result
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(python_code)
        temp_path = f.name

    try:
        test_argv = ["sparkgrep", temp_path]

        with patch("sys.argv", test_argv):
            result = main()

        assert result == 0  # Success exit code

    finally:
        os.unlink(temp_path)


def test_main_success_with_issues():
    """Test main function with files that have issues."""
    python_code = """
def problematic_function():
    df = load_data()
    display(df)  # Issue: display function
    df.show()    # Issue: show method
    return df
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(python_code)
        temp_path = f.name

    try:
        test_argv = ["sparkgrep", temp_path]

        with patch("sys.argv", test_argv):
            result = main()

        assert result == 1  # Failure exit code (issues found)

    finally:
        os.unlink(temp_path)


def test_main_multiple_files():
    """Test main function with multiple files."""
    # File with issues
    problematic_code = """
display(df1)
df1.show()
"""

    # File without issues
    clean_code = """
def clean_function():
    return sum([1, 2, 3])
"""

    files = []
    try:
        # Create problematic file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(problematic_code)
            files.append(f.name)

        # Create clean file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(clean_code)
            files.append(f.name)

        test_argv = ["sparkgrep"] + files

        with patch("sys.argv", test_argv):
            result = main()

        assert result == 1  # Should return 1 because issues were found

    finally:
        for file_path in files:
            os.unlink(file_path)


def test_main_with_notebook():
    """Test main function with notebook files."""
    notebook = {
        "nbformat": 4,
        "nbformat_minor": 4,
        "metadata": {},
        "cells": [
            {
                "cell_type": "code",
                "metadata": {},
                "source": [
                    "display(df)  # Issue in notebook\n",
                    "df.show()    # Another issue\n"
                ]
            }
        ]
    }

    with tempfile.NamedTemporaryFile(mode="w", suffix=".ipynb", delete=False) as f:
        json.dump(notebook, f)
        temp_path = f.name

    try:
        test_argv = ["sparkgrep", temp_path]

        with patch("sys.argv", test_argv):
            result = main()

        assert result == 1  # Issues found

    finally:
        os.unlink(temp_path)


def test_main_no_files_provided():
    """Test main function when no files are provided."""
    test_argv = ["sparkgrep"]

    with patch("sys.argv", test_argv):
        result = main()

    assert result == 0  # Should succeed (no files to process)


def test_main_nonexistent_files():
    """Test main function with nonexistent files."""
    test_argv = ["sparkgrep", "nonexistent1.py", "nonexistent2.ipynb"]

    with patch("sys.argv", test_argv):
        result = main()

    assert result == 0  # Should succeed (no files processed)


def test_main_return_values():
    """Test that main function returns correct exit codes."""
    # Test success case
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write("# Clean file")
        clean_file = f.name

    # Test failure case
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write("display(df)")
        problematic_file = f.name

    try:
        # Test clean file
        with patch("sys.argv", ["sparkgrep", clean_file]):
            result = main()
            assert result == 0

        # Test problematic file
        with patch("sys.argv", ["sparkgrep", problematic_file]):
            result = main()
            assert result == 1

    finally:
        os.unlink(clean_file)
        os.unlink(problematic_file)


def test_main_output_format():
    """Test that main function produces expected output format."""
    python_code = """
display(df)  # Line 2
df.show()    # Line 3
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(python_code)
        temp_path = f.name

    try:
        test_argv = ["sparkgrep", temp_path]

        with patch("sys.argv", test_argv):
            # Capture stdout to verify output format
            import io
            import contextlib

            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                result = main()

            output_text = output.getvalue()

            # Should contain filename and line information
            assert temp_path in output_text
            assert "Line" in output_text
            assert result == 1

    finally:
        os.unlink(temp_path)


def test_main_empty_files():
    """Test main function with empty files."""
    files = []
    try:
        # Create empty Python file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            files.append(f.name)

        # Create empty notebook
        empty_notebook = {
            "nbformat": 4,
            "nbformat_minor": 4,
            "metadata": {},
            "cells": []
        }
        with tempfile.NamedTemporaryFile(mode="w", suffix=".ipynb", delete=False) as f:
            json.dump(empty_notebook, f)
            files.append(f.name)

        test_argv = ["sparkgrep"] + files

        with patch("sys.argv", test_argv):
            result = main()

        assert result == 0  # Should succeed (no content to analyze)

    finally:
        for file_path in files:
            os.unlink(file_path)
