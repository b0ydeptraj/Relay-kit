from __future__ import annotations

from textwrap import dedent


TRACKS = {
    "quick-flow": {
        "levels": ["L0", "L1"],
        "use_for": "Small, well-bounded work with tight scope and low coordination overhead.",
        "artifacts": ["tech-spec", "investigation-notes", "qa-report"],
        "flow": ["workflow-router", "cook", "debug-hub", "fix-hub", "test-hub", "qa-governor"],
    },
    "product-flow": {
        "levels": ["L2", "L3"],
        "use_for": "Features, products, or platform work that need requirements, architecture, and story slicing.",
        "artifacts": ["product-brief", "prd", "architecture", "epics", "story", "qa-report"],
        "flow": ["workflow-router", "cook", "plan-hub", "architect", "scrum-master", "developer", "qa-governor"],
    },
    "enterprise-flow": {
        "levels": ["L4"],
        "use_for": "High-risk, compliance-sensitive, multi-tenant, or multi-team changes.",
        "artifacts": ["product-brief", "prd", "architecture", "epics", "story", "qa-report", "team-board"],
        "flow": ["bootstrap", "team", "workflow-router", "cook", "plan-hub", "architect", "scrum-master", "developer", "qa-governor"],
    },
}

COMPLEXITY_LADDER = {
    "L0": "Single bug or tiny refactor in a well-understood area. One module, one behavior, low ambiguity.",
    "L1": "Small feature or bug cluster. A few files, straightforward constraints, low architectural risk.",
    "L2": "Feature slice touching multiple components. Requires acceptance criteria and design alignment.",
    "L3": "Product or platform change with meaningful architectural trade-offs and rollout considerations.",
    "L4": "Enterprise-grade work with compliance, scale, security, migration, or cross-team coordination needs.",
}


def render_workflow_state() -> str:
    return dedent(
        """\
        # workflow-state

        ## Current request
        TBD

        ## Active lane
        - Lane id: primary
        - Mode: serial or parallel TBD

        ## Active orchestration
        - Layer-1 orchestrator: TBD
        - Layer-2 workflow hub: TBD
        - Active specialist: TBD

        ## Complexity level
        - Level: TBD
        - Reasoning: TBD

        ## Chosen track
        - Track: TBD
        - Why this track fits: TBD

        ## Completed artifacts
        - [ ] product-brief
        - [ ] PRD
        - [ ] architecture
        - [ ] epics
        - [ ] story
        - [ ] tech-spec
        - [ ] investigation-notes
        - [ ] qa-report
        - [ ] team-board

        ## Next skill
        TBD

        ## Known blockers
        TBD

        ## Escalation triggers noticed
        TBD

        ## Notes
        TBD
        """
    )



def render_team_board() -> str:
    return dedent(
        """\
        # team-board

        ## Shared objective
        TBD

        ## Active orchestrator
        - team

        ## Lanes
        | Lane | Owner skill | Current artifact | Status | Notes |
        |---|---|---|---|---|
        | primary | TBD | TBD | queued | TBD |
        | lane-2 | TBD | TBD | parked | TBD |
        | lane-3 | TBD | TBD | parked | TBD |

        ## Shared artifacts that must stay authoritative
        - `.ai-kit/state/workflow-state.md`
        - `.ai-kit/contracts/project-context.md`
        - `.ai-kit/contracts/PRD.md`
        - `.ai-kit/contracts/architecture.md`

        ## Merge order
        TBD

        ## Conflict risks
        TBD

        ## Decision log
        TBD
        """
    )
