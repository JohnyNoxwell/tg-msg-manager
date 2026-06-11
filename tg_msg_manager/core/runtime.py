import os
import sys
from dataclasses import dataclass
from typing import List, Optional

from .config import Settings, load_settings

APP_HOME_ENV = "TG_HOME"
DEFAULT_APP_HOME = "TG_MSG_MANAGER"


def _resolve_under_root(root: str, path: str) -> str:
    if os.path.isabs(path):
        return path
    return os.path.join(root, path)


def _default_app_home() -> str:
    configured_home = os.environ.get(APP_HOME_ENV)
    if configured_home:
        return os.path.abspath(os.path.expanduser(configured_home))
    return os.path.join(os.path.expanduser("~"), DEFAULT_APP_HOME)


def _ensure_base_directories(root: str) -> None:
    for relative_path in (
        "LOGS",
        "DB_EXPORTS",
        "PRIVAT_DIALOGS",
        "PUBLIC_GROUPS",
        os.path.join("exports", "channels"),
    ):
        os.makedirs(os.path.join(root, relative_path), exist_ok=True)


@dataclass(frozen=True)
class AppPaths:
    project_root: str
    config_path: str
    db_path: str
    lock_path: str
    logs_dir: str
    db_exports_dir: str
    private_dialogs_dir: str
    public_groups_dir: str
    channel_exports_dir: str = ""

    def artifact_roots(self) -> List[str]:
        return [
            self.public_groups_dir,
            self.private_dialogs_dir,
            self.db_exports_dir,
            self.channel_exports_dir,
        ]

    def ensure_directories(self) -> None:
        directories = [
            self.project_root,
            os.path.dirname(self.db_path),
            self.logs_dir,
            self.db_exports_dir,
            self.private_dialogs_dir,
            self.public_groups_dir,
            self.channel_exports_dir,
        ]
        for directory in directories:
            os.makedirs(directory, exist_ok=True)


@dataclass(frozen=True)
class AppRuntime:
    settings: Settings
    paths: AppPaths
    python_executable: str


def build_app_runtime(
    *,
    project_root: Optional[str] = None,
    config_path: Optional[str] = None,
    python_executable: Optional[str] = None,
    require_api_credentials: bool = True,
) -> AppRuntime:
    if project_root is None and config_path:
        resolved_config_path = os.path.abspath(os.path.expanduser(config_path))
        resolved_project_root = os.path.dirname(resolved_config_path)
    else:
        resolved_project_root = os.path.abspath(
            os.path.expanduser(project_root) if project_root else _default_app_home()
        )
        resolved_config_path = os.path.abspath(
            config_path or os.path.join(resolved_project_root, "config.json")
        )

    _ensure_base_directories(resolved_project_root)
    settings = load_settings(
        resolved_config_path,
        require_api_credentials=require_api_credentials,
    )
    paths = AppPaths(
        project_root=resolved_project_root,
        config_path=resolved_config_path,
        db_path=_resolve_under_root(resolved_project_root, settings.db_path),
        lock_path=os.path.join(resolved_project_root, ".tg_msg_manager.lock"),
        logs_dir=os.path.join(resolved_project_root, "LOGS"),
        db_exports_dir=os.path.join(resolved_project_root, "DB_EXPORTS"),
        private_dialogs_dir=os.path.join(resolved_project_root, "PRIVAT_DIALOGS"),
        public_groups_dir=os.path.join(resolved_project_root, "PUBLIC_GROUPS"),
        channel_exports_dir=os.path.join(resolved_project_root, "exports", "channels"),
    )
    paths.ensure_directories()
    return AppRuntime(
        settings=settings,
        paths=paths,
        python_executable=python_executable or sys.executable,
    )
