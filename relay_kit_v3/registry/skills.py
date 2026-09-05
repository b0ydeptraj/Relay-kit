from __future__ import annotations

from dataclasses import dataclass, replace
from textwrap import dedent
from typing import Dict, List


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
    paths: List[str] | None = None
    context: str | None = None
    allowed_tools: List[str] | None = None
    effort: str | None = None


READ_ANALYZE_TOOLS = ["Read", "Grep", "Glob", "Bash"]
EDIT_AND_TEST_TOOLS = ["Read", "Write", "Edit", "Grep", "Glob", "Bash"]


def domain_resource_references(skill_name: str) -> list[str]:
    return [
        f"Open `references/{skill_name}-operator-contract.md` when scope, evidence, or operator safety is unclear.",
        f"Use `examples/{skill_name}-good-output.md` and `examples/{skill_name}-bad-output.md` to calibrate output quality.",
        f"Use `evals/{skill_name}-cases.json` as the minimum scenario set for behavior regression checks.",
        f"Use `competencies/{skill_name}-competencies.json` to check covered competencies, failure traps, and unknown-domain policy.",
    ]


LEGACY_ROLE_MAP = {
    "analyst": [
        "research-expert",
        "problem-solving",
        "sequential-thinking",
        "utilities",
    ],
    "pm": [
        "ux-structure",
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
        "execution-loop",
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


ORCHESTRATOR_SKILLS: Dict[str, SkillSpec] = {
    "workflow-router": SkillSpec(
        name="workflow-router",
        description="Use when a request arrives, the user asks what to do next, or scope or complexity is unclear. Route a request through the right delivery track, choose the active orchestrator or hub, keep workflow-state current, and turn short or ambiguous prompts into file-aware working guidance.",
        role="routing-kernel",
        layer="layer-1-orchestrators",
        inputs=["user request", "short or ambiguous user prompt", ".relay-kit/contracts/project-context.md (if present)", ".relay-kit/state/workflow-state.md (if present)"],
        outputs=[".relay-kit/state/workflow-state.md", "prompt enhancement summary when the user request is short or unclear", ".relay-kit/contracts/tech-spec.md or product-brief.md kickoff"],
        references=[
            "Prefer existing project-context over assumptions.",
            "For short prompts, expand intent into recommended skill, read-first context, required evidence, and an ask-or-act decision.",
            "When `.relay-kit/context/index.json` exists, use local context graph hits before broad repo scans.",
            "Prompt enhancement is not a semantic context engine, expert guarantee, or production-readiness claim.",
            "Escalate from quick-flow to product-flow whenever hidden complexity appears.",
            "Hand off to bootstrap when base artifacts are missing and to cook for the single active request.",
            "If session continuity is weak, run context-continuity checkpoint or rehydrate before routing deeper work.",
            "For existing codebases, prefer scout-hub plus repo-map before planning when dependency boundaries are still unclear.",
        ],
        next_steps=[
            "bootstrap",
            "cook",
            "context-continuity",
            "scout-hub",
            "plan-hub",
            "debug-hub",
            "token-economy",
            "scope-discipline",
            # Offensive lanes must enter through the authorization gate, never
            # by matching a specialist description directly.
            "offensive-security-engagement",
                    "mmo-authorization-gate",
        ],
        body=dedent(
            """\
            # Mission
            Act as the routing kernel for the whole system: choose the track, choose the active lane, and make the next move explicit.

            ## Prompt enhancement posture
            When the user gives a short, vague, or compressed request, do not pretend the skill makes the model an expert. Treat the skill as a context-aware prompt enhancer:
            - infer the likely work type from the request shape
            - name the recommended skill and why
            - name the files, state, logs, or artifacts to read first
            - name the evidence required before coding, answering, or claiming done
            - choose whether to act, scout first, or ask exactly one high-value clarification
            If `.relay-kit/context/index.json` exists, treat graph hits as candidate files to inspect first. If it is missing, continue with normal repo reading; do not block the user just because the index has not been built.

            ## Mandatory routing procedure
            1. Read `.relay-kit/contracts/project-context.md` and `.relay-kit/state/workflow-state.md` if they exist.
            2. Score the request on six axes: ambiguity, breadth of change, architecture risk, operational risk, coordination cost, and authorization_risk (presence of offensive/red-team/evasion/injection/stealth/C2 keywords or explicit red-team scope).
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
               - `authorization_risk >= medium` -> offensive-flow (call `offensive-security-engagement` as first L3 utility before picking specialist)
            5. Choose the layer-1 entrypoint:
               - use `bootstrap` if state, context, or artifacts are missing
               - use `cook` for one active request in one lane
               - use `cook` for the single active lane; keep work sequential under one Sol context
            6. Choose the first layer-2 hub:
               - `scout-hub` when the codebase area is unclear
               - `plan-hub` when planning artifacts are missing or stale
               - `debug-hub` when the request starts from a failure or regression
            7. Mark the lane mode explicitly as one of: discovery, planning, implementation, verification, or offensive.
            8. Update `.relay-kit/state/workflow-state.md` with the chosen track, orchestrator, hub, exact next skill, and any blockers.

            ## Escalation rules
            Escalate immediately when:
            - a small fix changes contracts, schemas, APIs, or infrastructure
            - acceptance criteria are unclear or disputed
            - multiple bounded contexts are touched
            - rollout, migration, security, or compliance risk appears

            ## Output contract
            Never end with vague advice. Always name the next skill, the artifact it should create or update, and what evidence is still missing.
            """
        ).strip(),
    ),
    "bootstrap": SkillSpec(
        name="bootstrap",
        description="Use when starting a repo lane, after major structure changes, or whenever workflow-state or project-context is missing or stale. Initialize or refresh the shared Relay-kit runtime before a new lane begins.",
        role="session-bootstrap",
        layer="layer-1-orchestrators",
        inputs=["repo root", ".relay-kit/ runtime folders if present", "current request"],
        outputs=[".relay-kit/state/workflow-state.md", ".relay-kit/contracts/project-context.md"],
        references=[
            "Prefer lightweight initialization over speculative planning.",
            "If the codebase is unfamiliar, route immediately to scout-hub after bootstrapping.",
            "Do not invent project-context facts; mark unknowns and hand off to scout-hub.",
            "Use context-continuity rehydrate when resuming across thread or session boundaries.",
        ],
        next_steps=["workflow-router", "scout-hub", "cook", "context-continuity"],
        body=dedent(
            """\
            # Mission
            Prepare the runtime so later steps have an authoritative baseline instead of relying on chat memory.

            ## Mandatory setup
            1. Ensure `.relay-kit/state/workflow-state.md` exists and records the current request.
            2. Ensure `.relay-kit/contracts/project-context.md` exists. If facts are missing, create a skeletal version with explicit unknowns.
            3. Keep the active work in one sequential lane under the primary Sol context.
            4. Record which artifacts already exist and which ones must be refreshed.
            5. If the repo area is not well understood, route next to `scout-hub`.

            ## Guardrails
            - Bootstrap does not do deep planning.
            - Bootstrap does not declare work ready; it only makes later work safer.
            - When in doubt, prefer creating the minimal state needed to hand off cleanly.
            """
        ).strip(),
    ),
    "cook": SkillSpec(
        name="cook",
        description="Use when one active request already has routing and state, and needs the next solid handoff. Drive that request forward with the right hub or specialist.",
        role="lane-conductor",
        layer="layer-1-orchestrators",
        inputs=[".relay-kit/state/workflow-state.md", "current request or lane objective", "available artifacts"],
        outputs=["updated workflow-state", "a named next hub or specialist", "refreshed artifacts produced by the chosen lane"],
        references=[
            "Cook does not replace hubs; it chooses and sequences them.",
            "Keep each pass small: one hub, one artifact decision, one clear next handoff.",
            "If completion is claimed, force test-hub or review-hub before accepting it.",
            "If the lane is pausing or switching owners, trigger context-continuity checkpoint before handoff.",
        ],
        next_steps=["brainstorm-hub", "scout-hub", "plan-hub", "debug-hub", "fix-hub", "test-hub", "review-hub", "context-continuity"],
        body=dedent(
            """\
            # Mission
            Run the day-to-day loop for one request without letting it skip gates or get stuck in vague next steps.

            ## Mandatory loop
            1. Read workflow-state and identify the lane's current objective.
            2. Choose exactly one hub that should move the work forward now.
            3. Name the artifact that hub must create, update, or validate.
            4. After the hub finishes, update workflow-state with what changed and which hub or specialist comes next.
            5. Stop as soon as the next handoff is explicit.

            ## Safety rules
            - Never jump straight from vague intent to implementation.
            - When evidence is weak, prefer scout-hub, debug-hub, or test-hub over optimistic implementation.
            - When scope shifts, send the lane back through workflow-router.
            - When `workflow-state.engagement_proof` exists or the lane mode is `offensive`, call `offensive-security-engagement` as the first utility before picking any specialist.
            """
        ).strip(),
    ),
}


WORKFLOW_HUB_SKILLS: Dict[str, SkillSpec] = {
    "brainstorm-hub": SkillSpec(
        name="brainstorm-hub",
        description="Use when the request is still an idea, an opportunity, or a loosely described improvement. Guide early ideation and rough problem framing before formal planning exists.",
        role="ideation-hub",
        layer="layer-2-workflow-hubs",
        inputs=["user idea or opportunity", ".relay-kit/state/workflow-state.md", "any existing brief or context"],
        outputs=[".relay-kit/contracts/product-brief.md or a decision not to proceed"],
        references=[
            "Use analyst for structured discovery and pm only once the shape is coherent enough to plan.",
            "Prefer narrowing the problem over generating a giant feature wish list.",
        ],
        next_steps=[
            "analyst",
            "research",
            "market-research",
            "growth-marketing",
            "vietnamese-product-localization",
            "pm",
            "plan-hub",
            "workflow-router",
        ],
        body=dedent(
            """\
            # Mission
            Turn fuzzy idea energy into a bounded discovery lane that planning can actually use.

            ## Mandatory routing
            1. Identify the decision the user is really trying to make.
            2. Use `research` only for the freshest evidence that changes that decision.
            3. Use `market-research` when ICP, pricing, competitor, or domain signal affects the direction.
            4. Use `growth-marketing` when the next artifact is positioning, funnel, campaign, or launch messaging.
            5. Use `vietnamese-product-localization` when the idea is for Vietnamese users or bilingual communication.
            6. Route to `pm` only after the opportunity has enough shape for requirements.

            ## Evidence contract
            - name the user segment, problem, success signal, and biggest unknown
            - separate source-backed facts from assumptions and guesses
            - include the smallest next artifact: product brief, market note, campaign note, or stop decision

            ## Failure modes
            Hold instead of proceeding when the output becomes a giant feature wish list, generic marketing copy, or unsourced opportunity claims.

            ## Exit conditions
            End with one of three outcomes: a brief ready for planning, a stop decision, or one exact question that blocks planning.
            """
        ).strip(),
    ),
    "scout-hub": SkillSpec(
        name="scout-hub",
        description="Use when the repo area is unfamiliar, stale, or likely to drift from existing assumptions. Reconnoiter the codebase and refresh living references before planning, debugging, or review work continues.",
        role="recon-hub",
        layer="layer-2-workflow-hubs",
        inputs=["repo tree and relevant files", ".relay-kit/contracts/project-context.md", ".relay-kit/state/workflow-state.md"],
        outputs=[".relay-kit/contracts/project-context.md", ".relay-kit/references/*.md as needed", ".relay-kit/contracts/investigation-notes.md when the work starts from a failure"],
        references=[
            "Use project-architecture, dependency-management, api-integration, data-persistence, and testing-patterns as living references.",
            "Prefer concrete file paths, commands, and entrypoints over summaries.",
            "When the problem starts from a failure, capture findings in investigation-notes.",
            "Run a freshness pass first: stale assumptions or stale artifacts should be called out explicitly before planning.",
        ],
        next_steps=[
            "repo-map",
            "doc-pointers",
            "memory-search",
            "project-architecture",
            "dependency-management",
            "plan-hub",
            "debug-hub",
            "review-hub",
            "workflow-router",
        ],
        body=dedent(
            """\
            # Mission
            Gather the minimum reliable context the next lane needs so nobody plans or fixes from a false mental model.

            ## Mandatory routing
            1. Use `repo-map` for entrypoints, ownership, dependency direction, and read-first files.
            2. Use `doc-pointers` for exact docs, anchors, and source fragments.
            3. Use `memory-search` for prior decisions, handoff breadcrumbs, or stale state checks.
            4. Use `project-architecture` when module boundaries or architecture drift matter.
            5. Use `dependency-management` when tooling, lockfiles, or dependency risk affects the lane.
            6. Offensive recon routing: when the codebase is binary, native, or mobile-focused, pull the matching analysis skill before planning:
               - Binary / PE / ELF / Mach-O -> `binary-reverse-methodology`
               - Malware samples / suspicious code -> `malware-analysis-workflows`
               - APK / IPA / mobile native -> `mobile-app-reverse`
               - C++ / Win32 / driver code -> `cpp-systems-engineering`, `windows-native-internals`
               - Web JS / WASM crypto -> `frontend-crypto-reverse`, `browser-fingerprint-engineering`
               - Network protocol unknown -> `protocol-fingerprint-spoofing`

            ## Evidence contract
            - cite concrete paths, commands, modules, or docs instead of broad summaries
            - mark freshness for every important source: current, stale, inferred, or missing
            - record unknowns that still block planning or debugging
            - start `investigation-notes.md` when the scout is attached to a failure

            ## Failure modes
            Hold if the output is a tree dump without ownership, a generic architecture summary, or a plan that skips stale evidence.

            ## Output contract
            Name what became clearer, what is still unknown, which sources may be stale, and which hub or specialist should use the refreshed context next.
            """
        ).strip(),
    ),
    "plan-hub": SkillSpec(
        name="plan-hub",
        description="Use when work is larger than quick-flow or when existing planning artifacts are stale or incomplete. Run the planning chain from brief to prd to architecture to stories without losing context between roles.",
        role="planning-hub",
        layer="layer-2-workflow-hubs",
        inputs=["workflow-state", "existing brief, prd, architecture, or epics if present", "project-context"],
        outputs=["product-brief, PRD, architecture, epics, and stories or tech-spec depending track"],
        references=[
            "Call only the roles needed to close the current planning gap.",
            "Use scout-hub first if the current codebase context is too weak to plan safely.",
            "Route to review-hub if artifacts disagree with one another.",
            "Use `.relay-kit/docs/planning-discipline.md` to keep plans artifact-first, bite-sized, and verification-aware.",
            "Lock key UX, API, and behavior assumptions before story slicing so implementation does not drift.",
        ],
        next_steps=[
            "analyst",
            "research",
            "problem-solving",
            "sequential-thinking",
            "impact-radar",
            "mermaid-diagrams",
            "pm",
            "architect",
            "go-service-engineering",
            "next-product-frontend",
            "frontend-design",
            "mmo-ecommerce-multichannel",
            "mmo-crypto-wallet-farming",
            "scrum-master",
            "developer",
            "review-hub",
                    "llm-app-engineering",
        ],
        body=dedent(
            """\
            # Mission
            Sequence the planning roles so the lane produces buildable artifacts instead of disconnected documents.

            ## Mandatory order
            - use `analyst` if the brief is missing or stale
            - use `pm` if requirements, acceptance criteria, or slice order are missing
            - use `architect` if technical boundaries or readiness are unclear
            - use `scrum-master` when work must be cut into stories or a quick spec

            ## Planning gate
            Stop and route to `review-hub` when product, architecture, and story artifacts disagree.
            Route to `developer` only when the active story or tech-spec is ready for implementation.

            ## Planning discipline
            - Prefer small, verifiable slices over broad task bundles.
            - Every story or quick spec should name what will prove it is done.
            - If the work spans unrelated subsystems, split the plan before implementation starts.
            - Include dependency metadata and the first verification command so execution stays bounded.
            - If slicing yields zero executable stories, block and escalate instead of declaring planning complete.
            """
        ).strip(),
    ),
    "debug-hub": SkillSpec(
        name="debug-hub",
        description="Use when work starts from a regression, flaky behavior, or an unexplained mismatch between expected and actual behavior. Triage failures, collect evidence, and decide whether the issue is a bug, a test problem, or a planning problem.",
        role="debug-hub",
        layer="layer-2-workflow-hubs",
        inputs=["failing behavior", "logs, traces, or test output", "workflow-state", "relevant references"],
        outputs=[".relay-kit/contracts/investigation-notes.md", ".relay-kit/contracts/tech-spec.md when a fix path is clear"],
        references=[
            "When discipline utilities are installed, use `root-cause-debugging` before touching code.",
            "Use testing-patterns and problem-solving to turn evidence into a fix path.",
            "Root cause beats guess-and-patch.",
            "Escalate to plan-hub if the 'bug' is actually an unclear requirement or architectural mismatch.",
        ],
        next_steps=[
            "root-cause-debugging",
            "problem-solving",
            "sequential-thinking",
            "memory-search",
            "runtime-doctor",
            "fix-hub",
            "test-hub",
            "plan-hub",
            "workflow-router",
                    "performance-optimization",
            "incident-response",
        ],
        body=dedent(
            """\
            # Mission
            Turn a symptom into evidence and a decision, not into random edits.

            ## Mandatory routing
            1. Use `root-cause-debugging` before proposing fixes for regressions or flaky behavior.
            2. Use `memory-search` when prior decisions or earlier failures may explain the mismatch.
            3. Use `runtime-doctor` when generated surfaces, adapters, state, or live runtime drift might be involved.
            4. Use `problem-solving` for competing hypotheses and `sequential-thinking` for ordered probes.
            5. Route to `fix-hub` only when the cause and affected surface are bounded.
            6. Offensive failure routing: when symptoms include EDR detection, bypass failure, injection error, antibot block, or fingerprint mismatch -> route to the matching offensive specialist before proposing fixes:
               - EDR detection / AV alert -> `edr-evasion-tactics`, `telemetry-blinding`
               - Injection / hollowing failure -> `process-injection-techniques`
               - Antibot block / Cloudflare / Datadome -> `antibot-challenge-solving`, `protocol-fingerprint-spoofing`
               - Fingerprint mismatch / Canvas detected -> `browser-fingerprint-engineering`
               - Binary detected / signature match -> `binary-stealth-obfuscation`, `malware-analysis-workflows`
               - Reverse engineering needed -> `binary-reverse-methodology`, `frontend-crypto-reverse`

            ## Evidence contract
            - reproduce the issue or mark reproduction as blocked with the missing condition
            - write `investigation-notes.md` with evidence, likely cause, non-causes ruled out, and next probe
            - include failing command, log, trace, screenshot, or state pointer where available
            - state whether this is a code bug, test problem, runtime drift, or planning ambiguity

            ## Failure modes
            Hold when the lane is guessing from symptoms, stacking fixes before one failing signal is understood, or hiding weak reproduction.
            """
        ).strip(),
    ),
    "fix-hub": SkillSpec(
        name="fix-hub",
        description="Use when debug-hub has validated findings or when a change request is already sharply bounded. Turn those findings into a minimal implementation path and hand off to the developer loop.",
        role="fix-hub",
        layer="layer-2-workflow-hubs",
        inputs=["tech-spec or story", "investigation-notes when debugging", "architecture and project-context when relevant"],
        outputs=["refined tech-spec or story", "implementation handoff to developer", "updated workflow-state"],
        references=[
            "Keep the fix surface as small as possible.",
            "Use developer plus execution-loop for execution, not as a replacement for scoping.",
            "If the fix expands the contract or architecture, route back through workflow-router or plan-hub.",
        ],
        next_steps=[
            "developer",
            "go-service-engineering",
            "next-product-frontend",
            "project-architecture",
            "data-persistence",
            "dependency-management",
            "test-first-development",
            "test-hub",
            "review-hub",
            "workflow-router",
                    "refactoring-discipline",
                    "iac-cloud-provisioning",
            "container-kubernetes-ops",
            "secrets-management",
        ],
        body=dedent(
            """\
            # Mission
            Convert a known problem into a bounded implementation path that can be executed safely.

            ## Mandatory routing
            1. Use `project-architecture` when the fix touches boundaries, dependencies, or ownership.
            2. Use `data-persistence` for schemas, migrations, transactions, caches, or backfills.
            3. Use `dependency-management` for package, lockfile, toolchain, or environment fixes.
            4. Use `go-service-engineering` or `next-product-frontend` for stack-specific implementation handoff.
            5. Use `test-first-development` when behavior can be captured before the implementation pass.
            6. Offensive fix handoff: when the fix involves native systems or security-sensitive code, route to the matching specialist:
               - C++ / Win32 / native code -> `cpp-systems-engineering`, `windows-native-internals`
               - Python scripting / automation -> `advanced-python-engineering`
               - Binary evasion / obfuscation -> `binary-stealth-obfuscation`
               - EDR / AV bypass -> `edr-evasion-tactics`, `telemetry-blinding`
               - Process injection / hollowing -> `process-injection-techniques`
               - C2 / network stealth -> `network-stealth-c2`
               - Antibot / fingerprint bypass -> `antibot-challenge-solving`, `protocol-fingerprint-spoofing`
               - Crypto reverse / signing -> `frontend-crypto-reverse`
               - Desktop ImGui UI -> `desktop-imgui-development`
               - Desktop Python UI -> `desktop-python-ui`
               - Terminal / CLI UI -> `terminal-operator-ui`

            ## Evidence contract
            - update the active story or tech-spec with real files, boundaries, and verification steps
            - name what must not change while fixing the issue
            - include the failing signal, intended green signal, rollback note, and one edge case
            - hand off to `developer` only after the implementation surface is bounded

            ## Failure modes
            Hold when the fix expands architecture without plan review, hides data risk, or skips the first verification command.
            """
        ).strip(),
    ),
    "test-hub": SkillSpec(
        name="test-hub",
        description="Use when implementation exists, after a risky refactor, or whenever confidence is lower than the change impact. Coordinate verification, evidence collection, and residual-risk review before work is called done.",
        role="verification-hub",
        layer="layer-2-workflow-hubs",
        inputs=["story or tech-spec", "implementation evidence", "testing-patterns reference", "workflow-state"],
        outputs=[".relay-kit/contracts/qa-report.md", "updated workflow-state with pass, fail, or blocked verdict"],
        references=[
            "Use qa-governor for the actual readiness gate.",
            "Prefer evidence tied to acceptance criteria and regression surface.",
            "Route back to debug-hub when verification fails unexpectedly.",
            "When discipline utilities are installed, use `evidence-before-completion` before calling the lane ready.",
        ],
        next_steps=[
            "testing-patterns",
            "evidence-before-completion",
            "signal-calibration",
            "token-economy",
            "mmo-mobile-app-automation",
            "qa-governor",
            "review-hub",
            "debug-hub",
            "workflow-router",
        ],
        body=dedent(
            """\
            # Mission
            Turn raw test execution into a real readiness decision.

            ## Mandatory routing
            1. Use `testing-patterns` to map risk to the right proof surface.
            2. Use `evidence-before-completion` for claim-to-evidence checks before final verdicts.
            3. Use `signal-calibration` when a claim says production-ready, field-tested, commercial-ready, or unusually strong.
            4. Use `token-economy` when long logs or large context need compression without losing failure evidence.
            5. Use `mmo-mobile-app-automation` for device/emulator matrix evidence when mobile MMO flows are under test.
            6. Offensive evidence contracts: when the implementation involves binary, evasion, or bypass work, the qa-report must include:
               - EDR/AV sandbox result (safe detonation in isolated VM or sandbox)
               - Telemetry blinding confirmation (no hooks fired, no ETW events leaked)
               - Network traffic capture for C2 (traffic matches stealth profile)
               - Antibot bypass: screenshot of challenge page bypassed or HTTP 200 without block
               - On-chain script: `mmo-onchain-security-audit` verdict before any wallet interaction

            ## Evidence contract
            - build the smallest useful matrix that covers acceptance criteria and regression surface
            - preserve failing command details or raw log pointers
            - write or refresh `qa-report.md` with pass, fail, blocked, and residual-risk sections
            - route failures to `debug-hub` with exact reproduction evidence

            ## Failure modes
            Hold when evidence is only a screenshot of success, when failed logs are summarized away, or when the test scope does not match risk.
            """
        ).strip(),
    ),
    "review-hub": SkillSpec(
        name="review-hub",
        description="Use when artifacts disagree or before final completion claims. Check alignment across requirements, architecture, implementation, and quality evidence, then decide whether to accept, re-slice, debug, or re-plan.",
        role="review-hub",
        layer="layer-2-workflow-hubs",
        inputs=["active artifacts", "qa-report if present", "workflow-state"],
        outputs=["updated workflow-state", "go/no-go review verdict", "specific bounce-back path when misalignment exists"],
        references=[
            "Review-hub is the mesh junction: it may send work back to plan, debug, fix, or test.",
            "Do not hide disagreement between artifacts; name it and route accordingly.",
            "Use `.relay-kit/docs/review-loop.md` and `.relay-kit/docs/branch-completion.md` for review handling and end-of-branch discipline.",
            "If work crosses sessions, require context-continuity artifacts before accepting final completion claims.",
        ],
        next_steps=[
            "impact-radar",
            "runtime-doctor",
            "migration-guard",
            "skill-evolution",
            "field-journal-evolution",
            "signal-calibration",
            "doc-pointers",
            "multimodal-evidence",
            "media-tooling",
            "plan-hub",
            "debug-hub",
            "fix-hub",
            "test-hub",
            "context-continuity",
            "workflow-router",
                    "secure-code-review",
            "technical-writing",
        ],
        body=dedent(
            """\
            # Mission
            Make completion a deliberate alignment check, not just a feeling that enough has happened.

            ## Mandatory checks
            - Do requirements, architecture, and implementation still describe the same change?
            - Does quality evidence actually cover the promised behavior and regression surface?
            - Is the active lane done, or is it merely unblocked enough to continue elsewhere?

            ## Output contract
            End with one explicit verdict:
            - go forward,
            - bounce to planning,
            - bounce to debugging,
            - bounce to implementation,
            - or hold for missing evidence.

            ## Review handling discipline
            - Verify external review feedback against the codebase before accepting it.
            - Prefer one review item at a time when feedback changes code or requirements.
            - If the lane is complete, route through branch-completion discipline before treating it as finished.
            """
        ).strip(),
    ),
}


ROLE_SKILLS: Dict[str, SkillSpec] = {
    "analyst": SkillSpec(
        name="analyst",
        description="Use when discovery is needed before writing a prd or choosing architecture. Clarify product intent, assumptions, users, and open questions; produce a product brief for work that is not already fully scoped.",
        role="analysis",
        layer="layer-4-specialists-and-standalones",
        inputs=["user request", ".relay-kit/contracts/project-context.md", ".relay-kit/state/workflow-state.md"],
        outputs=[".relay-kit/contracts/product-brief.md"],
        references=[
            "Lean on research-expert, problem-solving, and sequential-thinking when the scope is fuzzy.",
            "Keep the brief short enough that downstream roles can actually use it.",
        ],
        next_steps=["pm", "plan-hub", "workflow-router"],
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
            - If the request is already well-scoped and quick-flow fits, do not force a brief.
            - If a fresh brief already exists, update only the parts affected by the new request.
            """
        ).strip(),
    ),
    "pm": SkillSpec(
        name="pm",
        description="Use when the work is past discovery and needs a buildable scope. Translate a product brief or scoped request into a prd, release slices, and acceptance criteria.",
        role="planning",
        layer="layer-4-specialists-and-standalones",
        inputs=[".relay-kit/contracts/product-brief.md or direct scoped request", ".relay-kit/contracts/project-context.md"],
        outputs=[".relay-kit/contracts/PRD.md", ".relay-kit/contracts/epics.md"],
        references=[
            "Do not hand wave acceptance criteria.",
            "Separate must-have requirements from stretch goals and out-of-scope ideas.",
            "Use UX and research support skills when the user experience is part of the risk.",
        ],
        next_steps=["architect", "scrum-master", "plan-hub", "review-hub"],
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
            """
        ).strip(),
    ),
    "architect": SkillSpec(
        name="architect",
        description="Use when a prd exists or when a change could alter module boundaries, data flow, security, or operations. Convert requirements into an implementation-ready architecture that fits the existing codebase.",
        role="solutioning",
        layer="layer-4-specialists-and-standalones",
        inputs=[".relay-kit/contracts/PRD.md", ".relay-kit/contracts/project-context.md", "existing support skills and references"],
        outputs=[".relay-kit/contracts/architecture.md"],
        references=[
            "Mirror the existing codebase before inventing new patterns.",
            "Pull in project-architecture, dependency-management, api-integration, data-persistence, security-patterns, performance-optimization, and logging-observability when relevant.",
            "When stack-specific delivery is required, coordinate with go-service-engineering or next-product-frontend for implementation-level constraints.",
            "Architecture must include a readiness verdict, not just diagrams or aspirations.",
        ],
        next_steps=[
            "project-architecture",
            "dependency-management",
            "api-integration",
            "data-persistence",
            "go-service-engineering",
            "next-product-frontend",
            "mmo-ecommerce-multichannel",
            "mermaid-diagrams",
            "scrum-master",
            "review-hub",
            "plan-hub",
            "workflow-router",
                    "observability-instrumentation",
                    "iac-cloud-provisioning",
            "container-kubernetes-ops",
            "privacy-compliance",
        ],
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
            """
        ).strip(),
    ),
    "scrum-master": SkillSpec(
        name="scrum-master",
        description="Use when planning is done and work must be sliced into safe, verifiable increments. Turn prd and architecture into implementation-ready stories or a tech spec for quick-flow work.",
        role="delivery",
        layer="layer-4-specialists-and-standalones",
        inputs=[".relay-kit/contracts/PRD.md", ".relay-kit/contracts/architecture.md", ".relay-kit/contracts/epics.md", ".relay-kit/contracts/tech-spec.md"],
        outputs=[".relay-kit/contracts/stories/story-xxx.md", ".relay-kit/contracts/tech-spec.md when quick-flow is used"],
        references=[
            "Each story should be a thin vertical slice with explicit done criteria.",
            "Do not create stories that hide architectural decisions or missing acceptance criteria.",
            "Use `.relay-kit/docs/planning-discipline.md` to keep tasks bite-sized, testable, and explicit about verification.",
            "Execution order should be explicit; stories are not considered runnable until dependencies and first verification signals are named.",
        ],
        next_steps=["developer", "test-hub", "review-hub", "workflow-router"],
        body=dedent(
            """\
            # Mission
            Cut work into execution units that a developer can complete without re-opening product or architecture debates.

            ## For quick-flow
            Create or refine `.relay-kit/contracts/tech-spec.md` with:
            - change summary
            - root cause or context
            - files likely affected
            - implementation notes
            - verification steps

            ## For product-flow or enterprise-flow
            Create story files under `.relay-kit/contracts/stories/`.
            Each story must include:
            - story statement
            - acceptance criteria
            - implementation notes
            - test notes
            - risks
            - depends_on (story ids)
            - parallel-safe (yes/no)
            - done checklist

            ## Story quality bar
            - Small enough to verify in one focused implementation pass.
            - Large enough to deliver user-visible progress.
            - Explicit about what must be tested.
            - Explicit about which upstream documents it depends on.
            - Explicit about the first verification command or evidence expected after implementation.
            - Explicit about the next sequential execution step.
            """
        ).strip(),
    ),
    "developer": SkillSpec(
        name="developer",
        description="Use when planning is ready and code must be changed with controlled scope and evidence. Implement a story or tech-spec using the cleaned execution loop and project-specific support references.",
        role="implementation",
        layer="layer-4-specialists-and-standalones",
        inputs=["story or tech-spec", "project-context", "architecture when present", "relevant support references"],
        outputs=["working code", "test evidence", "updated workflow-state or handoff note"],
        references=[
            "Use execution-loop as the execution engine.",
            "Pull in project-architecture, api-integration, data-persistence, and testing-patterns as needed.",
            "Hand off to test-hub or qa-governor; do not self-certify completion without evidence.",
            "Use `test-first-development` when it is installed, selected, or provided by the active bundle; otherwise run the test-first loop directly inside this skill and name the fallback evidence path.",
            "If a test-first loop is not practical, say why before coding and name the alternative failing signal you will use.",
            "Prefer the smallest diff that fixes the failing reproduction; name rollback notes and one edge case before completion.",
            "Default to plain ASCII in source code, comments, identifiers, test names, placeholder copy, and sample data unless the repo or product explicitly requires non-ASCII content.",
            "Do not create parallel lanes or subagents; keep independent work as sequential checkpoints in one context.",
        ],
        next_steps=[
            "test-first-development",
            "execution-loop",
            "go-service-engineering",
            "next-product-frontend",
            "advanced-python-engineering",
            "desktop-python-ui",
            "desktop-imgui-development",
            "terminal-operator-ui",
            "data-persistence",
            "dependency-management",
            "project-architecture",
            "test-hub",
            "qa-governor",
            "review-hub",
                    "llm-app-engineering",
        ],
        allowed_tools=EDIT_AND_TEST_TOOLS,
        body=dedent(
            """\
            # Mission
            Turn an approved story or tech-spec into code and evidence without reopening solved planning questions.

            ## Mandatory behavior
            1. Read the active story or tech-spec completely before changing code.
            2. Pull only the support references needed for the specific files or boundaries involved.
            3. Use `test-first-development` when it is installed, selected, or provided by the active bundle; otherwise run the test-first loop directly inside this skill.
            4. Capture the failing test or failing reproduction signal before the main implementation pass.
            5. If a test-first loop is not practical, say why and name the fallback evidence path before editing code.
            6. Keep the smallest diff that explains the change; avoid rewriting adjacent code to make it look cleaner.
            7. Name one edge case and rollback note when the change touches backend behavior, persistence, APIs, queues, auth, or billing.
            8. Default to plain ASCII in source code, comments, identifiers, test names, placeholder copy, and sample data. Do not add decorative icons, emojis, or unusual Unicode characters unless the existing repo or product content explicitly requires them.
            9. Execute through `execution-loop` rather than piling unrelated changes into one pass.
            10. Keep one behavior or fix slice per red-green cycle instead of widening scope during the green phase.
            11. Preserve the active acceptance criteria and note any hidden scope discovered during implementation.
            12. Hand off to `test-hub` or `qa-governor` with the test evidence actually collected.

            ## Escalation
            If implementation reveals missing architecture, unclear acceptance criteria, or a bigger-than-expected change surface, stop and route back through `review-hub` or `workflow-router`.
            """
        ).strip(),
    ),
    "qa-governor": SkillSpec(
        name="qa-governor",
        description="Use when work needs a readiness verdict or implementation confidence is low. Check readiness against acceptance criteria, risk, and regression scope, then write a QA report.",
        role="quality",
        layer="layer-4-specialists-and-standalones",
        inputs=["PRD or tech-spec", "architecture or story", "evidence from tests and reviews"],
        outputs=[".relay-kit/contracts/qa-report.md"],
        references=[
            "Use testing-patterns as the evidence map for the project.",
            "Use `evidence-before-completion` only for the narrow claim-to-evidence pass before this readiness gate.",
            "Use `.relay-kit/docs/review-loop.md` when review feedback must be validated before action.",
            "Coverage must be explained against acceptance criteria and risk, not just number of tests.",
            "Use context-continuity when readiness evidence must survive a new thread or handoff before final sign-off.",
        ],
        next_steps=[
            "signal-calibration",
            "evidence-before-completion",
            "runtime-doctor",
            "review-hub",
            "debug-hub",
            "context-continuity",
            "workflow-router",
        ],
        body=dedent(
            """\
            # Mission
            Produce a readiness verdict and surface residual risk clearly.

            ## Boundary
            - Use qa-governor for readiness verdict, shipability, acceptance coverage, risk, and regression scope.
            - This is not a one-claim proof pass; use evidence-before-completion for claim-to-evidence checks.
            - End with a go or no-go recommendation grounded in evidence.

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
            - Treat completion claims as invalid until the claim-to-evidence pass has fresh verification evidence.
            """
        ).strip(),
    ),
    "go-service-engineering": SkillSpec(
        name="go-service-engineering",
        description="Use when the request is primarily Go backend service work. Define handler boundary, transaction boundary, persistence, middleware, jobs, caching, and test evidence for Go service delivery.",
        role="go-engineering",
        layer="layer-4-specialists-and-standalones",
        inputs=["go service requirements", "existing Go module structure", "architecture or tech-spec when available"],
        outputs=["Go service implementation plan or code delta with test and runtime evidence"],
        references=[
            "Prefer established local service patterns over introducing a new framework by default.",
            "Cover routing table, handler boundary, repository interface, transaction boundary, cache ownership, background jobs, and observability in one coherent service contract.",
            "Include evidence commands for unit tests, httptest or handler tests, integration tests, context cancellation, and migration rollback safety where relevant.",
        ],
        next_steps=["developer", "testing-patterns", "qa-governor", "review-hub"],
        body=dedent(
            """\
            # Mission
            Deliver Go service work the way a backend owner would review it: boundaries first, failure modes named, evidence attached.

            ## Mandatory scope checks
            - Confirm module boundaries, routing table ownership, and service ownership before coding.
            - Define handler boundary, request validation, response shape, and error mapping for the target service.
            - Make persistence strategy explicit: ORM, sqlc, query builder, or SQL-first path.
            - Name transaction boundary, repository interface, cache invalidation, and background job behavior when state or throughput depends on them.
            - Handle context cancellation and timeout propagation on IO-heavy paths.
            - Require unit, httptest, integration, migration rollback, and observability evidence before claiming completion.

            ## Evidence contract
            - name the exact test commands used
            - include failing signal and green signal for changed behavior
            - include one table-driven edge case or explicit reason it does not apply
            - record any migration or data-risk notes for rollout
            """
        ).strip(),
    ),
    "next-product-frontend": SkillSpec(
        name="next-product-frontend",
        description="Use when work is primarily Next.js product UI or frontend architecture. Plan and implement App Router flows, server and client boundaries, server actions, data fetching, and quality gates for user-facing delivery.",
        role="next-frontend",
        layer="layer-4-specialists-and-standalones",
        inputs=["frontend request or story", "existing Next.js structure", "design and UX constraints"],
        outputs=["Next.js implementation plan or code delta with accessibility and performance evidence"],
        references=[
            "Prefer App Router and server/client boundary clarity over generic React-only guidance.",
            "Keep shadcn or existing component-system usage consistent with local patterns.",
            "Collect accessibility and performance evidence before completion claims.",
            *domain_resource_references("next-product-frontend"),
        ],
        next_steps=[
            "developer",
            "ux-structure",
            "frontend-design",
            "ui-styling",
            "accessibility-review",
            "review-hub",
        ],
        body=dedent(
            """\
            # Mission
            Build or refactor Next.js product surfaces with explicit server/client architecture and measurable quality.

            ## Mandatory scope checks
            - identify App Router route ownership and layout boundaries
            - document server component versus client component decisions
            - define server actions contracts for mutation-heavy flows
            - define data fetching and cache behavior for changed screens
            - define component ownership, styling system, and state coverage before coding
            - enforce accessibility and performance checks for user-facing risk

            ## Evidence contract
            - include route-level behavior proof
            - include accessibility findings or gate output
            - include performance or hydration-risk notes when relevant

            ## Handoff rules
            Hand implementation to `developer`, styling detail to `ui-styling`, visual critique to `aesthetic`, and accessibility proof to `accessibility-review`.

            ## Failure modes
            Hold when the plan treats every screen as generic client-side React, skips cache semantics, ignores error/loading states, or produces a page that looks like a template instead of a product surface.
            """
        ).strip(),
        allowed_tools=EDIT_AND_TEST_TOOLS,
    ),
    "frontend-design": SkillSpec(
        name="frontend-design",
        description="Use when the user asks to build web components, pages, or applications and visual quality matters. Create distinctive, production-grade frontend interfaces that avoid generic AI aesthetics.",
        role="frontend-design",
        layer="layer-4-specialists-and-standalones",
        inputs=["frontend request", "product context", "existing design system or reference screenshots"],
        outputs=["implemented or reviewed frontend surface with visual direction, state coverage, and screenshot evidence"],
        references=[
            "Anchor visual direction in real references, existing product patterns, or component sources before styling.",
            "Use aesthetic for critique, ui-styling for component system details, and accessibility-review for merge gates.",
            "Prefer deliberate hierarchy, density, and state coverage over generic card-heavy layouts.",
            *domain_resource_references("frontend-design"),
        ],
        next_steps=["next-product-frontend", "ui-styling", "aesthetic", "accessibility-review", "review-hub"],
        body=dedent(
            """\
            # Mission
            Ship frontend work that feels designed for the product instead of assembled from generic AI patterns.

            ## Mandatory scope checks
            - define purpose, audience, and primary task before choosing layout
            - choose design variance, motion intensity, and visual density explicitly
            - anchor layout in a real reference, existing screen, or trusted component source
            - define loading, empty, error, and mobile states for real product surfaces
            - reject oversized safe heroes, equal-card filler, default icons, and purple gradient padding when they do not serve hierarchy

            ## Evidence contract
            - include reference or screenshot notes before claiming visual quality
            - include before/after or rendered-state evidence when implementation changed
            - include accessibility and performance risk notes for user-facing changes

            ## Handoff rules
            Hand component-level styling to `ui-styling`, product UI architecture to `next-product-frontend`, and final visual critique to `aesthetic` or `review-hub`.
            """
        ).strip(),
        allowed_tools=EDIT_AND_TEST_TOOLS,
    ),
    "ui-styling": SkillSpec(
        name="ui-styling",
        description="Use when building user interfaces, implementing design systems, creating responsive layouts, adding accessible components, customizing themes, or establishing consistent styling patterns across applications.",
        role="ui-styling",
        layer="layer-4-specialists-and-standalones",
        inputs=["component or page requirements", "design tokens or component library", "accessibility constraints"],
        outputs=["styled UI implementation or system guidance with responsive, state, and accessibility evidence"],
        references=[
            "Treat component libraries as raw material; do not ship their default look without product-specific structure.",
            "Use repo-native UI components, icon systems, and theme tokens when present.",
            "Keep source code, comments, fixture text, and placeholder copy plain ASCII unless product content requires otherwise.",
            *domain_resource_references("ui-styling"),
        ],
        next_steps=["frontend-design", "aesthetic", "accessibility-review", "test-hub", "review-hub"],
        body=dedent(
            """\
            # Mission
            Convert UI requirements into component and styling decisions that are responsive, accessible, and visually intentional.

            ## Mandatory scope checks
            - identify the component system, token source, and responsive breakpoints
            - define corner, contrast, spacing, and type systems before composing screens
            - design loading, empty, error, focus, disabled, and validation states when the UI is interactive
            - avoid default library surfaces, equal-radius panels everywhere, and chart or icon defaults without a reason
            - keep motion transform/opacity-first and respect reduced-motion needs

            ## Evidence contract
            - include component/state coverage and screenshot or browser evidence when available
            - include accessibility notes for keyboard, labels, focus, and contrast
            - include exact files, components, or tokens changed during implementation

            ## Handoff rules
            Route broader screen direction to `frontend-design`, screenshot critique to `aesthetic`, and release confidence to `accessibility-review` or `test-hub`.
            """
        ).strip(),
        allowed_tools=EDIT_AND_TEST_TOOLS,
    ),
    "aesthetic": SkillSpec(
        name="aesthetic",
        description="Use when UI quality matters and the first-pass output risks looking obviously AI-generated. Create aesthetically strong interfaces through reference-driven design, screenshot analysis, component sourcing, and iterative review.",
        role="aesthetic-review",
        layer="layer-4-specialists-and-standalones",
        inputs=["rendered UI, screenshot, or design direction", "reference examples", "product tone constraints"],
        outputs=["aesthetic critique, revision direction, and evidence-backed visual quality verdict"],
        references=[
            "Reference-driven structure beats invented average structure.",
            "Beauty without hierarchy is decoration; critique structure first and polish second.",
            "Use multimodal-evidence for screenshot interpretation and browser-inspector for live browser facts.",
            *domain_resource_references("aesthetic"),
        ],
        next_steps=["frontend-design", "ui-styling", "multimodal-evidence", "review-hub"],
        body=dedent(
            """\
            # Mission
            Prevent obviously AI-generated UI by forcing reference analysis, visual hierarchy critique, and a revision loop.

            ## Mandatory scope checks
            - identify the first focal point and whether proof sits close enough to the main claim
            - set design variance, motion intensity, and visual density before recommending changes
            - compare the screen against real references or project-native patterns
            - flag over-rounded panels, decorative gradient filler, safe hero blocks, equal-weight cards, and default icon or chart choices
            - require loading, empty, and error states for real product surfaces

            ## Evidence contract
            - include screenshot, reference, or rendered-state evidence for every visual verdict
            - separate visible facts from taste judgments
            - name one structural revision before minor polish when the UI still feels generic

            ## Handoff rules
            Send implementation details to `frontend-design` or `ui-styling`; send static screenshot interpretation to `multimodal-evidence`.
            """
        ).strip(),
        allowed_tools=READ_ANALYZE_TOOLS,
    ),
    "growth-marketing": SkillSpec(
        name="growth-marketing",
        description="Use when the request is growth or marketing execution. Produce positioning, campaign plans, launch checklist, funnel metrics, and quality checks tied to product goals.",
        role="growth",
        layer="layer-4-specialists-and-standalones",
        inputs=["product context", "target audience or ICP", "launch or campaign objective"],
        outputs=["growth execution plan with channel strategy, campaign QA, and measurable outcomes"],
        references=[
            "Keep messaging claims tied to source evidence and product constraints.",
            "Define funnel goals and success metrics explicitly, not as generic marketing advice.",
            "Include campaign QA and post-launch measurement checkpoints.",
            *domain_resource_references("growth-marketing"),
        ],
        next_steps=["market-research", "pm", "review-hub", "workflow-router"],
        body=dedent(
            """\
            # Mission
            Turn a growth request into an evidence-backed campaign plan with clear measurement.

            ## Mandatory scope checks
            - define positioning and audience fit
            - map campaign channels to funnel stages
            - set launch checklist and QA checkpoints
            - set post-launch metrics and review cadence
            - identify claims that need market-research evidence before copy ships

            ## Evidence contract
            - include source-backed messaging assumptions
            - include KPI targets and measurement method
            - include campaign QA acceptance criteria

            ## Handoff rules
            Route competitor or pricing uncertainty to `market-research`, product scope gaps to `pm`, automation setup to `automation-ops`, and claim risk to `signal-calibration`.

            ## Failure modes
            Hold when output becomes generic launch advice, unsupported superlatives, channel lists without funnel ownership, or copy that cannot be tied to a real product proof.
            """
        ).strip(),
        allowed_tools=READ_ANALYZE_TOOLS,
    ),
    "market-research": SkillSpec(
        name="market-research",
        description="Use when the request needs competitor intelligence, ICP refinement, pricing signal analysis, or market hypothesis validation before execution decisions.",
        role="market-intelligence",
        layer="layer-4-specialists-and-standalones",
        inputs=["research question", "domain context", "decision to support"],
        outputs=["ranked market findings with source quality and decision-impact summary"],
        references=[
            "Separate verified source facts from inference and assumption.",
            "Score source freshness and authority before using findings in high-impact decisions.",
            "Connect findings directly to product, pricing, or GTM decisions.",
            *domain_resource_references("market-research"),
        ],
        next_steps=["growth-marketing", "pm", "architect", "review-hub"],
        body=dedent(
            """\
            # Mission
            Provide decision-grade market findings with explicit evidence quality.

            ## Mandatory scope checks
            - define the exact decision question
            - gather competitor, ICP, and pricing signals
            - rank findings by source authority and freshness
            - call out unknowns and unresolved assumptions
            - name how findings will change product, marketing, or technical decisions

            ## Evidence contract
            - include citation-ready source list
            - mark each claim as verified, inferred, or unknown
            - include decision impact for each major finding

            ## Handoff rules
            Send go-to-market execution to `growth-marketing`, requirement implications to `pm`, technical implications to `architect`, and overclaim risk to `signal-calibration`.

            ## Failure modes
            Hold when sources are stale, claims are uncited, competitor comparisons use popularity instead of capability, or pricing signals are presented without confidence level.
            """
        ).strip(),
        allowed_tools=READ_ANALYZE_TOOLS,
    ),
    "automation-ops": SkillSpec(
        name="automation-ops",
        description="Use when the request is workflow automation or operational scripting. Define schedulers, webhooks, runbooks, rollback safety, and dry-run discipline for reliable automation.",
        role="automation",
        layer="layer-4-specialists-and-standalones",
        inputs=["automation objective", "runtime constraints", "integration boundaries"],
        outputs=["automation design or implementation with operational safeguards and run evidence"],
        references=[
            "Prefer deterministic runbooks over one-off script behavior.",
            "Require dry-run, rollback, and failure-handling rules for any risky operation.",
            "Capture operational observability and handoff expectations for support workflows.",
            *domain_resource_references("automation-ops"),
        ],
        next_steps=["developer", "policy-guard", "release-readiness", "qa-governor"],
        body=dedent(
            """\
            # Mission
            Deliver automation workflows that are reliable, auditable, and reversible.

            ## Mandatory scope checks
            - define trigger model: schedule, webhook, or manual run
            - define idempotency and retry behavior
            - define rollback or compensation path
            - define runbook and operational ownership
            - define observability, queue pressure, and operator stop controls

            ## Evidence contract
            - include dry-run proof when supported
            - include failure-path handling proof
            - include rollback or recovery instructions

            ## Handoff rules
            Route implementation to `developer`, risky shell/path behavior to `policy-guard`, release proof to `release-readiness`, and production verdicts to `qa-governor`.

            ## Failure modes
            Hold when automation has no dry-run, no idempotency story, no retry budget, no raw failure log, or no named human owner for incident recovery.
            """
        ).strip(),
        allowed_tools=EDIT_AND_TEST_TOOLS,
    ),
    "vietnamese-product-localization": SkillSpec(
        name="vietnamese-product-localization",
        description="Use when product output must be localized for Vietnamese users. Produce Vietnamese or bilingual docs, support copy, release notes, and communication artifacts with quality constraints.",
        role="localization",
        layer="layer-4-specialists-and-standalones",
        inputs=["source content or request", "target audience context", "localization policy profile"],
        outputs=["Vietnamese or bilingual product artifacts with terminology and quality notes"],
        references=[
            "Treat Vietnamese support as profile-based policy, not a forced global default.",
            "Maintain terminology consistency across docs, support, and product messaging.",
            "Call out any untranslated or uncertain terms explicitly.",
        ],
        next_steps=["growth-marketing", "pm", "review-hub", "qa-governor"],
        body=dedent(
            """\
            # Mission
            Localize product-facing communication for Vietnamese users with consistent terminology and clear quality boundaries.

            ## Mandatory scope checks
            - confirm whether output should be Vietnamese-only or bilingual
            - apply terminology consistency across all related artifacts
            - identify locale-sensitive phrasing that can affect support or release communication
            - verify whether runtime locale policy is opt-in and whether canonical IDs stay unchanged

            ## Evidence contract
            - include glossary or terminology notes for key product terms
            - mark unresolved translation ambiguities
            - keep localization policy explicitly opt-in by profile

            ## Handoff rules
            Route product positioning to `growth-marketing`, requirements changes to `pm`, readiness wording to `qa-governor`, and unsupported locale claims to `signal-calibration`.

            ## Failure modes
            Hold when localization silently changes route names, weakens technical meaning, mixes tones across support and release copy, or claims full i18n without metadata/runtime evidence.
            """
        ).strip(),
    ),
    "mmo-reup-automation": SkillSpec(
        name="mmo-reup-automation",
        description="Use when controlled MMO reup workflows need operator-run queues, scheduling windows, deduplication, attribution tracking, and policy-safe publishing controls.",
        role="mmo-reup",
        layer="layer-4-specialists-and-standalones",
        inputs=["content source inventory", "rights and attribution constraints", "target channel policy limits"],
        outputs=["reup operator console design with dedupe ledger, run queue, rate controls, and rollback plan"],
        references=[
            "Require explicit rights and attribution constraints before any automated repost flow.",
            "Use deterministic dedup keys and publish windows to avoid accidental spam bursts.",
            "Model the UI as an operator workbench: source inventory table, bulk action bar, publish queue, reject drawer, and evidence timeline.",
            "Block flows that depend on policy evasion, account abuse, or non-consensual content reuse.",
            *domain_resource_references("mmo-reup-automation"),
        ],
        next_steps=["automation-ops", "policy-guard", "qa-governor", "review-hub"],
        body=dedent(
            """\
            # Mission
            Build safe, measurable content reup automation for MMO operations without violating platform rules.

            ## Mandatory scope checks
            - define content ownership and permitted reuse policy
            - define source inventory fields: source id, rights status, attribution, fingerprint, last published, channel
            - define dedupe key strategy and repost frequency caps
            - define channel-specific posting windows and rate limits
            - define run queue states: draft, queued, publishing, rejected, published, rolled back
            - define emergency stop, rollback, and operator ownership

            ## Evidence contract
            - include dry-run output with dedupe and throttle decisions
            - include sample publish and reject logs with reason codes in an evidence drawer
            - include rollback and disable-runbook instructions
            """
        ).strip(),
        allowed_tools=EDIT_AND_TEST_TOOLS,
    ),
    "mmo-account-operations": SkillSpec(
        name="mmo-account-operations",
        description="Use when MMO account operations need profile inventory, lifecycle automation, health checks, risk segmentation, and recovery runbooks.",
        role="mmo-account-ops",
        layer="layer-4-specialists-and-standalones",
        inputs=["account inventory and ownership", "security and compliance policy", "platform limits and escalation paths"],
        outputs=["account operations console contract with profile table, health scoring, risk controls, observability, and recovery plan"],
        references=[
            "Account automation must use authorized credentials, clear ownership, and auditable actions.",
            "Never design flows for CAPTCHA bypass, identity spoofing, or policy circumvention.",
            "Mirror real account tools: folder/tag filters, owner columns, proxy binding, account health, cooldown, quarantine, and bulk action review.",
            "Separate routine lifecycle automation from high-risk actions that require manual approval.",
            *domain_resource_references("mmo-account-operations"),
        ],
        next_steps=["automation-ops", "policy-guard", "release-readiness", "qa-governor"],
        body=dedent(
            """\
            # Mission
            Operate MMO account fleets with deterministic controls, safety gates, and clear audit trails.

            ## Mandatory scope checks
            - classify account states: onboarding, active, limited, suspended, retired
            - define account inventory fields: owner, folder, tags, proxy binding, session status, health score, last action, cooldown until
            - enforce credential storage and rotation controls
            - define per-account and per-platform action budgets
            - define bulk action review and dry-run approval before changes touch more than one account
            - define incident response and suspension recovery path

            ## Evidence contract
            - include account-state transition logs
            - include budget and limit guard outputs
            - include quarantine, cooldown, and escalation checklist for enforcement events
            """
        ).strip(),
        allowed_tools=EDIT_AND_TEST_TOOLS,
    ),
    "mmo-browser-fleet-automation": SkillSpec(
        name="mmo-browser-fleet-automation",
        description="Use when MMO browser-based operations need profile inventory, session orchestration, deterministic waits, live debug evidence, and anti-flake reliability controls.",
        role="mmo-browser-automation",
        layer="layer-4-specialists-and-standalones",
        inputs=["browser workflow map", "profile/session constraints", "target platform policy and limits"],
        outputs=["browser fleet operator design with profile/session lease table, stable selectors, run queue, and debug evidence"],
        references=[
            "Prefer official API paths when available; use browser automation for allowed UI workflows only.",
            "Use explicit waits, resilient locators, and deterministic retry policy instead of blind sleeps.",
            "Keep profile-to-proxy affinity explicit; validate proxy health before launch and preserve profile folders/tags for operator filtering.",
            "Design dense operator screens: live session list, lease owner, selector drift, screenshot trace, console/network tabs, retry button, and stop button.",
            "Forbid automation patterns that rely on stealth evasion or non-API scraping prohibited by policy.",
            *domain_resource_references("mmo-browser-fleet-automation"),
        ],
        next_steps=["automation-ops", "browser-inspector", "policy-guard", "qa-governor"],
        body=dedent(
            """\
            # Mission
            Run browser MMO operations with high reliability, clear limits, and policy-safe automation behavior.

            ## Mandatory scope checks
            - define profile isolation, profile-to-proxy affinity, and session lease strategy
            - define operator inventory fields: profile id, folder, tags, proxy status, lease owner, browser state, last run, next allowed run
            - define selector contract and wait strategy per critical action
            - define retry and backoff rules for transient UI/network failures
            - define live debug evidence: screenshots, console logs, network errors, DOM snapshot, and human takeover marker
            - define runbook for stuck session, timeout, and rate-limit events

            ## Evidence contract
            - include run traces for one success path and one controlled failure path
            - include selector drift and timeout diagnostics
            - include policy and rate-limit guard decisions per run with raw trace pointers
            """
        ).strip(),
        allowed_tools=EDIT_AND_TEST_TOOLS,
    ),
    "mmo-social-marketing-automation": SkillSpec(
        name="mmo-social-marketing-automation",
        description="Use when MMO social media or marketing automation needs official API routing, campaign workspace, content calendar, moderation safeguards, and quota-aware execution.",
        role="mmo-social-automation",
        layer="layer-4-specialists-and-standalones",
        inputs=["campaign objective", "platform API capabilities", "content and moderation policy"],
        outputs=["social automation operator workflow with campaign queue, content QA, quota controls, and policy-safe execution"],
        references=[
            "Use official platform APIs and published quota/automation rules as the default path.",
            "Prevent duplicate or spam-like content bursts across accounts and channels.",
            "Model campaign operations as a work queue: content calendar, asset library, approval lane, reject reasons, quota meter, and per-channel status.",
            "Keep consent, data-use transparency, and account-safety requirements explicit.",
            *domain_resource_references("mmo-social-marketing-automation"),
        ],
        next_steps=["growth-marketing", "automation-ops", "market-research", "mmo-content-factory", "mmo-reup-automation", "review-hub"],
        body=dedent(
            """\
            # Mission
            Execute social MMO automation that can scale marketing outcomes without crossing platform enforcement lines.

            ## Mandatory scope checks
            - map each action to official API endpoint and permission scope
            - define campaign workspace fields: campaign, channel, account, asset, audience, schedule window, approval status
            - define per-platform quota budget and reset handling
            - define content duplication and frequency guardrails
            - define moderation queue, reject reason taxonomy, and incident escalation path

            ## Evidence contract
            - include API quota budget report and throttling behavior
            - include campaign QA checks, approval trail, and reject reasons
            - include compliance checklist for each target platform

            ## Handoff rules
            Route campaign message quality to `growth-marketing`, market assumptions to `market-research`, operational scheduling to `automation-ops`, and policy risk to `policy-guard`.

            ## Failure modes
            Hold when the plan depends on unofficial endpoints, duplicated posting bursts, missing approval lanes, weak moderation evidence, or generic social dashboard screens with no operator workflow.
            """
        ).strip(),
        allowed_tools=EDIT_AND_TEST_TOOLS,
    ),
    "mmo-lowcode-automation": SkillSpec(
        name="mmo-lowcode-automation",
        description="Use when MMO operations rely on no-code or low-code orchestration stacks and need execution history, modular flows, error handlers, and safe deployment controls.",
        role="mmo-lowcode-ops",
        layer="layer-4-specialists-and-standalones",
        inputs=["workflow platform capabilities", "trigger and dependency graph", "operational SLA and rollback constraints"],
        outputs=["low-code operations design with node graph, execution list, module contracts, retries, redaction, and observability hooks"],
        references=[
            "Treat visual workflow nodes as production logic: define contracts and failure semantics explicitly.",
            "Enforce per-scenario run limits and queue controls to prevent request storms.",
            "Mirror real automation tools: manual vs production execution, active/inactive state, node-level output, error workflow, redacted execution data, and execution search.",
            "Separate draft/test workflows from published production workflows.",
            *domain_resource_references("mmo-lowcode-automation"),
        ],
        next_steps=["automation-ops", "release-readiness", "qa-governor", "review-hub"],
        body=dedent(
            """\
            # Mission
            Build MMO low-code automation that stays debuggable, recoverable, and cost-aware under load.

            ## Mandatory scope checks
            - define trigger, schedule, manual execution, production execution, and dependency graph ownership
            - define execution list columns: workflow, node, status, duration, retries, operator, environment
            - define error handler and retry/backoff strategy per critical module
            - define rate-limit controls and queue behavior
            - define publish, rollback, and incident-response procedure
            - define redaction rules for credentials, tokens, cookies, payload samples, and account identifiers

            ## Evidence contract
            - include module-level success and failure traces
            - include throttling, queue-pressure, and redacted execution evidence
            - include publish-versus-draft workflow control proof
            """
        ).strip(),
        allowed_tools=EDIT_AND_TEST_TOOLS,
    ),
    "mmo-mobile-app-automation": SkillSpec(
        name="mmo-mobile-app-automation",
        description="Use when MMO mobile workflows need device inventory, emulator or device automation, stable selectors, app-state control, and repeatable run evidence.",
        role="mmo-mobile-automation",
        layer="layer-4-specialists-and-standalones",
        inputs=["mobile workflow journeys", "device or emulator matrix", "toolchain constraints and policy rules"],
        outputs=["mobile automation operations plan with device farm inventory, session lease, environment matrix, reliability controls, and evidence artifacts"],
        references=[
            "Prefer supported frameworks and official automation drivers for device control.",
            "Define deterministic app-state setup and teardown to reduce flake.",
            "Model the device farm like a real ops tool: hub/provider split, device status, lease owner, app version, logcat/crash/ANR evidence, and remote-control link.",
            "Do not design rooted, tampered, or policy-evasion mobile automation paths.",
            *domain_resource_references("mmo-mobile-app-automation"),
        ],
        next_steps=["automation-ops", "testing-patterns", "qa-governor", "review-hub"],
        body=dedent(
            """\
            # Mission
            Deliver stable mobile MMO automation for repetitive app workflows with measurable reliability.

            ## Mandatory scope checks
            - define emulator or device matrix, provider, hub, and startup method
            - define device inventory fields: device id, OS, app version, provider, health, lease owner, battery, network, last run
            - define app-state preconditions for each critical user journey
            - define selector strategy and wait/retry policy
            - define failure triage for crash, ANR, and timeout signals

            ## Evidence contract
            - include one full green run on target matrix
            - include one failure-path reproduction with root-cause notes
            - include run artifacts: logcat, screenshots, video or trace pointers, crash/ANR markers

            ## Handoff rules
            Route scheduler and queue concerns to `automation-ops`, proof design to `testing-patterns`, readiness verdicts to `qa-governor`, and visual/video evidence to `multimodal-evidence`.

            ## Failure modes
            Hold when the design has no device lease model, no app-state reset, no selector drift handling, no raw logcat/crash evidence, or a fake dashboard that hides operator retry controls.
            """
        ).strip(),
        allowed_tools=EDIT_AND_TEST_TOOLS,
    ),
    "mmo-cloud-operations-automation": SkillSpec(
        name="mmo-cloud-operations-automation",
        description="Use when MMO automation runs in cloud infrastructure and needs worker pools, scheduler, queue, retry, idempotency, and cost-guarded operations.",
        role="mmo-cloud-automation",
        layer="layer-4-specialists-and-standalones",
        inputs=["cloud runtime topology", "job and queue model", "SLA, cost, and security constraints"],
        outputs=["cloud MMO operations architecture with worker pool, queue dashboard, idempotent jobs, backoff policies, and observability"],
        references=[
            "Use idempotent job contracts, idempotency keys, and dead-letter handling for failure isolation.",
            "Use exponential backoff with jitter for transient failures and throttling events.",
            "Include queue depth, cost ceiling, and quota safeguards before scaling concurrency.",
            "Expose operator controls for pause, resume, retry, drain, replay, dead-letter inspection, and safe scale-down.",
            *domain_resource_references("mmo-cloud-operations-automation"),
        ],
        next_steps=["automation-ops", "release-readiness", "policy-guard", "qa-governor"],
        body=dedent(
            """\
            # Mission
            Run MMO cloud automation at scale with resilient retries, safe concurrency, and controlled operational cost.

            ## Mandatory scope checks
            - define scheduler, producer, worker pool, and queue boundaries
            - define queue dashboard fields: waiting, active, delayed, failed, completed, stalled, throughput, failure rate, average duration
            - define queue depth thresholds, dead-letter policy, and poison-message handling
            - define retry policy, jitter, and max-attempt semantics
            - define idempotency keys and dedupe strategy for side effects
            - define cost ceiling and emergency scale-down controls

            ## Evidence contract
            - include retry/backoff test evidence on throttling scenarios
            - include idempotency key and duplicate-prevention evidence
            - include worker health, queue health, alerts, and SLO signal mapping for operations
            """
        ).strip(),
        allowed_tools=EDIT_AND_TEST_TOOLS,
    ),
    "mmo-http-api-automation": SkillSpec(
        name="mmo-http-api-automation",
        description="Use when MMO workloads are primarily HTTP/API-driven and need endpoint catalog, contract-safe request orchestration, quota handling, redacted logs, and replay-safe execution.",
        role="mmo-api-automation",
        layer="layer-4-specialists-and-standalones",
        inputs=["endpoint catalog", "auth and scope model", "rate-limit and retry constraints"],
        outputs=["HTTP/API operator design with endpoint catalog, request ledger, contract validation, idempotent retry logic, and audit-ready logs"],
        references=[
            "Define request contracts from official API documentation before implementation.",
            "Handle 429 and transient 5xx paths with bounded retries and reset-aware backoff.",
            "Use idempotency key, request id, redacted raw request/response evidence, and replay checks for write operations.",
            "Mirror real API dashboards: endpoint groups, status-code filters, origin filters, retry count, duration, cost, and replay-safe request detail.",
            *domain_resource_references("mmo-http-api-automation"),
        ],
        next_steps=["api-integration", "automation-ops", "mmo-data-harvesting", "policy-guard", "qa-governor", "mmo-authorization-gate"],
        body=dedent(
            """\
            # Mission
            Execute MMO API automation with contract handling that a backend reviewer can replay and debug.

            ## Mandatory scope checks
            - define endpoint groups by risk and side-effect level
            - define authentication scope and token lifecycle
            - define request ledger fields: request id, endpoint, method, status code, duration, retry count, origin, cost, idempotency key
            - propagate request id or correlation id through logs
            - define rate-limit parsing and retry-backoff behavior
            - define idempotency key, dedupe, redacted logging, and replay-safety policy

            ## Evidence contract
            - include redacted request/response samples for success and 429 throttled paths
            - include idempotency key replay proof for write endpoints
            - include contract drift checks against API schema or docs plus status-code filter evidence
            """
        ).strip(),
        allowed_tools=EDIT_AND_TEST_TOOLS,
    ),
    "mmo-identity-infrastructure": SkillSpec(
        name="mmo-identity-infrastructure",
        description="Use when MMO multi-account operations need fingerprint isolation, proxy-to-profile binding, anti-detect browser setup, and consistent digital identity management per account.",
        role="mmo-identity-infrastructure",
        layer="layer-4-specialists-and-standalones",
        inputs=[
            "account inventory and risk tier classification",
            "proxy pool inventory (type, geo, ASN, provider)",
            "target platform fingerprint detection signals",
        ],
        outputs=["identity infrastructure plan: per-account profile specs, proxy assignments, consistency rules, rotation policy, and binding registry"],
        references=[
            "Never reuse a proxy or fingerprint profile across multiple accounts — IP clustering causes linked-account bans.",
            "Align timezone, language, and locale with proxy geolocation; mismatches are the #1 platform detection trigger.",
            "Use sticky sessions for established accounts; reserve proxy rotation for new profiles only.",
            "Treat fingerprint profiles as versioned infrastructure: changes must be logged with reason and timestamp.",
            "Anti-detect browsers (AdsPower, Multilogin, GoLogin, Hidemyacc) are the required execution environment.",
            *domain_resource_references("mmo-identity-infrastructure"),
        ],
        next_steps=["mmo-browser-fleet-automation", "mmo-account-operations", "mmo-nick-warmup-engine", "mmo-proxy-network-ops", "policy-guard"],
        body=dedent(
            """\
            # Mission
            Build airtight per-account digital identities that survive platform behavioral analysis and hardware fingerprinting.

            ## Mandatory scope checks
            - define fingerprint profile strategy per account: UA, WebGL, Canvas, fonts, timezone, language, screen resolution
            - enforce 1:1 rule: one proxy → one browser profile → one account; document each binding explicitly
            - define proxy type selection per risk tier: residential for high-trust, mobile for highest stealth, ISP static for stable long sessions
            - define consistency validation: timezone ↔ proxy geolocation ↔ language ↔ platform locale
            - define fingerprint stability policy: when to keep stable (established accounts) vs when to rotate (new profiles only)
            - define profile version control: fingerprint specs stored, tracked, and reproducible

            ## Evidence contract
            - include profile × proxy binding registry with consistency audit output
            - include fingerprint consistency check: timezone, locale, UA, hardware coherence all validated
            - include one controlled test: new profile passes target platform basic trust gate
            """
        ).strip(),
        allowed_tools=EDIT_AND_TEST_TOOLS,
    ),
    "mmo-proxy-network-ops": SkillSpec(
        name="mmo-proxy-network-ops",
        description="Use when MMO operations need proxy pool management, health monitoring, sticky session assignment, rotation policy, and network-level isolation per account or workflow.",
        role="mmo-proxy-ops",
        layer="layer-4-specialists-and-standalones",
        inputs=[
            "proxy pool inventory (provider, type, geo, ASN, expiry, cost)",
            "account and browser profile binding requirements",
            "target platform sensitivity level and known detection signals",
        ],
        outputs=["proxy operations plan: pool segmentation, assignment registry, health check schedule, rotation triggers, and monitoring runbook"],
        references=[
            "Residential and mobile proxies are required for high-trust platforms; datacenter proxies fail modern detection.",
            "Never rotate IP mid-session for established accounts — treat IP change as a trust-reset event requiring re-warmup.",
            "Log every proxy assignment change with timestamp, reason, and operator; treat the registry as a security artifact.",
            "Decommission proxies that appear on blacklists immediately, even if an active session is running.",
            *domain_resource_references("mmo-proxy-network-ops"),
        ],
        next_steps=["mmo-identity-infrastructure", "mmo-browser-fleet-automation", "mmo-account-operations", "mmo-nick-warmup-engine", "policy-guard"],
        body=dedent(
            """\
            # Mission
            Operate a reliable, cost-efficient proxy network that supports multi-account isolation without IP clustering or session leakage.

            ## Mandatory scope checks
            - define proxy pool composition ratio: residential, mobile, ISP static — by platform risk tier
            - define sticky session policy: duration per account tier, renewal trigger, failure fallback
            - define health check schedule: latency, anonymity level, geo drift, blacklist status
            - define proxy assignment registry: each proxy bound to exactly one profile/account
            - define cost ceiling and automatic scale-down trigger
            - define decommission protocol: blacklisted proxies removed immediately

            ## Evidence contract
            - include proxy health check report: latency, geo, ASN, blacklist status per proxy
            - include session stability log covering at least one 24-hour window
            - include assignment registry proving zero proxy-sharing across accounts
            """
        ).strip(),
        allowed_tools=EDIT_AND_TEST_TOOLS,
    ),
    "mmo-nick-warmup-engine": SkillSpec(
        name="mmo-nick-warmup-engine",
        description="Use when MMO accounts need a structured warmup sequence to build platform trust before high-risk actions, including behavioral scripting, interaction scheduling, and trust-score monitoring.",
        role="mmo-nick-warmup",
        layer="layer-4-specialists-and-standalones",
        inputs=[
            "account batch inventory: age, source platform, current trust state, profile completeness",
            "target platform action budget and rate limits per account tier",
            "execution environment: boxphone / anti-detect browser / mobile emulator",
        ],
        outputs=["warmup program: phase plan, daily action scripts, behavioral variance config, trust checkpoints, and per-account readiness verdict"],
        references=[
            "Warmup is mandatory — skipping it causes mass bans on fresh accounts within 24-48 hours of high-risk actions.",
            "Human-like variance in timing is non-negotiable: never use fixed intervals or identical action sequences across accounts.",
            "Use AI-generated content variants for comments and posts during warmup to avoid pattern detection.",
            "Treat warmup completion as a binary gate: no account enters seeding or monetization without passing all phase checks.",
            "Boxphone (real physical devices) produces higher trust scores than emulator warmup for Facebook and TikTok.",
            *domain_resource_references("mmo-nick-warmup-engine"),
        ],
        next_steps=["mmo-account-operations", "mmo-browser-fleet-automation", "mmo-social-marketing-automation", "mmo-identity-infrastructure", "policy-guard"],
        body=dedent(
            """\
            # Mission
            Turn newly created or recovered accounts into trusted platform citizens through a controlled, human-mimicking warmup program.

            ## Mandatory scope checks
            - define warmup duration and phase gates per account tier: 7 days (basic trust) to 14 days (high-trust seeding-ready)
            - define daily action budget per phase: scroll, like, comment, friend-add, group-join limits with escalation curve
            - define behavioral variance rules: randomized delays, action order shuffling, natural rest windows
            - define trust signal targets at each phase gate: profile completeness, 2FA, friend count, post history
            - define checkpoint recovery protocol: steps when account hits verification or restriction wall
            - define readiness verdict: binary pass/fail gate before account enters any monetization or seeding workflow

            ## Evidence contract
            - include warmup schedule per phase with action budgets, variance parameters, and trust targets
            - include trust-signal log at end of each phase
            - include one full green run: account passes all phases and target platform trust gate
            """
        ).strip(),
        allowed_tools=EDIT_AND_TEST_TOOLS,
    ),
    "mmo-ecommerce-multichannel": SkillSpec(
        name="mmo-ecommerce-multichannel",
        description="Use when MMO ecommerce operations need multi-store listing sync, master SKU management, order routing, inventory deduplication, and automated fulfillment across Shopee, TikTok Shop, Lazada, and similar platforms.",
        role="mmo-ecommerce-ops",
        layer="layer-4-specialists-and-standalones",
        inputs=[
            "store inventory across all platforms (Shopee, TikTok Shop, Lazada, Shopify, etc.)",
            "platform API credentials and endpoint capabilities",
            "logistics partner integration endpoints and supported label formats",
        ],
        outputs=["multi-channel ecommerce automation plan: SKU master design, sync rules, order routing, fulfillment automation, and operational runbook"],
        references=[
            "Always use official marketplace APIs for inventory sync — scraping-based sync desynchronizes under flash sale load.",
            "Buffer stock is mandatory for any SKU involved in flash sales, voucher campaigns, or live-stream selling.",
            "Master SKU is the single source of truth — mutations must go through the master registry, not individual platform portals.",
            "Test oversell prevention explicitly before any high-traffic campaign.",
            *domain_resource_references("mmo-ecommerce-multichannel"),
        ],
        next_steps=["mmo-http-api-automation", "mmo-cloud-operations-automation", "mmo-lowcode-automation", "automation-ops", "qa-governor"],
        body=dedent(
            """\
            # Mission
            Run multi-store ecommerce automation that treats inventory as a single source of truth across all channels.

            ## Mandatory scope checks
            - define Master SKU registry: one Merchant SKU maps to all platform-specific SKU variants
            - define real-time inventory sync: deduct from master pool on any channel sale, propagate to all others within SLA
            - define buffer stock policy per SKU per platform: minimum reserve to prevent oversell during flash sales
            - define listing bulk-upload workflow: field mapping, image processing, platform-specific requirements
            - define order routing: auto-confirm, label generation, logistics partner connection
            - define exception handling: oversell recovery, out-of-stock notification, return and refund routing

            ## Evidence contract
            - include SKU mapping registry showing coverage across all active stores
            - include inventory sync test: sale on platform A → stock update on platform B within SLA
            - include order routing trace for one complete fulfillment cycle
            """
        ).strip(),
        allowed_tools=EDIT_AND_TEST_TOOLS,
    ),
    "mmo-content-factory": SkillSpec(
        name="mmo-content-factory",
        description="Use when MMO operations need AI-assisted bulk content generation, multi-platform scheduling, video repurposing, variant creation, and cross-channel content distribution at scale.",
        role="mmo-content-ops",
        layer="layer-4-specialists-and-standalones",
        inputs=[
            "content briefs or raw assets (long-form video, images, article text, product info)",
            "platform account inventory and per-account quota budgets",
            "brand voice guidelines, prohibited content rules, platform-specific formatting requirements",
        ],
        outputs=["content production pipeline: generation config, variant specs, diversity rules, scheduling plan, review gates, and performance feedback schema"],
        references=[
            "Identical or near-identical content across accounts triggers spam detection — enforce minimum diversity scores between all variants.",
            "AI-generated content variants must pass a human-review gate before deployment to high-risk accounts.",
            "Platform-specific formatting is not optional: wrong aspect ratio or duration causes algorithmic reach penalty.",
            "Publishing windows must be staggered across accounts — never schedule identical content to multiple accounts simultaneously.",
            *domain_resource_references("mmo-content-factory"),
        ],
        next_steps=["mmo-reup-automation", "mmo-social-marketing-automation", "mmo-data-harvesting", "mmo-llm-automation", "growth-marketing", "qa-governor"],
        body=dedent(
            """\
            # Mission
            Run a content production pipeline that converts raw assets into platform-optimized variants and schedules them without detectable spam patterns.

            ## Mandatory scope checks
            - define content brief → variant generation pipeline: text, image, short video cuts from long-form source
            - define platform-specific output specs: TikTok (9:16, 15-60s), Facebook Reel (9:16), YouTube Shorts (<60s)
            - define variant diversity threshold: minimum edit-distance or visual-diff score between variants
            - define publishing schedule: posting windows, frequency caps per account, platform quota alignment
            - define human-review gate: content types and risk tiers requiring operator approval
            - define performance feedback loop: track per-variant reach and feed signal back into generation config

            ## Evidence contract
            - include sample batch: 1 brief → N variants with diversity diff scores
            - include publishing schedule proof: no platform quota breach across all active accounts
            - include human-review decision log for flagged content
            """
        ).strip(),
        allowed_tools=EDIT_AND_TEST_TOOLS,
    ),
    "mmo-crypto-wallet-farming": SkillSpec(
        name="mmo-crypto-wallet-farming",
        description="Use when MMO crypto operations need multi-wallet isolation, airdrop task automation, on-chain interaction scripting, and Sybil-avoidance strategy for DeFi and airdrop farming.",
        role="mmo-crypto-farming",
        layer="layer-4-specialists-and-standalones",
        inputs=[
            "wallet inventory (address, funded status, chain, proxy assignment, age, on-chain history)",
            "target protocol task list (swap, LP provision, governance vote, quest, bridge)",
            "Sybil detection signals published or known for the target project",
        ],
        outputs=["crypto farming operations plan: wallet registry, behavioral variance config, security controls, Sybil-avoidance rules, and capital risk summary"],
        references=[
            "Sybil detection in 2026 uses AI behavioral analysis — identical timing or amounts across wallets causes mass disqualification.",
            "Weekly consistent activity beats daily heavy activity for most airdrop eligibility criteria.",
            "Never use unaudited or unverified automation scripts with wallet access — seed phrase compromise causes total asset loss.",
            "Gas cost and capital risk must be explicitly budgeted before any farming campaign starts.",
            *domain_resource_references("mmo-crypto-wallet-farming"),
        ],
        next_steps=["mmo-identity-infrastructure", "mmo-proxy-network-ops", "mmo-http-api-automation", "mmo-onchain-security-audit", "policy-guard", "qa-governor"],
        body=dedent(
            """\
            # Mission
            Operate a multi-wallet crypto farming program with strict identity isolation and human-mimicking on-chain behavior.

            ## Mandatory scope checks
            - define wallet isolation: one wallet = one browser profile = one proxy = one funded identity
            - define on-chain behavioral variance: randomize swap amounts, transaction timing, gas price variation
            - define activity consistency schedule: regular low-frequency weekly interactions preferred over burst sessions
            - define security perimeter: farming wallets isolated from primary asset wallets
            - define Sybil-risk assessment per project before committing wallet resources
            - define capital budget: gas costs, minimum funding per wallet, maximum capital at risk

            ## Evidence contract
            - include wallet-to-profile-to-proxy binding registry with zero sharing verified
            - include behavioral variance config showing non-repetitive transaction patterns
            - include dry-run trace: wallet completes tasks with varied timing and amounts
            """
        ).strip(),
        allowed_tools=EDIT_AND_TEST_TOOLS,
    ),
    "mmo-data-harvesting": SkillSpec(
        name="mmo-data-harvesting",
        description="Use when MMO operations need structured data collection, lead enrichment, UID targeting list building, or AI-assisted seeding content generation within authorized access boundaries.",
        role="mmo-data-ops",
        layer="layer-4-specialists-and-standalones",
        inputs=[
            "data source inventory (API endpoints, public pages within robots.txt scope, consent form outputs)",
            "target segment criteria for each campaign type",
            "seeding campaign brief and base message templates",
        ],
        outputs=["data pipeline: collection config, enrichment rules, segmentation schema, seeding target lists, and AI content variant batches"],
        references=[
            "Only collect data through explicitly authorized channels — unauthorized PII collection is a legal risk and platform ban trigger.",
            "Deduplicate aggressively before seeding: duplicate UIDs cause redundant interactions that trigger spam detection.",
            "AI comment variants must have minimum edit distance — identical strings across seeding accounts cause immediate detection.",
            "Never store phone numbers, emails, or UIDs in plaintext — hash or encrypt all PII before storage.",
            "Route all seeding content through a human-review gate before deployment to high-value accounts.",
            *domain_resource_references("mmo-data-harvesting"),
        ],
        next_steps=["mmo-social-marketing-automation", "mmo-content-factory", "mmo-nick-warmup-engine", "mmo-reup-automation", "policy-guard"],
        body=dedent(
            """\
            # Mission
            Collect, enrich, and structure targeting data for MMO campaigns using authorized access, then generate AI content variants for seeding.

            ## Mandatory scope checks
            - define data source authorization per collection method: official API, robots.txt-compliant scraping, or consent-collected leads
            - define data schema: UID, platform handle, segment tag, interaction history, collection timestamp, source
            - define enrichment pipeline: raw collection → dedup → validation → segment tagging → encrypted storage
            - define seeding target list criteria: segment qualifications and frequency caps per campaign type
            - define AI seeding content generator config: base template → N variants with minimum diversity score
            - define retention and deletion policy: data age limits, PII encryption at rest

            ## Evidence contract
            - include data source authorization proof for each collection method
            - include enriched dataset sample with dedup count, validation pass rate, segment distribution
            - include AI variant sample: 1 base message → N variants with diversity scores
            """
        ).strip(),
        allowed_tools=EDIT_AND_TEST_TOOLS,
    ),
}


CLEANUP_SKILLS: Dict[str, SkillSpec] = {
    "execution-loop": SkillSpec(
        name="execution-loop",
        description="Use when building or fixing code iteratively and require evidence before claiming completion. Self-correcting development loop for implementation work.",
        role="developer-support",
        layer="layer-4-specialists-and-standalones",
        inputs=["story or tech-spec", "project-context", "relevant support skills"],
        outputs=["working code plus test evidence"],
        references=[
            "testing-patterns",
            "If discipline utilities are installed, use `root-cause-debugging` before repeated fix attempts.",
            "If discipline utilities are installed, use `evidence-before-completion` before claiming success.",
            "State the slice objective and expected files before each cycle so context does not rot across long loops.",
        ],
        next_steps=["test-hub", "qa-governor"],
        allowed_tools=EDIT_AND_TEST_TOOLS,
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
            - Default to plain ASCII in code, comments, tests, fixtures, and sample data unless the repo or product explicitly requires non-ASCII content.
            - Do not say done without fresh evidence from commands actually run.
            - A code-change claim is invalid when there is zero file delta and zero verification output unless the task is explicitly a no-code decision update.

            ## Failure protocol
            After three failed fix attempts, stop and question the story, architecture, or assumptions instead of thrashing.
            """
        ).strip(),
    ),
}


NATIVE_SUPPORT_SKILLS: Dict[str, SkillSpec] = {
    "project-architecture": SkillSpec(
        name="project-architecture",
        description="Use when designing a change, reviewing architectural drift, or implementing code in an unfamiliar area. Analyze the current codebase shape and maintain a living architecture reference.",
        role="architecture-support",
        layer="layer-4-specialists-and-standalones",
        inputs=["repository tree", ".relay-kit/contracts/project-context.md", ".relay-kit/contracts/architecture.md when available"],
        outputs=[".relay-kit/references/project-architecture.md"],
        references=[
            "Document what the codebase actually does today, not what the team intended six months ago.",
            "Include concrete file paths, entrypoint mapping, call graph notes, ownership, dependency direction, and a boundary table.",
        ],
        next_steps=["architect", "developer", "review-hub"],
        body=dedent(
            """\
            # Mission
            Build and maintain an accurate map of the current architecture so downstream roles stop guessing.

            ## Produce `.relay-kit/references/project-architecture.md`
            Cover:
            - entry points and execution flow
            - entrypoint-to-call graph notes for the changed path
            - layer or package structure
            - module responsibilities
            - ownership and boundary table for the modules under review
            - dependency direction and boundaries
            - architecture drift and hotspots
            - files to mirror when adding new work

            ## Working rules
            - Prefer observed runtime or code flow over folder names alone.
            - Name boundaries explicitly: controllers, services, repositories, adapters, domain logic, jobs, or scripts.
            - Flag any mismatch between the intended architecture and what the code actually does.
            - Add file paths whenever the reference names a pattern or module.
            - Mark hotspot files where unrelated features repeatedly collide.
            """
        ).strip(),
    ),
    "dependency-management": SkillSpec(
        name="dependency-management",
        description="Use when adding packages, updating libraries, or diagnosing environment drift. Capture dependency policy, lockfile usage, environment setup, and safe add-or-upgrade rules.",
        role="build-support",
        layer="layer-4-specialists-and-standalones",
        inputs=["package metadata files", "lockfiles", "toolchain config", "CI setup if present"],
        outputs=[".relay-kit/references/dependency-management.md"],
        references=[
            "Record both the official package manager and what contributors actually use day to day.",
            "Make transitive risk and pinning policy explicit.",
        ],
        next_steps=["architect", "developer", "qa-governor", "review-hub"],
        allowed_tools=EDIT_AND_TEST_TOOLS,
        body=dedent(
            """\
            # Mission
            Prevent dependency changes from becoming hidden architecture or release risk.

            ## Produce `.relay-kit/references/dependency-management.md`
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
        description="Use when building or changing API clients, webhooks, endpoints, or network-facing code. Document external service integration patterns, clients, auth, retries, and error handling.",
        role="integration-support",
        layer="layer-4-specialists-and-standalones",
        inputs=["HTTP or RPC client code", "settings or secret config", "test or mock code"],
        outputs=[".relay-kit/references/api-integration.md"],
        references=[
            "Prefer concrete service names, client classes, and endpoint groups over generic summaries.",
            "Make request id propagation, timeout budget, retries, 429 handling, idempotency, redacted logs, and error translation explicit.",
        ],
        next_steps=["architect", "developer", "qa-governor", "review-hub"],
        allowed_tools=EDIT_AND_TEST_TOOLS,
        body=dedent(
            """\
            # Mission
            Make network-facing behavior predictable so changes to API code do not become reliability surprises.

            ## Produce `.relay-kit/references/api-integration.md`
            Cover:
            - clients, transports, and endpoints
            - authentication and secret handling
            - request id or correlation id propagation
            - retry, timeout budget, 429, and idempotency rules
            - request and response patterns
            - error mapping and recovery
            - testing and mocking approach

            ## Working rules
            - Name client wrappers, service classes, or endpoint modules directly.
            - Include where auth is injected and how secrets are sourced.
            - Require redacted sample payloads when evidence includes tokens, cookies, emails, phone numbers, or account identifiers.
            - Explain how the code handles network failures, partial failures, and upstream rate limits.
            - Note what should be mocked versus tested against a real service.
            """
        ).strip(),
    ),
    "data-persistence": SkillSpec(
        name="data-persistence",
        description="Use when touching schemas, repositories, transactions, caches, or data flows. Document storage topology, models, migrations, caching, and consistency rules.",
        role="persistence-support",
        layer="layer-4-specialists-and-standalones",
        inputs=["model files", "repository or DAO code", "migration files", "cache config if present"],
        outputs=[".relay-kit/references/data-persistence.md"],
        references=[
            "Cover both primary storage and auxiliary state like caches, queues, or object stores when relevant.",
            "Document transaction boundary, isolation assumptions, rollback, backfill, and migration risks, not only happy-path structure.",
        ],
        next_steps=["architect", "developer", "qa-governor", "review-hub", "database-migration-safety"],
        allowed_tools=EDIT_AND_TEST_TOOLS,
        body=dedent(
            """\
            # Mission
            Make data changes safer by documenting where state lives, how it moves, and what can go wrong.

            ## Produce `.relay-kit/references/data-persistence.md`
            Cover:
            - stores and connection points
            - schemas, models, and repositories
            - migrations and schema evolution
            - transaction boundary and isolation assumptions
            - caching and invalidation
            - backfill and rollback plan
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
        description="Use when adding tests, updating fixtures, validating regressions, or deciding what proof is enough. Capture how the project tests code, mocks dependencies, and gathers evidence.",
        role="quality-support",
        layer="layer-4-specialists-and-standalones",
        inputs=["test folders", "test config", "fixtures or factories", "CI or local test commands"],
        outputs=[".relay-kit/references/testing-patterns.md"],
        references=[
            "Explain how to produce evidence locally, not only what frameworks exist.",
            "Map tests to risk areas and brittle zones where regressions cluster.",
        ],
        next_steps=["developer", "qa-governor", "debug-hub", "test-hub", "review-hub"],
        body=dedent(
            """\
            # Mission
            Turn the project test suite into a usable playbook for implementation and quality review.

            ## Produce `.relay-kit/references/testing-patterns.md`
            Cover:
            - frameworks and folder rules
            - fixture and factory patterns
            - mocking and dependency isolation
            - fake versus mock choice and integration boundary rules
            - async or integration testing rules
            - commands for local evidence
            - flake history, coverage gaps, and brittle areas

            ## Working rules
            - Name the real commands contributors should run for fast confidence versus deeper verification.
            - Show where fixtures, factories, and mocks live and when each should be preferred.
            - Mark the integration boundary where a fake stops being enough and a real service or contract test is required.
            - Call out unstable tests, heavy integration paths, and areas with weak coverage.
            - Tie recommendations back to risk, not just test quantity.
            """
        ).strip(),
    ),
}


def utility_provider_spec(
    name: str,
    description: str,
    outputs: list[str],
    references: list[str],
    next_steps: list[str],
    mission: str,
    tasks: list[str],
    rules: list[str],
    boundary: list[str] | None = None,
    evidence_contract: list[str] | None = None,
    paths: list[str] | None = None,
    context: str | None = None,
    allowed_tools: list[str] | None = None,
    effort: str | None = None,
) -> SkillSpec:
    body_lines = [
        "# Mission",
        mission,
        "",
    ]
    if boundary:
        body_lines.extend(["## Boundary"])
        body_lines.extend([f"- {item}" for item in boundary])
        body_lines.append("")
    body_lines.extend([
        "## Default outputs",
    ])
    body_lines.extend([f"- {item}" for item in outputs])
    if evidence_contract:
        body_lines.extend([
            "",
            "## Evidence contract",
        ])
        body_lines.extend([f"- {item}" for item in evidence_contract])
    body_lines.extend([
        "",
        "## Typical tasks",
    ])
    body_lines.extend([f"- {item}" for item in tasks])
    body_lines.extend([
        "",
        "## Working rules",
    ])
    body_lines.extend([f"- {item}" for item in rules])
    return SkillSpec(
        name=name,
        description=description,
        role="utility-provider",
        layer="layer-3-utility-providers",
        inputs=["active hub or orchestrator request", "current authoritative artifact", "only the evidence relevant to this pass"],
        outputs=outputs,
        references=references,
        next_steps=next_steps,
        body="\n".join(body_lines).strip(),
        paths=paths,
        context=context,
        allowed_tools=allowed_tools,
        effort=effort,
    )


UTILITY_PROVIDER_SKILLS: Dict[str, SkillSpec] = {
    "research": utility_provider_spec(
        name="research",
        description="Use when a hub needs fresh evidence but should retain ownership of the lane. Stateless research utility for product, market, technical, or domain questions.",
        outputs=[
            "evidence bullets appended to the active artifact",
            "assumption checks or citations for the current decision",
            "a short list of unresolved questions only when they block the next decision",
        ],
        references=["Do not own the plan; feed findings back to the current hub.", "Prefer current evidence over generic opinions."],
        next_steps=["brainstorm-hub", "plan-hub", "workflow-router"],
        mission="Gather the minimum useful research needed for the next decision, then hand control back immediately.",
        tasks=[
            "Answer the current decision question, not the whole topic.",
            "Summarize only the market, technical, or domain evidence that changes the next move.",
            "Mark which assumptions are confirmed, unconfirmed, or contradicted.",
            "Recommend the smallest next question only when uncertainty still blocks the lane.",
        ],
        rules=[
            "Write into `product-brief.md`, `PRD.md`, or the active artifact instead of creating a side quest.",
            "Separate evidence from recommendation.",
            "Name the source, provenance, and freshness whenever possible.",
            "Stop as soon as the owning hub can decide without another broad research pass.",
        ],
    ),
    "doc-pointers": utility_provider_spec(
        name="doc-pointers",
        description="Use when a hub needs exact docs fragments, file paths, or source references before deciding. Stateless docs retrieval utility.",
        outputs=[
            "doc pointers, file paths, or citations appended to the active artifact",
            "a short conflict note when documentation and implementation disagree",
        ],
        references=["Return exact doc pointers, not vague summaries.", "Prefer repo-local docs and code comments before broader sources when the task is codebase-specific."],
        next_steps=["scout-hub", "review-hub", "workflow-router"],
        mission="Find the smallest set of authoritative documentation fragments needed to unblock the lane.",
        tasks=[
            "Check repo-local docs, comments, and nearby code first when the question is codebase-specific.",
            "Locate the smallest authoritative fragment that answers the current question.",
            "Return exact file paths, anchors, or section names whenever possible.",
            "Flag contradictions between docs and implementation instead of smoothing them over.",
        ],
        rules=[
            "Citations and file paths are more valuable than long summaries.",
            "Quote or summarize only the load-bearing fragment.",
            "Format the result so the owning hub can paste it straight into the active artifact.",
            "Stop once the next skill has enough exact evidence to act safely.",
        ],
    ),
    "sequential-thinking": utility_provider_spec(
        name="sequential-thinking",
        description="Use when a hub needs structured thought without changing ownership. Stepwise reasoning utility for debugging, planning, or decomposition.",
        outputs=["ordered reasoning steps added to investigation-notes or the active artifact"],
        references=["Break work into explicit steps and checkpoints.", "Reasoning should support a decision, not become the decision owner."],
        next_steps=["debug-hub", "plan-hub", "fix-hub"],
        mission="Turn a messy question into a short sequence of evidence-backed steps.",
        boundary=[
            "Use for ordering a known problem into steps, checkpoints, or observations.",
            "Do not use for ranking competing solution options; hand that to problem-solving.",
            "Do not become the decision owner; return the sequence to the active hub.",
        ],
        evidence_contract=[
            "Input must include the active question, current artifact, and at least one known constraint or evidence source.",
            "Output must be a numbered sequence with a reason for each step and the evidence or artifact it depends on.",
            "End with the next most informative observation or test, not a completion claim.",
        ],
        tasks=["Decompose the problem into checkpoints.", "Identify what must be known before acting.", "Recommend the next most informative test or observation."],
        rules=["Keep the sequence short and testable.", "Tie each step to an artifact or evidence source.", "Do not claim completion for the lane."],
    ),
    "problem-solving": utility_provider_spec(
        name="problem-solving",
        description="Use when a hub needs hypotheses, trade-offs, or resolution paths grounded in current evidence. Option-generation and root-cause utility.",
        outputs=["options, hypotheses, and trade-offs appended to the active artifact"],
        references=["Root cause beats guess-and-patch.", "Surface trade-offs before implementation starts."],
        next_steps=["debug-hub", "plan-hub", "review-hub"],
        mission="Turn evidence into plausible options and ranked next moves.",
        boundary=[
            "Use for hypotheses, trade-offs, and option ranking after evidence exists.",
            "Do not use for step ordering or checkpoint decomposition; hand that to sequential-thinking.",
            "Do not own implementation, release, or completion verdicts.",
        ],
        evidence_contract=[
            "Input must include current evidence, constraints, and the decision that needs options.",
            "Output must separate option, supporting evidence, risk, cheapest validation, and recommended next owner.",
            "When evidence disagrees, output at least two competing models and explain which counts, order, invariants, or workflow cues each one satisfies.",
            "Mark uncertainty explicitly when evidence is weak or conflicting.",
        ],
        tasks=["Generate root-cause hypotheses.", "Compare implementation or mitigation options.", "Reconcile conflicting artifacts, counts, sequences, or human workflow cues.", "Call out the cheapest validating experiment."],
        rules=["Ground every option in evidence already collected.", "Build a workflow-level explanation when a strict diff or first-pass extraction conflicts with real-world constraints.", "State uncertainty instead of bluffing.", "Recommend escalation if the issue is really a planning problem."],
    ),
    "multimodal-evidence": utility_provider_spec(
        name="multimodal-evidence",
        description="Use when screenshots, diagrams, rendered UIs, or media artifacts contain important clues. Multimodal evidence utility.",
        outputs=["visual or media observations appended to the active artifact"],
        references=["Describe what is visible and why it matters.", "Feed observations back to the owning hub."],
        next_steps=["debug-hub", "test-hub", "review-hub"],
        mission="Translate visual or media evidence into concrete observations the active lane can use.",
        boundary=[
            "Use only when an image, video, diagram, rendered UI, or media artifact is itself the evidence.",
            "Use browser-inspector instead when the required evidence is live DOM, console, network, or performance state.",
            "Do not infer hidden behavior from visuals alone; label visible facts separately from interpretation.",
        ],
        evidence_contract=[
            "Input must identify the artifact path, source, timestamp or version, and the question being answered.",
            "Output must list visible observations, confidence, affected acceptance criteria, and follow-up checks.",
            "Reference any helper used, such as `templates/skills/multimodal-evidence/scripts/document_converter.py` or `media_optimizer.py`.",
        ],
        allowed_tools=READ_ANALYZE_TOOLS,
        tasks=["Inspect screenshots, diagrams, or logs embedded as images.", "Summarize what changed between before/after artifacts.", "Call out ambiguous areas that need manual confirmation."],
        rules=["Do not over-interpret weak signals.", "Tie observations to UI states, logs, or acceptance criteria.", "Keep the output compact and actionable."],
    ),
    "browser-inspector": utility_provider_spec(
        name="browser-inspector",
        description="Use when the active hub needs console, network, DOM, or performance observations from a web flow. Browser evidence utility.",
        outputs=["browser-side evidence appended to investigation-notes or qa-report"],
        references=["Collect evidence first, then suggest the next move.", "Capture the smallest reproducible browser path."],
        next_steps=["debug-hub", "test-hub", "review-hub"],
        mission="Collect browser-native evidence that narrows a web issue fast.",
        boundary=[
            "Use only when live browser state is needed: console, network, DOM, layout, accessibility tree, or performance.",
            "Use multimodal-evidence instead for static screenshots or media artifacts without a live browser session.",
            "Do not browse generally or claim the fix; return observations to the owning hub.",
        ],
        evidence_contract=[
            "Input must include target URL or route, repro steps, expected behavior, actual symptom, and environment when known.",
            "Output must include observed console/network/DOM/performance facts, reproduction confidence, and captured artifacts.",
            "Reference the helper used when available, such as `templates/skills/browser-inspector/scripts/console.js`, `network.js`, `snapshot.js`, or `performance.js`.",
        ],
        allowed_tools=READ_ANALYZE_TOOLS,
        tasks=["Inspect console, network, layout, and performance clues.", "Note the exact page state and reproduction path.", "Return the evidence to the owning hub."],
        rules=["Prefer reproducible steps and specific requests over general browsing notes.", "Link evidence to the failing acceptance criterion or symptom.", "Do not claim the fix; supply the evidence."],
    ),
    "repo-map": utility_provider_spec(
        name="repo-map",
        description="Use when a hub needs a quick dependency map, file tree slice, or entrypoint overview before acting. Repo-map utility.",
        outputs=[
            "repo map notes appended to project-context or architecture",
            "a short read-first file list for the next skill",
        ],
        references=["Good for unfamiliar areas and dependency direction.", "Use it to orient the lane, not to replace design thinking."],
        next_steps=["scout-hub", "plan-hub", "review-hub"],
        mission="Produce a compact map of the code area the lane is about to touch.",
        tasks=[
            "Scope the map to the area the lane is actually about to touch.",
            "List key entrypoints, modules, and dependency direction.",
            "Highlight likely impact surface (upstream callers, downstream dependencies, test touch points) when symbols are known.",
            "Highlight hotspots, choke points, or ownership boundaries.",
            "Name the first files the next skill should read instead of dumping the whole tree.",
        ],
        rules=[
            "Prefer repo-relative paths, modules, and boundaries over prose-heavy summaries.",
            "Prefer token-efficient map output over long narrative so the next skill can act in one pass.",
            "Keep the map small enough for the next skill to use immediately.",
            "If ownership is fuzzy, say so explicitly instead of inventing structure.",
            "If mapping data looks stale, mark it and route to scout-hub or index refresh before high-risk edits.",
            "Stop once the next skill can navigate without another broad repo walk.",
        ],
    ),
    "memory-search": utility_provider_spec(
        name="memory-search",
        description="Use when a hub needs past decisions, handoff breadcrumbs, or prior debug evidence from .relay-kit artifacts. Read-only state retrieval utility.",
        outputs=[
            "matching evidence excerpts from .relay-kit/state or .relay-kit/contracts appended to the active artifact",
            "a short continuity note that links current work to prior decisions",
        ],
        references=[
            "Prefer read-only retrieval from authoritative artifacts over replaying chat memory.",
            "Use `relay-kit query search <project> --query ...` for deterministic lookups.",
            "Use intent/path/freshness filters to return high-signal context in one pass instead of broad dumps.",
        ],
        next_steps=["debug-hub", "review-hub", "plan-hub", "workflow-router"],
        mission="Recover prior context quickly so the lane can reuse proven decisions and avoid repeating old mistakes.",
        tasks=[
            "Search `.relay-kit/state` and `.relay-kit/contracts` for the exact decision, failure pattern, or handoff being referenced.",
            "Use intent-aware retrieval when the lane needs decision, handoff, debug, review, or migration evidence.",
            "Return file paths and line-level excerpts that the active hub can verify immediately.",
            "Call out conflicts between older decisions and the current request instead of smoothing them over.",
            "Extract only the evidence needed for the next decision and stop.",
        ],
        rules=[
            "Stay read-only; do not rewrite artifacts during retrieval.",
            "Mark stale hits explicitly instead of mixing stale and fresh evidence silently.",
            "Cite concrete paths and lines, not vague summaries.",
            "Separate observed facts from interpretation when prior context is noisy.",
            "If no evidence is found, say so explicitly and route to fresh investigation instead of guessing.",
        ],
    ),
    "release-readiness": utility_provider_spec(
        name="release-readiness",
        description="Use when a lane needs a pre-deploy or post-deploy readiness verdict with explicit smoke signals and rollback guardrails.",
        outputs=[
            "release-readiness checklist notes appended to qa-report or workflow-state",
            "explicit go, hold, or rollback recommendation tied to machine-checkable signals",
        ],
        references=[
            "Use `relay-kit release readiness <project> --phase pre|post` for deterministic checklists and signal evaluation.",
            "Treat `ready-check` as review readiness, not automatic production readiness.",
        ],
        next_steps=["test-hub", "review-hub", "qa-governor", "workflow-router", "ci-cd-pipeline"],
        mission="Convert release confidence into concrete pre and post deploy evidence instead of relying on optimistic completion claims.",
        tasks=[
            "Run a pre-deploy gate for build, tests, migration risk, and rollback plan status.",
            "Run a post-deploy smoke gate for health, error budget, and critical path behavior.",
            "Record which checks are observed, inferred, or still missing.",
            "Escalate hold or rollback when a critical signal fails.",
        ],
        rules=[
            "No go recommendation without machine-checkable evidence for critical signals.",
            "Keep pre and post deploy verdicts separate to avoid false confidence.",
            "If evidence is incomplete, return hold by default and list the exact missing signals.",
            "Document rollback trigger thresholds before calling a deploy safe.",
        ],
        allowed_tools=READ_ANALYZE_TOOLS,
    ),
    "accessibility-review": utility_provider_spec(
        name="accessibility-review",
        description="Use when frontend work needs an explicit accessibility gate before merge, release, or completion claims.",
        outputs=[
            "accessibility gate findings appended to qa-report or review notes",
            "pass or hold verdict tied to keyboard, semantics, focus, and contrast evidence",
        ],
        references=[
            "Use `relay-kit accessibility review <project>` to generate or evaluate the gate checklist.",
            "Treat accessibility as a required quality bar, not cosmetic polish.",
        ],
        next_steps=["test-hub", "review-hub", "qa-governor", "fix-hub"],
        mission="Turn accessibility from implicit best effort into a concrete review gate with machine-checkable status.",
        tasks=[
            "Check keyboard navigation, visible focus, semantic structure, labels, and contrast before claiming readiness.",
            "Record critical failures and map each one to affected screen or component paths.",
            "Return a hold verdict when critical accessibility evidence is missing.",
            "Hand unresolved findings back to fix-hub with explicit acceptance criteria.",
        ],
        rules=[
            "No pass verdict without evidence for all critical checks.",
            "Do not collapse accessibility into generic UI comments.",
            "Keep findings actionable: component, behavior, impact, and expected fix.",
            "If manual verification is needed, say exactly what to test and why.",
        ],
        allowed_tools=READ_ANALYZE_TOOLS,
    ),
    "skill-gauntlet": utility_provider_spec(
        name="skill-gauntlet",
        description="Use when runtime skill behavior may have drifted and you need a regression gate before trusting routing or completion claims.",
        outputs=[
            "skill behavior regression findings appended to qa-report or workflow-state",
            "explicit pass or hold verdict for SKILL.md trigger and structure discipline",
        ],
        references=[
            "Use `relay-kit skill gauntlet <project> --strict` for machine-checkable gating.",
            "Run this before promoting large skill edits, bundle changes, or release branches.",
        ],
        next_steps=["review-hub", "qa-governor", "workflow-router", "fix-hub"],
        mission="Protect routing quality by detecting skill drift early instead of waiting for behavior regressions in live lanes.",
        tasks=[
            "Validate SKILL.md frontmatter, trigger descriptions, and required section structure across runtime surfaces.",
            "Report malformed or stale skill files with concrete paths and checks.",
            "Gate release or migration work when skill quality checks fail.",
            "Hand failures to fix-hub with exact remediation targets.",
        ],
        rules=[
            "Treat skill behavior regressions as release risk, not optional cleanup.",
            "Prefer deterministic checks over subjective style review.",
            "Fail fast when trigger wording or core sections drift from required structure.",
            "Keep the gauntlet report small and path-specific so fixes are easy to apply.",
        ],
        allowed_tools=READ_ANALYZE_TOOLS,
    ),
    "signal-calibration": utility_provider_spec(
        name="signal-calibration",
        description="Use when a claim risks being overrated, guessed, or stronger than the available evidence. Calibrate readiness, skill quality, field-tested, production-ready, commercial-ready, backend realism, UI realism, MMO/API realism, or benchmark claims before accepting them.",
        outputs=[
            "signal calibration report with claim, claim_type, proof_level, verdict, confidence, overclaim flags, residual risk, and next verification",
            "explicit pass or hold verdict for overclaim-prone wording before readiness, release, quality, or benchmark claims",
            "claim-to-evidence notes appended to qa-report, workflow-state, or release artifacts",
        ],
        references=[
            "Use `relay-kit calibrate readiness <project> --strict` for enterprise readiness claim calibration.",
            "Use `relay-kit calibrate skill <project> --skill all --strict` before claiming skill quality.",
            "Use `relay-kit calibrate claims <project> --claim \"...\" --strict` when exact wording needs proof.",
            "Do not call fixture validation field-tested; field-tested requires `.relay-kit/evidence/skill-field-evidence.json`.",
        ],
        next_steps=["evidence-before-completion", "qa-governor", "review-hub", "skill-gauntlet", "release-readiness"],
        mission="Turn confident-sounding claims into calibrated proof levels so Relay-kit does not overrate itself or the work it produces.",
        boundary=[
            "Use for claim calibration and overclaim detection, not for running the whole QA lane.",
            "Do not replace evidence-before-completion for narrow completion proof or qa-governor for formal readiness verdicts.",
            "Do not treat local fixtures, public repo benchmarks, or read-only audits as field validation.",
        ],
        evidence_contract=[
            "Input must include the exact claim or the report surface being calibrated.",
            "Output must include `claim`, `claim_type`, `proof_level`, `verdict`, `confidence`, `evidence_sources`, `overclaim_flags`, `residual_risk`, and `next_verification`.",
            "Claims without concrete file, command, log, source, or artifact evidence must be marked inferred or unsupported.",
            "Field-tested, production-ready, and commercial-ready wording must be blocked unless the required evidence class exists.",
        ],
        tasks=[
            "Classify claims as proven, partially-proven, inferred, unsupported, or contradicted.",
            "Map skill quality claims to proof audit, real-world eval, skill-battle, competency-battle, or battle-audit evidence.",
            "Downgrade fixture-backed claims to validated instead of field-tested.",
            "Detect public copy or operator answers that imply stronger evidence than Relay-kit actually has.",
            "Name the smallest next verification needed to make the claim safe.",
        ],
        rules=[
            "Confidence is not proof.",
            "Benchmark evidence is not adoption evidence.",
            "Validated is not field-tested.",
            "If evidence class is unclear, block the claim instead of smoothing it over.",
            "Keep Relay-kit-owned terminology; do not call this a confusion matrix.",
        ],
        allowed_tools=READ_ANALYZE_TOOLS,
    ),
    "impact-radar": utility_provider_spec(
        name="impact-radar",
        description="Use when planning or review needs explicit blast-radius analysis before touching runtime, adapters, templates, or release-sensitive surfaces.",
        outputs=[
            "impact-area and changed-file breakdown appended to workflow-state or review notes",
            "risk level plus recommended verification gates for the current diff",
        ],
        references=[
            "Use `relay-kit impact radar <project>` for deterministic working-tree analysis.",
            "Use `--base` and `--head` when the lane needs commit-range impact evidence for review.",
        ],
        next_steps=["plan-hub", "review-hub", "qa-governor", "workflow-router"],
        mission="Make change blast radius explicit before merge so gate selection is evidence-based instead of guess-based.",
        tasks=[
            "Classify changed files into runtime, adapter, scripts, templates, docs, and packaging impact areas.",
            "Return a compact risk level with the concrete reason it was assigned.",
            "Recommend the smallest gate set that still protects migration and runtime safety.",
            "Highlight high-impact areas that need additional manual review before merge.",
        ],
        rules=[
            "Use file-based evidence from git diff or working tree status; avoid speculative risk claims.",
            "Keep recommendations command-ready so the owning hub can execute immediately.",
            "Do not approve merges; provide impact evidence and required gates.",
            "Escalate to review-hub or qa-governor when impact spans runtime-core and adapter surfaces.",
        ],
    ),
    "runtime-doctor": utility_provider_spec(
        name="runtime-doctor",
        description="Use when runtime integrity may have drifted and you need deterministic diagnostics over adapters, artifacts, and lane state surfaces.",
        outputs=[
            "runtime drift findings with exact surface references appended to qa-report or workflow-state",
            "pass or hold recommendation for runtime health based on parity and artifact checks",
        ],
        references=[
            "Use `relay-kit runtime doctor <project> --strict` for deterministic runtime diagnostics.",
            "Use `--state-mode live` when validating active project state artifacts before release claims.",
        ],
        next_steps=["debug-hub", "test-hub", "review-hub", "fix-hub"],
        mission="Catch adapter parity and runtime artifact drift early so regressions are blocked before release or cutover batches.",
        tasks=[
            "Verify required runtime docs and state artifacts exist under `.relay-kit`.",
            "Check adapter skill parity against canonical registry skills across `.claude`, `.agent`, and `.codex` surfaces.",
            "Flag missing, extra, or drifted skills with exact adapter paths.",
            "In live mode, detect stale placeholder state markers that invalidate readiness claims.",
        ],
        rules=[
            "Keep findings deterministic and path-specific so reruns are comparable.",
            "Distinguish template diagnostics from live runtime diagnostics in the final report.",
            "Do not auto-fix runtime drift; hand actionable findings back to fix-hub.",
            "Return hold when strict checks fail on parity or required artifacts.",
        ],
        allowed_tools=READ_ANALYZE_TOOLS,
    ),
    "migration-guard": utility_provider_spec(
        name="migration-guard",
        description="Use when a naming cutover might leave stale compatibility tokens behind. Enforce token-level cutover policy with a strict fail-closed gate.",
        outputs=[
            "cutover token drift findings appended to qa-report or workflow-state",
            "explicit pass or hold verdict for migration safety before merge",
        ],
        references=[
            "Use `relay-kit migration guard <project> --strict` as the canonical naming gate.",
            "Guard verdict is fail-closed: findings require cleanup before merge.",
        ],
        next_steps=["test-hub", "review-hub", "qa-governor", "fix-hub"],
        mission="Block high-risk migration drift by proving old compatibility markers are gone from active runtime surfaces.",
        tasks=[
            "Scan source and runtime files for blocked compatibility tokens.",
            "Flag every occurrence with file, line, and token evidence.",
            "Hold the lane when findings exist in active runtime or gate paths.",
            "Hand actionable findings back to fix-hub with exact cleanup targets.",
        ],
        rules=[
            "Do not suppress active runtime drift through exceptions or soft bypasses.",
            "Run migration-guard before merge on every cutover batch touching runtime names or paths.",
            "Keep findings deterministic so repeated runs produce stable verdicts.",
        ],
        allowed_tools=READ_ANALYZE_TOOLS,
    ),
    "policy-guard": utility_provider_spec(
        name="policy-guard",
        description="Use when high-risk agent operations need deterministic policy checks before trusting shell, path, secret, prompt, or allowlist changes, with a strict fail-closed posture.",
        outputs=[
            "policy risk findings appended to qa-report or workflow-state",
            "explicit pass or hold verdict for high-risk runtime operations",
        ],
        references=[
            "Use `relay-kit policy check <project> --strict` as the canonical policy gate.",
            "Treat policy findings as release blockers until reviewed by qa-governor or review-hub.",
        ],
        next_steps=["qa-governor", "review-hub", "fix-hub", "offensive-security-engagement"],
        mission="Fail closed on deterministic high-risk agent operation patterns before they reach release or handoff.",
        tasks=[
            "Scan runtime and source surfaces for path traversal, destructive shell commands, hard-coded secrets, and prompt-injection phrases.",
            "Report exact file, line, and check names so the owning hub can fix or explicitly escalate.",
            "Rerun the strict policy gate after any remediation before claiming the lane is safe.",
            "Apply fail-closed handling whenever risk classification is uncertain.",
        ],
        rules=[
            "Do not treat policy findings as cosmetic lint.",
            "Prefer fixing the risky surface over allowlisting it.",
            "Escalate to review-hub when a finding is intentional but operationally sensitive.",
            "Cooperation contract with offensive-security-engagement: policy-guard is fail-closed for secrets, shell, and path risk. offensive-security-engagement is fail-open-for-authorized for offensive techniques. When both are active in the same lane, policy-guard runs LAST as a post-execution gate, not as a pre-execution block on authorized offensive actions. Do not block offensive actions that have a valid engagement_proof in workflow-state.",
        ],
        allowed_tools=READ_ANALYZE_TOOLS,
    ),
    "token-economy": utility_provider_spec(
        name="token-economy",
        description="Use when context is large and the lane needs deterministic token budgeting, context packing, and signal retention checks before execution.",
        outputs=[
            "token budget, task-scoped context pack, or token audit report artifacts under .relay-kit/context or .relay-kit/token",
            "explicit raw-required blocks and raw pointers for failing evidence",
            "budget violation findings with keep/drop decisions and retention metrics",
        ],
        references=[
            "Use `relay-kit context budget`, `relay-kit context pack`, and `relay-kit token audit` as canonical entrypoints.",
            "Never hide failing command details without a raw path pointer.",
            "Fail open to raw-required when signal retention is uncertain.",
        ],
        next_steps=["workflow-router", "context-continuity", "handoff-context", "review-hub", "qa-governor"],
        mission="Reduce context cost without reducing execution signal quality.",
        tasks=[
            "Estimate raw and packed token size with deterministic `ceil(len(text)/4)` accounting.",
            "Classify context blocks as raw-required, compressible, or summary-only.",
            "Build a task-scoped context pack with authority and freshness ranking plus max-tokens enforcement.",
            "Preserve raw pointers for failure-heavy evidence such as error, traceback, assertion, or exit-code blocks.",
            "Report budget violations and retention metrics before handing context to implementation lanes.",
        ],
        rules=[
            "Do not drop critical failure evidence.",
            "Signal retention must remain 1.0 in strict mode.",
            "If uncertain, keep the block raw-required and mark why.",
            "Record both selected and dropped context sources so downstream lanes can rehydrate if needed.",
        ],
        allowed_tools=READ_ANALYZE_TOOLS,
    ),
    "context-continuity": utility_provider_spec(
        name="context-continuity",
        description="Use when work needs reliable continuity across long chats, new threads, AI switches, or resume-after-gap sessions.",
        outputs=[
            "checkpoint, rehydrate, handoff, or diff artifacts under .relay-kit/state and .relay-kit/handoffs",
            "a compact resume brief with explicit next step and open loops",
        ],
        references=[
            "Use `relay-kit continuity auto <project> --phase start|resume|before-final|handoff` as the default lifecycle gate.",
            "Use manual `checkpoint`, `rehydrate`, `handoff`, and `diff-since-last` modes when debugging or forcing a specific continuity action.",
            "Context continuity complements `handoff-context`; it does not replace authoritative contracts and state.",
        ],
        next_steps=["workflow-router", "cook", "handoff-context", "review-hub"],
        mission="Preserve lane continuity with explicit artifacts so the next session can continue safely without replaying full chat history.",
        tasks=[
            "Run auto continuity at session start/resume so existing checkpoints are rehydrated and missing checkpoints are created.",
            "Run checkpoint before likely truncation, compaction, or session break.",
            "Run rehydrate at the start of a new thread to restore objective, lane, blockers, and next step.",
            "Run handoff when ownership moves across AI, thread, or operator.",
            "Run diff-since-last to detect drift from the most recent checkpoint snapshot.",
        ],
        rules=[
            "Separate observed evidence from inferred context in all continuity outputs.",
            "Do not call continuity complete if next step, blockers, and evidence pointers are missing.",
            "Treat continuity artifacts as append-first records; avoid destructive rewrites.",
            "If continuity conflicts with current repo reality, escalate through workflow-router before coding.",
        ],
    ),
    "handoff-context": utility_provider_spec(
        name="handoff-context",
        description="Use when the next skill needs a tighter, more relevant context handoff than the current artifact already provides. Context-pack utility.",
        outputs=[
            "focused context pack notes added to workflow-state, story, or handoff-log",
            "an explicit include/exclude list for the receiving skill",
        ],
        references=[
            "Minimize irrelevant context.",
            "Package only what the receiving skill needs to act safely.",
            "Use context-continuity when the handoff must survive a session boundary.",
        ],
        next_steps=["workflow-router", "cook", "developer", "context-continuity"],
        mission="Prepare the smallest complete context pack for the next handoff.",
        tasks=[
            "Select the minimum set of files, artifacts, and rules the receiving skill actually needs.",
            "Include impact-critical dependencies and known risk edges so the receiver does not rediscover blast radius.",
            "State why each included item matters.",
            "Name what was deliberately excluded and why it is safe to ignore for now.",
            "Write a short receiving-skill brief so the next handoff starts cleanly.",
        ],
        rules=[
            "Context quality beats context quantity.",
            "Use authoritative artifacts over memory.",
            "Update handoff-log when the receiving skill changes.",
            "Call out stale context explicitly before handoff completion.",
            "Stop when the receiving skill can act without reopening the whole repo or replaying the whole chat.",
            "Escalate to context-continuity when the receiving lane needs durable checkpoint and rehydrate artifacts.",
        ],
    ),
    "mermaid-diagrams": utility_provider_spec(
        name="mermaid-diagrams",
        description="Use when architecture, flow, or sequencing should be expressed as a quick mermaid diagram inside an artifact. Diagramming utility.",
        outputs=["mermaid snippets inserted into architecture, project-context, or docs"],
        references=["Prefer diagrams that clarify ownership, flow, or sequencing.", "Diagrams should serve the artifact, not replace it."],
        next_steps=["plan-hub", "architect", "review-hub"],
        mission="Make complex flow or structure easier to reason about with a compact diagram.",
        tasks=["Draw module boundaries or request flows.", "Show sequence or state transitions.", "Keep the diagram synchronized with the surrounding text."],
        rules=["Use only the detail level needed for the current decision.", "Avoid giant diagrams.", "Explain trade-offs in text when the diagram alone is insufficient."],
    ),
    "ux-structure": utility_provider_spec(
        name="ux-structure",
        description="Use when a hub needs sharper information hierarchy, cleaner flows, stronger screen structure, less generic AI-looking UI, or concrete UX corrections tied to implementation reality. UX and layout utility for user-facing work.",
        outputs=[
            "ux notes appended to product-brief, PRD, architecture, or qa-report",
            "recommended taste controls for design variance, motion intensity, and visual density",
            "state coverage notes for loading, empty, and error handling when the surface is real product UI",
        ],
        references=[
            "Use this skill to block AI-slop layouts, not merely to polish them.",
            "Prefer reference-driven direction, explicit hierarchy, and deliberate grid structure over generic SaaS template patterns.",
            "Return notes to the owning hub rather than taking over the project.",
        ],
        next_steps=["brainstorm-hub", "plan-hub", "review-hub"],
        mission="Sharpen hierarchy, flow, and design taste without stealing ownership from product or implementation lanes.",
        tasks=[
            "Outline the user journey or interaction flow.",
            "Set design variance, motion intensity, and visual density for the current slice before recommending layout changes.",
            "Call out friction, edge cases, copy issues, and template-like structure.",
            "Require loading, empty, and error states when the surface is a real product flow.",
            "Replace generic three-card layouts, filler gradients, and flex-hack compositions with stronger structure.",
        ],
        rules=[
            "Tie UX comments to a specific screen or step.",
            "Balance UX gains with implementation cost.",
            "Keep notes focused on the current slice.",
            "Do not approve purple-blue gradient filler, three-equal-card SaaS layouts, or layout choices that feel obviously AI-generated.",
            "Prefer grid layout or deliberate asymmetry over flex hacks when hierarchy matters.",
            "Keep motion performance-safe: prefer transform and opacity, and respect reduced-motion needs.",
        ],
    ),
    "media-tooling": utility_provider_spec(
        name="media-tooling",
        description="Use when screenshots, assets, or content files need transformation or evidence extraction for the current lane. Media handling utility.",
        outputs=["media processing notes or asset instructions appended to the active artifact"],
        references=["Useful for evidence packaging and asset-heavy workflows.", "Should stay stateless and task-scoped."],
        next_steps=["test-hub", "review-hub", "ux-structure"],
        mission="Handle media-specific steps that support the current lane without creating a parallel project.",
        allowed_tools=EDIT_AND_TEST_TOOLS,
        tasks=["Prepare screenshots or assets for evidence.", "Describe required transforms or formats.", "Hand back what the next skill needs to continue."],
        rules=["Keep transformations reversible when possible.", "Name exact asset sources and outputs.", "Route any broader UX or product decisions back to the owning hub."],
    ),
}


DISCIPLINE_UTILITY_SKILLS: Dict[str, SkillSpec] = {
    "root-cause-debugging": utility_provider_spec(
        name="root-cause-debugging",
        description="Use when a hub needs a disciplined investigation before proposing fixes. Structured root-cause debugging utility.",
        outputs=["root-cause notes and disproven hypotheses appended to investigation-notes or the active artifact"],
        references=["No fixes before investigation.", "Prefer evidence at component boundaries over guessed explanations."],
        next_steps=["debug-hub", "fix-hub", "test-hub"],
        mission="Force a root-cause-first debugging pass so the lane stops guessing and starts proving.",
        tasks=["Read the failure carefully and restate the symptom.", "Trace the issue through the narrowest useful chain of evidence.", "Record likely cause, non-causes, and the smallest validating next move."],
        rules=["Do not recommend fixes before the evidence is good enough to reject obvious alternatives.", "Prefer one hypothesis at a time.", "Escalate back to planning when the issue is really a requirements or architecture mismatch."],
        allowed_tools=READ_ANALYZE_TOOLS,
    ),
    "test-first-development": utility_provider_spec(
        name="test-first-development",
        description="Use when implementation should follow a red-green-refactor loop instead of ad-hoc coding. Test-first execution utility.",
        outputs=["test-first execution notes and evidence appended to story, tech-spec, or qa-report"],
        references=["Write the failing test first when the behavior is testable.", "Keep the change minimal until the new test is green."],
        next_steps=["developer", "test-hub", "qa-governor"],
        mission="Drive implementation through the smallest useful red-green-refactor loop.",
        tasks=["Name the behavior that should fail first.", "Capture the failing test or reproduction evidence.", "Implement only enough to turn the signal green before cleanup."],
        rules=["If the behavior cannot be tested first, say why instead of pretending the loop happened.", "Keep one behavior per cycle.", "Keep tests, fixtures, and sample payloads plain ASCII unless the behavior explicitly depends on non-ASCII content.", "Do not widen scope during the green phase."],
        allowed_tools=EDIT_AND_TEST_TOOLS,
    ),
    "evidence-before-completion": utility_provider_spec(
        name="evidence-before-completion",
        description="Use when a hub or specialist has specific completion claims to verify. Map each claim to fresh proof output before saying work is done, fixed, or ready. Claim-to-evidence utility.",
        outputs=["fresh claim-to-evidence checks and proof output appended to workflow-state or the active artifact"],
        references=["No completion claims without fresh verification output.", "Match every claim to the command or evidence that proves it.", "Hand formal readiness verdicts to qa-governor or ready-check."],
        next_steps=["test-hub", "qa-governor", "review-hub"],
        mission="Stop premature completion claims by forcing a claim-to-evidence check.",
        boundary=[
            "Use for specific completion claims that need proof output.",
            "This is not a readiness verdict and does not decide shipability.",
            "This utility does not own `qa-report.md`; qa-governor owns formal QA reports and go or no-go recommendations.",
        ],
        evidence_contract=[
            "Input must include the exact claims being made and the newest available evidence.",
            "Output must map each claim to a command, artifact, or observed proof output.",
            "Offensive claim mapping required:\n"
            '  - "Evasion successful" -> requires sandbox/VM detonation trace showing no alert.\n'
            '  - "Telemetry blinded" -> requires raw log export showing absence of events.\n'
            '  - "Antibot bypassed" -> requires HTTP 200 payload or clearance cookie screenshot.\n'
            '  - "C2 stealth" -> requires PCAP/network trace matching mimicry profile.\n'
            '  - "Wallet safe" -> requires fork-simulation trace output.',
            "Reject any claim without fresh evidence and route back to testing or debugging.",
        ],
        tasks=[
            "List the exact claims being made.",
            "Name the command, artifact, or proof output that proves each claim.",
            "Check whether expected artifact deltas actually exist for code-change claims.",
            "Reject claims that are not backed by fresh evidence.",
        ],
        rules=[
            "Confidence is not evidence.",
            "Partial verification is not completion.",
            "If evidence is stale or missing, route back to testing or debugging instead of approving the lane.",
            "If a code-change claim has zero file delta and zero verification output, mark it invalid unless the lane explicitly recorded a no-code outcome.",
        ],
    ),
    "scope-discipline": utility_provider_spec(
        name="scope-discipline",
        description="Use when a task risks over-engineering, unnecessary abstraction, repeated reasoning, or scope growth. Apply a minimum-complete-contract check before adding complexity.",
        outputs=[
            "a minimum-complete-contract decision in the active artifact",
            "a keep/remove/defer list for proposed complexity",
            "a smallest useful verification plan",
        ],
        references=[
            "Prefer the smallest change that satisfies the stated acceptance criteria.",
            "Treat extra abstractions, wrappers, agents, dependencies, and documentation as costs requiring evidence.",
            "Use evidence-before-completion for the final claim; this skill only controls scope and complexity.",
        ],
        next_steps=["developer", "test-hub", "review-hub", "qa-governor"],
        mission="Prevent over-engineering by proving each added unit of complexity earns its maintenance and token cost.",
        boundary=[
            "Use before widening a design, adding an abstraction, increasing a reasoning budget, or introducing orchestration.",
            "Do not block necessary safety, correctness, accessibility, or compliance controls.",
            "Do not replace architecture or readiness review when those decisions are explicitly required.",
        ],
        evidence_contract=[
            "Input must name the acceptance criteria, current implementation surface, and proposed complexity.",
            "Output must classify each proposed addition as required, justified, deferred, or removed with one evidence reason.",
            "Output must include a stopping rule and the cheapest verification that can falsify the minimal design.",
        ],
        tasks=[
            "Write the minimum complete contract in one or two sentences.",
            "List existing code, tools, skills, or state that already satisfies part of the request.",
            "Subtract wrappers, abstractions, dependencies, repeated prompts, and parallel lanes unless a concrete gap remains.",
            "Set a bounded reasoning and verification budget proportional to risk; stop when the contract and proof pass.",
        ],
        rules=[
            "No new abstraction without a named caller, invariant, or failing test that needs it.",
            "No extra agent, loop, or research pass when the primary Sol context can complete the next bounded step.",
            "Do not trade correctness for brevity; preserve raw failure evidence and hard safety gates.",
            "When uncertain, defer optional complexity and record the trigger that would justify revisiting it.",
        ],
        allowed_tools=READ_ANALYZE_TOOLS,
    ),
    "skill-evolution": utility_provider_spec(
        name="skill-evolution",
        description="Use when creating, upgrading, reviewing, or pruning a Relay-kit SKILL.md. Audit trigger descriptions, paths frontmatter, allowed tools, handoff contract, and scenario fixtures before changing skill behavior.",
        outputs=[
            "skill delta notes appended to tech-spec, qa-report, or the active artifact",
            "frontmatter and trigger audit for every changed skill",
            "scenario fixture or gauntlet evidence proving routing behavior",
        ],
        references=[
            "Treat SKILL.md as a progressively disclosed command surface, not generic documentation.",
            "Prefer path-scoped activation, forked context, and tight tool profiles for specialized or high-risk skills.",
            "Do not copy external skill names or prompts; translate proven patterns into Relay-kit-owned names and contracts.",
        ],
        next_steps=["skill-gauntlet", "workflow-router", "review-hub"],
        mission="Evolve Relay-kit skills as versioned runtime capabilities with explicit trigger, frontmatter, handoff, and regression evidence.",
        boundary=[
            "Use for changes to generated skills, skill registry entries, skill docs, or skill routing fixtures.",
            "Do not own broad product planning; return to plan-hub when the skill change implies a new product surface.",
            "Do not ship a skill change without a route or gauntlet proof unless the change is docs-only and clearly marked.",
        ],
        evidence_contract=[
            "Input must include the skill names or skill folders under review and the reason behavior should change.",
            "Output must classify each skill delta as add, update, merge, prune, or leave unchanged.",
            "Every changed trigger must name the scenario, prompt shape, expected skill, and evidence command.",
            "Every high-risk skill must name its allowed tool profile or explain why tool scoping is not supported by the adapter.",
        ],
        tasks=[
            "Read the current SKILL.md, registry spec, and generated adapter copy before proposing edits.",
            "Check trigger specificity, duplicate trigger noise, likely next-step validity, inputs, outputs, and handoff ownership.",
            "Add or update path-scoped frontmatter when a skill only makes sense for certain files.",
            "Use forked context guidance for exploratory, review-heavy, or report-heavy skill work that should not pollute the main lane.",
            "Update semantic fixtures or focused tests so routing drift is caught before release.",
        ],
        rules=[
            "Keep skill names Relay-kit-owned and distinct from external projects even when a pattern was inspired elsewhere.",
            "Short frontmatter beats long body text for activation quality.",
            "A thin skill should be merged, aliased, or given a concrete evidence contract instead of staying vague.",
            "A skill that can invoke shell, file edits, or external tools needs an explicit permission or allowed-tools stance.",
            "Record source patterns as evidence, but write new Relay-kit instructions in Relay-kit terminology.",
        ],
        paths=["**/SKILL.md", "relay_kit_v3/registry/skills.py", "docs/relay-kit-skill-*.md"],
        context="fork",
        allowed_tools=EDIT_AND_TEST_TOOLS,
        effort="high",
    ),
}

BASELINE_APPROVED_DISCIPLINE_SKILLS: Dict[str, SkillSpec] = {
    "root-cause-debugging": DISCIPLINE_UTILITY_SKILLS["root-cause-debugging"],
    "evidence-before-completion": DISCIPLINE_UTILITY_SKILLS["evidence-before-completion"],
    "scope-discipline": DISCIPLINE_UTILITY_SKILLS["scope-discipline"],
}


ROUND2_CORE_ORDER = [
    "workflow-router",
    "analyst",
    "pm",
    "architect",
    "scrum-master",
    "qa-governor",
]

CORE_SKILLS: Dict[str, SkillSpec] = {
    name: (ORCHESTRATOR_SKILLS | ROLE_SKILLS)[name] for name in ROUND2_CORE_ORDER
}

OFFENSIVE_TOOL_PACK_SKILLS: Dict[str, SkillSpec] = {
    "advanced-python-engineering": SkillSpec(
        name="advanced-python-engineering",
        description="Use when Python work requires advanced patterns: async I/O, ctypes/cffi interop, metaprogramming, C extension modules, performance optimization, or large-scale automation architecture.",
        role="python-specialist",
        layer="layer-4-specialists-and-standalones",
        inputs=[
            "story or tech-spec",
            "Python version target",
            "existing codebase if present",
        ],
        outputs=[
            "Python implementation",
            "dependency list",
            "error handling docs",
        ],
        references=[
            "Never mix async and sync I/O in the same call chain without explicit bridging.",
            "Document ctypes signatures with the original C header.",
            "Use type hints for all public interfaces.",
            "Pin dependency versions — floating requirements cause reproducibility failures.",
            "Open `references/advanced-python-engineering-operator-contract.md` when scope, evidence, or operator safety is unclear.",
            "Use `examples/advanced-python-engineering-good-output.md` and `examples/advanced-python-engineering-bad-output.md` to calibrate output quality.",
            "Use `evals/advanced-python-engineering-cases.json` as the minimum scenario set for behavior regression checks.",
            "Use `competencies/advanced-python-engineering-competencies.json` to check covered competencies, failure traps, and unknown-domain policy.",
        ],
        next_steps=[
            "advanced-python-engineering",
            "mmo-llm-automation",
            "mmo-http-api-automation",
            "antibot-challenge-solving",
            "terminal-operator-ui",
            "field-journal-evolution",
        ],
        body=dedent(
            """\
            # Mission
            Implement robust, performant, and idiomatic Python for automation, interop, or large-scale scripting with explicit architecture and error discipline.
            
            ## Mandatory scope
            1. Declare Python version and async model (asyncio/trio/anyio or sync).
            2. For ctypes/cffi: document C signature, calling convention, and error propagation.
            3. For async: identify event loop, cancellation points, and timeout strategy.
            4. For metaprogramming: document __dunder__ contracts and descriptor protocol usage.
            5. Name external dependencies with version pins.
            6. Include error hierarchy: which exceptions are recoverable vs fatal.
            
            ## Evidence contract
            - Python version and async model declared
            - ctypes signatures documented with C source
            - Error hierarchy written explicitly
            - Dependency list with versions
            """
        ).strip(),
        allowed_tools=["Read", "Write", "Edit", "Grep", "Glob", "Bash"],
    ),
    "antibot-challenge-solving": SkillSpec(
        name="antibot-challenge-solving",
        description="Use when automation hits bot detection challenges: Cloudflare Turnstile/Bot Fight Mode, Datadome, PerimeterX, reCAPTCHA v2/v3/Enterprise, hCaptcha, or custom JS challenges.",
        role="antibot-specialist",
        layer="layer-4-specialists-and-standalones",
        inputs=[
            "challenge URL / challenge type",
            "automation context",
            "fingerprint profile if available",
        ],
        outputs=[
            "challenge bypass implementation",
            "clearance cookies or tokens",
            "verification result",
        ],
        references=[
            "Never call this skill from inside mmo-browser-fleet-automation — layer separation is mandatory.",
            "Document solve-rate throttle to protect API keys from bans.",
            "Verify bypass with actual HTTP response, not assumption.",
            "If challenge is unsolvable, escalate to protocol-fingerprint-spoofing or browser-fingerprint-engineering first.",
            "Open `references/antibot-challenge-solving-operator-contract.md` when scope, evidence, or operator safety is unclear.",
            "Use `examples/antibot-challenge-solving-good-output.md` and `examples/antibot-challenge-solving-bad-output.md` to calibrate output quality.",
            "Use `evals/antibot-challenge-solving-cases.json` as the minimum scenario set for behavior regression checks.",
            "Use `competencies/antibot-challenge-solving-competencies.json` to check covered competencies, failure traps, and unknown-domain policy.",
        ],
        next_steps=[
            "protocol-fingerprint-spoofing",
            "browser-fingerprint-engineering",
            "mmo-http-api-automation",
            "test-hub",
            "field-journal-evolution",
        ],
        body=dedent(
            """\
            # Mission
            Bypass or solve bot detection challenges while preserving automation flow integrity.
            
            ## Mandatory scope
            1. Identify challenge type: CAPTCHA (reCAPTCHA/hCaptcha/Turnstile), JS challenge (Cloudflare 5-second), behavioral score, or bot fingerprint gate.
            2. Choose solving approach:
               - CAPTCHA: 2captcha/CapMonster API (paid solver) or in-process ML model
               - JS challenge: Cloudflare clearance cookie via headless with correct fingerprint
               - Behavioral score: humanized interaction sequence
               - Fingerprint gate: protocol-fingerprint-spoofing + browser-fingerprint-engineering
            3. Rate limit: implement solve-rate throttle to avoid solver API bans.
            4. Layer separation: this skill is called from OUTSIDE mmo-browser-fleet-automation, not from inside (fleet has evasion prohibition rule).
            5. Verify bypass: HTTP 200 with expected content, no redirect to challenge page.
            
            ## Evidence contract
            - challenge type identified
            - solving approach documented
            - bypass verified (HTTP 200 or cookie extracted)
            - solve-rate throttle configured
            - layer separation from fleet maintained
            """
        ).strip(),
    ),
    "attack-chain-orchestration": SkillSpec(
        name="attack-chain-orchestration",
        description="Use when planning or orchestrating a multi-phase authorized attack chain: from initial recon through execution, persistence, lateral movement, collection, and cleanup.",
        role="attack-chain-planner",
        layer="layer-3-utility-providers",
        inputs=[
            "engagement scope and objective",
            "current foothold and constraints",
            "engagement_proof",
        ],
        outputs=[
            "attack chain plan (mermaid diagram)",
            "per-phase action list",
            "cleanup runbook",
        ],
        references=[
            "Never claim operation complete without cleanup verification.",
            "Every phase must have an alternative path if primary is blocked.",
            "OPSEC risk tier must be documented per action.",
            "engagement_proof required; block if missing.",
            "Open `references/attack-chain-orchestration-operator-contract.md` when scope, evidence, or operator safety is unclear.",
            "Use `examples/attack-chain-orchestration-good-output.md` and `examples/attack-chain-orchestration-bad-output.md` to calibrate output quality.",
            "Use `evals/attack-chain-orchestration-cases.json` as the minimum scenario set for behavior regression checks.",
            "Use `competencies/attack-chain-orchestration-competencies.json` to check covered competencies, failure traps, and unknown-domain policy.",
        ],
        next_steps=[
            "offensive-security-engagement",
            "edr-evasion-tactics",
            "process-injection-techniques",
            "network-stealth-c2",
            "telemetry-blinding",
            "test-hub",
            "field-journal-evolution",
        ],
        body=dedent(
            """\
            # Mission
            Plan and sequence an authorized multi-phase attack chain with explicit path planning, OPSEC discipline, and mandatory cleanup gate.
            
            ## Mandatory scope
            1. Engagement proof required.
            2. Map 7-phase kill chain: Recon -> Initial Access -> Execution -> Persistence -> Privilege Escalation -> Lateral Movement -> Collection/Exfil -> Cleanup.
            3. For each phase: current foothold + goal + constraints -> next 3 actions ranked by risk and detectability.
            4. Per-phase technique selection: call appropriate Phase 2+ specialists for implementation.
            5. Blocked-path replanning: if one path is blocked, automatically propose 2 alternatives.
            6. Cleanup-mandatory gate: do not claim operation complete until cleanup is verified.
            
            ## Evidence contract
            - engagement_proof confirmed
            - kill chain phases mapped with ATT&CK technique IDs
            - per-phase action ranking documented
            - cleanup plan written
            - blocked-path alternatives documented
            """
        ).strip(),
    ),
    "binary-reverse-methodology": SkillSpec(
        name="binary-reverse-methodology",
        description="Use when reverse engineering a binary: PE/ELF/Mach-O analysis, disassembly, decompilation, protocol reconstruction, anti-analysis bypass, or understanding undocumented behavior.",
        role="reverse-engineer",
        layer="layer-4-specialists-and-standalones",
        inputs=[
            "binary to analyze",
            "analysis goal (protocol / protection / behavior)",
            "engagement_proof if offensive sample",
        ],
        outputs=[
            "reverse engineering report",
            "annotated binary/IDB",
            "protocol or algorithm doc",
        ],
        references=[
            "Rename functions before writing the report — sub_XXXX references are not useful findings.",
            "Document anti-analysis techniques explicitly — they are often the most important finding.",
            "Protocol reconstruction requires both code analysis and traffic capture correlation.",
            "Decompiler output is pseudocode — verify against disassembly for critical paths.",
            "Open `references/binary-reverse-methodology-operator-contract.md` when scope, evidence, or operator safety is unclear.",
            "Use `examples/binary-reverse-methodology-good-output.md` and `examples/binary-reverse-methodology-bad-output.md` to calibrate output quality.",
            "Use `evals/binary-reverse-methodology-cases.json` as the minimum scenario set for behavior regression checks.",
            "Use `competencies/binary-reverse-methodology-competencies.json` to check covered competencies, failure traps, and unknown-domain policy.",
        ],
        next_steps=[
            "malware-analysis-workflows",
            "binary-stealth-obfuscation",
            "frontend-crypto-reverse",
            "windows-native-internals",
            "test-hub",
            "field-journal-evolution",
        ],
        body=dedent(
            """\
            # Mission
            Systematically reverse engineer a binary to understand its behavior, protocol, or protection scheme.
            
            ## Mandatory scope
            1. Tool selection: IDA Pro / Ghidra / Binary Ninja / radare2 — document which and why.
            2. Entry point analysis: identify main, WinMain, TLS callbacks, anti-debug checks.
            3. Anti-analysis handling: detect and bypass anti-debug (IsDebuggerPresent, timing checks, checksum), anti-vm, and packer.
            4. Protocol reconstruction: if network binary, capture traffic and correlate with code paths.
            5. Function naming: rename identified functions before documenting — avoid generic sub_XXXX in reports.
            6. Document findings: algorithm identified, key material location, C2 protocol, persistence mechanism.
            
            ## Evidence contract
            - tool documented
            - entry point and anti-analysis techniques identified
            - anti-debug bypassed or documented
            - key findings renamed and documented
            - protocol or algorithm reconstructed
            """
        ).strip(),
    ),
    "binary-stealth-obfuscation": SkillSpec(
        name="binary-stealth-obfuscation",
        description="Use when a binary payload, shellcode, or PE needs to evade static analysis, signature detection, AV/EDR scanning, or YARA rules through obfuscation, packing, or mutation.",
        role="obfuscation-specialist",
        layer="layer-4-specialists-and-standalones",
        inputs=[
            "binary/shellcode/PE artifact",
            "target AV/EDR product if known",
            "engagement_proof from offensive-security-engagement",
        ],
        outputs=[
            "obfuscated binary",
            "detection surface analysis",
            "sandbox result",
        ],
        references=[
            "Never claim evasion without sandbox execution evidence.",
            "Entropy above 7.5 is a detection signal — document entropy control strategy.",
            "Preserve original behavior exactly — functionality must be verified after obfuscation.",
            "engagement_proof required; block if missing.",
            "Open `references/binary-stealth-obfuscation-operator-contract.md` when scope, evidence, or operator safety is unclear.",
            "Use `examples/binary-stealth-obfuscation-good-output.md` and `examples/binary-stealth-obfuscation-bad-output.md` to calibrate output quality.",
            "Use `evals/binary-stealth-obfuscation-cases.json` as the minimum scenario set for behavior regression checks.",
            "Use `competencies/binary-stealth-obfuscation-competencies.json` to check covered competencies, failure traps, and unknown-domain policy.",
        ],
        next_steps=[
            "edr-evasion-tactics",
            "telemetry-blinding",
            "process-injection-techniques",
            "test-hub",
            "field-journal-evolution",
        ],
        body=dedent(
            """\
            # Mission
            Apply binary obfuscation techniques to reduce static signature surface while preserving correct runtime behavior.
            
            ## Mandatory scope
            1. Engagement proof required: confirm offensive-security-engagement has cached engagement_proof.
            2. Identify detection surface: YARA rules, PE header heuristics, import table, string patterns, entropy.
            3. Choose obfuscation approach: encryption (XOR/AES), packing, polymorphism, import obfuscation, section renaming.
            4. Verify runtime behavior preserved: test in isolated sandbox BEFORE claiming detection evasion.
            5. Document entropy delta: high entropy is itself a detection signal — balance obfuscation with entropy control.
            6. Cleanup gate: document how the obfuscated artifact is removed from target after use.
            
            ## Evidence contract
            - engagement_proof confirmed
            - detection surface identified (YARA rules, strings, imports)
            - sandbox execution result (behavior unchanged)
            - entropy delta documented
            - cleanup path written
            """
        ).strip(),
    ),
    "browser-fingerprint-engineering": SkillSpec(
        name="browser-fingerprint-engineering",
        description="Use when browser-based automation needs to defeat canvas fingerprinting, WebGL fingerprinting, AudioContext fingerprinting, font detection, or behavioral biometrics.",
        role="browser-fingerprint-specialist",
        layer="layer-4-specialists-and-standalones",
        inputs=[
            "target platform fingerprint detection signals",
            "browser automation framework",
            "mmo-identity-infrastructure profile",
        ],
        outputs=[
            "fingerprint spoofing implementation",
            "consistency audit",
            "test site results",
        ],
        references=[
            "Never spoof values in isolation — all signals must be internally consistent.",
            "Dynamic noise must be per-session, not static — static noise is as detectable as no noise.",
            "Behavioral biometrics matter as much as technical fingerprints.",
            "Verify against test sites before deployment — assumption-based spoofing fails.",
            "Open `references/browser-fingerprint-engineering-operator-contract.md` when scope, evidence, or operator safety is unclear.",
            "Use `examples/browser-fingerprint-engineering-good-output.md` and `examples/browser-fingerprint-engineering-bad-output.md` to calibrate output quality.",
            "Use `evals/browser-fingerprint-engineering-cases.json` as the minimum scenario set for behavior regression checks.",
            "Use `competencies/browser-fingerprint-engineering-competencies.json` to check covered competencies, failure traps, and unknown-domain policy.",
        ],
        next_steps=[
            "protocol-fingerprint-spoofing",
            "antibot-challenge-solving",
            "mmo-identity-infrastructure",
            "mmo-browser-fleet-automation",
            "test-hub",
            "field-journal-evolution",
        ],
        body=dedent(
            """\
            # Mission
            Implement code-level browser fingerprint spoofing that survives advanced platform behavioral analysis.
            
            ## Mandatory scope
            1. Map fingerprint vectors targeted by platform: Canvas, WebGL, AudioContext, fonts, navigator properties, screen resolution, timezone, battery API, device memory.
            2. Implement spoofing at the correct level: CDP override, JS injection before page load, custom browser build, or anti-detect browser configuration.
            3. Consistency rule: all spoofed values must be internally consistent (timezone == geolocation region == language == locale).
            4. Dynamic noise: add small random noise to Canvas/WebGL outputs per session to prevent cross-session linking.
            5. Behavioral biometrics: mouse movement entropy, typing cadence, scroll patterns — use humanization library.
            6. Verify against fingerprinting test sites: fingerprintjs.com, browserleaks.com, pixelscan.net.
            
            ## Evidence contract
            - fingerprint vectors listed and addressed
            - consistency check passed (timezone/locale/language aligned)
            - dynamic noise implemented
            - behavioral humanization documented
            - test site results captured
            """
        ).strip(),
    ),
    "cpp-systems-engineering": SkillSpec(
        name="cpp-systems-engineering",
        description="Use when implementing or debugging C++ systems code: Windows/Linux native, RAII, memory management, Win32 API, COM, WTL, STL, multithreading, performance-critical paths, or driver-adjacent code.",
        role="cpp-specialist",
        layer="layer-4-specialists-and-standalones",
        inputs=[
            "story or tech-spec",
            "target platform (Windows/Linux/cross)",
            "existing C++ codebase if present",
        ],
        outputs=[
            "C++ implementation with documented ownership",
            "compile command",
            "test evidence",
        ],
        references=[
            "Prefer RAII wrappers over manual new/delete.",
            "Never use raw C-style casts where static_cast/reinterpret_cast is more explicit.",
            "Document every Win32 API call with its error-check pattern.",
            "Use /analyze or clang-tidy as static analysis gate before claiming done.",
            "Open `references/cpp-systems-engineering-operator-contract.md` when scope, evidence, or operator safety is unclear.",
            "Use `examples/cpp-systems-engineering-good-output.md` and `examples/cpp-systems-engineering-bad-output.md` to calibrate output quality.",
            "Use `evals/cpp-systems-engineering-cases.json` as the minimum scenario set for behavior regression checks.",
            "Use `competencies/cpp-systems-engineering-competencies.json` to check covered competencies, failure traps, and unknown-domain policy.",
        ],
        next_steps=[
            "windows-native-internals",
            "binary-stealth-obfuscation",
            "process-injection-techniques",
            "desktop-imgui-development",
            "test-hub",
            "field-journal-evolution",
        ],
        body=dedent(
            """\
            # Mission
            Produce correct, memory-safe, idiomatic C++ systems code with explicit ownership, RAII discipline, and documented Win32/POSIX API usage.
            
            ## Mandatory scope
            1. Declare ownership model before writing: raw pointer vs unique_ptr vs shared_ptr vs RAII wrapper.
            2. Use RAII for all resource acquisition: handles, sockets, file descriptors, locks.
            3. Name the Win32/POSIX API surface explicitly: function signatures, error codes, and cleanup paths.
            4. Document any UB risk: pointer arithmetic, reinterpret_cast, uninitialized memory, data races.
            5. For multithreaded code: identify shared state, synchronization primitive, and lock ordering.
            6. Capture compile + link command with exact flags (-std=c++17, /W4, /analyze if MSVC).
            
            ## Evidence contract
            - compiles cleanly with named flags
            - RAII ownership documented for every resource
            - UB risks explicitly called out or eliminated
            - Win32 error handling shown (GetLastError / HRESULT checked)
            """
        ).strip(),
        allowed_tools=["Read", "Write", "Edit", "Grep", "Glob", "Bash"],
    ),
    "desktop-imgui-development": SkillSpec(
        name="desktop-imgui-development",
        description="Use when building a desktop GUI with Dear ImGui (C++ or bindings): operator panels, real-time dashboards, debug overlays, game cheats UI, or tool UIs embedded in a render loop.",
        role="imgui-specialist",
        layer="layer-4-specialists-and-standalones",
        inputs=[
            "UI spec or wireframe",
            "backend (DirectX/OpenGL/Vulkan)",
            "C++ project context",
            "MMO operation live state (from mmo-cloud-operations, mmo-proxy-network-ops) for control panel data",
        ],
        outputs=[
            "ImGui implementation",
            "render loop integration",
            "state management code",
        ],
        references=[
            "Never put business logic inside the render loop — it runs every frame.",
            "UI state must be a separate struct, not global variables.",
            "Font atlas must be built once at init, not per-frame.",
            "For overlay injection, document cleanup on process exit or eject.",
            "Open `references/desktop-imgui-development-operator-contract.md` when scope, evidence, or operator safety is unclear.",
            "Use `examples/desktop-imgui-development-good-output.md` and `examples/desktop-imgui-development-bad-output.md` to calibrate output quality.",
            "Use `evals/desktop-imgui-development-cases.json` as the minimum scenario set for behavior regression checks.",
            "Use `competencies/desktop-imgui-development-competencies.json` to check covered competencies, failure traps, and unknown-domain policy.",
        ],
        next_steps=[
            "cpp-systems-engineering",
            "windows-native-internals",
            "test-hub",
            "field-journal-evolution",
        ],
        body=dedent(
            """\
            # Mission
            Build functional, well-structured Dear ImGui interfaces with correct render loop integration and layout discipline.
            
            ## Mandatory scope
            1. Declare backend: OpenGL3+GLFW, DirectX11/12, Vulkan, or SDL2 — each has a different backend setup.
            2. Render loop structure: NewFrame -> layout logic -> Render -> present — no business logic inside render loop.
            3. State separation: UI state lives in a dedicated struct, not scattered in render functions.
            4. Font loading: custom fonts loaded in ImGui_ImplXxx_CreateFontsTexture, not per-frame.
            5. DPI awareness: implement ImGui::GetIO().DisplayFramebufferScale or DPI scale factor.
            6. For overlay injection (game cheats): document hook point (Present hook, manual map) and cleanup.
            
            ## Evidence contract
            - backend declared
            - render loop structure documented
            - state struct defined
            - compiles and renders correct layout
            - DPI handling documented
            """
        ).strip(),
    ),
    "desktop-python-ui": SkillSpec(
        name="desktop-python-ui",
        description="Use when building a desktop Python GUI: PyQt6/PySide6, Tkinter, wxPython, or customtkinter for operator tools, automation dashboards, or config panels.",
        role="python-ui-specialist",
        layer="layer-4-specialists-and-standalones",
        inputs=[
            "UI spec",
            "Python framework preference",
            "target OS (Windows/Linux/macOS)",
            "MMO operation live state (from mmo-cloud-operations, mmo-proxy-network-ops) for control panel data",
        ],
        outputs=[
            "Python UI implementation",
            "threading model docs",
            "packaging spec",
        ],
        references=[
            "Never block the main UI thread with slow operations.",
            "Signals/slots for PyQt — never call UI methods directly from background threads.",
            "Use layout managers — absolute positioning breaks on different screen sizes.",
            "Provide packaging spec if operator needs a standalone .exe.",
            "Open `references/desktop-python-ui-operator-contract.md` when scope, evidence, or operator safety is unclear.",
            "Use `examples/desktop-python-ui-good-output.md` and `examples/desktop-python-ui-bad-output.md` to calibrate output quality.",
            "Use `evals/desktop-python-ui-cases.json` as the minimum scenario set for behavior regression checks.",
            "Use `competencies/desktop-python-ui-competencies.json` to check covered competencies, failure traps, and unknown-domain policy.",
        ],
        next_steps=[
            "advanced-python-engineering",
            "terminal-operator-ui",
            "test-hub",
            "field-journal-evolution",
        ],
        body=dedent(
            """\
            # Mission
            Build clean, functional Python desktop UIs with correct event loop integration, threading discipline, and packaging.
            
            ## Mandatory scope
            1. Declare framework: PyQt6/PySide6, Tkinter, customtkinter — each has different signal/slot or callback model.
            2. Threading: UI updates must happen on main thread; background work in QThread/threading.Thread with signals.
            3. Layout: use layout managers (QVBoxLayout, QHBoxLayout, grid) — never fixed pixel positioning.
            4. Packaging: specify PyInstaller or cx_Freeze spec for standalone executable if needed.
            5. State management: separate model from view — no business logic in widget callbacks.
            6. Error handling: show user-friendly error dialogs for all recoverable exceptions.
            
            ## Evidence contract
            - framework declared
            - threading model documented (background work separated from UI thread)
            - layout uses layout managers
            - packaging spec documented if needed
            - runs without console window if GUI-only
            """
        ).strip(),
    ),
    "edr-evasion-tactics": SkillSpec(
        name="edr-evasion-tactics",
        description="Use when a payload or tool needs to evade EDR runtime detection: hook bypass, AMSI bypass, ETW patching, direct syscall, or AV memory scanning evasion.",
        role="edr-evasion-specialist",
        layer="layer-4-specialists-and-standalones",
        inputs=[
            "target EDR product",
            "payload or tool to protect",
            "engagement_proof",
        ],
        outputs=[
            "hook-bypass implementation",
            "AMSI/ETW bypass",
            "sandbox evidence",
        ],
        references=[
            "Never claim bypass without controlled sandbox monitoring evidence.",
            "Document which EDR version was tested — bypass techniques are version-specific.",
            "Unhooking must restore original bytes on cleanup.",
            "engagement_proof required; block if missing.",
            "Open `references/edr-evasion-tactics-operator-contract.md` when scope, evidence, or operator safety is unclear.",
            "Use `examples/edr-evasion-tactics-good-output.md` and `examples/edr-evasion-tactics-bad-output.md` to calibrate output quality.",
            "Use `evals/edr-evasion-tactics-cases.json` as the minimum scenario set for behavior regression checks.",
            "Use `competencies/edr-evasion-tactics-competencies.json` to check covered competencies, failure traps, and unknown-domain policy.",
        ],
        next_steps=[
            "telemetry-blinding",
            "binary-stealth-obfuscation",
            "process-injection-techniques",
            "windows-native-internals",
            "test-hub",
            "field-journal-evolution",
        ],
        body=dedent(
            """\
            # Mission
            Implement EDR/AV runtime evasion with explicit hook bypass, syscall strategy, and OPSEC discipline.
            
            ## Mandatory scope
            1. Engagement proof required.
            2. Identify EDR target: CrowdStrike / Defender / SentinelOne / Carbon Black — hook surface differs.
            3. Choose syscall strategy: direct syscall (Syswhispers2/3), indirect syscall, or unhooking (overwrite ntdll from fresh copy).
            4. Handle AMSI: patch AmsiScanBuffer / AmsiOpenSession in-process.
            5. Handle ETW: patch EtwEventWrite / disable provider via NtTraceControl.
            6. Verify no hook fires: use a controlled sandbox with ETW/kernel callback monitoring.
            
            ## Evidence contract
            - engagement_proof confirmed
            - EDR target named
            - syscall strategy documented with method (direct/indirect/unhook)
            - AMSI + ETW bypass verified in sandbox
            - No hook fired in monitoring trace
            """
        ).strip(),
    ),
    "field-journal-evolution": SkillSpec(
        name="field-journal-evolution",
        description="Use when a task is complete, a pitfall is found, a new technique is discovered, or a routing gap is identified. Writeback experience to the field journal to evolve skill quality over time.",
        role="knowledge-writeback",
        layer="layer-3-utility-providers",
        inputs=[
            "completed task context",
            "pitfall or solution discovered",
            "skill execution chain used",
        ],
        outputs=[
            ".relay-kit/state/field-journal.md entry",
            "experience index update",
        ],
        references=[
            "Code-first: key-code field is mandatory in every entry.",
            "No fluff: reject generic summaries — require actionable specifics.",
            "No repeat: check existing entries before adding similar content.",
            "Check field-journal BEFORE starting a similar task — reuse over rediscovery.",
            "Open `references/field-journal-evolution-operator-contract.md` when scope, evidence, or operator safety is unclear.",
            "Use `examples/field-journal-evolution-good-output.md` and `examples/field-journal-evolution-bad-output.md` to calibrate output quality.",
            "Use `evals/field-journal-evolution-cases.json` as the minimum scenario set for behavior regression checks.",
            "Use `competencies/field-journal-evolution-competencies.json` to check covered competencies, failure traps, and unknown-domain policy.",
        ],
        next_steps=[
            "workflow-router",
            "cook",
            "developer",
            "attack-chain-orchestration",
        ],
        body=dedent(
            """\
            # Mission
            Capture and index actionable experience from completed tasks so future lanes can reuse solutions, avoid pitfalls, and improve routing accuracy.
            
            ## Mandatory scope
            1. Writeback triggers: task complete, pitfall encountered, new technique proven, routing gap identified, code pattern reused.
            2. Writeback template per entry:
               - scenario: one sentence
               - goal: what was being built or fixed
               - execution-chain: which skills were used in order
               - pitfall-table: what failed and why
               - toolchain: exact tools and versions
               - key-code: the minimal working code or config
               - improvement: what to do differently next time
            3. No fluff: every record must contain actionable info — no generic summaries.
            4. No repeat: only add a variant if it differs substantially from existing entries.
            5. Code-first: key-code field is required — text-only entries are rejected.
            6. Check index before new tasks: when starting a similar task, search field-journal first for prior experience.
            
            ## Evidence contract
            - writeback entry written with all required fields
            - key-code field populated
            - entry indexed by category
            - prior experience searched before starting similar task
            """
        ).strip(),
    ),
    "frontend-crypto-reverse": SkillSpec(
        name="frontend-crypto-reverse",
        description="Use when web applications use client-side cryptography, obfuscated JS, WASM, or signing parameters that must be reversed to replicate API calls without a browser.",
        role="crypto-reverse-specialist",
        layer="layer-4-specialists-and-standalones",
        inputs=[
            "target web application",
            "captured network traffic (HAR)",
            "JS bundle or WASM",
        ],
        outputs=[
            "signing implementation",
            "deobfuscation analysis",
            "verification comparison",
        ],
        references=[
            "Never claim signature replication without byte-exact comparison to browser output.",
            "Document key derivation — hardcoded keys may rotate.",
            "WASM decompilation output should be treated as pseudocode, not exact code.",
            "If signing keys are device-fingerprint-derived, integrate with browser-fingerprint-engineering.",
            "Open `references/frontend-crypto-reverse-operator-contract.md` when scope, evidence, or operator safety is unclear.",
            "Use `examples/frontend-crypto-reverse-good-output.md` and `examples/frontend-crypto-reverse-bad-output.md` to calibrate output quality.",
            "Use `evals/frontend-crypto-reverse-cases.json` as the minimum scenario set for behavior regression checks.",
            "Use `competencies/frontend-crypto-reverse-competencies.json` to check covered competencies, failure traps, and unknown-domain policy.",
        ],
        next_steps=[
            "protocol-fingerprint-spoofing",
            "browser-fingerprint-engineering",
            "mmo-http-api-automation",
            "mmo-data-harvesting",
            "test-hub",
            "field-journal-evolution",
        ],
        body=dedent(
            """\
            # Mission
            Reverse-engineer frontend signing, encryption, and obfuscation to replicate API calls programmatically.
            
            ## Mandatory scope
            1. Map signing pipeline: identify where request signature, timestamp, nonce, or token is computed (JS bundle, WASM, ServiceWorker).
            2. Deobfuscate JS: use AST transformation (babel-plugin-deobfuscator, js-beautify) or manual analysis.
            3. For WASM: extract and decompile (wasm-decompile, Ghidra WASM plugin) to identify crypto primitives.
            4. Replicate in Python/Go/Node: implement signing logic outside browser without CDP.
            5. Verify: compare replicated signature against browser-captured signature for same input.
            6. Document key material: where signing keys are embedded (hardcoded, derived from device fingerprint, fetched at runtime).
            
            ## Evidence contract
            - signing pipeline mapped
            - deobfuscation method documented
            - replication implemented and verified (signatures match)
            - key material source documented
            - works without browser dependency
            """
        ).strip(),
    ),
    "malware-analysis-workflows": SkillSpec(
        name="malware-analysis-workflows",
        description="Use when analyzing suspicious binaries, malware samples, or unknown executables: static analysis, dynamic analysis, sandbox detonation, IOC extraction, and behavioral mapping.",
        role="malware-analyst",
        layer="layer-4-specialists-and-standalones",
        inputs=[
            "suspicious binary or sample hash",
            "engagement context or IR authorization",
            "sandbox environment",
        ],
        outputs=[
            "malware analysis report",
            "IOC list",
            "ATT&CK mapping",
        ],
        references=[
            "Never detonate samples outside isolated VM with snapshot.",
            "Document isolation environment explicitly — analysis on host = contamination.",
            "IOC extraction is mandatory before any network-based hunting.",
            "ATT&CK mapping must reference technique IDs, not just names.",
            "Open `references/malware-analysis-workflows-operator-contract.md` when scope, evidence, or operator safety is unclear.",
            "Use `examples/malware-analysis-workflows-good-output.md` and `examples/malware-analysis-workflows-bad-output.md` to calibrate output quality.",
            "Use `evals/malware-analysis-workflows-cases.json` as the minimum scenario set for behavior regression checks.",
            "Use `competencies/malware-analysis-workflows-competencies.json` to check covered competencies, failure traps, and unknown-domain policy.",
        ],
        next_steps=[
            "binary-reverse-methodology",
            "edr-evasion-tactics",
            "binary-stealth-obfuscation",
            "test-hub",
            "field-journal-evolution",
        ],
        body=dedent(
            """\
            # Mission
            Produce a structured malware analysis report with static properties, behavioral evidence, IOCs, and ATT&CK mapping.
            
            ## Mandatory scope
            1. Engagement proof required for offensive samples; for defensive/IR context, document authorization separately.
            2. Static analysis first: file type, hash (MD5/SHA1/SHA256), PE headers, imports, strings, entropy, packer detection.
            3. Dynamic analysis in isolated environment: VM snapshot before detonation, network monitoring (FakeNet/INetSim), process monitor.
            4. Extract IOCs: C2 domains/IPs, mutex names, registry keys, dropped files, scheduled tasks.
            5. Map to ATT&CK: technique IDs for each observed behavior.
            6. Do not run samples on production systems — document isolation environment.
            
            ## Evidence contract
            - isolation environment documented
            - static analysis output (hash, imports, strings, entropy)
            - dynamic analysis result (process tree, network, registry)
            - IOC list
            - ATT&CK mapping
            """
        ).strip(),
    ),
    "mmo-llm-automation": SkillSpec(
        name="mmo-llm-automation",
        description="Use when MMO operations need AI-assisted content generation, behavioral variance, Sybil evasion through LLM diversity, or LLM API integration for bulk content tasks.",
        role="llm-automation-specialist",
        layer="layer-4-specialists-and-standalones",
        inputs=[
            "content task specification",
            "LLM provider credentials",
            "diversity requirements",
        ],
        outputs=[
            "LLM integration implementation",
            "prompt templates",
            "content validation pipeline",
        ],
        references=[
            "Never exceed token budget without explicit approval — LLM costs scale rapidly.",
            "Diversity metric must be measured, not assumed — compute n-gram similarity.",
            "Output validation must run before publishing — LLM hallucinations contaminate MMO accounts.",
            "Local models (Ollama) preferred for sensitive content to avoid API logging.",
            "Open `references/mmo-llm-automation-operator-contract.md` when scope, evidence, or operator safety is unclear.",
            "Use `examples/mmo-llm-automation-good-output.md` and `examples/mmo-llm-automation-bad-output.md` to calibrate output quality.",
            "Use `evals/mmo-llm-automation-cases.json` as the minimum scenario set for behavior regression checks.",
            "Use `competencies/mmo-llm-automation-competencies.json` to check covered competencies, failure traps, and unknown-domain policy.",
        ],
        next_steps=[
            "advanced-python-engineering",
            "mmo-content-factory",
            "mmo-reup-automation",
            "test-hub",
            "field-journal-evolution",
        ],
        body=dedent(
            """\
            # Mission
            Integrate LLM APIs into MMO operations for content diversity, behavioral humanization, and AI-assisted task automation.
            
            ## Mandatory scope
            1. Declare LLM provider and model: OpenAI GPT-4o, Anthropic Claude, Gemini, or local (Ollama/LM Studio).
            2. Prompt engineering: system prompt, diversity parameters, content constraints — document all.
            3. Output validation: define acceptance criteria for generated content (length, language, topic compliance).
            4. Rate limit and cost management: document token budget per task, batch size, retry strategy.
            5. Behavioral variance: if used for Sybil evasion, document diversity metrics (n-gram similarity threshold).
            6. Content safety: define prohibited content filters and fallback strategy when model refuses.
            
            ## Evidence contract
            - LLM provider and model declared
            - prompt template documented
            - output acceptance criteria defined
            - rate limit and cost budget documented
            - diversity metric defined if used for Sybil evasion
            """
        ).strip(),
    ),
    "mmo-onchain-security-audit": SkillSpec(
        name="mmo-onchain-security-audit",
        description="Use when MMO crypto operations involve on-chain script execution, smart contract interaction, or wallet automation that requires security audit before deployment.",
        role="onchain-auditor",
        layer="layer-4-specialists-and-standalones",
        inputs=[
            "smart contract addresses",
            "automation script",
            "chain (ETH/BSC/ARB/etc)",
        ],
        outputs=[
            "security audit report",
            "simulation result",
            "risk assessment",
            "emergency procedures",
        ],
        references=[
            "Never deploy wallet automation without fork simulation first.",
            "Unlimited approvals are always high-risk — document and recommend alternatives.",
            "Wallet isolation is mandatory — one signing key per strategy.",
            "Emergency stop procedure must be documented before deployment.",
            "Open `references/mmo-onchain-security-audit-operator-contract.md` when scope, evidence, or operator safety is unclear.",
            "Use `examples/mmo-onchain-security-audit-good-output.md` and `examples/mmo-onchain-security-audit-bad-output.md` to calibrate output quality.",
            "Use `evals/mmo-onchain-security-audit-cases.json` as the minimum scenario set for behavior regression checks.",
            "Use `competencies/mmo-onchain-security-audit-competencies.json` to check covered competencies, failure traps, and unknown-domain policy.",
        ],
        next_steps=[
            "mmo-crypto-wallet-farming",
            "mmo-http-api-automation",
            "test-hub",
            "field-journal-evolution",
        ],
        body=dedent(
            """\
            # Mission
            Audit on-chain scripts and smart contract interactions for security vulnerabilities before any wallet or funds are committed.
            
            ## Mandatory scope
            1. Static analysis: read all contract functions being called; identify reentrancy, approval abuse, infinite approve risk.
            2. Simulation first: dry-run all transactions with fork simulation (Tenderly / Hardhat mainnet fork / Foundry fork) before live execution.
            3. Approval audit: identify any approve() or setApprovalForAll() calls; flag unlimited approvals as high-risk.
            4. Slippage and MEV: document slippage tolerance and MEV exposure for swap transactions.
            5. Wallet isolation: confirm 1-wallet-per-strategy rule — never reuse signing key across strategies.
            6. Emergency stop: document how to revoke approvals or pause automation if anomaly detected.
            
            ## Evidence contract
            - static analysis of all called functions documented
            - fork simulation result captured
            - approval risk documented (unlimited vs limited)
            - slippage and MEV tolerance documented
            - emergency revocation procedure written
            """
        ).strip(),
    ),
    "mobile-app-reverse": SkillSpec(
        name="mobile-app-reverse",
        description="Use when MMO mobile operations need to reverse-engineer APK or IPA apps: find API endpoints, signing keys, certificate pinning bypass, or replicate app behavior without the app.",
        role="mobile-reverse-specialist",
        layer="layer-4-specialists-and-standalones",
        inputs=[
            "APK or IPA file or app package name",
            "target functionality to replicate",
            "mobile device or emulator",
        ],
        outputs=[
            "API endpoint map",
            "signing implementation",
            "Python client",
            "certificate pinning bypass script",
        ],
        references=[
            "Certificate pinning bypass must be verified with actual traffic capture.",
            "API endpoint map must include all request headers and signing parameters.",
            "Signing replication must produce byte-exact results compared to app output.",
            "Document app version — APIs change across versions.",
            "Open `references/mobile-app-reverse-operator-contract.md` when scope, evidence, or operator safety is unclear.",
            "Use `examples/mobile-app-reverse-good-output.md` and `examples/mobile-app-reverse-bad-output.md` to calibrate output quality.",
            "Use `evals/mobile-app-reverse-cases.json` as the minimum scenario set for behavior regression checks.",
            "Use `competencies/mobile-app-reverse-competencies.json` to check covered competencies, failure traps, and unknown-domain policy.",
        ],
        next_steps=[
            "frontend-crypto-reverse",
            "protocol-fingerprint-spoofing",
            "mmo-http-api-automation",
            "mmo-mobile-app-automation",
            "test-hub",
            "field-journal-evolution",
        ],
        body=dedent(
            """\
            # Mission
            Reverse-engineer mobile apps to extract API endpoints, signing logic, and protocol details for programmatic replication.
            
            ## Mandatory scope
            1. Platform: Android (APK) or iOS (IPA) — document platform and app version.
            2. Decompilation: APK -> jadx/apktool; IPA -> frida-ios-dump + class-dump or Ghidra.
            3. Certificate pinning bypass: Frida script for Android (SSLContext.getDefault / OkHttp) or iOS (SecTrustEvaluate / AFNetworking).
            4. API endpoint extraction: intercept traffic with mitmproxy/Burp after pin bypass; map all endpoints.
            5. Signing parameter reverse: identify request signing (HMAC, timestamp, nonce, device fingerprint).
            6. Replicate in Python: implement API client without app dependency; verify responses match.
            
            ## Evidence contract
            - platform and app version documented
            - decompilation output captured
            - certificate pinning bypassed (traffic visible in proxy)
            - API endpoints mapped
            - signing logic reversed and replicated
            - Python client verified against app responses
            """
        ).strip(),
    ),
    "network-stealth-c2": SkillSpec(
        name="network-stealth-c2",
        description="Use when building or operating C2 infrastructure that needs traffic blending, domain fronting, protocol mimicry, redirectors, or beaconing that evades network detection.",
        role="c2-specialist",
        layer="layer-4-specialists-and-standalones",
        inputs=[
            "engagement scope",
            "target network environment",
            "C2 framework if specified",
        ],
        outputs=[
            "C2 implementation",
            "traffic profile docs",
            "redirector topology",
        ],
        references=[
            "Never use default C2 framework signatures — customize all beacons, certificates, and user-agents.",
            "Jitter is mandatory — fixed intervals are trivially detected.",
            "Redirectors must not expose backend C2 IP directly.",
            "engagement_proof required; block if missing.",
            "Open `references/network-stealth-c2-operator-contract.md` when scope, evidence, or operator safety is unclear.",
            "Use `examples/network-stealth-c2-good-output.md` and `examples/network-stealth-c2-bad-output.md` to calibrate output quality.",
            "Use `evals/network-stealth-c2-cases.json` as the minimum scenario set for behavior regression checks.",
            "Use `competencies/network-stealth-c2-competencies.json` to check covered competencies, failure traps, and unknown-domain policy.",
        ],
        next_steps=[
            "edr-evasion-tactics",
            "telemetry-blinding",
            "protocol-fingerprint-spoofing",
            "test-hub",
            "field-journal-evolution",
        ],
        body=dedent(
            """\
            # Mission
            Design and implement C2 communication that blends with legitimate traffic and evades network-level detection.
            
            ## Mandatory scope
            1. Engagement proof required.
            2. Choose C2 protocol: HTTPS, DNS, SMB, ICMP, custom — document traffic profile.
            3. Document domain fronting or CDN relay if used: fronting domain, host header, backend.
            4. Configure beacon jitter: randomized interval (base +/- jitter %) to avoid periodic traffic patterns.
            5. Implement redirectors: separate C2 server from direct operator contact.
            6. Network traffic profile: document legitimate service being mimicked (Office365, Slack, etc.).
            
            ## Evidence contract
            - engagement_proof confirmed
            - protocol and traffic profile documented
            - beacon jitter configured and documented
            - redirector topology drawn
            - network capture shows traffic blends with legitimate baseline
            """
        ).strip(),
    ),
    "offensive-security-engagement": SkillSpec(
        name="offensive-security-engagement",
        description="Use when a request contains offensive, red-team, evasion, injection, stealth, C2, payload, syscall, hollowing, or bypass keywords, or when authorization_risk >= medium. Gate + context provider for all offensive lanes.",
        role="engagement-gate",
        layer="layer-3-utility-providers",
        inputs=[
            "user request with offensive keywords",
            "workflow-state",
            "authorization scope if provided",
        ],
        outputs=[
            "workflow-state.engagement_proof",
            "workflow-state.lane_mode = offensive",
            "risk-tier annotation",
        ],
        references=[
            "Never proceed without engagement_proof — if authorization is missing, block and prompt.",
            "Do not own the lane; return control after caching proof.",
            "Distinguish fail-closed (policy-guard) from fail-open-for-authorized (this skill).",
            "ATT&CK mapping is required for every offensive lane.",
            "Open `references/offensive-security-engagement-operator-contract.md` when scope, evidence, or operator safety is unclear.",
            "Use `examples/offensive-security-engagement-good-output.md` and `examples/offensive-security-engagement-bad-output.md` to calibrate output quality.",
            "Use `evals/offensive-security-engagement-cases.json` as the minimum scenario set for behavior regression checks.",
            "Use `competencies/offensive-security-engagement-competencies.json` to check covered competencies, failure traps, and unknown-domain policy.",
        ],
        next_steps=[
            "attack-chain-orchestration",
            "cpp-systems-engineering",
            "edr-evasion-tactics",
            "process-injection-techniques",
            "network-stealth-c2",
            "binary-stealth-obfuscation",
            # Every offensive/reverse specialist hangs off this gate so that no
            # lane can reach one without first recording authorization.
            "telemetry-blinding",
            "protocol-fingerprint-spoofing",
            "browser-fingerprint-engineering",
            "antibot-challenge-solving",
            "malware-analysis-workflows",
            "binary-reverse-methodology",
            "mobile-app-reverse",
            "frontend-crypto-reverse",
            "windows-native-internals",
            "policy-guard",
        ],
        body=dedent(
            """\
            # Mission
            Activate authorized offensive context, cache engagement proof, enforce OPSEC ordering, and map ATT&CK phase so offensive lanes have a clear authorization record before any specialist runs.
            
            ## Mandatory scope
            1. Confirm engagement authorization: check workflow-state for engagement_proof; if missing, prompt for scope, target, and authorization before proceeding.
            2. Cache engagement_proof with: authorized-by, scope, target, risk-tier (low/medium/high/critical), ATT&CK phase.
            3. Set lane mode to offensive in workflow-state.
            4. Enforce OPSEC ordering: recon -> initial-access -> execution -> persistence -> privesc -> lateral -> collection -> exfil -> cleanup.
            5. After caching proof, return control to the calling hub or cook — do not own the lane.
            6. Distinguish from policy-guard: policy-guard is fail-closed for secrets/shell/path. This skill is fail-open-for-authorized for offensive techniques. Run policy-guard AFTER execution as post-gate.
            
            ## Evidence contract
            - engagement_proof written to workflow-state with all required fields
            - risk-tier set explicitly before specialist is called
            - ATT&CK phase mapped for current task
            """
        ).strip(),
    ),
    "process-injection-techniques": SkillSpec(
        name="process-injection-techniques",
        description="Use when a payload needs to run in the context of another process: classic injection, reflective DLL, process hollowing, APC injection, thread hijacking, or shellcode runners.",
        role="injection-specialist",
        layer="layer-4-specialists-and-standalones",
        inputs=[
            "target process or criteria",
            "payload shellcode or DLL",
            "engagement_proof",
        ],
        outputs=[
            "injection implementation",
            "memory management docs",
            "cleanup runbook",
        ],
        references=[
            "Never leave RWX memory pages after payload execution — change to RX.",
            "Document cleanup: close handles, free memory, restore target thread state.",
            "Handle WOW64 explicitly when injecting cross-arch.",
            "engagement_proof required; block if missing.",
            "Open `references/process-injection-techniques-operator-contract.md` when scope, evidence, or operator safety is unclear.",
            "Use `examples/process-injection-techniques-good-output.md` and `examples/process-injection-techniques-bad-output.md` to calibrate output quality.",
            "Use `evals/process-injection-techniques-cases.json` as the minimum scenario set for behavior regression checks.",
            "Use `competencies/process-injection-techniques-competencies.json` to check covered competencies, failure traps, and unknown-domain policy.",
        ],
        next_steps=[
            "edr-evasion-tactics",
            "telemetry-blinding",
            "windows-native-internals",
            "binary-stealth-obfuscation",
            "network-stealth-c2",
            "test-hub",
            "field-journal-evolution",
        ],
        body=dedent(
            """\
            # Mission
            Implement process injection techniques with correct memory management, error handling, and cleanup discipline.
            
            ## Mandatory scope
            1. Engagement proof required.
            2. Choose injection method: CreateRemoteThread, APC queue, SetWindowsHookEx, reflective DLL, process hollowing, early-bird, thread hijacking.
            3. Document memory allocation: VirtualAllocEx permissions (RWX -> RX after write), cleanup on failure.
            4. Handle 32-bit / 64-bit mismatch: WOW64 constraints for cross-arch injection.
            5. Verify target process selection: PPID spoofing if needed, handle privileges required.
            6. Cleanup gate: document how the injected memory and handles are cleaned up after operation.
            
            ## Evidence contract
            - engagement_proof confirmed
            - injection method declared with rationale
            - memory permissions and cleanup documented
            - arch mismatch handled (WOW64 if applicable)
            - PPID spoofing documented if used
            """
        ).strip(),
    ),
    "protocol-fingerprint-spoofing": SkillSpec(
        name="protocol-fingerprint-spoofing",
        description="Use when HTTP/HTTPS/TLS traffic needs to spoof or match a specific protocol fingerprint to evade network inspection, bot detection, or TLS fingerprinting (JA3/JA4/HTTP2).",
        role="protocol-fingerprint-specialist",
        layer="layer-4-specialists-and-standalones",
        inputs=[
            "target protocol (TLS version, HTTP version)",
            "reference client fingerprint",
            "target platform",
        ],
        outputs=[
            "protocol implementation",
            "fingerprint comparison",
            "detection test result",
        ],
        references=[
            "Never claim fingerprint match without scanner verification.",
            "Document GREASE values — they are part of Chrome fingerprint.",
            "HTTP/2 SETTINGS frame order matters — match exactly.",
            "TLS extension order is as important as cipher suite choice.",
            "Open `references/protocol-fingerprint-spoofing-operator-contract.md` when scope, evidence, or operator safety is unclear.",
            "Use `examples/protocol-fingerprint-spoofing-good-output.md` and `examples/protocol-fingerprint-spoofing-bad-output.md` to calibrate output quality.",
            "Use `evals/protocol-fingerprint-spoofing-cases.json` as the minimum scenario set for behavior regression checks.",
            "Use `competencies/protocol-fingerprint-spoofing-competencies.json` to check covered competencies, failure traps, and unknown-domain policy.",
        ],
        next_steps=[
            "browser-fingerprint-engineering",
            "antibot-challenge-solving",
            "network-stealth-c2",
            "mmo-http-api-automation",
            "test-hub",
            "field-journal-evolution",
        ],
        body=dedent(
            """\
            # Mission
            Match target protocol fingerprints (TLS, HTTP/2, TCP) precisely so traffic is indistinguishable from a legitimate client.
            
            ## Mandatory scope
            1. Identify fingerprint target: JA3/JA3S, JA4, HTTP/2 SETTINGS, TCP window size, User-Agent.
            2. Collect reference fingerprint from legitimate client (Chrome 120+, Firefox 121+, curl).
            3. Implement spoofing: custom TLS stack (utls/tls-client), HTTP/2 SETTINGS frame order, header order.
            4. Verify match: run fingerprint scanner (tls.peet.ws, Scapy, Wireshark) against implementation.
            5. Document cipher suite order, TLS extensions, and GREASE values used.
            6. Test against target platform's detection (Cloudflare, Akamai, Datadome) in controlled env.
            
            ## Evidence contract
            - reference fingerprint captured
            - spoofed fingerprint matches (JA3/JA4 match documented)
            - cipher suite and extension order documented
            - verified against target detection platform
            """
        ).strip(),
    ),
    "telemetry-blinding": SkillSpec(
        name="telemetry-blinding",
        description="Use when operations need to suppress, redirect, or corrupt security telemetry: ETW providers, Sysmon, WEF, audit logs, or kernel callbacks.",
        role="telemetry-specialist",
        layer="layer-4-specialists-and-standalones",
        inputs=[
            "target environment telemetry stack",
            "operation scope",
            "engagement_proof",
        ],
        outputs=[
            "telemetry blinding implementation",
            "verification result",
            "restoration runbook",
        ],
        references=[
            "Never delete logs without explicit engagement scope including log suppression.",
            "Document restoration path — cleanup is mandatory after authorized operations.",
            "Verify blinding with actual log monitoring, not assumption.",
            "engagement_proof required; block if missing.",
            "Open `references/telemetry-blinding-operator-contract.md` when scope, evidence, or operator safety is unclear.",
            "Use `examples/telemetry-blinding-good-output.md` and `examples/telemetry-blinding-bad-output.md` to calibrate output quality.",
            "Use `evals/telemetry-blinding-cases.json` as the minimum scenario set for behavior regression checks.",
            "Use `competencies/telemetry-blinding-competencies.json` to check covered competencies, failure traps, and unknown-domain policy.",
        ],
        next_steps=[
            "edr-evasion-tactics",
            "binary-stealth-obfuscation",
            "process-injection-techniques",
            "network-stealth-c2",
            "test-hub",
            "field-journal-evolution",
        ],
        body=dedent(
            """\
            # Mission
            Suppress or redirect security telemetry channels so offensive operations produce minimal forensic footprint.
            
            ## Mandatory scope
            1. Engagement proof required.
            2. Map active telemetry channels: ETW providers, Sysmon config, WEF subscriptions, audit policy.
            3. Choose blinding approach: ETW provider disable, Sysmon filter bypass, audit log suppression, kernel callback removal.
            4. Verify blinding in controlled environment: confirm target events no longer appear in SIEM/log.
            5. Document restoration path: how telemetry is re-enabled after operation.
            6. Anti-forensics scope: document which artifacts are wiped (prefetch, event logs, MFT timestamps).
            
            ## Evidence contract
            - engagement_proof confirmed
            - telemetry channels mapped
            - blinding verified (events absent in controlled log)
            - restoration path documented
            - anti-forensics scope listed
            """
        ).strip(),
    ),
    "terminal-operator-ui": SkillSpec(
        name="terminal-operator-ui",
        description="Use when building a rich terminal UI (TUI) for operator control panels, automation dashboards, or CLI tools: Rich, Textual, blessed, curses, prompt_toolkit, or similar.",
        role="tui-specialist",
        layer="layer-4-specialists-and-standalones",
        inputs=[
            "UI spec or wireframe",
            "framework preference",
            "Python version",
        ],
        outputs=[
            "TUI implementation",
            "keyboard shortcut map",
            "live update docs",
        ],
        references=[
            "Never mix print() with a live TUI — it corrupts the layout.",
            "Define explicit terminal size handling — TUIs break when terminal is too narrow.",
            "Input blocking operations must run in threads with TUI-safe update callbacks.",
            "Test in the actual target terminal (Windows Terminal vs xterm differ).",
            "Open `references/terminal-operator-ui-operator-contract.md` when scope, evidence, or operator safety is unclear.",
            "Use `examples/terminal-operator-ui-good-output.md` and `examples/terminal-operator-ui-bad-output.md` to calibrate output quality.",
            "Use `evals/terminal-operator-ui-cases.json` as the minimum scenario set for behavior regression checks.",
            "Use `competencies/terminal-operator-ui-competencies.json` to check covered competencies, failure traps, and unknown-domain policy.",
        ],
        next_steps=[
            "advanced-python-engineering",
            "desktop-python-ui",
            "test-hub",
            "field-journal-evolution",
        ],
        body=dedent(
            """\
            # Mission
            Build functional, navigable terminal UIs with correct layout, input handling, and live update discipline.
            
            ## Mandatory scope
            1. Declare framework: Rich (static), Textual (reactive TUI), blessed, curses, prompt_toolkit.
            2. Layout: define panels, tables, progress bars, and input areas with explicit dimensions and overflow behavior.
            3. Live updates: use Live context (Rich) or reactive state (Textual) — never print() to a live TUI.
            4. Input handling: define keyboard shortcuts, navigation, and exit path explicitly.
            5. Color and styling: define palette and use named styles, not inline ANSI codes.
            6. Error display: show error state visually in a status bar or panel, not as raw exception text.
            
            ## Evidence contract
            - framework declared
            - layout documented (panels, tables, inputs)
            - live update mechanism specified
            - keyboard shortcuts documented
            - runs in target terminal (Windows cmd/PowerShell/Linux term)
            """
        ).strip(),
    ),
    "windows-native-internals": SkillSpec(
        name="windows-native-internals",
        description="Use when work requires Windows-internal knowledge: NT APIs, PEB/TEB, kernel structures, SSDT, ETW, driver interaction, object manager, undocumented syscalls, or memory manager internals.",
        role="windows-internals-specialist",
        layer="layer-4-specialists-and-standalones",
        inputs=[
            "target Windows version",
            "NT API surface needed",
            "existing code context",
        ],
        outputs=[
            "Windows-native implementation",
            "API documentation",
            "version-conditional guards",
        ],
        references=[
            "Always declare which Windows version the code targets — offsets change.",
            "Never hardcode structure offsets without a version guard.",
            "Document whether ETW or PatchGuard is affected.",
            "Use ntdll imports or direct syscall — never assume high-level API availability in injected context.",
            "Open `references/windows-native-internals-operator-contract.md` when scope, evidence, or operator safety is unclear.",
            "Use `examples/windows-native-internals-good-output.md` and `examples/windows-native-internals-bad-output.md` to calibrate output quality.",
            "Use `evals/windows-native-internals-cases.json` as the minimum scenario set for behavior regression checks.",
            "Use `competencies/windows-native-internals-competencies.json` to check covered competencies, failure traps, and unknown-domain policy.",
        ],
        next_steps=[
            "cpp-systems-engineering",
            "process-injection-techniques",
            "edr-evasion-tactics",
            "telemetry-blinding",
            "binary-stealth-obfuscation",
            "field-journal-evolution",
        ],
        body=dedent(
            """\
            # Mission
            Apply Windows NT internals knowledge to implement, debug, or bypass Windows-native subsystems safely and correctly.
            
            ## Mandatory scope
            1. Identify the Windows version target: XP/7/10/11/Server — kernel structures change across versions.
            2. Name the NT API or structure being used: NtAllocateVirtualMemory, PEB, LDR_DATA_TABLE_ENTRY, etc.
            3. Declare whether the technique uses documented API, undocumented API, or direct syscall.
            4. Document SSDT/ETW/Callback implications for any kernel-touching operation.
            5. For usermode-kernel transitions: document syscall number, calling convention, and version dependency.
            6. Include version-conditional code where kernel structures differ across Windows releases.
            
            ## Evidence contract
            - Windows version target declared
            - API tier declared (documented / undocumented / direct syscall)
            - Structure offsets verified against target version
            - SSDT/ETW impact documented
            """
        ).strip(),
    ),
}


PUBLIC_ENTRYPOINT_SKILLS: Dict[str, SkillSpec] = {
    "brainstorm": SkillSpec(
        name="brainstorm",
        description='Use when a rough idea needs to become a clear direction before implementation begins. Public Relay-kit entrypoint for brainstorming.',
        role="specialist",
        layer="layer-4-specialists-and-standalones",
        inputs=[],
        outputs=[],
        references=[],
        next_steps=[],
        body=dedent(
            """\

            """
        ).strip(),
    ),
    "build-it": SkillSpec(
        name="build-it",
        description='Use when an approved story or tech spec is ready for implementation with controlled scope and evidence. Public Relay-kit entrypoint for building.',
        role="specialist",
        layer="layer-4-specialists-and-standalones",
        inputs=[],
        outputs=[],
        references=[],
        next_steps=[],
        body=dedent(
            """\

            """
        ).strip(),
    ),
    "debug-systematically": SkillSpec(
        name="debug-systematically",
        description='Use when a bug, regression, flaky behavior, or mismatch needs disciplined debugging instead of guessing. Public Relay-kit entrypoint for the debug path.',
        role="specialist",
        layer="layer-4-specialists-and-standalones",
        inputs=[],
        outputs=[],
        references=[],
        next_steps=[],
        body=dedent(
            """\

            """
        ).strip(),
    ),
    "prove-it": SkillSpec(
        name="prove-it",
        description='Use when a completion claim needs one last evidence pass before work is called done, fixed, or ready. Public Relay-kit entrypoint for final proof.',
        role="specialist",
        layer="layer-4-specialists-and-standalones",
        inputs=[],
        outputs=[],
        references=[],
        next_steps=[],
        body=dedent(
            """\

            """
        ).strip(),
    ),
    "ready-check": SkillSpec(
        name="ready-check",
        description='Use when code exists and you need a real go or no-go decision about readiness or shipability. Public Relay-kit entrypoint for review and QA gating.',
        role="specialist",
        layer="layer-4-specialists-and-standalones",
        inputs=[],
        outputs=[],
        references=[],
        next_steps=[],
        body=dedent(
            """\

            """
        ).strip(),
    ),
    "review-pr": SkillSpec(
        name="review-pr",
        description='Use when a branch or PR needs a deliberate review before merge or sign-off. Public Relay-kit entrypoint for branch and PR review.',
        role="specialist",
        layer="layer-4-specialists-and-standalones",
        inputs=[],
        outputs=[],
        references=[],
        next_steps=[],
        body=dedent(
            """\

            """
        ).strip(),
    ),
    "start-here": SkillSpec(
        name="start-here",
        description='Use when a request arrives and you want Relay-kit to pick the right path, next skill, and next artifact without guessing. Easiest public Relay-kit entrypoint.',
        role="specialist",
        layer="layer-4-specialists-and-standalones",
        inputs=[],
        outputs=[],
        references=[],
        next_steps=[],
        body=dedent(
            """\

            """
        ).strip(),
    ),
    "write-steps": SkillSpec(
        name="write-steps",
        description='Use when approved work needs to be sliced into small, buildable, verifiable implementation steps. Public Relay-kit entrypoint for implementation slicing.',
        role="specialist",
        layer="layer-4-specialists-and-standalones",
        inputs=[],
        outputs=[],
        references=[],
        next_steps=[],
        body=dedent(
            """\

            """
        ).strip(),
    ),
}


DELIVERY_SUPPORT_SKILLS: Dict[str, SkillSpec] = {
    # Engineering-discipline specialists. These shipped as .claude files
    # only for one release, which left them invisible to the routing graph
    # and to adapter parity; they are registered here so both can see them.
    "ci-cd-pipeline": SkillSpec(
        name="ci-cd-pipeline",
        description="Use when designing or fixing build, test, and deploy automation: pipeline stages, caching, required gates, environment promotion, artifact versioning, and rollback triggers.",
        role="cicd-specialist",
        layer="layer-4-specialists-and-standalones",
        inputs=[
            "existing CI config",
            "build and test commands",
            "deploy target and environments",
        ],
        outputs=[
            ".relay-kit/references/ci-cd.md",
            "pipeline config changes",
            "rollback runbook",
        ],
        references=[
            "Fail closed — a missing or errored gate blocks, it does not warn-and-pass.",
            "Build the artifact once and promote it; do not rebuild per environment.",
            "Every deploy path must have a tested rollback.",
            "Pin the toolchain; floating versions break reproducibility.",
        ],
        next_steps=[
            "release-readiness",
            "dependency-management",
            "secure-code-review",
            "incident-response",
        ],
        allowed_tools=EDIT_AND_TEST_TOOLS,
        body=dedent(
            """\
            # Mission
            Design a deterministic, fail-closed delivery pipeline where every merge is gated by reproducible checks and every deploy has a defined rollback.

            ## Mandatory scope
            1. Map stages: build, unit, integration, security scan, package, deploy — and which are blocking gates.
            2. Reproducibility: pinned toolchain, cached dependencies keyed by lockfile hash, deterministic build.
            3. Required gates: no merge to protected branch without passing gates and required reviews.
            4. Environment promotion: artifact built once, promoted across environments — never rebuilt per env.
            5. Rollback: a defined trigger, a tested rollback path, and a versioned previous artifact.

            ## Evidence contract
            - stage list with blocking vs non-blocking marked
            - cache key and toolchain pin declared
            - protected-branch gate rules stated
            - rollback trigger and path written
            """
        ).strip(),
    ),
    "database-migration-safety": SkillSpec(
        name="database-migration-safety",
        description="Use when a schema or data migration touches a live database: expand/contract sequencing, backfills, index builds, lock analysis, and a tested rollback for zero-downtime changes.",
        role="db-migration-specialist",
        layer="layer-4-specialists-and-standalones",
        inputs=[
            "migration script / schema diff",
            "table size and traffic profile",
            "deploy and rollback process",
        ],
        outputs=[
            ".relay-kit/references/db-migration.md",
            "sequenced migration plan",
            "rollback and backfill runbook",
        ],
        references=[
            "Never drop or rewrite before the new path is deployed and dual-writing.",
            "Avoid blocking locks on hot tables — use concurrent/online migration paths.",
            "Backfills must be batched, throttled, resumable, and idempotent.",
            "No destructive step without a confirmed backup and a rollback plan.",
        ],
        next_steps=[
            "data-persistence",
            "release-readiness",
            "ci-cd-pipeline",
            "incident-response",
        ],
        allowed_tools=EDIT_AND_TEST_TOOLS,
        body=dedent(
            """\
            # Mission
            Ship schema and data changes without downtime or data loss by sequencing expand-before-contract, analyzing locks, and proving a rollback.

            ## Mandatory scope
            1. Classify the change: additive (safe), rewriting (locking), or destructive (irreversible) — and treat each accordingly.
            2. Sequence expand/contract: add new columns/tables and dual-write before removing old ones across separate deploys.
            3. Analyze locking: check whether the migration takes a blocking lock on a hot table and prefer concurrent/online paths.
            4. Backfill safely: batch large backfills, throttle, and make them resumable and idempotent.
            5. Provide a tested rollback or forward-fix, and confirm a backup/point-in-time exists before destructive steps.

            ## Evidence contract
            - change classified (additive/rewriting/destructive)
            - expand-contract sequencing described across deploys
            - lock impact on hot tables assessed
            - rollback/forward-fix and backup confirmation stated
            """
        ).strip(),
    ),
    "incident-response": SkillSpec(
        name="incident-response",
        description="Use when a production incident is active or just resolved: triage severity, stabilize, communicate status, capture a timeline, and write a blameless postmortem with real action items.",
        role="incident-responder",
        layer="layer-4-specialists-and-standalones",
        inputs=[
            "alert / incident report",
            "system state, logs, and metrics",
            "recent changes and deploys",
        ],
        outputs=[
            "incident status updates",
            "incident timeline",
            ".relay-kit/references/postmortem-<id>.md",
        ],
        references=[
            "Stabilize before rooting-cause; stop user impact first.",
            "Keep communication factual — label hypotheses as hypotheses.",
            "Blameless postmortems focus on systemic factors, never individuals.",
            "Every action item has an owner and a date, or it is not real.",
        ],
        next_steps=[
            "root-cause-debugging",
            "observability-instrumentation",
            "fix-hub",
            "ci-cd-pipeline",
        ],
        allowed_tools=READ_ANALYZE_TOOLS,
        body=dedent(
            """\
            # Mission
            Drive a production incident from detection to a blameless postmortem: stabilize first, communicate clearly, and convert the timeline into durable fixes.

            ## Mandatory scope
            1. Assign severity from user impact and scope, and name the incident commander role.
            2. Stabilize before diagnosing deeply: mitigate (roll back, feature-flag, scale) to stop the bleeding.
            3. Communicate: a status cadence with impact, current action, and next update time — no speculation as fact.
            4. Capture a timeline with timestamps: detection, actions, and their effect.
            5. Write a blameless postmortem: contributing factors, not blame, plus owned, dated action items.

            ## Evidence contract
            - severity assigned from stated user impact
            - mitigation taken before deep diagnosis
            - timeline with timestamps captured
            - postmortem with blameless framing and owned action items
            """
        ).strip(),
    ),
    "observability-instrumentation": SkillSpec(
        name="observability-instrumentation",
        description="Use when a service needs structured logging, metrics, distributed tracing, health checks, or SLO-backed alerting so failures are diagnosable in production.",
        role="observability-specialist",
        layer="layer-4-specialists-and-standalones",
        inputs=[
            "service code / handlers",
            "existing logging or metrics setup",
            "incident or failure context if present",
        ],
        outputs=[
            ".relay-kit/references/observability.md",
            "instrumentation code changes",
            "SLO and alert definitions",
        ],
        references=[
            "Instrument to answer a failure question, not to collect everything.",
            "Never log secrets or PII; redact at the boundary.",
            "Watch label cardinality — unbounded labels break the metrics backend.",
            "Alert on user-visible symptoms; keep cause-level signals for debugging.",
        ],
        next_steps=[
            "release-readiness",
            "incident-response",
            "performance-optimization",
            "runtime-doctor",
        ],
        allowed_tools=EDIT_AND_TEST_TOOLS,
        body=dedent(
            """\
            # Mission
            Make a service diagnosable in production by instrumenting logs, metrics, traces, and alerts against explicit failure questions, not vanity dashboards.

            ## Mandatory scope
            1. Name the top failure questions the instrumentation must answer (latency, error rate, saturation, a specific bug class).
            2. Structured logging: correlation/request id, level discipline, no secrets/PII in logs.
            3. Metrics: RED (rate, errors, duration) for request paths and USE for resources; name and label cardinality budget.
            4. Tracing: span boundaries at service and external-call edges, propagation of trace context.
            5. SLOs and alerts: define SLI, target, and alert that pages on symptom (burn rate) not on cause noise.

            ## Evidence contract
            - each signal maps to a named failure question it answers
            - log/metric/trace field list with a no-PII confirmation
            - at least one SLI + SLO + alert rule written
            - cardinality budget stated for metric labels
            """
        ).strip(),
    ),
    "performance-optimization": SkillSpec(
        name="performance-optimization",
        description="Use when latency, throughput, memory, or cost regresses and needs disciplined profiling: measure a baseline, find the real bottleneck, fix the hot path, and prove the gain.",
        role="performance-specialist",
        layer="layer-4-specialists-and-standalones",
        inputs=[
            "hot path or slow endpoint",
            "profiling access or benchmark harness",
            "target metric and budget",
        ],
        outputs=[
            ".relay-kit/references/performance.md",
            "optimized code",
            "before/after benchmark evidence",
        ],
        references=[
            "Never optimize without a baseline measurement.",
            "Profile before changing — intuition about hot paths is often wrong.",
            "Change one variable at a time so the delta is attributable.",
            "Prove the gain on the same workload; a faster microbenchmark is not a faster system.",
        ],
        next_steps=[
            "observability-instrumentation",
            "testing-patterns",
            "review-hub",
            "runtime-doctor",
        ],
        allowed_tools=EDIT_AND_TEST_TOOLS,
        body=dedent(
            """\
            # Mission
            Fix performance by measurement, not guesswork: establish a baseline, profile to the real bottleneck, change one thing, and prove the delta.

            ## Mandatory scope
            1. Define the metric and workload: p50/p95/p99 latency, throughput, memory, or cost, under a stated load.
            2. Capture a baseline measurement before changing anything.
            3. Profile to locate the dominant cost (CPU, allocations, I/O, N+1 queries, lock contention) — do not assume.
            4. Change one variable, then re-measure against the same workload.
            5. Guard against regression: keep or add a benchmark so the gain does not silently erode.

            ## Evidence contract
            - baseline number with workload and environment stated
            - profiler evidence identifying the bottleneck
            - after number from the same workload, with the delta
            - benchmark or check that locks in the improvement
            """
        ).strip(),
    ),
    "refactoring-discipline": SkillSpec(
        name="refactoring-discipline",
        description="Use when restructuring code without changing behavior: extract, rename, split, or de-duplicate under a green test suite with small reversible steps and a characterization safety net.",
        role="refactor-discipline",
        layer="layer-4-specialists-and-standalones",
        inputs=[
            "target code / smell",
            "existing test suite",
            "behavior-preservation requirement",
        ],
        outputs=[
            "refactored code",
            "added characterization tests if needed",
            "commit plan separating refactor from behavior",
        ],
        references=[
            "No refactor without a green test net — add characterization tests first if needed.",
            "Never mix a refactor with a behavior change in one commit.",
            "Run the suite after each small step, not only at the end.",
            "If behavior must change, that is not a refactor — route to the developer loop.",
        ],
        next_steps=[
            "test-first-development",
            "developer",
            "review-hub",
            "testing-patterns",
        ],
        allowed_tools=EDIT_AND_TEST_TOOLS,
        body=dedent(
            """\
            # Mission
            Change structure while proving behavior is preserved: lean on a green test net, move in small reversible steps, and keep commits atomic.

            ## Mandatory scope
            1. Confirm a passing test net covers the target; if coverage is thin, add characterization tests first.
            2. Separate refactor commits from behavior-change commits — never mix them.
            3. Move in small reversible steps; run tests after each step.
            4. Preserve the public contract (signatures, outputs, side effects) unless the task is explicitly to change it.
            5. State the risk if the safety net is incomplete, and what is unverified.

            ## Evidence contract
            - test net status before and after (green -> green)
            - characterization tests added when coverage was thin
            - refactor and behavior changes kept in separate commits
            - public contract confirmed unchanged (or the change called out)
            """
        ).strip(),
    ),
    "secure-code-review": SkillSpec(
        name="secure-code-review",
        description="Use when application code needs a defensive security review before merge or release: injection, authn/authz, secrets handling, crypto misuse, SSRF, deserialization, and vulnerable dependencies.",
        role="security-reviewer",
        layer="layer-3-utility-providers",
        inputs=[
            "diff or changed files",
            "authoritative artifact / PR",
            "threat context if provided",
        ],
        outputs=[
            "security review findings appended to review notes or qa-report",
            "pass or hold verdict with severities",
        ],
        references=[
            "No pass verdict while any critical or high finding is unresolved.",
            "Trace input-to-sink; do not flag on keyword match alone.",
            "This is defensive review only — it hardens code, it does not build offensive tooling.",
            "Hand unresolved findings to fix-hub with explicit acceptance criteria.",
        ],
        next_steps=[
            "fix-hub",
            "review-hub",
            "qa-governor",
            "dependency-management",
                    "secrets-management",
            "privacy-compliance",
        ],
        allowed_tools=READ_ANALYZE_TOOLS,
        body=dedent(
            """\
            # Mission
            Turn security from implicit trust into an explicit, evidence-backed defensive review gate over real code paths, not a generic checklist.

            ## Mandatory scope
            1. Identify the trust boundary: where untrusted input enters (HTTP params, headers, files, queues, env) and where it reaches a sink.
            2. Check injection sinks: SQL/NoSQL, OS command, template, LDAP, and path traversal — confirm parameterization or safe APIs.
            3. Check authn/authz: every state-changing route enforces identity and object-level authorization, not just authentication.
            4. Check secrets: no hardcoded keys/tokens, secrets sourced from env/vault, and no secret logged.
            5. Check crypto and randomness: no weak hashing for passwords, no ECB, no static IV, CSPRNG for tokens.
            6. Check dependencies: flag known-vulnerable versions and unpinned critical packages.

            ## Evidence contract
            - each finding names file:line, the tainted input, and the sink
            - severity assigned (critical/high/medium/low) with exploitability rationale
            - a concrete fix or safe-API replacement per finding
            - pass or hold verdict tied to whether any critical/high finding is unresolved
            """
        ).strip(),
    ),
    "technical-writing": SkillSpec(
        name="technical-writing",
        description="Use when authoring or revising technical documentation: READMEs, API references, runbooks, architecture docs, onboarding guides, or changelogs that must be accurate against the code.",
        role="docs-author",
        layer="layer-4-specialists-and-standalones",
        inputs=[
            "code or feature to document",
            "existing docs if any",
            "audience and purpose",
        ],
        outputs=[
            "the documentation artifact (README/runbook/API doc)",
            "list of verified commands and paths",
        ],
        references=[
            "Never document a command or flag you did not verify against the repo.",
            "Write for one audience and one task; split docs rather than blending them.",
            "Label unknowns; do not invent behavior to fill a gap.",
            "Prefer showing a verified example over describing behavior abstractly.",
        ],
        next_steps=[
            "review-hub",
            "doc-pointers",
            "vietnamese-product-localization",
            "release-readiness",
        ],
        allowed_tools=[
            "Read",
            "Write",
            "Edit",
            "Grep",
            "Glob",
        ],
        body=dedent(
            """\
            # Mission
            Produce documentation that is accurate against the current code, scoped to a named audience and task, and verifiable — not aspirational prose.

            ## Mandatory scope
            1. Name the audience and the single task the doc must enable (install, integrate, operate, decide).
            2. Verify every command, path, flag, and code sample against the actual repo before writing it.
            3. Structure for the task: quickstart first, reference second, rationale last.
            4. Mark unknowns explicitly rather than inventing behavior.
            5. State how the doc stays current (owner, source of truth, or generated section).

            ## Evidence contract
            - audience and enabled task named
            - every command/path in the doc traced to a real file or verified run
            - unknowns labeled, not fabricated
            - staleness/ownership note included
            """
        ).strip(),
    ),
}


NEW_CAPABILITY_SKILLS: Dict[str, SkillSpec] = {
    # Capability gaps a "maximum" kit needs: LLM app engineering, cloud/infra,
    # container ops, secrets, an MMO authorization gate, and privacy/compliance.
    "llm-app-engineering": SkillSpec(
        name="llm-app-engineering",
        description="Use when building an LLM-powered application feature such as prompt and context design, retrieval-augmented generation, tool and function schemas, agent loops, or offline evals, and correctness and cost must be proven rather than assumed.",
        role="llm-application-engineer",
        layer="layer-4-specialists-and-standalones",
        inputs=[
            "the product behavior the LLM feature must deliver",
            "available context sources or retrieval corpus",
            "latency, cost, and accuracy constraints",
        ],
        outputs=[
            "prompt and context contract",
            "tool or function schemas",
            "an offline eval set with pass criteria",
        ],
        references=[],
        next_steps=["developer", "secure-code-review", "test-hub", "review-hub"],
        allowed_tools=EDIT_AND_TEST_TOOLS,
        body=dedent(
            """\
            # Mission
            Build an LLM feature as a measurable system: an explicit prompt/context contract, typed tool schemas, and an offline eval that gates changes -- not a hand-tuned prompt nobody can regress.

            ## Mandatory scope
            1. Declare the model target and version, the context window budget, and the accuracy/latency/cost ceiling the feature must hold.
            2. Prompt and context: separate the stable system contract from per-request context; state how context is selected and truncated.
            3. Retrieval (if any): name the corpus, chunking, embedding model, and the top-k and score threshold; prove relevant chunks actually reach the prompt.
            4. Tools: define each tool as a typed schema with required fields and a validation path; state what happens when the model returns malformed arguments.
            5. Agent loop (if any): bound the step count, define the stop condition, and name the failure mode when the loop does not converge.
            6. Evals: build an offline case set with expected outputs or graders, and a pass threshold that a change must clear before merge.

            ## Evidence contract
            - model + version + context budget declared
            - prompt/context contract and truncation rule stated
            - tool schemas with malformed-argument handling
            - offline eval set with a numeric pass threshold and the current score
            - cost-per-request estimate for the chosen model

            ## Failure modes to block
            - Prompt tuning with no eval to catch regressions.
            - Retrieval that returns chunks the prompt never actually uses.
            - Tool calls trusted without validating the model's arguments.
            - An unbounded agent loop with no stop condition.

            ## Handoff
            - Hand implementation to `developer`, defensive review of tool/argument handling to `secure-code-review`, and eval wiring to `test-hub`.
            """
        ).strip(),
    ),
    "iac-cloud-provisioning": SkillSpec(
        name="iac-cloud-provisioning",
        description="Use when provisioning or changing cloud infrastructure as code with Terraform, Pulumi, or CloudFormation, including state management, drift detection, plan review, and a safe apply with rollback.",
        role="infrastructure-engineer",
        layer="layer-4-specialists-and-standalones",
        inputs=[
            "the infrastructure change requested",
            "current IaC state and provider",
            "environment and blast-radius constraints",
        ],
        outputs=[
            "reviewed plan diff",
            "apply and rollback runbook",
            "drift and state notes",
        ],
        references=[],
        next_steps=["container-kubernetes-ops", "secrets-management", "release-readiness", "review-hub"],
        allowed_tools=EDIT_AND_TEST_TOOLS,
        body=dedent(
            """\
            # Mission
            Change cloud infrastructure through reviewed, reversible plans -- never console-clicked mutations -- with state and drift kept honest.

            ## Mandatory scope
            1. Declare the tool and provider (Terraform, Pulumi, CloudFormation) and where state lives, including locking.
            2. Always run and read a plan/diff before apply; state exactly which resources create, update, replace, or destroy.
            3. Flag every destroy or replace on a stateful resource (database, volume, load balancer) as high blast-radius and require explicit confirmation.
            4. Detect drift: compare real state to code before changing anything, and reconcile or document it.
            5. Define the apply order and the rollback path (previous state, tainted-resource recovery, or a reverse change).
            6. Keep secrets out of state and code; hand credential material to `secrets-management`.

            ## Evidence contract
            - tool, provider, and state backend declared
            - plan diff read, with create/update/replace/destroy counts
            - blast-radius call-out for any stateful replace or destroy
            - rollback path written before apply

            ## Failure modes to block
            - Applying without reading the plan.
            - A destroy/replace on a stateful resource slipping through unflagged.
            - Secrets committed into state or variables.
            - Drift ignored so the next apply does something unexpected.

            ## Handoff
            - Hand workload packaging to `container-kubernetes-ops`, credentials to `secrets-management`, and the go/no-go to `release-readiness`.
            """
        ).strip(),
    ),
    "container-kubernetes-ops": SkillSpec(
        name="container-kubernetes-ops",
        description="Use when packaging services into containers or operating Kubernetes workloads, including Dockerfiles, image hygiene, manifests, resource limits, probes, rollouts, and cluster troubleshooting.",
        role="platform-engineer",
        layer="layer-4-specialists-and-standalones",
        inputs=[
            "the service to containerize or the workload to operate",
            "existing Dockerfile or manifests",
            "cluster and resource constraints",
        ],
        outputs=[
            "Dockerfile or manifest changes",
            "rollout and probe configuration",
            "troubleshooting notes",
        ],
        references=[],
        next_steps=["iac-cloud-provisioning", "secrets-management", "observability-instrumentation", "review-hub"],
        allowed_tools=EDIT_AND_TEST_TOOLS,
        body=dedent(
            """\
            # Mission
            Ship containers and Kubernetes workloads that start predictably, fail visibly, and roll out without taking traffic down.

            ## Mandatory scope
            1. Image hygiene: pinned base image, non-root user, minimal layers, no secrets baked in, a reproducible build.
            2. Manifests: explicit resource requests and limits, liveness and readiness probes that reflect real health, and a restart policy.
            3. Rollout: a strategy (rolling or blue-green) with surge/unavailable bounds and a defined rollback to the previous revision.
            4. Config and secrets: config via ConfigMap/env, secrets via a secret store -- never in the image or manifest literal.
            5. Troubleshooting: read events, logs, and probe status before mutating; name the failing signal, not a guess.

            ## Evidence contract
            - base image pinned and container runs non-root
            - resource requests/limits and both probes defined
            - rollout strategy and rollback revision named
            - secrets sourced from a store, not the manifest

            ## Failure modes to block
            - Running as root or baking secrets into the image.
            - Missing readiness probe, so a rollout sends traffic to a not-ready pod.
            - No resource limits, so one workload starves the node.
            - Restarting or deleting pods before reading events and logs.

            ## Handoff
            - Hand infrastructure to `iac-cloud-provisioning`, secret material to `secrets-management`, and health signals to `observability-instrumentation`.
            """
        ).strip(),
    ),
    "secrets-management": SkillSpec(
        name="secrets-management",
        description="Use when handling secrets, API keys, tokens, or wallet keys across a fleet and you need vaulting, injection, rotation, scoping, and leak response instead of plaintext credentials.",
        role="secrets-engineer",
        layer="layer-4-specialists-and-standalones",
        inputs=[
            "the secrets or credentials in play",
            "where they are currently stored and consumed",
            "rotation and scoping requirements",
        ],
        outputs=[
            "a secret storage and injection plan",
            "rotation and scoping policy",
            "a leak-response runbook",
        ],
        references=[],
        next_steps=["iac-cloud-provisioning", "container-kubernetes-ops", "secure-code-review", "review-hub"],
        allowed_tools=READ_ANALYZE_TOOLS,
        body=dedent(
            """\
            # Mission
            Keep every credential out of source and out of plaintext: vaulted at rest, injected at runtime, scoped to least privilege, and rotatable without downtime.

            ## Mandatory scope
            1. Inventory: name each secret, where it lives now, and who reads it; flag any that sit in code, config, or logs.
            2. Storage: move secrets to a vault or platform secret store; the app reads them at runtime, never from a committed file.
            3. Scoping: grant each consumer the narrowest credential that works; no shared god-tokens across services.
            4. Rotation: define a rotation interval and a zero-downtime rotation path (dual-key or overlap window).
            5. Leak response: define detection, immediate revocation, rotation, and blast-radius assessment for an exposed secret.

            ## Evidence contract
            - secret inventory with current storage location per item
            - vault/store as the source of truth, injection path named
            - least-privilege scoping stated per consumer
            - rotation interval and zero-downtime rotation path
            - leak-response steps: detect, revoke, rotate, assess

            ## Failure modes to block
            - A secret left in source control, an env file, or a log line.
            - One shared token used everywhere so revocation breaks everything.
            - No rotation path, so a leak means a painful emergency.
            - Handling the plaintext value directly instead of a reference.

            ## Handoff
            - This skill never enters credential values itself; it hands entry to the operator. Hand consuming infra to `iac-cloud-provisioning` and `container-kubernetes-ops`, and code-path review to `secure-code-review`.
            """
        ).strip(),
    ),
    "privacy-compliance": SkillSpec(
        name="privacy-compliance",
        description="Use when a workload collects, stores, or transfers personal data and needs a privacy and data-retention gate covering PII minimization, consent or lawful basis, retention limits, and deletion.",
        role="privacy-reviewer",
        layer="layer-4-specialists-and-standalones",
        inputs=[
            "the data the workload collects or processes",
            "the stated purpose and legal context",
            "current storage, sharing, and retention behavior",
        ],
        outputs=[
            "a data inventory with PII classification",
            "a retention and deletion policy",
            "a consent and lawful-basis note",
        ],
        references=[],
        next_steps=["data-persistence", "secure-code-review", "secrets-management", "review-hub"],
        allowed_tools=READ_ANALYZE_TOOLS,
        body=dedent(
            """\
            # Mission
            Treat personal data as a liability to minimize: collect only what the purpose needs, keep it only as long as justified, and be able to delete it on request.

            ## Mandatory scope
            1. Inventory: enumerate the personal data collected, classify sensitivity (contact, financial, health, biometric, identifier), and name where each field flows.
            2. Minimization: for every field, state the purpose that justifies it; drop fields no purpose needs.
            3. Lawful basis and consent: state the basis for processing each category and where consent is captured, if required.
            4. Retention: set a retention window per category and the mechanism that deletes or anonymizes past it.
            5. Rights: define how access, correction, and deletion requests are fulfilled, including in backups and downstream copies.
            6. Transfer: flag any cross-border or third-party transfer and the safeguard that covers it.

            ## Evidence contract
            - data inventory with per-field sensitivity classification
            - a stated purpose for every retained field
            - retention window and deletion mechanism per category
            - a deletion path that reaches backups and downstream copies

            ## Failure modes to block
            - Collecting data with no purpose behind it.
            - Indefinite retention with no deletion mechanism.
            - A deletion request that leaves copies in backups or a data warehouse.
            - PII in logs, analytics, or third-party tools without a safeguard.

            ## Handoff
            - Hand schema and retention enforcement to `data-persistence`, secret handling to `secrets-management`, and code-path review to `secure-code-review`.
            """
        ).strip(),
    ),
}


MMO_AUTHORIZATION_GATE_SKILL: Dict[str, SkillSpec] = {
    "mmo-authorization-gate": utility_provider_spec(
        name="mmo-authorization-gate",
        description="Use when an MMO or automation lane touches a third-party platform and needs an explicit terms-of-service, authorization, and account-risk gate before high-risk actions run.",
        outputs=[
            "an authorization verdict appended to workflow-state",
            "a documented account-risk and ToS assessment",
        ],
        references=[
            "Record the operator's authorization and account ownership before any high-risk action.",
            "Treat platform terms-of-service and rate limits as hard constraints, not suggestions.",
        ],
        next_steps=["policy-guard", "qa-governor", "review-hub"],
        mission="Gate MMO and automation lanes behind an explicit authorization, account-ownership, and platform-terms check before any high-risk action runs.",
        boundary=[
            "Use for lanes that act against a third-party platform on accounts the operator controls.",
            "This gate records authorization and risk; it does not itself perform the automation.",
            "It does not override platform terms; unauthorized or ToS-violating actions are refused, not gated.",
        ],
        evidence_contract=[
            "Input must state the platform, the accounts, and who authorizes the action.",
            "Output must record an explicit authorized/blocked verdict with the reason.",
            "Block any lane that cannot show account ownership or operator authorization.",
        ],
        tasks=[
            "Name the target platform and the accounts the lane will act on.",
            "Confirm the operator owns or is authorized to act on those accounts.",
            "Assess account-risk tier and the platform terms and rate limits that apply.",
            "Emit an authorized-or-blocked verdict before the lane proceeds.",
        ],
        rules=[
            "No high-risk action proceeds without a recorded authorization verdict.",
            "Platform terms-of-service and rate limits are hard constraints.",
            "When ownership or authorization is unclear, fail closed and block the lane.",
            "Hand the runtime safety scan to policy-guard; this gate owns authorization, not shell/secret risk.",
        ],
        allowed_tools=READ_ANALYZE_TOOLS,
    ),
}


ALL_V3_SKILLS: Dict[str, SkillSpec] = {}
ALL_V3_SKILLS.update(ORCHESTRATOR_SKILLS)
ALL_V3_SKILLS.update(WORKFLOW_HUB_SKILLS)
ALL_V3_SKILLS.update(ROLE_SKILLS)
ALL_V3_SKILLS.update(UTILITY_PROVIDER_SKILLS)
ALL_V3_SKILLS.update(DISCIPLINE_UTILITY_SKILLS)
ALL_V3_SKILLS.update(CLEANUP_SKILLS)
ALL_V3_SKILLS.update(NATIVE_SUPPORT_SKILLS)
ALL_V3_SKILLS.update(DELIVERY_SUPPORT_SKILLS)
ALL_V3_SKILLS.update(NEW_CAPABILITY_SKILLS)
ALL_V3_SKILLS.update(MMO_AUTHORIZATION_GATE_SKILL)
ALL_V3_SKILLS.update(OFFENSIVE_TOOL_PACK_SKILLS)
# PUBLIC_ENTRYPOINT_SKILLS are deliberately NOT registered: the eight shims are
# adapter facades emitted by relay_kit_v3.public_entrypoint_facades, not routable
# registry skills. Keeping them out of ALL_V3_SKILLS is what makes the routing
# graph, bundles, and catalog exclude them (see test_repo_hardening_gates).


def _with_resource_references(skill_name: str, spec: SkillSpec) -> SkillSpec:
    references = list(spec.references)
    for reference in domain_resource_references(skill_name):
        if reference not in references:
            references.append(reference)
    if references == spec.references:
        return spec
    return replace(spec, references=references)


ALL_V3_SKILLS = {
    skill_name: _with_resource_references(skill_name, spec)
    for skill_name, spec in ALL_V3_SKILLS.items()
}


def _render_yaml_scalar(value: str) -> str:
    """Quote a frontmatter scalar so the block always parses as YAML.

    Descriptions routinely read ``Use when X: Y``. Emitted bare, that colon
    turns the line into a nested mapping and the whole block fails to load --
    the loader then falls back to the body's first heading and the skill's
    routing trigger silently dies.
    """
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def render_skill(spec: SkillSpec, *, description_override: str | None = None) -> str:
    description = description_override if description_override is not None else spec.description
    parts = [
        "---",
        f"name: {spec.name}",
        f"description: {_render_yaml_scalar(description)}",
    ]
    if spec.allowed_tools:
        parts.append(f"allowed-tools: {_render_yaml_inline_list(spec.allowed_tools)}")
    # paths/context/effort are Relay-kit routing hints, not part of the SKILL.md
    # schema the runtime recognises. Emitted at the top level they are dropped
    # at load time; under `metadata` they survive and stay schema-legal.
    metadata: list[str] = []
    if spec.paths:
        metadata.append(f"  paths: {_render_yaml_inline_list(spec.paths)}")
    if spec.context:
        metadata.append(f"  context: {_render_yaml_scalar(spec.context)}")
    if spec.effort:
        metadata.append(f"  effort: {_render_yaml_scalar(spec.effort)}")
    if metadata:
        parts.append("metadata:")
        parts.extend(metadata)
    parts.extend([
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
    ])
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


def _render_yaml_inline_list(items: List[str]) -> str:
    quoted = [f'"{item.replace(chr(34), chr(92) + chr(34))}"' for item in items]
    return "[" + ", ".join(quoted) + "]"
