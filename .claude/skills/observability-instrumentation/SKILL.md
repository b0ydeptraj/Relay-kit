---
name: observability-instrumentation
description: Use when a service needs structured logging, metrics, distributed tracing, health checks, or SLO-backed alerting so failures are diagnosable in production.
allowed-tools: ["Read", "Write", "Edit", "Grep", "Glob", "Bash"]
---

# Mission
Make a service diagnosable in production by instrumenting logs, metrics, traces, and alerts against explicit failure questions, not vanity dashboards.

## Mandatory scope
1. Name the top failure questions the instrumentation must answer (latency, error rate, saturation, a specific bug class).
2. Structured logging: correlation/request id, level discipline, no secrets/PII in logs.
3. Metrics: RED (rate, errors, duration) for request paths and USE for resources; name and label cardinality budget.
4. Tracing: span boundaries at service and external-call edges, propagation of trace context.
5. SLOs and alerts: define SLI, target, and alert that pages on symptom (burn rate) not on cause noise.

## Evidence contract
- each signal maps to a named failure question it answers
- log/metric/trace field list with a no-PII confirmation
- at least one SLI + SLO + alert rule written
- cardinality budget stated for metric labels

## Role
- observability-specialist

## Layer
- layer-4-specialists-and-standalones

## Inputs
- service code / handlers
- existing logging or metrics setup
- incident or failure context if present

## Outputs
- .relay-kit/references/observability.md
- instrumentation code changes
- SLO and alert definitions

## Reference skills and rules
- Instrument to answer a failure question, not to collect everything.
- Never log secrets or PII; redact at the boundary.
- Watch label cardinality — unbounded labels break the metrics backend.
- Alert on user-visible symptoms; keep cause-level signals for debugging.
- Open `references/observability-instrumentation-operator-contract.md` when scope, evidence, or operator safety is unclear.
- Use `examples/observability-instrumentation-good-output.md` and `examples/observability-instrumentation-bad-output.md` to calibrate output quality.
- Use `evals/observability-instrumentation-cases.json` as the minimum scenario set for behavior regression checks.
- Use `competencies/observability-instrumentation-competencies.json` to check covered competencies, failure traps, and unknown-domain policy.

## Likely next step
- release-readiness
- incident-response
- performance-optimization
- runtime-doctor
