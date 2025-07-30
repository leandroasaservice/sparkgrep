from typing import List, Tuple


# Patterns to detect useless Spark actions
USELESS_PATTERNS = [
    # display() function calls.
    (r"\s*display\s*\(", "display() function or method call"),
    # .show() method calls (debugging leftover)
    (r"^\s*\w+\.show\s*\(", ".show() method call"),
    # .collect() without assignment (often inefficient debugging)
    (r"^\s*\w+\.collect\s*\(\s*\)\s*$", ".collect() call without assignment"),
    # .count() without assignment (often inefficient debugging)
    (r"^\s*\w+\.count\s*\(\s*\)\s*$", ".count() call without assignment"),
    # .toPandas() without assignment (often debugging leftover)
    (r"^\s*\w+\.toPandas\s*\(\s*\)\s*$", ".toPandas() without assignment"),
    # dbutils.notebook.exit() without parameters (debugging leftover)
    (r"dbutils\.notebook\.exit\s*\(\s*\)", "dbutils.notebook.exit() call"),
]


def build_patterns_list(
    disable_default_patterns: bool = False, additional_patterns: List[str] = None
) -> List[Tuple[str, str]]:
    """Build the list of patterns to check based on configuration.

    Args:
        disable_default_patterns: If True, don't include default patterns
        additional_patterns: List of additional patterns in 'pattern:description' format

    Returns:
        List of (pattern, description) tuples
    """
    patterns = []

    # Add default patterns unless disabled
    if not disable_default_patterns:
        patterns.extend(USELESS_PATTERNS)

    # Add additional patterns
    if additional_patterns:
        for pattern_desc in additional_patterns:
            if ":" in pattern_desc:
                pattern, description = pattern_desc.split(":", 1)
                patterns.append((pattern, description))
            else:
                # TODO replace with log warning.
                print(
                    f"""
                    Warning: Invalid pattern format '{pattern_desc}'.
                    Use 'pattern:description'
                    """
                )

    return patterns
