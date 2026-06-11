# Отчет Stage 5W.4 - PyPI Install Smoke

Статус: PASSED

## Prerequisite, preflight и tag evidence

- `STAGE_5W_3_PYPI_WORKFLOW_PUBLISH_REPORT.md`: `PASSED`; основной PyPI
  содержит `tg-msg-manager==0.1.0`.
- До stage рабочее дерево было чистым; после создания task-файла
  `git status --short` показывал только разрешенный `docs/stages/active/`;
  `git diff --check` прошел.
- Local `v0.1.0`: type `tag`, object
  `0a1474402f6a95c96ed84f6ed627c4a62eb7e13c`, peeled target
  `2f4ae2448d2e0b3217debd31f093127358215d7f`.
- Remote `origin` содержит те же tag object и peeled target.

## Public PyPI evidence

- `https://pypi.org/pypi/tg-msg-manager/0.1.0/json`: HTTP `200`;
  project/version `tg-msg-manager` / `0.1.0`.
- `tg_msg_manager-0.1.0-py3-none-any.whl`, SHA-256
  `70a10ef8a9fb3c6f81de38b336e7983c0d3db7be00013bc00cf82e23afe1c87c`.
- `tg_msg_manager-0.1.0.tar.gz`, SHA-256
  `951bee67ea7e44c6d89ecc4b70456ba95d9c5610e813b3085fe923a032ac3eb5`.
- Имена и SHA-256 совпали с evidence Stage 5W.3. Первая sandbox-попытка
  public check получила DNS error; разрешенный сетевой повтор прошел.

## Fresh install и metadata

- Fresh workspace: `/tmp/tg-msg-manager-5w4-oP88kx`; isolated virtualenv:
  `.venv-pypi-install`; isolated `HOME` находился внутри workspace.
- Python `3.12`; pip после upgrade: `26.1.2`.
- Exact install:
  `python -m pip install --index-url https://pypi.org/simple/ --no-cache-dir "tg-msg-manager==0.1.0"`.
- Использован только основной PyPI. TestPyPI, extra index, local wheel,
  `--find-links`, editable install и source from repo не использовались.
- `pip freeze`: `Telethon==1.43.2`, `annotated-types==0.7.0`,
  `pyaes==1.6.1`, `pyasn1==0.6.3`, `pydantic==2.13.4`,
  `pydantic-core==2.46.4`, `pydantic-settings==2.14.1`,
  `python-dotenv==1.2.2`, `rsa==4.9.1`, `tg-msg-manager==0.1.0`,
  `typing-inspection==0.4.2`, `typing_extensions==4.15.0`.
- `pip show tg-msg-manager`: Name `tg-msg-manager`, Version `0.1.0`,
  Requires `pydantic, pydantic-settings, telethon`.
- Installed metadata inspection: passed; version/name/Requires-Python,
  required dependencies, MIT classifier, `License-File: LICENSE`, installed
  LICENSE file и console script `tg-msg-manager = tg_msg_manager.cli:main`
  подтверждены.
- Optional import sanity: passed.

## Help-only smoke и cleanup

- `tg-msg-manager --help`: exit `0`.
- `tg-msg-manager target --help`: exit `0`.
- `tg-msg-manager target names --help`: exit `0`.
- `python -m tg_msg_manager.cli --help`: exit `0`.
- Telegram client/network/API/session/runtime-data access не выполнялся;
  help запускался с isolated `HOME`.
- Workspace удален; `test ! -d /tmp/tg-msg-manager-5w4-oP88kx` прошел.

## Границы, команды и lifecycle

- Выполнены: `git status --short`, `git diff --check`, exact local/remote tag
  checks, public PyPI JSON check, fresh venv/pip install, pip freeze/show,
  metadata/import/help checks и cleanup check.
- Tests, full tests, Telegram/live/runtime commands, publish/upload,
  workflow dispatch, GitHub Release, git push и tag create/modify/delete/push
  не выполнялись.
- Credentials, tokens, secrets, `.pypirc`, shell history и private artifacts
  не читались.
- Production code, tests, workflows, package metadata/version/dependencies,
  CLI, SQLite и dataset/export contracts не изменялись.
- Финальные `git status --short` и `git diff --check` прошли: status содержит
  только три разрешенных docs-файла, whitespace errors отсутствуют.
- Изменены только `docs/stages/completed/stage_5w_4_pypi_install_smoke.md`,
  `docs/stages/reports/STAGE_5W_4_PYPI_INSTALL_SMOKE_REPORT.md` и
  `docs/stages/README.md`.
- `stage-writer`: applied from
  `/Users/maczone/.codex/skills/stage-writer/SKILL.md`.
- `stage-reviewer: applied from .skills/stage-reviewer/SKILL.md`; verdict:
  pass.
- `architecture-guard: applied from .skills/architecture-guard/SKILL.md`;
  verdict: pass.
- `stage-completion-auditor: applied from
  .skills/stage-completion-auditor/SKILL.md`.
- После отчета task перемещен из `active/` в `completed/`, index обновлен.

Решение: `READY_FOR_OPTIONAL_GITHUB_RELEASE_OR_RELEASE_CHAIN_CLOSEOUT`.

Следующий рекомендуемый stage:
`STAGE_5X_GITHUB_RELEASE_OR_RELEASE_CHAIN_CLOSEOUT_DECISION`.
