#!/usr/bin/env python3
"""Forwarding shim for relay_kit_v3.scripts.update_tests."""
import sys
from relay_kit_v3.scripts import update_tests

if __name__ == "__main__":
    if hasattr(update_tests, "main"):
        sys.exit(update_tests.main())
