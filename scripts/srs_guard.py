#!/usr/bin/env python3
"""Forwarding shim for relay_kit_v3.scripts.srs_guard."""
import sys
from relay_kit_v3.scripts import srs_guard

if __name__ == "__main__":
    if hasattr(srs_guard, "main"):
        sys.exit(srs_guard.main())
