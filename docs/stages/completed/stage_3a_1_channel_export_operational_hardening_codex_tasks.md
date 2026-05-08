# STAGE 3A.1 — CHANNEL EXPORT OPERATIONAL HARDENING — CODEX TASK FILE

Status: completed
Stage: 3A.1
Scope: historical task instructions

## 0. Purpose

This file is intended to be given directly to Codex / AI coding agent.

It contains:

1. The exact prompt to use.
2. Non-negotiable architectural constraints.
3. Reuse rules for existing incremental/state/progress patterns.
4. Direct prohibitions.
5. A maximally atomic TODO list.
6. Stop conditions.
7. Verification commands.
8. Final Definition of Done.

Stage 3A.1 is not a new feature stage. It is an operational hardening pass for the already implemented `export-channel` feature.

---

# 1. Copy-paste prompt for Codex

Use this prompt in Codex:

```text
Read AGENTS.md first.

Then read:
- docs/stages/stage_3a_direct_channel_export_backlog.md
- docs/stages/stage_3a_direct_channel_export_agent_tasks.md
- docs/refactor/STAGE_3A_DIRECT_CHANNEL_EXPORT_REPORT.md

Now implement Stage 3A.1 — Channel Export Operational Hardening.

Goal:
Improve the existing `export-channel` implementation by adding operational reliability:
- streaming export instead of materializing all records in memory;
- incremental channel export state;
- append-only update mode;
- real `--force` behavior;
- progress events;
- console progress display;
- no-new-posts handling;
- safe state update only after successful export.

Strict architecture rules:
- Do not change existing behavior of `export`, `db-export`, `export-pm`, `update`, `retry`, `report`, `clean`, `delete`, `schedule`, `setup`.
- Do not change existing user export format.
- Do not change existing DB export format.
- Do not change existing private archive format.
- Do not change SQLite schema.
- Do not add analytics, scoring, NLP, embeddings, semantic search, graph analysis, political analysis, government-affiliation detection, or dashboard logic.
- Do not put channel export logic into ExportService, DBExportService, PrivateArchiveService, or ContextEngine.
- Keep all new channel export operational logic under `tg_msg_manager/services/channel_export/`.
- Reuse the existing incremental/state/progress ideology from DB export/private archive, but do not directly import DBExportStateManager or DBExport-specific components unless they are already generic.
- Prefer a dedicated `ChannelExportStateManager`.
- Service must remain orchestration-only.
- Do not print directly from service. Use events/callbacks and render progress in CLI layer.
- State must only be updated after successful file writes.
- Default media mode must remain `metadata`.
- `--media full` must remain blocked/deferred unless Stage 3B is explicitly being implemented.
- Do not implement Stage 3B or Stage 3C here.

Implementation requirements:
1. Add `channel_export_state.json`.
2. Add incremental mode based on `last_exported_message_id`.
3. Add append-only update for `messages.jsonl`, `messages.txt`, and `media_manifest.jsonl`.
4. Rebuild/update `manifest.json` after each successful run.
5. Implement real `--force` behavior:
   - ignore state;
   - perform full re-export;
   - overwrite existing dataset files;
   - recreate state.
6. Replace current full in-memory `mapped_records` list with streaming or bounded-batch writing.
7. Add progress events:
   - started;
   - channel_resolved;
   - state_loaded;
   - progress;
   - no_new_posts;
   - completed;
   - failed.
8. Add console progress renderer:
   - show processed posts;
   - show media records;
   - support unknown total;
   - print final summary.
9. Add tests:
   - first full export;
   - second incremental export appends only new posts;
   - no-new-posts case;
   - force re-export overwrites;
   - state not updated on failure;
   - progress events emitted;
   - old commands unchanged.
10. Update docs:
   - README;
   - COMMANDS.md;
   - LIVE_SMOKE_CHECKLIST.md;
   - PROJECT_ARCHITECTURE_OVERVIEW.md if needed;
   - CHANGELOG.md;
   - Stage 3A.1 report.

Before editing code:
1. Inspect current `services/channel_export/`.
2. Inspect DB export incremental/state/progress pattern.
3. Inspect private archive state/progress/media patterns.
4. Summarize implementation plan in 10–15 lines.
5. Then implement.

Final verification:
- python3 -m compileall tg_msg_manager
- ruff check tg_msg_manager tests
- ruff format --check tg_msg_manager tests
- pytest tests/test_channel_export_*.py
- make test
- make verify
- python3 -m tg_msg_manager.cli export-channel --help

Return:
- files changed;
- tests run;
- results;
- known limitations;
- whether Stage 3A.1 is complete.
```

---

# 2. Stage definition

## 2.1. Stage name

```text
Stage 3A.1 — Channel Export Operational Hardening
```

## 2.2. Main goal

Make `export-channel` operationally safe for real use on larger channels.

Stage 3A created the feature. Stage 3A.1 hardens it.

## 2.3. Main problems to solve

Current known limitations:

```text
1. Full re-export only.
2. No channel_export_state.json.
3. No incremental append mode.
4. --force is not fully meaningful.
5. Service may materialize all mapped records in memory.
6. No dedicated progress display for long exports.
7. No no-new-posts handling.
8. State safety around partial failures is not formalized.
```

## 2.4. Expected result

After Stage 3A.1:

```text
export-channel first run:
  full export
  writes dataset files
  writes state

export-channel second run:
  reads state
  exports only new posts
  appends to existing dataset
  updates manifest
  updates state

export-channel --force:
  ignores state
  full re-export
  overwrites dataset files
  recreates state

long export:
  streams records
  shows progress
  does not hold all records in memory

failure:
  state is not advanced incorrectly
```

---

# 3. Non-negotiable constraints

## 3.1. No unrelated behavior changes

Do not change:

```text
export
db-export
export-pm
update
retry
report
clean
delete
schedule
setup
```

Do not change:

```text
existing user export output
existing DB export output
existing private archive output
existing retry/report behavior
existing clean/delete safety behavior
```

## 3.2. No SQLite migration

Do not add migrations. Do not add tables. Do not persist channel posts in SQLite.

Stage 3A.1 state must be filesystem-based:

```text
channel_export_state.json
```

## 3.3. No analytics

Do not add:

```text
political analysis
government-affiliation detection
propaganda detection
narrative classification
sentiment
user scoring
channel scoring
graph analysis
embeddings
semantic search
LLM calls
```

## 3.4. No Stage 3B / 3C work

Do not implement:

```text
full media download hardening
thumbnail mode
discussion group export
comments export
linked discussion mapping
source export from groups
```

`--media full` should remain blocked/deferred unless it already existed and is safe.

## 3.5. Do not grow hot-path services

Do not add operational channel export logic into:

```text
tg_msg_manager/services/export/service.py
tg_msg_manager/services/db_export/service.py
tg_msg_manager/services/private_archive/service.py
tg_msg_manager/services/context/engine.py
```

Allowed modifications there:

```text
none preferred
only import compatibility/docs if absolutely necessary
```

## 3.6. Keep channel export isolated

All new logic should live under:

```text
tg_msg_manager/services/channel_export/
```

Expected new files:

```text
state_manager.py
progress.py        # optional
```

Expected modified files:

```text
service.py
payload_writer.py
event_emitter.py
models.py
```

CLI-layer modifications are allowed in:

```text
tg_msg_manager/cli.py
tg_msg_manager/cli_commands.py
tg_msg_manager/cli_parser.py
```

Runtime path modifications are allowed only if needed.

---

# 4. Reuse rules

## 4.1. What to reuse

Reuse patterns from existing code:

```text
DB export:
  - incremental source/loading idea
  - state manager idea
  - append/update idea
  - progress callback pattern
  - run status success/failed
  - force/overwrite semantics if compatible

Private archive:
  - progress/event style
  - media/status reporting style
  - failure logging style if useful

Global project:
  - CLI parser style
  - CLI command handler style
  - runtime paths style
  - service event rendering style
  - tests/fake client style
  - docs style
```

## 4.2. What not to reuse directly

Do not directly import domain-specific components if they carry wrong semantics:

```text
DBExportStateManager
DBExportSourceLoader
DBExportPayloadWriter
PrivateArchiveStateManager
PrivateArchive media classes
user_id-specific state logic
db-export-specific manifest logic
```

Instead create channel-specific components using the same style.

## 4.3. Required new component

Create:

```text
tg_msg_manager/services/channel_export/state_manager.py
```

This should own:

```text
load state
save state
detect first run
detect incremental run
detect force run
compute last_exported_message_id
update state after success
avoid state advancement on failure
```

---

# 5. Target state file

## 5.1. File path

Inside each channel export directory:

```text
channel_export_state.json
```

Example:

```text
exports/channels/@example__123456789/channel_export_state.json
```

## 5.2. State schema

Minimum:

```json
{
  "schema_version": "1.0",
  "channel_id": 123456789,
  "channel_username": "example",
  "channel_title": "Example Channel",
  "last_exported_message_id": 98765,
  "last_exported_at": "2026-05-07T12:00:00+00:00",
  "message_count_total": 4521,
  "media_count_total": 1200,
  "last_run_status": "completed",
  "updated_at": "2026-05-07T12:00:00+00:00"
}
```

Optional:

```json
{
  "date_from": "2024-01-01T00:00:00+00:00",
  "date_to": "2026-05-07T12:00:00+00:00",
  "last_manifest_path": "manifest.json"
}
```

## 5.3. State rules

```text
1. State is created after successful first export.
2. State is updated after successful incremental export.
3. State is not updated if export fails before successful write completion.
4. State is replaced after --force full re-export.
5. State must tolerate missing optional fields.
6. State must validate channel_id to avoid appending one channel into another channel directory.
```

---

# 6. Incremental logic

## 6.1. First run

Condition:

```text
state does not exist
or --force is used
```

Behavior without force:

```text
mode = full
write new dataset files
write manifest
write state
```

Behavior with force:

```text
mode = force_full
ignore existing state
overwrite dataset files
write manifest
write state
```

## 6.2. Incremental run

Condition:

```text
state exists
and --force is false
```

Behavior:

```text
1. load last_exported_message_id
2. fetch channel messages newer than last_exported_message_id
3. append new records to messages.jsonl
4. append new blocks to messages.txt
5. append media records to media_manifest.jsonl
6. update manifest
7. update state
```

## 6.3. No new posts

Condition:

```text
state exists
and no message_id > last_exported_message_id
```

Behavior:

```text
1. emit no_new_posts event
2. do not append files
3. do not advance last_exported_message_id
4. optionally update checked_at if schema includes it
5. print clear CLI message
```

## 6.4. Ordering

Telegram iteration may return newest-to-oldest.

For append files, new posts should be appended in chronological/message_id ascending order unless the existing dataset explicitly uses descending order.

Preferred:

```text
new posts sorted by message_id ascending before append
```

If streaming prevents sorting all new posts, use bounded batch or document order.

MVP acceptable:

```text
collect only new posts batch in memory
not all historical records
```

Do not collect full channel history in memory.

---

# 7. Streaming requirement

## 7.1. Current anti-pattern to remove

Do not use:

```python
mapped_records = [
    ...
    async for message in ...
]
```

for the entire export.

## 7.2. Required pattern

Use one of:

```text
fetch -> map -> write immediately
```

or:

```text
fetch -> map -> bounded batch -> write batch
```

Allowed bounded batch size:

```text
100
500
1000
```

But do not accumulate all records for large exports.

## 7.3. Counts

Streaming writer must still compute:

```text
message_count
media_count
downloaded_media_count
skipped_media_count
date_from
date_to
last_exported_message_id
```

## 7.4. Existing full export

For full export, overwrite files and stream records.

## 7.5. Incremental export

For incremental export, append files and stream only new records.

---

# 8. Progress requirements

## 8.1. Service must not print directly

Do not use `print()` inside:

```text
services/channel_export/service.py
services/channel_export/payload_writer.py
services/channel_export/state_manager.py
```

Service emits events.

CLI renders them.

## 8.2. Events

Add or extend events:

```text
channel_export.started
channel_export.channel_resolved
channel_export.state_loaded
channel_export.progress
channel_export.no_new_posts
channel_export.completed
channel_export.failed
```

## 8.3. Progress payload

Minimum:

```json
{
  "processed_posts": 1250,
  "media_records": 340,
  "total_posts": null,
  "mode": "incremental",
  "elapsed_seconds": 12.5
}
```

Optional:

```json
{
  "written_jsonl": 1250,
  "written_txt": 1250,
  "last_message_id": 98765
}
```

## 8.4. Unknown total

Total may be unknown.

Do not fake total.

If total is unknown:

```text
Processed posts: 1250
```

If total is known:

```text
Processed posts: 1250 / 48213 (2.59%)
```

## 8.5. CLI display

For interactive terminal:

```text
Processed posts: 1250 | Media records: 340 | Elapsed: 00:00:12
```

For non-interactive output or tests:

```text
print progress every N records
```

Default progress interval:

```text
100
```

If adding CLI arg:

```text
--progress-interval 100
```

Optional. Do not add if unnecessary.

## 8.6. Final summary

Always print final summary:

```text
Channel export completed
Mode: full/incremental/force_full
Posts exported this run: N
Total known exported posts: N
Media records added: N
Manifest: ...
JSONL: ...
TXT: ...
Media manifest: ...
State: ...
```

---

# 9. File writing behavior

## 9.1. Full export

Open mode:

```text
write / overwrite
```

Affected files:

```text
messages.jsonl
messages.txt
media_manifest.jsonl
manifest.json
channel_export_state.json
```

## 9.2. Incremental export

Open mode:

```text
append for JSONL/TXT/media_manifest
overwrite for manifest/state
```

Affected files:

```text
messages.jsonl        append
messages.txt          append
media_manifest.jsonl  append
manifest.json         overwrite
state                 overwrite after success
```

## 9.3. Force export

Open mode:

```text
overwrite all dataset files
```

State:

```text
recreated after success
```

## 9.4. Failure safety

If export fails:

```text
do not advance state
emit failed event
return non-zero via CLI if project style uses exceptions
do not claim completed
```

MVP may leave partial appended records if failure occurs during writing, but must not advance state incorrectly.

Better:

```text
write incremental records to temp files
append temp files only after success
then update state
```

If temp append is too much for this stage, document limitation.

---

# 10. Atomic TODO list

## 10.1. Preparation

- [ ] Read `AGENTS.md`.
- [ ] Read `docs/stages/stage_3a_direct_channel_export_backlog.md`.
- [ ] Read `docs/stages/stage_3a_direct_channel_export_agent_tasks.md`.
- [ ] Read `docs/refactor/STAGE_3A_DIRECT_CHANNEL_EXPORT_REPORT.md`.
- [ ] Inspect `tg_msg_manager/services/channel_export/`.
- [ ] Inspect `tg_msg_manager/services/channel_export/service.py`.
- [ ] Inspect `tg_msg_manager/services/channel_export/payload_writer.py`.
- [ ] Inspect `tg_msg_manager/services/channel_export/event_emitter.py`.
- [ ] Inspect `tg_msg_manager/services/channel_export/models.py`.
- [ ] Inspect `tg_msg_manager/services/db_export/service.py`.
- [ ] Inspect `tg_msg_manager/services/db_export/state_manager.py` if present.
- [ ] Inspect `tg_msg_manager/services/db_export/source_loader.py` if present.
- [ ] Inspect `tg_msg_manager/services/private_archive/` for event/progress patterns.
- [ ] Inspect CLI command handler for `export-channel`.
- [ ] Inspect CLI event rendering style.
- [ ] Inspect current tests for channel export.
- [ ] Write a 10–15 line implementation plan before editing.

## 10.2. Baseline

- [ ] Run `git status --short`.
- [ ] Run `git rev-parse HEAD`.
- [ ] Run `git branch --show-current`.
- [ ] Run `pytest tests/test_channel_export_*.py`.
- [ ] Run `make test`.
- [ ] Run `make verify`.
- [ ] Create `docs/refactor/STAGE_3A_1_BASELINE.md`.
- [ ] Record current commit.
- [ ] Record current branch.
- [ ] Record baseline command results.
- [ ] Record known current limitations.
- [ ] Stop if baseline is broken and not documented.

## 10.3. Models update

File:

```text
tg_msg_manager/services/channel_export/models.py
```

Tasks:

- [ ] Add `ChannelExportState` dataclass.
- [ ] Add `ChannelExportRunMode` constants or enum-like constants.
- [ ] Add `ChannelExportRunStats` dataclass.
- [ ] Add `state_path` to `ChannelExportPlan`.
- [ ] Add state path to `ChannelExportResult` if useful.
- [ ] Add run mode to `ChannelExportResult`.
- [ ] Add `posts_exported_this_run` if different from total.
- [ ] Keep Python 3.9-compatible typing unless project uses newer syntax.
- [ ] Ensure models do not import Telegram.
- [ ] Ensure models do not write files.
- [ ] Run `python3 -m compileall tg_msg_manager/services/channel_export`.

Suggested dataclasses:

```python
@dataclass(frozen=True)
class ChannelExportState:
    schema_version: str
    channel_id: int
    channel_username: Optional[str]
    channel_title: Optional[str]
    last_exported_message_id: Optional[int]
    last_exported_at: Optional[datetime]
    message_count_total: int
    media_count_total: int
    last_run_status: str
    updated_at: datetime
```

```python
@dataclass(frozen=True)
class ChannelExportRunStats:
    mode: str
    posts_exported: int
    media_records_added: int
    downloaded_media_count: int
    skipped_media_count: int
    date_from: Optional[datetime]
    date_to: Optional[datetime]
    last_exported_message_id: Optional[int]
```

## 10.4. Plan builder update

File:

```text
tg_msg_manager/services/channel_export/plan_builder.py
```

Tasks:

- [ ] Add `state_path` to generated plan.
- [ ] State path must be `output_dir / "channel_export_state.json"`.
- [ ] Ensure plan builder does not load state.
- [ ] Ensure plan builder does not write state.
- [ ] Update plan builder tests.
- [ ] Test state path exists in plan.
- [ ] Test path is deterministic.

## 10.5. State manager creation

Create:

```text
tg_msg_manager/services/channel_export/state_manager.py
```

Tasks:

- [ ] Add `ChannelExportStateManager` class.
- [ ] Add `load(path: Path) -> Optional[ChannelExportState]`.
- [ ] Add `save(path: Path, state: ChannelExportState) -> None`.
- [ ] Add `state_exists(path: Path) -> bool`.
- [ ] Add `determine_run_mode(state, force: bool) -> str`.
- [ ] Add `validate_state_for_channel(state, channel: ChannelIdentity) -> None`.
- [ ] Add JSON serialization helper.
- [ ] Add JSON deserialization helper.
- [ ] Convert datetime to ISO strings.
- [ ] Parse ISO strings back to datetime.
- [ ] Tolerate missing optional fields.
- [ ] Reject state if `channel_id` does not match current channel.
- [ ] Do not import CLI.
- [ ] Do not import DBExportStateManager.
- [ ] Do not write dataset files.
- [ ] Add tests.

State manager tests:

- [ ] Load missing state returns `None`.
- [ ] Save then load round-trip.
- [ ] Channel ID mismatch raises clear error.
- [ ] Force mode ignores existing state.
- [ ] Existing state gives incremental mode.
- [ ] Missing state gives full mode.
- [ ] Corrupt JSON raises clear error.
- [ ] Missing optional fields tolerated if possible.

## 10.6. Payload writer streaming refactor

File:

```text
tg_msg_manager/services/channel_export/payload_writer.py
```

Tasks:

- [ ] Inspect current writer API.
- [ ] Replace whole-list writing with streaming or bounded-batch writing.
- [ ] Add write mode support:
  - `write`
  - `append`
- [ ] For full/force export, open output files in write mode.
- [ ] For incremental export, open output files in append mode.
- [ ] Write JSONL one record at a time.
- [ ] Write TXT one block at a time.
- [ ] Write media manifest one media record at a time.
- [ ] Track `posts_exported`.
- [ ] Track `media_records_added`.
- [ ] Track `date_from`.
- [ ] Track `date_to`.
- [ ] Track `last_exported_message_id`.
- [ ] Accept optional progress callback.
- [ ] Call progress callback every N records.
- [ ] Do not print.
- [ ] Do not import CLI.
- [ ] Do not load state.
- [ ] Add tests for write mode.
- [ ] Add tests for append mode.
- [ ] Add tests for counts.
- [ ] Add tests for empty run.
- [ ] Add tests for progress callback.

If current architecture prefers writer to receive already mapped records:

- [ ] Keep writer simple.
- [ ] Move streaming orchestration to service.
- [ ] Do not accumulate full channel history.

## 10.7. Post fetcher incremental support

File:

```text
tg_msg_manager/services/channel_export/post_fetcher.py
```

Tasks:

- [ ] Add optional `min_message_id` or `last_exported_message_id` parameter.
- [ ] Fetch only messages newer than `last_exported_message_id` if possible.
- [ ] If Telegram client supports offset/min_id, use it.
- [ ] If client interface does not support min_id, filter in fetcher/service by `message_id > last_exported_message_id`.
- [ ] Do not change global Telegram client interface unless necessary.
- [ ] If interface change is necessary, keep backward compatibility.
- [ ] Stop fetching older messages once message_id <= last_exported_message_id if iteration order allows.
- [ ] Preserve `limit`.
- [ ] Add tests:
  - no state fetches all;
  - last_exported filters older messages;
  - no-new-posts returns empty;
  - limit still works.

## 10.8. Service orchestration refactor

File:

```text
tg_msg_manager/services/channel_export/service.py
```

Tasks:

- [ ] Import `ChannelExportStateManager`.
- [ ] Initialize state manager in service.
- [ ] Determine plan before state load.
- [ ] Load state from `plan.state_path`.
- [ ] Validate state channel_id.
- [ ] Determine run mode:
  - `full`
  - `incremental`
  - `force_full`
- [ ] Emit `channel_export.started`.
- [ ] Emit `channel_export.channel_resolved`.
- [ ] Emit `channel_export.state_loaded`.
- [ ] For full run, overwrite files.
- [ ] For force run, overwrite files and ignore state.
- [ ] For incremental run, append files.
- [ ] Replace `mapped_records = [...]` with streaming/bounded-batch flow.
- [ ] Filter records newer than `last_exported_message_id`.
- [ ] If no new posts, emit `channel_export.no_new_posts`.
- [ ] If no new posts, return result with `posts_exported_this_run = 0`.
- [ ] If no new posts, do not append files.
- [ ] If no new posts, do not incorrectly advance state.
- [ ] After successful write, build updated state.
- [ ] Save updated state.
- [ ] Write updated manifest.
- [ ] Emit `channel_export.completed`.
- [ ] On exception, emit `channel_export.failed`.
- [ ] On exception, do not save advanced state.
- [ ] Keep service orchestration-only.
- [ ] Do not add render logic.
- [ ] Do not add media download logic.
- [ ] Do not add analytics.

Service tests:

- [ ] First full export writes state.
- [ ] First full export writes files.
- [ ] Second export with newer fake messages appends only new posts.
- [ ] Second export without newer messages emits no-new-posts.
- [ ] `--force` overwrites existing files.
- [ ] Failed write does not update state.
- [ ] Progress events emitted.
- [ ] Completed event includes summary.

## 10.9. Event emitter update

File:

```text
tg_msg_manager/services/channel_export/event_emitter.py
```

Tasks:

- [ ] Add event type constants or helper methods for:
  - started;
  - channel_resolved;
  - state_loaded;
  - progress;
  - no_new_posts;
  - completed;
  - failed.
- [ ] Ensure payloads are plain dicts.
- [ ] Ensure no dataclass objects leak if renderer cannot handle them.
- [ ] Add progress payload helper if useful.
- [ ] Add tests if event emitter has tests.

## 10.10. CLI progress rendering

Files:

```text
tg_msg_manager/cli_commands.py
tg_msg_manager/cli.py
```

or existing event renderer file.

Tasks:

- [ ] Locate current event rendering pattern.
- [ ] Reuse existing console status style.
- [ ] Add rendering for `channel_export.started`.
- [ ] Add rendering for `channel_export.channel_resolved`.
- [ ] Add rendering for `channel_export.state_loaded`.
- [ ] Add rendering for `channel_export.progress`.
- [ ] Add rendering for `channel_export.no_new_posts`.
- [ ] Add rendering for `channel_export.completed`.
- [ ] Add rendering for `channel_export.failed`.
- [ ] Do not print progress from service.
- [ ] Support unknown total.
- [ ] Print processed posts count.
- [ ] Print media records count.
- [ ] Print mode.
- [ ] Print final summary.
- [ ] Ensure tests do not fail due to carriage-return output.
- [ ] If using `\r`, disable it in non-interactive tests.
- [ ] If adding progress interval option, document it.

CLI output examples:

```text
Resolving channel: @example
Channel resolved: Example Channel (@example, id=123456789)
Mode: incremental
Last exported message_id: 98765
Processed posts: 100 | Media records: 25
Processed posts: 200 | Media records: 51
Completed.
```

No-new-posts example:

```text
No new posts found.
State unchanged.
```

## 10.11. CLI options update

File:

```text
tg_msg_manager/cli_parser.py
```

Tasks:

- [ ] Check if `--force` already exists.
- [ ] Ensure `--force` help text is accurate.
- [ ] If adding `--progress-interval`, set default 100.
- [ ] Do not add analytics flags.
- [ ] Do not expose `--media full` as implemented if still blocked.
- [ ] Update CLI parser tests.

Suggested help text:

```text
--force
  Ignore existing channel export state and perform a full re-export.
```

Optional:

```text
--progress-interval
  Print progress every N processed posts. Default: 100.
```

## 10.12. Manifest update

File:

```text
tg_msg_manager/services/channel_export/manifest_writer.py
```

Tasks:

- [ ] Add run mode to manifest export block.
- [ ] Add state file to included files.
- [ ] Add total message count if known.
- [ ] Add posts exported this run.
- [ ] Add last_exported_message_id.
- [ ] Add last_run_status.
- [ ] Preserve existing manifest fields.
- [ ] Update manifest tests.

Possible manifest additions:

```json
{
  "export": {
    "run_mode": "incremental",
    "posts_exported_this_run": 27,
    "message_count_total": 1277,
    "last_exported_message_id": 98231,
    "state_file": "channel_export_state.json"
  }
}
```

## 10.13. Tests — required new/updated files

Create or update:

```text
tests/test_channel_export_state_manager.py
tests/test_channel_export_payload_writer.py
tests/test_channel_export_service.py
tests/test_cli_export_channel.py
tests/test_channel_export_manifest.py
```

Required cases:

- [ ] State missing -> full mode.
- [ ] State exists -> incremental mode.
- [ ] Force -> force_full mode.
- [ ] State channel mismatch -> error.
- [ ] State save/load roundtrip.
- [ ] Corrupt state -> clear error.
- [ ] Full export creates state.
- [ ] Incremental export appends only new posts.
- [ ] Incremental export does not duplicate old posts.
- [ ] No-new-posts case returns cleanly.
- [ ] No-new-posts does not append.
- [ ] No-new-posts does not advance state incorrectly.
- [ ] Force export overwrites.
- [ ] Failure does not update state.
- [ ] Progress callback receives counts.
- [ ] Progress event emitted every interval.
- [ ] CLI renders no-new-posts.
- [ ] CLI renders final summary.
- [ ] Existing `export-channel --help` still works.
- [ ] `--media full` remains blocked if Stage 3B not implemented.

## 10.14. Documentation update

Update:

```text
README.md
COMMANDS.md
docs/testing/LIVE_SMOKE_CHECKLIST.md
CHANGELOG.md
```

Optional if architecture overview needs sync:

```text
PROJECT_ARCHITECTURE_OVERVIEW.md
docs/ARCHITECTURE_RULES.md
AGENTS.md
```

README tasks:

- [ ] Document incremental behavior.
- [ ] Document `channel_export_state.json`.
- [ ] Document `--force`.
- [ ] Document that repeated run appends only new posts.
- [ ] Document that no SQLite schema is used.
- [ ] Document that media full is still deferred if not implemented.

COMMANDS.md tasks:

- [ ] Update `export-channel`.
- [ ] Explain `--force`.
- [ ] Explain progress output.
- [ ] Explain default `--media metadata`.

LIVE_SMOKE_CHECKLIST tasks:

- [ ] Add first-run export-channel smoke.
- [ ] Add second-run incremental smoke.
- [ ] Add no-new-posts smoke.
- [ ] Add force re-export smoke.
- [ ] Mention expected `channel_export_state.json`.

CHANGELOG tasks:

- [ ] Add Stage 3A.1 entry.
- [ ] Mention streaming export.
- [ ] Mention incremental state.
- [ ] Mention append-only update.
- [ ] Mention progress display.
- [ ] Mention force behavior.
- [ ] Do not mention Stage 3B features.

## 10.15. Stage report

Create:

```text
docs/refactor/STAGE_3A_1_CHANNEL_EXPORT_OPERATIONAL_HARDENING_REPORT.md
```

Required sections:

```markdown
# Stage 3A.1 — Channel Export Operational Hardening Report

## 1. Summary

## 2. Baseline

## 3. Implemented changes

## 4. Incremental state

## 5. Streaming behavior

## 6. Force behavior

## 7. Progress events and CLI output

## 8. Files changed

## 9. Tests added/updated

## 10. Verification results

| Command | Result |
|---|---|

## 11. Remaining limitations

## 12. Deferred to Stage 3B

## 13. Ready for Stage 3B?
```

Remaining limitations should mention if true:

```text
--media full still deferred
no discussion context export
no SQLite persistence for channel posts
no analytics
total post count may be unknown
```

---

# 11. Verification commands

Run in this order.

## 11.1. Targeted tests

```bash
pytest tests/test_channel_export_*.py
```

## 11.2. Compile

```bash
python3 -m compileall tg_msg_manager
```

## 11.3. Lint

```bash
ruff check tg_msg_manager tests
```

## 11.4. Format

```bash
ruff format --check tg_msg_manager tests
```

## 11.5. Full tests

```bash
make test
```

## 11.6. Full verify

```bash
make verify
```

## 11.7. CLI help

```bash
python3 -m tg_msg_manager.cli export-channel --help
```

## 11.8. Import smoke

```bash
python3 - <<'PY'
from tg_msg_manager.services.channel_export import ChannelExportService, ChannelExportOptions
print("channel export import smoke ok")
PY
```

---

# 12. Stop conditions

Stop and report instead of continuing if:

```text
baseline tests fail before changes
existing command behavior changes unexpectedly
SQLite migration seems required
channel export requires editing ExportService/DBExportService/PrivateArchiveService/ContextEngine
incremental implementation risks corrupting existing dataset files
state cannot be safely validated against channel_id
tests reveal duplicate appended messages
--force cannot be implemented safely
progress rendering breaks tests/CI output
```

If a stop condition occurs, do not hack around it. Explain the exact conflict and propose the smallest safe next step.

---

# 13. Final Definition of Done

Stage 3A.1 is complete only if all items are true:

```text
[ ] channel_export_state.json exists after successful export
[ ] first run performs full export
[ ] second run performs incremental export
[ ] repeated run with no new posts does not append duplicates
[ ] --force performs full re-export
[ ] messages.jsonl append behavior works
[ ] messages.txt append behavior works
[ ] media_manifest.jsonl append behavior works
[ ] manifest.json updates after successful run
[ ] state updates only after successful run
[ ] service no longer materializes full channel history in memory
[ ] progress events are emitted
[ ] CLI renders progress
[ ] CLI renders final summary
[ ] no direct print inside channel export service
[ ] no SQLite schema changes
[ ] no analytics added
[ ] no Stage 3B/3C features added
[ ] existing export/db-export/export-pm behavior unchanged
[ ] targeted channel export tests pass
[ ] full test suite passes
[ ] make verify passes
[ ] docs updated
[ ] live smoke checklist updated
[ ] changelog updated
[ ] Stage 3A.1 report created
```

---

# 14. Recommended next stage after this

Only after Stage 3A.1 is complete:

```text
Stage 3B — Media Download Hardening
```

Stage 3B may then reuse:

```text
state manager
progress events
console renderer
append/update pattern
failure-status reporting
```

Do not start Stage 3B inside this task.
