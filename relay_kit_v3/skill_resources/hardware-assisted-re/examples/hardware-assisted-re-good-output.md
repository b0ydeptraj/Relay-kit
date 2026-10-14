# hardware-assisted-re - strong example

**Request:** a scoped, authorized task that matches `hardware-assisted-re`.

**Response shape that passes the contract:**

Scope check: the target matches `hardware-assisted-re` (use when analysis or evasion needs hypervisor-level (ring -1) techniques: ept hooking / npt hooking (memory cloaking / page shadowing) on intel vt-x and amd-v/svm, hardware breakpoints via dr registers, vmexit storm mitigation, or bypassing integrity checkers (battleye, vanguard, eac) that validate code pages from kernel level); staying in this lane, not widening it.

Findings, each anchored to evidence:
- observation: a concrete artifact/command result tied to hardware, assisted, analysis, cited by path or output id.
- inference: what the observation implies, marked as inference, with a confidence level.
- unknown: what was not covered, stated as a bounded gap rather than a certainty.

Verdict: the question is answered, partially answered, or unresolved - stated explicitly, with the residual risk and the next skill (`reverse-hub` or a sibling) that should continue.

Nothing is called confirmed without the command output or artifact that proves it.
