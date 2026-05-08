# Architecture Documentation

## Purpose

Architecture docs are stable references for repository boundaries, storage/model decisions, and service organization. Stage task files should not replace architecture docs.

## Current architecture docs

- [`ARCHITECTURE_RULES.md`](ARCHITECTURE_RULES.md) - current layer, facade, storage, and schema guardrails.
- [`PROJECT_ARCHITECTURE_OVERVIEW.md`](PROJECT_ARCHITECTURE_OVERVIEW.md) - architecture snapshot; treat as a snapshot until refreshed.
- [`CONTEXT_ENGINE_SPLIT_MAP.md`](CONTEXT_ENGINE_SPLIT_MAP.md) - context component split.
- [`CONTEXT_RELATION_TABLES_DECISION.md`](CONTEXT_RELATION_TABLES_DECISION.md) - context relation table status.
- [`DB_EXPORT_SERVICE_SPLIT_MAP.md`](DB_EXPORT_SERVICE_SPLIT_MAP.md) - DB export split.
- [`EXPORT_SERVICE_SPLIT_MAP.md`](EXPORT_SERVICE_SPLIT_MAP.md) - export service split.
- [`PRIVATE_ARCHIVE_SPLIT_MAP.md`](PRIVATE_ARCHIVE_SPLIT_MAP.md) - private archive split.
- [`SQLITE_WRITE_PATH_SPLIT_MAP.md`](SQLITE_WRITE_PATH_SPLIT_MAP.md) - SQLite write path split.
- [`STORAGE_CONTRACT_SPLIT_MAP.md`](STORAGE_CONTRACT_SPLIT_MAP.md) - storage contract split.
- [`PAYLOADS_SPLIT_MAP.md`](PAYLOADS_SPLIT_MAP.md) - payload module split.
- [`DATASET_WRITE_SAFETY.md`](DATASET_WRITE_SAFETY.md) - direct channel export filesystem write/commit safety contract.
- [`DATASET_FORMAT.md`](DATASET_FORMAT.md) - direct channel export dataset, manifest, and state schema contract.
- [`STATE_AND_INCREMENTAL_MODEL.md`](STATE_AND_INCREMENTAL_MODEL.md) - direct channel export state and incremental consistency model.

## Channel export docs

- [`STAGE_3C_CHANNEL_DISCUSSION_CONTEXT_EXPORT_DESIGN.md`](STAGE_3C_CHANNEL_DISCUSSION_CONTEXT_EXPORT_DESIGN.md) - discussion export architecture design.
- Stage 3A/3B/3C completion records live under [`../stages/reports/`](../stages/reports/).

Current channel export service organization:

- `tg_msg_manager/services/channel_export/service.py` is the orchestration facade.
- Dataset included-file construction is delegated to `included_files_builder.py`.
- Manifest construction coordination is delegated to `manifest_coordinator.py`.
- `ChannelExportResult` construction is delegated to `result_builder.py`.
- Media behavior remains in media-specific channel export modules.
- Discussion behavior remains under `tg_msg_manager/services/channel_export/discussions/`.

These modules preserve the existing dataset, manifest, state, media, discussion, and CLI behavior. They do not add product features or SQLite persistence.

## Dataset/state docs

- Direct channel export dataset and state behavior are documented in [`../../README.md`](../../README.md), [`../../COMMANDS.md`](../../COMMANDS.md), and Stage 3A/3B/3C reports.
- Direct channel export dataset field contracts are documented in [`DATASET_FORMAT.md`](DATASET_FORMAT.md).
- Direct channel export filesystem write and commit behavior is documented in [`DATASET_WRITE_SAFETY.md`](DATASET_WRITE_SAFETY.md).
- Direct channel export state and incremental invariants are documented in [`STATE_AND_INCREMENTAL_MODEL.md`](STATE_AND_INCREMENTAL_MODEL.md).
- SQLite identity and link behavior are documented in [`SQLITE_MESSAGE_ID_AUDIT.md`](SQLITE_MESSAGE_ID_AUDIT.md).

## Media/discussion docs

- Media filename and extension handling is documented in [`MEDIA_HANDLING.md`](MEDIA_HANDLING.md).
- Media and discussion behavior is current in [`../../COMMANDS.md`](../../COMMANDS.md) and the Stage 3B/3C reports.
- Discussion architecture details are in [`STAGE_3C_CHANNEL_DISCUSSION_CONTEXT_EXPORT_DESIGN.md`](STAGE_3C_CHANNEL_DISCUSSION_CONTEXT_EXPORT_DESIGN.md).

## Rules for adding architecture docs

- Put current architecture guidance here, not in active stage prompts.
- Keep historical reports under `docs/stages/reports/`.
- Update architecture docs when boundaries, formats, state files, schemas, storage contracts, or protected-file rules change.
- Do not add analytics, OSINT, profiling, media analysis, schema migrations, or product features through architecture docs alone.
