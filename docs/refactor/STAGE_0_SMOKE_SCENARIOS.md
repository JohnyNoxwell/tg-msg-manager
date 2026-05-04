# Stage 0 Smoke Scenarios

Date: 2026-05-04

These are manual or near-manual smoke checks. None of them require live Telegram access unless explicitly stated.

## 1. CLI Help Surface

Run each command and confirm exit code `0` plus a valid usage block.

Commands:

- `python3 -m tg_msg_manager.cli --help`
- `python3 -m tg_msg_manager.cli export --help`
- `python3 -m tg_msg_manager.cli update --help`
- `python3 -m tg_msg_manager.cli db-export --help`
- `python3 -m tg_msg_manager.cli retry --help`
- `python3 -m tg_msg_manager.cli report --help`
- `python3 -m tg_msg_manager.cli clean --help`
- `python3 -m tg_msg_manager.cli delete --help`
- `python3 -m tg_msg_manager.cli schedule --help`
- `python3 -m tg_msg_manager.cli setup --help`

Expected success condition:

- every command prints `usage: ...`;
- top-level help lists all major commands;
- no import error or traceback is produced.

## 2. Offline Fixture Harness

Run:

- `python3 -m unittest tests.test_fixture_e2e -q`

Expected success condition:

- `Ran 4 tests`
- `OK`

What this covers:

- tracked sync with offline fixture data;
- DB export over fixture-backed storage;
- retry/report flows without Telethon or network access.

## 3. Database Smoke

Preferred offline command:

- `python3 -m unittest tests.test_storage_sqlite -q`

Expected success condition:

- test DB is created and cleaned up automatically;
- suite passes without live Telegram access;
- storage methods for messages, targets, export summaries, retry reads, and reports remain healthy.

Tables expected in a healthy temporary DB:

- `messages`
- `users`
- `chats`
- `sync_targets`
- `sync_state`
- `message_target_links`
- `message_context_links`
- `retry_queue`

Storage sanity checks:

- a saved message can be read back;
- target links are counted deterministically;
- export iterators return ascending `(timestamp, message_id)` order;
- retry listing preserves defined status ordering.

## 4. Export Smoke

Preferred offline command:

- `python3 -m unittest tests.test_db_exporter -q`

Expected success condition:

- TXT and JSONL export tests pass;
- export artifacts are created on disk;
- output files are non-empty;
- repeated export with unchanged fingerprint skips rewrite.

Specific behaviors covered:

- TXT grouping by date and author continuity;
- JSONL line validity and Unicode preservation;
- manifest/fingerprint skip for single-part and multipart export;
- AI JSON profile excludes heavy raw payload by default.

## 5. Script Smoke

Active helper scripts:

- `python3 scripts/export_user_context_from_db.py --help`
- `python3 scripts/reset_and_seed_targets.py --help`

Import-only maintenance script:

- `python3 -c "import scripts.cleanup_exports"`

Expected success condition:

- help text or import completes without traceback.
