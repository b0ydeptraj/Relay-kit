#!/usr/bin/env python3
"""Forwarding shim for relay_kit_v3.scripts.gen_entrypoint_block."""
import sys
from relay_kit_v3.scripts import gen_entrypoint_block

if __name__ == "__main__":
    if hasattr(gen_entrypoint_block, "main"):
        sys.exit(gen_entrypoint_block.main())
