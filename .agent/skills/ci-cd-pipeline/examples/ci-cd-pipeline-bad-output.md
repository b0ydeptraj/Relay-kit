# ci-cd-pipeline Weak Output Anti-Example

Request: handle a ci-cd-pipeline request, name files first, and identify the proof surface before editing

Weak answer:

This looks like `ci-cd-pipeline`, so follow the usual checklist and it should be fine.

Why this fails:

- No file path from `repo with a CI workflow file, a lockfile, and a deploy script targeting staging and prod` was inspected.
- No symbol such as `build` was confirmed.
- No proof surface was named for `blocking gate`.
- It blurs verified evidence and inference, which is exactly how overclaim slips back into Relay-kit.

Correction:

Name the concrete path, inspect or search it, state what is verified, and leave unverified claims labeled until a gate proves them.
