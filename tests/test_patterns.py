"""
Unit tests for the patterns module.
"""

import pytest
from src.patterns import USELESS_PATTERNS, build_patterns_list


class TestUselessPatterns:
    """Test the predefined useless patterns."""

    def test_useless_patterns_count(self):
        """Test that we have the expected number of patterns."""
        assert len(USELESS_PATTERNS) == 7

    def test_pattern_structure(self):
        """Test that each pattern has the correct structure."""
        for pattern, description in USELESS_PATTERNS:
            assert isinstance(pattern, str), f"Pattern should be string: {pattern}"
            assert isinstance(
                description, str
            ), f"Description should be string: {description}"
            assert len(pattern) > 0, "Pattern should not be empty"
            assert len(description) > 0, "Description should not be empty"

    def test_pattern_descriptions(self):
        """Test that pattern descriptions are meaningful."""
        descriptions = [desc for _, desc in USELESS_PATTERNS]
        expected_keywords = ["display", "show", "collect", "toPandas", "dbutils"]

        for keyword in expected_keywords:
            found = any(keyword in desc for desc in descriptions)
            assert found, f"Expected keyword '{keyword}' not found in descriptions"


class TestBuildPatternsList:
    """Test the build_patterns_list function."""

    def test_default_patterns_only(self):
        """Test building patterns list with default patterns only."""
        patterns = build_patterns_list()

        assert len(patterns) == 7
        assert patterns == USELESS_PATTERNS

    def test_disable_default_patterns(self):
        """Test building patterns list with default patterns disabled."""
        patterns = build_patterns_list(disable_default_patterns=True)

        assert len(patterns) == 0

    def test_additional_patterns_valid(self):
        """Test adding valid additional patterns."""
        additional = ["test_pattern:test description", "another_pattern:another desc"]
        patterns = build_patterns_list(additional_patterns=additional)

        assert len(patterns) == 9  # 7 default + 2 additional
        assert ("test_pattern", "test description") in patterns
        assert ("another_pattern", "another desc") in patterns

    def test_additional_patterns_invalid_format(self, capsys):
        """Test adding invalid additional patterns (should show warning)."""
        additional = ["invalid_pattern_no_colon", "valid:pattern"]
        patterns = build_patterns_list(additional_patterns=additional)

        # Should have 7 default + 1 valid additional
        assert len(patterns) == 8
        assert ("valid", "pattern") in patterns

        # Should print warning for invalid format
        captured = capsys.readouterr()
        assert "Warning: Invalid pattern format" in captured.out
        assert "invalid_pattern_no_colon" in captured.out

    def test_additional_patterns_with_disabled_defaults(self):
        """Test additional patterns with default patterns disabled."""
        additional = ["custom:Custom pattern"]
        patterns = build_patterns_list(
            disable_default_patterns=True, additional_patterns=additional
        )

        assert len(patterns) == 1
        assert patterns[0] == ("custom", "Custom pattern")

    def test_additional_patterns_none(self):
        """Test with None additional patterns."""
        patterns = build_patterns_list(additional_patterns=None)

        assert len(patterns) == 7
        assert patterns == USELESS_PATTERNS

    def test_additional_patterns_empty_list(self):
        """Test with empty additional patterns list."""
        patterns = build_patterns_list(additional_patterns=[])

        assert len(patterns) == 7
        assert patterns == USELESS_PATTERNS

    def test_complex_pattern_descriptions(self):
        """Test patterns with complex descriptions containing colons."""
        additional = ["pattern:Description with: colons and punctuation!"]
        patterns = build_patterns_list(additional_patterns=additional)

        assert len(patterns) == 8
        assert ("pattern", "Description with: colons and punctuation!") in patterns

    def test_empty_pattern_components(self):
        """Test patterns with empty components."""
        additional = [":empty_pattern", "empty_description:", "::double_colon"]
        patterns = build_patterns_list(additional_patterns=additional)

        assert len(patterns) == 10  # 7 default + 3 additional
        assert ("", "empty_pattern") in patterns
        assert ("empty_description", "") in patterns
        assert ("", ":double_colon") in patterns
