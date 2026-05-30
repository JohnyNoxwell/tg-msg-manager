# STAGE 5B.2 — отчет

Дата: 2026-05-30
Статус: выполнено

## Что изменено

- Добавлен `tg_msg_manager/services/channel_export/run_summary.py` с `ChannelRunSummaryBuilder`.
- В `run_full_export()` для `discussion_mode == none` больше не накапливаются полные `ChannelPostRecord` только ради `run_changelog.jsonl`.
- `ChannelRunChangelogWriter.append_entry()` сохранил путь через `posts` и получил дополнительный путь через `summary`.
- `docs/architecture/README.md` обновлен ссылкой на новый helper в организации channel export.

## Файлы

- `tg_msg_manager/services/channel_export/run_summary.py`
- `tg_msg_manager/services/channel_export/run_changelog.py`
- `tg_msg_manager/services/channel_export/workflows/context.py`
- `tg_msg_manager/services/channel_export/workflows/full_export.py`
- `tests/services/channel_export/test_channel_export_run_summary.py`
- `tests/services/channel_export/test_channel_export_service.py`
- `docs/architecture/README.md`
- `docs/stages/reports/STAGE_5B_2_CHANNEL_EXPORT_POST_BUFFER_BOUNDARIES_REPORT.md`
- `docs/stages/completed/stage_5b_2_channel_export_post_buffer_boundaries.md`
- `docs/stages/README.md`

## Уменьшенный buffering path

- Прямой full/force channel export без discussion теперь хранит только ids, first/last id, first/last timestamp и count для changelog.
- В changelog передается `posts=()` и `summary=ChannelRunSummary`.

## Оставлено без изменений

- `discussion_mode == full` и `discussion_mode == metadata` сохраняют список полных records, потому что discussion export использует post records.
- Incremental export оставлен без изменений.
- No-new-posts path оставлен без изменений.

## Сохранение схем и форматов

- Схема `run_changelog.jsonl` не менялась: ключи и значения формируются теми же полями.
- `test_changelog_summary_output_matches_posts_output` проверяет байтовую эквивалентность JSONL-строки между `posts` и `summary` при фиксированных `run_id` и времени.
- Dataset/state/manifest/discussion formats не менялись; dataset contract tests прошли.

## Проверки

- `pytest tests/services/channel_export/test_channel_export_run_summary.py tests/services/channel_export/test_channel_export_service.py`: passed
- `pytest tests/services/channel_export/test_channel_export_dataset_contracts.py`: passed
- `python3 -m compileall tg_msg_manager`: passed
- `ruff check tg_msg_manager tests`: passed
- `git diff --check`: passed

## Skills

- `stage-reviewer`: applied from `.skills/stage-reviewer/SKILL.md`
- `architecture-guard`: applied from `.skills/architecture-guard/SKILL.md`

## Lifecycle cleanup

- Stage file moved from `docs/stages/active/` to `docs/stages/completed/`.
- `docs/stages/README.md` updated.

## Architecture guard

- `ChannelExportService` не менялся.
- Новая логика находится в focused channel export module.
- SQLite, CLI, dataset schemas, state semantics и discussion behavior не менялись.
