# facebook-automation - weak example (what to avoid)

**Request:** the same scoped task for `facebook-automation`.

**Weak response that fails the contract:**

> It's a facebook automation task, so the usual approach applies. Based on the names involved it looks fine, nothing suspicious, and there's nothing else to worry about. Done.

**Why it fails:**
- Guesses the result from names instead of reading the actual artifact or running the check.
- Cites no file, offset, command, or captured output - no evidence id behind any claim.
- States a negative ("nothing suspicious") as certainty after looking at nothing - a zero-coverage search sold as proof of absence.
- Declares "Done" while every real question is still unresolved, and never routes back through `mmo-authorization-gate` or names residual risk.

The corrective: anchor each claim to concrete evidence, separate observation from inference, bound the negatives, and end with an explicit answered/partial/unresolved verdict.
