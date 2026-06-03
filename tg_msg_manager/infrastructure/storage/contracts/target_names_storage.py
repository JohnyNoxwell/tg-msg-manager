from typing import List, Protocol, runtime_checkable

from ..records import (
    TargetNameResolutionRecord,
    TargetNameSnapshotRecord,
    TargetNameTargetRecord,
)


@runtime_checkable
class TargetNamesStorage(Protocol):
    def resolve_target_name_target(self, target: str) -> TargetNameResolutionRecord:
        """Resolves a target using only locally stored metadata."""

    def get_target_name_snapshots(
        self, target: TargetNameTargetRecord
    ) -> List[TargetNameSnapshotRecord]:
        """Returns local name snapshots for a resolved target."""
