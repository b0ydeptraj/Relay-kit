from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class SkillSpec:
    name: str
    description: str
    role: str
    layer: str
    inputs: List[str]
    outputs: List[str]
    references: List[str]
    next_steps: List[str]
    body: str


def utility_provider_spec(
    name: str,
    description: str,
    outputs: list[str],
    references: list[str],
    next_steps: list[str],
    mission: str,
    tasks: list[str],
    rules: list[str],
) -> SkillSpec:
    body_lines = [
        "# Mission",
        mission,
        "",
        "## Default outputs",
    ]
    body_lines.extend([f"- {item}" for item in outputs])
    body_lines.extend(
        [
            "",
            "## Typical tasks",
        ]
    )
    body_lines.extend([f"- {item}" for item in tasks])
    body_lines.extend(
        [
            "",
            "## Working rules",
        ]
    )
    body_lines.extend([f"- {item}" for item in rules])
    return SkillSpec(
        name=name,
        description=description,
        role="utility-provider",
        layer="layer-3-utility-providers",
        inputs=[
            "active hub or orchestrator request",
            "current authoritative artifact",
            "only the evidence relevant to this pass",
        ],
        outputs=outputs,
        references=references,
        next_steps=next_steps,
        body="\n".join(body_lines).strip(),
    )


def render_skill(spec: SkillSpec) -> str:
    parts = [
        "---",
        f"name: {spec.name}",
        f"description: {spec.description}",
        "---",
        "",
        spec.body.strip(),
        "",
        "## Role",
        f"- {spec.role}",
        "",
        "## Layer",
        f"- {spec.layer}",
        "",
        "## Inputs",
    ]
    parts.extend(f"- {item}" for item in spec.inputs)
    parts.extend(
        [
            "",
            "## Outputs",
        ]
    )
    parts.extend(f"- {item}" for item in spec.outputs)
    parts.extend(
        [
            "",
            "## Reference skills and rules",
        ]
    )
    parts.extend(f"- {item}" for item in spec.references)
    parts.extend(
        [
            "",
            "## Likely next step",
        ]
    )
    parts.extend(f"- {item}" for item in spec.next_steps)
    return "\n".join(parts).rstrip() + "\n"
