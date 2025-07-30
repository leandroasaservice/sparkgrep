import argparse
import sys


try:
    from .file_processors import process_single_file
    from .patterns import build_patterns_list
    from .utils import report_results
except ImportError:
    from file_processors import process_single_file
    from patterns import build_patterns_list
    from utils import report_results


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Check for useless Spark actions")
    parser.add_argument("files", nargs="*", help="Files to check")
    parser.add_argument("--config", help="Configuration file (not implemented yet)")
    parser.add_argument(
        "--additional-patterns",
        nargs="*",
        help='Additional regex patterns to check (format: "pattern:description")',
    )
    parser.add_argument(
        "--disable-default-patterns",
        action="store_true",
        help="Disable default patterns and only use additional ones",
    )
    return parser.parse_args()


def main():
    """Main entry point for the CLI."""
    args = parse_arguments()

    if not args.files:
        print("No files provided")
        return 0

    patterns = build_patterns_list(
        disable_default_patterns=args.disable_default_patterns,
        additional_patterns=args.additional_patterns,
    )

    if not patterns:
        print("No patterns to check")
        return 0

    total_issues = 0

    for file_path in args.files:
        issues = process_single_file(file_path, patterns)
        report_results(file_path, issues)
        total_issues += len(issues)

    if total_issues > 0:
        print(f"\nFound {total_issues} useless Spark action(s)")
        print("Please remove these before committing.")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
