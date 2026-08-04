#!/usr/bin/env python3
"""Forwarding shim for relay_kit_v3.scripts.package_smoke."""
import sys
from relay_kit_v3.scripts import package_smoke

if __name__ == "__main__":
    if hasattr(package_smoke, "main"):
        sys.exit(package_smoke.main())
