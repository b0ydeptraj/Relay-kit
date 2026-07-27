---
name: incident-response
description: "Use when a production incident is active or just resolved: triage severity, stabilize, communicate status, capture a timeline, and write a blameless postmortem with real action items."
allowed-tools: ["Read", "Grep", "Glob", "Bash"]
---

# Mission
Drive a production incident from detection to a blameless postmortem: stabilize first, communicate clearly, and convert the timeline into durable fixes.

## Mandatory scope
1. Assign severity from user impact and scope, and name the incident commander role.
2. Stabilize before diagnosing deeply: mitigate (roll back, feature-flag, scale) to stop the bleeding.
3. Communicate: a status cadence with impact, current action, and next update time — no speculation as fact.
4. Capture a timeline with timestamps: detection, actions, and their effect.
5. Write a blameless postmortem: contributing factors, not blame, plus owned, dated action items.

## Evidence contract
- severity assigned from stated user impact
- mitigation taken before deep diagnosis
- timeline with timestamps captured
- postmortem with blameless framing and owned action items

## Role
- incident-responder

## Layer
- layer-4-specialists-and-standalones

## Inputs
- alert / incident report
- system state, logs, and metrics
- recent changes and deploys

## Outputs
- incident status updates
- incident timeline
- .relay-kit/references/postmortem-<id>.md

## Reference skills and rules
- Stabilize before rooting-cause; stop user impact first.
- Keep communication factual — label hypotheses as hypotheses.
- Blameless postmortems focus on systemic factors, never individuals.
- Every action item has an owner and a date, or it is not real.
- Open `references/incident-response-operator-contract.md` when scope, evidence, or operator safety is unclear.
- Use `examples/incident-response-good-output.md` and `examples/incident-response-bad-output.md` to calibrate output quality.
- Use `evals/incident-response-cases.json` as the minimum scenario set for behavior regression checks.
- Use `competencies/incident-response-competencies.json` to check covered competencies, failure traps, and unknown-domain policy.

## Likely next step
- root-cause-debugging
- observability-instrumentation
- fix-hub
- ci-cd-pipeline
