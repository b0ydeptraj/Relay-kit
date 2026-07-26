# secure-code-review Weak Output Anti-Example

Request: handle a secure-code-review request, name files first, and identify the proof surface before editing

Weak answer:

This looks like `secure-code-review`, so follow the usual checklist and it should be fine.

Why this fails:

- No file path from `web service repo with HTTP handlers, a database layer, auth middleware, and a dependency lockfile` was inspected.
- No symbol such as `build_query` was confirmed.
- No proof surface was named for `tainted input`.
- It blurs verified evidence and inference, which is exactly how overclaim slips back into Relay-kit.

Correction:

Name the concrete path, inspect or search it, state what is verified, and leave unverified claims labeled until a gate proves them.
