import sys


if __name__ == "__main__":
    import os

    script_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, script_dir)

    from cli import main

    sys.exit(main())
else:
    # When imported as a module, use relative imports
    from .cli import main
