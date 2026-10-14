#!/usr/bin/env python3
"""
Launcher for RelayKit Studio Desktop GUI App.
Usage:
    python scripts/run_app.py
"""

import sys
from pathlib import Path

# Add project root to sys.path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from tools.gui_app.app import launch_app


if __name__ == "__main__":
    launch_app()
