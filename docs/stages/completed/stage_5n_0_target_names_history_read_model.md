# STAGE 5N.0 — Target Names History Read Model

Status: active task
Stage: 5N.0
Type: feature/storage-read/service
Depends on: `user_identity_history`, `users`, `sync_targets`, `chats`, local SQLite read path; no active stage prerequisites.

---

## 0. CODEX ENTRY CONTRACT

Read `AGENTS.md` first. Then read `.skills/stage-reviewer/SKILL.md`, `.skills/architecture-guard/SKILL.md`, `.skills/stage-completion-auditor/SKILL.md`, and this stage file. Apply `stage-reviewer` before implementation changes, `architecture-guard` before reporting, and `stage-completion-auditor` before claiming complete.

Do not implement CLI command wiring in this stage. Do not execute Stage 5N.1 or 5N.2.

## 1. PURPOSE

Create the read-only storage/query/service foundation for a future:

```bash
tg-msg-manager target names <target>
```

The stage must expose local target-name history facts without Telegram calls or SQLite writes.

Known storage gap: current SQLite stores user display/username snapshots in `user_identity_history`, but does not store chat/channel title history. `chats.title` is current metadata only.

## 2. FILES TO INSPECT

Required:

- `AGENTS.md`
- `.skills/stage-reviewer/SKILL.md`
- `.skills/architecture-guard/SKILL.md`
- `.skills/stage-completion-auditor/SKILL.md`
- `TASK_CODEX_TARGET_NAMES_HISTORY_STAGE_FILES.md`
- `docs/architecture/README.md`
- `docs/architecture/ARCHITECTURE_RULES.md`
- `docs/architecture/STORAGE_CONTRACT_SPLIT_MAP.md`
- `docs/architecture/SQLITE_SCHEMA_SPLIT_MAP.md`
- `docs/architecture/SQLITE_MESSAGE_ID_AUDIT.md`
- `docs/development/PRIVACY_AND_SENSITIVE_ARTIFACTS.md`
- `tg_msg_manager/infrastructure/storage/_sqlite_identity.py`
- `tg_msg_manager/infrastructure/storage/read/targets.py`
- `tg_msg_manager/infrastructure/storage/read/__init__.py`
- `tg_msg_manager/infrastructure/storage/_sqlite_read_path.py`
- `tg_msg_manager/infrastructure/storage/contracts/common.py`
- `tg_msg_manager/infrastructure/storage/records.py`
- `tg_msg_manager/infrastructure/storage/schema/tables.py`
- `tests/infrastructure/storage/test_storage_sqlite.py`

Allowed to create or edit:

- `tg_msg_manager/infrastructure/storage/read/target_names.py`
- `tg_msg_manager/infrastructure/storage/read/__init__.py`
- `tg_msg_manager/infrastructure/storage/_sqlite_read_path.py`
- `tg_msg_manager/infrastructure/storage/contracts/target_names_storage.py`
- `tg_msg_manager/infrastructure/storage/contracts/__init__.py`
- `tg_msg_manager/infrastructure/storage/records.py`
- `tg_msg_manager/services/target_names/__init__.py`
- `tg_msg_manager/services/target_names/models.py`
- `tg_msg_manager/services/target_names/query.py`
- `tests/infrastructure/storage/test_target_names_history_storage.py`
- `tests/services/target_names/test_target_names_query.py`
- `docs/stages/reports/STAGE_5N_0_TARGET_NAMES_HISTORY_READ_MODEL_REPORT.md`

## 3. HARD PROHIBITIONS

- Do not add CLI commands, argparse wiring, or user docs in this stage.
- Do not change SQLite schema, `PRAGMA user_version`, migrations, indexes, or compatibility rewrites.
- Do not write to SQLite from the new service/query path.
- Do not add raw SQL outside `tg_msg_manager/infrastructure/storage/`.
- Do not add business logic to protected service facades or compatibility wrappers.
- Treat `_sqlite_read_path.py` and `read/__init__.py` as mechanical wiring only.
- Do not import CLI from service/core/infrastructure modules.
- Do not call Telegram or resolve live entities.
- Do not read private artifacts, real DB files, sessions, credentials, logs, exports, screenshots, or media.
- Do not add analytics, OSINT, profiling, identity claims, or LLM behavior.
- Do not change existing export/db-export/report output contracts.

## 4. ATOMIC IMPLEMENTATION TASKS

1. Confirm the current storage facts: `user_identity_history` has `observed_at`, `author_name`, `username`; `chats` has current `title` only.
2. Add narrow storage DTOs/contracts for local target-name lookup and history reads. Keep `BaseStorage` untouched unless unavoidable; if touched, only add protocol-compatible declarations.
3. Add read-side SQL under `infrastructure/storage/read/target_names.py` for local target resolution by numeric id and locally stored username, with ambiguity detection.
4. Add service/query logic under `services/target_names/` to normalize snapshots into fields `username`, `display_name`, and `title`, derive `old_value` from previous observed value, filter duplicate consecutive values, and sort ascending.
5. Represent missing title history explicitly as empty history with current title when a chat target is found; do not synthesize fake title changes.
6. Add focused storage and service tests using temporary synthetic SQLite data only.

## 5. REQUIRED DOCS

No user docs in this stage. The report must document the storage blocker: chat/channel title history is not available from current schema.

## 6. TESTS / VERIFICATION

Run:

```bash
python3 -m unittest tests.infrastructure.storage.test_target_names_history_storage -q
python3 -m unittest tests.services.target_names.test_target_names_query -q
python3 -m unittest tests.infrastructure.storage.test_storage_sqlite -q
git diff --check
```

Desired before closing the full 5N workflow:

```bash
make test
make verify
```

Do not claim checks passed unless actually run.

## 7. REPORT

Create `docs/stages/reports/STAGE_5N_0_TARGET_NAMES_HISTORY_READ_MODEL_REPORT.md` in Russian.

Include: status, files added/modified/deleted, storage facts found, schema changed yes/no, Telegram calls added yes/no, tests added, verification run/not run, deferred items, privacy boundary confirmation, and `stage-reviewer: applied from .skills/stage-reviewer/SKILL.md`, `architecture-guard: applied from .skills/architecture-guard/SKILL.md`, `stage-completion-auditor: applied from .skills/stage-completion-auditor/SKILL.md`.

## 8. COMPLETION CRITERIA

- Local read model resolves known targets without Telegram access.
- User username/display-name history is derived from local snapshots.
- Chat/channel title history gap is explicit and not hidden.
- Unknown and ambiguous target states are represented for Stage 5N.1.
- Focused tests pass or failures are recorded.
- Required report exists.
- lifecycle cleanup is completed according to AGENTS.md.

## 9. OUTPUT LIMITS

Final response must follow `AGENTS.md`, be in Russian, avoid full diffs, and mention only changed files, checks, preservation, notes, and stage status.
