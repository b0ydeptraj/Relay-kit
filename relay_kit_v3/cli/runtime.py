import argparse
from relay_kit_v3.cli.utils import _run_script_main

def run_runtime_doctor(args: argparse.Namespace) -> int:
    from scripts import runtime_doctor

    doctor_argv = [args.project_path, "--state-mode", args.state_mode, "--adapters", *args.adapters]
    if getattr(args, "strict", False):
        doctor_argv.append("--strict")
    return _run_script_main(runtime_doctor, "runtime_doctor.py", doctor_argv)
