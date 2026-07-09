# Relay-Kit v4 Architecture

## 1. Entry Points and Execution Flow
- **Canonical Entrypoint**: `relay_kit.py` - Core CLI responsible for taking flags (e.g. `--bundle`, `--ai`) and invoking the v3 bundle generators.
- **Public Facade**: `relay_kit_public_cli.py` - An advanced wrapper providing the friendlier user-facing command surface (`relay-kit doctor`, `relay-kit eval`, `relay-kit prompt enhance`, etc.) without rewriting the underlying generation flow.
- **Execution Flow**: 
  1. User calls `relay-kit` or `python relay_kit.py`
  2. Arguments are parsed, bundle configuration is loaded from `skills.manifest.yaml` and internal Python dictionaries (`BUNDLES`).
  3. The generator reads markdown templates from `templates/` and writes `.md` skill artifacts into `.agent/skills/`, `.claude/skills/`, or `.codex/skills/`.

## 2. Layer and Package Structure
- `relay_kit_v3/`: Core python package handling all heavy lifting.
  - `generator.py` (Bundle creation)
  - `evidence_ledger.py`, `pulse.py` (Logging and reporting)
  - `token_economy.py`, `context_index.py` (Context budget and indexing)
- `templates/`: Markdown templates for skills.
- `.relay-kit/`: Local runtime directory injected into user projects containing state, references, and contracts.

## 3. Module Responsibilities
- **Generation Layer**: Converts taxonomy rules into static markdown `.md` files that AI agents read.
- **Adapter Layer**: Isolates AI-specific output paths (`.claude`, `.codex`, `.agent`) while keeping content identical via `skills.manifest.yaml`.
- **Diagnostics Layer**: Python scripts (`doctor`, `gauntlet`, `readiness`) that verify if generated markdown skills are still intact and functioning correctly in the target project.

## 4. Ownership and Boundary Table
| Module / Path | Responsibility | Owner / Role |
|---|---|---|
| `relay_kit.py` | Command execution, bundle dispatch | Python CLI / Core |
| `skills.manifest.yaml` | Taxonomy, whitelist, adapter configuration | Architect |
| `templates/skills/` | Raw text components for agent prompts | PM / Designer |
| `.agent/skills/` | Emitted runtime skill artifacts for Antigravity | AI Orchestrator |

## 5. Dependency Direction and Boundaries
- `relay_kit_public_cli.py` -> `relay_kit.py` -> `relay_kit_v3` package.
- Generation code (`relay_kit_v3`) depends heavily on standard library (`json`, `pathlib`) and does not dynamically depend on AI APIs during generation (pure local execution).

## 6. Architecture Drift and Hotspots
- **Hotspot**: `skills.manifest.yaml` is a highly modified file. When adding new skills, both the YAML file and the `templates/` folder must be updated in sync.
- **Drift Risk**: Keeping `relay_kit_public_cli.py` commands in sync with `relay_kit_v3/` internals. If an internal module like `token_economy` changes its signature, the public CLI must be updated.

## 7. Files to Mirror When Adding New Work
When adding a new Skill:
1. Update `skills.manifest.yaml` to register the skill in a layer.
2. Create markdown definitions in `templates/skills/<skill-name>/SKILL.md`.
3. If adding a new CLI command, modify `relay_kit_public_cli.py` and implement the logic in `relay_kit_v3/`.
