# Contributing to Relay-kit

Relay-kit is not a random prompt dump.

Treat changes as changes to a workflow system with:

- adapter runtime parity
- shared artifacts under `.ai-kit/`
- bundle gating
- a live compatibility cycle for technical renames

## Before you change anything

Read the current public and runtime docs first:

- `README.md`
- `docs/relay-kit-start-flow.md`
- `docs/how-to-write-skills.md`
- `.ai-kit/docs/folder-structure.md`
- `.ai-kit/docs/bundle-gating.md`

## Contribution rules

### Skills

If you add or edit a skill:

- follow `docs/how-to-write-skills.md`
- keep descriptions in `Use when...` trigger style
- prefer improving an existing skill or adding an alias before creating a new
  canonical skill
- keep the public surface small and easy to remember

### Docs

If you edit docs:

- prefer repo-relative paths over machine-local absolute paths
- update current docs, not stale historical notes
- keep public onboarding simple and move deep internals into docs

### Runtime and bundles

If you touch runtime generation, bundles, or validation:

- explain why the change belongs in the current bundle
- explain why it should or should not affect `baseline`
- do not break adapter parity casually
- do not remove compatibility aliases until the active cycle allows it

## Validation

Run this before submitting a change:

```bash
python scripts/validate_runtime.py
```

If your change affects entrypoints or compatibility docs, also check:

```bash
python relay_kit.py --list-skills
python python_kit.py --list-skills
```

## Pull request checklist

- [ ] The change matches the current Relay-kit structure.
- [ ] Public docs and public naming stay consistent.
- [ ] No stale local path leaked into public docs.
- [ ] Bundle placement is intentional.
- [ ] Validation passed locally.

## What not to do

- do not turn Relay-kit into a plugin runtime
- do not import large persona systems just because they look popular
- do not expand the public surface without clear value
- do not remove compatibility layers early
