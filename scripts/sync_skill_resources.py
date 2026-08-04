#!/usr/bin/env python3
"""Forwarding shim for relay_kit_v3.scripts.sync_skill_resources."""
import sys
from relay_kit_v3.scripts import sync_skill_resources

if __name__ == "__main__":
    if hasattr(sync_skill_resources, "main"):
        sys.exit(sync_skill_resources.main())
