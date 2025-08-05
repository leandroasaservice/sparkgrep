"""
Unit tests for the check_spark_actions module.
"""

import pytest
import tempfile
import os
from unittest.mock import patch

from sparkgrep.check_spark_actions import main
from sparkgrep import check_spark_actions


def test_module_import():
    """Test that the module can be imported successfully."""
    assert hasattr(check_spark_actions, 'main')
    assert callable(check_spark_actions.main)


def test_main_function_with_real_files():
    """Test the main function with real files containing issues."""
    python_code = "display(df)\ndf.show()"

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(python_code)
        temp_path = f.name

    try:
        test_argv = ["check_spark_actions", temp_path]

        with patch("sys.argv", test_argv):
            result = main()

        assert result == 1  # Should find issues

    finally:
        os.unlink(temp_path)


def test_main_function_clean_files():
    """Test the main function with clean files."""
    python_code = "def clean(): return sum([1, 2, 3])"

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(python_code)
        temp_path = f.name

    try:
        test_argv = ["check_spark_actions", temp_path]

        with patch("sys.argv", test_argv):
            result = main()

        assert result == 0  # Should find no issues

    finally:
        os.unlink(temp_path)


def test_main_function_no_files():
    """Test the main function with no files provided."""
    test_argv = ["check_spark_actions"]

    with patch("sys.argv", test_argv):
        result = main()

    assert result == 0  # Should succeed


def test_main_function_return_type():
    """Test that the main function returns an integer."""
    test_argv = ["check_spark_actions"]

    with patch("sys.argv", test_argv):
        result = main()

    assert isinstance(result, int)
    assert result in [0, 1]
