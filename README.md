# Python Kit v3.1

`python-kit` now runs with a registry-driven v3 entrypoint while preserving the previous generator as `python_kit_legacy.py`.

## What changed in round 3

- keeps the round 2 BMAD-lite base in place
- adds a **4-layer topology** closer to the hub-and-spoke model:
  - layer 1 orchestrators: `workflow-router`, `bootstrap`, `team`, `cook`
  - layer 2 workflow hubs: `brainstorm-hub`, `scout-hub`, `plan-hub`, `debug-hub`, `fix-hub`, `test-hub`, `review-hub`
  - layer 3 utility providers: existing stateless utilities from your legacy kits remain external support capabilities
  - layer 4 specialists and standalones: `analyst`, `pm`, `architect`, `scrum-master`, `developer`, `qa-governor`, `agentic-loop`, and native support skills
- upgrades workflow state so orchestrator, hub, lane, and specialist are all visible
- adds `team-board.md` for multi-lane coordination and `investigation-notes.md` for debug-first work
- preserves legacy kits through `python_kit_legacy.py`

## Runtime layout

After running v3 generation, the repo uses these runtime folders:

- `.claude/skills/` -> Claude runtime skills
- `.agent/skills/` -> Gemini/Antigravity runtime skills
- `.codex/skills/` -> Codex runtime skills
- `.ai-kit/contracts/` -> shared workflow contracts
- `.ai-kit/state/` -> workflow state and multi-lane coordination state
- `.ai-kit/references/` -> living support references
- `.ai-kit/docs/` -> topology, migration, and runtime helper docs

## Quick start

### list bundles and kits

```bash
python python_kit.py --list-skills
```

### generate the full round 3 layer set

```bash
python python_kit.py . --bundle round3 --ai claude --emit-contracts --emit-docs --emit-reference-templates
python python_kit.py . --bundle round3 --ai gemini --emit-contracts --emit-docs --emit-reference-templates
python python_kit.py . --bundle round3 --ai codex --emit-contracts --emit-docs --emit-reference-templates
```

### generate only orchestrators or hubs

```bash
python python_kit.py . --bundle orchestrators --ai claude --emit-contracts --emit-docs
python python_kit.py . --bundle workflow-hubs --ai claude --emit-contracts --emit-docs
python python_kit.py . --bundle round3-core --ai claude --emit-contracts --emit-docs
```

### legacy kits

```bash
python python_kit.py . --legacy-kit python --ai claude
python python_kit.py . --legacy-kit flutter --ai claude
python python_kit.py . --legacy-kit antigravity --ai gemini
python python_kit.py . --legacy-kit claudekit --ai claude
python python_kit.py . --legacy-kit ui-ux --ai codex
python python_kit.py . --legacy-kit full --ai all
```

## v3 bundles

| Bundle | What it writes |
|---|---|
| `bmad-core` | round 2 compatibility core skills |
| `bmad-lite` | round 2 core + cleaned `agentic-loop` |
| `cleanup` | cleanup-only runtime skills |
| `legacy-native` | native support skills (`project-architecture`, `dependency-management`, `api-integration`, `data-persistence`, `testing-patterns`) |
| `round2` | round 2 compatibility bundle |
| `orchestrators` | layer 1 orchestration skills |
| `workflow-hubs` | layer 2 workflow hubs |
| `role-core` | layer 4 role specialists including `developer` |
| `round3-core` | orchestrators + hubs + role specialists |
| `round3` | full round 3 set: orchestrators + hubs + roles + cleanup + native support |

Use `--emit-contracts`, `--emit-docs`, and `--emit-reference-templates` to materialize `.ai-kit/` outputs alongside skill generation.

## AI adapters

| `--ai` | Output folder | Notes |
|---|---|---|
| `claude` | `.claude/skills/` | Claude runtime |
| `gemini` | `.agent/skills/` | Gemini/Antigravity runtime |
| `codex` | `.codex/skills/` | Codex runtime |
| `all` | `.claude/skills/` + `.agent/skills/` | `all` does not include Codex |
| `generic` | `.python-kit-prompts/` | prompt output only |

## 4-layer usage model

1. `workflow-router` chooses track and entrypoint.
2. `bootstrap`, `cook`, or `team` own orchestration.
3. one workflow hub runs the current playbook (`plan-hub`, `debug-hub`, `test-hub`, etc.).
4. specialists and support skills produce or refresh the real artifacts.

This keeps orchestration separate from execution, while still using BMAD-style context handoff through shared artifacts.

## Migration notes

- `python_kit.py` remains the active v3 entrypoint.
- `python_kit_legacy.py` remains the preserved old generator.
- `round2` behavior stays available.
- `round3` adds the 4-layer topology on top of the round 2 base instead of replacing it.
- `agentic-loop` remains the execution engine, but now sits behind a first-class `developer` specialist and the new hubs.
