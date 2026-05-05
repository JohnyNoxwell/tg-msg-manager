from dataclasses import dataclass
from typing import Any

from ...utils.ui import UI


@dataclass(frozen=True)
class PrivateArchiveSourceDescriptor:
    user_id: int
    first_name: str
    last_name: str
    username: str
    target_name: str


class PrivateArchiveSourceResolver:
    def resolve(self, user_entity: Any) -> PrivateArchiveSourceDescriptor:
        return PrivateArchiveSourceDescriptor(
            user_id=int(getattr(user_entity, "id", 0) or 0),
            first_name=str(getattr(user_entity, "first_name", "") or ""),
            last_name=str(getattr(user_entity, "last_name", "") or ""),
            username=str(getattr(user_entity, "username", "") or ""),
            target_name=UI.format_name(user_entity),
        )
