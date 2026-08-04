#!/usr/bin/env python3
"""Forwarding shim for relay_kit_v3.scripts.check_v5."""
import sys
from relay_kit_v3.scripts import check_v5

if __name__ == "__main__":
    if hasattr(check_v5, "main"):
        sys.exit(check_v5.main())
