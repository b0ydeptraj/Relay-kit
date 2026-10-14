---
name: reverse-hub
description: "Use when a claim depends on a shipped binary or package, a decompilation, passive runtime evidence, or behavior the available source does not establish. Route reverse-engineering across native, managed, Electron/JavaScript, mobile, firmware, browser, and network-capture targets, pick the right specialist, and keep every conclusion anchored to evidence and stated limitations."
---

# Mission
Turn a shipped artifact or an observed runtime into evidence-anchored findings, not plausible-sounding guesses about code you never read.

## When not to use
Do not enter reverse-hub for ordinary analysis of a source repository you already have. If the question is answerable from readable source, route to `scout-hub`. reverse-hub is for shipped binaries, decompilation, passive runtime evidence, or behavior the available source cannot establish.

## Target routing
Pick the first specialist from the target the user actually supplies. Never pick an example target on the user's behalf; if the target is a vague "my app", ask which artifact first.
1. Native binary (PE/ELF/Mach-O), packer, protection, or layout question -> `binary-reverse-methodology`.
2. Suspicious or unknown sample, IOC extraction, or behavioral mapping -> `malware-analysis-workflows`.
3. Android (APK/XAPK/split), iOS (IPA), Flutter, or other mobile native -> `mobile-app-reverse`.
4. Electron/JavaScript (ASAR or extracted tree), WASM, obfuscated web JS, or client-side signing/crypto -> `frontend-crypto-reverse`; the body-level specialists `electron-app-analyzer`, `javascript-deobfuscator`, and `java-decompiler`/`dotnet-decompiler` cover managed and packaged variants when installed.
5. Signature match or detectability question on a produced artifact -> `binary-stealth-obfuscation`.
6. Network capture (PCAP/HAR/SAZ), protocol, or C2 traffic shape -> `network-stealth-c2`; use `browser-inspector` for live browser-side console/network evidence.
7. On-chain, wallet, or smart-contract reversing -> `mmo-onchain-security-audit` before any transaction-shaped action.
8. Screenshots, crash images, or media artifacts that carry the evidence -> `multimodal-evidence`.

## Investigation workflow
1. Turn the request into a checklist of questions and the evidence type each one needs.
2. Reuse prior session state, artifact identity, and retained evidence via `memory-search` before re-running analysis.
3. Start with the smallest useful overview, then follow each question from entry point to result; do not rerun an identical analysis without a changed input or a resolved blocker.
4. Parse packaged resources and config with format-aware tools, not by inferring from filenames.
5. Corroborate each conclusion with the evidence type it requires; reach for runtime observation only when static evidence cannot answer the question, and plan any runtime capture as bounded and controlled before anything runs.
6. Use `problem-solving` for competing hypotheses and `sequential-thinking` for ordered probes; split independent questions across lanes through `handoff-context` when workers are available.

## Evidence contract
- Maintain a finding ledger in `investigation-notes.md` linking each conclusion to an evidence id, confidence, the search boundary, and the remaining unknowns.
- Every finding separates observations, inferences, and unknowns; cite the evidence, not a vibe.
- Never describe static analysis as having observed execution; keep runtime actions scoped to the declared target and lifecycle.
- Report a bounded negative search as bounded, never as proof of absence.
- Before finishing, mark each question answered, partially answered, or unresolved, and run `evidence-before-completion` before any "confirmed" claim.

## Failure modes
Hold when the lane is guessing behavior from names, treating a truncated preview as complete, claiming runtime behavior from static reads, or declaring a feature absent after only a bounded search. Route back to `debug-hub` when the target is actually a reproducible local bug, and to `review-hub` when findings must become a verdict.

## Role
- reverse-engineering-hub

## Layer
- layer-2-workflow-hubs

## Inputs
- target artifact or runtime handle (binary, package, ASAR, APK/IPA, firmware image, capture, URL)
- the exact question the claim depends on
- .relay-kit/state/workflow-state.md
- prior investigation-notes or evidence if present

## Outputs
- .relay-kit/contracts/investigation-notes.md with a finding ledger
- answered/partial/unresolved verdict per question
- handoff to a reverse specialist or back to debug-hub/fix-hub

## Reference skills and rules
- Skip reverse-hub for ordinary source-repository architecture analysis; use scout-hub and the normal read-first tools when the source already answers the question.
- Prefer static evidence; use runtime observation only when static analysis cannot answer the open question.
- Separate observations, inferences, and unknowns in every finding; never describe static analysis as having observed execution.
- A bounded negative search is reported as bounded, not as proof of absence.
- Route on-chain or wallet-adjacent reversing through `mmo-onchain-security-audit` before any transaction-shaped action.
- Open `references/reverse-hub-operator-contract.md` when scope, evidence, or operator safety is unclear.
- Use `examples/reverse-hub-good-output.md` and `examples/reverse-hub-bad-output.md` to calibrate output quality.
- Use `evals/reverse-hub-cases.json` as the minimum scenario set for behavior regression checks.
- Use `competencies/reverse-hub-competencies.json` to check covered competencies, failure traps, and unknown-domain policy.

## Likely next step
- binary-reverse-methodology
- malware-analysis-workflows
- mobile-app-reverse
- frontend-crypto-reverse
- binary-stealth-obfuscation
- network-stealth-c2
- mmo-onchain-security-audit
- multimodal-evidence
- browser-inspector
- memory-search
- problem-solving
- sequential-thinking
- evidence-before-completion
- runtime-doctor
- token-economy
- handoff-context
- debug-hub
- review-hub
- workflow-router
- android-apk-pentester
- anti-debugging-techniques
- binary-identifier
- binary-patcher
- binary-protection-bypass
- dotnet-decompiler
- dotnet-keygen
- dotnet-patcher
- electron-app-analyzer
- electron-builder-repacker
- electron-builder-unpacker
- flutter-app-reverser
- frida-hooker
- go-binary-reverser
- hardware-assisted-re
- ida-nuitka-reconstructor
- ios-ipa-analyzer
- java-decompiler
- javascript-deobfuscator
- license-robustness-audit
- master-unlock
- memory-dumper
- nuitka-decryptor
- pyinstaller-unpacker
- rust-binary-analyzer
- ssl-pinning-bypass
- symbolic-execution-tools
- tauri-unpacker
- vm-and-bytecode-reverse
- writerpro-pentest
