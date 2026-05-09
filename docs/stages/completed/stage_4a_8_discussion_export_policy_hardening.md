# Stage 4A.8 — Channel Discussion Export Policy Hardening

## 1. Context

Channel discussion export is potentially very expensive.

A realistic channel dataset can contain:

```text
20 000 channel posts
100 comments per post
= 2 000 000 discussion comments
```

Even without media, this can produce multi-gigabyte JSONL/TXT outputs. With media, the dataset can grow to tens or hundreds of gigabytes.

The current infrastructure is not intended to handle mass discussion harvesting as a default workflow.

Therefore, discussion export must remain limited and explicit.

## 2. Goal

Do not expand full discussion comment export now.

Instead, formalize a safe policy:

```text
discussion none      — default / safest mode
discussion metadata  — lightweight metadata only
discussion full      — explicit heavy mode for small scoped runs
```

The project should prioritize safe discussion metadata extraction, not mass comment harvesting.

## 3. Required Product Policy

### 3.1 Default Mode

The default discussion mode must remain:

```text
none
```

No automatic full comment export.

### 3.2 Metadata Mode

Introduce or document a lightweight discussion metadata mode if not already present.

Expected concept:

```text
discussion metadata
```

This mode should collect only post-level discussion metadata, not comments.

For each channel post, store or expose metadata such as:

```json
{
  "channel_id": 1523454586,
  "channel_message_id": 59089,
  "has_comments": true,
  "discussion_chat_id": 2059154512,
  "replies_count": 90,
  "comments_exported": false,
  "source": "raw_payload.replies"
}
```

Acceptable source:

```text
raw_payload.replies.comments
raw_payload.replies.channel_id
raw_payload.replies.replies
```

Do not fetch discussion comments in metadata mode.

### 3.3 Full Mode

Keep full comment export as an explicit heavy mode only.

Expected use:

```bash
tg export-channel --channel <channel> --limit 100 --discussion full --max-comments-per-post 20
```

Full mode must not be encouraged for full multi-year channel archives.

## 4. Scope Decision

Current priority:

```text
safe discussion metadata extraction
```

Not priority:

```text
mass export of all comments around all channel posts
```

Do not build large-scale comment crawling infrastructure in this stage.

## 5. Implementation Tasks

### 5.1 Preserve Existing Full Mode

Do not remove `discussion full`.

Keep it available for small scoped exports.

Do not rewrite its internals unless needed for correctness or clear status reporting.

### 5.2 Add / Formalize Metadata Mode

If `metadata` mode does not exist, add it to discussion mode validation.

Valid modes should be:

```text
none
metadata
full
```

Rules:

- `none`: no discussion metadata file and no comment fetching, unless existing project contract says otherwise.
- `metadata`: extract post-level discussion metadata only; do not fetch comments.
- `full`: fetch comments with limits.

### 5.3 Extract Nested Telegram Replies Metadata

Ensure channel post mapping reads nested Telegram replies metadata:

```python
raw_payload["replies"]["comments"]
raw_payload["replies"]["channel_id"]
raw_payload["replies"]["replies"]
```

Required behavior:

- populate `replies_count` from nested `raw_payload.replies.replies` if top-level replies_count is missing;
- safely handle missing/non-dict `replies`;
- safely handle invalid values;
- do not crash on partial raw payload.

Top-level value should remain preferred:

```text
message.replies_count > raw_payload.replies_count > raw_payload.replies.replies
```

### 5.4 Metadata Output

If the current dataset schema already has an appropriate place for discussion metadata, reuse it.

If not, add a minimal metadata output file, for example:

```text
discussion_metadata.jsonl
```

Potential record shape:

```json
{
  "channel_id": 1523454586,
  "channel_message_id": 59089,
  "has_comments": true,
  "discussion_chat_id": 2059154512,
  "replies_count": 90,
  "comments_exported": false,
  "source": "raw_payload.replies"
}
```

Requirements:

- JSONL only is enough for MVP;
- no TXT projection required in this stage unless trivial;
- no full raw_payload duplication in metadata records;
- keep records compact.

### 5.5 Manifest / State

Update manifest summaries only if the project already records discussion outputs there.

Potential manifest fields:

```json
{
  "discussion": {
    "mode": "metadata",
    "metadata_count": 30,
    "comment_count": 0,
    "comments_exported": false
  }
}
```

Do not introduce complex state machinery for metadata mode unless necessary.

### 5.6 CLI / Menu

Expose mode choice consistently.

Direct CLI:

```bash
tg export-channel --channel <channel> --discussion none
tg export-channel --channel <channel> --discussion metadata
tg export-channel --channel <channel> --discussion full
```

Interactive menu should clearly distinguish:

```text
Discussion export mode [none/metadata/full] (Enter = none):
```

If user selects `full`, show a clear warning:

```text
Full discussion export is a heavy mode. Use small limits and max-comments-per-post.
```

Do not force confirmation if the project style avoids extra prompts, but the warning must be visible.

### 5.7 Safety Limits for Full Mode

Do not make large-scale full export easier in this stage.

If current limits exist, preserve them.

If adding guardrails is simple and consistent with current CLI style, add:

```text
--max-comments-per-post
```

default should remain conservative.

Do not add global crawling features such as:

```text
--all-comments-for-all-posts
```

## 6. Tests Required

Add or update tests.

### 6.1 Mode Validation Tests

Cover:

- `none` accepted;
- `metadata` accepted;
- `full` accepted;
- invalid mode rejected.

### 6.2 Post Mapper Tests

Cover:

- top-level replies_count is used;
- nested `raw_payload.replies.replies` is used when top-level missing;
- top-level value wins over nested value;
- missing replies does not crash;
- non-dict replies does not crash;
- invalid nested replies value does not crash.

### 6.3 Metadata Mode Tests

Cover:

- metadata mode writes discussion metadata records;
- metadata mode does not call comment fetcher;
- metadata mode sets `comments_exported = false`;
- metadata mode records `discussion_chat_id` from `raw_payload.replies.channel_id`;
- metadata mode records `has_comments` from `raw_payload.replies.comments`;
- metadata mode records `replies_count`.

### 6.4 Full Mode Regression Tests

Cover:

- full mode still calls discussion comment fetcher;
- existing full mode behavior is preserved;
- full mode does not become default.

### 6.5 CLI/Menu Tests

Cover:

- CLI accepts `--discussion metadata`;
- CLI default remains `none`;
- interactive empty input remains `none`;
- interactive metadata input is passed correctly;
- full mode warning is emitted or documented according to project style.

## 7. Hard Prohibitions

Do not:

- make `full` discussion export default;
- silently fetch comments in `metadata` mode;
- build mass comment crawling infrastructure;
- add media download for discussion comments;
- add OCR/STT/media analysis;
- add analytics/LLM/OSINT/profiling logic;
- change SQLite schema unless explicitly required and documented;
- rewrite channel export service broadly;
- duplicate large raw payloads in metadata records;
- remove existing `full` mode;
- break existing `none` mode;
- claim identity/profiling features.

## 8. Documentation

Update:

- `README.md`
- `docs/COMMANDS.md` or equivalent CLI reference
- `CHANGELOG.md` if used
- stage report if this is implemented as a stage

Documentation must explain:

```text
discussion none      — default, no discussion export
discussion metadata  — lightweight post-level discussion metadata
discussion full      — heavy comment export for small scoped runs
```

Mention explicitly:

```text
Full discussion export can produce very large datasets and should be used only with limits.
```

Suggested warning text:

```text
Full discussion export is a heavy mode. For large channels it can produce millions of records and multi-gigabyte datasets. Prefer metadata mode for broad channel archives.
```

## 9. Verification Commands

Run:

```bash
python3 -m compileall tg_msg_manager
pytest tests/test_channel_discussion*.py tests/test_channel_export*.py tests/test_channel_post_mapper*.py
ruff check tg_msg_manager tests
ruff format --check tg_msg_manager tests
```

If the project has make targets:

```bash
make test
make verify
```

Do not claim commands passed unless actually run.

## 10. Stage Lifecycle

If this is implemented as a stage:

1. Create a report:

```text
docs/stages/reports/STAGE_4A_8_DISCUSSION_EXPORT_POLICY_HARDENING_REPORT.md
```

2. Move task file from:

```text
docs/stages/active/
```

to:

```text
docs/stages/completed/
```

3. Update:

```text
docs/stages/README.md
```

4. Ensure `docs/stages/active/` contains only unfinished or next-stage tasks.

## 11. Final Agent Response Format

Use:

```markdown
## Summary

## Policy decision

## Files changed

## Behavior

## Tests

## Verification

## Remaining risks

## Status
```

In `Verification`, list only commands that were actually run and their actual result.
