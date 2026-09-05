# tech-spec

> Path: `.relay-kit/contracts/tech-spec.md`
> Purpose: Small-change spec used by the quick flow for bug fixes and narrowly scoped features.
> Used by: workflow-router, cook, developer, fix-hub, test-hub

## Change summary
Fill in only with evidence, decisions, or open questions relevant to this artifact.

No evidence recorded yet.

## Root cause or context
Fill in only with evidence, decisions, or open questions relevant to this artifact.

No evidence recorded yet.

## Files likely affected
Fill in only with evidence, decisions, or open questions relevant to this artifact.

No evidence recorded yet.

## Implementation notes
Fill in only with evidence, decisions, or open questions relevant to this artifact.

No evidence recorded yet.

## Verification steps
Fill in only with evidence, decisions, or open questions relevant to this artifact.

No evidence recorded yet.

## GPT-5.6 Sol skill optimization delta

- Updated: single-Sol routing removes `team` and `delegation-control` from the registry, generated adapters, and default fixtures.
- Added: `scope-discipline` as a baseline discipline utility for minimum-complete-contract, subtraction, bounded reasoning, and proof-linked stopping.
- Preserved: native Codex/Responses compaction; no custom compaction layer or StateM dependency was added.
- Verification: focused suite `python -m pytest -q tests/test_workflow_eval.py tests/test_live_state_hygiene.py tests/test_competency_battle.py tests/test_skill_proof_audit.py tests/test_context_search_eval.py tests/test_skill_resources.py tests/test_repo_hardening_gates.py tests/test_skill_frontmatter_valid.py tests/test_skill_reference_resolves.py tests/test_enterprise_bundle.py` -> 2405 passed.
- Research ledger: `docs/gpt56-sol-efficiency-and-scope-discipline.md` records 50 sources, decisions, and residual risk.
