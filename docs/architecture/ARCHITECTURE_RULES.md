# Architecture Rules

Last updated: 2026-06-17

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

## Application Runtime Assembly Boundary

`tg_msg_manager/application/` is the application/runtime assembly layer. It may
wire core models, infrastructure resources, services, process/session
lifecycle, and Telegram adapters into explicit runtime/session objects.

Application runtime modules may:

- construct and own runtime/session assembly;
- coordinate process lock, logging, telemetry reset, storage lifecycle, and
  optional Telegram client lifecycle;
- create service bundles from explicit runtime resources;
- provide headless entrypoints that CLI or other adapters can call.

Stable non-CLI runtime entrypoint:

- `from tg_msg_manager.application import ApplicationSession`
- pass `needs_client=False` for local/headless runtime assembly that must not
  construct a Telegram client.

Application runtime modules must not:

- render CLI output or parse CLI arguments;
- import `tg_msg_manager.cli`, `cli_commands`, `cli_menu`, or `cli_parser`;
- contain raw SQL or SQLite schema changes;
- add export, dataset, media, discussion, analytics, OSINT, profiling, or
  LLM-dependent product logic.

CLI remains an adapter over this boundary: parse args, route menu choices,
render output, call runtime/session APIs.

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
- `tg_msg_manager/services/db_export/service.py` is a facade only.
- `tg_msg_manager/services/channel_export/service.py` is a channel export orchestration facade.
- export artifact formatting/writing stays in dedicated `services/db_export/` components.
- channel export result, manifest, included-file, media, discussion, payload, and state logic must stay in focused `services/channel_export/` components.
- sync orchestration must not grow raw SQL branches.

## 6. Analytics Read Boundary

- future analytics queries belong under `tg_msg_manager/infrastructure/storage/read/analytics/`.
- analytics reads normalized local data only.
- no new analytics feature should grow export/context hot-path services.

## Analytics Boundary

Future analytics must be implemented as read-only services over normalized storage projections.

Forbidden:

- adding analytics to `ExportService`
- adding analytics to `DBExportService`
- adding analytics to `ContextEngine`
- adding analytics SQL to the service layer
- adding Telegram fetches to analytics

## 7. No New Features In Hot-Path Compatibility Files

Do not add new product logic directly into:

- `tg_msg_manager/services/exporter.py`
- `tg_msg_manager/services/context_engine.py`
- `tg_msg_manager/services/db_exporter.py`
- `tg_msg_manager/services/private_archive.py`
- `tg_msg_manager/infrastructure/storage/_sqlite_write_path.py`
- `tg_msg_manager/infrastructure/storage/_sqlite_sync_state.py`
- `tg_msg_manager/infrastructure/storage/_sqlite_read_path.py`

Allowed changes there:

- thin wrappers;
- import forwarding;
- dependency wiring;
- compatibility-only bug fixes.

## Compatibility Wrappers

The following files are compatibility wrappers or aggregators only:

- `tg_msg_manager/services/exporter.py`
- `tg_msg_manager/services/context_engine.py`
- `tg_msg_manager/services/db_exporter.py`
- `tg_msg_manager/services/private_archive.py`
- `tg_msg_manager/core/models/service_payloads.py`
- `tg_msg_manager/infrastructure/storage/interface.py`

Package-level re-export entrypoints are also compatibility surfaces:

- `tg_msg_manager/services/db_export/__init__.py`
- `tg_msg_manager/services/private_archive/__init__.py`

New code must not add business logic to these files.

## Facade Growth Protection

The following modules are orchestration facades:

- `tg_msg_manager/services/export/service.py`
- `tg_msg_manager/services/context/engine.py`
- `tg_msg_manager/services/db_export/service.py`
- `tg_msg_manager/services/private_archive/service.py`
- `tg_msg_manager/services/channel_export/service.py`

New business logic must not be added directly to these files.
If a facade grows because of a new concern, extract a dedicated component first.

## 8. Telegram And Filesystem Boundaries

- no raw Telegram calls outside adapters/fetch layers (`core/telegram/`, sync/context fetch helpers);
- no direct filesystem writes outside writer/export modules.

## 9. Service Boundaries

- DB export logic must not be added back to `tg_msg_manager/services/db_export/service.py`.
- Private archive must reuse shared pipeline pieces where possible and stay out of the sync/export monoliths.
- New business logic must not be added directly to `tg_msg_manager/services/export/service.py`, `tg_msg_manager/services/context/engine.py`, or `tg_msg_manager/services/channel_export/service.py`.
- `ChannelExportService` should normalize options, resolve sources, select run mode, delegate payload/media/discussion/manifest/result helpers, save state in the established order, and emit high-level events.
- Services should depend on narrow storage contracts from `tg_msg_manager/infrastructure/storage/contracts/`.
- New services must not depend on the compatibility storage interface aggregator when a narrow contract exists.
- New payload models belong in `tg_msg_manager/core/models/payloads/`, not `service_payloads.py`.
- Context relation tables must follow the documented decision in `docs/architecture/CONTEXT_RELATION_TABLES_DECISION.md`.

## 10. Message Identity Rule

- Telegram message identity is `(chat_id, message_id)`.
- cross-table links must not rely on bare `message_id` when chat scope matters.

## 11. Schema Rule

- no schema change without an explicit migration note/documentation update.

## 12. Test Rule

Every architecture change needs:

- unit coverage for new pure logic;
- storage/fixture coverage when persistence changes;
- CLI regression coverage when command surface changes.
