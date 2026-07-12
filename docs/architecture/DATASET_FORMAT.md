# Dataset Format

## 1. Overview

`export-channel` writes a filesystem-first dataset under `exports/channels/<channel_slug>/`.

Current dataset files:

```text
manifest.json
messages.jsonl
messages.txt
media_manifest.jsonl
run_changelog.jsonl
channel_export_state.json
media/
discussion_metadata.jsonl
discussion_comments.jsonl
discussion_comments.txt
discussion_threads.jsonl
discussion_export_state.json
```

Discussion metadata is written only for explicit `--discussion metadata` runs with current-run posts. Discussion comment/thread/state files are written only for explicit `--discussion full` runs with current-run posts. Media files under `media/` are written only for explicit `--media full`.

Channel posts and discussion comments are not persisted to SQLite.

## 2. messages.jsonl

Each line is one channel post JSON object with exact top-level keys:

```text
message_id
channel_id
channel_title
channel_username
timestamp
text
views
forwards
replies_count
reactions
media
raw_payload
```

Contract notes:

- `message_id` and `channel_id` are integers.
- `timestamp` is ISO 8601 text.
- `text`, counters, title, and username may be `null`.
- `reactions` and `raw_payload` are JSON objects after JSON-safe normalization.
- `media` is a list of channel post media records.

Nested `media` records in `messages.jsonl` use exact keys:

```text
media_id
message_id
media_index
media_type
mime_type
file_name
file_size
width
height
duration
local_path
sha256
download_status
```

## 3. media_manifest.jsonl

Each line is one media record JSON object with exact keys:

```text
media_id
message_id
media_index
media_type
mime_type
file_name
file_size
width
height
duration
local_path
sha256
download_status
error
original_filename
detected_extension
filename_strategy
final_filename
final_path
```

Committed media manifest rows must not use final `pending` status.

Current committed statuses:

```text
metadata_only
downloaded
already_exists
skipped_by_size
skipped_by_type
failed
```

## 4. run_changelog.jsonl

Each line is one completed `export-channel` run summary. It is a derived audit artifact; canonical post data remains in `messages.jsonl`.

Top-level keys:

```text
run_id
export_target_type
export_target_id
export_target_name
run_mode
started_at
finished_at
previous_cursor
new_cursor
new_message_count
new_message_ids
first_new_message_id
last_new_message_id
first_new_message_date
last_new_message_date
artifact_paths
warnings
```

Contract notes:

- `run_mode` is `full`, `force_full`, or `incremental`.
- `previous_cursor` and `new_cursor` mirror `channel_export_state.json.last_exported_message_id` before and after the run.
- `new_message_ids` lists message ids written in that run. No-new-posts runs write an entry with `new_message_count` `0` and an empty id list.
- The changelog is append-only per dataset path. A force export overwrites payload files but preserves the run changelog history.
- The changelog does not store message text and is not persisted to SQLite.

## 5. discussion_comments.jsonl

Each line is one discussion comment JSON object with exact keys:

```text
message_id
discussion_chat_id
channel_id
channel_message_id
discussion_root_message_id
author_id
author_name
username
timestamp
text
reply_to_id
media
reactions
raw_payload
```

Contract notes:

- `reply_to_id` is preserved when available.
- Reply trees are not reconstructed.
- Discussion comment media is metadata-only; no full media download fields are required.
- `media` is a list, usually empty in the current implementation.

## 6. discussion_metadata.jsonl

Each line is one compact channel-post discussion metadata object with exact keys:

```text
channel_id
channel_message_id
has_comments
discussion_chat_id
replies_count
comments_exported
source
```

Contract notes:

- Metadata mode does not fetch comments.
- `comments_exported` is always `false` in metadata mode.
- `source` is `raw_payload.replies` when extracted from Telegram replies metadata.
- Full `raw_payload` is not duplicated in metadata records.

## 7. discussion_threads.jsonl

Each line is one discussion thread status JSON object with exact keys:

```text
channel_id
channel_username
channel_message_id
discussion_chat_id
discussion_root_message_id
comments_count
exported_comments_count
status
error
```

Allowed statuses:

```text
not_available
not_linked
no_comments
exported
partial
failed
```

## 8. manifest.json

Top-level manifest keys:

```text
dataset_type
schema_version
exported_at
source
export
discussion
status
```

`source` keys:

```text
type
id
username
title
```

`export` includes message and media counters, date bounds, formats, media mode, media limits, media type allowlist, and `included_files`.

`discussion` is `{"mode": "none"}` for default discussion mode. For `--discussion metadata`, it includes:

```text
mode
discussion_chat_id
metadata_count
comment_count
comments_exported
included_files
```

Current writers emit a discussion object. The `update-channels` batch reader also
accepts legacy manifests where `discussion` is missing or JSON `null`, treating
them as mode `none` without rewriting the artifact. Non-null scalar/list values
remain invalid.

For `--discussion full`, it includes:

```text
mode
discussion_chat_id
thread_count
comment_count
failed_thread_count
max_comments_per_post
included_files
```

## 9. channel_export_state.json

Channel state exact keys:

```text
schema_version
channel_id
channel_username
channel_title
last_exported_message_id
last_exported_at
message_count_total
media_count_total
downloaded_media_count_total
already_existing_media_count_total
skipped_media_count_total
skipped_by_size_count_total
skipped_by_type_count_total
failed_media_count_total
last_run_status
updated_at
date_from
date_to
last_manifest_path
```

The current `schema_version` is `1.0`.

## 10. discussion_export_state.json

Discussion state exact keys:

```text
schema_version
channel_id
discussion_chat_id
last_run_at
thread_count_total
comment_count_total
failed_thread_count_total
last_run_status
updated_at
```

The current `schema_version` is `1.0`.

## 11. TXT Projections

`messages.txt` and `discussion_comments.txt` are direct channel export human-readable projections. They are not canonical schemas and do not use the user/group `--txt-profile` profiles.

Contract tests only smoke-check stable identifying content such as message ids, timestamps, author/channel context, media sections, and comment text. They are not full golden snapshots.

## 12. Compatibility Rules

Compatibility rules:

- Do not change output filenames without explicit active stage scope.
- Do not change JSON key names or remove keys without explicit active stage scope.
- Nullable fields should remain present as keys with `null` values where the current schema emits them.
- `--discussion none` must not emit discussion dataset files.
- No-new-posts runs must not mutate discussion state.
- SQLite schema is unrelated to this filesystem dataset and must not be changed for dataset-format work.

## 13. Schema Change Policy

Any dataset schema change requires:

- explicit active stage scope;
- tests;
- docs update;
- changelog/update note if public behavior changes.

If documentation and implementation disagree, document current behavior first unless the active task explicitly permits a behavior change.
