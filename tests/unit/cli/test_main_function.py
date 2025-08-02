"""
Unit tests for CLI main function core functionality.
"""

import pytest
import tempfile
import os
from unittest.mock import patch, MagicMock

from sparkgrep.cli import main


@patch("sparkgrep.cli.parse_arguments")
@patch("sparkgrep.cli.build_patterns_list")
@patch("sparkgrep.cli.process_single_file")
@patch("sparkgrep.cli.report_results")
def test_main_success_no_issues(mock_report, mock_process, mock_build_patterns, mock_parse):
    """Test main function with successful execution and no issues."""
    # Setup mocks
    mock_args = MagicMock()
    mock_args.files = ["file1.py", "file2.py"]
    mock_args.disable_default_patterns = False
    mock_args.additional_patterns = None
    mock_parse.return_value = mock_args

    mock_build_patterns.return_value = [("pattern", "description")]
    mock_process.return_value = []  # No issues

    # Call main
    result = main()

    # Assertions
    assert result == 0
    mock_parse.assert_called_once()
    mock_build_patterns.assert_called_once_with(
        disable_default_patterns=False, additional_patterns=None
    )
    assert mock_process.call_count == 2
    assert mock_report.call_count == 2


@patch("sparkgrep.cli.parse_arguments")
@patch("sparkgrep.cli.build_patterns_list")
@patch("sparkgrep.cli.process_single_file")
@patch("sparkgrep.cli.report_results")
def test_main_success_with_issues(mock_report, mock_process, mock_build_patterns, mock_parse, capsys):
    """Test main function with issues found."""
    # Setup mocks
    mock_args = MagicMock()
    mock_args.files = ["file1.py"]
    mock_args.disable_default_patterns = False
    mock_args.additional_patterns = None
    mock_parse.return_value = mock_args

    mock_build_patterns.return_value = [("pattern", "description")]
    mock_process.return_value = [(1, "issue", "line content")]  # One issue

    # Call main
    result = main()

    # Assertions
    assert result == 1
    mock_parse.assert_called_once()
    mock_build_patterns.assert_called_once()
    mock_process.assert_called_once()
    mock_report.assert_called_once()

    # Check output
    captured = capsys.readouterr()
    assert "Found 1 useless Spark action(s)" in captured.out
    assert "Please remove these before committing." in captured.out


@patch("sparkgrep.cli.parse_arguments")
@patch("sparkgrep.cli.build_patterns_list")
@patch("sparkgrep.cli.process_single_file")
@patch("sparkgrep.cli.report_results")
def test_main_multiple_files_with_issues(mock_report, mock_process, mock_build_patterns, mock_parse, capsys):
    """Test main function with multiple files having issues."""
    # Setup mocks
    mock_args = MagicMock()
    mock_args.files = ["file1.py", "file2.py"]
    mock_args.disable_default_patterns = False
    mock_args.additional_patterns = None
    mock_parse.return_value = mock_args

    mock_build_patterns.return_value = [("pattern", "description")]
    mock_process.side_effect = [
        [(1, "issue1", "line1"), (2, "issue2", "line2")],  # 2 issues in file1
        [(3, "issue3", "line3")],  # 1 issue in file2
    ]

    # Call main
    result = main()

    # Assertions
    assert result == 1
    assert mock_process.call_count == 2
    assert mock_report.call_count == 2

    # Check output
    captured = capsys.readouterr()
    assert "Found 3 useless Spark action(s)" in captured.out


@patch("sparkgrep.cli.parse_arguments")
def test_main_no_files_provided(mock_parse, capsys):
    """Test main function when no files are provided."""
    mock_args = MagicMock()
    mock_args.files = []
    mock_parse.return_value = mock_args

    result = main()

    assert result == 0
    captured = capsys.readouterr()
    assert "No files provided" in captured.out


@patch("sparkgrep.cli.parse_arguments")
@patch("sparkgrep.cli.build_patterns_list")
def test_main_no_patterns_to_check(mock_build_patterns, mock_parse, capsys):
    """Test main function when no patterns are available to check."""
    mock_args = MagicMock()
    mock_args.files = ["file1.py"]
    mock_args.disable_default_patterns = True
    mock_args.additional_patterns = None
    mock_parse.return_value = mock_args

    mock_build_patterns.return_value = []  # No patterns

    result = main()

    assert result == 0
    captured = capsys.readouterr()
    assert "No patterns to check" in captured.out


@patch("sparkgrep.cli.parse_arguments")
@patch("sparkgrep.cli.build_patterns_list")
@patch("sparkgrep.cli.process_single_file")
@patch("sparkgrep.cli.report_results")
def test_main_with_additional_patterns(mock_report, mock_process, mock_build_patterns, mock_parse):
    """Test main function with additional patterns."""
    # Setup mocks
    mock_args = MagicMock()
    mock_args.files = ["file1.py"]
    mock_args.disable_default_patterns = False
    mock_args.additional_patterns = ["custom:Custom pattern"]
    mock_parse.return_value = mock_args

    mock_build_patterns.return_value = [("pattern", "description")]
    mock_process.return_value = []

    # Call main
    result = main()

    # Assertions
    assert result == 0
    mock_build_patterns.assert_called_once_with(
        disable_default_patterns=False,
        additional_patterns=["custom:Custom pattern"],
    )


@patch("sparkgrep.cli.parse_arguments")
@patch("sparkgrep.cli.build_patterns_list")
@patch("sparkgrep.cli.process_single_file")
@patch("sparkgrep.cli.report_results")
def test_main_with_disabled_default_patterns(mock_report, mock_process, mock_build_patterns, mock_parse):
    """Test main function with disabled default patterns."""
    # Setup mocks
    mock_args = MagicMock()
    mock_args.files = ["file1.py"]
    mock_args.disable_default_patterns = True
    mock_args.additional_patterns = ["custom:Custom pattern"]
    mock_parse.return_value = mock_args

    mock_build_patterns.return_value = [("custom", "Custom pattern")]
    mock_process.return_value = []

    # Call main
    result = main()

    # Assertions
    assert result == 0
    mock_build_patterns.assert_called_once_with(
        disable_default_patterns=True, additional_patterns=["custom:Custom pattern"]
    )


@patch("sparkgrep.cli.parse_arguments")
@patch("sparkgrep.cli.build_patterns_list")
@patch("sparkgrep.cli.process_single_file")
@patch("sparkgrep.cli.report_results")
def test_main_file_processing_order(mock_report, mock_process, mock_build_patterns, mock_parse):
    """Test that files are processed in the correct order."""
    # Setup mocks
    mock_args = MagicMock()
    mock_args.files = ["file1.py", "file2.py", "file3.py"]
    mock_args.disable_default_patterns = False
    mock_args.additional_patterns = None
    mock_parse.return_value = mock_args

    mock_build_patterns.return_value = [("pattern", "description")]
    mock_process.return_value = []

    # Call main
    main()

    # Check that files were processed in order
    expected_calls = [
        (("file1.py", [("pattern", "description")]),),
        (("file2.py", [("pattern", "description")]),),
        (("file3.py", [("pattern", "description")]),),
    ]

    assert mock_process.call_args_list == expected_calls


@patch("sparkgrep.cli.parse_arguments")
@patch("sparkgrep.cli.build_patterns_list")
@patch("sparkgrep.cli.process_single_file")
@patch("sparkgrep.cli.report_results")
def test_main_issue_counting(mock_report, mock_process, mock_build_patterns, mock_parse, capsys):
    """Test that issues are counted correctly across files."""
    # Setup mocks
    mock_args = MagicMock()
    mock_args.files = ["file1.py", "file2.py", "file3.py"]
    mock_args.disable_default_patterns = False
    mock_args.additional_patterns = None
    mock_parse.return_value = mock_args

    mock_build_patterns.return_value = [("pattern", "description")]
    mock_process.side_effect = [
        [(1, "issue1", "line1"), (2, "issue2", "line2")],  # 2 issues
        [],  # 0 issues
        [
            (3, "issue3", "line3"),
            (4, "issue4", "line4"),
            (5, "issue5", "line5"),
        ],  # 3 issues
    ]

    # Call main
    result = main()

    # Assertions
    assert result == 1
    captured = capsys.readouterr()
    assert "Found 5 useless Spark action(s)" in captured.out


@patch("sparkgrep.cli.parse_arguments")
@patch("sparkgrep.cli.build_patterns_list")
@patch("sparkgrep.cli.process_single_file")
@patch("sparkgrep.cli.report_results")
def test_main_with_config_file_argument(mock_report, mock_process, mock_build_patterns, mock_parse):
    """Test main function with config file argument (not implemented yet)."""
    mock_args = MagicMock()
    mock_args.files = ["test.py"]
    mock_args.config = "config.json"
    mock_args.disable_default_patterns = False
    mock_args.additional_patterns = None
    mock_parse.return_value = mock_args

    mock_build_patterns.return_value = [("pattern", "description")]
    mock_process.return_value = []

    result = main()

    assert result == 0
    # Config is parsed but not used yet (per the comment in the code)
    mock_parse.assert_called_once()


@patch("sparkgrep.cli.parse_arguments")
@patch("sparkgrep.cli.build_patterns_list")
@patch("sparkgrep.cli.process_single_file")
@patch("sparkgrep.cli.report_results")
def test_main_mixed_file_results(mock_report, mock_process, mock_build_patterns, mock_parse, capsys):
    """Test main function with mixed results across files."""
    mock_args = MagicMock()
    mock_args.files = ["clean.py", "problematic1.py", "clean2.py", "problematic2.py"]
    mock_args.disable_default_patterns = False
    mock_args.additional_patterns = None
    mock_parse.return_value = mock_args

    mock_build_patterns.return_value = [("pattern", "description")]

    # Mixed results: some files clean, some with issues
    mock_process.side_effect = [
        [],  # clean.py - no issues
        [(1, "issue1", "line1"), (2, "issue2", "line2")],  # problematic1.py - 2 issues
        [],  # clean2.py - no issues
        [(5, "issue3", "line3")],  # problematic2.py - 1 issue
    ]

    result = main()

    assert result == 1  # Should fail due to issues
    captured = capsys.readouterr()
    assert "Found 3 useless Spark action(s)" in captured.out


@patch("sparkgrep.cli.parse_arguments")
@patch("sparkgrep.cli.build_patterns_list")
@patch("sparkgrep.cli.process_single_file")
@patch("sparkgrep.cli.report_results")
def test_main_empty_patterns_with_files(mock_report, mock_process, mock_build_patterns, mock_parse, capsys):
    """Test main function with files but empty patterns list."""
    mock_args = MagicMock()
    mock_args.files = ["test1.py", "test2.py"]
    mock_args.disable_default_patterns = True
    mock_args.additional_patterns = []
    mock_parse.return_value = mock_args

    mock_build_patterns.return_value = []  # Empty patterns

    result = main()

    assert result == 0
    captured = capsys.readouterr()
    assert "No patterns to check" in captured.out

    # Should not process any files when no patterns
    mock_process.assert_not_called()
    mock_report.assert_not_called()


def test_main_entry_point_integration():
    """Test the main function as an entry point."""
    # Test with minimal arguments that should succeed
    test_argv = ["script"]

    with patch("sys.argv", test_argv):
        result = main()
        assert result == 0  # Should succeed with no files
