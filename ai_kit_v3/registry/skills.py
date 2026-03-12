from __future__ import annotations

from dataclasses import dataclass
from textwrap import dedent
from typing import Dict, List


@dataclass(frozen=True)
class SkillSpec:
    name: str
    description: str
    role: str
    inputs: List[str]
    outputs: List[str]
    references: List[str]
    next_steps: List[str]
    body: str


LEGACY_ROLE_MAP = {
    "analyst": [
        "research-expert",
        "problem-solving",
        "sequential-thinking",
        "utilities",
    ],
    "pm": [
        "ui-ux-pro-max",
        "research-expert",
        "code-review",
    ],
    "architect": [
        "project-architecture",
        "dependency-management",
        "api-integration",
        "data-persistence",
        "async-patterns",
        "security-patterns",
        "performance-optimization",
        "logging-observability",
    ],
    "developer": [
        "project-architecture",
        "dependency-management",
        "api-integration",
        "data-persistence",
        "agentic-loop",
        "testing-patterns",
        "systematic-debugging",
        "refactoring-expert",
        "code-review",
    ],
    "qa-governor": [
        "dependency-management",
        "api-integration",
        "data-persistence",
        "testing-patterns",
        "systematic-debugging",
        "code-review",
    ],
}


CORE_SKILLS: Dict[str, SkillSpec] = {
    "workflow-router": SkillSpec(
        name="workflow-router",
        description="route a request through the right delivery track, choose the next skill, and keep workflow-state current. use when a request arrives, the user asks what to do next, or scope or complexity is unclear.",
        role="orchestrator",
        inputs=["user request", ".ai-kit/contracts/project-context.md (if present)", ".ai-kit/state/workflow-state.md (if present)"],
        outputs=[".ai-kit/state/workflow-state.md", ".ai-kit/contracts/tech-spec.md or product-brief.md kickoff"],
        references=[
            "Use legacy support skills by role when specialized analysis is required.",
            "Prefer existing project-context over assumptions.",
            "Escalate from quick-flow to product-flow whenever hidden complexity appears.",
        ],
        next_steps=["analyst", "pm", "architect", "scrum-master", "developer", "qa-governor"],
        body=dedent(
            """\
            # Mission
            Decide how the request should move through the system and make the next step explicit.

            ## Mandatory routing procedure
            1. Read `.ai-kit/contracts/project-context.md` if it exists.
            2. Score the request on five axes: ambiguity, breadth of change, architecture risk, operational risk, and coordination cost.
            3. Classify complexity:
               - `L0`: single bug or tiny refactor
               - `L1`: small feature or bug cluster
               - `L2`: multi-component feature slice
               - `L3`: product or platform change with design trade-offs
               - `L4`: enterprise, compliance, or scale-sensitive work
            4. Choose track:
               - `L0-L1` -> quick-flow
               - `L2-L3` -> product-flow
               - `L4` -> enterprise-flow
            5. Update `.ai-kit/state/workflow-state.md` with:
               - chosen complexity level and why
               - chosen track and why
               - artifacts already available
               - exact next skill to invoke
               - blockers or open questions
            6. If quick-flow is selected, ensure `.ai-kit/contracts/tech-spec.md` exists before implementation begins.
            7. If product-flow or enterprise-flow is selected, start with `analyst` unless a recent `product-brief.md` already exists and is still valid.

            ## Escalation rules
            Escalate to the next track immediately when any of the following appears:
            - The change touches multiple bounded contexts.
            - Acceptance criteria are unclear or disputed.
            - Security, migration, or rollout risk appears.
            - A small fix now changes contracts, schemas, APIs, or infrastructure.

            ## Output contract
            Never end with vague advice. Always name the next skill, the artifact it should create or update, and what evidence is still missing.
            """
        ).strip(),
    ),
    "analyst": SkillSpec(
        name="analyst",
        description="clarify product intent, assumptions, users, and open questions; produce a product brief for work that is not already fully scoped. use when discovery is needed before writing a prd or choosing architecture.",
        role="analysis",
        inputs=["user request", ".ai-kit/contracts/project-context.md", ".ai-kit/state/workflow-state.md"],
        outputs=[".ai-kit/contracts/product-brief.md"],
        references=[
            "Lean on research-expert, problem-solving, and sequential-thinking when the scope is fuzzy.",
            "Keep the brief short enough that downstream roles can actually use it.",
        ],
        next_steps=["pm", "workflow-router"],
        body=dedent(
            """\
            # Mission
            Turn an idea, problem report, or vague request into a brief that downstream roles can reason from.

            ## Produce `product-brief.md`
            Cover these sections:
            - problem statement
            - target users and jobs-to-be-done
            - desired outcomes and success signals
            - assumptions and unknowns
            - constraints and non-goals
            - open questions

            ## Guardrails
            - Prefer validated facts over storytelling.
            - Call out what is unknown instead of silently guessing.
            - If the request is already well-scoped and `workflow-router` selected quick-flow, do not force a brief.
            - If a fresh brief already exists, update only the parts affected by the new request.

            ## Handoff
            End by stating whether the brief is ready for `pm`, or exactly what question still blocks planning.
            """
        ).strip(),
    ),
    "pm": SkillSpec(
        name="pm",
        description="translate a product brief or scoped request into a prd, release slices, and acceptance criteria. use when the work is past discovery and needs a buildable scope.",
        role="planning",
        inputs=[".ai-kit/contracts/product-brief.md or direct scoped request", ".ai-kit/contracts/project-context.md"],
        outputs=[".ai-kit/contracts/PRD.md", ".ai-kit/contracts/epics.md"],
        references=[
            "Do not hand wave acceptance criteria.",
            "Separate must-have requirements from stretch goals and out-of-scope ideas.",
            "Use UX and research support skills when the user experience is part of the risk.",
        ],
        next_steps=["architect", "scrum-master", "workflow-router"],
        body=dedent(
            """\
            # Mission
            Create a buildable plan, not a wish list.

            ## Produce `PRD.md`
            Include:
            - objective and scope
            - functional requirements
            - non-functional requirements
            - out of scope
            - acceptance criteria
            - risks and mitigations
            - release slices

            ## Produce `epics.md`
            Organize the PRD into thin vertical slices with an order that reduces risk early.

            ## Readiness gate
            The PRD is not ready if any of the following is missing:
            - unambiguous acceptance criteria
            - named risks for hard or irreversible changes
            - explicit out-of-scope section
            - at least one suggested slice order

            ## Handoff
            Tell `architect` what constraints matter most and tell `scrum-master` which epic should be cut first.
            """
        ).strip(),
    ),
    "architect": SkillSpec(
        name="architect",
        description="convert requirements into an implementation-ready architecture that fits the existing codebase. use when a prd exists or when a change could alter module boundaries, data flow, security, or operations.",
        role="solutioning",
        inputs=[".ai-kit/contracts/PRD.md", ".ai-kit/contracts/project-context.md", "existing support skills and references"],
        outputs=[".ai-kit/contracts/architecture.md"],
        references=[
            "Mirror the existing codebase before inventing new patterns.",
            "Pull in project-architecture, dependency-management, api-integration, data-persistence, security-patterns, performance-optimization, and logging-observability when relevant.",
            "Architecture must include a readiness verdict, not just diagrams or aspirations.",
        ],
        next_steps=["scrum-master", "qa-governor", "workflow-router"],
        body=dedent(
            """\
            # Mission
            Make downstream implementation safer by turning requirements into explicit technical constraints and decisions.

            ## Produce `architecture.md`
            Include:
            - current-system constraints
            - proposed design
            - module boundaries
            - data flow and integrations
            - operational concerns
            - trade-offs and ADR notes
            - implementation readiness verdict

            ## Mandatory behavior
            - Reuse existing patterns unless there is a documented reason not to.
            - Name interfaces, boundaries, and ownership explicitly.
            - State how observability, rollback, and failure handling will work for risky changes.
            - Flag any requirement that cannot be satisfied within the current architecture without upstream scope negotiation.

            ## Readiness gate
            Mark the design blocked when schemas, APIs, migrations, or cross-service contracts are still ambiguous.
            """
        ).strip(),
    ),
    "scrum-master": SkillSpec(
        name="scrum-master",
        description="turn prd and architecture into implementation-ready stories or a tech spec for quick-flow work. use when planning is done and work must be sliced into safe, verifiable increments.",
        role="delivery",
        inputs=[".ai-kit/contracts/PRD.md", ".ai-kit/contracts/architecture.md", ".ai-kit/contracts/epics.md", ".ai-kit/contracts/tech-spec.md"],
        outputs=[".ai-kit/contracts/stories/story-xxx.md", ".ai-kit/contracts/tech-spec.md when quick-flow is used"],
        references=[
            "Each story should be a thin vertical slice with explicit done criteria.",
            "Do not create stories that hide architectural decisions or missing acceptance criteria.",
        ],
        next_steps=["developer", "qa-governor", "workflow-router"],
        body=dedent(
            """\
            # Mission
            Cut work into execution units that a developer can complete without re-opening product or architecture debates.

            ## For quick-flow
            Create or refine `.ai-kit/contracts/tech-spec.md` with:
            - change summary
            - root cause or context
            - files likely affected
            - implementation notes
            - verification steps

            ## For product-flow or enterprise-flow
            Create story files under `.ai-kit/contracts/stories/`.
            Each story must include:
            - story statement
            - acceptance criteria
            - implementation notes
            - test notes
            - risks
            - done checklist

            ## Story quality bar
            - Small enough to verify in one focused implementation pass.
            - Large enough to deliver user-visible progress.
            - Explicit about what must be tested.
            - Explicit about which upstream documents it depends on.
            """
        ).strip(),
    ),
    "qa-governor": SkillSpec(
        name="qa-governor",
        description="check readiness and completion against acceptance criteria, risk, and regression scope; write a qa report before completion is claimed. use before saying work is done or when implementation confidence is low.",
        role="quality",
        inputs=["PRD or tech-spec", "architecture or story", "evidence from tests and reviews"],
        outputs=[".ai-kit/contracts/qa-report.md"],
        references=[
            "Use testing-patterns, systematic-debugging, and code-review as support skills.",
            "Coverage must be explained against acceptance criteria and risk, not just number of tests.",
        ],
        next_steps=["developer", "workflow-router"],
        body=dedent(
            """\
            # Mission
            Prevent premature completion claims and surface residual risk clearly.

            ## Produce `qa-report.md`
            Include:
            - scope checked
            - acceptance coverage
            - risk matrix
            - regression surface
            - evidence collected
            - go or no-go recommendation

            ## Mandatory checks
            - Compare actual evidence to acceptance criteria, not just implementation intent.
            - Name the regression surface explicitly.
            - Call out missing tests, weak evidence, or unverified assumptions.
            - Bounce work back when story, tech-spec, or architecture is still underspecified.
            """
        ).strip(),
    ),
}


CLEANUP_SKILLS: Dict[str, SkillSpec] = {
    "agentic-loop": SkillSpec(
        name="agentic-loop",
        description="self-correcting development loop for implementation work. use when building or fixing code iteratively and require evidence before claiming completion.",
        role="developer-support",
        inputs=["story or tech-spec", "project-context", "relevant support skills"],
        outputs=["working code plus test evidence"],
        references=[
            "testing-patterns",
            "systematic-debugging",
            "code-review",
        ],
        next_steps=["qa-governor"],
        body=dedent(
            """\
            # Mission
            Execute implementation work in a tight loop without resorting to random fixes.

            ## The loop
            1. Understand the story or tech-spec completely.
            2. Make the smallest viable code change toward the goal.
            3. Run the relevant checks or tests.
            4. Analyze the result.
            5. If it failed, debug root cause before changing anything else.
            6. If it passed, collect evidence and hand off to QA.

            ## Non-negotiable rules
            - No quick fixes without root-cause reasoning.
            - No stacking multiple unrelated changes in one test cycle.
            - Write or update a failing test whenever the change fixes a bug.
            - Do not say done without fresh evidence from commands actually run.

            ## Failure protocol
            After three failed fix attempts, stop and question the story, architecture, or assumptions instead of thrashing.
            """
        ).strip(),
    ),
}


NATIVE_SUPPORT_SKILLS: Dict[str, SkillSpec] = {
    "project-architecture": SkillSpec(
        name="project-architecture",
        description="analyze the current codebase shape and maintain a living architecture reference. use before designing a change, reviewing architectural drift, or implementing code in an unfamiliar area.",
        role="architecture-support",
        inputs=["repository tree", ".ai-kit/contracts/project-context.md", ".ai-kit/contracts/architecture.md when available"],
        outputs=[".ai-kit/references/project-architecture.md"],
        references=[
            "Document what the codebase actually does today, not what the team intended six months ago.",
            "Include concrete file paths, entrypoints, and dependency direction.",
        ],
        next_steps=["architect", "developer", "code-review"],
        body=dedent(
            """\
            # Mission
            Build and maintain an accurate map of the current architecture so downstream roles stop guessing.

            ## Produce `.ai-kit/references/project-architecture.md`
            Cover:
            - entry points and execution flow
            - layer or package structure
            - module responsibilities
            - dependency direction and boundaries
            - architecture drift and hotspots
            - files to mirror when adding new work

            ## Working rules
            - Prefer observed runtime or code flow over folder names alone.
            - Name boundaries explicitly: controllers, services, repositories, adapters, domain logic, jobs, or scripts.
            - Flag any mismatch between the intended architecture and what the code actually does.
            - Add file paths whenever the reference names a pattern or module.
            """
        ).strip(),
    ),
    "dependency-management": SkillSpec(
        name="dependency-management",
        description="capture dependency policy, lockfile usage, environment setup, and safe add or upgrade rules. use before adding packages, updating libraries, or diagnosing environment drift.",
        role="build-support",
        inputs=["package metadata files", "lockfiles", "toolchain config", "CI setup if present"],
        outputs=[".ai-kit/references/dependency-management.md"],
        references=[
            "Record both the official package manager and what contributors actually use day to day.",
            "Make transitive risk and pinning policy explicit.",
        ],
        next_steps=["architect", "developer", "qa-governor"],
        body=dedent(
            """\
            # Mission
            Prevent dependency changes from becoming hidden architecture or release risk.

            ## Produce `.ai-kit/references/dependency-management.md`
            Cover:
            - package manager and lockfiles
            - environment and toolchain setup
            - version pinning and upgrade policy
            - dev vs prod dependencies
            - how to add a new dependency
            - known dependency risks

            ## Working rules
            - Name the exact files that define dependencies.
            - Note whether the team uses strict pinning, ranges, extras, or split requirement sets.
            - Explain how contributors should add, upgrade, and verify dependencies without drifting from CI.
            - Flag packages that are security-sensitive, hard to upgrade, or tightly coupled to runtime behavior.
            """
        ).strip(),
    ),
    "api-integration": SkillSpec(
        name="api-integration",
        description="document external service integration patterns, clients, auth, retries, and error handling. use when building or changing API clients, webhooks, endpoints, or network-facing code.",
        role="integration-support",
        inputs=["HTTP or RPC client code", "settings or secret config", "test or mock code"],
        outputs=[".ai-kit/references/api-integration.md"],
        references=[
            "Prefer concrete service names, client classes, and endpoint groups over generic summaries.",
            "Make retries, timeouts, idempotency, and error translation explicit.",
        ],
        next_steps=["architect", "developer", "qa-governor"],
        body=dedent(
            """\
            # Mission
            Make network-facing behavior predictable so changes to API code do not become reliability surprises.

            ## Produce `.ai-kit/references/api-integration.md`
            Cover:
            - clients, transports, and endpoints
            - authentication and secret handling
            - retry, timeout, and idempotency rules
            - request and response patterns
            - error mapping and recovery
            - testing and mocking approach

            ## Working rules
            - Name client wrappers, service classes, or endpoint modules directly.
            - Include where auth is injected and how secrets are sourced.
            - Explain how the code handles network failures, partial failures, and upstream rate limits.
            - Note what should be mocked versus tested against a real service.
            """
        ).strip(),
    ),
    "data-persistence": SkillSpec(
        name="data-persistence",
        description="document storage topology, models, migrations, caching, and consistency rules. use when touching schemas, repositories, transactions, caches, or data flows.",
        role="persistence-support",
        inputs=["model files", "repository or DAO code", "migration files", "cache config if present"],
        outputs=[".ai-kit/references/data-persistence.md"],
        references=[
            "Cover both primary storage and auxiliary state like caches, queues, or object stores when relevant.",
            "Document rollback and migration risks, not only happy-path structure.",
        ],
        next_steps=["architect", "developer", "qa-governor"],
        body=dedent(
            """\
            # Mission
            Make data changes safer by documenting where state lives, how it moves, and what can go wrong.

            ## Produce `.ai-kit/references/data-persistence.md`
            Cover:
            - stores and connection points
            - schemas, models, and repositories
            - migrations and schema evolution
            - transactions and consistency
            - caching and invalidation
            - data risks and rollback notes

            ## Working rules
            - Name concrete stores and frameworks: Postgres, Redis, SQLite, MongoDB, ORM, query builder, and so on.
            - Explain who owns writes, reads, cache invalidation, and transaction boundaries.
            - Flag destructive migrations, data backfills, and dual-write or consistency hazards.
            - Include file paths for models, repositories, migrations, and seed logic when they exist.
            """
        ).strip(),
    ),
    "testing-patterns": SkillSpec(
        name="testing-patterns",
        description="capture how the project tests code, mocks dependencies, and gathers evidence. use when adding tests, updating fixtures, validating regressions, or deciding what proof is enough.",
        role="quality-support",
        inputs=["test folders", "test config", "fixtures or factories", "CI or local test commands"],
        outputs=[".ai-kit/references/testing-patterns.md"],
        references=[
            "Explain how to produce evidence locally, not only what frameworks exist.",
            "Map tests to risk areas and brittle zones where regressions cluster.",
        ],
        next_steps=["developer", "qa-governor", "code-review"],
        body=dedent(
            """\
            # Mission
            Turn the project test suite into a usable playbook for implementation and quality review.

            ## Produce `.ai-kit/references/testing-patterns.md`
            Cover:
            - frameworks and folder rules
            - fixture and factory patterns
            - mocking and dependency isolation
            - async or integration testing rules
            - commands for local evidence
            - coverage gaps and brittle areas

            ## Working rules
            - Name the real commands contributors should run for fast confidence versus deeper verification.
            - Show where fixtures, factories, and mocks live and when each should be preferred.
            - Call out unstable tests, heavy integration paths, and areas with weak coverage.
            - Tie recommendations back to risk, not just test quantity.
            """
        ).strip(),
    ),
}


def render_skill(spec: SkillSpec) -> str:
    parts = [
        "---",
        f"name: {spec.name}",
        f"description: {spec.description}",
        "---",
        "",
        spec.body.strip(),
        "",
        "## Inputs",
    ]
    parts.extend(f"- {item}" for item in spec.inputs)
    parts.extend([
        "",
        "## Outputs",
    ])
    parts.extend(f"- {item}" for item in spec.outputs)
    parts.extend([
        "",
        "## Reference skills and rules",
    ])
    parts.extend(f"- {item}" for item in spec.references)
    parts.extend([
        "",
        "## Likely next step",
    ])
    parts.extend(f"- {item}" for item in spec.next_steps)
    return "\n".join(parts).rstrip() + "\n"
