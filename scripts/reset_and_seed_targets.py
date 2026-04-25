import argparse
import shutil
from pathlib import Path

from tg_msg_manager.infrastructure.storage.sqlite import SQLiteStorage


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TARGETS_FILE = ROOT / "DB_TARGETS.txt"
DEFAULT_DB_PATH = ROOT / "messages.db"
EXPORT_DIRS = [
    ROOT / "DB_EXPORTS",
    ROOT / "PUBLIC_GROUPS",
    ROOT / "PRIVAT_DIALOGS",
]


def parse_targets(path: Path) -> list[tuple[int, str, int]]:
    targets: list[tuple[int, str, int]] = []
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or "user_id=" not in line or "chat_id=" not in line:
            continue

        parts = [part.strip() for part in line.split("|")]
        if len(parts) != 3:
            raise ValueError(f"Unexpected target line format: {line}")

        name_part, user_part, chat_part = parts
        if ". " not in name_part:
            raise ValueError(f"Missing index prefix in target line: {line}")

        author_name = name_part.split(". ", 1)[1].strip()
        user_id = int(user_part.split("=", 1)[1].strip())
        chat_id = int(chat_part.split("=", 1)[1].strip())
        targets.append((user_id, author_name, chat_id))

    if not targets:
        raise ValueError(f"No targets found in {path}")
    return targets


def remove_path(path: Path):
    if path.is_dir():
        shutil.rmtree(path, ignore_errors=True)
    elif path.exists():
        path.unlink()


def reset_workspace(db_path: Path):
    for extra in (db_path, Path(f"{db_path}-wal"), Path(f"{db_path}-shm")):
        remove_path(extra)
    for directory in EXPORT_DIRS:
        if directory.exists():
            shutil.rmtree(directory, ignore_errors=True)
        directory.mkdir(parents=True, exist_ok=True)


def seed_targets(db_path: Path, targets: list[tuple[int, str, int]], depth: int):
    storage = SQLiteStorage(str(db_path))
    try:
        for user_id, author_name, chat_id in targets:
            storage.register_target(
                user_id=user_id,
                author_name=author_name,
                chat_id=chat_id,
                deep_mode=True,
                recursive_depth=depth,
            )
    finally:
        storage._conn.close()


def main():
    parser = argparse.ArgumentParser(description="Reset local Telegram exports and reseed sync_targets.")
    parser.add_argument("--targets-file", default=str(DEFAULT_TARGETS_FILE))
    parser.add_argument("--db-path", default=str(DEFAULT_DB_PATH))
    parser.add_argument("--depth", type=int, default=2)
    args = parser.parse_args()

    targets_file = Path(args.targets_file).resolve()
    db_path = Path(args.db_path).resolve()
    targets = parse_targets(targets_file)

    reset_workspace(db_path)
    seed_targets(db_path, targets, args.depth)

    print(f"Reset complete: {len(targets)} targets seeded into {db_path.name}")
    print("Deep mode: enabled")
    print(f"Default recursive depth for all seeded targets: {args.depth}")
    print("Next step: run your external update command.")


if __name__ == "__main__":
    main()
