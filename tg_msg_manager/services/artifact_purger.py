import logging
import os
import shutil
from typing import Sequence

logger = logging.getLogger(__name__)


def purge_user_artifacts(artifact_roots: Sequence[str], user_id: int) -> int:
    """Delete matching user artifacts only within the explicitly provided roots."""
    deleted_count = 0
    pattern = f"_{user_id}"

    for artifact_root in artifact_roots:
        if not os.path.exists(artifact_root):
            continue
        for root, dirs, files in os.walk(artifact_root):
            for filename in files:
                if pattern not in filename:
                    continue
                path = os.path.join(root, filename)
                try:
                    os.remove(path)
                    deleted_count += 1
                    logger.debug(f"Deleted file: {path}")
                except Exception as exc:
                    logger.error(f"Error deleting file {path}: {exc}")

            for dirname in list(dirs):
                if pattern not in dirname:
                    continue
                path = os.path.join(root, dirname)
                try:
                    shutil.rmtree(path)
                    deleted_count += 1
                    dirs.remove(dirname)
                    logger.debug(f"Deleted directory: {path}")
                except Exception as exc:
                    logger.error(f"Error deleting directory {path}: {exc}")

    return deleted_count
