# privacy-compliance Weak Output Anti-Example

Request: review what personal data a feature collects, justify each field, and name the retention and deletion path

Weak answer:

This looks like `privacy-compliance`, so apply the standard fix and it should be fine.

Why this fails:

- No file path from `a product repo with a signup form, a user data model, an analytics client, and a data-retention job` was inspected.
- No symbol such as `User` was confirmed.
- No proof surface was named for `PII classification`.
- It blurs verified evidence and inference, which is how overclaim slips back in.

Correction:

Name the concrete path, inspect or search it, state what is verified, and leave unverified claims labeled until a gate proves them.
