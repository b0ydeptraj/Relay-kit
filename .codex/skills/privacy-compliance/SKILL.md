---
name: privacy-compliance
description: "Use when a workload collects, stores, or transfers personal data and needs a privacy and data-retention gate covering PII minimization, consent or lawful basis, retention limits, and deletion."
allowed-tools: ["Read", "Grep", "Glob", "Bash"]
---

# Mission
Treat personal data as a liability to minimize: collect only what the purpose needs, keep it only as long as justified, and be able to delete it on request.

## Mandatory scope
1. Inventory: enumerate the personal data collected, classify sensitivity (contact, financial, health, biometric, identifier), and name where each field flows.
2. Minimization: for every field, state the purpose that justifies it; drop fields no purpose needs.
3. Lawful basis and consent: state the basis for processing each category and where consent is captured, if required.
4. Retention: set a retention window per category and the mechanism that deletes or anonymizes past it.
5. Rights: define how access, correction, and deletion requests are fulfilled, including in backups and downstream copies.
6. Transfer: flag any cross-border or third-party transfer and the safeguard that covers it.

## Evidence contract
- data inventory with per-field sensitivity classification
- a stated purpose for every retained field
- retention window and deletion mechanism per category
- a deletion path that reaches backups and downstream copies

## Failure modes to block
- Collecting data with no purpose behind it.
- Indefinite retention with no deletion mechanism.
- A deletion request that leaves copies in backups or a data warehouse.
- PII in logs, analytics, or third-party tools without a safeguard.

## Handoff
- Hand schema and retention enforcement to `data-persistence`, secret handling to `secrets-management`, and code-path review to `secure-code-review`.

## Role
- privacy-reviewer

## Layer
- layer-4-specialists-and-standalones

## Inputs
- the data the workload collects or processes
- the stated purpose and legal context
- current storage, sharing, and retention behavior

## Outputs
- a data inventory with PII classification
- a retention and deletion policy
- a consent and lawful-basis note

## Reference skills and rules
- Open `references/privacy-compliance-operator-contract.md` when scope, evidence, or operator safety is unclear.
- Use `examples/privacy-compliance-good-output.md` and `examples/privacy-compliance-bad-output.md` to calibrate output quality.
- Use `evals/privacy-compliance-cases.json` as the minimum scenario set for behavior regression checks.
- Use `competencies/privacy-compliance-competencies.json` to check covered competencies, failure traps, and unknown-domain policy.

## Likely next step
- data-persistence
- secure-code-review
- secrets-management
- review-hub
