# TXT Rendering

## Scope

TXT output is a human-readable projection for export artifacts. JSONL/database records remain canonical.

## Profiles

- `context-readable` is the default TXT profile for user/group `export`.
- `legacy` preserves the old flat log-style TXT output and remains available explicitly.
- `db-export` remains legacy TXT by default.

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
