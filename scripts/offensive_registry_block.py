#!/usr/bin/env python3
"""Forwarding shim for relay_kit_v3.scripts.offensive_registry_block."""
import sys
from relay_kit_v3.scripts import offensive_registry_block

if __name__ == "__main__":
    if hasattr(offensive_registry_block, "main"):
        sys.exit(offensive_registry_block.main())
