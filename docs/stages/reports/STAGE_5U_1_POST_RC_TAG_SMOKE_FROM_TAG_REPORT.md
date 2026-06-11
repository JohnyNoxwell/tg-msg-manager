# Отчет Stage 5U.1 - Post-RC Tag Smoke From Tag

Статус: PASSED

## Цель и prerequisite evidence

- Повторно проверена сборка, изолированная установка и help-only CLI smoke из
  exact source уже существующего тега `v0.1.0-rc1`, не из текущей ветки.
- Stage 5U: `PASSED`; его отчет подтверждает создание и push annotated tag,
  target commit и отсутствие TestPyPI/PyPI/GitHub Release/stable tag на момент
  Stage 5U.
- Local tag существует, имеет тип `tag` и peeled target
  `2a3b57deed5be899a27577b43e02904123f85823`.
- Remote tag существует: tag object
  `0e4171f33ca2de08d597059bd40d812f2a06f1f1`; peeled target совпадает с
  `2a3b57deed5be899a27577b43e02904123f85823`.
- До smoke рабочее дерево содержало только разрешенный active task-файл.

## Изолированный build/install/smoke

- Первая попытка: `/tmp/tg-msg-manager-5u1-Fbl7oG`; metadata проверена, затем
  sandbox DNS заблокировал установку `build`; каталог удален.
- Успешная попытка: `/tmp/tg-msg-manager-5u1-asJDk6`; каталог удален.
- `git archive --format=tar v0.1.0-rc1`: passed.
- Metadata exported source: `tg-msg-manager`, version `0.1.0`,
  `tg-msg-manager = tg_msg_manager.cli:main`.
- Build venv, `pip install --upgrade pip build` и
  `python -m build <tag-source> --outdir <temp-dist>`: passed.
- Fresh install venv и установка exact built wheel: passed.

Артефакты и SHA-256:

- `tg_msg_manager-0.1.0-py3-none-any.whl`:
  `b4a385bdac651875c7a610cc2d58aa7a4d4b84147954e6463c45a209b13dd18a`
- `tg_msg_manager-0.1.0.tar.gz`:
  `7ee8dc188052cca61fc840b43cdf8e77c54af2fb8b33d8c5210f5a69e335ebce`

Help-only smoke:

- `tg-msg-manager --help`: passed; `usage: tg-msg-manager [-h]`.
- `tg-msg-manager target --help`: passed; subcommand `names` присутствует.
- `tg-msg-manager target names --help`: passed.
- `python -m tg_msg_manager.cli --help`: passed.

## Команды, cleanup и границы

- `git status --short --untracked-files=all`, `git diff --check`, local/remote
  tag checks, tag type/target checks и repository artifact check: passed.
- Sandbox remote-check сначала failed из-за DNS; повтор с network permission:
  passed.
- Оба `/tmp/tg-msg-manager-5u1-*` каталога удалены; cleanup verification:
  passed.
- Repository `dist/`, `build/`, `*.egg-info`, `.venv-build`: отсутствуют.
- Не запускались publish, workflow dispatch, GitHub Release, rollback, новые
  tag-команды, Telegram/live/private-artifact команды: запрещены scope.
- Telegram access, credentials, sessions и client initialization не выполнялись.
- Production code, tests, CLI, SQLite, dataset/export contracts, package
  metadata, dependencies и version не изменялись.
- Stage не создавал TestPyPI/PyPI publish, GitHub Release, stable tag или другие
  новые теги; существующие поздние release-состояния не изменялись.
- Изменены только этот отчет и lifecycle task-файла Stage 5U.1;
  `docs/stages/README.md` уже отражал completed lifecycle и не изменялся.

## Skills и lifecycle

- `stage-writer`: applied from
  `/Users/maczone/.codex/skills/stage-writer/SKILL.md`.
- `stage-reviewer: applied from .skills/stage-reviewer/SKILL.md`; verdict:
  pass.
- `architecture-guard: applied from .skills/architecture-guard/SKILL.md`;
  architecture-sensitive изменения отсутствуют.
- `stage-completion-auditor: applied from
  .skills/stage-completion-auditor/SKILL.md`.
- После создания отчета active task перемещен в completed; индекс уже содержал
  корректную completed запись.

Итоговая рекомендация: Proceed to STAGE_5U_2_LICENSE_METADATA_DECISION before
TestPyPI publishing
