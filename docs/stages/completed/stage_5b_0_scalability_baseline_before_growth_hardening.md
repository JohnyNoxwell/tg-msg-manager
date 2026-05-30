# STAGE 5B.0 — Scalability Baseline Before Growth Hardening

Status: active task
Stage: 5B.0
Type: report
Depends on: `AGENTS.md`; `docs/stages/README.md`; current hot paths listed below

---

## 0. CODEX ENTRY CONTRACT

1. Read `AGENTS.md`.
2. Apply `stage-reviewer` before doing stage work. If no tool exists, read `.skills/stage-reviewer/SKILL.md`.
3. Apply `architecture-guard` because this stage audits CLI/services/storage growth risks. If no tool exists, read `.skills/architecture-guard/SKILL.md`.
4. Do not implement fixes in this stage.
5. Do not start any other active 5B stage.

## 1. PURPOSE

Create a factual baseline for scalability bottlenecks before implementation stages change behavior or structure.

The report must identify only measured or code-evident risks in:

- SQLite write queue and write transaction path;
- private archive per-message persistence;
- channel export post buffering;
- DB export memory/materialization paths;
- channel discussion export fetch/write pressure;
- SQLite schema module growth.

## 2. FILES TO INSPECT

Inspect only:

- `AGENTS.md`
- `docs/stages/README.md`
- `docs/architecture/README.md`
- `docs/architecture/ARCHITECTURE_RULES.md`
- `docs/development/README.md`
- `tg_msg_manager/infrastructure/storage/sqlite.py`
- `tg_msg_manager/infrastructure/storage/_sqlite_write_path.py`
- `tg_msg_manager/infrastructure/storage/write/message_writer.py`
- `tg_msg_manager/infrastructure/storage/_sqlite_schema.py`
- `tg_msg_manager/services/private_archive/service.py`
- `tg_msg_manager/services/private_archive/stream_processor.py`
- `tg_msg_manager/services/channel_export/workflows/full_export.py`
- `tg_msg_manager/services/channel_export/workflows/incremental_export.py`
- `tg_msg_manager/services/channel_export/run_changelog.py`
- `tg_msg_manager/services/channel_export/discussions/exporter.py`
- `tg_msg_manager/services/channel_export/discussions/fetcher.py`
- `tg_msg_manager/services/db_export/summary.py`
- `tg_msg_manager/services/db_export/payload_writer.py`
- `tg_msg_manager/infrastructure/storage/read/exports.py`
- `tests/services/private_archive/test_private_archive_components.py`
- `tests/services/channel_export/`
- `tests/services/db_export/`
- `tests/infrastructure/storage/test_storage_sqlite.py`

May create:

- `docs/stages/reports/STAGE_5B_0_SCALABILITY_BASELINE_REPORT.md`

May update:

- `docs/stages/README.md` during lifecycle cleanup only.

## 3. HARD PROHIBITIONS

- Do not edit runtime code.
- Do not edit tests.
- Do not edit SQLite schema or migrations.
- Do not add dependencies.
- Do not run live Telegram commands.
- Do not read `docs/archive/`, unrelated completed stages, or existing `docs/stages/reports/` files unrelated to this stage.
- Do not propose analytics, OSINT, profiling, OCR, STT, media recognition, GUI, SaaS, or LLM behavior inside exporter/core.

## 4. ATOMIC IMPLEMENTATION TASKS

1. Record line counts for the inspected hot-path files with `wc -l`.
2. Record exact code locations where memory grows with dataset size.
3. Record exact code locations where write flushing or queueing can throttle throughput.
4. Record exact code locations where sequential Telegram/media/discussion work can dominate runtime.
5. Write a Russian factual report with findings, evidence paths, and recommended follow-up stage IDs only.

## 5. REQUIRED DOCS

Create only:

- `docs/stages/reports/STAGE_5B_0_SCALABILITY_BASELINE_REPORT.md`

The report must be factual. It must not authorize implementation outside later active stages.

## 6. TESTS / VERIFICATION

Run:

- `git diff --check`
- `python3 -m compileall tg_msg_manager`

Optional if dependencies are available:

- `ruff check tg_msg_manager tests`

Do not claim optional checks passed unless actually run.

## 7. REPORT

The report must be in Russian and include:

- files inspected;
- commands run and results;
- exact bottleneck locations by path;
- which later 5B stages each finding maps to;
- confirmation that no code behavior changed.

## 8. COMPLETION CRITERIA

- Report exists and is factual.
- No runtime code or tests were changed.
- Required checks are recorded.
- `stage-reviewer` and `architecture-guard` application is recorded in the report.
- lifecycle cleanup is completed according to AGENTS.md.

## 9. OUTPUT LIMITS

Final response must follow `AGENTS.md` final structure, be in Russian, and stay under 1200 characters.
