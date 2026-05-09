# STAGE 4A.3 — CLI COMMANDS / REPORT RENDERERS

Status: active task  
Stage: 4A.3  
Type: CLI surface and output rendering  
Depends on: Stage 4A.1, Stage 4A.2

---

## 0. CODEX ENTRY CONTRACT

```text
Read AGENTS.md first.

Execute Stage 4A.3 — CLI Commands / Report Renderers.

Expose validate-dataset and inspect-dataset as read-only CLI commands.
Render deterministic Markdown and JSON reports.
Do not require Telegram client.
Do not modify datasets.
Do not implement analytics.
```

---

## 1. PURPOSE

Expose Stage 4A functionality through public CLI.

Commands:

```bash
python3 -m tg_msg_manager.cli validate-dataset --path exports/channels/example
python3 -m tg_msg_manager.cli validate-dataset --path exports/channels/example --json

python3 -m tg_msg_manager.cli inspect-dataset --path exports/channels/example
python3 -m tg_msg_manager.cli inspect-dataset --path exports/channels/example --json
```

---

## 2. CLI PARSER TASKS

Modify:

```text
tg_msg_manager/cli_parser.py
```

Tasks:

- [ ] Add subparser `validate-dataset`.
- [ ] Add required `--path`.
- [ ] Add optional `--json`.
- [ ] Add subparser `inspect-dataset`.
- [ ] Add required `--path`.
- [ ] Add optional `--json`.
- [ ] Keep command names stable and explicit.
- [ ] Do not overload existing `report` command.
- [ ] Do not require Telegram connection.

---

## 3. CLI DISPATCH TASKS

Modify:

```text
tg_msg_manager/cli.py
tg_msg_manager/cli_commands.py
```

or current dispatch modules.

Tasks:

- [ ] Add `_handle_validate_dataset_command(ctx, args)` or equivalent.
- [ ] Add `_handle_inspect_dataset_command(ctx, args)` or equivalent.
- [ ] Ensure commands are classified as not needing Telegram client.
- [ ] Ensure commands work from filesystem only.
- [ ] Convert path string to `Path`.
- [ ] Print Markdown by default.
- [ ] Print JSON when `--json` is used.
- [ ] Return non-zero / raise `SystemExit(1)` on validation errors if project style supports it.
- [ ] Do not make warnings exit non-zero unless `--strict` is explicitly implemented.

Recommended behavior:

```text
validate-dataset:
  errors -> prints report -> exits 1
  warnings only -> prints report -> exits 0
  ok -> prints report -> exits 0

inspect-dataset:
  always exits 0 unless path cannot be read / invalid command usage
```

If current CLI architecture does not use exit codes consistently, follow project style and document behavior.

---

## 4. REPORT RENDERER TASKS

Implement in:

```text
tg_msg_manager/services/dataset_validation/report_renderer.py
```

### A. Markdown validation report

Required sections:

```text
# Dataset Validation Report

## Status
## Dataset Path
## Files Checked
## Errors
## Warnings
## Summary
```

Rules:

- [ ] Stable ordering.
- [ ] Clear issue codes.
- [ ] Include file path and line if available.
- [ ] Use `None` / `No errors` / `No warnings` consistently.
- [ ] Do not dump huge records.

### B. JSON validation report

Required top-level shape:

```json
{
  "status": "ok|warnings|errors",
  "dataset_path": "...",
  "summary": {},
  "issues": []
}
```

Issue shape:

```json
{
  "severity": "error|warning",
  "code": "...",
  "message": "...",
  "path": "...",
  "line": 123
}
```

### C. Markdown inspection report

Required sections:

```text
# Dataset Inspection Report

## Dataset Path
## Files
## Messages
## Media
## Discussions
## State
## Notes
```

### D. JSON inspection report

Required top-level shape:

```json
{
  "dataset_path": "...",
  "files": {},
  "messages": {},
  "media": {},
  "discussions": {},
  "state": {},
  "notes": []
}
```

---

## 5. INSPECTOR TASKS

Implement in:

```text
tg_msg_manager/services/dataset_validation/inspector.py
```

Tasks:

- [ ] Add `validate_dataset(options)` high-level function.
- [ ] Add `inspect_dataset(options)` high-level function.
- [ ] Reuse validators from Stage 4A.1/4A.2.
- [ ] Aggregate errors/warnings.
- [ ] Build summary counts.
- [ ] Keep stable ordering.
- [ ] Avoid reading very large media files.
- [ ] Do not analyze text content.

Inspection should include:

```text
dataset path
file existence/size
message count
min/max message_id if cheap
media status counts
discussion present yes/no
discussion comment count
discussion thread count
state cursor
manifest counts
warnings/errors summary
```

---

## 6. I18N / INTERACTIVE MENU

Do not add validate/inspect to the interactive menu in this stage unless it is extremely low-risk and explicitly consistent with current menu design.

Default target for Stage 4A:

```text
Direct CLI commands only.
```

If adding i18n strings is necessary for help text, update both Russian and English.

---

## 7. TESTS

Create / update:

```text
tests/test_dataset_validation_cli.py
tests/test_dataset_validation_renderers.py
```

Required tests:

- [ ] parser help includes `validate-dataset`.
- [ ] parser help includes `inspect-dataset`.
- [ ] validate-dataset requires `--path`.
- [ ] inspect-dataset requires `--path`.
- [ ] commands do not require Telegram client.
- [ ] Markdown validation report renders status/errors/warnings.
- [ ] JSON validation report is valid JSON.
- [ ] Markdown inspection report renders counts.
- [ ] JSON inspection report is valid JSON.
- [ ] validate-dataset returns/raises failure for errors according to chosen CLI policy.
- [ ] warnings-only validation does not fail unless strict mode exists.

---

## 8. DOCS

Update:

```text
README.md
COMMANDS.md
docs/README.md
docs/architecture/DATASET_FORMAT.md or new docs/architecture/DATASET_VALIDATION.md
```

Document:

```text
- validate-dataset command
- inspect-dataset command
- read-only nature
- no Telegram access required
- no analytics
- no repair/migration behavior
- status meanings: ok/warnings/errors
```

---

## 9. VERIFICATION

Run:

```bash
pytest tests/test_dataset_validation_cli.py tests/test_dataset_validation_renderers.py
pytest tests/test_dataset_validation_*.py
python3 -m compileall tg_msg_manager
ruff check tg_msg_manager tests
ruff format --check tg_msg_manager tests
python3 -m tg_msg_manager.cli validate-dataset --help
python3 -m tg_msg_manager.cli inspect-dataset --help
```

If practical:

```bash
make test
make verify
```

Do not claim commands passed unless actually run.

---

## 10. COMPLETION CRITERIA

Complete only if:

- [ ] `validate-dataset` exists.
- [ ] `inspect-dataset` exists.
- [ ] both commands are read-only.
- [ ] both commands do not require Telegram client.
- [ ] Markdown and JSON outputs are deterministic.
- [ ] validation errors are visible and test-covered.
- [ ] docs are updated.
- [ ] no interactive menu expansion was done unless explicitly justified.
