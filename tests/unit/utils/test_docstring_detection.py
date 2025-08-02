"""
Unit tests for utils docstring detection functionality.
"""

import pytest
from sparkgrep.utils import detect_docstring_start, is_docstring_line


# Detect Docstring Start Tests

def test_triple_quote_docstring_start():
    """Test detection of triple quote docstring start."""
    assert detect_docstring_start('"""This is a docstring') == '"""'
    assert detect_docstring_start("'''This is a docstring") == "'''"
    assert detect_docstring_start('    """Indented docstring') == '"""'
    assert detect_docstring_start("    '''Indented docstring") == "'''"


def test_complete_docstring_single_line():
    """Test complete docstring on single line (should return None)."""
    assert detect_docstring_start('"""Complete docstring"""') is None
    assert detect_docstring_start("'''Complete docstring'''") is None


def test_no_docstring():
    """Test lines without docstring markers."""
    assert detect_docstring_start("regular code line") is None
    assert detect_docstring_start("# comment") is None
    assert detect_docstring_start("") is None
    assert detect_docstring_start('print("hello")') is None


def test_docstring_in_string_literal():
    """Test docstring markers inside string literals."""
    assert detect_docstring_start('text = "This has """ inside"') is None
    assert detect_docstring_start("text = 'This has ''' inside'") is None


def test_docstring_start_edge_cases():
    """Test edge cases for docstring detection."""
    # Multiple quotes in one line (but starting docstring)
    assert detect_docstring_start('"""Start""" # but this continues') == '"""'

    # Mixed quote types
    assert detect_docstring_start('"""Start with double quotes') == '"""'
    assert detect_docstring_start("'''Start with single quotes") == "'''"

    # Whitespace variations
    assert detect_docstring_start('\t\t"""Tabs before docstring') == '"""'
    assert detect_docstring_start('   """Spaces before docstring') == '"""'


def test_docstring_false_positives():
    """Test cases that should not be detected as docstring starts."""
    # Quotes inside strings should not trigger docstring detection
    assert detect_docstring_start('print("She said """hello"""")') is None
    assert detect_docstring_start("print('He said '''world'''')") is None

    # Comments with quotes
    assert detect_docstring_start('# This is a comment with """quotes"""') is None


def test_docstring_start_with_escapes():
    """Test docstring detection with escaped quotes."""
    assert detect_docstring_start('text = "He said \\"hello\\""') is None
    assert detect_docstring_start('"""This is a real docstring') == '"""'


def test_docstring_start_mixed_indentation():
    """Test docstring start detection with mixed indentation."""
    assert detect_docstring_start('\t   """Mixed tabs and spaces') == '"""'
    assert detect_docstring_start('   \t"""Spaces then tabs') == '"""'


# Is Docstring Line Tests

def test_docstring_detection_flow():
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


def test_single_quote_docstring():
    """Test single quote docstring detection."""
    in_docstring, marker = is_docstring_line("'''Start docstring", False, None)
    assert in_docstring is True
    assert marker == "'''"

    in_docstring, marker = is_docstring_line("end docstring'''", True, "'''")
    assert in_docstring is False
    assert marker is None


def test_no_docstring_detection():
    """Test when no docstring is detected."""
    in_docstring, marker = is_docstring_line("regular code", False, None)
    assert in_docstring is False
    assert marker is None


def test_maintain_state_inside_docstring():
    """Test maintaining state when inside docstring."""
    in_docstring, marker = is_docstring_line(
        "content inside docstring", True, '"""'
    )
    assert in_docstring is True
    assert marker == '"""'


def test_docstring_line_complex_scenarios():
    """Test complex docstring scenarios."""
    # Nested quotes inside docstring
    in_docstring, marker = is_docstring_line('"""Start docstring', False, None)
    assert in_docstring is True
    assert marker == '"""'

    # Content with quotes inside docstring
    in_docstring, marker = is_docstring_line('This has "quotes" inside', True, '"""')
    assert in_docstring is True
    assert marker == '"""'

    # End with content after closing quotes
    in_docstring, marker = is_docstring_line('End docstring""" # comment', True, '"""')
    assert in_docstring is False
    assert marker is None


def test_docstring_multiline_edge_cases():
    """Test edge cases with multiline docstrings."""
    # Start and end on same line (no docstring detected)
    in_docstring, marker = is_docstring_line('"""Single line docstring"""', False, None)
    assert in_docstring is False
    assert marker is None

    # Mixed quote types ending
    in_docstring, marker = is_docstring_line('End with different quotes\'\'\'', True, '"""')
    assert in_docstring is True  # Should maintain state, wrong ending marker
    assert marker == '"""'


def test_docstring_with_escaped_quotes():
    """Test docstring detection with escaped quotes."""
    # Escaped quotes should not end docstring
    in_docstring, marker = is_docstring_line('Content with \\"escaped\\" quotes', True, '"""')
    assert in_docstring is True
    assert marker == '"""'

    # Real end should work
    in_docstring, marker = is_docstring_line('Real end"""', True, '"""')
    assert in_docstring is False
    assert marker is None


def test_docstring_unicode_content():
    """Test docstring detection with unicode content."""
    # Unicode content inside docstring
    in_docstring, marker = is_docstring_line('Unicode: 🎉 émojis', True, '"""')
    assert in_docstring is True
    assert marker == '"""'

    # Unicode markers
    in_docstring, marker = is_docstring_line('"""Start with unicode 🎉', False, None)
    assert in_docstring is True
    assert marker == '"""'


def test_docstring_empty_lines():
    """Test docstring detection with empty lines."""
    # Empty line inside docstring
    in_docstring, marker = is_docstring_line('', True, '"""')
    assert in_docstring is True
    assert marker == '"""'

    # Whitespace-only line inside docstring
    in_docstring, marker = is_docstring_line('   \t  ', True, '"""')
    assert in_docstring is True
    assert marker == '"""'
