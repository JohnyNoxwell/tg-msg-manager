# STAGE 5A.0 — EXTERNAL POST-PROCESSING BOUNDARY SKELETON

Status: active task
Stage: 5A.0
Type: architecture / extension skeleton
Depends on: Dataset Contract V1 and validation/doctor boundary

---

## 0. CODEX ENTRY CONTRACT

```text
Read AGENTS.md first.

Execute Stage 5A.0 — External Post-Processing Boundary Skeleton.

Goal:
Create a minimal external post-processing boundary skeleton without adding analytics to exporter core.

Do not add analytics implementation.
Do not add LLM logic.
Do not modify exporter behavior.
Do not modify dataset formats.
Do not add runtime dependencies unless explicitly required and justified.

Use AGENTS.md compact output format.
```

---

## 1. PURPOSE

This stage prepares future expansion without polluting exporter core.

It should define where future post-processing modules may live and how they may read exported datasets.

It must not implement OSINT, profiling, fingerprinting, OCR, STT, media recognition, or LLM reporting.

---

## 2. FILES TO INSPECT

Required:

```text
AGENTS.md
docs/architecture/DATASET_CONTRACT_V1.md
docs/architecture/
README.md
COMMANDS.md
pyproject.toml
```

Optional only if needed:

```text
tg_msg_manager/services/dataset_validation/
```

Do not inspect:

```text
exporter runtime modules unless needed to verify boundary references
docs/archive
unrelated stages
```

---

## 3. HARD PROHIBITIONS

Do not add:

```text
analytics implementation
OSINT interpretation
profiling
fingerprinting
identity claims
sentiment analysis
narrative classification
OCR
STT
media recognition
LLM-dependent behavior
new exporter features
new dataset formats
new SQLite schema
new persistence
```

Do not change:

```text
export behavior
validate/inspect behavior
doctor behavior
CLI command names
dataset output files
```

---

## 4. ATOMIC TASKS

### 4.1 Define boundary document

Create:

```text
docs/architecture/POST_PROCESSING_BOUNDARY.md
```

It must define:

```text
post-processing reads exported datasets
post-processing must not be embedded in exporter core
post-processing may depend on DATASET_CONTRACT_V1
post-processing outputs must be separate artifacts
post-processing must not mutate source datasets by default
```

### 4.2 Create optional skeleton location only if useful

If the repo should contain a placeholder package/directory, create minimal docs-only or empty-safe structure.

Allowed:

```text
post_processing/README.md
```

or:

```text
examples/post_processing/README.md
```

Prefer docs-only if code skeleton would imply implementation.

### 4.3 Document allowed future categories

Allowed future categories as documentation only:

```text
dataset loaders
deterministic transforms
report schemas
LLM prompt templates outside exporter
stylometry/fingerprint modules outside exporter
fraud/fundraising detectors outside exporter
```

Each must be clearly labeled future/post-processing, not exporter core.

### 4.4 Update AGENTS.md only if needed

If AGENTS.md already has sufficient boundary rules, do not update it.

If update is needed, add only a short pointer to `POST_PROCESSING_BOUNDARY.md`.

### 4.5 Update docs index

Update:

```text
docs/README.md
```

only if needed to index the new boundary doc.

---

## 5. REQUIRED DOCS

Required:

```text
docs/architecture/POST_PROCESSING_BOUNDARY.md
docs/stages/reports/STAGE_5A_0_EXTERNAL_POST_PROCESSING_BOUNDARY_SKELETON_REPORT.md
```

Conditional:

```text
docs/README.md if new architecture doc must be indexed
AGENTS.md only if existing boundary rules are insufficient
README.md only if project positioning needs a short boundary clarification
```

Do not create implementation docs for features not implemented.

---

## 6. TESTS / VERIFICATION

Docs/skeleton stage.

Run:

```bash
python3 -m compileall tg_msg_manager
ruff check tg_msg_manager tests
```

If a code skeleton is added, run relevant import/compile checks.

Do not claim checks passed unless actually run.

---

## 7. REPORT

Create:

```text
docs/stages/reports/STAGE_5A_0_EXTERNAL_POST_PROCESSING_BOUNDARY_SKELETON_REPORT.md
```

Report must record:

```text
boundary docs created
skeleton path created or intentionally not created
AGENTS.md changed or not needed
runtime behavior unchanged
checks run
completion status
```

---

## 8. COMPLETION CRITERIA

This stage is complete when:

```text
post-processing boundary is documented
no analytics implementation was added
exporter core is unchanged
docs index updated if required
checks were run or inability documented
required report exists
lifecycle cleanup is completed according to AGENTS.md
```

---

## 9. OUTPUT LIMITS

Use AGENTS.md compact final response format.

Do not paste full docs.
Do not include broad future recommendations unless required by a real blocker.
