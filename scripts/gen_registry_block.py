#!/usr/bin/env python3
"""Forwarding shim for relay_kit_v3.scripts.gen_registry_block."""
import sys
from relay_kit_v3.scripts import gen_registry_block

if __name__ == "__main__":
    if hasattr(gen_registry_block, "main"):
        sys.exit(gen_registry_block.main())
