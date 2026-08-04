#!/usr/bin/env python3
"""Forwarding shim for relay_kit_v3.scripts.cleanup_monolith."""
import sys
from relay_kit_v3.scripts import cleanup_monolith

if __name__ == "__main__":
    if hasattr(cleanup_monolith, "main"):
        sys.exit(cleanup_monolith.main())
