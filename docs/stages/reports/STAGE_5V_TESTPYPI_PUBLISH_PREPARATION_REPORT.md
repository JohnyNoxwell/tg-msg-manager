# Отчет Stage 5V - TestPyPI Publish Source Decision

Статус: PASSED

## Prerequisites

- Отчеты Stage 5U, 5U.1, 5U.2, 5U.3 и 5U.4 существуют и имеют статус
  `PASSED`.
- Текущий HEAD: `2f4ae2448d2e0b3217debd31f093127358215d7f`.
- Локальный `v0.1.0-rc1` является annotated tag и указывает на commit
  `2a3b57deed5be899a27577b43e02904123f85823`.
- Remote `refs/tags/v0.1.0-rc1` существует:
  `0e4171f33ca2de08d597059bd40d812f2a06f1f1`.

## Сравнение metadata

- Текущие и tagged metadata совпадают по package name `tg-msg-manager`,
  version `0.1.0` и script `tg-msg-manager = tg_msg_manager.cli:main`.
- Текущий `pyproject.toml` содержит `license = { file = "LICENSE" }` и
  classifier `License :: OSI Approved :: MIT License`; tagged source их не
  содержит.
- Текущий holder в `LICENSE`: `R.P.`; tagged holder: `RP`.
- Следовательно, `v0.1.0-rc1` предшествует утвержденной MIT metadata и не
  должен публиковаться в TestPyPI.

## Tag и GitHub Release state

- Локальный и remote stable tag `v0.1.0` отсутствуют.
- GitHub Releases `v0.1.0-rc1` и `v0.1.0` отсутствуют (`release not found`).
- Проверки package-index name/auth отложены до отдельного Stage 5V.1.
- Build, install, upload, publish, создание/удаление/push тегов и GitHub
  Release не выполнялись.

## Команды и результаты

- `git status --short`: passed; присутствовали только разрешенные
  stage/lifecycle docs.
- `git diff --check`: passed.
- `git tag --list "v0.1.0-rc1"` и exact `git ls-remote`: passed.
- `git tag --list "v0.1.0"` и exact `git ls-remote`: passed, тег отсутствует.
- `gh release view v0.1.0-rc1`: первая sandbox-попытка заблокирована сетью;
  разрешенный повтор: `release not found`.
- `gh release view v0.1.0`: sandbox-попытка и первый разрешенный повтор
  заблокированы сетью/таймаутом; второй разрешенный повтор: `release not found`.
- `git show v0.1.0-rc1:pyproject.toml` и structured `tomllib` comparison:
  passed.

## Scope и lifecycle

- Изменены только этот отчет, `docs/stages/README.md` и lifecycle location
  task-файла Stage 5V.
- Production code, tests, CLI, SQLite, dataset/export contracts, package
  metadata, dependencies, version и publish state не изменялись.
- `stage-reviewer: applied from .skills/stage-reviewer/SKILL.md`; verdict:
  pass.
- `architecture-guard: applied from .skills/architecture-guard/SKILL.md`;
  scope pass, architecture-sensitive изменения отсутствуют.
- `stage-completion-auditor: applied from
  .skills/stage-completion-auditor/SKILL.md`.
- Task-файл перемещен из `active/` в `completed/`; lifecycle index обновлен.

Итоговое решение: `NEW_RC_TAG_REQUIRED_BEFORE_TESTPYPI`

Рекомендация: Proceed to `STAGE_5U_5_RC2_TAG_PLAN`.
