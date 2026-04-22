# Fact-check refresh cho `relay_kit_review_vietnamese.md` (2026-04-22)

- Nguon review doi chieu: `C:\Users\b0ydeptrai\OneDrive\May tinh\relay_kit_review_vietnamese.md`
- Thoi diem refresh: `2026-04-22` (Asia/Bangkok)
- Repo kiem tra: `C:\Users\b0ydeptrai\OneDrive\Documents\relay-kit`
- Muc tieu: cap nhat lai claim ky thuat theo trang thai hien tai sau checkpoint.

## Bang Dung/Sai/Chua xac minh (refresh)

| # | Claim tu review cu | Ket qua 2026-04-22 | Bang chung | Ghi chu |
|---|---|---|---|---|
| 1 | Phien ban dang xet o commit `b1e86e2` | Sai (da cu) | `git rev-parse --short HEAD` -> `c3ebcb5` | Commit trong review cu khong con la HEAD hien tai. |
| 2 | `python scripts/validate_runtime.py` chay pass | Dung | `py -3.12 scripts\validate_runtime.py` -> `Runtime validation passed.` | Van pass sau checkpoint. |
| 3 | `validate_runtime.py` dai `422` dong | Sai | `(Get-Content scripts\validate_runtime.py | Measure-Object -Line).Lines` -> `395` | So dong trong review cu da stale. |
| 4 | Registry co `46` skill | Sai | `len(relay_kit_v3.registry.skills.ALL_V3_SKILLS)` -> `49` | Runtime skill set da mo rong. |
| 5 | Manifest/layer khop runtime skill set | Dung | `manifest_unique=49`, `registry=49` | Khop o cap do layer-model vs registry. |
| 6 | `relay_kit_legacy.py` ~93KB | Dung | `Get-Item relay_kit_legacy.py` -> `Length 93672` | Van ~93KB. |
| 7 | `relay_kit_v3/registry/skills.py` = `90,001` bytes va `1,495` dong | Sai | file hien tai: `1155` bytes, `30` dong | Registry da split module, claim cu khong con dung. |
| 8 | Khong co test suite runtime | Sai | Thu muc `tests/` ton tai, `pytest -q tests` -> `10 passed` | Da co runtime test suite o root. |
| 9 | `__pycache__` da bi commit vao git | Sai | `git ls-files | Select-String '__pycache__'` -> khong co ket qua | Khong thay `__pycache__` tracked. |
| 10 | Token BMAD (`create_bmad_upgrade`, `bmad-core`, `bmad-lite`) con trong runtime source chinh | Sai (voi source chinh) | `git grep ... -- relay_kit.py relay_kit_v3/generator.py scripts` -> `NO_MATCH_IN_ACTIVE_RUNTIME` | Van co vet tich trong `build/lib` va docs lich su, nhung khong con trong runtime source chinh. |
| 11 | Co 3 entrypoint: `relay_kit.py`, `relay_kit_legacy.py`, `relay_kit_public_cli.py` | Dung | `Test-Path` ca 3 file -> `True` | Khop. |
| 12 | Skill folder `54` vs registry `46` | Sai | `.claude/.agent/.codex` hien tai moi ben `57` skill folders; registry la `49` | So lieu cu khong con dung. |
| 13 | Co SRS-first contract/policy/guard trong runtime | Dung | Ton tai `.relay-kit/contracts/srs-spec.md`, `.relay-kit/state/srs-policy.json`, `scripts/srs_guard.py` | Khop. |
| 14 | Migration guard + allowlist dang dung | Dung | `py -3.12 scripts\migration_guard.py . --json` -> `findings_count: 0` | Guard van xanh. |
| 15 | Context continuity co 4 lenh `checkpoint/rehydrate/handoff/diff-since-last` | Dung | `py -3.12 scripts\context_continuity.py --help` | Du 4 subcommand. |
| 16 | `validate_runtime` check gauntlet + guard + context + adapter/bundle generation | Dung | `scripts/validate_runtime.py` co cac ham `validate_skill_gauntlet`, `validate_migration_guard`, `validate_srs_guard`, `validate_context_continuity_utility`, `validate_adapter_targets`, `validate_generated_bundle`, ... | Pham vi check hien tai rong hon ban cu. |
| 17 | License la `Proprietary` | Dung | `pyproject.toml` co `license = { text = "Proprietary" }` | Khop. |
| 18 | So sao GitHub Relay-kit/BMAD | Chua xac minh trong pass nay | Khong truy van API ngoai trong lan refresh local-only | Metrics ben ngoai de stale, can run API check rieng neu can. |

## Ket luan nhanh

- Review cu dung mot phan huong ky thuat, nhung nhieu so lieu da stale sau cac dot chinh sua va checkpoint.
- Sau checkpoint ngay `2026-04-22`, can uu tien claims co tinh tai lap bang command local; tranh dong bang cac so lieu de thay doi nhanh (line count, star count, ...).
