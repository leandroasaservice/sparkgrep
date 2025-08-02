"""
Unit tests for Python file processing functionality.
"""

import pytest
from pathlib import Path
import tempfile
import os

from sparkgrep.file_processors import check_python_file


def test_check_python_file_with_matches():
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


def test_check_python_file_no_matches():
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


def test_check_python_file_skip_comments():
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


def test_check_python_file_skip_docstrings():
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


def test_check_python_file_single_quote_docstring():
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


def test_check_python_file_nonexistent():
    """Test checking nonexistent Python file."""
    patterns = [(r"display\s*\(", "display function")]

    issues = check_python_file(Path("nonexistent.py"), patterns)
    assert len(issues) == 0


def test_check_python_file_empty_patterns():
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


def test_check_python_file_complex_patterns():
    """Test checking Python file with complex regex patterns."""
    patterns = [
        (r"^\s*\w+\.collect\s*\(\s*\)\s*$", "collect without assignment"),
        (r"^\s*\w+\.count\s*\(\s*\)\s*$", "count without assignment"),
        (r"display\s*\(", "display function"),
    ]

    python_code = """
def test_function():
    display(df)  # Should match
    df.collect()  # Should match
    result = df.collect()  # Should NOT match (assignment)
    df.count()  # Should match
    total = df.count()  # Should NOT match (assignment)
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(python_code)
        temp_path = f.name

    try:
        issues = check_python_file(Path(temp_path), patterns)

        # Should find 3 issues: display, collect, count
        assert len(issues) == 3

        issue_descriptions = [issue[1] for issue in issues]
        assert "display function" in issue_descriptions
        assert "collect without assignment" in issue_descriptions
        assert "count without assignment" in issue_descriptions
    finally:
        os.unlink(temp_path)


def test_check_python_file_multiline_docstring():
    """Test handling of multiline docstrings."""
    patterns = [(r"display\s*\(", "display function")]

    python_code = '''
def test_function():
    """
    This is a multiline docstring.
    It contains display(df) which should be ignored.
    Even this line with display(df) should be ignored.
    """
    display(df)  # This should be found
'''

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(python_code)
        temp_path = f.name

    try:
        issues = check_python_file(Path(temp_path), patterns)
        assert len(issues) == 1
        assert issues[0][1] == "display function"
        assert issues[0][0] == 6  # Line number should be 6
    finally:
        os.unlink(temp_path)


def test_check_python_file_nested_functions():
    """Test checking Python file with nested functions."""
    patterns = [(r"display\s*\(", "display function")]

    python_code = """
def outer_function():
    def inner_function():
        display(df)  # Should be found
        return "inner"

    display(df)  # Should be found
    inner_function()
    return "outer"
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(python_code)
        temp_path = f.name

    try:
        issues = check_python_file(Path(temp_path), patterns)
        assert len(issues) == 2

        # Check both issues are display functions
        for issue in issues:
            assert issue[1] == "display function"
    finally:
        os.unlink(temp_path)


def test_check_python_file_string_literals():
    """Test that patterns in string literals are not matched."""
    patterns = [(r"display\s*\(", "display function")]

    python_code = '''
def test_function():
    message = "This mentions display(df) but should not match"
    print("display(df) in print should not match")
    sql = """
    SELECT display(column) FROM table
    This display(df) should not match either
    """
    actual_display = display(df)  # This should match
'''

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(python_code)
        temp_path = f.name

    try:
        issues = check_python_file(Path(temp_path), patterns)
        assert len(issues) == 1  # Only the actual display call
        assert issues[0][1] == "display function"
    finally:
        os.unlink(temp_path)


def test_check_python_file_class_methods():
    """Test checking Python file with class methods."""
    patterns = [(r"display\s*\(", "display function")]

    python_code = '''
class TestClass:
    def __init__(self):
        display(df)  # Should be found

    def method1(self):
        """Method with display(df) in docstring - should be ignored"""
        display(df)  # Should be found

    @staticmethod
    def static_method():
        display(df)  # Should be found

    @classmethod
    def class_method(cls):
        display(df)  # Should be found
'''

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(python_code)
        temp_path = f.name

    try:
        issues = check_python_file(Path(temp_path), patterns)
        assert len(issues) == 4  # All display calls except in docstring

        for issue in issues:
            assert issue[1] == "display function"
    finally:
        os.unlink(temp_path)


def test_check_python_file_decorators():
    """Test checking Python file with decorators."""
    patterns = [(r"display\s*\(", "display function")]

    python_code = '''
@decorator
def decorated_function():
    display(df)  # Should be found

@property
def property_method(self):
    display(df)  # Should be found

@display(df)  # This should be found too
def function_with_display_decorator():
    pass
'''

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(python_code)
        temp_path = f.name

    try:
        issues = check_python_file(Path(temp_path), patterns)
        assert len(issues) == 3  # All display calls

        for issue in issues:
            assert issue[1] == "display function"
    finally:
        os.unlink(temp_path)


def test_check_python_file_import_statements():
    """Test that import statements with patterns are not matched."""
    patterns = [(r"display\s*\(", "display function")]

    python_code = '''
from some_module import display
import display as disp
from display import something

def test_function():
    display(df)  # This should be found
'''

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(python_code)
        temp_path = f.name

    try:
        issues = check_python_file(Path(temp_path), patterns)
        assert len(issues) == 1  # Only the function call
        assert issues[0][1] == "display function"
    finally:
        os.unlink(temp_path)


def test_check_python_file_large_file():
    """Test checking a large Python file."""
    patterns = [(r"display\s*\(", "display function")]

    # Create a large file with many lines
    lines = []
    for i in range(1000):
        if i % 100 == 0:
            lines.append(f"    display(df_{i})  # Issue on line {i+1}")
        else:
            lines.append(f"    print('Line {i+1}')")

    python_code = "def large_function():\n" + "\n".join(lines)

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(python_code)
        temp_path = f.name

    try:
        issues = check_python_file(Path(temp_path), patterns)
        assert len(issues) == 10  # Every 100th line

        # Check line numbers are correct
        expected_lines = [i + 2 for i in range(0, 1000, 100)]  # +2 for function def and 1-based indexing
        actual_lines = sorted([issue[0] for issue in issues])
        assert actual_lines == expected_lines
    finally:
        os.unlink(temp_path)
