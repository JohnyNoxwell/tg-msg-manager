# Stage 4A.7 — DB Export TXT Profile Parity

## 1. Context

Stage 4A.5 introduced TXT rendering profiles:

- `context-readable`
- `legacy`

The regular Telegram export flow already exposes TXT profile selection and should use `context-readable` as the default human-readable TXT format.

The DB export flow still behaves asymmetrically:

- `export` supports TXT profile selection.
- `db-export` still defaults to legacy behavior or does not expose a clear TXT profile choice through the console flow.
- As a result, DB-to-TXT exports can still produce the old flat-log format with date separators and inline `re:` reply snippets.

This stage closes that gap by adding explicit TXT profile selection to DB export, both in direct CLI usage and in the interactive console menu.

## 2. Goal

Add TXT profile selection to DB export without changing the rendering architecture.

The user must be able to choose:

- `context-readable`
- `legacy`

from:

1. direct CLI command;
2. interactive console menu.

The implementation must reuse the existing rendering layer. Do not duplicate TXT formatting logic inside DB export.

## 3. Expected Behavior

### 3.1 Direct CLI

The following commands must be valid:

```bash
tg db-export --user-id 7690756730 --txt-profile context-readable
tg db-export --user-id 7690756730 --txt-profile legacy
```

If DB export requires additional project-specific arguments, preserve the current required argument set and only add TXT profile support.

### 3.2 Interactive Console Menu

When the user chooses DB export and TXT output, the console flow must ask:

```text
TXT format [context-readable/legacy] (Enter = context-readable):
```

Rules:

- Enter / empty input = `context-readable`
- `context-readable` = new readable context-block TXT
- `legacy` = old flat-log TXT
- invalid value = reject clearly according to the existing menu validation style

### 3.3 Default

For DB export through CLI/menu, default to:

```text
context-readable
```

Legacy must remain available as explicit opt-in.

## 4. Non-Goals

Do not implement any unrelated feature.

This stage does not include:

- new export modes;
- new context extraction algorithm;
- schema migrations;
- new dataset format;
- analytics;
- LLM analysis;
- OSINT;
- media processing;
- OCR/STT;
- channel export changes.

## 5. Files to Inspect

Inspect these files before implementation:

- `tg_msg_manager/cli_parser.py`
- `tg_msg_manager/cli_menu.py`
- `tg_msg_manager/cli_commands.py`
- `tg_msg_manager/cli_support.py`
- `tg_msg_manager/services/db_export/service.py`
- `tg_msg_manager/services/db_export/payload_writer.py`
- `tg_msg_manager/services/rendering/txt_profiles.py`
- `tg_msg_manager/services/rendering/txt_renderer.py`
- `tg_msg_manager/services/rendering/legacy_txt_renderer.py`
- `tg_msg_manager/services/rendering/context_readable_txt_renderer.py`
- existing DB export tests
- existing CLI/menu tests

## 6. Implementation Tasks

### 6.1 CLI Parser

Add `--txt-profile` to the DB export CLI command.

Requirements:

- choices:
  - `context-readable`
  - `legacy`
- default:
  - `context-readable`
- reuse constants from `txt_profiles.py`;
- do not hardcode profile strings in multiple unrelated places;
- invalid values must be rejected by parser validation.

Expected parser-level behavior:

```bash
tg db-export ... --txt-profile context-readable
tg db-export ... --txt-profile legacy
tg db-export ... --txt-profile invalid-value
```

The invalid profile must fail cleanly.

### 6.2 CLI Command Handler

Ensure the DB export command handler reads `args.txt_profile` and passes it into:

```python
DBExportService.export_user_messages(...)
```

or the equivalent existing DB export service entrypoint.

Do not rewrite the DB export service. Only add missing plumbing if the service already supports the parameter.

### 6.3 Interactive Menu

Add TXT profile prompt to the DB export menu flow.

Prompt only when output format is TXT.

Do not ask for TXT profile if the user selected JSON or another non-TXT output.

Expected prompt:

```text
TXT format [context-readable/legacy] (Enter = context-readable):
```

Validation rules:

- empty input -> `context-readable`
- exact `context-readable` -> `context-readable`
- exact `legacy` -> `legacy`
- invalid input -> reject using existing menu validation style

If a helper already exists for TXT profile prompt from Stage 4A.5, reuse it.

### 6.4 DB Export Service

Confirm that `DBExportService.export_user_messages()` accepts a TXT profile parameter.

If it already accepts:

```python
txt_profile: str = TXT_PROFILE_LEGACY
```

change DB-export-facing default to `context-readable` only where appropriate.

Important distinction:

- service default may remain conservative if changing it risks internal behavior;
- CLI/menu default must be `context-readable`.

If changing the service default is safe and consistent with the project contract, change it to the shared default constant.

Do not alter JSON export behavior.

### 6.5 Payload Writer / Renderer

Ensure DB TXT export passes the selected profile into the existing rendering dispatcher.

Requirements:

- `legacy` uses legacy renderer;
- `context-readable` uses context-readable renderer;
- no renderer code is duplicated inside DB export;
- no raw string-based formatting is added to DB export service.

### 6.6 Documentation

Update relevant documentation:

- `README.md`
- `docs/COMMANDS.md` or equivalent command reference
- `CHANGELOG.md` if the project uses it
- stage report after implementation

Documentation must mention:

```bash
tg db-export ... --txt-profile context-readable
tg db-export ... --txt-profile legacy
```

and note:

- DB TXT export now supports TXT profile selection;
- `context-readable` is the default for DB TXT export;
- `legacy` remains available for compatibility.

## 7. Tests

Add or update tests.

### 7.1 Parser Tests

Cover:

- DB export accepts `--txt-profile context-readable`;
- DB export accepts `--txt-profile legacy`;
- invalid profile is rejected;
- omitted profile defaults to `context-readable`.

### 7.2 Command Handler Tests

Cover:

- DB export command passes `context-readable` to DB export service;
- DB export command passes `legacy` to DB export service when explicitly requested.

### 7.3 Interactive Menu Tests

Cover:

- empty TXT profile input -> `context-readable`;
- explicit `context-readable` -> `context-readable`;
- explicit `legacy` -> `legacy`;
- invalid value is rejected or handled according to existing menu style;
- prompt is shown only for TXT output.

### 7.4 Rendering Integration Tests

Add or update DB export TXT tests:

- `legacy` output contains old flat-log/date-message style;
- `context-readable` output contains context-readable markers where applicable:
  - `CONTEXT BLOCK`
  - `[REPLIED MESSAGE]`
  - `[CONTEXT BEFORE]`
  - `[TARGET MESSAGE]` or `[TARGET MESSAGES]`
  - `[CONTEXT AFTER]`

Do not require all markers if the fixture does not contain enough context for all sections. Test the markers that should appear for the fixture.

## 8. Hard Prohibitions

Do not:

- change SQLite schema;
- change DB stored message format;
- change JSON/JSONL behavior;
- change context extraction logic;
- change reply resolution logic;
- change channel export;
- change media export;
- add analytics;
- add LLM behavior;
- add OSINT/sentiment/profiling logic;
- add OCR/STT;
- duplicate renderer logic inside DB export;
- remove legacy TXT format;
- silently change behavior without tests.

## 9. Verification Commands

Run:

```bash
python3 -m compileall tg_msg_manager
pytest tests
ruff check tg_msg_manager tests
ruff format --check tg_msg_manager tests
```

If the project has make targets, also run:

```bash
make test
make verify
```

Do not claim commands passed unless actually run.

## 10. Stage Lifecycle

After implementation and verification:

1. Create a factual report under:

```text
docs/stages/reports/
```

Suggested filename:

```text
STAGE_4A_7_DB_EXPORT_TXT_PROFILE_PARITY_REPORT.md
```

2. Move this task file from:

```text
docs/stages/active/
```

to:

```text
docs/stages/completed/
```

3. Update:

```text
docs/stages/README.md
```

4. Ensure `docs/stages/active/` contains only unfinished or next-stage task files.

## 11. Final Agent Response Format

Use this final response structure:

```markdown
## Summary

## Files changed

## Behavior

## Tests

## Verification

## Notes

## Status
```

In `Verification`, list only commands that were actually run and their actual result.
