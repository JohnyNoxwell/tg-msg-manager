# Documentation Index

## 1. How to use this documentation

Start from the smallest relevant set of docs.

1. Read [`../AGENTS.md`](../AGENTS.md) first.
2. Read the active task file, usually under [`stages/active/`](stages/active/).
3. Read only the architecture or development docs referenced by that task.
4. Use reports as factual history, not current instructions.
5. Do not read archive material unless explicitly asked.

## 2. For coding agents

This repository is a Telegram history data pipeline with strict architecture boundaries. Documentation is part of the implementation: if behavior, commands, file formats, architecture boundaries, workflow, testing, or known limitations change, the matching docs must change in the same work.

Do not use roadmap or archive files as permission to implement features. Implementation requires an explicit active task.

## 3. Architecture docs

Use [`architecture/README.md`](architecture/README.md) for current architecture guidance, protected boundaries, storage/model decisions, and split maps. Channel dataset validation / inspection is documented in [`architecture/DATASET_VALIDATION.md`](architecture/DATASET_VALIDATION.md), and external post-processing boundaries are documented in [`architecture/POST_PROCESSING_BOUNDARY.md`](architecture/POST_PROCESSING_BOUNDARY.md).

## 4. Development docs

Use [`development/README.md`](development/README.md) for CLI contracts, testing guidance, PR checks, and development guardrails.

## 5. Stages

Use [`stages/README.md`](stages/README.md) for active tasks, completed historical task files, and factual stage reports.

Only files under [`stages/active/`](stages/active/) are executable current stage tasks.

## 6. Roadmap

Use [`roadmap/README.md`](roadmap/README.md) for roadmap navigation. Roadmap entries are not implementation permission.

## 7. Archive

Use [`archive/README.md`](archive/README.md) for archived notes, old prompts, and deprecated stage files.

Archive content is not current guidance unless the user explicitly asks to use it.

## 8. Rule: do not read everything by default

Do not load the whole docs tree by default. Select docs by relevance:

- architecture change: read `AGENTS.md`, active task, and `docs/architecture/README.md`;
- CLI or workflow change: read `AGENTS.md`, active task, and `docs/development/README.md`;
- stage work: read `AGENTS.md`, the active stage file, and referenced reports;
- roadmap discussion: read `docs/roadmap/README.md`;
- historical investigation: read the relevant report or archive file only.
