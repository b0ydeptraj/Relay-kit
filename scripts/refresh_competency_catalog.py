#!/usr/bin/env python3
"""Forwarding shim for relay_kit_v3.scripts.refresh_competency_catalog."""
import sys
from relay_kit_v3.scripts import refresh_competency_catalog

if __name__ == "__main__":
    if hasattr(refresh_competency_catalog, "main"):
        sys.exit(refresh_competency_catalog.main())
