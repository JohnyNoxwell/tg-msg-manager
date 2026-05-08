import shutil
from pathlib import Path
from typing import Optional, TextIO


def temp_path_for(path: Path) -> Path:
    target_path = Path(path)
    return target_path.with_name(f"{target_path.name}.tmp")


def cleanup_temp(path: Path) -> None:
    temp_path = temp_path_for(path)
    try:
        temp_path.unlink()
    except FileNotFoundError:
        return


def atomic_replace(source: Path, target: Path) -> None:
    Path(source).replace(Path(target))


class AtomicTextFile:
    def __init__(self, path: Path, *, mode: str = "w", encoding: str = "utf-8"):
        if mode not in {"w", "a"}:
            raise ValueError(f"Unsupported atomic text mode: {mode!r}")
        self.path = Path(path)
        self.mode = mode
        self.encoding = encoding
        self.temp_path = temp_path_for(self.path)
        self._handle: Optional[TextIO] = None
        self._committed = False

    def open(self) -> TextIO:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if self.mode == "a" and self.path.exists():
            shutil.copyfile(self.path, self.temp_path)
        else:
            self.temp_path.write_text("", encoding=self.encoding)
        self._handle = self.temp_path.open("a", encoding=self.encoding)
        return self._handle

    def close(self) -> None:
        if self._handle is not None:
            self._handle.close()
            self._handle = None

    def commit(self) -> None:
        if self._committed:
            return
        self.close()
        atomic_replace(self.temp_path, self.path)
        self._committed = True

    def rollback(self) -> None:
        self.close()
        cleanup_temp(self.path)


def atomic_write_text(path: Path, content: str, *, encoding: str = "utf-8") -> None:
    writer = AtomicTextFile(path, mode="w", encoding=encoding)
    try:
        handle = writer.open()
        handle.write(content)
        writer.commit()
    except Exception:
        writer.rollback()
        raise
