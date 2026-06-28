---
name: mmo-llm-automation
description: Use when MMO operations need AI-assisted content generation, behavioral variance, Sybil evasion through LLM diversity, or LLM API integration for bulk content tasks.
---

# Mission
Integrate LLM APIs into MMO operations for content diversity, behavioral humanization, and AI-assisted task automation.

## Mandatory scope
1. Declare LLM provider and model: OpenAI GPT-4o, Anthropic Claude, Gemini, or local (Ollama/LM Studio).
2. Prompt engineering: system prompt, diversity parameters, content constraints — document all.
3. Output validation: define acceptance criteria for generated content (length, language, topic compliance).
4. Rate limit and cost management: document token budget per task, batch size, retry strategy.
5. Behavioral variance: if used for Sybil evasion, document diversity metrics (n-gram similarity threshold).
6. Content safety: define prohibited content filters and fallback strategy when model refuses.

## Evidence contract
- LLM provider and model declared
- prompt template documented
- output acceptance criteria defined
- rate limit and cost budget documented
- diversity metric defined if used for Sybil evasion

## Role
- llm-automation-specialist

## Layer
- layer-4-specialists-and-standalones

## Inputs
- content task specification
- LLM provider credentials
- diversity requirements

## Outputs
- LLM integration implementation
- prompt templates
- content validation pipeline

## Reference skills and rules
- Never exceed token budget without explicit approval — LLM costs scale rapidly.
- Diversity metric must be measured, not assumed — compute n-gram similarity.
- Output validation must run before publishing — LLM hallucinations contaminate MMO accounts.
- Local models (Ollama) preferred for sensitive content to avoid API logging.
- Open `references/mmo-llm-automation-operator-contract.md` when scope, evidence, or operator safety is unclear.
- Use `examples/mmo-llm-automation-good-output.md` and `examples/mmo-llm-automation-bad-output.md` to calibrate output quality.
- Use `evals/mmo-llm-automation-cases.json` as the minimum scenario set for behavior regression checks.
- Use `competencies/mmo-llm-automation-competencies.json` to check covered competencies, failure traps, and unknown-domain policy.

## Likely next step
- advanced-python-engineering
- mmo-content-factory
- mmo-reup-automation
- test-hub
- field-journal-evolution
