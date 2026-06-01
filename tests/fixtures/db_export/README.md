# DB Export Synthetic Fixtures

All records in this directory are artificial. They use deterministic synthetic
IDs, names, chat titles, usernames, timestamps, text, and relative paths.

Scope:

- `db-export` output under `DB_EXPORTS/`;
- `context-readable` TXT;
- `legacy` TXT;
- compact `ai` JSONL;
- writer state shape for `FileRotateWriter`.

Out of scope:

- `export-pm`;
- private archive outputs;
- real Telegram data;
- media binaries;
- sessions, credentials, logs, SQLite DB files, screenshots, or ignored export artifacts.
