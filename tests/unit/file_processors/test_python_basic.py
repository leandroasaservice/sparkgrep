import pytest
import tempfile
import os
from pathlib import Path

from sparkgrep.file_processors import check_python_file


def test_check_python_file_with_matches():
    """Test checking a Python file that contains pattern matches."""
    python_code = """
def process_data():
    # Load data
    df = spark.read.parquet("data.parquet")

    # Process data
    display(df)  # This should match
    df.show()    # This should match

    return df
"""

    patterns = [
        (r"display\(", "display function"),
        (r"\.show\(", "show method")
    ]

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(python_code)
        temp_path = f.name

    try:
        issues = check_python_file(Path(temp_path), patterns)

        assert len(issues) == 2

        # Check that both patterns were found
        descriptions = [issue[1] for issue in issues]
        assert "display function" in descriptions
        assert "show method" in descriptions

        # Check line numbers are reasonable
        line_numbers = [issue[0] for issue in issues]
        assert all(line_num > 0 for line_num in line_numbers)

    finally:
        os.unlink(temp_path)


def test_check_python_file_no_matches():
    """Test checking a Python file with no pattern matches."""
    python_code = """
def clean_function():
    data = [1, 2, 3, 4, 5]
    result = sum(data)
    print(f"Result: {result}")
    return result

class CleanClass:
    def __init__(self):
        self.value = 42

    def get_value(self):
        return self.value
"""

    patterns = [
        (r"display\(", "display function"),
        (r"\.show\(", "show method")
    ]

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(python_code)
        temp_path = f.name

    try:
        issues = check_python_file(Path(temp_path), patterns)
        assert len(issues) == 0

    finally:
        os.unlink(temp_path)


def test_check_python_file_nonexistent():
    """Test handling of nonexistent Python files."""
    patterns = [(r"display\(", "display function")]

    issues = check_python_file(Path("nonexistent_file.py"), patterns)
    assert len(issues) == 0


def test_check_python_file_empty_patterns():
    """Test with empty patterns list."""
    python_code = """
def test_function():
    display(df)
    df.show()
"""

    patterns = []  # Empty patterns list

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(python_code)
        temp_path = f.name

    try:
        issues = check_python_file(Path(temp_path), patterns)
        assert len(issues) == 0

    finally:
        os.unlink(temp_path)


def test_check_python_file_empty_file():
    """Test processing an empty Python file."""
    python_code = ""  # Empty file
    patterns = [(r"display\(", "display function")]

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(python_code)
        temp_path = f.name

    try:
        issues = check_python_file(Path(temp_path), patterns)
        assert len(issues) == 0

    finally:
        os.unlink(temp_path)


def test_check_python_file_only_whitespace():
    """Test processing a file with only whitespace."""
    python_code = "   \n\t\n   \n"  # Only whitespace
    patterns = [(r"display\(", "display function")]

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(python_code)
        temp_path = f.name

    try:
        issues = check_python_file(Path(temp_path), patterns)
        assert len(issues) == 0

    finally:
        os.unlink(temp_path)


def test_check_python_file_simple_patterns():
    """Test with simple regex patterns."""
    python_code = """
simple_function()
another_call()
display(df)
"""

    patterns = [
        (r"simple_function", "simple function"),
        (r"another_call", "another call"),
        (r"display", "display call")
    ]

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(python_code)
        temp_path = f.name

    try:
        issues = check_python_file(Path(temp_path), patterns)

        assert len(issues) == 3
        descriptions = [issue[1] for issue in issues]
        assert "simple function" in descriptions
        assert "another call" in descriptions
        assert "display call" in descriptions

    finally:
        os.unlink(temp_path)


def test_check_python_file_line_numbers():
    """Test that line numbers are reported correctly."""
    python_code = """# Line 1
def function():  # Line 2
    display(df)  # Line 3 - should be found
    return True  # Line 4
"""

    patterns = [(r"display\(", "display function")]

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(python_code)
        temp_path = f.name

    try:
        issues = check_python_file(Path(temp_path), patterns)

        assert len(issues) == 1
        # Line number should be 3
        line_info = issues[0][0]
        assert "3" in str(line_info)

    finally:
        os.unlink(temp_path)


def test_check_python_file_multiple_matches_same_line():
    """Test multiple pattern matches on the same line."""
    python_code = """
# This line has multiple issues
display(df); df.show(); display(df2)
"""

    patterns = [
        (r"display\(", "display function"),
        (r"\.show\(", "show method")
    ]

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(python_code)
        temp_path = f.name

    try:
        issues = check_python_file(Path(temp_path), patterns)

        # Should find all patterns (function returns one match per pattern per line)
        assert len(issues) >= 2
        descriptions = [issue[1] for issue in issues]
        assert "display function" in descriptions
        assert "show method" in descriptions

    finally:
        os.unlink(temp_path)


def test_check_python_file_case_sensitivity():
    """Test pattern matching case sensitivity."""
    python_code = """
Display(df)  # Uppercase
DISPLAY(df)  # All caps
display(df)  # Lowercase
"""

    patterns = [(r"display\(", "display function")]  # Lowercase pattern

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(python_code)
        temp_path = f.name

    try:
        issues = check_python_file(Path(temp_path), patterns)

        # Should find matches based on pattern case sensitivity (usually case-insensitive)
        assert len(issues) >= 1

    finally:
        os.unlink(temp_path)
