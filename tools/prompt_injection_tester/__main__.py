#!/usr/bin/env python3
"""Entry point for running as a module: python -m prompt_injection_tester"""

from .cli import main

if __name__ == "__main__":
    raise SystemExit(main())
