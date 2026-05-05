from typing import List, Optional, Protocol, runtime_checkable

from ....core.models.reporting import (
    ReportDatabaseSummary,
    ReportRetrySummary,
    ReportTargetSummary,
)


@runtime_checkable
class ReportStorage(Protocol):
    def get_report_database_summary(self) -> ReportDatabaseSummary:
        """Returns global database/reporting summary."""

    def get_report_target_summaries(self) -> List[ReportTargetSummary]:
        """Returns tracked target summaries for audit reporting."""

    def get_report_retry_summary(
        self, now_ts: Optional[int] = None
    ) -> ReportRetrySummary:
        """Returns aggregated retry queue state."""
