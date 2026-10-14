# Checkpoint Recovery & State Machine Guide

This guide establishes the pattern for state resilience across unexpected page reloads, SPA route navigations, and process interruptions in Chrome Extension automation.

---

## 1. The Interruption Problem

In real-world browser runs:
* Single Page Applications (SPAs) push and pop history states.
* Session timeouts cause full-page redirects to login portals.
* Users or network flakiness cause accidental tab refreshes.

If an automation extension keeps all progress in volatile JavaScript variables, any page unload wipes execution state, causing the script to restart from Step 0 and duplicate work or trigger rate limits.

---

## 2. Checkpoint State Architecture

The extension separates configuration from execution state.

### State Schema in `chrome.storage.local`:
```json
{
  "activeRun": {
    "runId": "run_1728000000",
    "tabId": 12,
    "status": "running",
    "courseOrTask": "task-alpha",
    "currentStepIndex": 4,
    "completedSteps": [0, 1, 2, 3],
    "lastCheckpointUrl": "https://example.com/step-4",
    "updatedAt": 1728000045
  }
}
```

---

## 3. Resume-On-Arrival Protocol

Every content script bootstraps using the following checkpoint verification:

```javascript
async function initOrResumeRunner() {
    const data = await chrome.storage.local.get(['activeRun']);
    const run = data.activeRun;

    if (!run || run.status !== 'running') {
        return; // Standby mode
    }

    // Verify current URL matches expectation
    const currentUrl = location.href;
    const currentStep = run.steps[run.currentStepIndex];

    if (!currentStep) {
        await finishRun(run);
        return;
    }

    // Step dispatch based on checkpoint
    console.log(`[ExtensionRunner] Resuming step ${run.currentStepIndex}: ${currentStep.name}`);
    await executeStep(currentStep, run);
}

document.addEventListener('DOMContentLoaded', initOrResumeRunner);
```

### Critical Rules:
1. **Atomic Step Commit**: Only increment `currentStepIndex` and commit to storage AFTER the step's verification assertion passes.
2. **Duplicate Prevention**: If a step already recorded a success marker in storage, never execute its DOM click again.
3. **Graceful Skip Ledger**: If a non-critical step times out, record `{ stepIndex, status: 'skipped', reason: 'timeout' }` so the report indicates the skip without breaking the sequence.
