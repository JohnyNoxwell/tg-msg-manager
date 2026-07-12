# STAGE 7C.0 — BULK INCREMENTAL CHANNEL UPDATE

Status: completed
Stage: 7C.0
Type: implementation
Depends on: current `export-channel` dataset, manifest, state, incremental, application-runtime, and CLI contracts

---

## 0. CODEX ENTRY CONTRACT

1. Read `AGENTS.md`, then this file.
2. Apply `stage-reviewer` before implementation and `architecture-guard` before editing CLI/services.
3. Read only the files and docs listed below; inspect before editing.
4. Write a plan of at most 5 bullets.
5. Implement only this stage; do not start later work.

## 1. PURPOSE

Add a direct CLI command `update-channels` that sequentially discovers all completed broadcast-channel datasets under one channel-export root and invokes the existing single-channel incremental exporter for each dataset. One channel failure must not stop the remaining channels, and the command must print a deterministic final summary.

## 2. FILES TO INSPECT

Required docs:

- `docs/architecture/README.md`
- `docs/architecture/STATE_AND_INCREMENTAL_MODEL.md`
- `docs/architecture/DATASET_FORMAT.md`
- `docs/development/CLI_CONTRACT.md`
- `docs/development/PR_CHECKLIST.md`
- `README.md`
- `COMMANDS.md`

Required source/tests:

- `tg_msg_manager/services/channel_export/models.py`
- `tg_msg_manager/services/channel_export/state_manager.py`
- `tg_msg_manager/services/channel_export/service.py` — inspection only
- `tg_msg_manager/services/channel_export/manifest_writer.py`
- `tg_msg_manager/services/channel_export/__init__.py`
- `tg_msg_manager/application/services.py` — mechanical service wiring only
- `tg_msg_manager/cli/channel_export_options.py`
- `tg_msg_manager/cli/commands/channel_export.py`
- `tg_msg_manager/cli/commands/__init__.py`
- `tg_msg_manager/cli/__init__.py` — mechanical dispatch/context wiring only
- `tg_msg_manager/cli_parser.py`
- `tests/cli/test_channel_export_cli.py`
- `tests/services/channel_export/test_channel_export_service.py`
- `.github/workflows/ci.yml`
- `Makefile`

May create:

- focused modules under `tg_msg_manager/services/channel_export/` for dataset discovery, manifest-to-options reconstruction, batch orchestration, and batch result models;
- focused tests under `tests/services/channel_export/`;
- `docs/stages/reports/STAGE_7C_0_BULK_INCREMENTAL_CHANNEL_UPDATE_REPORT.md`.

Do not inspect unrelated completed stages, reports, roadmap, or archive files.

## 3. HARD PROHIBITIONS

- Do not change SQLite schema or persist channel posts/discussion comments in SQLite.
- Do not change `export-channel` names, flags, defaults, dataset formats, state semantics, incremental/force/no-new-work behavior, or output layout.
- Do not add batch logic to protected `ChannelExportService`; it must remain single-channel orchestration only.
- Do not add feature logic to CLI, application wiring, compatibility wrappers, validation, inspection, or doctor modules.
- Do not run channels concurrently; the first implementation is sequential to preserve Telegram rate-limit and filesystem safety.
- Do not add `--force`, historical media/discussion backfill, retries, scheduling, analytics, profiling, classification, OCR, STT, or new runtime dependencies.
- Do not rewrite invalid datasets, silently substitute defaults for malformed manifests, or let one failed channel abort later channels.
- Do not perform unrelated refactors, formatting churn, or cleanup.

## 4. ATOMIC IMPLEMENTATION TASKS

1. Define focused immutable models for discovered dataset targets and per-channel/final batch results. Keep them outside compatibility aggregators.
2. Implement deterministic discovery of immediate child directories under the selected root. Treat a directory containing either `channel_export_state.json` or `manifest.json` as a candidate, require both files for execution, and sort candidates by directory name. Record missing-pair, malformed, unreadable, and inconsistent candidates as failures without mutation; ignore unrelated directories containing neither file.
3. Reconstruct each `ChannelExportOptions` from committed state plus manifest: use `@username` when present, otherwise the stored numeric channel ID; preserve manifest media mode, media size/types, discussion mode, and included `messages.jsonl`/`messages.txt` formats; require and preserve `max_comments_per_post` for `discussion=full`. For `none`/`metadata`, where that value is not persisted and comments are not fetched, use the existing model default explicitly. Set `output_dir` to the scanned root, `limit=None`, and `force=False`. Reject missing or invalid required values instead of guessing.
4. Add a dedicated batch service that receives the existing `ChannelExportService`, processes targets sequentially, continues after per-target exceptions, and returns ordered `updated`, `no_new_posts`, and `failed` results. It must delegate every actual export to `export_channel()`.
5. Add `update-channels --output-dir <path>`; `--output-dir` is optional and defaults to the normal channel export root. Wire the batch service mechanically through application runtime/context. Render one compact line per channel and a final deterministic total; exit non-zero after processing all candidates when any candidate failed.
6. Add tests for empty root, deterministic ordering, option reconstruction, username/numeric-ID target selection, successful update, no-new-posts, malformed dataset isolation, exporter exception isolation, sequential calls, summary rendering, default/custom root, client requirement, and aggregate non-zero exit behavior. Preserve existing `export-channel` tests.

## 5. REQUIRED DOCS

- Update `README.md` and `COMMANDS.md` with the exact command, discovery rules, sequential/failure behavior, and private/no-username resolution caveat.
- Update `docs/development/CLI_CONTRACT.md` and its contract-test references.
- Update `docs/architecture/README.md` only if the implemented module organization adds current architecture guidance.
- Do not change dataset-contract docs because this stage must not change dataset files or schemas.

## 6. TESTS / VERIFICATION

Run focused checks first, then the full gates:

```bash
python3 -m pytest tests/services/channel_export tests/cli/test_channel_export_cli.py -q
python3 -m compileall tg_msg_manager
make verify
make pre-commit
```

Do not claim a check passed unless it was run. If `make verify` cannot run because of tooling/environment failure, keep the stage incomplete or blocked and record the exact failure.

## 7. REPORT

Create `docs/stages/reports/STAGE_7C_0_BULK_INCREMENTAL_CHANNEL_UPDATE_REPORT.md` in Russian with:

- implemented command and boundaries;
- changed files;
- discovery and option-reconstruction contract;
- failure/exit behavior;
- exact checks and results;
- remaining caveats, especially numeric-ID resolution for private channels.

After the report exists and all completion criteria pass, perform lifecycle cleanup according to `AGENTS.md` and update `docs/stages/README.md`.

## 8. COMPLETION CRITERIA

- `update-channels` updates every valid discovered dataset through the existing incremental exporter in deterministic sequential order.
- Existing single-channel behavior and dataset/state contracts are unchanged.
- Invalid datasets and per-channel failures are isolated, reported, and produce a final non-zero exit only after all candidates were processed.
- Focused tests, `make verify`, and `make pre-commit` pass.
- Required user/developer docs and the Russian factual report are complete.
- `stage-completion-auditor` passes after completion is claimed.
- lifecycle cleanup is completed according to `AGENTS.md`.

## 9. OUTPUT LIMITS

- Follow the final response format and 1200-character limit from `AGENTS.md`.
- No full diffs, large copied code blocks, generic summaries, or future recommendations.
