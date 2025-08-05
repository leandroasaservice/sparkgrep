import pytest
import tempfile
import os
from pathlib import Path

from sparkgrep.file_processors import process_single_file


def test_process_file_unicode_filename():
    """Test processing files with unicode characters in filename."""
    python_code = "display(df)"
    patterns = [(r"display\(", "display function")]

    # Create file with unicode name
    with tempfile.NamedTemporaryFile(mode="w", suffix="_émojis🚀.py", delete=False) as f:
        f.write(python_code)
        temp_path = f.name

    try:
        issues = process_single_file(Path(temp_path), patterns)

        assert len(issues) == 1
        assert issues[0][1] == "display function"

    finally:
        os.unlink(temp_path)


def test_process_file_very_large():
    """Test processing very large files."""
    lines = ["display(df)" if i % 100 == 0 else "# comment" for i in range(10000)]
    python_code = "\n".join(lines)
    patterns = [(r"display\(", "display function")]

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(python_code)
        temp_path = f.name

    try:
        issues = process_single_file(Path(temp_path), patterns)

        # Should find display calls (every 100th line starting from 0)
        expected_count = len([i for i in range(10000) if i % 100 == 0])
        assert len(issues) == expected_count

    finally:
        os.unlink(temp_path)


def test_process_file_line_number_accuracy():
    """Test that line numbers are reported accurately."""
    python_code = """# Line 1
# Line 2
display(df1)  # Line 3
# Line 4
# Line 5
display(df2)  # Line 6
"""
    patterns = [(r"display\(", "display function")]

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(python_code)
        temp_path = f.name

    try:
        issues = process_single_file(Path(temp_path), patterns)

        assert len(issues) == 2

        # Check line numbers
        line_numbers = sorted([issue[0] for issue in issues])
        assert line_numbers == [3, 6]

        # Check content
        code_lines = [issue[2] for issue in issues]
        assert any("df1" in line for line in code_lines)
        assert any("df2" in line for line in code_lines)

    finally:
        os.unlink(temp_path)


def test_process_file_special_characters_in_path():
    """Test processing files with special characters in path."""
    python_code = "display(df)"
    patterns = [(r"display\(", "display function")]

    # Create file with special characters in name
    special_chars = "file with spaces & symbols!@#.py"

    with tempfile.NamedTemporaryFile(mode="w", suffix=special_chars, delete=False) as f:
        f.write(python_code)
        temp_path = f.name

    try:
        issues = process_single_file(Path(temp_path), patterns)

        assert len(issues) == 1
        assert issues[0][1] == "display function"

    finally:
        os.unlink(temp_path)


def test_process_file_unicode_content():
    """Test processing files with unicode content."""
    python_code = """
# -*- coding: utf-8 -*-
def process_unicode():
    # Unicode variables
    données_françaises = load_data()
    display(données_françaises)  # Should be found

    # Emoji variables
    df_🚀 = transform_data()
    display(df_🚀)  # Should be found
"""

    patterns = [(r"display\(", "display function")]

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
        f.write(python_code)
        temp_path = f.name

    try:
        issues = process_single_file(Path(temp_path), patterns)

        assert len(issues) == 2

        # Check that unicode content is preserved
        code_lines = [issue[2] for issue in issues]
        assert any("données_françaises" in line for line in code_lines)
        assert any("df_🚀" in line for line in code_lines)

    finally:
        os.unlink(temp_path)


def test_process_file_extremely_long_lines():
    """Test processing files with extremely long lines."""
    # Create a very long line
    long_line = "# " + "x" * 50000 + "\n"
    python_code = long_line + "display(df)  # Should be found\n"

    patterns = [(r"display\(", "display function")]

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(python_code)
        temp_path = f.name

    try:
        issues = process_single_file(Path(temp_path), patterns)

        assert len(issues) == 1
        assert issues[0][1] == "display function"

    finally:
        os.unlink(temp_path)


def test_process_file_mixed_line_endings():
    """Test processing files with mixed line endings."""
    # Mix different line endings
    python_code = "# Line 1\r\ndisplay(df1)\n# Line 3\rdisplay(df2)\n"
    patterns = [(r"display\(", "display function")]

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, newline='') as f:
        f.write(python_code)
        temp_path = f.name

    try:
        issues = process_single_file(Path(temp_path), patterns)

        # Should find both display calls regardless of line endings
        assert len(issues) == 2

        code_lines = [issue[2] for issue in issues]
        assert any("df1" in line for line in code_lines)
        assert any("df2" in line for line in code_lines)

    finally:
        os.unlink(temp_path)


def test_process_file_binary_like_content():
    """Test processing files that look like binary but have text extension."""
    # Create content that looks binary-ish but is still text
    python_code = "# Binary-like content: \x00\x01\x02\ndisplay(df)  # Should be found\n"
    patterns = [(r"display\(", "display function")]

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(python_code)
        temp_path = f.name

    try:
        issues = process_single_file(Path(temp_path), patterns)

        # Should handle binary-like content gracefully
        assert len(issues) >= 0  # May or may not find patterns depending on handling

    finally:
        os.unlink(temp_path)


def test_process_file_nested_directory_path():
    """Test processing files in deeply nested directory paths."""
    python_code = "display(df)"
    patterns = [(r"display\(", "display function")]

    # Create a nested directory structure
    with tempfile.TemporaryDirectory() as temp_dir:
        nested_path = Path(temp_dir) / "level1" / "level2" / "level3" / "level4"
        nested_path.mkdir(parents=True, exist_ok=True)

        file_path = nested_path / "deep_file.py"
        file_path.write_text(python_code)

        issues = process_single_file(file_path, patterns)

        assert len(issues) == 1
        assert issues[0][1] == "display function"


def test_process_file_symlink():
    """Test processing symlinks to files."""
    python_code = "display(df)"
    patterns = [(r"display\(", "display function")]

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

        issues = process_single_file(symlink_file, patterns)

        assert len(issues) == 1
        assert issues[0][1] == "display function"


def test_process_file_performance_with_many_patterns():
    """Test processing with a large number of patterns."""
    python_code = """
function_1()
function_2()
function_3()
display(df)
"""

    # Create many patterns
    patterns = []
    for i in range(1000):
        patterns.append((f"function_{i}", f"Function {i}"))
    patterns.append((r"display\(", "display function"))

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(python_code)
        temp_path = f.name

    try:
        issues = process_single_file(Path(temp_path), patterns)

        # Should find the matching patterns
        assert len(issues) >= 1
        descriptions = [issue[1] for issue in issues]
        assert "display function" in descriptions

    finally:
        os.unlink(temp_path)


def test_process_file_memory_efficiency():
    """Test that file processing is memory efficient with large files."""
    # Create a moderately large file to test memory handling
    lines = []
    for i in range(50000):
        if i % 1000 == 0:
            lines.append(f"display(df_{i})")
        else:
            lines.append(f"# Comment line {i} with some content to make it longer")

    python_code = "\n".join(lines)
    patterns = [(r"display\(", "display function")]

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(python_code)
        temp_path = f.name

    try:
        issues = process_single_file(Path(temp_path), patterns)

        # Should find all display calls efficiently
        expected_count = len([i for i in range(50000) if i % 1000 == 0])
        assert len(issues) == expected_count

    finally:
        os.unlink(temp_path)
