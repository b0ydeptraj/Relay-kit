# frida-hooker - strong example

**Request:** a scoped, authorized task that matches `frida-hooker`.

**Response shape that passes the contract:**

Scope check: the target matches `frida-hooker` (use when a lane needs frida hooker: generate and inject frida hooks for dynamic instrumentation — license bypass, ssl pinning bypass, function tracing, crypto interception, anti-debug bypass); staying in this lane, not widening it.

Findings, each anchored to evidence:
- observation: a concrete artifact/command result tied to frida, hooker, lane, cited by path or output id.
- inference: what the observation implies, marked as inference, with a confidence level.
- unknown: what was not covered, stated as a bounded gap rather than a certainty.

Verdict: the question is answered, partially answered, or unresolved - stated explicitly, with the residual risk and the next skill (`reverse-hub` or a sibling) that should continue.

Nothing is called confirmed without the command output or artifact that proves it.
