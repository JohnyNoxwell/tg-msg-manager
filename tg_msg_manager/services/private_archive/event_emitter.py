from typing import Any

from ...core.models.payloads.private_archive import (
    PrivateArchiveCompletedPayload,
    PrivateArchiveMediaSavedPayload,
    PrivateArchiveProgressPayload,
    PrivateArchiveStartedPayload,
)
from ...core.service_events import (
    PrivateArchiveEvents,
    ServiceEventSink,
    emit_service_event,
)


class PrivateArchiveEventEmitter:
    def __init__(self, event_sink: ServiceEventSink = None):
        self.event_sink = event_sink

    def _emit(self, name: str, **payload: Any) -> None:
        emit_service_event(self.event_sink, name, **payload)

    def emit_started(
        self, *, target_name: str, user_id: int, user_dir: str, last_id: int
    ) -> None:
        payload = PrivateArchiveStartedPayload(
            target_name=target_name,
            user_id=user_id,
            user_dir=user_dir,
            last_id=last_id,
        )
        self._emit(PrivateArchiveEvents.STARTED, **payload.as_dict())

    def emit_progress(self, *, count: int, stats: Any, archive_stats: Any) -> None:
        payload = PrivateArchiveProgressPayload(
            count=count,
            stats=stats,
            archive_stats=archive_stats,
        )
        self._emit(PrivateArchiveEvents.PROGRESS, **payload.as_dict())

    def emit_media_saved(self, *, filename: str, path: str) -> None:
        payload = PrivateArchiveMediaSavedPayload(filename=filename, path=path)
        self._emit(PrivateArchiveEvents.MEDIA_SAVED, **payload.as_dict())

    def emit_completed(
        self,
        *,
        target_name: str,
        count: int,
        stats: Any,
        archive_stats: Any,
    ) -> None:
        payload = PrivateArchiveCompletedPayload(
            target_name=target_name,
            count=count,
            stats=stats,
            archive_stats=archive_stats,
        )
        self._emit(PrivateArchiveEvents.COMPLETED, **payload.as_dict())
