# llm-app-engineering Weak Output Anti-Example

Request: review an LLM feature change, name the prompt/retrieval/tool files, and identify the eval that gates it

Weak answer:

This looks like `llm-app-engineering`, so apply the standard fix and it should be fine.

Why this fails:

- No file path from `an LLM feature repo with a prompt module, a retrieval index, tool schemas, and an offline eval set` was inspected.
- No symbol such as `build_prompt` was confirmed.
- No proof surface was named for `prompt contract`.
- It blurs verified evidence and inference, which is how overclaim slips back in.

Correction:

Name the concrete path, inspect or search it, state what is verified, and leave unverified claims labeled until a gate proves them.
