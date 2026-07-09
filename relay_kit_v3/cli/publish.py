import argparse
import sys
import json
from pathlib import Path


def run_publish(args: argparse.Namespace) -> int:
    if args.action == "plan":
        report = build_publication_plan(
            args.project_path,
            channel=args.channel,
            target_version=args.target_version,
            dist_dir=args.dist_dir,
            ci_url=args.ci_url,
            release_url=args.release_url,
            package_url=args.package_url,
            allow_dev=args.allow_dev,
        )
        if args.output_file:
            write_publication_plan(args.project_path, report, output_file=args.output_file)
        if args.json:
            print(json.dumps(report, ensure_ascii=True, indent=2))
        else:
            print(render_publication_plan(report))
        if args.strict and report["status"] != "ready":
            return 2
        return 0
    if args.action == "evidence":
        report = build_publication_evidence(
            args.project_path,
            channel=args.channel,
            dist_dir=args.dist_dir,
            ci_url=args.ci_url,
            release_url=args.release_url,
            package_url=args.package_url,
            twine_check_file=args.twine_check_file,
            upload_log_file=args.upload_log_file,
            publication_plan_file=args.publication_plan_file,
            allow_dev=args.allow_dev,
        )
        output_path = write_publication_evidence(args.project_path, report, output_file=args.output_file)
        if args.json:
            print(
                json.dumps(
                    {
                        "output_file": str(output_path),
                        "evidence": report,
                    },
                    ensure_ascii=True,
                    indent=2,
                )
            )
        else:
            print(render_publication_evidence(report))
            print(f"Wrote {output_path}")
        if args.strict and report["status"] != "published":
            return 2
        return 0
    if args.action == "trail":
        report = build_publication_trail(
            args.project_path,
            channel=args.channel,
            target_version=args.target_version,
            dist_dir=args.dist_dir,
            evidence_dir=args.evidence_dir,
            ci_url=args.ci_url,
            release_url=args.release_url,
            package_url=args.package_url,
            shell=args.shell,
            allow_dev=args.allow_dev,
        )
        output_path = write_publication_trail(args.project_path, report, output_file=args.output_file)
        markdown_path = write_publication_trail_markdown(args.project_path, report, output_file=args.markdown_file)
        if args.json:
            print(
                json.dumps(
                    {
                        "output_file": str(output_path),
                        "markdown_file": str(markdown_path),
                        "trail": report,
                    },
                    ensure_ascii=True,
                    indent=2,
                )
            )
        else:
            print(render_publication_trail(report))
            print(f"Wrote {output_path}")
            print(f"Wrote {markdown_path}")
        if args.strict and report["status"] != "ready":
            return 2
        return 0
    if args.action == "index-check":
        report = build_package_index_check(
            args.project_path,
            channel=args.channel,
            target_version=args.target_version,
            package_url=args.package_url,
            timeout_seconds=args.timeout,
        )
        output_path = write_package_index_check(args.project_path, report, output_file=args.output_file)
        if args.json:
            print(
                json.dumps(
                    {
                        "output_file": str(output_path),
                        "index_check": report,
                    },
                    ensure_ascii=True,
                    indent=2,
                )
            )
        else:
            print(render_package_index_check(report))
            print(f"Wrote {output_path}")
        if args.strict and report["status"] != "published":
            return 2
        return 0
    if args.action == "status":
        report = build_publication_trail_status(args.project_path, trail_file=args.trail_file)
        if args.json:
            print(json.dumps(report, ensure_ascii=True, indent=2))
        else:
            print(render_publication_trail_status(report))
        if args.strict and report["status"] != "complete":
            return 2
        return 0
    return 2

