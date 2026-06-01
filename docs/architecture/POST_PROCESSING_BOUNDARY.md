# Post-Processing Boundary

## Purpose

Post-processing is a separate layer after dataset export, validation, inspection, and doctor reporting.

Allowed pipeline:

```text
export -> validate/inspect -> dataset doctor -> post-processing -> optional LLM report
```

Exporter core must remain a dataset producer. It must not embed post-processing, analytics, OSINT interpretation, profiling, fingerprinting, OCR, STT, media recognition, or LLM-dependent behavior.

## Input Boundary

Post-processing may read exported datasets that conform to:

- [`DATASET_CONTRACT_V1.md`](DATASET_CONTRACT_V1.md)
- [`DATASET_VALIDATION.md`](DATASET_VALIDATION.md)

Post-processing may also read validation, inspection, and doctor reports as inputs.

Post-processing must not require Telegram network access through exporter services. If a future tool needs network enrichment, it must live outside exporter core and must document that boundary explicitly.

## Mutation Boundary

By default, post-processing must not mutate source datasets.

Forbidden by default:

- editing `manifest.json`;
- editing `messages.jsonl`;
- editing `messages.txt`;
- editing `media_manifest.jsonl`;
- editing `channel_export_state.json`;
- editing discussion payload/state files;
- moving or rewriting media files;
- changing SQLite schema or writing post-processing results into exporter storage.

If a future repair tool is explicitly scoped, it must use a separate stage and must not be presented as post-processing analysis.

## Output Boundary

Post-processing outputs must be separate artifacts outside the source dataset contract, or in a clearly separate output directory.

Allowed examples for future stages:

```text
POST_PROCESSING/<dataset_slug>/
reports/<dataset_slug>/
derived/<dataset_slug>/
```

Output artifacts must identify:

- source dataset path;
- source manifest schema version;
- tool name and version if available;
- generated time;
- whether the output is deterministic;
- whether external services or LLMs were used.

Generated post-processing artifacts are not part of `direct_channel_export` Dataset Contract V1 unless a future explicit stage changes the contract.

## Allowed Future Categories

The following categories are allowed as future external post-processing examples only. They are not exporter-core permissions, not current CLI commands, and not implementation scope by themselves.

- Markdown summary: a readable derived summary of dataset metadata, validation status, artifact list, and high-level counts.
- JSON summary: a machine-readable derived summary with source dataset path, manifest schema version, generated time, deterministic flag, and count/status fields.
- Static HTML report: a standalone derived report artifact that reads exported dataset facts and validation/doctor results, without mutating the dataset; see [`STATIC_DATASET_SUMMARY_REPORT_DESIGN.md`](STATIC_DATASET_SUMMARY_REPORT_DESIGN.md).
- LLM prompt pack outside exporter core: optional downstream prompt files prepared from already exported and user-approved dataset summaries.
- Timeline summary: a deterministic chronological summary of exported message timestamps and counts, without interpreting intent, sentiment, or identity.
- Media status summary: a derived count/status view over `media_manifest.jsonl`, without OCR, STT, media recognition, transcoding, or media analysis.
- Discussion coverage summary: a derived count/status view over discussion metadata/comments/threads, without social graph analysis or user profiling.
- Redaction checklist: a local checklist for reviewing sensitive fields before sharing derived artifacts.

These examples may read exported datasets and validation, inspection, or doctor outputs. They must write separate derived artifacts and must not mutate source datasets by default.

Any work that interprets people, identities, intent, influence, fraud, fundraising, narratives, sentiment, bot status, or behavioral patterns remains outside exporter core and outside validation/doctor layers. It also requires a separate explicit stage before any implementation.

## Forbidden In Exporter Core

Do not add these to channel export, DB export, context engine, private archive, storage write paths, validation, or doctor services:

- analytics implementation;
- OSINT interpretation;
- profiling;
- fingerprinting;
- identity claims;
- sentiment analysis;
- narrative classification;
- OCR;
- STT;
- media recognition;
- LLM-dependent behavior;
- new persistence for derived analysis.

## Skeleton Decision

This stage intentionally creates documentation only.

No `post_processing/` Python package is created because an empty package would imply implementation readiness. Future stages may add a package or examples directory only with explicit scoped tasks and tests.
