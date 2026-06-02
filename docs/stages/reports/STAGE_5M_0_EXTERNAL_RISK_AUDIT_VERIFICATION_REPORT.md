# Отчет Stage 5M.0 - External Risk Audit Verification

## Статус

Stage 5M.0 завершен после проверки и lifecycle cleanup.

## Итоговый вывод

EXTERNAL_RISK_AUDIT_VERIFIED_WITH_FOLLOWUPS

## Навыки

- `stage-reviewer: applied from .skills/stage-reviewer/SKILL.md`
- `architecture-guard: applied from .skills/architecture-guard/SKILL.md`
- `stage-completion-auditor: applied from .skills/stage-completion-auditor/SKILL.md`

## Проверенные файлы

- `AGENTS.md`
- `.skills/stage-reviewer/SKILL.md`
- `.skills/architecture-guard/SKILL.md`
- `.skills/stage-completion-auditor/SKILL.md`
- `README.md`
- `COMMANDS.md`
- `CHANGELOG.md`
- `pyproject.toml`
- `Makefile`
- `.gitignore`
- `docs/README.md`
- `docs/development/README.md`
- `docs/development/PRIVACY_AND_SENSITIVE_ARTIFACTS.md`
- `docs/development/RELEASE_CHECKLIST_SCOPE.md`
- `docs/development/LOCAL_VERIFICATION_MATRIX.md`
- `docs/development/RELEASE_CANDIDATE_DECISION.md`
- `docs/architecture/NON_CHANNEL_EXPORT_CONTRACT_V1.md`
- `docs/architecture/PRIVATE_ARCHIVE_CONTRACT_DEFERRED_DECISION.md`
- `docs/architecture/CURRENT_PROJECT_CONTEXT.md`
- `docs/stages/README.md`
- `docs/stages/reports/STAGE_5L_1_RELEASE_CANDIDATE_DECISION_RECHECK_REPORT.md`
- `docs/stages/reports/STAGE_5K_4_RELEASE_CANDIDATE_DECISION_REPORT.md`
- `docs/stages/reports/STAGE_5J_2_FIXTURE_TO_CONTRACT_VERIFICATION_REPORT.md`
- `docs/stages/reports/STAGE_5J_3_RELEASE_READINESS_RECHECK_CHANGELOG_FINALIZATION_REPORT.md`
- `.github/workflows/ci.yml`
- `config.example.json`
- `run.py`
- `tg_msg_manager/cli_parser.py`
- `tg_msg_manager/cli/`
- `tg_msg_manager/services/`
- `tg_msg_manager/infrastructure/storage/`
- `tests/`

`backlog/` отсутствует. Приватные артефакты, реальные exports, sessions, SQLite DB contents, logs, screenshots, media и real Telegram data не читались.

## Audit point / evidence / classification / severity / follow-up

| Audit point | Evidence | Classification | Severity | Follow-up |
| --- | --- | --- | --- | --- |
| Generated-output filenames, `_partN`, rotation, no-new-work, `.export_state`, `export-pm` coverage | `NON_CHANNEL_EXPORT_CONTRACT_V1.md`, 5J.2 и 5J.3 reports фиксируют focused coverage и deferred gaps; `file_writer.py` и DB export tests покрывают часть `_partN`/skip mechanics; `.export_state` normal path не создает | partially confirmed / needs follow-up stage | medium | 5M.5 |
| `schedule` macOS-only UX/doc/test gap | README отмечает macOS/launchd; `scheduler.py` пишет LaunchAgents и вызывает `launchctl`; tests мокают launchctl; COMMANDS не содержит отдельный `schedule` reference; i18n содержит stale Linux/Windows strings | partially confirmed | medium | 5M.3 |
| `config.json` / credentials / `.gitignore` safety | `.gitignore` игнорирует config, env, sessions, DB, logs, exports; privacy doc перечисляет категории; `config.example.json` placeholder-only | already handled | low | 5M.1 verification |
| Credentials/session/export privacy visibility | README ссылается на privacy doc; privacy doc явно запрещает раскрытие private artifacts; release/local verification docs запрещают live/private checks | already handled | low | 5M.1 can tighten if needed |
| `run.py` vs package/CLI entrypoints | `run.py` imports `tg_msg_manager.cli.main`; `pyproject.toml` maps `tg-msg-manager = tg_msg_manager.cli:main`; `cli/__main__.py` delegates to `main` | false / not applicable | low | none |
| CI absent/present/insufficient | `.github/workflows/ci.yml` exists, runs on push main and PR, Python 3.11/3.12, installs `.[dev]`, runs `make verify`; no secrets/live checks | already handled | low | 5M.4 can document bridge |
| `--limit` per-dialog ambiguity | README Known Limitations says user multi-dialog export applies `--limit` per `sync_chat`; code passes limit from dialog loop to each `sync_chat`; COMMANDS only says existing sync meanings | partially confirmed | medium | 5M.3 |
| `export-pm` stable/core presentation vs deferred contract | README lists `export-pm` in quick reference/features and has known limitation; contract docs and reports say private archive contract deferred/excluded | partially confirmed | medium | 5M.2 |
| Public `backlog/` noise/privacy risk | `backlog/` directory is absent; `.gitignore` ignores `backlog/` and `LOCAL_BACKLOG.md` | false / not applicable | low | none |
| Telethon session recovery, FloodWait/rate limits, SQLite concurrency | Session sensitivity documented; login FloodWait has CLI error formatting; `max_rps` is in config examples; README notes SQLite pressure for large deep exports, but operational guidance is scattered and FloodWait/rate-limit expectations are not fully user-facing | partially confirmed | medium | 5M.6 |

## Confirmed issues

- Broader generated-output contract coverage remains incomplete.
- `schedule` UX is macOS/launchd in implementation, while command reference coverage is incomplete and i18n still has stale Linux/Windows scheduler strings.
- `--limit` semantics are clear in README Known Limitations but under-specified in COMMANDS.
- `export-pm` is visible as a feature while its contract remains explicitly deferred.
- Operational risk guidance exists but is scattered and incomplete for FloodWait/rate limits and SQLite concurrency caveats.

## Already-handled points

- `config.json`, env files, Telethon sessions, SQLite DB files, exports, logs and runtime state are ignored/documented as sensitive.
- CI exists and runs offline `make verify` on push/PR without credentials.
- Release-candidate formatting blocker from 5K.4 is superseded by 5L.1 green local verification.
- `run.py`, module entrypoint, and console script point to the same CLI main.

## False / not applicable points

- Public `backlog/` risk is not applicable because `backlog/` is absent and ignored.
- Runtime entrypoint divergence is not confirmed.

## Missing evidence

- Live Telegram smoke behavior was not verified because 5M.0 forbids real Telegram data, sessions, credentials, and private artifacts.
- No private artifact contents were inspected.

## Измененные файлы

- `docs/stages/reports/STAGE_5M_0_EXTERNAL_RISK_AUDIT_VERIFICATION_REPORT.md`
- `docs/stages/README.md`
- `docs/stages/completed/stage_5m_0_external_risk_audit_verification.md`
- `docs/stages/active/stage_5m_0_external_risk_audit_verification.md` removed by lifecycle move.

## Recommended follow-up order

1. 5M.1 config / credentials / gitignore safety audit.
2. 5M.2 public docs feature status alignment.
3. 5M.3 schedule / limit / entrypoint UX audit.
4. 5M.4 CI / local verification bridge plan.
5. 5M.5 deferred contract coverage prioritization.
6. 5M.6 operational risk notes.

## Проверки

- `git diff --check`: passed.
- `perl -ne 'if(/[ \t]$/){print "$ARGV:$.:$_"; $bad=1} END{exit($bad?1:0)}' docs/stages/reports/STAGE_5M_0_EXTERNAL_RISK_AUDIT_VERIFICATION_REPORT.md docs/stages/completed/stage_5m_0_external_risk_audit_verification.md docs/stages/active/stage_5m_1_config_credentials_gitignore_safety_audit.md docs/stages/active/stage_5m_2_public_docs_feature_status_alignment.md docs/stages/active/stage_5m_3_schedule_limit_entrypoint_ux_audit.md docs/stages/active/stage_5m_4_ci_local_verification_bridge_plan.md docs/stages/active/stage_5m_5_deferred_contract_coverage_prioritization.md docs/stages/active/stage_5m_6_operational_risk_notes.md docs/stages/README.md`: passed.

## Подтверждения

- Runtime behavior не менялся.
- CLI behavior не менялся.
- Tests и fixtures не менялись.
- SQLite/storage/services не менялись.
- Output formats, dataset formats, state semantics, retry behavior и release metadata не менялись.
- Release, tag, version bump, package build/upload/publish не выполнялись.

## Lifecycle

- Финальный отчет создан.
- Stage-файл перенесен из `docs/stages/active/` в `docs/stages/completed/`.
- `docs/stages/README.md` обновлен.
- В `docs/stages/active/` остались только незавершенные Stage 5M.1-5M.6 task files.
