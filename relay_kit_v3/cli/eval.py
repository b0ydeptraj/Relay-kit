import argparse
import sys
import json
from pathlib import Path


def run_eval(args: argparse.Namespace) -> int:
    if args.action == "skill-battle":
        report = build_skill_battle(
            args.project_path,
            skill=args.skill,
            suite=args.suite,
            cleanup=args.cleanup,
            min_score=args.min_score,
        )
        if args.output_file:
            write_skill_battle(args.project_path, report, args.output_file)
        if args.json:
            print(json.dumps(report, ensure_ascii=True, indent=2))
        else:
            print(render_skill_battle(report))
        if args.strict and report["status"] != "pass":
            return 2
        return 0

    if args.action == "competency-battle":
        report = build_competency_battle(
            args.project_path,
            skill=args.skill,
            suite=args.suite,
            cleanup=args.cleanup,
        )
        if args.output_file:
            write_competency_battle(args.project_path, report, args.output_file)
        if args.json:
            print(json.dumps(report, ensure_ascii=True, indent=2))
        else:
            print(render_competency_battle(report))
        if args.strict and report["status"] != "pass":
            return 2
        return 0

    if args.action == "skill-weakness-report":
        battle_report = None
        if args.battle_file:
            battle_report = json.loads(Path(args.battle_file).read_text(encoding="utf-8"))
        report = build_skill_weakness_report(args.project_path, battle_report=battle_report)
        if args.output_file:
            write_skill_battle(args.project_path, report, args.output_file)
        if args.json:
            print(json.dumps(report, ensure_ascii=True, indent=2))
        else:
            print(render_skill_weakness_report(report))
        if args.strict and report["status"] != "pass":
            return 2
        return 0

    if args.action == "battle-audit":
        report = build_battle_audit(args.project_path, skill_battle_file=args.skill_battle_file)
        if args.output_file:
            write_battle_audit(args.project_path, report, args.output_file)
        if args.json:
            print(json.dumps(report, ensure_ascii=True, indent=2))
        else:
            print(render_battle_audit(report))
        if args.strict and report["status"] != "pass":
            return 2
        return 0

    if args.action == "repo-profile":
        report = build_repo_profile(args.project_path, write_index=args.write_index)
        if args.output_file:
            write_repo_profile(args.project_path, report, args.output_file)
        if args.json:
            print(json.dumps(report, ensure_ascii=True, indent=2))
        else:
            print(render_repo_profile(report))
        if args.strict and report.get("unknown_domain_mode"):
            return 2
        return 0

    if args.action == "domain-pack":
        if args.domain_action == "list":
            report = build_domain_pack_list(args.project_path)
        else:
            if not args.pack:
                print("relay-kit eval domain-pack run requires --pack <name>")
                return 2
            report = run_domain_pack(args.project_path, args.pack)
        if args.output_file:
            write_domain_pack_report(args.project_path, report, args.output_file)
        if args.json:
            print(json.dumps(report, ensure_ascii=True, indent=2))
        else:
            print(render_domain_pack_report(report))
        if args.strict and report["status"] != "pass":
            return 2
        return 0

    if args.action == "battle-benchmark":
        report = build_battle_benchmark(
            args.project_path,
            suite=args.suite,
            cleanup=args.cleanup,
            repo_limit=args.repo_limit,
        )
        if args.output_file:
            write_battle_benchmark(args.project_path, report, args.output_file)
        if args.json:
            print(json.dumps(report, ensure_ascii=True, indent=2))
        else:
            print(render_battle_benchmark(report))
        if args.strict and report["status"] != "pass":
            return 2
        return 0

    if args.action == "real-world":
        report = build_real_world_eval_report(
            args.project_path,
            cases_file=args.cases_file,
        )
        if args.output_file:
            write_real_world_eval_report(args.project_path, report, args.output_file)
        if args.json:
            print(json.dumps(report, ensure_ascii=True, indent=2))
        else:
            print(render_real_world_eval_report(report))
        if args.strict and report["status"] != "pass":
            return 2
        return 0

    if args.action != "run":
        return 2
    from scripts import eval_workflows

    eval_argv = [args.project_path]
    if args.scenario_fixtures:
        eval_argv.extend(["--scenario-fixtures", args.scenario_fixtures])
    if args.output_file:
        eval_argv.extend(["--output-file", args.output_file])
    if args.baseline_file:
        eval_argv.extend(["--baseline-file", args.baseline_file])
    if args.min_pass_rate is not None:
        eval_argv.extend(["--min-pass-rate", str(args.min_pass_rate)])
    if args.min_route_margin is not None:
        eval_argv.extend(["--min-route-margin", str(args.min_route_margin)])
    if args.min_evidence_coverage is not None:
        eval_argv.extend(["--min-evidence-coverage", str(args.min_evidence_coverage)])
    if args.min_scenarios is not None:
        eval_argv.extend(["--min-scenarios", str(args.min_scenarios)])
    if args.json:
        eval_argv.append("--json")
    if args.strict:
        eval_argv.append("--strict")
    return eval_workflows.main(eval_argv)

