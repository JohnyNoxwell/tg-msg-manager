# STAGE 4A.5.1 — RENDERING MODELS / LEGACY PROFILE PRESERVATION

Status: active task  
Stage: 4A.5.1  
Type: renderer extraction / compatibility preservation  
Depends on: Stage 4A.5.0

---

## 0. CODEX ENTRY CONTRACT

```text
Read AGENTS.md first.

Execute Stage 4A.5.1 — Rendering Models / Legacy Profile Preservation.

Extract or isolate the existing TXT formatting behavior as the `legacy` profile.
Do not change current legacy output semantics except for unavoidable mechanical extraction.
Do not implement the new readable profile yet beyond interfaces/skeleton if needed.
```

---

## 1. PURPOSE

Before adding the new readable format, preserve the old TXT format as an explicit profile:

```text
txt_profile = legacy
```

This prevents backward compatibility breakage.

---

## 2. TARGET FILES / PACKAGE

Preferred package:

```text
tg_msg_manager/services/rendering/
  __init__.py
  txt_profiles.py
  models.py
  legacy_txt_renderer.py
```

If existing project structure has a better place, use it, but keep rendering logic out of hot-path services.

---

## 3. HARD PROHIBITIONS

Do not:

```text
- change context extraction
- change message ordering
- change JSONL output
- change SQLite schema
- change channel export schema
- change DB storage
- add analytics
- add interpretation
- add media logic
- alter old TXT format intentionally
```

This stage is compatibility-first.

---

## 4. TASKS — PROFILE CONSTANTS

In `txt_profiles.py` or equivalent:

- [ ] Define `TXT_PROFILE_CONTEXT_READABLE = "context-readable"`.
- [ ] Define `TXT_PROFILE_LEGACY = "legacy"`.
- [ ] Define `DEFAULT_TXT_PROFILE = TXT_PROFILE_CONTEXT_READABLE`.
- [ ] Define allowed set.
- [ ] Add `validate_txt_profile(value: str | None) -> str`.
- [ ] Empty / None should resolve to default where appropriate.
- [ ] Unknown value should raise `ValueError`.

---

## 5. TASKS — RENDER MODELS

In `models.py` or equivalent:

Add only if useful. Suggested dataclasses:

```text
RenderMessage
ContextBlock
TxtRenderOptions
```

Potential fields:

```text
RenderMessage:
  message_id
  timestamp
  author_name
  user_id
  text
  reply_to_id
  reply_excerpt
  reply_author_name
  reply_timestamp
  role

ContextBlock:
  block_id
  date
  chat_id
  chat_title
  target_user_id
  target_author_name
  replied_message
  context_before
  target_messages
  context_after

TxtRenderOptions:
  profile
  target_user_id
  include_ids
  max_reply_excerpt_chars
```

Rules:

```text
- Keep models rendering-facing only.
- Do not make them storage models.
- Do not force schema changes to populate them.
```

If existing export record shape is already sufficient, avoid excessive new models.

---

## 6. TASKS — LEGACY RENDERER

In `legacy_txt_renderer.py`:

- [ ] Move or wrap existing TXT formatting.
- [ ] Preserve old date headers if existing tests depend on them.
- [ ] Preserve old author/time display.
- [ ] Preserve old reply/missing-reply behavior for legacy.
- [ ] Ensure output is deterministic.
- [ ] Add function/class with clear API.

Possible API:

```python
class LegacyTxtRenderer:
    def render(self, records, options) -> str:
        ...
```

or function:

```python
def render_legacy_txt(records, options) -> str:
    ...
```

Use project style.

---

## 7. TASKS — MECHANICAL DELEGATION

Where old TXT writing currently happens:

- [ ] Replace inline formatting with call to legacy renderer where safe.
- [ ] Keep old behavior by passing `legacy` initially where necessary.
- [ ] Do not add new formatting logic into service orchestration files.
- [ ] Avoid large service rewrites.

Allowed mechanical pattern:

```text
service obtains records -> renderer renders text -> writer writes output
```

Forbidden pattern:

```text
service contains if/else formatting blocks for all profiles
```

If a small `if profile == ...` dispatcher is needed, keep it in rendering package, not service.

---

## 8. TESTS

Create / update:

```text
tests/test_txt_profiles.py
tests/test_legacy_txt_renderer.py
```

Required tests:

- [ ] default profile constant is `context-readable`.
- [ ] validator accepts `context-readable`.
- [ ] validator accepts `legacy`.
- [ ] validator rejects unknown profile.
- [ ] legacy renderer emits old-style date separator or current old format.
- [ ] legacy renderer includes timestamp.
- [ ] legacy renderer includes author/user id as before.
- [ ] legacy renderer preserves missing reply text shape if explicitly required by existing tests.

If exact old output is already tested elsewhere, update tests to call `legacy`.

---

## 9. VERIFICATION

Run:

```bash
pytest tests/test_txt_profiles.py tests/test_legacy_txt_renderer.py
python3 -m compileall tg_msg_manager
ruff check tg_msg_manager tests
ruff format --check tg_msg_manager tests
```

If names differ, run the relevant renderer/profile tests.

---

## 10. COMPLETION CRITERIA

Complete only if:

- [ ] `legacy` profile exists.
- [ ] old TXT behavior remains accessible.
- [ ] profile validation exists.
- [ ] rendering logic is isolated.
- [ ] no protected service file gained new formatting logic.
- [ ] tests prove legacy path still works.
