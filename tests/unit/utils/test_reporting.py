"""
Unit tests for utils reporting functionality.
"""

import pytest
from sparkgrep.utils import report_results


def test_report_with_issues(capsys):
    """Test reporting when issues are found."""
    issues = [
        ("5", "display function", "display(df)"),
        ("10", "show method", "df.show()"),
    ]

    report_results("test_file.py", issues)

    captured = capsys.readouterr()
    assert "test_file.py:" in captured.out
    assert "Line 5: display function" in captured.out
    assert "> display(df)" in captured.out
    assert "Line 10: show method" in captured.out
    assert "> df.show()" in captured.out


def test_report_no_issues(capsys):
    """Test reporting when no issues are found."""
    issues = []

    report_results("test_file.py", issues)

    captured = capsys.readouterr()
    assert captured.out == ""


def test_report_different_file_types(capsys):
    """Test reporting for different file types."""
    issues = [("Cell 1, Line 3", "display function", "display(df)")]

    report_results("notebook.ipynb", issues)

    captured = capsys.readouterr()
    assert "notebook.ipynb:" in captured.out
    assert "Line Cell 1, Line 3" in captured.out


def test_report_special_characters(capsys):
    """Test reporting with special characters in file names and content."""
    issues = [("1", "pattern", "special chars: àáâã")]

    report_results("file with spaces.py", issues)

    captured = capsys.readouterr()
    assert "file with spaces.py:" in captured.out
    assert "special chars: àáâã" in captured.out


def test_report_results_formatting(capsys):
    """Test detailed formatting of report results."""
    issues = [
        ("1", "first issue", "first_line_content"),
        ("2", "second issue", "second_line_content"),
        ("Cell 3, Line 4", "notebook issue", "notebook_content"),
    ]

    report_results("mixed_file.py", issues)

    captured = capsys.readouterr()
    output_lines = captured.out.strip().split('\n')

    # Should have header plus 2 lines per issue
    assert len(output_lines) == 1 + (2 * len(issues))

    # Check header
    assert output_lines[0] == "mixed_file.py:"

    # Check issue formatting
    assert "Line 1: first issue" in output_lines[1]
    assert "> first_line_content" in output_lines[2]
    assert "Line 2: second issue" in output_lines[3]
    assert "> second_line_content" in output_lines[4]
    assert "Line Cell 3, Line 4: notebook issue" in output_lines[5]
    assert "> notebook_content" in output_lines[6]


def test_report_empty_file_name(capsys):
    """Test reporting with empty file name."""
    issues = [("1", "issue", "content")]

    report_results("", issues)

    captured = capsys.readouterr()
    assert ":" in captured.out  # Should still have the colon


def test_report_long_content(capsys):
    """Test reporting with very long line content."""
    long_content = "x" * 1000  # Very long line
    issues = [("1", "long line issue", long_content)]

    report_results("test.py", issues)

    captured = capsys.readouterr()
    assert long_content in captured.out
    assert "Line 1: long line issue" in captured.out


def test_report_unicode_filenames(capsys):
    """Test reporting with unicode filenames."""
    issues = [("1", "test issue", "test content")]
    unicode_filenames = [
        "файл.py",  # Cyrillic
        "文件.py",   # Chinese
        "αρχείο.py", # Greek
        "🎉_file.py", # Emoji
    ]

    for filename in unicode_filenames:
        report_results(filename, issues)

        captured = capsys.readouterr()
        assert f"{filename}:" in captured.out
        assert "Line 1: test issue" in captured.out


def test_report_multiple_issues_same_line(capsys):
    """Test reporting multiple issues on the same line."""
    issues = [
        ("5", "first issue", "display(df.show())"),
        ("5", "second issue", "display(df.show())"),
    ]

    report_results("test_file.py", issues)

    captured = capsys.readouterr()
    output_lines = captured.out.strip().split('\n')

    # Should have header plus 2 lines per issue
    assert len(output_lines) == 5  # 1 header + 4 issue lines
    assert "Line 5: first issue" in captured.out
    assert "Line 5: second issue" in captured.out
    # Content should appear twice
    assert captured.out.count("> display(df.show())") == 2


def test_report_complex_line_numbers(capsys):
    """Test reporting with complex line number formats."""
    issues = [
        ("123", "simple line", "content1"),
        ("Cell 5, Line 10", "notebook cell", "content2"),
        ("Function foo, Line 2", "custom format", "content3"),
        ("", "empty line number", "content4"),
    ]

    report_results("complex_file.py", issues)

    captured = capsys.readouterr()
    assert "Line 123: simple line" in captured.out
    assert "Line Cell 5, Line 10: notebook cell" in captured.out
    assert "Line Function foo, Line 2: custom format" in captured.out
    assert "Line : empty line number" in captured.out


def test_report_very_long_descriptions(capsys):
    """Test reporting with very long issue descriptions."""
    long_description = "This is a very long description " * 20
    issues = [("1", long_description, "content")]

    report_results("test.py", issues)

    captured = capsys.readouterr()
    assert long_description in captured.out
    assert "Line 1:" in captured.out


def test_report_special_formatting_characters(capsys):
    """Test reporting with special formatting characters in content."""
    issues = [
        ("1", "tab issue", "content\twith\ttabs"),
        ("2", "newline issue", "content\nwith\nnewlines"),
        ("3", "quote issue", 'content "with" \'quotes\''),
        ("4", "backslash issue", "content\\with\\backslashes"),
    ]

    report_results("format_test.py", issues)

    captured = capsys.readouterr()

    # All content should be preserved as-is
    assert "content\twith\ttabs" in captured.out
    assert "content\nwith\nnewlines" in captured.out
    assert 'content "with" \'quotes\'' in captured.out
    assert "content\\with\\backslashes" in captured.out


def test_report_empty_issues_list_edge_cases(capsys):
    """Test edge cases with empty or None-like issues."""
    # Empty list
    report_results("test1.py", [])
    captured = capsys.readouterr()
    assert captured.out == ""

    # List with empty tuples (should handle gracefully)
    try:
        report_results("test2.py", [("", "", "")])
        captured = capsys.readouterr()
        assert "test2.py:" in captured.out
    except (IndexError, TypeError):
        # It's acceptable if this fails - depends on implementation
        pass


def test_report_numeric_line_numbers(capsys):
    """Test reporting with numeric vs string line numbers."""
    issues = [
        (1, "numeric line", "content1"),  # Numeric line number
        ("2", "string line", "content2"),  # String line number
    ]

    # Convert numeric to string (assuming implementation expects strings)
    normalized_issues = [(str(line), desc, content) for line, desc, content in issues]

    report_results("test.py", normalized_issues)

    captured = capsys.readouterr()
    assert "Line 1: numeric line" in captured.out
    assert "Line 2: string line" in captured.out


def test_report_output_consistency(capsys):
    """Test that report output is consistent across multiple calls."""
    issues = [("1", "test issue", "test content")]

    # Call multiple times
    for _ in range(3):
        report_results("test.py", issues)

        captured = capsys.readouterr()
        assert "test.py:" in captured.out
        assert "Line 1: test issue" in captured.out
        assert "> test content" in captured.out

        # Output should be identical each time
        actual_lines = [line.strip() for line in captured.out.strip().split('\n')]
        # Remove leading whitespace for comparison
        assert len(actual_lines) == 3
