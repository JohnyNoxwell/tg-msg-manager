from datetime import datetime, timezone

from tg_msg_manager.core.models.message import MessageData
from tg_msg_manager.services.rendering import LegacyTxtRenderer, TxtRenderOptions


def _message(
    message_id: int,
    *,
    user_id: int = 10,
    author_name: str = "Alice",
    text: str = "hello",
    reply_to_id: int | None = None,
) -> MessageData:
    return MessageData(
        message_id=message_id,
        chat_id=20,
        user_id=user_id,
        author_name=author_name,
        timestamp=datetime(2024, 2, 17, 15, message_id, tzinfo=timezone.utc),
        text=text,
        media_type=None,
        reply_to_id=reply_to_id,
        fwd_from_id=None,
        context_group_id=None,
        raw_payload={},
    )


def test_legacy_renderer_keeps_flat_date_timestamp_and_author_shape():
    rendered = LegacyTxtRenderer().render(
        [_message(1)],
        TxtRenderOptions(profile="legacy", target_user_id=10),
    )

    assert "==================== 17 February 2024 ====================" in rendered
    assert "[15:01:00] <Alice (10)>:" in rendered
    assert "hello" in rendered


def test_legacy_renderer_preserves_noisy_missing_reply_shape():
    rendered = LegacyTxtRenderer().render(
        [_message(2, reply_to_id=99)],
        TxtRenderOptions(profile="legacy", target_user_id=10),
    )

    assert "[reply_to: 99 - original message not found in local DB]" in rendered
