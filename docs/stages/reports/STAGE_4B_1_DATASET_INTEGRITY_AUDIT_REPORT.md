# STAGE 4B.1 - DATASET INTEGRITY AUDIT REPORT

## 1. Область

Stage 4B.1 выполнен как audit-only. Runtime-код, тесты, CLI, dataset artifacts и SQLite schema не изменялись.

Применимые lifecycle-правила из `AGENTS.md`: активный stage выполняется отдельно, отчет пишется до cleanup, завершенный task переносится в `docs/stages/completed/`, `docs/stages/README.md` обновляется, следующие stage не запускаются.

## 2. Проверенные файлы

- `AGENTS.md`
- `COMMANDS.md`
- `README.md`
- `docs/architecture/README.md`
- `docs/architecture/DATASET_VALIDATION.md`
- `docs/architecture/DATASET_FORMAT.md`
- `tg_msg_manager/services/channel_export/`
- `tg_msg_manager/services/dataset_validation/`
- `tg_msg_manager/services/rendering/`
- `tg_msg_manager/services/db_export/`
- `tests/test_channel_export_*.py`
- `tests/test_dataset_validation_contracts.py`
- `tests/test_context_readable_txt_renderer.py`
- `tests/test_db_export_components.py`
- `tests/fixtures/dataset_validation/`

Archive и completed stage файлы не инспектировались.

## 3. Checklist

| Capability | Status | Evidence | Tests / fixtures | Gap | Next |
| --- | --- | --- | --- | --- | --- |
| Reliable incremental export | implemented | `ChannelExportStateManager.determine_run_mode()`, `_run_incremental_export()`, `ChannelPostFetcher.iter_posts(min_message_id=...)`, append write session, no-new-posts branch | `tests/test_channel_export_service.py`, `tests/test_channel_export_payload_writer.py`, `tests/test_channel_export_state_consistency.py` | не ACID across all files/media; docs already state this | none |
| Manifest per export | implemented | `manifest_writer.py`, `manifest_coordinator.py`, `manifest.json` contract docs | `tests/test_channel_export_manifest.py`, `tests/test_channel_export_manifest_coordinator.py`, `tests/test_channel_export_dataset_contracts.py` | no-new-posts rewrites manifest summary only | none |
| Changelog/equivalent new-message summary | partial | result fields/events include this-run counts; incremental appends only new rows | `tests/test_channel_export_service.py`, `tests/test_channel_export_result_builder.py` | no standalone `run_changelog.jsonl`; no per-run durable list of new message ids | Stage 4B.3 |
| Stable message IDs and media IDs | implemented | channel `message_id` is Telegram id; `media_id=f"{message_id}_{media_index:02d}"`; stable media path resolution | `tests/test_channel_export_dataset_contracts.py`, `tests/test_channel_export_post_mapper.py`, `tests/test_channel_export_media_filename.py` | current channel mapper supports one media record per post | Stage 4B.2 only if validator cross-checks are added |
| Duplicate detection | implemented | `validate_messages_jsonl()` emits `duplicate_message_id`; discussion comments emit `duplicate_discussion_comment_id` | `invalid_duplicate_messages`, `tests/test_dataset_validation_contracts.py` | no duplicate media-id validator found | Stage 4B.2 |
| Message-ID gap detection | missing | message summary records min/max only; no gap issue code in validators | `tests/test_dataset_validation_contracts.py` has no gap fixture | Telegram deleted/unavailable gaps need warning semantics | Stage 4B.2 |
| Reply-link validation | partial | discussion validator checks non-negative `reply_to_id` and channel post links; renderer shows missing replies in user/group TXT | `tests/test_dataset_validation_contracts.py`, `tests/test_context_readable_txt_renderer.py` | no channel dataset reply-chain validation; no check that `reply_to_id` targets exported comment/message when available | Stage 4B.2 |
| Media-link validation | implemented | `validate_media_manifest()` checks known statuses, path escape, required file for `downloaded`/`already_exists` | `invalid_missing_media_file`, media relationship tests | no SHA-256 verification by default; no media duplicate-id validator | Stage 4B.2 if scoped |
| Raw JSON/JSONL and readable TXT/MD separation | partial | channel export writes `messages.jsonl` and `messages.txt`; discussion full writes JSONL and TXT; user/group TXT is projection only | `tests/test_channel_export_dataset_contracts.py`, docs | Markdown projection is not a formal artifact | Stage 4B.4 if projection contract includes MD/equivalent |
| AI-friendly chunks/context/metadata/authors/replies/dates/message IDs | partial | DB export JSONL `serialize_ai_payload()`; context-readable TXT groups context blocks for user/group export | `tests/test_db_export_components.py`, `tests/test_context_readable_txt_renderer.py` | channel export has raw JSONL + simple TXT, no `ai_chunks.jsonl` or formal chunk contract | Stage 4B.4 |

## 4. Текущие artifacts

Canonical channel artifacts:

- `manifest.json`
- `messages.jsonl`
- `media_manifest.jsonl`
- `channel_export_state.json`
- optional `discussion_metadata.jsonl`
- optional `discussion_comments.jsonl`
- optional `discussion_threads.jsonl`
- optional `discussion_export_state.json`

Readable/derived projections:

- `messages.txt`
- optional `discussion_comments.txt`
- user/group `context-readable` TXT
- DB export compact AI JSONL

No current formal artifacts:

- `run_changelog.jsonl`
- `ai_chunks.jsonl`
- Markdown dataset projection

## 5. Validation behavior

Current stable issue codes observed in implementation:

- errors: `dataset_path_missing`, `dataset_path_not_directory`, `missing_required_file`, `invalid_jsonl`, `invalid_jsonl_object`, `file_unreadable`, `missing_message_id`, `duplicate_message_id`, `invalid_media_path`, `media_path_escape`, `media_file_missing`, `invalid_json`, `invalid_manifest_shape`, `negative_count`, `invalid_discussion_comments_jsonl`, `invalid_discussion_threads_jsonl`, `duplicate_discussion_comment_id`
- warnings: `unknown_media_status`, `failed_media_records_present`, `manifest_shape_drift`, `manifest_count_mismatch`, `manifest_included_file_missing`, `discussion_count_mismatch`, `state_status_drift`, `state_identity_mismatch`, `state_count_mismatch`, `discussion_state_without_payload`, `discussion_payload_without_state`, `missing_discussion_file`, `discussion_comment_unlinked`, `discussion_thread_unlinked`, `empty_dataset`, `unknown_extra_file`

Validation is read-only and does not repair, migrate, fetch, analyze content, OCR/STT, or write SQLite data.

## 6. Incremental behavior

Current implementation uses `channel_export_state.json.last_exported_message_id` as cursor. A non-force second run uses Telegram `min_id` and local fallback filtering, then appends to `messages.jsonl`, `messages.txt`, and `media_manifest.jsonl`. State advances only after payload and manifest writes succeed. No-new-posts runs emit a no-new event and keep state unchanged.

Evidence: `tg_msg_manager/services/channel_export/service.py`, `state_manager.py`, `post_fetcher.py`, `payload_writer.py`; tests in `tests/test_channel_export_service.py`, `tests/test_channel_export_payload_writer.py`, `tests/test_channel_export_state_consistency.py`.

## 7. AI-friendly/readable behavior

Implemented:

- DB export compact AI JSONL includes message id, chat id, user id, author, timestamp, text, reply ids, media type, context group id, service marker, reactions.
- User/group `context-readable` TXT groups context blocks and renders reply/missing-reply markers.
- Channel export readable TXT includes timestamp, channel label, `message_id`, text, and media lines.

Not implemented:

- formal channel `ai_chunks.jsonl`;
- chunk metadata contract;
- channel reply-chain reconstruction;
- Markdown projection artifact.

## 8. Deferred work

- Stage 4B.2: message-id gap detection, reply-link validation, duplicate/media validator hardening, stable issue-code docs/fixtures.
- Stage 4B.3: standalone per-run changelog artifact or documented equivalent.
- Stage 4B.4: derived AI-ready projection contract, e.g. `ai_chunks.jsonl`, with stable source references.

## 9. Verification

- `pytest tests/test_dataset_validation_contracts.py` - passed, 20 tests.
- `pytest tests/test_channel_export_*.py` - passed, 208 tests.
- `pytest tests/test_context_readable_txt_renderer.py` - passed, 10 tests.
- `pytest tests/test_db_export_components.py` - passed, 5 tests.

No required focused command was skipped.

## 10. SQLite/schema

SQLite schema unchanged. Dataset schema unchanged. Runtime behavior unchanged.

## 11. Known limitations

- Current validation docs mention "missing channel post `message_id`", but implementation only checks missing/invalid `message_id` field and duplicates, not ID-range gaps.
- Count mismatches are warnings for compatibility with older datasets.
- SHA-256 media verification is not performed by default.
- Reply-tree reconstruction remains intentionally absent.

## 12. Recommendation

Proceed to Stage 4B.2. The audit found no blocker for validation hardening if it remains read-only, warning-first for ambiguous Telegram gaps, and covered by fixtures/docs.
