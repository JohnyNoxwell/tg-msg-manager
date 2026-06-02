# Operational Risks And Limits

Status: operational guidance for local runs.

This page documents current operational caveats. It does not create stronger
runtime guarantees and does not authorize live checks, private artifact reads,
schema changes, recovery features, or scheduler changes.

## Telethon Sessions

Telethon session files are local authentication material. Treat these patterns
as sensitive and private:

```text
*.session
*.session-shm
*.session-wal
*.session-journal
```

Do not copy, upload, diff, summarize, or paste session contents into docs,
reports, issues, prompts, screenshots, or fixtures.

If a session is missing, corrupted, expired, or invalidated by Telegram, the
next command that needs Telegram access may require re-authentication through
Telethon. The project does not provide a separate session repair workflow.

## FloodWait And Rate Limits

Telegram rate limits are external and can change. Current code has a local
token-bucket throttler configured by `max_rps` and handles some Telethon
`FloodWaitError` cases by sleeping and lowering the local request rate.

Operational expectations:

- `max_rps` is a local pacing hint, not a Telegram guarantee.
- FloodWait can still happen during large exports, media downloads, deletes, or
  repeated commands.
- A command may sleep for the wait duration reported by Telegram.
- Lowering `max_rps` can reduce pressure, but it cannot guarantee that Telegram
  will not return FloodWait.
- Login/authentication FloodWait errors are reported to the CLI user, but they
  may require waiting before retrying.

## SQLite Concurrent Access

The local SQLite database is optimized for normal single-user local CLI runs.
The storage layer uses WAL for the main write connection and a background write
queue, but SQLite is still a local embedded database.

Operational expectations:

- Avoid running multiple long write-heavy commands against the same DB at the
  same time.
- Very large deep exports, private archives, retries, and updates can keep the
  background writer busy.
- Concurrent readers are safer than concurrent writers, but external tools or
  multiple project processes can still cause lock contention.
- If SQLite reports a busy/locked database condition, stop duplicate writers and
  rerun after the active command has flushed and exited.

This page does not make SQLite schema or persistence internals public contract
surfaces.

## Scheduler And Background Runs

The built-in `schedule` command targets macOS `launchd` / `launchctl`. It writes
a LaunchAgent plist that runs:

```text
python -m tg_msg_manager.cli update
```

Operational expectations:

- Non-macOS scheduler behavior is not supported by the current command.
- Scheduled runs use the configured local environment, session, database, and
  filesystem paths available to the LaunchAgent.
- Scheduler stdout/stderr goes under `LOGS/`; logs may contain operational
  details and must be treated as sensitive local artifacts.
- Do not overlap scheduled `update` runs with manual long-running write-heavy
  commands against the same DB.

## Live Smoke Checks

Live Telegram smoke checks require credentials, a valid session, and privacy-safe
handling. They are manual/session-dependent and separate from offline release
verification.

Do not claim live smoke checks passed unless a future active stage explicitly
scopes them and records the exact command/result without exposing private
message contents, sessions, DB rows, logs, media, screenshots, or credentials.
