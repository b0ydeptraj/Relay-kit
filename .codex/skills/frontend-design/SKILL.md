---
name: frontend-design
description: "Use when a frontend surface must be IMPLEMENTED in code (component, page, or app). Writes/edits source files, wires state, and captures rendered evidence. Does not review screenshots as its primary verdict — hand finished output to `aesthetic` for that."
allowed-tools: ["Read", "Write", "Edit", "Grep", "Glob", "Bash"]
---

# Mission
IMPLEMENT a frontend surface — write and edit the source files, run it, capture evidence. Stop before deciding whether the result is visually good; that verdict belongs to `aesthetic`.

## Scope boundary (do not violate)
- IN scope: route/component/page scaffolding, state wiring, repo-native styling, responsive breakpoints, loading/empty/error/mobile states, dev-server verification.
- OUT of scope: visual quality verdict ("this is AI-generated looking", "feels bland"), screenshot critique, taste calls → `aesthetic`.
- OUT of scope: component-system/token design decisions → `ui-styling`. Architecture of a Next.js product → `next-product-frontend`. Final accessibility gate → `accessibility-review`.

## Pre-flight checklist (block the edit if any is missing)
1. Target file paths named.
2. Repo-native component library + token source identified (grep for `button`, `card`, `theme`, `tailwind.config`, `styled` etc.).
3. At least one reference anchor (URL, screenshot, or an existing in-repo screen the new work extends).
4. Primary task of the surface stated in one sentence.
5. Required states enumerated (default + any of loading/empty/error/mobile that apply).

## Build loop
1. Reuse hunt: for each piece of UI, find an existing component in the repo; only create new if none fits.
2. Implement in small vertical slices (one state at a time).
3. After each slice, run the dev server / Storybook / test harness and capture evidence.
4. Record exact files changed with `file_path:line` citations.
5. When done, hand off to `aesthetic` with the rendered evidence attached — do not self-approve.

## Evidence contract
- diff or new files with precise paths
- rendered screenshots for every claimed state
- list of states NOT covered with reason
- note explicit handoff: `aesthetic` for visual verdict, `accessibility-review` before merge
- if you had to invent a new component, state why reuse was impossible

## Failure modes to self-check
- You wrote "looks great" / "distinctive" / "production-grade" without a screenshot ⇒ delete the claim, let `aesthetic` judge.
- You added a new Button/Card/Modal when the repo already has one ⇒ revert, use the existing one.
- You skipped loading/empty/error states on a surface that fetches data ⇒ not done.

## Role
- frontend-design

## Layer
- layer-4-specialists-and-standalones

## Inputs
- concrete build request with target surface (component, page, or app)
- existing design system, tokens, or component library in the repo
- at least one real reference (screenshot, URL, or named product pattern)

## Outputs
- edited/new source files at the stated paths
- rendered-state evidence (dev-server screenshot, Storybook capture, or test output)
- list of states covered (default / loading / empty / error / focus / disabled / mobile)
- explicit handoff note to `aesthetic` when visual verdict is still pending

## Reference skills and rules
- This skill WRITES code. Before any edit, confirm repo-native component library, token source, and routing/state conventions — do not introduce a parallel stack.
- Every claim 'UI looks good' must come from `aesthetic`, not from this skill. This skill ships the artifact; `aesthetic` judges it.
- Reuse before invent: search for an existing component matching the need before creating a new one.
- Do not ship card-grid filler, oversized safe heroes, default icons, or gradient padding unless they serve a named hierarchy decision.
- Open `references/frontend-design-operator-contract.md` when scope, evidence, or operator safety is unclear.
- Use `examples/frontend-design-good-output.md` and `examples/frontend-design-bad-output.md` to calibrate output quality.
- Use `evals/frontend-design-cases.json` as the minimum scenario set for behavior regression checks.
- Use `competencies/frontend-design-competencies.json` to check covered competencies, failure traps, and unknown-domain policy.

## Likely next step
- aesthetic
- ui-styling
- accessibility-review
- test-hub
- review-hub
