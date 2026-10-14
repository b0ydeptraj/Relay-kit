const test = require('node:test');
const assert = require('node:assert/strict');
const path = require('node:path');
const bridge = require('../.agent/skills/mmo-browser-fleet-automation/scripts/browser_media_bridge.js');

test('Html5MediaController mutes video attributes correctly for autoplay bypass', () => {
    const video = {
        defaultMuted: false,
        muted: false,
        volume: 1,
        playsInline: false
    };
    bridge.Html5MediaController.muteForPlayback(video);
    assert.equal(video.defaultMuted, true);
    assert.equal(video.muted, true);
    assert.equal(video.volume, 0);
    assert.equal(video.playsInline, true);
});

test('Html5MediaController reads state correctly', () => {
    const video = {
        readyState: 4,
        currentTime: 42.5,
        duration: 100,
        paused: false,
        ended: false,
        seeking: false,
        error: null
    };
    const state = bridge.Html5MediaController.getState(video);
    assert.equal(state.ready, true);
    assert.equal(state.currentTime, 42.5);
    assert.equal(state.duration, 100);
    assert.equal(state.paused, false);
    assert.equal(state.ended, false);
});

test('ResilientStepRunner completes successful step within timeout', async () => {
    const runner = bridge.createRunner();
    const result = await runner.withStepTimeout(async (signal) => {
        return 'success_val';
    }, 1000, { isCritical: true, stepLabel: 'test-step' });

    assert.equal(result.success, true);
    assert.equal(result.result, 'success_val');
    assert.equal(result.skipped, false);
});

test('ResilientStepRunner gracefully skips non-critical step on timeout', async () => {
    const runner = bridge.createRunner();
    let onSkipCalled = false;

    const result = await runner.withStepTimeout(async (signal) => {
        await new Promise(r => setTimeout(r, 200));
        return 'done';
    }, 50, {
        isCritical: false,
        stepLabel: 'non-critical-quiz',
        onSkip: () => { onSkipCalled = true; }
    });

    assert.equal(result.success, false);
    assert.equal(result.skipped, true);
    assert.equal(onSkipCalled, true);
    assert.match(result.reason, /timed out after 50ms/);
});

test('ResilientStepRunner throws error on critical step timeout', async () => {
    const runner = bridge.createRunner();
    await assert.rejects(
        async () => {
            await runner.withStepTimeout(async (signal) => {
                await new Promise(r => setTimeout(r, 200));
            }, 50, { isCritical: true, stepLabel: 'critical-auth' });
        },
        /Step \[critical-auth\] timed out after 50ms/
    );
});

test('ResilientStepRunner cancel() immediately aborts active signal', async () => {
    const runner = bridge.createRunner();
    let abortedInStep = false;

    const promise = runner.withStepTimeout(async (signal) => {
        return new Promise((resolve, reject) => {
            signal.addEventListener('abort', () => {
                abortedInStep = true;
                reject(new Error('Aborted'));
            });
        });
    }, 5000, { isCritical: true });

    setTimeout(() => runner.cancel(), 20);

    await assert.rejects(promise, /Aborted/);
    assert.equal(abortedInStep, true);
});

test('FrameRpcBridge attaches receiver and replies to dispatched commands', async () => {
    let messageListener = null;
    const fakeWindow = {
        addEventListener: (event, fn) => { if (event === 'message') messageListener = fn; },
        removeEventListener: (event, fn) => { if (event === 'message') messageListener = null; }
    };
    globalThis.window = fakeWindow;

    const detach = bridge.FrameRpcBridge.attachFrameReceiver('*', {
        ping: (data) => `pong_${data.val}`
    });

    assert.ok(messageListener);

    let sentReply = null;
    const fakeSource = {
        postMessage: (payload) => { sentReply = payload; }
    };

    // Simulate incoming command
    messageListener({
        origin: 'https://example.com',
        source: fakeSource,
        data: {
            type: 'FRAME_RPC_REQ',
            session: 's1',
            requestId: 'r1',
            command: 'ping',
            data: { val: 42 }
        }
    });

    await new Promise(r => setTimeout(r, 20));

    assert.ok(sentReply);
    assert.equal(sentReply.type, 'FRAME_RPC_RES');
    assert.equal(sentReply.session, 's1');
    assert.equal(sentReply.requestId, 'r1');
    assert.equal(sentReply.ok, true);
    assert.equal(sentReply.result, 'pong_42');

    detach();
    delete globalThis.window;
});

