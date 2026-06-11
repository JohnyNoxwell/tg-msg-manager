# Отчет Stage 5W.1 - PyPI Trusted Publishing Setup

Статус: PASSED

## Prerequisite, preflight и skills

- `STAGE_5W_0_3_STABLE_TAG_ISOLATED_INSTALL_SMOKE_REPORT.md`: `PASSED`;
  решение `READY_FOR_STAGE_5W_1_PYPI_TRUSTED_PUBLISHING_SETUP`.
- Исходный worktree содержал только ожидаемые stage/lifecycle/report
  изменения; `git diff --check` прошел.
- `stage-reviewer: applied from .skills/stage-reviewer/SKILL.md`; verdict:
  pass, stage имеет проверяемые границы и setup-only scope.
- `architecture-guard: applied from .skills/architecture-guard/SKILL.md`;
  verdict: pass, production/CLI/storage/dataset границы не затронуты.

## Stable tag evidence

- Local `v0.1.0`: тип `tag`, object
  `0a1474402f6a95c96ed84f6ed627c4a62eb7e13c`, peeled target
  `2f4ae2448d2e0b3217debd31f093127358215d7f`.
- Remote `v0.1.0`: object и peeled target совпали с local.

## Workflow

- Создан `.github/workflows/pypi-publish.yml`.
- Единственный trigger: `workflow_dispatch`; единственный input: обязательный
  string `tag`.
- Build job проверяет префикс `v`, checkout-ит exact
  `refs/tags/${{ inputs.tag }}` с полной history и сравнивает `HEAD` с
  `refs/tags/${TAG}^{commit}`.
- Distributions собираются один раз через `python -m build`; затем выполняется
  `python -m twine check dist/*`; только после проверки `dist/*` передается
  через `actions/upload-artifact@v4`.
- Отдельный publish job имеет `needs: build`, скачивает artifact через
  `actions/download-artifact@v4`, использует `environment: pypi`,
  `id-token: write` и `pypa/gh-action-pypi-publish@release/v1`.
- TestPyPI endpoint, `repository-url`, username/password/api-token,
  `secrets.*`, TWINE/PyPI token variables и `.pypirc` не используются.
- Automatic triggers отсутствуют.

## GitHub Environment и Trusted Publisher tuple

- `gh auth status`: авторизация подтверждена; реальные token/credential values
  не читались.
- Первый GET `/repos/JohnyNoxwell/tg-msg-manager/environments/pypi`: HTTP 404.
- Environment `pypi` создан через разрешенный `gh api --method PUT`.
- Повторный GET подтвердил environment `pypi`, created_at
  `2026-06-11T08:51:15Z`; environment secrets не создавались.
- Tuple для отдельной ручной регистрации на PyPI:

```text
PyPI project: tg-msg-manager
owner: JohnyNoxwell
repository: tg-msg-manager
workflow filename: pypi-publish.yml
environment name: pypi
```

## Проверки и границы

- Выполнены: `git status --short`, `git diff --check`, local/remote tag
  checks, `gh auth status`, environment GET/PUT/GET, Ruby YAML parse,
  positive required-pattern `rg`, prohibited-pattern `rg`, финальные
  repository checks.
- YAML parse прошел. Все required controls найдены; prohibited patterns
  отсутствуют.
- Workflow не запускался; package не публиковался и не загружался; PyPI
  publisher не регистрировался; GitHub Release не создавался.
- Tags не создавались, не изменялись, не удалялись и не push-ились; `git push`
  не выполнялся.
- Builds, installs, tests, package smoke, Telegram/live/runtime команды не
  выполнялись.
- Credentials, реальные tokens, secrets, `.pypirc`, shell history, private
  artifacts, Telegram sessions, exports/logs/media/screenshots/DBs не
  читались.
- Production code, tests, package metadata/version/dependencies, TestPyPI
  workflow, CLI behavior, SQLite и dataset/export contracts не менялись.
- Изменения stage ограничены main PyPI workflow, отчетом и lifecycle файлами.

## Решение

- `stage-completion-auditor: applied from
  .skills/stage-completion-auditor/SKILL.md`; verdict: complete.
- Lifecycle cleanup выполнен: task перемещен в `completed/`, index обновлен,
  active stage отсутствует.
- Финальное решение:
  `READY_FOR_STAGE_5W_2_PYPI_TRUSTED_PUBLISHER_REGISTRATION`.
- Следующий рекомендуемый stage:
  `STAGE_5W_2_PYPI_TRUSTED_PUBLISHER_REGISTRATION` - вручную зарегистрировать
  exact PyPI Trusted Publisher/Pending Publisher tuple без публикации.
