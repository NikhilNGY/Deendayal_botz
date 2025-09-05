import logging
import logging.config
from typing import Union, Optional, AsyncGenerator

from aiohttp import web
from pyrogram import Client, types

from Deendayal_botz.database.ia_filterdb import Media
from Deendayal_botz.info import *
from utils import temp

# ==============================
# Logging Configuration
# ==============================
logging.config.fileConfig("logging.conf")
logger = logging.getLogger(__name__)

# Set log levels for noisy libraries
logging.getLogger().setLevel(logging.INFO)
logging.getLogger("pyrogram").setLevel(logging.ERROR)
logging.getLogger("imdbpy").setLevel(logging.ERROR)
logging.getLogger("aiohttp").setLevel(logging.ERROR)
logging.getLogger("aiohttp.web").setLevel(logging.ERROR)

# ==============================
# Main Bot Class
# ==============================
class DeendayalXBot(Client):
    def __init__(self):
        super().__init__(
            name=SESSION,
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            workers=150,
            plugins={"root": "plugins"},
            sleep_threshold=5,
        )

    async def iter_messages(
        self,
        chat_id: Union[int, str],
        limit: int,
        offset: int = 0,
    ) -> Optional[AsyncGenerator["types.Message", None]]:
        """
        Iterate through chat messages sequentially.

        Args:
            chat_id (int | str): Chat ID or username.
            limit (int): Maximum number of messages to fetch.
            offset (int, optional): Starting message offset. Defaults to 0.

        Yields:
            types.Message: Telegram messages one by one.
        """
        current = offset
        while current < limit:
            fetch_count = min(200, limit - current)
            if fetch_count <= 0:
                break

            messages = await self.get_messages(
                chat_id, list(range(current, current + fetch_count + 1))
            )

            for message in messages:
                if message:
                    yield message
                    current += 1


# ==============================
# Bot Instances
# ==============================
DeendayalBot = DeendayalXBot()

multi_clients = {}
work_loads = {}
