# Dataset Doctor Examples

This page uses only synthetic channel dataset examples under
[`../examples/`](../examples/). It explains how to read `validate-dataset`,
`inspect-dataset`, and `inspect-dataset --doctor` output.

The doctor is read-only. It does not repair, migrate, fetch from Telegram,
rewrite files, mutate SQLite, analyze message meaning, classify users or
content, perform OCR/STT/media recognition, or call LLMs.

## Healthy Dataset

Example path:
[`../examples/channel_dataset_minimal/`](../examples/channel_dataset_minimal/).

`validate-dataset` status:

```text
Status
ok

Errors
No errors

Warnings
No warnings
```

`inspect-dataset` summarizes deterministic facts such as file presence,
message count, media status counts, discussion counts, state cursor, and
validation notes. It does not interpret message text.

`inspect-dataset --doctor` output:

```text
Status
ok

Summary
- errors: 0
- warnings: 0

Findings
- INFO dataset_healthy: No validation issues were found. Action: No action required.
```

## Warning Example

Example path:
[`../examples/channel_dataset_warning_gap/`](../examples/channel_dataset_warning_gap/).

This variant deliberately skips message id `1002`. `validate-dataset` reports
`warnings`, not `errors`, because Telegram deletions, unavailable messages, or
scoped exports can create gaps.

Doctor finding:

```text
WARNING message_id_gap_detected (messages.jsonl): Message id gap detected; Telegram deletions or unavailable messages may also cause this: 1002-1002 (1 missing) Action: Review export scope and Telegram deletions; use a wider or forced export if parents are required.
```

Interpretation:

- `message_id_gap_detected` means local ids are not contiguous.
- It is not proof of exporter data loss by itself.
- Review export scope, Telegram deletions, and whether a forced or wider export
  is needed for your local use case.

## Error Example

Example path:
[`../examples/channel_dataset_missing_required_file/`](../examples/channel_dataset_missing_required_file/).

This variant deliberately omits `messages.jsonl`. `validate-dataset` returns
`errors` and exits with code `1`.

Doctor findings:

```text
ERROR missing_required_file (messages.jsonl): Required messages JSONL file is missing Action: Restore the missing artifact or re-run export-channel for this dataset.
WARNING manifest_count_mismatch (manifest.json): Manifest message_count differs from messages.jsonl count Action: Review manifest/state consistency; re-run export-channel --force if the dataset is stale.
WARNING manifest_included_file_missing (manifest.json): Manifest included file is missing: messages.jsonl Action: Restore the missing artifact or re-run export-channel for this dataset.
```

Interpretation:

- `missing_required_file` means the dataset is structurally incomplete.
- Count and manifest warnings can follow from the missing artifact.
- Restore the missing file from backup or rebuild the dataset; do not hand-edit
  doctor output as if it repaired the dataset.

## Common Warning And Error Categories

`missing_conditional_file` appears when manifest mode requires an artifact that
is absent, such as `discussion_metadata.jsonl` for discussion metadata mode or
discussion comments/thread/state files for full discussion mode. Restore the
artifact or rerun `export-channel` with the intended mode.

Media path issues include `invalid_media_path`, `media_path_escape`, and
`media_file_missing`. These apply to downloaded or already-existing media rows
whose `final_path` or `local_path` is invalid, escapes the dataset root, or
points to a missing local file. Check paths inside the dataset or rerun with the
intended media mode.

Reply parent warnings include `reply_parent_missing`,
`reply_parent_outside_export_scope`, `discussion_reply_parent_missing`, and
`discussion_reply_parent_outside_export_scope`. They mean a reply points to a
parent that is not present in the exported scope. Telegram deletions, scoped
limits, unavailable parents, or discussion export limits can cause this.

Suggested actions are deterministic guidance. They do not imply that the doctor
has changed files, fetched Telegram data, rewritten state, or repaired SQLite.
