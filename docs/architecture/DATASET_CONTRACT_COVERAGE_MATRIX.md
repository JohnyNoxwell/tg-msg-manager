# Dataset Contract Coverage Matrix

This matrix maps Dataset Contract V1 requirements to current docs, tests, fixtures, and known gaps. It is factual coverage inventory only; it does not redefine dataset behavior.

Coverage source labels:

- `contract doc`: `docs/architecture/DATASET_CONTRACT_V1.md`
- `format doc`: `docs/architecture/DATASET_FORMAT.md`
- `validation doc`: `docs/architecture/DATASET_VALIDATION.md`
- `export contract test`: `tests/services/channel_export/test_channel_export_dataset_contracts.py`
- `service test`: `tests/services/channel_export/test_channel_export_service.py`
- `validator test`: `tests/services/dataset_validation/test_dataset_validation_contracts.py`
- `fixture`: `tests/fixtures/dataset_validation/`

| Contract area | Expected status | Current coverage | Gap or next stage |
| --- | --- | --- | --- |
| Contract scope: `direct_channel_export`, schema `1.0`, filesystem-first channel dataset | REQUIRED | contract doc; format doc | No runtime behavior proof in this matrix. |
| Status labels: `REQUIRED`, `OPTIONAL`, `CONDITIONAL`, `NOT_EXPECTED`, `LEGACY_COMPAT`, `UNKNOWN_NEEDS_CHECK` | REQUIRED documentation labels | contract doc | Docs-only labels; no runtime enum expected. |
| Dataset root `exports/channels/<channel_slug>/` | REQUIRED for default channel export | contract doc; format doc | Slug construction is documented but not proven by inspected tests. |
| `manifest.json` top-level keys and discussion/export sections | REQUIRED | contract doc; format doc; export contract test `test_manifest_contract_without_and_with_discussion`; fixture `valid_minimal_channel_dataset`, `valid_discussion_dataset` | Exact manifest subkey coverage is partial; matrix found no full golden fixture assertion for every manifest field. |
| `messages.jsonl` exact channel post keys | CONDITIONAL; current CLI default writes it | contract doc; format doc; export contract test `test_messages_jsonl_contract_has_exact_keys_and_types`; fixtures | Covered for key shape and representative nullable text. |
| Nested `messages.jsonl` media keys | CONDITIONAL with message media | contract doc; format doc; export contract test `test_messages_jsonl_contract_has_exact_keys_and_types`; validator media relationship tests | Covered for key shape and relationship checks. |
| `messages.txt` projection | CONDITIONAL; current CLI default writes it | contract doc; format doc; export contract test `test_txt_projection_smoke_contracts`; fixtures | Clarified by Stage 5D.3: smoke marker coverage is the intended TXT projection contract; no full golden snapshot is required. |
| `media_manifest.jsonl` exact keys | REQUIRED | contract doc; format doc; export contract test `test_media_manifest_jsonl_contract_has_exact_keys_and_final_statuses`; fixtures | Covered for key shape. |
| Media statuses: `metadata_only`, `downloaded`, `already_exists`, `skipped_by_size`, `skipped_by_type`, `failed`; no committed `pending` | REQUIRED status set | contract doc; format doc; export contract test; validator media status tests | Validator has relationship coverage for several statuses; exact final status set is covered in export contract test. |
| `media/` directory and media path boundaries | CONDITIONAL for `--media full` | contract doc; format doc; validator tests `test_downloaded_media_with_existing_file_is_ok`, `test_media_path_traversal_is_error`, `test_skipped_media_does_not_require_file` | Current required tests do not prove every documented media subdirectory. |
| `channel_export_state.json` exact keys and schema `1.0` | REQUIRED | contract doc; format doc; export contract test `test_state_file_contracts_have_exact_keys`; fixtures | Covered for key shape and completed status. |
| `run_changelog.jsonl` required artifact and no-new-posts audit role | REQUIRED | contract doc; format doc; export contract tests `test_run_changelog_writer_contract_has_exact_keys_and_artifact_paths`, `test_run_changelog_fixture_rows_match_contract_keys`; validator test `test_missing_run_changelog_reports_contract_error`; fixtures | Covered for exact top-level keys, exact `artifact_paths` keys, fixture rows, and no message text field. |
| `discussion_metadata.jsonl` exact keys | CONDITIONAL for `--discussion metadata` | contract doc; format doc; export contract test `test_discussion_metadata_jsonl_contract_has_exact_keys`; validator test `test_discussion_metadata_mode_requires_metadata_file` | No static metadata fixture in `tests/fixtures/dataset_validation/`; validator test builds one dynamically. |
| `discussion_comments.jsonl` exact keys | CONDITIONAL for `--discussion full` | contract doc; format doc; export contract test `test_discussion_comments_jsonl_contract_has_exact_keys`; fixture `valid_discussion_dataset`; validator discussion tests | Covered for key shape and relationship checks. |
| `discussion_comments.txt` projection | CONDITIONAL for `--discussion full` | contract doc; format doc; export contract test `test_txt_projection_smoke_contracts`; fixture `valid_discussion_dataset` | Clarified by Stage 5D.3: smoke marker coverage is the intended TXT projection contract; no full golden snapshot is required. |
| `discussion_threads.jsonl` exact keys and statuses | CONDITIONAL for `--discussion full` | contract doc; format doc; export contract test `test_discussion_threads_jsonl_contract_has_exact_keys_and_statuses`; fixture `valid_discussion_dataset`; validator discussion tests | Covered for key shape and allowed statuses. |
| `discussion_export_state.json` exact keys and schema `1.0` | CONDITIONAL for `--discussion full` | contract doc; format doc; export contract test `test_state_file_contracts_have_exact_keys`; fixture `valid_discussion_dataset` | Covered for key shape and completed status. |
| Media mode matrix: `none`, `metadata`, `full` | REQUIRED behavior matrix | contract doc; format doc; export contract test covers metadata/full manifest shape; included-files builder test covers `none`; service tests cover no download calls for `none` and `metadata`, full download, skip, existing, failed outcomes | Closed by Stage 5D.4 for compact mode coverage. |
| Discussion mode matrix: `none`, `metadata`, `full` | REQUIRED behavior matrix | contract doc; format doc; included-files builder matrix test covers mode-specific included files; service tests cover none, metadata, full, incremental, force, no-new-posts discussion behavior; validator tests cover missing mode-specific files | Closed by Stage 5D.4 for included-file matrix coverage. |
| Run modes: full, force full, incremental, no-new-posts | REQUIRED behavior matrix | contract doc; format doc; service tests cover full write, force overwrite, incremental append, no-new-posts state preservation, changelog append facts, and compact run-mode matrix assertions | Closed by Stage 5D.4 for compact contract-level run-mode coverage. |
| `include_jsonl` / `include_txt` service options | CONDITIONAL service options; current CLI defaults true | contract doc; included-files builder tests cover manifest omission; service tests cover disabled payload file absence | Closed by Stage 5D.4; payload writer now opens only enabled payload files. |
| Partial failure contract: payload/manifest/state ordering, per-thread failures, media failure rows, non-ACID media files | REQUIRED failure contract | contract doc; validator tests cover failed media records as warnings and partial discussion fixture errors | Export failure ordering is not proven by inspected contract/validator tests. |
| Validation command statuses: `ok`, `warnings`, `errors` | REQUIRED validation contract | validation doc; validator tests for valid fixtures, warnings, and errors | Covered for representative findings. |
| Validation read-only boundary | REQUIRED | validation doc; validator tests `test_validate_and_inspect_dataset_are_read_only`, `test_doctor_is_read_only`, CLI no-client tests | Covered for local filesystem snapshots and CLI no-client boundary. |
| Validation relationship checks: messages, replies, media, discussion links, mode-specific files | REQUIRED validation concerns | validation doc; validator message/media/discussion relationship tests; fixtures | Covered for representative deterministic relationships, not exhaustive historical drift. |
| Doctor boundary and deterministic renderers | REQUIRED read-only diagnostic layer | validation doc; validator tests in `TestDatasetDoctor` | Covered for representative healthy/error outputs and read-only behavior. |
| Non-channel dataset families: group/user `export`, `db-export`, `export-pm` | UNKNOWN_NEEDS_CHECK for Dataset Contract V1 | contract doc | Explicit gap; future stages may define separate contracts from existing behavior and tests. |

## Fixture Coverage

| Fixture | Coverage role | Gap or next stage |
| --- | --- | --- |
| `valid_minimal_channel_dataset` | Minimal valid channel dataset with base files and `run_changelog.jsonl`. | Does not cover discussion or downloaded media file. |
| `valid_discussion_dataset` | Full discussion files, discussion state, comments, threads, and base files. | Does not cover metadata-only discussion fixture. |
| `partial_discussion_dataset` | Invalid/partial discussion artifact relationships. | Used for validator error coverage. |
| `invalid_bad_jsonl` | Invalid JSONL line-number reporting. | Narrow JSONL parse failure fixture. |
| `invalid_duplicate_messages` | Duplicate message id error. | Narrow message-id fixture. |
| `invalid_missing_media_file` | Missing downloaded media file error. | Narrow media path fixture. |

## Current Gap Closure Plan

Execution order:

1. Stage 5D.2: exact `run_changelog.jsonl` key set contract tests. Completed.
2. Stage 5D.3: TXT projection contract clarification. Completed.
3. Stage 5D.4: channel export mode matrix tests for media/run/include options. Completed.
4. Stage 5D.5: safe first export guide.

Final classification:

- Exact `run_changelog.jsonl` key set was `test-only`; closed by Stage 5D.2.
- TXT projection coverage was `docs-only`; closed by Stage 5D.3. Current contract intentionally promises stable smoke assertions, not full golden snapshots.
- `--media none` was `test-only`; closed by Stage 5D.4.
- Full, force, incremental, and no-new-posts compact contract-level coverage was `test-only`; closed by Stage 5D.4.
- `include_jsonl=False` and `include_txt=False` were `behavior-mismatch` candidates; closed by Stage 5D.4 with focused `payload_writer` behavior fix and service tests.
- Non-channel dataset families are `out-of-scope` for Dataset Contract V1.
