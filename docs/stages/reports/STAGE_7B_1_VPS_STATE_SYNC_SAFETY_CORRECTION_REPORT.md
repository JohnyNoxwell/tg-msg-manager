# STAGE 7B.1 — VPS state sync safety correction report

## Scope summary

Исправлен `deploy/local/tg-state-sync.sh`: default local source теперь корень checkout, но `push` синхронизирует только явный allowlist runtime state tg-msg-manager. Исходный код, `.git`, docs/tests/deploy, virtualenv, build/scratch и неизвестные root-level файлы не попадают в push.

## Changed files

- `.dockerignore`
- `deploy/local/tg-state-sync.sh`
- `deploy/vps/README.md`
- `docs/stages/reports/STAGE_7B_1_VPS_STATE_SYNC_SAFETY_CORRECTION_REPORT.md`
- `docs/stages/README.md`
- `docs/stages/completed/stage_7b_1_vps_state_sync_safety_correction.md`

## Behavior preservation notes

Код приложения, CLI, SQLite schema, export formats, Telegram authorization, Dockerfile, `compose.yaml`, сервисы, storage, тесты приложения и shell aliases Stage 7B.0 не изменялись.

## Sync allowlist notes

`push` строит NUL-delimited `--files-from` allowlist только из разрешённых runtime root files/patterns и директорий. `push --dry-run` не создаёт remote directory. `push --apply` создаёт только `TGMM_REMOTE_STATE_DIR`, затем запускает rsync. `--delete` не используется.

Если локальный `.tg_msg_manager.lock` существует, helper пишет предупреждение в stderr, но lock не синхронизирует и не удаляет.

## Pull behavior notes

`pull exports` получает только `exports/`, `DB_EXPORTS/`, `PUBLIC_GROUPS/`, `PRIVAT_DIALOGS/`. `pull logs` получает только `LOGS/`, `delete_log.txt` и root-level `*.log`. Отсутствующие optional paths пропускаются с коротким сообщением. Pull не загружает обратно configs, Telegram sessions или SQLite databases.

## Secret/data exclusion notes

`.dockerignore` усилен для `config.local.json`, `.env.local`, session/SQLite sidecars, `DB_TARGETS.txt`, `*_state.json`, `.tg_msg_manager.lock`, `delete_log.txt`, root-level `*.log`, `DB_EXPORTS`, `PUBLIC_GROUPS`, `PRIVAT_DIALOGS`, `LOGS`, `exports`, `logs`, без ослабления `.git`, venv/cache/build protections.

## Check results

- `sh -n deploy/local/tg-state-sync.sh`: passed.
- `git diff --check`: passed.
- `make verify`: passed, `634 passed`.
- `make pre-commit`: passed, embedded `make verify` completed with `634 passed`.

## Docker availability result

- `docker info`: failed after sandbox escalation; Docker daemon unavailable: `Cannot connect to the Docker daemon at unix:///Users/maczone/.docker/run/docker.sock. Is the docker daemon running?`
- Docker build/Compose checks were not run because Docker daemon was unavailable.

## Manual safety inspection result

Code inspection confirms push can only pass entries emitted by `build_push_file_list` into `rsync --from0 --files-from`. That list never includes `.git`, source package directories, `docs`, `tests`, `deploy`, `.github`, virtualenvs, build artifacts, `scratch`, `.tg_msg_manager.lock`, or unknown root-level files.

## Blockers or caveats

Docker daemon was unavailable in the local Codex environment. No real VPS or real runtime data was used.

## Skill application

- `stage-reviewer: applied from .skills/stage-reviewer/SKILL.md`
- `architecture-guard: not required; stage changed deployment helper/docs/.dockerignore only and did not touch CLI code, services, storage, protected files, compatibility wrappers, dataset/export behavior, or architecture rules`
- `stage-completion-auditor: applied from .skills/stage-completion-auditor/SKILL.md`
