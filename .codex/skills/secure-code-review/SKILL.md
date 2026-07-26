---
name: secure-code-review
description: "Use when application code needs a defensive security review before merge or release: injection, authn/authz, secrets handling, crypto misuse, SSRF, deserialization, and vulnerable dependencies."
allowed-tools: ["Read", "Grep", "Glob", "Bash"]
---

# Mission
Turn security from implicit trust into an explicit, evidence-backed defensive review gate over real code paths, not a generic checklist.

## Mandatory scope
1. Identify the trust boundary: where untrusted input enters (HTTP params, headers, files, queues, env) and where it reaches a sink.
2. Check injection sinks: SQL/NoSQL, OS command, template, LDAP, and path traversal — confirm parameterization or safe APIs.
3. Check authn/authz: every state-changing route enforces identity and object-level authorization, not just authentication.
4. Check secrets: no hardcoded keys/tokens, secrets sourced from env/vault, and no secret logged.
5. Check crypto and randomness: no weak hashing for passwords, no ECB, no static IV, CSPRNG for tokens.
6. Check dependencies: flag known-vulnerable versions and unpinned critical packages.

## Evidence contract
- each finding names file:line, the tainted input, and the sink
- severity assigned (critical/high/medium/low) with exploitability rationale
- a concrete fix or safe-API replacement per finding
- pass or hold verdict tied to whether any critical/high finding is unresolved

## Role
- security-reviewer

## Layer
- layer-3-utility-providers

## Inputs
- diff or changed files
- authoritative artifact / PR
- threat context if provided

## Outputs
- security review findings appended to review notes or qa-report
- pass or hold verdict with severities

## Reference skills and rules
- No pass verdict while any critical or high finding is unresolved.
- Trace input-to-sink; do not flag on keyword match alone.
- This is defensive review only — it hardens code, it does not build offensive tooling.
- Hand unresolved findings to fix-hub with explicit acceptance criteria.
- Open `references/secure-code-review-operator-contract.md` when scope, evidence, or operator safety is unclear.
- Use `examples/secure-code-review-good-output.md` and `examples/secure-code-review-bad-output.md` to calibrate output quality.
- Use `evals/secure-code-review-cases.json` as the minimum scenario set for behavior regression checks.
- Use `competencies/secure-code-review-competencies.json` to check covered competencies, failure traps, and unknown-domain policy.

## Likely next step
- fix-hub
- review-hub
- qa-governor
- dependency-management
