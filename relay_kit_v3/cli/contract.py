import argparse
import json
from relay_kit_v3.contract_export import write_contract_export
from relay_kit_v3.contract_import import import_contracts, render_contract_import_report

def run_contract_export(args: argparse.Namespace) -> int:
    output_path = write_contract_export(args.project_path, args.output_file)
    print(f"Wrote {output_path}")
    return 0

def run_contract_import(args: argparse.Namespace) -> int:
    report = import_contracts(
        args.project_path,
        contract_file=args.contract_file,
        apply=args.apply,
        force=getattr(args, "force", False),
    )
    if getattr(args, "json", False):
        print(json.dumps(report, ensure_ascii=True, indent=2))
    else:
        print(render_contract_import_report(report))
        
def run_contract(args: argparse.Namespace) -> int:
    action = getattr(args, "action", None)
    if action == "export":
        return run_contract_export(args)
    elif action == "import":
        return run_contract_import(args)
    return 1

