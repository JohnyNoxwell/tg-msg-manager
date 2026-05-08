from time import perf_counter
from typing import Any, Optional

from ...core.service_events import ServiceEventSink, emit_service_event


class ChannelExportEvents:
    STARTED = "channel_export.started"
    CHANNEL_RESOLVED = "channel_export.channel_resolved"
    STATE_LOADED = "channel_export.state_loaded"
    PROGRESS = "channel_export.progress"
    NO_NEW_POSTS = "channel_export.no_new_posts"
    COMPLETED = "channel_export.completed"
    FAILED = "channel_export.failed"


class ChannelExportEventEmitter:
    def __init__(self, event_sink: Optional[ServiceEventSink] = None):
        self.event_sink = event_sink
        self._run_started_at: Optional[float] = None

    def _emit(self, event_name: str, **payload: Any) -> None:
        emit_service_event(self.event_sink, event_name, **payload)

    def mark_run_started(self) -> None:
        self._run_started_at = perf_counter()

    def elapsed_seconds(self) -> float:
        if self._run_started_at is None:
            return 0.0
        return perf_counter() - self._run_started_at

    def emit_started(self, **payload: Any) -> None:
        self.mark_run_started()
        self._emit(ChannelExportEvents.STARTED, **payload)

    def emit_channel_resolved(self, **payload: Any) -> None:
        self._emit(ChannelExportEvents.CHANNEL_RESOLVED, **payload)

    def emit_state_loaded(self, **payload: Any) -> None:
        self._emit(ChannelExportEvents.STATE_LOADED, **payload)

    def emit_progress(self, **payload: Any) -> None:
        self._emit(ChannelExportEvents.PROGRESS, **payload)

    def emit_no_new_posts(self, **payload: Any) -> None:
        self._emit(ChannelExportEvents.NO_NEW_POSTS, **payload)

    def emit_completed(self, **payload: Any) -> None:
        self._emit(ChannelExportEvents.COMPLETED, **payload)

    def emit_failed(self, **payload: Any) -> None:
        self._emit(ChannelExportEvents.FAILED, **payload)
