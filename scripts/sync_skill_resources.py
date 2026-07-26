"""
Copy competencies/evals/examples/references from .agent/skills/<name>/
into relay_kit_v3/skill_resources/<name>/
for all 31 skills (23 offensive + 8 entrypoint) that are missing.
"""
import shutil
from pathlib import Path

REPO = Path(r"C:\Users\b0ydeptrai\Documents\relay-kit")
SRC_BASE = REPO / ".agent" / "skills"
DST_BASE = REPO / "relay_kit_v3" / "skill_resources"

ALL_31 = [
    # 23 offensive
    "advanced-python-engineering","antibot-challenge-solving","attack-chain-orchestration",
    "binary-reverse-methodology","binary-stealth-obfuscation","browser-fingerprint-engineering",
    "cpp-systems-engineering","desktop-imgui-development","desktop-python-ui",
    "edr-evasion-tactics","field-journal-evolution","frontend-crypto-reverse",
    "malware-analysis-workflows","mmo-llm-automation","mmo-onchain-security-audit",
    "mobile-app-reverse","network-stealth-c2","offensive-security-engagement",
    "process-injection-techniques","protocol-fingerprint-spoofing","telemetry-blinding",
    "terminal-operator-ui","windows-native-internals",
    # 8 entrypoint
    "brainstorm","build-it","debug-systematically","prove-it","ready-check","review-pr","start-here","write-steps",
]

SUBDIRS = ["competencies", "evals", "examples", "references"]

copied = 0
skipped = 0
for skill in ALL_31:
    src_skill = SRC_BASE / skill
    dst_skill = DST_BASE / skill
    dst_skill.mkdir(parents=True, exist_ok=True)

    for subdir in SUBDIRS:
        src_dir = src_skill / subdir
        dst_dir = dst_skill / subdir
        if src_dir.exists():
            dst_dir.mkdir(exist_ok=True)
            for f in src_dir.iterdir():
                dst_f = dst_dir / f.name
                shutil.copy2(f, dst_f)
                copied += 1
        else:
            skipped += 1

    print(f"  OK {skill}")

print(f"\nDone: {copied} files copied, {skipped} missing subdirs skipped")
