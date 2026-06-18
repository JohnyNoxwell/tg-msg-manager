# STAGE 7A.0 — TEST INFRASTRUCTURE BASELINE AND HARDENING PLAN REPORT

Статус: complete

## Что проверено

- `AGENTS.md`
- `Makefile`
- `.github/workflows/ci.yml`
- `pyproject.toml`
- `docs/development/README.md`
- `docs/development/LOCAL_VERIFICATION_MATRIX.md`
- `docs/development/PR_CHECKLIST.md`
- `docs/stages/README.md`

## Текущий baseline

- `make test` сейчас запускает `python3 -m unittest discover -s tests -q`.
- CI запускает `make verify` на Python 3.11 и 3.12.
- `make verify` запускает `make lint`, `make format-check`, `make test`.
- Dev extras содержат `pytest>=8.0.0,<9`, но pytest не является runner для `make test`.
- Конфигурация `pyproject.toml` содержит `tool.pytest.ini_options.testpaths = ["tests"]`.
- Обязательного coverage gate нет.
- Обязательного mypy/pyright gate нет.
- Отдельного обязательного fixture contract snapshot gate в `Makefile` нет.

## Что создано

- `docs/stages/completed/STAGE_7A_0_TEST_INFRASTRUCTURE_BASELINE_AND_HARDENING_PLAN.md`
- `docs/stages/active/STAGE_7A_1_PYTEST_AUTHORITY_AND_CI_GATE_ALIGNMENT.md`
- `docs/stages/active/STAGE_7A_2_FIXTURE_CONTRACT_SNAPSHOT_GATE.md`
- `docs/stages/active/STAGE_7A_3_COVERAGE_AND_TYPECHECK_GATE_PRECHECK.md`
- `docs/stages/reports/STAGE_7A_0_TEST_INFRASTRUCTURE_BASELINE_AND_HARDENING_PLAN_REPORT.md`

## Решение по этапам

- Stage 7A.1 переводит `make test` на pytest и сохраняет `make verify` как CI-parity gate.
- Stage 7A.2 добавляет обязательный fixture-backed contract snapshot gate через pytest/`make verify`.
- Stage 7A.3 делает precheck для coverage и type-check gate, без преждевременного добавления шумных обязательных инструментов.

## Проверки

- `python3 -m pytest tests -q`: passed, `633 passed in 38.40s`.

## Ограничения и caveats

- В рабочем дереве до Stage 7A.0 уже были несвязанные изменения в коде, stage lifecycle и docs; этот stage их не менял и не откатывал.
- Code/test gate изменения не выполнялись в Stage 7A.0, чтобы не форматировать и не смешивать чужие изменения.
- `git diff --check` не запускался после stage edits, потому что `docs/stages/README.md` уже имел несвязанные незакоммиченные изменения; итоговая проверка должна быть выполнена в чистом или согласованном рабочем дереве.

## Skills

- `stage-writer`: applied from `/Users/maczone/.codex/skills/stage-writer/SKILL.md`.
- `stage-reviewer`: applied from `.skills/stage-reviewer/SKILL.md`; candidate stages passed manual pre-flight review.
- `stage-completion-auditor`: applied from `.skills/stage-completion-auditor/SKILL.md`; Stage 7A.0 complete with caveat on pre-existing dirty worktree.

## Что сохранено

- Product code не изменялся.
- Test code не изменялся.
- CLI behavior не изменялся.
- SQLite schema не изменялась.
- Dataset/export formats не изменялись.
- Runtime dependencies не изменялись.

## Завершение

- Implementation: complete.
- Required docs: complete.
- Lifecycle cleanup: complete.
