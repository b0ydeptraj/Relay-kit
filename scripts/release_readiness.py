#!/usr/bin/env python3
"""Forwarding shim for relay_kit_v3.scripts.release_readiness."""
import sys
from relay_kit_v3.scripts import release_readiness

if __name__ == "__main__":
    if hasattr(release_readiness, "main"):
        sys.exit(release_readiness.main())
