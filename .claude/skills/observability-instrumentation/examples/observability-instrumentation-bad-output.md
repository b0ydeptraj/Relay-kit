# observability-instrumentation Weak Output Anti-Example

Request: handle a observability-instrumentation request, name files first, and identify the proof surface before editing

Weak answer:

This looks like `observability-instrumentation`, so follow the usual checklist and it should be fine.

Why this fails:

- No file path from `backend service repo with request handlers, a metrics client, and a logging config` was inspected.
- No symbol such as `request_id` was confirmed.
- No proof surface was named for `RED metrics`.
- It blurs verified evidence and inference, which is exactly how overclaim slips back into Relay-kit.

Correction:

Name the concrete path, inspect or search it, state what is verified, and leave unverified claims labeled until a gate proves them.
