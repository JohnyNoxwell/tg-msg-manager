# STAGE 4A.5.3 — EXPORT CLI AND INTERACTIVE MENU INTEGRATION

Status: active task  
Stage: 4A.5.3  
Type: CLI + interactive console integration  
Depends on: Stage 4A.5.2

---

## 0. CODEX ENTRY CONTRACT

```text
Read AGENTS.md first.

Execute Stage 4A.5.3 — Export CLI and Interactive Menu Integration.

Wire the TXT profile into both:
1. direct CLI export command
2. interactive console utility/menu export flow

Do not implement only direct CLI.
Do not leave the menu path hardcoded to the old TXT format.
```

---

## 1. PURPOSE

The new TXT profile must be usable in the real application path, not only in isolated renderer tests.

Required surfaces:

```text
Direct CLI:
  python3 -m tg_msg_manager.cli export --user-id 123 --chat-id 456 --txt-profile context-readable
  python3 -m tg_msg_manager.cli export --user-id 123 --chat-id 456 --txt-profile legacy

Interactive console utility:
  menu export flow must choose or apply txt_profile
```

---

## 2. DIRECT CLI TASKS

Modify:

```text
tg_msg_manager/cli_parser.py
tg_msg_manager/cli_commands.py
```

Tasks:

- [ ] Add `--txt-profile` to `export` command.
- [ ] Choices/validation:
  ```text
  context-readable
  legacy
  ```
- [ ] Default:
  ```text
  context-readable
  ```
- [ ] Pass parsed profile into export command handler.
- [ ] Pass profile into export service/options/writer path with minimal mechanical delegation.
- [ ] Ensure `--json` behavior remains unchanged.
- [ ] If TXT is not produced when `--json` is used, document/handle profile as ignored.
- [ ] Do not add `--txt-profile` to unrelated commands unless needed.

---

## 3. INTERACTIVE MENU TASKS

Modify:

```text
tg_msg_manager/cli_menu.py
tg_msg_manager/i18n.py
```

or current menu modules.

Required:

- [ ] Interactive export path must support the new TXT profile.
- [ ] It must not be direct-CLI-only.
- [ ] Add prompt if practical:
  ```text
  TXT profile [context-readable/legacy] (Enter = context-readable):
  ```
- [ ] Empty input -> `context-readable`.
- [ ] Invalid input -> standard invalid selection flow.
- [ ] Pass selected profile into the same export flow as direct CLI.
- [ ] If menu currently always exports JSON summary but TXT file is still generated, profile still matters.
- [ ] If menu can choose JSON/TXT, only ask profile when TXT output is relevant.

i18n:

- [ ] Add Russian string.
- [ ] Add English string.
- [ ] Keep wording short.

Suggested RU:

```text
TXT профиль [context-readable/legacy] (Enter = context-readable)
```

Suggested EN:

```text
TXT profile [context-readable/legacy] (Enter = context-readable)
```

---

## 4. EXPORT SERVICE / WRITER WIRING TASKS

Find current TXT writing path for user/group export.

Tasks:

- [ ] Add profile field to relevant export options/request object if one exists.
- [ ] If no options object exists, pass as explicit argument.
- [ ] Keep default at boundary.
- [ ] Route rendering through rendering package dispatcher.
- [ ] Ensure `legacy` calls legacy renderer.
- [ ] Ensure `context-readable` calls readable renderer.
- [ ] Do not add formatting if/else blocks inside protected service files beyond minimal dispatch call.

Preferred pattern:

```text
renderer = get_txt_renderer(txt_profile)
text = renderer.render(records, options)
writer.write(text)
```

---

## 5. DB-EXPORT POLICY

Recommended for this stage:

```text
db-export TXT default remains legacy.
```

Reason:

```text
db-export is more technical and may be used by scripts.
Changing its default may be more breaking.
```

Tasks:

- [ ] Do not change `db-export` default unless trivial and explicitly tested.
- [ ] If adding `--txt-profile` to `db-export`, default should be `legacy` for now.
- [ ] Document chosen behavior.

Do not block Stage 4A.5 if `db-export` integration is deferred. The required path is normal user/group export and interactive utility.

---

## 6. ERROR HANDLING

Rules:

```text
Unknown profile -> parser error in direct CLI.
Unknown profile in menu -> invalid selection and return/pause.
Renderer failure -> existing export error handling path.
```

Do not silently fall back to legacy on invalid explicit user input.

---

## 7. TESTS

Create / update:

```text
tests/test_txt_profile_cli.py
tests/test_txt_profile_menu.py
tests/test_export_txt_profile_integration.py
```

Required direct CLI tests:

- [ ] parser accepts `--txt-profile context-readable`.
- [ ] parser accepts `--txt-profile legacy`.
- [ ] parser rejects unknown profile.
- [ ] export parser default is `context-readable`.
- [ ] `--json` behavior remains unchanged.

Required menu tests:

- [ ] menu empty TXT profile input passes `context-readable`.
- [ ] menu `legacy` input passes `legacy`.
- [ ] menu invalid profile rejects and does not call export.
- [ ] menu integration does not require Telegram in test.

Required integration tests:

- [ ] export flow calls readable renderer by default.
- [ ] export flow calls legacy renderer when requested.
- [ ] old legacy output remains available.
- [ ] readable output contains context block labels.

---

## 8. VERIFICATION

Run:

```bash
pytest tests/test_txt_profile_cli.py tests/test_txt_profile_menu.py tests/test_export_txt_profile_integration.py
pytest tests/test_cli*.py
python3 -m compileall tg_msg_manager
ruff check tg_msg_manager tests
ruff format --check tg_msg_manager tests
python3 -m tg_msg_manager.cli export --help
```

If file names differ, run equivalent tests.

If practical:

```bash
make test
```

Do not claim commands passed unless actually run.

---

## 9. COMPLETION CRITERIA

Complete only if:

- [ ] direct CLI supports `--txt-profile`.
- [ ] direct CLI default is `context-readable` for user/group export.
- [ ] legacy profile remains available.
- [ ] interactive console utility supports or applies the profile.
- [ ] menu path is not left behind.
- [ ] renderer is wired into actual TXT output.
- [ ] JSON output behavior is unchanged.
- [ ] tests cover CLI and menu paths.
