from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class DatasetValidationOptions:
    dataset_path: Path
    strict: bool = False


@dataclass(frozen=True)
class DatasetInspectionOptions:
    dataset_path: Path
    strict: bool = False
