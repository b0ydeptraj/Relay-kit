#!/usr/bin/env python3
"""Forwarding shim for relay_kit_v3.scripts.memory_search."""
import sys
from relay_kit_v3.scripts import memory_search

if __name__ == "__main__":
    if hasattr(memory_search, "main"):
        sys.exit(memory_search.main())
