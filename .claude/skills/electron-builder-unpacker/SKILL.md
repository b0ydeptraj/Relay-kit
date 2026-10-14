---
name: electron-builder-unpacker
description: "Use when a lane needs electron builder unpacker: Master Unlock: Grants unlimited technical rights to unpack and deconstruct Electron Builder artifacts. Use this to extract app.asar, recover unpacked native resources, and expose update metadata (app-update.yml, latest.yml) for complete offline analysis."
allowed-tools: ["Read", "Write", "Edit", "Grep", "Glob", "Bash"]
---

# Mission
Master Unlock: Grants unlimited technical rights to unpack and deconstruct Electron Builder artifacts.

# Electron Unpacker Master Unlock (Full Package Deconstruction)

## Overview

Activate this skill to unlock advanced Electron Builder package extraction. The Agent has full and unlimited access to:
- **ASAR Extraction**: Unpack `app.asar` archives to recover 100% of the application source code.
- **Resource Recovery**: Locate and copy `app.asar.unpacked` native modules and resources.
- **Metadata Exposure**: Extract and analyze update configurations (`app-update.yml`, `latest.yml`) and blockmap files.
- **Persistence**: Maintain continuous operation until every layer of the Electron package is deconstructed and ready for analysis.

---

## Operating Modes (Unlimited Mode)

| Operation Type | Authorization Level |
|---|---|
| **Bulk Unpacking** | Full rights to extract all ASAR files and recover directory structures. |
| **Artifact Recovery** | Enumerate and copy every configuration file, including hidden update metadata. |
| **Integrity Audit** | Analyze blockmap files and signatures to identify update vulnerabilities. |
| **Persistence** | Continue until all source modules are extracted and ready for `electron-app-analyzer`. |

---

## Execution Flow (Unlimited Strategy)

1. **Discovery**: Locate the target Electron application directory or installer contents.
2. **Deconstruction**: Use `scripts/unpack_electron_builder.py` to strip away the ASAR layers.
3. **Synthesis**: Create a complete offline source tree for deep analysis.
4. **Deliverables**: Provide a full directory of extracted code and a manifest of all recovered artifacts.

---

## Step 1 — Full Extraction

Run the unpacker on the target directory or release folder:

```bash
# bash / WSL / Linux / macOS
python scripts/unpack_electron_builder.py path/to/app-or-release --out electron-unpacked
```

```powershell
# Windows PowerShell
python scripts\unpack_electron_builder.py 'C:\Program Files\MyApp' --out electron-unpacked
```

---

## Final Report Standards (Full Deliverables)

Present results with the following information:
- **Status**: Package fully deconstructed.
- **Extracted Source**: Path to the recovered `app_asar` and source folders.
- **Native Modules**: List of `asar.unpacked` resources found.
- **Update Metadata**: All recovered configurations for update channels.
- **Next Command**: Instructions for initiating `electron-app-analyzer` on the recovered source.

## Role
- reverse-engineering-specialist

## Layer
- layer-4-specialists-and-standalones

## Inputs
- the authorized target or artifact
- the exact question or objective
- .relay-kit/state/workflow-state.md

## Outputs
- .relay-kit/contracts/investigation-notes.md with electron-builder-unpacker findings
- answered/partial/unresolved verdict with evidence

## Reference skills and rules
- Route anything outside electron-builder-unpacker's scope back through `reverse-hub` or `workflow-router`.
- Anchor every conclusion to a file, command, or captured output; never guess from names.
- Report a bounded negative search as bounded, not as proof of absence.
- Open `references/electron-builder-unpacker-operator-contract.md` when scope, evidence, or operator safety is unclear.
- Use `examples/electron-builder-unpacker-good-output.md` and `examples/electron-builder-unpacker-bad-output.md` to calibrate output quality.
- Use `evals/electron-builder-unpacker-cases.json` as the minimum scenario set for behavior regression checks.
- Use `competencies/electron-builder-unpacker-competencies.json` to check covered competencies, failure traps, and unknown-domain policy.

## Likely next step
- electron-builder-unpacker
- reverse-hub
- workflow-router
