from pathlib import Path
from typing import List, Tuple


try:
    from .utils import (
        check_line_for_patterns,
        is_docstring_line,
        read_file_safely,
        should_skip_line,
        should_skip_notebook_line,
    )
except ImportError:
    from utils import (
        check_line_for_patterns,
        is_docstring_line,
        read_file_safely,
        should_skip_line,
        should_skip_notebook_line,
    )


def check_python_file(
    file_path: Path, patterns: List[Tuple[str, str]]
) -> List[Tuple[int, str, str]]:
    """Check a Python file for useless Spark actions."""
    issues = []
    lines = read_file_safely(file_path)

    if not lines:
        return issues

    in_docstring = False
    docstring_marker = None

    for line_num, line in enumerate(lines, 1):
        # Handle docstring detection
        in_docstring, docstring_marker = is_docstring_line(
            line, in_docstring, docstring_marker
        )

        # Skip lines that shouldn't be processed
        if should_skip_line(line, in_docstring):
            continue

        # Check line for pattern matches
        matches = check_line_for_patterns(line, patterns)
        for description, line_content in matches:
            issues.append((line_num, description, line_content))

    return issues


def _read_notebook_safely(file_path: Path):
    """Read notebook file safely, handling import and parsing errors."""
    try:
        import nbformat
    except ImportError:
        print("Warning: nbformat not installed, skipping notebook files")
        return None

    try:
        with open(file_path, encoding="utf-8") as f:
            return nbformat.read(f, as_version=4)
    except Exception as e:
        print(f"Warning: Could not read notebook {file_path}: {e}")
        return None


def _process_notebook_cell(
    cell, cell_num: int, patterns: List[Tuple[str, str]]
) -> List[Tuple[str, str, str]]:
    """Process a single notebook cell and return issues found."""
    issues = []

    if cell.cell_type != "code":
        return issues

    lines = cell.source.split("\n")
    for line_num, line in enumerate(lines, 1):
        if should_skip_notebook_line(line):
            continue

        matches = check_line_for_patterns(line, patterns)
        for description, line_content in matches:
            location = f"Cell {cell_num + 1}, Line {line_num}"
            issues.append((location, description, line_content))

    return issues


def check_notebook_file(
    file_path: Path, patterns: List[Tuple[str, str]]
) -> List[Tuple[str, str, str]]:
    """Check a Jupyter notebook file for useless Spark actions."""
    issues = []

    notebook = _read_notebook_safely(file_path)
    if notebook is None:
        return issues

    for cell_num, cell in enumerate(notebook.cells):
        cell_issues = _process_notebook_cell(cell, cell_num, patterns)
        issues.extend(cell_issues)

    return issues


def process_single_file(
    file_path: str, patterns: List[Tuple[str, str]]
) -> List[Tuple[str, str, str]]:
    """Process a single file and return issues found."""
    file_path = Path(file_path)

    if not file_path.exists():
        return []

    if file_path.suffix == ".py":
        return check_python_file(file_path, patterns)
    if file_path.suffix == ".ipynb":
        return check_notebook_file(file_path, patterns)
    return []
