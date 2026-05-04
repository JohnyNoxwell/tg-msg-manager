# SQLite Architecture Hardening TODO

## Progress note — 2026-05-04

Implemented slices from this TODO:

- added `users.current_author_name`;
- added `user_identity_history`;
- added migration/backfill for current author name and identity history;
- kept `messages.author_name` as historical message-time data;
- wired `register_target()` / `save_message()` so target/user current author name stays fresh.
- added `scripts/db_diagnostics.py`;
- added baseline/smoke/audit docs for SQLite hardening;
- added chat-safe `message_context_links` schema for fresh databases;
- added migration from legacy `message_context_links(message_id, context_message_id, link_type)` to chat-safe rows with preserved backup table;
- wired new reply context-link writes with `chat_id`, `distance`, `algorithm_version`, and `created_at`.
- added DB-backed `export_targets` table;
- added migration/backfill for tracked users into `export_targets`;
- wired `DBExportService` to persist export target filename/path/cursor/current identity into SQLite.

Still pending from the larger TODO:

- `export_runs`;
- DB-backed incremental export cursor/update flow;
- broader message-link hardening around `(chat_id, message_id)`.

## 0. Контекст и цель

Проект использует SQLite-базу `messages.db` для хранения Telegram-сообщений и последующего экспорта сообщений по пользователям, reply-контексту и контекстным окнам.

Текущая архитектура рабочая, но требует стабилизации перед расширением функционала. Основные риски:

1. В Telegram `message_id` уникален только внутри конкретного чата, а не глобально.
2. Часть таблиц связей использует только `message_id`, без `chat_id`.
3. Нет полноценной модели состояния экспорта.
4. Контекстные связи недостаточно типизированы.
5. Производные данные не имеют версии алгоритма.
6. Reply-граф частично неполный: часть `reply_to_id` указывает на сообщения, отсутствующие в базе.
7. Будущие функции вроде thread reconstruction, user dossier export, social graph и context-aware export update будут сложнее без схемной стабилизации.

Цель этого этапа — не переписать проект полностью, а укрепить схему базы, read-side запросы и экспортную модель так, чтобы дальнейшее расширение не ломало существующее поведение.

---

# 1. Жесткие ограничения

## 1.1. Не менять публичное CLI-поведение

### Задача
Сохранить совместимость текущего CLI.

### Атомарные требования

- Не переименовывать существующие CLI-команды без отдельного решения.
- Не менять формат обязательных аргументов CLI.
- Не менять существующие дефолтные значения без отдельного решения.
- Не менять текущий формат экспортируемых файлов, если это не вынесено в отдельный explicit migration step.
- Не удалять существующие команды.
- Не ломать уже существующие smoke-сценарии.
- Все изменения должны быть обратно совместимыми на уровне пользовательского сценария.

### Критерий приемки

Существующие команды запускаются так же, как до изменений.

---

## 1.2. Не добавлять новые фичи в hot-path файлы

### Задака
Остановить дальнейшее разрастание файлов, которые уже перегружены логикой.

### Атомарные требования

- Не добавлять новую бизнес-логику в перегруженные сервисы экспорта.
- Не добавлять новую SQL-логику прямо в CLI handlers.
- Не добавлять thread/social graph/profiling функции на этом этапе.
- Разрешены только изменения, необходимые для стабилизации схемы, миграций, индексов и export-state.
- Если существующий файл слишком большой, новая логика выносится в отдельный модуль.

### Критерий приемки

Новые изменения разделены по модулям: миграции, репозитории, сервисы, DTO/модели, тесты.

---

# 2. Зафиксировать текущее состояние перед изменениями

## 2.1. Создать baseline-проверки базы

### Задача
Перед миграциями зафиксировать текущее состояние базы и ожидания.

### Подзадачи

#### 2.1.1. Добавить скрипт диагностики схемы

Создать скрипт, например:

```text
scripts/db_diagnostics.py
```

Скрипт должен выводить:

- список таблиц;
- список колонок по каждой таблице;
- список индексов;
- количество записей в ключевых таблицах;
- `PRAGMA integrity_check`;
- `PRAGMA journal_mode`;
- диапазон timestamp в `messages`;
- количество сообщений;
- количество пользователей;
- количество чатов;
- количество reply-ссылок;
- количество missing reply references.

#### 2.1.2. Добавить диагностику качества данных

Проверять:

- сообщения без `user_id`;
- сообщения без `text` и без `media_type`;
- дубликаты по `(chat_id, message_id)`;
- дубликаты по `payload_hash`;
- `reply_to_id`, указывающие на отсутствующее сообщение;
- context links, указывающие на отсутствующее сообщение;
- target links, указывающие на отсутствующее сообщение;
- target links, указывающие на отсутствующего пользователя.

#### 2.1.3. Сохранить baseline-output

Добавить пример результата диагностики в файл:

```text
docs/db_baseline_report.md
```

Файл должен содержать дату проверки, имя базы и краткий вывод.

### Критерий приемки

Есть один скрипт, который можно запустить на текущей базе и получить воспроизводимый отчет о состоянии схемы и данных.

---

## 2.2. Зафиксировать smoke-сценарии экспорта

### Задача
Перед изменениями убедиться, что после миграций экспорт работает так же.

### Подзадачи

#### 2.2.1. Описать ручные smoke-сценарии

Создать файл:

```text
docs/export_smoke_scenarios.md
```

Описать минимум:

1. Экспорт сообщений одного пользователя по `user_id`.
2. Экспорт пользователя с reply-контекстом.
3. Экспорт пользователя с context window.
4. Повторный export/update без новых сообщений.
5. Повторный export/update с новыми сообщениями.
6. Экспорт пользователя, который менял ник.
7. Экспорт сообщения, у которого `reply_to_id` отсутствует в базе.

#### 2.2.2. Добавить технические проверки результата

Для каждого сценария описать:

- входные аргументы;
- ожидаемый файл;
- ожидаемое количество новых сообщений;
- ожидаемое поведение при отсутствии новых сообщений;
- ожидаемое поведение при missing reply;
- ожидаемое поведение при смене ника.

### Критерий приемки

Перед миграцией есть документированный набор smoke-сценариев, по которому можно проверить, что CLI-поведение не сломано.

---

# 3. Нормализовать идентификацию сообщений

## 3.1. Зафиксировать архитектурное правило

### Задача
Ввести единый принцип идентификации сообщений.

### Правило

Любое сообщение Telegram должно идентифицироваться парой:

```text
(chat_id, message_id)
```

`message_id` без `chat_id` запрещен для связей между таблицами.

### Атомарные требования

- Добавить это правило в архитектурный документ.
- Найти все места в коде, где используется только `message_id`.
- Классифицировать найденные места:
  - безопасное использование внутри одного уже выбранного `chat_id`;
  - небезопасное использование в связях;
  - небезопасное использование в export/update;
  - небезопасное использование в context/reply logic.
- Не менять все сразу вслепую.
- Сначала составить список мест, затем мигрировать.

### Критерий приемки

Есть документированный список мест, где `message_id` используется без `chat_id`, и план их замены.

---

## 3.2. Проверить таблицу `messages`

### Задача
Убедиться, что `messages` имеет корректный уникальный ключ.

### Подзадачи

#### 3.2.1. Проверить наличие уникальности

Проверить, есть ли уникальный индекс или primary key на:

```text
(chat_id, message_id)
```

#### 3.2.2. Если уникальности нет — добавить миграцию

Добавить индекс:

```sql
CREATE UNIQUE INDEX IF NOT EXISTS idx_messages_chat_message_unique
ON messages(chat_id, message_id);
```

#### 3.2.3. Проверить дубликаты перед миграцией

Перед созданием уникального индекса выполнить проверку:

```sql
SELECT chat_id, message_id, COUNT(*)
FROM messages
GROUP BY chat_id, message_id
HAVING COUNT(*) > 1;
```

#### 3.2.4. Если дубликаты есть — не выполнять destructive fix

Если найдены дубликаты:

- не удалять их автоматически;
- вывести ошибку миграции;
- создать diagnostic report;
- остановить миграцию.

### Критерий приемки

`messages` гарантирует уникальность `(chat_id, message_id)`.

---

## 3.3. Мигрировать `message_context_links`

### Задача
Сделать context links безопасными для нескольких чатов.

### Целевая логика

Таблица должна хранить минимум:

```text
chat_id
message_id
context_message_id
link_type
distance
algorithm_version
created_at
```

### Подзадачи

#### 3.3.1. Проверить текущую структуру

Определить фактические колонки таблицы:

```sql
PRAGMA table_info(message_context_links);
```

#### 3.3.2. Создать новую таблицу

Создать временную таблицу:

```sql
CREATE TABLE message_context_links_new (
    chat_id INTEGER NOT NULL,
    message_id INTEGER NOT NULL,
    context_message_id INTEGER NOT NULL,
    link_type TEXT NOT NULL DEFAULT 'unknown',
    distance INTEGER,
    algorithm_version TEXT NOT NULL DEFAULT 'legacy',
    created_at INTEGER NOT NULL,
    PRIMARY KEY (chat_id, message_id, context_message_id, link_type, algorithm_version),
    FOREIGN KEY (chat_id, message_id)
        REFERENCES messages(chat_id, message_id),
    FOREIGN KEY (chat_id, context_message_id)
        REFERENCES messages(chat_id, message_id)
);
```

#### 3.3.3. Перенести старые данные

Так как сейчас база содержит один чат, можно определить `chat_id` из таблицы `chats` или из `messages`.

Алгоритм:

1. Если в базе один чат — использовать его `chat_id`.
2. Если чатов больше одного — попытаться восстановить `chat_id` через join с `messages`.
3. Если восстановить невозможно — остановить миграцию и вывести ошибку.

#### 3.3.4. Проставить legacy metadata

Для старых записей:

```text
link_type = 'legacy'
algorithm_version = 'legacy'
created_at = текущий unix timestamp
distance = NULL
```

#### 3.3.5. Проверить ссылочную целостность

Проверить, что каждая связь указывает на существующие сообщения:

```sql
SELECT COUNT(*)
FROM message_context_links_new l
LEFT JOIN messages m1
  ON m1.chat_id = l.chat_id AND m1.message_id = l.message_id
LEFT JOIN messages m2
  ON m2.chat_id = l.chat_id AND m2.message_id = l.context_message_id
WHERE m1.message_id IS NULL OR m2.message_id IS NULL;
```

#### 3.3.6. Заменить старую таблицу

После успешной проверки:

- переименовать старую таблицу в backup;
- переименовать новую таблицу в `message_context_links`;
- создать индексы;
- не удалять backup-таблицу в первой версии миграции.

### Критерий приемки

`message_context_links` больше не зависит от глобальной уникальности `message_id`.

---

## 3.4. Мигрировать `message_target_links`

### Задача
Убедиться, что связь target-user → message также использует `(chat_id, message_id)`.

### Целевая структура

```text
target_user_id
chat_id
message_id
link_type
created_at
```

### Подзадачи

#### 3.4.1. Проверить текущие колонки

Выполнить:

```sql
PRAGMA table_info(message_target_links);
```

#### 3.4.2. Добавить `chat_id`, если отсутствует

Если `chat_id` отсутствует:

- создать новую таблицу `message_target_links_new`;
- восстановить `chat_id` через join с `messages`;
- перенести данные;
- проверить ссылочную целостность.

#### 3.4.3. Добавить `link_type`

Добавить тип связи:

```text
target_author
reply_context
window_context
mention_context
legacy
```

Если старая логика не различает типы — использовать:

```text
legacy
```

#### 3.4.4. Добавить `created_at`

Для старых строк использовать текущий unix timestamp или timestamp миграции.

#### 3.4.5. Создать индексы

Минимум:

```sql
CREATE INDEX IF NOT EXISTS idx_message_target_links_target
ON message_target_links(target_user_id);

CREATE INDEX IF NOT EXISTS idx_message_target_links_message
ON message_target_links(chat_id, message_id);

CREATE INDEX IF NOT EXISTS idx_message_target_links_target_message
ON message_target_links(target_user_id, chat_id, message_id);
```

### Критерий приемки

Все target links однозначно указывают на конкретное сообщение в конкретном чате.

---

# 4. Ввести модель состояния экспорта

## 4.1. Добавить таблицу `export_targets`

### Задача
Хранить состояние экспорта каждого пользователя в базе, а не только в файловой системе.

### Целевая структура

```sql
CREATE TABLE IF NOT EXISTS export_targets (
    target_user_id INTEGER PRIMARY KEY,
    export_filename TEXT,
    export_dir TEXT,
    last_exported_message_ts INTEGER,
    last_exported_message_id INTEGER,
    last_known_author_name TEXT,
    last_known_username TEXT,
    created_at INTEGER NOT NULL,
    updated_at INTEGER NOT NULL
);
```

### Подзадачи

#### 4.1.1. Создать миграцию

Добавить миграцию, которая создает таблицу, если ее нет.

#### 4.1.2. Заполнить из существующих данных

Для каждого уже отслеживаемого пользователя:

- взять `target_user_id` из `sync_targets` или текущих export settings;
- определить последний экспортированный message timestamp, если возможно;
- если невозможно — оставить `NULL`;
- определить актуальный nickname из `users` или последних сообщений;
- определить username, если он есть.

#### 4.1.3. Не доверять имени файла как источнику истины

Файл экспорта может быть переименован, ник мог измениться. Основной идентификатор — `target_user_id`.

#### 4.1.4. Поддержать папку `EXPORTED_USRS`

Если текущая логика использует папку `EXPORTED_USRS`, таблица должна хранить путь или имя файла, но не заменять `target_user_id` файловым именем.

### Критерий приемки

Для каждого экспортируемого пользователя база может сказать:

- кто экспортируется;
- куда экспортируется;
- до какого сообщения экспорт выполнен;
- какой последний известный nickname/username.

---

## 4.2. Добавить таблицу `export_runs`

### Задача
Хранить журнал запусков экспорта.

### Целевая структура

```sql
CREATE TABLE IF NOT EXISTS export_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    target_user_id INTEGER NOT NULL,
    started_at INTEGER NOT NULL,
    finished_at INTEGER,
    new_messages_count INTEGER NOT NULL DEFAULT 0,
    last_new_message_ts INTEGER,
    status TEXT NOT NULL,
    error TEXT,
    FOREIGN KEY (target_user_id)
        REFERENCES export_targets(target_user_id)
);
```

### Подзадачи

#### 4.2.1. Логировать старт экспорта

При запуске export/update создавать запись:

```text
status = 'running'
started_at = now
```

#### 4.2.2. Логировать успешное завершение

После успешного завершения:

```text
status = 'success'
finished_at = now
new_messages_count = N
last_new_message_ts = timestamp последнего нового сообщения
```

#### 4.2.3. Логировать ошибку

При ошибке:

```text
status = 'failed'
finished_at = now
error = текст ошибки
```

#### 4.2.4. Не скрывать частичные ошибки

Если часть сообщений экспортировалась, но затем произошла ошибка:

- записать `status = 'failed'`;
- сохранить количество уже обработанных сообщений;
- сохранить error;
- не обновлять `last_exported_message_ts`, если экспорт не завершился атомарно.

### Критерий приемки

Каждый запуск export/update оставляет запись в `export_runs`.

---

## 4.3. Перевести export update на DB-backed state

### Задача
`export update` должен определять новые сообщения через базу, а не через парсинг уже экспортированного текстового файла.

### Логика

Для пользователя:

1. Найти `target_user_id`.
2. Прочитать `last_exported_message_ts` и `last_exported_message_id`.
3. Найти сообщения пользователя после этой точки.
4. Экспортировать только новые.
5. Обновить `export_targets`.
6. Записать `export_runs`.

### Подзадачи

#### 4.3.1. Реализовать функцию получения export cursor

Функция должна возвращать:

```text
target_user_id
last_exported_message_ts
last_exported_message_id
export_filename
last_known_author_name
last_known_username
```

#### 4.3.2. Реализовать функцию поиска новых сообщений

Запрос должен учитывать:

```text
user_id = target_user_id
timestamp > last_exported_message_ts
```

Если timestamp совпадает, использовать `message_id` как tie-breaker.

#### 4.3.3. Обработать первый экспорт

Если cursor отсутствует:

- считать это первым экспортом;
- экспортировать все сообщения пользователя;
- создать запись в `export_targets`.

#### 4.3.4. Обработать отсутствие новых сообщений

Если новых сообщений нет:

- не менять файл;
- создать `export_runs` со статусом `success`;
- `new_messages_count = 0`.

#### 4.3.5. Обновлять cursor только после успешной записи файла

Порядок должен быть:

1. Найти новые сообщения.
2. Сформировать текст.
3. Записать файл.
4. Проверить, что запись завершилась.
5. Обновить `export_targets`.
6. Закрыть `export_runs` как success.

### Критерий приемки

Повторный `export update` не дублирует сообщения и корректно добавляет только новые.

---

# 5. Типизировать контекстные связи

## 5.1. Ввести enum-like значения `link_type`

### Задача
Контекст должен объяснять, почему сообщение попало в экспорт.

### Допустимые значения

```text
target_message
reply_parent
reply_child
window_before
window_after
same_thread
mention
legacy
unknown
```

### Подзадачи

#### 5.1.1. Добавить константы в код

Создать модуль, например:

```text
src/db/link_types.py
```

Или использовать существующий модуль constants.

#### 5.1.2. Заменить строковые литералы

Не использовать произвольные строки по проекту. Все значения брать из констант.

#### 5.1.3. Добавить validation helper

Функция:

```text
validate_context_link_type(value: str) -> bool
```

Или выбрасывать исключение при недопустимом типе.

#### 5.1.4. Использовать `legacy` для старых связей

Все старые связи после миграции должны иметь `legacy`, если невозможно определить точный тип.

### Критерий приемки

По каждой context-связи можно понять, каким алгоритмом и по какой причине она была создана.

---

## 5.2. Добавить `distance` для window context

### Задача
Хранить позицию контекстного сообщения относительно целевого.

### Логика

Для сообщения цели:

```text
distance = 0
```

Для сообщений до цели:

```text
-1, -2, -3...
```

Для сообщений после цели:

```text
+1, +2, +3...
```

Для reply-связей distance может быть `NULL`.

### Подзадачи

#### 5.2.1. Изменить построитель context window

Когда создается окно N/M:

- target message получает `link_type = target_message`, `distance = 0`;
- сообщения до цели получают `link_type = window_before`, `distance < 0`;
- сообщения после цели получают `link_type = window_after`, `distance > 0`.

#### 5.2.2. Не смешивать reply и window context

Если сообщение попало и как reply-parent, и как window-before:

- разрешить две связи с разными `link_type`;
- не затирать одну другой;
- primary key должен учитывать `link_type`.

#### 5.2.3. Добавить тест на порядок

Проверить, что экспорт сортирует контекст по timestamp/message_id, а не по порядку вставки в таблицу.

### Критерий приемки

Контекстное окно можно восстановить из базы без повторного пересчета.

---

# 6. Версионировать производные алгоритмы

## 6.1. Добавить `algorithm_version`

### Задача
Отличать старые context links от новых.

### Требование

Каждая производная связь должна иметь:

```text
algorithm_version
created_at
```

### Подзадачи

#### 6.1.1. Ввести текущую версию алгоритма

Например:

```text
context_window_v1
reply_context_v1
legacy
```

#### 6.1.2. Использовать версию при построении связей

Любой новый context link должен записываться с текущей версией.

#### 6.1.3. Добавить возможность пересчета

Добавить внутренний метод:

```text
rebuild_context_links(algorithm_version: str)
```

Метод должен:

- удалять только связи указанной версии;
- не трогать `legacy`, если явно не указано;
- пересоздавать связи по текущей логике.

#### 6.1.4. Не делать автоматический destructive rebuild

Пересчет не должен запускаться сам при обычном экспорте.

### Критерий приемки

После изменения эвристики можно пересчитать только нужные derived links без повреждения raw messages.

---

# 7. Обработать missing reply references

## 7.1. Добавить таблицу `missing_reply_refs`

### Задача
Явно хранить reply-ссылки, которые указывают на отсутствующие сообщения.

### Целевая структура

```sql
CREATE TABLE IF NOT EXISTS missing_reply_refs (
    chat_id INTEGER NOT NULL,
    message_id INTEGER NOT NULL,
    missing_reply_to_id INTEGER NOT NULL,
    detected_at INTEGER NOT NULL,
    status TEXT NOT NULL DEFAULT 'missing',
    PRIMARY KEY (chat_id, message_id, missing_reply_to_id)
);
```

### Подзадачи

#### 7.1.1. Добавить миграцию

Создать таблицу, если ее нет.

#### 7.1.2. Написать scanner

Scanner должен находить:

```sql
SELECT m.chat_id, m.message_id, m.reply_to_id
FROM messages m
LEFT JOIN messages r
  ON r.chat_id = m.chat_id
 AND r.message_id = m.reply_to_id
WHERE m.reply_to_id IS NOT NULL
  AND r.message_id IS NULL;
```

#### 7.1.3. Записывать найденные ссылки

Каждую missing reply записывать в `missing_reply_refs`.

#### 7.1.4. Не считать missing reply критической ошибкой экспорта

Если reply отсутствует:

- экспортировать целевое сообщение;
- добавить в экспорт техническую пометку;
- не падать.

Пример пометки:

```text
[reply_to: 123456 — original message not found in local DB]
```

#### 7.1.5. Подготовить future hook для догрузки

Добавить placeholder-метод:

```text
try_fetch_missing_reply(chat_id, missing_reply_to_id)
```

Пока метод может быть заглушкой.

### Критерий приемки

Missing replies видны в базе и не ломают экспорт.

---

# 8. Индексы под экспортные запросы

## 8.1. Добавить индексы для `messages`

### Задача
Оптимизировать основные выборки экспорта.

### Индексы

```sql
CREATE INDEX IF NOT EXISTS idx_messages_user_ts
ON messages(user_id, timestamp);

CREATE INDEX IF NOT EXISTS idx_messages_chat_message
ON messages(chat_id, message_id);

CREATE INDEX IF NOT EXISTS idx_messages_chat_reply
ON messages(chat_id, reply_to_id);

CREATE INDEX IF NOT EXISTS idx_messages_context_group
ON messages(context_group_id);
```

### Подзадачи

#### 8.1.1. Проверить существующие индексы

Перед добавлением выполнить:

```sql
PRAGMA index_list(messages);
```

#### 8.1.2. Не создавать дублирующие индексы

Если аналогичный индекс уже есть — не добавлять новый.

#### 8.1.3. Проверить query plan

Для основных запросов выполнить:

```sql
EXPLAIN QUERY PLAN ...
```

Минимум проверить:

- выборка сообщений пользователя по timestamp;
- выборка reply-parent;
- выборка context group;
- выборка сообщений после export cursor.

### Критерий приемки

Основные export-запросы используют индексы.

---

## 8.2. Добавить индексы для link tables

### Задача
Ускорить выборки связей.

### Индексы

```sql
CREATE INDEX IF NOT EXISTS idx_context_links_source
ON message_context_links(chat_id, message_id);

CREATE INDEX IF NOT EXISTS idx_context_links_context
ON message_context_links(chat_id, context_message_id);

CREATE INDEX IF NOT EXISTS idx_context_links_type
ON message_context_links(link_type, algorithm_version);

CREATE INDEX IF NOT EXISTS idx_target_links_target
ON message_target_links(target_user_id);

CREATE INDEX IF NOT EXISTS idx_target_links_message
ON message_target_links(chat_id, message_id);
```

### Критерий приемки

Выборка контекста по сообщению и выборка сообщений по target user не требуют full table scan.

---

# 9. Разделить слои доступа к базе

## 9.1. Ввести read-side repositories

### Задача
Убрать SQL-запросы из сервисов экспорта и CLI.

### Предлагаемые модули

```text
src/db/repositories/messages_read_repository.py
src/db/repositories/context_links_repository.py
src/db/repositories/export_state_repository.py
src/db/repositories/users_repository.py
```

### Подзадачи

#### 9.1.1. `MessagesReadRepository`

Методы:

```text
get_message(chat_id, message_id)
get_user_messages(user_id, after_ts=None, after_message_id=None)
get_reply_parent(chat_id, reply_to_id)
get_messages_window(chat_id, center_message_id, before, after)
get_messages_by_context_group(context_group_id)
```

#### 9.1.2. `ContextLinksRepository`

Методы:

```text
insert_context_link(...)
insert_many_context_links(...)
get_context_for_message(chat_id, message_id)
delete_links_by_algorithm_version(algorithm_version)
```

#### 9.1.3. `ExportStateRepository`

Методы:

```text
get_export_target(target_user_id)
upsert_export_target(...)
create_export_run(...)
finish_export_run_success(...)
finish_export_run_failed(...)
```

#### 9.1.4. `UsersRepository`

Методы:

```text
get_user(user_id)
get_latest_user_identity(user_id)
update_current_identity(...)
record_identity_history(...)
```

### Критерий приемки

ExportService не содержит больших SQL-запросов напрямую.

---

# 10. User identity history

## 10.1. Добавить таблицу `user_identity_history`

### Задача
Отслеживать смены nickname/username без потери исторической достоверности сообщений.

### Целевая структура

```sql
CREATE TABLE IF NOT EXISTS user_identity_history (
    user_id INTEGER NOT NULL,
    observed_at INTEGER NOT NULL,
    author_name TEXT,
    username TEXT,
    chat_id INTEGER,
    source_message_id INTEGER,
    PRIMARY KEY (user_id, observed_at)
);
```

### Подзадачи

#### 10.1.1. Создать миграцию

Добавить таблицу.

#### 10.1.2. Заполнить историю из `messages`

Для каждого пользователя найти изменения `author_name` по времени.

Минимальная логика:

- отсортировать сообщения пользователя по timestamp;
- если `author_name` изменился — записать новую identity record;
- если username доступен в `raw_payload` или `users` — сохранить его.

#### 10.1.3. Не менять `messages.author_name`

`messages.author_name` должен оставаться историческим именем на момент сообщения.

#### 10.1.4. Актуальный ник хранить отдельно

Текущий nickname/username хранить в `users` или `export_targets.last_known_*`.

### Критерий приемки

Можно определить, какой ник был у пользователя в разные периоды, и какой ник актуален сейчас.

---

# 11. Миграции

## 11.1. Ввести системную таблицу миграций, если ее нет

### Задача
Все изменения схемы должны быть версионированы.

### Целевая структура

```sql
CREATE TABLE IF NOT EXISTS schema_migrations (
    version TEXT PRIMARY KEY,
    applied_at INTEGER NOT NULL
);
```

### Подзадачи

#### 11.1.1. Проверять примененные миграции

Перед выполнением миграции проверять, есть ли версия в `schema_migrations`.

#### 11.1.2. Выполнять миграции в транзакции

Каждая миграция должна выполняться внутри transaction.

#### 11.1.3. Записывать успешную миграцию

После успешного применения добавить запись:

```text
version
applied_at
```

#### 11.1.4. При ошибке делать rollback

Если миграция падает — база не должна оставаться в промежуточном состоянии.

### Критерий приемки

Повторный запуск миграций безопасен и не применяет одну миграцию дважды.

---

## 11.2. Создать порядок миграций

### Рекомендуемый порядок

```text
001_schema_migrations_table
002_messages_unique_chat_message_index
003_context_links_chat_id_and_metadata
004_target_links_chat_id_and_metadata
005_export_targets
006_export_runs
007_missing_reply_refs
008_user_identity_history
009_export_indexes
```

### Критерий приемки

Миграции применяются последовательно и воспроизводимо.

---

# 12. Тесты

## 12.1. Unit tests для SQL/repositories

### Задача
Проверить работу новых repository methods на временной SQLite-базе.

### Подзадачи

#### 12.1.1. Создать test fixture

Fixture должна создавать минимальную базу с:

- одним чатом;
- двумя пользователями;
- несколькими сообщениями;
- reply-связью;
- missing reply;
- context window;
- export target.

#### 12.1.2. Проверить `get_user_messages`

Сценарии:

- первый экспорт;
- export after timestamp;
- tie-breaker по message_id;
- отсутствие новых сообщений.

#### 12.1.3. Проверить `get_reply_parent`

Сценарии:

- reply parent существует;
- reply parent отсутствует;
- reply_to_id из другого чата не матчится.

#### 12.1.4. Проверить context links

Сценарии:

- insert one;
- insert many;
- duplicate insert;
- разные `link_type` для одной пары сообщений;
- разные `algorithm_version`.

#### 12.1.5. Проверить export state

Сценарии:

- создать export target;
- обновить cursor;
- создать export run;
- закрыть success;
- закрыть failed.

### Критерий приемки

Тесты проходят на чистой временной базе без реального `messages.db`.

---

## 12.2. Regression tests для CLI

### Задача
Проверить, что пользовательское поведение CLI не сломалось.

### Подзадачи

#### 12.2.1. Создать минимальную тестовую базу

Использовать small fixture DB.

#### 12.2.2. Запустить существующие export-команды

Проверить:

- команда завершается без ошибки;
- файл создается;
- сообщения отсортированы правильно;
- reply-контекст добавляется;
- missing reply не ломает экспорт.

#### 12.2.3. Проверить повторный export update

Запустить дважды:

- первый раз экспортирует сообщения;
- второй раз не дублирует их;
- `export_runs` содержит две записи;
- второй запуск имеет `new_messages_count = 0`.

### Критерий приемки

CLI smoke tests проходят после миграций.

---

# 13. Документация

## 13.1. Создать `docs/database_architecture.md`

### Содержание

Документ должен описывать:

1. Core tables:
   - `messages`;
   - `users`;
   - `chats`.
2. Derived tables:
   - `message_context_links`;
   - `message_target_links`;
   - `missing_reply_refs`;
   - `user_identity_history`.
3. Export tables:
   - `export_targets`;
   - `export_runs`.
4. Правило идентификации сообщений:
   - всегда `(chat_id, message_id)`.
5. Правило raw vs derived:
   - raw tables не пересчитываются;
   - derived tables можно пересчитывать;
   - derived tables должны иметь `algorithm_version`.
6. Правило export update:
   - источник истины — DB cursor, а не текстовый файл.
7. Правило missing replies:
   - не fatal error;
   - фиксируются в отдельной таблице;
   - экспортируются с технической пометкой.

### Критерий приемки

Новый разработчик может понять схему без чтения всего кода.

---

# 14. Порядок выполнения для агента

## Этап 1 — безопасная диагностика

1. Добавить `scripts/db_diagnostics.py`.
2. Добавить `docs/db_baseline_report.md`.
3. Добавить `docs/export_smoke_scenarios.md`.
4. Не менять схему.
5. Не менять экспорт.

## Этап 2 — миграционная инфраструктура

1. Добавить `schema_migrations`.
2. Добавить runner миграций.
3. Добавить транзакционность.
4. Добавить rollback on error.
5. Проверить повторный запуск.

## Этап 3 — уникальность сообщений

1. Проверить дубликаты `(chat_id, message_id)`.
2. Добавить unique index.
3. Добавить индексы под read-side.
4. Добавить тесты.

## Этап 4 — link tables hardening

1. Мигрировать `message_context_links`.
2. Мигрировать `message_target_links`.
3. Добавить `chat_id`.
4. Добавить `link_type`.
5. Добавить `algorithm_version`.
6. Добавить `created_at`.
7. Добавить индексы.
8. Проверить ссылочную целостность.

## Этап 5 — export-state

1. Добавить `export_targets`.
2. Добавить `export_runs`.
3. Добавить repository.
4. Перевести export update на DB cursor.
5. Проверить отсутствие дублей при повторном update.

## Этап 6 — missing replies

1. Добавить `missing_reply_refs`.
2. Добавить scanner.
3. Интегрировать scanner в диагностику.
4. Добавить graceful handling в экспорт.
5. Добавить тест.

## Этап 7 — user identity history

1. Добавить таблицу.
2. Заполнить из сообщений.
3. Не менять исторические `messages.author_name`.
4. Использовать актуальную identity для имени файла и changelog.

## Этап 8 — документация и regression

1. Добавить `docs/database_architecture.md`.
2. Добавить CLI regression tests.
3. Запустить smoke-сценарии.
4. Сравнить экспорт до/после.
5. Исправить несовместимости.

---

# 15. Definition of Done

Работа считается завершенной, если выполнены все условия:

- `messages` имеет уникальность по `(chat_id, message_id)`.
- Все message links используют `chat_id`.
- `message_context_links` содержит `link_type`, `distance`, `algorithm_version`, `created_at`.
- `message_target_links` содержит `chat_id` и тип связи.
- Есть `export_targets`.
- Есть `export_runs`.
- `export update` использует DB-backed cursor.
- Повторный export update не дублирует сообщения.
- Missing replies фиксируются в `missing_reply_refs`.
- Missing replies не ломают экспорт.
- Есть индексы под основные export-запросы.
- SQL вынесен из ExportService в repositories.
- Есть диагностика базы.
- Есть миграции.
- Есть тесты на repositories.
- Есть regression/smoke сценарии CLI.
- Есть `docs/database_architecture.md`.
- Публичное CLI-поведение не изменено.

---

# 16. Запреты для агента

Не делать:

- не переписывать весь проект без необходимости;
- не менять CLI-контракты;
- не удалять старые таблицы без backup;
- не удалять сообщения из `messages`;
- не изменять `messages.author_name` задним числом;
- не считать `message_id` глобально уникальным;
- не использовать имя файла как основной идентификатор пользователя;
- не парсить экспортированный `.txt` как источник истины для update;
- не добавлять social graph/thread reconstruction/profiling на этом этапе;
- не смешивать raw data и derived data без `algorithm_version`;
- не выполнять destructive rebuild без явной команды;
- не глотать ошибки миграций;
- не обновлять export cursor до успешной записи файла.

---

# 17. Короткий технический вывод

Этот этап нужен не для новых функций, а для стабилизации фундамента.

Главная цель:

```text
Сделать базу надежной для экспорта сообщений, нескольких чатов, incremental update и будущей аналитики.
```

Главное архитектурное правило:

```text
Telegram message identity = (chat_id, message_id)
```

Главное export-правило:

```text
Источник истины для update = база данных, а не уже экспортированный текстовый файл.
```

Главное правило derived data:

```text
Все производные связи должны быть типизированы и версионированы.
```
