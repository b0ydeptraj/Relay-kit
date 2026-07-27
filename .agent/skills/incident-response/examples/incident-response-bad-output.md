# incident-response Weak Output Anti-Example

Request: handle a incident-response request, name files first, and identify the proof surface before editing

Weak answer:

This looks like `incident-response`, so follow the usual checklist and it should be fine.

Why this fails:

- No file path from `production service with alerting, deploy history, and dashboards during an active latency/error spike` was inspected.
- No symbol such as `rollback` was confirmed.
- No proof surface was named for `severity`.
- It blurs verified evidence and inference, which is exactly how overclaim slips back into Relay-kit.

Correction:

Name the concrete path, inspect or search it, state what is verified, and leave unverified claims labeled until a gate proves them.
