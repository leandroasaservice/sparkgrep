import pytest
import tempfile
import os
from pathlib import Path

from sparkgrep.file_processors import check_python_file


def test_check_python_file_skip_comments():
    """Test that comments are properly skipped."""
    python_code = """
def process_data():
    # display(df)  - This is a comment and should be skipped
    df = load_data()
    # df.show()    - This is also a comment

    # But this should be found:
    display(df)  # Real function call

    return df
"""

    patterns = [(r"display\(", "display function")]

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(python_code)
        temp_path = f.name

    try:
        issues = check_python_file(Path(temp_path), patterns)

        # Should only find the real function call, not the commented ones
        assert len(issues) == 1
        assert issues[0][1] == "display function"

        # The found issue should be on the line with the actual call
        assert "display(df)  # Real function call" in issues[0][2]

    finally:
        os.unlink(temp_path)


def test_check_python_file_skip_docstrings():
    """Test that docstrings are properly skipped."""
    python_code = '''
def example_function():
    """
    This is a docstring that contains display(df) which should be skipped.
    It also mentions df.show() but this should also be ignored.
    """

    # This is the actual code that should be detected
    display(df)  # This should be found

    return result
'''

    patterns = [(r"display\(", "display function")]

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(python_code)
        temp_path = f.name

    try:
        issues = check_python_file(Path(temp_path), patterns)

        # Should only find the actual function call, not the one in docstring
        assert len(issues) == 1
        assert issues[0][1] == "display function"
        assert "This should be found" in issues[0][2]

    finally:
        os.unlink(temp_path)


def test_check_python_file_multiline_docstring():
    """Test handling of multiline docstrings."""
    python_code = '''
def complex_function():
    """
    This is a multiline docstring.

    It contains display(df) and df.show() examples
    that should not be detected as issues.

    Example usage:
        df = load_data()
        display(df)  # This is in docstring
    """

    # Actual code starts here
    df = get_dataframe()
    display(df)  # This should be detected
'''

    patterns = [(r"display\(", "display function")]

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(python_code)
        temp_path = f.name

    try:
        issues = check_python_file(Path(temp_path), patterns)

        # Should only find the actual call outside the docstring
        assert len(issues) == 1
        assert "This should be detected" in issues[0][2]

    finally:
        os.unlink(temp_path)


def test_check_python_file_string_literals():
    """Test that patterns in string literals are handled appropriately."""
    python_code = '''
def test_strings():
    # These are in strings and may or may not be detected
    message = "Please use display(df) to see results"
    sql_query = """
        SELECT * FROM table
        WHERE display(column) > 0
    """

    # This should definitely be detected
    display(actual_df)  # Real function call
'''

    patterns = [(r"display\(", "display function")]

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(python_code)
        temp_path = f.name

    try:
        issues = check_python_file(Path(temp_path), patterns)

        # Should find at least the real function call
        assert len(issues) >= 1

        # Check that the real function call is found
        real_call_found = any("actual_df" in issue[2] for issue in issues)
        assert real_call_found

    finally:
        os.unlink(temp_path)


def test_check_python_file_unicode_content():
    """Test processing files with unicode content."""
    python_code = """
# -*- coding: utf-8 -*-
# Processing données françaises 🚀
def traiter_données():
    df_世界 = load_data()
    display(df_世界)  # Should be found
    return df_世界
"""

    patterns = [(r"display\(", "display function")]

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
        f.write(python_code)
        temp_path = f.name

    try:
        issues = check_python_file(Path(temp_path), patterns)

        assert len(issues) == 1
        assert issues[0][1] == "display function"

        # Check that unicode is preserved in the line content
        assert "df_世界" in issues[0][2]

    finally:
        os.unlink(temp_path)


def test_check_python_file_complex_patterns():
    """Test with complex regex patterns."""
    python_code = """
def analyze_data():
    df.collect()  # Should match
    result = df.collect()  # Should not match (has assignment)
    df.count()    # Should match
    total = df.count()  # Should not match (has assignment)

    display(df)   # Should match
"""

    patterns = [
        (r"\.collect\(\)(?!\s*[=])", "collect without assignment"),
        (r"\.count\(\)(?!\s*[=])", "count without assignment"),
        (r"display\(", "display function")
    ]

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(python_code)
        temp_path = f.name

    try:
        issues = check_python_file(Path(temp_path), patterns)

        # Should find patterns that match the criteria
        assert len(issues) >= 3

        descriptions = [issue[1] for issue in issues]
        assert "collect without assignment" in descriptions
        assert "count without assignment" in descriptions
        assert "display function" in descriptions

    finally:
        os.unlink(temp_path)


def test_check_python_file_mixed_quotes():
    """Test handling of mixed quote styles."""
    python_code = """
def mixed_quotes():
    single = 'This has display(df) in single quotes'
    double = "This has display(df) in double quotes"
    triple_single = '''Triple single quotes with display(df)'''
    triple_double = \"\"\"Triple double quotes with display(df)\"\"\"

    # This should be found
    display(real_df)
"""

    patterns = [(r"display\(", "display function")]

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(python_code)
        temp_path = f.name

    try:
        issues = check_python_file(Path(temp_path), patterns)

        # Should find at least the real function call
        assert len(issues) >= 1

        # Check that the real call is found
        real_call_found = any("real_df" in issue[2] for issue in issues)
        assert real_call_found

    finally:
        os.unlink(temp_path)


def test_check_python_file_escaped_quotes():
    """Test handling of escaped quotes in strings."""
    python_code = '''
def escaped_quotes():
    message = "String with \\"escaped quotes\\" and display(df)"
    another = 'Single quotes with \\\'escaped\\\' and display(df)'

    # Real function call
    display(dataframe)
'''

    patterns = [(r"display\(", "display function")]

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(python_code)
        temp_path = f.name

    try:
        issues = check_python_file(Path(temp_path), patterns)

        # Should find at least the real function call
        assert len(issues) >= 1

        # Check that the real call is found
        real_call_found = any("dataframe" in issue[2] for issue in issues)
        assert real_call_found

    finally:
        os.unlink(temp_path)


def test_check_python_file_f_strings():
    """Test handling of f-strings."""
    python_code = '''
def f_string_test():
    name = "world"
    message = f"Hello {name}, use display(df) to see data"
    dynamic = f"Process {display(df)} inline"  # This might be detected

    # Real function call
    display(actual_data)
'''

    patterns = [(r"display\(", "display function")]

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(python_code)
        temp_path = f.name

    try:
        issues = check_python_file(Path(temp_path), patterns)

        # Should find at least the real function call
        assert len(issues) >= 1

        # Check that the real call is found
        real_call_found = any("actual_data" in issue[2] for issue in issues)
        assert real_call_found

    finally:
        os.unlink(temp_path)


def test_check_python_file_raw_strings():
    """Test handling of raw strings."""
    python_code = r'''
def raw_string_test():
    regex_pattern = r"display\(.*\)"  # Raw string
    path = r"C:\display\folder"       # Raw string with display

    # Real function call
    display(df)
'''

    patterns = [(r"display\(", "display function")]

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(python_code)
        temp_path = f.name

    try:
        issues = check_python_file(Path(temp_path), patterns)

        # Should find at least the real function call
        assert len(issues) >= 1

    finally:
        os.unlink(temp_path)
