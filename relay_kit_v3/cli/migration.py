import argparse
import sys
import json
from pathlib import Path
from relay_kit_v3.cli.utils import _run_script_main


def run_migration(args: argparse.Namespace) -> int:
    if args.action != "guard":
        return 2
    from scripts import naming_guard

    guard_argv = [args.project_path]
    if args.strict:
        guard_argv.append("--strict")
    if args.json:
        guard_argv.append("--json")
    return _run_script_main(naming_guard, "naming_guard.py", guard_argv)

