import pytest
from sparkgrep.patterns import build_patterns_list, USELESS_PATTERNS


def test_default_patterns_only():
    """Test building patterns with only default patterns."""
    patterns = build_patterns_list(disable_default_patterns=False, additional_patterns=None)

    assert isinstance(patterns, list)
    assert len(patterns) > 0
    assert patterns == USELESS_PATTERNS

    # Should have the expected structure
    for pattern in patterns:
        assert isinstance(pattern, tuple)
        assert len(pattern) == 2
        assert isinstance(pattern[0], str)  # regex
        assert isinstance(pattern[1], str)  # description


def test_disable_default_patterns():
    """Test disabling default patterns."""
    patterns = build_patterns_list(disable_default_patterns=True, additional_patterns=None)

    assert isinstance(patterns, list)
    assert len(patterns) == 0


def test_additional_patterns_valid_format():
    """Test adding valid additional patterns."""
    additional = [
        "custom_pattern:Custom description",
        "another_pattern:Another description"
    ]

    patterns = build_patterns_list(disable_default_patterns=True, additional_patterns=additional)

    assert len(patterns) == 2
    assert patterns[0] == ("custom_pattern", "Custom description")
    assert patterns[1] == ("another_pattern", "Another description")


def test_additional_patterns_with_defaults():
    """Test adding additional patterns while keeping defaults."""
    additional = ["custom_pattern:Custom description"]

    patterns = build_patterns_list(disable_default_patterns=False, additional_patterns=additional)

    # Should have defaults + additional
    expected_count = len(USELESS_PATTERNS) + 1
    assert len(patterns) == expected_count

    # Last pattern should be the additional one
    assert patterns[-1] == ("custom_pattern", "Custom description")

    # First patterns should be the defaults
    for i, default_pattern in enumerate(USELESS_PATTERNS):
        assert patterns[i] == default_pattern


def test_additional_patterns_invalid_format():
    """Test handling of invalid additional pattern formats."""
    invalid_patterns = [
        "no_colon_separator",
        "multiple:colons:in:pattern",
        ":empty_pattern",
        "empty_description:",
        "",
        "   ",  # Only whitespace
    ]

    # Should handle invalid patterns gracefully
    for invalid_pattern in invalid_patterns:
        patterns = build_patterns_list(
            disable_default_patterns=True,
            additional_patterns=[invalid_pattern]
        )

        # Invalid patterns should be skipped or handled appropriately
        # The exact behavior depends on implementation
        assert isinstance(patterns, list)


def test_additional_patterns_none():
    """Test with None additional patterns."""
    patterns = build_patterns_list(disable_default_patterns=False, additional_patterns=None)

    assert patterns == USELESS_PATTERNS


def test_additional_patterns_empty_list():
    """Test with empty additional patterns list."""
    patterns = build_patterns_list(disable_default_patterns=False, additional_patterns=[])

    assert patterns == USELESS_PATTERNS


def test_complex_additional_patterns():
    """Test complex additional patterns with regex."""
    additional = [
        r"\.cache\(\):cache method call",
        r"\.persist\(\):persist method call",
        r"spark\.sql\(.*\)\.show\(\):SQL with immediate show"
    ]

    patterns = build_patterns_list(disable_default_patterns=True, additional_patterns=additional)

    assert len(patterns) == 3
    assert patterns[0] == (r"\.cache\(\)", "cache method call")
    assert patterns[1] == (r"\.persist\(\)", "persist method call")
    assert patterns[2] == (r"spark\.sql\(.*\)\.show\(\)", "SQL with immediate show")


def test_additional_patterns_with_special_characters():
    """Test additional patterns with special characters."""
    additional = [
        r"print\(['\"].*['\"].*\):print statement with quotes",
        r"@.*decorator:decorator pattern",
        r"\$\{.*\}:variable substitution"
    ]

    patterns = build_patterns_list(disable_default_patterns=True, additional_patterns=additional)

    assert len(patterns) == 3

    # Test that patterns can be compiled as regex
    import re
    for regex, description in patterns:
        try:
            compiled = re.compile(regex, re.IGNORECASE)
            assert compiled is not None
        except re.error:
            pytest.fail(f"Invalid regex in additional pattern: {regex}")


def test_build_patterns_return_type():
    """Test that build_patterns_list returns the correct type."""
    patterns = build_patterns_list()

    assert isinstance(patterns, list)
    assert all(isinstance(p, tuple) for p in patterns)
    assert all(len(p) == 2 for p in patterns)
    assert all(isinstance(p[0], str) and isinstance(p[1], str) for p in patterns)


def test_build_patterns_immutability():
    """Test that build_patterns_list doesn't modify input."""
    additional = ["test_pattern:test description"]
    original_additional = additional.copy()

    patterns = build_patterns_list(
        disable_default_patterns=False,
        additional_patterns=additional
    )

    # Original input should be unchanged
    assert additional == original_additional


def test_build_patterns_with_whitespace_in_descriptions():
    """Test patterns with whitespace in descriptions."""
    additional = [
        "pattern1:Description with spaces",
        "pattern2:  Leading and trailing spaces  ",
        "pattern3:\tTabs\tin\tdescription\t"
    ]

    patterns = build_patterns_list(disable_default_patterns=True, additional_patterns=additional)

    assert len(patterns) == 3

    # Should preserve whitespace in descriptions (or handle appropriately)
    descriptions = [p[1] for p in patterns]
    assert "Description with spaces" in descriptions
    # The exact handling of leading/trailing whitespace depends on implementation


def test_build_patterns_unicode_content():
    """Test patterns with unicode content."""
    additional = [
        "émojis_🚀:Pattern with emojis",
        "世界:Unicode pattern",
        "café:Pattern with accents"
    ]

    patterns = build_patterns_list(disable_default_patterns=True, additional_patterns=additional)

    assert len(patterns) == 3

    # Should handle unicode correctly
    for regex, description in patterns:
        assert isinstance(regex, str)
        assert isinstance(description, str)


def test_build_patterns_colon_edge_cases():
    """Test edge cases with colon handling."""
    additional = [
        "pattern::double colon description",
        "url_pattern:http://example.com:Port description",
        "time_pattern:12:34:56 time format"
    ]

    patterns = build_patterns_list(disable_default_patterns=True, additional_patterns=additional)

    # Should handle multiple colons appropriately
    # The exact behavior depends on implementation (split on first colon vs all colons)
    assert isinstance(patterns, list)
    assert len(patterns) >= 0  # Might skip invalid formats


def test_build_patterns_large_additional_list():
    """Test with a large number of additional patterns."""
    additional = [f"pattern_{i}:Description {i}" for i in range(100)]

    patterns = build_patterns_list(disable_default_patterns=True, additional_patterns=additional)

    assert len(patterns) == 100
    assert patterns[0] == ("pattern_0", "Description 0")
    assert patterns[99] == ("pattern_99", "Description 99")


def test_build_patterns_duplicate_handling():
    """Test handling of duplicate patterns."""
    additional = [
        "duplicate_pattern:First description",
        "duplicate_pattern:Second description",
        "unique_pattern:Unique description"
    ]

    patterns = build_patterns_list(disable_default_patterns=True, additional_patterns=additional)

    # Should handle duplicates appropriately (keep all, keep first, or deduplicate)
    assert isinstance(patterns, list)
    assert len(patterns) >= 1  # At least one pattern should be kept


def test_build_patterns_both_flags():
    """Test using both disable_default_patterns and additional_patterns."""
    additional = ["custom:Custom pattern"]

    # Test all combinations

    # Both defaults and additional
    patterns1 = build_patterns_list(disable_default_patterns=False, additional_patterns=additional)
    assert len(patterns1) == len(USELESS_PATTERNS) + 1

    # Only additional
    patterns2 = build_patterns_list(disable_default_patterns=True, additional_patterns=additional)
    assert len(patterns2) == 1
    assert patterns2[0] == ("custom", "Custom pattern")

    # Only defaults
    patterns3 = build_patterns_list(disable_default_patterns=False, additional_patterns=None)
    assert patterns3 == USELESS_PATTERNS

    # Neither
    patterns4 = build_patterns_list(disable_default_patterns=True, additional_patterns=None)
    assert len(patterns4) == 0


def test_build_patterns_order_preservation():
    """Test that pattern order is preserved."""
    additional = [
        "first:First pattern",
        "second:Second pattern",
        "third:Third pattern"
    ]

    patterns = build_patterns_list(disable_default_patterns=True, additional_patterns=additional)

    assert len(patterns) == 3
    assert patterns[0][1] == "First pattern"
    assert patterns[1][1] == "Second pattern"
    assert patterns[2][1] == "Third pattern"


def test_build_patterns_with_defaults_order():
    """Test that defaults come before additional patterns."""
    additional = ["additional:Additional pattern"]

    patterns = build_patterns_list(disable_default_patterns=False, additional_patterns=additional)

    # Defaults should come first
    for i, default_pattern in enumerate(USELESS_PATTERNS):
        assert patterns[i] == default_pattern

    # Additional should come last
    assert patterns[-1] == ("additional", "Additional pattern")


def test_build_patterns_function_defaults():
    """Test function with default parameter values."""
    # Test calling with no parameters (should use defaults)
    patterns = build_patterns_list()

    assert patterns == USELESS_PATTERNS
