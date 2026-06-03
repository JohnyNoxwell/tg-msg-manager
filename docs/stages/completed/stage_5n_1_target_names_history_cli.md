# STAGE 5N.1 — Target Names History CLI

Status: active task
Stage: 5N.1
Type: feature/CLI/docs
Depends on: `docs/stages/reports/STAGE_5N_0_TARGET_NAMES_HISTORY_READ_MODEL_REPORT.md`, Stage 5N.0 read model.

---

## 0. CODEX ENTRY CONTRACT

Read `AGENTS.md` first. Then read `.skills/stage-reviewer/SKILL.md`, `.skills/architecture-guard/SKILL.md`, `.skills/stage-completion-auditor/SKILL.md`, this stage file, and the Stage 5N.0 report. Apply `stage-reviewer` before implementation changes, `architecture-guard` before reporting, and `stage-completion-auditor` before claiming complete.

Do not execute Stage 5N.2.

## 1. PURPOSE

Add the read-only CLI command:

```bash
tg-msg-manager target names <target> [--field all|username|display_name|title] [--format text|json]
```

Defaults: `--field all`, `--format text`.

The command must read local metadata only and must not contact Telegram.

## 2. FILES TO INSPECT

Required:

- `AGENTS.md`
- `.skills/stage-reviewer/SKILL.md`
- `.skills/architecture-guard/SKILL.md`
- `.skills/stage-completion-auditor/SKILL.md`
- `TASK_CODEX_TARGET_NAMES_HISTORY_STAGE_FILES.md`
- `docs/stages/reports/STAGE_5N_0_TARGET_NAMES_HISTORY_READ_MODEL_REPORT.md`
- `docs/development/CLI_CONTRACT.md`
- `docs/development/PRIVACY_AND_SENSITIVE_ARTIFACTS.md`
- `docs/user/QUICKSTART.md`
- `README.md`
- `COMMANDS.md`
- `tg_msg_manager/cli_parser.py`
- `tg_msg_manager/cli/__init__.py`
- `tg_msg_manager/cli/commands/__init__.py`
- `tg_msg_manager/cli/commands/report.py`
- `tg_msg_manager/cli_commands.py`
- `tg_msg_manager/services/target_names/`
- `tests/cli/test_cli.py`
- `tests/cli/test_non_channel_contract_cli.py`

Allowed to create or edit:

- `tg_msg_manager/cli_parser.py`
- `tg_msg_manager/cli/__init__.py`
- `tg_msg_manager/cli/commands/__init__.py`
- `tg_msg_manager/cli/commands/target_names.py`
- `tg_msg_manager/cli_commands.py`
- `tg_msg_manager/services/target_names/renderers.py`
- `tests/cli/test_target_names_cli.py`
- `tests/services/target_names/test_target_names_renderers.py`
- `COMMANDS.md`
- `docs/user/QUICKSTART.md`
- `docs/development/CLI_CONTRACT.md`
- `docs/stages/reports/STAGE_5N_1_TARGET_NAMES_HISTORY_CLI_REPORT.md`

## 3. HARD PROHIBITIONS

- Do not change Stage 5N.0 storage semantics except for narrow bug fixes required by tests.
- Do not change SQLite schema, migrations, indexes, `PRAGMA user_version`, export formats, non-channel contracts, report output, retry behavior, or existing command defaults.
- Do not instantiate or require Telegram client for `target names`; add `target` to the local-only command set.
- Do not add raw SQL to CLI or services.
- Do not add business logic to protected service facades or compatibility wrappers.
- Treat `cli_commands.py`, `cli/commands/__init__.py`, and CLI handler maps as mechanical routing/import wiring only.
- Do not read private artifacts, real DB files, sessions, credentials, logs, exports, screenshots, or media.
- Do not include real Telegram IDs/usernames/names/chat titles/message text in tests/docs.
- Do not add analytics, OSINT, profiling, identity claims, suspicious-behavior language, or LLM behavior.
- Do not publish, tag, bump version, or create package artifacts.

## 4. ATOMIC IMPLEMENTATION TASKS

1. Add nested argparse command `target names` with choices for `--field` and `--format`; preserve existing command help tests by updating expected command surface intentionally.
2. Add CLI handler that calls the Stage 5N.0 query service and renders text or JSON only to stdout.
3. Add text renderer with stable sections: `Target`, `Type`, optional `Current`, and `<Field> history`; render missing old values as `-`.
4. Add JSON renderer with deterministic keys: `target`, `target_type`, `current`, `history`; use JSON `null` for missing values.
5. Add controlled errors for `target_not_found` and `ambiguous_target`; JSON mode must emit only JSON on stdout/stderr according to existing project convention selected in implementation.
6. Add CLI and renderer tests for all/default, field filtering, JSON output, empty history, unknown target, ambiguous target, and parser validation.
7. Update `COMMANDS.md`, `docs/user/QUICKSTART.md`, and `docs/development/CLI_CONTRACT.md` for the new local-only command and limitations.

## 5. REQUIRED DOCS

Update only:

- `COMMANDS.md`
- `docs/user/QUICKSTART.md`
- `docs/development/CLI_CONTRACT.md`

Docs must state that the command is local-only, may be incomplete if the target was not observed before, does not refresh Telegram metadata, and is not identity/profiling analysis.

## 6. TESTS / VERIFICATION

Run:

```bash
python3 -m unittest tests.cli.test_target_names_cli -q
python3 -m unittest tests.services.target_names.test_target_names_renderers -q
python3 -m unittest discover tests -p '*target*names*.py'
python3 -m unittest discover tests -p '*target*history*.py'
python3 -m unittest tests.cli.test_cli -q
python3 -m unittest tests.cli.test_non_channel_contract_cli -q
git diff --check
```

Final desired checks before closing the 5N workflow:

```bash
make test
make verify
```

Do not claim checks passed unless actually run.

## 7. REPORT

Create `docs/stages/reports/STAGE_5N_1_TARGET_NAMES_HISTORY_CLI_REPORT.md` in Russian.

Include: status, files added/modified/deleted, CLI contract, output contract, errors, docs updated, tests added, verification run/not run, SQLite schema changed yes/no, Telegram calls added yes/no, title-history limitation, and `stage-reviewer: applied from .skills/stage-reviewer/SKILL.md`, `architecture-guard: applied from .skills/architecture-guard/SKILL.md`, `stage-completion-auditor: applied from .skills/stage-completion-auditor/SKILL.md`.

## 8. COMPLETION CRITERIA

- `target names` appears in CLI help.
- Defaults are `--field all` and `--format text`.
- Command is read-only and does not require Telegram client initialization.
- Text and JSON outputs are deterministic and covered by tests.
- Unknown and ambiguous targets return controlled errors.
- Empty history is not a failure when the target exists.
- User docs and CLI contract are updated.
- Required report exists.
- lifecycle cleanup is completed according to AGENTS.md.

## 9. OUTPUT LIMITS

Final response must follow `AGENTS.md`, be in Russian, avoid full diffs, and mention only changed files, checks, preservation, notes, and stage status.
