---
name: iac-cloud-provisioning
description: "Use when provisioning or changing cloud infrastructure as code with Terraform, Pulumi, or CloudFormation, including state management, drift detection, plan review, and a safe apply with rollback."
allowed-tools: ["Read", "Write", "Edit", "Grep", "Glob", "Bash"]
---

# Mission
Change cloud infrastructure through reviewed, reversible plans -- never console-clicked mutations -- with state and drift kept honest.

## Mandatory scope
1. Declare the tool and provider (Terraform, Pulumi, CloudFormation) and where state lives, including locking.
2. Always run and read a plan/diff before apply; state exactly which resources create, update, replace, or destroy.
3. Flag every destroy or replace on a stateful resource (database, volume, load balancer) as high blast-radius and require explicit confirmation.
4. Detect drift: compare real state to code before changing anything, and reconcile or document it.
5. Define the apply order and the rollback path (previous state, tainted-resource recovery, or a reverse change).
6. Keep secrets out of state and code; hand credential material to `secrets-management`.

## Evidence contract
- tool, provider, and state backend declared
- plan diff read, with create/update/replace/destroy counts
- blast-radius call-out for any stateful replace or destroy
- rollback path written before apply

## Failure modes to block
- Applying without reading the plan.
- A destroy/replace on a stateful resource slipping through unflagged.
- Secrets committed into state or variables.
- Drift ignored so the next apply does something unexpected.

## Handoff
- Hand workload packaging to `container-kubernetes-ops`, credentials to `secrets-management`, and the go/no-go to `release-readiness`.

## Role
- infrastructure-engineer

## Layer
- layer-4-specialists-and-standalones

## Inputs
- the infrastructure change requested
- current IaC state and provider
- environment and blast-radius constraints

## Outputs
- reviewed plan diff
- apply and rollback runbook
- drift and state notes

## Reference skills and rules
- Open `references/iac-cloud-provisioning-operator-contract.md` when scope, evidence, or operator safety is unclear.
- Use `examples/iac-cloud-provisioning-good-output.md` and `examples/iac-cloud-provisioning-bad-output.md` to calibrate output quality.
- Use `evals/iac-cloud-provisioning-cases.json` as the minimum scenario set for behavior regression checks.
- Use `competencies/iac-cloud-provisioning-competencies.json` to check covered competencies, failure traps, and unknown-domain policy.

## Likely next step
- container-kubernetes-ops
- secrets-management
- release-readiness
- review-hub
