# Current Project Context

Status: current portable context after Stage 5C, 5D, and 5E.

Use this file as a compact starting point for a new Codex chat. It records
current project identity, boundaries, recently closed work, risks, and the next
rational docs/product-hardening plan. It does not authorize implementation work
without an active stage file.

## 1. Project Identity

- Distribution/package project name: `tg-msg-manager`.
- Import package/module root: `tg_msg_manager`.
- Console script: `tg-msg-manager`.
- Console script mapping: `tg-msg-manager = tg_msg_manager.cli:main`.
- Primary Python entrypoint: `python3 -m tg_msg_manager.cli`.
- README display name: `TG_MSG_MNGR`.
- Current package version: `0.1.0`.
- Version source: `pyproject.toml` `[project].version` is the single packaging
  version source. There is no runtime `tg_msg_manager.__version__`.
- Version bumps, tags, publishing, release artifacts, runtime version APIs, and
  package renames require separate explicit stage scope.

The project is a local Telegram export/data CLI and pipeline. It supports
SQLite-backed sync, local DB export, private dialog archive, direct channel
filesystem datasets, read-only dataset validation/inspection/doctor output,
retry handling, cleanup, and local operational reports.

The project is not a SaaS monitoring platform, analytics engine, OSINT
interpretation engine, profiling system, bot detector, narrative classifier,
OCR/STT/media-analysis tool, GUI dashboard, or LLM reporting product.

Preferred boundary:

```text
export -> validate/inspect -> dataset doctor -> post-processing -> optional LLM report
```

Post-processing and optional LLM reports stay outside exporter core.

## 2. Current Architecture

### CLI Layer

The CLI is thin: parse args, validate basic input, call services, and render
high-level results. Current public commands are `export`, `update`, `retry`,
`report`, `clean`, `export-pm`, `delete`, `schedule`, `setup`, `db-export`,
`validate-dataset`, `inspect-dataset`, and `export-channel`.

Do not change command names, flags, defaults, parser behavior, output formats,
or exit behavior without explicit active stage scope, tests, and docs.

### Runtime / Config

Settings come from init args, `TG_*` environment variables, `config.json`, and
`.env` in that precedence order. Legacy config aliases remain supported:
`exclude_chats -> whitelist_chats` and `language` / `ui_language -> lang`.

Credentials, Telethon sessions, local SQLite databases, logs, exports, and
runtime state are private by default. Docs and reports must use synthetic
examples unless an active task explicitly scopes a safe diagnostic.

### Services

Services orchestrate. They must not contain raw SQL, storage implementation
details, large feature algorithms, analytics, profiling, OSINT logic, media
analysis, or LLM-dependent behavior.

Protected service facades and compatibility wrappers stay thin. Feature logic
belongs in focused modules with one responsibility.

### Channel Export

`export-channel` is a filesystem-first direct channel dataset exporter for
broadcast channels. Groups and supergroups are out of scope for this command.
Channel posts and discussion comments are not persisted to SQLite.

Current organization:

- `tg_msg_manager/services/channel_export/service.py` is the orchestration
  facade.
- Full, incremental, and no-new-posts run paths live under
  `tg_msg_manager/services/channel_export/workflows/`.
- Included-file construction lives in `included_files_builder.py`.
- Manifest coordination lives in `manifest_coordinator.py`.
- Result construction lives in `result_builder.py`.
- Run summary facts live in `run_summary.py`.
- Media behavior stays in media-specific channel export modules.
- Discussion behavior stays under
  `tg_msg_manager/services/channel_export/discussions/`.
- `ChannelExportWorkflowContext` is wiring/helper context, not a product logic
  container.

Default channel export modes are `--media metadata` and `--discussion none`.
`--media full` and `--discussion full` are explicit heavier modes. Discussion
full exports comments only for posts fetched in the current run.

### Dataset Contract

Dataset Contract V1 covers `direct_channel_export` filesystem datasets with
manifest schema `1.0`. Current files include `manifest.json`,
`messages.jsonl`, `messages.txt`, `media_manifest.jsonl`,
`run_changelog.jsonl`, `channel_export_state.json`, optional `media/`, and
mode-specific discussion files.

`messages.jsonl`, `messages.txt`, discussion payloads, state files, and
manifest included files follow mode-specific rules documented in
`DATASET_CONTRACT_V1.md` and `DATASET_FORMAT.md`. `messages.txt` and
`discussion_comments.txt` are human-readable projections, not canonical schemas.

Non-CLI service options `include_jsonl=False` and `include_txt=False` now mean
the matching payload file is omitted and is not opened for that run.

Dataset format changes require explicit active stage scope, tests, and docs.

### Validation / Inspection / Doctor

`validate-dataset` checks deterministic local filesystem structure and
relationships. `inspect-dataset` summarizes deterministic counts/statuses.
`inspect-dataset --doctor` adds deterministic severity, artifact path, message,
and suggested next action over validation findings.

These commands are read-only. They must not use Telegram network access, repair,
migrate, fetch, mutate, rewrite datasets, alter SQLite schema, analyze message
meaning, classify users/content, perform OCR/STT/media processing, or call LLMs.

### Storage / SQLite

SQLite storage remains infrastructure-only. SQL belongs under
`tg_msg_manager/infrastructure/storage/`. Core/domain must not import
infrastructure; infrastructure must not import services; service/core/storage
modules must not import CLI.

`SQLiteStorage` composes `SQLiteSchemaMixin`, identity, read/write path, sync
state, and base storage behavior. SQLite schema changes, migrations, new tables,
new indexes, and new columns require a separate explicit stage.

### Schema Split Status

Stage 5D.0 extracted table, index, and inspection helpers:

- `schema/tables.py`
- `schema/indexes.py`
- `schema/inspection.py`

Stage 5E.1 extracted migration, compatibility, and backfill helpers:

- `schema/migrations.py`: `run_migrations` for `PRAGMA user_version` 2 through
  14.
- `schema/compat.py`: compatibility column ensures, legacy table rewrites,
  legacy chat-id resolution, composite primary key migration, and legacy target
  link population.
- `schema/backfills.py`: export target backfill, missing reply refs backfill,
  context link normalization, and target link reclassification.

`tg_msg_manager/infrastructure/storage/_sqlite_schema.py` remains the
`SQLiteSchemaMixin` compatibility surface. It owns initialization ordering and
thin delegating wrappers around extracted schema helpers.

Preserved invariants:

- `_init_db` order: tables, user identity schema, export target columns, sync
  target columns, retry queue columns, indexes, migrations, commit.
- Existing table SQL, index SQL, migration SQL, backup table names, exception
  strings, log strings, commit behavior, and `PRAGMA user_version` transitions.
- Extracted schema helpers do not import services, CLI, or dataset modules.

### Post-Processing Boundary

Post-processing is downstream of export, validation, inspection, and doctor
output. It reads exported datasets and writes separate artifacts. It must not be
embedded into channel export, DB export, context engine, private archive,
storage write paths, validation, or doctor logic. Source datasets must not be
mutated by default.

## 3. Closed In Stage 5C

- Dataset Contract Coverage Matrix created and linked.
- Pytest collection hygiene tightened with `testpaths = ["tests"]`; scratch
  files are not collected by default.
- Required project skill fallback files were verified, and `AGENTS.md` routing
  requires checking `.skills/<skill-name>/SKILL.md` before claiming a missing
  skill/tool.
- CLI / README / COMMANDS parity was audited; CLI runtime stayed unchanged and
  `docs/development/CLI_CONTRACT.md` was corrected.
- Privacy and sensitive artifact handling guide was added.
- Package identity and version policy were documented; no rename, release, tag,
  publish, or runtime version API was added.

## 4. Closed In Stage 5D

- Dataset Contract gaps were classified and ordered.
- `run_changelog.jsonl` exact top-level keys and `artifact_paths` keys gained
  contract coverage.
- Channel TXT projections were clarified as smoke/marker contracts, not full
  golden snapshots. User/group `export` and `db-export` still default to
  `context-readable`; `legacy` remains explicit.
- Channel export mode matrix tests covered media modes, discussion modes,
  output toggles, and full/force/incremental/no-new-posts run modes.
- Safe first channel export guide was added with synthetic examples and privacy
  guardrails.
- The `include_jsonl=False` / `include_txt=False` behavior mismatch was closed:
  Stage 5D.4 changed `payload_writer.py` so disabled payload files are not
  opened, while public CLI defaults stayed unchanged.

## 5. Closed In Stage 5E

- Stage 5E.0 recorded baseline storage/architecture checks and the exact helper
  groups allowed for extraction.
- Stage 5E.1 mechanically extracted migration, compatibility, and backfill
  helpers into the storage schema package.
- Stage 5E.2 expanded regression tests for extracted migration callback order,
  final `PRAGMA user_version = 14`, and thin `SQLiteSchemaMixin` delegation.
- No SQLite schema behavior, CLI behavior, service behavior, dataset behavior,
  or storage contracts changed during Stage 5E.2.

## 6. Current Risks

Closed risks:

- Pytest no longer collects scratch tests by default.
- Required skill fallback routing is verified.
- CLI docs drift found in Stage 5C.3 was corrected.
- Sensitive artifact categories and agent handling rules are documented.
- Package identity/version policy is explicit.
- Dataset Contract V1 coverage gaps for run changelog keys, TXT projection
  intent, mode matrix rows, and include toggles are closed.
- SQLite schema split Stage 2 has regression coverage.

Remaining risks:

- Dataset Contract V1 does not cover non-channel dataset families:
  user/group `export`, `db-export`, and `export-pm`.
- Partial failure ordering is documented but not exhaustively proven by the
  inspected contract/validator tests.
- Media subdirectory coverage is representative, not exhaustive.
- Channel TXT projection tests intentionally remain smoke/marker checks, not
  full golden snapshots.
- Very large deep-export passes remain the main pressure area for SQLite
  background writing.

Deferred risks:

- Non-channel dataset contracts should be defined later from existing behavior
  and tests only.
- Post-processing examples and static summary reports need design before
  implementation.
- SQLite schema split Stage 3 should happen only if a concrete remaining risk
  is identified.

Do not do prematurely:

- Do not add analytics, OSINT, profiling, OCR, STT, media recognition, bot
  detection, narrative classification, or LLM report behavior to exporter core.
- Do not create GUI/Web UI/SaaS surfaces.
- Do not mutate private artifacts or inspect ignored private contents for docs
  and governance work.

## 7. Next Rational Plan

Recommended next block:

1. Build a full user quickstart index that links existing safe guides and
   command references.
2. Add a synthetic channel dataset example using anonymized, deterministic
   fixture content.
3. Add dataset doctor output examples over synthetic datasets.
4. Design post-processing examples later, after examples and boundaries are
   clear.
5. Design static dataset summary report examples later, as downstream artifacts.
6. Start SQLite schema split Stage 3 only if a concrete risk remains after the
   current split map and regression coverage.

## 8. Future Stage Prohibitions

- Do not add analytics, OSINT, profiling, classification, OCR, STT, media
  analysis, or LLM-dependent behavior to exporter core.
- Do not change SQLite schema, migrations, storage contracts, tables, indexes,
  columns, or `PRAGMA user_version` without explicit active stage scope.
- Do not change dataset formats, filenames, JSON keys, manifest/state layout,
  media/discussion behavior, incremental/force/no-new-work behavior, or output
  layout without docs and tests.
- Do not bloat protected service facades or compatibility wrappers.
- Do not read private local artifacts, sessions, databases, credentials, logs,
  or export contents unless the active stage explicitly scopes that diagnostic.
- Do not build GUI, Web UI, dashboard, SaaS, or product analytics surfaces
  prematurely.
