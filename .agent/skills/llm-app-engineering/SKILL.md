---
name: llm-app-engineering
description: "Use when building an LLM-powered application feature such as prompt and context design, retrieval-augmented generation, tool and function schemas, agent loops, or offline evals, and correctness and cost must be proven rather than assumed."
allowed-tools: ["Read", "Write", "Edit", "Grep", "Glob", "Bash"]
---

# Mission
Build an LLM feature as a measurable system: an explicit prompt/context contract, typed tool schemas, and an offline eval that gates changes -- not a hand-tuned prompt nobody can regress.

## Mandatory scope
1. Declare the model target and version, the context window budget, and the accuracy/latency/cost ceiling the feature must hold.
2. Prompt and context: separate the stable system contract from per-request context; state how context is selected and truncated.
3. Retrieval (if any): name the corpus, chunking, embedding model, and the top-k and score threshold; prove relevant chunks actually reach the prompt.
4. Tools: define each tool as a typed schema with required fields and a validation path; state what happens when the model returns malformed arguments.
5. Agent loop (if any): bound the step count, define the stop condition, and name the failure mode when the loop does not converge.
6. Evals: build an offline case set with expected outputs or graders, and a pass threshold that a change must clear before merge.

## Evidence contract
- model + version + context budget declared
- prompt/context contract and truncation rule stated
- tool schemas with malformed-argument handling
- offline eval set with a numeric pass threshold and the current score
- cost-per-request estimate for the chosen model

## Failure modes to block
- Prompt tuning with no eval to catch regressions.
- Retrieval that returns chunks the prompt never actually uses.
- Tool calls trusted without validating the model's arguments.
- An unbounded agent loop with no stop condition.

## Handoff
- Hand implementation to `developer`, defensive review of tool/argument handling to `secure-code-review`, and eval wiring to `test-hub`.

## Role
- llm-application-engineer

## Layer
- layer-4-specialists-and-standalones

## Inputs
- the product behavior the LLM feature must deliver
- available context sources or retrieval corpus
- latency, cost, and accuracy constraints

## Outputs
- prompt and context contract
- tool or function schemas
- an offline eval set with pass criteria

## Reference skills and rules
- Open `references/llm-app-engineering-operator-contract.md` when scope, evidence, or operator safety is unclear.
- Use `examples/llm-app-engineering-good-output.md` and `examples/llm-app-engineering-bad-output.md` to calibrate output quality.
- Use `evals/llm-app-engineering-cases.json` as the minimum scenario set for behavior regression checks.
- Use `competencies/llm-app-engineering-competencies.json` to check covered competencies, failure traps, and unknown-domain policy.

## Likely next step
- developer
- secure-code-review
- test-hub
- review-hub
