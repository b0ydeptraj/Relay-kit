import argparse
import sys
import json
from pathlib import Path
from relay_kit_v3.cli.utils import _run_script_main


def run_accessibility(args: argparse.Namespace) -> int:
    if args.action != "review":
        return 2
    from scripts import accessibility_review

    review_argv = [args.project_path]
    for option_name in ("surface", "report_file", "output_file"):
        value = getattr(args, option_name)
        if value:
            review_argv.extend([f"--{option_name.replace('_', '-')}", value])
    if args.strict:
        review_argv.append("--strict")
    if args.json:
        review_argv.append("--json")
    return _run_script_main(accessibility_review, "accessibility_review.py", review_argv)

