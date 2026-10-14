# dotnet-decompiler - strong example

**Request:** a scoped, authorized task that matches `dotnet-decompiler`.

**Response shape that passes the contract:**

Scope check: the target matches `dotnet-decompiler` (use when a lane needs dotnet decompiler: automated ); staying in this lane, not widening it.

Findings, each anchored to evidence:
- observation: a concrete artifact/command result tied to dotnet, decompiler, lane, cited by path or output id.
- inference: what the observation implies, marked as inference, with a confidence level.
- unknown: what was not covered, stated as a bounded gap rather than a certainty.

Verdict: the question is answered, partially answered, or unresolved - stated explicitly, with the residual risk and the next skill (`reverse-hub` or a sibling) that should continue.

Nothing is called confirmed without the command output or artifact that proves it.
