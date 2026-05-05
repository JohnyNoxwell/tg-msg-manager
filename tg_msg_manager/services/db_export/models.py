from dataclasses import dataclass
from typing import Any, Optional

from .summary import DBExportPlan, DBExportSource


@dataclass(frozen=True)
class ExistingExportArtifact:
    output_path: str
    part_count: int


@dataclass(frozen=True)
class SkipDecision:
    should_skip: bool
    reason: str
    previous_fingerprint: Optional[dict[str, Any]] = None
    current_fingerprint: Optional[dict[str, Any]] = None
    artifact: Optional[ExistingExportArtifact] = None


@dataclass(frozen=True)
class DBExportWriteResult:
    count: int
    current_part: int
    write_calls: int
    bytes_written: int
    rotation_count: int
    state_persist_count: int


__all__ = [
    "DBExportPlan",
    "DBExportSource",
    "DBExportWriteResult",
    "ExistingExportArtifact",
    "SkipDecision",
]
