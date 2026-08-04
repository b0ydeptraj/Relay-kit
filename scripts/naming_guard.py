#!/usr/bin/env python3
"""Forwarding shim for relay_kit_v3.scripts.naming_guard."""
import sys
from relay_kit_v3.scripts import naming_guard

if __name__ == "__main__":
    if hasattr(naming_guard, "main"):
        sys.exit(naming_guard.main())
