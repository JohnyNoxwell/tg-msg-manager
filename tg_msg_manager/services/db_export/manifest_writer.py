from typing import Any, Dict, List, Optional

from .manifest import expected_export_paths, load_export_manifest


class DBExportManifestWriter:
    """Compatibility helper for legacy manifest-backed DB export state."""

    def load_manifest(self, output_dir: str, user_id: int) -> Optional[Dict[str, Any]]:
        return load_export_manifest(output_dir, user_id)

    def expected_paths(self, output_path: str, part_count: int) -> List[str]:
        return expected_export_paths(output_path, part_count)
