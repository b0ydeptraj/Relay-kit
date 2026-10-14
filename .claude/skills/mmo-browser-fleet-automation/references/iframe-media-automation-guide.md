# Cross-Origin Iframe & Media Automation Engineering Guide

This guide establishes the architectural patterns and operator standards for interacting with embedded cross-origin iframes (YouTube, Vimeo, LMS quiz widgets, CAPTCHA frames) and HTML5 media players within Relay-kit browser fleet automation.

---

## 1. Cross-Origin Iframe PostMessage RPC Bridge

### Problem
Direct DOM access across origins is blocked by browser Same-Origin Policy (SOP). Using Chrome DevTools Protocol (CDP) to penetrate frames can trigger modern bot detection scripts (Cloudflare, Datadome, PerimeterX) that monitor CDP domains.

### Solution Pattern
Deploy an injectable content script into child frames (`all_frames: true` in Extension, or via `page.frame_locator().evaluate()`) that speaks a structured bidirectional `postMessage` protocol:

```javascript
// Protocol Message Shape
{
  type: 'FRAME_RPC_REQ',    // or 'FRAME_RPC_RES'
  session: 'session-id',     // Prevents stale worker overlap
  requestId: 'req_xyz123',   // Maps requests to response promises
  command: 'seek',           // Target action name
  data: { seconds: 120 }     // Command arguments
}
```

### Critical Implementation Rules:
1. **Origin Verification**: Explicitly check `event.origin` on both ends. Never accept wildcard `'*'` in production financial or authentication frames.
2. **Session Fencing**: When a tab reloads or a step restarts, increment session epoch so lingering in-flight iframe promises cannot corrupt the new state.
3. **Transient Error Handling**: Wrap `postMessage` cleanup in `try/catch` or `finally` blocks to prevent origin mismatch errors from swallowing genuine step completion results.

---

## 2. Chromium Autoplay Policy Bypass & Fast-Forward Seeking

### Autoplay Restriction Bypass
Chromium blocks unmuted audio/video playback without prior user interaction (`NotAllowedError`).
* **Deterministic Fix**:
  ```javascript
  video.defaultMuted = true;
  video.muted = true;
  video.volume = 0;
  video.playsInline = true;
  ```
* **Simulated Overlay Click**: Before calling `video.play()`, locate and click visible thumbnail overlays (e.g. `button.ytp-large-play-button`, `.ytmCuedOverlayPlayButton`).

### Resilient Seeking with Element-Swap Recovery
When seeking large jumps or during end-of-video loops, modern players (such as YouTube's HTML5 engine) frequently swap out the `<video>` element or recreate decoder instances.
* **Algorithm**:
  1. Assign `video.currentTime = targetSeconds`.
  2. Poll on a 200–300ms cadence.
  3. In each iteration, re-query the active `<video>` element: if `currentElement !== cachedElement`, update reference and re-assert seek.
  4. Wait until `!video.seeking` and `Math.abs(video.currentTime - targetSeconds) <= tolerance`.

---

## 3. Bounded Step Execution & Deterministic Cancellation

### AbortController Signal Pipeline
Blind sleeps (`time.sleep()`, `setTimeout()`) leak background executions and produce flaky fleet runs when an operator pauses or cancels a session.
* **Standard**: Pass `AbortSignal` into every wait loop, delay timer, and cross-frame RPC call:
  ```javascript
  function delay(ms, signal) {
    if (signal?.aborted) throw new DOMException('Aborted', 'AbortError');
    return new Promise((resolve, reject) => {
      const timer = setTimeout(() => {
        signal?.removeEventListener('abort', onAbort);
        resolve();
      }, ms);
      const onAbort = () => {
        clearTimeout(timer);
        reject(new DOMException('Aborted', 'AbortError'));
      };
      signal?.addEventListener('abort', onAbort, { once: true });
    });
  }
  ```

### Step Categorization & Graceful Skip
* **Critical Steps (Fail-Stop)**: Navigation checkpoints, authentication gates, exam submissions. If a timeout occurs, stop the run and report the error immediately.
* **Non-Critical Steps (Bounded Skip)**: Secondary in-video quiz popups, non-mandatory ads/waiters, tab previews. Bound with a short deadline (e.g. 15s `STEP_TIMEOUT_MS`). If the deadline expires, log a console warning and gracefully skip to the next step without aborting the pipeline.

---

## 4. Chrome Extension Manifest V3 Service Worker Resilience

In Chrome Manifest V3, background service workers are terminated after ~30 seconds of inactivity.
* When waking, requests sent to `chrome.runtime.sendMessage` may fail with:
  `Could not establish connection. Receiving end does not exist` or `The message port closed before a response was received`.
* **Retry Strategy**: Detect these exact transient errors and retry 2 times with a 300ms exponential backoff. Do not retry real operational errors or cancelled contexts.
