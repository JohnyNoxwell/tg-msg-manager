# Stage 3D.0.5 - AGENTS.md Rewrite Report

## 1. Summary

`AGENTS.md` was rewritten as a concise repository-level agent contract.

No runtime code was changed. No product feature was added. No SQLite schema change was made.

## 2. AGENTS.md structure

The rewritten file uses the required sections:

- mandatory first step;
- project identity;
- non-negotiable architecture rules;
- protected files and boundaries;
- documentation map;
- relevant-doc selection policy;
- stage workflow;
- coding rules;
- testing policy;
- documentation policy;
- forbidden behavior;
- stop-and-report conditions;
- final response expectations.

## 3. Rules added

The contract now explicitly states:

- read `AGENTS.md` first;
- identify and read the active task file;
- do not read the whole docs tree by default;
- do not use archive as current guidance unless explicitly asked;
- documentation is part of implementation;
- a stage is incomplete while required docs are stale or missing;
- roadmap items are not implementation permission.

## 4. Documentation map added

The file points agents to:

- `docs/README.md`
- `docs/architecture/`
- `docs/development/`
- `docs/stages/active/`
- `docs/stages/completed/`
- `docs/stages/reports/`
- `docs/roadmap/`
- `docs/archive/`

## 5. Context-size policy

The contract directs agents to read only relevant task-linked docs and not to load completed stage files, all reports, or archive files by default.

## 6. Protected boundaries

The protected service facades and compatibility wrappers are listed explicitly. `ChannelExportService` is included as an orchestration-only protected facade.

## 7. Remaining alignment work

Stage 3D.0.6 must still align root `README.md`, `COMMANDS.md`, and `CHANGELOG.md` with the new docs paths.

Stage 3D.0.7 must still run final verification and create the final governance report.
