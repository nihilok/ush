import time
import uuid
from typing import Optional

from data.constants import DB_PATH, BASE_URL
from data.short_urls import ShortURLDatabase


class URLShortener:

    DEFAULT_EXPIRY = 3600 * 24 * 7
    DOMAIN = BASE_URL

    @classmethod
    async def shorten(cls, url: str, expiry_timestamp: Optional[int] = None):
        key = uuid.uuid5(uuid.NAMESPACE_URL, url).hex[:8]
        await ShortURLDatabase(DB_PATH).insert_url(
            key,
            url,
            (
                expiry_timestamp
                if expiry_timestamp is not None
                else int(time.time()) + cls.DEFAULT_EXPIRY
            ),
        )
        return f"{cls.DOMAIN}{key}"

    @staticmethod
    def retrieve(key):
        url = ShortURLDatabase(DB_PATH).retrieve_url(key)
        return url
