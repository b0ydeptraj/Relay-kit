import argparse
import sys
import json
from pathlib import Path


def run_manifest(args: argparse.Namespace) -> int:
    if args.action == "write":
        output_path = write_manifest(args.project_path, args.output_file)
        print(f"Wrote {output_path}")
        return 0
    if args.action == "stamp":
        try:
            output_path = write_trust_stamp(
                args.project_path,
                manifest_file=args.manifest_file,
                trust_file=args.trust_file,
                issuer=args.issuer,
                channel=args.channel,
            )
        except ValueError as exc:
            print(f"Manifest trust stamp failed: {exc}")
            return 2
        print(f"Wrote {output_path}")
        return 0
    if args.action == "verify":
        manifest_path = Path(args.manifest_file) if args.manifest_file else Path(args.project_path) / ".relay-kit" / "manifest" / "bundles.json"
        result = (
            verify_trusted_manifest_file(manifest_path, args.trust_file)
            if args.trusted
            else verify_manifest_file(manifest_path)
        )
        if result.ok:
            print("Trust verification passed." if args.trusted else "Manifest verification passed.")
            return 0
        print("Trust verification failed." if args.trusted else "Manifest verification failed.")
        for finding in result.findings:
            print(f"- {finding}")
        return 2
    return 2

