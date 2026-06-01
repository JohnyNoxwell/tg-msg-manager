# Non-Channel Export Contract V1

## Status

Draft contract for current user/group `export` and `db-export` artifacts under
`DB_EXPORTS/`.

This document records existing behavior and fixture-backed expectations. It
does not require runtime changes, CLI changes, SQLite schema changes, storage
changes, output-format changes, new validators, analytics, OSINT, profiling,
OCR, STT, media recognition, or LLM behavior.

`export-pm` and private archive outputs are excluded.

## Scope

Covered output families:

- user/group `export` final TXT or compact JSONL artifact;
- `db-export` final TXT or compact JSONL artifact;
- shared TXT projection rules for `context-readable` and `legacy`;
- compact `ai` JSONL rows where the current DB export serializer is used;
- generated filenames, part-file path shape, and writer state where supported
  by fixtures and the test plan.

Out of scope:

- direct channel export Dataset Contract V1 internals;
- private archive / `export-pm`;
- full raw JSON profile;
- exact rotation thresholds;
- SQLite schema as a public contract;
- release readiness, package versioning, publish, tag, or migration claims;
- real Telegram examples or private data.

## Relationship To Dataset Contract V1

`docs/architecture/DATASET_CONTRACT_V1.md` remains the formal contract for
direct `export-channel` filesystem datasets.

This non-channel contract is separate. It covers user/group `export` and
`db-export` artifacts written under `DB_EXPORTS/` and does not redefine channel
dataset files, manifests, validators, dataset doctor output, or channel export
state.

## TXT Rendering Relationship

TXT output is a projection. JSONL and SQLite records remain the structured data
surfaces. Shared renderer boundaries are documented in
`docs/architecture/TXT_RENDERING.md`.

`context-readable` is the default TXT profile for user/group `export` and
`db-export`. `legacy` is an explicit compatibility profile.

## User/Group `export`

Current supported contract surface:

- final artifact is TXT by default or compact JSONL when JSON output is
  requested;
- TXT default profile is `context-readable`;
- `legacy` keeps flat log-style TXT output when selected;
- compact JSONL follows the shared `ai` serializer shape where the same message
  data fields are available.

The contract does not cover Telegram fetching, context discovery, retry policy,
or sync state internals beyond produced artifact shape.

## `db-export`

Current supported contract surface:

- output is written under `DB_EXPORTS/` by default;
- target-user filenames use the safe display name plus user id and the selected
  extension;
- TXT default profile is `context-readable`;
- `legacy` keeps flat log-style TXT output when selected;
- `--json` writes compact `ai` JSONL by default;
- writer state can appear under `.writer_state/<artifact_stem>.json`.

The normal current path does not create `.export_state/<user_id>.json`; that
legacy manifest fallback remains deferred and is not a required current output.

## Shared TXT Projection Rules

Fixture-backed `context-readable` expectations:

- `# Telegram Export` header;
- `TXT profile: context-readable`;
- target and chat labels;
- `CONTEXT BLOCK #NNNN` sections ordered by timestamp/message id;
- `[REPLIED MESSAGE]`, `[CONTEXT BEFORE]`, `[TARGET MESSAGE]` or
  `[TARGET MESSAGES]`, and `[CONTEXT AFTER]`;
- compact missing reply marker;
- reply-present excerpt line when the replied message is present locally.

Fixture-backed `legacy` expectations:

- date separator header;
- timestamp plus author line;
- reply-present `re:` snippet;
- legacy missing-reply line.

Exact full-line golden snapshots are test fixtures, not a broader guarantee
that every future cosmetic line is immutable.

## Compact JSONL Rules

Compact `ai` JSONL rows omit null, empty string, and empty list values.

Fixture-backed key candidates:

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

Full raw JSON payload output is deferred.

## Filenames, Part Files, And State

Current stable path candidates:

```text
DB_EXPORTS/<safe_target_name>_<user_id>.txt
DB_EXPORTS/<safe_target_name>_<user_id>.jsonl
DB_EXPORTS/<safe_target_name>_<user_id>_partN.txt
DB_EXPORTS/<safe_target_name>_<user_id>_partN.jsonl
DB_EXPORTS/.writer_state/<safe_target_name>_<user_id>.json
```

The part-file suffix shape is in scope. Exact rotation thresholds are deferred.

`.writer_state` current supported keys:

```text
current_part
current_count
```

`.export_state/` is legacy manifest fallback only and is not required for normal
current output.

## Fixtures And Tests

Fixture support:

- `tests/fixtures/non_channel_export/`
- `tests/fixtures/db_export/`

Test-plan support:

- `docs/development/NON_CHANNEL_CONTRACT_TEST_PLAN.md`

Implemented focused fixture-backed tests:

- `tests/services/rendering/test_non_channel_contract_fixtures.py`
- `tests/services/db_export/test_non_channel_contract_jsonl.py`
- `tests/cli/test_non_channel_contract_cli.py`

The implemented tests are focused fixture-backed checks. Future tests must
remain offline, deterministic, synthetic-only, and credential-free.

## Privacy Constraints

Docs, fixtures, tests, and reports for this contract must use only synthetic
values. They must not include real Telegram IDs, usernames, names, chat titles,
message text, paths, media, sessions, credentials, logs, SQLite DB contents,
screenshots, ignored export artifacts, or realistic private conversations.

## Known Limitations

- Focused fixture-backed contract tests exist; broader generated-output coverage
  remains planned.
- Filename and part-file expectations remain current supported candidates until
  generated-output tests are added.
- `.export_state/` is not a normal current output requirement.
- Full raw JSON profile is deferred.
- Private archive / `export-pm` is deferred to separate archive-contract work.
- SQLite schema and DB persistence internals are not public contract surfaces in
  this document.
