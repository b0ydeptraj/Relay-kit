# secrets-management Battle Contract

Primary role: secrets-engineer
Battle family: secrets

Anchor every secrets-management answer to a real artifact, repo area, or explicit missing-context question. The goal is to reduce ambiguity by tying the answer to files, symbols, commands, docs, logs, or state -- not to sound like an expert.

## Concrete Battle Profile

- Repo profile: a fleet repo with an env config, a secret-store client, a rotation script, and an access-scoping policy
- First files to inspect: config/settings.py, infra/secrets_client.py, scripts/rotate.py, docs/secret-policy.md
- Symbols or named surfaces to confirm: get_secret, rotate_credential, scope_token
- Evidence terms that should appear in a strong answer: vaulted secret, least privilege, rotation window, leak response

## Working Loop

1. Restate the user task as a verifiable repo action.
2. Name the candidate files before giving advice.
3. Inspect at least one source file and one proof surface for this domain.
4. Separate verified facts, inferred risk, and unknowns.
5. End with the next executable check or handoff.

## Failure Modes To Block

- A secret left in source control, an env file, or a log line.
- One shared token everywhere so revocation breaks everything.
- Treating a checklist as proof.
- Claiming the change is ready before the domain evidence was inspected.

## Evidence Checklist

- File evidence: cite exact paths or say which anchor is missing.
- Behavior evidence: cite the vaulted secret or least privilege surface that proves the claim.
- Risk evidence: name residual risk and the smallest next verification.
- Handoff evidence: name the receiving skill or gate when another lane should continue.
