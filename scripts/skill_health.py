#!/usr/bin/env python3
"""
skill_health.py - Audit all skills in Relay-kit for structural completeness.
Reports: has SKILL.md, scripts/, evals/, examples/, competencies/, references/

Usage:
    python scripts/skill_health.py
    python scripts/skill_health.py --adapter .agent
    python scripts/skill_health.py --filter bypass
    python scripts/skill_health.py --output health_report.json

Exit code 0 = all skills healthy, 1 = some skills incomplete.
"""

import argparse
import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

REQUIRED_COMPONENTS = {
    "SKILL.md":       {"required": True,  "type": "file",      "weight": 3},
    "scripts":        {"required": False, "type": "directory",  "weight": 2},
    "references":     {"required": False, "type": "directory",  "weight": 1},
    "evals":          {"required": False, "type": "directory",  "weight": 1},
    "examples":       {"required": False, "type": "directory",  "weight": 1},
    "competencies":   {"required": False, "type": "directory",  "weight": 1},
    "agents":         {"required": False, "type": "directory",  "weight": 1},
}

MAX_SCORE = sum(c["weight"] for c in REQUIRED_COMPONENTS.values())


def audit_skill(skill_path: Path) -> dict:
    name = skill_path.name
    result = {"name": name, "path": str(skill_path), "components": {}, "score": 0, "max": MAX_SCORE}

    for comp, meta in REQUIRED_COMPONENTS.items():
        comp_path = skill_path / comp
        exists = comp_path.exists()
        if exists and meta["type"] == "directory":
            file_count = len(list(comp_path.iterdir())) if comp_path.is_dir() else 0
            result["components"][comp] = {"exists": True, "files": file_count}
        else:
            result["components"][comp] = {"exists": exists, "files": 0}

        if exists:
            result["score"] += meta["weight"]
        elif meta["required"]:
            result["missing_required"] = result.get("missing_required", []) + [comp]

    result["completeness_pct"] = round(100 * result["score"] / result["max"])
    result["has_scripts"] = result["components"].get("scripts", {}).get("exists", False)
    result["is_prompt_only"] = not result["has_scripts"]
    return result


def grade(pct: int) -> str:
    if pct >= 90: return "A"
    if pct >= 70: return "B"
    if pct >= 50: return "C"
    if pct >= 30: return "D"
    return "F"


def main():
    p = argparse.ArgumentParser(description="Relay-kit skill health auditor")
    p.add_argument("--adapter", default=".agent", choices=[".agent", ".claude", ".codex"])
    p.add_argument("--filter", help="Filter skill names containing this string")
    p.add_argument("--output", help="Save JSON report to file")
    p.add_argument("--show-all", action="store_true", help="Show all skills (default: only incomplete)")
    p.add_argument("--sort", choices=["name","score","grade"], default="score")
    args = p.parse_args()

    skills_dir = REPO_ROOT / args.adapter / "skills"
    if not skills_dir.exists():
        print(f"[-] Skills directory not found: {skills_dir}"); sys.exit(1)

    skill_dirs = sorted([d for d in skills_dir.iterdir() if d.is_dir()])
    if args.filter:
        skill_dirs = [d for d in skill_dirs if args.filter.lower() in d.name.lower()]

    results = [audit_skill(d) for d in skill_dirs]

    # Sort
    if args.sort == "score":
        results.sort(key=lambda r: r["score"])
    elif args.sort == "grade":
        results.sort(key=lambda r: r["completeness_pct"])
    else:
        results.sort(key=lambda r: r["name"])

    # Statistics
    total = len(results)
    prompt_only = sum(1 for r in results if r["is_prompt_only"])
    with_scripts = sum(1 for r in results if r["has_scripts"])
    avg_score = sum(r["completeness_pct"] for r in results) / total if total else 0
    full_complete = sum(1 for r in results if r["completeness_pct"] == 100)

    print(f"\n{'='*60}")
    print(f"  Relay-kit Skill Health Report ({args.adapter})")
    print(f"{'='*60}")
    print(f"  Total skills   : {total}")
    print(f"  Avg completeness: {avg_score:.1f}%")
    print(f"  With scripts/  : {with_scripts} ({100*with_scripts//total}%)")
    print(f"  Prompt-only    : {prompt_only} ({100*prompt_only//total}%)")
    print(f"  Fully complete : {full_complete} ({100*full_complete//total}%)")
    print(f"{'='*60}")

    print(f"\n{'Skill':<40} {'%':>4} {'Grade':>6} {'Scripts':>8} {'Evals':>6} {'Refs':>5}")
    print("-" * 70)

    incomplete = [r for r in results if not args.show_all and r["completeness_pct"] < 100]
    display = results if args.show_all else incomplete

    for r in display:
        g = grade(r["completeness_pct"])
        sc = r["components"].get("scripts", {})
        ev = r["components"].get("evals", {})
        rf = r["components"].get("references", {})
        scripts_str = f"[OK]{sc.get('files',0)}" if sc.get("exists") else "[--]"
        evals_str   = f"[OK]" if ev.get("exists") else "[--]"
        refs_str    = f"[OK]" if rf.get("exists") else "[--]"
        print(f"  {r['name']:<38} {r['completeness_pct']:>3}% {g:>6} {scripts_str:>8} {evals_str:>6} {refs_str:>5}")

    if not display and not args.show_all:
        print("  All skills complete! Use --show-all to see details.")

    if args.output:
        with open(args.output, "w") as f:
            json.dump({
                "summary": {"total": total, "avg_completeness": round(avg_score, 1),
                            "with_scripts": with_scripts, "prompt_only": prompt_only,
                            "fully_complete": full_complete},
                "skills": results
            }, f, indent=2)
        print(f"\n[+] Full report saved: {args.output}")

    # Exit with error if any required component missing
    failures = [r for r in results if r.get("missing_required")]
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()

