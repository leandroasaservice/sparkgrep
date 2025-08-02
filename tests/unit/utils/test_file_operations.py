"""
Unit tests for utils file operations functionality.
"""

import pytest
from pathlib import Path
from unittest.mock import patch, mock_open
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


def test_read_file_unicode_error(capsys):
    """Test handling of unicode decode errors."""
    with patch("builtins.open", mock_open()) as mock_file:
        mock_file.side_effect = UnicodeDecodeError("utf-8", b"", 0, 1, "test error")

        result = read_file_safely(Path("test.py"))

        assert result == []
        captured = capsys.readouterr()
        assert "Warning: Could not read" in captured.out
        assert "encoding issues" in captured.out


def test_read_empty_file():
    """Test reading an empty file."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        temp_path = f.name

    try:
        result = read_file_safely(Path(temp_path))
        assert result == []
    finally:
        os.unlink(temp_path)


def test_read_file_permission_error():
    """Test handling of permission errors when reading files."""
    with patch("builtins.open") as mock_open_func:
        mock_open_func.side_effect = PermissionError("Permission denied")

        result = read_file_safely(Path("protected_file.py"))
        assert result == []


def test_read_file_with_different_encodings():
    """Test reading files with different content types."""
    test_cases = [
        "Simple ASCII content",
        "Unicode content with émojis 🎉",
        "Mixed content: ASCII + Unicode = ✓",
        "",  # Empty content
        "\n\n\n",  # Only newlines
    ]

    for content in test_cases:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write(content)
            temp_path = f.name

        try:
            result = read_file_safely(Path(temp_path))
            if content:
                assert len(result) > 0
                assert "".join(result) == content
            else:
                assert result == []
        finally:
            os.unlink(temp_path)


def test_read_file_io_error():
    """Test handling of general IO errors."""
    with patch("builtins.open") as mock_open_func:
        mock_open_func.side_effect = IOError("General IO error")

        result = read_file_safely(Path("problematic_file.py"))
        assert result == []


def test_read_file_large_content():
    """Test reading a file with large content."""
    large_content = "line\n" * 10000  # 10k lines

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(large_content)
        temp_path = f.name

    try:
        result = read_file_safely(Path(temp_path))
        assert len(result) == 10000
        assert all(line == "line\n" for line in result)
    finally:
        os.unlink(temp_path)


def test_read_file_special_characters():
    """Test reading files with special characters in content."""
    special_content = "Special chars: @#$%^&*()_+{}|:<>?[]\\;'\",./"

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
        f.write(special_content)
        temp_path = f.name

    try:
        result = read_file_safely(Path(temp_path))
        assert len(result) == 1
        assert result[0] == special_content
    finally:
        os.unlink(temp_path)


def test_read_file_with_bom():
    """Test reading files with byte order mark (BOM)."""
    content = "Content with BOM"

    with tempfile.NamedTemporaryFile(mode="wb", suffix=".py", delete=False) as f:
        # Write UTF-8 BOM + content
        f.write(b'\xef\xbb\xbf' + content.encode('utf-8'))
        temp_path = f.name

    try:
        result = read_file_safely(Path(temp_path))
        # Should handle BOM gracefully
        assert len(result) >= 1
        # Content should be readable (BOM might be stripped by Python)
        joined_result = "".join(result)
        assert "Content with BOM" in joined_result
    finally:
        os.unlink(temp_path)
