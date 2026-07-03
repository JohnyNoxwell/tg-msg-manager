# STAGE 7B.0 — VPS Docker Compose Deployment Wrapper

Status: completed
Stage: 7B.0
Type: implementation
Depends on: current local CLI entry point in `pyproject.toml`, current command contracts in `README.md` and `COMMANDS.md`, and empty `docs/stages/active/` state before this file.

---

## 0. CODEX ENTRY CONTRACT

Read `AGENTS.md` first. Use `stage-reviewer` before implementation. Use `architecture-guard` if implementation touches CLI code, services, storage, protected files, compatibility wrappers, dataset/export behavior, or architecture rules.

Work only on a separate branch and through a PR. Do not connect to a real VPS. Do not request or transfer real `config.json`, Telegram sessions, SQLite databases, exports, or logs.

The repository is prepared for manual Ubuntu 24.04 VPS use through Docker Compose. The expected VPS checkout path is `/opt/tg-msg-manager`. Persistent state lives on the host in `/opt/tg-msg-manager/state` and is mounted into the container as `/root/TG_MSG_MANAGER`.

## 1. PURPOSE

Add Docker Compose packaging and small deployment helpers that run the existing `tg-msg-manager` CLI from the current checkout while preserving all application behavior and keeping real user data outside the image and repository.

The container must support:

```bash
docker compose run --rm tg-msg-manager --help
docker compose run --rm tg-msg-manager update
docker compose run --rm tg-msg-manager export ...
```

Running without CLI arguments must keep the existing interactive CLI mode.

## 2. FILES TO INSPECT

Required:

```text
AGENTS.md
pyproject.toml
tg_msg_manager/cli/__init__.py
tg_msg_manager/cli_parser.py
README.md
COMMANDS.md
docs/stages/README.md
```

May create or edit only:

```text
Dockerfile
compose.yaml
.dockerignore
deploy/vps/tgm
deploy/vps/tg-shell.sh
deploy/vps/install-shell.sh
deploy/vps/README.md
deploy/local/tg-state-sync.sh
docs/stages/active/stage_7b_0_vps_docker_compose_deployment.md
docs/stages/reports/STAGE_7B_0_VPS_DOCKER_COMPOSE_DEPLOYMENT_REPORT.md
docs/stages/README.md
docs/stages/completed/stage_7b_0_vps_docker_compose_deployment.md
```

Do not inspect unrelated source, completed stages, archived prompts, existing report files unrelated to this stage, or the whole docs tree.

## 3. HARD PROHIBITIONS

- Do not change public CLI names, flags, defaults, output formats, filenames, export layout, retry behavior, Telegram authorization, logging behavior, or interactive behavior.
- Do not change SQLite schema, migrations, storage SQL, dataset formats, state semantics, incremental behavior, force behavior, or no-new-work behavior.
- Do not modify service facades, compatibility wrappers, storage modules, export modules, channel export modules, or CLI handlers unless a blocker proves a minimal mechanical wiring change is required.
- Do not add analytics, OSINT, profiling, classification, OCR, STT, LLM behavior, GUI, dashboard, SaaS, systemd units, cron jobs, GitHub secrets, container registry setup, CI workflows, ports, networks, restart policy, privileged mode, `cap_add`, host networking, or background service mode.
- Do not add `config.json`, `.env`, Telegram sessions, SQLite files, exports, logs, or real data to the image or repository.
- Do not use `--delete` in the sync helper.

## 4. ATOMIC IMPLEMENTATION TASKS

1. Add `Dockerfile` using `python:3.12-slim`, installing the package from the current checkout, setting the console entrypoint to `tg-msg-manager`, and avoiding any CMD that starts a background service.
2. Add `compose.yaml` with one service `tg-msg-manager`, build from `.`, `working_dir: /root/TG_MSG_MANAGER`, `HOME=/root`, bind mount `${TGMM_STATE_DIR:-/opt/tg-msg-manager/state}:/root/TG_MSG_MANAGER`, `stdin_open: true`, `tty: true`, and `init: true`.
3. Add `.dockerignore` excluding local caches and sensitive artifacts, including `.git`, `.venv`, `__pycache__`, `.pytest_cache`, `.ruff_cache`, `*.session`, `*.db`, `*.sqlite`, `*.sqlite3`, `config.json`, `.env`, `exports`, `logs`, and `TG_MSG_MANAGER`, while keeping source, `pyproject.toml`, root docs, license, and build files available.
4. Add executable `deploy/vps/tgm` that resolves the repository root relative to itself and runs `docker compose run --rm tg-msg-manager "$@"`.
5. Add `deploy/vps/tg-shell.sh` for shell sourcing with `TGMM_ROOT="${TGMM_ROOT:-/opt/tg-msg-manager}"` and exact functions:

```sh
tg() {
  "$TGMM_ROOT/deploy/vps/tgm" "$@"
}

tgd() {
  "$TGMM_ROOT/deploy/vps/tgm" clean --apply --yes "$@"
}

tge() {
  "$TGMM_ROOT/deploy/vps/tgm" export --deep --json --user-id "$@"
}

tgh() {
  "$TGMM_ROOT/deploy/vps/tgm" target names "$@"
}

tgpm() {
  "$TGMM_ROOT/deploy/vps/tgm" export-pm --user-id "$@"
}

tgr() {
  "$TGMM_ROOT/deploy/vps/tgm" clean --dry-run --yes "$@"
}

tgu() {
  "$TGMM_ROOT/deploy/vps/tgm" update "$@"
}
```

6. Add executable `deploy/vps/install-shell.sh` that idempotently adds a `source /opt/tg-msg-manager/deploy/vps/tg-shell.sh` block to `~/.bashrc`, and to `~/.zshrc` only if it already exists, using explicit begin/end markers without overwriting dotfiles.
7. Add executable `deploy/local/tg-state-sync.sh` supporting `push --dry-run`, `push --apply`, `pull exports`, `pull logs`, and `pull all`, using rsync over SSH with `TGMM_SSH_HOST=${TGMM_SSH_HOST:-vps}`, `TGMM_LOCAL_STATE_DIR=${TGMM_LOCAL_STATE_DIR:-$HOME/TG_MSG_MANAGER}`, `TGMM_REMOTE_STATE_DIR=${TGMM_REMOTE_STATE_DIR:-/opt/tg-msg-manager/state}`, `--partial`, and `--info=progress2`.
8. Add `deploy/vps/README.md` in Russian with requirements, clone path, state directory creation, image build, shell hook installation, command examples, Mac state transfer examples, warning to stop the local app before push, warning not to publish secrets or add them to images/issues/PRs, and warning that `tgd` runs `clean --apply --yes`.
9. Create the factual stage report, then if complete perform lifecycle cleanup according to `AGENTS.md`.

## 5. REQUIRED DOCS

Required:

```text
deploy/vps/README.md
docs/stages/reports/STAGE_7B_0_VPS_DOCKER_COMPOSE_DEPLOYMENT_REPORT.md
docs/stages/README.md
```

Do not update `README.md` or `COMMANDS.md` unless implementation changes user-facing repository workflow beyond `deploy/vps/README.md`.

## 6. TESTS / VERIFICATION

Run and record:

```bash
docker build .
TGMM_STATE_DIR=$(mktemp -d) docker compose run --rm tg-msg-manager --help
sh -n deploy/vps/tgm
sh -n deploy/vps/tg-shell.sh
sh -n deploy/vps/install-shell.sh
sh -n deploy/local/tg-state-sync.sh
make verify
make pre-commit
```

If Docker is unavailable in the Codex environment, record the Docker checks as not run with the exact reason. Do not claim any check passed unless it was actually run.

## 7. REPORT

Write `docs/stages/reports/STAGE_7B_0_VPS_DOCKER_COMPOSE_DEPLOYMENT_REPORT.md` in Russian.

Include:

```text
scope summary
changed files
behavior preservation notes
secret/data exclusion notes
Docker/Compose check results
shell syntax check results
make verify result
make pre-commit result
blockers or caveats
stage-reviewer: applied from .skills/stage-reviewer/SKILL.md
architecture-guard: applied from .skills/architecture-guard/SKILL.md or not required with reason
```

## 8. COMPLETION CRITERIA

- Dockerfile, Compose file, Docker ignore rules, VPS wrappers, shell hook installer, local sync helper, and VPS README are implemented within scope.
- No application behavior, public CLI contract, SQLite schema, export formats, Telegram authorization, service logic, storage logic, or protected files changed.
- Sensitive artifacts and real data are excluded from the Docker image and repository.
- Required checks are run and recorded, or environment blockers are recorded honestly.
- Factual report exists in Russian.
- `docs/stages/README.md` is updated.
- lifecycle cleanup is completed according to AGENTS.md.
- PR exists for the branch.

## 9. OUTPUT LIMITS

Final response must follow `AGENTS.md` final format, be in Russian, and stay under 1200 characters.

Do not paste full diffs, large code blocks, long summaries, unrelated recommendations, or future-stage plans.
