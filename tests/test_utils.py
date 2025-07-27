"""
Unit tests for the utils module.
"""

import pytest
from pathlib import Path
from unittest.mock import patch, mock_open, MagicMock
import tempfile
import os

from src.utils import (
    read_file_safely,
    detect_docstring_start,
    is_docstring_line,
    should_skip_line,
    should_skip_notebook_line,
    check_line_for_patterns,
    report_results,
)


class TestReadFileSafely:
    """Test the read_file_safely function."""

    def test_read_existing_file(self):
        """Test reading an existing file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("line1\nline2\nline3\n")
            temp_path = f.name

        try:
            result = read_file_safely(Path(temp_path))
            assert result == ["line1\n", "line2\n", "line3\n"]
        finally:
            os.unlink(temp_path)

    def test_read_nonexistent_file(self):
        """Test reading a nonexistent file."""
        result = read_file_safely(Path("nonexistent_file.py"))
        assert result == []

    def test_read_file_unicode_error(self, capsys):
        """Test handling of unicode decode errors."""
        with patch("builtins.open", mock_open()) as mock_file:
            mock_file.side_effect = UnicodeDecodeError("utf-8", b"", 0, 1, "test error")

            result = read_file_safely(Path("test.py"))

            assert result == []
            captured = capsys.readouterr()
            assert "Warning: Could not read" in captured.out
            assert "encoding issues" in captured.out

    def test_read_empty_file(self):
        """Test reading an empty file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            temp_path = f.name

        try:
            result = read_file_safely(Path(temp_path))
            assert result == []
        finally:
            os.unlink(temp_path)


class TestDetectDocstringStart:
    """Test the detect_docstring_start function."""

    def test_triple_quote_docstring_start(self):
        """Test detection of triple quote docstring start."""
        assert detect_docstring_start('"""This is a docstring') == '"""'
        assert detect_docstring_start("'''This is a docstring") == "'''"
        assert detect_docstring_start('    """Indented docstring') == '"""'
        assert detect_docstring_start("    '''Indented docstring") == "'''"

    def test_complete_docstring_single_line(self):
        """Test complete docstring on single line (should return None)."""
        assert detect_docstring_start('"""Complete docstring"""') is None
        assert detect_docstring_start("'''Complete docstring'''") is None

    def test_no_docstring(self):
        """Test lines without docstring markers."""
        assert detect_docstring_start("regular code line") is None
        assert detect_docstring_start("# comment") is None
        assert detect_docstring_start("") is None
        assert detect_docstring_start('print("hello")') is None

    def test_docstring_in_string_literal(self):
        """Test docstring markers inside string literals."""
        assert detect_docstring_start('text = "This has """ inside"') is None
        assert detect_docstring_start("text = 'This has ''' inside'") is None


class TestIsDocstringLine:
    """Test the is_docstring_line function."""

    def test_docstring_detection_flow(self):
        """Test the complete docstring detection flow."""
        # Start outside docstring
        in_docstring, marker = is_docstring_line('"""Start docstring', False, None)
        assert in_docstring is True
        assert marker == '"""'

        # Continue inside docstring
        in_docstring, marker = is_docstring_line("docstring content", True, '"""')
        assert in_docstring is True
        assert marker == '"""'

        # End docstring
        in_docstring, marker = is_docstring_line('end docstring"""', True, '"""')
        assert in_docstring is False
        assert marker is None

    def test_single_quote_docstring(self):
        """Test single quote docstring detection."""
        in_docstring, marker = is_docstring_line("'''Start docstring", False, None)
        assert in_docstring is True
        assert marker == "'''"

        in_docstring, marker = is_docstring_line("end docstring'''", True, "'''")
        assert in_docstring is False
        assert marker is None

    def test_no_docstring_detection(self):
        """Test when no docstring is detected."""
        in_docstring, marker = is_docstring_line("regular code", False, None)
        assert in_docstring is False
        assert marker is None

    def test_maintain_state_inside_docstring(self):
        """Test maintaining state when inside docstring."""
        in_docstring, marker = is_docstring_line(
            "content inside docstring", True, '"""'
        )
        assert in_docstring is True
        assert marker == '"""'


class TestShouldSkipLine:
    """Test the should_skip_line function."""

    def test_skip_comments(self):
        """Test skipping comment lines."""
        assert should_skip_line("# This is a comment", False) is True
        assert should_skip_line("    # Indented comment", False) is True
        assert should_skip_line("#", False) is True

    def test_skip_empty_lines(self):
        """Test skipping empty lines."""
        assert should_skip_line("", False) is True
        assert should_skip_line("   ", False) is True
        assert should_skip_line("\t\t", False) is True

    def test_skip_docstring_lines(self):
        """Test skipping lines inside docstrings."""
        assert should_skip_line("any content", True) is True
        assert should_skip_line("", True) is True
        assert should_skip_line("# even comments", True) is True

    def test_do_not_skip_code_lines(self):
        """Test not skipping actual code lines."""
        assert should_skip_line('print("hello")', False) is False
        assert should_skip_line("def function():", False) is False
        assert should_skip_line("    return value", False) is False

    def test_edge_cases(self):
        """Test edge cases for line skipping."""
        # Line starting with # but not a comment (in string)
        assert should_skip_line('text = "# not a comment"', False) is False
        # Mixed whitespace
        assert should_skip_line("\t \t", False) is True


class TestShouldSkipNotebookLine:
    """Test the should_skip_notebook_line function."""

    def test_skip_comments(self):
        """Test skipping notebook comment lines."""
        assert should_skip_notebook_line("# This is a comment") is True
        assert should_skip_notebook_line("    # Indented comment") is True

    def test_skip_magic_commands(self):
        """Test skipping magic commands."""
        assert should_skip_notebook_line("%matplotlib inline") is True
        assert should_skip_notebook_line("%%sql") is True
        assert should_skip_notebook_line("    %cd /tmp") is True

    def test_do_not_skip_code_lines(self):
        """Test not skipping regular code lines."""
        assert should_skip_notebook_line('print("hello")') is False
        assert should_skip_notebook_line("df.show()") is False
        assert (
            should_skip_notebook_line('result = spark.sql("SELECT * FROM table")')
            is False
        )

    def test_edge_cases(self):
        """Test edge cases for notebook line skipping."""
        # % in string literals
        assert should_skip_notebook_line('text = "This has % symbol"') is False
        # # in string literals
        assert should_skip_notebook_line('text = "This has # symbol"') is False


class TestCheckLineForPatterns:
    """Test the check_line_for_patterns function."""

    def test_single_match(self):
        """Test matching single pattern."""
        patterns = [(r"display\s*\(", "display function")]
        line = "display(df)"

        matches = check_line_for_patterns(line, patterns)

        assert len(matches) == 1
        assert matches[0] == ("display function", "display(df)")

    def test_multiple_matches(self):
        """Test matching multiple patterns."""
        patterns = [
            (r"display\s*\(", "display function"),
            (r"df\.show\s*\(", "show method"),
        ]
        line = "display(df.show())"

        matches = check_line_for_patterns(line, patterns)

        assert len(matches) == 2
        assert ("display function", "display(df.show())") in matches
        assert ("show method", "display(df.show())") in matches

    def test_no_matches(self):
        """Test when no patterns match."""
        patterns = [(r"display\s*\(", "display function")]
        line = 'print("hello world")'

        matches = check_line_for_patterns(line, patterns)

        assert len(matches) == 0

    def test_case_insensitive_matching(self):
        """Test case-insensitive pattern matching."""
        patterns = [(r"DISPLAY\s*\(", "display function")]
        line = "display(df)"

        matches = check_line_for_patterns(line, patterns)

        assert len(matches) == 1
        assert matches[0] == ("display function", "display(df)")

    def test_empty_patterns(self):
        """Test with empty patterns list."""
        patterns = []
        line = "display(df)"

        matches = check_line_for_patterns(line, patterns)

        assert len(matches) == 0

    def test_complex_patterns(self):
        """Test with complex regex patterns."""
        patterns = [
            (r"^\s*\w+\.collect\s*\(\s*\)\s*$", "collect without assignment"),
            (r"^\s*\w+\.count\s*\(\s*\)\s*$", "count without assignment"),
            (r"dbutils\.notebook\.exit\s*\(\s*\)", "dbutils exit"),
        ]

        # Test collect pattern
        matches = check_line_for_patterns("df.collect()", patterns)
        assert len(matches) == 1
        assert matches[0][0] == "collect without assignment"

        # Test count pattern
        matches = check_line_for_patterns("df.count()", patterns)
        assert len(matches) == 1
        assert matches[0][0] == "count without assignment"

        # Test dbutils pattern
        matches = check_line_for_patterns("dbutils.notebook.exit()", patterns)
        assert len(matches) == 1
        assert matches[0][0] == "dbutils exit"


class TestReportResults:
    """Test the report_results function."""

    def test_report_with_issues(self, capsys):
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

    def test_report_no_issues(self, capsys):
        """Test reporting when no issues are found."""
        issues = []

        report_results("test_file.py", issues)

        captured = capsys.readouterr()
        assert captured.out == ""

    def test_report_different_file_types(self, capsys):
        """Test reporting for different file types."""
        issues = [("Cell 1, Line 3", "display function", "display(df)")]

        report_results("notebook.ipynb", issues)

        captured = capsys.readouterr()
        assert "notebook.ipynb:" in captured.out
        assert "Line Cell 1, Line 3" in captured.out

    def test_report_special_characters(self, capsys):
        """Test reporting with special characters in file names and content."""
        issues = [("1", "pattern", "special chars: àáâã")]

        report_results("file with spaces.py", issues)

        captured = capsys.readouterr()
        assert "file with spaces.py:" in captured.out
        assert "special chars: àáâã" in captured.out
