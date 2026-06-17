# STAGE 6E.0 - CI GATE ALIGNMENT AND RUFF FORMAT GUARDRAILS REPORT

Статус: complete

## Что изменено

- `AGENTS.md`
  - Добавлено правило CI-parity: stage с изменениями code/tests не может быть complete без `make verify`, если CI запускает `make verify`.
  - Зафиксированы исключения: docs-only без code/test изменений или environment/tooling failure с incomplete/blocked статусом.
  - Добавлен локальный pre-push/handoff guardrail `make pre-commit`; `make verify` остаётся authoritative gate.
- `pyproject.toml`
  - Ruff pin изменён с `ruff>=0.15.0,<0.16` на `ruff==0.15.17`.
- `docs/development/README.md`
  - Developer workflow дополнен правилом CI-parity и `make pre-commit`.
- `docs/development/LOCAL_VERIFICATION_MATRIX.md`
  - Добавлено правило, что focused checks не заменяют `make verify` для code/test changes.
- `docs/development/PR_CHECKLIST.md`
  - Добавлены пункты `make verify` и `make pre-commit` для code/test changes.
- `docs/stages/README.md`
  - Добавлена stage completion policy, report entry и completed prompt record.
- `docs/stages/completed/STAGE_6E_0_CI_GATE_ALIGNMENT_AND_RUFF_FORMAT_GUARDRAILS.md`
  - Stage task moved from active to completed.
- `docs/stages/reports/STAGE_6E_0_CI_GATE_ALIGNMENT_AND_RUFF_FORMAT_GUARDRAILS_REPORT.md`
  - Создан factual completion report.
- `tg_msg_manager/application/resources.py`
- `tg_msg_manager/infrastructure/storage/_sqlite_write_path.py`
- `tests/architecture/test_application_runtime_contract.py`
- `tests/architecture/test_static_boundaries.py`
- `tests/cli/test_cli.py`
- `tests/infrastructure/storage/test_storage_sqlite.py`
  - Только `ruff format` изменения.

## Что исправлено

- Stage/report discipline больше не разрешает завершать code/test stage с `make verify: not run`, когда CI authoritative gate использует `make verify`.
- Локальная dependency policy больше не допускает Ruff patch drift относительно наблюдавшегося CI formatter: используется `ruff==0.15.17`.
- Существующий repository formatter drift отформатирован тем же Ruff version.

## Что сохранено

- CLI behavior не изменялся.
- SQLite schema не изменялась.
- Export formats, manifest/state/output layout не изменялись.
- Telegram logic не изменялась.
- Тесты изменены только форматированием.
- Protected service facades и compatibility wrappers не изменялись.
- `.pre-commit-config.yaml` не добавлялся: выбран минимальный documented guardrail `make pre-commit`.
- Lock file / constraints file не добавлялись: exact Ruff pin в existing dev extras является самым узким изменением.

## Проверки

- `python -m pip install -e .[dev]`: failed, локальный shell не содержит команду `python`.
- `python3 -m pip install -e .[dev]`: passed after approved network access; installed `ruff-0.15.17`.
- `ruff --version`: passed, `ruff 0.15.17`.
- `ruff format tg_msg_manager tests`: passed, 6 files reformatted.
- `make verify`: passed.
- `make pre-commit`: passed.
- `git diff --check`: passed.

## CI parity

- CI gate in `.github/workflows/ci.yml`: `make verify`.
- Local/stage completion gate documented as `make verify` for code/test changes.
- Focused checks remain allowed only as additional checks, not as replacement.
- Remaining exceptions: docs-only stages without code/test changes; impossible tooling/environment with incomplete or blocked status.

## Skills

- `stage-reviewer`: applied from `.skills/stage-reviewer/SKILL.md`; verdict pass.
- `architecture-guard`: applied from `.skills/architecture-guard/SKILL.md`; violations none.
- `stage-completion-auditor`: applied from `.skills/stage-completion-auditor/SKILL.md`; verdict complete.

## Не изменялось

- CLI commands, flags, defaults, outputs.
- SQLite schema or migrations.
- Dataset/export formats.
- Telegram fetch/export behavior.
- Test semantics.
- Heavy dependency management tools.

## Завершение

- Implementation: complete.
- Required docs: complete.
- Lifecycle cleanup: complete.
