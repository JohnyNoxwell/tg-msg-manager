# Foundation Backlog

Этот backlog является исполнимой очередью для foundation-first развития проекта.

## Active stages

1. `stagt_0.md` — Foundation Stabilization
2. `stagt_1.md` — Export Pipeline Refactor
3. `stagt_2.md` — Context Pipeline Refactor
4. `stagt_3.md` — Retry Reliability Layer
5. `stagt_4.md` — Audit / Report Read-Side
6. `stagt_5.md` — Fixture And E2E Hardening

Progress rule:
- execution progress is tracked inline in active `stagt_*.md` files;
- shipped batches are summarized in `CHANGELOG.md`.

## What counts as foundation

- стабилизация runtime contracts и regression invariants;
- декомпозиция `ExportService` и `DeepModeEngine`;
- ограниченный и typed `retry`;
- read-only operational reporting;
- fixture-based e2e coverage без сети.

## Out of foundation

Следующие направления не входят в активную foundation-очередь:
- аналитический слой;
- keyword/topic extraction;
- graph analytics/export;
- advanced user-facing context quality reporting.

Эти направления перенесены в post-foundation roadmap.

## Legacy drafts

Старые черновики поздних этапов сохранены в `backlog/archive/`:
- `stagt_6_legacy.md`
- `stagt_7_legacy.md`
- `stagt_8_legacy.md`

Они не считаются активными этапами исполнения.
