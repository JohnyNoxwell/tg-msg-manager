# STAGE 4A.6 — CONTEXT_GROUP_ID FALLBACK HARDENING FOR CONTEXT-READABLE TXT

Status: active task  
Stage: 4A.6  
Type: renderer hardening / output correctness  
Depends on: Stage 4A.5 — Context-Readable TXT Export Profile

---

## 0. CODEX ENTRY CONTRACT

```text
Read AGENTS.md first.

You are working on tg-msg-manager.

Execute Stage 4A.6 — Context Group ID Fallback Hardening for Context-Readable TXT.

This task fixes a renderer fallback risk discovered after Stage 4A.5.

The context-readable TXT renderer currently groups messages by `context_group_id` when present.
However, if export records contain target and non-target context messages without `context_group_id`,
fallback grouping may create blocks only from target messages and omit surrounding non-target context.

This is a renderer/output hardening task.

Do not rewrite context extraction.
Do not change deep-mode algorithm.
Do not change Telegram fetching.
Do not change SQLite schema.
Do not change JSONL schema.
Do not change dataset/state schema.
Do not add analytics, OSINT, profiling, OCR, STT, media processing, dashboards, or SaaS logic.
```

---

## 1. PROBLEM

Stage 4A.5 added:

```text
context-readable TXT profile
legacy TXT profile
CLI/menu profile selection
```

The new renderer groups by existing `context_group_id`.

Risk:

```text
If records have no context_group_id, non-target context messages may be dropped from output.
```

Example broken scenario:

```text
records:
  10:00 User A: before context
  10:01 Target: target message
  10:02 User B: after context

context_group_id:
  None
  None
  None
```

Expected output:

```text
[CONTEXT BEFORE]
10:00 User A
before context

[TARGET MESSAGE]
10:01 Target
target message

[CONTEXT AFTER]
10:02 User B
after context
```

Unacceptable output:

```text
[CONTEXT BEFORE]
None

[TARGET MESSAGE]
10:01 Target
target message

[CONTEXT AFTER]
None
```

---

## 2. GOAL

Ensure `context-readable` TXT output preserves non-target context messages whenever the export pipeline already provides them, even when `context_group_id` is missing.

Required behavior:

```text
1. Records with context_group_id remain grouped by context_group_id.
2. Records without context_group_id are not silently dropped.
3. If ungrouped records contain at least one target message, render them as a context block.
4. If all records are ungrouped and include before/target/after messages, output must preserve before/after context.
5. Do not fetch missing replies.
6. Do not reconstruct full reply trees.
7. Do not infer conversation meaning.
```

---

## 3. HARD PROHIBITIONS

Do not implement:

```text
- new Telegram fetch behavior
- new context extraction logic
- deep-mode algorithm changes
- context window calculation changes
- reply-tree reconstruction engine
- database migrations
- SQLite schema changes
- JSONL schema changes
- dataset schema changes
- state schema changes
- media handling changes
- analytics
- OSINT interpretation
- profiling
- sentiment analysis
- bot detection
- OCR
- STT
- media analysis
- media optimization
- dashboards/UI/TUI rewrite
```

---

## 4. PROTECTED FILES

Do not add new feature logic directly into:

```text
tg_msg_manager/services/export/service.py
tg_msg_manager/services/db_export/service.py
tg_msg_manager/services/private_archive/service.py
tg_msg_manager/services/context/engine.py
tg_msg_manager/services/channel_export/service.py
```

Allowed:

```text
- renderer-only fix
- tests
- documentation/report note
- minimal imports if required
```

Expected primary file:

```text
tg_msg_manager/services/rendering/context_readable_txt_renderer.py
```

---

## 5. FILES TO INSPECT

Before changing code, inspect:

```text
tg_msg_manager/services/rendering/context_readable_txt_renderer.py
tg_msg_manager/services/rendering/models.py
tg_msg_manager/services/rendering/txt_renderer.py
tg_msg_manager/services/db_export/payload_writer.py
tests/test_context_readable_txt_renderer.py
tests/test_export_txt_profile_integration.py
docs/stages/reports/STAGE_4A_5_CONTEXT_READABLE_TXT_PROFILE_REPORT.md
```

Confirm current behavior before patching.

---

## 6. RECOMMENDED IMPLEMENTATION

Target method:

```text
ContextReadableTxtRenderer._group_messages()
```

Recommended minimal policy:

```text
- keep current grouping by context_group_id
- collect messages without context_group_id into fallback_messages
- if fallback_messages contain target messages, append fallback_messages as one additional block
- if target_user_id is None, append fallback_messages as one additional block
- if fallback_messages contain no target messages and grouped blocks exist, do not create confusing standalone block
- if fallback_messages contain no target messages and no grouped blocks exist, append fallback_messages as one fallback block
```

Pseudo-logic:

```python
groups = list(grouped.values())

if fallback_messages:
    if target_user_id is None:
        groups.append(fallback_messages)
    elif any(message.user_id == target_user_id for message in fallback_messages):
        groups.append(fallback_messages)
    elif not groups:
        groups.append(fallback_messages)

if not groups and messages:
    groups.append(messages)
```

Then preserve existing deterministic sorting:

```python
return sorted(
    groups,
    key=lambda group: (
        min(message.timestamp for message in group),
        min(message.message_id for message in group),
    ),
)
```

Do not overbuild local-window clustering in this stage.

---

## 7. EDGE CASE RULES

### A. All records grouped

If all messages have `context_group_id`:

```text
Behavior should remain unchanged.
```

### B. All records ungrouped and contain target

If no message has `context_group_id`, but records include target and non-target context:

```text
Render one context block preserving before/target/after.
```

### C. Mixed grouped + ungrouped

If some records are grouped and some are ungrouped:

```text
- grouped records remain grouped by context_group_id
- ungrouped records containing target are rendered as fallback block
- output order remains chronological by block start
```

### D. Ungrouped non-target-only records

If ungrouped records do not contain target:

Recommended:

```text
Do not create an extra block if grouped target blocks already exist.
```

Fallback:

```text
If there are no other groups, render them as one block to avoid total data loss.
```

### E. Missing replied message

No change:

```text
↪ missing reply #id
```

Do not fetch missing replied messages.

---

## 8. TEST TASKS

Update or create:

```text
tests/test_context_readable_txt_renderer.py
```

Add tests:

### Test 1 — preserves ungrouped before/target/after

- [ ] Create 3 `RenderMessage` records.
- [ ] All have `context_group_id=None`.
- [ ] First record is non-target.
- [ ] Second record is target.
- [ ] Third record is non-target.
- [ ] Render with `target_user_id`.
- [ ] Assert output contains `[CONTEXT BEFORE]`.
- [ ] Assert before text appears after `[CONTEXT BEFORE]`.
- [ ] Assert output contains `[TARGET MESSAGE]`.
- [ ] Assert target text appears.
- [ ] Assert output contains `[CONTEXT AFTER]`.
- [ ] Assert after text appears.

### Test 2 — does not drop ungrouped non-target markers

- [ ] Use unique marker strings:
  ```text
  BEFORE_UNGROUPED_MARKER
  TARGET_UNGROUPED_MARKER
  AFTER_UNGROUPED_MARKER
  ```
- [ ] Assert all markers appear in output.

### Test 3 — grouped behavior remains unchanged

- [ ] Create records with same `context_group_id`.
- [ ] Render.
- [ ] Assert one `CONTEXT BLOCK`.
- [ ] Assert context before/target/after sections are correct.

### Test 4 — mixed grouped + fallback target block

- [ ] Create one grouped cluster with target.
- [ ] Create one ungrouped cluster containing target and context.
- [ ] Render.
- [ ] Assert output contains two `CONTEXT BLOCK` headers.
- [ ] Assert ungrouped context text appears.
- [ ] Assert chronological block order is deterministic.

### Test 5 — ungrouped non-target-only records

- [ ] Create grouped target block.
- [ ] Add ungrouped non-target-only record.
- [ ] Assert behavior matches chosen policy.
- [ ] Preferred: non-target-only fallback record does not create separate confusing target block.
- [ ] Document/test chosen policy.

---

## 9. OPTIONAL DOC / REPORT UPDATE

If repository stage lifecycle expects every micro-stage to have a report, create:

```text
docs/stages/reports/STAGE_4A_6_CONTEXT_GROUP_ID_FALLBACK_HARDENING_REPORT.md
```

Minimum sections:

```text
# Stage 4A.6 — Context Group ID Fallback Hardening Report

## 1. Summary
## 2. Problem
## 3. Behavior fixed
## 4. Files changed
## 5. Tests
## 6. Verification results
## 7. Runtime behavior statement
## 8. Remaining limitations
## 9. Status
```

Runtime behavior statement:

```text
No Telegram fetching behavior changed.
No context extraction behavior changed.
No JSONL schema changed.
No dataset/state schema changed.
No SQLite schema changed.
No analytics/OCR/STT/media optimization added.
```

Update if applicable:

```text
CHANGELOG.md
docs/stages/README.md
```

Keep docs concise.

---

## 10. VERIFICATION

Run at minimum:

```bash
pytest tests/test_context_readable_txt_renderer.py
pytest tests/test_export_txt_profile_integration.py
python3 -m compileall tg_msg_manager
ruff check tg_msg_manager tests
ruff format --check tg_msg_manager tests
```

If practical:

```bash
pytest tests/test_*txt*profile*.py tests/test_*txt*renderer*.py tests/test_cli*.py
make test
make verify
```

Do not claim commands passed unless actually run.

---

## 11. COMPLETION CRITERIA

Stage 4A.6 is complete only if:

- [ ] ungrouped target/context records are preserved.
- [ ] non-target before/after messages are not dropped when `context_group_id` is missing.
- [ ] grouped `context_group_id` behavior remains unchanged.
- [ ] mixed grouped + fallback records are deterministic.
- [ ] tests cover the fallback risk.
- [ ] no context extraction behavior changed.
- [ ] no schema/storage/fetching behavior changed.
- [ ] verification commands were run or honestly reported as not run.
