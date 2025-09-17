import asyncio
import random
from typing import Optional

from TikTokLive import TikTokLiveClient
from TikTokLive.client.logger import LogLevel


class TikTokLiveChecker:
    """Checks TikTok live status using TikTokLive library."""

    def __init__(self):
        # Disable logging for cleaner output
        import logging
        logging.getLogger('TikTokLive').setLevel(logging.CRITICAL)

    async def is_user_live(self, username: str) -> Optional[bool]:
        """
        Check if user is live with retry logic.
        Returns True if live, False if offline, None if unknown.
        """
        for attempt in range(3):
            try:
                # Create client for this username
                client = TikTokLiveClient(unique_id=f"@{username}")
                client.logger.setLevel(LogLevel.CRITICAL.value)

                # Check live status
                is_live = await client.is_live()
                return is_live

            except Exception:
                if attempt < 2:  # Only wait if not the last attempt
                    # Exponential backoff with jitter
                    delay = (2 ** attempt) + random.uniform(0, 1)
                    await asyncio.sleep(delay)

        return None  # Unknown status after all retries

    async def get_stream_url(self, username: str) -> Optional[str]:
        """
        Get the stream URL for recording if user is live.
        Skip double-check due to TikTok API inconsistencies.
        """
        try:
            # Check with TikTokLive client
            client = TikTokLiveClient(unique_id=f"@{username}")
            client.logger.setLevel(LogLevel.CRITICAL.value)

            if await client.is_live():
                stream_url = f"https://www.tiktok.com/@{username}/live"
                print(f"🔍 TikTokLive confirms @{username} is live, attempting recording...")
                return stream_url

        except Exception as e:
            print(f"Error getting stream URL: {e}")

        return None