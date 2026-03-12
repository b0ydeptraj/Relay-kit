from __future__ import annotations

from dataclasses import dataclass
from textwrap import dedent
from typing import Dict, List


@dataclass(frozen=True)
class ArtifactContract:
    name: str
    path: str
    purpose: str
    sections: List[str]
    used_by: List[str]


ARTIFACT_CONTRACTS: Dict[str, ArtifactContract] = {
    "product-brief": ArtifactContract(
        name="product-brief",
        path=".ai-kit/contracts/product-brief.md",
        purpose="Capture the problem, users, outcomes, assumptions, and constraints before detailed planning.",
        sections=[
            "Problem statement",
            "Target users and jobs-to-be-done",
            "Desired outcomes and success signals",
            "Assumptions and unknowns",
            "Constraints and non-goals",
            "Open questions",
        ],
        used_by=["analyst", "pm", "workflow-router"],
    ),
    "prd": ArtifactContract(
        name="prd",
        path=".ai-kit/contracts/PRD.md",
        purpose="Define scope, functional/non-functional requirements, acceptance criteria, release slices, and risks.",
        sections=[
            "Objective and scope",
            "Functional requirements",
            "Non-functional requirements",
            "Out of scope",
            "Acceptance criteria",
            "Risks and mitigations",
            "Release slices",
        ],
        used_by=["pm", "architect", "scrum-master", "qa-governor"],
    ),
    "architecture": ArtifactContract(
        name="architecture",
        path=".ai-kit/contracts/architecture.md",
        purpose="Translate the PRD into concrete technical structure, data flow, interfaces, and implementation constraints.",
        sections=[
            "Current-system constraints",
            "Proposed design",
            "Module boundaries",
            "Data flow and integrations",
            "Operational concerns",
            "Trade-offs and ADR notes",
            "Implementation readiness verdict",
        ],
        used_by=["architect", "scrum-master", "qa-governor"],
    ),
    "epics": ArtifactContract(
        name="epics",
        path=".ai-kit/contracts/epics.md",
        purpose="Break work into coherent slices and define sequencing before story creation.",
        sections=[
            "Epic overview",
            "Per-epic goals",
            "Dependencies",
            "Definition of done",
            "Suggested order",
        ],
        used_by=["pm", "scrum-master"],
    ),
    "story": ArtifactContract(
        name="story",
        path=".ai-kit/contracts/stories/story-001.md",
        purpose="Provide implementation-ready, focused context for a single vertical slice.",
        sections=[
            "Story statement",
            "Acceptance criteria",
            "Implementation notes",
            "Test notes",
            "Risks",
            "Done checklist",
        ],
        used_by=["scrum-master", "developer", "qa-governor"],
    ),
    "project-context": ArtifactContract(
        name="project-context",
        path=".ai-kit/contracts/project-context.md",
        purpose="Document current codebase patterns, constraints, and rules that every later step must respect.",
        sections=[
            "Existing architecture",
            "Coding conventions",
            "Dependency and toolchain rules",
            "Domain and compliance constraints",
            "Known sharp edges",
            "Files or modules to mirror",
        ],
        used_by=["workflow-router", "analyst", "pm", "architect", "scrum-master", "qa-governor"],
    ),
    "qa-report": ArtifactContract(
        name="qa-report",
        path=".ai-kit/contracts/qa-report.md",
        purpose="Record acceptance coverage, risk review, regression impact, and remaining gaps before declaring work complete.",
        sections=[
            "Scope checked",
            "Acceptance coverage",
            "Risk matrix",
            "Regression surface",
            "Evidence collected",
            "Go / no-go recommendation",
        ],
        used_by=["qa-governor", "developer"],
    ),
    "tech-spec": ArtifactContract(
        name="tech-spec",
        path=".ai-kit/contracts/tech-spec.md",
        purpose="Small-change spec used by the quick flow for bug fixes and narrowly scoped features.",
        sections=[
            "Change summary",
            "Root cause or context",
            "Files likely affected",
            "Implementation notes",
            "Verification steps",
        ],
        used_by=["workflow-router", "developer", "qa-governor"],
    ),
    "workflow-state": ArtifactContract(
        name="workflow-state",
        path=".ai-kit/state/workflow-state.md",
        purpose="Keep phase, chosen track, current artifact, next recommended skill, and blockers visible across sessions.",
        sections=[
            "Current request",
            "Complexity level",
            "Chosen track",
            "Completed artifacts",
            "Next skill",
            "Known blockers",
            "Notes",
        ],
        used_by=["workflow-router", "team-orchestrators"],
    ),
}


SECTION_HINTS = {
    "product-brief": {
        "Problem statement": "What problem exists today, for whom, and why it matters now.",
        "Target users and jobs-to-be-done": "Primary user segments and what they are trying to accomplish.",
        "Desired outcomes and success signals": "Business/user outcomes and how success will be judged.",
        "Assumptions and unknowns": "Anything still uncertain that can change scope or design.",
        "Constraints and non-goals": "Budget, time, platform, compliance, and what will deliberately not be solved.",
        "Open questions": "Questions that must be answered before PRD or architecture can be considered stable.",
    },
    "prd": {
        "Objective and scope": "State the product objective and scope boundaries in plain language.",
        "Functional requirements": "List numbered requirements with user-facing intent.",
        "Non-functional requirements": "Performance, reliability, security, observability, supportability.",
        "Out of scope": "Name tempting ideas that are intentionally excluded from this slice.",
        "Acceptance criteria": "Concrete pass/fail conditions tied to scope.",
        "Risks and mitigations": "Product, technical, delivery, and adoption risks.",
        "Release slices": "Propose thin vertical slices or milestones.",
    },
    "architecture": {
        "Current-system constraints": "Patterns that already exist and should not be broken casually.",
        "Proposed design": "High-level shape of the change and why it fits the current system.",
        "Module boundaries": "What belongs where. Name modules, owners, and interfaces.",
        "Data flow and integrations": "Request/response paths, persistence, external APIs, messaging.",
        "Operational concerns": "Security, performance, migration, logging, rollout, failure handling.",
        "Trade-offs and ADR notes": "What was chosen, what was rejected, and why.",
        "Implementation readiness verdict": "Ready / blocked, with the exact missing inputs if blocked.",
    },
}


def render_artifact(contract: ArtifactContract) -> str:
    hints = SECTION_HINTS.get(contract.name, {})
    lines = [
        f"# {contract.name}",
        "",
        f"> Path: `{contract.path}`",
        f"> Purpose: {contract.purpose}",
        f"> Used by: {', '.join(contract.used_by)}",
        "",
    ]
    for section in contract.sections:
        lines.append(f"## {section}")
        lines.append(hints.get(section, "Fill in only with evidence, decisions, or open questions relevant to this artifact."))
        lines.append("")
        lines.append("TBD")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"
