# STAGE 4C.0C — TEST LAYOUT GROUPING REPORT

## Статус

- Stage 4C.0C завершён.
- Flat `tests/test_*.py` layout сгруппирован по subsystem directories.
- Assertions и test intent не менялись.
- Runtime modules, CLI behavior, SQLite schema и dataset formats не менялись.

## Old path -> new path

- `tests/test_architecture_wrappers.py` -> `tests/architecture/test_architecture_wrappers.py`
- `tests/test_compat_imports.py` -> `tests/architecture/test_compat_imports.py`
- `tests/test_channel_export_cli.py` -> `tests/cli/test_channel_export_cli.py`
- `tests/test_cli.py` -> `tests/cli/test_cli.py`
- `tests/test_cli_ui_refresh.py` -> `tests/cli/test_cli_ui_refresh.py`
- `tests/test_txt_profile_cli.py` -> `tests/cli/test_txt_profile_cli.py`
- `tests/test_txt_profile_menu.py` -> `tests/cli/test_txt_profile_menu.py`
- `tests/test_concurrency.py` -> `tests/core/test_concurrency.py`
- `tests/test_config.py` -> `tests/core/test_config.py`
- `tests/test_data_model.py` -> `tests/core/test_data_model.py`
- `tests/test_i18n.py` -> `tests/core/test_i18n.py`
- `tests/test_observability.py` -> `tests/core/test_observability.py`
- `tests/test_telegram_core.py` -> `tests/core/telegram/test_telegram_core.py`
- `tests/test_fixture_e2e.py` -> `tests/e2e/test_fixture_e2e.py`
- `tests/test_storage_sqlite.py` -> `tests/infrastructure/storage/test_storage_sqlite.py`
- `tests/test_alias_manager.py` -> `tests/services/alias_manager/test_alias_manager.py`
- `tests/test_channel_export_dataset_contracts.py` -> `tests/services/channel_export/test_channel_export_dataset_contracts.py`
- `tests/test_channel_export_included_files_builder.py` -> `tests/services/channel_export/test_channel_export_included_files_builder.py`
- `tests/test_channel_export_manifest.py` -> `tests/services/channel_export/test_channel_export_manifest.py`
- `tests/test_channel_export_manifest_coordinator.py` -> `tests/services/channel_export/test_channel_export_manifest_coordinator.py`
- `tests/test_channel_export_media_downloader.py` -> `tests/services/channel_export/test_channel_export_media_downloader.py`
- `tests/test_channel_export_media_filename.py` -> `tests/services/channel_export/test_channel_export_media_filename.py`
- `tests/test_channel_export_media_policy.py` -> `tests/services/channel_export/test_channel_export_media_policy.py`
- `tests/test_channel_export_payload_writer.py` -> `tests/services/channel_export/test_channel_export_payload_writer.py`
- `tests/test_channel_export_plan_builder.py` -> `tests/services/channel_export/test_channel_export_plan_builder.py`
- `tests/test_channel_export_post_fetcher.py` -> `tests/services/channel_export/test_channel_export_post_fetcher.py`
- `tests/test_channel_export_post_mapper.py` -> `tests/services/channel_export/test_channel_export_post_mapper.py`
- `tests/test_channel_export_renderers.py` -> `tests/services/channel_export/test_channel_export_renderers.py`
- `tests/test_channel_export_result_builder.py` -> `tests/services/channel_export/test_channel_export_result_builder.py`
- `tests/test_channel_export_service.py` -> `tests/services/channel_export/test_channel_export_service.py`
- `tests/test_channel_export_source_resolver.py` -> `tests/services/channel_export/test_channel_export_source_resolver.py`
- `tests/test_channel_export_state_consistency.py` -> `tests/services/channel_export/test_channel_export_state_consistency.py`
- `tests/test_channel_export_state_manager.py` -> `tests/services/channel_export/test_channel_export_state_manager.py`
- `tests/test_channel_export_discussion_exporter.py` -> `tests/services/channel_export/discussions/test_channel_export_discussion_exporter.py`
- `tests/test_channel_export_discussion_fetcher.py` -> `tests/services/channel_export/discussions/test_channel_export_discussion_fetcher.py`
- `tests/test_channel_export_discussion_mapper.py` -> `tests/services/channel_export/discussions/test_channel_export_discussion_mapper.py`
- `tests/test_channel_export_discussion_models.py` -> `tests/services/channel_export/discussions/test_channel_export_discussion_models.py`
- `tests/test_channel_export_discussion_options.py` -> `tests/services/channel_export/discussions/test_channel_export_discussion_options.py`
- `tests/test_channel_export_discussion_payload_writer.py` -> `tests/services/channel_export/discussions/test_channel_export_discussion_payload_writer.py`
- `tests/test_channel_export_discussion_renderers.py` -> `tests/services/channel_export/discussions/test_channel_export_discussion_renderers.py`
- `tests/test_channel_export_discussion_resolver.py` -> `tests/services/channel_export/discussions/test_channel_export_discussion_resolver.py`
- `tests/test_channel_export_discussion_state_manager.py` -> `tests/services/channel_export/discussions/test_channel_export_discussion_state_manager.py`
- `tests/test_cleaner.py` -> `tests/services/cleaner/test_cleaner.py`
- `tests/test_dataset_validation_contracts.py` -> `tests/services/dataset_validation/test_dataset_validation_contracts.py`
- `tests/test_db_export_components.py` -> `tests/services/db_export/test_db_export_components.py`
- `tests/test_db_exporter.py` -> `tests/services/db_export/test_db_exporter.py`
- `tests/test_export_txt_profile_integration.py` -> `tests/services/db_export/test_export_txt_profile_integration.py`
- `tests/test_file_writer.py` -> `tests/services/file_writer/test_file_writer.py`
- `tests/test_private_archive_components.py` -> `tests/services/private_archive/test_private_archive_components.py`
- `tests/test_context_readable_txt_renderer.py` -> `tests/services/rendering/test_context_readable_txt_renderer.py`
- `tests/test_legacy_txt_renderer.py` -> `tests/services/rendering/test_legacy_txt_renderer.py`
- `tests/test_txt_profiles.py` -> `tests/services/rendering/test_txt_profiles.py`
- `tests/test_reporting.py` -> `tests/services/reporting/test_reporting.py`
- `tests/test_retry_worker.py` -> `tests/services/retry/test_retry_worker.py`
- `tests/test_scheduler.py` -> `tests/services/scheduler/test_scheduler.py`
- `tests/test_services.py` -> `tests/services/test_services.py`
- `tests/test_sync_system.py` -> `tests/services/sync/test_sync_system.py`

## Изменённые файлы

- `tests/**`
- `docs/development/CLI_CONTRACT.md`
- `docs/stages/README.md`

## Проверки

- `pytest --collect-only -q`: passed, 492 collected including existing `scratch/test_whitelist.py`
- `python3 -m compileall tg_msg_manager`: passed
- `ruff check tg_msg_manager tests`: passed
- `pytest tests -q`: passed, 491 passed, 31 subtests passed
- `make test`: passed, 452 unittest tests

## Не выполнялось

- `pytest.ini` inspection: file is absent in repository.

## Baseline failures

- None.
