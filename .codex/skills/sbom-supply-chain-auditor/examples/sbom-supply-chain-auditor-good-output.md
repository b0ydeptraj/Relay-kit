# sbom-supply-chain-auditor - strong example

**Request:** a scoped, authorized task that matches `sbom-supply-chain-auditor`.

**Response shape that passes the contract:**

Scope check: the target matches `sbom-supply-chain-auditor` (use when a lane needs sbom supply chain auditor: audit dependency manifests and lockfiles for sbom extraction, risky install scripts, unpinned versions, remote/git dependency sources, dependency-confusion and typosquat/known-malicious package names, lockfile integrity gaps, copyleft license risk, and secret-like values); staying in this lane, not widening it.

Findings, each anchored to evidence:
- observation: a concrete artifact/command result tied to sbom, supply, chain, cited by path or output id.
- inference: what the observation implies, marked as inference, with a confidence level.
- unknown: what was not covered, stated as a bounded gap rather than a certainty.

Verdict: the question is answered, partially answered, or unresolved - stated explicitly, with the residual risk and the next skill (`offensive-security-engagement` or a sibling) that should continue.

Nothing is called confirmed without the command output or artifact that proves it.
