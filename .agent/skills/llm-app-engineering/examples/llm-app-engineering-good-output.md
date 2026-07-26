# llm-app-engineering Battle-Calibrated Output

Request: review an LLM feature change, name the prompt/retrieval/tool files, and identify the eval that gates it

Recommended skill: `llm-app-engineering` because the request matches `llm-application-engineer` work and has concrete repo anchors.

Read first:

- `src/llm/prompt.py`
- `src/llm/retrieval.py`
- `evals/cases.jsonl`

Evidence gathered:

- Confirmed `build_prompt` and its `prompt contract` before recommending changes.
- Checked `top-k retrieval` against `src/llm/retrieval.py` as the proof surface.
- Identified `tool schema` as a required proof term before completion.

Answer:

Inspect the named paths, compare them against the expected llm-engineering proof surface, and only then recommend a change. If an anchor is missing, ask one question that names the missing file, config, or policy.

Residual risk:

- `offline eval` remains unverified until the focused gate for this domain is captured.
