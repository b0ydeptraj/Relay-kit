#!/usr/bin/env python3
"""Forwarding shim for relay_kit_v3.scripts.refresh_skill_battle_resources."""
import sys
from relay_kit_v3.scripts import refresh_skill_battle_resources

if __name__ == "__main__":
    if hasattr(refresh_skill_battle_resources, "main"):
        sys.exit(refresh_skill_battle_resources.main())
