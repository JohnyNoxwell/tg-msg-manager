# Отчет Stage 5V.4 - TestPyPI Workflow Publish

Статус: PASSED

## Prerequisites и pre-upload state

- Stage 5V.3 имеет статус `PASSED` и
  `READY_FOR_STAGE_5V_4_TESTPYPI_WORKFLOW_PUBLISH`.
- Workflow существует на default branch `main`; Environment `testpypi`
  подтвержден.
- Exact annotated tag `v0.1.0-rc2`: local/remote tag object
  `962f3e413cd87d443ab5775e59e9539e84dfe57f`, peeled target
  `2f4ae2448d2e0b3217debd31f093127358215d7f`.
- До dispatch workflow runs отсутствовали; публичные TestPyPI и PyPI JSON
  checks для `tg-msg-manager` вернули HTTP `404`.

## Единственный dispatch и run evidence

- Выполнен ровно один разрешенный dispatch:
  `gh workflow run testpypi-publish.yml --repo JohnyNoxwell/tg-msg-manager
  --ref main -f tag=v0.1.0-rc2`.
- Run ID: `27314027216`; URL:
  `https://github.com/JohnyNoxwell/tg-msg-manager/actions/runs/27314027216`.
- Event/ref/workflow SHA: `workflow_dispatch`, `main`,
  `5ade6c6b249c4ab40b340e14c0e0f8b91242c7a8`.
- Run завершен с `success`; единственный run в workflow listing.
- Build job `80690506902`: `success`; validate tag, exact tag checkout, peeled
  target verification, build, twine check и artifact upload прошли.
- Publish job `80690539765`: `success`; artifact download и Trusted Publishing
  в TestPyPI прошли.
- GitHub artifact `release-distributions`: присутствует, не expired.
- Повторный dispatch не выполнялся.

## Public TestPyPI evidence

- Project/version: `tg-msg-manager` / `0.1.0`.
- `tg_msg_manager-0.1.0-py3-none-any.whl`, SHA-256:
  `fbefdacff174590c7391998c0086b68006337be3bc66148371f57088edcaa6ea`.
- `tg_msg_manager-0.1.0.tar.gz`, SHA-256:
  `c117cc75fc470f3a2629a2166d14511df40330135f329beaabc1dce3daf4f586`.
- Имена, package types, project name и version совпадают с Stage 5U.7
  expectations; checksum equality с предыдущим локальным build не требовалась.
- Public PyPI JSON check после публикации вернул HTTP `404`; PyPI не затронут.

## Проверки, границы и lifecycle

- Exact local/remote tag checks: passed.
- Workflow/default branch/Environment checks: passed.
- Pre/post workflow run listings и terminal run/job inspection: passed.
- Public TestPyPI filenames/SHA-256 verification: passed.
- `git diff --check`: passed.
- Workflow сообщил GitHub warning о будущем переходе JavaScript actions с
  Node.js 20 на Node.js 24; текущий run успешно завершен.
- Source, tests, workflow, package metadata/version/dependencies, tags,
  releases, secrets, environments и publisher settings не изменялись.
- `stage-reviewer: applied from .skills/stage-reviewer/SKILL.md`; verdict:
  pass.
- `architecture-guard: applied from .skills/architecture-guard/SKILL.md`;
  verdict: pass, architecture-sensitive изменения отсутствуют.
- `stage-completion-auditor: applied from
  .skills/stage-completion-auditor/SKILL.md`; verdict: complete.
- Task-файл перемещен из `active/` в `completed/`, lifecycle index обновлен.

Решение: exact RC2 artifacts опубликованы и публично проверены на TestPyPI;
PyPI не затронут.
