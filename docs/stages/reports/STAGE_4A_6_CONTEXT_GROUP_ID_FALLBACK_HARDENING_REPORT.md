# Stage 4A.6 — Context Group ID Fallback Hardening Report

## 1. Summary

Stage 4A.6 hardened the `context-readable` TXT renderer fallback path for records without `context_group_id`.

Ungrouped records that include a target message now render together as one context block, preserving already-provided non-target before/after context.

## 2. Problem

Stage 4A.5 grouped context-readable TXT output by `context_group_id` when present. When records were ungrouped, the fallback path created singleton target blocks and could drop non-target context records that were already present in the export payload.

## 3. Behavior fixed

- Records with `context_group_id` remain grouped by `context_group_id`.
- Records without `context_group_id` are collected as fallback records.
- Fallback records render as one block when `target_user_id` is unknown.
- Fallback records render as one block when they include at least one target message.
- Fallback non-target-only records do not create an extra block when grouped target blocks already exist.
- Fallback non-target-only records render as one block when no grouped blocks exist, avoiding total data loss.
- Block order remains deterministic by earliest timestamp and message id.

## 4. Files changed

- `tg_msg_manager/services/rendering/context_readable_txt_renderer.py`
- `tests/test_context_readable_txt_renderer.py`
- `tests/test_export_txt_profile_integration.py`
- `CHANGELOG.md`
- `docs/stages/README.md`
- `docs/stages/completed/stage_4a_6_context_group_id_fallback_hardening.md`
- `docs/stages/reports/STAGE_4A_6_CONTEXT_GROUP_ID_FALLBACK_HARDENING_REPORT.md`

## 5. Tests

- Added renderer coverage for ungrouped before/target/after records.
- Added marker assertions proving ungrouped before, target, and after messages are all present.
- Added grouped `context_group_id` regression coverage.
- Added mixed grouped plus ungrouped fallback coverage with deterministic block order.
- Added ungrouped non-target-only coverage for both grouped-present and no-group fallback policies.
- Added export integration coverage for context-readable output preserving ungrouped context.

## 6. Verification results

- `pytest tests/test_context_readable_txt_renderer.py` — passed, 10 tests.
- `pytest tests/test_export_txt_profile_integration.py` — passed, 5 tests.
- `python3 -m compileall tg_msg_manager` — passed.
- `ruff check tg_msg_manager tests` — passed.
- `ruff format --check tg_msg_manager tests` — passed.
- `pytest tests/test_*txt*profile*.py tests/test_*txt*renderer*.py tests/test_cli*.py` — passed, 51 tests.
- `make test` — passed, 412 unittest tests.
- `make verify` — passed.

An initial attempt to run `make test` and `make verify` concurrently failed because both invoked the same SQLite-heavy unittest suite at the same time. They passed when rerun serially.

## 7. Runtime behavior statement

No Telegram fetching behavior changed.

No context extraction behavior changed.

No JSONL schema changed.

No dataset/state schema changed.

No SQLite schema changed.

No analytics/OCR/STT/media optimization added.

## 8. Remaining limitations

- The renderer still only formats records it receives.
- Missing replies are not fetched.
- Reply trees are not reconstructed.
- Ungrouped non-target-only fallback records are intentionally not emitted as a separate block when grouped target blocks already exist.

## 9. Status

Stage 4A.6 complete.
