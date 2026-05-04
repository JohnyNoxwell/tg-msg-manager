from typing import Any, Awaitable, Callable, Optional, Tuple, Union

from .scan_ranges import ScanRange


def build_scan_message_stream(
    *,
    client: Any,
    entity: Any,
    scan_range: ScanRange,
    single_worker_limit: Optional[int],
    api_from_user: Optional[Any],
    prefetched_messages: Optional[list[Any]],
    iter_prefetched_messages: Union[
        Callable[[list[Any]], Awaitable[Any]],
        Callable[[list[Any]], Any],
    ],
) -> Tuple[Any, bool]:
    if scan_range.role == "HEAD" and prefetched_messages is not None:
        return iter_prefetched_messages(prefetched_messages), True

    return (
        client.iter_messages(
            entity,
            limit=single_worker_limit,
            offset_id=scan_range.upper + 1,
            from_user=api_from_user,
        ),
        False,
    )


def should_skip_scan_message(
    *,
    msg_data: Any,
    scan_range: ScanRange,
    from_user_id: Optional[int],
    local_sender_filter_id: Optional[int],
    using_prefetched_messages: bool,
    force_resync: bool,
    tail_id: int,
    head_id: int,
) -> bool:
    if (
        (using_prefetched_messages or local_sender_filter_id is not None)
        and from_user_id
        and msg_data.user_id != from_user_id
    ):
        return True

    if (
        not force_resync
        and scan_range.role == "TAIL"
        and tail_id > 0
        and tail_id < msg_data.message_id <= head_id
    ):
        return True

    return False


def mark_scan_completion_flags(
    *,
    worker_state: Any,
    scan_range: ScanRange,
    single_worker_limit: Optional[int],
    stop_requested: bool,
    using_prefetched_messages: bool,
    prefetched_head_complete: bool,
) -> None:
    if (
        scan_range.role == "HEAD"
        and single_worker_limit is None
        and not stop_requested
        and (not using_prefetched_messages or prefetched_head_complete)
    ):
        worker_state.head_scan_complete = True
    if scan_range.role == "TAIL" and single_worker_limit is None and not stop_requested:
        worker_state.tail_scan_complete = True
