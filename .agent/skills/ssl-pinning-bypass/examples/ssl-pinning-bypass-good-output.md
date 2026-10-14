# ssl-pinning-bypass - strong example

**Request:** a scoped, authorized task that matches `ssl-pinning-bypass`.

**Response shape that passes the contract:**

Scope check: the target matches `ssl-pinning-bypass` (use when mobile or desktop app ssl certificate pinning blocks mitm traffic interception); staying in this lane, not widening it.

Findings, each anchored to evidence:
- observation: a concrete artifact/command result tied to ssl, pinning, bypass, cited by path or output id.
- inference: what the observation implies, marked as inference, with a confidence level.
- unknown: what was not covered, stated as a bounded gap rather than a certainty.

Verdict: the question is answered, partially answered, or unresolved - stated explicitly, with the residual risk and the next skill (`reverse-hub` or a sibling) that should continue.

Nothing is called confirmed without the command output or artifact that proves it.
