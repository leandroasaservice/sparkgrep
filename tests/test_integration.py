"""
Integration tests for the complete Databricks actions checker workflow.
"""

import pytest
import tempfile
import os
import json
import subprocess
import sys
from pathlib import Path

from src.cli import main
from src.patterns import USELESS_PATTERNS
from src.file_processors import process_single_file
from src.patterns import build_patterns_list


class TestEndToEndIntegration:
    """Test complete end-to-end workflows."""

    def test_full_workflow_python_file_with_issues(self, capsys):
        """Test complete workflow with Python file containing issues."""
        python_code = """
def test_function():
    display(df)  # Should be caught
    df.show()  # Should be caught
    df.collect()
    df.count()
    df.toPandas()
    print("This is fine")
    return result
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(python_code)
            temp_path = f.name

        try:
            # Test using the complete workflow
            patterns = build_patterns_list()
            issues = process_single_file(temp_path, patterns)

            # Should find 5 issues
            assert len(issues) == 5

            # Check specific issues
            issue_descriptions = [issue[1] for issue in issues]
            assert "display() function call" in issue_descriptions
            assert ".show() method call" in issue_descriptions
            assert ".collect() call without assignment" in issue_descriptions
            assert ".count() call without assignment" in issue_descriptions
            assert ".toPandas() without assignment" in issue_descriptions

        finally:
            os.unlink(temp_path)

    def test_full_workflow_notebook_with_issues(self):
        """Test complete workflow with Jupyter notebook containing issues."""
        notebook_content = {
            "cells": [
                {
                    "cell_type": "code",
                    "source": "# Setup\nimport pandas as pd\nfrom pyspark.sql import SparkSession",
                    "metadata": {},
                    "outputs": [],
                },
                {
                    "cell_type": "code",
                    "source": "display(df)  # Should be caught",
                    "metadata": {},
                    "outputs": [],
                },
                {
                    "cell_type": "code",
                    "source": "df.show()  # Should be caught\nresult = df.collect()  # Should NOT be caught (assignment)",
                    "metadata": {},
                    "outputs": [],
                },
                {
                    "cell_type": "markdown",
                    "source": "This is markdown with display(df) - should be ignored",
                },
                {
                    "cell_type": "code",
                    "source": "# This is a comment with display(df) - should be ignored\nprint('hello')",
                    "metadata": {},
                    "outputs": [],
                },
            ],
            "metadata": {},
            "nbformat": 4,
            "nbformat_minor": 2,
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".ipynb", delete=False) as f:
            json.dump(notebook_content, f)
            temp_path = f.name

        try:
            patterns = build_patterns_list()
            issues = process_single_file(temp_path, patterns)

            # Should find 2 issues (display and show)
            assert len(issues) == 2

            # Check specific issues
            issue_descriptions = [issue[1] for issue in issues]
            assert "display() function call" in issue_descriptions
            assert ".show() method call" in issue_descriptions

            # Check cell locations
            locations = [issue[0] for issue in issues]
            assert "Cell 2, Line 1" in locations
            assert "Cell 3, Line 1" in locations

        finally:
            os.unlink(temp_path)

    def test_full_workflow_mixed_files(self):
        """Test complete workflow with mixed file types."""
        # Create Python file
        python_code = """
def test_function():
    display(df)
    print("hello")
"""

        # Create notebook file
        notebook_content = {
            "cells": [
                {
                    "cell_type": "code",
                    "source": "df.show()",
                    "metadata": {},
                    "outputs": [],
                }
            ],
            "metadata": {},
            "nbformat": 4,
            "nbformat_minor": 2,
        }

        # Create unsupported file
        text_content = "display(df)\nThis should be ignored"

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False
        ) as py_file, tempfile.NamedTemporaryFile(
            mode="w", suffix=".ipynb", delete=False
        ) as nb_file, tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False
        ) as txt_file:
            py_file.write(python_code)
            py_path = py_file.name

            json.dump(notebook_content, nb_file)
            nb_path = nb_file.name

            txt_file.write(text_content)
            txt_path = txt_file.name

        try:
            patterns = build_patterns_list()

            # Process all files
            py_issues = process_single_file(py_path, patterns)
            nb_issues = process_single_file(nb_path, patterns)
            txt_issues = process_single_file(txt_path, patterns)  # Should be empty

            # Check results
            assert len(py_issues) == 1
            assert len(nb_issues) == 1
            assert len(txt_issues) == 0

            assert py_issues[0][1] == "display() function call"
            assert nb_issues[0][1] == ".show() method call"

        finally:
            os.unlink(py_path)
            os.unlink(nb_path)
            os.unlink(txt_path)

    def test_full_workflow_no_issues(self):
        """Test complete workflow with clean files."""
        python_code = '''
def test_function():
    """
    This function has display(df) in docstring but it's ignored.
    """
    # Also has display(df) in comment but it's ignored
    result = df.collect()  # This is assigned, so it's OK
    pandas_df = df.toPandas()  # This is assigned, so it's OK
    print("All good")
    return result
'''

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(python_code)
            temp_path = f.name

        try:
            patterns = build_patterns_list()
            issues = process_single_file(temp_path, patterns)

            # Should find no issues
            assert len(issues) == 0

        finally:
            os.unlink(temp_path)

    def test_custom_patterns_integration(self):
        """Test integration with custom patterns."""
        python_code = """
def test_function():
    display(df)  # Default pattern
    spark.sql("SELECT * FROM table").show()  # Custom pattern
    custom_debug_function()  # Custom pattern
    print("hello")
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(python_code)
            temp_path = f.name

        try:
            # Test with custom patterns
            patterns = build_patterns_list(
                disable_default_patterns=False,
                additional_patterns=[
                    r"custom_debug_function\s*\(\s*\):Custom debug function",
                    r"\.sql\s*\([^)]*\)\.show\s*\(\s*\):SQL show without assignment",
                ],
            )

            issues = process_single_file(temp_path, patterns)

            # Should find 3 issues (1 default + 2 custom)
            assert len(issues) == 3

            issue_descriptions = [issue[1] for issue in issues]
            assert "display() function call" in issue_descriptions
            assert "Custom debug function" in issue_descriptions
            assert "SQL show without assignment" in issue_descriptions

        finally:
            os.unlink(temp_path)


class TestPreCommitHookIntegration:
    """Test pre-commit hook integration scenarios."""

    def test_pre_commit_hook_success_scenario(self):
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
            import sys
            from unittest.mock import patch

            test_argv = ["check-databricks-actions", temp_path]

            with patch("sys.argv", test_argv):
                result = main()
                assert result == 0  # Success

        finally:
            os.unlink(temp_path)

    def test_pre_commit_hook_failure_scenario(self):
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
            import sys
            from unittest.mock import patch

            test_argv = ["check-databricks-actions", temp_path]

            with patch("sys.argv", test_argv):
                result = main()
                assert result == 1  # Failure

        finally:
            os.unlink(temp_path)

    def test_pre_commit_hook_multiple_files(self):
        """Test pre-commit hook with multiple files."""
        # Create multiple files
        clean_code = """
def clean_function():
    result = df.collect()
    return result
"""

        problematic_code = """
def problematic_function():
    display(df)
    return None
"""

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False
        ) as clean_file, tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False
        ) as problem_file:
            clean_file.write(clean_code)
            clean_path = clean_file.name

            problem_file.write(problematic_code)
            problem_path = problem_file.name

        try:
            # Simulate pre-commit hook call with multiple files
            import sys
            from unittest.mock import patch

            test_argv = ["check-databricks-actions", clean_path, problem_path]

            with patch("sys.argv", test_argv):
                result = main()
                assert result == 1  # Should fail due to problematic file

        finally:
            os.unlink(clean_path)
            os.unlink(problem_path)

    def test_pre_commit_hook_with_options(self):
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
            import sys
            from unittest.mock import patch

            test_argv = [
                "check-databricks-actions",
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


class TestErrorHandlingIntegration:
    """Test error handling in integration scenarios."""

    def test_nonexistent_file_handling(self):
        """Test handling of nonexistent files."""
        import sys
        from unittest.mock import patch

        test_argv = ["check-databricks-actions", "nonexistent.py"]

        with patch("sys.argv", test_argv):
            result = main()
            assert result == 0  # Should succeed (no files processed)

    def test_mixed_existent_nonexistent_files(self):
        """Test handling of mix of existent and nonexistent files."""
        python_code = """
def test_function():
    display(df)
    print("hello")
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(python_code)
            temp_path = f.name

        try:
            import sys
            from unittest.mock import patch

            test_argv = ["check-databricks-actions", temp_path, "nonexistent.py"]

            with patch("sys.argv", test_argv):
                result = main()
                assert result == 1  # Should fail due to issues in existing file

        finally:
            os.unlink(temp_path)

    def test_invalid_notebook_handling(self):
        """Test handling of invalid notebook files."""
        # Create invalid notebook
        invalid_notebook = "This is not valid JSON"

        with tempfile.NamedTemporaryFile(mode="w", suffix=".ipynb", delete=False) as f:
            f.write(invalid_notebook)
            temp_path = f.name

        try:
            import sys
            from unittest.mock import patch

            test_argv = ["check-databricks-actions", temp_path]

            with patch("sys.argv", test_argv):
                result = main()
                assert result == 0  # Should succeed (no files processed due to error)

        finally:
            os.unlink(temp_path)

    def test_empty_files_handling(self):
        """Test handling of empty files."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("")  # Empty file
            temp_path = f.name

        try:
            import sys
            from unittest.mock import patch

            test_argv = ["check-databricks-actions", temp_path]

            with patch("sys.argv", test_argv):
                result = main()
                assert result == 0  # Should succeed (no issues in empty file)

        finally:
            os.unlink(temp_path)


class TestPatternMatchingIntegration:
    """Test pattern matching integration scenarios."""

    def test_complex_code_patterns(self):
        """Test complex real-world code patterns."""
        python_code = """
def complex_function():
    # This should be caught
    display(df)

    # This should be caught
    df.show()

    # This should be caught
    df.collect()

    # This should be caught
    df.count()

    # This should be caught
    df.toPandas()

    # This should be caught
    dbutils.notebook.exit()

    # These should NOT be caught (assignments)
    result = df.collect()
    pandas_df = df.toPandas()

    # These should NOT be caught (in strings)
    print("display(df) is not allowed")
    query = "SELECT * FROM table"

    # These should NOT be caught (in comments)
    # display(df)  # This is commented out

    # These should NOT be caught (different patterns)
    df.select("*").show()  # This will NOT be caught (chained method call)

    return result
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(python_code)
            temp_path = f.name

        try:
            patterns = build_patterns_list()
            issues = process_single_file(temp_path, patterns)

            # Should find 6 issues
            assert len(issues) == 6

            issue_descriptions = [issue[1] for issue in issues]
            assert "display() function call" in issue_descriptions
            assert ".show() method call" in issue_descriptions
            assert ".collect() call without assignment" in issue_descriptions
            assert ".count() call without assignment" in issue_descriptions
            assert ".toPandas() without assignment" in issue_descriptions
            assert "dbutils.notebook.exit() call" in issue_descriptions

            # Check that .show() appears once (standalone only, not in chain)
            show_count = sum(
                1 for desc in issue_descriptions if ".show() method call" in desc
            )
            assert show_count == 1

        finally:
            os.unlink(temp_path)

    def test_edge_case_patterns(self):
        """Test edge cases in pattern matching."""
        python_code = """
def edge_cases():
    # Whitespace variations
    display( df )
    display(df)
    display (df)

    # Method call variations
    df.show( )
    df.show()
    df . show ()  # This will NOT be caught (space before dot)

    # These should NOT match
    my_display(df)
    display_result = df.collect()
    show_method = df.show

    return None
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(python_code)
            temp_path = f.name

        try:
            patterns = build_patterns_list()
            issues = process_single_file(temp_path, patterns)

            # Should find 5 issues (3 display + 2 show)
            assert len(issues) == 5

            issue_descriptions = [issue[1] for issue in issues]
            display_count = sum(
                1 for desc in issue_descriptions if "display() function call" in desc
            )
            show_count = sum(
                1 for desc in issue_descriptions if ".show() method call" in desc
            )

            assert display_count == 3
            assert show_count == 2

        finally:
            os.unlink(temp_path)
