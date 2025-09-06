#!/usr/bin/env python3
"""
Modernized main.py — starts the Deendayal bot, loads plugins, initializes clients, DBs, and web server.
Fully async, robust, with inline logging configuration.
"""

import os
import sys
import asyncio
import glob
import importlib.util
import logging
from pathlib import Path
from datetime import date, datetime

import pytz
from aiohttp import web
from pyrogram import __version__ as PYROGRAM_VERSION
from pyrogram.raw.all import layer as PYRO_LAYER
from pyrogram import idle

# -------------------------
# Project imports
# -------------------------
from Deendayal_botz.database.ia_filterdb import (
    Media, Media2, choose_mediaDB, tempDict, db as clientDB
)
from Deendayal_botz.database.users_chats_db import db
from Deendayal_botz.info import (
    DATABASE_URI, DATABASE_URI2, LOG_CHANNEL, LOG_STR, PORT, ON_HEROKU
)
from utils import temp
from Deendayal_botz.script import script
from Deendayal_botz.plugins import web_server, check_expired_premium
from Deendayal_botz.Bot import DeendayalBot
from Deendayal_botz.util.keepalive import ping_server
from Deendayal_botz.Bot.clients import initialize_clients

# -------------------------
# Logging setup (inline, modern)
# -------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("DeendayalBot")
logging.getLogger("pyrogram").setLevel(logging.ERROR)
logging.getLogger("imdbpy").setLevel(logging.ERROR)
logging.getLogger("aiohttp").setLevel(logging.ERROR)

# -------------------------
# Globals
# -------------------------
botStartTime = asyncio.get_event_loop().time()
PLUGINS_GLOB = "plugins/*.py"

# -------------------------
# Plugin helpers
# -------------------------
def discover_plugin_paths(pattern: str):
    return [Path(p) for p in glob.glob(pattern) if Path(p).is_file()]

def import_plugin_from_path(path: Path):
    module_name = f"plugins.{path.stem}"
    try:
        spec = importlib.util.spec_from_file_location(module_name, str(path))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        sys.modules[module_name] = module
        logger.info(f"✅ Plugin loaded: {path.stem}")
        return module
    except Exception as e:
        logger.exception(f"Failed to load plugin {path}: {e}")
        return None

# -------------------------
# Main bot startup
# -------------------------
async def start_deendayal_bot():
    logger.info("🚀 Initializing Deendayal Bot")

    # Start Pyrogram bot
    try:
        await DeendayalBot.start()
    except Exception as e:
        logger.exception("Failed to start DeendayalBot: %s", e)
        raise

    # Bot info
    me = await DeendayalBot.get_me()
    DeendayalBot.username = f"@{me.username}" if me.username else None
    logger.info("🤖 Bot started as: %s", DeendayalBot.username or "UNKNOWN")

    # Initialize additional clients
    try:
        await initialize_clients()
    except Exception:
        logger.exception("Error initializing extra clients")

    # Load plugins
    for path in discover_plugin_paths(PLUGINS_GLOB):
        import_plugin_from_path(path)

    # Heroku keepalive
    if ON_HEROKU:
        try:
            asyncio.create_task(ping_server())
        except Exception:
            logger.exception("Failed to schedule keepalive ping task")

    # Restore banned users/chats
    try:
        banned_users, banned_chats = await db.get_banned()
        temp.BANNED_USERS = banned_users or []
        temp.BANNED_CHATS = banned_chats or []
    except Exception:
        logger.exception("Failed to restore banned users/chats")

    # Ensure DB indexes
    try:
        await Media.ensure_indexes()
        await Media2.ensure_indexes()
    except Exception:
        logger.exception("Failed to ensure indexes on Media/Media2")

    # Choose media DB based on free space
    try:
        stats = await clientDB.command("dbStats")
        data_mb = stats.get("dataSize", 0) / (1024**2)
        index_mb = stats.get("indexSize", 0) / (1024**2)
        free_dbSize = round(512 - (data_mb + index_mb), 2)

        if DATABASE_URI2 and free_dbSize < 62:
            tempDict["indexDB"] = DATABASE_URI2
            logger.warning(
                "Primary DB low on space (%.2f MB). Switching to secondary DB.", free_dbSize
            )
        elif not DATABASE_URI2:
            logger.error("Secondary DB URI missing (DATABASE_URI2). Exiting.")
            await DeendayalBot.stop()
            sys.exit(1)
        else:
            logger.info("Primary DB free space: %.2f MB", free_dbSize)

        await choose_mediaDB()
    except Exception:
        logger.exception("Error checking DB stats / choosing media DB")

    # Temp bot identity
    try:
        temp.ME = me.id
        temp.U_NAME = me.username
        temp.B_NAME = me.first_name
        temp.B_LINK = me.mention
    except Exception:
        logger.exception("Failed to set temporary bot identity variables")

    # Background tasks
    try:
        DeendayalBot.loop.create_task(check_expired_premium(DeendayalBot))
    except Exception:
        logger.exception("Failed to schedule premium check task")

    # Logs
    logger.info(
        "%s with Pyrogram v%s (Layer %s) started on %s",
        me.first_name,
        PYROGRAM_VERSION,
        PYRO_LAYER,
        DeendayalBot.username,
    )
    logger.info(LOG_STR)
    logger.info(script.LOGO)

    # Restart message to LOG_CHANNEL
    try:
        tz = pytz.timezone("Asia/Kolkata")
        now = datetime.now(tz)
        today = date.today()
        time_str = now.strftime("%H:%M:%S %p")
        await DeendayalBot.send_message(
            chat_id=LOG_CHANNEL,
            text=script.RESTART_TXT.format(temp.B_LINK, today, time_str),
        )
    except Exception:
        logger.exception("Failed to send restart message to LOG_CHANNEL")

    # Start aiohttp web server
    try:
        runner = web.AppRunner(await web_server())
        await runner.setup()
        site = web.TCPSite(runner, "0.0.0.0", PORT)
        await site.start()
        logger.info("🌐 Web server started on 0.0.0.0:%s", PORT)
    except Exception:
        logger.exception("Failed to start web server")

    # Idle until termination
    try:
        await idle()
    finally:
        logger.info("🛑 Shutdown initiated. Stopping DeendayalBot")
        try:
            await DeendayalBot.stop()
        except Exception:
            logger.exception("Error stopping DeendayalBot")

# -------------------------
# Entrypoint
# -------------------------
if __name__ == "__main__":
    try:
        asyncio.run(start_deendayal_bot())
    except KeyboardInterrupt:
        logger.info("Service stopped — KeyboardInterrupt received. Bye 👋")
    except Exception:
        logger.exception("Fatal exception in main loop")
