# mmo-captcha-farm - strong example

**Request:** a scoped, authorized task that matches `mmo-captcha-farm`.

**Response shape that passes the contract:**

Scope check: the target matches `mmo-captcha-farm` (use when mmo automation hits captcha at scale: manage captcha solving farm with multiple api keys, rate optimization, cost tracking, and failover between services (2captcha, capmonster, anticaptcha, deathbycaptcha)); staying in this lane, not widening it.

Findings, each anchored to evidence:
- observation: a concrete artifact/command result tied to mmo, captcha, farm, cited by path or output id.
- inference: what the observation implies, marked as inference, with a confidence level.
- unknown: what was not covered, stated as a bounded gap rather than a certainty.

Verdict: the question is answered, partially answered, or unresolved - stated explicitly, with the residual risk and the next skill (`mmo-authorization-gate` or a sibling) that should continue.

Nothing is called confirmed without the command output or artifact that proves it.
