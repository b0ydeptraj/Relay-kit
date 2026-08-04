#!/usr/bin/env python3
"""Forwarding shim for relay_kit_v3.scripts.generate_modules."""
import sys
from relay_kit_v3.scripts import generate_modules

if __name__ == "__main__":
    if hasattr(generate_modules, "main"):
        sys.exit(generate_modules.main())
