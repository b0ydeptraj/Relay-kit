#!/usr/bin/env python3
"""Forwarding shim for relay_kit_v3.scripts.eval_workflows."""
import sys
from relay_kit_v3.scripts import eval_workflows

if __name__ == "__main__":
    if hasattr(eval_workflows, "main"):
        sys.exit(eval_workflows.main())
