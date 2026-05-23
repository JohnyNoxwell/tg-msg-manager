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

The following categories are allowed as future post-processing work only. They are not exporter-core permissions.

- dataset loaders;
- deterministic transforms;
- report schemas;
- LLM prompt templates outside exporter;
- stylometry/fingerprint modules outside exporter;
- fraud/fundraising detectors outside exporter.

Any category that interprets people, identities, intent, influence, fraud, fundraising, narratives, sentiment, bot status, or behavioral patterns must remain outside exporter core and outside validation/doctor layers.

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
