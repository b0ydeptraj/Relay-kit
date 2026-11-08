# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project discipline (AGENTS.md is binding)

`AGENTS.md` enforces four tiers at "KỊCH MAXIMUM" severity. Follow them:
- **Zero-fluff**: no filler phrases, no restating the prompt, no reprinting whole files for small edits. ≤2 sentences of explanation for one-line fixes.
- **Evidence-first**: every claim about code needs a real `file:line` citation (verify with tools before asserting). Mark unverified guesses `[GIẢ THUYẾT - CHƯA KIỂM CHỨNG]`.
- **Subtraction-first**: prove you can't reuse/delete existing code before adding a class, helper, wrapper, or abstraction. No `[YAP]`/`[FLUFF]` comments.
- **No completion claim without proof**: never say "done/works/optimized" without passing build/test output, a screenshot (UI), or a clean run log.

## What this is

A Python package (`relay-kit`, v4.0.0) that **generates coding-agent runtime skills** from one central registry into adapter surfaces: `.claude/skills/`, `.codex/skills/`, `.agent/skills/`. It is a skill/workflow generator, not an application runtime itself. `requires-python = ">=3.10`; the only hard dep is `pyyaml`.

## Commands

```bash
python -m pytest                      # full suite (testpaths=tests, timeout 600s/test)
python -m pytest tests/test_readiness_check.py            # one file
python -m pytest tests/test_readiness_check.py::test_name  # one test
python -m pytest -k readiness         # by keyword
```

```bash
python scripts/validate_runtime.py    # REQUIRED validation before submitting (see CONTRIBUTING.md)
python relay_kit.py --list-skills     # list active runtime bundles
python scripts/migration_guard.py . --strict   # run when naming/path cutover tokens could drift
python scripts/naming_guard.py        # naming-token guard
```

```bash
# Generation (canonical entrypoint). --ai picks the adapter surface; --bundle picks the skill set.
python relay_kit.py . --bundle runtime --ai all --emit-contracts --emit-docs --emit-reference-templates
python relay_kit.py . --bundle core --ai claude --emit-docs
```

```bash
# Public CLI wrapper (thin layer over relay_kit.py + the cli engine)
python relay_kit_public_cli.py doctor .
python relay_kit_public_cli.py readiness check . --profile enterprise --json
```

`relay_kit_public_cli.py --all` maps to `relay_kit.py --ai all`. Tests legitimately shell out to the full gate pipeline and can take ~4 minutes (hence the 600s per-test timeout in `pyproject.toml`).

## Architecture

**Single source of truth → generator → adapter surfaces.** The flow is registry-driven; do not hand-edit generated `.claude/skills` etc. as the primary change — edit the registry.

1. **Registry** (`relay_kit_v3/registry/`): skills are `SkillSpec` dataclasses (`relay_kit_v3/registry/skills.py:8`). Companion modules: `artifacts.py`, `workflows.py`, `topology.py`, `gating.py`, `support_refs.py`, `extension_pack_skills.py`. Skills are grouped into named collections (`CORE_SKILLS`, `ORCHESTRATOR_SKILLS`, `WORKFLOW_HUB_SKILLS`, `ROLE_SKILLS`, `UTILITY_PROVIDER_SKILLS`, `OFFENSIVE_TOOL_PACK_SKILLS`, etc.) imported by the generator.

2. **Bundles** (`relay_kit_v3/generator.py:64`, `BUNDLES`): named unions of those collections — `core`, `orchestration`, `runtime`, `baseline`, `enterprise` (default, = everything). `--bundle` selects one. Retired bundle names are remapped in `relay_kit.py:22` (`RETIRED_BUNDLE_HINTS`).

3. **Generator** (`relay_kit_v3/generator.py`): `create_runtime_bundle(...)` renders skills, agent profiles (`agent_profiles.py`), slash commands (`command_registry.py`), `.relay-kit/` artifacts/contracts/docs, and public-entrypoint facades for each requested adapter via `adapters.py` (`targets_for`).

4. **Adapters** (`relay_kit_v3/adapters.py`): map one skill source to `.claude`/`.codex`/`.agent`/`.relay-kit-prompts`. "Adapter parity" (same behavior across surfaces) is a hard invariant — see `test_runtime_skill_command_portability.py`, `test_adapter_diagnostics.py`.

5. **CLI engine** (`relay_kit_v3/cli/`): schema-driven dispatch. `engine.py` reads `command_schema.yaml` and builds argparse from it; each subcommand is a module in `relay_kit_v3/cli/` (e.g. `doctor.py`, `readiness.py`, `context.py`, `eval.py`). Add a command by editing the schema + a handler module, not by scattering argparse.

6. **Entrypoints**: `relay_kit.py` is canonical (generation + SRS policy + locale). `relay_kit_public_cli.py` is the friendly wrapper (doctor/readiness/release/publish/context/eval/etc.). `relay_kit_compat.py` holds canonical constants (`CANONICAL_ARTIFACT_ROOT`, `CANONICAL_ENTRYPOINT`).

**Runtime state artifacts** live under `.relay-kit/` (`state/workflow-state.md`, `team-board.md`, `lane-registry.md`, `handoff-log.md`) — the shared memory skills read/write. The handoff contract fields are fixed in `skills.manifest.yaml`.

**Skill resources** (`relay_kit_v3/skill_resources/`, 175 dirs): per-skill `references/`, `examples/` (good/bad output), `evals/*-cases.json`, `competencies/*.json`. The `*-battle`/`gauntlet` tooling scores skills against these fixtures. Regenerate with `scripts/regen_all_resources.py` / `sync_skill_resources.py`.

## Working on skills

Per `CONTRIBUTING.md` + `docs/how-to-write-skills.md`:
- Define a skill by **trigger ("Use when…"), workflow, artifact I/O, stop condition, next handoff** — never by persona ("act as a senior X").
- Prefer improving an existing skill or adding an alias over a new canonical skill. Keep `SKILL.md` lean; push depth into `references/`/`scripts/`.
- New/heavily-rewritten skills must be reviewed by a **different path** than the one that authored them (e.g. `review-hub`, a gauntlet).
- Many skills are offensive-security / RE / automation extension packs gated behind authorization skills (`offensive-security-engagement`, `mmo-authorization-gate`). They carry their own scope-and-authorization contracts — respect those gates.

## Multi-adapter config present

This repo also ships `.codex/` (with `config.toml`) and `GEMINI.md` — it is itself installed across Codex/Gemini/Claude. To import the Codex/Gemini agent config (MCP servers, commands, subagents, skills, instructions) into Claude Code, reply `/import` to scan, then `/import --yes=<digest>` to apply.
