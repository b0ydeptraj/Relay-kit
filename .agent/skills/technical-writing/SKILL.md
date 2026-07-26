---
name: technical-writing
description: "Use when authoring or revising technical documentation: READMEs, API references, runbooks, architecture docs, onboarding guides, or changelogs that must be accurate against the code."
allowed-tools: ["Read", "Write", "Edit", "Grep", "Glob"]
---

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

## Role
- docs-author

## Layer
- layer-4-specialists-and-standalones

## Inputs
- code or feature to document
- existing docs if any
- audience and purpose

## Outputs
- the documentation artifact (README/runbook/API doc)
- list of verified commands and paths

## Reference skills and rules
- Never document a command or flag you did not verify against the repo.
- Write for one audience and one task; split docs rather than blending them.
- Label unknowns; do not invent behavior to fill a gap.
- Prefer showing a verified example over describing behavior abstractly.
- Open `references/technical-writing-operator-contract.md` when scope, evidence, or operator safety is unclear.
- Use `examples/technical-writing-good-output.md` and `examples/technical-writing-bad-output.md` to calibrate output quality.
- Use `evals/technical-writing-cases.json` as the minimum scenario set for behavior regression checks.
- Use `competencies/technical-writing-competencies.json` to check covered competencies, failure traps, and unknown-domain policy.

## Likely next step
- review-hub
- doc-pointers
- vietnamese-product-localization
- release-readiness
