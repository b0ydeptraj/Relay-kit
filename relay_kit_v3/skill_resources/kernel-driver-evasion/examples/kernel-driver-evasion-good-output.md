# kernel-driver-evasion - strong example

**Request:** a scoped, authorized task that matches `kernel-driver-evasion`.

**Response shape that passes the contract:**

Scope check: the target matches `kernel-driver-evasion` (use when a payload needs ring 0 evasion: byovd (bring your own vulnerable driver), dkom (direct kernel object manipulation), kernel callback suppression (obregistercallbacks, pssetcreateprocessnotifyroutine), dse bypass, patchguard (kpp) timer disarm, or ppl (protected process light) bypass via eprocess ); staying in this lane, not widening it.

Findings, each anchored to evidence:
- observation: a concrete artifact/command result tied to kernel, driver, evasion, cited by path or output id.
- inference: what the observation implies, marked as inference, with a confidence level.
- unknown: what was not covered, stated as a bounded gap rather than a certainty.

Verdict: the question is answered, partially answered, or unresolved - stated explicitly, with the residual risk and the next skill (`offensive-security-engagement` or a sibling) that should continue.

Nothing is called confirmed without the command output or artifact that proves it.
