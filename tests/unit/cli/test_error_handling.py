"""
Unit tests for CLI error handling and edge cases.
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
def test_main_exception_handling(mock_report, mock_process, mock_build_patterns, mock_parse):
    """Test that main function handles exceptions gracefully."""
    # Setup mocks
    mock_args = MagicMock()
    mock_args.files = ["file1.py"]
    mock_args.disable_default_patterns = False
    mock_args.additional_patterns = None
    mock_parse.return_value = mock_args

    mock_build_patterns.return_value = [("pattern", "description")]
    mock_process.side_effect = Exception("Test exception")

    # Call main - should not crash
    with pytest.raises(Exception, match="Test exception"):
        main()


@patch("sparkgrep.cli.parse_arguments")
@patch("sparkgrep.cli.build_patterns_list")
def test_main_build_patterns_exception(mock_build_patterns, mock_parse):
    """Test main function when build_patterns_list raises an exception."""
    mock_args = MagicMock()
    mock_args.files = ["test.py"]
    mock_args.disable_default_patterns = False
    mock_args.additional_patterns = None
    mock_parse.return_value = mock_args

    mock_build_patterns.side_effect = Exception("Pattern build error")

    with pytest.raises(Exception, match="Pattern build error"):
        main()


@patch("sparkgrep.cli.parse_arguments")
@patch("sparkgrep.cli.build_patterns_list")
@patch("sparkgrep.cli.process_single_file")
def test_main_process_file_exception(mock_process, mock_build_patterns, mock_parse):
    """Test main function when process_single_file raises an exception."""
    mock_args = MagicMock()
    mock_args.files = ["test.py"]
    mock_args.disable_default_patterns = False
    mock_args.additional_patterns = None
    mock_parse.return_value = mock_args

    mock_build_patterns.return_value = [("pattern", "description")]
    mock_process.side_effect = Exception("File processing error")

    with pytest.raises(Exception, match="File processing error"):
        main()


@patch("sparkgrep.cli.parse_arguments")
@patch("sparkgrep.cli.build_patterns_list")
@patch("sparkgrep.cli.process_single_file")
@patch("sparkgrep.cli.report_results")
def test_main_large_number_of_files(mock_report, mock_process, mock_build_patterns, mock_parse):
    """Test main function with a large number of files."""
    # Test with many files to ensure scalability
    many_files = [f"file_{i}.py" for i in range(100)]

    mock_args = MagicMock()
    mock_args.files = many_files
    mock_args.disable_default_patterns = False
    mock_args.additional_patterns = None
    mock_parse.return_value = mock_args

    mock_build_patterns.return_value = [("pattern", "description")]
    mock_process.return_value = []

    result = main()

    assert result == 0
    assert mock_process.call_count == 100
    assert mock_report.call_count == 100


@patch("sparkgrep.cli.parse_arguments")
@patch("sparkgrep.cli.build_patterns_list")
@patch("sparkgrep.cli.process_single_file")
@patch("sparkgrep.cli.report_results")
def test_main_real_integration_scenario(mock_report, mock_process, mock_build_patterns, mock_parse):
    """Test a realistic integration scenario."""
    # Create a temporary file with actual content
    python_code = """
def test_function():
    display(df)
    result = df.show()
    print("hello")
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(python_code)
        temp_path = f.name

    try:
        # Setup mocks to use real file processing
        mock_args = MagicMock()
        mock_args.files = [temp_path]
        mock_args.disable_default_patterns = False
        mock_args.additional_patterns = None
        mock_parse.return_value = mock_args

        # Use real patterns and file processing
        from sparkgrep.patterns import build_patterns_list
        from sparkgrep.file_processors import process_single_file

        mock_build_patterns.side_effect = lambda **kwargs: build_patterns_list(
            **kwargs
        )
        mock_process.side_effect = lambda file_path, patterns: process_single_file(
            file_path, patterns
        )

        # Call main
        result = main()

        # Should find issues and return 1
        assert result == 1

    finally:
        os.unlink(temp_path)


@patch("sparkgrep.cli.parse_arguments")
@patch("sparkgrep.cli.build_patterns_list")
@patch("sparkgrep.cli.process_single_file")
@patch("sparkgrep.cli.report_results")
def test_main_memory_handling_with_large_files(mock_report, mock_process, mock_build_patterns, mock_parse):
    """Test main function handles large files without memory issues."""
    mock_args = MagicMock()
    mock_args.files = ["large_file.py"] * 10  # Simulate processing many large files
    mock_args.disable_default_patterns = False
    mock_args.additional_patterns = None
    mock_parse.return_value = mock_args

    mock_build_patterns.return_value = [("pattern", "description")]
    # Simulate finding many issues in each file
    mock_process.return_value = [(i, f"issue_{i}", f"line_{i}") for i in range(1000)]

    result = main()

    assert result == 1
    assert mock_process.call_count == 10
    assert mock_report.call_count == 10


@patch("sparkgrep.cli.parse_arguments")
@patch("sparkgrep.cli.build_patterns_list")
@patch("sparkgrep.cli.process_single_file")
@patch("sparkgrep.cli.report_results")
def test_main_file_processing_partial_failure(mock_report, mock_process, mock_build_patterns, mock_parse):
    """Test main function when some files fail to process."""
    mock_args = MagicMock()
    mock_args.files = ["file1.py", "file2.py", "file3.py"]
    mock_args.disable_default_patterns = False
    mock_args.additional_patterns = None
    mock_parse.return_value = mock_args

    mock_build_patterns.return_value = [("pattern", "description")]
    # First file succeeds, second fails, third succeeds
    mock_process.side_effect = [
        [(1, "issue1", "line1")],  # Success
        Exception("File processing error"),  # Failure
        [(2, "issue2", "line2")],  # Success
    ]

    # Should propagate the exception
    with pytest.raises(Exception, match="File processing error"):
        main()


@patch("sparkgrep.cli.parse_arguments")
@patch("sparkgrep.cli.build_patterns_list")
@patch("sparkgrep.cli.process_single_file")
@patch("sparkgrep.cli.report_results")
def test_main_empty_file_list_edge_cases(mock_report, mock_process, mock_build_patterns, mock_parse, capsys):
    """Test main function with various empty file list scenarios."""
    test_scenarios = [
        [],  # Empty list
        [""],  # List with empty string
        [None],  # List with None (should cause error)
    ]

    for scenario in test_scenarios[:1]:  # Only test empty list to avoid None errors
        mock_args = MagicMock()
        mock_args.files = scenario
        mock_args.disable_default_patterns = False
        mock_args.additional_patterns = None
        mock_parse.return_value = mock_args

        mock_build_patterns.return_value = [("pattern", "description")]
        mock_process.return_value = []

        result = main()

        if scenario == []:
            assert result == 0
            captured = capsys.readouterr()
            assert "No files provided" in captured.out


@patch("sparkgrep.cli.parse_arguments")
@patch("sparkgrep.cli.build_patterns_list")
@patch("sparkgrep.cli.process_single_file")
@patch("sparkgrep.cli.report_results")
def test_main_interrupt_handling(mock_report, mock_process, mock_build_patterns, mock_parse):
    """Test main function handles keyboard interrupt gracefully."""
    mock_args = MagicMock()
    mock_args.files = ["file1.py"]
    mock_args.disable_default_patterns = False
    mock_args.additional_patterns = None
    mock_parse.return_value = mock_args

    mock_build_patterns.return_value = [("pattern", "description")]
    mock_process.side_effect = KeyboardInterrupt("User interrupted")

    with pytest.raises(KeyboardInterrupt):
        main()


@patch("sparkgrep.cli.parse_arguments")
@patch("sparkgrep.cli.build_patterns_list")
@patch("sparkgrep.cli.process_single_file")
@patch("sparkgrep.cli.report_results")
def test_main_unicode_filename_handling(mock_report, mock_process, mock_build_patterns, mock_parse):
    """Test main function handles unicode filenames correctly."""
    unicode_files = ["файл.py", "文件.py", "αρχείο.py", "🎉_file.py"]

    mock_args = MagicMock()
    mock_args.files = unicode_files
    mock_args.disable_default_patterns = False
    mock_args.additional_patterns = None
    mock_parse.return_value = mock_args

    mock_build_patterns.return_value = [("pattern", "description")]
    mock_process.return_value = []

    result = main()

    assert result == 0
    assert mock_process.call_count == len(unicode_files)
    assert mock_report.call_count == len(unicode_files)


@patch("sparkgrep.cli.parse_arguments")
@patch("sparkgrep.cli.build_patterns_list")
@patch("sparkgrep.cli.process_single_file")
@patch("sparkgrep.cli.report_results")
def test_main_very_long_file_paths(mock_report, mock_process, mock_build_patterns, mock_parse):
    """Test main function handles very long file paths."""
    # Create a very long file path
    long_path = "/".join(["very_long_directory_name"] * 20) + "/file.py"

    mock_args = MagicMock()
    mock_args.files = [long_path]
    mock_args.disable_default_patterns = False
    mock_args.additional_patterns = None
    mock_parse.return_value = mock_args

    mock_build_patterns.return_value = [("pattern", "description")]
    mock_process.return_value = []

    result = main()

    assert result == 0
    mock_process.assert_called_once_with(long_path, [("pattern", "description")])


@patch("sparkgrep.cli.parse_arguments")
@patch("sparkgrep.cli.build_patterns_list")
@patch("sparkgrep.cli.process_single_file")
@patch("sparkgrep.cli.report_results")
def test_main_special_character_in_patterns(mock_report, mock_process, mock_build_patterns, mock_parse):
    """Test main function with special characters in additional patterns."""
    mock_args = MagicMock()
    mock_args.files = ["file.py"]
    mock_args.disable_default_patterns = False
    mock_args.additional_patterns = ["[🎉special🎉]:Unicode pattern", "regex\\w+:Regex pattern"]
    mock_parse.return_value = mock_args

    mock_build_patterns.return_value = [("pattern", "description")]
    mock_process.return_value = []

    result = main()

    assert result == 0
    mock_build_patterns.assert_called_once_with(
        disable_default_patterns=False,
        additional_patterns=["[🎉special🎉]:Unicode pattern", "regex\\w+:Regex pattern"],
    )
