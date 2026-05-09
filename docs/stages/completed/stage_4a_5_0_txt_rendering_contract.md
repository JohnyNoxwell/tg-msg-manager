# STAGE 4A.5.0 — TXT RENDERING CONTRACT / ARCHITECTURE BOUNDARY

Status: active task  
Stage: 4A.5.0  
Type: rendering architecture contract  
Scope: TXT export presentation only

---

## 0. CODEX ENTRY CONTRACT

```text
Read AGENTS.md first.

You are working on tg-msg-manager.

Execute Stage 4A.5.0 — TXT Rendering Contract / Architecture Boundary.

This stage defines the architecture boundary for a new context-readable TXT profile.

This is not an exporter rewrite.
This is not a context extraction rewrite.
This is not a dataset schema stage.
This is not a SQLite stage.
This is not an analytics stage.

Do not change message collection semantics.
Do not change context/deep-mode semantics.
Do not change JSONL schema.
Do not change SQLite schema.
Do not add analytics, OSINT, profiling, OCR, STT, media processing, dashboards, or SaaS logic.
```

---

## 1. PURPOSE

Current problem:

```text
Existing TXT output is too log-like for grouped chat exports with context.
It shows messages linearly and exposes technical reply metadata too loudly.
It is hard to read as conversation context.
```

Target:

```text
Add a new default human-readable TXT profile for group/user exports with context.
```

Preferred visible structure:

```text
CONTEXT BLOCK #0001 · 2024-02-17
TARGET: Volodymyr (716598577)
CHAT: <chat title / chat_id>
TIME RANGE: 15:50:41–16:50:27

[REPLIED MESSAGE]
...

[CONTEXT BEFORE]
...

[TARGET MESSAGE]
...

[CONTEXT AFTER]
...
```

If multiple target messages exist in one merged context cluster:

```text
[TARGET MESSAGES]
...
```

---

## 2. REQUIRED PROFILES

Implement TXT profiles:

```text
context-readable
legacy
```

Default decision:

```text
export TXT default: context-readable
legacy available explicitly
```

Compatibility rule:

```text
legacy must preserve the previous flat TXT shape as closely as possible.
```

Do not delete the old format.

---

## 3. CLI AND INTERACTIVE REQUIREMENT

Implementation must be available in both surfaces:

```text
1. Direct CLI command flags.
2. Interactive console utility / menu flow.
```

Direct CLI example target:

```bash
python3 -m tg_msg_manager.cli export --user-id 123 --chat-id 456 --txt-profile context-readable
python3 -m tg_msg_manager.cli export --user-id 123 --chat-id 456 --txt-profile legacy
```

Interactive console requirement:

```text
The menu export flow must allow choosing TXT profile or must clearly use the new default.
It must not be implemented only for direct CLI.
```

Recommended interactive prompt:

```text
TXT profile [context-readable/legacy] (Enter = context-readable):
```

Only ask this when TXT output is relevant. If export is JSON-only, do not force irrelevant profile selection unless current menu cannot know output type.

---

## 4. HARD PROHIBITIONS

Do not implement:

```text
- new Telegram fetch behavior
- new context algorithm
- reply-tree reconstruction beyond already available data
- analytics summaries
- sentiment analysis
- bot detection
- OSINT
- profiling
- topic modeling
- OCR
- STT
- media analysis
- media optimization
- ffmpeg
- HTML export
- dashboard / TUI rewrite
- SQLite migrations
- JSONL schema changes
- channel export schema changes
- discussion export schema changes
```

TXT renderer must be a projection of already available data.

---

## 5. PROTECTED FILES

Do not add feature logic directly into:

```text
tg_msg_manager/services/export/service.py
tg_msg_manager/services/db_export/service.py
tg_msg_manager/services/private_archive/service.py
tg_msg_manager/services/context/engine.py
tg_msg_manager/services/channel_export/service.py
```

Allowed minimal changes:

```text
- mechanical delegation to renderer
- argument passing
- option plumbing
```

New logic should live in a rendering-focused package.

Recommended package:

```text
tg_msg_manager/services/rendering/
  __init__.py
  txt_profiles.py
  models.py
  legacy_txt_renderer.py
  context_readable_txt_renderer.py
```

If the project already has a better rendering package, use that instead. Do not duplicate existing rendering abstractions.

---

## 6. CORE DESIGN RULES

### Rule A — TXT is not canonical data

```text
JSONL / database records remain canonical.
TXT is a human-readable projection.
```

### Rule B — renderer only formats

Renderer may:

```text
- group already-provided context records into display blocks
- order records deterministically
- create section headers
- shorten missing reply metadata
- render author/time/message text
```

Renderer must not:

```text
- fetch missing messages
- infer motives
- classify users
- alter stored data
- mutate records
- repair context
```

### Rule C — old format remains accessible

```text
legacy profile must remain available for scripts/users that expect old shape.
```

### Rule D — no noisy missing reply line

Prefer compact representation:

```text
↪ missing reply #341081
```

instead of:

```text
[reply_to: 341081 - original message not found in local DB]
```

### Rule E — reply quote line should be human-friendly

Prefer:

```text
↪ replies to Ната · 15:59:21 · "Ну суд, судом..."
```

or if author/time unavailable:

```text
↪ replies to "Ну суд, судом..."
```

Do not overfit to one dataset.

---

## 7. TARGET CONTEXT BLOCK SEMANTICS

Recommended block model:

```text
ContextBlock:
  block_id
  date
  chat_id / chat title
  target_user_id
  target_author_name
  time_range
  replied_message
  context_before[]
  target_messages[]
  context_after[]
```

A block can contain one or multiple target messages.

Grouping rule should use existing context cluster data if available.

If no explicit cluster model exists:

```text
Use current export ordering and context group information if available.
Do not invent a new deep context algorithm.
```

---

## 8. IMPLEMENTATION PLAN

### A. Baseline inspection

- [ ] Read `AGENTS.md`.
- [ ] Inspect current TXT writer for user/group export.
- [ ] Inspect current DB TXT writer.
- [ ] Inspect current context cluster / exported record shape.
- [ ] Inspect tests covering TXT output.
- [ ] Identify where old TXT format is generated.
- [ ] Identify where CLI args are passed to export options.
- [ ] Identify interactive menu export flow in `cli_menu.py`.

### B. Define profile constants

- [ ] Add `context-readable`.
- [ ] Add `legacy`.
- [ ] Add validator/parser for TXT profile.
- [ ] Keep default profile constant:
  ```text
  DEFAULT_TXT_PROFILE = "context-readable"
  ```

### C. Define render models

- [ ] Add lightweight render-facing dataclasses if useful.
- [ ] Avoid coupling renderer to storage internals more than necessary.
- [ ] Do not add schema migrations.

### D. Establish default policy

- [ ] Direct `export` TXT default becomes `context-readable`.
- [ ] Legacy profile remains opt-in.
- [ ] Decide whether `db-export` default remains legacy for this stage.
- [ ] Document the decision in stage report.

Recommended:

```text
export default = context-readable
db-export default = legacy unless integration is trivial and safe
```

### E. Prepare later blocks

- [ ] Do not fully implement renderer in this block unless trivial.
- [ ] Create only necessary skeleton/contracts if working in small commits.
- [ ] Keep compile clean.

---

## 9. TEST PLAN FOR THIS BLOCK

Add tests for:

- [ ] profile parser accepts `context-readable`.
- [ ] profile parser accepts `legacy`.
- [ ] profile parser rejects unknown value.
- [ ] default profile is `context-readable`.
- [ ] direct CLI parser exposes `--txt-profile` where applicable.
- [ ] interactive menu has a path to choose or apply TXT profile.

---

## 10. VERIFICATION

Run:

```bash
pytest tests/test_*txt*profile*.py tests/test_cli*.py
python3 -m compileall tg_msg_manager
ruff check tg_msg_manager tests
ruff format --check tg_msg_manager tests
```

If file names differ, run the equivalent relevant tests.

Do not claim commands passed unless actually run.

---

## 11. COMPLETION CRITERIA

This block is complete only if:

- [ ] architecture boundary is clear.
- [ ] profile names are defined.
- [ ] default decision is encoded or documented.
- [ ] protected service files do not gain rendering logic.
- [ ] direct CLI and interactive console requirements are explicitly planned.
- [ ] tests exist or are planned for the profile contract.
