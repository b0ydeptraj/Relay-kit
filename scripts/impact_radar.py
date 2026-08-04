#!/usr/bin/env python3
"""Forwarding shim for relay_kit_v3.scripts.impact_radar."""
import sys
from relay_kit_v3.scripts import impact_radar

if __name__ == "__main__":
    if hasattr(impact_radar, "main"):
        sys.exit(impact_radar.main())
