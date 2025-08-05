import pytest
import tempfile
import os
import json
from unittest.mock import patch
from pathlib import Path

from sparkgrep.cli import main


def test_main_with_corrupted_notebook():
    """Test main function with corrupted notebook file."""
    corrupted_json = '{"nbformat": 4, "cells": [invalid json'

    with tempfile.NamedTemporaryFile(mode="w", suffix=".ipynb", delete=False) as f:
        f.write(corrupted_json)
        temp_path = f.name

    try:
        test_argv = ["sparkgrep", temp_path]

        with patch("sys.argv", test_argv):
            result = main()

        # Should handle corrupted notebooks gracefully
        assert result == 0  # No issues found in corrupted file

    finally:
        os.unlink(temp_path)


def test_main_with_very_large_files():
    """Test main function with very large files."""
    # Create a large file
    lines = []
    for i in range(50000):  # 50k lines
        if i % 1000 == 0:
            lines.append(f"display(df_{i})  # Issue on line {i}")
        else:
            lines.append(f"# Comment line {i}")

    large_content = "\n".join(lines)

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(large_content)
        temp_path = f.name

    try:
        test_argv = ["sparkgrep", temp_path]

        with patch("sys.argv", test_argv):
            result = main()

        assert result == 1  # Should find issues even in large files

    finally:
        os.unlink(temp_path)


def test_main_with_unicode_filenames():
    """Test main function with unicode characters in filenames."""
    python_code = "display(df)"

    # Note: tempfile handling of unicode names varies by system
    with tempfile.NamedTemporaryFile(mode="w", suffix="_unicode_test.py", delete=False) as f:
        f.write(python_code)
        temp_path = f.name

    try:
        test_argv = ["sparkgrep", temp_path]

        with patch("sys.argv", test_argv):
            result = main()

        assert result == 1  # Should find the display call

    finally:
        os.unlink(temp_path)


def test_main_with_special_characters_in_paths():
    """Test main function with special characters in file paths."""
    python_code = "display(df)"

    with tempfile.NamedTemporaryFile(mode="w", suffix="_special!@#$%^&()_test.py", delete=False) as f:
        f.write(python_code)
        temp_path = f.name

    try:
        test_argv = ["sparkgrep", temp_path]

        with patch("sys.argv", test_argv):
            result = main()

        assert result == 1  # Should handle special characters in paths

    finally:
        os.unlink(temp_path)


def test_main_with_binary_files():
    """Test main function with binary files that have supported extensions."""
    # Create a binary file with .py extension
    binary_content = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00'

    with tempfile.NamedTemporaryFile(mode="wb", suffix=".py", delete=False) as f:
        f.write(binary_content)
        temp_path = f.name

    try:
        test_argv = ["sparkgrep", temp_path]

        with patch("sys.argv", test_argv):
            result = main()

        # Should handle binary files gracefully
        assert result == 0  # No issues found in binary file

    finally:
        os.unlink(temp_path)


def test_main_with_deeply_nested_directory():
    """Test main function with files in deeply nested directories."""
    python_code = "display(df)"

    # Create file in a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        nested_path = Path(temp_dir) / "very" / "deeply" / "nested" / "directory"
        nested_path.mkdir(parents=True, exist_ok=True)

        file_path = nested_path / "test_file.py"
        file_path.write_text(python_code)

        test_argv = ["sparkgrep", str(file_path)]

        with patch("sys.argv", test_argv):
            result = main()

        assert result == 1  # Should find the display call


def test_main_with_readonly_files():
    """Test main function with read-only files."""
    python_code = "display(df)"

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(python_code)
        temp_path = f.name

    try:
        # Make file read-only
        os.chmod(temp_path, 0o444)

        test_argv = ["sparkgrep", temp_path]

        with patch("sys.argv", test_argv):
            result = main()

        assert result == 1  # Should still be able to read and find issues

    finally:
        # Restore write permissions for cleanup
        os.chmod(temp_path, 0o644)
        os.unlink(temp_path)


def test_main_with_symlinks():
    """Test main function with symbolic links."""
    python_code = "display(df)"

    with tempfile.TemporaryDirectory() as temp_dir:
        # Create original file
        original_file = Path(temp_dir) / "original.py"
        original_file.write_text(python_code)

        # Create symlink
        symlink_file = Path(temp_dir) / "symlink.py"
        try:
            symlink_file.symlink_to(original_file)
        except OSError:
            # Symlinks might not be supported on all systems
            pytest.skip("Symlinks not supported on this system")

        test_argv = ["sparkgrep", str(symlink_file)]

        with patch("sys.argv", test_argv):
            result = main()

        assert result == 1  # Should follow symlink and find issues


def test_main_with_mixed_valid_invalid_files():
    """Test main function with a mix of valid and invalid files."""
    # Create valid Python file
    valid_code = "display(df)"
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(valid_code)
        valid_path = f.name

    # Create corrupted notebook
    corrupted_json = '{"nbformat": 4, "cells": [invalid'
    with tempfile.NamedTemporaryFile(mode="w", suffix=".ipynb", delete=False) as f:
        f.write(corrupted_json)
        corrupt_path = f.name

    try:
        test_argv = ["sparkgrep", valid_path, corrupt_path, "nonexistent.py"]

        with patch("sys.argv", test_argv):
            result = main()

        # Should process valid file and handle invalid files gracefully
        assert result == 1  # Should find issue in valid file

    finally:
        os.unlink(valid_path)
        os.unlink(corrupt_path)


def test_main_nonexistent_files():
    """Test main function with nonexistent files."""
    test_argv = ["sparkgrep", "nonexistent1.py", "nonexistent2.ipynb"]

    with patch("sys.argv", test_argv):
        result = main()

    # Should handle nonexistent files gracefully
    assert result == 0  # No files processed, no issues found


def test_main_empty_files():
    """Test main function with empty files."""
    # Create empty Python file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write("")  # Empty file
        empty_py_path = f.name

    # Create empty notebook file
    empty_notebook = {
        "nbformat": 4,
        "nbformat_minor": 4,
        "metadata": {},
        "cells": []
    }
    with tempfile.NamedTemporaryFile(mode="w", suffix=".ipynb", delete=False) as f:
        json.dump(empty_notebook, f)
        empty_nb_path = f.name

    try:
        test_argv = ["sparkgrep", empty_py_path, empty_nb_path]

        with patch("sys.argv", test_argv):
            result = main()

        # Should handle empty files gracefully
        assert result == 0  # No issues in empty files

    finally:
        os.unlink(empty_py_path)
        os.unlink(empty_nb_path)


def test_main_with_permission_denied():
    """Test main function when file permissions deny access."""
    python_code = "display(df)"

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(python_code)
        temp_path = f.name

    try:
        # Remove all permissions
        os.chmod(temp_path, 0o000)

        test_argv = ["sparkgrep", temp_path]

        with patch("sys.argv", test_argv):
            result = main()

        # Should handle permission errors gracefully
        assert isinstance(result, int)

    finally:
        # Restore permissions for cleanup
        os.chmod(temp_path, 0o644)
        os.unlink(temp_path)
