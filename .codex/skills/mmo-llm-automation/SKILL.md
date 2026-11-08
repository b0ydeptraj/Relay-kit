---
name: mmo-llm-automation
description: "LIBRARY LAYER. Use when a pipeline needs an LLM primitive: prompt template, temperature strategy, model routing (GPT / Claude / local / cheap-tier), persona variance for Sybil-risk reduction, retries, cost budget. Produces generate(brief) -> text. Does NOT schedule, distribute, or compose a multi-step content run; that is `mmo-content-factory` (pipeline)."
allowed-tools: ["Read", "Write", "Edit", "Bash"]
---

# Mission
Be a reliable LLM generation primitive the content pipeline can call. One brief in, one scored generation out, with cost and variance recorded.

## Scope boundary (do not violate)
- IN scope: prompt template, model routing, variance control, self-grade, cost accounting, retry on fail.
- OUT of scope: scheduling, platform-specific formatting, multi-step campaigns, cross-channel distribution -> `mmo-content-factory`.
- OUT of scope: building an LLM app with memory, tools, or multi-turn agent loop -> `llm-app-engineering`.

## Pre-flight
1. Brief has required fields: topic, length, tone, persona, language, constraints.
2. Model preference list exists with cost table.
3. Budget cap set.
4. Quality rubric named (keyword coverage, forbidden-phrase list, length bounds, language tag).

## Generate contract (one call)
```
generate(brief) -> {
  text: str,
  model_used: str,
  tokens_in: int, tokens_out: int,
  cost: float,
  variance_score: float,   # 0..1 vs sibling outputs in same batch
  self_grade: pass | fail:<reason>,
  retries: int
}
```

## Variance controls
- Temperature schedule per generation index (0.4, 0.7, 0.9, ...) rather than one fixed value.
- Persona rotation across sibling outputs.
- Post-generation n-gram similarity check vs siblings; reject if too similar.

## Failure modes to self-check
- You scheduled a post or picked a platform -> wrong layer, return generation only.
- You exceeded budget silently -> stop batch, write breach record.
- You returned text without model/cost -> invalid, redo accounting.
- Variance across sibling outputs is near 0 -> increase temperature or rotate persona, retry.

## Role
- mmo-llm-library

## Layer
- layer-4-specialists-and-standalones

## Inputs
- brief: {topic, length, tone, persona, language, constraints}
- model preference list with per-model cost + token limits
- variance budget: how much to diverge across N outputs for the same brief
- quality rubric for self-grading before returning

## Outputs
- generate(brief) -> {text, model_used, tokens_in, tokens_out, cost, variance_score}
- retry ledger when self-grade fails
- cost report per batch vs budget cap

## Reference skills and rules
- This skill is a LIBRARY. It produces one generation at a time plus variance controls. It does not know about schedules, platforms, or distribution - that is mmo-content-factory.
- Persona variance is NOT impersonation of a real person. Personas are abstract voice profiles (tone, vocabulary band, sentence length).
- Every generation records model, tokens, and cost. A batch that exceeds budget stops with a budget-breach record.
- Self-grading against the brief's quality rubric is mandatory before returning.
- Open `references/mmo-llm-automation-operator-contract.md` when scope, evidence, or operator safety is unclear.
- Use `examples/mmo-llm-automation-good-output.md` and `examples/mmo-llm-automation-bad-output.md` to calibrate output quality.
- Use `evals/mmo-llm-automation-cases.json` as the minimum scenario set for behavior regression checks.
- Use `competencies/mmo-llm-automation-competencies.json` to check covered competencies, failure traps, and unknown-domain policy.

## Likely next step
- mmo-content-factory
- llm-app-engineering
- secrets-management
