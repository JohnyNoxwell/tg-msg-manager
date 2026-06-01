# Privacy And Sensitive Artifacts

This project is a local Telegram export/data pipeline. Local files can contain Telegram credentials, session material, private messages, media, database rows, and operational logs. Treat local artifacts as private by default.

This guide is an operational handling rule, not a security product claim.

## Sensitive Categories

### Credentials And Local Config

Sensitive patterns:

- `config.json`
- `config.local.json`
- `.env`
- `.env.local`

`config.example.json` is a public template. Real local config files can contain Telegram API credentials, account labels, local database paths, allowlists, include lists, language settings, and rate-limit settings. Do not paste real values into docs, reports, issues, prompts, screenshots, or test fixtures.

### Telethon Sessions

Sensitive patterns:

- `*.session`
- `*.session-shm`
- `*.session-wal`
- `*.session-journal`

Session files are local authentication material. Do not read, copy, summarize, upload, diff, or include them in archives. If a task involves login behavior, use documented config fields and code paths; do not inspect session file contents.

### SQLite Databases

Sensitive patterns:

- `messages.db*`
- `*.db`
- `*.sqlite`
- SQLite sidecars such as `*.db-wal`, `*.db-shm`, `*.sqlite-wal`, and `*.sqlite-shm`

SQLite files may contain synced Telegram message text, authors, chat identifiers, reply links, retry state, export targets, and local metadata. Do not inspect database contents unless an active task explicitly scopes that exact diagnostic and the output can be reported without exposing private data.

### Export Directories

Sensitive directories:

- `DB_EXPORTS/`
- `PUBLIC_GROUPS/`
- `PRIVAT_DIALOGS/`
- `exports/`

These directories can contain exported messages, channel datasets, private dialog archives, media paths, manifests, state files, and generated reports over private data. Do not open ignored export artifact contents during docs, governance, architecture, or unrelated code stages.

### Logs And Runtime State

Sensitive patterns:

- `LOGS/`
- `*.log`
- `delete_log.txt`
- `.tg_msg_manager.lock`
- `export_state.json`
- `deep_export_state.json`
- `deep_json_export_state.json`
- `json_export_state.json`
- `pm_export_state.json`
- `DB_TARGETS.txt`

Logs and state files may include account names, target ids, chat ids, filesystem paths, operational failures, or export progress. Report only categories and patterns unless an active task requires exact filenames that are already public examples.

### Fixtures

Public fixtures under `tests/fixtures/` must stay synthetic and anonymized. They must not contain real Telegram identifiers, private payloads, copied production message bodies, real media, session data, or credential-derived values.

When adding or editing fixtures:

- use deterministic fake ids and names;
- keep payloads minimal;
- document fixture-specific edge cases in the fixture README;
- never derive fixture text by copying private exports.

### Reports And Screenshots

Stage reports, issue comments, screenshots, terminal transcripts, and PR notes must not include private message contents, credentials, sessions, local database rows, or raw ignored artifact excerpts.

Safe report content:

- changed tracked file paths;
- ignored artifact categories and path patterns;
- command names and pass/fail status;
- aggregate counts when they do not reveal message content or identities.

Unsafe report content:

- real message text;
- real API credentials;
- session bytes or filenames tied to a real account;
- copied rows from SQLite or JSONL exports;
- screenshots showing private chats, exports, logs, or config.

## Agent Rules

Coding agents must:

1. Read `AGENTS.md` and the active task first.
2. Inspect only files allowed by the active task.
3. Treat ignored artifact paths as private by default.
4. Use `git status --ignored --short` only for names/categories when a stage asks for ignored artifact inventory.
5. Avoid opening ignored private artifact contents unless the active task explicitly scopes that exact file category.
6. Report private artifact handling by category, not by copied content.
7. Stop and report a blocker if completing a task would require exposing private contents outside the scoped diagnostic.

## Git Handling

Current ignore policy excludes local config, session files, SQLite databases, export directories, logs, runtime state, scratch files, build artifacts, and Python caches.

Before committing, check:

```bash
git status --ignored --short
git diff --check
```

Do not add ignored artifacts with `git add -f` unless a task explicitly names a synthetic fixture or public template and verifies that it contains no private data.
