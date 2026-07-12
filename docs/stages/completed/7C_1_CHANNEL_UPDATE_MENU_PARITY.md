# STAGE 7C.1 — CHANNEL UPDATE MENU PARITY

Status: completed
Stage: 7C.1
Type: implementation
Depends on: Stage 7C.0 `update-channels` command and current interactive main-menu contracts

---

## 0. CODEX ENTRY CONTRACT

1. Read `AGENTS.md`, then this file.
2. Apply `stage-reviewer` and `architecture-guard` before implementation.
3. Inspect only listed files, write a plan of at most 5 bullets, and implement only this scope.

## 1. PURPOSE

Expose bulk channel-export update in the interactive console menu and reorder main-menu actions into export, update/maintenance, settings, then information groups.

## 2. FILES TO INSPECT

- `tg_msg_manager/cli_menu.py`
- `tg_msg_manager/cli_io.py`
- `tg_msg_manager/i18n.py`
- `tg_msg_manager/cli/commands/channel_export.py` — inspection only
- `tests/cli/test_cli.py`
- `tests/cli/test_cli_ui_refresh.py`
- `tests/cli/test_channel_export_cli.py`
- `README.md`
- `COMMANDS.md`
- `docs/development/CLI_CONTRACT.md`
- `.github/workflows/ci.yml`
- `Makefile`

May create `docs/stages/reports/STAGE_7C_1_CHANNEL_UPDATE_MENU_PARITY_REPORT.md`. Do not inspect unrelated stages, reports, roadmap, or archive files.

## 3. HARD PROHIBITIONS

- Do not change direct command names, flags, defaults, dataset/state formats, SQLite schema, export algorithms, or service behavior.
- Do not duplicate batch-update logic in menu/CLI rendering.
- Do not change service, storage, validation, doctor, or protected facade implementations.
- Do not add concurrency, retry, scheduling, runtime dependencies, or unrelated menu redesign.
- Preserve `00`, `98`, `R`, and `P` shortcuts; numeric menu remapping is explicitly scoped.

## 4. ATOMIC IMPLEMENTATION TASKS

1. Add a thin interactive handler that invokes the existing `update-channels` CLI handler with the default channel export root, keeps the menu alive after aggregate failures, and pauses after rendering.
2. Render and dispatch this exact order: `01` user export, `02` PM archive, `03` DB export, `04` channel export, `05` tracked-target update, `06` channel-export update, `07` retry queue, `08` global clean, `09` delete data, `10` scheduler, `11` setup, `12` audit report, `13` about, then `98` language and `00` exit.
3. Add Russian/English labels and descriptions for channel-export update. Keep existing semantic translation keys for existing actions.
4. Update routing/rendering tests for exact order, new handler delegation, partial-failure menu survival, and preserved special shortcuts.

## 5. REQUIRED DOCS

- Update `COMMANDS.md` interactive menu numbering/order and legacy shortcut notes.
- Update Russian and English menu references in `README.md` where numbering is stated.
- Update `docs/development/CLI_CONTRACT.md` with interactive parity coverage only if needed.

## 6. TESTS / VERIFICATION

```bash
python3 -m pytest tests/cli/test_cli.py tests/cli/test_cli_ui_refresh.py tests/cli/test_channel_export_cli.py -q
python3 -m compileall tg_msg_manager
make verify
make pre-commit
```

Do not claim success unless commands were run. Environment/tooling failure leaves the stage incomplete.

## 7. REPORT

Create `docs/stages/reports/STAGE_7C_1_CHANNEL_UPDATE_MENU_PARITY_REPORT.md` in Russian with changed files, exact menu order, preserved contracts, checks, and skill application facts.

## 8. COMPLETION CRITERIA

- Interactive menu exposes bulk channel update and follows the exact ordered mapping.
- Direct CLI, service, dataset, state, SQLite, and special shortcut contracts remain unchanged.
- Focused tests, `make verify`, and `make pre-commit` pass; report exists.
- `stage-completion-auditor` passes and lifecycle cleanup is completed according to `AGENTS.md`.

## 9. OUTPUT LIMITS

- Follow the final format and 1200-character limit from `AGENTS.md`.
- No full diffs, large code blocks, generic summaries, or future recommendations.
