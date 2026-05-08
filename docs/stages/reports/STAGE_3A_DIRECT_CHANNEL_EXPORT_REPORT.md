# Stage 3A — Direct Channel Export Report

## 1. Summary

Stage 3A direct channel export is complete.

Implemented scope:

- `export-channel` CLI parser
- CLI command handler
- CLI context wiring
- interactive menu wiring
- runtime path for `exports/channels`
- README / `COMMANDS.md` docs
- live smoke checklist update
- changelog update

Supporting verification hardening that was required to pass the final gate:

- installed `pytest` into the active environment used by the verification run
- cleaned duplicate async teardown coverage in reporting tests
- hardened SQLite migration/idempotency around `sync_targets` composite-key migration
- stopped forcing WAL reconfiguration on read-only SQLite connections
- closed SQLite handles and removed `-wal` / `-shm` files in affected tests

## 2. Implemented files

- `tg_msg_manager/cli_parser.py`
- `tg_msg_manager/cli_commands.py`
- `tg_msg_manager/cli.py`
- `tg_msg_manager/core/runtime.py`
- `tests/test_channel_export_cli.py`
- `tests/test_cli.py`
- `README.md`
- `COMMANDS.md`
- `docs/testing/LIVE_SMOKE_CHECKLIST.md`
- `CHANGELOG.md`

## 3. CLI command

Added:

```bash
python3 -m tg_msg_manager.cli export-channel --channel @example --limit 100 --media metadata
```

Supported CLI flags in Stage 3A:

- `--channel` required
- `--limit`
- `--media`
- `--output-dir`
- `--force`

Current media behavior:

- `metadata` default
- `none` supported
- `full` exposed but fails clearly as not implemented yet

Interactive menu surface:

- main `tg` menu exposes `export-channel`
- two-digit menu codes are supported in the interactive console
- legacy one-character shortcuts remain accepted for compatibility

## 4. Dataset layout

Runtime root:

```text
exports/channels/
```

Dataset files:

- `manifest.json`
- `messages.jsonl`
- `messages.txt`
- `media_manifest.jsonl`
- `media/`

## 5. Media mode behavior

- Default mode is `metadata`
- Full media is not downloaded by default
- `--media full` is intentionally blocked in the CLI until a real downloader exists

## 6. Architecture constraints preserved

- No changes to `ExportService`
- No changes to `DBExportService`
- No changes to `PrivateArchiveService`
- No changes to `ContextEngine`
- No analytics added
- No SQLite schema changes added
- Channel export logic remains isolated under `services/channel_export/`

## 7. Tests added

- `tests/test_channel_export_cli.py`

Adjusted compatibility coverage:

- `tests/test_cli.py`

Local preflight that passed:

- `python3 -m unittest tests.test_channel_export_cli tests.test_channel_export_plan_builder tests.test_channel_export_renderers tests.test_channel_export_manifest tests.test_channel_export_media_policy tests.test_channel_export_source_resolver tests.test_channel_export_post_fetcher tests.test_channel_export_post_mapper tests.test_channel_export_payload_writer tests.test_channel_export_service -q`

## 8. Final verification

| Command | Result |
|---|---|
| `python3 -m compileall tg_msg_manager` | passed |
| `ruff check tg_msg_manager tests` | passed |
| `ruff format --check tg_msg_manager tests` | passed |
| `pytest tests/test_channel_export_*.py` | passed |
| `make test` | passed |
| `make verify` | passed |
| `python3 -m tg_msg_manager.cli export-channel --help` | passed |

## 9. Known limitations

- Broadcast channels only; groups and supergroups are not supported by `export-channel`
- No discussion group export yet
- No group source extraction yet
- No analytics
- No embeddings
- No SQLite persistence for channel posts
- No incremental update/checkpoint layer for channel posts yet; Stage 3A is full re-export only
- `--media full` deferred and not implemented

## 10. Deferred tasks

- Real full-media download implementation
- Optional `PROJECT_ARCHITECTURE_OVERVIEW.md` / architecture-doc updates for channel export

## 11. Ready for Stage 3B?

Yes.

Stage 3A is complete with the requested final verification gate passing.
