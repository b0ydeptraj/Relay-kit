#!/usr/bin/env python3
"""Forwarding shim for relay_kit_v3.scripts.accessibility_review."""
import sys
from relay_kit_v3.scripts import accessibility_review

if __name__ == "__main__":
    if hasattr(accessibility_review, "main"):
        sys.exit(accessibility_review.main())
