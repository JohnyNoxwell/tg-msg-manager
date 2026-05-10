# STAGE 4B.0 — CONSOLE UTILITY VISUAL REFRESH

Status: active task
Stage: 4B.0
Type: presentation / UX
Depends on: `tg_msg_manager/cli.py`, `tg_msg_manager/cli_menu.py`, `tg_msg_manager/cli_io.py`, `tg_msg_manager/utils/ui.py`

---

## 0. CODEX ENTRY CONTRACT

```text
Read AGENTS.md first.

Execute Stage 4B.0 — Console Utility Visual Refresh.

Goal:
Refresh terminal presentation only.

Do not start later stages.
Do not change command names, CLI flags, defaults, output files, SQLite schema, or data flow unless explicitly scoped.

Use AGENTS.md compact output format.
```

## 1. PURPOSE

Refresh the interactive console utility so prompts, menus, summaries, warnings, and errors are easier to scan in TTY mode. Keep runtime behavior unchanged. Keep non-TTY output readable. Keep changes local to terminal presentation.

## 2. FILES TO INSPECT

Required:

```text
tg_msg_manager/utils/ui.py
tg_msg_manager/cli_menu.py
tg_msg_manager/cli_io.py
```

Optional only if needed:

```text
tg_msg_manager/cli.py
```

May read:

```text
AGENTS.md
this stage file
tests that exercise the in-scope files
```

Do not read or change:

```text
unrelated source modules
unrelated docs
docs/archive
docs/stages/completed
existing docs/stages/reports files unrelated to this stage
```

## 3. HARD PROHIBITIONS

Do not change:

```text
export logic
sync logic
delete logic
retry logic
scheduler logic
database behavior
file formats
command-line arguments
defaults
locale behavior
data validation rules
output filenames
output directory layout
SQLite schema
```

Do not add:

```text
analytics
OSINT logic
profiling
fingerprinting
OCR
STT
media recognition
LLM-dependent behavior
dashboard UI
web UI
GUI toolkit
new persistence
new report formats
new runtime dependencies
```

## 4. ATOMIC IMPLEMENTATION TASKS

1. Inspect current terminal helpers.
   - identify existing color helpers
   - identify existing icon helpers
   - identify header, menu, prompt, and summary renderers
   - do not edit yet

2. Define presentation constants.
   - palette names
   - semantic state labels
   - icon constants
   - no runtime behavior changes

3. Update header and section rendering.
   - main menu header
   - section separators
   - subsection labels

4. Update menu row rendering.
   - menu item labels
   - numbering and alignment
   - disabled or unavailable state if already present

5. Update prompt rendering.
   - input prompt
   - confirmation prompt
   - empty or default choice hint

6. Update status rendering.
   - success
   - warning
   - error
   - neutral info

7. Update summary rendering.
   - operation summary
   - no-new-work summary
   - failure summary

8. Verify TTY and non-TTY output.
   - color disabled remains readable
   - no layout jitter introduced
   - no behavior changes

## 5. REQUIRED DOCS

Do not update docs unless code changes alter visible CLI help, command surface, documented examples, output snippets, command behavior, defaults, or architecture boundaries.

Required:

```text
docs/stages/reports/STAGE_4B_0_CONSOLE_UTILITY_VISUAL_REFRESH_REPORT.md
```

Conditional:

```text
CHANGELOG.md only if project convention records this user-visible change
README.md only if existing examples, screenshots, or output snippets become inaccurate
COMMANDS.md only if command behavior, flags, or documented output examples change
Architecture docs only if responsibilities or boundaries change
```

Do not update docs just to restate the stage.
Do not create documentation churn.

## 6. TESTS / VERIFICATION

Run focused checks for changed paths:

```bash
python3 -m compileall tg_msg_manager
ruff check tg_msg_manager tests
pytest tests -q -k "cli or menu or ui"
```

If exact tests are known, include them.
If those tests do not exist or the filter is too broad, run the closest focused tests available and record the exact command.
Do not claim checks passed unless actually run.
If a check cannot be run, record the exact reason.

## 7. REPORT

Create:

```text
docs/stages/reports/STAGE_4B_0_CONSOLE_UTILITY_VISUAL_REFRESH_REPORT.md
```

Report must record:

- exact files changed
- exact checks run
- what changed
- what remained unchanged
- what was not run and why
- completion status

## 8. COMPLETION CRITERIA

This stage is complete when:

- requested implementation is done;
- prohibited behavior remains unchanged;
- docs were updated only if required, or no docs update was needed;
- tests/checks are recorded;
- the report exists;
- lifecycle cleanup is completed according to AGENTS.md.

## 9. OUTPUT LIMITS

Use AGENTS.md compact final response format.

Final response must contain only:

```text
DONE:
- ...

CHANGED:
- ...

CHECKS:
- ...

NOTES:
- ...

STAGE:
- complete/incomplete: <reason if incomplete>
```

Do not paste full diffs.
Do not explain the task back to the user.
Do not include broad summaries.
Do not include future recommendations unless required by a real blocker.
