# Release Checklist Scope

Status: no-publish checklist boundary.

This document defines what the Stage 5K release checklist may inspect. It does
not authorize an actual release.

## Forbidden In 5K

- Version bumps.
- Git tag creation.
- Package build artifacts.
- Package upload or publish.
- Runtime `__version__` API additions.
- `pyproject.toml` metadata changes.
- CLI behavior, output format, SQLite schema, storage, service, fixture, or
  runtime changes.
- Live Telegram checks that require credentials, sessions, private exports, or
  real Telegram data.

## Allowed Checklist Actions

- Inspect release-facing docs and package metadata.
- Audit package identity, console script mapping, and version-source docs.
- Audit privacy and sensitive-artifact boundaries.
- Audit changelog and known limitations against completed reports.
- Run safe offline local checks requested by active stage files.
- Record blockers, gaps, skipped checks, and evidence in Russian stage reports.

## Safe Local Checks

The active stage file decides the required command set. Safe offline commands
may include:

```bash
git diff --check
make lint
make format-check
make test
make verify
python3 -m unittest discover tests -p '*non_channel*contract*.py'
```

Do not run package publish/upload commands. Do not run a package build unless a
future active stage explicitly scopes a local dry-run build.

## Optional / Manual Checks

Manual live Telegram smoke checks require explicit future scope, credentials,
and privacy-safe reporting. They are never required for the offline 5K release
checklist.

## Evidence Needed Before A Future Actual Release Stage

- Completed 5K reports for scope, packaging metadata, docs/privacy/changelog,
  local verification, and release-candidate decision.
- Exact check commands and results.
- Explicit confirmation that version, tags, release artifacts, publish/upload,
  CLI behavior, SQLite schema, output formats, and private artifact boundaries
  stayed unchanged during 5K.
- A separate active release/version stage if an actual release is later desired.
