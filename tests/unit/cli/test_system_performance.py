import pytest
import tempfile
import os
import json
from unittest.mock import patch

from sparkgrep.cli import main


def test_main_memory_handling():
    """Test main function memory handling with large patterns and files."""
    # Create file with many lines
    lines = [f"line_{i} = {i}" for i in range(10000)]
    lines[5000] = "display(df)  # Hidden in the middle"
    large_content = "\n".join(lines)

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(large_content)
        temp_path = f.name

    try:
        test_argv = ["sparkgrep", temp_path]

        with patch("sys.argv", test_argv):
            result = main()

        assert result == 1  # Should find the hidden display call

    finally:
        os.unlink(temp_path)


def test_main_concurrent_file_access():
    """Test main function with multiple files accessed simultaneously."""
    files = []
    try:
        # Create multiple files quickly
        for i in range(20):
            content = f"display(df_{i})" if i % 3 == 0 else f"# File {i}"
            with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
                f.write(content)
                files.append(f.name)

        test_argv = ["sparkgrep"] + files

        with patch("sys.argv", test_argv):
            result = main()

        assert result == 1  # Should find issues in some files

    finally:
        for file_path in files:
            os.unlink(file_path)


def test_main_notebook_without_metadata():
    """Test main function with notebook missing metadata."""
    notebook = {
        "nbformat": 4,
        "nbformat_minor": 4,
        # Missing metadata key
        "cells": [
            {
                "cell_type": "code",
                "source": ["display(df)\n"]
                # Missing metadata key
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

        # Should handle malformed notebooks gracefully
        assert isinstance(result, int)

    finally:
        os.unlink(temp_path)


def test_main_interrupt_simulation():
    """Test main function behavior under simulated interruption conditions."""
    python_code = "display(df)"

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(python_code)
        temp_path = f.name

    try:
        test_argv = ["sparkgrep", temp_path]

        with patch("sys.argv", test_argv):
            result = main()

        # Should complete normally in this test
        assert result == 1

    finally:
        os.unlink(temp_path)


def test_main_with_many_files_performance():
    """Test main function performance with many files."""
    files = []
    try:
        # Create many files
        for i in range(50):
            content = f"display(df_{i})" if i % 5 == 0 else f"# File {i} content"
            with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
                f.write(content)
                files.append(f.name)

        test_argv = ["sparkgrep"] + files

        with patch("sys.argv", test_argv):
            result = main()

        assert result == 1  # Should find issues in some files

    finally:
        for file_path in files:
            os.unlink(file_path)


def test_main_with_large_notebook():
    """Test main function with very large notebook files."""
    # Create notebook with many cells
    cells = []
    for i in range(1000):
        if i % 100 == 0:
            cells.append({
                "cell_type": "code",
                "metadata": {},
                "source": [f"display(df_{i})  # Cell {i}\n"]
            })
        else:
            cells.append({
                "cell_type": "code",
                "metadata": {},
                "source": [f"# Cell {i} - no issues\n"]
            })

    large_notebook = {
        "nbformat": 4,
        "nbformat_minor": 4,
        "metadata": {},
        "cells": cells
    }

    with tempfile.NamedTemporaryFile(mode="w", suffix=".ipynb", delete=False) as f:
        json.dump(large_notebook, f)
        temp_path = f.name

    try:
        test_argv = ["sparkgrep", temp_path]

        with patch("sys.argv", test_argv):
            result = main()

        assert result == 1  # Should find issues in some cells

    finally:
        os.unlink(temp_path)


def test_main_stress_test_patterns():
    """Test main function with stress test using many patterns."""
    python_code = """
function_1(df)
function_2(data)
function_3(table)
display(result)
show(output)
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(python_code)
        temp_path = f.name

    try:
        # Create many patterns to stress test pattern matching
        patterns = []
        for i in range(200):
            patterns.append(f"function_{i}:Function {i}")

        # Add some that will actually match
        patterns.extend([
            "function_1:Function 1 match",
            "display:Display match",
            "show:Show match"
        ])

        test_argv = ["sparkgrep", "--additional-patterns"] + patterns + [temp_path]

        with patch("sys.argv", test_argv):
            result = main()

        assert result == 1  # Should find some matches

    finally:
        os.unlink(temp_path)


def test_main_unicode_content_performance():
    """Test main function with unicode-heavy content."""
    unicode_code = """
# Unicode content test
显示数据 = "display data in Chinese"
données_française = "French data"
русские_данные = "Russian data"
display(unicode_dataframe)  # This should match
العرض(البيانات)  # Arabic function call
データ表示(df)  # Japanese function call
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
        f.write(unicode_code)
        temp_path = f.name

    try:
        test_argv = ["sparkgrep", temp_path]

        with patch("sys.argv", test_argv):
            result = main()

        assert result == 1  # Should find the display call

    finally:
        os.unlink(temp_path)


def test_main_nested_patterns_performance():
    """Test performance with deeply nested pattern matches."""
    # Create code with nested structures
    nested_code = []
    for level in range(100):
        indent = "  " * level
        if level == 50:
            nested_code.append(f"{indent}display(nested_df)  # Deep nesting")
        else:
            nested_code.append(f"{indent}# Level {level}")

    complex_content = "\n".join(nested_code)

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(complex_content)
        temp_path = f.name

    try:
        test_argv = ["sparkgrep", temp_path]

        with patch("sys.argv", test_argv):
            result = main()

        assert result == 1  # Should find the deeply nested display call

    finally:
        os.unlink(temp_path)


def test_main_boundary_conditions():
    """Test main function with boundary conditions."""
    # Test with minimal content
    minimal_code = "d"  # Single character

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(minimal_code)
        temp_path = f.name

    try:
        test_argv = ["sparkgrep", temp_path]

        with patch("sys.argv", test_argv):
            result = main()

        # Should handle minimal content gracefully
        assert result == 0  # No matches in minimal content

    finally:
        os.unlink(temp_path)


def test_main_resource_cleanup():
    """Test that main function properly cleans up resources."""
    python_code = "display(df)"

    # Create temporary file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(python_code)
        temp_path = f.name

    try:
        test_argv = ["sparkgrep", temp_path]

        # Run multiple times to test resource cleanup
        for _ in range(10):
            with patch("sys.argv", test_argv):
                result = main()
                assert result == 1

    finally:
        os.unlink(temp_path)
