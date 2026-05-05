import asyncio
from typing import Optional

from ...core.models.message import MessageData
from ...core.telegram.interface import TelegramClientInterface
from .media_policy import PrivateArchiveMediaPolicy


class PrivateArchiveMediaDownloader:
    def __init__(
        self,
        client: TelegramClientInterface,
        *,
        media_policy: PrivateArchiveMediaPolicy,
        download_semaphore: asyncio.Semaphore,
    ):
        self.client = client
        self.media_policy = media_policy
        self.download_semaphore = download_semaphore

    async def download(self, message: MessageData, *, media_dir: str) -> Optional[str]:
        if not self.media_policy.should_download(message):
            return None
        target_path = self.media_policy.target_path(
            media_dir=media_dir, message=message
        )
        async with self.download_semaphore:
            return await self.client.download_media(message.media_ref, file=target_path)
