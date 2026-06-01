# TXT Rendering

## Scope

TXT output is a human-readable projection for export artifacts. JSONL/database records remain canonical.

Direct channel export writes `messages.txt` and, with `--discussion full`, `discussion_comments.txt`. These files are direct renderer projections for reading channel datasets. They do not use the user/group `--txt-profile` profiles and are not a canonical schema.

## Profiles

- `context-readable` is the default TXT profile for user/group `export` and `db-export`.
- `legacy` preserves the old flat log-style TXT output and remains available explicitly.
- `DEFAULT_TXT_PROFILE` is `context-readable`.

## Context-Readable Structure

The readable profile renders deterministic context blocks from already available export/context records:

```text
CONTEXT BLOCK #0001
[REPLIED MESSAGE]
[CONTEXT BEFORE]
[TARGET MESSAGE] or [TARGET MESSAGES]
[CONTEXT AFTER]
```

Missing replies are compact:

```text
↪ missing reply #341081
```

The old technical missing-reply line remains limited to `legacy`.

## Boundaries

Renderers may format, order, and group already-provided records by existing fields such as `context_group_id`, `reply_to_id`, timestamps, authors, and text.

Renderers must not fetch, infer, repair, mutate, analyze, classify, OCR, STT, optimize media, alter context extraction, or change JSONL, dataset, state, or SQLite schemas.

Channel TXT tests are smoke/marker checks for stable identifying content such as message ids, timestamps, author/channel context, media sections, and comment text. They are not full golden snapshots of every rendered line.
