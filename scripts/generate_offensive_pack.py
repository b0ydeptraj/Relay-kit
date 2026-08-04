#!/usr/bin/env python3
"""Forwarding shim for relay_kit_v3.scripts.generate_offensive_pack."""
import sys
from relay_kit_v3.scripts import generate_offensive_pack

if __name__ == "__main__":
    if hasattr(generate_offensive_pack, "main"):
        sys.exit(generate_offensive_pack.main())
