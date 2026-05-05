import asyncio
from dataclasses import dataclass
from typing import Any, Callable, Optional

from ...core.models.payloads.export import ExportSyncProgressPayload


@dataclass
class SyncProgressStats:
    processed: int = 0
    skipped: int = 0
    linked: int = 0


class SyncProgressReporter:
    def __init__(
        self,
        *,
        initial_db_total: int,
        progress_stats: Any,
        emit_progress: Callable[[ExportSyncProgressPayload], None],
        interval_seconds: float = 0.5,
    ):
        self.initial_db_total = initial_db_total
        self.progress_stats = progress_stats
        self.emit_progress = emit_progress
        self.interval_seconds = interval_seconds
        self._done_event = asyncio.Event()
        self._task: Optional[asyncio.Task] = None

    async def draw_status(self, extra: str = "") -> None:
        db_total = self.initial_db_total + self.progress_stats.linked
        self.emit_progress(
            ExportSyncProgressPayload(
                db_total=db_total,
                extra=extra,
            )
        )

    async def _draw_status_loop(self) -> None:
        while not self._done_event.is_set():
            await self.draw_status()
            await asyncio.sleep(self.interval_seconds)

    def start(self) -> None:
        self._task = asyncio.create_task(self._draw_status_loop())

    async def finalize(self) -> None:
        self._done_event.set()
        if self._task is not None:
            await self._task
        await self.draw_status()
