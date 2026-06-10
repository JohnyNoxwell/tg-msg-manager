# Черновик заметок Release Candidate Stage 5Q

Статус: черновик release-candidate notes; stable release не заявлен.

## Реализованное и подтвержденное

- Проект остается локальным Telegram export/data pipeline и CLI.
- Публичная документация и фактический CLI согласованы, включая local-only
  `target names`.
- Package identity подтверждена как `tg-msg-manager`, import root -
  `tg_msg_manager`, console script - `tg-msg-manager = tg_msg_manager.cli:main`.
- Stage 5P post-refactor verification и аудиты Stage 5Q.0-5Q.2 имеют статус
  `PASSED`.
- Tracked sensitive/private artifact blocker candidates не обнаружены.

## Известные ограничения

- Live Telegram smoke checks остаются manual/session-dependent и не входят в
  offline release verification.
- License metadata отсутствует.
- Runtime dependencies имеют нижние границы без верхних; совместимость будущих
  major-релизов этим checklist не подтверждена.
- Это не подтверждение stable readiness и не факт выпуска.

## Отложенные области

- Chat/channel title history Stage 5N.2.
- Публичный contract для private archive / `export-pm`.
- Generated-output coverage для filenames, rotation и no-new-work, full raw
  JSON и SQLite schema contract status.
- Любые analytics, OSINT interpretation, profiling, GUI/SaaS и
  LLM-dependent core behavior.

## Ожидающие проверки

- Stage 5R.0: только локальный package build dry-run.
- Stage 5R.1: только isolated wheel install smoke после успешного Stage 5R.0.
- Release-candidate tag plan и stable release decision остаются отдельными
  будущими стейджами.

Версия, tag, build artifact, upload/publish и stable release не создавались.
