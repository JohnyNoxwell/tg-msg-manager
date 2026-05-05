# Architecture Rules

Last updated: 2026-05-05

## 1. CLI Thin Only

CLI modules may:

- parse arguments;
- build runtime context;
- call services;
- render output;
- route menu choices.

CLI modules must not:

- embed raw SQL;
- implement Telegram traversal;
- implement deep-context clustering;
- own export-file formatting rules.

## 2. Services Do Not Contain SQL

- `services/*` use storage interfaces or grouped storage methods.
- SQL belongs under `tg_msg_manager/infrastructure/storage/`.
- New write operations go into `infrastructure/storage/write/`.
- New read queries go into `infrastructure/storage/read/`.

## 3. Storage Does Not Import Services

- storage may depend on models/records/helpers inside infrastructure/core;
- storage must not import `tg_msg_manager.services.*`.

## 4. Context Logic Is Isolated

- `tg_msg_manager/services/context/engine.py` is a facade.
- reply-chain, candidate-window, cluster building, dedup state, and scope policy live in dedicated context modules.
- context logic must not write files or call CLI code.

## 5. Export Logic Is Orchestration Only

- `tg_msg_manager/services/export/service.py` orchestrates sync flow.
- export artifact formatting/writing stays in `services/db_exporter.py` and `services/db_export/`.
- sync orchestration must not grow raw SQL branches.

## 6. Analytics Read Boundary

- future analytics queries belong under `tg_msg_manager/infrastructure/storage/read/analytics/`.
- analytics reads normalized local data only.
- no new analytics feature should grow export/context hot-path services.

## 7. No New Features In Hot-Path Compatibility Files

Do not add new product logic directly into:

- `tg_msg_manager/services/exporter.py`
- `tg_msg_manager/services/context_engine.py`
- `tg_msg_manager/services/private_archive.py`
- `tg_msg_manager/infrastructure/storage/_sqlite_write_path.py`
- `tg_msg_manager/infrastructure/storage/_sqlite_sync_state.py`
- `tg_msg_manager/infrastructure/storage/_sqlite_read_path.py`

Allowed changes there:

- thin wrappers;
- import forwarding;
- dependency wiring;
- compatibility-only bug fixes.

## 8. Telegram And Filesystem Boundaries

- no raw Telegram calls outside adapters/fetch layers (`core/telegram/`, sync/context fetch helpers);
- no direct filesystem writes outside writer/export modules.

## 9. Message Identity Rule

- Telegram message identity is `(chat_id, message_id)`.
- cross-table links must not rely on bare `message_id` when chat scope matters.

## 10. Schema Rule

- no schema change without an explicit migration note/documentation update.

## 11. Test Rule

Every architecture change needs:

- unit coverage for new pure logic;
- storage/fixture coverage when persistence changes;
- CLI regression coverage when command surface changes.
