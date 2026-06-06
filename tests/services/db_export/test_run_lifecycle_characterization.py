import asyncio
from datetime import datetime
from types import SimpleNamespace

import pytest

from tg_msg_manager.core.models.message import MessageData
from tg_msg_manager.services.db_export.models import (
    DBExportWriteResult,
    ExistingExportArtifact,
    SkipDecision,
)
from tg_msg_manager.services.db_export.service import DBExportService
from tg_msg_manager.services.db_export.summary import DBExportPlan, DBExportSource


def _message(message_id=7, timestamp=1700000000):
    return MessageData(
        message_id=message_id,
        chat_id=2,
        user_id=3,
        author_name="Stable User",
        timestamp=datetime.fromtimestamp(timestamp),
        text="hello",
        media_type=None,
        reply_to_id=None,
        fwd_from_id=None,
        context_group_id=None,
        raw_payload={},
    )


def _source(messages=None, *, source_count=None):
    messages = messages if messages is not None else [_message()]
    return DBExportSource(
        export_summary=None,
        export_rows=None,
        export_row_iter_factory=None,
        messages=messages,
        source_count=len(messages) if source_count is None else source_count,
    )


class FakeStorage:
    pass


class FakeSourceLoader:
    def __init__(self, events, *, full_source=None, incremental_source=None):
        self.events = events
        self.full_source = full_source
        self.incremental_source = incremental_source

    def load_full_source(self, **kwargs):
        self.events.append(("load_full", kwargs))
        if isinstance(self.full_source, Exception):
            raise self.full_source
        return self.full_source

    def load_incremental_source(self, **kwargs):
        self.events.append(("load_incremental", kwargs))
        if isinstance(self.incremental_source, Exception):
            raise self.incremental_source
        return self.incremental_source


class FakePlanBuilder:
    def __init__(self, events, output_path):
        self.events = events
        self.output_path = str(output_path)

    def prepare_plan(self, **kwargs):
        self.events.append(("prepare_plan", kwargs))
        return DBExportPlan(
            target_author="Stable User",
            output_path=self.output_path,
            ext=".jsonl",
            fingerprint={
                "user_id": 3,
                "message_count": kwargs["source"].source_count,
                "first_message_id": 7,
                "last_message_id": 8,
                "first_timestamp": 1700000000,
                "last_timestamp": 1700000100,
                "as_json": kwargs["as_json"],
                "include_date": kwargs["include_date"],
                "json_profile": kwargs["json_profile"],
                "txt_profile": None,
            },
        )


class FakeSkipPolicy:
    def __init__(self, events, artifact=None):
        self.events = events
        self.artifact = artifact

    def find_skip_decision(self, **kwargs):
        self.events.append(("skip_policy", kwargs))
        return SkipDecision(
            should_skip=self.artifact is not None,
            reason="unchanged" if self.artifact else "changed",
            artifact=self.artifact,
        )

    def artifact_paths_exist(self, output_path, part_count):
        return True


class FakeStateManager:
    def __init__(self, events, *, export_target=None, supports_update=True):
        self.events = events
        self.export_target = export_target
        self.supports_update = supports_update

    def start_run(self, *, user_id):
        self.events.append(("start_run", user_id))
        return 101

    def finish_run(self, run_id, **kwargs):
        self.events.append(("finish_run", run_id, kwargs))

    def extract_export_cursor(self, **kwargs):
        self.events.append(("extract_cursor", kwargs))
        return 1700000100, 8

    def upsert_export_target_state(self, **kwargs):
        self.events.append(("upsert_state", kwargs))

    def get_export_target(self, user_id):
        self.events.append(("get_export_target", user_id))
        return self.export_target

    def supports_incremental_update(self, **kwargs):
        self.events.append(("supports_update", kwargs))
        return self.supports_update

    def resolve_existing_export_path(self, **kwargs):
        self.events.append(("resolve_existing_path", kwargs))
        export_target = kwargs["export_target"]
        return f"{export_target.export_dir}/{export_target.export_filename}"

    def refresh_export_target_artifact_from_db_state(self, **kwargs):
        self.events.append(("refresh_state", kwargs))


class FakePayloadWriter:
    def __init__(self, events, *, raises=None, progress_items=None, count=2):
        self.events = events
        self.raises = raises
        self.progress_items = progress_items or []
        self.count = count

    async def write_payloads(self, **kwargs):
        self.events.append(("write_payloads", kwargs))
        for idx, item in enumerate(self.progress_items, start=1):
            kwargs["on_progress"](idx, item)
        if self.raises is not None:
            raise self.raises
        writer = SimpleNamespace(
            current_part=1,
            write_calls=1,
            bytes_written=32,
            rotation_count=0,
            state_persist_count=1,
        )
        result = DBExportWriteResult(
            count=self.count,
            current_part=1,
            write_calls=1,
            bytes_written=32,
            rotation_count=0,
            state_persist_count=1,
        )
        return writer, result

    def cleanup_existing_export_files(self, **kwargs):
        self.events.append(("cleanup_existing", kwargs))

    def write_batch_size(self, *, as_json, json_profile):
        return 1000


class FakeEventEmitter:
    def __init__(self, events):
        self.events = events

    def emit_completed(self, **kwargs):
        self.events.append(("emit_completed", kwargs))

    def emit_skipped_unchanged(self, **kwargs):
        self.events.append(("emit_skipped", kwargs))


def _service(
    events,
    *,
    output_path,
    full_source=None,
    incremental_source=None,
    export_target=None,
    skip_artifact=None,
    payload_writer=None,
):
    return DBExportService(
        FakeStorage(),
        source_loader=FakeSourceLoader(
            events,
            full_source=full_source,
            incremental_source=incremental_source,
        ),
        plan_builder=FakePlanBuilder(events, output_path),
        skip_policy=FakeSkipPolicy(events, artifact=skip_artifact),
        state_manager=FakeStateManager(events, export_target=export_target),
        payload_writer=payload_writer or FakePayloadWriter(events),
        event_emitter=FakeEventEmitter(events),
    )


def test_full_export_run_records_start_success_state_and_completion(tmp_path):
    events = []
    output_path = tmp_path / "Stable_User_3.jsonl"
    service = _service(events, output_path=output_path, full_source=_source())

    result = asyncio.run(
        service.export_user_messages(3, output_dir=str(tmp_path), as_json=True)
    )

    assert result == str(output_path)
    assert [event[0] for event in events] == [
        "start_run",
        "load_full",
        "prepare_plan",
        "skip_policy",
        "cleanup_existing",
        "write_payloads",
        "emit_completed",
        "upsert_state",
        "extract_cursor",
        "finish_run",
    ]
    assert events[-1] == (
        "finish_run",
        101,
        {
            "status": "success",
            "new_messages_count": 2,
            "last_new_message_ts": 1700000100,
            "error": None,
        },
    )
    assert events[-3][1]["part_count"] == 1


def test_full_export_unchanged_reuses_artifact_without_writing(tmp_path):
    events = []
    output_path = tmp_path / "Stable_User_3.jsonl"
    artifact = ExistingExportArtifact(output_path=str(output_path), part_count=3)
    service = _service(
        events,
        output_path=output_path,
        full_source=_source(),
        skip_artifact=artifact,
    )

    result = asyncio.run(
        service.export_user_messages(3, output_dir=str(tmp_path), as_json=True)
    )

    assert result == str(output_path)
    event_names = [event[0] for event in events]
    assert "write_payloads" not in event_names
    assert "cleanup_existing" not in event_names
    assert "emit_skipped" in event_names
    assert events[-1][2] == {
        "status": "success",
        "new_messages_count": 0,
        "last_new_message_ts": None,
        "error": None,
    }
    upsert_event = next(event for event in events if event[0] == "upsert_state")
    assert upsert_event[1]["output_path"] == str(output_path)
    assert upsert_event[1]["part_count"] == 3


def test_update_run_with_no_new_rows_returns_existing_path_without_writing(tmp_path):
    events = []
    output_path = tmp_path / "Stable_User_3.jsonl"
    output_path.write_text('{"message_id":7}\n', encoding="utf-8")
    export_target = SimpleNamespace(
        export_filename=output_path.name,
        export_dir=str(tmp_path),
        last_exported_message_ts=1700000000,
        last_exported_message_id=7,
        last_known_author_name="Stable User",
    )
    service = _service(
        events,
        output_path=output_path,
        incremental_source=None,
        export_target=export_target,
    )

    result = asyncio.run(
        service.update_user_messages(3, output_dir=str(tmp_path), as_json=True)
    )

    assert result == str(output_path)
    event_names = [event[0] for event in events]
    assert "write_payloads" not in event_names
    assert "refresh_state" not in event_names
    assert events[-1][2] == {
        "status": "success",
        "new_messages_count": 0,
        "last_new_message_ts": None,
        "error": None,
    }


def test_update_run_failure_records_progress_before_writer_error(tmp_path):
    events = []
    output_path = tmp_path / "Stable_User_3.jsonl"
    output_path.write_text('{"message_id":7}\n', encoding="utf-8")
    export_target = SimpleNamespace(
        export_filename=output_path.name,
        export_dir=str(tmp_path),
        last_exported_message_ts=1700000000,
        last_exported_message_id=7,
        last_known_author_name="Stable User",
    )
    progress_item = {"timestamp": 1700000200}
    service = _service(
        events,
        output_path=output_path,
        incremental_source=_source([_message(8, 1700000200)]),
        export_target=export_target,
        payload_writer=FakePayloadWriter(
            events,
            raises=RuntimeError("writer stopped"),
            progress_items=[progress_item],
        ),
    )

    with pytest.raises(RuntimeError, match="writer stopped"):
        asyncio.run(
            service.update_user_messages(3, output_dir=str(tmp_path), as_json=True)
        )

    assert "refresh_state" not in [event[0] for event in events]
    assert events[-1] == (
        "finish_run",
        101,
        {
            "status": "failed",
            "new_messages_count": 1,
            "last_new_message_ts": 1700000200,
            "error": "writer stopped",
        },
    )


def test_full_export_source_failure_records_failed_run_without_state_update(tmp_path):
    events = []
    output_path = tmp_path / "Stable_User_3.jsonl"
    service = _service(
        events,
        output_path=output_path,
        full_source=RuntimeError("source unavailable"),
    )

    with pytest.raises(RuntimeError, match="source unavailable"):
        asyncio.run(
            service.export_user_messages(3, output_dir=str(tmp_path), as_json=True)
        )

    event_names = [event[0] for event in events]
    assert "upsert_state" not in event_names
    assert "write_payloads" not in event_names
    assert events[-1] == (
        "finish_run",
        101,
        {
            "status": "failed",
            "new_messages_count": 0,
            "last_new_message_ts": None,
            "error": "source unavailable",
        },
    )
