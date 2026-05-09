# Discussion Export Diagnoser

## Purpose

Diagnose Telegram channel discussion export problems from runtime output and exported artifacts.

Use this skill to distinguish `not_linked`, metadata-only behavior, full fetch failures, wrong discussion root handling, access/API problems, and incremental no-new-work states.

This skill diagnoses. It does not expand discussion crawling or implement fixes unless explicitly requested.

## When To Use

Use when channel discussion export produces:

```text
0 comments
not_linked threads
failed threads
missing discussion_chat_id
missing discussion_root_message_id
unexpected metadata-only output
Telegram API errors
```

## Inputs

Use only relevant available artifacts:

```text
runtime console output
manifest.json
messages.jsonl
discussion_threads.jsonl
discussion_comments.jsonl
discussion_export_state.json
channel_export_state.json
```

Important fields:

```text
discussion.mode
thread_count
comment_count
failed_thread_count
status
channel_message_id
discussion_chat_id
discussion_root_message_id
comments_count
exported_comments_count
error
raw_payload.replies.channel_id
raw_payload.replies.replies
```

If artifacts are insufficient, request the single most useful missing artifact or field.

## Diagnostic Rules

### Mode: none

If mode is `none`:

```text
no discussion export is expected
0 comments is expected
```

### Mode: metadata

If mode is `metadata`:

```text
full comments are not expected
only lightweight post-level discussion metadata should be exported
0 discussion_comments rows may be expected
```

### Status: not_linked

Likely when:

```text
discussion_chat_id is null
status is not_linked
thread rows exist
comments are 0
```

If `messages.jsonl` has:

```text
raw_payload.replies.channel_id
raw_payload.replies.replies
```

but thread rows have `discussion_chat_id = null`, likely cause:

```text
mapper/resolver ignores raw_payload.replies.channel_id or raw_payload.replies.replies
```

### Status: failed

Likely when:

```text
status is failed
discussion_chat_id is present
error is present
exported_comments_count is 0
failed_thread_count > 0
```

If errors include:

```text
MsgIdInvalid
PeerIdInvalid
The message ID used in the peer was invalid
Cannot get replies
```

Likely cause:

```text
fetcher uses channel post message_id as reply_to inside discussion group instead of discussion root message id
```

### Empty but not failed

If:

```text
status is linked or metadata
comments_count is 0
exported_comments_count is 0
error is null
```

Likely cause may be:

```text
post has no comments
metadata mode does not fetch comments
state says no new work
```

### Incremental no-new-work

Check state files for:

```text
last exported message id
tail state
force_full flag
no-new-work indicators
```

If force/full was not used and state is current, 0 new comments may be expected.

## Hard Prohibitions

Do not recommend:

```text
making discussion full the default
mass crawling comments by default
raising max comments for broad archives
adding analytics/LLM/profiling to exporter
changing SQLite schema unless active stage explicitly allows it
```

Preferred policy:

```text
discussion none      — safe/default
discussion metadata  — broad archive mode
discussion full      — explicit heavy mode for small scoped runs
```

## Output Format

Return only:

```text
DIAGNOSIS:
- <short diagnosis>

EVIDENCE:
- <artifact/field>: <value or pattern>

LIKELY_CAUSE:
- <short cause>

NEXT_PATCH:
- <minimal patch direction>

DO_NOT:
- <forbidden expansion or none>

CONFIDENCE:
- low/medium/high
```

## Rules

No broad architecture essay.

No implementation until asked.

Do not invent missing artifact fields.

Prefer exact error strings.

If artifacts are insufficient, ask for one missing artifact only.

## Example

Input:

```text
Discussion threads this run: 10
Discussion comments this run: 0
Failed discussion threads this run: 10
error: MsgIdInvalid
discussion_chat_id: present
discussion_root_message_id: null
```

Output:

```text
DIAGNOSIS:
- full discussion fetch reaches discussion entity but fails for every thread

EVIDENCE:
- failed_thread_count: 10
- error: MsgIdInvalid
- discussion_chat_id: present
- discussion_root_message_id: null

LIKELY_CAUSE:
- fetcher likely uses channel post message_id as reply_to inside discussion group instead of discussion root message id

NEXT_PATCH:
- resolve and store discussion_root_message_id before fetching replies; use root id for full fetch

DO_NOT:
- do not make full discussion export default or expand mass crawling

CONFIDENCE:
- high
```
