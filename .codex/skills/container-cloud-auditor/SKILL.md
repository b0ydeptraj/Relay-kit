---
name: container-cloud-auditor
description: "Use when a lane needs container cloud auditor: Audit Docker, Compose, Kubernetes, Terraform, and cloud configuration for exposed services, privileged runtime settings, hardcoded secrets, and risky infrastructure defaults."
allowed-tools: ["Read", "Write", "Edit", "Grep", "Glob", "Bash"]
---

# Mission
Audit Docker, Compose, Kubernetes, Terraform, and cloud configuration for exposed services, privileged runtime settings, hardcoded secrets, and risky infrastructure defaults.

# Container Cloud Auditor

## Purpose

Use for authorized review of container and cloud deployment artifacts in recovered source, app repos, or exported infrastructure bundles.

## Workflow

1. Run `python container-cloud-auditor/scripts/analyze_container_cloud.py <target> --out output/container-cloud-auditor`.
2. Review `findings.json` and `REPORT.md`.
3. Chain findings into remediation or pentest report generation.

## Coverage

Files are auto-classified (Dockerfile / Compose / Kubernetes / Terraform) so each rule applies in the right context. ~30 rules across:

- **Dockerfile** — `:latest`/unpinned base, `USER root` / no non-root USER, remote `ADD`, pipe-to-shell installs, secrets in `ENV`/`ARG`, missing `HEALTHCHECK`.
- **Compose / containers** — `privileged`, host networking, added capabilities (`SYS_ADMIN`/`ALL`), mounted `docker.sock`, `:latest` images.
- **Kubernetes** — `hostNetwork`/`hostPID`/`hostIPC`, `hostPath`, `allowPrivilegeEscalation`, `runAsNonRoot: false`, `readOnlyRootFilesystem: false`, dangerous capabilities, `automountServiceAccountToken`, `LoadBalancer` exposure, missing resource limits / securityContext.
- **Terraform / cloud** — public S3 ACL, `0.0.0.0/0` ingress, wildcard IAM (`*` / `*:*`), encryption disabled, `publicly_accessible`.
- **Secrets (any file)** — AWS/Google keys, private-key blocks, Slack tokens, hardcoded credentials.

## Role
- offensive-security-specialist

## Layer
- layer-4-specialists-and-standalones

## Inputs
- the authorized target or artifact
- the exact question or objective
- .relay-kit/state/workflow-state.md

## Outputs
- .relay-kit/contracts/investigation-notes.md with container-cloud-auditor findings
- answered/partial/unresolved verdict with evidence

## Reference skills and rules
- Route anything outside container-cloud-auditor's scope back through `offensive-security-engagement` or `workflow-router`.
- Anchor every conclusion to a file, command, or captured output; never guess from names.
- Report a bounded negative search as bounded, not as proof of absence.
- Open `references/container-cloud-auditor-operator-contract.md` when scope, evidence, or operator safety is unclear.
- Use `examples/container-cloud-auditor-good-output.md` and `examples/container-cloud-auditor-bad-output.md` to calibrate output quality.
- Use `evals/container-cloud-auditor-cases.json` as the minimum scenario set for behavior regression checks.
- Use `competencies/container-cloud-auditor-competencies.json` to check covered competencies, failure traps, and unknown-domain policy.

## Likely next step
- container-cloud-auditor
- offensive-security-engagement
- workflow-router
