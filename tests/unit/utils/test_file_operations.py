import pytest
from pathlib import Path
import tempfile
import os

from sparkgrep.utils import read_file_safely


def test_read_existing_file():
    """Test reading an existing file."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write("line1\nline2\nline3\n")
        temp_path = f.name

    try:
        result = read_file_safely(Path(temp_path))
        assert result == ["line1\n", "line2\n", "line3\n"]
    finally:
        os.unlink(temp_path)


def test_read_nonexistent_file():
    """Test reading a nonexistent file."""
    result = read_file_safely(Path("nonexistent_file.py"))
    assert result == []


def test_read_empty_file():
    """Test reading an empty file."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        temp_path = f.name

    try:
        result = read_file_safely(Path(temp_path))
        assert result == []
    finally:
        os.unlink(temp_path)


def test_read_file_with_unicode():
    """Test reading a file with unicode content."""
    content = "# -*- coding: utf-8 -*-\n# Comment with émojis 🚀\nprint('Hello 世界')\n"

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
        f.write(content)
        temp_path = f.name

    try:
        result = read_file_safely(Path(temp_path))
        assert len(result) == 3
        assert "émojis 🚀" in result[1]
        assert "世界" in result[2]
    finally:
        os.unlink(temp_path)


def test_read_file_with_different_line_endings():
    """Test reading files with different line endings."""
    content_unix = "line1\nline2\nline3\n"

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, newline='\n') as f:
        f.write(content_unix)
        temp_path = f.name

    try:
        result = read_file_safely(Path(temp_path))
        assert len(result) == 3
        assert all(line.endswith('\n') for line in result)
    finally:
        os.unlink(temp_path)


def test_read_large_file():
    """Test reading a large file."""
    lines = [f"line_{i}\n" for i in range(1000)]

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.writelines(lines)
        temp_path = f.name

    try:
        result = read_file_safely(Path(temp_path))
        assert len(result) == 1000
        assert result[0] == "line_0\n"
        assert result[999] == "line_999\n"
    finally:
        os.unlink(temp_path)


def test_read_file_with_special_characters():
    """Test reading files with special characters in content."""
    content = "def test():\n    print('Special chars: !@#$%^&*()[]{}|\\\\;:'\\'\"')\n    return True\n"

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(content)
        temp_path = f.name

    try:
        result = read_file_safely(Path(temp_path))
        assert len(result) == 3
        assert "Special chars:" in result[1]
    finally:
        os.unlink(temp_path)


def test_read_file_pathlib_path():
    """Test that function works with pathlib.Path objects."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write("test content\n")
        temp_path = f.name

    try:
        # Test with Path object
        path_obj = Path(temp_path)
        result = read_file_safely(path_obj)
        assert result == ["test content\n"]
    finally:
        os.unlink(temp_path)


def test_read_file_permissions_handling():
    """Test handling of permission-related issues."""
    # Test with a path that shouldn't exist and cause FileNotFoundError
    result = read_file_safely(Path("/nonexistent/deeply/nested/file.py"))
    assert result == []


def test_read_file_with_bom():
    """Test reading files with BOM (Byte Order Mark)."""
    content = "print('Hello World')\n"

    with tempfile.NamedTemporaryFile(mode="wb", suffix=".py", delete=False) as f:
        # Write BOM + content
        f.write(b'\xef\xbb\xbf' + content.encode('utf-8'))
        temp_path = f.name

    try:
        result = read_file_safely(Path(temp_path))
        assert len(result) == 1
        # BOM should be handled by UTF-8 decoder
        assert "print('Hello World')" in result[0]
    finally:
        os.unlink(temp_path)
