# discipline-utilities-baseline-proposal

## Status

- Proposed
- Decision owner: `python-kit` architecture
- Current recommendation: keep `discipline-utilities` as an optional overlay bundle

## Decision to make

Should `discipline-utilities` stay as a long-lived optional bundle, or should some of its skills be folded into a future baseline after `round4`?

Current skills in scope:

- `root-cause-debugging`
- `test-first-development`
- `evidence-before-completion`

## Current architecture constraints

The current baseline already has a clear 4-layer model and strict bundle gating:

- runtime entrypoint: `C:\Users\b0ydeptrai\OneDrive\Documents\python-kit\python_kit.py`
- bundle registry: `C:\Users\b0ydeptrai\OneDrive\Documents\python-kit\ai_kit_v3\generator.py`
- bundle gating: `C:\Users\b0ydeptrai\OneDrive\Documents\python-kit\ai_kit_v3\registry\gating.py`
- skill registry: `C:\Users\b0ydeptrai\OneDrive\Documents\python-kit\ai_kit_v3\registry\skills.py`
- topology docs: `C:\Users\b0ydeptrai\OneDrive\Documents\python-kit\.ai-kit\docs\layer-model.md`

That means any future fold must preserve:

1. `round2`, `round3`, and `round4` compatibility
2. the 4-layer model
3. low baseline noise for normal projects
4. adapter parity across `.claude`, `.agent`, and `.codex`
5. clean separation between lane-owning skills and support utilities

## Strict fold criteria

A `discipline-utilities` skill may be folded into a future baseline only if all of the following are true.

### 1. Layer fit is still correct

The skill must remain a layer-3 utility provider.

It must not:

- become a lane owner
- require its own state file
- require its own contract
- behave like a second planner, router, or reviewer

### 2. Cross-cutting value is proven

The skill must be meaningfully useful across the baseline, not just for one narrow working style.

Minimum threshold:

- referenced by at least 2 hubs and 1 specialist or support skill
- or referenced by 3 independent baseline skills that span planning, execution, and verification

### 3. Baseline cost is low

The skill must not make the default baseline heavier than necessary.

Red flags:

- adds mandatory ceremony to simple tasks
- forces one engineering style on every repo
- expands `round4` without clear value for most projects

### 4. Adapter/runtime behavior is symmetric

The skill must behave the same when generated into:

- `C:\Users\b0ydeptrai\OneDrive\Documents\python-kit\.claude\skills\`
- `C:\Users\b0ydeptrai\OneDrive\Documents\python-kit\.agent\skills\`
- `C:\Users\b0ydeptrai\OneDrive\Documents\python-kit\.codex\skills\`

If one adapter needs special caveats, the skill should stay optional.

### 5. Gating remains clean

Folding the skill into a future baseline must not:

- leak into `round2`
- leak into `round3`
- create a second hidden baseline
- require extra docs/contracts/state that should have remained optional

### 6. The skill is stable, not experimental

The skill should survive at least one release cycle as an overlay without major rewrites to:

- its own body
- the hubs/specialists that reference it
- the docs that explain how to use it

## Current evidence

The current overlay is wired into the runtime as follows.

### `root-cause-debugging`

Evidence:

- runtime skill exists in:
  - `C:\Users\b0ydeptrai\OneDrive\Documents\python-kit\.claude\skills\root-cause-debugging\SKILL.md`
  - `C:\Users\b0ydeptrai\OneDrive\Documents\python-kit\.agent\skills\root-cause-debugging\SKILL.md`
  - `C:\Users\b0ydeptrai\OneDrive\Documents\python-kit\.codex\skills\root-cause-debugging\SKILL.md`
- referenced from:
  - `C:\Users\b0ydeptrai\OneDrive\Documents\python-kit\.claude\skills\debug-hub\SKILL.md`
  - `C:\Users\b0ydeptrai\OneDrive\Documents\python-kit\.claude\skills\agentic-loop\SKILL.md`

Assessment:

- Strong debugging discipline
- Good fit for layer 3
- Not yet proven as a baseline-wide requirement
- Currently strongest when work starts from failures, regressions, or unexplained behavior

Decision now:

- keep as optional overlay

Future fold eligibility:

- possible candidate later if it becomes directly referenced by additional core execution or review paths

### `test-first-development`

Evidence:

- runtime skill exists in:
  - `C:\Users\b0ydeptrai\OneDrive\Documents\python-kit\.claude\skills\test-first-development\SKILL.md`
  - `C:\Users\b0ydeptrai\OneDrive\Documents\python-kit\.agent\skills\test-first-development\SKILL.md`
  - `C:\Users\b0ydeptrai\OneDrive\Documents\python-kit\.codex\skills\test-first-development\SKILL.md`
- referenced from:
  - `C:\Users\b0ydeptrai\OneDrive\Documents\python-kit\.claude\skills\developer\SKILL.md`

Assessment:

- Useful discipline for engineering quality
- Too opinionated to become baseline-wide today
- Not every repo, feature, or migration path can realistically adopt test-first as the default
- Fails the low-noise requirement for a universal baseline

Decision now:

- keep as optional overlay

Future fold eligibility:

- do not fold unless the project explicitly raises the baseline philosophy to test-first by default

### `evidence-before-completion`

Evidence:

- runtime skill exists in:
  - `C:\Users\b0ydeptrai\OneDrive\Documents\python-kit\.claude\skills\evidence-before-completion\SKILL.md`
  - `C:\Users\b0ydeptrai\OneDrive\Documents\python-kit\.agent\skills\evidence-before-completion\SKILL.md`
  - `C:\Users\b0ydeptrai\OneDrive\Documents\python-kit\.codex\skills\evidence-before-completion\SKILL.md`
- referenced from:
  - `C:\Users\b0ydeptrai\OneDrive\Documents\python-kit\.claude\skills\test-hub\SKILL.md`
  - `C:\Users\b0ydeptrai\OneDrive\Documents\python-kit\.claude\skills\qa-governor\SKILL.md`
  - `C:\Users\b0ydeptrai\OneDrive\Documents\python-kit\.claude\skills\agentic-loop\SKILL.md`

Assessment:

- Strongest candidate for eventual baseline inclusion
- Fits verification and completion gates well
- Cross-cutting value is higher than the other two skills
- Still adds friction to quick-flow or low-risk tasks if made mandatory too early

Decision now:

- keep as optional overlay

Future fold eligibility:

- strongest future candidate if the project decides that completion claims must always be evidence-backed

## Candidate scoring

Scoring scale:

- `High`: likely candidate for future fold
- `Medium`: useful but should stay optional until more evidence exists
- `Low`: should remain overlay unless baseline philosophy changes

| Skill | Layer fit | Cross-cutting value | Baseline noise risk | Current fold readiness | Recommendation |
|---|---|---|---|---|---|
| `root-cause-debugging` | High | Medium | Low-Medium | Medium | Keep optional now, re-evaluate later |
| `test-first-development` | High | Low-Medium | High | Low | Keep optional long-term |
| `evidence-before-completion` | High | High | Medium | Medium-High | Best future fold candidate, but not yet |

## Decision

The safe decision today is:

1. keep `discipline-utilities` as an auxiliary bundle
2. do not fold any of the 3 skills into `round4`
3. treat `evidence-before-completion` as the first candidate for future baseline inclusion
4. treat `root-cause-debugging` as the second candidate
5. keep `test-first-development` as an overlay unless baseline philosophy changes

## What would justify a future fold

Only reconsider a fold if all of these remain true at the same time:

1. the overlay skills stay stable across one more release cycle
2. `round2`, `round3`, and `round4` gating remains clean in temp-output verification
3. the referenced hubs/specialists do not need further structural changes
4. the fold adds no new contracts or state files
5. the fold does not materially slow low-risk flows

## Recommended future path

### Near term

- keep `discipline-utilities` separate
- let the runtime and docs settle
- observe whether teams actually reach for the overlay or ignore it

### Medium term

If the architecture wants a stricter baseline later:

- consider folding `evidence-before-completion` into a future `round5-core`
- consider folding `root-cause-debugging` only if debugging discipline becomes mandatory in more than the current failure-oriented flows

### Do not do by default

- do not fold `test-first-development` into the baseline without an explicit policy decision
- do not create a second router, planner, or reviewer around these skills
- do not convert worktree/review lifecycle docs into routeable skills

## Final verdict

`discipline-utilities` should remain an optional overlay for now.

That is the strictest and safest choice because it preserves the current 4-layer architecture, keeps `round4` clean, and still gives advanced teams access to stronger execution discipline without forcing extra baseline complexity onto every project.
