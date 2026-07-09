import argparse
import sys
from relay_kit_v3.shell_compaction import run_compacted_command, ShellCompactionError

def run_shell_compact(args: argparse.Namespace) -> int:
    command = list(getattr(args, "command", []))
    if command and command[0] == "--":
        command = command[1:]
    if not command:
        print("Missing command. Use: relay-kit shell compact <project> -- <command...>", file=sys.stderr)
        return 2
    try:
        report = run_compacted_command(
            command,
            project_root=args.project_path,
            cwd=args.cwd or args.project_path,
            strict=getattr(args, "strict", False),
            timeout=getattr(args, "timeout", None),
        )
    except ShellCompactionError as exc:
        print(f"Shell compaction failed: {exc}", file=sys.stderr)
        return 2
    except FileNotFoundError as exc:
        print(f"Command not found: {exc}", file=sys.stderr)
        return 2
    return report.returncode
