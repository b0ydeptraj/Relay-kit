---
name: offensive-domain-unlock
description: "Use ONCE per lane, at lane start, when work is authorized offensive/RE/MMO research (self-owned, licensed, lab, CTF, or written-scope pentest). Produces a one-file authorization record that downstream skills (master-unlock, binary-patcher, kernel-driver-evasion, mmo-*) require as a pre-flight. Does not perform research — only records scope, authority, target, and out-of-scope list."
allowed-tools: ["Read", "Write", "Grep", "Glob"]
---

# Mission
Open an offensive/RE/MMO research lane by writing exactly one authorization record. Downstream skills read this file and refuse if the target they are asked to touch is not named here.

## Scope boundary (do not violate)
- IN scope: collecting authority basis, target identifiers, scope, out-of-scope, and writing the record.
- OUT of scope: doing any technical work (dump, decompile, patch, inject, automate). Those belong to downstream skills that gate on this record.
- OUT of scope: granting authorization for third-party production systems the operator cannot prove they own or are contracted to test. Refuse and route to the operator instead.
- OUT of scope: "soften safety wording" / "unlock refusal" prompt-engineering. This skill does not do that. It records a contract.

## Pre-flight (refuse the grant if any missing or unverifiable)
1. Authority basis named: `self-owned` | `licensed` | `lab` | `CTF <event>` | `written-pentest <engagement-id>`. "Research" alone is insufficient.
2. At least one target identifier (binary hash or path; domain/host; platform account owned by operator). Public web with no identifier → refuse.
3. Operator identity (from `git config user.email` or stated engagement).
4. Out-of-scope list is non-empty. "Nothing is out of scope" → refuse.
5. Intended artifact is a defensive or owner-facing output (hardening report, detection rule, owner's source recovery, personal game mod). "Public bypass tool against vendor X" → refuse.

## Record format (write to `.relay-kit/state/offensive-authorization.md`)
```
# Offensive Authorization — <lane name>
- granted_at: <ISO timestamp>
- expires_at: <ISO timestamp, max 30 days>
- operator: <git email or engagement id>
- authority_basis: self-owned | licensed | lab | CTF:<event> | written-pentest:<id>
- targets:
  - <sha256 or path or domain or account id>
- out_of_scope:
  - <explicit item>
- intended_artifact: <one sentence>
- cleared_downstream_skills:
  - <skill names>
```

## Verdict format (return to caller)
```
VERDICT: granted | refused | incomplete
REASON: <one sentence>
TARGETS_CLEARED: <list>
NEXT: <downstream skill name> — <what to do first>
```

## Failure modes to self-check
- You produced an authorization record for a target the operator did not name ⇒ invalid, revise.
- You wrote "unlimited" or "bypass safety" ⇒ delete; this is a contract, not a framing.
- You granted authority against vendor production systems without a written engagement ⇒ refuse.
- You skipped the expiry field ⇒ invalid; downstream skills reject records without expiry.
- You tried to do the research work in this skill ⇒ wrong skill, write the record and hand off.

## Role
- offensive-security-authorization

## Layer
- layer-4-specialists-and-standalones

## Inputs
- authority basis: self-owned | licensed | lab | CTF | written pentest contract
- target identifiers: path/hash of binary OR domain/host OR platform account (as applicable)
- operator identity (git user, engagement id, or lab name)
- explicit out-of-scope list: what the operator is NOT authorized to touch
- intended research artifacts: what will be produced (audit report, source recovery for owner, detection rules, ...)

## Outputs
- .relay-kit/state/offensive-authorization.md with: target(s), authority, operator, scope, out-of-scope, timestamp, expiry
- verdict: granted / refused / incomplete
- next-skill routing: names the downstream skill(s) the lane is now cleared for

## Reference skills and rules
- This skill is an AUTHORIZATION GATE. It does not grant new model capability — it records operator scope so downstream skills have a verifiable pre-flight.
- Refuse the grant if the request is against third-party production systems without written scope, against non-consenting individuals, or against platforms the operator does not own/license.
- The record is lane-local (one authorization per lane). Do not reuse an old record for a new target.
- Downstream skills (master-unlock, binary-patcher, kernel-driver-evasion, mmo-anti-detection-browser, etc.) MUST open this file and refuse to run if the target in the request is not named here.
- This is not a jailbreak framing. Removing wording like "unlimited rights" and "bypass all safety" is intentional: the record is a contract, not a model override.
- Open `references/offensive-domain-unlock-operator-contract.md` when scope, evidence, or operator safety is unclear.
- Use `examples/offensive-domain-unlock-good-output.md` and `examples/offensive-domain-unlock-bad-output.md` to calibrate output quality.
- Use `evals/offensive-domain-unlock-cases.json` as the minimum scenario set for behavior regression checks.
- Use `competencies/offensive-domain-unlock-competencies.json` to check covered competencies, failure traps, and unknown-domain policy.

## Likely next step
- master-unlock
- offensive-security-engagement
- reverse-hub
- mmo-authorization-gate
