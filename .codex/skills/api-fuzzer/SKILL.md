---
name: api-fuzzer
description: "Use when fuzzing REST/GraphQL/gRPC APIs for vulnerabilities: IDOR, mass assignment, authentication bypass, injection, business logic flaws, rate limit bypass, and parameter pollution. Parses OpenAPI/Swagger specs and generates test cases automatically. Engagement proof required."
allowed-tools: ["Read", "Write", "Edit", "Grep", "Glob", "Bash"]
---

# Mission
Use when fuzzing REST/GraphQL/gRPC APIs for vulnerabilities: IDOR, mass assignment, authentication bypass, injection, business logic flaws, rate limit bypass, and parameter pollution.

# API Fuzzer

> Automated API security testing via intelligent fuzzing of endpoints.

## Mission
Discover API security vulnerabilities through automated parameter fuzzing and boundary testing.

## Mandatory scope checks
1. Engagement proof required
2. Confirm target API is in scope
3. Obtain API documentation (OpenAPI/Swagger/Postman collection)
4. Define auth token/headers for authenticated testing
5. Set rate limits to avoid DoS

## Test categories
| Category | What to test |
|---|---|
| IDOR | Enumerate IDs: /users/1 -> /users/2 -> /users/999999 |
| Mass assignment | Add unexpected fields: isAdmin, role, verified |
| Auth bypass | Remove auth header, change roles, JWT manipulation |
| Injection | SQLi, NoSQLi, XSS, command injection in all params |
| Rate limit | Hammer endpoint: 1000 reqs/min |
| Business logic | Negative quantities, invalid states, race conditions |
| Parameter pollution | ?param=A&param=B duplicate params |
| HTTP method fuzzing | PUT/DELETE/PATCH on read-only resources |

## Evidence contract
- engagement_proof confirmed
- each finding documented with request/response pair
- CVSS score estimated
- remediation recommendation provided

## Role
- offensive-security-specialist

## Layer
- layer-4-specialists-and-standalones

## Inputs
- the authorized target or artifact
- the exact question or objective
- .relay-kit/state/workflow-state.md

## Outputs
- .relay-kit/contracts/investigation-notes.md with api-fuzzer findings
- answered/partial/unresolved verdict with evidence

## Reference skills and rules
- Route anything outside api-fuzzer's scope back through `offensive-security-engagement` or `workflow-router`.
- Anchor every conclusion to a file, command, or captured output; never guess from names.
- Report a bounded negative search as bounded, not as proof of absence.
- Open `references/api-fuzzer-operator-contract.md` when scope, evidence, or operator safety is unclear.
- Use `examples/api-fuzzer-good-output.md` and `examples/api-fuzzer-bad-output.md` to calibrate output quality.
- Use `evals/api-fuzzer-cases.json` as the minimum scenario set for behavior regression checks.
- Use `competencies/api-fuzzer-competencies.json` to check covered competencies, failure traps, and unknown-domain policy.

## Likely next step
- api-fuzzer
- offensive-security-engagement
- workflow-router
