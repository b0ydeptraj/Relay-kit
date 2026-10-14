# web-app-scanner operator contract

## Scope
`web-app-scanner` is a layer-4 offensive-security specialist. Use when a lane needs web app scanner: Authorized web application testing from the CLI. Subdomain enumeration (crt.sh / subfinder / DNS brute) with dangling-CNAME subdomain-takeover detection to map the whole estate, per-host passive recon (security headers / cookies / TLS / advanced CORS bypass tests), non-destructive active vulnerability checks (exposed .git/.env, reflected XSS, open redirect, path traversal, header injection, SSTI, SSRF-to-metadata, directory listing) with link crawling, optional nuclei & ffuf, and guarded sqlmap SQL injection testing — one orchestrated whole-system scan into a severity-ranked findings report.

Enter it only for work that matches that scope; route anything broader back through `offensive-security-engagement` or `workflow-router` so the lane keeps a single owner.

## Authorization
This specialist runs only against artifacts and targets the operator is authorized to analyze or test. When ownership or authorization is unclear, fail closed and hand the decision to `offensive-security-engagement` before any action that changes state outside the workspace.

## Evidence rules
- Anchor every conclusion to a concrete file, offset, command, or captured output, not to a guess from a name.
- Separate what was observed from what was inferred, and name what is still unknown.
- Report a search that found nothing as bounded to what it covered, never as proof of absence.
- Do not claim a result is confirmed without the command output, log, or artifact that proves it.

## Hold conditions
Hold and route back when the only basis for a claim is a filename or symbol, when a capture was truncated, or when the lane would act outside the authorized target.

## Exit
End with the concrete finding, the evidence behind it, the residual unknowns, and the next skill (`offensive-security-engagement`, `workflow-router`, or a sibling specialist) that should continue.
