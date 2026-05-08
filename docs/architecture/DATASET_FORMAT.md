# Dataset Format

## 1. Overview

`export-channel` writes a filesystem-first dataset under `exports/channels/<channel_slug>/`.

Current dataset files:

```text
manifest.json
messages.jsonl
messages.txt
media_manifest.jsonl
channel_export_state.json
media/
discussion_comments.jsonl
discussion_comments.txt
discussion_threads.jsonl
discussion_export_state.json
```

Discussion files are written only for explicit `--discussion full` runs with current-run posts. Media files under `media/` are written only for explicit `--media full`.

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

## 4. discussion_comments.jsonl

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

## 5. discussion_threads.jsonl

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

## 6. manifest.json

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

`discussion` is `{"mode": "none"}` for default discussion mode. For `--discussion full`, it includes:

```text
mode
discussion_chat_id
thread_count
comment_count
failed_thread_count
max_comments_per_post
included_files
```

## 7. channel_export_state.json

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

## 8. discussion_export_state.json

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

## 9. TXT Projections

`messages.txt` and `discussion_comments.txt` are human-readable projections.

Contract tests only smoke-check stable identifying content such as message ids, timestamps, author/channel context, media sections, and comment text. They are not full golden snapshots.

## 10. Compatibility Rules

Compatibility rules:

- Do not change output filenames without explicit active stage scope.
- Do not change JSON key names or remove keys without explicit active stage scope.
- Nullable fields should remain present as keys with `null` values where the current schema emits them.
- `--discussion none` must not emit discussion dataset files.
- No-new-posts runs must not mutate discussion state.
- SQLite schema is unrelated to this filesystem dataset and must not be changed for dataset-format work.

## 11. Schema Change Policy

Any dataset schema change requires:

- explicit active stage scope;
- tests;
- docs update;
- changelog/update note if public behavior changes.

If documentation and implementation disagree, document current behavior first unless the active task explicitly permits a behavior change.
