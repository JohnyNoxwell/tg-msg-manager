# Deferred Contract Coverage Prioritization

Status: prioritized docs plan.

This document ranks deferred contract coverage gaps for user/group `export`,
`db-export`, and separate private archive work. It does not implement tests,
fixtures, runtime behavior, CLI behavior, output format changes, or SQLite
schema changes.

`export-pm` remains outside Non-Channel Export Contract V1.

## Recommended Order

1. Generated-output filenames.
2. `_partN` part-file paths.
3. DB-backed no-new-work / skip behavior.
4. Rotation threshold decision.
5. `.export_state` legacy fallback decision.
6. Private archive / `export-pm` contract precheck.
7. Full raw JSON profile decision.
8. Real Telegram smoke checklist separation.
9. SQLite schema public-contract decision.

## Ranked Coverage Matrix

### 1. Generated-output filenames

- Risk: medium.
- User-facing impact: high; users see and reuse `DB_EXPORTS/<safe_name>_<id>`.
- Regression likelihood: medium; naming depends on author resolution and safe-name normalization.
- Test feasibility: high; current component tests already check deterministic examples.
- Fixture needs: small synthetic user/name cases.
- Runtime-change needs: none expected.
- Private-data needs: none.
- Stage size: small.
- Recommended order: 1.

### 2. `_partN` part-file paths

- Risk: medium.
- User-facing impact: high for large exports and resumed artifact handling.
- Regression likelihood: medium; paths depend on `FileRotateWriter` and artifact existence checks.
- Test feasibility: high; existing tests cover multipart skip behavior with temp files.
- Fixture needs: generated-output temp fixture, not checked-in large files.
- Runtime-change needs: none expected.
- Private-data needs: none.
- Stage size: small to medium.
- Recommended order: 2.

### 3. DB-backed no-new-work / skip behavior

- Risk: high.
- User-facing impact: high; avoids unnecessary rewrites and preserves existing artifacts.
- Regression likelihood: medium to high; depends on export target DB state, fingerprints, part counts, and artifact paths.
- Test feasibility: high with temporary SQLite/mock storage and synthetic messages.
- Fixture needs: synthetic DB state or temp DB setup; no real DB contents.
- Runtime-change needs: none expected for contract tests.
- Private-data needs: none.
- Stage size: medium.
- Recommended order: 3.

### 4. Rotation thresholds

- Risk: medium.
- User-facing impact: medium; threshold controls when `_partN` appears.
- Regression likelihood: medium; current default is implementation detail in `FileRotateWriter`.
- Test feasibility: medium; should first decide whether exact threshold is public contract or only behavior guarded by smaller injected limits.
- Fixture needs: temp generated outputs; avoid checked-in huge files.
- Runtime-change needs: none for decision/tests if injection is already available.
- Private-data needs: none.
- Stage size: small decision or medium test stage.
- Recommended order: 4.

### 5. `.export_state` legacy fallback

- Risk: low to medium.
- User-facing impact: low for normal current output; it is legacy fallback only.
- Regression likelihood: low; current tests assert normal path does not write it and fallback can backfill DB state.
- Test feasibility: high.
- Fixture needs: small synthetic legacy manifest fixture if promoted.
- Runtime-change needs: none expected.
- Private-data needs: none.
- Stage size: small.
- Recommended order: 5.

### 6. Private archive / `export-pm` contract

- Risk: high.
- User-facing impact: high because `export-pm` is a visible command.
- Regression likelihood: medium to high; output combines text log, media folders, SQLite side effects, sync state, and retry behavior.
- Test feasibility: medium; needs synthetic private-archive fixtures and careful privacy boundaries.
- Fixture needs: new private archive synthetic fixtures; no real private dialogs.
- Runtime-change needs: none for precheck, possible later for contract seams.
- Private-data needs: none; real private artifacts must not be read.
- Stage size: large if contract implementation, medium for precheck.
- Recommended order: 6.

### 7. Full raw JSON profile

- Risk: medium.
- User-facing impact: low until explicitly exposed as a public CLI profile.
- Regression likelihood: medium if promoted because raw payload shape follows Telethon data.
- Test feasibility: medium with small synthetic payloads.
- Fixture needs: synthetic raw payload fixtures.
- Runtime-change needs: maybe, if CLI/docs expose a full profile.
- Private-data needs: none.
- Stage size: medium.
- Recommended order: 7.

### 8. Real Telegram smoke checks

- Risk: medium.
- User-facing impact: medium for release confidence, not artifact contract.
- Regression likelihood: not deterministic.
- Test feasibility: low for automation; manual/session-dependent only.
- Fixture needs: none; do not turn real data into fixtures.
- Runtime-change needs: none.
- Private-data needs: credentials/session required for live run, but reports must not expose private contents.
- Stage size: small checklist/doc stage.
- Recommended order: 8.

### 9. SQLite schema as public contract

- Risk: high.
- User-facing impact: low for external users; high blast radius for maintainers.
- Regression likelihood: high if treated as public API.
- Test feasibility: medium, but it would freeze internals.
- Fixture needs: schema inspection fixtures or tests only if explicitly scoped.
- Runtime-change needs: none for decision; possible high cost if promoted.
- Private-data needs: none.
- Stage size: medium decision stage or large contract stage.
- Recommended order: 9; keep non-public unless a future stage explicitly scopes it.

## Notes

- Current focused Non-Channel Export Contract V1 coverage should remain limited
  to user/group `export` and `db-export`.
- Generated-output contract stages should use temporary directories and
  synthetic messages rather than checked-in large artifacts.
- Private archive work should begin with a separate precheck before any contract
  is created.
