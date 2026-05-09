# Stage 3E.5 — Interactive Channel Export Options Parity Report

## 1. Summary

Stage 3E.5 added missing `export-channel` options to the interactive menu path.

Interactive channel export now prompts for discussion mode, max comments per post, force re-export, output directory, max media size, and media types. Empty answers preserve the previous menu defaults.

## 2. Problem

Direct `export-channel` already supported discussion and advanced media/output options, but the interactive menu hardcoded:

```text
discussion=none
max_comments_per_post=DEFAULT_MAX_COMMENTS_PER_POST
output_dir=None
force=False
max_media_size=None
media_types=None
```

## 3. Interactive Options Added

- `discussion`: `none` or `full`, with empty input defaulting to `none`.
- `max-comments-per-post`: positive integer, with empty input defaulting to `100`.
- `force`: accepts `y`, `yes`, `true`, `1`, `n`, `no`, `false`, `0`, and empty input.
- `output-dir`: empty input maps to `None`; non-empty input is passed to the direct handler.
- `max-media-size`: empty input maps to `None`; non-empty input is parsed with existing media size parsing.
- `media-types`: empty input maps to `None`; non-empty input is parsed with existing media type parsing.

## 4. Files Changed

- `tg_msg_manager/cli_menu.py`
- `tg_msg_manager/i18n.py`
- `tests/test_channel_export_cli.py`
- `README.md`
- `COMMANDS.md`
- `CHANGELOG.md`
- `docs/stages/README.md`
- `docs/stages/completed/stage_3e_5_interactive_channel_export_options_parity.md`
- `docs/stages/reports/STAGE_3E_5_INTERACTIVE_CHANNEL_EXPORT_OPTIONS_PARITY_REPORT.md`

## 5. Validation Behavior

- Invalid discussion input prints the standard invalid selection message and returns to the menu pause.
- Invalid max comments per post input prints the standard invalid selection message and returns to the menu pause.
- Invalid force input prints the standard invalid selection message and returns to the menu pause.
- Max media size and media types use the existing channel export parsers, preserving direct CLI parsing semantics.

## 6. Tests

Added regression coverage for:

- Default interactive channel export preserving previous values.
- `discussion=full` passed to the handler.
- Custom `max_comments_per_post` passed to the handler.
- `force=y` passed as `True`.
- `output_dir` passed to the handler.
- `max_media_size` passed as parsed bytes.
- `media_types` passed as the parsed tuple.
- Invalid discussion rejection.
- Invalid max comments per post rejection.
- Invalid force rejection.
- `export-channel --help` parser behavior.

## 7. Verification Results

- `pytest tests/test_channel_export_cli.py`: passed, 26 tests.
- `pytest tests/test_cli.py tests/test_channel_export_cli.py`: passed, 49 tests.
- `pytest tests/test_channel_export_*.py`: passed, 186 tests.
- `python3 -m compileall tg_msg_manager`: passed.
- `ruff check tg_msg_manager tests`: passed.
- `ruff format --check tg_msg_manager tests`: passed.
- `python3 -m tg_msg_manager.cli export-channel --help`: passed and printed help.
- `make test`: passed, 392 tests, when run sequentially.
- `make verify`: passed, including compileall, ruff check, format check, and 392 unittest tests, when run sequentially.

Note: the literal requested glob command `pytest tests/test_cli_menu*.py tests/test_cli*.py` did not start pytest in this shell because `tests/test_cli_menu*.py` has no matching file. The relevant CLI/menu tests were run explicitly instead.

## 8. Runtime Behavior Statement

No direct CLI behavior changed.
No dataset schema changed.
No state schema changed.
No SQLite schema changed.
No analytics/OCR/STT/media optimization added.

## 9. Remaining Limitations

- Discussion comment media remains metadata-only.
- No new discussion modes were added.
- No media optimization, compression, ffmpeg processing, OCR, STT, media analysis, analytics, OSINT, profiling, or SQLite persistence was added.

## 10. Status

Stage 3E.5 is complete.
