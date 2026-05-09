# STAGE 3E.5 — INTERACTIVE CHANNEL EXPORT OPTIONS PARITY

Status: active task  
Stage: 3E.5  
Type: CLI/menu integration hardening  
Scope: interactive menu only  
Do not implement unrelated features.

---

## 0. CODEX ENTRY CONTRACT

```text
Read AGENTS.md first.

You are working on tg-msg-manager.

Execute Stage 3E.5 — Interactive Channel Export Options Parity.

This task adds missing export-channel options to the interactive menu path.

This is not a channel export behavior rewrite.
This is not a new export feature.
This is not an analytics stage.
This is not a SQLite stage.

Do not change existing direct CLI flag behavior.
Do not change dataset schemas.
Do not change state schemas.
Do not change SQLite schema.
Do not add analytics, OSINT, OCR, STT, media optimization, or media analysis.
```

---

## 1. PURPOSE

Current behavior:

```text
Direct CLI supports channel discussion export and advanced media/output options.
Interactive menu export-channel path does not expose those options.
```

Known issue:

```text
Interactive menu currently hardcodes:
discussion=DISCUSSION_MODE_NONE
max_comments_per_post=DEFAULT_MAX_COMMENTS_PER_POST
output_dir=None
force=False
max_media_size=None
media_types=None
```

Goal:

```text
Bring interactive channel export closer to direct CLI parity by prompting for:
- discussion none/full
- max-comments-per-post
- force
- output-dir
- max-media-size
- media-types
```

This stage must only affect the interactive menu path.

---

## 2. CURRENT BEHAVIOR TO PRESERVE

Preserve:

```text
- direct `export-channel` CLI behavior
- direct CLI flags and defaults
- existing channel export service behavior
- existing dataset files and schemas
- existing media modes: none / metadata / full
- existing discussion modes: none / full
- existing max-comments-per-post validation
- existing max-media-size validation
- existing media-types validation
- existing force behavior
- existing output-dir behavior
- existing non-interactive behavior when stdin/stdout are not TTY
```

Do not remove or rename existing prompts unless necessary.

Do not make the menu path less usable for simple exports.

---

## 3. HARD PROHIBITIONS

Do not implement:

```text
- new export modes
- new discussion modes
- discussion media full download
- media optimization/compression
- OCR
- speech-to-text
- ffmpeg integration
- image/video/audio analysis
- analytics
- OSINT
- bot detection
- sentiment analysis
- user profiling
- SQLite schema changes
- migrations
- DB persistence for channel exports
- dashboard/UI rewrite
- curses/TUI framework
```

Do not modify these protected files unless absolutely necessary for mechanical import/type compatibility:

```text
tg_msg_manager/services/export/service.py
tg_msg_manager/services/db_export/service.py
tg_msg_manager/services/private_archive/service.py
tg_msg_manager/services/context/engine.py
tg_msg_manager/services/channel_export/service.py
```

Rules:

```text
- Do not add feature logic to protected service files.
- Keep ChannelExportService orchestration-only.
- This task should primarily touch CLI/menu/input/testing/docs files.
```

---

## 4. TARGET USER FLOW

Interactive channel export should ask:

```text
1. Channel:
2. Limit optional:
3. Media mode: none / metadata / full
4. Export discussions? none / full
5. Max comments per post [default]:
6. Force full export? y/N
7. Output directory optional:
8. Max media size optional:
9. Media types optional:
```

Recommended behavior:

```text
- Empty discussion input -> none
- Empty max-comments-per-post -> default
- Empty force input -> false
- Empty output-dir input -> None
- Empty max-media-size input -> None
- Empty media-types input -> None
```

Important usability rule:

```text
Do not force advanced options for users who want the default path.
```

Acceptable UX pattern:

```text
Ask all prompts with clear defaults.
```

Better UX pattern, if already consistent with project style:

```text
Ask "Configure advanced channel export options? [y/N]".
If no, use safe defaults.
If yes, ask output-dir, max-media-size, media-types, force.
But discussion should still be asked separately because it is a major channel export feature.
```

Use the least invasive approach compatible with existing menu style.

---

## 5. VALIDATION RULES

### 5.1 Discussion mode

Allowed:

```text
none
full
```

Rules:

```text
- empty -> none
- case-insensitive
- invalid -> print invalid selection and return to menu/pause
```

### 5.2 Max comments per post

Rules:

```text
- empty -> DEFAULT_MAX_COMMENTS_PER_POST
- must be positive integer or follow existing validator behavior
- invalid -> print invalid selection and return to menu/pause
```

Use existing validation if available:

```text
validate_max_comments_per_post
```

Do not duplicate service validation if a validator exists.

### 5.3 Force

Allowed examples:

```text
y
yes
true
1
n
no
false
0
empty
```

Rules:

```text
- empty -> false
- y/yes/true/1 -> true
- n/no/false/0 -> false
- invalid -> print invalid selection and return to menu/pause
```

### 5.4 Output directory

Rules:

```text
- empty -> None
- otherwise pass as raw string/path value exactly as direct CLI handler expects
- do not create custom path semantics in menu
```

### 5.5 Max media size

Rules:

```text
- empty -> None
- otherwise pass as string to existing direct CLI handler, if direct handler already validates/parses it
- do not duplicate size parser if existing command handler already owns validation
```

If current direct CLI stores parsed size in `args.max_media_size`, inspect actual behavior before deciding.

### 5.6 Media types

Rules:

```text
- empty -> None
- accept same format as direct CLI
- examples may include: photo,video,document,audio
- pass to direct CLI handler in the same shape expected by direct CLI path
```

Do not introduce new media type names.

---

## 6. IMPLEMENTATION PLAN

### A. Baseline inspection

- [ ] Read `AGENTS.md`.
- [ ] Inspect interactive menu implementation:
  ```text
  tg_msg_manager/cli_menu.py
  ```
- [ ] Inspect direct channel export handler:
  ```text
  tg_msg_manager/cli_commands.py
  ```
- [ ] Inspect CLI parser flags:
  ```text
  tg_msg_manager/cli_parser.py
  ```
- [ ] Inspect CLI input/render helpers:
  ```text
  tg_msg_manager/cli_io.py
  ```
- [ ] Inspect i18n files used by the project.
- [ ] Inspect existing CLI/menu tests.

### B. Record current gap

- [ ] Confirm interactive menu currently hardcodes:
  ```text
  discussion=DISCUSSION_MODE_NONE
  max_comments_per_post=DEFAULT_MAX_COMMENTS_PER_POST
  output_dir=None
  force=False
  max_media_size=None
  media_types=None
  ```
- [ ] Record this in the stage report.

### C. Add menu prompts

In `_handle_menu_export_channel` or a small helper called from it:

- [ ] Prompt for `discussion`.
- [ ] Normalize empty input to `none`.
- [ ] Validate `discussion` with existing discussion validator or allowed constants.
- [ ] Prompt for `max-comments-per-post`.
- [ ] Normalize empty input to default.
- [ ] Validate positive integer / existing validator.
- [ ] Prompt for `force`.
- [ ] Normalize empty input to false.
- [ ] Validate boolean-like input.
- [ ] Prompt for `output-dir`.
- [ ] Normalize empty input to `None`.
- [ ] Prompt for `max-media-size`.
- [ ] Normalize empty input to `None`.
- [ ] Prompt for `media-types`.
- [ ] Normalize empty input to `None`.

Keep function readable. If `_handle_menu_export_channel` becomes too large, extract pure helpers inside `cli_menu.py`.

### D. Namespace passed to direct handler

Update the `Namespace` passed to `_handle_export_channel_command` so it includes user-selected values:

```python
Namespace(
    channel=...,
    limit=...,
    media=...,
    max_media_size=...,
    media_types=...,
    discussion=...,
    max_comments_per_post=...,
    output_dir=...,
    force=...,
)
```

The direct handler should remain the single path that builds the final `ChannelExportOptions` where practical.

### E. i18n / prompt text

Add or reuse prompt keys for:

```text
prompt_channel_discussion_mode
prompt_channel_max_comments_per_post
prompt_channel_force
prompt_channel_output_dir
prompt_channel_max_media_size
prompt_channel_media_types
```

If the project stores localization separately for English/Russian, update both.

Suggested prompt meanings:

```text
Export discussions? none/full [none]
Max comments per post [default]
Force full export? y/N
Output directory optional
Max media size optional
Media types optional
```

Do not break existing localization.

### F. Tests

Add/update tests for interactive menu path.

Required coverage:

- [ ] default interactive channel export still passes:
  ```text
  discussion=none
  max_comments_per_post=DEFAULT_MAX_COMMENTS_PER_POST
  output_dir=None
  force=False
  max_media_size=None
  media_types=None
  ```
- [ ] interactive discussion `full` is passed to handler.
- [ ] custom max-comments-per-post is passed to handler.
- [ ] force `y` is passed as `True`.
- [ ] output-dir is passed to handler.
- [ ] max-media-size is passed to handler.
- [ ] media-types is passed to handler.
- [ ] invalid discussion mode is rejected.
- [ ] invalid max-comments-per-post is rejected.
- [ ] invalid force value is rejected.
- [ ] direct CLI parser tests remain unchanged.
- [ ] `export-channel --help` still works.

Testing approach:

```text
Mock TerminalInput.prompt_with_esc.
Mock _handle_export_channel_command.
Assert Namespace fields.
```

Do not require real Telegram connection in tests.

### G. Docs

Update relevant docs:

```text
README.md
COMMANDS.md
docs/stages/README.md
```

If architecture docs mention interactive channel export, update them too.

Docs must state:

```text
Interactive channel export can now configure:
- discussion none/full
- max comments per post
- force full export
- output directory
- max media size
- media types
```

Do not over-document implementation internals in user docs.

### H. Stage report

Create:

```text
docs/stages/reports/STAGE_3E_5_INTERACTIVE_CHANNEL_EXPORT_OPTIONS_PARITY_REPORT.md
```

Required sections:

```text
# Stage 3E.5 — Interactive Channel Export Options Parity Report

## 1. Summary
## 2. Problem
## 3. Interactive options added
## 4. Files changed
## 5. Validation behavior
## 6. Tests
## 7. Verification results
## 8. Runtime behavior statement
## 9. Remaining limitations
## 10. Status
```

Runtime statement must say:

```text
No direct CLI behavior changed.
No dataset schema changed.
No state schema changed.
No SQLite schema changed.
No analytics/OCR/STT/media optimization added.
```

---

## 7. VERIFICATION

Run at minimum:

```bash
pytest tests/test_cli_menu*.py tests/test_cli*.py
python3 -m compileall tg_msg_manager
ruff check tg_msg_manager tests
ruff format --check tg_msg_manager tests
python3 -m tg_msg_manager.cli export-channel --help
```

If the exact test file names differ, run the relevant CLI/menu test files plus the full channel export tests if practical:

```bash
pytest tests/test_channel_export_*.py
```

If practical:

```bash
make test
make verify
```

Do not claim commands passed if they were not run.

---

## 8. COMPLETION CRITERIA

Complete only if:

- [ ] interactive menu exposes discussion none/full.
- [ ] interactive menu exposes max-comments-per-post.
- [ ] interactive menu exposes force.
- [ ] interactive menu exposes output-dir.
- [ ] interactive menu exposes max-media-size.
- [ ] interactive menu exposes media-types.
- [ ] defaults preserve previous behavior.
- [ ] direct CLI behavior is unchanged.
- [ ] validation errors are handled cleanly.
- [ ] tests cover default and custom menu paths.
- [ ] docs updated.
- [ ] stage report created.
- [ ] no dataset schema changed.
- [ ] no SQLite schema changed.
- [ ] no analytics/media processing feature added.

---

## 9. FINAL CLEANUP

After completion:

- [ ] Move this task file from:
  ```text
  docs/stages/active/
  ```
  to:
  ```text
  docs/stages/completed/
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

---

## 10. FINAL RESPONSE FORMAT

```text
## Summary
- interactive channel export now exposes discussion and advanced options

## Files changed
- path
- path

## Verification
- command: result
- command: result

## Behavior
- direct CLI unchanged
- dataset schema unchanged
- state schema unchanged
- SQLite unchanged
- no analytics/OCR/STT/media optimization added

## Remaining limitations
- item
- item

## Stage status
Stage 3E.5: complete / partial / blocked
```
