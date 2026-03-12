from __future__ import annotations

from textwrap import dedent
from typing import Dict, List


LAYER_MODEL: Dict[str, Dict[str, object]] = {
    "layer-1-orchestrators": {
        "purpose": "Coordinate the whole system, choose the active lane, and keep shared state current.",
        "skills": ["workflow-router", "bootstrap", "team", "cook"],
    },
    "layer-2-workflow-hubs": {
        "purpose": "Run repeatable multi-step workflows and hand off to the right specialist or support skill.",
        "skills": [
            "brainstorm-hub",
            "scout-hub",
            "plan-hub",
            "debug-hub",
            "fix-hub",
            "test-hub",
            "review-hub",
        ],
    },
    "layer-3-utility-providers": {
        "purpose": "Stateless capabilities and analysis helpers. These should be called by hubs when present rather than acting as top-level entrypoints.",
        "skills": [
            "research-expert",
            "docs-seeker",
            "sequential-thinking",
            "problem-solving",
            "ai-multimodal",
            "chrome-devtools",
            "repomix",
            "context-engineering",
            "mermaidjs-v11",
            "ui-ux-pro-max",
            "media-processing",
        ],
    },
    "layer-4-specialists-and-standalones": {
        "purpose": "Role specialists and native support skills that actually produce architecture, stories, code, and quality evidence.",
        "skills": [
            "analyst",
            "pm",
            "architect",
            "scrum-master",
            "developer",
            "qa-governor",
            "agentic-loop",
            "project-architecture",
            "dependency-management",
            "api-integration",
            "data-persistence",
            "testing-patterns",
        ],
    },
}


HUB_MESH: Dict[str, List[str]] = {
    "brainstorm-hub": ["plan-hub", "workflow-router"],
    "scout-hub": ["plan-hub", "debug-hub", "review-hub", "workflow-router"],
    "plan-hub": ["brainstorm-hub", "scout-hub", "fix-hub", "review-hub", "workflow-router"],
    "debug-hub": ["fix-hub", "test-hub", "scout-hub", "workflow-router"],
    "fix-hub": ["debug-hub", "test-hub", "review-hub", "workflow-router"],
    "test-hub": ["debug-hub", "fix-hub", "review-hub", "workflow-router"],
    "review-hub": ["plan-hub", "debug-hub", "fix-hub", "test-hub", "workflow-router"],
}


ORCHESTRATOR_RULES = {
    "bootstrap": "Initialize state, detect missing contracts, and prepare the repo for a new line of work.",
    "team": "Coordinate multiple lanes, avoid overlap, and keep shared artifacts authoritative.",
    "cook": "Run the day-to-day loop for one request by selecting the right hub and checking completion gates.",
    "workflow-router": "Act as the routing kernel that chooses the track, specialist, and escalation path.",
}


PARALLEL_LANE_RULES = [
    "Never let two lanes edit the same artifact section without an explicit merge order.",
    "Shared artifacts win over chat memory; update the artifact before handing off.",
    "If a lane discovers architecture or scope drift, it must update workflow-state and notify team immediately.",
    "Use scout-hub before parallelizing into unfamiliar parts of the codebase.",
]


HUB_SUPPORT_MAP = {
    "brainstorm-hub": ["analyst", "pm", "research-expert", "ui-ux-pro-max"],
    "scout-hub": [
        "project-architecture",
        "dependency-management",
        "api-integration",
        "data-persistence",
        "testing-patterns",
        "docs-seeker",
        "repomix",
        "context-engineering",
    ],
    "plan-hub": ["analyst", "pm", "architect", "scrum-master", "research-expert", "ui-ux-pro-max"],
    "debug-hub": ["developer", "testing-patterns", "systematic-debugging", "problem-solving", "sequential-thinking", "chrome-devtools"],
    "fix-hub": ["developer", "agentic-loop", "project-architecture", "api-integration", "data-persistence", "refactoring-expert"],
    "test-hub": ["qa-governor", "testing-patterns", "agentic-loop", "systematic-debugging"],
    "review-hub": ["qa-governor", "testing-patterns", "code-review", "project-architecture"],
}



def render_layer_model() -> str:
    lines = [
        "# layer-model",
        "",
        "This repo now follows a 4-layer hub-and-spoke topology so orchestration and execution are separate concerns.",
        "",
    ]
    for layer_name, meta in LAYER_MODEL.items():
        lines.append(f"## {layer_name}")
        lines.append(str(meta["purpose"]))
        lines.append("")
        for skill in meta["skills"]:
            lines.append(f"- {skill}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"



def render_hub_mesh() -> str:
    lines = [
        "# hub-mesh",
        "",
        "Workflow hubs are allowed to call across the mesh when the current lane hits ambiguity, risk, or missing evidence.",
        "",
        "## Cross-hub references",
        "",
    ]
    for hub, neighbors in HUB_MESH.items():
        lines.append(f"### {hub}")
        lines.append("Can hand off to:")
        for neighbor in neighbors:
            lines.append(f"- {neighbor}")
        lines.append("")

    lines.append("## Recommended support map")
    lines.append("")
    for hub, supports in HUB_SUPPORT_MAP.items():
        lines.append(f"### {hub}")
        for support in supports:
            lines.append(f"- {support}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"



def render_orchestrator_rules() -> str:
    lines = [
        "# orchestrator-rules",
        "",
        "Layer-1 orchestrators own coordination, not implementation.",
        "",
    ]
    for name, rule in ORCHESTRATOR_RULES.items():
        lines.append(f"## {name}")
        lines.append(rule)
        lines.append("")

    lines.append("## Parallel lane rules")
    lines.append("")
    for rule in PARALLEL_LANE_RULES:
        lines.append(f"- {rule}")
    lines.append("")
    return "\n".join(lines).rstrip() + "\n"



def render_round3_changelog() -> str:
    return dedent(
        """\
        # round3-changelog

        Round 3 tightens orchestration around the 4-layer model:

        - adds layer-1 orchestrators: `bootstrap`, `team`, `cook`
        - adds layer-2 workflow hubs: `brainstorm-hub`, `scout-hub`, `plan-hub`, `debug-hub`, `fix-hub`, `test-hub`, `review-hub`
        - adds an explicit `developer` specialist so execution has a first-class handoff target
        - upgrades workflow-state to record orchestrator, hub, lane, and active specialist
        - adds `team-board.md` and `investigation-notes.md` so multi-lane and debugging work have stable artifacts
        - keeps round2 bundle behavior intact while adding new round3 bundles
        """
    )
