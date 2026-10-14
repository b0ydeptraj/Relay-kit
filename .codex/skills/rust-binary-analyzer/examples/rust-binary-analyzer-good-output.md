# rust-binary-analyzer - strong example

**Request:** a scoped, authorized task that matches `rust-binary-analyzer`.

**Response shape that passes the contract:**

Scope check: the target matches `rust-binary-analyzer` (use when a lane needs rust binary analyzer: analyze rust native binaries — demangle symbols, extract panic paths to reconstruct module map, detect frameworks (tauri/actix/rocket/axum), locate license validation logic); staying in this lane, not widening it.

Findings, each anchored to evidence:
- observation: a concrete artifact/command result tied to rust, binary, analyzer, cited by path or output id.
- inference: what the observation implies, marked as inference, with a confidence level.
- unknown: what was not covered, stated as a bounded gap rather than a certainty.

Verdict: the question is answered, partially answered, or unresolved - stated explicitly, with the residual risk and the next skill (`reverse-hub` or a sibling) that should continue.

Nothing is called confirmed without the command output or artifact that proves it.
