# STAGE 4A.5.4 — DOCS / TESTS / REPORT / LIFECYCLE CLEANUP

Status: active task  
Stage: 4A.5.4  
Type: finalization and governance  
Depends on: Stage 4A.5.0, 4A.5.1, 4A.5.2, 4A.5.3

---

## 0. CODEX ENTRY CONTRACT

```text
Read AGENTS.md first.

Execute Stage 4A.5.4 — Docs / Tests / Report / Lifecycle Cleanup.

Finish Stage 4A.5 properly:
- docs updated
- tests complete
- verification recorded
- report created
- stage lifecycle cleaned up

Do not start Stage 4B.
Do not implement unrelated rendering formats.
```

---

## 1. PURPOSE

Close the context-readable TXT profile stage with documentation, tests, and report.

---

## 2. DOCS TO UPDATE

Update:

```text
README.md
COMMANDS.md
CHANGELOG.md
docs/stages/README.md
```

Optional if architecture docs exist:

```text
docs/architecture/DATASET_FORMAT.md
docs/architecture/TXT_RENDERING.md
```

Recommended new doc:

```text
docs/architecture/TXT_RENDERING.md
```

---

## 3. REQUIRED DOC CONTENT

Docs must explain:

```text
- TXT is a projection, not canonical data.
- JSONL/database records remain canonical.
- `context-readable` is the default TXT profile for user/group export.
- `legacy` remains available.
- The readable profile renders context blocks.
- The readable profile uses:
  [REPLIED MESSAGE]
  [CONTEXT BEFORE]
  [TARGET MESSAGE] / [TARGET MESSAGES]
  [CONTEXT AFTER]
- Missing replies are compact:
  ↪ missing reply #id
- Direct CLI supports `--txt-profile`.
- Interactive console utility/menu also supports or applies the profile.
```

Do not over-document internal implementation in README. Keep README compact.

---

## 4. COMMANDS.MD EXAMPLES

Add examples:

```bash
python3 -m tg_msg_manager.cli export --user-id 123456789 --chat-id 987654321
python3 -m tg_msg_manager.cli export --user-id 123456789 --chat-id 987654321 --txt-profile context-readable
python3 -m tg_msg_manager.cli export --user-id 123456789 --chat-id 987654321 --txt-profile legacy
```

Explain:

```text
Default TXT profile for export is context-readable.
Use legacy for the old flat log-style TXT output.
```

Mention interactive utility:

```text
The interactive menu export flow uses the same TXT profile behavior and can select the profile if TXT output is generated.
```

---

## 5. CHANGELOG

Add new version entry following project style:

```text
Stage 4A.5 Context-Readable TXT Export Profile
```

Required points:

```text
Added context-readable TXT profile.
Made it default for user/group TXT export.
Kept legacy TXT profile available.
Wired profile into direct CLI and interactive console utility.
No JSONL/SQLite/export fetching behavior changed.
```

---

## 6. STAGE REPORT

Create:

```text
docs/stages/reports/STAGE_4A_5_CONTEXT_READABLE_TXT_PROFILE_REPORT.md
```

Required sections:

```text
# Stage 4A.5 — Context-Readable TXT Export Profile Report

## 1. Summary
## 2. Problem
## 3. Profiles added
## 4. Default behavior
## 5. CLI integration
## 6. Interactive menu integration
## 7. Renderer behavior
## 8. Files changed
## 9. Tests
## 10. Verification results
## 11. Runtime behavior statement
## 12. Remaining limitations
## 13. Status
```

Runtime statement must say:

```text
No Telegram fetching behavior changed.
No context extraction behavior changed.
No JSONL schema changed.
No dataset schema changed.
No state schema changed.
No SQLite schema changed.
No analytics/OCR/STT/media optimization added.
```

Verification section must list only commands actually run.

---

## 7. TEST CONSOLIDATION

Before finalizing, ensure tests cover:

```text
profile parser
legacy renderer
context-readable renderer
direct CLI parser
interactive menu profile selection
actual export render dispatch
docs/help surface if tested
```

Run relevant test groups.

---

## 8. FINAL VERIFICATION

Run at minimum:

```bash
pytest tests/test_txt_profiles.py tests/test_legacy_txt_renderer.py tests/test_context_readable_txt_renderer.py
pytest tests/test_txt_profile_cli.py tests/test_txt_profile_menu.py tests/test_export_txt_profile_integration.py
python3 -m compileall tg_msg_manager
ruff check tg_msg_manager tests
ruff format --check tg_msg_manager tests
python3 -m tg_msg_manager.cli export --help
```

If exact test file names differ:

```bash
pytest tests/test_*txt*profile*.py tests/test_*txt*renderer*.py tests/test_cli*.py
```

If practical:

```bash
make test
make verify
```

Do not claim commands passed unless actually run.

---

## 9. LIFECYCLE CLEANUP

After implementation and report:

- [ ] Move Stage 4A.5 task files from:
  ```text
  docs/stages/active/
  ```
  to:
  ```text
  docs/stages/completed/
  ```

- [ ] Move general prompt to:
  ```text
  docs/archive/old_prompts/
  ```

- [ ] Update:
  ```text
  docs/stages/README.md
  ```

- [ ] Ensure:
  ```text
  docs/stages/active/
  ```
  contains only unfinished or next active work.

Do not move files before the report exists.

---

## 10. COMPLETION CRITERIA

Stage 4A.5 is complete only if:

- [ ] `context-readable` TXT profile exists.
- [ ] `legacy` TXT profile exists.
- [ ] user/group export TXT default is `context-readable`.
- [ ] old TXT format remains accessible as `legacy`.
- [ ] direct CLI supports `--txt-profile`.
- [ ] interactive console utility/menu supports or applies the same profile behavior.
- [ ] readable output is block-based.
- [ ] readable output includes required section labels.
- [ ] tests cover renderers, CLI, and menu.
- [ ] docs updated.
- [ ] changelog updated.
- [ ] stage report created.
- [ ] lifecycle cleanup completed.
- [ ] no unrelated runtime/schema/storage changes were made.
