from pathlib import Path
from typing import Any

from .batch_discovery import ChannelDatasetDiscovery
from .batch_models import (
    BATCH_STATUS_FAILED,
    BATCH_STATUS_NO_NEW_POSTS,
    BATCH_STATUS_UPDATED,
    ChannelBatchUpdateItem,
    ChannelBatchUpdateResult,
)
from .batch_options import ChannelBatchOptionsBuilder


class ChannelBatchUpdateService:
    def __init__(
        self,
        *,
        channel_exporter: Any,
        discovery: ChannelDatasetDiscovery | None = None,
        options_builder: ChannelBatchOptionsBuilder | None = None,
    ):
        self.channel_exporter = channel_exporter
        self.discovery = discovery or ChannelDatasetDiscovery()
        self.options_builder = options_builder or ChannelBatchOptionsBuilder()

    async def update_all(self, root: Path) -> ChannelBatchUpdateResult:
        root = Path(root)
        items = []
        for dataset_dir in self.discovery.discover(root):
            channel = dataset_dir.name
            try:
                options = self.options_builder.build(dataset_dir, root=root)
                channel = options.channel
                result = await self.channel_exporter.export_channel(options)
                status = (
                    BATCH_STATUS_UPDATED
                    if result.posts_exported_this_run > 0
                    else BATCH_STATUS_NO_NEW_POSTS
                )
                items.append(
                    ChannelBatchUpdateItem(
                        dataset_dir=dataset_dir,
                        channel=channel,
                        status=status,
                        posts_exported=result.posts_exported_this_run,
                    )
                )
            except Exception as exc:
                items.append(
                    ChannelBatchUpdateItem(
                        dataset_dir=dataset_dir,
                        channel=channel,
                        status=BATCH_STATUS_FAILED,
                        error=str(exc),
                    )
                )
        return ChannelBatchUpdateResult(items=tuple(items))
