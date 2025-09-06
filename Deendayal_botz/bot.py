#!/usr/bin/env python3
"""
main.py — starts the Deendayal bot, loads plugins, initializes clients, DBs and web server.
Modernized for clarity, type safety, and best practices.
"""

import sys
import os
import asyncio
import logging
import time as _time
from pathlib import Path
from datetime import date, datetime
from typing import List

import pytz
from aiohttp import web
from pyrogram import __version__ as PYROGRAM_VERSION
from pyrogram.raw.all import layer as PYRO_LAYER
from pyrogram import idle

# -------------------------
# Project imports
# -------------------------
from Deendayal_botz.database.ia_filterdb import (
    Media,
    Media2,
    choose_mediaDB,
    tempDict,
    db as clientDB,
)
from Deendayal_botz.database.users_chats_db import db
from Deendayal_botz.info import (
    CAPTION_LANGUAGES,
    DATABASE_URI,
    DATABASE_URI2,
    LOG_CHANNEL,
    LOG_STR,
    PORT,
    ON_HEROKU,
)
from utils import temp
from Deendayal_botz.script import script
from Deendayal_botz.plugins import web_server, check_expired_premium
from Deendayal_botz.Bot import DeendayalBot
from Deendayal_botz.util.keepalive import ping_server
from Deendayal_botz.Bot.clients import initialize_clients

# -------------------------
# Logging configuration
# -------------------------
def setup_logger():
    logging.basicConfig(
        format='[%(asctime)s] %(levelname)s:%(name)s: %(message)s',
        level=logging.INFO,
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    # Reduce noise from dependencies
    for noisy_logger in ("pyrogram", "imdbpy", "aiohttp", "aiohttp.web"):
        logging.getLogger(noisy_logger).setLevel(logging.ERROR)

setup_logger()
logger = logging.getLogger(__name__)

botStartTime = _time.time()
PLUGINS_DIR = Path("plugins")

# -------------------------
# Helper functions
# -------------------------
def discover_plugin_paths(directory: Path) -> List[Path]:
    """Return list of plugin file paths matching *.py in the given directory."""
    return [p for p in directory.glob("*.py") if p.is_file()]

def import_plugin_from_path(path: Path):
    """Dynamically import a plugin module given a Path and register it under plugins.<stem>."""
    import importlib.util
    module_name = f"plugins.{path.stem}"
    try:
        spec = importlib.util.spec_from_file_location(module_name, str(path))
        module = importlib.util.module_from_spec(spec)
        if spec.loader is not None:
            spec.loader.exec_module(module)  # type: ignore
            sys.modules[module_name] = module
            logger.info(f"Deendayal dhakad Imported => {path.stem}")
        else:
            raise ImportError(f"No loader for {path}")
    except Exception as exc:
        logger.exception(f"Failed to load plugin {path}: {exc}")

# -------------------------
# Main startup coroutine
# -------------------------
async def deendayal_start():
    logger.info("Initializing Deendayal_Botz")

    # Start Telegram Bot client
    try:
        await DeendayalBot.start()
    except Exception as e:
        logger.exception("Failed to start DeendayalBot")
        raise

    # Get bot info
    me = await DeendayalBot.get_me()
    DeendayalBot.username = getattr(me, "username", None)
    logger.info(f"Bot started as: {DeendayalBot.username or 'UNKNOWN'}")

    # Initialize additional clients
    try:
        await initialize_clients()
    except Exception:
        logger.exception("Error initializing extra clients (initialize_clients)")

    # Import plugins
    for path in discover_plugin_paths(PLUGINS_DIR):
        import_plugin_from_path(path)

    # Heroku keepalive ping
    if ON_HEROKU:
        try:
            asyncio.create_task(ping_server())
        except Exception:
            logger.exception("Failed to schedule ping_server task")

    # Restore banned users/chats
    try:
        b_users, b_chats = await db.get_banned()
        temp.BANNED_USERS = b_users or []
        temp.BANNED_CHATS = b_chats or []
    except Exception:
        logger.exception("Failed to restore banned users/chats from DB")

    # Ensure DB indexes & switching
    try:
        await Media.ensure_indexes()
        await Media2.ensure_indexes()
        stats = await clientDB.command("dbStats")
        data_mb = stats.get("dataSize", 0) / (1024 * 1024)
        index_mb = stats.get("indexSize", 0) / (1024 * 1024)
        free_dbSize = round(512 - (data_mb + index_mb), 2)

        if DATABASE_URI2 and free_dbSize < 62:
            tempDict["indexDB"] = DATABASE_URI2
            logger.info(f"Primary DB low on space ({free_dbSize:.2f} MB). Using secondary DB for new indexes.")
        elif not DATABASE_URI2:
            logger.error("Missing second DB URI (DATABASE_URI2). Exiting.")
            await DeendayalBot.stop()
            sys.exit(1)
        else:
            logger.info(f"Primary DB free space: {free_dbSize:.2f} MB. Using primary DB.")

        await choose_mediaDB()
    except Exception:
        logger.exception("Error while checking DB stats or choosing media DB")

    # Set runtime bot identity temp variables
    try:
        me = await DeendayalBot.get_me()
        temp.ME = me.id
        temp.U_NAME = me.username
        temp.B_NAME = me.first_name
        temp.B_LINK = me.mention
        DeendayalBot.username = f"@{me.username}" if me.username else None
    except Exception:
        logger.exception("Failed to populate temp bot identity values")

    # Start premium check task
    try:
        asyncio.create_task(check_expired_premium(DeendayalBot))
    except Exception:
        logger.exception("Failed to schedule check_expired_premium task")

    # Startup Logs
    logger.info("%s with Pyrogram v%s (Layer %s) started on %s.",
        getattr(me, "first_name", "Bot"),
        PYROGRAM_VERSION,
        PYRO_LAYER,
        DeendayalBot.username)
    logger.info(LOG_STR)
    logger.info(script.LOGO)

    # Send restart message to log channel
    try:
        tz = pytz.timezone("Asia/Kolkata")
        now = datetime.now(tz)
        today = now.date()
        time_str = now.strftime("%I:%M:%S %p")
        await DeendayalBot.send_message(
            chat_id=LOG_CHANNEL,
            text=script.RESTART_TXT.format(temp.B_LINK, today, time_str),
        )
    except Exception:
        logger.exception("Failed to send restart message to LOG_CHANNEL")

    # Setup and start web server
    try:
        app = web.AppRunner(await web_server())
        await app.setup()
        site = web.TCPSite(app, "0.0.0.0", PORT)
        await site.start()
        logger.info(f"Web server started on 0.0.0.0:{PORT}")
    except Exception:
        logger.exception("Failed to start web server")

    # Idle and graceful shutdown
    try:
        await idle()
    finally:
        logger.info("Shutdown initiated. Stopping DeendayalBot.")
        try:
            await DeendayalBot.stop()
        except Exception:
            logger.exception("Error while stopping DeendayalBot")


# -------------------------
# Entrypoint
# -------------------------
def main():
    try:
        asyncio.run(deendayal_start())
    except KeyboardInterrupt:
        logger.info("Service Stopped — KeyboardInterrupt received. Bye 👋")
    except Exception:
        logger.exception("Fatal exception in main loop")
    finally:
        logger.info("Event loop cleanup complete.")

if __name__ == "__main__":
    main()
