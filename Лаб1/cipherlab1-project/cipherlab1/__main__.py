import sys

from .cli import main

if __name__ == "__main__":
    for stream in (sys.stdout, sys.stderr):
        try:  # кирилиця в консолі Windows
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass
    sys.exit(main())
