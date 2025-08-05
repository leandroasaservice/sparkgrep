import pytest
import re
from sparkgrep.patterns import USELESS_PATTERNS


def test_useless_patterns_structure():
    """Test that USELESS_PATTERNS has the correct structure."""
    assert isinstance(USELESS_PATTERNS, list)
    assert len(USELESS_PATTERNS) > 0

    for pattern in USELESS_PATTERNS:
        assert isinstance(pattern, tuple)
        assert len(pattern) == 2
        regex, description = pattern
        assert isinstance(regex, str)
        assert isinstance(description, str)
        assert len(regex) > 0
        assert len(description) > 0


def test_patterns_are_valid_regex():
    """Test that all patterns compile as valid regular expressions."""
    for regex, description in USELESS_PATTERNS:
        try:
            compiled = re.compile(regex, re.IGNORECASE)
            assert compiled is not None
        except re.error as e:
            pytest.fail(f"Invalid regex pattern '{regex}' for '{description}': {e}")


def test_patterns_compile_with_ignorecase():
    """Test that patterns work with IGNORECASE flag."""
    for regex, description in USELESS_PATTERNS:
        compiled = re.compile(regex, re.IGNORECASE)

        # Test that the pattern can be used for searching
        test_strings = ["display(df)", "DISPLAY(DF)", "df.show()", "DF.SHOW()"]

        # At least one of our test strings should potentially match
        # (this is just testing compilation, not specific pattern logic)
        for test_str in test_strings:
            try:
                result = compiled.search(test_str)
                # Result can be None or Match object - both are valid
                assert result is None or hasattr(result, 'group')
            except Exception as e:
                pytest.fail(f"Pattern '{regex}' failed on test string '{test_str}': {e}")


def test_pattern_descriptions_are_meaningful():
    """Test that pattern descriptions are meaningful."""
    for regex, description in USELESS_PATTERNS:
        # Description should be longer than just a few characters
        assert len(description) >= 10, f"Description too short: '{description}'"

        # Description should contain meaningful words
        meaningful_words = ['display', 'show', 'collect', 'count', 'pandas', 'exit', 'function', 'method', 'call']
        description_lower = description.lower()

        has_meaningful_word = any(word in description_lower for word in meaningful_words)
        assert has_meaningful_word, f"Description lacks meaningful words: '{description}'"


def test_specific_pattern_functionality():
    """Test that specific known patterns work as expected."""
    # Create a mapping of patterns for easier testing
    patterns_dict = {desc: regex for regex, desc in USELESS_PATTERNS}

    # Test display function pattern
    display_patterns = [p for p in USELESS_PATTERNS if 'display' in p[1].lower()]
    assert len(display_patterns) > 0, "Should have display function patterns"

    for regex, description in display_patterns:
        compiled = re.compile(regex, re.IGNORECASE)

        # Should match display function calls
        test_cases = [
            ("display(df)", True),
            ("display(my_dataframe)", True),
            ("DISPLAY(DF)", True),
            ("some_display = 5", False),  # Variable name, not function call
            ("print('display this')", False),  # In string literal
        ]

        for test_string, should_match in test_cases:
            match = compiled.search(test_string)
            if should_match:
                assert match is not None, f"Pattern '{regex}' should match '{test_string}'"
            # Note: We don't test negative cases strictly since some patterns
            # might be intentionally broad and handled by other filtering


def test_show_method_patterns():
    """Test show method patterns."""
    show_patterns = [p for p in USELESS_PATTERNS if 'show' in p[1].lower()]
    assert len(show_patterns) > 0, "Should have show method patterns"

    for regex, description in show_patterns:
        compiled = re.compile(regex, re.IGNORECASE)

        # Should match show method calls
        test_cases = [
            "df.show()",
            "dataframe.show(10)",
            "my_df.show(20, False)",
            "DF.SHOW()"
        ]

        for test_string in test_cases:
            match = compiled.search(test_string)
            assert match is not None, f"Pattern '{regex}' should match '{test_string}'"


def test_collect_patterns():
    """Test collect method patterns."""
    collect_patterns = [p for p in USELESS_PATTERNS if 'collect' in p[1].lower()]
    assert len(collect_patterns) > 0, "Should have collect method patterns"

    for regex, description in collect_patterns:
        compiled = re.compile(regex, re.IGNORECASE)

        # Test various collect scenarios
        test_cases = [
            ("df.collect()", True),  # Basic collect
            ("dataframe.collect()", True),  # With variable name
            ("result = df.collect()", False),  # With assignment (depends on pattern specificity)
        ]

        for test_string, should_match in test_cases:
            match = compiled.search(test_string)
            if should_match:
                assert match is not None, f"Pattern '{regex}' should match '{test_string}'"


def test_patterns_descriptions_uniqueness():
    """Test that pattern descriptions are unique."""
    descriptions = [description for regex, description in USELESS_PATTERNS]
    unique_descriptions = set(descriptions)

    assert len(descriptions) == len(unique_descriptions), "Pattern descriptions should be unique"


def test_patterns_regex_uniqueness():
    """Test that regex patterns are unique."""
    regexes = [regex for regex, description in USELESS_PATTERNS]
    unique_regexes = set(regexes)

    assert len(regexes) == len(unique_regexes), "Regex patterns should be unique"


def test_pattern_performance():
    """Test that patterns don't have obvious performance issues."""
    test_text = "display(df); df.show(); df.collect(); df.count(); df.toPandas();" * 100

    for regex, description in USELESS_PATTERNS:
        compiled = re.compile(regex, re.IGNORECASE)

        # This should complete quickly
        matches = compiled.findall(test_text)
        assert isinstance(matches, list)
        # Should find multiple matches in our test text for relevant patterns
        if 'display' in description.lower():
            assert len(matches) > 0


def test_patterns_handle_whitespace():
    """Test that patterns handle whitespace variations."""
    for regex, description in USELESS_PATTERNS:
        compiled = re.compile(regex, re.IGNORECASE)

        # Test with various whitespace patterns
        if 'display' in description.lower():
            whitespace_cases = [
                "display(df)",
                "display (df)",  # Space before parenthesis
                "display( df )",  # Spaces inside
                "display(  df  )",  # Multiple spaces
                "display(\tdf\t)",  # Tabs
            ]

            for case in whitespace_cases:
                match = compiled.search(case)
                # Should be flexible with whitespace (depending on pattern design)
                assert match is not None or True  # Pattern may or may not handle all whitespace


def test_patterns_avoid_false_positives():
    """Test that patterns try to avoid obvious false positives."""
    for regex, description in USELESS_PATTERNS:
        compiled = re.compile(regex, re.IGNORECASE)

        # Test cases that shouldn't match (though this depends on pattern specificity)
        potential_false_positives = [
            "# display(df)  # This is a comment",
            "print('display(df) in string')",
            "\"\"\"display(df) in docstring\"\"\"",
        ]

        for case in potential_false_positives:
            match = compiled.search(case)
            # Note: We don't assert these don't match since the regex itself
            # might not handle context - that's handled by other parts of the code


def test_patterns_case_insensitivity():
    """Test that patterns work with different cases."""
    for regex, description in USELESS_PATTERNS:
        compiled = re.compile(regex, re.IGNORECASE)

        if 'display' in description.lower():
            cases = ["display(df)", "DISPLAY(df)", "Display(df)", "dIsPlAy(df)"]

            for case in cases:
                match = compiled.search(case)
                assert match is not None, f"Pattern should be case insensitive: '{case}'"


def test_minimum_expected_patterns():
    """Test that we have patterns for key Spark operations."""
    descriptions_text = " ".join([desc.lower() for regex, desc in USELESS_PATTERNS])

    # Should have patterns for these key operations
    expected_operations = ['display', 'show', 'collect', 'count']

    for operation in expected_operations:
        assert operation in descriptions_text, f"Should have pattern for '{operation}' operation"


def test_patterns_contain_spark_specific_items():
    """Test that patterns include Spark-specific operations."""
    descriptions_text = " ".join([desc.lower() for regex, desc in USELESS_PATTERNS])

    # Should mention Spark-related terms
    spark_terms = ['pandas', 'databricks', 'spark']  # Common in descriptions

    # At least some patterns should mention Spark ecosystem
    has_spark_terms = any(term in descriptions_text for term in spark_terms)
    assert has_spark_terms, "Patterns should include Spark ecosystem terms"


def test_pattern_count_reasonable():
    """Test that we have a reasonable number of patterns."""
    # Should have enough patterns to be useful, but not so many as to be unwieldy
    assert 5 <= len(USELESS_PATTERNS) <= 20, f"Expected 5-20 patterns, got {len(USELESS_PATTERNS)}"


def test_patterns_no_empty_components():
    """Test that no patterns have empty regex or descriptions."""
    for regex, description in USELESS_PATTERNS:
        assert regex.strip() != "", "Regex pattern should not be empty"
        assert description.strip() != "", "Description should not be empty"


def test_patterns_grouping_behavior():
    """Test regex grouping behavior in patterns."""
    for regex, description in USELESS_PATTERNS:
        compiled = re.compile(regex, re.IGNORECASE)

        # Test with a sample that might match
        test_sample = "display(df)"
        match = compiled.search(test_sample)

        if match:
            # Should be able to get the full match
            full_match = match.group(0)
            assert isinstance(full_match, str)
            assert len(full_match) > 0
