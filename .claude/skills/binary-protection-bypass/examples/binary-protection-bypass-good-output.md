# binary-protection-bypass - strong example

**Request:** a scoped, authorized task that matches `binary-protection-bypass`.

**Response shape that passes the contract:**

Scope check: the target matches `binary-protection-bypass` (use when a lane needs binary protection bypass: identify and bypass binary mitigations (aslr, pie, nx/dep, stack canary, relro, fortify, cet, mte) on elf binaries); staying in this lane, not widening it.

Findings, each anchored to evidence:
- observation: a concrete artifact/command result tied to binary, protection, bypass, cited by path or output id.
- inference: what the observation implies, marked as inference, with a confidence level.
- unknown: what was not covered, stated as a bounded gap rather than a certainty.

Verdict: the question is answered, partially answered, or unresolved - stated explicitly, with the residual risk and the next skill (`reverse-hub` or a sibling) that should continue.

Nothing is called confirmed without the command output or artifact that proves it.
