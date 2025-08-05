import pytest
from io import StringIO
import sys
from contextlib import redirect_stdout

from sparkgrep.utils import report_results


def test_report_with_issues():
    """Test reporting with issues found."""
    issues = [
        (5, "display function", "display(df)"),
        (10, "show method", "df.show()"),
        (15, "collect method", "df.collect()")
    ]

    # Capture stdout
    output = StringIO()
    with redirect_stdout(output):
        report_results("test_file.py", issues)

    result = output.getvalue()

    # Check that all issues are reported
    assert "test_file.py" in result
    assert "Line 5: display function" in result
    assert "Line 10: show method" in result
    assert "Line 15: collect method" in result
    assert "display(df)" in result
    assert "df.show()" in result
    assert "df.collect()" in result


def test_report_no_issues():
    """Test reporting when no issues are found."""
    issues = []

    output = StringIO()
    with redirect_stdout(output):
        report_results("clean_file.py", issues)

    result = output.getvalue()

    # Should be empty output for clean files
    assert result == ""


def test_report_different_file_types():
    """Test reporting with different file types."""
    issues = [(1, "display function", "display(df)")]

    file_types = ["script.py", "notebook.ipynb", "module.py"]

    for file_type in file_types:
        output = StringIO()
        with redirect_stdout(output):
            report_results(file_type, issues)

        result = output.getvalue()
        assert file_type in result
        assert "Line 1: display function" in result


def test_report_special_characters_in_filename():
    """Test reporting with special characters in filename."""
    issues = [(1, "display function", "display(df)")]
    filename = "file with spaces & special chars!.py"

    output = StringIO()
    with redirect_stdout(output):
        report_results(filename, issues)

    result = output.getvalue()
    assert filename in result


def test_report_special_characters_in_content():
    """Test reporting with special characters in code content."""
    issues = [
        (1, "display function", "display(df_with_émojis_🚀)"),
        (2, "show method", "df.show()  # Comment with 世界"),
        (3, "collect method", "result = df.collect()  # Special: !@#$%^&*()")
    ]

    output = StringIO()
    with redirect_stdout(output):
        report_results("unicode_file.py", issues)

    result = output.getvalue()
    assert "émojis_🚀" in result
    assert "世界" in result
    assert "!@#$%^&*()" in result


def test_report_long_content_lines():
    """Test reporting with very long content lines."""
    long_line = "display(" + "very_long_parameter_name_" * 20 + ")"
    issues = [(1, "display function", long_line)]

    output = StringIO()
    with redirect_stdout(output):
        report_results("file.py", issues)

    result = output.getvalue()
    assert "display(" in result
    # Should handle long lines without issues


def test_report_multiple_issues_same_line():
    """Test reporting multiple issues on the same line."""
    issues = [
        (5, "display function", "display(df); df.show()"),
        (5, "show method", "display(df); df.show()")
    ]

    output = StringIO()
    with redirect_stdout(output):
        report_results("file.py", issues)

    result = output.getvalue()

    # Both issues should be reported even though they're on the same line
    assert result.count("Line 5:") == 2
    assert "display function" in result
    assert "show method" in result


def test_report_formatting_consistency():
    """Test that reporting format is consistent."""
    issues = [
        (1, "pattern1", "code1"),
        (100, "pattern2", "code2"),
        (9999, "pattern3", "code3")
    ]

    output = StringIO()
    with redirect_stdout(output):
        report_results("file.py", issues)

    result = output.getvalue()
    lines = result.strip().split('\n')

    # Report format: filename, then for each issue: "Line X: description" and "> code"
    # So we expect: 1 filename line + 2 lines per issue = 1 + 3*2 = 7 lines
    assert len(lines) == 7

    # Check that we have filename and issue formatting
    assert "file.py:" in lines[0]
    assert "Line 1: pattern1" in result
    assert "Line 100: pattern2" in result
    assert "Line 9999: pattern3" in result


def test_report_empty_filename():
    """Test reporting with empty filename."""
    issues = [(1, "display function", "display(df)")]

    output = StringIO()
    with redirect_stdout(output):
        report_results("", issues)

    result = output.getvalue()
    # Should still work, even with empty filename
    assert "Line 1: display function" in result


def test_report_very_large_line_numbers():
    """Test reporting with very large line numbers."""
    issues = [(999999, "display function", "display(df)")]

    output = StringIO()
    with redirect_stdout(output):
        report_results("huge_file.py", issues)

    result = output.getvalue()
    assert "Line 999999:" in result


def test_report_zero_line_number():
    """Test reporting with zero line number (edge case)."""
    issues = [(0, "display function", "display(df)")]

    output = StringIO()
    with redirect_stdout(output):
        report_results("file.py", issues)

    result = output.getvalue()
    assert "Line 0:" in result


def test_report_mixed_line_numbers():
    """Test reporting with mixed line number ordering."""
    issues = [
        (50, "display function", "display(df)"),
        (5, "show method", "df.show()"),
        (25, "collect method", "df.collect()")
    ]

    output = StringIO()
    with redirect_stdout(output):
        report_results("file.py", issues)

    result = output.getvalue()

    # All issues should be reported regardless of order
    assert "Line 50:" in result
    assert "Line 5:" in result
    assert "Line 25:" in result


def test_report_empty_code_content():
    """Test reporting with empty code content."""
    issues = [(1, "display function", "")]

    output = StringIO()
    with redirect_stdout(output):
        report_results("file.py", issues)

    result = output.getvalue()
    assert "file.py" in result
    assert "Line 1: display function" in result


def test_report_none_values_handling():
    """Test that report_results handles edge cases gracefully."""
    # Empty issues list
    output = StringIO()
    with redirect_stdout(output):
        report_results("file.py", [])

    assert output.getvalue() == ""

    # Issues with various edge case values
    issues = [
        (1, "description", "code"),
        (2, "", "code_with_empty_description"),
        (3, "description", "")
    ]

    output = StringIO()
    with redirect_stdout(output):
        report_results("file.py", issues)

    result = output.getvalue()
    # Should handle all cases without crashing
    assert "file.py" in result
    # Format: filename + 2 lines per issue = 1 + 3*2 = 7 lines
    assert len(result.strip().split('\n')) == 7
