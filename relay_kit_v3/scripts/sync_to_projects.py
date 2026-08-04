"""
Sync relay-kit updates to target project folders.
Copies:
1. New/updated skills from .agent, .codex, .claude adapters
2. Updated skills.manifest.yaml
3. Updated relay_kit_v3 (if present in target)
"""
import shutil
import subprocess
import sys
from pathlib import Path

RELAY_KIT = Path(r"C:\Users\b0ydeptrai\Documents\relay-kit")
TARGETS = [
    Path(r"C:\Users\b0ydeptrai\Documents\anti-browser"),
]

ADAPTERS = [".agent", ".codex", ".claude"]

# 14 new skills to sync
NEW_SKILLS = [
    "ci-cd-pipeline",
    "container-kubernetes-ops",
    "database-migration-safety",
    "iac-cloud-provisioning",
    "incident-response",
    "llm-app-engineering",
    "mmo-authorization-gate",
    "observability-instrumentation",
    "performance-optimization",
    "privacy-compliance",
    "refactoring-discipline",
    "secrets-management",
    "secure-code-review",
    "technical-writing",
]


def sync_skill(skill_name: str, src_base: Path, dst_base: Path):
    src = src_base / skill_name
    dst = dst_base / skill_name
    if not src.exists():
        print(f"    SKIP {skill_name}: source not found")
        return False
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)
    return True


def sync_to_target(target: Path):
    print(f"\n{'='*60}")
    print(f"Syncing to: {target}")
    print('='*60)

    # Check target has relay-kit structure
    if not (target / ".agent" / "skills").exists():
        print(f"  SKIP: {target} has no .agent/skills/ directory")
        return

    # 1. Sync new skills to all adapters
    for adapter in ADAPTERS:
        src_skills = RELAY_KIT / adapter / "skills"
        dst_skills = target / adapter / "skills"
        dst_skills.mkdir(parents=True, exist_ok=True)

        copied = 0
        for skill_name in NEW_SKILLS:
            if sync_skill(skill_name, src_skills, dst_skills):
                copied += 1
                print(f"  [{adapter}] + {skill_name}")
        print(f"  [{adapter}] Copied {copied} new skills")

    # 2. Sync skills.manifest.yaml
    src_manifest = RELAY_KIT / "skills.manifest.yaml"
    dst_manifest = target / "skills.manifest.yaml"
    if src_manifest.exists():
        shutil.copy2(src_manifest, dst_manifest)
        print(f"  [manifest] Updated skills.manifest.yaml")

    # 3. Sync .relay-kit/docs if exists in target
    src_rk_docs = RELAY_KIT / ".relay-kit" / "docs"
    dst_rk_docs = target / ".relay-kit" / "docs"
    if src_rk_docs.exists() and dst_rk_docs.exists():
        for f in src_rk_docs.iterdir():
            if f.is_file():
                dst = dst_rk_docs / f.name
                shutil.copy2(f, dst)
        print(f"  [.relay-kit/docs] Synced docs")

    print(f"\n  Done for {target.name}")


def verify_counts(target: Path):
    for adapter in ADAPTERS:
        skills_dir = target / adapter / "skills"
        if skills_dir.exists():
            count = sum(1 for d in skills_dir.iterdir() if d.is_dir())
            print(f"  {adapter}/skills: {count} skills")


if __name__ == "__main__":
    for target in TARGETS:
        sync_to_target(target)
        print(f"\nVerifying counts:")
        verify_counts(target)

    print("\n\nAll targets synced!")
