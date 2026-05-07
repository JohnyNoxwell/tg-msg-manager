import asyncio
import logging
import sqlite3
import threading
from typing import Any, Optional

from .interface import BaseStorage
from ._sqlite_identity import SQLiteIdentityMixin
from ._sqlite_read_path import SQLiteReadPathMixin
from ._sqlite_schema import SQLiteSchemaMixin
from ._sqlite_sync_state import SQLiteSyncStateMixin
from ._sqlite_write_path import SQLiteWritePathMixin
from .write.connection import create_sqlite_connection
from .write.transaction import StorageTransactionCoordinator
from ...core.telemetry import telemetry

logger = logging.getLogger(__name__)


class SQLiteStorage(
    SQLiteSchemaMixin,
    SQLiteIdentityMixin,
    SQLiteWritePathMixin,
    SQLiteReadPathMixin,
    SQLiteSyncStateMixin,
    BaseStorage,
):
    """
    SQLite storage with separated schema, write-path, read-path, and sync-state concerns.
    """

    def __init__(
        self, db_path: str = "messages.db", process_manager: Optional[Any] = None
    ):
        self.db_path = db_path
        self._pm = process_manager
        self._lock = threading.Lock()
        self._conn = self._create_connection()
        self._transaction_coordinator = StorageTransactionCoordinator(
            connection=self._conn,
            lock=self._lock,
        )
        self._init_db()

        self._write_queue = asyncio.Queue()
        self._worker_task = None
        self._shutdown_event = asyncio.Event()

    def _create_connection(self):
        return create_sqlite_connection(self.db_path, enable_wal=True)

    def _get_connection(self) -> sqlite3.Connection:
        return create_sqlite_connection(self.db_path, enable_wal=False)

    def _read_connection(self) -> sqlite3.Connection:
        return self._get_connection()

    def _write_transaction(self):
        return self._transaction_coordinator.write_transaction()

    def should_stop(self) -> bool:
        """Returns True if a shutdown has been requested internally or via ProcessManager."""
        external_stop = self._pm.shutdown_requested if self._pm else False
        return self._shutdown_event.is_set() or external_stop

    async def start(self):
        """Starts the background writer task."""
        if not self._worker_task:
            self._worker_task = asyncio.create_task(self._background_writer())

    async def _ensure_worker_started(self):
        """Lazily starts the writer so async save calls work even without explicit start()."""
        if not self._worker_task:
            await self.start()

    async def flush(self):
        """Waits until queued writes are persisted."""
        await self._ensure_worker_started()
        with telemetry.time_block("storage.flush.total"):
            await self._write_queue.join()

    def request_stop(self):
        """Sets the shutdown event to signal workers to stop."""
        self._shutdown_event.set()

    async def close(self):
        """Flushes the queue and stops the background writer."""
        self._shutdown_event.set()
        if self._worker_task:
            await self._worker_task
            self._worker_task = None
        self._conn.close()
