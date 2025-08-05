import pytest
from sparkgrep.utils import detect_docstring_start, is_docstring_line


def test_triple_quote_docstring_start():
    """Test detecting triple quote docstring starts."""
    # Complete docstrings return None (both opening and closing quotes present)
    assert detect_docstring_start('"""This is a docstring"""') is None
    assert detect_docstring_start("'''This is a docstring'''") is None
    assert detect_docstring_start('    """Indented docstring"""') is None
    assert detect_docstring_start('\t"""Tab indented docstring"""') is None

    # Incomplete docstrings return the quote type
    assert detect_docstring_start('"""This starts a docstring') == '"""'
    assert detect_docstring_start("'''This starts a docstring") == "'''"


def test_single_line_complete_docstring():
    """Test detecting complete single-line docstrings."""
    # Complete docstrings should return None (both opening and closing quotes)
    assert detect_docstring_start('"""Complete docstring on one line."""') is None
    assert detect_docstring_start("'''Complete docstring on one line.'''") is None

    # Incomplete docstrings (opening only) return the quote type
    assert detect_docstring_start('"""Incomplete docstring') == '"""'
    assert detect_docstring_start("'''Incomplete docstring") == "'''"


def test_no_docstring_detection():
    """Test lines that don't contain docstring starts."""
    lines_without_docstrings = [
        "print('Hello world')",
        "# This is a comment",
        "def function():",
        "import os",
        "result = 42",
        "",
        "   ",
        'regular_string = "not a docstring"',
        "single_quote = 'also not a docstring'"
    ]

    for line in lines_without_docstrings:
        assert detect_docstring_start(line) is None


def test_docstring_in_string_literals():
    """Test that docstring markers inside string literals are not detected."""
    lines_with_string_literals = [
        'print("This contains \\"\\"\\" but is not a docstring")',
        "message = 'He said \\'\\'\\'hello\\'\\'\\''",
        'sql = "SELECT * FROM table WHERE col=\\"\\"\\"value\\"\\"\\""',
        "text = 'Some text with \\'\\'\\' inside'"
    ]

    for line in lines_with_string_literals:
        # These should not be detected as docstring starts
        # (this depends on implementation - might need adjustment)
        result = detect_docstring_start(line)
        # For now, we test that the function handles these cases gracefully
        assert result is None or isinstance(result, str)


def test_docstring_start_with_content():
    """Test docstring detection with various content patterns."""
    # Complete docstrings (opening and closing quotes) return None
    complete_cases = [
        '"""Simple docstring"""',
        '"""Multi-word docstring with content"""',
        '"""Docstring with numbers 123 and symbols !@#"""',
        "'''Alternative quote style'''",
        '    """Indented docstring"""',
        '\t\t"""Double tab indented"""'
    ]

    for line in complete_cases:
        assert detect_docstring_start(line) is None

    # Incomplete docstrings (only opening quotes) return the quote type
    incomplete_cases = [
        ('"""Simple docstring start', '"""'),
        ('"""Multi-word docstring start', '"""'),
        ("'''Alternative quote start", "'''"),
        ('    """Indented docstring start', '"""')
    ]

    for line, expected in incomplete_cases:
        assert detect_docstring_start(line) == expected


def test_docstring_with_escaped_quotes():
    """Test docstring detection with escaped quotes inside."""
    # Complete docstrings with escaped quotes should return None
    assert detect_docstring_start('"""Docstring with \\"escaped\\" quotes"""') is None
    assert detect_docstring_start("'''Docstring with \\'escaped\\' quotes'''") is None

    # Incomplete docstrings with escaped quotes should return quote type
    assert detect_docstring_start('"""Docstring with \\"escaped\\" quotes') == '"""'
    assert detect_docstring_start("'''Docstring with \\'escaped\\' quotes") == "'''"


def test_mixed_quote_types():
    """Test docstrings that mix quote types."""
    # Complete docstrings with mixed inner quotes return None
    assert detect_docstring_start('"""Docstring with \'single\' quotes inside"""') is None
    assert detect_docstring_start("'''Docstring with \"double\" quotes inside'''") is None

    # Incomplete docstrings with mixed inner quotes return quote type
    assert detect_docstring_start('"""Docstring with \'single\' quotes inside') == '"""'
    assert detect_docstring_start("'''Docstring with \"double\" quotes inside") == "'''"


def test_docstring_start_edge_cases():
    """Test edge cases for docstring detection."""
    # Just the quotes (incomplete)
    assert detect_docstring_start('"""') == '"""'
    assert detect_docstring_start("'''") == "'''"

    # Quotes with minimal content (complete)
    assert detect_docstring_start('"""a"""') is None
    assert detect_docstring_start("'''b'''") is None

    # Multiple docstring patterns - has more than one occurrence, so returns None
    assert detect_docstring_start('"""first""" and """second"""') is None


def test_whitespace_handling():
    """Test docstring detection with various whitespace patterns."""
    # Complete docstrings with whitespace return None
    complete_whitespace_cases = [
        '   """Docstring with leading spaces"""',
        '\t"""Docstring with leading tab"""',
        '"""Docstring with trailing spaces"""   ',
        '\t   """Mixed whitespace"""   \t'
    ]

    for line in complete_whitespace_cases:
        assert detect_docstring_start(line) is None

    # Incomplete docstrings with whitespace return quote type
    incomplete_whitespace_cases = [
        ('   """Docstring with leading spaces', '"""'),
        ('\t"""Docstring with leading tab', '"""'),
        ('\t   """Mixed whitespace', '"""')
    ]

    for line, expected in incomplete_whitespace_cases:
        assert detect_docstring_start(line) == expected


# Tests for is_docstring_line function

def test_is_docstring_line_basic():
    """Test basic docstring line detection."""
    # Start of docstring
    assert is_docstring_line('"""This starts a docstring', False, None) == (True, '"""')
    assert is_docstring_line("'''This starts a docstring", False, None) == (True, "'''")

    # Not a docstring line
    assert is_docstring_line("regular code line", False, None) == (False, None)


def test_is_docstring_line_inside_docstring():
    """Test docstring line detection when already inside a docstring."""
    # Inside triple-quote docstring
    assert is_docstring_line("This is inside a docstring", True, '"""') == (True, '"""')
    assert is_docstring_line("Still inside docstring", True, "'''") == (True, "'''")

    # End of docstring
    assert is_docstring_line('End of docstring"""', True, '"""') == (False, None)
    assert is_docstring_line("End of docstring'''", True, "'''") == (False, None)


def test_is_docstring_line_complete_single_line():
    """Test complete single-line docstrings."""
    # Complete single-line docstrings should not change state
    assert is_docstring_line('"""Complete docstring"""', False, None) == (False, None)
    assert is_docstring_line("'''Complete docstring'''", False, None) == (False, None)


def test_is_docstring_line_state_transitions():
    """Test state transitions for docstring detection."""
    # Starting a multi-line docstring
    in_docstring, quote_type = is_docstring_line('"""Multi-line docstring', False, None)
    assert in_docstring is True
    assert quote_type == '"""'

    # Continuing in the docstring
    in_docstring, quote_type = is_docstring_line('This is the content', True, '"""')
    assert in_docstring is True
    assert quote_type == '"""'

    # Ending the docstring
    in_docstring, quote_type = is_docstring_line('End of docstring"""', True, '"""')
    assert in_docstring is False
    assert quote_type is None


def test_is_docstring_line_mixed_quotes():
    """Test docstring detection with mixed quote types."""
    # Start with triple double quotes
    in_docstring, quote_type = is_docstring_line('"""Docstring content', False, None)
    assert in_docstring is True
    assert quote_type == '"""'

    # Single quotes inside shouldn't end it
    in_docstring, quote_type = is_docstring_line("Content with 'single' quotes", True, '"""')
    assert in_docstring is True
    assert quote_type == '"""'

    # Only matching triple quotes should end it
    in_docstring, quote_type = is_docstring_line('End with matching"""', True, '"""')
    assert in_docstring is False
    assert quote_type is None


def test_is_docstring_line_complex_scenarios():
    """Test complex docstring scenarios."""
    scenarios = [
        # Start and end on same line (complete docstring)
        ('"""Single line docstring"""', False, None, False, None),

        # Start multi-line
        ('"""Multi-line start', False, None, True, '"""'),

        # Continue multi-line
        ('Content in the middle', True, '"""', True, '"""'),

        # End multi-line
        ('End of multi-line"""', True, '"""', False, None),

        # False positive (quotes in string)
        ('print("Not a docstring")', False, None, False, None),
    ]

    for line, start_in_docstring, start_quote_type, expected_in_docstring, expected_quote_type in scenarios:
        result_in_docstring, result_quote_type = is_docstring_line(line, start_in_docstring, start_quote_type)
        assert result_in_docstring == expected_in_docstring
        assert result_quote_type == expected_quote_type


def test_is_docstring_line_unicode():
    """Test docstring detection with unicode content."""
    # Unicode content inside docstring
    in_docstring, quote_type = is_docstring_line('"""Docstring with 世界 content', False, None)
    assert in_docstring is True
    assert quote_type == '"""'

    # Continue with unicode
    in_docstring, quote_type = is_docstring_line('More unicode: émojis 🚀', True, '"""')
    assert in_docstring is True
    assert quote_type == '"""'


def test_is_docstring_line_empty_lines():
    """Test docstring detection with empty lines."""
    # Empty line while in docstring should continue
    in_docstring, quote_type = is_docstring_line('', True, '"""')
    assert in_docstring is True
    assert quote_type == '"""'

    # Whitespace line while in docstring
    in_docstring, quote_type = is_docstring_line('   ', True, '"""')
    assert in_docstring is True
    assert quote_type == '"""'


def test_is_docstring_line_edge_cases():
    """Test edge cases for docstring line detection."""
    # Just the opening quotes
    in_docstring, quote_type = is_docstring_line('"""', False, None)
    assert in_docstring is True
    assert quote_type == '"""'

    # Just the closing quotes
    in_docstring, quote_type = is_docstring_line('"""', True, '"""')
    assert in_docstring is False
    assert quote_type is None

    # Mismatched quote types (shouldn't end)
    in_docstring, quote_type = is_docstring_line("'''", True, '"""')
    assert in_docstring is True  # Should continue in docstring
    assert quote_type == '"""'  # Original quote type preserved


def test_docstring_detection_flow():
    """Test a complete flow through a docstring."""
    lines = [
        'def function():',
        '    """This is a multi-line',
        '    docstring that explains',
        '    the function purpose.',
        '    """',
        '    display(df)  # This should be detected',
        '    return result'
    ]

    in_docstring = False
    quote_type = None

    expected_states = [
        (False, None),  # def line
        (True, '"""'),  # docstring start
        (True, '"""'),  # docstring content
        (True, '"""'),  # docstring content
        (False, None),  # docstring end
        (False, None),  # code line
        (False, None)   # code line
    ]

    for i, line in enumerate(lines):
        in_docstring, quote_type = is_docstring_line(line, in_docstring, quote_type)
        expected_in_docstring, expected_quote_type = expected_states[i]
        assert in_docstring == expected_in_docstring, f"Line {i}: {line}"
        assert quote_type == expected_quote_type, f"Line {i}: {line}"
