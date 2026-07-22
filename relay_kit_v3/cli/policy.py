import argparse
import sys
import json
from pathlib import Path

from relay_kit_v3.policy_packs import POLICY_PACKS

def run_policy(args: argparse.Namespace) -> int:
    if args.action == "list":
        print("Relay-kit policy packs")
        for name, pack in sorted(POLICY_PACKS.items()):
            print(f"- {name}: {pack.description}")
        return 0
    if args.action == "check":
        from scripts import policy_guard

        policy_argv = [args.project_path, "--pack", args.pack]
        if args.strict:
            policy_argv.append("--strict")
        if args.json:
            policy_argv.append("--json")
        return policy_guard.main(policy_argv)
    return 2

