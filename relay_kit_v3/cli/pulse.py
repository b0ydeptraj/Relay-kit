import argparse
import sys
import json
from pathlib import Path


def run_pulse(args: argparse.Namespace) -> int:
    if args.action != "build":
        return 2
    report = build_pulse_report(
        args.project_path,
        profile=args.profile,
        evidence_limit=args.evidence_limit,
        include_readiness=args.include_readiness,
        include_publication=args.include_publication,
        include_package_index=args.include_package_index,
        include_support_request=args.include_support_request,
        include_commercial_dossier=args.include_commercial_dossier,
        include_context_audit=args.include_context_audit,
        include_lane_audit=args.include_lane_audit,
        include_adapter_diagnostics=args.include_adapter_diagnostics,
        include_token_audit=args.include_token_audit,
        include_delegation_audit=args.include_delegation_audit,
        include_query_search=args.include_query_search,
        include_service_boundaries=args.include_service_boundaries,
        workflow_eval_file=args.workflow_eval_file,
        readiness_file=args.readiness_file,
        publication_file=args.publication_file,
        package_index_file=args.package_index_file,
        support_request_file=args.support_request_file,
        commercial_dossier_file=args.commercial_dossier_file,
        context_audit_file=args.context_audit_file,
        lane_audit_file=args.lane_audit_file,
        adapter_diagnostics_file=args.adapter_diagnostics_file,
        token_audit_file=args.token_audit_file,
        delegation_audit_file=args.delegation_audit_file,
        signal_calibration_file=args.signal_calibration_file,
        include_signal_calibration=not args.skip_signal_calibration,
        query_search_file=args.query_search_file,
        service_boundaries_file=args.service_boundaries_file,
        query_search_text=args.query_search_text,
        output_dir=args.output_dir,
        history_limit=args.history_limit,
    )
    outputs = write_pulse_report(
        args.project_path,
        report,
        output_dir=args.output_dir,
        record_history=not args.no_history,
    )
    if args.json:
        payload = {
            "outputs": {name: str(path) for name, path in outputs.items()},
            "report": report,
        }
        print(json.dumps(payload, ensure_ascii=True, indent=2))
    else:
        print(f"Wrote {outputs['json']}")
        print(f"Wrote {outputs['html']}")
        print(f"Pulse status: {report['status']}")
        print(f"Pulse score: {report['pulse_score']}")
    # Pulse build is a reporting command; it should emit artifacts even when status is hold.
    return 0

