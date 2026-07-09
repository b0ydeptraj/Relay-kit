import argparse
import sys
import json
from relay_kit_v3.field_journal import FieldJournal
from relay_kit_v3.evidence_quality import EvidenceGateError

def run_journal_list(args: argparse.Namespace) -> int:
    journal = FieldJournal(getattr(args, "project_path", "."))
    entries = journal.list_entries()
    
    if not entries:
        print("Journal is empty.")
        return 0
        
    print(f"{'ID':<36} | {'STATUS':<10} | {'CONFIDENCE':<10} | {'EVIDENCE_REF'}")
    print("-" * 80)
    for e in entries:
        print(f"{e.get('id', '')[:36]:<36} | {e.get('status', ''):<10} | {e.get('confidence', ''):<10} | {e.get('evidence_ref', '')}")
    return 0

def run_journal_inspect(args: argparse.Namespace) -> int:
    journal = FieldJournal(getattr(args, "project_path", "."))
    entry = journal.get_entry(args.id)
    
    if not entry:
        print(f"Entry {args.id} not found.")
        return 1
        
    print(json.dumps(entry, indent=2, ensure_ascii=False))
    return 0

def run_journal_promote(args: argparse.Namespace) -> int:
    journal = FieldJournal(getattr(args, "project_path", "."))
    success = journal.promote_entry(args.id)
    
    if success:
        print(f"Successfully promoted entry {args.id} to high confidence.")
        return 0
    else:
        print(f"Failed to promote: Entry {args.id} not found.")
        return 1

def run_journal_capture(args: argparse.Namespace) -> int:
    journal = FieldJournal(getattr(args, "project_path", "."))
    
    entry = {
        "evidence_ref": getattr(args, "evidence_ref", ""),
        "content": getattr(args, "content", ""),
        "error_signature": getattr(args, "error_signature", "")
    }
    
    try:
        captured = journal.capture(entry, promotion_recommended=False)
        print(f"Captured entry {captured['id']}")
        return 0
    except EvidenceGateError as e:
        print(f"Capture blocked by EvidenceGate: {e}")
        return 1
    except Exception as e:
        print(f"Failed to capture entry: {e}")
        return 1

def run_journal(args: argparse.Namespace) -> int:
    action = getattr(args, "action", None)
    if action == "list":
        return run_journal_list(args)
    elif action == "inspect":
        return run_journal_inspect(args)
    elif action == "promote":
        return run_journal_promote(args)
    elif action == "capture":
        return run_journal_capture(args)
    raise ValueError(f"Unknown journal action: {action}")
