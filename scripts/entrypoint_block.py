#!/usr/bin/env python3
"""Forwarding shim for relay_kit_v3.scripts.entrypoint_block."""
import sys
from relay_kit_v3.scripts import entrypoint_block

if __name__ == "__main__":
    if hasattr(entrypoint_block, "main"):
        sys.exit(entrypoint_block.main())
