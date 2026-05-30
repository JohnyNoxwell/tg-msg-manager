# Stage 5B.3 — DB Export Memory Boundaries Report

## Статус

- Завершено.
- Runtime-код не изменялся: текущая реализация уже использует iterator-based путь для exact-safe AI JSON export при наличии `get_user_export_summary()` / `get_user_export_summary_since()` и `iter_user_export_rows()` / `iter_user_export_rows_since()`.

## Iterator-based пути

- Полный AI JSON DB export: `load_export_source()` возвращает `export_row_iter_factory`, когда доступны summary и `iter_user_export_rows()`.
- Инкрементальный AI JSON DB export: `load_incremental_export_source()` возвращает `export_row_iter_factory`, когда доступны summary и `iter_user_export_rows_since()`.
- `DBExportPayloadWriter.write_payloads()` сохраняет существующий streaming write path для `export_row_iter_factory`.

## Материализованные пути

- `context-readable` TXT оставлен материализованным: renderer сортирует, группирует `context_group_id`, строит reply lookup и должен сохранить точную группировку/reply semantics.
- Legacy TXT оставлен на `MessageData`/lookup поведении: exact reply snippet behavior зависит от полного локального lookup.
- `full` JSON profile оставлен на message path: row renderer покрывает AI JSON projection, а `full` профиль сохраняет `raw_payload` semantics.

## Тесты

- Добавлен `TestDBExporter.test_streaming_ai_json_output_matches_materialized_message_output`: parsed AI JSON record из streaming row path совпадает с materialized message path.
- Существующие tests сохраняют проверки, что streaming AI JSON path не вызывает `get_user_messages()` и `get_user_export_rows()` при доступном iterator getter.

## Документация

- `docs/architecture/TXT_RENDERING.md` и `COMMANDS.md` не обновлялись: CLI, форматы, TXT semantics и documented limitations не менялись.

## Проверки

- `pytest tests/services/db_export/test_db_exporter.py -k streaming_ai_json_output_matches_materialized_message_output` — passed.
- `pytest tests/services/db_export/test_db_export_components.py tests/services/db_export/test_db_exporter.py tests/services/db_export/test_export_txt_profile_integration.py` — passed.
- `python3 -m compileall tg_msg_manager` — passed.
- `ruff check tg_msg_manager tests` — passed.

## Навыки

- stage-reviewer: applied from `.skills/stage-reviewer/SKILL.md`; verdict pass, blockers none, risk low.
- architecture-guard: applied from `.skills/architecture-guard/SKILL.md`; verdict pass, violations none, risk low.
- stage-completion-auditor: applied from `.skills/stage-completion-auditor/SKILL.md`; verdict complete, blockers none.

## Lifecycle

- Cleanup выполнен после создания отчета: stage file moved to completed, `docs/stages/README.md` updated.
