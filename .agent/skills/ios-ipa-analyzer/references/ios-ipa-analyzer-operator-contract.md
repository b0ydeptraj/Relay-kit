# ios-ipa-analyzer operator contract

## Scope
`ios-ipa-analyzer` is a layer-4 reverse-engineering specialist. Use when analyzing iOS IPA files for reverse engineering, security research, or app analysis. Extract app structure, binary analysis, plist inspection, framework inventory, and entitlements from .ipa archives. Works on non-jailbroken device for static analysis.

Enter it only for work that matches that scope; route anything broader back through `reverse-hub` or `workflow-router` so the lane keeps a single owner.

## Authorization
This specialist runs only against artifacts and targets the operator is authorized to analyze or test. When ownership or authorization is unclear, fail closed and hand the decision to `reverse-hub` before any action that changes state outside the workspace.

## Evidence rules
- Anchor every conclusion to a concrete file, offset, command, or captured output, not to a guess from a name.
- Separate what was observed from what was inferred, and name what is still unknown.
- Report a search that found nothing as bounded to what it covered, never as proof of absence.
- Do not claim a result is confirmed without the command output, log, or artifact that proves it.

## Hold conditions
Hold and route back when the only basis for a claim is a filename or symbol, when a capture was truncated, or when the lane would act outside the authorized target.

## Exit
End with the concrete finding, the evidence behind it, the residual unknowns, and the next skill (`reverse-hub`, `workflow-router`, or a sibling specialist) that should continue.
