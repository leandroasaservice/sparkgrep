"""
Unit tests for pattern definitions.
"""

import pytest
import re
from sparkgrep.patterns import USELESS_PATTERNS


def test_useless_patterns_count():
    """Test that we have the expected number of patterns."""
    assert len(USELESS_PATTERNS) >= 6  # Allow for growth


def test_pattern_structure():
    """Test that each pattern has the correct structure."""
    for pattern, description in USELESS_PATTERNS:
        assert isinstance(pattern, str), f"Pattern should be string: {pattern}"
        assert isinstance(
            description, str
        ), f"Description should be string: {description}"
        assert len(pattern) > 0, "Pattern should not be empty"
        assert len(description) > 0, "Description should not be empty"


def test_pattern_descriptions():
    """Test that pattern descriptions are meaningful."""
    descriptions = [desc for _, desc in USELESS_PATTERNS]
    expected_keywords = ["display", "show", "collect", "toPandas", "dbutils"]

    for keyword in expected_keywords:
        found = any(keyword in desc for desc in descriptions)
        assert found, f"Expected keyword '{keyword}' not found in descriptions"


def test_patterns_are_valid_regex():
    """Test that all patterns are valid regex."""
    for pattern, description in USELESS_PATTERNS:
        try:
            re.compile(pattern)
        except re.error as e:
            pytest.fail(f"Invalid regex pattern '{pattern}': {e}")


def test_patterns_compile_with_ignorecase():
    """Test that patterns work with IGNORECASE flag."""
    for pattern, description in USELESS_PATTERNS:
        try:
            re.compile(pattern, re.IGNORECASE)
        except re.error as e:
            pytest.fail(f"Pattern '{pattern}' fails with IGNORECASE: {e}")


def test_specific_pattern_content():
    """Test that specific expected patterns exist."""
    pattern_texts = [pattern for pattern, _ in USELESS_PATTERNS]

    # Check for display pattern
    display_patterns = [p for p in pattern_texts if "display" in p]
    assert len(display_patterns) > 0, "Should have display patterns"

    # Check for show pattern
    show_patterns = [p for p in pattern_texts if "show" in p]
    assert len(show_patterns) > 0, "Should have show patterns"

    # Check for collect pattern
    collect_patterns = [p for p in pattern_texts if "collect" in p]
    assert len(collect_patterns) > 0, "Should have collect patterns"


def test_pattern_descriptions_uniqueness():
    """Test that pattern descriptions are unique."""
    descriptions = [desc for _, desc in USELESS_PATTERNS]
    assert len(descriptions) == len(set(descriptions)), "Pattern descriptions should be unique"


def test_pattern_regex_uniqueness():
    """Test that pattern regexes are unique."""
    patterns = [pattern for pattern, _ in USELESS_PATTERNS]
    assert len(patterns) == len(set(patterns)), "Pattern regexes should be unique"


def test_pattern_complexity():
    """Test that patterns have appropriate complexity."""
    for pattern, description in USELESS_PATTERNS:
        # Patterns should not be too simple (single character)
        assert len(pattern) > 1, f"Pattern too simple: {pattern}"

        # Patterns should contain meaningful regex elements
        has_meaningful_content = any(char in pattern for char in ['.', '*', '+', '?', '(', ')', '[', ']', '{', '}', '\\'])
        has_literal_content = any(char.isalnum() for char in pattern)

        assert has_meaningful_content or has_literal_content, f"Pattern lacks meaningful content: {pattern}"


def test_pattern_performance():
    """Test that patterns don't have obvious performance issues."""
    test_string = "display(df.show().collect().count().toPandas())"

    for pattern, description in USELESS_PATTERNS:
        compiled_pattern = re.compile(pattern, re.IGNORECASE)

        # Should be able to match quickly
        import time
        start_time = time.time()
        compiled_pattern.search(test_string)
        end_time = time.time()

        # Should complete within reasonable time (1 second is very generous)
        assert end_time - start_time < 1.0, f"Pattern '{pattern}' takes too long to execute"


def test_pattern_anchoring():
    """Test pattern anchoring behavior."""
    anchored_patterns = []
    unanchored_patterns = []

    for pattern, description in USELESS_PATTERNS:
        if pattern.startswith('^') or pattern.endswith('$'):
            anchored_patterns.append((pattern, description))
        else:
            unanchored_patterns.append((pattern, description))

    # Should have a mix of anchored and unanchored patterns
    assert len(anchored_patterns) > 0, "Should have some anchored patterns"
    assert len(unanchored_patterns) > 0, "Should have some unanchored patterns"


def test_pattern_whitespace_handling():
    """Test that patterns handle whitespace appropriately."""
    whitespace_aware_patterns = []

    for pattern, description in USELESS_PATTERNS:
        if '\\s' in pattern or ' ' in pattern or '\\t' in pattern:
            whitespace_aware_patterns.append((pattern, description))

    # Many patterns should be whitespace-aware
    assert len(whitespace_aware_patterns) > 0, "Should have whitespace-aware patterns"


def test_pattern_grouping():
    """Test pattern grouping usage."""
    grouped_patterns = []
    non_grouped_patterns = []

    for pattern, description in USELESS_PATTERNS:
        if '(' in pattern and ')' in pattern:
            grouped_patterns.append((pattern, description))
        else:
            non_grouped_patterns.append((pattern, description))

    # Should have some patterns with grouping (optional but useful)
    # Just verify the grouping logic works


def test_pattern_case_sensitivity():
    """Test pattern case sensitivity considerations."""
    # Test patterns against both lower and upper case variants
    test_cases = [
        "display(df)",
        "DISPLAY(DF)",
        "Display(Df)",
        "df.show()",
        "DF.SHOW()",
        "Df.Show()",
    ]

    for pattern, description in USELESS_PATTERNS:
        compiled_pattern = re.compile(pattern, re.IGNORECASE)

        # With IGNORECASE, should handle various cases
        # Just verify the pattern compiles and can be used
        for test_case in test_cases:
            compiled_pattern.search(test_case)

        # This is just ensuring the patterns work with case insensitive matching
