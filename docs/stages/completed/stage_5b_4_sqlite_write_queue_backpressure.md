# STAGE 5B.4 — SQLite Write Queue Backpressure

Status: active task
Stage: 5B.4
Type: implementation
Depends on: `tg_msg_manager/infrastructure/storage/sqlite.py`; `tg_msg_manager/infrastructure/storage/_sqlite_write_path.py`

---

## 0. CODEX ENTRY CONTRACT

1. Read `AGENTS.md`.
2. Read this stage file only.
3. Apply `stage-reviewer` before implementation. If no tool exists, read `.skills/stage-reviewer/SKILL.md`.
4. Apply `architecture-guard` because this touches storage write behavior. If no tool exists, read `.skills/architecture-guard/SKILL.md`.
5. Do not start any other active 5B stage.

## 1. PURPOSE

Prevent unbounded SQLite write queue growth and expose queue pressure with telemetry while preserving public storage behavior and schema.

Current risk to address:

- `SQLiteStorage` uses an unbounded `asyncio.Queue()`.
- `save_message()` and `save_messages()` call `put_nowait()`.
- A fast producer can grow memory while the single writer drains batches of 500.

## 2. FILES TO INSPECT

Inspect only:

- `AGENTS.md`
- `docs/architecture/README.md`
- `docs/architecture/ARCHITECTURE_RULES.md`
- `docs/architecture/SQLITE_WRITE_PATH_SPLIT_MAP.md`
- `tg_msg_manager/infrastructure/storage/sqlite.py`
- `tg_msg_manager/infrastructure/storage/_sqlite_write_path.py`
- `tg_msg_manager/infrastructure/storage/write/message_writer.py`
- `tg_msg_manager/infrastructure/storage/write/transaction.py`
- `tg_msg_manager/infrastructure/storage/contracts/common.py`
- `tg_msg_manager/core/config.py` only if configuration is strictly needed
- `config.example.json` only if configuration is changed
- `README.md` only if configuration is changed
- `tests/infrastructure/storage/test_storage_sqlite.py`
- `tests/core/test_config.py` only if configuration is changed

May create:

- focused tests under `tests/infrastructure/storage/`;
- `docs/stages/reports/STAGE_5B_4_SQLITE_WRITE_QUEUE_BACKPRESSURE_REPORT.md`.

## 3. HARD PROHIBITIONS

- Do not change SQLite schema or migrations.
- Do not add raw SQL outside storage modules.
- Do not change message identity rules.
- Do not change existing storage method signatures unless all callers and contracts remain backward-compatible.
- Do not add CLI flags.
- Do not add business logic to compatibility wrappers.
- Do not make services depend on storage implementation details.
- Do not drop queued messages silently.

## 4. ATOMIC IMPLEMENTATION TASKS

1. Replace the unbounded write queue with a bounded queue using an internal default limit.
2. Preserve async method signatures for `save_message()`, `save_messages()`, and `flush()`.
3. Replace `put_nowait()` with awaited queue insertion so producers apply backpressure instead of growing memory.
4. Add telemetry counters for queue depth or wait events using `tg_msg_manager/core/telemetry.py`.
5. Keep background commit batch size behavior unchanged unless a focused test proves the change is behavior-preserving.
6. Add tests proving:
   - save calls wait instead of dropping data when the queue is full;
   - `flush()` still drains all queued writes;
   - close still drains writes before closing the connection.

## 5. REQUIRED DOCS

Update docs only if a new setting is introduced:

- `README.md`
- `config.example.json`

If no setting is introduced, no user docs are required.

Always create:

- `docs/stages/reports/STAGE_5B_4_SQLITE_WRITE_QUEUE_BACKPRESSURE_REPORT.md`

## 6. TESTS / VERIFICATION

Run:

- `pytest tests/infrastructure/storage/test_storage_sqlite.py`
- `pytest tests/services/test_services.py`
- `python3 -m compileall tg_msg_manager`
- `ruff check tg_msg_manager tests`

If config changes:

- `pytest tests/core/test_config.py`

## 7. REPORT

Report in Russian:

- queue limit decision and where it lives;
- telemetry added;
- behavior preserved;
- tests/checks run;
- `stage-reviewer` and `architecture-guard` application.

## 8. COMPLETION CRITERIA

- Write queue is bounded.
- Producers await when queue capacity is exhausted.
- No queued writes are dropped silently.
- Storage API, SQLite schema, and CLI behavior are preserved.
- Required tests pass or blockers are documented.
- lifecycle cleanup is completed according to AGENTS.md.

## 9. OUTPUT LIMITS

Final response must follow `AGENTS.md` final structure, be in Russian, and stay under 1200 characters.
