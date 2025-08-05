import pytest
from unittest.mock import patch
import sys

from sparkgrep.cli import parse_arguments


def test_parse_arguments_basic():
    """Test basic argument parsing."""
    test_argv = ["sparkgrep", "file1.py", "file2.py"]

    with patch.object(sys, 'argv', test_argv):
        args = parse_arguments()

        assert args.files == ["file1.py", "file2.py"]
        assert args.config is None
        assert args.additional_patterns is None
        assert args.disable_default_patterns is False


def test_parse_arguments_with_config():
    """Test argument parsing with config file."""
    test_argv = ["sparkgrep", "--config", "config.json", "file.py"]

    with patch.object(sys, 'argv', test_argv):
        args = parse_arguments()

        assert args.files == ["file.py"]
        assert args.config == "config.json"


def test_parse_arguments_with_additional_patterns():
    """Test argument parsing with additional patterns."""
    # Note: argparse treats everything after --additional-patterns as patterns
    test_argv = ["sparkgrep", "file.py", "--additional-patterns", "pattern1:desc1", "pattern2:desc2"]

    with patch.object(sys, 'argv', test_argv):
        args = parse_arguments()

        assert args.files == ["file.py"]
        assert args.additional_patterns == ["pattern1:desc1", "pattern2:desc2"]


def test_parse_arguments_disable_default_patterns():
    """Test argument parsing with disabled default patterns."""
    test_argv = ["sparkgrep", "--disable-default-patterns", "file.py"]

    with patch.object(sys, 'argv', test_argv):
        args = parse_arguments()

        assert args.files == ["file.py"]
        assert args.disable_default_patterns is True


def test_parse_arguments_no_files():
    """Test argument parsing with no files provided."""
    test_argv = ["sparkgrep"]

    with patch.object(sys, 'argv', test_argv):
        args = parse_arguments()

        assert args.files == []


def test_parse_arguments_all_options():
    """Test argument parsing with all options."""
    test_argv = [
        "sparkgrep",
        "--config", "config.json",
        "--additional-patterns", "pattern1:desc1", "pattern2:desc2",
        "--disable-default-patterns",
        "file1.py", "file2.py"
    ]

    with patch.object(sys, 'argv', test_argv):
        args = parse_arguments()

        assert args.files == ["file1.py", "file2.py"]
        assert args.config == "config.json"
        assert args.additional_patterns == ["pattern1:desc1", "pattern2:desc2"]
        assert args.disable_default_patterns is True


def test_parse_arguments_single_additional_pattern():
    """Test parsing single additional pattern."""
    test_argv = ["sparkgrep", "file.py", "--additional-patterns", "single_pattern:description"]

    with patch.object(sys, 'argv', test_argv):
        args = parse_arguments()

        assert args.additional_patterns == ["single_pattern:description"]
        assert args.files == ["file.py"]


def test_parse_arguments_empty_additional_patterns():
    """Test parsing with additional patterns flag but no patterns."""
    test_argv = ["sparkgrep", "file.py", "--additional-patterns"]

    with patch.object(sys, 'argv', test_argv):
        args = parse_arguments()

        # When no patterns are provided after the flag, it should be empty list
        assert args.additional_patterns == []
        assert args.files == ["file.py"]


def test_parse_arguments_multiple_files():
    """Test parsing multiple files."""
    files = ["file1.py", "file2.py", "notebook1.ipynb", "notebook2.ipynb", "script.py"]
    test_argv = ["sparkgrep"] + files

    with patch.object(sys, 'argv', test_argv):
        args = parse_arguments()

        assert args.files == files


def test_parse_arguments_file_with_spaces():
    """Test parsing files with spaces in names."""
    test_argv = ["sparkgrep", "file with spaces.py", "another file.ipynb"]

    with patch.object(sys, 'argv', test_argv):
        args = parse_arguments()

        assert args.files == ["file with spaces.py", "another file.ipynb"]


def test_parse_arguments_special_characters():
    """Test parsing arguments with special characters."""
    test_argv = ["sparkgrep", "--config", "config-file_v2.json", "file@symbol.py"]

    with patch.object(sys, 'argv', test_argv):
        args = parse_arguments()

        assert args.config == "config-file_v2.json"
        assert args.files == ["file@symbol.py"]


def test_parse_arguments_long_patterns():
    """Test parsing with long pattern descriptions."""
    long_pattern = "very_complex_regex_pattern:This is a very long description that explains what this pattern does in detail"
    test_argv = ["sparkgrep", "file.py", "--additional-patterns", long_pattern]

    with patch.object(sys, 'argv', test_argv):
        args = parse_arguments()

        assert args.additional_patterns == [long_pattern]
        assert args.files == ["file.py"]


def test_parse_arguments_unicode_filenames():
    """Test parsing with unicode filenames."""
    unicode_files = ["fichier_français.py", "文件_中文.ipynb", "файл_русский.py"]
    test_argv = ["sparkgrep"] + unicode_files

    with patch.object(sys, 'argv', test_argv):
        args = parse_arguments()

        assert args.files == unicode_files


def test_parse_arguments_patterns_with_special_regex():
    """Test parsing patterns with special regex characters."""
    regex_patterns = [
        r"\.show\(\):Show method pattern",
        r"\$\{.*\}:Variable substitution pattern",
        r"[a-zA-Z]+\(\):Function call pattern"
    ]
    test_argv = ["sparkgrep", "file.py", "--additional-patterns"] + regex_patterns

    with patch.object(sys, 'argv', test_argv):
        args = parse_arguments()

        assert args.additional_patterns == regex_patterns
        assert args.files == ["file.py"]


def test_parse_arguments_mixed_file_extensions():
    """Test parsing with various file extensions."""
    files = ["script.py", "notebook.ipynb", "module.py", "analysis.ipynb"]
    test_argv = ["sparkgrep"] + files

    with patch.object(sys, 'argv', test_argv):
        args = parse_arguments()

        assert args.files == files


def test_parse_arguments_relative_and_absolute_paths():
    """Test parsing with mixed path types."""
    files = ["./relative/path.py", "/absolute/path.ipynb", "../parent/file.py"]
    test_argv = ["sparkgrep"] + files

    with patch.object(sys, 'argv', test_argv):
        args = parse_arguments()

        assert args.files == files


def test_parse_arguments_config_with_spaces():
    """Test parsing config file with spaces in path."""
    test_argv = ["sparkgrep", "--config", "path with spaces/config file.json", "file.py"]

    with patch.object(sys, 'argv', test_argv):
        args = parse_arguments()

        assert args.config == "path with spaces/config file.json"


def test_parse_arguments_empty_file_list():
    """Test parsing with just flags but no files."""
    test_argv = ["sparkgrep", "--disable-default-patterns", "--config", "config.json"]

    with patch.object(sys, 'argv', test_argv):
        args = parse_arguments()

        assert args.files == []
        assert args.disable_default_patterns is True
        assert args.config == "config.json"


def test_parse_arguments_order_independence():
    """Test that argument order doesn't matter."""
    # Test different orders of the same arguments
    files = ["file1.py", "file2.py"]

    orders = [
        ["sparkgrep", "--config", "config.json", "--disable-default-patterns"] + files,
        ["sparkgrep", "--disable-default-patterns", "--config", "config.json"] + files,
        ["sparkgrep"] + files + ["--config", "config.json", "--disable-default-patterns"],
    ]

    for test_argv in orders:
        with patch.object(sys, 'argv', test_argv):
            args = parse_arguments()

            assert args.files == files
            assert args.config == "config.json"
            assert args.disable_default_patterns is True


def test_parse_arguments_help_description():
    """Test that the parser has proper help text."""
    test_argv = ["sparkgrep", "file.py"]

    with patch.object(sys, 'argv', test_argv):
        args = parse_arguments()

        # Basic smoke test - make sure parsing doesn't crash
        assert hasattr(args, 'files')
        assert hasattr(args, 'config')
        assert hasattr(args, 'additional_patterns')
        assert hasattr(args, 'disable_default_patterns')


def test_parse_arguments_return_type():
    """Test that parse_arguments returns the correct type."""
    test_argv = ["sparkgrep", "file.py"]

    with patch.object(sys, 'argv', test_argv):
        args = parse_arguments()

        # Should return argparse.Namespace-like object
        assert hasattr(args, 'files')
        assert hasattr(args, 'config')
        assert hasattr(args, 'additional_patterns')
        assert hasattr(args, 'disable_default_patterns')

        # Check attribute types
        assert isinstance(args.files, list)
        assert args.config is None or isinstance(args.config, str)
        assert args.additional_patterns is None or isinstance(args.additional_patterns, list)
        assert isinstance(args.disable_default_patterns, bool)


def test_parse_arguments_default_values():
    """Test default values for all arguments."""
    test_argv = ["sparkgrep"]

    with patch.object(sys, 'argv', test_argv):
        args = parse_arguments()

        assert args.files == []
        assert args.config is None
        assert args.additional_patterns is None
        assert args.disable_default_patterns is False
