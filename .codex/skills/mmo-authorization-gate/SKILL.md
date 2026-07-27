---
name: mmo-authorization-gate
description: "Use when an MMO or automation lane touches a third-party platform and needs an explicit terms-of-service, authorization, and account-risk gate before high-risk actions run."
allowed-tools: ["Read", "Grep", "Glob", "Bash"]
---

# Mission
Gate MMO and automation lanes behind an explicit authorization, account-ownership, and platform-terms check before any high-risk action runs.

## Boundary
- Use for lanes that act against a third-party platform on accounts the operator controls.
- This gate records authorization and risk; it does not itself perform the automation.
- It does not override platform terms; unauthorized or ToS-violating actions are refused, not gated.

## Default outputs
- an authorization verdict appended to workflow-state
- a documented account-risk and ToS assessment

## Evidence contract
- Input must state the platform, the accounts, and who authorizes the action.
- Output must record an explicit authorized/blocked verdict with the reason.
- Block any lane that cannot show account ownership or operator authorization.

## Typical tasks
- Name the target platform and the accounts the lane will act on.
- Confirm the operator owns or is authorized to act on those accounts.
- Assess account-risk tier and the platform terms and rate limits that apply.
- Emit an authorized-or-blocked verdict before the lane proceeds.

## Working rules
- No high-risk action proceeds without a recorded authorization verdict.
- Platform terms-of-service and rate limits are hard constraints.
- When ownership or authorization is unclear, fail closed and block the lane.
- Hand the runtime safety scan to policy-guard; this gate owns authorization, not shell/secret risk.

## Role
- utility-provider

## Layer
- layer-3-utility-providers

## Inputs
- active hub or orchestrator request
- current authoritative artifact
- only the evidence relevant to this pass

## Outputs
- an authorization verdict appended to workflow-state
- a documented account-risk and ToS assessment

## Reference skills and rules
- Record the operator's authorization and account ownership before any high-risk action.
- Treat platform terms-of-service and rate limits as hard constraints, not suggestions.
- Open `references/mmo-authorization-gate-operator-contract.md` when scope, evidence, or operator safety is unclear.
- Use `examples/mmo-authorization-gate-good-output.md` and `examples/mmo-authorization-gate-bad-output.md` to calibrate output quality.
- Use `evals/mmo-authorization-gate-cases.json` as the minimum scenario set for behavior regression checks.
- Use `competencies/mmo-authorization-gate-competencies.json` to check covered competencies, failure traps, and unknown-domain policy.

## Likely next step
- policy-guard
- qa-governor
- review-hub
