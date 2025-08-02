"""
Unit tests for utils line processing functionality.
"""

import pytest
from sparkgrep.utils import should_skip_line, should_skip_notebook_line


# Should Skip Line Tests

def test_skip_comments():
    """Test skipping comment lines."""
    assert should_skip_line("# This is a comment", False) is True
    assert should_skip_line("    # Indented comment", False) is True
    assert should_skip_line("#", False) is True


def test_skip_empty_lines():
    """Test skipping empty lines."""
    assert should_skip_line("", False) is True
    assert should_skip_line("   ", False) is True
    assert should_skip_line("\t\t", False) is True


def test_skip_docstring_lines():
    """Test skipping lines inside docstrings."""
    assert should_skip_line("any content", True) is True
    assert should_skip_line("", True) is True
    assert should_skip_line("# even comments", True) is True


def test_do_not_skip_code_lines():
    """Test not skipping actual code lines."""
    assert should_skip_line('print("hello")', False) is False
    assert should_skip_line("def function():", False) is False
    assert should_skip_line("    return value", False) is False


def test_skip_line_edge_cases():
    """Test edge cases for line skipping."""
    # Line starting with # but not a comment (in string)
    assert should_skip_line('text = "# not a comment"', False) is False
    # Mixed whitespace
    assert should_skip_line("\t \t", False) is True
    # Only whitespace with newline
    assert should_skip_line("   \n", False) is True


def test_skip_line_whitespace_variations():
    """Test various whitespace scenarios."""
    whitespace_variations = [
        "",  # Empty
        " ",  # Single space
        "\t",  # Single tab
        "   ",  # Multiple spaces
        "\t\t",  # Multiple tabs
        " \t ",  # Mixed spaces and tabs
        "\n",  # Just newline
        " \n",  # Space then newline
        "\t\n",  # Tab then newline
    ]

    for line in whitespace_variations:
        assert should_skip_line(line, False) is True


def test_skip_line_comment_variations():
    """Test various comment line patterns."""
    comment_patterns = [
        "# Simple comment",
        "#Comment without space",
        "    # Indented comment",
        "\t# Tab indented comment",
        "# Comment with special chars: @#$%",
        "# TODO: Fix this",
        "# FIXME: Bug here",
        "# NOTE: Important info",
    ]

    for comment in comment_patterns:
        assert should_skip_line(comment, False) is True


def test_skip_line_unicode_content():
    """Test line skipping with unicode content."""
    # Unicode in comments should still skip
    assert should_skip_line("# Comment with émojis 🎉", False) is True

    # Unicode in code should not skip
    assert should_skip_line('text = "Unicode: 🎉"', False) is False


def test_skip_line_complex_indentation():
    """Test line skipping with complex indentation."""
    # Various indentation patterns
    indented_lines = [
        "    # Four spaces comment",
        "\t# Tab comment",
        "\t    # Mixed indentation comment",
        "        # Deep indentation comment",
    ]

    for line in indented_lines:
        assert should_skip_line(line, False) is True


# Should Skip Notebook Line Tests

def test_skip_notebook_comments():
    """Test skipping notebook comment lines."""
    assert should_skip_notebook_line("# This is a comment") is True
    assert should_skip_notebook_line("    # Indented comment") is True


def test_skip_magic_commands():
    """Test skipping magic commands."""
    assert should_skip_notebook_line("%matplotlib inline") is True
    assert should_skip_notebook_line("%%sql") is True
    assert should_skip_notebook_line("    %cd /tmp") is True


def test_do_not_skip_notebook_code_lines():
    """Test not skipping regular code lines."""
    assert should_skip_notebook_line('print("hello")') is False
    assert should_skip_notebook_line("df.show()") is False
    assert (
        should_skip_notebook_line('result = spark.sql("SELECT * FROM table")')
        is False
    )


def test_skip_notebook_line_edge_cases():
    """Test edge cases for notebook line skipping."""
    # % in string literals
    assert should_skip_notebook_line('text = "This has % symbol"') is False
    # # in string literals
    assert should_skip_notebook_line('text = "This has # symbol"') is False


def test_skip_notebook_magic_variations():
    """Test various magic command patterns."""
    magic_commands = [
        "%pwd",
        "%ls",
        "%time some_function()",
        "%matplotlib inline",
        "%%sql SELECT * FROM table",
        "%%bash echo hello",
        "%%capture output",
        "%run ./another_notebook.ipynb",
    ]

    for cmd in magic_commands:
        assert should_skip_notebook_line(cmd) is True
        assert should_skip_notebook_line(f"  {cmd}") is True  # With indentation


def test_notebook_line_false_positives():
    """Test cases that should not be skipped in notebooks."""
    false_positives = [
        'print("Usage: %s" % script_name)',
        'percentage = 50%',
        'sql_query = "SELECT * FROM table"',
        'url = "https://example.com#section"',
        'comment_in_string = "This is a # comment"',
    ]

    for line in false_positives:
        assert should_skip_notebook_line(line) is False


def test_notebook_advanced_magic_commands():
    """Test advanced magic command patterns."""
    # Test only single line magics
    single_line_magics = [
        "%load_ext autoreload",
        "%autoreload 2",
        "%%writefile test.py",
        "%%capture --no-stderr",
        "%who_ls DataFrame",
    ]

    for magic in single_line_magics:
        assert should_skip_notebook_line(magic) is True


def test_notebook_line_with_special_characters():
    """Test notebook line processing with special characters."""
    # Test cases with expected results
    test_cases = [
        ("# Comment with special chars: @#$%^&*()", True),
        ("%matplotlib --help", True),
        ("%%bash", True),  # Just the magic part
        ('text = "Not a % magic command"', False),
        ('url = "http://example.com#anchor"', False),
    ]

    for line, expected in test_cases:
        assert should_skip_notebook_line(line) is expected


def test_notebook_line_unicode_magic():
    """Test notebook line processing with unicode in magic commands."""
    # Test unicode lines directly
    assert should_skip_notebook_line("# Unicode comment: 🎉") is True
    assert should_skip_notebook_line("%cd /path/with/émojis") is True
    assert should_skip_notebook_line("%%bash") is True


def test_notebook_line_empty_and_whitespace():
    """Test notebook line processing with empty and whitespace lines."""
    # Empty lines in notebooks should not be skipped (different from Python files)
    assert should_skip_notebook_line("") is False
    assert should_skip_notebook_line("   ") is False
    assert should_skip_notebook_line("\t\t") is False

    # But magic commands with whitespace should still be skipped
    assert should_skip_notebook_line("  %pwd  ") is True
    assert should_skip_notebook_line("\t%%sql\t") is True
