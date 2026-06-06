import json
import os
from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class WriterState:
    current_part: int = 1
    current_count: int = 0


@dataclass(frozen=True)
class WriterStateRecovery:
    state: WriterState
    persist: bool
    remove_legacy: bool = False


class WriterStateStore:
    def __init__(self, state_path: str, legacy_state_path: str):
        self.state_path = state_path
        self.legacy_state_path = legacy_state_path

    def save(self, state: WriterState) -> None:
        os.makedirs(os.path.dirname(self.state_path), exist_ok=True)
        with open(self.state_path, "w", encoding="utf-8") as file:
            json.dump(
                {
                    "current_part": state.current_part,
                    "current_count": state.current_count,
                },
                file,
            )

    @staticmethod
    def remove(path: str) -> None:
        os.remove(path)

    def recover(
        self,
        *,
        path_for_part: Callable[[int], str],
        as_json: bool,
        max_msgs: int,
    ) -> WriterStateRecovery:
        existing_state_path = (
            self.state_path
            if os.path.exists(self.state_path)
            else self.legacy_state_path
        )
        if os.path.exists(existing_state_path):
            try:
                state = self._load(existing_state_path)
                if os.path.exists(path_for_part(state.current_part)):
                    is_legacy = existing_state_path == self.legacy_state_path
                    return WriterStateRecovery(
                        state=state,
                        persist=is_legacy,
                        remove_legacy=is_legacy,
                    )
            except Exception:
                pass

        state = WriterState()
        while True:
            path = path_for_part(state.current_part)
            if not os.path.exists(path):
                break
            state = WriterState(
                current_part=state.current_part,
                current_count=self._count_messages(path, as_json=as_json),
            )
            if state.current_count < max_msgs:
                break
            state = WriterState(current_part=state.current_part + 1)
        return WriterStateRecovery(state=state, persist=True)

    @staticmethod
    def _load(path: str) -> WriterState:
        with open(path, "r", encoding="utf-8") as file:
            state = json.load(file)
        return WriterState(
            current_part=max(1, int(state.get("current_part", 1))),
            current_count=max(0, int(state.get("current_count", 0))),
        )

    @staticmethod
    def _count_messages(path: str, *, as_json: bool) -> int:
        try:
            with open(path, "r", encoding="utf-8") as file:
                return sum(1 for _ in file) if as_json else 0
        except Exception:
            return 0
