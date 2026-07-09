import argparse
import sys
import json
from pathlib import Path


def run_commercial(args: argparse.Namespace) -> int:
    if args.action != "dossier":
        return 2
    report = build_commercial_dossier(
        args.project_path,
        channel=args.channel,
        ci_url=args.ci_url,
        release_url=args.release_url,
        package_url=args.package_url,
        sla_url=args.sla_url,
        support_url=args.support_url,
        legal_owner=args.legal_owner,
        support_owner=args.support_owner,
        readiness_profile=args.readiness_profile,
        skip_readiness_tests=args.skip_readiness_tests,
        publication_trail_file=args.publication_trail_file,
        support_request_file=args.support_request_file,
        support_bundle_file=args.support_bundle_file,
    )
    output_path = write_commercial_dossier(args.project_path, report, output_file=args.output_file)
    if args.json:
        print(
            json.dumps(
                {
                    "output_file": str(output_path),
                    "dossier": report,
                },
                ensure_ascii=True,
                indent=2,
            )
        )
    else:
        print(render_commercial_dossier(report))
        print(f"Wrote {output_path}")
    if args.strict and report["status"] != "ready":
        return 2
    return 0

