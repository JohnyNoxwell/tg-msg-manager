from pathlib import Path
from typing import Tuple

from tg_msg_manager.core.models.dataset_contracts import (
    CHANNEL_STATE_JSON,
    MANIFEST_JSON,
)


class ChannelDatasetDiscovery:
    def discover(self, root: Path) -> Tuple[Path, ...]:
        root = Path(root)
        if not root.exists():
            return ()
        if not root.is_dir():
            raise ValueError(f"Channel export root is not a directory: {root}")

        candidates = []
        for child in root.iterdir():
            if not child.is_dir():
                continue
            if (child / CHANNEL_STATE_JSON).exists() or (
                child / MANIFEST_JSON
            ).exists():
                candidates.append(child)
        return tuple(sorted(candidates, key=lambda path: path.name))
