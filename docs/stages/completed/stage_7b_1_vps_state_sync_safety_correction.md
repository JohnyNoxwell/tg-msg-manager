# STAGE 7B.1 — VPS state sync safety correction

Status: completed
Stage: 7B.1
Type: implementation
Depends on: Stage 7B.0 merge commit `b912b51`.

## 0. CODEX ENTRY CONTRACT

Read `AGENTS.md` first. Use `stage-reviewer` before implementation. Use `architecture-guard` only if implementation touches CLI code, services, storage, protected files, compatibility wrappers, dataset/export behavior, or architecture rules.

Work only on a separate branch and through a PR. Do not connect to a real VPS. Do not use real `config.json`, Telegram sessions, SQLite databases, exports, or logs.

## 1. PURPOSE

Correct the Stage 7B.0 local state sync helper so it syncs only tg-msg-manager runtime state, not the source checkout, while preserving Docker Compose behavior and all application behavior.

## 2. FILES TO INSPECT

Required:

```text
AGENTS.md
.dockerignore
deploy/local/tg-state-sync.sh
deploy/vps/README.md
docs/stages/README.md
```

May create or edit only:

```text
.dockerignore
deploy/local/tg-state-sync.sh
deploy/vps/README.md
docs/stages/active/stage_7b_1_vps_state_sync_safety_correction.md
docs/stages/reports/STAGE_7B_1_VPS_STATE_SYNC_SAFETY_CORRECTION_REPORT.md
docs/stages/README.md
docs/stages/completed/stage_7b_1_vps_state_sync_safety_correction.md
```

## 3. HARD PROHIBITIONS

- Do not change Dockerfile, compose.yaml, CLI code, services, storage, application tests, or Stage 7B.0 shell aliases unless a blocker proves it is required.
- Do not change public CLI behavior, SQLite schema, export formats, Telegram authorization, Docker Compose logic, service behavior, storage behavior, or logging behavior.
- Do not add systemd, cron, CI workflows, registry setup, secrets, or network services.
- Do not use `--delete` in sync helpers.
- Do not connect to a real VPS or transfer real config, sessions, SQLite databases, exports, or logs.

## 4. ATOMIC IMPLEMENTATION TASKS

1. Change `deploy/local/tg-state-sync.sh` default `TGMM_LOCAL_STATE_DIR` to the checkout root two levels above the script, while preserving manual override.
2. Make push use an explicit allowlist of runtime root files and directories only; preserve relative structure, warn to stderr if `.tg_msg_manager.lock` exists, never sync it, never sync source/docs/tests/deploy/.git/venvs/build/scratch/unknown files, and do not create remote directories during `push --dry-run`.
3. Make `push --apply` create `TGMM_REMOTE_STATE_DIR` if needed, then rsync with archive mode, compression, `--partial`, and `--info=progress2`.
4. Preserve pull commands. `pull exports` fetches `exports/`, `DB_EXPORTS/`, `PUBLIC_GROUPS/`, `PRIVAT_DIALOGS/`; `pull logs` fetches `LOGS/`, `delete_log.txt`, and root-level `*.log`; `pull all` runs both. Missing optional paths must be skipped with a short message and must not stop remaining pulls.
5. Update `.dockerignore` to exclude runtime state and sidecars without weakening existing protections.
6. Update `deploy/vps/README.md` in Russian with the corrected local source, allowlist behavior, examples, lock handling, WAL/SHM sidecars, and secret warnings.
7. Create the factual report in Russian, then perform lifecycle cleanup according to `AGENTS.md`.

## 5. REQUIRED DOCS

Required:

```text
deploy/vps/README.md
docs/stages/reports/STAGE_7B_1_VPS_STATE_SYNC_SAFETY_CORRECTION_REPORT.md
docs/stages/README.md
```

## 6. TESTS / VERIFICATION

Run and record:

```bash
sh -n deploy/local/tg-state-sync.sh
git diff --check
make verify
make pre-commit
```

Check manually by code inspection that push cannot transfer `.git`, source code, `docs`, `tests`, or virtualenvs.

Run Docker build/Compose checks only if Docker daemon is available. If unavailable, record exact reason without marking them passed.

## 7. REPORT

Write `docs/stages/reports/STAGE_7B_1_VPS_STATE_SYNC_SAFETY_CORRECTION_REPORT.md` in Russian.

Include:

```text
scope summary
changed files
behavior preservation notes
sync allowlist notes
pull behavior notes
secret/data exclusion notes
check results
Docker availability result
manual safety inspection result
blockers or caveats
stage-reviewer: applied from .skills/stage-reviewer/SKILL.md
architecture-guard: applied from .skills/architecture-guard/SKILL.md or not required with reason
stage-completion-auditor: applied from .skills/stage-completion-auditor/SKILL.md
```

## 8. COMPLETION CRITERIA

- Local sync helper defaults to checkout root but only pushes explicit runtime state allowlist.
- Pull behavior preserves export/log retrieval and does not pull config, sessions, or SQLite databases.
- `.dockerignore` excludes required runtime state and sidecars.
- Russian VPS docs are updated.
- Required checks are run and recorded, or environment blockers are recorded honestly.
- Factual report exists in Russian.
- `docs/stages/README.md` is updated and lifecycle cleanup is complete.
- PR exists for the branch.

## 9. OUTPUT LIMITS

Final response must follow `AGENTS.md` final format, be in Russian, and stay under 1200 characters.
