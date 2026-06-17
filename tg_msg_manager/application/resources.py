"""Runtime resource construction for application sessions."""

import os
from dataclasses import dataclass
from typing import Optional

from ..core.process import ProcessManager
from ..core.runtime import AppRuntime
from ..core.telegram.client import TelethonClientWrapper
from ..infrastructure.storage.sqlite import SQLiteStorage


@dataclass(frozen=True)
class RuntimeResourceFactory:
    runtime: AppRuntime
    needs_client: bool = True

    def create_process_manager(self) -> ProcessManager:
        return ProcessManager(lock_path=self.runtime.paths.lock_path)

    def create_storage(self, process_manager: ProcessManager) -> SQLiteStorage:
        return SQLiteStorage(
            self.runtime.paths.db_path, process_manager=process_manager
        )

    def resolve_session_path(self) -> str:
        session_name = self.runtime.settings.session_name
        if os.path.isabs(session_name):
            return session_name
        return os.path.join(self.runtime.paths.project_root, session_name)

    def create_telegram_client(self) -> Optional[TelethonClientWrapper]:
        if not self.needs_client:
            return None
        return TelethonClientWrapper(
            self.resolve_session_path(),
            self.runtime.settings.api_id,
            self.runtime.settings.api_hash,
            max_rps=self.runtime.settings.max_rps,
        )
