#!/usr/bin/env python3
"""Forwarding shim for relay_kit_v3.scripts.migration_guard."""
import sys
from relay_kit_v3.scripts import migration_guard

if __name__ == "__main__":
    if hasattr(migration_guard, "main"):
        sys.exit(migration_guard.main())
