# Отчет Stage 5U - Create Release Candidate Tag

Статус: PASSED

## Цель и prerequisite evidence

- Создан и отправлен только annotated RC-тег `v0.1.0-rc1`.
- Stage 5P: `PASSED`.
- Stage 5Q checklist: `PASSED`.
- Stage 5R.0 package build dry-run: `PASSED`.
- Stage 5R.1 isolated wheel install / CLI smoke: `PASSED`.
- Stage 5S tag plan: `PASSED`, предложен `v0.1.0-rc1`.
- Stage 5T: `KEEP_AS_RELEASE_CANDIDATE`, поскольку evidence выполнения RC-тега
  и post-RC smoke отсутствовало.

## Package и tag evidence

- `pyproject.toml`: package `tg-msg-manager`, version `0.1.0`, console script
  `tg-msg-manager = tg_msg_manager.cli:main`.
- До выполнения `git tag --list "v0.1.0-rc1"` и
  `git ls-remote --tags origin` подтвердили отсутствие тега.
- Tagged commit: `2a3b57deed5be899a27577b43e02904123f85823`
  (`2a3b57d docs: complete stable release decision`).
- Annotated local tag: `v0.1.0-rc1`; tagger timestamp:
  `2026-06-10 21:59:34 +0300`.
- `git push origin v0.1.0-rc1`: passed.
- Remote verification: `0e4171f33ca2de08d597059bd40d812f2a06f1f1`
  at `refs/tags/v0.1.0-rc1`; peeled target локально подтвержден как tagged
  commit выше.

## Команды и результаты

- `python3` / `tomllib` inspection: passed.
- `git status --short`: passed; до tag был только Stage 5U task-файл, после
  выполнения только разрешенные stage-owned docs/lifecycle changes.
- `git diff --check`: passed.
- `git tag --list`, `git ls-remote --tags origin`, `git rev-parse HEAD`,
  `git log --oneline -5`: passed.
- Первая sandbox-попытка `git tag -a ...`: failed (`Operation not permitted`);
  повтор после разрешения: passed.
- Финальная sandbox-попытка exact remote verification: failed (DNS);
  повтор с network-разрешением: passed.
- Local tag verification, push и exact remote tag verification: passed.
- Package build/install, TestPyPI/PyPI publish, GitHub Release, stable tag,
  rollback и post-RC smoke не запускались: запрещены scope.

## Scope и lifecycle

- Изменены только этот отчет, `docs/stages/README.md` и lifecycle-перемещение
  task-файла Stage 5U.
- Production code, tests, CLI, SQLite, dataset/export contracts, package
  metadata, dependencies и version не изменялись.
- TestPyPI/PyPI, GitHub Release и stable tag `v0.1.0` не создавались.
- Rollback не выполнялся. Только для отдельного явного разрешения:
  `git tag -d v0.1.0-rc1`; `git push origin :refs/tags/v0.1.0-rc1`.
- `stage-reviewer: applied from .skills/stage-reviewer/SKILL.md`; verdict:
  pass, blockers отсутствуют.
- `architecture-guard: applied from .skills/architecture-guard/SKILL.md`;
  architecture-sensitive изменения отсутствуют.
- `stage-completion-auditor: applied from
  .skills/stage-completion-auditor/SKILL.md`.
- Task-файл перемещен из `active/` в `completed/`; индекс обновлен.

Итоговая рекомендация: Proceed to STAGE_5U_1_POST_RC_TAG_SMOKE_FROM_TAG
