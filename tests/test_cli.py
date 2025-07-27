"""
Unit tests for the cli module.
"""

import pytest
import sys
from unittest.mock import patch, MagicMock
import tempfile
import os

from src.cli import parse_arguments, main


class TestParseArguments:
    """Test the parse_arguments function."""

    def test_parse_arguments_basic(self):
        """Test basic argument parsing."""
        with patch("sys.argv", ["script", "file1.py", "file2.ipynb"]):
            args = parse_arguments()

            assert args.files == ["file1.py", "file2.ipynb"]
            assert args.config is None
            assert args.additional_patterns is None
            assert args.disable_default_patterns is False

    def test_parse_arguments_with_config(self):
        """Test argument parsing with config file."""
        with patch("sys.argv", ["script", "file1.py", "--config", "config.json"]):
            args = parse_arguments()

            assert args.files == ["file1.py"]
            assert args.config == "config.json"

    def test_parse_arguments_with_additional_patterns(self):
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

    def test_parse_arguments_disable_default_patterns(self):
        """Test argument parsing with disabled default patterns."""
        with patch("sys.argv", ["script", "file1.py", "--disable-default-patterns"]):
            args = parse_arguments()

            assert args.files == ["file1.py"]
            assert args.disable_default_patterns is True

    def test_parse_arguments_no_files(self):
        """Test argument parsing with no files provided."""
        with patch("sys.argv", ["script"]):
            args = parse_arguments()

            assert args.files == []

    def test_parse_arguments_all_options(self):
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


class TestMain:
    """Test the main function."""

    @patch("scripts.cli.parse_arguments")
    @patch("scripts.cli.build_patterns_list")
    @patch("scripts.cli.process_single_file")
    @patch("scripts.cli.report_results")
    def test_main_success_no_issues(
        self, mock_report, mock_process, mock_build_patterns, mock_parse
    ):
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

    @patch("scripts.cli.parse_arguments")
    @patch("scripts.cli.build_patterns_list")
    @patch("scripts.cli.process_single_file")
    @patch("scripts.cli.report_results")
    def test_main_success_with_issues(
        self, mock_report, mock_process, mock_build_patterns, mock_parse, capsys
    ):
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
        assert "Found 1 useless Databricks action(s)" in captured.out
        assert "Please remove these before committing." in captured.out

    @patch("scripts.cli.parse_arguments")
    @patch("scripts.cli.build_patterns_list")
    @patch("scripts.cli.process_single_file")
    @patch("scripts.cli.report_results")
    def test_main_multiple_files_with_issues(
        self, mock_report, mock_process, mock_build_patterns, mock_parse, capsys
    ):
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
        assert "Found 3 useless Databricks action(s)" in captured.out

    @patch("scripts.cli.parse_arguments")
    def test_main_no_files_provided(self, mock_parse, capsys):
        """Test main function when no files are provided."""
        mock_args = MagicMock()
        mock_args.files = []
        mock_parse.return_value = mock_args

        result = main()

        assert result == 0
        captured = capsys.readouterr()
        assert "No files provided" in captured.out

    @patch("scripts.cli.parse_arguments")
    @patch("scripts.cli.build_patterns_list")
    def test_main_no_patterns_to_check(self, mock_build_patterns, mock_parse, capsys):
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

    @patch("scripts.cli.parse_arguments")
    @patch("scripts.cli.build_patterns_list")
    @patch("scripts.cli.process_single_file")
    @patch("scripts.cli.report_results")
    def test_main_with_additional_patterns(
        self, mock_report, mock_process, mock_build_patterns, mock_parse
    ):
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

    @patch("scripts.cli.parse_arguments")
    @patch("scripts.cli.build_patterns_list")
    @patch("scripts.cli.process_single_file")
    @patch("scripts.cli.report_results")
    def test_main_with_disabled_default_patterns(
        self, mock_report, mock_process, mock_build_patterns, mock_parse
    ):
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

    @patch("scripts.cli.parse_arguments")
    @patch("scripts.cli.build_patterns_list")
    @patch("scripts.cli.process_single_file")
    @patch("scripts.cli.report_results")
    def test_main_file_processing_order(
        self, mock_report, mock_process, mock_build_patterns, mock_parse
    ):
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
        result = main()

        # Check that files were processed in order
        expected_calls = [
            (("file1.py", [("pattern", "description")]),),
            (("file2.py", [("pattern", "description")]),),
            (("file3.py", [("pattern", "description")]),),
        ]

        assert mock_process.call_args_list == expected_calls

    @patch("scripts.cli.parse_arguments")
    @patch("scripts.cli.build_patterns_list")
    @patch("scripts.cli.process_single_file")
    @patch("scripts.cli.report_results")
    def test_main_issue_counting(
        self, mock_report, mock_process, mock_build_patterns, mock_parse, capsys
    ):
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
        assert "Found 5 useless Databricks action(s)" in captured.out

    @patch("scripts.cli.parse_arguments")
    @patch("scripts.cli.build_patterns_list")
    @patch("scripts.cli.process_single_file")
    @patch("scripts.cli.report_results")
    def test_main_real_integration_scenario(
        self, mock_report, mock_process, mock_build_patterns, mock_parse
    ):
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
            from src.patterns import build_patterns_list
            from src.file_processors import process_single_file

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

    @patch("scripts.cli.parse_arguments")
    @patch("scripts.cli.build_patterns_list")
    @patch("scripts.cli.process_single_file")
    @patch("scripts.cli.report_results")
    def test_main_exception_handling(
        self, mock_report, mock_process, mock_build_patterns, mock_parse
    ):
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

    def test_main_entry_point_integration(self):
        """Test the main function as an entry point."""
        # Test with minimal arguments that should succeed
        test_argv = ["script"]

        with patch("sys.argv", test_argv):
            result = main()
            assert result == 0  # Should succeed with no files
