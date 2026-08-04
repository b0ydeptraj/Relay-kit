#!/usr/bin/env python3
"""Forwarding shim for relay_kit_v3.scripts.validate_runtime."""
import sys
from relay_kit_v3.scripts import validate_runtime

if __name__ == "__main__":
    if hasattr(validate_runtime, "main"):
        sys.exit(validate_runtime.main())
