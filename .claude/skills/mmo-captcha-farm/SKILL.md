---
name: mmo-captcha-farm
description: "Use ONLY after antibot-challenge-solving has classified the challenge as solver-API addressable and chosen to route to a paid solver. Operates the solver pool: multi-service keys, balance + ban health, cost tracking, failover between 2captcha / CapMonster / AntiCaptcha / DeathByCaptcha. Does NOT classify challenges or decide the strategy."
allowed-tools: ["Read", "Write", "Edit", "Bash"]
---

# Mission
Keep solver throughput high and cost bounded across a key pool with failover. Downstream automation submits challenge payloads and gets tokens back.

## Scope boundary (do not violate)
- IN scope: key health check, submit, poll result, failover, balance watch, cost ledger.
- OUT of scope: deciding WHAT challenge needs solving and HOW -> antibot-challenge-solving.
- OUT of scope: browser-side injection of the solved token into the page -> caller (fleet / automation).

## Pre-flight (refuse the run if any missing)
1. Upstream decision record from antibot-challenge-solving naming solver-API as chosen strategy.
2. At least one API key per preferred service, each with positive balance.
3. Hourly budget cap set (numeric).
4. Expected rate (solves/hour) set.

## Solve loop (per request)
1. CHECK budget guard: hourly_spent + estimated_cost <= budget -> else refuse and signal upstream.
2. SELECT key: head of preferred list with (balance > 2x avg cost) AND (ban_state == clean) AND (rate_limit_free).
3. SUBMIT payload to service with timeout.
4. POLL until result or max_wait.
5. ON failure codes (ban, rate_limit, insufficient_balance): mark key, drop to next service, retry.
6. LOG cost, latency, service, verdict to ledger.
7. RETURN token or failure reason to caller.

## Key health states
- clean: usable
- low_balance: below threshold, warn, still usable
- rate_limited: temporary skip for N seconds
- banned: removed from rotation until operator confirms

## Failure modes to self-check
- You ran without an upstream classify record -> wrong order, route to antibot-challenge-solving.
- You kept solving after budget cap -> budget violation, stop.
- You hardcoded an API key -> delete, use secrets-management.
- You tried to solve a challenge the service does not support -> fail-fast, do not burn balance.

## Role
- captcha-solver-ops

## Layer
- layer-4-specialists-and-standalones

## Inputs
- strategy decision from antibot-challenge-solving: {challenge_type, chosen_strategy: solver-api, service_preference_order}
- API keys per service in secrets-management
- budget: max cost per hour, max cost per 1000 solves
- rate target: solves/hour expected

## Outputs
- solver pool status: per-key balance, ban state, solves/hour, cost/solve
- failover log with reason codes
- cost report vs budget
- solver output stream to caller (consumer is the automation that needed the token)

## Reference skills and rules
- This skill is a SOLVER FARM. It does not decide IF solver-API is the right strategy; antibot-challenge-solving decides that first. If the upstream decision is reverse-JS or browser-based, STOP and do not run.
- Every solve must log cost and latency; budget guard refuses submission once hourly budget is spent.
- Key rotation triggers: ban detected, balance below threshold, 3 consecutive rate-limit errors.
- Service rates are market data and drift; keep the matrix in references, not hardcoded in the body.
- Open `references/mmo-captcha-farm-operator-contract.md` when scope, evidence, or operator safety is unclear.
- Use `examples/mmo-captcha-farm-good-output.md` and `examples/mmo-captcha-farm-bad-output.md` to calibrate output quality.
- Use `evals/mmo-captcha-farm-cases.json` as the minimum scenario set for behavior regression checks.
- Use `competencies/mmo-captcha-farm-competencies.json` to check covered competencies, failure traps, and unknown-domain policy.

## Likely next step
- antibot-challenge-solving
- mmo-browser-fleet-automation
- policy-guard
