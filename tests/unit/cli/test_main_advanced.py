import pytest
import tempfile
import os
from unittest.mock import patch

from sparkgrep.cli import main


def test_main_mixed_existent_nonexistent():
    """Test main function with mix of existent and nonexistent files."""
    python_code = "display(df)"

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(python_code)
        temp_path = f.name

    try:
        test_argv = ["sparkgrep", temp_path, "nonexistent.py"]

        with patch("sys.argv", test_argv):
            result = main()

        assert result == 1  # Should find issues in the existing file

    finally:
        os.unlink(temp_path)


def test_main_unsupported_file_types():
    """Test main function with unsupported file types."""
    content = "display(df); df.show();"

    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write(content)
        temp_path = f.name

    try:
        test_argv = ["sparkgrep", temp_path]

        with patch("sys.argv", test_argv):
            result = main()

        assert result == 0  # Should succeed (file type not supported)

    finally:
        os.unlink(temp_path)


def test_main_large_number_of_files():
    """Test main function with many files."""
    files = []
    try:
        # Create multiple files, some with issues, some without
        for i in range(10):
            if i % 2 == 0:
                code = f"display(df_{i})  # Issue in file {i}"
            else:
                code = f"# Clean file {i}\nprint('No issues here')"

            with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
                f.write(code)
                files.append(f.name)

        test_argv = ["sparkgrep"] + files

        with patch("sys.argv", test_argv):
            result = main()

        assert result == 1  # Should find issues in even-numbered files

    finally:
        for file_path in files:
            os.unlink(file_path)


def test_main_unicode_content():
    """Test main function with unicode content."""
    python_code = """
# -*- coding: utf-8 -*-
# Processing données françaises 🚀
df_世界 = load_data()
display(df_世界)  # Should be found
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
        f.write(python_code)
        temp_path = f.name

    try:
        test_argv = ["sparkgrep", temp_path]

        with patch("sys.argv", test_argv):
            result = main()

        assert result == 1  # Should find the display call

    finally:
        os.unlink(temp_path)


def test_main_very_large_single_file():
    """Test main function with a very large single file."""
    # Create a large file with many lines
    lines = []
    for i in range(5000):
        if i == 2500:  # Put issue in the middle
            lines.append("display(large_dataframe)  # Issue in large file")
        else:
            lines.append(f"# Line {i} - no issues here")

    large_content = "\n".join(lines)

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(large_content)
        temp_path = f.name

    try:
        test_argv = ["sparkgrep", temp_path]

        with patch("sys.argv", test_argv):
            result = main()

        assert result == 1  # Should find the issue even in large file

    finally:
        os.unlink(temp_path)


def test_main_mixed_file_types():
    """Test main function with mix of Python and notebook files."""
    files = []
    try:
        # Create Python file with issues
        python_code = "display(python_df)"
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(python_code)
            files.append(f.name)

        # Create notebook with issues
        notebook = {
            "nbformat": 4,
            "nbformat_minor": 4,
            "metadata": {},
            "cells": [
                {
                    "cell_type": "code",
                    "metadata": {},
                    "source": ["display(notebook_df)\n"]
                }
            ]
        }
        import json
        with tempfile.NamedTemporaryFile(mode="w", suffix=".ipynb", delete=False) as f:
            json.dump(notebook, f)
            files.append(f.name)

        test_argv = ["sparkgrep"] + files

        with patch("sys.argv", test_argv):
            result = main()

        assert result == 1  # Should find issues in both file types

    finally:
        for file_path in files:
            os.unlink(file_path)


def test_main_deeply_nested_code_structures():
    """Test main function with deeply nested code structures."""
    nested_code = """
def level1():
    def level2():
        def level3():
            def level4():
                def level5():
                    display(deeply_nested_df)  # Deep issue
                    return "deep"
                return level5()
            return level4()
        return level3()
    return level2()
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(nested_code)
        temp_path = f.name

    try:
        test_argv = ["sparkgrep", temp_path]

        with patch("sys.argv", test_argv):
            result = main()

        assert result == 1  # Should find issues in nested code

    finally:
        os.unlink(temp_path)


def test_main_multiline_statements():
    """Test main function with multiline statements."""
    multiline_code = '''
result = df.select(
    "column1",
    "column2"
).filter(
    col("column1") > 0
).display()  # This should be caught

df.show(
    20,
    truncate=False
)  # This should also be caught
'''

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(multiline_code)
        temp_path = f.name

    try:
        test_argv = ["sparkgrep", temp_path]

        with patch("sys.argv", test_argv):
            result = main()

        assert result == 1  # Should find issues in multiline statements

    finally:
        os.unlink(temp_path)


def test_main_with_string_literals():
    """Test main function ignores patterns in string literals."""
    code_with_strings = '''
# This should not trigger
comment = "This is a display(df) call in a string"
sql_query = """
    SELECT * FROM table
    WHERE display(column) > 0  -- This is in SQL string
"""

# But this should trigger
actual_display = display(real_df)  # Real function call
'''

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(code_with_strings)
        temp_path = f.name

    try:
        test_argv = ["sparkgrep", temp_path]

        with patch("sys.argv", test_argv):
            result = main()

        assert result == 1  # Should find only the real function call

    finally:
        os.unlink(temp_path)


def test_main_performance_stress_test():
    """Test main function performance with many patterns and files."""
    files = []
    try:
        # Create multiple files with various patterns
        for i in range(20):
            if i % 3 == 0:
                code = f"display(df_{i})\ndf_{i}.show()\ncollect_{i}()"
            elif i % 3 == 1:
                code = f"# File {i} with comments only\n# No issues here"
            else:
                code = f"def function_{i}():\n    return {i}"

            with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
                f.write(code)
                files.append(f.name)

        test_argv = ["sparkgrep"] + files

        with patch("sys.argv", test_argv):
            result = main()

        assert result == 1  # Should find issues in some files

    finally:
        for file_path in files:
            os.unlink(file_path)
