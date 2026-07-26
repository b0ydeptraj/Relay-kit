# refactoring-discipline Weak Output Anti-Example

Request: handle a refactoring-discipline request, name files first, and identify the proof surface before editing

Weak answer:

This looks like `refactoring-discipline`, so follow the usual checklist and it should be fine.

Why this fails:

- No file path from `repo with a tangled module, a passing unit suite, and duplicated logic across files` was inspected.
- No symbol such as `OrderService` was confirmed.
- No proof surface was named for `green test net`.
- It blurs verified evidence and inference, which is exactly how overclaim slips back into Relay-kit.

Correction:

Name the concrete path, inspect or search it, state what is verified, and leave unverified claims labeled until a gate proves them.
