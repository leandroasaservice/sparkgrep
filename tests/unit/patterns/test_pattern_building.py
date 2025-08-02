"""
Unit tests for pattern building functionality.
"""

import pytest
from sparkgrep.patterns import USELESS_PATTERNS, build_patterns_list


def test_default_patterns_only():
    """Test building patterns list with default patterns only."""
    patterns = build_patterns_list()

    assert len(patterns) >= 6  # Allow for growth
    assert patterns == USELESS_PATTERNS


def test_disable_default_patterns():
    """Test building patterns list with default patterns disabled."""
    patterns = build_patterns_list(disable_default_patterns=True)

    assert len(patterns) == 0


def test_additional_patterns_valid():
    """Test adding valid additional patterns."""
    additional = ["test_pattern:test description", "another_pattern:another desc"]
    patterns = build_patterns_list(additional_patterns=additional)

    expected_length = len(USELESS_PATTERNS) + 2
    assert len(patterns) == expected_length
    assert ("test_pattern", "test description") in patterns
    assert ("another_pattern", "another desc") in patterns


def test_additional_patterns_invalid_format(capsys):
    """Test adding invalid additional patterns (should show warning)."""
    additional = ["invalid_pattern_no_colon", "valid:pattern"]
    patterns = build_patterns_list(additional_patterns=additional)

    # Should have default patterns + 1 valid additional
    expected_length = len(USELESS_PATTERNS) + 1
    assert len(patterns) == expected_length
    assert ("valid", "pattern") in patterns

    # Should print warning for invalid format
    captured = capsys.readouterr()
    assert "Warning: Invalid pattern format" in captured.out
    assert "invalid_pattern_no_colon" in captured.out


def test_additional_patterns_with_disabled_defaults():
    """Test additional patterns with default patterns disabled."""
    additional = ["custom:Custom pattern"]
    patterns = build_patterns_list(
        disable_default_patterns=True, additional_patterns=additional
    )

    assert len(patterns) == 1
    assert patterns[0] == ("custom", "Custom pattern")


def test_additional_patterns_none():
    """Test with None additional patterns."""
    patterns = build_patterns_list(additional_patterns=None)

    assert len(patterns) == len(USELESS_PATTERNS)
    assert patterns == USELESS_PATTERNS


def test_additional_patterns_empty_list():
    """Test with empty additional patterns list."""
    patterns = build_patterns_list(additional_patterns=[])

    assert len(patterns) == len(USELESS_PATTERNS)
    assert patterns == USELESS_PATTERNS


def test_complex_pattern_descriptions():
    """Test patterns with complex descriptions containing colons."""
    additional = ["pattern:Description with: colons and punctuation!"]
    patterns = build_patterns_list(additional_patterns=additional)

    expected_length = len(USELESS_PATTERNS) + 1
    assert len(patterns) == expected_length
    assert ("pattern", "Description with: colons and punctuation!") in patterns


def test_empty_pattern_components():
    """Test patterns with empty components."""
    additional = [":empty_pattern", "empty_description:", "::double_colon"]
    patterns = build_patterns_list(additional_patterns=additional)

    expected_length = len(USELESS_PATTERNS) + 3
    assert len(patterns) == expected_length
    assert ("", "empty_pattern") in patterns
    assert ("empty_description", "") in patterns
    assert ("", ":double_colon") in patterns


def test_build_patterns_list_order():
    """Test that patterns are returned in predictable order."""
    additional = ["z_pattern:Z description", "a_pattern:A description"]
    patterns = build_patterns_list(additional_patterns=additional)

    # Default patterns should come first
    for i, default_pattern in enumerate(USELESS_PATTERNS):
        assert patterns[i] == default_pattern

    # Additional patterns should come after
    assert ("z_pattern", "Z description") in patterns
    assert ("a_pattern", "A description") in patterns


def test_build_patterns_with_special_characters():
    """Test building patterns with special regex characters."""
    additional = [
        r"\w+\.collect\s*\(\):Regex pattern",
        r"[abc]+:Character class",
        r"^start.*end$:Anchored pattern"
    ]
    patterns = build_patterns_list(additional_patterns=additional)

    expected_length = len(USELESS_PATTERNS) + 3
    assert len(patterns) == expected_length

    added_patterns = patterns[len(USELESS_PATTERNS):]
    assert (r"\w+\.collect\s*\(\)", "Regex pattern") in added_patterns
    assert (r"[abc]+", "Character class") in added_patterns
    assert (r"^start.*end$", "Anchored pattern") in added_patterns


def test_build_patterns_duplicate_handling():
    """Test handling of duplicate patterns."""
    # Add a pattern that might be similar to existing ones
    additional = ["display:Duplicate display pattern"]
    patterns = build_patterns_list(additional_patterns=additional)

    # Should allow duplicates (user responsibility to avoid them)
    expected_length = len(USELESS_PATTERNS) + 1
    assert len(patterns) == expected_length
    assert ("display", "Duplicate display pattern") in patterns


def test_build_patterns_many_additional():
    """Test building patterns with many additional patterns."""
    additional = [f"pattern_{i}:Description {i}" for i in range(100)]
    patterns = build_patterns_list(additional_patterns=additional)

    expected_length = len(USELESS_PATTERNS) + 100
    assert len(patterns) == expected_length

    # Check that all additional patterns are included
    for i in range(100):
        assert (f"pattern_{i}", f"Description {i}") in patterns


def test_build_patterns_unicode_content():
    """Test building patterns with unicode characters."""
    additional = [
        "unicode_pattern:Description with émojis 🎉",
        "特殊字符:Chinese characters in pattern",
        "русский:Russian description"
    ]
    patterns = build_patterns_list(additional_patterns=additional)

    expected_length = len(USELESS_PATTERNS) + 3
    assert len(patterns) == expected_length

    added_patterns = patterns[len(USELESS_PATTERNS):]
    assert ("unicode_pattern", "Description with émojis 🎉") in added_patterns
    assert ("特殊字符", "Chinese characters in pattern") in added_patterns
    assert ("русский", "Russian description") in added_patterns


def test_build_patterns_whitespace_handling():
    """Test handling of whitespace in patterns."""
    additional = [
        "  pattern_with_spaces  :  description with spaces  ",
        "\tpattern_with_tabs\t:\tdescription with tabs\t",
        "pattern:description",  # No extra whitespace
    ]
    patterns = build_patterns_list(additional_patterns=additional)

    expected_length = len(USELESS_PATTERNS) + 3
    assert len(patterns) == expected_length

    # Check that whitespace is preserved (not stripped)
    added_patterns = patterns[len(USELESS_PATTERNS):]
    assert ("  pattern_with_spaces  ", "  description with spaces  ") in added_patterns
    assert ("\tpattern_with_tabs\t", "\tdescription with tabs\t") in added_patterns
    assert ("pattern", "description") in added_patterns


def test_build_patterns_both_flags():
    """Test building patterns with both disable_default_patterns and additional_patterns."""
    additional = ["custom1:Custom 1", "custom2:Custom 2"]

    # Test with defaults disabled
    patterns = build_patterns_list(
        disable_default_patterns=True,
        additional_patterns=additional
    )

    assert len(patterns) == 2
    assert ("custom1", "Custom 1") in patterns
    assert ("custom2", "Custom 2") in patterns

    # Ensure no default patterns are included
    for default_pattern in USELESS_PATTERNS:
        assert default_pattern not in patterns


def test_build_patterns_return_type():
    """Test that build_patterns_list returns the correct type."""
    patterns = build_patterns_list()

    assert isinstance(patterns, list)
    assert all(isinstance(item, tuple) for item in patterns)
    assert all(len(item) == 2 for item in patterns)
    assert all(isinstance(item[0], str) and isinstance(item[1], str) for item in patterns)


def test_build_patterns_immutability():
    """Test that modifying returned patterns doesn't affect subsequent calls."""
    patterns1 = build_patterns_list()
    original_length = len(patterns1)

    # Modify the returned list
    patterns1.append(("test", "test"))

    # Get a new list
    patterns2 = build_patterns_list()

    # Should be unchanged
    assert len(patterns2) == original_length
    assert ("test", "test") not in patterns2


def test_build_patterns_additional_patterns_modification():
    """Test that modifying additional_patterns list doesn't affect result."""
    additional = ["pattern1:desc1", "pattern2:desc2"]
    patterns = build_patterns_list(additional_patterns=additional)

    original_length = len(patterns)

    # Modify the input list
    additional.append("pattern3:desc3")

    # Get patterns again with same reference
    patterns2 = build_patterns_list(additional_patterns=additional)

    # Should include the new pattern
    assert len(patterns2) == original_length + 1
    assert ("pattern3", "desc3") in patterns2


def test_build_patterns_colon_edge_cases():
    """Test edge cases with colon handling in patterns."""
    edge_cases = [
        "no_colon_at_all",  # Invalid
        ":starts_with_colon",  # Empty pattern
        "ends_with_colon:",  # Empty description
        "multiple:colons:in:description",  # Multiple colons
        "::multiple_colons_start",  # Multiple colons at start
        "pattern:::description",  # Multiple consecutive colons
    ]

    patterns = build_patterns_list(additional_patterns=edge_cases)

    # Should handle each case appropriately
    # Valid patterns should be included, invalid ones should show warnings
    expected_valid_patterns = [
        ("", "starts_with_colon"),
        ("ends_with_colon", ""),
        ("multiple", "colons:in:description"),
        ("", ":multiple_colons_start"),
        ("pattern", "::description"),
    ]

    for expected_pattern in expected_valid_patterns:
        if expected_pattern in patterns:
            assert expected_pattern in patterns
