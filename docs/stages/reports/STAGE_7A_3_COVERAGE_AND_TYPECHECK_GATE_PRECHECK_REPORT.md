# Stage 7A.3 — отчет по precheck coverage и typecheck gate

Статус: завершено.

## Навыки

- stage-reviewer: applied from .skills/stage-reviewer/SKILL.md
- stage-completion-auditor: applied from .skills/stage-completion-auditor/SKILL.md

## Инвентаризация

- `pyproject.toml` не содержит `coverage`, `pytest-cov`, `mypy`, `pyright`, `pyre` или отдельного type-check target.
- `[project.optional-dependencies].dev` содержит только `ruff==0.15.17` и `pytest>=8.0.0,<9`.
- `Makefile` содержит `lint`, `format-check`, `test`, `verify`, `pre-commit`; обязательных coverage/typecheck gate нет.
- `.github/workflows/ci.yml` запускает `make verify` на Python `3.11` и `3.12`.
- Package metadata объявляет `requires-python = ">=3.9"`, а Ruff настроен на `target-version = "py39"`.
- В `tests/` и `tg_msg_manager/` есть типовые `typing` imports, но нет обязательной статической проверки типов.

## Рекомендация

1. Сначала отдельный stage для coverage baseline: добавить только измерение покрытия и отчет baseline без обязательного порога.
2. Затем отдельный stage для минимального coverage gate: выбрать узкий порог после baseline и включить его в `make verify`.
3. После этого отдельный typecheck precheck: выбрать `mypy` или `pyright`, зафиксировать исключения для Python `>=3.9` и CI `3.11/3.12`.
4. Typecheck gate делать обязательным только после отдельного debt-reduction stage, если baseline показывает приемлемый шум.

## Проверки

- `python3 -m pytest tests -q`: passed, `634 passed in 37.26s`
- `git diff --check`: passed

## Измененные файлы

- `docs/stages/reports/STAGE_7A_3_COVERAGE_AND_TYPECHECK_GATE_PRECHECK_REPORT.md`
- `docs/stages/README.md`
- `docs/stages/completed/STAGE_7A_3_COVERAGE_AND_TYPECHECK_GATE_PRECHECK.md`
- `docs/stages/active/STAGE_7A_3_COVERAGE_AND_TYPECHECK_GATE_PRECHECK.md`

## Не изменялось

- Product code и tests не менялись.
- CLI names, flags, defaults, outputs и behavior не менялись.
- SQLite schema, migrations и dataset/export formats не менялись.
- Mandatory coverage/typecheck dependencies и gates не добавлялись.

## Итог

Coverage/typecheck gate precheck выполнен. Рекомендована последовательность через baseline, затем узкий coverage gate, затем отдельный typecheck precheck/debt-reduction.
