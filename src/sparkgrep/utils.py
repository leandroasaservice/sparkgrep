import re
from pathlib import Path
from typing import List, Tuple, Union


def read_file_safely(file_path: Path) -> List[str]:
    """Read file content safely, handling encoding errors."""
    try:
        with open(file_path, encoding="utf-8") as f:
            return f.readlines()
    except FileNotFoundError:
        return []
    except UnicodeDecodeError:
        print(f"Warning: Could not read {file_path} due to encoding issues")
        return []


def detect_docstring_start(line: str) -> Union[str, None]:
    """Detect if line starts a docstring and return the marker."""
    stripped_line = line.strip()

    if stripped_line.startswith('"""'):
        return '"""' if stripped_line.count('"""') == 1 else None
    if stripped_line.startswith("'''"):
        return "'''" if stripped_line.count("'''") == 1 else None

    return None


def is_docstring_line(
    line: str, in_docstring: bool, docstring_marker: str
) -> Tuple[bool, str]:
    """Check if line is part of a docstring and update docstring state."""
    if not in_docstring:
        marker = detect_docstring_start(line)
        if marker:
            return True, marker
    elif docstring_marker in line.strip():
        return False, None

    return in_docstring, docstring_marker


def should_skip_line(line: str, in_docstring: bool) -> bool:
    """Check if line should be skipped (comments, empty lines, docstrings)."""
    stripped_line = line.strip()
    return in_docstring or stripped_line.startswith("#") or not stripped_line


def should_skip_notebook_line(line: str) -> bool:
    """Check if a notebook line should be skipped (comments, magic commands)."""
    stripped_line = line.strip()
    return stripped_line.startswith("#") or stripped_line.startswith("%")


def check_line_for_patterns(
    line: str, patterns: List[Tuple[str, str]]
) -> List[Tuple[str, str]]:
    """Check a single line against all patterns and return matches."""
    matches = []
    for pattern, description in patterns:
        if re.search(pattern, line, re.IGNORECASE):
            matches.append((description, line.strip()))
    return matches


def report_results(file_path: str, issues: List[Tuple[str, str, str]]) -> None:
    """Report issues found in a file."""
    if issues:
        print(f"\n{file_path}:")
        for line_info, description, line_content in issues:
            print(f"  Line {line_info}: {description}")
            print(f"    > {line_content}")
