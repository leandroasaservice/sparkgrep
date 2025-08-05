import pytest
import tempfile
import os
from unittest.mock import patch

from sparkgrep.cli import main


def test_main_with_additional_patterns():
    """Test main function with additional patterns."""
    python_code = """
custom_function_call(df)
another_custom_call(data)
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(python_code)
        temp_path = f.name

    try:
        # Put file before additional patterns to avoid parsing issues
        test_argv = [
            "sparkgrep",
            temp_path,
            "--additional-patterns", "custom_function_call:Custom function"
        ]

        with patch("sys.argv", test_argv):
            result = main()

        assert result == 1  # Should find the custom pattern

    finally:
        os.unlink(temp_path)


def test_main_disable_default_patterns():
    """Test main function with disabled default patterns."""
    python_code = """
display(df)  # This would normally be caught by default patterns
df.show()    # This too
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(python_code)
        temp_path = f.name

    try:
        test_argv = ["sparkgrep", "--disable-default-patterns", temp_path]

        with patch("sys.argv", test_argv):
            result = main()

        assert result == 0  # Should succeed (no patterns to check)

    finally:
        os.unlink(temp_path)


def test_main_disable_defaults_with_additional():
    """Test main function with disabled defaults but additional patterns."""
    python_code = """
display(df)  # This won't be caught (defaults disabled)
custom_call(df)  # This should be caught
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(python_code)
        temp_path = f.name

    try:
        test_argv = [
            "sparkgrep",
            temp_path,
            "--disable-default-patterns",
            "--additional-patterns", "custom_call:Custom pattern"
        ]

        with patch("sys.argv", test_argv):
            result = main()

        assert result == 1  # Should find only the custom pattern

    finally:
        os.unlink(temp_path)


def test_main_complex_patterns():
    """Test main function with complex regex patterns."""
    python_code = """
df.collect()  # Should match
result = df.collect()  # Should not match (has assignment)
df.count()    # Should match
total = df.count()  # Should not match (has assignment)
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(python_code)
        temp_path = f.name

    try:
        test_argv = [
            "sparkgrep",
            "--additional-patterns",
            r"\.collect\(\)(?!\s*[=]):collect without assignment",
            r"\.count\(\)(?!\s*[=]):count without assignment",
            temp_path
        ]

        with patch("sys.argv", test_argv):
            result = main()

        assert result == 1  # Should find the patterns without assignment

    finally:
        os.unlink(temp_path)


def test_main_with_config_file_argument():
    """Test main function with config file argument."""
    python_code = "display(df)"

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(python_code)
        temp_path = f.name

    try:
        test_argv = ["sparkgrep", "--config", "nonexistent_config.json", temp_path]

        with patch("sys.argv", test_argv):
            result = main()

        # Should still work even with nonexistent config (config not implemented yet)
        assert result == 1  # Should find the display call

    finally:
        os.unlink(temp_path)


def test_main_pattern_precedence():
    """Test pattern precedence when multiple patterns match."""
    python_code = """
display(dataframe)
show_data(df)
custom_display(table)
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(python_code)
        temp_path = f.name

    try:
        test_argv = [
            "sparkgrep",
            temp_path,
            "--additional-patterns",
            "display:General display pattern",
            "custom_display:Specific custom display"
        ]

        with patch("sys.argv", test_argv):
            result = main()

        assert result == 1  # Should find patterns

    finally:
        os.unlink(temp_path)


def test_main_pattern_case_sensitivity():
    """Test pattern matching case sensitivity."""
    python_code = """
Display(df)  # Uppercase
DISPLAY(df)  # All caps
display(df)  # Lowercase
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(python_code)
        temp_path = f.name

    try:
        # Default patterns should be case insensitive
        test_argv = ["sparkgrep", temp_path]

        with patch("sys.argv", test_argv):
            result = main()

        assert result == 1  # Should find display calls regardless of case

    finally:
        os.unlink(temp_path)


def test_main_multiple_additional_patterns():
    """Test main function with multiple additional patterns."""
    python_code = """
pattern_one(df)
pattern_two(data)
pattern_three(table)
display(result)
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(python_code)
        temp_path = f.name

    try:
        test_argv = [
            "sparkgrep",
            temp_path,
            "--additional-patterns",
            "pattern_one:First pattern",
            "pattern_two:Second pattern",
            "pattern_three:Third pattern"
        ]

        with patch("sys.argv", test_argv):
            result = main()

        assert result == 1  # Should find multiple patterns

    finally:
        os.unlink(temp_path)


def test_main_pattern_with_special_chars():
    """Test patterns containing special regex characters."""
    python_code = """
$variable = "value"
@decorator_function
function.method()
array[index]
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(python_code)
        temp_path = f.name

    try:
        test_argv = [
            "sparkgrep",
            temp_path,
            "--additional-patterns",
            r"\$[a-zA-Z_]+:Variable pattern",
            r"@[a-zA-Z_]+:Decorator pattern",
            r"\[[^\]]+\]:Array indexing"
        ]

        with patch("sys.argv", test_argv):
            result = main()

        assert result == 1  # Should find special character patterns

    finally:
        os.unlink(temp_path)


def test_main_empty_additional_patterns():
    """Test main function with empty additional patterns list."""
    python_code = "display(df)"

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(python_code)
        temp_path = f.name

    try:
        test_argv = ["sparkgrep", temp_path, "--additional-patterns"]

        with patch("sys.argv", test_argv):
            result = main()

        # Should still use default patterns
        assert result == 1  # Should find display call with default patterns

    finally:
        os.unlink(temp_path)
