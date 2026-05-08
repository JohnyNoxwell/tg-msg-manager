from typing import Any

from .discussions.errors import ChannelDiscussionStateError
from .errors import ChannelExportStateError

CHANNEL_COUNTER_FIELDS = (
    "message_count_total",
    "media_count_total",
    "downloaded_media_count_total",
    "already_existing_media_count_total",
    "skipped_media_count_total",
    "skipped_by_size_count_total",
    "skipped_by_type_count_total",
    "failed_media_count_total",
)

DISCUSSION_COUNTER_FIELDS = (
    "thread_count_total",
    "comment_count_total",
    "failed_thread_count_total",
)


def validate_channel_state_integrity(state: Any) -> None:
    _validate_non_negative_fields(
        state,
        CHANNEL_COUNTER_FIELDS,
        error_cls=ChannelExportStateError,
        label="Channel export state",
    )
    last_message_id = getattr(state, "last_exported_message_id", None)
    if last_message_id is not None and int(last_message_id) < 0:
        raise ChannelExportStateError(
            "Channel export state has negative last_exported_message_id"
        )
    if getattr(state, "last_run_status", None) != "completed":
        raise ChannelExportStateError(
            "Channel export state last_run_status must be 'completed'"
        )


def validate_channel_state_for_incremental(
    previous_state: Any,
    new_state: Any,
) -> None:
    validate_channel_state_integrity(previous_state)
    validate_channel_state_integrity(new_state)
    if previous_state.channel_id != new_state.channel_id:
        raise ChannelExportStateError(
            "Incremental channel state belongs to a different channel"
        )
    _validate_not_decreasing(
        previous_state,
        new_state,
        ("message_count_total", "media_count_total", *CHANNEL_COUNTER_FIELDS[2:]),
        error_cls=ChannelExportStateError,
        label="Channel export state",
    )
    previous_last = previous_state.last_exported_message_id
    new_last = new_state.last_exported_message_id
    if previous_last is not None and new_last is not None and new_last < previous_last:
        raise ChannelExportStateError(
            "Channel export state last_exported_message_id moved backwards"
        )


def validate_discussion_state_integrity(state: Any) -> None:
    _validate_non_negative_fields(
        state,
        DISCUSSION_COUNTER_FIELDS,
        error_cls=ChannelDiscussionStateError,
        label="Discussion export state",
    )
    if getattr(state, "last_run_status", None) != "completed":
        raise ChannelDiscussionStateError(
            "Discussion export state last_run_status must be 'completed'"
        )


def validate_discussion_state_for_incremental(
    previous_state: Any,
    new_state: Any,
) -> None:
    validate_discussion_state_integrity(previous_state)
    validate_discussion_state_integrity(new_state)
    if previous_state.channel_id != new_state.channel_id:
        raise ChannelDiscussionStateError(
            "Incremental discussion state belongs to a different channel"
        )
    if (
        previous_state.discussion_chat_id is not None
        and new_state.discussion_chat_id is not None
        and previous_state.discussion_chat_id != new_state.discussion_chat_id
    ):
        raise ChannelDiscussionStateError(
            "Incremental discussion state belongs to a different discussion chat"
        )
    _validate_not_decreasing(
        previous_state,
        new_state,
        DISCUSSION_COUNTER_FIELDS,
        error_cls=ChannelDiscussionStateError,
        label="Discussion export state",
    )


def validate_discussion_state_matches_channel(
    channel: Any,
    discussion_state: Any,
) -> None:
    validate_discussion_state_integrity(discussion_state)
    if discussion_state.channel_id != channel.channel_id:
        raise ChannelDiscussionStateError(
            "Discussion export state belongs to a different channel"
        )


def validate_discussion_state_matches_source(
    discussion_state: Any,
    discussion_chat_id: int | None,
) -> None:
    validate_discussion_state_integrity(discussion_state)
    if (
        discussion_state.discussion_chat_id is not None
        and discussion_chat_id is not None
        and discussion_state.discussion_chat_id != discussion_chat_id
    ):
        raise ChannelDiscussionStateError(
            "Discussion export state belongs to a different discussion chat"
        )


def _validate_non_negative_fields(
    state: Any,
    fields: tuple[str, ...],
    *,
    error_cls: type[Exception],
    label: str,
) -> None:
    for field in fields:
        value = getattr(state, field)
        if value < 0:
            raise error_cls(f"{label} has negative {field}")


def _validate_not_decreasing(
    previous_state: Any,
    new_state: Any,
    fields: tuple[str, ...],
    *,
    error_cls: type[Exception],
    label: str,
) -> None:
    for field in fields:
        if getattr(new_state, field) < getattr(previous_state, field):
            raise error_cls(f"{label} {field} moved backwards")
