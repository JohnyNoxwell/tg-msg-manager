# Architecture Rules

Last updated: 2026-05-04

## 1. No New Features In Hot-Path Files

Do not add new product logic directly into these files:

- `tg_msg_manager/cli.py`
- `tg_msg_manager/services/exporter.py`
- `tg_msg_manager/services/context_engine.py`
- `tg_msg_manager/services/db_exporter.py`
- `tg_msg_manager/infrastructure/storage/_sqlite_read_path.py`
- `tg_msg_manager/infrastructure/storage/_sqlite_write_path.py`

Allowed changes in those files:

- thin compatibility wrappers;
- dependency wiring;
- orchestration and dispatch;
- import forwarding;
- small bug fixes that preserve behavior.

Required direction:

- CLI parsing goes into `tg_msg_manager/cli_parser.py`.
- CLI command handlers go into `tg_msg_manager/cli_commands.py`.
- Interactive menu flows go into `tg_msg_manager/cli_menu.py`.
- Sync-domain helpers go into `tg_msg_manager/services/sync/`.
- Context-domain helpers go into `tg_msg_manager/services/context/`.
- DB export formatting/state helpers go into `tg_msg_manager/services/db_export/`.
- SQLite read queries go into `tg_msg_manager/infrastructure/storage/read/`.

## 2. Ingestion And Analysis Stay Separate

Ingestion means:

- Telegram sync/export/update flows;
- PM archive flows;
- retry replays of ingestion work;
- cleanup/delete operations that mutate Telegram or local persistence.

Analysis means:

- graph analytics;
- interaction metrics;
- linguistic statistics;
- temporal statistics;
- read-only profile/report generation over stored local data.

Rules:

- Analysis must read from storage/read-side, not from live Telegram traversal.
- Analysis must not mutate Telegram.
- Analysis modules must not open raw SQLite connections from the presentation layer.

Recommended target package for future analysis work:

```text
tg_msg_manager/analysis/
    graph_builder.py
    interaction_metrics.py
    temporal_activity.py
    linguistic_stats.py
    reports.py
```

## 3. CLI Is Presentation And Dispatch Only

`tg_msg_manager.cli` and related CLI modules may:

- parse arguments;
- build runtime context;
- call services;
- render output;
- route menu choices.

CLI modules must not:

- embed raw SQL;
- implement Telegram traversal algorithms;
- implement DB export formatting rules;
- implement deep-mode clustering logic;
- grow command-specific business logic inline inside `cli.py`.

## 4. Storage Interface Owns Persistence Boundaries

Rules:

- Services use storage interfaces and grouped read/write methods.
- Services do not embed raw SQL.
- New read queries go into the correct file under `infrastructure/storage/read/`.
- New write queries go into the appropriate storage write/sync module.
- Analysis code should consume storage/read-side APIs instead of opening SQLite directly.
- Telegram messages are identified by the composite key `(chat_id, message_id)`.
- Storage links and cross-table references must not rely on bare `message_id` when chat scope is ambiguous.
- `messages.author_name` is historical message-time data and must not be rewritten retroactively.
- Current user naming lives outside `messages`, in `users.current_author_name`.
- Author-name changes are tracked in `user_identity_history`.

## 5. Every New Feature Needs A Test Boundary

Minimum expectations:

- at least one unit test for pure logic;
- at least one storage/fixture integration test when persistence is crossed;
- no live Telegram dependency in the standard test suite;
- a CLI smoke check if command surface changes.

## 6. Documentation Must Track Architecture Changes

Update rules:

- `README.md` only for user-visible behavior;
- `COMMANDS.md` only for command-surface changes;
- `docs/refactor/` and architecture docs for internal boundaries;
- `ROADMAP.md` / `TODO.md` only when priorities change.

`PROJECT_ARCHITECTURE_OVERVIEW.md` is a snapshot, not the only source of truth.
