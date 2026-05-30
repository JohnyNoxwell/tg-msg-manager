# Stage 5B.0 - baseline масштабируемости перед growth hardening

## Статус

- Статус: завершено.
- Тип: report-only baseline.
- Поведение кода: не менялось.
- Runtime code/tests: не изменялись.
- SQLite schema/migrations: не изменялись.

## Примененные skill

- stage-reviewer: applied from .skills/stage-reviewer/SKILL.md; verdict pass; blockers none; risk low.
- architecture-guard: applied from .skills/architecture-guard/SKILL.md; verdict pass; violations none; risk low.
- stage-completion-auditor: applied from .skills/stage-completion-auditor/SKILL.md; verdict complete; blockers none.

## Проверенные документы

- `AGENTS.md`
- `docs/stages/active/stage_5b_0_scalability_baseline_before_growth_hardening.md`
- `docs/stages/README.md`
- `docs/architecture/README.md`
- `docs/architecture/ARCHITECTURE_RULES.md`
- `docs/development/README.md`

## Line counts

- `tg_msg_manager/infrastructure/storage/sqlite.py`: 92
- `tg_msg_manager/infrastructure/storage/_sqlite_write_path.py`: 242
- `tg_msg_manager/infrastructure/storage/write/message_writer.py`: 199
- `tg_msg_manager/infrastructure/storage/_sqlite_schema.py`: 1175
- `tg_msg_manager/services/private_archive/service.py`: 109
- `tg_msg_manager/services/private_archive/stream_processor.py`: 123
- `tg_msg_manager/services/channel_export/workflows/full_export.py`: 93
- `tg_msg_manager/services/channel_export/workflows/incremental_export.py`: 121
- `tg_msg_manager/services/channel_export/run_changelog.py`: 96
- `tg_msg_manager/services/channel_export/discussions/exporter.py`: 412
- `tg_msg_manager/services/channel_export/discussions/fetcher.py`: 83
- `tg_msg_manager/services/db_export/summary.py`: 290
- `tg_msg_manager/services/db_export/payload_writer.py`: 179
- `tg_msg_manager/infrastructure/storage/read/exports.py`: 359
- Runtime hot-path total: 3573
- `tests/services/private_archive/test_private_archive_components.py`: 239
- `tests/infrastructure/storage/test_storage_sqlite.py`: 2143
- `tests/services/channel_export/`: 28 files, 6005 total lines
- `tests/services/db_export/`: 4 files, 1210 total lines

## Найденные code-evident bottlenecks

### SQLite write queue / transaction path

- `tg_msg_manager/infrastructure/storage/sqlite.py:45`: `_write_queue = asyncio.Queue()` без заданного `maxsize`; producer-side backpressure не задан.
- `tg_msg_manager/infrastructure/storage/_sqlite_write_path.py:30` и `:47-48`: `put_nowait` кладет одиночные и batch messages без ожидания емкости очереди.
- `tg_msg_manager/infrastructure/storage/_sqlite_write_path.py:25-34`: `save_message(..., flush=True)` по умолчанию сразу вызывает `flush`; `sqlite.py:76-80` ждет `queue.join()`.
- `tg_msg_manager/infrastructure/storage/_sqlite_write_path.py:78-85`: background writer собирает максимум 500 items и пишет их через `to_thread`.
- `tg_msg_manager/infrastructure/storage/write/message_writer.py:38-47`: batch сохраняется в одной write transaction, но внутри идет per-message loop.
- `tg_msg_manager/infrastructure/storage/write/message_writer.py:59-155`: каждый message проходит SELECT, target link, user/chat/context upserts, message upsert, reply-state refresh и sync-state update.
- Follow-up: Stage 5B.4.

### Private archive per-message persistence

- `tg_msg_manager/services/private_archive/stream_processor.py:101-114`: Telegram stream обрабатывается последовательно.
- `tg_msg_manager/services/private_archive/stream_processor.py:79`: каждый message вызывает `storage.save_message(message, target_id=user_id)` без `flush=False`, значит используется default flush из `_sqlite_write_path.py:25-34`.
- `tg_msg_manager/services/private_archive/stream_processor.py:56-59` и `:80-86`: media download и file append await-ятся последовательно для каждого message.
- `tg_msg_manager/services/private_archive/service.py:46`: semaphore на 3 download slots существует, но в проверенном stream path нет параллельного scheduling.
- Follow-up: Stage 5B.1.

### Channel export post buffering

- `tg_msg_manager/services/channel_export/workflows/full_export.py:34-47`: full export пишет record и одновременно накапливает весь `current_run_records`.
- `tg_msg_manager/services/channel_export/workflows/full_export.py:50-57`: discussion export запускается после полного накопления posts.
- `tg_msg_manager/services/channel_export/workflows/full_export.py:71-79`: run changelog получает `tuple(current_run_records)`.
- `tg_msg_manager/services/channel_export/workflows/incremental_export.py:27-43`: incremental export накапливает все `mapped_records`, затем сортирует весь список.
- `tg_msg_manager/services/channel_export/workflows/incremental_export.py:99-107`: run changelog получает `tuple(mapped_records)`.
- `tg_msg_manager/services/channel_export/run_changelog.py:43`: changelog материализует `new_message_ids` для всех posts.
- Follow-up: Stage 5B.2.

### Discussion fetch/write pressure

- `tg_msg_manager/services/channel_export/discussions/exporter.py:119-130`: posts обрабатываются последовательно; thread и comments пишутся внутри одного session loop.
- `tg_msg_manager/services/channel_export/discussions/exporter.py:253-258`: для каждого post выполняется отдельный `fetch_comments_for_post`.
- `tg_msg_manager/services/channel_export/discussions/fetcher.py:19-35`: comments накапливаются в list, обрезаются и сортируются; размер ограничен `max_comments_per_post + 1`.
- `tg_msg_manager/services/channel_export/discussions/exporter.py:275-283`: mapped comments материализуются в tuple перед записью.
- Follow-up: Stage 5B.2.

### DB export memory/materialization paths

- `tg_msg_manager/infrastructure/storage/read/exports.py:56-67`: `get_user_messages` делает `fetchall()` и возвращает list `MessageData`.
- `tg_msg_manager/services/db_export/summary.py:117`: fallback path загружает все user messages.
- `tg_msg_manager/services/db_export/summary.py:192-199`: incremental fallback строит `messages = []` и append-ит все новые messages.
- `tg_msg_manager/services/db_export/summary.py:268-269`: fallback plan создает list и сортирует messages.
- `tg_msg_manager/infrastructure/storage/read/exports.py:203-242` и `:244-297`: streaming iterators используют `fetchmany(chunk_size=1000)` и являются bounded alternative.
- `tg_msg_manager/infrastructure/storage/read/exports.py:299-323` и `:325-359`: legacy row getters используют `fetchall()`.
- `tg_msg_manager/services/db_export/payload_writer.py:89-93`: TXT path строит `msg_lookup` по всем `source.messages`.
- `tg_msg_manager/services/db_export/payload_writer.py:95-106`: context-readable TXT path материализует `records = list(...)` и рендерит весь content перед записью.
- `tg_msg_manager/services/db_export/payload_writer.py:118-163`: обычный writer буферизует только batch blocks (`100`, `500`, `1000`), что ограничивает pending buffer.
- Follow-up: Stage 5B.3.

### SQLite schema module growth

- `tg_msg_manager/infrastructure/storage/_sqlite_schema.py:20-31`: один mixin orchestrates create/ensure/index/migration flow.
- `tg_msg_manager/infrastructure/storage/_sqlite_schema.py:36-181`: table creation for multiple domains находится в одном файле.
- `tg_msg_manager/infrastructure/storage/_sqlite_schema.py:183-214`: index creation также находится в этом же module.
- `tg_msg_manager/infrastructure/storage/_sqlite_schema.py:216-261`: ensure-column helpers смешаны с schema creation.
- `tg_msg_manager/infrastructure/storage/_sqlite_schema.py:263-416`: version migrations v2-v14 находятся в одном method.
- `tg_msg_manager/infrastructure/storage/_sqlite_schema.py:510-1175`: large table migration/backfill helpers остаются в этом же file.
- Follow-up: Stage 5B.5.

## Test evidence inspected

- `tests/infrastructure/storage/test_storage_sqlite.py:96-116`: batch save covered for 10 messages.
- `tests/infrastructure/storage/test_storage_sqlite.py:322-327`: export row iterator covered with `chunk_size=2`.
- `tests/services/private_archive/test_private_archive_components.py:74-144`: stream processor covers empty and one-message sequential flows.
- `tests/services/channel_export/discussions/test_channel_export_discussion_fetcher.py:61-76`: discussion fetcher covers `max_comments_per_post + 1` behavior.
- `tests/services/db_export/test_db_exporter.py:357-370`: AI JSON export uses iterator and avoids `get_user_messages`.

## Команды и результаты

- `wc -l <listed runtime hot-path files and direct test files>`: passed; total 5955.
- `wc -l <tests/services/channel_export/* and tests/services/db_export/*>`: passed; total 7215.
- `python3 -m compileall tg_msg_manager`: passed.
- `ruff check tg_msg_manager tests`: passed.
- `git diff --check`: passed.

## Измененные файлы

- `docs/stages/reports/STAGE_5B_0_SCALABILITY_BASELINE_REPORT.md`: создан factual report.
- `docs/stages/active/stage_5b_0_scalability_baseline_before_growth_hardening.md`: перемещен после завершения stage.
- `docs/stages/completed/stage_5b_0_scalability_baseline_before_growth_hardening.md`: создан lifecycle move.
- `docs/stages/README.md`: обновлен active/completed/report index для Stage 5B.0.

## Scope confirmation

- Runtime code changed: no.
- Tests changed: no.
- CLI changed: no.
- SQLite schema changed: no.
- Dataset/export formats changed: no.
- Report authorizes implementation: no; findings map only to active follow-up Stage 5B.1-5B.5.
