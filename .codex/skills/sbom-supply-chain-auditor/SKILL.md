---
name: sbom-supply-chain-auditor
description: "Use when a lane needs sbom supply chain auditor: Audit dependency manifests and lockfiles for SBOM extraction, risky install scripts, unpinned versions, remote/git dependency sources, dependency-confusion and typosquat/known-malicious package names, lockfile integrity gaps, copyleft license risk, and secret-like values."
allowed-tools: ["Read", "Write", "Edit", "Grep", "Glob", "Bash"]
---

# Mission
Audit dependency manifests and lockfiles for SBOM extraction, risky install scripts, unpinned versions, remote/git dependency sources, dependency-confusion and typosquat/known-malicious package names, lockfile integrity gaps, copyleft license risk, and secret-like values.

# SBOM Supply Chain Auditor

## Purpose

Use after source recovery or on application repos to identify dependency and supply-chain risks.

## Workflow

1. Run `python sbom-supply-chain-auditor/scripts/analyze_supply_chain.py <target> --out output/sbom-supply-chain-auditor`.
2. Review `findings.json` and `REPORT.md`.
3. Use findings to prioritize dependency pinning, secret rotation, and package trust review.

## Coverage

- **Install-time execution** — npm `preinstall`/`install`/`postinstall`/`prepare` scripts.
- **Version hygiene** — floating/unpinned npm & Python versions; `file:` local deps.
- **Remote sources** — `git+`/`http(s)` deps (high unless pinned to a commit hash).
- **Dependency confusion** — scoped `@scope/pkg` that may resolve from the public registry.
- **Typosquat / malware** — names one edit from popular packages, and a curated known-malicious list (critical).
- **Lockfile integrity** — `package-lock.json` entries missing integrity hashes.
- **License risk** — missing license, or copyleft/restrictive (AGPL/GPL/SSPL/UNLICENSED).
- **Secrets** — password/token/secret-like values in manifests.

> Heuristic, not a CVE feed. Typosquat/known-malicious lists are a curated subset — pair with a vulnerability database for full coverage.

## Role
- offensive-security-specialist

## Layer
- layer-4-specialists-and-standalones

## Inputs
- the authorized target or artifact
- the exact question or objective
- .relay-kit/state/workflow-state.md

## Outputs
- .relay-kit/contracts/investigation-notes.md with sbom-supply-chain-auditor findings
- answered/partial/unresolved verdict with evidence

## Reference skills and rules
- Route anything outside sbom-supply-chain-auditor's scope back through `offensive-security-engagement` or `workflow-router`.
- Anchor every conclusion to a file, command, or captured output; never guess from names.
- Report a bounded negative search as bounded, not as proof of absence.
- Open `references/sbom-supply-chain-auditor-operator-contract.md` when scope, evidence, or operator safety is unclear.
- Use `examples/sbom-supply-chain-auditor-good-output.md` and `examples/sbom-supply-chain-auditor-bad-output.md` to calibrate output quality.
- Use `evals/sbom-supply-chain-auditor-cases.json` as the minimum scenario set for behavior regression checks.
- Use `competencies/sbom-supply-chain-auditor-competencies.json` to check covered competencies, failure traps, and unknown-domain policy.

## Likely next step
- sbom-supply-chain-auditor
- offensive-security-engagement
- workflow-router
