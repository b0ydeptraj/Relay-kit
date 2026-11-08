---
name: mmo-content-factory
description: "PIPELINE LAYER. Use when a multi-step content run needs to be orchestrated: brief -> N variants (via `mmo-llm-automation`) -> media/repurpose -> per-platform format -> schedule -> distribution. Does NOT generate text itself (that is `mmo-llm-automation`), post to platforms (that is `mmo-social-marketing-automation`), or run media transforms (that is `media-tooling`)."
allowed-tools: ["Read", "Write", "Edit"]
---

# Mission
Orchestrate the multi-step content run and hand each step to the right downstream skill. Keep variance, media, formatting, and schedule as separate traceable stages.

## Scope boundary (do not violate)
- IN scope: pipeline plan, batch bookkeeping, reject bookkeeping, schedule, handoff to publisher.
- OUT of scope: LLM generation -> `mmo-llm-automation`.
- OUT of scope: media repurposing (video/image transforms) -> `media-tooling`.
- OUT of scope: API posting to TikTok/FB/IG -> `mmo-social-marketing-automation`.
- OUT of scope: dedupe + rights check for reposts -> `mmo-reup-automation`.

## Stage graph (reference)
```
brief
  -> [mmo-llm-automation] variants batch (N, scored)
  -> [media-tooling] media per variant
  -> [per-platform format] payload per platform
  -> [schedule] windows per platform (quota-aware)
  -> [mmo-social-marketing-automation] publish
  -> audit row per item
```

## Audit row format (one per published item)
```
- brief_id: <id>
  variant_id: <id>
  platform: <name>
  schedule_window: <ISO>
  publish_status: queued | published | rejected
  reject_reason: <code or empty>
  variance_score: <float>
  cost_text: <usd>
  cost_media: <usd>
```

## Failure modes to self-check
- You generated text inline -> wrong layer, delegate to mmo-llm-automation.
- You called the TikTok API -> wrong layer, delegate to mmo-social-marketing-automation.
- You scheduled beyond platform quota -> quota breach, reduce schedule.
- You published variants with variance_score below threshold -> Sybil risk, re-batch.

## Role
- mmo-content-pipeline

## Layer
- layer-4-specialists-and-standalones

## Inputs
- campaign brief with target platforms and schedule windows
- asset inventory: source videos, images, templates
- per-platform policy and quota from mmo-social-marketing-automation
- quality gate rubric and reject reasons taxonomy

## Outputs
- pipeline plan: step graph with owning skill per step
- variant batch: N generations with variance scores (from mmo-llm-automation)
- repurposed media batch (from media-tooling)
- per-platform formatted payload queue, each tied to a schedule window
- handoff to mmo-social-marketing-automation for publishing

## Reference skills and rules
- This skill ORCHESTRATES. It does not generate text (mmo-llm-automation), transform media (media-tooling), or post (mmo-social-marketing-automation).
- Every text variant must carry its mmo-llm-automation variance_score. Reject the batch if variance is below threshold.
- Every published item has an audit row: brief_id, variant_id, platform, schedule_window, publish_status, reject_reason.
- Platform rate limits are honored via mmo-social-marketing-automation quota; this pipeline must not schedule beyond quota.
- Open `references/mmo-content-factory-operator-contract.md` when scope, evidence, or operator safety is unclear.
- Use `examples/mmo-content-factory-good-output.md` and `examples/mmo-content-factory-bad-output.md` to calibrate output quality.
- Use `evals/mmo-content-factory-cases.json` as the minimum scenario set for behavior regression checks.
- Use `competencies/mmo-content-factory-competencies.json` to check covered competencies, failure traps, and unknown-domain policy.

## Likely next step
- mmo-llm-automation
- media-tooling
- mmo-social-marketing-automation
- mmo-reup-automation
- policy-guard
