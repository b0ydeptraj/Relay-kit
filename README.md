# Python Kit v3

`python-kit` now runs with a registry-driven v3 entrypoint while preserving the previous generator as `python_kit_legacy.py`.

## What Changed

- `python_kit.py` is now the v3 BMAD-lite entrypoint
- `python_kit_legacy.py` preserves the old monolithic generator and old kit inventory
- `ai_kit_v3/` contains the registry-driven round2 implementation
- v3 writes orchestration skills, contracts, workflow state, docs, and living reference templates
- legacy kits remain available through `--legacy-kit`

## Runtime Layout

After running v3 generation, the repo uses these runtime folders:

- `.claude/skills/` -> Claude runtime skills
- `.agent/skills/` -> Gemini/Antigravity runtime skills
- `.codex/skills/` -> Codex runtime skills
- `.ai-kit/contracts/` -> shared workflow contracts
- `.ai-kit/state/` -> workflow state and breadcrumbs
- `.ai-kit/references/` -> living support references
- `.ai-kit/docs/` -> migration/runtime helper docs

## Prerequisites

- Python 3.10+ (`python --version`)
- Git
- Optional CLIs if you still use legacy generation directly against tools:
  - Claude: `claude`
  - Gemini/Antigravity: `gemini`
  - Codex: `.codex/skills` support in Codex

## Quick Start

### v3 bundles

```bash
python python_kit.py --list-skills
python python_kit.py . --bundle round2 --ai claude --emit-contracts --emit-docs --emit-reference-templates
python python_kit.py . --bundle round2 --ai gemini --emit-contracts --emit-docs --emit-reference-templates
python python_kit.py . --bundle round2 --ai codex --emit-contracts --emit-docs --emit-reference-templates
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

## v3 Bundles

| Bundle | What it writes |
|--------|----------------|
| `bmad-core` | Core orchestration skills |
| `bmad-lite` | Core orchestration + cleaned `agentic-loop` |
| `cleanup` | Cleanup-only runtime skills |
| `legacy-native` | Native support skills (`project-architecture`, `dependency-management`, `api-integration`, `data-persistence`, `testing-patterns`) |
| `round2` | Core + cleanup + native support skills |

Use `--emit-contracts`, `--emit-docs`, and `--emit-reference-templates` to materialize `.ai-kit/` outputs alongside skill generation.

## Legacy Kits

The old kits are still listed and runnable through `--legacy-kit`:

- `python`
- `flutter`
- `antigravity`
- `claudekit`
- `ui-ux`
- `full`

Use `python python_kit.py --list-skills` to see both v3 bundles and legacy kits together.

## AI Adapters

| `--ai` | Output folder | Notes |
|--------|---------------|-------|
| `claude` | `.claude/skills/` | Claude runtime |
| `gemini` | `.agent/skills/` | Gemini/Antigravity runtime |
| `codex` | `.codex/skills/` | Codex runtime |
| `all` | `.claude/skills/` + `.agent/skills/` | `all` does not include Codex |
| `generic` | `.python-kit-prompts/` | Prompt output only |

## Migration Notes

- v2-style `--kit` is no longer the primary interface for the repo entrypoint.
- Use `--bundle` for v3 generation.
- Use `--legacy-kit` when you need the old generator behavior.
- `python_kit_legacy.py` is preserved and should not be edited in place during v3 migration.
- `agentic-loop` runtime output is now generated from the cleaned round2 registry template rather than the old leaked authoring prompt.

## Example Outputs From `round2`

Running:

```bash
python python_kit.py . --bundle round2 --ai claude --emit-contracts --emit-docs --emit-reference-templates
```

creates outputs like:

- `.claude/skills/workflow-router/SKILL.md`
- `.claude/skills/architect/SKILL.md`
- `.claude/skills/project-architecture/SKILL.md`
- `.ai-kit/contracts/PRD.md`
- `.ai-kit/contracts/architecture.md`
- `.ai-kit/contracts/qa-report.md`
- `.ai-kit/state/workflow-state.md`
- `.ai-kit/references/project-architecture.md`
- `.ai-kit/references/api-integration.md`
- `.ai-kit/references/data-persistence.md`
- `.ai-kit/references/testing-patterns.md`

## Publish To GitHub

Commit only the intended round2 scope when the repo already has unrelated local changes:

```bash
git add README.md python_kit.py python_kit_legacy.py ai_kit_v3 .ai-kit .claude/skills .agent/skills .codex/skills
git commit -m "feat: merge BMAD-lite round2 upgrade pack"
git push origin main
```

## Credits

- [claudekit-skills](https://github.com/anthropics/claudekit-skills)
- [antigravity-kit](https://github.com/vudovn/antigravity-kit)
- [ui-ux-pro-max-skill](https://ui-ux-pro-max-skill.nextlevelbuilder.io/)
