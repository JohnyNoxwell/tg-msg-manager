from typing import Protocol, runtime_checkable


@runtime_checkable
class AnalyticsStorage(Protocol):
    """Reserved read-only contract for future analytics projections."""
