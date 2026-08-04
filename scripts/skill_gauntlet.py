#!/usr/bin/env python3
"""Forwarding shim for relay_kit_v3.scripts.skill_gauntlet."""
import sys
from relay_kit_v3.scripts import skill_gauntlet

if __name__ == "__main__":
    if hasattr(skill_gauntlet, "main"):
        sys.exit(skill_gauntlet.main())
