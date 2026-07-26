# llm-app-engineering Battle Contract

Primary role: llm-application-engineer
Battle family: llm-engineering

Anchor every llm-app-engineering answer to a real artifact, repo area, or explicit missing-context question. The goal is to reduce ambiguity by tying the answer to files, symbols, commands, docs, logs, or state -- not to sound like an expert.

## Concrete Battle Profile

- Repo profile: an LLM feature repo with a prompt module, a retrieval index, tool schemas, and an offline eval set
- First files to inspect: src/llm/prompt.py, src/llm/retrieval.py, src/llm/tools.py, evals/cases.jsonl
- Symbols or named surfaces to confirm: build_prompt, retrieve_context, tool_schema
- Evidence terms that should appear in a strong answer: prompt contract, top-k retrieval, tool schema, offline eval

## Working Loop

1. Restate the user task as a verifiable repo action.
2. Name the candidate files before giving advice.
3. Inspect at least one source file and one proof surface for this domain.
4. Separate verified facts, inferred risk, and unknowns.
5. End with the next executable check or handoff.

## Failure Modes To Block

- Tuning a prompt with no eval to catch regressions.
- Retrieval that returns chunks the prompt never uses.
- Treating a checklist as proof.
- Claiming the change is ready before the domain evidence was inspected.

## Evidence Checklist

- File evidence: cite exact paths or say which anchor is missing.
- Behavior evidence: cite the prompt contract or top-k retrieval surface that proves the claim.
- Risk evidence: name residual risk and the smallest next verification.
- Handoff evidence: name the receiving skill or gate when another lane should continue.
