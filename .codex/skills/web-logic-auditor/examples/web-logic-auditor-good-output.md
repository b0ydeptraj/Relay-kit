# web-logic-auditor - strong example

**Request:** a scoped, authorized task that matches `web-logic-auditor`.

**Response shape that passes the contract:**

Scope check: the target matches `web-logic-auditor` (use when a lane needs web logic auditor: authorized testing of access-control and business-logic flaws that pattern scanners cannot find — idor/bola, broken function-level authorization, mass assignment, business-logic abuse, and race conditions); staying in this lane, not widening it.

Findings, each anchored to evidence:
- observation: a concrete artifact/command result tied to web, logic, auditor, cited by path or output id.
- inference: what the observation implies, marked as inference, with a confidence level.
- unknown: what was not covered, stated as a bounded gap rather than a certainty.

Verdict: the question is answered, partially answered, or unresolved - stated explicitly, with the residual risk and the next skill (`offensive-security-engagement` or a sibling) that should continue.

Nothing is called confirmed without the command output or artifact that proves it.
