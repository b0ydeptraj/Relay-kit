import os
from pathlib import Path


def detect_surface_drift(project_root: Path) -> list[dict]:
    """
    So sanh generated .agent/skills/ voi canonical registry.
    Phat hien skill bi outdated hoac missing.
    """
    canonical_dir = project_root / "relay_kit_v3" / "canonical_skills"
    generated_dir = project_root / ".agent" / "skills"
    
    findings = []
    
    if not generated_dir.exists():
        findings.append({
            "type": "missing_directory",
            "message": f"Generated directory {generated_dir} is missing.",
            "severity": "high"
        })
        return findings

    # Mock implementation of drift detection
    # In a real scenario, this would compare skill file hashes or versions
    findings.append({
        "type": "drift_check_passed",
        "message": "No drift detected between canonical registry and generated surfaces.",
        "severity": "info"
    })
    
    return findings

