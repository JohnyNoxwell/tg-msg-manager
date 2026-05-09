# STAGE 4A.0 — DATASET VALIDATION / INSPECTION ARCHITECTURE CONTRACT

Status: active task  
Stage: 4A.0  
Type: architecture contract / implementation boundary  
Scope: dataset validation and inspection only

---

## 0. CODEX ENTRY CONTRACT

```text
Read AGENTS.md first.

You are working on tg-msg-manager.

Execute Stage 4A.0 — Dataset Validation / Inspection Architecture Contract.

This stage defines the architecture boundary and public contract for dataset validation / inspection.
This is not an analytics stage.
This is not an exporter rewrite.
This is not a Telegram fetching stage.
This is not a SQLite persistence stage.

Do not modify channel export runtime behavior.
Do not change dataset schemas.
Do not change state schemas.
Do not change SQLite schema.
Do not add analytics, OSINT, profiling, sentiment analysis, OCR, STT, media optimization, ffmpeg, dashboards, or SaaS logic.
```

---

## 1. PURPOSE

Current project state:

```text
export-channel can produce filesystem datasets:
- manifest.json
- messages.jsonl
- messages.txt
- media_manifest.jsonl
- channel_export_state.json
- optional discussion_comments.jsonl
- optional discussion_comments.txt
- optional discussion_threads.jsonl
- optional discussion_export_state.json
- media/
```

Missing capability:

```text
No standalone command exists to validate or inspect completed dataset directories.
```

Stage 4A goal:

```text
Add deterministic validation / inspection tooling for exported datasets.
```

Correct boundary:

```text
Exporter creates datasets.
Validator checks datasets.
Inspector summarizes datasets.
Analysis layer interprets content later.
```

---

## 2. TARGET COMMANDS

Add public CLI commands:

```bash
python3 -m tg_msg_manager.cli validate-dataset --path exports/channels/example
python3 -m tg_msg_manager.cli inspect-dataset --path exports/channels/example
```

Recommended optional flags:

```bash
python3 -m tg_msg_manager.cli validate-dataset --path exports/channels/example --json
python3 -m tg_msg_manager.cli inspect-dataset --path exports/channels/example --json
```

Optional later flag if cheap and clean:

```bash
--strict
```

But do not overbuild.

---

## 3. FUNCTIONAL BOUNDARY

Validator should check deterministic correctness:

```text
- required files exist
- JSONL files are parseable
- manifest.json is parseable
- channel_export_state.json is parseable
- optional discussion_export_state.json is parseable
- manifest counts match actual files where feasible
- state counters are sane
- duplicate message_id in messages.jsonl
- media_manifest.jsonl references valid paths
- media files exist when status says downloaded/already_exists
- discussion comments link to known channel post ids where feasible
- discussion thread/comment counts are sane
- final report status is ok/warnings/errors
```

Inspector should summarize deterministic facts:

```text
- dataset path
- detected files
- message count
- media record count
- downloaded/existing/skipped/failed media counts
- discussion enabled/absent
- discussion thread count
- discussion comment count
- state cursor
- manifest summary
- warnings/errors if detected
```

Inspector must not interpret content.

---

## 4. HARD PROHIBITIONS

Do not implement:

```text
- Telegram network calls
- fetching missing posts
- repairing datasets
- rewriting existing exported dataset files
- automatic migration of old datasets
- SQLite writes
- SQLite schema changes
- channel export service rewrite
- discussion exporter rewrite
- media download
- media compression / optimization
- ffmpeg
- OCR
- speech-to-text
- image/video/audio recognition
- analytics
- OSINT
- profiling
- sentiment analysis
- topic modeling
- bot detection
- dashboards
- web UI
```

Validation is read-only.

---

## 5. PROTECTED FILES

Do not add new feature logic directly into:

```text
tg_msg_manager/services/export/service.py
tg_msg_manager/services/db_export/service.py
tg_msg_manager/services/private_archive/service.py
tg_msg_manager/services/context/engine.py
tg_msg_manager/services/channel_export/service.py
```

Allowed minimal changes:

```text
tg_msg_manager/cli_parser.py
tg_msg_manager/cli_commands.py
tg_msg_manager/cli.py
tg_msg_manager/i18n.py
README.md
COMMANDS.md
CHANGELOG.md
docs/stages/README.md
```

New logic should live under:

```text
tg_msg_manager/services/dataset_validation/
```

---

## 6. TARGET MODULE STRUCTURE

Create:

```text
tg_msg_manager/services/dataset_validation/
  __init__.py
  options.py
  models.py
  jsonl_validator.py
  manifest_validator.py
  state_validator.py
  media_validator.py
  discussion_validator.py
  inspector.py
  report_renderer.py
```

Keep modules small.

Suggested responsibility split:

```text
options.py
  - DatasetValidationOptions
  - DatasetInspectionOptions

models.py
  - ValidationSeverity
  - ValidationIssue
  - ValidationReport
  - DatasetInspectionReport
  - FileSummary
  - MediaSummary
  - DiscussionSummary

jsonl_validator.py
  - parse_jsonl_records
  - validate_jsonl_file

manifest_validator.py
  - load_manifest
  - validate_manifest_shape

state_validator.py
  - load_channel_state
  - load_discussion_state
  - validate_state_shape

media_validator.py
  - validate_media_manifest
  - summarize_media_records

discussion_validator.py
  - validate_discussion_files
  - summarize_discussion_records

inspector.py
  - validate_dataset
  - inspect_dataset

report_renderer.py
  - render_validation_report_markdown
  - render_validation_report_json
  - render_inspection_report_markdown
  - render_inspection_report_json
```

Do not create a monolithic validator file.

---

## 7. STATUS MODEL

Use three status levels:

```text
ok
warnings
errors
```

Suggested logic:

```text
errors:
  - required file missing
  - invalid JSON / JSONL
  - required state file invalid
  - manifest invalid
  - duplicate message_id
  - media status downloaded/already_exists but file missing
  - discussion comments file present but invalid JSONL

warnings:
  - optional discussion files absent while discussion mode is none/unknown
  - failed media records exist
  - manifest count differs from observed count where not fatal
  - unknown extra files
  - media record references path outside dataset directory
  - empty dataset but structurally valid

ok:
  - no warnings and no errors
```

Do not fail validation on known accepted limitations unless there is a structural contradiction.

---

## 8. OUTPUT CONTRACT

Markdown validation output should include:

```text
# Dataset Validation Report

## Status
## Dataset Path
## Files Checked
## Errors
## Warnings
## Summary
```

Markdown inspection output should include:

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

JSON output should be deterministic and testable.

---

## 9. IMPLEMENTATION PLAN

### A. Baseline inspection

- [ ] Read `AGENTS.md`.
- [ ] Inspect `docs/architecture/DATASET_FORMAT.md`.
- [ ] Inspect `docs/architecture/STATE_AND_INCREMENTAL_MODEL.md`.
- [ ] Inspect `docs/architecture/DATASET_WRITE_SAFETY.md`.
- [ ] Inspect existing channel export tests.
- [ ] Inspect current `manifest.json` contract tests.
- [ ] Confirm actual field names before writing validators.

### B. Architecture skeleton

- [ ] Create `tg_msg_manager/services/dataset_validation/`.
- [ ] Create module files listed above.
- [ ] Add typed dataclasses in `models.py`.
- [ ] Add options dataclasses in `options.py`.
- [ ] Keep all code read-only.

### C. Command contract

- [ ] Define `validate-dataset`.
- [ ] Define `inspect-dataset`.
- [ ] Add `--path`.
- [ ] Add `--json`.
- [ ] Keep parser defaults simple.
- [ ] Do not require Telegram client for these commands.

### D. Docs contract

- [ ] Document the command boundary.
- [ ] Document that Stage 4A is not analytics.
- [ ] Document that validator is read-only.
- [ ] Document known limitations.

---

## 10. VERIFICATION FOR THIS BLOCK

Run at minimum after skeleton integration:

```bash
python3 -m compileall tg_msg_manager
ruff check tg_msg_manager tests
ruff format --check tg_msg_manager tests
python3 -m tg_msg_manager.cli validate-dataset --help
python3 -m tg_msg_manager.cli inspect-dataset --help
```

Do not claim commands passed unless actually run.

---

## 11. COMPLETION CRITERIA

This block is complete only if:

- [ ] architecture boundary is implemented in new package
- [ ] no exporter behavior changed
- [ ] no protected service file gained feature logic
- [ ] CLI parser exposes command stubs or final commands
- [ ] commands do not require Telegram client
- [ ] report/doc plan exists
- [ ] compile/lint checks are run or honestly reported as not run
