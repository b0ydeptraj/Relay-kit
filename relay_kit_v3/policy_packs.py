"""Named policy guard packs for Relay-kit governance profiles."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class PolicyPack:
    name: str
    description: str
    required_files: tuple[str, ...] = ()


POLICY_PACKS: dict[str, PolicyPack] = {
    "baseline": PolicyPack(
        name="baseline",
        description="Default deterministic source and runtime risk checks.",
    ),
    "team": PolicyPack(
        name="team",
        description="Baseline checks plus durable team state and handoff surfaces.",
        required_files=(
            ".relay-kit/state/team-board.md",
            ".relay-kit/state/lane-registry.md",
            ".relay-kit/state/handoff-log.md",
        ),
    ),
    "enterprise": PolicyPack(
        name="enterprise",
        description="Team checks plus security, testing, observability, review, and release governance surfaces.",
        required_files=(
            ".relay-kit/state/team-board.md",
            ".relay-kit/state/lane-registry.md",
            ".relay-kit/state/handoff-log.md",
            ".relay-kit/references/security-patterns.md",
            ".relay-kit/references/testing-patterns.md",
            ".relay-kit/references/logging-observability.md",
            ".relay-kit/docs/review-loop.md",
            ".relay-kit/docs/branch-completion.md",
            ".relay-kit/docs/bundle-gating.md",
        ),
    ),
}

DEFAULT_POLICY_PACK = "baseline"


def get_policy_pack(name: str | None) -> PolicyPack:
    pack_name = name or DEFAULT_POLICY_PACK
    try:
        return POLICY_PACKS[pack_name]
    except KeyError as exc:
        available = ", ".join(sorted(POLICY_PACKS))
        raise ValueError(f"Unknown policy pack {pack_name!r}. Available packs: {available}") from exc


def missing_required_files(project_root: Path, pack: PolicyPack) -> list[str]:
    return [path for path in pack.required_files if not (project_root / path).exists()]
