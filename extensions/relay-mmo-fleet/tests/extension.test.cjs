const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

const bg = require('../background.js');
const content = require('../content.js');

test('manifest.json conforms to hardened Manifest V3 specs', () => {
    const manifestPath = path.join(__dirname, '..', 'manifest.json');
    assert.ok(fs.existsSync(manifestPath));
    const manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf8'));

    assert.equal(manifest.manifest_version, 3);
    assert.equal(manifest.name, 'RelayKit MMO Fleet Operator');
    assert.ok(manifest.permissions.includes('cookies'));
    assert.ok(manifest.permissions.includes('storage'));
    assert.ok(manifest.optional_permissions.includes('debugger'));
    assert.equal(manifest.background.service_worker, 'background.js');
    assert.equal(manifest.content_scripts[0].all_frames, true);
});

test('exportTabCookies formats cookies in JSON and Netscape formats', async () => {
    const fakeCookies = [
        {
            domain: '.example.com',
            name: 'session_id',
            value: 'sess_123456',
            path: '/',
            secure: true,
            expirationDate: 1735689600
        },
        {
            domain: 'example.com',
            name: 'cf_clearance',
            value: 'clr_abc',
            path: '/',
            secure: false,
            expirationDate: null
        }
    ];

    globalThis.chrome = {
        cookies: {
            getAll: async (query) => {
                assert.ok(query.url === 'https://example.com/app' || query.domain === 'example.com');
                return fakeCookies;
            }
        }
    };

    const res = await bg.exportTabCookies('https://example.com/app');
    assert.equal(res.total, 2);
    assert.equal(res.domain, 'example.com');
    assert.match(res.netscape, /\.example\.com\tTRUE\t\/\tTRUE\t1735689600\tsession_id\tsess_123456/);
    assert.match(res.netscape, /example\.com\tFALSE\t\/\tFALSE\t0\tcf_clearance\tclr_abc/);

    delete globalThis.chrome;
});

test('CDP dispatcher throws when chrome.debugger is unattached or unavailable', async () => {
    globalThis.chrome = {}; // debugger missing

    await assert.rejects(
        async () => bg.dispatchCdpClick(10, { x: 100, y: 200 }),
        /chrome\.debugger API is not enabled/
    );

    await assert.rejects(
        async () => bg.dispatchCdpType(10, 'secret_pass'),
        /chrome\.debugger API is not enabled/
    );

    delete globalThis.chrome;
});

test('updateTaskState commits patches to chrome.storage.local', async () => {
    const storageStore = {};
    globalThis.chrome = {
        storage: {
            local: {
                get: async (keys) => ({ fleetRunState: storageStore.fleetRunState }),
                set: async (val) => Object.assign(storageStore, val)
            }
        }
    };

    const updated = await bg.updateTaskState({ status: 'running', activeLease: 'worker-1' });
    assert.equal(updated.status, 'running');
    assert.equal(updated.activeLease, 'worker-1');
    assert.ok(updated.updatedAt > 0);
    assert.equal(storageStore.fleetRunState.status, 'running');

    delete globalThis.chrome;
});

test('content script harvestWebStorage detects JWT tokens in storage', () => {
    const fakeLocal = {
        theme: 'dark',
        auth_token: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.do_not_leak',
        user_id: '99'
    };

    globalThis.localStorage = {
        length: 3,
        key: (i) => Object.keys(fakeLocal)[i],
        getItem: (k) => fakeLocal[k]
    };
    globalThis.sessionStorage = { length: 0, key: () => null, getItem: () => null };
    globalThis.location = { href: 'https://app.target.com/dashboard' };

    const data = content.harvestWebStorage();
    assert.equal(data.tokens.length, 1);
    assert.equal(data.tokens[0].key, 'auth_token');
    assert.equal(data.tokens[0].source, 'localStorage');
    assert.match(data.tokens[0].token, /^eyJ/);

    delete globalThis.localStorage;
    delete globalThis.sessionStorage;
    delete globalThis.location;
});

test('content script MediaController mutes media for autoplay policy bypass', () => {
    const fakeVideo = {
        defaultMuted: false,
        muted: false,
        volume: 1,
        playsInline: false
    };

    content.MediaController.mute(fakeVideo);
    assert.equal(fakeVideo.defaultMuted, true);
    assert.equal(fakeVideo.muted, true);
    assert.equal(fakeVideo.volume, 0);
    assert.equal(fakeVideo.playsInline, true);
});

test('getBaseDomain correctly identifies eTLD+1 and multi-part domains', () => {
    assert.equal(bg.getBaseDomain('www.youtube.com'), 'youtube.com');
    assert.equal(bg.getBaseDomain('chat.zalo.me'), 'zalo.me');
    assert.equal(bg.getBaseDomain('sub.domain.co.uk'), 'domain.co.uk');
    assert.equal(bg.getBaseDomain('m.facebook.com'), 'facebook.com');
});

test('exportTabCookies on YouTube automatically queries google.com SSO ecosystem', async () => {
    const queriedDomains = [];
    globalThis.chrome = {
        cookies: {
            getAll: async (query) => {
                if (query.domain) queriedDomains.push(query.domain);
                if (query.domain === 'google.com') {
                    return [{ domain: '.google.com', name: 'SID', value: 'google_session', path: '/' }];
                }
                if (query.domain === 'youtube.com') {
                    return [{ domain: '.youtube.com', name: 'LOGIN_INFO', value: 'yt_login', path: '/' }];
                }
                return [];
            }
        }
    };

    const res = await bg.exportTabCookies('https://www.youtube.com/watch?v=dQw4w9WgXcQ');
    assert.ok(queriedDomains.includes('youtube.com'));
    assert.ok(queriedDomains.includes('google.com'));
    assert.equal(res.total, 2);
    assert.ok(res.cookies.some(c => c.name === 'SID' && c.domain === '.google.com'));
    assert.ok(res.cookies.some(c => c.name === 'LOGIN_INFO' && c.domain === '.youtube.com'));

    delete globalThis.chrome;
});

test('content script IndexedDbEngine dumpAll returns empty array gracefully when unsupported', async () => {
    // When indexedDB is not present
    const res = await content.IndexedDbEngine.dumpAll();
    assert.deepEqual(res, []);
});

test('content script harvestVideoLinks extracts and deduplicates video URLs from TikTok anchors', () => {
    const fakeAnchors = [
        { href: 'https://www.tiktok.com/@creator/video/7106594312292453675?is_from_webapp=1', getAttribute: () => 'https://www.tiktok.com/@creator/video/7106594312292453675' },
        { href: 'https://www.tiktok.com/@creator/video/7106594312292453675', getAttribute: () => 'https://www.tiktok.com/@creator/video/7106594312292453675' },
        { href: 'https://www.tiktok.com/@creator/video/9999999999999999999', getAttribute: () => 'https://www.tiktok.com/@creator/video/9999999999999999999' },
        { href: 'https://www.tiktok.com/about', getAttribute: () => 'https://www.tiktok.com/about' }
    ];

    globalThis.window = { location: { hostname: 'www.tiktok.com' } };
    globalThis.document = {
        querySelectorAll: (selector) => {
            if (selector.includes('/video/')) {
                return fakeAnchors.filter(a => a.href.includes('/video/'));
            }
            return [];
        }
    };

    const res = content.harvestVideoLinks();
    assert.equal(res.platform, 'tiktok');
    assert.equal(res.count, 2);
    assert.ok(res.urls.includes('https://www.tiktok.com/@creator/video/7106594312292453675'));
    assert.ok(res.urls.includes('https://www.tiktok.com/@creator/video/9999999999999999999'));

    delete globalThis.window;
    delete globalThis.document;
});

test('content script executeTikTokUpload is exposed and validates file input presence gracefully', async () => {
    assert.equal(typeof content.executeTikTokUpload, 'function');
    globalThis.window = { location: { href: 'https://www.tiktok.com/tiktokstudio/upload' } };
    globalThis.document = {
        querySelector: () => null,
        querySelectorAll: () => []
    };

    try {
        await content.executeTikTokUpload({ fileName: 'test.mp4', fileBase64: 'AAAA', findInputTimeoutMs: 50 });
        assert.fail('Should throw when no upload input found');
    } catch (err) {
        assert.ok(err.message.includes('Không tìm thấy khung tải video'));
    }

    delete globalThis.window;
    delete globalThis.document;
});

test('content script injectApiSniffer creates script element and exposes sniffer queue', () => {
    assert.equal(typeof content.injectApiSniffer, 'function');
    assert.ok(Array.isArray(content.localSniffQueue));

    let scriptCreated = false;
    globalThis.window = {};
    globalThis.document = {
        createElement: (tag) => {
            if (tag === 'script') {
                scriptCreated = true;
                return { remove: () => {} };
            }
            return {};
        },
        head: { appendChild: () => {} }
    };

    content.injectApiSniffer();
    assert.equal(scriptCreated, true);

    delete globalThis.window;
    delete globalThis.document;
});

test('manifest.json registers sniffer_inject.js in world MAIN at document_start', () => {
    const manifestPath = path.join(__dirname, '..', 'manifest.json');
    const manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf8'));

    const mainWorldScript = manifest.content_scripts.find(s => s.world === 'MAIN');
    assert.ok(mainWorldScript, 'Must have a content script registered in world: MAIN');
    assert.ok(mainWorldScript.js.includes('sniffer_inject.js'));
    assert.equal(mainWorldScript.run_at, 'document_start');
    assert.equal(mainWorldScript.all_frames, true);

    const injectFilePath = path.join(__dirname, '..', 'sniffer_inject.js');
    assert.ok(fs.existsSync(injectFilePath), 'sniffer_inject.js must exist on disk');
});

