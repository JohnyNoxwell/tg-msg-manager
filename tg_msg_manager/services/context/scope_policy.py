from dataclasses import dataclass


@dataclass(frozen=True)
class ContextScopePolicy:
    window_size: int
    max_cluster: int
    recursive_depth: int

    @property
    def active_depth(self) -> int:
        return min(max(self.recursive_depth, 1), 3)
