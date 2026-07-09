import argparse
from relay_kit_v3.cli.utils import _run_script_main

def run_skill_gauntlet(args: argparse.Namespace) -> int:
    from scripts import skill_gauntlet

    gauntlet_argv = [args.project_path]
    if getattr(args, "json", False):
        gauntlet_argv.append("--json")
    if getattr(args, "strict", False):
        gauntlet_argv.append("--strict")
    if getattr(args, "semantic", False):
        gauntlet_argv.append("--semantic")
    if getattr(args, "scenario_fixtures", None):
        gauntlet_argv.extend(["--scenario-fixtures", args.scenario_fixtures])
    return _run_script_main(skill_gauntlet, "skill_gauntlet.py", gauntlet_argv)
