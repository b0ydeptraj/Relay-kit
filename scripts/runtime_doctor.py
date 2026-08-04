#!/usr/bin/env python3
"""Forwarding shim for relay_kit_v3.scripts.runtime_doctor."""
import sys
from relay_kit_v3.scripts import runtime_doctor

if __name__ == "__main__":
    if hasattr(runtime_doctor, "main"):
        sys.exit(runtime_doctor.main())
