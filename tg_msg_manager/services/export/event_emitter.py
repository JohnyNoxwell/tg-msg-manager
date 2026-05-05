from typing import Any, Optional

from ...core.service_events import ExportEvents
from ...core.models.payloads.export import ExportSyncProgressPayload
from ...core.service_events import ServiceEventSink, emit_service_event


class ExportEventEmitter:
    def __init__(self, event_sink: Optional[ServiceEventSink] = None):
        self.event_sink = event_sink

    def emit(self, event_name: str, **payload: Any) -> None:
        emit_service_event(self.event_sink, event_name, **payload)

    def emit_sync_progress(self, payload: ExportSyncProgressPayload) -> None:
        self.emit(ExportEvents.SYNC_PROGRESS, **payload.as_dict())
