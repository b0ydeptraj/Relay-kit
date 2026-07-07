# Relay-Kit V5 Roadmap — Governed Runtime

> **Mission**: Relay-Kit V5 turns static skill installation into a governed runtime: schema-driven commands, trusted extensions, tiered semantic context retrieval, evidence-backed memory, and bounded multi-lane orchestration.

---

## V5 Global Definition Of Done

V5 chi duoc coi la complete khi TAT CA cac gate sau pass:

| # | Gate | V4-compatible command | V5 target command |
|---|---|---|---|
| 1 | Full pytest pass | `pytest` | `pytest` (khong doi) |
| 2 | validate_runtime pass | `python scripts/validate_runtime.py` | `relay-kit runtime validate .` |
| 3 | runtime_doctor live strict pass | `python scripts/runtime_doctor.py . --strict --state-mode live` | `relay-kit runtime doctor . --strict` |
| 4 | skill_gauntlet semantic pass | `python scripts/skill_gauntlet.py . --semantic --strict` | `relay-kit skill gauntlet . --semantic --strict` |
| 5 | workflow eval pass | `python scripts/run_eval.py .` | `relay-kit eval run .` |
| 6 | adapter diagnose all strict pass | `python scripts/adapter_diagnose.py . --adapter all --strict` | `relay-kit adapter diagnose . --adapter all --strict` |
| 7 | readiness enterprise pass (hoac hold co documented blocker) | `python scripts/readiness_check.py . --profile enterprise` | `relay-kit readiness check . --profile enterprise` |
| 8 | V4 command compatibility 100% | `pytest tests/test_cli_compat.py` | `pytest tests/test_cli_compat.py` (khong doi) |
| 9 | No stale generated surfaces | `python scripts/adapter_diagnose.py . --strict` | `relay-kit adapter diagnose . --strict` |
| 10 | No untrusted extension can activate | `pytest tests/test_extension_trust_policy.py` | `relay-kit extension audit . --strict` |
| 11 | No journal entry without evidence_ref | `relay-kit journal list . --filter missing-evidence` returns 0 | `relay-kit journal list . --filter missing-evidence` returns 0 |
| 12 | Multi-lane lock prevents same-file writes | `pytest tests/test_lane_concurrency.py` | `pytest tests/test_lane_concurrency.py` (khong doi) |

> [!CAUTION]
> Neu bat ky gate nao fail, V5 KHONG duoc release. Moi gate phai co command chay duoc va output kiem chung duoc.

---

## Baseline Hien Tai (V4 — So Lieu Thuc)

```
relay_kit_public_cli.py (~2.9k dong)
    |
    v
relay_kit.py  -->  relay_kit_v3/  (35+ modules)
    |
skills.manifest.yaml
    |
    v
.agent/skills/  .claude/skills/  .codex/skills/  (static .md files)
```

| Metric | Gia tri thuc |
|---|---|
| Canonical skills (ALL_V3_SKILLS registry) | **74** |
| Generated adapter skill dirs (.agent/skills/) | **105** |
| Dong code relay_kit_public_cli.py | **~2.9k** |
| Context/state/continuity | Co (nhung chua co field-tested self-learning memory) |
| CLI command groups | Viet tay, moi command moi = them ~80 dong Python |
| Plugin/extension system | Chua co |
| Context search | Keyword + graph ranking |
| Agent memory | Relay-kit has continuity/state artifacts, but no evidence-backed learned pattern journal yet. |
| Multi-lane | Co skill `team` nhung chua co runtime lane lock |

**3 diem yeu cot loi can xu ly:**
1. `relay_kit_public_cli.py` viet tay qua nhieu — moi command moi = risk regression.
2. Context search is mostly lexical today; graph-aware ranking exists but is not yet a full indexed semantic retrieval engine.
3. Relay-kit has continuity/state artifacts, but no evidence-backed learned pattern journal yet.

---

## V5.0 — CLI Modularization

**Muc tieu:** Tach `relay_kit_public_cli.py` thanh cac module nho, giu nguyen public facade on dinh, them schema-driven command registry.

> [!IMPORTANT]
> KHONG xoa `relay_kit_public_cli.py`. Giu no lam thin public facade. Chi tach command groups sang `relay_kit_v3/cli/` va sinh command tu schema/registry.

### Deliverables

| # | Feature | File | Dau ra ky vong |
|---|---|---|---|
| 5.0.1 | **Command Group Split** | `relay_kit_v3/cli/` [NEW dir] | Tach cac `_parse_*_args` functions tu `relay_kit_public_cli.py` sang cac file rieng: `cli/doctor.py`, `cli/context.py`, `cli/adapter.py`, `cli/delegation.py`, etc. |
| 5.0.2 | **Schema Command Registry** | `relay_kit_v3/cli/command_schema.yaml` [NEW] | Moi command co entry: `name`, `args`, `flags`, `handler`, `help_text`. CLI engine doc file nay de sinh parser. |
| 5.0.3 | **CLI Engine** | `relay_kit_v3/cli/engine.py` [NEW] | Doc `command_schema.yaml`, tu dong sinh `argparse` subparsers. Command moi chi can them 1 entry YAML + 1 handler function. |
| 5.0.4 | **Backward Compat Test Suite** | `tests/test_cli_compat.py` [NEW] | 100% cac lenh V4 hien co phai pass. Test bang cach chay tung lenh voi `--help` va so sanh output. |
| 5.0.5 | **Thin Facade** | `relay_kit_public_cli.py` [MODIFY] | Phase target: giam tu ~2.9k dong xuong < 500 dong. Stretch target: < 200 dong sau khi tat ca command groups migrate xong. |

### Acceptance Criteria
- `relay-kit doctor .` pass truoc va sau khi modularize.
- `relay-kit command list .` tra ve dung so luong commands nhu V4.
- `pytest tests/test_cli_compat.py` — 100% pass, 0 regression.
- `relay_kit_public_cli.py` con < 500 dong (phase target). Stretch target < 200 dong sau khi migration hoan tat.
- Every migrated command preserves exit code, stdout schema, stderr behavior.
- CLI help snapshot does not drift unless explicitly approved.

### Migration Strategy

> [!WARNING]
> CLI modularization la phase rui ro nhat. Neu tach sai la vo toan bo DX.

**Rules:**
- KHONG migrate tat ca commands cung luc.
- Moi PR chi migrate 1 command group (e.g., `context`, `adapter`, `delegation`).
- Old parser va new schema parser chay song song trong compatibility window.
- Golden CLI snapshots bat buoc cho help text, exit code, JSON output schema.
- Chi khi parity test 100% cho 1 group moi merge PR va chuyen sang group tiep theo.

**Golden Snapshot format:**
```
tests/cli_snapshots/
  doctor_help.txt          # relay-kit doctor --help output
  doctor_exit_0.txt        # relay-kit doctor . exit code and stdout
  context_search_help.txt  # relay-kit context search --help output
  ...
```

### Dau Ra Khi Hoan Thanh (Expected Output)
```
relay_kit_v3/
  cli/
    __init__.py
    engine.py              # Doc command_schema.yaml, sinh argparse
    command_schema.yaml     # Registry cua toan bo commands
    doctor.py              # Handler cho relay-kit doctor
    context.py             # Handler cho relay-kit context *
    adapter.py             # Handler cho relay-kit adapter *
    delegation.py          # Handler cho relay-kit delegation *
    lane.py                # Handler cho relay-kit lane *
    locale.py              # Handler cho relay-kit locale *
    eval.py                # Handler cho relay-kit eval *
    calibrate.py           # Handler cho relay-kit calibrate *
    prompt.py              # Handler cho relay-kit prompt *
    service.py             # Handler cho relay-kit service *
    skill.py               # Handler cho relay-kit skill *
    runtime.py             # Handler cho relay-kit runtime *
    impact.py              # Handler cho relay-kit impact *
    shell.py               # Handler cho relay-kit shell *
    token.py               # Handler cho relay-kit token *
    query.py               # Handler cho relay-kit query *
    evidence.py            # Handler cho relay-kit evidence *
    contract.py            # Handler cho relay-kit contract *
    publish.py             # Handler cho relay-kit publish *
    support.py             # Handler cho relay-kit support *
    readiness.py           # Handler cho relay-kit readiness *
    release.py             # Handler cho relay-kit release *
    agent_cmd.py           # Handler cho relay-kit agent *
    command_cmd.py         # Handler cho relay-kit command *
tests/
  test_cli_compat.py       # Backward compat test suite
```

**command_schema.yaml mau:**
```yaml
commands:
  doctor:
    handler: relay_kit_v3.cli.doctor.run
    args:
      project_path: { default: ".", help: "Project root" }
    flags:
      --skip-tests: { action: store_true }
      --policy-pack: { choices: [default, strict, permissive] }
      --verbose: { action: store_true }
      --json: { action: store_true }

  context.search:
    handler: relay_kit_v3.cli.context.run_search
    args:
      project_path: { default: ".", help: "Project root" }
    flags:
      --query: { required: true }
      --limit: { type: int, default: 10 }
      --json: { action: store_true }
```

---

## V5.1 — Trusted Extension Packs

**Muc tieu:** Cho phep cai them skills tu nguon ben ngoai, nhung PHAI qua cong kiem chung nghiem ngat. Day KHONG phai plugin tu do.

> [!WARNING]
> Khong cho phep `relay-kit plugin install <random-url>`. Moi extension pack phai co manifest signature, hash verification, trust metadata, va phai pass skill gauntlet truoc khi kich hoat.

### Deliverables

| # | Feature | File | Dau ra ky vong |
|---|---|---|---|
| 5.1.1 | **Extension Pack Format** | `relay_kit_v3/extensions/pack_format.py` [NEW] | Dinh nghia cau truc: `pack.yaml` (metadata + hash), `skills/` (SKILL.md files), `trust.sig` (optional GPG signature) |
| 5.1.2 | **Trust Policy Engine** | `relay_kit_v3/extensions/trust_policy.py` [NEW] | 3 trust levels: `verified` (co sig), `reviewed` (user approved), `untrusted` (blocked by default). Config tai `.relay-kit/trust-policy.yaml` |
| 5.1.3 | **Extension Installer** | `relay_kit_v3/extensions/installer.py` [NEW] | `relay-kit extension install <path-or-url> --trust reviewed`. Download, verify hash, dat vao quarantine, chay skill gauntlet, chi activate neu pass. |
| 5.1.4 | **Skill Gauntlet Gate** | `relay_kit_v3/extensions/gauntlet_gate.py` [NEW] | Moi skill trong pack phai pass: naming guard, manifest registration, routing check, eval fixture check. Fail = block activation. |
| 5.1.5 | **Quarantine Manager** | `relay_kit_v3/extensions/quarantine.py` [NEW] | Extension lifecycle: `downloaded -> verified -> quarantined -> reviewed -> active`. Pack nam trong `.relay-kit/extensions/quarantine/<pack>/` cho den khi pass gauntlet va duoc review. |
| 5.1.6 | **Extension List/Remove** | `relay_kit_v3/extensions/manager.py` [NEW] | `relay-kit extension list .` va `relay-kit extension remove . <pack-name>` |
| 5.1.7 | **Extension Permission Manifest** | `relay_kit_v3/extensions/permissions.py` [NEW] | Moi pack phai khai bao permissions trong `pack.yaml`: `allowed_adapters`, `allowed_commands`, `allowed_paths`, `network_required`, `shell_required`, `writes_generated_surface`, `requires_human_review`. Extension requesting shell/network = blocked unless trust level = verified. |

### Extension Lifecycle
```
downloaded  -->  verified (hash check)  -->  quarantined (.relay-kit/extensions/quarantine/<pack>/)
    |                                            |
    |                                            v
    |                                       gauntlet pass?
    |                                        /        \\
    |                                      YES         NO
    |                                       |           |
    |                                  reviewed     BLOCKED
    |                                       |
    v                                  activate
  REJECT                          (generate adapter surface)
```

### Acceptance Criteria
- `relay-kit extension install ./my-pack --trust reviewed` chi thanh cong neu skill gauntlet pass 100%.
- Extension voi hash mismatch bi reject voi error message ro rang.
- Extension moi install PHAI nam trong quarantine truoc, KHONG duoc update skills.manifest.yaml truc tiep.
- Chi sau khi gauntlet pass + review xong moi generate adapter surface va update installed.json.
- `relay-kit extension list .` hien thi pack name, trust level, skill count, install date, lifecycle state.
- Extension untrusted khong the activate bang bat ky cach nao.
- Extension requesting shell/network permissions bi blocked unless trust level = verified.

**pack.yaml permissions mau:**
```yaml
permissions:
  shell: false
  network: false
  write_paths:
    - ".relay-kit/extensions/"
  adapters:
    - codex
    - claude
    - agent
  requires_human_review: true
```

### Dau Ra Khi Hoan Thanh
```
relay_kit_v3/
  extensions/
    __init__.py
    pack_format.py         # Pack structure validator
    trust_policy.py        # Trust level engine
    installer.py           # Download + verify + quarantine + gauntlet + activate
    quarantine.py          # Quarantine lifecycle manager
    gauntlet_gate.py       # Pre-activation quality gate
    manager.py             # List, remove, inspect extensions

.relay-kit/
  trust-policy.yaml        # User-configurable trust rules
  extensions/
    installed.json         # Registry cua packs da active
    quarantine/            # Packs dang cho review
      <pack-name>/
        pack.yaml
        skills/
```

**pack.yaml mau (ben trong extension pack):**
```yaml
name: custom-devops-skills
version: 1.0.0
author: b0ydeptraj
hash: sha256:abc123...
skills:
  - kubernetes-operations
  - terraform-infrastructure
  - ci-cd-pipeline
trust: reviewed
```

---

## V5.2 — Context Search Upgrade (Tiered)

**Muc tieu:** Nang cap context search theo 3 tang, KHONG bat buoc model nang.

> [!IMPORTANT]
> Default van la lexical + graph ranking (khong can model). Embedding la OPTIONAL.

### 3 Tang Search

| Tier | Mode | Dependency | Khi nao dung |
|---|---|---|---|
| **Tier 0 (Default)** | Lexical + Graph Ranking | Khong can gi them | Moi project, moi may |
| **Tier 1 (Optional)** | Local Embedding nhe | `pip install relay-kit[embeddings]` + `nomic-embed-text-v1.5` (137MB) | Khi can semantic search chinh xac hon |
| **Tier 2 (Pro)** | Multilingual Embedding | `pip install relay-kit[embeddings]` + `bge-m3` (570MB) | Project nhieu tieng Viet, can do chinh xac cao nhat |

### Deliverables

| # | Feature | File | Dau ra ky vong |
|---|---|---|---|
| 5.2.1 | **Graph Ranker** | `relay_kit_v3/context_graph.py` [NEW] | Skill dependency graph tu `Likely next step` trong SKILL.md. Khi search "network error", biet `api-integration` lien quan `mmo-http-api-automation` qua dependency chain. |
| 5.2.2 | **Lexical Scorer Upgrade** | `relay_kit_v3/context_index.py` [MODIFY] | BM25 thay vi simple keyword match. Tinh tf-idf score cho moi `.md` file. |
| 5.2.3 | **Embedding Adapter** | `relay_kit_v3/semantic_index.py` [NEW] | Abstract interface: load model, encode text, cosine similarity. Support `nomic-embed-text-v1.5` va `bge-m3`. |
| 5.2.4 | **Tiered Search Router** | `relay_kit_v3/search_router.py` [NEW] | Tu dong chon tier dua tren installed dependencies. Flag `--embedding-model` de override. |
| 5.2.5 | **Context Search Eval Suite** | `tests/context_search_eval.json` [NEW] | 20+ test cases voi expected results. Benchmark accuracy truoc khi claim "semantic search". |
| 5.2.6 | **Dynamic Token Budgeting** | `relay_kit_v3/token_economy.py` [MODIFY] | Tu tinh budget theo project size. **Budget la upper bound, KHONG phai default prompt size.** Token economy phai minimize context truoc, sau do moi cap theo tier. Tier: project <50 file = 30k, 50-200 = 60k, 200-500 = 90k, >500 = 120k. |
| 5.2.7 | **Index Freshness + Invalidation** | `relay_kit_v3/context_index_state.py` [NEW] | Store file hash, mtime, model name, index version. Reindex only changed files. Fail/warn when query uses stale index. |

### Acceptance Criteria
- Tier 0 (default): `relay-kit context search . --query "xu ly loi network"` tra ve ket qua hop ly KHONG can model.
- Tier 1: accuracy cao hon Tier 0 tren eval suite (measured, khong guess).
- `relay-kit context search . --embedding-model nomic-embed-text-v1.5` va `--embedding-model bge-m3` deu hoat dong.
- `pytest tests/test_context_search_eval.py` pass voi minimum 80% precision tren eval suite cho Tier 0.
- Khong co model nao duoc download tu dong. User phai chay `relay-kit context install-model <name>` explicitly.
- Editing 1 SKILL.md chi reindex file do, khong full reindex.
- Query against stale index tra ve warning unless `--allow-stale` flag.

### Dau Ra Khi Hoan Thanh
```
relay_kit_v3/
  context_graph.py         # Skill dependency graph builder
  semantic_index.py        # Embedding model adapter (optional)
  search_router.py         # Tiered search dispatcher

tests/
  context_search_eval.json # 20+ test cases voi expected ranking
  test_context_search_eval.py  # Automated eval runner
```

**context_search_eval.json mau:**
```json
[
  {
    "query": "xu ly loi network timeout",
    "expected_top_3": ["api-integration", "mmo-http-api-automation", "protocol-fingerprint-spoofing"],
    "tier": "all"
  },
  {
    "query": "debug memory leak",
    "expected_top_3": ["debug-hub", "root-cause-debugging", "windows-native-internals"],
    "tier": "all"
  }
]
```

---

## V5.3 — Field Journal (Evidence-Backed Memory)

**Muc tieu:** Ghi nho kinh nghiem tu cac session truoc, nhung KHONG tu dong promote. Moi entry phai co evidence, va chi duoc activate sau khi qua gate.

> [!CAUTION]
> KHONG cho AI tu sua skill/template. Memory la append-only. Promote chi khi co human approval hoac strict evidence gate pass.

### Deliverables

| # | Feature | File | Dau ra ky vong |
|---|---|---|---|
| 5.3.1 | **Journal Capture** | `relay_kit_v3/field_journal.py` [NEW] | Capture candidate automatically ONLY when completion evidence exists (test pass, command output hash, verified fix). Neu khong co evidence, user/agent phai chay `relay-kit journal capture .` manually. Ghi vao `.relay-kit/memory/journal.jsonl` (append-only). |
| 5.3.2 | **Evidence Quality Gate** | `relay_kit_v3/evidence_quality.py` [NEW] | Tu choi ghi vao journal neu: khong co test pass, khong co command output, hoac fix chua duoc verify. Moi entry phai co `evidence_ref` tro den output thuc. Memory ma khong co evidence thi khong vao journal. |
| 5.3.3 | **Pattern Retriever** | `relay_kit_v3/pattern_retriever.py` [NEW] | Khi `debug-hub` bat dau, scan journal cho entries co `error_signature` tuong tu. Inject vao context (khong sua prompt template). Chi inject entries co `confidence >= medium`. |
| 5.3.4 | **Journal CLI** | `relay_kit_v3/cli/journal.py` [NEW] | `relay-kit journal list .` — hien thi entries. `relay-kit journal inspect . --id <id>` — xem chi tiet. `relay-kit journal promote . --id <id>` — human approve de nang confidence. `relay-kit journal capture .` — manual capture khi auto-capture khong du evidence. |
| 5.3.5 | **No Auto-Promote Guard** | `relay_kit_v3/field_journal.py` | Auto-promote DISABLED hoan toan trong V5. Entries moi tao luon co `status: candidate`, `confidence: low`. Chi chuyen sang `promoted` khi human chay `relay-kit journal promote . --id <id>`. Strict gate CHI duoc recommend promotion (ghi flag `promotion_recommended: true`), KHONG duoc tu dong promote. |

### Acceptance Criteria
- Journal chi auto-capture khi completion evidence ton tai. Khong co evidence = khong vao journal (user phai chay manual capture).
- Sau 3 lan debug thanh cong CO evidence, `.relay-kit/memory/journal.jsonl` co 3 entries voi day du fields.
- Entry khong co `evidence_ref` bi reject voi error message ro rang.
- Pattern retriever inject context TRUOC khi debug-hub bat dau, KHONG phai sau.
- `relay-kit journal list .` hien thi bang co: id, date, error_signature, status, confidence.
- KHONG co code path nao cho phep tu dong promote entry. Strict gate CHI ghi `promotion_recommended: true`, human moi duoc approve.
- KHONG co code path nao cho phep tu dong sua `templates/skills/` hoac SKILL.md files.

### 5.3.6 — Journal Redaction Gate

| # | Feature | File | Dau ra ky vong |
|---|---|---|---|
| 5.3.6 | **Journal Redaction Gate** | `relay_kit_v3/journal_redaction.py` [NEW] | Redact secrets, tokens, emails, absolute sensitive paths truoc khi ghi vao journal. Giu raw evidence hash, KHONG giu raw secret content. |

**Acceptance:**
- Journal capture rejects hoac redacts: API keys, bearer tokens, cookies, private keys, emails.
- Redaction duoc test voi fixtures (`tests/journal_redaction_fixtures.json`).
- Redacted entry van giu `evidence_ref` hash de truy vet.

### Dau Ra Khi Hoan Thanh
```
relay_kit_v3/
  field_journal.py         # Capture + append-only write + no-auto-promote
  evidence_quality.py      # Quality gate cho journal entries
  pattern_retriever.py     # Retrieve + inject relevant entries
  cli/
    journal.py             # CLI: list, inspect, promote

.relay-kit/
  memory/
    journal.jsonl          # Append-only journal entries
```

**journal.jsonl entry mau:**
```json
{
  "id": "j-20260707-001",
  "date": "2026-07-07T16:00:00Z",
  "error_signature": "TypeError: Cannot read property 'map' of undefined",
  "root_cause": "API response changed from array to object wrapper",
  "fix_applied": "Added response.data unwrap before .map()",
  "evidence_ref": "sha256:def456...",
  "source_session": "d93cee11-60f2-49b4-8be6-00ee2a7a34e4",
  "confidence": "low",
  "status": "candidate",
  "retrieve_count": 0,
  "promote_history": []
}
```

---

## V5.4 — Multi-Lane Runtime

**Muc tieu:** Lane locks, event bus, delegation ledger. Static Pulse dashboard nang cap truoc. FastAPI dashboard sau.

> [!IMPORTANT]
> KHONG lam ImGui desktop client trong V5. Day la experiment cho V6 neu can.

### Deliverables

| # | Feature | File | Dau ra ky vong |
|---|---|---|---|
| 5.4.1 | **Lane Lock Manager** | `relay_kit_v3/lane_lock.py` [NEW] | File-level mutex dung SQLite WAL. Lock record: `lane_id`, `file_path`, `agent_id`, `acquired_at`, `ttl`. Auto-expire sau TTL. |
| 5.4.2 | **Event Ledger** | `relay_kit_v3/event_ledger.py` [NEW] | Append-only event log dung SQLite WAL. Events: `lane_started`, `file_locked`, `file_unlocked`, `task_completed`, `task_failed`, `handoff`. |
| 5.4.3 | **Delegation Lifecycle** | `relay_kit_v3/delegation_control.py` [MODIFY] | Tich hop voi lane lock: truoc khi delegate, check lock. Sau khi delegate xong, release lock + ghi event. |
| 5.4.4 | **Multi-Lane CLI** | `relay_kit_v3/cli/lane.py` [NEW] | `relay-kit lane run . --agents 3 --tasks tasks.json` — fork sub-processes voi lane lock protection. |
| 5.4.5 | **Pulse Dashboard Upgrade** | `relay_kit_v3/pulse.py` [MODIFY] | Them lane status, lock status, event timeline vao pulse report. `relay-kit pulse build .` xuat static HTML dashboard. |
| 5.4.6 | **FastAPI Live Dashboard** | `relay_kit_v3/dashboard/` [NEW] | `relay-kit dashboard .` — FastAPI + HTMX, doc tu event ledger, hien thi real-time. Khong can build step. OPTIONAL — chi lam sau khi 5.4.1-5.4.5 on dinh. |

### 5.4.0 — Lane Simulation Mode (TRUOC khi spawn agent that)

| # | Feature | File | Dau ra ky vong |
|---|---|---|---|
| 5.4.0 | **Lane Simulation** | `relay_kit_v3/lane_simulator.py` [NEW] | `relay-kit lane simulate . --tasks tasks.json --agents 3`. Mo phong lane lock truoc khi fork agent that. Detect lock conflicts, estimate token budget, canh bao high-reasoning agent count. |

**Acceptance:**
- Simulation detects lock conflicts TRUOC khi spawn agents.
- Simulation estimates token budget va high-reasoning agent count.
- `relay-kit lane simulate` khong ton quota, chi doc tasks.json va .relay-kit/state/.

### Acceptance Criteria
- 3 agent chay song song khong ghi de file cua nhau (verified bang file hash check sau khi chay).
- `relay-kit lane run` terminate gracefully neu 1 agent crash (khong zombie process).
- Event ledger co >= 10 events sau 1 lan chay multi-lane.
- `relay-kit pulse build .` xuat file HTML co lane status table.
- Lock auto-expire sau TTL (default 5 phut). Test bang cach set TTL = 2s va verify unlock.

### Dau Ra Khi Hoan Thanh
```
relay_kit_v3/
  lane_lock.py             # SQLite WAL file-level mutex
  event_ledger.py          # Append-only event log
  cli/
    lane.py                # Multi-lane CLI runner
  dashboard/               # OPTIONAL FastAPI + HTMX
    __init__.py
    app.py
    templates/
      index.html

.relay-kit/
  runtime/
    lane-locks.db          # SQLite WAL lock database
    event-ledger.db        # SQLite WAL event log
```

---

## Dependency Graph

```
V5.0 (CLI Modularization) ---- prerequisite cho tat ca
  |
  +---> V5.1 (Trusted Extensions) --- dung command registry de register extension commands
  |
  +---> V5.2 (Context Search) ------- dung command registry cho search commands
  |         |
  |         +---> V5.3 (Field Journal) --- dung graph ranking de retrieve patterns
  |
  +---> V5.4 (Multi-Lane) ----------- dung command registry + event model
              |
              +--- V5.3 (evidence gate controls lane handoff)
```

> V5.0 la **prerequisite**. Phai lam truoc.
> V5.1, V5.2, V5.4 co the lam song song sau khi V5.0 done.
> V5.3 phu thuoc V5.2 (context graph cho pattern retrieval).
> V5.5 la phase cuoi — chi bat dau khi V5.0-V5.4 feature-complete.

---

## V5.5 — Runtime Proof & Release Hardening

**Muc tieu:** Bien V5 tu feature-complete thanh release-proven. Phase nay KHONG them feature moi, chi them co che chung minh.

> [!IMPORTANT]
> V5.5 la phase bat buoc truoc khi release. Khong co V5.5, V5 chi la "code xong" chu chua phai "song duoc".

### Deliverables

| # | Feature | File | Dau ra ky vong |
|---|---|---|---|
| 5.5.1 | **V5 Release Doctor** | `relay_kit_v3/v5_release_doctor.py` [NEW] | Chay tat ca 12 Global Done gates trong 1 lenh. Output: pass/fail cho tung gate + tong ket. |
| 5.5.2 | **V4-to-V5 Migration Smoke** | `tests/test_v4_migration.py` [NEW] | Lay 1 V4 project, chay V5 upgrade, verify: state khong mat, skills khong thay doi, commands van chay. |
| 5.5.3 | **Generated Surface Drift Detector** | `relay_kit_v3/surface_drift.py` [NEW] | So sanh generated .agent/skills/ voi canonical registry. Phat hien skill bi outdated hoac missing. |
| 5.5.4 | **Extension Install/Remove Rollback Test** | `tests/test_extension_rollback.py` [NEW] | Install extension, remove no, verify repo tro ve trang thai sach (no leftover files). |
| 5.5.5 | **Journal Redaction Fixtures** | `tests/journal_redaction_fixtures.json` [NEW] | 20+ test cases voi API keys, tokens, emails, paths. Verify redaction hoat dong dung. |
| 5.5.6 | **Lane Concurrency Stress Test** | `tests/test_lane_concurrency.py` [NEW] | 10-lane simulation, verify: lock conflicts detected deterministically, no file corruption. |
| 5.5.7 | **Public Install Docs Refresh** | `docs/relay-kit-v5-upgrade.md` [NEW] | Huong dan upgrade tu V4, fresh install cho codex/claude/antigravity, troubleshooting. |

### Acceptance Criteria
- `relay-kit release doctor .` pass toan bo 12 gates.
- Fresh project install works cho codex/claude/antigravity.
- Existing V4 project upgrade KHONG mat state.
- Extension install rollback de lai repo sach.
- 10-lane simulation detect conflicts deterministically.
- All redaction fixtures pass.

---

## Thu Tu Thuc Hien

| Sprint | Phase | Uu tien | Ly do |
|---|---|---|---|
| 1 | V5.0.1 + V5.0.2 + V5.0.4 | Critical | Tach CLI, tao schema, viet compat tests + golden snapshots |
| 2 | V5.0.3 + V5.0.5 | Critical | CLI engine + thin facade |
| 3 | V5.1.1 + V5.1.2 + V5.1.4 + V5.1.7 | High | Extension format + trust + gauntlet + permissions |
| 4 | V5.1.3 + V5.1.5 + V5.1.6 + V5.2.1 + V5.2.2 | High | Extension installer/quarantine + graph ranker + BM25 |
| 5 | V5.2.3 + V5.2.4 + V5.2.5 + V5.2.6 + V5.2.7 | High | Embedding adapter + tiered router + eval suite + budget + index freshness |
| 6 | V5.3.1 + V5.3.2 + V5.3.3 + V5.3.6 | Medium | Journal capture + evidence gate + retriever + redaction |
| 7 | V5.3.4 + V5.3.5 | Medium | Journal CLI + no-auto-promote guard |
| 8 | V5.4.0 + V5.4.1 + V5.4.2 + V5.4.3 | Medium | Lane simulation + lock + event ledger + delegation |
| 9 | V5.4.4 + V5.4.5 | Low | Multi-lane CLI + pulse upgrade |
| 10 | V5.4.6 | Optional | FastAPI dashboard |
| 11 | V5.5 (all) | Critical | Runtime proof + release hardening — KHONG skip |

---

## Tong Ket So Lieu

| Metric | V4 hien tai | V5 muc tieu |
|---|---|---|
| Canonical skills | 74 | 74+ (trusted extension packs) |
| Adapter skill dirs | 105 | 105+ (generated surface) |
| CLI public facade | ~2.9k dong viet tay | < 500 dong (phase target), stretch < 200 |
| Context search | Keyword | Tiered: lexical+graph (default) / embedding (optional) / bge-m3 (pro) |
| Agent memory | Continuity/state artifacts (no learned pattern journal) | Append-only evidence-backed journal + gated retrieval |
| Max concurrent agents | 1 (co skill `team` nhung chua co runtime lock) | Bounded N, default 2, configurable by delegation policy |
| Extension system | Khong co | Trusted packs voi hash/signature/gauntlet/quarantine |
| GUI | Pulse static report | Pulse upgrade + optional FastAPI dashboard |

---

## Nhung Thu KHONG Lam Trong V5

| Feature | Ly do khong lam |
|---|---|
| ImGui Desktop Client | Event model chua on dinh, uu tien runtime truoc GUI |
| AI tu sua skill/template | Tao drift va overfit, vi pham governed runtime |
| Plugin install tu do (khong gate) | Cua dua prompt doc hai vao Relay-kit |
| Auto-promote memory entries | Can human approval hoac strict evidence gate |
| Xoa `relay_kit_public_cli.py` | Giu lam thin facade, chi giam code, khong xoa |
