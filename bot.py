#!/usr/bin/env python3
"""
main.py — starts the Deendayal bot, loads plugins, initializes clients, DBs and web server.
Rewritten for clarity, robustness and better error handling.
"""

import sys
import asyncio
import glob
import importlib.util
import logging
import logging.config
import time as _time
from pathlib import Path
from datetime import date, datetime

import pytz
from aiohttp import web
from pyrogram import __version__ as PYROGRAM_VERSION
from pyrogram.raw.all import layer as PYRO_LAYER
from pyrogram import idle

# project imports (keep these the same as in your project)
from database.ia_filterdb import Media, Media2, choose_mediaDB, tempDict, db as clientDB
from database.users_chats_db import db
from info import *
from utils import temp
from script import script
from plugins import web_server, check_expired_premium
from Deendayal_botz.Bot import DeendayalBot
from Deendayal_botz.util.keepalive import ping_server
from Deendayal_botz.Bot.clients import initialize_clients

# -------------------------
# Logging configuration
# -------------------------
logging.config.fileConfig("logging.conf")
logging.getLogger().setLevel(logging.INFO)
logging.getLogger("pyrogram").setLevel(logging.ERROR)
logging.getLogger("imdbpy").setLevel(logging.ERROR)
logging.getLogger("aiohttp").setLevel(logging.ERROR)
logging.getLogger("aiohttp.web").setLevel(logging.ERROR)
logger = logging.getLogger(__name__)

# -------------------------
# Globals & state
# -------------------------
botStartTime = _time.time()
PLUGINS_GLOB = "plugins/*.py"

# -------------------------
# Helper functions
# -------------------------
def discover_plugin_paths(pattern: str):
    """Return list of plugin file paths matching pattern."""
    return [Path(p) for p in glob.glob(pattern) if Path(p).is_file()]

def import_plugin_from_path(path: Path):
    """Dynamically import a plugin module given a Path and register it under plugins.<stem>."""
    module_name = f"plugins.{path.stem}"
    try:
        spec = importlib.util.spec_from_file_location(module_name, str(path))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        sys.modules[module_name] = module
        logger.info(f"Deendayal dhakad Imported => {path.stem}")
        return module
    except Exception as exc:
        logger.exception(f"Failed to load plugin {path}: {exc}")
        return None

# -------------------------
# Main startup coroutine
# -------------------------
async def Deendayal_start():
    logger.info("\n\nInitializing Deendayal_Botz")

    # start the bot client
    try:
        await DeendayalBot.start()
    except Exception as e:
        logger.exception("Failed to start DeendayalBot: %s", e)
        raise

    # get basic bot info
    me = await DeendayalBot.get_me()
    DeendayalBot.username = getattr(me, "username", None)
    logger.info("Bot started as: %s", DeendayalBot.username or "UNKNOWN")

    # initialize additional clients if any
    try:
        await initialize_clients()
    except Exception:
        logger.exception("Error initializing extra clients (initialize_clients)")

    # import plugins
    plugin_paths = discover_plugin_paths(PLUGINS_GLOB)
    for path in plugin_paths:
        import_plugin_from_path(path)

    # heroku keepalive ping if configured
    if ON_HEROKU:
        try:
            asyncio.create_task(ping_server())
        except Exception:
            logger.exception("Failed to schedule ping_server task")

    # restore banned lists from DB into memory
    try:
        b_users, b_chats = await db.get_banned()
        temp.BANNED_USERS = b_users or []
        temp.BANNED_CHATS = b_chats or []
    except Exception:
        logger.exception("Failed to restore banned users/chats from DB")

    # ensure indexes for media collections
    try:
        await Media.ensure_indexes()
        await Media2.ensure_indexes()
    except Exception:
        logger.exception("Failed to ensure indexes on Media/Media2")

    # choose media DB according to free space
    try:
        stats = await clientDB.command("dbStats")
        data_mb = stats.get("dataSize", 0) / (1024 * 1024)
        index_mb = stats.get("indexSize", 0) / (1024 * 1024)
        free_dbSize = round(512 - (data_mb + index_mb), 2)
        if DATABASE_URI2 and free_dbSize < 62:
            tempDict["indexDB"] = DATABASE_URI2
            logger.info("Primary DB low on space (%.2f MB). Using secondary DB for new indexes.", free_dbSize)
        elif not DATABASE_URI2:
            logger.error("Missing second DB URI (DATABASE_URI2). Exiting.")
            await DeendayalBot.stop()
            sys.exit(1)
        else:
            logger.info("Primary DB free space: %.2f MB. Using primary DB.", free_dbSize)
        await choose_mediaDB()
    except Exception:
        logger.exception("Error while checking DB stats or choosing media DB")

    # set runtime temp variables for bot identity
    try:
        me = await DeendayalBot.get_me()
        temp.ME = me.id
        temp.U_NAME = me.username
        temp.B_NAME = me.first_name
        temp.B_LINK = me.mention
        DeendayalBot.username = "@" + me.username if me.username else None
    except Exception:
        logger.exception("Failed to populate temp bot identity values")

    # start background tasks
    try:
        DeendayalBot.loop.create_task(check_expired_premium(DeendayalBot))
    except Exception:
        logger.exception("Failed to schedule check_expired_premium task")

    logger.info("%s with Pyrogram v%s (Layer %s) started on %s.", me.first_name, PYROGRAM_VERSION, PYRO_LAYER, DeendayalBot.username)
    logger.info(LOG_STR)
    logger.info(script.LOGO)

    # send restart message to LOG_CHANNEL (safe guarded)
    try:
        tz = pytz.timezone("Asia/Kolkata")
        today = date.today()
        now = datetime.now(tz)
        time_str = now.strftime("%H:%M:%S %p")
        await DeendayalBot.send_message(chat_id=LOG_CHANNEL, text=script.RESTART_TXT.format(temp.B_LINK, today, time_str))
    except Exception:
        logger.exception("Failed to send restart message to LOG_CHANNEL")

    # setup and start web server (plugin-provided web_server)
    try:
        app = web.AppRunner(await web_server())
        await app.setup()
        bind_address = "0.0.0.0"
        site = web.TCPSite(app, bind_address, PORT)
        await site.start()
        logger.info("Web server started on %s:%s", bind_address, PORT)
    except Exception:
        logger.exception("Failed to start web server")

    # finally idle and wait for termination
    try:
        await idle()
    finally:
        # graceful shutdown
        logger.info("Shutdown initiated. Stopping DeendayalBot.")
        try:
            await DeendayalBot.stop()
        except Exception:
            logger.exception("Error while stopping DeendayalBot")

# -------------------------
# Entrypoint
# -------------------------
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(Deendayal_start())
    except KeyboardInterrupt:
        logger.info("Service Stopped — KeyboardInterrupt received. Bye 👋")
    except Exception:
        logger.exception("Fatal exception in main loop")
    finally:
        # allow loop cleanup
        pending = asyncio.all_tasks(loop=loop)
        for task in pending:
            task.cancel()
        try:
            loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
        except Exception:
            pass
        loop.close()
        logger.info("Event loop closed.")