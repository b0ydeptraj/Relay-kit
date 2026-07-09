import os
from pathlib import Path

def check_roadmap_v5():
    root = Path(r"C:\Users\b0ydeptrai\Documents\relay-kit")
    
    expected_files = [
        # V5.0
        "relay_kit_public_cli.py",
        "relay_kit_v3/cli/engine.py",
        "relay_kit_v3/cli/command_schema.yaml",
        "tests/test_cli_compat.py",
        
        # V5.1
        "relay_kit_v3/extensions/pack_format.py",
        "relay_kit_v3/extensions/trust_policy.py",
        "relay_kit_v3/extensions/installer.py",
        "relay_kit_v3/extensions/gauntlet_gate.py",
        "relay_kit_v3/extensions/quarantine.py",
        "relay_kit_v3/extensions/manager.py",
        "relay_kit_v3/extensions/permissions.py",
        ".relay-kit/trust-policy.yaml",
        ".relay-kit/extensions/installed.json",
        
        # V5.2
        "relay_kit_v3/context_graph.py",
        "relay_kit_v3/context_index.py",
        "relay_kit_v3/semantic_index.py",
        "relay_kit_v3/search_router.py",
        "relay_kit_v3/token_economy.py",
        "relay_kit_v3/context_index_state.py",
        "tests/context_search_eval.json",
        "tests/test_context_search_eval.py",
        
        # V5.3
        "relay_kit_v3/field_journal.py",
        "relay_kit_v3/evidence_quality.py",
        "relay_kit_v3/pattern_retriever.py",
        "relay_kit_v3/cli/journal.py",
        "relay_kit_v3/journal_redaction.py",
        
        # V5.4
        "relay_kit_v3/lane_lock.py",
        "relay_kit_v3/event_ledger.py",
        "relay_kit_v3/delegation_control.py",
        "relay_kit_v3/cli/lane.py",
        "relay_kit_v3/pulse.py",
        "relay_kit_v3/lane_simulator.py",
        "relay_kit_v3/dashboard/app.py",
        "relay_kit_v3/dashboard/templates/index.html",
        ".relay-kit/runtime/lane-locks.db",
        ".relay-kit/runtime/event-ledger.db",
        
        # V5.5
        "relay_kit_v3/v5_release_doctor.py",
        "tests/test_v4_migration.py",
        "relay_kit_v3/surface_drift.py",
        "tests/test_extension_rollback.py",
        "tests/journal_redaction_fixtures.json",
        "tests/test_lane_concurrency.py",
        "docs/relay-kit-v5-upgrade.md",
    ]
    
    missing_files = []
    for rel_path in expected_files:
        full_path = root / rel_path
        if not full_path.exists():
            missing_files.append(rel_path)
            
    if missing_files:
        print("Missing files according to Roadmap V5:")
        for f in missing_files:
            print(f"  - {f}")
    else:
        print("All expected files from Roadmap V5 are present!")

if __name__ == "__main__":
    check_roadmap_v5()
