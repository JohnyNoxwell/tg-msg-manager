# STAGE 3A — DIRECT CHANNEL EXPORT — AGENT EXECUTION PLAN

Status: completed
Stage: 3A
Scope: historical task instructions

## 0. Purpose

This file is an execution plan for an AI coding agent.

It is stricter than the backlog.

The goal is to implement **Direct Channel Export** in `tg-msg-manager` without damaging the current architecture.

The feature must export Telegram channel posts directly from a channel into a filesystem dataset:

```text
manifest.json
messages.jsonl
messages.txt
media_manifest.jsonl
media/
```

This stage is **dataset projection only**.

It must not implement analytics.

---

# 1. Non-negotiable constraints

## 1.1. Do not change existing behavior

Do not change behavior of existing commands:

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
existing export format
existing DB export format
existing private archive format
existing SQLite schema
existing context behavior
existing retry behavior
existing report behavior
```

## 1.2. Do not add analytics

Do not implement:

```text
political analysis
government affiliation detection
narrative classification
sentiment analysis
user/channel scoring
influence scoring
graph analysis
embeddings
semantic search
LLM prompt generation
dashboard
REST API
```

The program exports facts. External tools analyze them.

## 1.3. Do not grow hot-path services

Do not add this feature into:

```text
tg_msg_manager/services/export/service.py
tg_msg_manager/services/db_export/service.py
tg_msg_manager/services/private_archive/service.py
tg_msg_manager/services/context/engine.py
```

These files may only be touched if absolutely necessary for imports or docs comments. Prefer not to touch them.

## 1.4. Do not add SQLite schema changes

Stage 3A is filesystem-first.

Do not create migrations for:

```text
channels
source_identities
source_export_runs
source_message_links
channel_posts
channel_media
```

These may be future stages, not Stage 3A.

## 1.5. Do not download full media by default

Default media mode must be:

```text
metadata
```

Full media download must be explicit:

```text
--media full
```

If full media download is too complex, defer it and implement metadata mode only.

## 1.6. Keep CLI thin

CLI should parse arguments and call service.

CLI must not contain:

```text
Telegram iteration logic
message mapping logic
media extraction logic
JSONL rendering logic
TXT rendering logic
manifest building logic
download logic
```

---

# 2. Target feature

Add a command:

```bash
python3 -m tg_msg_manager.cli export-channel --channel "@channel_username" --limit 100 --media metadata
```

Minimum output:

```text
exports/
  channels/
    @channel_username__123456789/
      manifest.json
      messages.jsonl
      messages.txt
      media_manifest.jsonl
      media/
        photos/
        videos/
        documents/
        audio/
        voice/
        animations/
        thumbnails/
```

If no media files are downloaded, `media/` may exist with empty subdirectories.

---

# 3. Target service package

Create:

```text
tg_msg_manager/services/channel_export/
```

Required MVP files:

```text
tg_msg_manager/services/channel_export/__init__.py
tg_msg_manager/services/channel_export/models.py
tg_msg_manager/services/channel_export/plan_builder.py
tg_msg_manager/services/channel_export/manifest_writer.py
tg_msg_manager/services/channel_export/jsonl_renderer.py
tg_msg_manager/services/channel_export/txt_renderer.py
tg_msg_manager/services/channel_export/media_policy.py
tg_msg_manager/services/channel_export/media_manifest_writer.py
tg_msg_manager/services/channel_export/source_resolver.py
tg_msg_manager/services/channel_export/post_fetcher.py
tg_msg_manager/services/channel_export/post_mapper.py
tg_msg_manager/services/channel_export/service.py
tg_msg_manager/services/channel_export/event_emitter.py
```

Optional only if implementing `--media full`:

```text
tg_msg_manager/services/channel_export/media_downloader.py
```

---

# 4. Implementation order

Follow this exact order.

Do not jump directly to CLI.

```text
1. Baseline checks
2. Models
3. Plan builder
4. Renderers
5. Manifest writer
6. Media policy
7. Media manifest writer
8. Source resolver
9. Post fetcher
10. Post mapper
11. Service orchestration
12. CLI parser
13. CLI command handler
14. Runtime paths
15. Tests
16. Docs
17. Live smoke checklist
18. Changelog
19. Final verification
20. Stage report
```

---

# 5. Phase 1 — Baseline

## 5.1. Goal

Confirm current project is clean before changing code.

## 5.2. Tasks

### 5.2.1. Check git state

Run:

```bash
git status --short
git rev-parse HEAD
git branch --show-current
```

### 5.2.2. Run baseline tests

Run:

```bash
make test
```

### 5.2.3. Run baseline verification

Run:

```bash
make verify
```

If `make verify` does not exist, run the closest existing project verification command.

### 5.2.4. Create baseline report

Create:

```text
docs/refactor/STAGE_3A_BASELINE.md
```

Content:

```markdown
# Stage 3A Baseline

## Commit

## Branch

## Git status

## Baseline commands

| Command | Result | Notes |
|---|---|---|

## Existing architecture constraints

## Feature scope
```

## 5.3. Stop condition

Stop and do not continue if:

```text
baseline tests fail
baseline verify fails
git state has unrelated uncommitted changes
```

Unless the failure is already known and documented.

---

# 6. Phase 2 — Models

## 6.1. Goal

Define pure data structures for channel export.

## 6.2. File

Create:

```text
tg_msg_manager/services/channel_export/models.py
```

## 6.3. Tasks

### 6.3.1. Add imports

Use Python 3.9-compatible typing unless project already requires newer syntax.

```python
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, Tuple
```

### 6.3.2. Add ChannelIdentity

```python
@dataclass(frozen=True)
class ChannelIdentity:
    channel_id: int
    title: Optional[str]
    username: Optional[str]
    access_hash: Optional[int] = None
```

### 6.3.3. Add ChannelExportOptions

```python
@dataclass(frozen=True)
class ChannelExportOptions:
    channel: str
    limit: Optional[int]
    media_mode: str
    output_dir: Path
    include_jsonl: bool = True
    include_txt: bool = True
    force: bool = False
```

### 6.3.4. Add ChannelMediaRecord

```python
@dataclass(frozen=True)
class ChannelMediaRecord:
    media_id: str
    message_id: int
    media_index: int
    media_type: Optional[str]
    mime_type: Optional[str]
    file_name: Optional[str]
    file_size: Optional[int]
    width: Optional[int]
    height: Optional[int]
    duration: Optional[float]
    local_path: Optional[str]
    sha256: Optional[str]
    download_status: str
```

### 6.3.5. Add ChannelPostRecord

```python
@dataclass(frozen=True)
class ChannelPostRecord:
    message_id: int
    channel_id: int
    channel_title: Optional[str]
    channel_username: Optional[str]
    timestamp: datetime
    text: Optional[str]
    views: Optional[int]
    forwards: Optional[int]
    replies_count: Optional[int]
    reactions: Dict[str, Any]
    media: Tuple[ChannelMediaRecord, ...]
    raw_payload: Dict[str, Any] = field(default_factory=dict)
```

### 6.3.6. Add ChannelExportPlan

```python
@dataclass(frozen=True)
class ChannelExportPlan:
    output_dir: Path
    manifest_path: Path
    messages_jsonl_path: Path
    messages_txt_path: Path
    media_manifest_path: Path
    media_dir: Path
```

### 6.3.7. Add ChannelExportResult

```python
@dataclass(frozen=True)
class ChannelExportResult:
    channel: ChannelIdentity
    message_count: int
    media_count: int
    downloaded_media_count: int
    skipped_media_count: int
    manifest_path: Path
    messages_jsonl_path: Path
    messages_txt_path: Path
    media_manifest_path: Path
```

## 6.4. Acceptance criteria

- Models contain no Telegram-specific imports.
- Models contain no filesystem writes.
- Models contain no JSON serialization logic.
- Models are importable.

## 6.5. Verification

Run:

```bash
python3 -m compileall tg_msg_manager/services/channel_export
```

---

# 7. Phase 3 — Plan builder

## 7.1. Goal

Create deterministic output paths for a channel export.

## 7.2. File

Create:

```text
tg_msg_manager/services/channel_export/plan_builder.py
```

## 7.3. Tasks

### 7.3.1. Add safe filename helper

Create a helper:

```python
def sanitize_path_part(value: str, *, fallback: str = "unknown") -> str:
    ...
```

Rules:

```text
strip whitespace
replace spaces with _
remove / and \
remove control characters
keep @ if username starts with @
limit length to 120 chars
fallback if empty
```

### 7.3.2. Add directory name builder

Create:

```python
def build_channel_directory_name(channel: ChannelIdentity) -> str:
    ...
```

Rules:

```text
if username exists:
  @username__channel_id

else if title exists:
  safe_title__channel_channel_id

else:
  channel_channel_id
```

### 7.3.3. Add plan builder class

Create:

```python
class ChannelExportPlanBuilder:
    def build(self, base_dir: Path, channel: ChannelIdentity) -> ChannelExportPlan:
        ...
```

### 7.3.4. Create expected paths

Plan must include:

```text
output_dir
manifest_path
messages_jsonl_path
messages_txt_path
media_manifest_path
media_dir
```

### 7.3.5. Create media subdirectories

Create or plan:

```text
media/photos
media/videos
media/documents
media/audio
media/voice
media/animations
media/thumbnails
```

Prefer creating directories in service or plan builder, but keep behavior consistent and tested.

## 7.4. Acceptance criteria

- Path generation deterministic.
- Unsafe characters removed.
- Username/title do not leak slashes into paths.
- No Telegram logic in this file.
- No rendering logic in this file.

## 7.5. Tests

Create:

```text
tests/test_channel_export_plan_builder.py
```

Test cases:

```text
username path
title-only path
empty title/username fallback
slashes removed
long title truncated
media dirs paths exist or are planned
```

---

# 8. Phase 4 — JSONL renderer

## 8.1. Goal

Render one `ChannelPostRecord` into one JSON object line.

## 8.2. File

Create:

```text
tg_msg_manager/services/channel_export/jsonl_renderer.py
```

## 8.3. Tasks

### 8.3.1. Add serialization helper

Create:

```python
def channel_post_to_dict(record: ChannelPostRecord) -> Dict[str, Any]:
    ...
```

Fields:

```text
message_id
channel_id
channel_title
channel_username
timestamp
text
views
forwards
replies_count
reactions
media
raw_payload
```

Timestamp must be ISO string.

### 8.3.2. Add media serializer

Create:

```python
def channel_media_to_dict(record: ChannelMediaRecord) -> Dict[str, Any]:
    ...
```

### 8.3.3. Add JSONL renderer

Create:

```python
class ChannelJsonlRenderer:
    def render_line(self, record: ChannelPostRecord) -> str:
        ...
```

Use:

```python
json.dumps(data, ensure_ascii=False, sort_keys=False)
```

Return line without or with trailing newline consistently. Prefer without trailing newline; writer adds newline.

## 8.4. Acceptance criteria

- One post renders as one JSON object.
- Output is valid JSON.
- UTF-8 Cyrillic text is preserved.
- Datetime is ISO string.
- No Python object repr leaks.

## 8.5. Tests

Add:

```text
tests/test_channel_export_renderers.py
```

Test:

```text
valid json
one-line output
datetime iso
media serialized
unicode preserved
```

---

# 9. Phase 5 — TXT renderer

## 9.1. Goal

Render channel posts for human reading.

## 9.2. File

Create:

```text
tg_msg_manager/services/channel_export/txt_renderer.py
```

## 9.3. Tasks

### 9.3.1. Define separator

Use existing project separator if available.

Otherwise:

```text
--------------------
```

### 9.3.2. Add renderer class

Create:

```python
class ChannelTxtRenderer:
    def render_block(self, record: ChannelPostRecord) -> str:
        ...
```

Format:

```text
[YYYY-MM-DD HH:MM:SS UTC] Channel Title (@username) | message_id=12345
Text...

Media:
- photo: media/photos/0000012345_01.jpg [metadata_only]
--------------------
```

### 9.3.3. Handle empty text

If text is missing:

```text
<NO TEXT>
```

or empty body, but be consistent.

### 9.3.4. Handle no media

Do not print empty noisy media block unless project style expects it.

## 9.4. Acceptance criteria

- message_id visible;
- timestamp visible;
- channel visible;
- text visible;
- media references visible;
- stable separator.

## 9.5. Tests

Add tests to:

```text
tests/test_channel_export_renderers.py
```

Test:

```text
text post
empty text post
post with media
separator present
message_id present
```

---

# 10. Phase 6 — Manifest writer

## 10.1. Goal

Write `manifest.json` describing the dataset.

## 10.2. File

Create:

```text
tg_msg_manager/services/channel_export/manifest_writer.py
```

## 10.3. Tasks

### 10.3.1. Add manifest builder

Create:

```python
def build_manifest(
    *,
    channel: ChannelIdentity,
    message_count: int,
    media_count: int,
    downloaded_media_count: int,
    skipped_media_count: int,
    date_from: Optional[datetime],
    date_to: Optional[datetime],
    media_mode: str,
    included_files: Tuple[str, ...],
    status: str = "completed",
) -> Dict[str, Any]:
    ...
```

### 10.3.2. Required manifest fields

Manifest must include:

```text
dataset_type = direct_channel_export
schema_version = 1.0
exported_at
source.type = channel
source.id
source.username
source.title
export.message_count
export.media_count
export.downloaded_media_count
export.skipped_media_count
export.date_from
export.date_to
export.formats
export.media_mode
export.included_files
status
```

### 10.3.3. Add writer class

Create:

```python
class ChannelManifestWriter:
    def write(self, path: Path, manifest: Dict[str, Any]) -> None:
        ...
```

Use:

```python
json.dumps(..., ensure_ascii=False, indent=2)
```

## 10.4. Acceptance criteria

- Manifest is valid JSON.
- Manifest has schema version.
- Manifest identifies channel.
- Manifest records counts.
- Manifest records media mode.
- Manifest is written after export completes.

## 10.5. Tests

Create:

```text
tests/test_channel_export_manifest.py
```

Test:

```text
dataset_type
schema_version
source block
counts
date fields
valid json file write
```

---

# 11. Phase 7 — Media policy

## 11.1. Goal

Classify media and decide paths/statuses without downloading.

## 11.2. File

Create:

```text
tg_msg_manager/services/channel_export/media_policy.py
```

## 11.3. Tasks

### 11.3.1. Define allowed modes

```python
MEDIA_MODE_NONE = "none"
MEDIA_MODE_METADATA = "metadata"
MEDIA_MODE_FULL = "full"
```

### 11.3.2. Add validation

Create:

```python
def validate_media_mode(value: str) -> str:
    ...
```

Accepted:

```text
none
metadata
full
```

### 11.3.3. Add category mapping

Create:

```python
def media_category(media_type: Optional[str], mime_type: Optional[str]) -> str:
    ...
```

Return one of:

```text
photos
videos
documents
audio
voice
animations
thumbnails
unknown
```

### 11.3.4. Add file extension helper

Create:

```python
def extension_for_media(*, media_type: Optional[str], mime_type: Optional[str], file_name: Optional[str]) -> str:
    ...
```

Rules:

```text
prefer safe extension from file_name
else infer from mime_type
else default .bin
```

### 11.3.5. Add target path builder

Create:

```python
def build_media_relative_path(
    *,
    message_id: int,
    media_index: int,
    media_type: Optional[str],
    mime_type: Optional[str],
    file_name: Optional[str],
) -> str:
    ...
```

Expected:

```text
media/photos/0000012345_01.jpg
```

### 11.3.6. Add status decision

Create:

```python
def initial_download_status(media_mode: str) -> str:
    ...
```

Rules:

```text
none -> skipped_by_mode
metadata -> metadata_only
full -> pending
```

If project prefers no `pending`, use `metadata_only` until download runs.

## 11.4. Acceptance criteria

- No Telegram imports.
- No filesystem writes.
- Stable paths.
- No caption/text in filename.
- Full mode not default here; only policy support.

## 11.5. Tests

Create:

```text
tests/test_channel_export_media_policy.py
```

Test:

```text
valid modes
invalid mode raises
photo category
video category
document category
unknown fallback
extension from filename
extension from mime type
stable path
zero-padded message id
```

---

# 12. Phase 8 — Media manifest writer

## 12.1. Goal

Write one media metadata record per line.

## 12.2. File

Create:

```text
tg_msg_manager/services/channel_export/media_manifest_writer.py
```

## 12.3. Tasks

### 12.3.1. Add serializer

Create:

```python
def media_record_to_dict(record: ChannelMediaRecord) -> Dict[str, Any]:
    ...
```

### 12.3.2. Add writer class

Create:

```python
class ChannelMediaManifestWriter:
    def render_line(self, record: ChannelMediaRecord) -> str:
        ...
```

Use JSONL:

```python
json.dumps(data, ensure_ascii=False)
```

## 12.4. Acceptance criteria

- One media object = one JSON line.
- Includes message_id.
- Includes media_id.
- Includes local_path.
- Includes download_status.
- Includes dimensions/duration if available.

## 12.5. Tests

Add to:

```text
tests/test_channel_export_renderers.py
```

or create:

```text
tests/test_channel_export_media_manifest.py
```

---

# 13. Phase 9 — Source resolver

## 13.1. Goal

Resolve CLI channel identifier into Telegram entity and channel identity.

## 13.2. File

Create:

```text
tg_msg_manager/services/channel_export/source_resolver.py
```

## 13.3. Tasks

### 13.3.1. Define resolver class

```python
class ChannelSourceResolver:
    def __init__(self, client):
        self.client = client

    async def resolve(self, channel: str) -> Tuple[Any, ChannelIdentity]:
        ...
```

### 13.3.2. Call client.get_entity

Use existing client interface method if available:

```python
entity = await self.client.get_entity(channel)
```

If current interface method is sync/async different, follow project style.

### 13.3.3. Extract identity fields

Extract defensively:

```text
id
title
username
access_hash
```

Use `getattr`.

### 13.3.4. Validate entity

Minimum validation:

```text
entity has id
```

Better validation:

```text
entity looks like channel/broadcast/chat supported by Telegram adapter
```

Do not overfit to Telethon class names if project has an abstraction.

### 13.3.5. Raise clear errors

Create exceptions or use project existing error pattern.

Suggested:

```python
class ChannelExportError(Exception): ...
class ChannelResolveError(ChannelExportError): ...
class InvalidChannelError(ChannelExportError): ...
```

## 13.4. Acceptance criteria

- Resolver does not fetch messages.
- Resolver does not write files.
- Resolver handles missing username.
- Resolver handles missing title.
- Resolver produces `ChannelIdentity`.

## 13.5. Tests

Create:

```text
tests/test_channel_export_source_resolver.py
```

Use fake client.

Test:

```text
successful username resolve
missing username
missing title
invalid entity
get_entity failure
```

---

# 14. Phase 10 — Post fetcher

## 14.1. Goal

Iterate messages from channel entity.

## 14.2. File

Create:

```text
tg_msg_manager/services/channel_export/post_fetcher.py
```

## 14.3. Tasks

### 14.3.1. Define fetcher

```python
class ChannelPostFetcher:
    def __init__(self, client):
        self.client = client

    async def iter_posts(self, entity, *, limit: Optional[int] = None):
        ...
```

### 14.3.2. Use existing iter_messages

Use:

```python
async for message in self.client.iter_messages(entity, limit=limit):
    ...
```

Adapt to actual signature.

### 14.3.3. Skip service messages

If message has service marker:

```python
if getattr(message, "is_service", False):
    continue
```

If the project uses `media_type == "service"` or another marker, adapt.

### 14.3.4. Do not map here

Fetcher yields raw project message objects.

Do not serialize or write.

## 14.4. Acceptance criteria

- Uses existing client interface.
- Supports limit.
- Does not write files.
- Does not render.
- Does not perform analytics.

## 14.5. Tests

Create:

```text
tests/test_channel_export_post_fetcher.py
```

Use fake async iterator.

Test:

```text
limit passed
messages yielded
service messages skipped
empty channel handled
```

---

# 15. Phase 11 — Post mapper

## 15.1. Goal

Map raw Telegram/project messages into `ChannelPostRecord`.

## 15.2. File

Create:

```text
tg_msg_manager/services/channel_export/post_mapper.py
```

## 15.3. Tasks

### 15.3.1. Define mapper class

```python
class ChannelPostMapper:
    def __init__(self, media_policy):
        self.media_policy = media_policy

    def map_post(
        self,
        message,
        channel: ChannelIdentity,
        *,
        media_mode: str,
    ) -> ChannelPostRecord:
        ...
```

### 15.3.2. Extract base fields

Extract defensively:

```text
message_id
timestamp/date
text/message
views
forwards
replies_count
reactions
raw_payload
```

Use project `MessageData` fields first. Fall back to `raw_payload`.

### 15.3.3. Extract text

Priority:

```text
message.text
message.message
raw_payload.message
```

If absent:

```text
None
```

### 15.3.4. Extract timestamp

Priority:

```text
message.timestamp
message.date
raw_payload.date
```

Must be `datetime` in record.

If timestamp is string, parse if project has helper; otherwise keep robust minimal conversion.

### 15.3.5. Extract reactions

If available, convert to plain dict/list. Do not leak raw Telethon objects into JSON.

If uncertain, set `{}`.

### 15.3.6. Extract media metadata

For each message media item, create `ChannelMediaRecord`.

MVP can support one media item per message if current project model exposes one media.

But design `Tuple[ChannelMediaRecord, ...]` for future albums.

### 15.3.7. Build media id

Use:

```text
<message_id>_<media_index_padded>
```

Example:

```text
12345_01
```

### 15.3.8. Do not download media here

Mapper only produces metadata and planned local path/status.

## 15.4. Acceptance criteria

- Mapper handles missing optional fields.
- Mapper outputs plain dataclasses.
- Mapper does not write files.
- Mapper does not import renderers.
- Mapper does not perform analytics.
- Mapper does not crash on missing media.

## 15.5. Tests

Create:

```text
tests/test_channel_export_post_mapper.py
```

Test:

```text
text-only post
post with media
missing views/forwards
missing reactions
empty text
raw payload missing optional fields
```

---

# 16. Phase 12 — Payload writer

## 16.1. Goal

Write generated render lines to files.

## 16.2. File

Create:

```text
tg_msg_manager/services/channel_export/payload_writer.py
```

## 16.3. Tasks

### 16.3.1. Define writer

```python
class ChannelPayloadWriter:
    def open(self, plan: ChannelExportPlan):
        ...
```

Simpler MVP:

```python
class ChannelPayloadWriter:
    def write_records(
        self,
        *,
        plan: ChannelExportPlan,
        records: Iterable[ChannelPostRecord],
        jsonl_renderer: ChannelJsonlRenderer,
        txt_renderer: ChannelTxtRenderer,
        media_manifest_writer: ChannelMediaManifestWriter,
    ) -> Tuple[int, int, Optional[datetime], Optional[datetime]]:
        ...
```

But avoid accumulating all records. Prefer streaming.

### 16.3.2. Ensure UTF-8

All files must use:

```python
encoding="utf-8"
```

### 16.3.3. Add newline handling

Each JSONL line must end with exactly one newline.

TXT block should have clean separators.

### 16.3.4. Count records

Return:

```text
message_count
media_count
date_from
date_to
```

### 16.3.5. Write media_manifest

For each media record in each post, write one JSONL line.

## 16.4. Acceptance criteria

- Streaming write.
- UTF-8.
- Counts returned.
- No Telegram imports.
- No analytics.

## 16.5. Tests

Create:

```text
tests/test_channel_export_payload_writer.py
```

Test:

```text
writes all files
counts messages
counts media
date_from/date_to
empty channel creates files
unicode preserved
```

---

# 17. Phase 13 — Service orchestration

## 17.1. Goal

Implement `ChannelExportService` as orchestration-only facade.

## 17.2. File

Create:

```text
tg_msg_manager/services/channel_export/service.py
```

## 17.3. Tasks

### 17.3.1. Define service

```python
class ChannelExportService:
    def __init__(
        self,
        *,
        client,
        base_dir: Path,
        event_sink=None,
    ):
        ...
```

### 17.3.2. Initialize components

Inside constructor or factory:

```text
ChannelSourceResolver
ChannelPostFetcher
ChannelPostMapper
ChannelExportPlanBuilder
ChannelJsonlRenderer
ChannelTxtRenderer
ChannelMediaManifestWriter
ChannelManifestWriter
ChannelPayloadWriter
EventEmitter
```

### 17.3.3. Add export method

```python
async def export_channel(self, options: ChannelExportOptions) -> ChannelExportResult:
    ...
```

Steps:

```text
1. validate media mode
2. resolve channel
3. build plan
4. create directories
5. emit started
6. fetch posts
7. map posts
8. write JSONL/TXT/media manifest
9. write manifest
10. emit completed
11. return result
```

### 17.3.4. Keep service thin

Do not put these in service:

```text
JSON serialization
TXT formatting
media classification
entity field extraction
filename sanitization
download details
analytics
```

### 17.3.5. Error handling

If export fails after partial files:

- emit failed event;
- re-raise error;
- optionally write manifest with status `failed` if this is simple;
- do not silently swallow errors.

### 17.3.6. Empty channel

If no posts found:

- create files;
- manifest message_count = 0;
- status completed;
- return result.

## 17.4. Acceptance criteria

- Service is orchestration-only.
- Service has no large helper methods.
- Service does not modify existing export services.
- Service supports metadata mode.
- Service writes all required files.

## 17.5. Tests

Create:

```text
tests/test_channel_export_service.py
```

Use fake client/fake messages.

Test:

```text
exports 2 posts
writes manifest
writes jsonl
writes txt
writes media manifest
handles empty channel
does not download media in metadata mode
emits completion event if event sink provided
```

---

# 18. Phase 14 — Package init

## 18.1. File

Create:

```text
tg_msg_manager/services/channel_export/__init__.py
```

## 18.2. Tasks

Export only public service and models if needed:

```python
from .service import ChannelExportService
from .models import ChannelExportOptions, ChannelExportResult

__all__ = [
    "ChannelExportOptions",
    "ChannelExportResult",
    "ChannelExportService",
]
```

## 18.3. Acceptance criteria

- Public import works:
  ```python
  from tg_msg_manager.services.channel_export import ChannelExportService
  ```

---

# 19. Phase 15 — Runtime paths

## 19.1. Goal

Add stable output root for channel exports.

## 19.2. Locate runtime path definitions

Search:

```bash
grep -R "exports" -n tg_msg_manager/core tg_msg_manager | head -50
grep -R "RuntimePaths" -n tg_msg_manager
```

## 19.3. Add path

Add:

```python
channel_exports_dir: Path
```

Expected path:

```text
exports/channels
```

Use existing project path conventions.

## 19.4. Do not break artifact roots

If project has `artifact_roots()` or cleanup/report path listing, add channel export root only if appropriate.

Do not make delete/clean destructive against channel exports unless explicitly designed and documented.

## 19.5. Acceptance criteria

- Channel export root exists or is created.
- Existing paths unchanged.
- Existing tests pass.

---

# 20. Phase 16 — CLI parser

## 20.1. Goal

Expose command to user.

## 20.2. File

Modify:

```text
tg_msg_manager/cli_parser.py
```

## 20.3. Tasks

### 20.3.1. Add subparser

Add:

```text
export-channel
```

### 20.3.2. Add required argument

```text
--channel
```

Required.

### 20.3.3. Add optional arguments

MVP:

```text
--limit
--media
--output-dir
--force
```

`--media` choices:

```text
none
metadata
full
```

Default:

```text
metadata
```

### 20.3.4. Do not add analytics flags

Do not add:

```text
--analyze
--score
--political
--affiliation
--narratives
```

## 20.4. Acceptance criteria

- `export-channel --help` works.
- Missing `--channel` fails.
- Invalid `--media` fails.
- Existing command help still works.

## 20.5. Tests

Create or update:

```text
tests/test_cli_export_channel.py
```

Test:

```text
help includes export-channel
channel is required
media choices enforced
limit parsed
```

---

# 21. Phase 17 — CLI command handler

## 21.1. Goal

Wire CLI args to service.

## 21.2. File

Modify:

```text
tg_msg_manager/cli_commands.py
```

## 21.3. Tasks

### 21.3.1. Add handler

```python
async def _handle_export_channel_command(ctx, args):
    ...
```

### 21.3.2. Build options

```python
options = ChannelExportOptions(
    channel=args.channel,
    limit=args.limit,
    media_mode=args.media,
    output_dir=args.output_dir or ctx.paths.channel_exports_dir,
    force=args.force,
)
```

Adapt to actual project types.

### 21.3.3. Call service

```python
result = await ctx.channel_exporter.export_channel(options)
```

### 21.3.4. Print result

Print concise result:

```text
Channel export completed
Messages: N
Media records: M
Manifest: ...
JSONL: ...
TXT: ...
Media manifest: ...
```

### 21.3.5. Register command in dispatcher

Where commands are dispatched, add:

```text
export-channel -> _handle_export_channel_command
```

## 21.4. Acceptance criteria

- Handler does not perform mapping/rendering.
- Handler does not directly call Telethon.
- Handler only builds options and calls service.
- Clear output paths are printed.

---

# 22. Phase 18 — CLI context wiring

## 22.1. Goal

Make service available in CLI runtime.

## 22.2. File

Modify:

```text
tg_msg_manager/cli.py
```

or actual CLI context file.

## 22.3. Tasks

### 22.3.1. Import service

```python
from tg_msg_manager.services.channel_export import ChannelExportService
```

### 22.3.2. Add context attribute

```python
self.channel_exporter = None
```

### 22.3.3. Initialize service when client is available

```python
self.channel_exporter = ChannelExportService(
    client=self.client,
    base_dir=self.paths.channel_exports_dir,
    event_sink=...,
)
```

### 22.3.4. Ensure command needs client

`export-channel` must require Telegram client.

If command-needs-client uses denylist and defaults to True, no change needed. Otherwise add explicitly.

## 22.4. Acceptance criteria

- `export-channel` initializes Telegram client.
- `db-export` still does not require Telegram client if previously so.
- `report` behavior unchanged.
- Existing CLI tests pass.

---

# 23. Phase 19 — Optional full media download

## 23.1. Decision point

If metadata mode is working, decide whether to implement `--media full` now.

If not enough confidence, defer full download to Stage 3B.

## 23.2. If deferring full download

Behavior:

```text
--media full returns clear "not implemented yet" error
```

or do not expose `full` choice until implemented.

Preferred for MVP:

```text
Expose only none/metadata
```

But if backlog requires `full`, implement safely.

## 23.3. If implementing full download

Create:

```text
tg_msg_manager/services/channel_export/media_downloader.py
```

Tasks:

```text
1. Use client.download_media if available.
2. Download to planned local path.
3. Skip if file already exists.
4. Compute sha256.
5. Mark status downloaded.
6. On failure, mark failed.
7. Do not crash whole export unless strict mode exists.
```

Add args only if implemented:

```text
--max-media-size
--media-types
```

Do not fake these options.

## 23.4. Acceptance criteria for full media

- Full media download explicit only.
- Existing files not downloaded again.
- Failures are recorded.
- Manifest counts downloaded/skipped.
- Large media controls exist or full mode is clearly experimental.

---

# 24. Phase 20 — Tests

## 24.1. Required test files

Create/update:

```text
tests/test_channel_export_plan_builder.py
tests/test_channel_export_renderers.py
tests/test_channel_export_manifest.py
tests/test_channel_export_media_policy.py
tests/test_channel_export_media_manifest.py
tests/test_channel_export_source_resolver.py
tests/test_channel_export_post_fetcher.py
tests/test_channel_export_post_mapper.py
tests/test_channel_export_payload_writer.py
tests/test_channel_export_service.py
tests/test_cli_export_channel.py
```

If this is too many files for project style, group them under fewer files, but preserve coverage.

## 24.2. Required test cases

### 24.2.1. Plan builder

```text
username path
title-only path
unsafe chars
long title
media dirs
```

### 24.2.2. Renderers

```text
valid JSONL
unicode
datetime ISO
TXT separator
empty text
media refs
```

### 24.2.3. Manifest

```text
dataset_type
schema_version
source block
counts
media mode
included files
```

### 24.2.4. Media policy

```text
mode validation
category mapping
extension inference
path construction
status decision
```

### 24.2.5. Resolver/fetcher/mapper

```text
successful resolve
invalid resolve
fetch messages
skip service messages
map text-only
map media
missing optional fields
```

### 24.2.6. Service

```text
empty channel
two posts
post with media metadata
all output files created
manifest counts correct
no media download in metadata mode
```

### 24.2.7. CLI

```text
help
required channel
media choices
handler dispatch
```

## 24.3. Run tests

Run:

```bash
pytest tests/test_channel_export_*.py
```

Then:

```bash
make test
make verify
```

## 24.4. Stop condition

Do not update docs as completed until tests pass.

---

# 25. Phase 21 — Documentation

## 25.1. README

Add short section:

```markdown
## Direct channel export

Export posts from a Telegram channel into a filesystem dataset.

Example:
```bash
python3 -m tg_msg_manager.cli export-channel --channel @example --limit 100 --media metadata
```
```

Do not overpromise analytics.

## 25.2. COMMANDS.md

If exists, add full command docs:

```text
export-channel
--channel
--limit
--media
--output-dir
--force
```

## 25.3. PROJECT_ARCHITECTURE_OVERVIEW.md

Add:

```markdown
## Channel export

`ChannelExportService` lives under `services/channel_export/`.

It is a filesystem-first dataset projection pipeline.

It does not write channel posts into SQLite in Stage 3A.

It does not perform analytics.

It writes:
- manifest.json
- messages.jsonl
- messages.txt
- media_manifest.jsonl
- media/
```

## 25.4. docs/ARCHITECTURE_RULES.md

Add:

```markdown
## Channel export rules

Direct channel export must live under `services/channel_export/`.

Do not add channel export logic into:
- ExportService
- DBExportService
- PrivateArchiveService
- ContextEngine

Channel export is dataset projection, not analytics.

Default media mode must not download full media.
```

## 25.5. AGENTS.md

Add same rule if not already present.

## 25.6. PR checklist

Add:

```markdown
- [ ] Channel export logic is isolated under services/channel_export/
- [ ] No analytics added to channel export
- [ ] No SQLite schema change added for Stage 3A
- [ ] Full media download is not default
- [ ] Existing export/db-export/export-pm behavior unchanged
```

---

# 26. Phase 22 — Live smoke checklist

## 26.1. File

Modify:

```text
docs/testing/LIVE_SMOKE_CHECKLIST.md
```

## 26.2. Add smoke scenario

Add:

```markdown
## Direct channel export

Required variables:
- TEST_CHANNEL

Command:
```bash
python3 -m tg_msg_manager.cli export-channel --channel "$TEST_CHANNEL" --limit 3 --media metadata
```

Expected:
- exit code 0
- output directory created under exports/channels/
- manifest.json exists
- messages.jsonl exists
- messages.txt exists
- media_manifest.jsonl exists
- media directory exists
- full media files are not downloaded in metadata mode
```

## 26.3. Optional full media smoke

Only if full mode implemented:

```markdown
## Direct channel export with full media

Non-routine test. May download files.

Command:
```bash
python3 -m tg_msg_manager.cli export-channel --channel "$TEST_CHANNEL" --limit 1 --media full
```
```

## 26.4. Acceptance criteria

- Commands are concrete.
- Expected files are listed.
- Full media smoke marked non-routine.

---

# 27. Phase 23 — Changelog

## 27.1. File

Modify:

```text
CHANGELOG.md
```

## 27.2. Add entry

If only metadata mode implemented:

```markdown
## Stage 3A — Direct Channel Export

- Added `export-channel` command for direct Telegram channel post export.
- Added filesystem dataset layout for channel exports.
- Added `manifest.json`, `messages.jsonl`, `messages.txt`, and `media_manifest.jsonl`.
- Added media metadata export.
- Added tests and live smoke checklist for channel export.
```

If full media implemented, add:

```markdown
- Added optional full media download via `--media full`.
```

Do not claim full media if not implemented.

---

# 28. Phase 24 — Final verification

## 28.1. Compile

Run:

```bash
python3 -m compileall tg_msg_manager
```

## 28.2. Lint

Run:

```bash
ruff check tg_msg_manager tests
```

## 28.3. Format check

Run:

```bash
ruff format --check tg_msg_manager tests
```

## 28.4. Tests

Run:

```bash
pytest tests/test_channel_export_*.py
make test
make verify
```

## 28.5. CLI help smoke

Run:

```bash
python3 -m tg_msg_manager.cli export-channel --help
```

## 28.6. Import smoke

Run:

```bash
python3 - <<'PY'
from tg_msg_manager.services.channel_export import ChannelExportService, ChannelExportOptions
print("channel export import smoke ok")
PY
```

## 28.7. Existing command smoke

Run existing lightweight help checks:

```bash
python3 -m tg_msg_manager.cli export --help
python3 -m tg_msg_manager.cli db-export --help
python3 -m tg_msg_manager.cli export-pm --help
```

## 28.8. Stop condition

Do not mark Stage 3A complete if any final check fails.

---

# 29. Phase 25 — Stage report

## 29.1. File

Create:

```text
docs/refactor/STAGE_3A_DIRECT_CHANNEL_EXPORT_REPORT.md
```

## 29.2. Required structure

```markdown
# Stage 3A — Direct Channel Export Report

## 1. Summary

## 2. Implemented files

## 3. CLI command

## 4. Dataset layout

## 5. Media mode behavior

## 6. Architecture constraints preserved

## 7. Tests added

## 8. Final verification

| Command | Result |
|---|---|

## 9. Known limitations

## 10. Deferred tasks

## 11. Ready for Stage 3B?
```

## 29.3. Known limitations to mention if applicable

```text
No discussion group export yet.
No group source extraction yet.
No analytics.
No embeddings.
No SQLite persistence for channel posts.
Full media may be deferred or experimental.
```

---

# 30. Final Definition of Done

Stage 3A is complete only if all are true:

```text
[ ] export-channel command exists
[ ] --channel is required
[ ] --limit works
[ ] default media mode is metadata
[ ] direct channel posts are fetched from Telegram API
[ ] output directory is deterministic
[ ] manifest.json is written
[ ] messages.jsonl is written
[ ] messages.txt is written
[ ] media_manifest.jsonl is written
[ ] media metadata is captured
[ ] full media is not downloaded by default
[ ] no analytics added
[ ] no SQLite schema migration added
[ ] new code isolated under services/channel_export/
[ ] existing hot-path services not expanded
[ ] tests added
[ ] make test passes
[ ] make verify passes
[ ] docs updated
[ ] live smoke checklist updated
[ ] changelog updated
[ ] Stage 3A report created
```

---

# 31. Future stages

Do not implement these now.

## Stage 3B — Full Media Download Hardening

```text
resume
sha256
max media size
media type allowlist
download retries
partial failure report
thumbnail mode
```

## Stage 3C — Channel Discussion Context Export

```text
linked discussion group
comments/replies
post-to-discussion mapping
discussion context dataset
```

## Stage 3D — Source Export from Groups

```text
sender_chat
forward_origin
anonymous admin
authored-as-channel in groups
forwarded-source extraction
```

## Stage 4 — LLM Analysis Packs

```text
prompt templates
dataset summaries
analysis instructions
no built-in scoring
```

---

# 32. Agent behavior rules

The agent must:

```text
work in small commits or logical chunks
run tests after each major block
prefer new files over modifying hot-path files
write defensive code for missing Telegram fields
avoid overfitting to one channel type
avoid raw Telethon objects in JSON output
avoid changing unrelated code
avoid adding analytics
avoid schema migration
document every new command
```

The agent must not:

```text
rewrite the project
rename existing commands
change existing export formats
put channel export into ExportService
put channel export into DBExportService
put channel export into PrivateArchiveService
put channel export into ContextEngine
download full media by default
create political conclusions
create government-affiliation labels
```
