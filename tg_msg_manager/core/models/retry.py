from dataclasses import dataclass
from enum import Enum


class RetryTaskStatus(str, Enum):
    PENDING = "pending"
    RETRYING = "retrying"
    COMPLETED = "completed"
    FAILED = "failed"


class RetryTaskType(str, Enum):
    SYNC_TARGET = "sync_target"
    ARCHIVE_PM = "archive_pm"
    EXPORT = "export"


@dataclass
class RetryRunStats:
    scanned: int = 0
    succeeded: int = 0
    rescheduled: int = 0
    failed: int = 0
    cleaned: int = 0
