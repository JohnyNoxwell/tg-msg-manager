# Non-Channel Export Contract Design

## Status

Design/precheck only.

This document is not a final contract. It records the recommended shape of
future contract work for user/group `export` and `db-export`. It does not change
runtime behavior, CLI behavior, output formats, TXT rendering, JSONL schema,
SQLite, storage behavior, tests, or fixtures.

`export-pm` is intentionally out of scope and remains deferred to separate
private archive contract work.

## Recommended Boundary

The next formal non-channel contract should cover user/group `export` and
`db-export` outputs under `DB_EXPORTS/`.

Recommended contract surfaces:

- final TXT artifact path and part-file naming;
- final JSONL artifact path and part-file naming;
- shared `context-readable` TXT projection markers;
- `legacy` TXT as compatibility mode;
- compact AI JSONL top-level keys where `export` and `db-export` use the same
  serializer;
- `.export_state/<user_id>.json` only as DB export writer state, not a public
  dataset manifest;
- `.writer_state/` only as writer implementation state until fixture-backed
  tests prove stable behavior.

Deferred surfaces:

- full raw JSON profile;
- exact full-line TXT golden output;
- every rotation threshold detail;
- no-new-work and incremental state guarantees beyond current DB export state
  behavior;
- private archive / `export-pm`.

## TXT Projection Recommendation

`context-readable` should be the primary contract surface for user/group
`export` and `db-export` TXT output.

Stable marker candidates:

```text
# Telegram Export
TXT profile: context-readable
CONTEXT BLOCK
[REPLIED MESSAGE]
[CONTEXT BEFORE]
[TARGET MESSAGE]
[TARGET MESSAGES]
[CONTEXT AFTER]
```

`legacy` should be documented as explicit compatibility mode. The future
contract should avoid full golden snapshots and should assert markers,
ordering-critical sections, target/chat labels, missing-reply behavior, and
synthetic fixture outputs.

`docs/architecture/TXT_RENDERING.md` remains the shared projection boundary. A
future contract should reference it instead of duplicating renderer internals.

## JSONL Recommendation

Shared compact JSONL expectations can be documented for the default `ai`
profile where outputs are produced by the current DB export JSONL serializer.

Stable key candidates:

```text
edit_date
message_id
chat_id
user_id
author_name
timestamp
text
reply_to_id
reply_to_top_id
forum_topic
media_type
fwd_from_id
context_group_id
is_service
reactions
```

The future contract should state that omitted empty/null fields are expected in
compact JSONL. Full raw payload output should remain out of scope until a
separate stage proves and documents it.

## Fixture And Test Prerequisites

Formal contract work should wait for synthetic fixtures or a fixture plan.
Required fixture families:

- user/group TXT `context-readable`;
- user/group TXT `legacy`;
- user/group compact JSONL;
- `db-export` TXT `context-readable`;
- `db-export` TXT `legacy`;
- `db-export` compact JSONL;
- part-file rotation;
- `.export_state/` and `.writer_state/` presence/skip behavior;
- no-new-work behavior.

Fixtures must use only synthetic IDs, names, chat titles, timestamps, text, and
paths. Real Telegram exports, sessions, credentials, logs, screenshots, local
DB files, and ignored private artifacts must not be used.

## Recommended Next Stage

Run a fixtures-first planning stage before creating a final
`NON_CHANNEL_EXPORT_CONTRACT_V1.md`.

The final contract should be created only after the project has privacy-safe
synthetic fixtures and contract tests for the output surfaces above.
