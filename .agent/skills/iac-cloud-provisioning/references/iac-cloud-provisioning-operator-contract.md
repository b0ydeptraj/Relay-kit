# iac-cloud-provisioning Battle Contract

Primary role: infrastructure-engineer
Battle family: infrastructure

Anchor every iac-cloud-provisioning answer to a real artifact, repo area, or explicit missing-context question. The goal is to reduce ambiguity by tying the answer to files, symbols, commands, docs, logs, or state -- not to sound like an expert.

## Concrete Battle Profile

- Repo profile: a Terraform repo with modules, a remote state backend, an environments folder, and a plan CI job
- First files to inspect: main.tf, modules/network/main.tf, environments/prod.tfvars, .github/workflows/plan.yml
- Symbols or named surfaces to confirm: aws_db_instance, terraform_remote_state, lifecycle
- Evidence terms that should appear in a strong answer: plan diff, state backend, blast radius, rollback path

## Working Loop

1. Restate the user task as a verifiable repo action.
2. Name the candidate files before giving advice.
3. Inspect at least one source file and one proof surface for this domain.
4. Separate verified facts, inferred risk, and unknowns.
5. End with the next executable check or handoff.

## Failure Modes To Block

- Applying without reading the plan.
- A destroy or replace on a stateful resource slipping through unflagged.
- Treating a checklist as proof.
- Claiming the change is ready before the domain evidence was inspected.

## Evidence Checklist

- File evidence: cite exact paths or say which anchor is missing.
- Behavior evidence: cite the plan diff or state backend surface that proves the claim.
- Risk evidence: name residual risk and the smallest next verification.
- Handoff evidence: name the receiving skill or gate when another lane should continue.
