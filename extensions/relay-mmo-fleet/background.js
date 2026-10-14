/**
 * background.js - RelayKit MMO Fleet Service Worker
 * 
 * Features:
 *   1. Cookie & Token Vault: Harvests cookies & session data for active tabs.
 *   2. CDP Debugger Engine: Emulates genuine event.isTrusted: true clicks and keystrokes.
 *   3. Off-page CSP Bypass Proxy: Sends telemetry/webhooks immune to host page CSP.
 *   4. Checkpoint State Machine: Coordinates task queues and tab resumption.
 */
'use strict';

// Helper: Extract eTLD+1 base domain
function getBaseDomain(hostname) {
    if (!hostname) return '';
    const parts = hostname.toLowerCase().split('.');
    if (parts.length <= 2) return hostname;
    const secondLast = parts[parts.length - 2];
    if (['com', 'co', 'edu', 'gov', 'org', 'net'].includes(secondLast) && parts.length >= 3) {
        return parts.slice(-3).join('.');
    }
    return parts.slice(-2).join('.');
}

// Known cross-domain SSO and auth ecosystem links
const SSO_ECOSYSTEMS = {
    'youtube.com': ['google.com'],
    'google.com': ['youtube.com'],
    'zalo.me': ['chat.zalo.me', 'id.zalo.me', 'wpa.chat.zalo.me'],
    'facebook.com': ['meta.com', 'messenger.com'],
    'messenger.com': ['facebook.com', 'meta.com'],
    'instagram.com': ['facebook.com', 'meta.com']
};

// 1. Cookie & Session Vault (Multi-Domain & Ecosystem Aware)
async function exportTabCookies(url, tabId) {
    if (!chrome.cookies) throw new Error('cookies API not available');
    const parsedUrl = new URL(url);
    const hostname = parsedUrl.hostname;
    const baseDomain = getBaseDomain(hostname);
    
    let storeId;
    if (typeof tabId === 'number' && chrome.cookies.getAllCookieStores) {
        try {
            const stores = await chrome.cookies.getAllCookieStores();
            const st = stores.find(s => s.tabIds.includes(tabId));
            if (st) storeId = st.id;
        } catch (_) {}
    }

    const domainTargets = new Set();
    domainTargets.add(hostname);
    if (baseDomain) domainTargets.add(baseDomain);
    
    for (const [key, related] of Object.entries(SSO_ECOSYSTEMS)) {
        if (hostname === key || hostname.endsWith('.' + key) || baseDomain === key) {
            for (const r of related) domainTargets.add(r);
        }
    }

    const cookieMap = new Map();

    // 1. Query exact URL
    try {
        const urlQuery = { url };
        if (storeId) urlQuery.storeId = storeId;
        const urlCookies = await chrome.cookies.getAll(urlQuery);
        for (const c of (urlCookies || [])) {
            const key = `${c.domain}|${c.path}|${c.name}`;
            cookieMap.set(key, c);
        }
    } catch (_) {}

    // 2. Query target domains and base domains
    for (const d of domainTargets) {
        try {
            const domQuery = { domain: d };
            if (storeId) domQuery.storeId = storeId;
            const domCookies = await chrome.cookies.getAll(domQuery);
            for (const c of (domCookies || [])) {
                const key = `${c.domain}|${c.path}|${c.name}`;
                cookieMap.set(key, c);
            }
        } catch (_) {}
    }

    const cookies = Array.from(cookieMap.values());
    
    // Netscape format
    const netscape = cookies.map(c => {
        const flag = (c.domain || '').startsWith('.') ? 'TRUE' : 'FALSE';
        const path = c.path || '/';
        const secure = c.secure ? 'TRUE' : 'FALSE';
        const expiry = c.expirationDate ? Math.round(c.expirationDate) : 0;
        return `${c.domain}\t${flag}\t${path}\t${secure}\t${expiry}\t${c.name}\t${c.value}`;
    }).join('\n');

    return {
        domain: baseDomain || hostname,
        hostname,
        total: cookies.length,
        cookies,
        netscape
    };
}

// 2. CDP Debugger Engine (isTrusted: true Event Dispatcher)
async function dispatchCdpClick(tabId, coords) {
    if (!chrome.debugger) {
        throw new Error('chrome.debugger API is not enabled. Request optional permissions.');
    }
    const target = { tabId };
    await chrome.debugger.attach(target, "1.3");
    try {
        const { x, y } = coords;
        // 1. Move to target
        await chrome.debugger.sendCommand(target, "Input.dispatchMouseEvent", {
            type: "mouseMoved", x, y
        });
        // 2. Press down
        await chrome.debugger.sendCommand(target, "Input.dispatchMouseEvent", {
            type: "mousePressed", x, y, button: "left", clickCount: 1
        });
        // 3. Natural dwell delay (40ms - 90ms)
        const dwell = 40 + Math.floor(Math.random() * 50);
        await new Promise(r => setTimeout(r, dwell));
        // 4. Release mouse
        await chrome.debugger.sendCommand(target, "Input.dispatchMouseEvent", {
            type: "mouseReleased", x, y, button: "left", clickCount: 1
        });
        return { success: true, coords, dwell };
    } finally {
        await chrome.debugger.detach(target);
    }
}

async function dispatchCdpType(tabId, text) {
    if (!chrome.debugger) {
        throw new Error('chrome.debugger API is not enabled.');
    }
    const target = { tabId };
    await chrome.debugger.attach(target, "1.3");
    try {
        for (const char of text) {
            await chrome.debugger.sendCommand(target, "Input.dispatchKeyEvent", {
                type: "keyDown", text: char
            });
            await chrome.debugger.sendCommand(target, "Input.dispatchKeyEvent", {
                type: "keyUp"
            });
            // 20-50ms typing jitter
            await new Promise(r => setTimeout(r, 20 + Math.floor(Math.random() * 30)));
        }
        return { success: true, charactersTyped: text.length };
    } finally {
        await chrome.debugger.detach(target);
    }
}

// 3. Off-page CSP Bypass Proxy
async function executeProxyFetch(request) {
    try {
        const response = await fetch(request.url, request.options || {});
        const text = await response.text();
        return { ok: response.ok, status: response.status, data: text };
    } catch (err) {
        return { ok: false, error: err.message };
    }
}

// 4. State & Checkpoint Machine
async function updateTaskState(statePatch) {
    const data = await chrome.storage.local.get(['fleetRunState']);
    const current = data.fleetRunState || { status: 'idle', tasks: [], currentTaskIndex: 0 };
    const updated = { ...current, ...statePatch, updatedAt: Date.now() };
    await chrome.storage.local.set({ fleetRunState: updated });
    return updated;
}

// 5. API Sniffer Ingestion Hub (Immune to host page Mixed Content / CSP)
const recentSniffedRequests = [];

function handleSnifferIngest(item) {
    if (!item || !item.url) return;
    if (!item.id) {
        item.id = 'req_' + Math.random().toString(36).substring(2, 10);
    }
    recentSniffedRequests.unshift(item);
    if (recentSniffedRequests.length > 200) recentSniffedRequests.pop();

    // Forward to local Sniffer Hub 8999 asynchronously
    try {
        fetch('http://127.0.0.1:8999/api/ingest', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(item)
        }).catch(() => {});
    } catch (_) {}
}

// 6. Message Dispatcher
if (typeof chrome !== 'undefined' && chrome.runtime?.onMessage) {
    chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    const tabId = sender.tab ? sender.tab.id : message.tabId;

    if (message.action === 'SNIFFER_INGEST') {
        handleSnifferIngest(message.payload);
        sendResponse({ ok: true });
        return true;
    }

    if (message.action === 'GET_SNIFFER_FEED') {
        sendResponse({ ok: true, requests: recentSniffedRequests });
        return true;
    }

    if (message.action === 'CLEAR_SNIFFER_FEED') {
        recentSniffedRequests.length = 0;
        try {
            fetch('http://127.0.0.1:8999/api/clear', { method: 'POST' }).catch(() => {});
        } catch (_) {}
        sendResponse({ ok: true });
        return true;
    }

    if (message.action === 'EXPORT_COOKIES') {
        const targetUrl = message.url || (sender.tab ? sender.tab.url : null);
        if (!targetUrl) {
            sendResponse({ ok: false, error: 'No valid URL provided for cookie export' });
            return true;
        }
        exportTabCookies(targetUrl, tabId)
            .then(data => sendResponse({ ok: true, data }))
            .catch(err => sendResponse({ ok: false, error: err.message }));
        return true;
    }

    if (message.action === 'CDP_CLICK') {
        if (!tabId) {
            sendResponse({ ok: false, error: 'No target tab ID for CDP click' });
            return true;
        }
        dispatchCdpClick(tabId, message.coords)
            .then(res => sendResponse({ ok: true, ...res }))
            .catch(err => sendResponse({ ok: false, error: err.message }));
        return true;
    }

    if (message.action === 'CDP_TYPE') {
        if (!tabId) {
            sendResponse({ ok: false, error: 'No target tab ID for CDP typing' });
            return true;
        }
        dispatchCdpType(tabId, message.text)
            .then(res => sendResponse({ ok: true, ...res }))
            .catch(err => sendResponse({ ok: false, error: err.message }));
        return true;
    }

    if (message.action === 'PROXY_FETCH') {
        executeProxyFetch(message)
            .then(res => sendResponse(res))
            .catch(err => sendResponse({ ok: false, error: err.message }));
        return true;
    }

    if (message.action === 'UPDATE_STATE') {
        updateTaskState(message.state)
            .then(state => sendResponse({ ok: true, state }))
            .catch(err => sendResponse({ ok: false, error: err.message }));
        return true;
    }

    if (message.action === 'GET_STATE') {
        chrome.storage.local.get(['fleetRunState'], res => {
            sendResponse({ ok: true, state: res.fleetRunState || { status: 'idle' } });
        });
        return true;
    }

    if (message.action === 'EXPLOIT_TAB') {
        const targetUrl = message.url;
        const cookiesToInject = message.cookies || [];
        (async () => {
            try {
                const tab = await chrome.tabs.create({ url: 'about:blank', active: true });
                // Inject cookies before navigating (handles httpOnly)
                for (const c of cookiesToInject) {
                    try {
                        await chrome.cookies.set({
                            url: targetUrl,
                            name: c.name,
                            value: c.value,
                            domain: c.domain || undefined,
                            path: c.path || '/',
                            secure: c.secure || false,
                            httpOnly: c.httpOnly || false,
                            sameSite: c.sameSite || 'lax'
                        });
                    } catch (_) {}
                }
                await chrome.tabs.update(tab.id, { url: targetUrl });
                sendResponse({ ok: true, tabId: tab.id, injected: cookiesToInject.length });
            } catch (err) {
                sendResponse({ ok: false, error: err.message });
            }
        })();
        return true;
    }

    return false;
});
}

// 7. Web Navigation Observer (Catches full-page SSR document navigations in real time)
if (typeof chrome !== 'undefined' && chrome.webNavigation?.onCommitted) {
    chrome.webNavigation.onCommitted.addListener(async details => {
        try {
            if (details.frameId !== 0) return; // Top-level navigations only
            const url = details.url;
            if (!url || url.startsWith('chrome') || url.startsWith('about:') || url.startsWith('edge:') || url.startsWith('devtools:')) return;
            if (url.includes('127.0.0.1:8999') || url.includes('localhost:8999') || url.includes(':8998') || url.includes(':8999')) return;
            if (/\.(png|jpe?g|gif|svg|webp|css|woff2?|ttf|ico)(\?.*)?$/i.test(url)) return;

            const parsed = new URL(url);
            const pathName = parsed.pathname;
            const fileName = pathName.split('/').pop() || pathName;
            const actionName = `Xem trang: ${fileName || parsed.hostname}`;

            const tags = ['PAGE', 'USER', 'NAV'];
            if (/([?&/](id|uid|masv|user_id)=\d+)|(\/[a-z_-]+\/\d{2,})/i.test(url) || /ketquahoctap|diem|soyeu/i.test(url)) {
                tags.push('IDOR');
            }

            let cookieHeader = '';
            if (chrome.cookies) {
                try {
                    const cList = await chrome.cookies.getAll({ url });
                    if (cList && cList.length > 0) {
                        cookieHeader = cList.map(c => `${c.name}=${c.value}`).join('; ');
                    }
                } catch (_) {}
            }

            const reqHeaders = {
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
            };
            if (cookieHeader) reqHeaders['cookie'] = cookieHeader;

            handleSnifferIngest({
                id: 'req_nav_' + Math.random().toString(36).substring(2, 10),
                url: url,
                method: 'GET',
                headers: reqHeaders,
                body: '',
                response_status: 200,
                response_body: `[Trang Web SSR Đã Tải Thành Công]\nURL: ${url}\nPhiên làm việc (Cookies): ${cookieHeader || '(Trang không dùng cookie)'}`,
                trigger_action: actionName,
                source: 'desktop',
                tags: tags,
                is_important: true,
                highlight_reason: `Điều hướng trang: ${fileName || parsed.hostname}`,
                timestamp: Date.now()
            });
        } catch (_) {}
    });
}

// Expose exports for unit tests
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        getBaseDomain,
        SSO_ECOSYSTEMS,
        exportTabCookies,
        dispatchCdpClick,
        dispatchCdpType,
        executeProxyFetch,
        updateTaskState
    };
}
