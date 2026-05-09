import asyncio
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

from tg_msg_manager.core.models.message import MessageData
from tg_msg_manager.services.db_export import DBExportService
from tg_msg_manager.services.db_export.models import DBExportSource
from tg_msg_manager.services.db_export.payload_writer import DBExportPayloadWriter
from tg_msg_manager.services.db_export.txt_renderer import DBExportTxtRenderer


def _message(
    message_id: int,
    *,
    user_id: int = 10,
    author_name: str = "Alice",
    text: str = "target",
    reply_to_id: int | None = None,
    context_group_id: str | None = "grp-1",
) -> MessageData:
    return MessageData(
        message_id=message_id,
        chat_id=99,
        user_id=user_id,
        author_name=author_name,
        timestamp=datetime(2024, 2, 17, 15, message_id, tzinfo=timezone.utc),
        text=text,
        media_type=None,
        reply_to_id=reply_to_id,
        fwd_from_id=None,
        context_group_id=context_group_id,
        raw_payload={},
    )


def test_payload_writer_calls_readable_renderer_when_profile_is_context_readable(
    tmp_path,
):
    source = DBExportSource(
        export_summary=None,
        export_rows=None,
        export_row_iter_factory=None,
        messages=[_message(1)],
        source_count=1,
    )

    with patch(
        "tg_msg_manager.services.db_export.payload_writer.render_txt_records",
        return_value="CONTEXT BLOCK #0001\n[TARGET MESSAGE]\n",
    ) as render:
        asyncio.run(
            DBExportPayloadWriter().write_payloads(
                source=source,
                output_path=str(tmp_path / "out.txt"),
                as_json=False,
                json_profile="ai",
                txt_profile="context-readable",
                expected_count=1,
                target_user_id=10,
                target_author="Alice",
            )
        )

    render.assert_called_once()
    assert "CONTEXT BLOCK #0001" in (tmp_path / "out.txt").read_text(encoding="utf-8")


def test_payload_writer_uses_legacy_renderer_when_profile_is_legacy(tmp_path):
    source = DBExportSource(
        export_summary=None,
        export_rows=None,
        export_row_iter_factory=None,
        messages=[_message(1)],
        source_count=1,
    )
    txt_renderer = MagicMock(spec=DBExportTxtRenderer)
    txt_renderer.format_block.return_value = ("legacy text\n", None, 10)

    asyncio.run(
        DBExportPayloadWriter(txt_renderer=txt_renderer).write_payloads(
            source=source,
            output_path=str(tmp_path / "out.txt"),
            as_json=False,
            json_profile="ai",
            txt_profile="legacy",
            expected_count=1,
            target_user_id=10,
            target_author="Alice",
        )
    )

    txt_renderer.format_block.assert_called_once()
    assert "legacy text" in (tmp_path / "out.txt").read_text(encoding="utf-8")


def test_export_service_default_txt_profile_remains_legacy_for_db_export(tmp_path):
    storage = MagicMock()
    storage.start_export_run.return_value = None
    storage.get_user_messages.return_value = [_message(1)]
    storage.get_user.return_value = {"user_id": 10, "first_name": "Alice"}
    storage.get_export_target.return_value = None

    output_path = asyncio.run(
        DBExportService(storage).export_user_messages(
            10,
            output_dir=str(tmp_path),
            as_json=False,
        )
    )

    assert "[15:01:00] <Alice (10)>:" in open(output_path, encoding="utf-8").read()


def test_export_service_writes_readable_output_when_requested(tmp_path):
    storage = MagicMock()
    storage.start_export_run.return_value = None
    storage.get_user_messages.return_value = [
        _message(1, user_id=20, author_name="Bob", text="before"),
        _message(2, user_id=10, author_name="Alice", text="target", reply_to_id=1),
    ]
    storage.get_user.return_value = {"user_id": 10, "first_name": "Alice"}
    storage.get_export_target.return_value = None

    output_path = asyncio.run(
        DBExportService(storage).export_user_messages(
            10,
            output_dir=str(tmp_path),
            as_json=False,
            txt_profile="context-readable",
        )
    )
    content = open(output_path, encoding="utf-8").read()

    assert "CONTEXT BLOCK #0001" in content
    assert "[TARGET MESSAGE]" in content


def test_export_service_readable_output_preserves_ungrouped_context(tmp_path):
    storage = MagicMock()
    storage.start_export_run.return_value = None
    storage.get_user_messages.return_value = [
        _message(
            1,
            user_id=20,
            author_name="Bob",
            text="EXPORT_BEFORE_UNGROUPED_MARKER",
            context_group_id=None,
        ),
        _message(
            2,
            user_id=10,
            author_name="Alice",
            text="EXPORT_TARGET_UNGROUPED_MARKER",
            context_group_id=None,
        ),
        _message(
            3,
            user_id=30,
            author_name="Carol",
            text="EXPORT_AFTER_UNGROUPED_MARKER",
            context_group_id=None,
        ),
    ]
    storage.get_user.return_value = {"user_id": 10, "first_name": "Alice"}
    storage.get_export_target.return_value = None

    output_path = asyncio.run(
        DBExportService(storage).export_user_messages(
            10,
            output_dir=str(tmp_path),
            as_json=False,
            txt_profile="context-readable",
        )
    )
    content = open(output_path, encoding="utf-8").read()

    assert content.count("CONTEXT BLOCK #") == 1
    assert "[CONTEXT BEFORE]" in content
    assert "[TARGET MESSAGE]" in content
    assert "[CONTEXT AFTER]" in content
    assert "EXPORT_BEFORE_UNGROUPED_MARKER" in content
    assert "EXPORT_TARGET_UNGROUPED_MARKER" in content
    assert "EXPORT_AFTER_UNGROUPED_MARKER" in content
