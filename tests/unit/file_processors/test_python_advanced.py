import pytest
import tempfile
import os
from pathlib import Path

from sparkgrep.file_processors import check_python_file


def test_check_python_file_nested_functions():
    """Test with nested functions and classes."""
    python_code = """
class DataProcessor:
    def __init__(self):
        self.data = None

    def process(self):
        display(self.data)  # Should be found

        def inner_function():
            display(nested_data)  # Should be found
            return True

        return inner_function()

    def analyze(self):
        self.data.show()  # Should be found
"""

    patterns = [
        (r"display\(", "display function"),
        (r"\.show\(", "show method")
    ]

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(python_code)
        temp_path = f.name

    try:
        issues = check_python_file(Path(temp_path), patterns)

        assert len(issues) == 3
        descriptions = [issue[1] for issue in issues]
        assert descriptions.count("display function") == 2
        assert descriptions.count("show method") == 1

    finally:
        os.unlink(temp_path)


def test_check_python_file_decorators():
    """Test that decorators don't interfere with pattern detection."""
    python_code = """
@decorator
def decorated_function():
    display(df)  # Should be found

@property
def get_data(self):
    return self.data.show()  # Should be found

@staticmethod
def static_method():
    # Comment about display()
    display(result)  # Should be found
"""

    patterns = [
        (r"display\(", "display function"),
        (r"\.show\(", "show method")
    ]

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(python_code)
        temp_path = f.name

    try:
        issues = check_python_file(Path(temp_path), patterns)

        assert len(issues) == 3
        descriptions = [issue[1] for issue in issues]
        assert descriptions.count("display function") == 2
        assert descriptions.count("show method") == 1

    finally:
        os.unlink(temp_path)


def test_check_python_file_import_statements():
    """Test that import statements are handled correctly."""
    python_code = """
import display_module
from package import display_function
from utils import show_data

def main():
    # These should be found
    display(df1)
    show_data.display(df2)  # Should be found
"""

    patterns = [(r"display\(", "display function")]

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(python_code)
        temp_path = f.name

    try:
        issues = check_python_file(Path(temp_path), patterns)

        # Should find the function calls but not the import statements
        assert len(issues) == 2

        # All found issues should be function calls, not imports
        for issue in issues:
            assert "import" not in issue[2].lower()
            assert "from" not in issue[2].lower()

    finally:
        os.unlink(temp_path)


def test_check_python_file_large_file():
    """Test processing a large Python file."""
    # Create a large file with patterns scattered throughout
    lines = []
    for i in range(1000):
        if i % 100 == 0:
            lines.append(f"display(df_{i})  # Line {i}")
        else:
            lines.append(f"# Comment line {i}")

    python_code = "\n".join(lines)
    patterns = [(r"display\(", "display function")]

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(python_code)
        temp_path = f.name

    try:
        issues = check_python_file(Path(temp_path), patterns)

        # Should find 10 display calls (every 100th line starting from 0)
        assert len(issues) == 10

        # Check that line numbers are correct
        line_numbers = [issue[0] for issue in issues]
        expected_lines = [i + 1 for i in range(0, 1000, 100)]  # +1 for 1-based indexing
        assert line_numbers == expected_lines

    finally:
        os.unlink(temp_path)


def test_check_python_file_deeply_nested_structures():
    """Test with deeply nested class and function structures."""
    python_code = """
class OuterClass:
    class InnerClass:
        def method1(self):
            display(self.data)  # Should be found

            class VeryInnerClass:
                def inner_method(self):
                    def nested_function():
                        display(nested_data)  # Should be found
                        return True
                    return nested_function()
            return VeryInnerClass()

        def method2(self):
            self.data.show()  # Should be found
"""

    patterns = [
        (r"display\(", "display function"),
        (r"\.show\(", "show method")
    ]

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(python_code)
        temp_path = f.name

    try:
        issues = check_python_file(Path(temp_path), patterns)

        assert len(issues) == 3
        descriptions = [issue[1] for issue in issues]
        assert descriptions.count("display function") == 2
        assert descriptions.count("show method") == 1

    finally:
        os.unlink(temp_path)


def test_check_python_file_async_functions():
    """Test with async functions and await statements."""
    python_code = """
import asyncio

async def async_process_data():
    data = await fetch_data()
    display(data)  # Should be found

    async def inner_async():
        result = await process_async()
        display(result)  # Should be found
        return result

    return await inner_async()

class AsyncProcessor:
    async def process(self):
        await self.prepare()
        self.data.show()  # Should be found
"""

    patterns = [
        (r"display\(", "display function"),
        (r"\.show\(", "show method")
    ]

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(python_code)
        temp_path = f.name

    try:
        issues = check_python_file(Path(temp_path), patterns)

        assert len(issues) == 3
        descriptions = [issue[1] for issue in issues]
        assert descriptions.count("display function") == 2
        assert descriptions.count("show method") == 1

    finally:
        os.unlink(temp_path)


def test_check_python_file_generators_and_comprehensions():
    """Test with generators, list comprehensions, and lambda functions."""
    python_code = """
def generator_function():
    for i in range(10):
        if i % 2 == 0:
            display(i)  # Should be found
            yield i

def comprehension_test():
    # List comprehension - pattern inside may or may not be detected
    results = [display(x) for x in data if x > 0]

    # Generator expression
    gen = (display(y) for y in items)

    # Lambda function
    process = lambda x: display(x)  # Should be found

    # Regular function call
    display(final_result)  # Should be found
"""

    patterns = [(r"display\(", "display function")]

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(python_code)
        temp_path = f.name

    try:
        issues = check_python_file(Path(temp_path), patterns)

        # Should find at least the clear function calls
        assert len(issues) >= 2

        # Check that we find the obvious ones
        code_lines = [issue[2] for issue in issues]
        assert any("final_result" in line for line in code_lines)

    finally:
        os.unlink(temp_path)


def test_check_python_file_exception_handling():
    """Test with try/except blocks and exception handling."""
    python_code = """
def handle_exceptions():
    try:
        data = load_risky_data()
        display(data)  # Should be found
    except ValueError as e:
        print(f"Error: {e}")
        display(error_data)  # Should be found
    except Exception:
        emergency_data.show()  # Should be found
    finally:
        cleanup()
        display(cleanup_info)  # Should be found
"""

    patterns = [
        (r"display\(", "display function"),
        (r"\.show\(", "show method")
    ]

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(python_code)
        temp_path = f.name

    try:
        issues = check_python_file(Path(temp_path), patterns)

        assert len(issues) == 4
        descriptions = [issue[1] for issue in issues]
        assert descriptions.count("display function") == 3
        assert descriptions.count("show method") == 1

    finally:
        os.unlink(temp_path)


def test_check_python_file_context_managers():
    """Test with context managers and with statements."""
    python_code = """
def context_manager_test():
    with open('file.txt') as f:
        data = f.read()
        display(data)  # Should be found

    with database_connection() as db:
        results = db.query("SELECT * FROM table")
        display(results)  # Should be found

    # Nested context managers
    with session_scope() as session:
        with transaction() as tx:
            entity = session.get(Entity, 1)
            display(entity)  # Should be found
"""

    patterns = [(r"display\(", "display function")]

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(python_code)
        temp_path = f.name

    try:
        issues = check_python_file(Path(temp_path), patterns)

        assert len(issues) == 3

        # All should be display functions
        descriptions = [issue[1] for issue in issues]
        assert all(desc == "display function" for desc in descriptions)

    finally:
        os.unlink(temp_path)


def test_check_python_file_multiple_inheritance():
    """Test with multiple inheritance and complex class hierarchies."""
    python_code = """
class BaseProcessor:
    def base_method(self):
        display(self.base_data)  # Should be found

class Mixin:
    def mixin_method(self):
        self.mixed_data.show()  # Should be found

class ComplexProcessor(BaseProcessor, Mixin):
    def __init__(self):
        super().__init__()
        self.data = None

    def complex_method(self):
        display(self.complex_data)  # Should be found
        super().base_method()
        self.mixin_method()
"""

    patterns = [
        (r"display\(", "display function"),
        (r"\.show\(", "show method")
    ]

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(python_code)
        temp_path = f.name

    try:
        issues = check_python_file(Path(temp_path), patterns)

        assert len(issues) == 3
        descriptions = [issue[1] for issue in issues]
        assert descriptions.count("display function") == 2
        assert descriptions.count("show method") == 1

    finally:
        os.unlink(temp_path)
