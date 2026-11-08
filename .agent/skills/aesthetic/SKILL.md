---
name: aesthetic
description: "Use when a frontend surface is ALREADY RENDERED (screenshot, dev-server, Storybook) and needs a visual-quality verdict + concrete revision direction. Read-only: never edits source. Inputs REQUIRE an actual image or URL — if none exists, send the lane to `frontend-design` first."
allowed-tools: ["Read", "Grep", "Glob", "Bash"]
---

# Mission
Judge a rendered UI with a verdict and a ranked revision list. Read-only. Structural issues come before polish.

## Scope boundary (do not violate)
- IN scope: reading screenshots/URLs, naming visible problems, ranking fixes, giving one structural revision + a short polish list, writing the handoff.
- OUT of scope: editing source files (even "one small CSS tweak") → hand to `frontend-design` or `ui-styling`.
- OUT of scope: building something new because the current screen looks bad — critique what exists; the build skill owns the next version.
- OUT of scope: accessibility verdict → `accessibility-review`. Pure image-OCR / multimodal reading → `multimodal-evidence`.

## Pre-flight (refuse the review if any missing)
1. A real rendered artifact (path to PNG, URL, Storybook link). **No screenshot → no verdict.**
2. A reference anchor (not "what looks good in general" — a specific comparator).
3. A one-sentence statement of the surface's primary task.

## Critique order (do them in this order; do not shuffle)
1. **Focal point** — can you name it in <2s? Is the proof close to the main claim?
2. **Hierarchy & density** — are weights/sizes/spacings telling the right story, or is everything the same weight?
3. **Generic-AI smell** — equal-weight card grid, oversized safe hero, default icon set, decorative gradient filler, every corner the same radius, chart that uses default library colors. Flag each with the exact region.
4. **State coverage** — does the surface handle loading / empty / error / mobile? If data-backed and it doesn't, demand it.
5. **Polish** — color, radius, motion, type details. Only after 1-4 pass.

## Verdict format
```
VERDICT: ship | revise-once | rebuild-structure
STRUCTURAL ISSUE (max 1): <one sentence, with region>
POLISH LIST (ranked): <3-5 items, each with a region>
NOT COVERED: <states the surface fails to show>
HANDOFF: <frontend-design | ui-styling | accessibility-review> — <exact next action>
```

## Failure modes to self-check
- You gave a verdict without citing a visible region ⇒ invalid, revise.
- You listed 10 polish items but no structural issue ⇒ you did not critique in the right order.
- You started editing a file ⇒ wrong skill, revert and hand off.
- You accepted "ship" on a data-backed surface with no empty/error state ⇒ invalid.

## Role
- aesthetic-review

## Layer
- layer-4-specialists-and-standalones

## Inputs
- rendered artifact (screenshot path, dev-server URL, or Storybook link) — mandatory
- at least one reference anchor (benchmark URL, named product pattern, or in-repo screen)
- product tone / target user constraints

## Outputs
- verdict: ship / revise-once / rebuild-structure
- ranked revision list (structure first, polish last) with exact UI regions cited
- generic-AI-smell flags with evidence coordinates (which card, which hero, which gradient)
- handoff note naming which build skill applies the fix

## Reference skills and rules
- This skill DOES NOT WRITE CODE. If a revision is accepted, hand off to `frontend-design` / `ui-styling` — do not edit files here.
- Every verdict must cite a visible region of the rendered artifact; taste without a coordinate is rejected.
- Structure (hierarchy, density, focal point, proof-near-claim) is critiqued BEFORE color/radius/motion polish.
- If no rendered artifact exists, stop and route to `frontend-design` — never judge from code alone.
- Open `references/aesthetic-operator-contract.md` when scope, evidence, or operator safety is unclear.
- Use `examples/aesthetic-good-output.md` and `examples/aesthetic-bad-output.md` to calibrate output quality.
- Use `evals/aesthetic-cases.json` as the minimum scenario set for behavior regression checks.
- Use `competencies/aesthetic-competencies.json` to check covered competencies, failure traps, and unknown-domain policy.

## Likely next step
- frontend-design
- ui-styling
- multimodal-evidence
- accessibility-review
- review-hub
