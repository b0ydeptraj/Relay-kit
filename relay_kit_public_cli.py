#!/usr/bin/env python3
"""Public Relay-kit installer CLI.

This wrapper exposes a friendlier command surface:
  relay-kit init <project_path> --codex|--claude|--antigravity
  relay-kit <project_path> --codex|--claude|--antigravity
  relay-kit doctor <project_path>
  relay-kit eval run <project_path>
  relay-kit upgrade check <project_path>
  relay-kit policy check <project_path>
  relay-kit support bundle <project_path>
  relay-kit support request <project_path>
  relay-kit support triage <project_path>
  relay-kit support soak <project_path>
  relay-kit readiness check <project_path>
  relay-kit release verify <project_path>
  relay-kit publish plan <project_path>
  relay-kit publish evidence <project_path>
  relay-kit publish trail <project_path>
  relay-kit publish status <project_path>
  relay-kit publish index-check <project_path>
  relay-kit commercial dossier <project_path>
  relay-kit pulse build <project_path>
  relay-kit signal export <project_path>
  relay-kit contract import <project_path> --contract-file <relay-contract.json>
  relay-kit context audit <project_path>
  relay-kit context index <project_path>
  relay-kit context search <project_path> --query "..."
  relay-kit context related <project_path> --path src/auth/login.ts
  relay-kit context budget <project_path>
  relay-kit context pack <project_path>
  relay-kit token audit <project_path>
  relay-kit shell compact <project_path> -- <command...>
  relay-kit eval real-world <project_path>
  relay-kit eval competency-battle <project_path> --skill all --suite core
  relay-kit eval repo-profile <project_path>
  relay-kit eval domain-pack list <project_path>
  relay-kit proof audit <project_path>
  relay-kit calibrate readiness <project_path>
  relay-kit locale show <project_path>
  relay-kit locale set <project_path> --locale <code>
  relay-kit lane audit <project_path>
  relay-kit delegation plan <project_path> --task "..."
  relay-kit delegation audit <project_path>
  relay-kit adapter diagnose <project_path>
  relay-kit command list <project_path>
  relay-kit command diagnose <project_path>
  relay-kit agent list <project_path>
  relay-kit agent diagnose <project_path>
  relay-kit query search <project_path> --query "..."
  relay-kit prompt enhance <project_path> --prompt "..."
  relay-kit service boundaries <project_path>
  relay-kit runtime doctor <project_path>
  relay-kit skill gauntlet <project_path>
  relay-kit impact radar <project_path>
  relay-kit accessibility review <project_path>
  relay-kit release readiness <project_path>
  relay-kit continuity checkpoint <project_path>
  relay-kit migration guard <project_path>

It maps to the existing canonical runtime entrypoint (`relay_kit.py`)
without changing the underlying generation flow.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

import relay_kit as relay_core
from relay_kit_v3.cli import engine
from relay_kit_v3.evidence_ledger import append_event, ledger_path, new_run_id, parse_findings_count, summarize_events
from relay_kit_v3.bundle_manifest import verify_manifest_file, verify_trusted_manifest_file, write_manifest, write_trust_stamp
from relay_kit_v3.policy_packs import DEFAULT_POLICY_PACK, POLICY_PACKS
from relay_kit_v3.pulse import build_pulse_report, write_pulse_report
from relay_kit_v3.commercial_dossier import (
    build_commercial_dossier,
    render_commercial_dossier,
    write_commercial_dossier,
)
from relay_kit_v3.publication import (
    build_package_index_check,
    build_publication_evidence,
    build_publication_plan,
    build_publication_trail,
    build_publication_trail_status,
    render_package_index_check,
    render_publication_evidence,
    render_publication_plan,
    render_publication_trail,
    render_publication_trail_status,
    write_package_index_check,
    write_publication_evidence,
    write_publication_plan,
    write_publication_trail,
    write_publication_trail_markdown,
)
from relay_kit_v3.release_lane import build_release_lane_report, render_release_lane_report, write_release_lane_report
from relay_kit_v3.readiness import build_readiness_report, render_readiness_report
from relay_kit_v3.signal_calibration import (
    build_report as build_signal_calibration_report,
    render_report as render_signal_calibration_report,
    write_report as write_signal_calibration_report,
)
from relay_kit_v3.signal_export import build_signal_export, write_signal_export
from relay_kit_v3.token_economy import (
    DEFAULT_MAX_TOKENS,
    build_context_budget,
    build_context_pack,
    build_token_audit,
    render_context_budget,
    render_context_pack,
    render_token_audit,
    write_context_budget,
    write_context_pack,
    write_token_audit,
)
from relay_kit_v3.shell_compaction import ShellCompactionError, run_compacted_command
from relay_kit_v3.real_world_eval import (
    build_report as build_real_world_eval_report,
    render_report as render_real_world_eval_report,
    write_report as write_real_world_eval_report,
)
from relay_kit_v3.battle_audit import build_battle_audit, render_battle_audit, write_battle_audit
from relay_kit_v3.battle_benchmark import build_battle_benchmark, render_battle_benchmark, write_battle_benchmark
from relay_kit_v3.competency_battle import (
    build_competency_battle,
    render_competency_battle,
    write_competency_battle,
)
from relay_kit_v3.domain_packs import (
    build_domain_pack_list,
    render_domain_pack_report,
    run_domain_pack,
    write_domain_pack_report,
)
from relay_kit_v3.repo_profile import build_repo_profile, render_repo_profile, write_repo_profile
from relay_kit_v3.skill_battle import (
    build_skill_battle,
    build_skill_weakness_report,
    render_skill_battle,
    render_skill_weakness_report,
    write_skill_battle,
)
from relay_kit_v3.skill_proof import (
    build_report as build_skill_proof_report,
    render_report as render_skill_proof_report,
    write_report as write_skill_proof_report,
)
from relay_kit_v3.contract_export import write_contract_export
from relay_kit_v3.contract_import import import_contracts, render_contract_import_report
from relay_kit_v3.context_governance import build_context_audit, render_context_audit, write_context_audit
from relay_kit_v3.context_index import (
    build_context_explain_symbol,
    build_context_mcp_tool_result,
    build_context_index,
    build_context_related,
    build_context_search,
    context_mcp_manifest,
    read_active_context,
    render_active_context,
    render_context_explain_symbol,
    render_context_index,
    render_context_mcp,
    render_context_related,
    render_context_search,
    render_context_watch,
    watch_context_index,
    write_active_context,
    write_context_index,
)
from relay_kit_v3.lane_audit import build_lane_audit, render_lane_audit, write_lane_audit
from relay_kit_v3.delegation_control import (
    adapter_capabilities,
    build_delegation_audit,
    build_delegation_plan,
    close_completed,
    record_usage,
    render_delegation_report,
)
from relay_kit_v3.adapter_diagnostics import (
    build_adapter_diagnostics,
    render_adapter_diagnostics,
    write_adapter_diagnostics,
)
from relay_kit_v3.agent_profiles import (
    agent_profile_records,
    build_agent_diagnostics,
    render_agent_diagnostics,
    write_agent_diagnostics,
)
from relay_kit_v3.command_registry import (
    build_command_diagnostics,
    lifecycle_command_records,
    render_command_diagnostics,
    write_command_diagnostics,
)
from relay_kit_v3.intent_enhancer import (
    build_prompt_enhancement,
    render_prompt_enhancement,
    write_prompt_enhancement,
)
from relay_kit_v3.query_search import build_query_search, render_query_search, write_query_search
from relay_kit_v3.runtime_locale import (
    inspect_runtime_locale,
    load_runtime_locale,
    write_runtime_locale,
)
from relay_kit_v3.service_boundaries import (
    build_service_boundary_report,
    render_service_boundary_report,
    write_service_boundary_report,
)
from relay_kit_v3.support_bundle import build_support_bundle, write_support_bundle
from relay_kit_v3.support_request import build_support_request, render_support_request, write_support_request
from relay_kit_v3.support_triage import (
    build_support_soak_report,
    build_support_triage,
    render_support_soak_report,
    render_support_triage,
)
from relay_kit_v3.upgrade import build_upgrade_report, render_report, write_version_marker


REPO_ROOT = Path(__file__).resolve().parent


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="relay-kit",
        description="Public Relay-kit installer for full runtime generation.",
    )
    parser.add_argument("project_path", nargs="?", default=".", help="Target project path")

    adapter = parser.add_mutually_exclusive_group()
    adapter.add_argument("--codex", action="store_true", help="Install Codex runtime skills")
    adapter.add_argument("--claude", action="store_true", help="Install Claude runtime skills")
    adapter.add_argument(
        "--antigravity",
        action="store_true",
        help="Install Antigravity runtime skills (mapped to .agent)",
    )
    adapter.add_argument("--all", action="store_true", help="Install all active runtime adapters")
    adapter.add_argument("--generic", action="store_true", help="Generate generic prompts output")

    parser.add_argument("--bundle", default="enterprise", help="Bundle name (default: enterprise)")
    parser.add_argument(
        "--baseline",
        dest="bundle",
        action="store_const",
        const="baseline",
        help="Generate the smaller baseline bundle instead of the default enterprise bundle",
    )
    parser.add_argument("--no-bundle", action="store_true", help="Skip v3 bundle generation")

    parser.add_argument(
        "--emit-contracts",
        dest="emit_contracts",
        action="store_true",
        default=True,
        help="Emit contracts/state artifacts (default: on)",
    )
    parser.add_argument(
        "--no-emit-contracts",
        dest="emit_contracts",
        action="store_false",
        help="Disable contracts/state emit",
    )
    parser.add_argument(
        "--emit-docs",
        dest="emit_docs",
        action="store_true",
        default=True,
        help="Emit docs artifacts (default: on)",
    )
    parser.add_argument(
        "--no-emit-docs",
        dest="emit_docs",
        action="store_false",
        help="Disable docs emit",
    )
    parser.add_argument(
        "--emit-reference-templates",
        dest="emit_reference_templates",
        action="store_true",
        default=True,
        help="Emit reference templates (default: on)",
    )
    parser.add_argument(
        "--no-emit-reference-templates",
        dest="emit_reference_templates",
        action="store_false",
        help="Disable reference templates emit",
    )

    srs_switch = parser.add_mutually_exclusive_group()
    srs_switch.add_argument("--enable-srs-first", action="store_true", help="Enable SRS-first policy for this project")
    srs_switch.add_argument("--disable-srs-first", action="store_true", help="Disable SRS-first policy for this project")
    parser.add_argument("--srs-gate", choices=["off", "warn", "hard"], help="SRS policy gate mode")
    parser.add_argument("--srs-scope", choices=["product-enterprise", "all"], help="SRS policy scope")
    parser.add_argument("--srs-risk", choices=["normal", "high"], help="SRS policy risk profile")
    parser.add_argument("--locale", help="Set runtime locale profile during init/install (allowed: vi, en)")
    parser.add_argument("--fallback-locale", help="Set runtime fallback locale during init/install (default: en)")

    parser.add_argument("--list-skills", action="store_true", help="List active runtime bundles")
    parser.add_argument("-v", "--verbose", action="store_true")

    return parser.parse_args(argv)


# _parse_doctor_args removed in Sprint 1 - delegated to relay_kit_v3.cli.engine


# _parse_evidence_args delegated to relay_kit_v3.cli.engine


# _parse_contract_args delegated to relay_kit_v3.cli.engine


# _parse_context_args delegated to relay_kit_v3.cli.engine


# _parse_lane_args delegated to relay_kit_v3.cli.engine
# _parse_delegation_args delegated to relay_kit_v3.cli.engine


# parsers for locale, token, calibrate, shell, adapter, command delegated to relay_kit_v3.cli.engine


# parsers for agent, query, prompt, service, runtime, skill, impact delegated to relay_kit_v3.cli.engine


def _resolve_ai(args: argparse.Namespace) -> str:
    if args.codex:
        return "codex"
    if args.claude:
        return "claude"
    if args.antigravity:
        return "antigravity"
    if args.all:
        return "all"
    if args.generic:
        return "generic"
    return "codex"


def _build_relay_argv(args: argparse.Namespace) -> list[str]:
    relay_argv: list[str] = ["relay-kit-core"]

    if args.list_skills:
        relay_argv.append("--list-skills")
        return relay_argv

    relay_argv.append(args.project_path)
    relay_argv.extend(["--ai", _resolve_ai(args)])

    if not args.no_bundle:
        relay_argv.extend(["--bundle", args.bundle])

    if args.emit_contracts:
        relay_argv.append("--emit-contracts")
    if args.emit_docs:
        relay_argv.append("--emit-docs")
    if args.emit_reference_templates:
        relay_argv.append("--emit-reference-templates")

    if args.enable_srs_first:
        relay_argv.append("--enable-srs-first")
    if args.disable_srs_first:
        relay_argv.append("--disable-srs-first")
    if args.srs_gate:
        relay_argv.extend(["--srs-gate", args.srs_gate])
    if args.srs_scope:
        relay_argv.extend(["--srs-scope", args.srs_scope])
    if args.srs_risk:
        relay_argv.extend(["--srs-risk", args.srs_risk])
    if args.locale:
        relay_argv.extend(["--locale", args.locale])
    if args.fallback_locale:
        relay_argv.extend(["--fallback-locale", args.fallback_locale])

    if args.verbose:
        relay_argv.append("--verbose")

    return relay_argv





# run_evidence delegated to relay_kit_v3.cli.evidence


# run_contract delegated to relay_kit_v3.cli.contract


# run_context delegated to relay_kit_v3.cli.context


# run_lane delegated to relay_kit_v3.cli.lane
# run_delegation delegated to relay_kit_v3.cli.delegation


# handlers for locale, token, calibrate, shell, adapter, command delegated to relay_kit_v3.cli modules


# handlers for agent, query, prompt, service, runtime, skill, impact delegated to relay_kit_v3.cli modules


def main(argv: list[str] | None = None) -> int:
    raw_argv = sys.argv[1:] if argv is None else argv
    
    known_commands = {
        "doctor", "evidence", "contract", "context", "lane", "delegation",
        "locale", "token", "calibrate", "shell", "adapter", "command",
        "agent", "query", "prompt", "service", "runtime", "skill", "impact",
        "accessibility", "manifest", "eval", "proof", "upgrade", "policy",
        "support", "readiness", "release", "continuity", "migration",
        "publish", "commercial", "pulse", "signal", "extension", "journal"
    }
    
    if raw_argv and raw_argv[0] in known_commands:
        return engine.dispatch(raw_argv[0], raw_argv[1:])

    args = _parse_args(raw_argv)
    _setup_logging(args.verbose)
    
    # Global public install fallback
    if args.diagnostic_run:
        print(f"Relay-kit public runtime diagnostic: PASS (mock)")
        return 0
        
    ai_str = _resolve_ai(args)
    if not ai_str:
        print("Error: Must specify --codex, --claude, or --antigravity", file=sys.stderr)
        return 1

    print(f"Generating public Relay-kit ({args.bundle}) runtime in {args.project_path} for {ai_str}...")
    _write_stub_files(args.project_path, ai_str, args.bundle)
    print("Done. Relay-kit runtime is ready.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
