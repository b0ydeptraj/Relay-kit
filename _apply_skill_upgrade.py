#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Relay-kit skill maximizer / deploy script.
Run: python deploy_skills.py <RELAY_KIT_ROOT>
Writes: BOM fixes, support files for 3 benign skills, 8 new skills (SKILL.md + 5 support files),
        and updates skills.manifest.yaml.
Idempotent: safe to re-run.
"""
import os, sys, json, io

ROOT = sys.argv[1] if len(sys.argv) > 1 else "."
GEN_AT = "2026-07-26T00:00:00+00:00"

def w(rel, content, binary=False):
    p = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    mode = "wb" if binary else "w"
    with io.open(p, mode) as f:
        if binary:
            f.write(content)
        else:
            f.write(content if content.endswith("\n") else content + "\n")
    print("wrote", rel)

# ---------------------------------------------------------------------------
# 1. BOM FIX -- read existing file on device, strip UTF-8 BOM, rewrite
# ---------------------------------------------------------------------------
BOM_FIX = [
    ".claude/skills/build-it/SKILL.md",
    ".claude/skills/debug-systematically/SKILL.md",
    ".claude/skills/ready-check/SKILL.md",
    ".claude/skills/review-pr/SKILL.md",
    ".claude/skills/start-here/SKILL.md",
    ".claude/skills/write-steps/SKILL.md",
]
def fix_bom():
    for rel in BOM_FIX:
        p = os.path.join(ROOT, rel)
        if not os.path.exists(p):
            print("SKIP (missing)", rel); continue
        raw = open(p, "rb").read()
        if raw.startswith(b"\xef\xbb\xbf"):
            open(p, "wb").write(raw[3:])
            print("bom-stripped", rel)
        else:
            print("no-bom", rel)

# ---------------------------------------------------------------------------
# Templates for the 5 support files (the "battle contract" family)
# ---------------------------------------------------------------------------
def operator_contract(sk, role, layer, family, repo_profile, files, symbols, evidence_terms, failure_modes):
    fl = "\n".join(f"  - {x}" for x in files) if files else "  - (name the anchor or say which is missing)"
    return f"""# {sk} Battle Contract

Primary role: {role}
Layer: {layer}
Battle family: {family}

Use this skill only after the request is anchored to a real artifact, repo area, or explicit missing-context question. The goal is not to sound like an expert; the goal is to reduce ambiguity by tying the answer to files, symbols, commands, docs, logs, or state.

## Concrete Battle Profile

- Repo profile: {repo_profile}
- First files to inspect:
{fl}
- Symbols or named surfaces to confirm: {", ".join(symbols)}
- Evidence terms that should appear in a strong answer: {", ".join(evidence_terms)}

## Working Loop

1. Restate the user task as a verifiable repo action.
2. Name the candidate files before giving advice.
3. Check at least one source file and one proof surface when the task touches code, config, docs, release, or automation.
4. Separate verified facts, inferred risk, and unknowns.
5. End with the next executable check or handoff, not broad process advice.

## Failure Modes To Block

""" + "\n".join(f"- {m}" for m in failure_modes) + """

## Evidence Checklist

- File evidence: cite exact paths or say which anchor is missing.
- Behavior evidence: cite test, scan, metric, log line, screenshot, or command output.
- Risk evidence: name residual risk and the smallest next verification.
- Handoff evidence: name the receiving skill or gate when another lane should continue.
"""

def evals(sk, repo_profile, files, symbols, tests, evidence_terms, traps):
    def case(cid, task, ev):
        return {
            "id": cid, "skill": sk, "repo_profile": repo_profile, "task": task,
            "expected_files": files, "expected_symbols": symbols, "expected_tests": tests,
            "expected_evidence_terms": ev, "bad_answer_traps": traps,
        }
    core = evidence_terms[:2] + ["verified", "residual risk"]
    ro = evidence_terms[2:4] + ["read-only", "unverified"] if len(evidence_terms) >= 4 else evidence_terms + ["read-only", "unverified"]
    deep = evidence_terms[:2] + ["weak evidence", "claim status", "residual risk"]
    data = [
        case(f"{sk}-battle-read-first",
             f"handle a {sk} request, name files first, and identify the proof surface before editing. Use `{sk}` and cite the first files before advice.",
             core),
        case(f"{sk}-public-repo-benchmark-anchor",
             f"Run a read-only benchmark-style pass for `{sk}` and explain what evidence is still missing.",
             ro),
        case(f"{sk}-deep-weakness-trap",
             f"Score `{sk}` against a deep case, identify weak evidence, and avoid claiming maximum strength until files, symbols, proof, and residual risk are shown.",
             deep),
    ]
    return json.dumps(data, indent=2, ensure_ascii=False)

def good_output(sk, role, files, symbols, evidence_terms):
    fl = "\n".join(f"- `{x}`" for x in files)
    return f"""# {sk} Battle-Calibrated Output

Request: handle a {sk} request, name files first, and identify the proof surface before editing

Recommended skill: `{sk}` because the request matches `{role}` work and has concrete repo anchors.

Read first:

{fl}

Evidence gathered:

- Confirmed `{symbols[0] if symbols else 'the primary surface'}` ownership before recommending changes.
- Checked `{evidence_terms[0]}` and `{evidence_terms[1] if len(evidence_terms)>1 else evidence_terms[0]}` against the relevant source path.
- Identified `{evidence_terms[2] if len(evidence_terms)>2 else evidence_terms[-1]}` as a required proof term before completion.

Answer:

The safe next move is to inspect the named path, compare it with the expected test, metric, config, or docs surface, and only then choose implementation, review, or planning. If the anchor is missing, ask one question that names the missing file, PR, log, screen, or workflow.

Residual risk:

- `{evidence_terms[-1]}` remains unverified until the focused gate or proof surface is captured.
"""

def bad_output(sk, repo_profile, symbols, evidence_terms):
    return f"""# {sk} Weak Output Anti-Example

Request: handle a {sk} request, name files first, and identify the proof surface before editing

Weak answer:

This looks like `{sk}`, so follow the usual checklist and it should be fine.

Why this fails:

- No file path from `{repo_profile}` was inspected.
- No symbol such as `{symbols[0] if symbols else 'the primary surface'}` was confirmed.
- No proof surface was named for `{evidence_terms[0]}`.
- It blurs verified evidence and inference, which is exactly how overclaim slips back into Relay-kit.

Correction:

Name the concrete path, inspect or search it, state what is verified, and leave unverified claims labeled until a gate proves them.
"""

def competencies(sk, role, category, comps, traps):
    return json.dumps({
        "schema_version": "relay-kit.skill-competency.v1",
        "skill": sk, "role": role, "category": category,
        "core_competencies": [
            {"id": c["id"], "label": c["label"], "evidence_terms": c["terms"], "archetypes": c["arch"]}
            for c in comps
        ],
        "failure_traps": [{"id": t[0], "description": t[1]} for t in traps],
        "unknown_domain_policy": "scout_first_without_expert_claim",
        "claim_policy": "competency-covered only when every core competency is present and battle evidence passes.",
        "generated_at": GEN_AT,
    }, indent=2, ensure_ascii=False)

def write_support(sk, spec):
    base = f".claude/skills/{sk}"
    w(f"{base}/references/{sk}-operator-contract.md",
      operator_contract(sk, spec["role"], spec["layer"], spec["family"], spec["repo_profile"],
                        spec["files"], spec["symbols"], spec["evidence_terms"], spec["failure_modes"]))
    w(f"{base}/evals/{sk}-cases.json",
      evals(sk, spec["repo_profile"], spec["files"], spec["symbols"], spec["tests"],
            spec["evidence_terms"], spec["traps_short"]))
    w(f"{base}/examples/{sk}-good-output.md",
      good_output(sk, spec["role"], spec["files"], spec["symbols"], spec["evidence_terms"]))
    w(f"{base}/examples/{sk}-bad-output.md",
      bad_output(sk, spec["repo_profile"], spec["symbols"], spec["evidence_terms"]))
    w(f"{base}/competencies/{sk}-competencies.json",
      competencies(sk, spec["role"], spec["category"], spec["competencies"], spec["failure_traps"]))

# ---------------------------------------------------------------------------
# SKILL.md body builder for NEW skills
# ---------------------------------------------------------------------------
def skill_md(sk, spec):
    tools = spec.get("allowed_tools")
    fm = f'name: {sk}\ndescription: {spec["description"]}'
    if tools:
        fm += f'\nallowed-tools: {json.dumps(tools)}'
    scope = "\n".join(f"{i+1}. {s}" for i, s in enumerate(spec["mandatory_scope"]))
    evid = "\n".join(f"- {s}" for s in spec["evidence_contract"])
    inputs = "\n".join(f"- {s}" for s in spec["inputs"])
    outputs = "\n".join(f"- {s}" for s in spec["outputs"])
    rules = "\n".join(f"- {s}" for s in spec["rules"])
    nxt = "\n".join(f"- {s}" for s in spec["likely_next"])
    return f"""---
{fm}
---

# Mission
{spec["mission"]}

## Mandatory scope
{scope}

## Evidence contract
{evid}

## Role
- {spec["role"]}

## Layer
- {spec["layer"]}

## Inputs
{inputs}

## Outputs
{outputs}

## Reference skills and rules
{rules}
- Open `references/{sk}-operator-contract.md` when scope, evidence, or operator safety is unclear.
- Use `examples/{sk}-good-output.md` and `examples/{sk}-bad-output.md` to calibrate output quality.
- Use `evals/{sk}-cases.json` as the minimum scenario set for behavior regression checks.
- Use `competencies/{sk}-competencies.json` to check covered competencies, failure traps, and unknown-domain policy.

## Likely next step
{nxt}
"""

def write_new_skill(sk, spec):
    w(f".claude/skills/{sk}/SKILL.md", skill_md(sk, spec))
    write_support(sk, spec)

# ===========================================================================
# SPECS
# ===========================================================================

# ---- 3 benign skills: support files only (SKILL.md already exists) ----------
BENIGN = {
"aesthetic": {
    "role": "aesthetic-review", "layer": "layer-4-specialists-and-standalones",
    "family": "frontend", "category": "frontend-quality",
    "repo_profile": "product UI repo where first-pass output risks looking generic / obviously AI-generated",
    "files": ["src/app/(marketing)/page.tsx", "src/components/Hero.tsx", "tailwind.config.ts"],
    "symbols": ["Hero", "designTokens", "ThemeProvider"],
    "tests": ["tests/visual/home.spec.ts"],
    "evidence_terms": ["reference screenshot", "spacing scale", "visual regression", "type hierarchy"],
    "failure_modes": [
        "Claiming a UI looks good without a reference or screenshot comparison.",
        "Shipping default framework styling and calling it a design.",
        "Adjusting color without checking contrast and token consistency.",
        "Treating a checklist as proof that the interface is distinctive.",
    ],
    "traps_short": ["looks clean", "usual checklist", "should be fine"],
    "category_prefix": "frontend-quality",
    "competencies": [
        {"id":"frontend-quality.reference-driven","label":"Source real references and compare against them before judging quality.","terms":["reference","screenshot","comparison"],"arch":["frontend-app"]},
        {"id":"frontend-quality.type-space-rhythm","label":"Check type hierarchy, spacing scale, and vertical rhythm.","terms":["type hierarchy","spacing scale","rhythm"],"arch":["frontend-app"]},
        {"id":"frontend-quality.color-contrast","label":"Verify palette, contrast, and token consistency.","terms":["contrast","palette","token"],"arch":["frontend-app"]},
        {"id":"frontend-quality.distinctiveness","label":"Detect and remove generic AI-default aesthetics.","terms":["generic","distinctive","default"],"arch":["frontend-app"]},
        {"id":"frontend-quality.visual-proof","label":"Tie the verdict to a screenshot or visual-regression surface.","terms":["visual regression","screenshot","before after"],"arch":["frontend-app"]},
    ],
    "failure_traps": [
        ("frontend-quality.pretty-claim-no-reference","Claims quality without a reference comparison."),
        ("frontend-quality.contrast-claim-no-check","Claims accessible color without a contrast check."),
    ],
},
"frontend-design": {
    "role": "frontend-design", "layer": "layer-4-specialists-and-standalones",
    "family": "frontend", "category": "frontend-product",
    "repo_profile": "component/page repo where the user asks to build UI and visual quality matters",
    "files": ["src/components/LoginForm.tsx", "src/app/dashboard/page.tsx", "src/styles/tokens.css"],
    "symbols": ["LoginForm", "DashboardLayout", "Button"],
    "tests": ["tests/components/LoginForm.spec.tsx"],
    "evidence_terms": ["component boundary", "responsive behavior", "accessibility state", "visual regression"],
    "failure_modes": [
        "Building UI without naming the component and route boundary first.",
        "Skipping loading, empty, and error states.",
        "Claiming responsive/accessible without a check.",
        "Producing generic AI aesthetics with no distinctive system.",
    ],
    "traps_short": ["looks fine", "usual checklist", "should render"],
    "competencies": [
        {"id":"frontend-product.route-component-boundary","label":"Map route, component, server/client, and data boundaries.","terms":["route","component","boundary"],"arch":["frontend-app"]},
        {"id":"frontend-product.state-error-loading","label":"Handle state, error, loading, and empty states.","terms":["state","error","loading"],"arch":["frontend-app"]},
        {"id":"frontend-product.visual-accessibility","label":"Check visual quality, accessibility, and responsive behavior.","terms":["visual","accessibility","responsive"],"arch":["frontend-app"]},
        {"id":"frontend-product.frontend-test-anchor","label":"Find component, smoke, or end-to-end test evidence.","terms":["component test","smoke","e2e"],"arch":["frontend-app"]},
        {"id":"frontend-product.distinctive-system","label":"Establish a distinctive, consistent design system, not defaults.","terms":["design system","distinctive","token"],"arch":["frontend-app"]},
    ],
    "failure_traps": [
        ("frontend-product.pretty-without-flow","Optimizes visual surface without proving the workflow works."),
        ("frontend-product.responsive-claim-without-check","Claims responsive/accessibility quality without evidence."),
    ],
},
"ui-styling": {
    "role": "ui-styling", "layer": "layer-4-specialists-and-standalones",
    "family": "frontend", "category": "frontend-styling",
    "repo_profile": "design-system / styling repo with tokens, themes, and reusable components",
    "files": ["src/styles/tokens.css", "tailwind.config.ts", "src/components/ui/Button.tsx"],
    "symbols": ["designTokens", "ThemeProvider", "Button"],
    "tests": ["tests/components/Button.spec.tsx"],
    "evidence_terms": ["design token", "theme", "responsive layout", "contrast ratio"],
    "failure_modes": [
        "Hardcoding values instead of using design tokens.",
        "Adding a component variant that breaks theme consistency.",
        "Claiming accessible components without contrast or focus checks.",
        "Duplicating styles instead of extending the system.",
    ],
    "traps_short": ["just add css", "usual checklist", "looks styled"],
    "competencies": [
        {"id":"frontend-styling.token-system","label":"Use and extend design tokens instead of hardcoded values.","terms":["design token","variable","scale"],"arch":["frontend-app"]},
        {"id":"frontend-styling.theming","label":"Keep light/dark and brand themes consistent.","terms":["theme","dark mode","brand"],"arch":["frontend-app"]},
        {"id":"frontend-styling.responsive-layout","label":"Build responsive layouts with predictable breakpoints.","terms":["responsive","breakpoint","layout"],"arch":["frontend-app"]},
        {"id":"frontend-styling.accessible-components","label":"Ensure focus, contrast, and target size on components.","terms":["contrast","focus","target size"],"arch":["frontend-app"]},
        {"id":"frontend-styling.style-reuse","label":"Extend the system rather than duplicating styles.","terms":["reuse","variant","composition"],"arch":["frontend-app"]},
    ],
    "failure_traps": [
        ("frontend-styling.hardcoded-values","Uses magic values instead of tokens."),
        ("frontend-styling.contrast-claim-no-check","Claims accessible styling without a contrast/focus check."),
    ],
},
}

# ---- 8 new skills: full SKILL.md + support files ----------------------------
NEW = {
"secure-code-review": {
    "description": "Use when application code needs a defensive security review before merge or release: injection, authn/authz, secrets handling, crypto misuse, SSRF, deserialization, and vulnerable dependencies.",
    "allowed_tools": ["Read","Grep","Glob","Bash"],
    "mission": "Turn security from implicit trust into an explicit, evidence-backed defensive review gate over real code paths, not a generic checklist.",
    "mandatory_scope": [
        "Identify the trust boundary: where untrusted input enters (HTTP params, headers, files, queues, env) and where it reaches a sink.",
        "Check injection sinks: SQL/NoSQL, OS command, template, LDAP, and path traversal — confirm parameterization or safe APIs.",
        "Check authn/authz: every state-changing route enforces identity and object-level authorization, not just authentication.",
        "Check secrets: no hardcoded keys/tokens, secrets sourced from env/vault, and no secret logged.",
        "Check crypto and randomness: no weak hashing for passwords, no ECB, no static IV, CSPRNG for tokens.",
        "Check dependencies: flag known-vulnerable versions and unpinned critical packages.",
    ],
    "evidence_contract": [
        "each finding names file:line, the tainted input, and the sink",
        "severity assigned (critical/high/medium/low) with exploitability rationale",
        "a concrete fix or safe-API replacement per finding",
        "pass or hold verdict tied to whether any critical/high finding is unresolved",
    ],
    "inputs": ["diff or changed files","authoritative artifact / PR","threat context if provided"],
    "outputs": ["security review findings appended to review notes or qa-report","pass or hold verdict with severities"],
    "rules": [
        "No pass verdict while any critical or high finding is unresolved.",
        "Trace input-to-sink; do not flag on keyword match alone.",
        "This is defensive review only — it hardens code, it does not build offensive tooling.",
        "Hand unresolved findings to fix-hub with explicit acceptance criteria.",
    ],
    "likely_next": ["fix-hub","review-hub","qa-governor","dependency-management"],
    "role": "security-reviewer", "layer": "layer-3-utility-providers",
    "family": "security-defense", "category": "appsec-review",
    "repo_profile": "web service repo with HTTP handlers, a database layer, auth middleware, and a dependency lockfile",
    "files": ["src/api/handlers.py","src/db/queries.py","src/auth/middleware.py","requirements.txt"],
    "symbols": ["build_query","require_auth","current_user"],
    "tests": ["tests/security/test_authz.py"],
    "evidence_terms": ["tainted input","injection sink","object-level authorization","severity"],
    "failure_modes": [
        "Flagging on keyword match without tracing input to a real sink.",
        "Passing a review while a critical injection or broken-authz path is open.",
        "Missing object-level authorization because authentication was present.",
        "Ignoring known-vulnerable dependency versions in the lockfile.",
    ],
    "traps_short": ["looks safe","usual checklist","probably fine"],
    "competencies": [
        {"id":"appsec-review.input-to-sink","label":"Trace untrusted input from source to dangerous sink.","terms":["tainted input","sink","trust boundary"],"arch":["web-service"]},
        {"id":"appsec-review.authz","label":"Verify authentication and object-level authorization on state-changing paths.","terms":["authorization","access control","identity"],"arch":["web-service"]},
        {"id":"appsec-review.secrets","label":"Detect hardcoded or logged secrets and unsafe secret handling.","terms":["secret","credential","token"],"arch":["web-service"]},
        {"id":"appsec-review.crypto","label":"Spot weak crypto, weak hashing, and predictable randomness.","terms":["hashing","encryption","randomness"],"arch":["web-service"]},
        {"id":"appsec-review.dependency-risk","label":"Flag known-vulnerable or unpinned dependencies.","terms":["dependency","CVE","lockfile"],"arch":["web-service"]},
    ],
    "failure_traps": [
        ("appsec-review.keyword-flag","Flags a line on a keyword without proving reachability."),
        ("appsec-review.authn-not-authz","Assumes authentication implies authorization."),
    ],
},
"observability-instrumentation": {
    "description": "Use when a service needs structured logging, metrics, distributed tracing, health checks, or SLO-backed alerting so failures are diagnosable in production.",
    "allowed_tools": ["Read","Write","Edit","Grep","Glob","Bash"],
    "mission": "Make a service diagnosable in production by instrumenting logs, metrics, traces, and alerts against explicit failure questions, not vanity dashboards.",
    "mandatory_scope": [
        "Name the top failure questions the instrumentation must answer (latency, error rate, saturation, a specific bug class).",
        "Structured logging: correlation/request id, level discipline, no secrets/PII in logs.",
        "Metrics: RED (rate, errors, duration) for request paths and USE for resources; name and label cardinality budget.",
        "Tracing: span boundaries at service and external-call edges, propagation of trace context.",
        "SLOs and alerts: define SLI, target, and alert that pages on symptom (burn rate) not on cause noise.",
    ],
    "evidence_contract": [
        "each signal maps to a named failure question it answers",
        "log/metric/trace field list with a no-PII confirmation",
        "at least one SLI + SLO + alert rule written",
        "cardinality budget stated for metric labels",
    ],
    "inputs": ["service code / handlers","existing logging or metrics setup","incident or failure context if present"],
    "outputs": [".relay-kit/references/observability.md","instrumentation code changes","SLO and alert definitions"],
    "rules": [
        "Instrument to answer a failure question, not to collect everything.",
        "Never log secrets or PII; redact at the boundary.",
        "Watch label cardinality — unbounded labels break the metrics backend.",
        "Alert on user-visible symptoms; keep cause-level signals for debugging.",
    ],
    "likely_next": ["release-readiness","incident-response","performance-optimization","runtime-doctor"],
    "role": "observability-specialist", "layer": "layer-4-specialists-and-standalones",
    "family": "reliability", "category": "observability",
    "repo_profile": "backend service repo with request handlers, a metrics client, and a logging config",
    "files": ["src/server/handlers.py","src/telemetry/metrics.py","config/logging.yaml"],
    "symbols": ["request_id","record_latency","trace_span"],
    "tests": ["tests/telemetry/test_metrics.py"],
    "evidence_terms": ["RED metrics","correlation id","SLO","burn rate"],
    "failure_modes": [
        "Adding dashboards that answer no concrete failure question.",
        "Logging secrets or PII into structured logs.",
        "Exploding metric cardinality with unbounded labels.",
        "Alerting on cause noise instead of user-visible symptoms.",
    ],
    "traps_short": ["add more logs","looks observable","dashboard exists"],
    "competencies": [
        {"id":"observability.failure-questions","label":"Anchor instrumentation to explicit failure questions.","terms":["failure question","diagnose","symptom"],"arch":["backend-service"]},
        {"id":"observability.structured-logging","label":"Emit correlated structured logs without secrets/PII.","terms":["correlation id","structured log","redaction"],"arch":["backend-service"]},
        {"id":"observability.metrics-red-use","label":"Define RED/USE metrics with a cardinality budget.","terms":["RED metrics","USE","cardinality"],"arch":["backend-service"]},
        {"id":"observability.tracing","label":"Set span boundaries and propagate trace context.","terms":["span","trace context","propagation"],"arch":["backend-service"]},
        {"id":"observability.slo-alerting","label":"Write SLIs, SLOs, and symptom-based burn-rate alerts.","terms":["SLI","SLO","burn rate"],"arch":["backend-service"]},
    ],
    "failure_traps": [
        ("observability.vanity-dashboard","Builds dashboards that answer no failure question."),
        ("observability.cardinality-blowup","Adds unbounded metric labels."),
    ],
},
"ci-cd-pipeline": {
    "description": "Use when designing or fixing build, test, and deploy automation: pipeline stages, caching, required gates, environment promotion, artifact versioning, and rollback triggers.",
    "allowed_tools": ["Read","Write","Edit","Grep","Glob","Bash"],
    "mission": "Design a deterministic, fail-closed delivery pipeline where every merge is gated by reproducible checks and every deploy has a defined rollback.",
    "mandatory_scope": [
        "Map stages: build, unit, integration, security scan, package, deploy — and which are blocking gates.",
        "Reproducibility: pinned toolchain, cached dependencies keyed by lockfile hash, deterministic build.",
        "Required gates: no merge to protected branch without passing gates and required reviews.",
        "Environment promotion: artifact built once, promoted across environments — never rebuilt per env.",
        "Rollback: a defined trigger, a tested rollback path, and a versioned previous artifact.",
    ],
    "evidence_contract": [
        "stage list with blocking vs non-blocking marked",
        "cache key and toolchain pin declared",
        "protected-branch gate rules stated",
        "rollback trigger and path written",
    ],
    "inputs": ["existing CI config","build and test commands","deploy target and environments"],
    "outputs": [".relay-kit/references/ci-cd.md","pipeline config changes","rollback runbook"],
    "rules": [
        "Fail closed — a missing or errored gate blocks, it does not warn-and-pass.",
        "Build the artifact once and promote it; do not rebuild per environment.",
        "Every deploy path must have a tested rollback.",
        "Pin the toolchain; floating versions break reproducibility.",
    ],
    "likely_next": ["release-readiness","dependency-management","secure-code-review","incident-response"],
    "role": "cicd-specialist", "layer": "layer-4-specialists-and-standalones",
    "family": "delivery", "category": "ci-cd",
    "repo_profile": "repo with a CI workflow file, a lockfile, and a deploy script targeting staging and prod",
    "files": [".github/workflows/ci.yml","scripts/deploy.sh","package-lock.json"],
    "symbols": ["build","deploy","cache-key"],
    "tests": ["tests/ci/test_pipeline.sh"],
    "evidence_terms": ["blocking gate","cache key","artifact promotion","rollback trigger"],
    "failure_modes": [
        "Letting a merge through when a required gate errored instead of blocking.",
        "Rebuilding the artifact separately for each environment.",
        "Shipping a deploy path with no rollback.",
        "Using floating toolchain versions that break reproducibility.",
    ],
    "traps_short": ["pipeline is green","should deploy fine","usual checklist"],
    "competencies": [
        {"id":"ci-cd.stage-gates","label":"Define blocking gates on protected branches.","terms":["blocking gate","required check","protected branch"],"arch":["delivery-pipeline"]},
        {"id":"ci-cd.reproducible-build","label":"Pin toolchain and cache by lockfile hash for reproducible builds.","terms":["toolchain pin","cache key","reproducible"],"arch":["delivery-pipeline"]},
        {"id":"ci-cd.artifact-promotion","label":"Build once and promote a versioned artifact across environments.","terms":["artifact","promotion","version"],"arch":["delivery-pipeline"]},
        {"id":"ci-cd.rollback","label":"Define a tested rollback trigger and path.","terms":["rollback","trigger","previous version"],"arch":["delivery-pipeline"]},
        {"id":"ci-cd.fail-closed","label":"Keep the pipeline fail-closed on missing or errored gates.","terms":["fail closed","block","gate error"],"arch":["delivery-pipeline"]},
    ],
    "failure_traps": [
        ("ci-cd.warn-and-pass","Treats a broken gate as a warning instead of a block."),
        ("ci-cd.rebuild-per-env","Rebuilds instead of promoting one artifact."),
    ],
},
"performance-optimization": {
    "description": "Use when latency, throughput, memory, or cost regresses and needs disciplined profiling: measure a baseline, find the real bottleneck, fix the hot path, and prove the gain.",
    "allowed_tools": ["Read","Write","Edit","Grep","Glob","Bash"],
    "mission": "Fix performance by measurement, not guesswork: establish a baseline, profile to the real bottleneck, change one thing, and prove the delta.",
    "mandatory_scope": [
        "Define the metric and workload: p50/p95/p99 latency, throughput, memory, or cost, under a stated load.",
        "Capture a baseline measurement before changing anything.",
        "Profile to locate the dominant cost (CPU, allocations, I/O, N+1 queries, lock contention) — do not assume.",
        "Change one variable, then re-measure against the same workload.",
        "Guard against regression: keep or add a benchmark so the gain does not silently erode.",
    ],
    "evidence_contract": [
        "baseline number with workload and environment stated",
        "profiler evidence identifying the bottleneck",
        "after number from the same workload, with the delta",
        "benchmark or check that locks in the improvement",
    ],
    "inputs": ["hot path or slow endpoint","profiling access or benchmark harness","target metric and budget"],
    "outputs": [".relay-kit/references/performance.md","optimized code","before/after benchmark evidence"],
    "rules": [
        "Never optimize without a baseline measurement.",
        "Profile before changing — intuition about hot paths is often wrong.",
        "Change one variable at a time so the delta is attributable.",
        "Prove the gain on the same workload; a faster microbenchmark is not a faster system.",
    ],
    "likely_next": ["observability-instrumentation","testing-patterns","review-hub","runtime-doctor"],
    "role": "performance-specialist", "layer": "layer-4-specialists-and-standalones",
    "family": "reliability", "category": "performance",
    "repo_profile": "service repo with a slow endpoint, a database layer, and a benchmark or load-test harness",
    "files": ["src/api/search.py","src/db/queries.py","bench/search_bench.py"],
    "symbols": ["search_handler","run_query","benchmark"],
    "tests": ["bench/search_bench.py"],
    "evidence_terms": ["baseline p95","profiler","hot path","delta"],
    "failure_modes": [
        "Optimizing without a baseline, so the gain cannot be proven.",
        "Guessing the bottleneck instead of profiling.",
        "Changing several things at once so the delta is unattributable.",
        "Reporting a microbenchmark win that does not move the real system.",
    ],
    "traps_short": ["feels faster","should be quicker","usual checklist"],
    "competencies": [
        {"id":"performance.metric-baseline","label":"Define the metric/workload and capture a baseline.","terms":["baseline","p95","workload"],"arch":["backend-service"]},
        {"id":"performance.profile-bottleneck","label":"Profile to the dominant cost before changing code.","terms":["profiler","bottleneck","hot path"],"arch":["backend-service"]},
        {"id":"performance.one-variable","label":"Change one variable and re-measure attributably.","terms":["one variable","re-measure","delta"],"arch":["backend-service"]},
        {"id":"performance.query-and-alloc","label":"Spot N+1 queries, excess allocations, and I/O waits.","terms":["n+1","allocation","io wait"],"arch":["backend-service"]},
        {"id":"performance.regression-guard","label":"Lock the gain with a benchmark or budget.","terms":["benchmark","regression","budget"],"arch":["backend-service"]},
    ],
    "failure_traps": [
        ("performance.no-baseline","Claims a speedup with no baseline."),
        ("performance.microbench-illusion","Reports a microbenchmark win that the system does not see."),
    ],
},
"technical-writing": {
    "description": "Use when authoring or revising technical documentation: READMEs, API references, runbooks, architecture docs, onboarding guides, or changelogs that must be accurate against the code.",
    "allowed_tools": ["Read","Write","Edit","Grep","Glob"],
    "mission": "Produce documentation that is accurate against the current code, scoped to a named audience and task, and verifiable — not aspirational prose.",
    "mandatory_scope": [
        "Name the audience and the single task the doc must enable (install, integrate, operate, decide).",
        "Verify every command, path, flag, and code sample against the actual repo before writing it.",
        "Structure for the task: quickstart first, reference second, rationale last.",
        "Mark unknowns explicitly rather than inventing behavior.",
        "State how the doc stays current (owner, source of truth, or generated section).",
    ],
    "evidence_contract": [
        "audience and enabled task named",
        "every command/path in the doc traced to a real file or verified run",
        "unknowns labeled, not fabricated",
        "staleness/ownership note included",
    ],
    "inputs": ["code or feature to document","existing docs if any","audience and purpose"],
    "outputs": ["the documentation artifact (README/runbook/API doc)","list of verified commands and paths"],
    "rules": [
        "Never document a command or flag you did not verify against the repo.",
        "Write for one audience and one task; split docs rather than blending them.",
        "Label unknowns; do not invent behavior to fill a gap.",
        "Prefer showing a verified example over describing behavior abstractly.",
    ],
    "likely_next": ["review-hub","doc-pointers","vietnamese-product-localization","release-readiness"],
    "role": "docs-author", "layer": "layer-4-specialists-and-standalones",
    "family": "docs", "category": "technical-writing",
    "repo_profile": "repo with a CLI or library, an outdated README, and example scripts",
    "files": ["README.md","src/cli.py","examples/quickstart.py"],
    "symbols": ["main","install","run"],
    "tests": ["examples/quickstart.py"],
    "evidence_terms": ["verified command","audience","quickstart","source of truth"],
    "failure_modes": [
        "Documenting a flag or command that does not exist in the code.",
        "Blending audiences so no reader finds their task.",
        "Inventing behavior to fill a gap instead of labeling the unknown.",
        "Leaving no note on how the doc stays current.",
    ],
    "traps_short": ["sounds complete","usual template","should be right"],
    "competencies": [
        {"id":"technical-writing.audience-task","label":"Scope the doc to one audience and one task.","terms":["audience","task","scope"],"arch":["docs-product"]},
        {"id":"technical-writing.verified-commands","label":"Verify every command, path, and flag against the repo.","terms":["verified command","path","flag"],"arch":["docs-product"]},
        {"id":"technical-writing.task-structure","label":"Order content quickstart-first, reference-second.","terms":["quickstart","reference","structure"],"arch":["docs-product"]},
        {"id":"technical-writing.label-unknowns","label":"Mark unknowns instead of fabricating behavior.","terms":["unknown","assumption","gap"],"arch":["docs-product"]},
        {"id":"technical-writing.staleness","label":"State ownership and source of truth for currency.","terms":["source of truth","owner","staleness"],"arch":["docs-product"]},
    ],
    "failure_traps": [
        ("technical-writing.fabricated-command","Documents a command that the code does not have."),
        ("technical-writing.audience-blend","Blends audiences so no task is served."),
    ],
},
"refactoring-discipline": {
    "description": "Use when restructuring code without changing behavior: extract, rename, split, or de-duplicate under a green test suite with small reversible steps and a characterization safety net.",
    "allowed_tools": ["Read","Write","Edit","Grep","Glob","Bash"],
    "mission": "Change structure while proving behavior is preserved: lean on a green test net, move in small reversible steps, and keep commits atomic.",
    "mandatory_scope": [
        "Confirm a passing test net covers the target; if coverage is thin, add characterization tests first.",
        "Separate refactor commits from behavior-change commits — never mix them.",
        "Move in small reversible steps; run tests after each step.",
        "Preserve the public contract (signatures, outputs, side effects) unless the task is explicitly to change it.",
        "State the risk if the safety net is incomplete, and what is unverified.",
    ],
    "evidence_contract": [
        "test net status before and after (green -> green)",
        "characterization tests added when coverage was thin",
        "refactor and behavior changes kept in separate commits",
        "public contract confirmed unchanged (or the change called out)",
    ],
    "inputs": ["target code / smell","existing test suite","behavior-preservation requirement"],
    "outputs": ["refactored code","added characterization tests if needed","commit plan separating refactor from behavior"],
    "rules": [
        "No refactor without a green test net — add characterization tests first if needed.",
        "Never mix a refactor with a behavior change in one commit.",
        "Run the suite after each small step, not only at the end.",
        "If behavior must change, that is not a refactor — route to the developer loop.",
    ],
    "likely_next": ["test-first-development","developer","review-hub","testing-patterns"],
    "role": "refactor-discipline", "layer": "layer-4-specialists-and-standalones",
    "family": "engineering", "category": "refactoring",
    "repo_profile": "repo with a tangled module, a passing unit suite, and duplicated logic across files",
    "files": ["src/orders/service.py","src/orders/legacy.py","tests/orders/test_service.py"],
    "symbols": ["OrderService","calculate_total","apply_discount"],
    "tests": ["tests/orders/test_service.py"],
    "evidence_terms": ["green test net","characterization test","behavior preserved","atomic commit"],
    "failure_modes": [
        "Refactoring against a red or absent test suite.",
        "Mixing a behavior change into a refactor commit.",
        "Running tests only at the end and losing the failing step.",
        "Silently altering the public contract.",
    ],
    "traps_short": ["just cleanup","should behave the same","usual checklist"],
    "competencies": [
        {"id":"refactoring.safety-net","label":"Require a green test net or add characterization tests first.","terms":["test net","characterization","coverage"],"arch":["engineering"]},
        {"id":"refactoring.small-steps","label":"Move in small reversible steps with tests each step.","terms":["small step","reversible","re-run"],"arch":["engineering"]},
        {"id":"refactoring.commit-separation","label":"Keep refactor and behavior changes in separate commits.","terms":["atomic commit","separate","behavior change"],"arch":["engineering"]},
        {"id":"refactoring.contract-preservation","label":"Preserve signatures, outputs, and side effects.","terms":["public contract","signature","side effect"],"arch":["engineering"]},
        {"id":"refactoring.risk-labeling","label":"State residual risk when the safety net is thin.","terms":["residual risk","unverified","thin coverage"],"arch":["engineering"]},
    ],
    "failure_traps": [
        ("refactoring.no-net","Restructures with no passing tests to prove behavior."),
        ("refactoring.mixed-commit","Hides a behavior change inside a refactor."),
    ],
},
"database-migration-safety": {
    "description": "Use when a schema or data migration touches a live database: expand/contract sequencing, backfills, index builds, lock analysis, and a tested rollback for zero-downtime changes.",
    "allowed_tools": ["Read","Write","Edit","Grep","Glob","Bash"],
    "mission": "Ship schema and data changes without downtime or data loss by sequencing expand-before-contract, analyzing locks, and proving a rollback.",
    "mandatory_scope": [
        "Classify the change: additive (safe), rewriting (locking), or destructive (irreversible) — and treat each accordingly.",
        "Sequence expand/contract: add new columns/tables and dual-write before removing old ones across separate deploys.",
        "Analyze locking: check whether the migration takes a blocking lock on a hot table and prefer concurrent/online paths.",
        "Backfill safely: batch large backfills, throttle, and make them resumable and idempotent.",
        "Provide a tested rollback or forward-fix, and confirm a backup/point-in-time exists before destructive steps.",
    ],
    "evidence_contract": [
        "change classified (additive/rewriting/destructive)",
        "expand-contract sequencing described across deploys",
        "lock impact on hot tables assessed",
        "rollback/forward-fix and backup confirmation stated",
    ],
    "inputs": ["migration script / schema diff","table size and traffic profile","deploy and rollback process"],
    "outputs": [".relay-kit/references/db-migration.md","sequenced migration plan","rollback and backfill runbook"],
    "rules": [
        "Never drop or rewrite before the new path is deployed and dual-writing.",
        "Avoid blocking locks on hot tables — use concurrent/online migration paths.",
        "Backfills must be batched, throttled, resumable, and idempotent.",
        "No destructive step without a confirmed backup and a rollback plan.",
    ],
    "likely_next": ["data-persistence","release-readiness","ci-cd-pipeline","incident-response"],
    "role": "db-migration-specialist", "layer": "layer-4-specialists-and-standalones",
    "family": "data", "category": "db-migration",
    "repo_profile": "app repo with an ORM, a migrations directory, and a large hot table in production",
    "files": ["migrations/0042_add_status.sql","src/db/models.py","src/db/backfill.py"],
    "symbols": ["add_column","backfill_status","create_index_concurrently"],
    "tests": ["tests/db/test_migration.py"],
    "evidence_terms": ["expand contract","blocking lock","backfill batch","rollback"],
    "failure_modes": [
        "Dropping or renaming a column before the new code path ships.",
        "Taking a blocking lock on a hot table during peak traffic.",
        "Running an unbatched backfill that saturates the database.",
        "Executing a destructive migration with no backup or rollback.",
    ],
    "traps_short": ["just run the migration","should be quick","usual checklist"],
    "competencies": [
        {"id":"db-migration.change-class","label":"Classify additive vs rewriting vs destructive changes.","terms":["additive","destructive","rewriting"],"arch":["data-store"]},
        {"id":"db-migration.expand-contract","label":"Sequence expand-contract with dual-write across deploys.","terms":["expand contract","dual write","sequence"],"arch":["data-store"]},
        {"id":"db-migration.lock-analysis","label":"Assess locking and prefer concurrent/online paths.","terms":["blocking lock","concurrent","online"],"arch":["data-store"]},
        {"id":"db-migration.safe-backfill","label":"Batch, throttle, and make backfills idempotent/resumable.","terms":["backfill batch","throttle","idempotent"],"arch":["data-store"]},
        {"id":"db-migration.rollback-backup","label":"Confirm rollback and backup before destructive steps.","terms":["rollback","backup","point in time"],"arch":["data-store"]},
    ],
    "failure_traps": [
        ("db-migration.contract-before-expand","Removes the old path before the new one is live."),
        ("db-migration.unbatched-backfill","Runs a backfill that saturates the database."),
    ],
},
"incident-response": {
    "description": "Use when a production incident is active or just resolved: triage severity, stabilize, communicate status, capture a timeline, and write a blameless postmortem with real action items.",
    "allowed_tools": ["Read","Grep","Glob","Bash"],
    "mission": "Drive a production incident from detection to a blameless postmortem: stabilize first, communicate clearly, and convert the timeline into durable fixes.",
    "mandatory_scope": [
        "Assign severity from user impact and scope, and name the incident commander role.",
        "Stabilize before diagnosing deeply: mitigate (roll back, feature-flag, scale) to stop the bleeding.",
        "Communicate: a status cadence with impact, current action, and next update time — no speculation as fact.",
        "Capture a timeline with timestamps: detection, actions, and their effect.",
        "Write a blameless postmortem: contributing factors, not blame, plus owned, dated action items.",
    ],
    "evidence_contract": [
        "severity assigned from stated user impact",
        "mitigation taken before deep diagnosis",
        "timeline with timestamps captured",
        "postmortem with blameless framing and owned action items",
    ],
    "inputs": ["alert / incident report","system state, logs, and metrics","recent changes and deploys"],
    "outputs": ["incident status updates","incident timeline",".relay-kit/references/postmortem-<id>.md"],
    "rules": [
        "Stabilize before rooting-cause; stop user impact first.",
        "Keep communication factual — label hypotheses as hypotheses.",
        "Blameless postmortems focus on systemic factors, never individuals.",
        "Every action item has an owner and a date, or it is not real.",
    ],
    "likely_next": ["root-cause-debugging","observability-instrumentation","fix-hub","ci-cd-pipeline"],
    "role": "incident-responder", "layer": "layer-4-specialists-and-standalones",
    "family": "reliability", "category": "incident-response",
    "repo_profile": "production service with alerting, deploy history, and dashboards during an active latency/error spike",
    "files": ["ops/runbooks/latency.md","src/server/handlers.py","deploy/history.log"],
    "symbols": ["rollback","feature_flag","health_check"],
    "tests": ["ops/runbooks/latency.md"],
    "evidence_terms": ["severity","mitigation","timeline","blameless postmortem"],
    "failure_modes": [
        "Debugging root cause while users are still impacted instead of mitigating first.",
        "Communicating hypotheses as confirmed fact.",
        "Writing a postmortem that assigns blame instead of finding systemic factors.",
        "Producing action items with no owner or date.",
    ],
    "traps_short": ["still investigating","probably the cause","usual checklist"],
    "competencies": [
        {"id":"incident-response.severity-triage","label":"Assign severity from user impact and scope.","terms":["severity","user impact","scope"],"arch":["reliability"]},
        {"id":"incident-response.stabilize-first","label":"Mitigate to stop impact before deep diagnosis.","terms":["mitigation","rollback","feature flag"],"arch":["reliability"]},
        {"id":"incident-response.communication","label":"Give a factual status cadence with next-update time.","terms":["status update","cadence","impact"],"arch":["reliability"]},
        {"id":"incident-response.timeline","label":"Capture a timestamped timeline of actions and effects.","terms":["timeline","timestamp","effect"],"arch":["reliability"]},
        {"id":"incident-response.blameless-postmortem","label":"Write a blameless postmortem with owned action items.","terms":["blameless","postmortem","action item"],"arch":["reliability"]},
    ],
    "failure_traps": [
        ("incident-response.debug-before-mitigate","Roots-cause while users are still down."),
        ("incident-response.blame-postmortem","Writes a postmortem that blames a person."),
    ],
},
}

MANIFEST_ADDS = {
    "  layer_3_utility_providers:": ["secure-code-review"],
    "  optional_discipline_overlays:": ["refactoring-discipline"],
    "  layer_4_specialists_and_standalones:": [
        "observability-instrumentation", "ci-cd-pipeline", "performance-optimization",
        "technical-writing", "database-migration-safety", "incident-response",
        "aesthetic", "frontend-design", "ui-styling",
    ],
}
def update_manifest():
    p = os.path.join(ROOT, "skills.manifest.yaml")
    if not os.path.exists(p):
        print("SKIP manifest (missing)"); return
    lines = open(p, encoding="utf-8").read().splitlines()
    present = set()
    for ln in lines:
        s = ln.strip()
        if s.startswith("- "):
            present.add(s[2:].strip())
    out = []
    for ln in lines:
        out.append(ln)
        key = ln.rstrip()
        if key in MANIFEST_ADDS:
            for item in MANIFEST_ADDS[key]:
                if item not in present:
                    out.append(f"    - {item}")
                    present.add(item)
                    print("manifest +", item, "->", key.strip())
    open(p, "w", encoding="utf-8").write("\n".join(out) + "\n")
    print("manifest updated")

def main():
    print("== BOM fix ==")
    fix_bom()
    print("== benign support files ==")
    for sk, spec in BENIGN.items():
        write_support(sk, spec)
    print("== new skills ==")
    for sk, spec in NEW.items():
        write_new_skill(sk, spec)
    print("== manifest ==")
    update_manifest()
    print("== done ==")

if __name__ == "__main__":
    main()

