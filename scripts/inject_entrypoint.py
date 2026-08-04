#!/usr/bin/env python3
"""Forwarding shim for relay_kit_v3.scripts.inject_entrypoint."""
import sys
from relay_kit_v3.scripts import inject_entrypoint

if __name__ == "__main__":
    if hasattr(inject_entrypoint, "main"):
        sys.exit(inject_entrypoint.main())
