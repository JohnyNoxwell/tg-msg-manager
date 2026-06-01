# Private Archive Contract Deferred Decision

## Status

Deferred decision only. This document is not a private archive contract and does
not create runtime guarantees.

`export-pm` remains outside user/group `export` plus `db-export` contract work.

## Decision

Private archive output is an archive-contract candidate, not a Dataset Contract
V1 dataset candidate.

Keep private archive contract work deferred until user/group and DB export
contracts have synthetic fixtures and tests.

## Current Output Family

Current `export-pm` behavior combines:

- `PRIVAT_DIALOGS/` base directory;
- user folder derived from safe display name plus user id;
- `chat_log.txt` and rotated part files;
- `media/photos/`, `media/videos/`, `media/voices/`, and `media/documents/`;
- media target filenames based on message id;
- SQLite message writes;
- private archive sync state;
- media skip/download behavior;
- retry behavior through the CLI failure path.

This mixed output family should not be folded into user/group `export` or
`db-export` contracts.

## Possible Future Contract Surfaces

Future private archive precheck may evaluate:

- folder naming;
- `chat_log.txt` naming and rotation;
- log line markers and timestamp shape;
- media category folders;
- media filename policy;
- sync state semantics;
- SQLite side effects;
- media skip/download/failure behavior;
- flush-before-mark-synced ordering.

## Deferred / Implementation Details

Do not contract yet:

- exact private message text examples;
- realistic private conversation examples;
- real user names, ids, paths, logs, media, sessions, or DB rows;
- media filename policy beyond current observed tests;
- SQLite side effects as a public artifact contract;
- failure and partial-download semantics without synthetic fixtures.

## Privacy Constraints

Future examples must be docs-only or fixture-only synthetic data. They must avoid
realistic private conversation content and use clearly fake names, ids, paths,
timestamps, and message text.

Real private dialogs, Telegram exports, sessions, credentials, logs,
screenshots, local DB files, media, and ignored private artifacts must not be
read or copied into docs, fixtures, reports, or tests.

## Future Path

Recommended path:

```text
PRIVATE_ARCHIVE_CONTRACT_DEFERRED
```

A later precheck can decide whether synthetic private archive fixtures are
needed first. A final private archive contract should not be created in this
stage.
