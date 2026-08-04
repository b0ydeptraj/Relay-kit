#!/usr/bin/env python3
"""Forwarding shim for relay_kit_v3.scripts.sync_to_projects."""
import sys
from relay_kit_v3.scripts import sync_to_projects

if __name__ == "__main__":
    if hasattr(sync_to_projects, "main"):
        sys.exit(sync_to_projects.main())
