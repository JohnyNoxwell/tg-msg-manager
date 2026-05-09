# STAGE 4A.5.2 — CONTEXT-READABLE TXT RENDERER

Status: active task  
Stage: 4A.5.2  
Type: new TXT renderer profile  
Depends on: Stage 4A.5.1

---

## 0. CODEX ENTRY CONTRACT

```text
Read AGENTS.md first.

Execute Stage 4A.5.2 — Context-Readable TXT Renderer.

Implement the new human-readable context block TXT renderer.

Do not change how context is collected.
Do not fetch missing replies.
Do not infer missing conversation structure.
Do not add analytics or interpretation.
```

---

## 1. PURPOSE

Add a readable TXT profile for group/user exports with context.

Profile name:

```text
context-readable
```

Main structure:

```text
[REPLIED MESSAGE]
[CONTEXT BEFORE]
[TARGET MESSAGE] or [TARGET MESSAGES]
[CONTEXT AFTER]
```

The whole file should be split into context blocks.

---

## 2. OUTPUT STRUCTURE

Recommended file header:

```text
# Telegram Export
TXT profile: context-readable
Target: <name> (<id>)
Chat: <chat title / id>
Generated at: <timestamp if already available>
```

Do not add generated timestamp if project tests require deterministic output and no timestamp source exists. Prefer deterministic test output.

Recommended block header:

```text
────────────────────────────────────────────────────────────
CONTEXT BLOCK #0001 · 2024-02-17
TARGET: Volodymyr (716598577)
CHAT: Example Chat (-100...)
TIME RANGE: 15:50:41–16:50:27
TARGET MESSAGES: 1
────────────────────────────────────────────────────────────
```

Sections:

```text
[REPLIED MESSAGE]
...

[CONTEXT BEFORE]
...

[TARGET MESSAGE]
...

[CONTEXT AFTER]
...
```

If several target messages:

```text
[TARGET MESSAGES]
...
```

---

## 3. MESSAGE RENDERING RULES

Single message format:

```text
15:59:21 · Ната (5224126993)
↪ replies to User · 15:50:41 · "excerpt..."
Text...
```

If no reply:

```text
15:59:21 · Ната (5224126993)
Text...
```

If reply target missing:

```text
15:59:21 · Ната (5224126993)
↪ missing reply #341081
Text...
```

If text is empty:

```text
(empty message)
```

or project's existing empty message marker.

Keep multiline text readable:

```text
15:59:21 · Ната (5224126993)
Line 1
Line 2
Line 3
```

Do not over-indent.

---

## 4. REPLIED MESSAGE RULES

`[REPLIED MESSAGE]` should represent the message directly replied to by the target message, if known.

Cases:

### A. Target replies to known message

```text
[REPLIED MESSAGE]
15:59:21 · Ната (5224126993)
Ну суд, судом...
```

### B. Target replies to missing message

```text
[REPLIED MESSAGE]
↪ missing reply #341081
```

### C. Target does not reply

```text
[REPLIED MESSAGE]
None
```

### D. Multiple target messages with different replied messages

Use:

```text
[REPLIED MESSAGE]
Multiple replied messages:
- target #341099 -> Ната · 15:59:21 · "Ну суд..."
- target #341102 -> missing reply #341081
```

or render each under target message if simpler.

Do not duplicate a full replied message if it already appears in context before unless duplication is currently simpler and tests allow it. Preferred compact version:

```text
[REPLIED MESSAGE]
15:59:21 · Ната — see CONTEXT BEFORE
```

---

## 5. CONTEXT BLOCK GROUPING RULES

Use existing context group/cluster data if available.

Do not invent a new context extraction algorithm.

Expected principle:

```text
One context block = one context cluster containing one or more target messages.
```

If the current export already has context group ids:

- [ ] group by `context_group_id`.
- [ ] order blocks by earliest timestamp/message id.
- [ ] assign stable block numbers.

If no context group ids are available:

- [ ] keep existing ordering.
- [ ] create one block per target message as a fallback.
- [ ] do not create complex clustering in this stage.

Optional merge rules only if already supported by existing data:

```text
- merge overlapping context windows
- avoid duplicate context messages
```

Do not build a full conversation thread engine.

---

## 6. SECTION ASSIGNMENT RULES

For each block:

```text
target messages = messages authored by target user
context before = non-target messages before first target message
context after = non-target messages after last target message
replied message = direct replied-to message of target message if available
```

If target messages appear before/after each other:

```text
keep all target messages in TARGET MESSAGES section
```

If a context message is also the replied message:

```text
render in CONTEXT BEFORE/AFTER and reference it in REPLIED MESSAGE, or duplicate if simpler.
```

Prefer no duplicate.

---

## 7. NOISY TECHNICAL METADATA RULES

Do not render this in context-readable:

```text
[reply_to: 321029 - original message not found in local DB]
```

Render this instead:

```text
↪ missing reply #321029
```

Do not render raw payloads.

Do not render internal Python object representations.

---

## 8. TRUNCATION RULES

Reply excerpts should be short.

Recommended default:

```text
max_reply_excerpt_chars = 80
```

If longer:

```text
"Боржників у Харкові не будуть відключати..."
```

Preserve full message text in actual message body.

Only excerpts are truncated.

---

## 9. TESTS

Create / update:

```text
tests/test_context_readable_txt_renderer.py
```

Required tests:

- [ ] renders file/header or block header.
- [ ] renders `[REPLIED MESSAGE]`.
- [ ] renders `[CONTEXT BEFORE]`.
- [ ] renders `[TARGET MESSAGE]`.
- [ ] renders `[TARGET MESSAGES]` when multiple target messages exist.
- [ ] renders `[CONTEXT AFTER]`.
- [ ] renders missing reply as `↪ missing reply #id`.
- [ ] does not render old noisy missing reply line.
- [ ] renders reply excerpt compactly.
- [ ] groups records by context group id if available.
- [ ] falls back safely when no context group id exists.
- [ ] output is deterministic.

Use synthetic records. Do not require Telegram.

---

## 10. VERIFICATION

Run:

```bash
pytest tests/test_context_readable_txt_renderer.py tests/test_txt_profiles.py
python3 -m compileall tg_msg_manager
ruff check tg_msg_manager tests
ruff format --check tg_msg_manager tests
```

Do not claim commands passed unless actually run.

---

## 11. COMPLETION CRITERIA

Complete only if:

- [ ] `context-readable` renderer exists.
- [ ] output uses context blocks.
- [ ] sections match required labels.
- [ ] missing replies are compact.
- [ ] multiple target messages in one block are supported or safely handled.
- [ ] renderer is deterministic.
- [ ] tests cover core readable format.
- [ ] no export/context algorithm changed.
