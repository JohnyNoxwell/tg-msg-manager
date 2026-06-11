# Отчет Stage 5W.3 - PyPI Workflow Publish

Статус: PASSED

## Prerequisites и pre-upload state

- Stage 5W.2: `PASSED`; решение
  `READY_FOR_STAGE_5W_3_PYPI_WORKFLOW_PUBLISH`.
- Рабочее дерево до stage было очищено: результаты Stage 5U.1 зафиксированы
  коммитом `af26c88` и отправлены в `origin/main`.
- Exact annotated tag `v0.1.0`: local/remote tag object
  `0a1474402f6a95c96ed84f6ed627c4a62eb7e13c`, peeled target
  `2f4ae2448d2e0b3217debd31f093127358215d7f`.
- `.github/workflows/pypi-publish.yml` существует на `origin/main`;
  Environment `pypi` подтвержден.
- До dispatch `gh run list --workflow pypi-publish.yml` вернул пустой список.
- Публичный pre-upload PyPI JSON check вернул HTTP `404`.

## Единственный dispatch и run evidence

- Выполнен ровно один dispatch:
  `gh workflow run pypi-publish.yml --repo JohnyNoxwell/tg-msg-manager
  --ref main -f tag=v0.1.0`.
- Run ID: `27345484415`; URL:
  `https://github.com/JohnyNoxwell/tg-msg-manager/actions/runs/27345484415`.
- Event/ref/workflow SHA: `workflow_dispatch`, `main`,
  `af26c88d00cd0b2c8b11e223d0fa0d36f63e92e7`.
- Run завершен с `success`; повторный dispatch/rerun не выполнялся.
- Build job `80792895080`: `success`; exact tag checkout/verification, build,
  twine check и artifact upload прошли.
- Publish job `80792965269`: `success`; artifact download и Trusted Publishing
  в основной PyPI прошли.
- GitHub сообщил неблокирующий warning о переходе JavaScript actions с Node.js
  20 на Node.js 24; текущий run успешно завершен.

## Public PyPI evidence

- Public endpoint `https://pypi.org/pypi/tg-msg-manager/0.1.0/json`: HTTP `200`.
- Project/version: `tg-msg-manager` / `0.1.0`.
- `tg_msg_manager-0.1.0-py3-none-any.whl`, SHA-256:
  `70a10ef8a9fb3c6f81de38b336e7983c0d3db7be00013bc00cf82e23afe1c87c`.
- `tg_msg_manager-0.1.0.tar.gz`, SHA-256:
  `951bee67ea7e44c6d89ecc4b70456ba95d9c5610e813b3085fe923a032ac3eb5`.

## Границы, skills и lifecycle

- Выполнены exact tag checks, workflow/default-branch/Environment checks,
  pre/post run listings, terminal run/job inspection, public PyPI artifact
  verification, `git status --short` и `git diff --check`.
- Не выполнялись повторный dispatch/rerun, TestPyPI publish, GitHub Release,
  tag operations, Telegram/live/runtime команды или private artifact access.
- Credentials, tokens и secrets не читались.
- Production code, tests, workflows, package metadata/version/dependencies,
  CLI, SQLite и dataset/export contracts не изменялись.
- Изменены только task/report Stage 5W.3 и lifecycle index.
- `stage-writer`: applied from
  `/Users/maczone/.codex/skills/stage-writer/SKILL.md`.
- `stage-reviewer: applied from .skills/stage-reviewer/SKILL.md`; verdict:
  pass.
- `architecture-guard: applied from .skills/architecture-guard/SKILL.md`;
  verdict: pass.
- `stage-completion-auditor: applied from
  .skills/stage-completion-auditor/SKILL.md`.
- После отчета task перемещен из `active/` в `completed/`, index обновлен.

Решение: `tg-msg-manager==0.1.0` опубликован и публично проверен на основном
PyPI.
