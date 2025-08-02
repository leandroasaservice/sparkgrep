"""
Unit tests for CLI argument parsing functionality.
"""

import pytest
import sys
from unittest.mock import patch

from sparkgrep.cli import parse_arguments


def test_parse_arguments_basic():
    """Test basic argument parsing."""
    with patch("sys.argv", ["script", "file1.py", "file2.ipynb"]):
        args = parse_arguments()

        assert args.files == ["file1.py", "file2.ipynb"]
        assert args.config is None
        assert args.additional_patterns is None
        assert args.disable_default_patterns is False


def test_parse_arguments_with_config():
    """Test argument parsing with config file."""
    with patch("sys.argv", ["script", "file1.py", "--config", "config.json"]):
        args = parse_arguments()

        assert args.files == ["file1.py"]
        assert args.config == "config.json"


def test_parse_arguments_with_additional_patterns():
    """Test argument parsing with additional patterns."""
    with patch(
        "sys.argv",
        [
            "script",
            "file1.py",
            "--additional-patterns",
            "pattern1:desc1",
            "pattern2:desc2",
        ],
    ):
        args = parse_arguments()

        assert args.files == ["file1.py"]
        assert args.additional_patterns == ["pattern1:desc1", "pattern2:desc2"]


def test_parse_arguments_disable_default_patterns():
    """Test argument parsing with disabled default patterns."""
    with patch("sys.argv", ["script", "file1.py", "--disable-default-patterns"]):
        args = parse_arguments()

        assert args.files == ["file1.py"]
        assert args.disable_default_patterns is True


def test_parse_arguments_no_files():
    """Test argument parsing with no files provided."""
    with patch("sys.argv", ["script"]):
        args = parse_arguments()

        assert args.files == []


def test_parse_arguments_all_options():
    """Test argument parsing with all options."""
    argv = [
        "script",
        "file1.py",
        "file2.ipynb",
        "--config",
        "config.json",
        "--additional-patterns",
        "pattern1:desc1",
        "pattern2:desc2",
        "--disable-default-patterns",
    ]

    with patch("sys.argv", argv):
        args = parse_arguments()

        assert args.files == ["file1.py", "file2.ipynb"]
        assert args.config == "config.json"
        assert args.additional_patterns == ["pattern1:desc1", "pattern2:desc2"]
        assert args.disable_default_patterns is True


def test_parse_arguments_help_flag():
    """Test argument parsing with help flag."""
    with patch("sys.argv", ["script", "--help"]):
        with pytest.raises(SystemExit):
            parse_arguments()


def test_parse_arguments_invalid_flag():
    """Test argument parsing with invalid flag."""
    with patch("sys.argv", ["script", "--invalid-flag"]):
        with pytest.raises(SystemExit):
            parse_arguments()


def test_parse_arguments_single_additional_pattern():
    """Test argument parsing with single additional pattern."""
    with patch("sys.argv", ["script", "file.py", "--additional-patterns", "pattern:desc"]):
        args = parse_arguments()

        assert args.files == ["file.py"]
        assert args.additional_patterns == ["pattern:desc"]


def test_parse_arguments_empty_additional_patterns():
    """Test argument parsing with empty additional patterns list."""
    with patch("sys.argv", ["script", "file.py", "--additional-patterns"]):
        args = parse_arguments()

        assert args.files == ["file.py"]
        assert args.additional_patterns == []


def test_parse_arguments_file_with_spaces():
    """Test argument parsing with files containing spaces."""
    with patch("sys.argv", ["script", "file with spaces.py", "another file.ipynb"]):
        args = parse_arguments()

        assert args.files == ["file with spaces.py", "another file.ipynb"]


def test_parse_arguments_special_characters():
    """Test argument parsing with special characters in filenames."""
    special_files = ["file-with-dashes.py", "file_with_underscores.py", "file.with.dots.py"]

    with patch("sys.argv", ["script"] + special_files):
        args = parse_arguments()

        assert args.files == special_files
