# secrets-management Weak Output Anti-Example

Request: review how a credential is stored, injected, scoped, and rotated, and name the leak-response path

Weak answer:

This looks like `secrets-management`, so apply the standard fix and it should be fine.

Why this fails:

- No file path from `a fleet repo with an env config, a secret-store client, a rotation script, and an access-scoping policy` was inspected.
- No symbol such as `get_secret` was confirmed.
- No proof surface was named for `vaulted secret`.
- It blurs verified evidence and inference, which is how overclaim slips back in.

Correction:

Name the concrete path, inspect or search it, state what is verified, and leave unverified claims labeled until a gate proves them.
