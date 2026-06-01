# Non-Channel Synthetic Fixtures Plan

## Status

Planning/reference document. Stage 5I.1 created the minimal checked-in fixture
set, and Stage 5J.1 added focused fixture-backed tests. This document does not
create runtime behavior, dataset contracts, CLI changes, SQLite changes, or
output format changes.

Scope is user/group `export` and `db-export`. `export-pm` and private archive
fixtures are out of scope.

## Fixture Families

Use one shared synthetic message corpus where possible, then derive expected
outputs for each command family.

Recommended corpus cases:

- single target user in one chat;
- target user across multiple chats;
- context before and after target messages;
- reply parent present;
- reply parent missing;
- ungrouped context records;
- edited-like metadata only when current serializers expose it;
- neutral media metadata only, no media files;
- date range spanning multiple timestamps;
- part-file rotation;
- no-new-work / skip state.

## Fixture Locations

Implemented fixture directories:

```text
tests/fixtures/non_channel_export/
tests/fixtures/db_export/
```

Docs example directories remain deferred:

```text
docs/examples/non_channel_export/
docs/examples/db_export/
```

Current checked-in test fixture shape:

```text
tests/fixtures/non_channel_export/corpus.jsonl
tests/fixtures/non_channel_export/expected_export_context_readable.txt
tests/fixtures/non_channel_export/expected_export_legacy.txt
tests/fixtures/non_channel_export/expected_export_ai.jsonl
tests/fixtures/db_export/expected_db_context_readable.txt
tests/fixtures/db_export/expected_db_legacy.txt
tests/fixtures/db_export/expected_db_ai.jsonl
tests/fixtures/db_export/expected_writer_state.json
```

Docs examples should be smaller than test fixtures and should contain only
synthetic placeholders.

## Expected Outputs

TXT coverage:

- `context-readable` header and context block markers;
- `[REPLIED MESSAGE]`, `[CONTEXT BEFORE]`, `[TARGET MESSAGE]`,
  `[TARGET MESSAGES]`, and `[CONTEXT AFTER]`;
- compact missing reply marker;
- `legacy` flat timestamp/author shape.

JSONL coverage:

- default compact `ai` JSONL;
- key omission for null/empty values;
- reply, media, forwarding, context group, service, edit, and reaction fields
  when present in synthetic raw payloads.

State/layout coverage:

- `DB_EXPORTS/` filename pattern;
- `_partN` rotated file pattern;
- `.writer_state/` current part/current count shape;
- `.export_state/<user_id>.json` remains deferred as legacy manifest fallback;
- no-new-work / skip behavior.

## Privacy Safeguards

Fixtures must use deterministic fake values only.

Allowed patterns:

```text
user_id: 5001
chat_id: 1001
username: synthetic_target
chat_title: Synthetic Group Alpha
text: Synthetic fixture message A
timestamp: 2026-01-01T12:00:00+00:00
path: DB_EXPORTS/Synthetic_Target_5001.txt
```

Forbidden:

- real Telegram IDs, usernames, names, chat titles, message text, paths, media,
  logs, screenshots, sessions, credentials, SQLite DB rows, or ignored private
  artifacts;
- copied snippets from real exports;
- realistic private conversation content;
- private archive / `export-pm` examples.

## Tests

Focused tests currently cover fixture parsing, TXT golden outputs, compact JSONL
keys/output, `.writer_state` shape, privacy markers, and `export-pm` exclusion.

Future expansions may add coverage for:

- deterministic output filenames;
- part-file rotation paths;
- `.writer_state` presence/skip behavior;
- `.export_state` legacy fallback behavior only if a future stage explicitly
  scopes it;
- no-new-work behavior using temporary DB/output directories.

Golden-file tests are appropriate for small synthetic expected outputs.
Generated-output comparisons are appropriate for rotation and state behavior.
SQLite should use temporary test databases only.

## Deferred

- additional fixture families beyond the minimal checked-in set;
- docs example directories;
- runtime fixture generator;
- real Telegram smoke fixtures;
- full raw JSON profile contract;
- private archive / `export-pm` fixtures;
- media file fixtures;
- any CLI, SQLite, renderer, or output format change.
