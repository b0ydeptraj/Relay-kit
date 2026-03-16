# investigation-notes

> Path: `.ai-kit/contracts/investigation-notes.md`
> Purpose: Preserve debugging evidence, hypotheses, and findings before a fix or closure decision.
> Used by: debug-hub, root-cause-debugging, fix-hub, review-hub

## Investigation summary
A pressure/debug check was performed during verification by trying to use detached Windows shell startup patterns for the local server. The approach using `cmd /c start` produced Windows popup errors rather than stable automation.

## Evidence
- Popup error observed: `Windows cannot find '" "'.`
- The error came from the detached command form, not from Next.js app code.
- Standard smoke checks using a foreground server plus HTTP requests succeeded, so the app itself remained healthy.

## Root cause
The empty-title quoting pattern used by `cmd /c start "" /b ...` interacted badly with the desktop shell context and path quoting, causing Windows to interpret the empty title marker as a path lookup.

## Resolution
Do not use the detached `cmd /c start` pattern for this workspace verification. Use foreground server execution for smoke checks and Playwright/browser tooling for visual review.

## Follow-up
If later automation needs detached servers on Windows, add a dedicated script rather than composing the command inline.
