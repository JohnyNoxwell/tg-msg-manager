# Non-Channel Contract Test Plan

## Status

Plan plus implemented focused tests. This document records intended coverage and
the current fixture-backed tests; it does not expand runtime behavior or claim
full contract coverage.

Scope is user/group `export` and `db-export` outputs under `DB_EXPORTS/`.
`export-pm` and private archive outputs are out of scope.

## Fixture Basis

Use only offline synthetic fixtures:

```text
tests/fixtures/non_channel_export/
tests/fixtures/db_export/
```

The fixtures cover reply-present, reply-missing, before/target/after context,
two synthetic chats, compact JSONL, TXT `context-readable`, TXT `legacy`, and a
metadata-only media case. They do not require Telegram credentials, network
access, real exports, sessions, logs, DB files, screenshots, or media.

## Test Locations

Recommended future test files:

```text
tests/services/rendering/test_non_channel_context_readable_contract.py
tests/services/rendering/test_non_channel_legacy_txt_contract.py
tests/services/db_export/test_non_channel_ai_jsonl_contract.py
tests/services/db_export/test_non_channel_db_export_state_contract.py
tests/cli/test_non_channel_contract_cli.py
```

Implemented focused fixture-backed tests:

```text
tests/services/rendering/test_non_channel_contract_fixtures.py
tests/services/db_export/test_non_channel_contract_jsonl.py
tests/cli/test_non_channel_contract_cli.py
```

`tests/services/private_archive/` must stay outside this contract except for an
explicit assertion that `export-pm` is excluded or deferred.

## Assertion Categories

TXT assertions:

- `context-readable` header and `TXT profile: context-readable`;
- `CONTEXT BLOCK` ordering and stable section markers;
- `[REPLIED MESSAGE]`, `[CONTEXT BEFORE]`, `[TARGET MESSAGE]`,
  `[TARGET MESSAGES]`, and `[CONTEXT AFTER]`;
- compact missing-reply marker;
- `legacy` date header, timestamp/author shape, and legacy missing-reply line.

JSONL assertions:

- compact `ai` key sets;
- omitted null, empty string, and empty list values;
- reply fields, `reply_to_top_id`, `forum_topic`, media metadata-only fields,
  forwarding id, edit date, context group id, service marker, and reactions.

Layout/state assertions:

- deterministic `DB_EXPORTS/` filenames and extensions;
- `_partN` rotated part-file paths;
- `.writer_state/<name>.json` current part/current count shape;
- `.export_state/` legacy manifest fallback remains deferred unless a future
  stage explicitly scopes legacy state coverage.

Safety assertions:

- fixture data remains obviously synthetic;
- no real Telegram IDs, names, usernames, chats, message text, media, sessions,
  credentials, logs, ignored DB files, or export artifacts are used;
- `export-pm` is excluded from user/group + `db-export` contract tests.

## Execution Expectations

Current and future tests must be deterministic and offline. They must not
connect to Telegram, read ignored private artifacts, or require configured
credentials.

Temporary SQLite databases may be used only when testing DB export behavior.
Generated-output comparisons are appropriate for filenames, part files, writer
state, and DB-backed skip/no-new-work behavior. Golden-file comparisons are
appropriate for the small TXT and compact JSONL fixture outputs.

The current focused tests are discovered by the routine unittest suite:

```bash
python3 -m unittest discover -s tests -q
make test
```

Do not claim additional future tests are covered by `make test` until they are
real test files.

## Deferred

- broader release-readiness claims beyond the draft contract and focused tests;
- private archive / `export-pm` contract tests;
- full raw JSON profile;
- exact rotation thresholds;
- SQLite schema contract status;
- real Telegram smoke data.
