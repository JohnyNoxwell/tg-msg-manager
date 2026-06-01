# Static Dataset Summary Report Design

## Status

Docs-only design for a future external derived artifact.

No report generator, CLI command, service, exporter hook, validator hook, doctor
hook, SQLite persistence, runtime package, or dataset contract change exists in
this stage.

## Boundary

The static dataset summary report is downstream of this pipeline:

```text
export -> validate/inspect -> dataset doctor -> post-processing -> optional LLM report
```

The report reads a completed direct channel export dataset plus validation,
inspection, and doctor outputs. It writes a separate derived artifact outside
the source dataset contract.

The report is not part of Dataset Contract V1 unless a later explicit stage
changes that contract.

## Intended Artifact

Future implementations may render the same summary model as static HTML,
Markdown, or JSON. Static HTML is the primary target for this design because it
can be reviewed locally without a service process.

The artifact should identify its source and generation context so it can be
reviewed without mutating the dataset.

## Required Fields

- `source_dataset_path`: local path that was read.
- `source_manifest_schema_version`: manifest `schema_version` from the source
  dataset.
- `generated_at`: report generation timestamp.
- `deterministic`: whether the report was produced only from deterministic
  local inputs.
- `external_service_used`: whether any external service was used.
- `llm_used`: whether any LLM was used.
- `message_count`: count from inspection or manifest comparison.
- `date_range`: earliest and latest exported message timestamps when available.
- `media_count`: media record count.
- `media_status_summary`: counts by media status from `media_manifest.jsonl` or
  inspection output.
- `discussion_coverage_summary`: discussion mode, metadata/comment/thread
  counts, failed thread count when available, and whether discussion artifacts
  are present.
- `validation_status`: `ok`, `warnings`, or `errors` from validation output.
- `doctor_findings_summary`: doctor status plus error/warning counts and finding
  codes.
- `artifact_list`: source and derived artifact paths included in the summary.
- `privacy_checklist`: local review flags before sharing derived artifacts.

## Privacy Checklist

A future report should make these review points explicit:

- source dataset path is local and may reveal workspace structure;
- message text, channel metadata, author fields, media metadata, and discussion
  records may be sensitive;
- private exports, sessions, credentials, SQLite databases, logs, screenshots,
  and real media must not be embedded unless separately approved;
- redaction status should be recorded before sharing;
- external service and LLM usage flags must be visible.

## Non-Goals

This design does not authorize:

- runtime implementation;
- a CLI command;
- exporter, validator, or doctor integration;
- SQLite persistence;
- mutation of source datasets;
- Dataset Contract V1 changes;
- Telegram network access;
- real report generation from real datasets in docs;
- analytics, OSINT interpretation, profiling, identity claims, fingerprinting,
  sentiment or narrative classification;
- OCR, STT, media recognition, transcoding, or media analysis;
- LLM-dependent core behavior.

## Relationship To Post-Processing Boundary

This report is an example of future external post-processing. It may read
Dataset Contract V1 artifacts and validation, inspection, and doctor outputs. It
must keep outputs separate from the source dataset and must not imply exporter
core permissions.
