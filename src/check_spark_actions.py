#!/usr/bin/env python3
"""Pre-commit hook to detect useless Spark actions.

This main entry point should be removed before committing.
Uses the modular structure for processing.
"""

import sys


# Handle both direct execution and module import
if __name__ == "__main__":
    # When running as a script, we need to handle imports differently
    import os

    script_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, script_dir)

    from cli import main

    sys.exit(main())
else:
    # When imported as a module, use relative imports
    from .cli import main
