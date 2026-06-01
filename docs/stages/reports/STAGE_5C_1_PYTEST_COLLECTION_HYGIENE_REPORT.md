# STAGE 5C.1 — PYTEST COLLECTION HYGIENE REPORT

## Итог

Stage 5C.1 завершен. Pytest discovery ограничен каталогом `tests/`; `scratch/test_whitelist.py` больше не собирается командой `python3 -m pytest --collect-only -q -p no:cacheprovider`.

## Проверенные файлы

- `AGENTS.md`
- `docs/stages/active/stage_5c_1_pytest_collection_hygiene.md`
- `pyproject.toml`
- `Makefile`
- `.gitignore`
- `scratch/test_whitelist.py`
- `tests/`

## Наблюдение до изменения

- Команда `python3 -m pytest --collect-only -q -p no:cacheprovider` собирала `scratch/test_whitelist.py::test_whitelist`.
- Всего до изменения было собрано 512 тестов.

## Измененные файлы

- `pyproject.toml` — добавлен узкий pytest collection boundary через `testpaths = ["tests"]`.
- `docs/stages/reports/STAGE_5C_1_PYTEST_COLLECTION_HYGIENE_REPORT.md` — добавлен этот отчет.
- `docs/stages/README.md` — обновлен lifecycle index.
- `docs/stages/completed/stage_5c_1_pytest_collection_hygiene.md` — stage-файл перенесен в completed.

## Проверки

- `python3 -m pytest --collect-only -q -p no:cacheprovider` — passed; после изменения собрано 511 тестов, `scratch/` не собирается.
- `python3 -m unittest discover -s tests -q` — passed; 472 теста, OK.
- `python3 -m compileall tg_msg_manager tests` — passed.
- `ruff check tg_msg_manager tests` — passed.
- `git diff --check` — passed.

## Подтверждения

- Runtime code не изменялся.
- CLI behavior не изменялось.
- Dataset formats не изменялись.
- SQLite schema не изменялась.
- `scratch/` файлы не удалялись и не редактировались.

## Навыки

- `stage-reviewer: applied from .skills/stage-reviewer/SKILL.md`
- `stage-completion-auditor: applied from .skills/stage-completion-auditor/SKILL.md`

## Lifecycle

- Финальный отчет создан.
- Stage-файл перенесен из `docs/stages/active/` в `docs/stages/completed/`.
- `docs/stages/README.md` обновлен.
