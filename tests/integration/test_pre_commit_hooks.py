"""
Integration tests for pre-commit hook scenarios.
"""

import pytest
import tempfile
import os
from unittest.mock import patch

from sparkgrep.cli import main


def test_pre_commit_hook_success_scenario():
    """Test successful pre-commit hook execution (no issues)."""
    python_code = """
def clean_function():
    result = df.collect()
    pandas_df = df.toPandas()
    print("All clean")
    return result
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(python_code)
        temp_path = f.name

    try:
        # Simulate pre-commit hook call
        test_argv = ["check-spark-actions", temp_path]

        with patch("sys.argv", test_argv):
            result = main()
            assert result == 0  # Success

    finally:
        os.unlink(temp_path)


def test_pre_commit_hook_failure_scenario():
    """Test pre-commit hook failure (issues found)."""
    python_code = """
def problematic_function():
    display(df)  # This should cause failure
    df.show()  # This should cause failure
    return None
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(python_code)
        temp_path = f.name

    try:
        # Simulate pre-commit hook call
        test_argv = ["check-spark-actions", temp_path]

        with patch("sys.argv", test_argv):
            result = main()
            assert result == 1  # Failure

    finally:
        os.unlink(temp_path)


def test_pre_commit_hook_with_options():
    """Test pre-commit hook with command-line options."""
    python_code = """
def test_function():
    display(df)  # Default pattern
    custom_debug()  # Custom pattern
    print("hello")
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(python_code)
        temp_path = f.name

    try:
        # Test with disabled default patterns and custom pattern
        test_argv = [
            "check-spark-actions",
            temp_path,
            "--disable-default-patterns",
            "--additional-patterns",
            r"custom_debug\s*\(\s*\):Custom debug function",
        ]

        with patch("sys.argv", test_argv):
            result = main()
            assert result == 1  # Should fail due to custom pattern match

    finally:
        os.unlink(temp_path)
