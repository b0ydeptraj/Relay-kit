import argparse
from relay_kit_v3.cli.utils import _run_script_main

def run_impact_radar(args: argparse.Namespace) -> int:
    from relay_kit_v3.scripts import impact_radar

    radar_argv = [args.project_path, "--head", args.head]
    if getattr(args, "base", None):
        radar_argv.extend(["--base", args.base])
    if getattr(args, "json", False):
        radar_argv.append("--json")
    return _run_script_main(impact_radar, "impact_radar.py", radar_argv)

def run_impact(args: argparse.Namespace) -> int:
    action = getattr(args, "action", None)
    if action == "radar":
        return run_impact_radar(args)
    return 1

