# symbolic-execution-tools - strong example

**Request:** a scoped, authorized task that matches `symbolic-execution-tools`.

**Response shape that passes the contract:**

Scope check: the target matches `symbolic-execution-tools` (use when a lane needs symbolic execution tools: symbolic execution and constraint solving with angr, z3, unicorn, and qiling); staying in this lane, not widening it.

Findings, each anchored to evidence:
- observation: a concrete artifact/command result tied to symbolic, execution, tools, cited by path or output id.
- inference: what the observation implies, marked as inference, with a confidence level.
- unknown: what was not covered, stated as a bounded gap rather than a certainty.

Verdict: the question is answered, partially answered, or unresolved - stated explicitly, with the residual risk and the next skill (`reverse-hub` or a sibling) that should continue.

Nothing is called confirmed without the command output or artifact that proves it.
