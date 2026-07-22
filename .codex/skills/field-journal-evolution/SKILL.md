---
name: field-journal-evolution
description: Use when a task is complete, a pitfall is found, a new technique is discovered, or a routing gap is identified. Writeback experience to the field journal to evolve skill quality over time.
---

# Mission
Capture and index actionable experience from completed tasks so future lanes can reuse solutions, avoid pitfalls, and improve routing accuracy.

## Mandatory scope
1. Writeback triggers: task complete, pitfall encountered, new technique proven, routing gap identified, code pattern reused.
2. Writeback template per entry:
   - scenario: one sentence
   - goal: what was being built or fixed
   - execution-chain: which skills were used in order
   - pitfall-table: what failed and why
   - toolchain: exact tools and versions
   - key-code: the minimal working code or config
   - improvement: what to do differently next time
3. No fluff: every record must contain actionable info — no generic summaries.
4. No repeat: only add a variant if it differs substantially from existing entries.
5. Code-first: key-code field is required — text-only entries are rejected.
6. Check index before new tasks: when starting a similar task, search field-journal first for prior experience.

## Evidence contract
- writeback entry written with all required fields
- key-code field populated
- entry indexed by category
- prior experience searched before starting similar task

## Role
- knowledge-writeback

## Layer
- layer-3-utility-providers

## Inputs
- completed task context
- pitfall or solution discovered
- skill execution chain used

## Outputs
- .relay-kit/state/field-journal.md entry
- experience index update

## Reference skills and rules
- Code-first: key-code field is mandatory in every entry.
- No fluff: reject generic summaries — require actionable specifics.
- No repeat: check existing entries before adding similar content.
- Check field-journal BEFORE starting a similar task — reuse over rediscovery.
- Open `references/field-journal-evolution-operator-contract.md` when scope, evidence, or operator safety is unclear.
- Use `examples/field-journal-evolution-good-output.md` and `examples/field-journal-evolution-bad-output.md` to calibrate output quality.
- Use `evals/field-journal-evolution-cases.json` as the minimum scenario set for behavior regression checks.
- Use `competencies/field-journal-evolution-competencies.json` to check covered competencies, failure traps, and unknown-domain policy.

## Likely next step
- workflow-router
- cook
- developer
- attack-chain-orchestration
