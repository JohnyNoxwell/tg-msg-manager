# Stage 3E.0 - Channel Export Service Decomposition Report

## 1. Summary

Stage 3E.0 decomposed `ChannelExportService` construction responsibilities into focused channel export modules without changing public behavior.

Completed:

- moved included-file list construction to `included_files_builder.py`;
- moved manifest construction coordination to `manifest_coordinator.py`;
- moved `ChannelExportResult` construction to `result_builder.py`;
- kept completion event emission explicit in `ChannelExportService`;
- added focused unit tests for the extracted helpers;
- updated architecture and facade guardrail docs;
- preserved channel export integration behavior.

## 2. Refactor scope

This was a refactor-only stage. The protected file change in `tg_msg_manager/services/channel_export/service.py` was mechanical delegation:

- replaced private `_included_files` logic with `build_included_files`;
- replaced private `_build_manifest` logic with `build_channel_export_manifest`;
- replaced private `_build_result` logic with `build_channel_export_result`;
- retained state save order, manifest write order, discussion state save order, and event emission order.

## 3. Modules added

Added:

```text
tg_msg_manager/services/channel_export/included_files_builder.py
tg_msg_manager/services/channel_export/manifest_coordinator.py
tg_msg_manager/services/channel_export/result_builder.py
```

Added tests:

```text
tests/test_channel_export_included_files_builder.py
tests/test_channel_export_manifest_coordinator.py
tests/test_channel_export_result_builder.py
```

## 4. ChannelExportService responsibilities after refactor

`ChannelExportService` remains the public orchestration facade. It now primarily:

- normalizes media and discussion options;
- resolves the source channel;
- builds the export plan;
- loads and validates state;
- selects full, force, incremental, or no-new-posts paths;
- delegates payload writing, media preparation, discussion export, manifest construction, and result construction;
- writes the manifest and saves state in the established order;
- emits high-level lifecycle events.

No-new-posts handling was not extracted in this stage. The branch is small and tightly couples manifest refresh, no-new-posts event emission, unchanged-state result assembly, and completion event emission. Extracting it would have increased call-surface complexity without reducing behavior risk.

## 5. Behavior preserved

Preserved:

- `export-channel` CLI options and defaults;
- dataset filenames and included-file ordering;
- manifest fields and discussion manifest block;
- `ChannelExportResult` fields;
- media metadata/full behavior;
- discussion none/full behavior;
- incremental, force, and no-new-posts behavior;
- state save ordering and manifest failure safety;
- no-new-posts discussion resolver/exporter inert behavior.

## 6. Tests added/updated

Added focused tests for:

- metadata included-files ordering;
- full-media included-files behavior;
- `include_jsonl=False`;
- `include_txt=False`;
- no discussion result;
- discussion result included files;
- manifest coordination with no discussion;
- manifest coordination with full discussion;
- media metadata manifest options;
- full media manifest limits/type options;
- result builder fields with and without discussion.

Existing integration tests were preserved.

## 7. Verification results

Baseline before refactor:

| Command | Result |
| --- | --- |
| `pytest tests/test_channel_export_*.py` | passed, 144 tests |

Focused post-refactor check:

| Command | Result |
| --- | --- |
| `pytest tests/test_channel_export_included_files_builder.py tests/test_channel_export_manifest_coordinator.py tests/test_channel_export_result_builder.py tests/test_channel_export_service.py tests/test_channel_export_manifest.py` | passed, 37 tests |
| `python3 -m compileall tg_msg_manager/services/channel_export` | passed |

Required Stage 3E.0 verification:

| Command | Result |
| --- | --- |
| `pytest tests/test_channel_export_*.py` | passed, 156 tests |
| `python3 -m compileall tg_msg_manager` | passed |
| `ruff check tg_msg_manager tests` | passed |
| `ruff format --check tg_msg_manager tests` | passed, 246 files already formatted |
| `python3 -m tg_msg_manager.cli export-channel --help` | passed |

`make test` and `make verify` were not run during this stage because the required verification passed and the stage-specific scope was channel export only.

## 8. Runtime behavior statement

No public CLI behavior changed.
No dataset schema changed.
No state schema changed.
No SQLite schema changed.
No product feature was added.

## 9. Remaining risks

- `ChannelExportService` still owns full/incremental/no-new-posts branching. This is intentional for Stage 3E.0 to keep the refactor behavior-preserving.
- Pre-existing unrelated worktree changes remain outside the Stage 3E.0 scope.

## 10. Status

Stage 3E.0: complete.
