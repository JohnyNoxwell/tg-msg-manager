# STAGE 3A — DIRECT CHANNEL EXPORT / DATASET PROJECTION BACKLOG

Archived: this file is preserved for history and is not current instructions unless explicitly referenced.

## 0. Назначение

Этот backlog описывает внедрение нового функционала в `tg-msg-manager`:

**прямой экспорт постов Telegram-канала** в структурированный датасет:

- `manifest.json`
- `messages.jsonl`
- `messages.txt`
- `media_manifest.jsonl`
- `media/` с опционально скачанными файлами

Это не аналитический слой. Приложение должно собирать, нормализовать и экспортировать данные. Интерпретация, политический анализ, нарративы, связи и выводы остаются задачей внешней LLM/аналитического инструмента.

---

# 1. Контекст текущей архитектуры

В проекте уже есть:

- CLI на `argparse`;
- `ExportService` для user-target export;
- `DBExportService` для экспорта накопленной SQLite-истории;
- `PrivateArchiveService` с media downloader/media policy;
- storage contracts;
- read/write split;
- payload modules;
- compatibility wrappers;
- guard tests;
- fixture-based E2E;
- live smoke checklist.

Stage 3A должен добавлять новый функционал **через отдельный пакет**, не раздувая существующие фасады.

---

# 2. Главный архитектурный принцип

Не добавлять direct channel export в:

```text
services/export/service.py
services/db_export/service.py
services/private_archive/service.py
services/context/engine.py
```

Создать отдельный пакет:

```text
tg_msg_manager/services/channel_export/
```

Рекомендуемое название для первого этапа:

```text
services/channel_export/
```

Переход к более общей `source_export` модели можно сделать позже, когда появятся:

- forwarded-source export;
- authored-as-channel messages from group;
- discussion context export;
- anonymous admin source export.

---

# 3. Цель Stage 3A

Добавить CLI-команду для прямого экспорта постов Telegram-канала:

```bash
python3 -m tg_msg_manager.cli export-channel --channel "@channel_username"
```

Минимальная цель:

```text
Telegram channel
→ iter_messages(channel)
→ normalized channel post records
→ manifest.json
→ messages.jsonl
→ messages.txt
→ media_manifest.jsonl
→ optional media files
```

---

# 4. Что НЕ входит в Stage 3A

На этом этапе нельзя добавлять:

- политический анализ;
- government-affiliation detection;
- scoring;
- NLP;
- embeddings;
- semantic search;
- graph analysis;
- dashboard;
- REST API;
- multi-account;
- discussion group export;
- group source extraction;
- автоматическую классификацию нарративов;
- автоматические обвинительные выводы.

Stage 3A — только сбор и экспорт датасета.

---

# 5. Целевая структура файлов экспорта

Для каждого канала создавать отдельную директорию:

```text
exports/
  channels/
    @channel_name__123456789/
      manifest.json
      messages.jsonl
      messages.txt
      media_manifest.jsonl
      export.log
      media/
        photos/
        videos/
        documents/
        audio/
        voice/
        animations/
        thumbnails/
```

`export.log` опционален, но рекомендуется.

---

# 6. Режимы media

Поддержать media mode:

```text
--media metadata
  default; media files are not downloaded, but metadata is exported

--media none
  do not export detailed media metadata, only has_media/media_type flags

--media full
  download full media files

--media thumbnails
  reserved for future; can be implemented later
```

MVP default:

```text
--media metadata
```

Не делать `full` default, чтобы случайно не скачать десятки гигабайт.

---

# 7. CLI backlog

## 7.1. Добавить команду

Файл:

```text
tg_msg_manager/cli_parser.py
```

Добавить:

```bash
export-channel
```

Аргументы:

```text
--channel REQUIRED
  username, numeric id, invite-resolved id, or entity string accepted by Telethon get_entity

--limit OPTIONAL
  max number of posts to export

--json OPTIONAL
  write JSONL output; default true for this command or always write JSONL

--txt OPTIONAL
  write TXT output; default true

--media OPTIONAL
  choices: none, metadata, full
  default: metadata

--output-dir OPTIONAL
  base output directory

--date-from OPTIONAL
  ISO date; can be implemented later if not trivial

--date-to OPTIONAL
  ISO date; can be implemented later if not trivial

--force OPTIONAL
  overwrite/re-export even if manifest indicates same latest post

--max-media-size OPTIONAL
  future-safe; skip full downloads above threshold

--media-types OPTIONAL
  comma-separated allowlist: photo,video,document,audio,voice,animation
```

MVP required args:

```text
--channel
--limit
--media
--output-dir
```

## 7.2. CLI handler

Файл:

```text
tg_msg_manager/cli_commands.py
```

Добавить handler:

```python
async def _handle_export_channel_command(ctx, args):
    ...
```

Он должен:

1. проверить, что Telegram client доступен;
2. создать или использовать `ChannelExportService`;
3. вызвать `export_channel(...)`;
4. вывести итоговые пути:
   - manifest;
   - messages.jsonl;
   - messages.txt;
   - media_manifest;
   - media directory.

## 7.3. CLIContext wiring

Файл:

```text
tg_msg_manager/cli.py
```

Добавить service dependency:

```python
self.channel_exporter: Optional[ChannelExportService] = None
```

В `initialize()` при `needs_client=True`:

```python
self.channel_exporter = ChannelExportService(
    client=self.client,
    base_dir=self.paths.channel_exports_dir,
    event_sink=render_service_event,
)
```

Если `paths.channel_exports_dir` отсутствует — добавить в runtime paths.

---

# 8. Runtime paths backlog

## 8.1. Добавить channel export directory

Проверить:

```text
tg_msg_manager/core/runtime.py
```

или где определяются paths.

Добавить:

```text
channel_exports_dir = exports/channels
```

Если есть централизованный `artifact_roots()`, добавить туда channel exports root, чтобы delete/cleanup/report могли учитывать его позже.

## 8.2. Не ломать существующие директории

Не менять:

- db exports path;
- private dialogs path;
- existing user export path;
- archive path.

---

# 9. Service package backlog

Создать пакет:

```text
tg_msg_manager/services/channel_export/
    __init__.py
    service.py
    source_resolver.py
    post_fetcher.py
    post_mapper.py
    plan_builder.py
    manifest_writer.py
    jsonl_renderer.py
    txt_renderer.py
    media_policy.py
    media_downloader.py
    media_manifest_writer.py
    payload_writer.py
    models.py
    event_emitter.py
```

MVP можно сделать меньше:

```text
service.py
source_resolver.py
post_fetcher.py
post_mapper.py
plan_builder.py
jsonl_renderer.py
txt_renderer.py
manifest_writer.py
media_policy.py
media_manifest_writer.py
models.py
```

`media_downloader.py` нужен только если реализуется `--media full`.

---

# 10. Models backlog

Файл:

```text
tg_msg_manager/services/channel_export/models.py
```

Добавить dataclasses:

```python
@dataclass(frozen=True)
class ChannelIdentity:
    channel_id: int
    title: Optional[str]
    username: Optional[str]
    access_hash: Optional[int] = None


@dataclass(frozen=True)
class ChannelExportOptions:
    channel: str
    limit: Optional[int]
    media_mode: str
    output_dir: Path
    include_jsonl: bool = True
    include_txt: bool = True
    force: bool = False


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
    raw_payload: Dict[str, Any]


@dataclass(frozen=True)
class ChannelExportPlan:
    output_dir: Path
    manifest_path: Path
    messages_jsonl_path: Path
    messages_txt_path: Path
    media_manifest_path: Path
    media_dir: Path


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

Использовать `typing.Optional`, `typing.Dict`, `typing.Tuple` для совместимости с Python 3.9.

---

# 11. Source resolver backlog

Файл:

```text
services/channel_export/source_resolver.py
```

Ответственность:

- принять `--channel`;
- вызвать `client.get_entity(channel)`;
- проверить, что entity похож на channel;
- вернуть `ChannelIdentity`;
- не выполнять fetch messages;
- не писать файлы.

Нужно учитывать:

- username: `@channel_name`;
- raw username: `channel_name`;
- numeric id;
- Telethon entity object after get_entity.

Ошибки:

```text
ChannelNotFound
ChannelAccessDenied
InvalidChannelEntity
```

Можно сначала использовать generic exceptions, но лучше добавить доменные исключения.

---

# 12. Telegram client interface backlog

Текущий `TelegramClientInterface.iter_messages(entity, limit, offset_id, from_user)` уже подходит для чтения канала.

Но для channel export могут понадобиться поля, которых нет в `MessageData`:

- views;
- forwards;
- replies count;
- reactions;
- grouped_id;
- post_author;
- media metadata;
- file name;
- file size;
- mime type;
- width/height/duration.

## 12.1. Не ломать MessageData

Не добавлять всё это напрямую в `MessageData`, если это сломает текущие сервисы.

Предпочтительно:

1. либо расширить `raw_payload` и извлекать channel-specific fields в `ChannelPostMapper`;
2. либо добавить новый adapter method:
   ```python
   iter_channel_posts(...)
   ```
3. либо добавить optional metadata extraction helper в channel export layer.

MVP recommendation:

```text
Reuse client.iter_messages(channel_entity)
Extract channel-specific fields from msg.raw_payload inside channel_export mapper.
```

## 12.2. Future adapter method

Если `MessageData` недостаточен, добавить в interface:

```python
async def iter_channel_posts(
    self,
    entity: Any,
    limit: Optional[int] = None,
) -> AsyncGenerator[ChannelPostRaw, None]:
    ...
```

Но не делать это в MVP, если можно использовать `iter_messages`.

---

# 13. Post fetcher backlog

Файл:

```text
services/channel_export/post_fetcher.py
```

Ответственность:

- итерировать посты канала через `client.iter_messages(entity, limit=...)`;
- пропускать service messages, если они не нужны;
- возвращать normalized records или raw messages;
- не писать файлы;
- не делать render.

MVP:

```python
async def iter_posts(self, entity, *, limit: Optional[int]):
    async for message in self.client.iter_messages(entity, limit=limit):
        if message.is_service:
            continue
        yield message
```

---

# 14. Channel post mapper backlog

Файл:

```text
services/channel_export/post_mapper.py
```

Ответственность:

- преобразовать `MessageData` + `ChannelIdentity` в `ChannelPostRecord`;
- извлечь media metadata;
- извлечь views/forwards/replies/reactions из `raw_payload`;
- создать `ChannelMediaRecord`;
- не писать файлы.

Если в `raw_payload` нет нужных полей — оставить `None`.

---

# 15. Media policy backlog

Файл:

```text
services/channel_export/media_policy.py
```

Ответственность:

- определить media mode;
- классифицировать media type;
- определить target local path;
- решить download/skip;
- не выполнять download напрямую.

Media categories:

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

File naming:

```text
<zero_padded_message_id>_<media_index>.<ext>
```

Example:

```text
0000012345_01.jpg
0000012345_02.jpg
0000012400_01.mp4
```

Do not use text/caption in filenames.

## 15.1. Extension handling

If real extension is unknown:

- use mime type;
- fallback to `.bin`;
- keep original filename only inside metadata, not as main stored filename.

---

# 16. Media metadata backlog

For every post with media, write media metadata to:

```text
media_manifest.jsonl
```

Each line:

```json
{
  "media_id": "12345_01",
  "message_id": 12345,
  "media_index": 1,
  "media_type": "photo",
  "mime_type": "image/jpeg",
  "file_name": null,
  "file_size": 245991,
  "width": 1280,
  "height": 720,
  "duration": null,
  "local_path": "media/photos/0000012345_01.jpg",
  "sha256": null,
  "download_status": "metadata_only"
}
```

Download statuses:

```text
none
metadata_only
downloaded
skipped_by_mode
skipped_by_size
failed
```

---

# 17. Media download backlog

Only if implementing:

```text
--media full
```

Create:

```text
services/channel_export/media_downloader.py
```

Reuse patterns from private archive:

```text
services/private_archive/media_downloader.py
services/private_archive/media_policy.py
```

But do not import private archive-specific classes into channel export if semantics differ.

Requirements:

- use semaphore;
- skip existing file if present;
- compute sha256 after download;
- update media_manifest status;
- never fail whole export on one media failure unless strict mode exists;
- record failure in export.log or result.

MVP can defer full media download and implement metadata only.

---

# 18. Plan builder backlog

Файл:

```text
services/channel_export/plan_builder.py
```

Responsibility:

- create output directory path;
- sanitize username/title;
- create paths:
  - manifest;
  - messages.jsonl;
  - messages.txt;
  - media_manifest.jsonl;
  - media directories.

Directory naming:

```text
@username__channel_id
```

If username absent:

```text
channel_<channel_id>
```

If title exists but no username:

```text
<safe_title>__channel_<id>
```

Need deterministic sanitization:

- spaces -> `_`;
- remove path separators;
- remove control chars;
- length limit.

---

# 19. Renderers backlog

## 19.1. JSONL renderer

Файл:

```text
services/channel_export/jsonl_renderer.py
```

Output:

```text
messages.jsonl
```

One post = one line.

Requirements:

- UTF-8;
- `ensure_ascii=False`;
- stable keys;
- datetime ISO format;
- include relative media paths;
- do not include full raw Telethon dump by default unless already sanitized.

## 19.2. TXT renderer

Файл:

```text
services/channel_export/txt_renderer.py
```

Output:

```text
messages.txt
```

Format:

```text
[2026-05-07 12:00:00 UTC] Channel Title (@username) | message_id=12345
Text...

Media:
- photo: media/photos/0000012345_01.jpg [metadata_only]
--------------------
```

Requirements:

- stable separator;
- readable timestamps;
- include message_id;
- include media refs;
- do not include huge raw payload.

---

# 20. Manifest backlog

Файл:

```text
services/channel_export/manifest_writer.py
```

Output:

```text
manifest.json
```

Fields:

```json
{
  "dataset_type": "direct_channel_export",
  "schema_version": "1.0",
  "exported_at": "2026-05-07T12:00:00+00:00",
  "source": {
    "type": "channel",
    "id": 123456789,
    "username": "channel_name",
    "title": "Channel Name"
  },
  "export": {
    "message_count": 4521,
    "media_count": 1200,
    "downloaded_media_count": 0,
    "date_from": "2024-01-01T00:00:00+00:00",
    "date_to": "2026-05-07T00:00:00+00:00",
    "formats": ["jsonl", "txt"],
    "media_mode": "metadata",
    "included_files": [
      "messages.jsonl",
      "messages.txt",
      "media_manifest.jsonl"
    ]
  }
}
```

Requirements:

- write after successful export;
- if partial export occurs, manifest should say partial/error status;
- include schema version.

---

# 21. Payload writer backlog

Файл:

```text
services/channel_export/payload_writer.py
```

Responsibility:

- write JSONL lines;
- write TXT lines;
- write media manifest lines;
- handle UTF-8;
- optionally use atomic temp file and rename.

For MVP:

- streaming write is acceptable;
- avoid accumulating all posts in memory.

---

# 22. Service orchestration backlog

Файл:

```text
services/channel_export/service.py
```

`ChannelExportService` should orchestrate only:

1. resolve channel;
2. build plan;
3. iterate posts;
4. map post records;
5. write JSONL/TXT/media manifest;
6. optionally download media;
7. write manifest;
8. emit events;
9. return `ChannelExportResult`.

It must not:

- contain raw Telethon-specific extraction logic;
- contain filename policy;
- contain TXT/JSON rendering logic;
- contain media download details;
- contain analytics.

---

# 23. Event emitter backlog

Файл:

```text
services/channel_export/event_emitter.py
```

Events:

```text
channel_export.started
channel_export.progress
channel_export.media_skipped
channel_export.media_downloaded
channel_export.completed
channel_export.failed
```

Should use existing service event rendering style if available.

Do not make events required for unit tests.

---

# 24. Storage backlog

MVP direct channel export can be **filesystem-only**.

Do not immediately write channel posts into SQLite unless there is a clear reason.

Reason:

- current SQLite schema is user-message oriented;
- adding channels/source identities to DB needs schema design;
- direct dataset export can work without schema migration.

## 24.1. Recommended MVP

No DB schema changes.

Use Telegram API → dataset files.

## 24.2. Future DB stage

Later, if needed:

```text
source_identities
source_export_runs
source_message_links
```

But do not do this in Stage 3A.

---

# 25. Tests backlog

## 25.1. Unit tests

Create:

```text
tests/test_channel_export_plan_builder.py
tests/test_channel_export_renderers.py
tests/test_channel_export_manifest.py
tests/test_channel_export_media_policy.py
tests/test_channel_export_service.py
tests/test_cli_export_channel.py
```

## 25.2. Test plan builder

Check:

- username path;
- no username path;
- unsafe chars sanitized;
- media directories created or planned;
- paths stable.

## 25.3. Test JSONL renderer

Check:

- one record = one line;
- datetime ISO;
- UTF-8;
- media local_path included;
- no Python object repr leakage.

## 25.4. Test TXT renderer

Check:

- message_id included;
- text included;
- media list included;
- separator stable;
- empty text handled.

## 25.5. Test manifest

Check:

- dataset_type;
- schema_version;
- source block;
- message_count;
- media_mode;
- included files.

## 25.6. Test media policy

Check:

- photo category;
- video category;
- document fallback;
- target filename stable;
- metadata mode does not download;
- full mode requests download.

## 25.7. Test service with fake client

Use existing fake/testing infrastructure if possible:

```text
tg_msg_manager/testing/
```

Fake client should yield channel messages.

Test:

- service writes all files;
- service handles empty channel;
- service handles post with media metadata;
- service handles media download failure without crashing whole export if non-strict.

## 25.8. CLI tests

Check:

- `export-channel --help`;
- required `--channel`;
- `--media` choices;
- handler wiring.

---

# 26. Live smoke checklist backlog

Update:

```text
docs/testing/LIVE_SMOKE_CHECKLIST.md
```

Add:

```markdown
### Direct channel export

Command:
python3 -m tg_msg_manager.cli export-channel --channel "$TEST_CHANNEL" --limit 3 --media metadata

Expected:
- exit code 0
- output directory under exports/channels/
- manifest.json exists
- messages.jsonl exists
- messages.txt exists
- media_manifest.jsonl exists
- no full media downloaded in metadata mode
```

Add optional full media smoke:

```bash
python3 -m tg_msg_manager.cli export-channel --channel "$TEST_CHANNEL" --limit 1 --media full
```

Mark it as non-routine because it downloads files.

---

# 27. Documentation backlog

Update:

```text
README.md
COMMANDS.md
PROJECT_ARCHITECTURE_OVERVIEW.md
CHANGELOG.md
docs/ARCHITECTURE_RULES.md
docs/PR_CHECKLIST.md
```

## 27.1. README

Add quick examples:

```bash
python3 -m tg_msg_manager.cli export-channel --channel @example --limit 100 --media metadata
python3 -m tg_msg_manager.cli export-channel --channel @example --limit 10 --media full
```

## 27.2. COMMANDS.md

Document all args.

## 27.3. Architecture overview

Add:

```text
ChannelExportService is filesystem-first dataset projection.
It does not write channel posts to SQLite in Stage 3A.
It does not perform analytics.
```

## 27.4. Changelog

Add entry:

```markdown
## Stage 3A — Direct Channel Export

- Added direct Telegram channel export command.
- Added channel dataset layout with manifest/messages/media manifest.
- Added media metadata export.
- Added optional full media download mode.
```

Only claim full media if implemented.

---

# 28. AGENTS.md / architecture rules update

Add rules:

```markdown
## Channel Export

Direct channel export must live under `services/channel_export/`.

It must not be added to:
- ExportService
- DBExportService
- PrivateArchiveService
- ContextEngine

Channel export is a dataset projection layer, not an analytics layer.

MVP channel export must be filesystem-first and must not require SQLite schema changes.

Media download must be optional. Default media mode must not download full media.
```

---

# 29. Implementation order

Recommended order:

```text
1. Add models.
2. Add plan_builder.
3. Add manifest_writer.
4. Add JSONL/TXT renderers.
5. Add media_policy metadata mode.
6. Add source_resolver.
7. Add post_fetcher.
8. Add post_mapper.
9. Add service orchestration.
10. Add CLI parser.
11. Add CLI handler/context wiring.
12. Add tests.
13. Add live smoke checklist.
14. Add docs/changelog.
15. Optional: add media full downloader.
```

If implementing full media download, do it after metadata mode works.

---

# 30. Acceptance criteria

Stage 3A is done if:

- [ ] `export-channel` command exists.
- [ ] `--channel` is required.
- [ ] `--limit` works.
- [ ] `--media metadata` is default.
- [ ] direct channel messages are exported from Telegram API.
- [ ] output directory is deterministic.
- [ ] `manifest.json` is written.
- [ ] `messages.jsonl` is written.
- [ ] `messages.txt` is written.
- [ ] `media_manifest.jsonl` is written.
- [ ] media metadata is captured.
- [ ] full media is not downloaded by default.
- [ ] no analytics is performed.
- [ ] no SQLite schema migration is required for MVP.
- [ ] tests pass.
- [ ] live smoke checklist updated.
- [ ] docs updated.
- [ ] existing commands still work.

---

# 31. Deferred tasks

Do not implement in Stage 3A:

```text
Stage 3B — Full Media Download Hardening
  - resume
  - sha256
  - max media size
  - media type allowlist
  - thumbnails

Stage 3C — Channel Discussion Context Export
  - linked discussion group
  - comments/replies
  - post-to-discussion mapping

Stage 3D — Source Export from Groups
  - sender_chat
  - forward_origin
  - anonymous admin
  - authored-as-channel in groups

Stage 4 — Dataset Analysis Prompt Packs
  - prepared prompts for LLM analysis
  - no built-in scoring
```

---

# 32. Risks

## 32.1. Telegram access

Export only works if current Telegram account can access the channel.

## 32.2. Large channels

Large channels can produce huge JSONL/TXT/media outputs.

Mitigation:

- support `--limit`;
- later add date filters;
- default media metadata only.

## 32.3. Media size

Full media download can be very large.

Mitigation:

- do not default to full;
- later add max size and allowlist.

## 32.4. Raw payload instability

Telethon raw payload fields may vary.

Mitigation:

- schema should tolerate `None`;
- keep raw extraction defensive;
- tests should cover missing fields.

## 32.5. Scope creep

This feature can easily become analytics.

Mitigation:

- no interpretation in Stage 3A;
- only dataset export.
