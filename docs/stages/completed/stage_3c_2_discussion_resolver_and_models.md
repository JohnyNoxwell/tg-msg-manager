# STAGE 3C.2 — DISCUSSION RESOLVER AND MODELS

Status: completed
Stage: 3C.2
Scope: historical task instructions

## 0. CODEX ENTRY PROMPT

```text
Read AGENTS.md first.

Then read this file completely before editing anything.

You are working on tg-msg-manager.

This task is part of Stage 3C — Channel Discussion Context Export.

Follow the scope exactly. Do not implement later Stage 3C parts unless this file explicitly allows it.

When in doubt, preserve existing behavior and stop at the boundary defined in this file.
```

---

## 1. GLOBAL ARCHITECTURAL DECISION

Stage 3C is an export/dataset-layer extension only.

```text
Stage 3C does not write discussion data into SQLite.
Stage 3C does not change SQLite schema.
Stage 3C does not change existing export/db-export/export-pm behavior.
Stage 3C does not add analytics.
Stage 3C does not add OSINT interpretation.
Stage 3C does not add OCR, speech-to-text, image/video/audio analysis.
```

Discussion data must be represented as files inside the channel export dataset, not as database records.

Target dataset direction:

```text
exports/channels/<channel_slug>/
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

The exact files are introduced gradually across Stage 3C sub-stages. Do not create files outside the current task scope.

---

## 2. HARD PROHIBITIONS

Do not implement:

```text
- SQLite schema changes
- DB persistence for discussion comments
- migrations
- discussion/comment analytics
- sentiment analysis
- bot detection
- user profiling
- influence scoring
- narrative classification
- OCR
- image/video analysis
- speech-to-text
- media full download for discussion comments
- reply-tree reconstruction beyond preserving reply_to_id
- refresh/backfill of old discussion threads outside current-run posts
- Stage 3D
- Stage 4
- GUI/dashboard/SaaS features
```

Do not add feature logic to protected hot-path files:

```text
tg_msg_manager/services/export/service.py
tg_msg_manager/services/db_export/service.py
tg_msg_manager/services/private_archive/service.py
tg_msg_manager/services/context/engine.py
```

Do not bloat:

```text
tg_msg_manager/services/channel_export/service.py
```

`ChannelExportService` may orchestrate only. Any discussion-specific logic must live under:

```text
tg_msg_manager/services/channel_export/discussions/
```

---


## 3. PURPOSE

This stage introduces the discussion architecture skeleton:

```text
- discussion options
- discussion models
- discussion state model
- discussion resolver
- CLI argument parsing
```

This stage must not fetch comments and must not write discussion dataset files.

---

## 4. ALLOWED SCOPE

Allowed:

```text
tg_msg_manager/services/channel_export/discussions/
tg_msg_manager/services/channel_export/models.py
tg_msg_manager/cli_parser.py
tg_msg_manager/cli_commands.py
tests/test_channel_export_discussion_*.py
tests/test_channel_export_cli.py
docs/refactor/STAGE_3C_CHANNEL_DISCUSSION_CONTEXT_EXPORT_DESIGN.md
```

Potentially allowed only if necessary:

```text
tg_msg_manager/services/channel_export/service.py
```

But only to carry options through existing structures. Do not implement discussion export in the service in this stage.

---

## 5. EXPECTED CLI CONTRACT

Add:

```bash
--discussion none|full
--max-comments-per-post N
```

Default:

```text
--discussion none
```

Recommended default for max comments:

```text
100
```

Validation:

```text
--max-comments-per-post must be a positive integer.
```

Do not add:

```text
--discussion-media
--discussion-depth
--refresh-discussions
--backfill-discussions
```

---

## 6. TARGET FILES

Create:

```text
tg_msg_manager/services/channel_export/discussions/__init__.py
tg_msg_manager/services/channel_export/discussions/errors.py
tg_msg_manager/services/channel_export/discussions/options.py
tg_msg_manager/services/channel_export/discussions/models.py
tg_msg_manager/services/channel_export/discussions/resolver.py
```

Add tests:

```text
tests/test_channel_export_discussion_options.py
tests/test_channel_export_discussion_models.py
tests/test_channel_export_discussion_resolver.py
```

Update if needed:

```text
tests/test_channel_export_cli.py
```

---

## 7. MODEL CONTRACT

### 7.1. Options

Define constants:

```python
DISCUSSION_MODE_NONE = "none"
DISCUSSION_MODE_FULL = "full"
ALLOWED_DISCUSSION_MODES = {"none", "full"}
```

Define validation:

```python
validate_discussion_mode(value: str) -> str
```

Behavior:

- [ ] lowercases input
- [ ] strips whitespace
- [ ] accepts `none`
- [ ] accepts `full`
- [ ] raises `ValueError` for unsupported values

Define max comments validation if not handled in CLI only:

```python
validate_max_comments_per_post(value: int) -> int
```

Behavior:

- [ ] accepts positive integer
- [ ] rejects zero
- [ ] rejects negative values

### 7.2. Discussion options

Either extend `ChannelExportOptions` directly:

```python
discussion_mode: str = "none"
max_comments_per_post: int = 100
```

Or create a nested dataclass:

```python
ChannelDiscussionOptions
```

Preferred simple MVP:

```python
@dataclass(frozen=True)
class ChannelDiscussionOptions:
    mode: str = "none"
    max_comments_per_post: int = 100
```

Then include it in `ChannelExportOptions` only if this fits current style.

Avoid overengineering.

### 7.3. Thread record

Create:

```python
ChannelDiscussionThreadRecord
```

Fields:

```text
channel_id: int
channel_username: Optional[str]
channel_message_id: int
discussion_chat_id: Optional[int]
discussion_root_message_id: Optional[int]
comments_count: int
exported_comments_count: int
status: str
error: Optional[str] = None
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

### 7.4. Comment record

Create:

```python
ChannelDiscussionCommentRecord
```

Fields:

```text
message_id: int
discussion_chat_id: int
channel_id: int
channel_message_id: int
discussion_root_message_id: Optional[int]
author_id: Optional[int]
author_name: Optional[str]
username: Optional[str]
timestamp: datetime
text: Optional[str]
reply_to_id: Optional[int]
media: tuple
reactions: dict
raw_payload: dict
```

Media should remain metadata only or empty in Stage 3C.

### 7.5. Discussion state

Create:

```python
ChannelDiscussionExportState
```

Fields:

```text
schema_version: str
channel_id: int
discussion_chat_id: Optional[int]
last_run_at: Optional[datetime]
thread_count_total: int
comment_count_total: int
failed_thread_count_total: int
last_run_status: str
updated_at: datetime
```

### 7.6. Discussion result

Create:

```python
ChannelDiscussionExportResult
```

Fields:

```text
mode: str
discussion_chat_id: Optional[int]
thread_count: int
comment_count: int
failed_thread_count: int
comments_jsonl_path: Optional[Path]
comments_txt_path: Optional[Path]
threads_jsonl_path: Optional[Path]
state_path: Optional[Path]
```

---

## 8. RESOLVER CONTRACT

Create a resolver skeleton:

```python
class ChannelDiscussionResolver:
    async def resolve(self, channel_entity: Any) -> ChannelDiscussionSource:
        ...
```

Create source model:

```python
ChannelDiscussionSource
```

Fields:

```text
status: str
discussion_chat_id: Optional[int]
discussion_entity: Optional[Any]
error: Optional[str]
```

Allowed source statuses:

```text
disabled
not_available
not_linked
resolved
failed
```

Expected behavior:

- [ ] If discussion mode is `none`, resolver should not be called by runtime later.
- [ ] Resolver should be safe if channel has no linked discussion group.
- [ ] Resolver should not throw for normal not-linked cases.
- [ ] Resolver may return `failed` for unexpected exceptions.
- [ ] Resolver should not fetch comments.
- [ ] Resolver should not write files.
- [ ] Resolver should not modify state.

Telegram-specific lookup should be conservative. Use available entity attributes if present. If the real Telegram client API requires a specific request, isolate it behind this resolver and keep it testable with fake clients/entities.

Do not assume every channel has discussions.

---

## 9. CLI TASKS

Update parser:

- [ ] Add `--discussion`.
- [ ] Choices:
  - [ ] `none`
  - [ ] `full`
- [ ] Default:
  - [ ] `none`
- [ ] Add `--max-comments-per-post`.
- [ ] Type:
  - [ ] positive integer parser.
- [ ] Default:
  - [ ] `100`

Update command handler:

- [ ] Pass discussion mode into export options.
- [ ] Pass max comments per post into export options.
- [ ] Do not run discussion export yet.
- [ ] Do not print discussion summary yet unless result structure already supports it safely.

---

## 10. TEST TASKS

### A. Options tests

- [ ] `validate_discussion_mode("none") == "none"`
- [ ] `validate_discussion_mode("full") == "full"`
- [ ] `validate_discussion_mode(" FULL ") == "full"`
- [ ] invalid mode raises `ValueError`
- [ ] max comments accepts `1`
- [ ] max comments accepts `100`
- [ ] max comments rejects `0`
- [ ] max comments rejects `-1`

### B. CLI tests

- [ ] parser accepts default discussion mode.
- [ ] parser accepts `--discussion none`.
- [ ] parser accepts `--discussion full`.
- [ ] parser rejects invalid discussion mode.
- [ ] parser accepts `--max-comments-per-post 50`.
- [ ] parser rejects `--max-comments-per-post 0`.
- [ ] parser rejects `--max-comments-per-post -1`.

### C. Model tests

- [ ] thread record can be constructed.
- [ ] comment record can be constructed.
- [ ] state record can be constructed.
- [ ] result record can be constructed.

### D. Resolver tests

Use fake client/entity.

- [ ] no linked discussion returns `not_linked`.
- [ ] resolved linked discussion returns `resolved`.
- [ ] unexpected client error returns `failed` or raises a domain-specific error according to chosen contract.
- [ ] resolver does not fetch comments.

---

## 11. DOCUMENTATION TASKS

Update design note if needed:

```text
docs/refactor/STAGE_3C_CHANNEL_DISCUSSION_CONTEXT_EXPORT_DESIGN.md
```

Add a short 3C.2 progress note if the repository uses stage reports:

```text
docs/refactor/STAGE_3C_2_DISCUSSION_RESOLVER_AND_MODELS_REPORT.md
```

Report must say:

```text
- models/options/resolver added
- CLI accepts discussion flags
- no comments fetching implemented
- no dataset files written
- no SQLite changes
- Stage 3C.3 not started
```

---

## 12. VERIFICATION COMMANDS

Run:

```bash
pytest tests/test_channel_export_discussion_*.py tests/test_channel_export_cli.py
pytest tests/test_channel_export_*.py
python3 -m compileall tg_msg_manager
ruff check tg_msg_manager tests
ruff format --check tg_msg_manager tests
python3 -m tg_msg_manager.cli export-channel --help
```

Do not claim commands passed unless actually run.

---

## 13. COMPLETION CRITERIA

Complete only if:

- [ ] Discussion options exist.
- [ ] Discussion models exist.
- [ ] Discussion resolver skeleton exists.
- [ ] CLI accepts `--discussion none|full`.
- [ ] CLI accepts `--max-comments-per-post`.
- [ ] Default remains `--discussion none`.
- [ ] No comments are fetched.
- [ ] No discussion files are written.
- [ ] No SQLite schema changes.
- [ ] Existing channel export tests still pass.
- [ ] Stage 3C.3 not started.

---

## 14. FINAL RESPONSE FORMAT

```text
## Summary
- discussion models/options/resolver added
- CLI flags added
- no comment fetching implemented

## Files changed
- path
- path

## Tests
- command: result

## Behavior preserved
- default discussion none
- no SQLite changes
- no legacy command changes

## Stage status
Stage 3C.2: complete / partial / blocked
Stage 3C.3: not started
```
