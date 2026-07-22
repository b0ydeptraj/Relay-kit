---
name: advanced-python-engineering
description: Use when Python work requires advanced patterns: async I/O, ctypes/cffi interop, metaprogramming, C extension modules, performance optimization, or large-scale automation architecture.
allowed-tools: ["Read", "Write", "Edit", "Grep", "Glob", "Bash"]
---

# Mission
Implement robust, performant, and idiomatic Python for automation, interop, or large-scale scripting with explicit architecture and error discipline.

## Mandatory scope
1. Declare Python version and async model (asyncio/trio/anyio or sync).
2. For ctypes/cffi: document C signature, calling convention, and error propagation.
3. For async: identify event loop, cancellation points, and timeout strategy.
4. For metaprogramming: document __dunder__ contracts and descriptor protocol usage.
5. Name external dependencies with version pins.
6. Include error hierarchy: which exceptions are recoverable vs fatal.

## Evidence contract
- Python version and async model declared
- ctypes signatures documented with C source
- Error hierarchy written explicitly
- Dependency list with versions

## Role
- python-specialist

## Layer
- layer-4-specialists-and-standalones

## Inputs
- story or tech-spec
- Python version target
- existing codebase if present

## Outputs
- Python implementation
- dependency list
- error handling docs

## Reference skills and rules
- Never mix async and sync I/O in the same call chain without explicit bridging.
- Document ctypes signatures with the original C header.
- Use type hints for all public interfaces.
- Pin dependency versions — floating requirements cause reproducibility failures.
- Open `references/advanced-python-engineering-operator-contract.md` when scope, evidence, or operator safety is unclear.
- Use `examples/advanced-python-engineering-good-output.md` and `examples/advanced-python-engineering-bad-output.md` to calibrate output quality.
- Use `evals/advanced-python-engineering-cases.json` as the minimum scenario set for behavior regression checks.
- Use `competencies/advanced-python-engineering-competencies.json` to check covered competencies, failure traps, and unknown-domain policy.

## Likely next step
- advanced-python-engineering
- mmo-llm-automation
- mmo-http-api-automation
- antibot-challenge-solving
- terminal-operator-ui
- field-journal-evolution
