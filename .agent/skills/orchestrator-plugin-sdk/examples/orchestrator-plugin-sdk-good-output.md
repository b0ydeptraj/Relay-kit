# orchestrator-plugin-sdk - strong example

**Request:** a scoped, authorized task that matches `orchestrator-plugin-sdk`.

**Response shape that passes the contract:**

Scope check: the target matches `orchestrator-plugin-sdk` (use when a lane needs orchestrator plugin sdk: scaffold and validate new toolkit skills with the standard file layout, metadata, output contract, and orchestrator registration checklist); staying in this lane, not widening it.

Findings, each anchored to evidence:
- observation: a concrete artifact/command result tied to orchestrator, plugin, sdk, cited by path or output id.
- inference: what the observation implies, marked as inference, with a confidence level.
- unknown: what was not covered, stated as a bounded gap rather than a certainty.

Verdict: the question is answered, partially answered, or unresolved - stated explicitly, with the residual risk and the next skill (`workflow-router` or a sibling) that should continue.

Nothing is called confirmed without the command output or artifact that proves it.
