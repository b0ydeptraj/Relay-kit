#!/usr/bin/env python3
"""Forwarding shim for relay_kit_v3.scripts.regen_all_resources."""
import sys
from relay_kit_v3.scripts import regen_all_resources

if __name__ == "__main__":
    if hasattr(regen_all_resources, "main"):
        sys.exit(regen_all_resources.main())
