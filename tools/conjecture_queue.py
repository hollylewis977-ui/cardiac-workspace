#!/usr/bin/env python3
"""Compatibility entrypoint; the queue now performs cardiac research."""
import sys
from research_queue import main

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    raise SystemExit(main())
