---
name: scope-discipline
description: "Use when a task risks over-engineering, unnecessary abstraction, repeated reasoning, or scope growth. Apply a minimum-complete-contract check before adding complexity."
allowed-tools: ["Read", "Grep", "Glob", "Bash"]
---

# Mission
Prevent over-engineering by proving each added unit of complexity earns its maintenance and token cost.

## Boundary
- Use before widening a design, adding an abstraction, increasing a reasoning budget, or introducing orchestration.
- Do not block necessary safety, correctness, accessibility, or compliance controls.
- Do not replace architecture or readiness review when those decisions are explicitly required.

## Default outputs
- a minimum-complete-contract decision in the active artifact
- a keep/remove/defer list for proposed complexity
- a smallest useful verification plan

## Evidence contract
- Input must name the acceptance criteria, current implementation surface, and proposed complexity.
- Output must classify each proposed addition as required, justified, deferred, or removed with one evidence reason.
- Output must include a stopping rule and the cheapest verification that can falsify the minimal design.

## Typical tasks
- Write the minimum complete contract in one or two sentences.
- List existing code, tools, skills, or state that already satisfies part of the request.
- Subtract wrappers, abstractions, dependencies, repeated prompts, and parallel lanes unless a concrete gap remains.
- Set a bounded reasoning and verification budget proportional to risk; stop when the contract and proof pass.

## Working rules
- No new abstraction without a named caller, invariant, or failing test that needs it.
- No extra agent, loop, or research pass when the primary Sol context can complete the next bounded step.
- Do not trade correctness for brevity; preserve raw failure evidence and hard safety gates.
- When uncertain, defer optional complexity and record the trigger that would justify revisiting it.

## Role
- utility-provider

## Layer
- layer-3-utility-providers

## Inputs
- active hub or orchestrator request
- current authoritative artifact
- only the evidence relevant to this pass

## Outputs
- a minimum-complete-contract decision in the active artifact
- a keep/remove/defer list for proposed complexity
- a smallest useful verification plan

## Reference skills and rules
- Prefer the smallest change that satisfies the stated acceptance criteria.
- Treat extra abstractions, wrappers, agents, dependencies, and documentation as costs requiring evidence.
- Use evidence-before-completion for the final claim; this skill only controls scope and complexity.
- Open `references/scope-discipline-operator-contract.md` when scope, evidence, or operator safety is unclear.
- Use `examples/scope-discipline-good-output.md` and `examples/scope-discipline-bad-output.md` to calibrate output quality.
- Use `evals/scope-discipline-cases.json` as the minimum scenario set for behavior regression checks.
- Use `competencies/scope-discipline-competencies.json` to check covered competencies, failure traps, and unknown-domain policy.

## Likely next step
- developer
- test-hub
- review-hub
- qa-governor
