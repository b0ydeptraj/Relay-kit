# discipline-utilities-gauntlet-task-matrix

## Purpose

This file freezes the initial `12 repo / 36 task` matrix for the `discipline-utilities` gauntlet.

Each repo contributes:

- 1 `root-cause-debugging` task
- 1 `test-first-development` task
- 1 `evidence-before-completion` task

Status meanings:

- `ready`: seed evidence is already specific enough to start calibration
- `conditional`: the seed is real, but calibration must confirm the path is worth keeping

## Track A — Python library / core utility

| Task ID | Repo | Skill under test | Candidate task | Seed evidence | Target files | Status |
|---|---|---|---|---|---|---|
| A1-D | `pallets/click` | `root-cause-debugging` | Reproduce and explain the infinite-generator hang in pager tempfile mode. | `C:\Users\b0ydeptrai\OneDrive\Documents\ai-kit-pilot\click\src\click\_termui_impl.py:535` | `src/click/_termui_impl.py`, `tests/test_utils.py` | `ready` |
| A1-T | `pallets/click` | `test-first-development` | Add a regression-first test around pager behavior before any mitigation for non-terminating or extremely large iterables. | `C:\Users\b0ydeptrai\OneDrive\Documents\ai-kit-pilot\click\tests\test_utils.py`, `C:\Users\b0ydeptrai\OneDrive\Documents\ai-kit-pilot\click\src\click\_termui_impl.py:535` | `tests/test_utils.py`, `src/click/_termui_impl.py` | `ready` |
| A1-E | `pallets/click` | `evidence-before-completion` | Review any proposed cleanup around `Parameter.default` semantics only if code plus tests prove no callback or flag regressions. | `C:\Users\b0ydeptrai\OneDrive\Documents\ai-kit-pilot\click\src\click\core.py:2125` | `src/click/core.py`, related tests in `tests/` | `conditional` |
| A2-D | `pallets/itsdangerous` | `root-cause-debugging` | Investigate positional `salt` compatibility drift in `TimedSerializer.loads` and explain the real failure mode. | `C:\Users\b0ydeptrai\OneDrive\Documents\ai-kit-pilot\itsdangerous\src\itsdangerous\timed.py:182`, `C:\Users\b0ydeptrai\OneDrive\Documents\ai-kit-pilot\itsdangerous\src\itsdangerous\serializer.py:328` | `src/itsdangerous/timed.py`, `src/itsdangerous/serializer.py`, `tests/test_itsdangerous/test_timed.py` | `ready` |
| A2-T | `pallets/itsdangerous` | `test-first-development` | Write a failing compatibility test for legacy-style positional salt calls before deciding whether to preserve or reject the API. | `C:\Users\b0ydeptrai\OneDrive\Documents\ai-kit-pilot\itsdangerous\tests\test_itsdangerous\test_timed.py:96`, `C:\Users\b0ydeptrai\OneDrive\Documents\ai-kit-pilot\itsdangerous\src\itsdangerous\timed.py:182` | `tests/test_itsdangerous/test_timed.py`, `src/itsdangerous/timed.py` | `ready` |
| A2-E | `pallets/itsdangerous` | `evidence-before-completion` | Require explicit compatibility proof before accepting any change to timed serializer loading semantics. | `C:\Users\b0ydeptrai\OneDrive\Documents\ai-kit-pilot\itsdangerous\tests\test_itsdangerous\test_timed.py:104`, `:115` | `tests/test_itsdangerous/test_timed.py`, `src/itsdangerous/timed.py` | `ready` |
| A3-D | `pallets-eco/blinker` | `root-cause-debugging` | Explain and reproduce the `receiver_connected.send` exception path that currently disconnects and re-raises without a test. | `C:\Users\b0ydeptrai\OneDrive\Documents\ai-kit-pilot\blinker\src\blinker\base.py:135` | `src/blinker/base.py`, `tests/test_signals.py` | `ready` |
| A3-T | `pallets-eco/blinker` | `test-first-development` | Add the missing `receivers_for(ANY)` regression test before considering any behavior change. | `C:\Users\b0ydeptrai\OneDrive\Documents\ai-kit-pilot\blinker\src\blinker\base.py:336` | `tests/test_signals.py`, `src/blinker/base.py` | `ready` |
| A3-E | `pallets-eco/blinker` | `evidence-before-completion` | Demand proof that weak-ref cleanup and ANY-sender delivery still agree before calling signal changes complete. | `C:\Users\b0ydeptrai\OneDrive\Documents\ai-kit-pilot\blinker\tests\test_signals.py:417`, `:442-449` | `tests/test_signals.py`, `src/blinker/base.py` | `ready` |
| A4-D | `pallets/markupsafe` | `root-cause-debugging` | Investigate why extension-init coverage is skipped when speedups are unavailable or inactive, and separate environment cause from code bug. | `C:\Users\b0ydeptrai\OneDrive\Documents\ai-kit-pilot\markupsafe\tests\test_ext_init.py:14-20` | `tests/test_ext_init.py`, `tests/conftest.py`, `src/markupsafe/` | `ready` |
| A4-T | `pallets/markupsafe` | `test-first-development` | Add or tighten tests around pure-Python fallback versus `_speedups` activation before any packaging or import-path change. | `C:\Users\b0ydeptrai\OneDrive\Documents\ai-kit-pilot\markupsafe\tests\conftest.py:33`, `tests/test_ext_init.py:14-20` | `tests/test_ext_init.py`, `tests/conftest.py` | `conditional` |
| A4-E | `pallets/markupsafe` | `evidence-before-completion` | Do not accept any extension-init or speedups fix without proof on both “speedups active” and “speedups unavailable” paths. | `C:\Users\b0ydeptrai\OneDrive\Documents\ai-kit-pilot\markupsafe\tests\test_ext_init.py:20` | `tests/test_ext_init.py`, build/test commands for extension path | `ready` |

## Track B — Python app / tooling / service

| Task ID | Repo | Skill under test | Candidate task | Seed evidence | Target files | Status |
|---|---|---|---|---|---|---|
| B1-D | `httpie/cli` | `root-cause-debugging` | Investigate the confusion between request kwargs and send kwargs in debug output and identify where the real split leaks. | `C:\Users\b0ydeptrai\OneDrive\Documents\ai-kit-pilot\httpie-cli\httpie\client.py:88` | `httpie/client.py`, related tests | `ready` |
| B1-T | `httpie/cli` | `test-first-development` | Write a focused regression test around expected versus unexpected error paths before touching core error handling. | `C:\Users\b0ydeptrai\OneDrive\Documents\ai-kit-pilot\httpie-cli\httpie\core.py:139`, `:175` | `httpie/core.py`, relevant tests in `tests/` | `conditional` |
| B1-E | `httpie/cli` | `evidence-before-completion` | Require command-level proof for redirect and error handling before accepting any simplification in core request flow. | `C:\Users\b0ydeptrai\OneDrive\Documents\ai-kit-pilot\httpie-cli\httpie\core.py:175` | `httpie/core.py`, `httpie/client.py`, CLI tests | `conditional` |
| B2-D | `encode/httpx` | `root-cause-debugging` | Reproduce the `auth-int` path and determine whether the failure is unsupported protocol, missing branch, or test gap. | `C:\Users\b0ydeptrai\OneDrive\Documents\ai-kit-pilot\httpx\httpx\_auth.py:267` | `httpx/_auth.py`, auth tests | `ready` |
| B2-T | `encode/httpx` | `test-first-development` | Add a failing test for digest `auth-int` or malformed `qop` handling before changing auth behavior. | `C:\Users\b0ydeptrai\OneDrive\Documents\ai-kit-pilot\httpx\httpx\_auth.py:267-299` | `tests/`, `httpx/_auth.py` | `ready` |
| B2-E | `encode/httpx` | `evidence-before-completion` | Require RFC-aligned evidence before claiming digest auth behavior is fixed or complete. | `C:\Users\b0ydeptrai\OneDrive\Documents\ai-kit-pilot\httpx\httpx\_auth.py:293-305` | `httpx/_auth.py`, auth tests, docs/spec references | `ready` |
| B3-D | `pallets/flask` | `root-cause-debugging` | Investigate async-path behavior around optional `asgiref` support and separate environment skip from framework bug. | `C:\Users\b0ydeptrai\OneDrive\Documents\ai-kit-pilot\flask\tests\test_async.py:11` | `tests/test_async.py`, async support files in `src/flask/` | `conditional` |
| B3-T | `pallets/flask` | `test-first-development` | Add a targeted regression test around optional dependency paths before changing async or config behavior. | `C:\Users\b0ydeptrai\OneDrive\Documents\ai-kit-pilot\flask\tests\test_config.py:39`, `tests/test_reqctx.py:148` | `tests/test_config.py`, `tests/test_reqctx.py`, related source files | `conditional` |
| B3-E | `pallets/flask` | `evidence-before-completion` | Require proof on both optional-dependency-present and missing paths before accepting any async/config compatibility fix. | `C:\Users\b0ydeptrai\OneDrive\Documents\ai-kit-pilot\flask\tests\test_async.py:11`, `tests/test_config.py:39` | `tests/test_async.py`, `tests/test_config.py`, `src/flask/` | `conditional` |
| B4-D | `fastapi/fastapi` | `root-cause-debugging` | Investigate whether Decimal encoding ambiguity is a real round-trip bug or only a documentation mismatch. | `C:\Users\b0ydeptrai\OneDrive\Documents\ai-kit-pilot\fastapi\fastapi\encoders.py:42` | `fastapi/encoders.py`, tests covering JSONable encoding | `ready` |
| B4-T | `fastapi/fastapi` | `test-first-development` | Add a focused test for Decimal serialization edge cases before changing encoder behavior. | `C:\Users\b0ydeptrai\OneDrive\Documents\ai-kit-pilot\fastapi\fastapi\encoders.py:42-56` | `tests/`, `fastapi/encoders.py` | `ready` |
| B4-E | `fastapi/fastapi` | `evidence-before-completion` | Require proof before any deprecation cleanup tied to `openapi_prefix` or lifespan migration. | `C:\Users\b0ydeptrai\OneDrive\Documents\ai-kit-pilot\fastapi\fastapi\applications.py:931`, `fastapi/routing.py:1292`, `:4868-4900` | `fastapi/applications.py`, `fastapi/routing.py`, deprecation tests/docs | `ready` |

## Track C — TypeScript / web / frontend-adjacent

| Task ID | Repo | Skill under test | Candidate task | Seed evidence | Target files | Status |
|---|---|---|---|---|---|---|
| C1-D | `sindresorhus/ky` | `root-cause-debugging` | Investigate whether the 400-status throw behavior in the methods test is correct or masking a deeper semantics mismatch. | `C:\Users\b0ydeptrai\OneDrive\Documents\ai-kit-pilot\ky\test\methods.ts:55` | `test/methods.ts`, related request/error handling source | `ready` |
| C1-T | `sindresorhus/ky` | `test-first-development` | Add a failing type or behavior test before changing `deepMerge` typing or merge semantics. | `C:\Users\b0ydeptrai\OneDrive\Documents\ai-kit-pilot\ky\source\utils\merge.ts:85` | `source/utils/merge.ts`, `test/`, type tests | `ready` |
| C1-E | `sindresorhus/ky` | `evidence-before-completion` | Require proof before changing `ResponsePromise.json` typing assumptions. | `C:\Users\b0ydeptrai\OneDrive\Documents\ai-kit-pilot\ky\source\types\ResponsePromise.ts:21` | `source/types/ResponsePromise.ts`, type tests | `conditional` |
| C2-D | `axios/axios` | `root-cause-debugging` | Investigate why adapter and regression tests are skipped, and distinguish runner limitation from real library issue. | `C:\Users\b0ydeptrai\OneDrive\Documents\ai-kit-pilot\axios\test\unit\adapters\http.js:490`, `:515`, `test/unit/regression/bugs.js:51` | `test/unit/adapters/http.js`, `test/unit/regression/bugs.js`, relevant adapter code in `lib/` | `ready` |
| C2-T | `axios/axios` | `test-first-development` | Convert one skipped regression or composeSignals path into a reproducible failing test before changing behavior. | `C:\Users\b0ydeptrai\OneDrive\Documents\ai-kit-pilot\axios\tests\unit\composeSignals.test.js:6`, `tests/unit/regression.test.js:56` | `tests/unit/composeSignals.test.js`, `tests/unit/regression.test.js`, source under `lib/` | `ready` |
| C2-E | `axios/axios` | `evidence-before-completion` | Require browser-plus-node proof for any adapter/header regression claim before calling it done. | `C:\Users\b0ydeptrai\OneDrive\Documents\ai-kit-pilot\axios\test\unit\core\AxiosHeaders.js:113`, `tests/unit/axiosHeaders.test.js:87` | `test/unit/core/AxiosHeaders.js`, `tests/unit/axiosHeaders.test.js`, source in `lib/core/` | `ready` |
| C3-D | `sindresorhus/p-limit` | `root-cause-debugging` | Investigate the Node 20 clearQueue skip and decide whether the failing surface belongs to AVA, DOMException, or the library. | `C:\Users\b0ydeptrai\OneDrive\Documents\ai-kit-pilot\p-limit\test.js:197` | `test.js`, `index.js` | `ready` |
| C3-T | `sindresorhus/p-limit` | `test-first-development` | Add a focused test for queue-clear rejection semantics that is less coupled to the current environment skip. | `C:\Users\b0ydeptrai\OneDrive\Documents\ai-kit-pilot\p-limit\test.js:197-209` | `test.js`, `index.js` | `ready` |
| C3-E | `sindresorhus/p-limit` | `evidence-before-completion` | Require proof of `pendingCount`, `activeCount`, and rejection semantics before accepting concurrency behavior changes. | `C:\Users\b0ydeptrai\OneDrive\Documents\ai-kit-pilot\p-limit\test.js:154-209` | `test.js`, `index.js` | `ready` |
| C4-D | `date-fns/date-fns` | `root-cause-debugging` | Investigate `closestIndexTo` invalid input semantics and determine whether current behavior is intentional, inconsistent, or just legacy. | `C:\Users\b0ydeptrai\OneDrive\Documents\ai-kit-pilot\date-fns\src\closestIndexTo\index.ts:32` | `src/closestIndexTo/index.ts`, matching tests | `ready` |
| C4-T | `date-fns/date-fns` | `test-first-development` | Add a focused test around decade-boundary semantics before changing the technical definition in `endOfDecade`. | `C:\Users\b0ydeptrai\OneDrive\Documents\ai-kit-pilot\date-fns\src\endOfDecade\index.ts:38` | `src/endOfDecade/index.ts`, corresponding tests | `ready` |
| C4-E | `date-fns/date-fns` | `evidence-before-completion` | Require strong compatibility proof before changing “undefined versus -1” or “2000-2009 versus 2001-2010” behavior. | `C:\Users\b0ydeptrai\OneDrive\Documents\ai-kit-pilot\date-fns\src\closestIndexTo\index.ts:32`, `src/endOfDecade/index.ts:38` | `src/closestIndexTo/index.ts`, `src/endOfDecade/index.ts`, tests, changelog impact | `ready` |

## Execution note

This matrix is concrete enough to begin the gauntlet, but calibration still has the right to reject a task if:

- the repo cannot be built on the pilot machine
- the seed evidence turns out to be non-actionable
- the target path is only an environment skip and not a product or library behavior worth evaluating

When a task is rejected in calibration, replace it with another task from the same repo and the same skill family. Do not move the skill family to a different repo slot.
