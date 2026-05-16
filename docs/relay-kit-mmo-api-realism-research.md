# Relay-kit MMO/API Realism Research

Status: public-source research note for MMO/API skill contracts.

This note is not a how-to for evasion, account abuse, CAPTCHA bypass, or platform rule circumvention. Relay-kit uses these sources to learn operator workflow shape, naming, data relationships, monitoring surfaces, and failure handling patterns for authorized automation systems.

## Public Sources Reviewed

| Source | Pattern internalized |
|---|---|
| GoLogin bulk actions docs | Profile list, checkbox selection, bulk action bar, folders, tags, proxy assignment, run/stop, clone/transfer, and caution before destructive actions. |
| GoLogin cloud browser proxy docs | Proxy is attached to a profile; proxy status should be checked before production automation starts. |
| AdsPower Local API article | Local API exposes account lookup, start/close browser, account search, and Selenium/Puppeteer automation integration. |
| Browserless session and Docker docs | Browser sessions need disconnect-vs-close semantics, reconnect TTL, concurrency limits, queue length, timeouts, persistent data, and metrics paths. |
| PinchTab README | Real browser automation tools model server, instance, profile, tab, bridge, dashboard, isolated profiles, stable refs, and token-efficient snapshots. |
| Steel Browser README | Browser automation infrastructure exposes session management, proxy support, extension support, request logging, session debug UI, and lifecycle cleanup. |
| Apify request queue docs | Scraping/automation jobs use persistent request queues, request ids, dedupe/unique keys, batch operations, reclaim, incremental runs, and datasets. |
| Crawlee session management docs | Session pools bind cookies/tokens/headers to sessions and filter blocked or non-working proxies instead of retrying blindly. |
| n8n executions and queue-mode docs | Real workflow tools distinguish manual vs production executions, active/inactive workflows, redacted execution data, main/webhook/worker roles, Redis queue, and execution ids. |
| BullMQ, Arena, and queue dashboards | Queue operators need waiting/active/delayed/failed/completed/stalled counts, rate-limit TTL, retry/backoff, stacktrace detail, permalinks, and one-click retry. |
| Scrapfly monitoring docs | API/scraping dashboards use filters for success, domain, method, status code, cost, origin, retries, duration, and error codes. |
| GADS device farm README | Mobile automation platforms split hub UI from providers, track devices, support remote control, Appium execution, and device/provider management. |

## Relay-kit Design Rules

- Realism beats presentation. MMO/API output must start from an operator workflow and data model, not a marketing dashboard.
- Dense tables beat hero layouts. The first screen should show inventory, queue state, health, filters, and actionable exceptions.
- Every bulk action needs dry-run, selected count, risk summary, and rollback or quarantine behavior.
- Every automation run needs a run id, owner, input scope, queue state, retry state, raw evidence pointer, and redacted sensitive fields.
- Profile/session systems must keep account, profile, proxy, session lease, cookies/tokens, and browser state as separate but linked entities.
- Browser and mobile systems must expose live debug evidence: screenshot/trace/log pointers, selector drift, timeout reason, crash or ANR marker, and manual takeover marker.
- Queue systems must expose waiting/active/delayed/failed/completed/stalled counts, rate-limit status, retry/backoff, dead-letter or quarantine, and safe replay controls.
- API systems must expose endpoint catalog, auth scope, request id, status code, duration, retry count, origin, cost, idempotency key, and redacted request/response detail.
- Low-code systems must expose node graph, execution list, manual vs production mode, active/inactive state, redacted node output, and error workflow.
- Social/reup systems must expose content source inventory, rights/attribution state, duplicate fingerprint, moderation queue, quota meter, publish window, and reject reason taxonomy.

## Safety Boundary

Relay-kit should learn product shape and operational discipline from the ecosystem, not evasion tactics. Generated systems should use authorized accounts, official APIs where available, published platform limits, redaction, dry-run, manual review for high-risk actions, and policy-guard escalation. Requests for CAPTCHA bypass, identity spoofing, credential theft, platform abuse, or hidden evasion must route to `policy-guard` and hold.
