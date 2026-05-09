# Stage 4A.5 — Context-Readable TXT Export Profile Report

## 1. Summary

Stage 4A.5 added profile-based TXT rendering for user/group export artifacts.

## 2. Problem

The previous TXT output was a flat log-style projection. It remained useful for compatibility, but it was hard to read when user/group exports included surrounding context and reply metadata.

## 3. Profiles added

- `context-readable`
- `legacy`

## 4. Default behavior

Direct user/group `export` TXT output defaults to `context-readable`.

`legacy` remains available explicitly through `--txt-profile legacy`.

`db-export` remains legacy TXT by default.

## 5. CLI integration

The direct `export` command accepts:

```bash
python3 -m tg_msg_manager.cli export --user-id 123 --chat-id 456 --txt-profile context-readable
python3 -m tg_msg_manager.cli export --user-id 123 --chat-id 456 --txt-profile legacy
```

Unknown TXT profiles fail at parser validation.

## 6. Interactive menu integration

The interactive export menu can generate TXT output and prompts for:

```text
TXT profile [context-readable/legacy] (Enter = context-readable)
```

Empty input selects `context-readable`. Invalid input is rejected without starting export.

## 7. Renderer behavior

TXT rendering now lives under `tg_msg_manager/services/rendering/`.

`context-readable` renders context blocks with:

```text
[REPLIED MESSAGE]
[CONTEXT BEFORE]
[TARGET MESSAGE] / [TARGET MESSAGES]
[CONTEXT AFTER]
```

Missing replies render compactly:

```text
↪ missing reply #id
```

The old noisy missing-reply line remains in the `legacy` profile.

## 8. Files changed

- `README.md`
- `COMMANDS.md`
- `CHANGELOG.md`
- `docs/architecture/README.md`
- `docs/architecture/TXT_RENDERING.md`
- `docs/development/CLI_CONTRACT.md`
- `docs/stages/README.md`
- `docs/stages/completed/stage_4a_5_0_txt_rendering_contract.md`
- `docs/stages/completed/stage_4a_5_1_rendering_models_and_legacy_profile.md`
- `docs/stages/completed/stage_4a_5_2_context_readable_renderer.md`
- `docs/stages/completed/stage_4a_5_3_export_cli_and_menu_integration.md`
- `docs/stages/completed/stage_4a_5_4_docs_tests_report_lifecycle.md`
- `docs/stages/reports/STAGE_4A_5_CONTEXT_READABLE_TXT_PROFILE_REPORT.md`
- `tg_msg_manager/cli_commands.py`
- `tg_msg_manager/cli_menu.py`
- `tg_msg_manager/cli_parser.py`
- `tg_msg_manager/cli_support.py`
- `tg_msg_manager/i18n.py`
- `tg_msg_manager/services/db_export/manifest.py`
- `tg_msg_manager/services/db_export/payload_writer.py`
- `tg_msg_manager/services/db_export/plan_builder.py`
- `tg_msg_manager/services/db_export/service.py`
- `tg_msg_manager/services/db_export/skip_policy.py`
- `tg_msg_manager/services/db_export/state_manager.py`
- `tg_msg_manager/services/db_export/summary.py`
- `tg_msg_manager/services/db_export/txt_renderer.py`
- `tg_msg_manager/services/db_export/txt_writer.py`
- `tg_msg_manager/services/export/export_writer.py`
- `tg_msg_manager/services/rendering/__init__.py`
- `tg_msg_manager/services/rendering/context_readable_txt_renderer.py`
- `tg_msg_manager/services/rendering/legacy_txt_renderer.py`
- `tg_msg_manager/services/rendering/models.py`
- `tg_msg_manager/services/rendering/txt_profiles.py`
- `tg_msg_manager/services/rendering/txt_renderer.py`
- `tests/test_context_readable_txt_renderer.py`
- `tests/test_export_txt_profile_integration.py`
- `tests/test_legacy_txt_renderer.py`
- `tests/test_txt_profile_cli.py`
- `tests/test_txt_profile_menu.py`
- `tests/test_txt_profiles.py`

## 9. Tests

Coverage was added for:

- TXT profile validation.
- Legacy TXT renderer availability.
- Context-readable block rendering.
- Direct CLI parser support and defaults.
- Interactive menu TXT profile selection.
- Export writer renderer dispatch.

## 10. Verification results

- `pytest tests/test_txt_profiles.py tests/test_legacy_txt_renderer.py tests/test_context_readable_txt_renderer.py tests/test_txt_profile_cli.py tests/test_txt_profile_menu.py tests/test_export_txt_profile_integration.py` — passed.
- `pytest tests/test_cli*.py` — passed.
- `python3 -m compileall tg_msg_manager` — passed.
- `ruff check tg_msg_manager tests` — passed.
- `ruff format --check tg_msg_manager tests` — passed.
- `python3 -m tg_msg_manager.cli export --help` — passed and shows `--txt-profile {context-readable,legacy}`.
- `make test` — passed.
- `make verify` — passed.

## 11. Runtime behavior statement

No Telegram fetching behavior changed.

No context extraction behavior changed.

No JSONL schema changed.

No dataset schema changed.

No state schema changed.

No SQLite schema changed.

No analytics/OCR/STT/media optimization added.

## 12. Remaining limitations

- `db-export` remains legacy TXT by default.
- `context-readable` groups by existing context data and falls back safely when no `context_group_id` exists; it does not reconstruct reply trees or fetch missing replies.

## 13. Status

Stage 4A.5 complete.
