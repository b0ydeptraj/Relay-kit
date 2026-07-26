# database-migration-safety Weak Output Anti-Example

Request: handle a database-migration-safety request, name files first, and identify the proof surface before editing

Weak answer:

This looks like `database-migration-safety`, so follow the usual checklist and it should be fine.

Why this fails:

- No file path from `app repo with an ORM, a migrations directory, and a large hot table in production` was inspected.
- No symbol such as `add_column` was confirmed.
- No proof surface was named for `expand contract`.
- It blurs verified evidence and inference, which is exactly how overclaim slips back into Relay-kit.

Correction:

Name the concrete path, inspect or search it, state what is verified, and leave unverified claims labeled until a gate proves them.
