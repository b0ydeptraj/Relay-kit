import argparse
import sys
import json
from pathlib import Path
from relay_kit_v3.cli.utils import _run_script_main


def run_continuity(args: argparse.Namespace) -> int:
    from scripts import context_continuity

    continuity_argv = [args.action, args.project_path]
    if getattr(args, "json", False):
        continuity_argv.append("--json")
    for option_name in (
        "objective",
        "lane",
        "blocker",
        "next_step",
        "note",
        "reason",
        "receiver",
        "phase",
        "max_age_minutes",
    ):
        value = getattr(args, option_name, None)
        if value is not None:
            continuity_argv.extend([f"--{option_name.replace('_', '-')}", str(value)])
    for option_name in ("force_checkpoint", "force_rehydrate"):
        if getattr(args, option_name, False):
            continuity_argv.append(f"--{option_name.replace('_', '-')}")
    return _run_script_main(context_continuity, "context_continuity.py", continuity_argv)

