#!/usr/bin/env python3
"""Forwarding shim for relay_kit_v3.scripts.policy_guard."""
import sys
from relay_kit_v3.scripts import policy_guard

if __name__ == "__main__":
    if hasattr(policy_guard, "main"):
        sys.exit(policy_guard.main())
