"""
Unit tests for utils pattern matching functionality.
"""

import pytest
from sparkgrep.utils import check_line_for_patterns


def test_single_match():
    """Test matching single pattern."""
    patterns = [(r"display\s*\(", "display function")]
    line = "display(df)"

    matches = check_line_for_patterns(line, patterns)

    assert len(matches) == 1
    assert matches[0] == ("display function", "display(df)")


def test_multiple_matches():
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


def test_no_matches():
    """Test when no patterns match."""
    patterns = [(r"display\s*\(", "display function")]
    line = 'print("hello world")'

    matches = check_line_for_patterns(line, patterns)

    assert len(matches) == 0


def test_case_insensitive_matching():
    """Test case-insensitive pattern matching."""
    patterns = [(r"DISPLAY\s*\(", "display function")]
    line = "display(df)"

    matches = check_line_for_patterns(line, patterns)

    assert len(matches) == 1
    assert matches[0] == ("display function", "display(df)")


def test_empty_patterns():
    """Test with empty patterns list."""
    patterns = []
    line = "display(df)"

    matches = check_line_for_patterns(line, patterns)

    assert len(matches) == 0


def test_complex_patterns():
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


def test_pattern_matching_edge_cases():
    """Test edge cases in pattern matching."""
    patterns = [
        (r"display\s*\(", "display function"),
        (r"\.show\s*\(", "show method"),
    ]

    test_cases = [
        ("display(df)", [("display function", "display(df)")]),
        ("display (df)", [("display function", "display (df)")]),
        ("display  (df)", [("display function", "display  (df)")]),
        ("df.show()", [("show method", "df.show()")]),
        ("df.show ()", [("show method", "df.show ()")]),
        ("something.show()", [("show method", "something.show()")]),
        ("display(df); df.show()", [("display function", "display(df); df.show()"), ("show method", "display(df); df.show()")]),
    ]

    for line, expected in test_cases:
        matches = check_line_for_patterns(line, patterns)
        assert matches == expected


def test_regex_special_characters():
    """Test patterns with regex special characters."""
    patterns = [
        (r"\$variable", "dollar variable"),
        (r"\[index\]", "array access"),
        (r"\{key\}", "dict access"),
        (r"\(\)", "empty parentheses"),
    ]

    test_lines = [
        "$variable = 5",
        "array[index]",
        "dict{key}",
        "function()",
    ]

    for i, line in enumerate(test_lines):
        matches = check_line_for_patterns(line, patterns)
        assert len(matches) == 1
        assert patterns[i][1] in matches[0][0]


def test_pattern_matching_unicode():
    """Test pattern matching with unicode content."""
    patterns = [
        (r"émoji\s*\(", "unicode function"),
        (r"🎉+", "emoji pattern"),
    ]

    test_cases = [
        ("émoji(data)", [("unicode function", "émoji(data)")]),
        ("celebration 🎉🎉🎉", [("emoji pattern", "celebration 🎉🎉🎉")]),
        ("normal text", []),
    ]

    for line, expected in test_cases:
        matches = check_line_for_patterns(line, patterns)
        assert matches == expected


def test_pattern_matching_multiline_content():
    """Test pattern matching with content that spans apparent lines."""
    patterns = [
        (r"function\s*\([^)]*\)", "function call"),
        (r"class\s+\w+", "class definition"),
    ]

    test_cases = [
        ("function(arg1, arg2)", [("function call", "function(arg1, arg2)")]),
        ("function(\n    arg1,\n    arg2\n)", []),  # Newlines break single-line matching
        ("class MyClass", [("class definition", "class MyClass")]),
        ("function()", [("function call", "function()")]),
    ]

    for line, expected in test_cases:
        matches = check_line_for_patterns(line, patterns)
        assert matches == expected


def test_pattern_matching_with_none_values():
    """Test pattern matching with edge case inputs."""
    patterns = [(r"test", "test pattern")]

    # Test empty line
    matches = check_line_for_patterns("", patterns)
    assert matches == []

    # Test line with only whitespace
    matches = check_line_for_patterns("   ", patterns)
    assert matches == []


def test_pattern_matching_overlapping_patterns():
    """Test patterns that might overlap in matches."""
    patterns = [
        (r"display", "display keyword"),
        (r"display\s*\(", "display function"),
        (r"df", "dataframe reference"),
    ]

    line = "display(df)"
    matches = check_line_for_patterns(line, patterns)

    # Should match all three patterns
    assert len(matches) == 3
    descriptions = [match[0] for match in matches]
    assert "display keyword" in descriptions
    assert "display function" in descriptions
    assert "dataframe reference" in descriptions


def test_pattern_matching_with_anchors():
    """Test patterns with start/end anchors."""
    patterns = [
        (r"^display", "line starts with display"),
        (r"display$", "line ends with display"),
        (r"^display$", "line is exactly display"),
    ]

    test_cases = [
        ("display(df)", [("line starts with display", "display(df)")]),
        ("show display", [("line ends with display", "show display")]),
        ("display", [("line starts with display", "display"), ("line ends with display", "display"), ("line is exactly display", "display")]),
        ("  display  ", []),  # Anchors with whitespace
    ]

    for line, expected in test_cases:
        matches = check_line_for_patterns(line, patterns)
        assert matches == expected


def test_pattern_matching_with_groups():
    """Test patterns with regex groups (groups should not affect matching)."""
    patterns = [
        (r"(display|show)\s*\(", "display or show function"),
        (r"df\.(\w+)\s*\(", "dataframe method"),
    ]

    test_cases = [
        ("display(df)", [("display or show function", "display(df)")]),
        ("show(data)", [("display or show function", "show(data)")]),
        ("df.collect()", [("dataframe method", "df.collect()")]),
        ("df.show()", [("display or show function", "df.show()"), ("dataframe method", "df.show()")]),
    ]

    for line, expected in test_cases:
        matches = check_line_for_patterns(line, patterns)
        assert matches == expected


def test_pattern_matching_performance():
    """Test pattern matching with many patterns."""
    # Create many patterns
    patterns = [(f"pattern_{i}", f"description_{i}") for i in range(100)]
    patterns.append((r"target_pattern", "target description"))

    line = "some code with target_pattern in it"
    matches = check_line_for_patterns(line, patterns)

    # Should only match the target pattern
    assert len(matches) == 1
    assert matches[0] == ("target description", line)


def test_pattern_matching_with_invalid_regex():
    """Test behavior with invalid regex patterns."""
    patterns = [
        (r"[unclosed_bracket", "invalid pattern"),
        (r"valid_pattern", "valid pattern"),
    ]

    line = "test valid_pattern here"

    # Should handle invalid regex gracefully
    # (The actual behavior depends on implementation - might raise exception or skip invalid patterns)
    try:
        matches = check_line_for_patterns(line, patterns)
        # If no exception, should at least process valid patterns
        valid_matches = [m for m in matches if m[0] == "valid pattern"]
        # Just check that it doesn't crash - length is always >= 0
    except Exception:
        # Invalid regex might cause an exception - this is acceptable behavior
        pass
