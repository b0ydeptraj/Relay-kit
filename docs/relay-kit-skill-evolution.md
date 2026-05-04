# relay-kit-skill-evolution

This note records the first Relay-kit-owned adoption slice from the local Claude Code reports export.
For the full Relay-kit-specific 12-report translation matrix, see `docs/relay-kit-claude-12-adoption-matrix.md`.

Source used:

- `01_Report_Lessons_Learned...md`: practical lessons on memory, context budget, parallel agents, worktree isolation, permission modes, and skill metadata.
- `09_Report_Skills_Plugin_System_Claude_Code.md`: skill frontmatter, conditional activation, forked context, allowed tools, dynamic discovery, and hot reload.
- `12_Report_Permission_System_Claude_Code.md`: deny-by-default permission flow, permission modes, rule matching, dangerous rule stripping, and shell-prefix risk.

The implementation intentionally does not copy external skill names or prompts. The adopted runtime surface is the Relay-kit skill `skill-evolution`.

## Adopted Patterns

| Pattern | Why it matters | Relay-kit adoption |
|---|---|---|
| Trigger metadata is the first activation gate | A skill should load because its description is precise, not because the body is long. | `skill-evolution` description names create, upgrade, review, prune, `SKILL.md`, frontmatter, allowed tools, handoff, and scenario fixtures. |
| Path-scoped activation | File-type or folder-specific skills should stay out of the active surface until relevant files are touched. | `skill-evolution` emits `paths: ["**/SKILL.md", "relay_kit_v3/registry/skills.py", "docs/relay-kit-skill-*.md"]`. |
| Forked context for skill review | Skill audits and report-heavy work should not pollute the main implementation lane. | `skill-evolution` emits `context: fork` and instructs return through `skill-gauntlet`, `workflow-router`, or `review-hub`. |
| Explicit tool profile | Any skill that can touch files, run shell, or inspect many paths needs a visible permission stance. | `skill-evolution` emits `allowed-tools: ["Read", "Write", "Edit", "Grep", "Glob", "Bash"]` and requires high-risk skills to name their allowed-tool stance. |
| Scenario proof before behavior claims | Skill changes are routing changes and should be regression-tested. | Tests now assert skill-upgrade prompts route to `skill-evolution`; generated adapter copies are checked by `skill_gauntlet`. |
| External inspiration, local ownership | External systems can inspire patterns, but Relay-kit needs stable names and contracts. | The skill explicitly forbids copying external names and requires add/update/merge/prune classification for every skill delta. |

## New Runtime Contract

Use `skill-evolution` when changing:

- generated `SKILL.md` files
- `relay_kit_v3/registry/skills.py`
- skill routing fixtures
- skill docs under `docs/relay-kit-skill-*.md`

Required output:

- classify each skill delta as add, update, merge, prune, or leave unchanged
- audit trigger text, frontmatter, allowed-tool stance, inputs, outputs, and likely next-step ownership
- add or update scenario proof when trigger behavior changes

## What Was Not Adopted Yet

- Full dynamic skill discovery or file watcher behavior inside Relay-kit. Current adapters may honor `paths` metadata, but Relay-kit does not run a resident watcher.
- Inline shell execution from skill markdown. Relay-kit keeps shell execution behind normal agent/tool permission flows and policy guard checks.
- Claude-specific permission modes as Relay-kit runtime modes. Relay-kit keeps deterministic `policy_guard` and enterprise doctor gates instead.

## Evidence

- `tests/test_enterprise_bundle.py::test_skill_evolution_frontmatter_uses_claude_activation_patterns`
- `tests/test_skill_gauntlet_semantic.py::test_semantic_skill_gauntlet_routes_skill_upgrade_to_skill_evolution`
- `scripts/validate_runtime.py` discipline-utilities parity includes `skill-evolution`

## Permission/Profile Audit Slice

The second adoption slice turns the `skill-evolution` rule for high-risk skills into a semantic gauntlet check.

What changed:

- high-risk skills must declare `allowed-tools` frontmatter in generated adapter copies
- registry specs must carry the same tool profile used by generated `SKILL.md`
- `skill_gauntlet --semantic --strict` fails when a high-risk skill is missing a tool profile, has malformed tool names, or drifts from registry metadata

Initial high-risk profile set:

- edit/test profile: `developer`, `execution-loop`, `test-first-development`, `skill-evolution`
- read/analyze gate profile: `accessibility-review`, `release-readiness`, `skill-gauntlet`, `runtime-doctor`, `migration-guard`, `policy-guard`, `root-cause-debugging`

This is not OS-level sandboxing. It is a machine-checked skill contract that prevents permission stance from silently disappearing during registry or generated-skill changes.

## Risk-Sensitive Profile Expansion Slice

The third adoption slice extends machine-checked tool profiles beyond the initial implementation and gate skills.

New profiled skills:

- edit/test profile: `api-integration`, `data-persistence`, `dependency-management`, `media-tooling`
- read/analyze profile: `browser-inspector`, `multimodal-evidence`

Why these are included:

- API, data, and dependency support skills often touch production-facing code, configuration, secrets, migrations, or lockfiles.
- Media tooling can write transformed evidence or asset files and needs an explicit edit/test stance.
- Browser and multimodal evidence utilities should stay analysis-scoped unless the owning hub routes to an implementation skill.

`skill_gauntlet --semantic --strict` now treats these as profiled risk-sensitive skills and fails if registry metadata, generated frontmatter, or adapter surfaces drift.
