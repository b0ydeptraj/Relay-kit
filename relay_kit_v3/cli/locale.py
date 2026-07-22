import argparse
import json
import sys
from pathlib import Path
from relay_kit_v3.runtime_locale import inspect_runtime_locale, load_runtime_locale, write_runtime_locale

def run_locale(args: argparse.Namespace) -> int:
    action = getattr(args, "action", None)
    if action == "show":
        return run_locale_show(args)
    if action == "set":
        return run_locale_set(args)
    return 2

def run_locale_show(args: argparse.Namespace) -> int:
    report = inspect_runtime_locale(args.project_path)
    if args.json:
        print(json.dumps(report, ensure_ascii=True, indent=2))
        return 0 if report.get("status") == "pass" else 2
    locale = load_runtime_locale(Path(args.project_path).resolve())
    print("Relay-kit runtime locale")
    print(f"- locale profile: {locale.get('locale_profile', 'en')}")
    print(f"- fallback locale: {locale.get('fallback_locale', 'en')}")
    print(f"- enforce output language: {locale.get('enforce_output_language', True)}")
    if report.get("status") != "pass":
        for finding in report.get("findings", []):
            print(f"  - {finding.get('summary', finding.get('id', 'finding'))}")
        return 2
    return 0

def run_locale_set(args: argparse.Namespace) -> int:
    try:
        policy = write_runtime_locale(
            Path(args.project_path).resolve(),
            locale=args.locale,
            fallback_locale=args.fallback_locale,
            enforce_output_language=args.enforce_output_language,
        )
        report = inspect_runtime_locale(args.project_path)
        report["policy"] = policy
        if getattr(args, "json", False):
            print(json.dumps(policy, ensure_ascii=True, indent=2))
            return 0 if report.get("status") == "pass" else 1
        print("Updated Relay-kit runtime locale")
        print(f"- locale profile: {args.locale}")
        if args.fallback_locale:
            print(f"- fallback locale: {args.fallback_locale}")
        print(f"- enforce output language: {args.enforce_output_language}")
        return 0
    except Exception as exc:
        print(f"Failed to update locale: {exc}", file=sys.stderr)
        return 1
