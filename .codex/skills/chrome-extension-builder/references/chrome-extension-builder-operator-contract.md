# chrome-extension-builder Operator Contract

Primary role: chrome-extension-architect
Layer: layer-4-specialists-and-standalones
Battle family: chrome-extension-mv3-automation

Use this skill when developing, refactoring, hardening, or auditing Chromium-based extensions (Manifest V3) for automation, scraping, or in-page security tooling.

## Concrete Battle Profile

- Repo profile: Chromium Manifest V3 extension repository with service worker, content scripts, popup, iframe injectors, and automated tests.
- First files to inspect: `manifest.json`, `background.js`, `content.js`, `popup.html`, `tests/`
- Symbols or named surfaces to confirm: `chrome.runtime.sendMessage`, `chrome.storage`, `MutationObserver`, `AbortController`, `postMessage`
- Evidence terms that should appear in a strong answer: Manifest V3, Service Worker lifecycle, CSP proxying, MutationObserver, isTrusted emulation, checkpoint recovery

## Working Loop

1. Restate the user task as a verifiable extension architecture requirement.
2. Check `manifest.json` permissions and script injection boundaries before recommending DOM or network logic.
3. Enforce `AbortController` cancellation and MutationObserver waiting for all in-page interactions.
4. Route cross-origin or external API traffic through the background worker to satisfy host CSP.
5. Provide automated test proof with zero-dependency `node:test` runners.

## Failure Modes To Block

- Using deprecated Manifest V2 patterns (`background.scripts` array, `webRequestBlocking`).
- Using busy-polling loops (`setInterval` every 200ms) that thrash multi-tab fleet CPU.
- Leaking global variables onto the target page's `window` object.
- Blind `time.sleep()` without `AbortSignal` cancellation tokens.
- Claiming an extension works without headless or unit test verification.
- Querying single-host URLs when handling SSO platforms (e.g. exporting YouTube without Google cookies).
- Passing leading dots in `chrome.cookies.set` `domain` parameter or ignoring `hostOnly` / `__Host-` specs.
- Performing unbounded cursor sweeps on IndexedDB without store filtering, causing OOM crashes on real user profiles with gigabytes of message history.
- Dumping multi-megabyte JSON strings directly into extension popup `<textarea>` elements without memory caching or payload size limits.
