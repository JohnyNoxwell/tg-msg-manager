"""Application runtime session lifecycle."""

import asyncio
from typing import Callable, Optional

from ..core.logging import setup_logging
from ..core.runtime import AppRuntime
from ..core.service_events import ServiceEventSink
from ..core.telemetry import telemetry
from .resources import RuntimeResourceFactory
from .services import ServiceBundle, create_service_bundle

LifecycleEventSink = Callable[[str], None]
LoginErrorHandler = Callable[[BaseException], bool]


class ApplicationSessionLockError(RuntimeError):
    """Raised when another tg-msg-manager process owns the lock."""


class ApplicationSession:
    """Owns process, storage, Telegram client, and service bundle lifecycle."""

    def __init__(
        self,
        runtime: AppRuntime,
        *,
        needs_client: bool = True,
        event_sink: ServiceEventSink,
        lifecycle_event_sink: Optional[LifecycleEventSink] = None,
        login_error_handler: Optional[LoginErrorHandler] = None,
        interrupt_callback: Optional[Callable] = None,
    ):
        self.runtime = runtime
        self.needs_client = needs_client
        self._event_sink = event_sink
        self._lifecycle_event_sink = lifecycle_event_sink
        self._login_error_handler = login_error_handler
        self._interrupt_callback = interrupt_callback
        self._resource_factory = RuntimeResourceFactory(
            runtime,
            needs_client=needs_client,
        )
        self.pm = self._resource_factory.create_process_manager()
        self.storage = None
        self.client = None
        self.services: Optional[ServiceBundle] = None

    def _emit_lifecycle_event(self, event: str) -> None:
        if self._lifecycle_event_sink is not None:
            self._lifecycle_event_sink(event)

    async def initialize(self) -> None:
        setup_logging(
            level=self.runtime.settings.log_level,
            log_dir=self.runtime.paths.logs_dir,
        )
        telemetry.reset()
        if not self.pm.acquire_lock():
            raise ApplicationSessionLockError

        self.pm.setup_async_signals(
            asyncio.get_running_loop(),
            self._interrupt_callback,
        )

        self._emit_lifecycle_event("storage_opening")
        self.storage = self._resource_factory.create_storage(self.pm)
        self._emit_lifecycle_event("storage_ready")
        await self.storage.start()

        if self.needs_client:
            self._emit_lifecycle_event("telegram_connecting")
            self.client = self._resource_factory.create_telegram_client()
            try:
                await self.client.connect()
            except Exception as exc:
                if self._login_error_handler is None:
                    raise
                if not self._login_error_handler(exc):
                    raise
                return
            self._emit_lifecycle_event("telegram_connected")

        self.services = create_service_bundle(
            runtime=self.runtime,
            storage=self.storage,
            client=self.client,
            needs_client=self.needs_client,
            event_sink=self._event_sink,
        )

    async def shutdown(self) -> None:
        if self.client:
            await self.client.disconnect()
        if self.storage:
            await self.storage.close()
        if self.pm:
            self.pm.release_lock()
