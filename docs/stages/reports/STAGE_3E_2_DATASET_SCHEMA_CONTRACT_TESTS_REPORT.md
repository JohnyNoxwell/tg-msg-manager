# Stage 3E.2 - Dataset Schema Contract Tests Report

## 1. Summary

Stage 3E.2 added explicit dataset schema contract tests and documented the current `export-channel` dataset format.

Completed:

- added contract tests for channel post JSONL rows;
- added contract tests for media manifest rows and committed statuses;
- added contract tests for discussion comments and discussion thread rows;
- added contract tests for manifest shape in discussion none/full modes;
- added contract tests for channel and discussion state files;
- added TXT projection smoke contract checks;
- documented dataset schemas and schema-change policy.

## 2. Schemas covered

Covered:

```text
messages.jsonl
media_manifest.jsonl
discussion_comments.jsonl
discussion_threads.jsonl
manifest.json
channel_export_state.json
discussion_export_state.json
messages.txt
discussion_comments.txt
```

## 3. Tests added

Added:

```text
tests/test_channel_export_dataset_contracts.py
```

The tests use inline exact key sets and field assertions. No runtime code was changed for this stage.

## 4. Docs updated

Added:

```text
docs/architecture/DATASET_FORMAT.md
```

Updated:

```text
docs/architecture/README.md
docs/stages/README.md
```

`docs/development/TESTING.md` does not exist, so no testing doc was updated there.

## 5. Compatibility policy

The dataset format doc now states that any dataset schema change requires:

- explicit active stage scope;
- tests;
- docs update;
- changelog/update note if public behavior changes.

If docs and implementation disagree, current behavior should be documented first unless an active task explicitly permits behavior changes.

## 6. Verification results

| Command | Result |
| --- | --- |
| `pytest tests/test_channel_export_dataset_contracts.py` | passed, 7 tests |
| `pytest tests/test_channel_export_*.py` | passed, 170 tests |
| `python3 -m compileall tg_msg_manager` | passed |
| `ruff check tg_msg_manager tests` | passed |
| `ruff format --check tg_msg_manager tests` | passed, 248 files already formatted |
| `python3 -m tg_msg_manager.cli export-channel --help` | passed |

`make test` and `make verify` were not run during this stage because the required verification passed and the stage scope was channel export schema contracts.

## 7. Runtime behavior statement

No intended runtime behavior change.
No CLI behavior change.
No SQLite schema change.
No product feature added.

Dataset schemas were documented and locked by tests; they were not intentionally changed.

## 8. Remaining limitations

- TXT projections have smoke contract tests rather than full golden snapshots.
- Contract tests lock current key sets but do not validate every possible value combination.
- Pre-existing unrelated worktree changes remain outside the Stage 3E.2 scope.

## 9. Status

Stage 3E.2: complete.
