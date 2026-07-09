import argparse
import sys
import json
from pathlib import Path


def run_support(args: argparse.Namespace) -> int:
    if args.action == "bundle":
        output_path = write_support_bundle(
            args.project_path,
            policy_pack=args.policy_pack,
            output_file=args.output_file,
            evidence_limit=args.evidence_limit,
        )
        if args.json:
            payload = {
                "output_file": str(output_path),
                "bundle": build_support_bundle(
                    args.project_path,
                    policy_pack=args.policy_pack,
                    evidence_limit=args.evidence_limit,
                ),
            }
            print(json.dumps(payload, ensure_ascii=True, indent=2))
            return 0
        print(f"Wrote {output_path}")
        return 0
    if args.action == "request":
        report = build_support_request(
            args.project_path,
            severity=args.severity,
            summary=args.summary,
            package_version=args.package_version,
            operating_system=args.operating_system,
            shell=args.shell,
            installed_bundle=args.installed_bundle,
            adapter_target=args.adapter_target,
            policy_pack=args.policy_pack,
            expected_behavior=args.expected_behavior,
            actual_behavior=args.actual_behavior,
            recent_changes=args.recent_changes,
            workaround=args.workaround,
            diagnostic_files=args.diagnostic_file,
        )
        output_path = write_support_request(args.project_path, report, output_file=args.output_file)
        if args.json:
            print(
                json.dumps(
                    {
                        "output_file": str(output_path),
                        "request": report,
                    },
                    ensure_ascii=True,
                    indent=2,
                )
            )
        else:
            print(render_support_request(report))
            print(f"Wrote {output_path}")
        if args.strict and report["status"] != "ready":
            return 2
        return 0
    if args.action == "triage":
        report = build_support_triage(args.project_path, request_file=args.request_file, bundle_file=args.bundle_file)
        if args.json:
            print(json.dumps(report, ensure_ascii=True, indent=2))
        else:
            print(render_support_triage(report))
        if args.strict and report["status"] != "ready":
            return 2
        return 0
    if args.action == "soak":
        report = build_support_soak_report(args.project_path, bundle_file=args.bundle_file)
        if args.json:
            print(json.dumps(report, ensure_ascii=True, indent=2))
        else:
            print(render_support_soak_report(report))
        if args.strict and report["status"] != "pass":
            return 2
        return 0
    return 2

