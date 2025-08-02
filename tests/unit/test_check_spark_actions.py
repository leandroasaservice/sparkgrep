"""
Unit tests for the check_spark_actions module.
"""

import pytest
import sys
import os
from unittest.mock import patch, MagicMock
import subprocess


# Check Spark Actions Script Tests

def test_script_execution_direct_run():
    """Test running the script directly."""
    with patch("sparkgrep.check_spark_actions.main") as mock_main:
        mock_main.return_value = 0

        # Simulate direct script execution
        with patch("sys.argv", ["check_spark_actions.py"]):
            with patch("builtins.__name__", "__main__"):
                # Import and execute the script
                import sparkgrep.check_spark_actions

                # Verify main was called
                mock_main.assert_called_once()


def test_script_execution_with_arguments():
    """Test running the script with command line arguments."""
    with patch("sparkgrep.check_spark_actions.main") as mock_main:
        mock_main.return_value = 1

        test_args = ["check_spark_actions.py", "file1.py", "file2.py"]
        with patch("sys.argv", test_args):
            with patch("builtins.__name__", "__main__"):
                # Import and execute
                import sparkgrep.check_spark_actions

                mock_main.assert_called_once()


def test_module_import_as_library():
    """Test importing the module as a library."""
    # This should not trigger script execution
    with patch("sparkgrep.check_spark_actions.main") as mock_main:
        # Import as module (not __main__)
        from sparkgrep import check_spark_actions

        # main should not be called when imported as module
        mock_main.assert_not_called()


def test_sys_path_modification():
    """Test that script modifies sys.path correctly."""
    with patch("sparkgrep.check_spark_actions.main") as mock_main:
        mock_main.return_value = 0

        with patch("sys.argv", ["check_spark_actions.py"]):
            with patch("builtins.__name__", "__main__"):
                with patch("os.path.dirname") as mock_dirname:
                    with patch("os.path.abspath") as mock_abspath:
                        mock_abspath.return_value = "/fake/path/check_spark_actions.py"
                        mock_dirname.return_value = "/fake/path"

                        # Import and execute
                        import sparkgrep.check_spark_actions

                        # Verify path operations were called
                        mock_abspath.assert_called()
                        mock_dirname.assert_called()


def test_script_exit_code_success():
    """Test script exits with success code."""
    with patch("sparkgrep.check_spark_actions.main") as mock_main:
        with patch("sys.exit") as mock_exit:
            mock_main.return_value = 0

            with patch("sys.argv", ["check_spark_actions.py"]):
                with patch("builtins.__name__", "__main__"):
                    import sparkgrep.check_spark_actions

                    mock_exit.assert_called_with(0)


def test_script_exit_code_failure():
    """Test script exits with failure code."""
    with patch("sparkgrep.check_spark_actions.main") as mock_main:
        with patch("sys.exit") as mock_exit:
            mock_main.return_value = 1

            with patch("sys.argv", ["check_spark_actions.py"]):
                with patch("builtins.__name__", "__main__"):
                    import sparkgrep.check_spark_actions

                    mock_exit.assert_called_with(1)


def test_main_function_import_when_module():
    """Test that main function is properly imported when used as module."""
    # Test relative import path
    from sparkgrep.check_spark_actions import main

    # Should be able to import main function
    assert callable(main)


def test_script_exception_handling():
    """Test script behavior when main raises an exception."""
    with patch("sparkgrep.check_spark_actions.main") as mock_main:
        mock_main.side_effect = Exception("Test exception")

        with patch("sys.argv", ["check_spark_actions.py"]):
            with patch("builtins.__name__", "__main__"):
                with pytest.raises(Exception, match="Test exception"):
                    import sparkgrep.check_spark_actions


def test_script_file_path_resolution():
    """Test that script correctly resolves its own file path."""
    with patch("sparkgrep.check_spark_actions.main") as mock_main:
        mock_main.return_value = 0

        with patch("sys.argv", ["check_spark_actions.py"]):
            with patch("builtins.__name__", "__main__"):
                with patch("os.path.abspath") as mock_abspath:
                    with patch("os.path.dirname") as mock_dirname:
                        # Mock the path resolution
                        mock_abspath.return_value = "/test/path/to/check_spark_actions.py"
                        mock_dirname.return_value = "/test/path/to"

                        import sparkgrep.check_spark_actions

                        # Verify __file__ was used correctly
                        mock_abspath.assert_called()
                        mock_dirname.assert_called()


def test_import_error_handling():
    """Test handling of import errors in different execution contexts."""
    # Test when cli module import fails
    with patch("builtins.__import__") as mock_import:
        mock_import.side_effect = ImportError("Cannot import cli")

        with pytest.raises(ImportError):
            from sparkgrep import check_spark_actions


def test_script_with_sys_path_insertion():
    """Test that the script correctly inserts its directory into sys.path."""
    with patch("sparkgrep.check_spark_actions.main") as mock_main:
        mock_main.return_value = 0

        # Mock the path operations
        fake_script_path = "/fake/path/to/script/check_spark_actions.py"
        fake_script_dir = "/fake/path/to/script"

        with patch("os.path.abspath", return_value=fake_script_path):
            with patch("os.path.dirname", return_value=fake_script_dir):
                with patch("sys.argv", ["check_spark_actions.py"]):
                    with patch("builtins.__name__", "__main__"):
                        import sparkgrep.check_spark_actions

                        # Verify that sys.path.insert was called with the script directory
                        # (This is indirectly tested by checking if the mock was called)
                        mock_main.assert_called_once()


def test_module_level_imports():
    """Test that module-level imports work correctly."""
    # Test that we can import the module without errors
    from sparkgrep import check_spark_actions

    # Check that the main function is available
    assert hasattr(check_spark_actions, 'main')
    assert callable(check_spark_actions.main)


def test_script_name_detection():
    """Test that the script correctly detects when it's run as main."""
    with patch("sparkgrep.check_spark_actions.main") as mock_main:
        mock_main.return_value = 0

        # Test with __name__ == "__main__"
        with patch("builtins.__name__", "__main__"):
            with patch("sys.argv", ["script"]):
                import sparkgrep.check_spark_actions
                mock_main.assert_called_once()

        # Reset mock
        mock_main.reset_mock()

        # Test with __name__ != "__main__"
        with patch("builtins.__name__", "not_main"):
            import sparkgrep.check_spark_actions
            mock_main.assert_not_called()


# Integration Tests

@pytest.mark.integration
def test_real_script_execution():
    """Test actual script execution (integration test)."""
    script_path = "src/sparkgrep/check_spark_actions.py"

    # Test with no arguments (should show help or handle gracefully)
    result = subprocess.run([
        sys.executable, script_path
    ], capture_output=True, text=True)

    # Should exit with 0 (no files provided)
    assert result.returncode == 0


@pytest.mark.integration
def test_script_with_nonexistent_file():
    """Test script with nonexistent file."""
    script_path = "src/sparkgrep/check_spark_actions.py"

    result = subprocess.run([
        sys.executable, script_path, "nonexistent_file.py"
    ], capture_output=True, text=True)

    # Should handle gracefully
    assert result.returncode == 0


@pytest.mark.integration
def test_script_help_functionality():
    """Test script help output."""
    script_path = "src/sparkgrep/check_spark_actions.py"

    result = subprocess.run([
        sys.executable, script_path, "--help"
    ], capture_output=True, text=True)

    # Should show help and exit successfully
    assert result.returncode == 0
    assert "Check for useless Spark actions" in result.stdout


def test_module_entry_point_consistency():
    """Test that module entry point works consistently."""
    # Test that both import methods work
    from sparkgrep.check_spark_actions import main as main1
    from sparkgrep import check_spark_actions
    main2 = check_spark_actions.main

    # Should be the same function
    assert main1 is main2


def test_error_propagation():
    """Test that errors from main function are properly propagated."""
    with patch("sparkgrep.check_spark_actions.main") as mock_main:
        # Test different return codes
        test_codes = [0, 1, 2, -1]

        for code in test_codes:
            mock_main.return_value = code

            with patch("sys.exit") as mock_exit:
                with patch("sys.argv", ["script"]):
                    with patch("builtins.__name__", "__main__"):
                        import sparkgrep.check_spark_actions

                        mock_exit.assert_called_with(code)

            # Reset for next iteration
            mock_main.reset_mock()


def test_import_isolation():
    """Test that imports don't interfere with each other."""
    # Multiple imports should work without side effects
    from sparkgrep import check_spark_actions as ca1
    from sparkgrep.check_spark_actions import main as main1

    # Second set of imports
    from sparkgrep import check_spark_actions as ca2
    from sparkgrep.check_spark_actions import main as main2

    # Should be the same objects
    assert ca1 is ca2
    assert main1 is main2
