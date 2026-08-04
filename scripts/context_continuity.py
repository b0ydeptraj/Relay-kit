#!/usr/bin/env python3
"""Forwarding shim for relay_kit_v3.scripts.context_continuity."""
import sys
from relay_kit_v3.scripts import context_continuity

if __name__ == "__main__":
    if hasattr(context_continuity, "main"):
        sys.exit(context_continuity.main())
