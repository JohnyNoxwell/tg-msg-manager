from datetime import datetime, timezone

from tg_msg_manager.core.models.message import MessageData
from tg_msg_manager.services.rendering import (
    ContextReadableTxtRenderer,
    TxtRenderOptions,
)


def _message(
    message_id: int,
    *,
    user_id: int,
    author_name: str,
    minute: int,
    text: str,
    reply_to_id: int | None = None,
    context_group_id: str | None = "grp-1",
) -> MessageData:
    return MessageData(
        message_id=message_id,
        chat_id=777,
        user_id=user_id,
        author_name=author_name,
        timestamp=datetime(2024, 2, 17, 15, minute, tzinfo=timezone.utc),
        text=text,
        media_type=None,
        reply_to_id=reply_to_id,
        fwd_from_id=None,
        context_group_id=context_group_id,
        raw_payload={},
    )


def test_context_readable_renderer_emits_required_context_sections():
    records = [
        _message(1, user_id=20, author_name="Bob", minute=1, text="before"),
        _message(
            2,
            user_id=10,
            author_name="Alice",
            minute=2,
            text="target",
            reply_to_id=1,
        ),
        _message(3, user_id=20, author_name="Bob", minute=3, text="after"),
    ]

    rendered = ContextReadableTxtRenderer().render(
        records,
        TxtRenderOptions(
            profile="context-readable",
            target_user_id=10,
            target_author_name="Alice",
            chat_title="Example Chat",
        ),
    )

    assert "CONTEXT BLOCK #0001" in rendered
    assert "[REPLIED MESSAGE]" in rendered
    assert "[CONTEXT BEFORE]" in rendered
    assert "[TARGET MESSAGE]" in rendered
    assert "[CONTEXT AFTER]" in rendered
    assert "Bob (20)" in rendered
    assert "target" in rendered
    assert '↪ replies to Bob · 15:01:00 · "before"' in rendered
    assert "↪ missing reply #1" not in rendered


def test_context_readable_renderer_uses_target_messages_label_for_multiple_targets():
    rendered = ContextReadableTxtRenderer().render(
        [
            _message(1, user_id=10, author_name="Alice", minute=1, text="one"),
            _message(2, user_id=10, author_name="Alice", minute=2, text="two"),
        ],
        TxtRenderOptions(profile="context-readable", target_user_id=10),
    )

    assert "[TARGET MESSAGES]" in rendered


def test_context_readable_renderer_renders_missing_reply_compactly():
    rendered = ContextReadableTxtRenderer().render(
        [
            _message(
                10,
                user_id=10,
                author_name="Alice",
                minute=10,
                text="target",
                reply_to_id=341081,
            )
        ],
        TxtRenderOptions(profile="context-readable", target_user_id=10),
    )

    assert "↪ missing reply #341081" in rendered
    assert "original message not found in local DB" not in rendered


def test_context_readable_renderer_truncates_reply_excerpt_in_multiple_replies():
    long_text = "x" * 120
    rendered = ContextReadableTxtRenderer().render(
        [
            _message(1, user_id=20, author_name="Bob", minute=1, text=long_text),
            _message(2, user_id=21, author_name="Carol", minute=2, text="reply two"),
            _message(
                3,
                user_id=10,
                author_name="Alice",
                minute=3,
                text="target one",
                reply_to_id=1,
            ),
            _message(
                4,
                user_id=10,
                author_name="Alice",
                minute=4,
                text="target two",
                reply_to_id=2,
            ),
        ],
        TxtRenderOptions(
            profile="context-readable",
            target_user_id=10,
            max_reply_excerpt_chars=20,
        ),
    )

    assert "Multiple replied messages:" in rendered
    assert '"' + ("x" * 17) + '..."' in rendered


def test_context_readable_renderer_groups_by_context_group_and_falls_back_per_target():
    rendered = ContextReadableTxtRenderer().render(
        [
            _message(
                1,
                user_id=10,
                author_name="Alice",
                minute=1,
                text="a",
                context_group_id="a",
            ),
            _message(
                2,
                user_id=10,
                author_name="Alice",
                minute=2,
                text="b",
                context_group_id="b",
            ),
            _message(
                3,
                user_id=10,
                author_name="Alice",
                minute=3,
                text="c",
                context_group_id=None,
            ),
        ],
        TxtRenderOptions(profile="context-readable", target_user_id=10),
    )

    assert rendered.count("CONTEXT BLOCK #") == 3


def test_context_readable_renderer_preserves_ungrouped_before_target_after():
    rendered = ContextReadableTxtRenderer().render(
        [
            _message(
                10,
                user_id=20,
                author_name="Bob",
                minute=10,
                text="BEFORE_UNGROUPED_MARKER",
                context_group_id=None,
            ),
            _message(
                11,
                user_id=10,
                author_name="Alice",
                minute=11,
                text="TARGET_UNGROUPED_MARKER",
                context_group_id=None,
            ),
            _message(
                12,
                user_id=30,
                author_name="Carol",
                minute=12,
                text="AFTER_UNGROUPED_MARKER",
                context_group_id=None,
            ),
        ],
        TxtRenderOptions(profile="context-readable", target_user_id=10),
    )

    assert rendered.count("CONTEXT BLOCK #") == 1
    assert "[CONTEXT BEFORE]" in rendered
    assert "[TARGET MESSAGE]" in rendered
    assert "[CONTEXT AFTER]" in rendered
    assert "BEFORE_UNGROUPED_MARKER" in rendered
    assert "TARGET_UNGROUPED_MARKER" in rendered
    assert "AFTER_UNGROUPED_MARKER" in rendered
    assert rendered.index("[CONTEXT BEFORE]") < rendered.index(
        "BEFORE_UNGROUPED_MARKER"
    )
    assert rendered.index("[TARGET MESSAGE]") < rendered.index(
        "TARGET_UNGROUPED_MARKER"
    )
    assert rendered.index("[CONTEXT AFTER]") < rendered.index("AFTER_UNGROUPED_MARKER")


def test_context_readable_renderer_preserves_grouped_context_group_behavior():
    rendered = ContextReadableTxtRenderer().render(
        [
            _message(
                20,
                user_id=20,
                author_name="Bob",
                minute=20,
                text="grouped before",
                context_group_id="stable-group",
            ),
            _message(
                21,
                user_id=10,
                author_name="Alice",
                minute=21,
                text="grouped target",
                context_group_id="stable-group",
            ),
            _message(
                22,
                user_id=30,
                author_name="Carol",
                minute=22,
                text="grouped after",
                context_group_id="stable-group",
            ),
        ],
        TxtRenderOptions(profile="context-readable", target_user_id=10),
    )

    assert rendered.count("CONTEXT BLOCK #") == 1
    assert rendered.index("[CONTEXT BEFORE]") < rendered.index("grouped before")
    assert rendered.index("[TARGET MESSAGE]") < rendered.index("grouped target")
    assert rendered.index("[CONTEXT AFTER]") < rendered.index("grouped after")


def test_context_readable_renderer_keeps_mixed_grouped_and_ungrouped_blocks_ordered():
    rendered = ContextReadableTxtRenderer().render(
        [
            _message(
                30,
                user_id=20,
                author_name="Bob",
                minute=30,
                text="grouped context before",
                context_group_id="grouped",
            ),
            _message(
                31,
                user_id=10,
                author_name="Alice",
                minute=31,
                text="grouped target",
                context_group_id="grouped",
            ),
            _message(
                40,
                user_id=20,
                author_name="Bob",
                minute=40,
                text="ungrouped context before",
                context_group_id=None,
            ),
            _message(
                41,
                user_id=10,
                author_name="Alice",
                minute=41,
                text="ungrouped target",
                context_group_id=None,
            ),
            _message(
                42,
                user_id=30,
                author_name="Carol",
                minute=42,
                text="ungrouped context after",
                context_group_id=None,
            ),
        ],
        TxtRenderOptions(profile="context-readable", target_user_id=10),
    )

    assert rendered.count("CONTEXT BLOCK #") == 2
    assert rendered.index("CONTEXT BLOCK #0001") < rendered.index("grouped target")
    assert rendered.index("CONTEXT BLOCK #0002") < rendered.index("ungrouped target")
    assert rendered.index("grouped target") < rendered.index("ungrouped target")
    assert "ungrouped context before" in rendered
    assert "ungrouped context after" in rendered


def test_context_readable_renderer_omits_mixed_ungrouped_non_target_only_block():
    rendered = ContextReadableTxtRenderer().render(
        [
            _message(
                50,
                user_id=10,
                author_name="Alice",
                minute=50,
                text="grouped target only",
                context_group_id="grouped",
            ),
            _message(
                51,
                user_id=20,
                author_name="Bob",
                minute=51,
                text="NON_TARGET_ONLY_UNGROUPED_MARKER",
                context_group_id=None,
            ),
        ],
        TxtRenderOptions(profile="context-readable", target_user_id=10),
    )

    assert rendered.count("CONTEXT BLOCK #") == 1
    assert "grouped target only" in rendered
    assert "NON_TARGET_ONLY_UNGROUPED_MARKER" not in rendered


def test_context_readable_renderer_renders_ungrouped_non_target_only_without_groups():
    rendered = ContextReadableTxtRenderer().render(
        [
            _message(
                60,
                user_id=20,
                author_name="Bob",
                minute=50,
                text="NON_TARGET_ONLY_NO_GROUP_MARKER",
                context_group_id=None,
            ),
        ],
        TxtRenderOptions(profile="context-readable", target_user_id=10),
    )

    assert rendered.count("CONTEXT BLOCK #") == 1
    assert "NON_TARGET_ONLY_NO_GROUP_MARKER" in rendered
