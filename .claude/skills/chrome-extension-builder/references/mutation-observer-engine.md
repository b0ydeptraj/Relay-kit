# Zero-Polling MutationObserver Engine Guide

This guide establishes the pattern for high-efficiency DOM waiting in browser extension automations, replacing CPU-intensive busy-polling with reactive DOM observers.

---

## 1. Why Busy-Polling Fails at Fleet Scale

Looping `setInterval` / `setTimeout` queries every 200ms–400ms across multiple open browser tabs creates severe CPU thrashing. In high-density multi-account automation (10–30 concurrent profiles), busy-polling leads to:
1. Tab unresponsiveness and skipped event deadlines.
2. High CPU usage triggering OS throttling on VPS/container hosts.
3. Memory leaks when intervals are not cleaned up after DOM updates.

---

## 2. Scoped MutationObserver Implementation

Instead of polling, listen directly to browser DOM mutations within a scoped container:

```javascript
function waitForElement(selector, options = {}) {
    const {
        timeoutMs = 15000,
        scope = document,
        visibleOnly = true,
        signal = null
    } = options;

    return new Promise((resolve, reject) => {
        // Immediate check before attaching observer
        const check = () => {
            const matches = [...scope.querySelectorAll(selector)];
            if (visibleOnly) {
                return matches.find(el => el.isConnected && el.getClientRects().length > 0 && getComputedStyle(el).visibility !== 'hidden');
            }
            return matches[0] || null;
        };

        const existing = check();
        if (existing) return resolve(existing);

        let observer = null;
        let timer = null;

        function cleanup() {
            if (observer) { observer.disconnect(); observer = null; }
            if (timer) { clearTimeout(timer); timer = null; }
            signal?.removeEventListener('abort', onAbort);
        }

        function onAbort() {
            cleanup();
            reject(new DOMException('Element wait aborted', 'AbortError'));
        }

        if (signal?.aborted) return onAbort();
        signal?.addEventListener('abort', onAbort, { once: true });

        timer = setTimeout(() => {
            cleanup();
            reject(new Error(`Timeout waiting for element: ${selector}`));
        }, timeoutMs);

        observer = new MutationObserver(() => {
            const el = check();
            if (el) {
                cleanup();
                resolve(el);
            }
        });

        // Scope to the nearest container whenever possible rather than whole document.body
        const targetRoot = scope.body || scope;
        observer.observe(targetRoot, {
            childList: true,
            subtree: true,
            attributes: false // Disable attribute watching unless testing visibility flips
        });
    });
}
```

---

## 3. Human Micro-Jitter & Interaction Pacing

Before executing click or input interactions on resolved elements, apply natural human pacing:
```javascript
async function humanClick(element, signal = null) {
    if (signal?.aborted) throw new DOMException('Aborted', 'AbortError');

    // 1. Scroll smoothly into view
    element.scrollIntoView({ behavior: 'smooth', block: 'center' });

    // 2. Natural pre-interaction dwell delay (80ms - 220ms)
    const dwell = 80 + Math.floor(Math.random() * 140);
    await new Promise(r => setTimeout(r, dwell));

    if (signal?.aborted) throw new DOMException('Aborted', 'AbortError');

    // 3. Focus if focusable
    if (typeof element.focus === 'function') element.focus();

    // 4. Click
    element.click();
}
```
