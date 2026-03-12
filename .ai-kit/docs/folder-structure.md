# folder-structure

Recommended runtime layout:

- `.ai-kit/contracts/` -> stable artifact contracts shared across roles
- `.ai-kit/state/` -> workflow-state and other runtime breadcrumbs
- `.ai-kit/references/` -> living support references for architecture, APIs, persistence, testing, and dependency policy
- `.claude/skills/`, `.agent/skills/`, `.codex/skills/` -> adapter-specific skill folders
- `python_kit_legacy.py` -> renamed old generator, still used for legacy analysis/template kits
- `python_kit.py` -> new v3 entrypoint that adds orchestration, routing, and contracts
