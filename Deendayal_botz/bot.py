"""
Modernized Pyrogram Bot with Healthcheck for Koyeb
"""

import asyncio
import logging
import os
import threading
from contextlib import asynccontextmanager

from fastapi import FastAPI
import uvicorn
from pyrogram import Client, filters, enums
from pyrogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

# ==============================
# 🔹 Logging
# ==============================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# ==============================
# 🔹 Healthcheck Webserver
# ==============================
app = FastAPI()

@app.get("/")
def health():
    return {"status": "ok"}

def run_web():
    uvicorn.run(app, host="0.0.0.0", port=8080)

def start_web_server():
    thread = threading.Thread(target=run_web, daemon=True)
    thread.start()
    logger.info("✅ Healthcheck webserver running on port 8080")

# ==============================
# 🔹 Config Loader
# ==============================
def load_config():
    required = ["API_ID", "API_HASH", "BOT_TOKEN"]
    missing = [v for v in required if not os.getenv(v)]
    if missing:
        logger.error(f"❌ Missing env vars: {', '.join(missing)}")
        raise ValueError("Missing required environment variables")
    return {
        "API_ID": int(os.getenv("API_ID")),
        "API_HASH": os.getenv("API_HASH"),
        "BOT_TOKEN": os.getenv("BOT_TOKEN"),
    }

# ==============================
# 🔹 Handlers
# ==============================
def register_handlers(bot: Client):
    @bot.on_message(filters.private & filters.text)
    async def private_handler(client: Client, message: Message):
        await message.reply_text(
            "👋 Hello! Your bot is live on Koyeb 🚀",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("🌐 Support", url="https://t.me/placeholder")]]
            ),
        )

    @bot.on_callback_query(filters.regex("^test"))
    async def callback_handler(client: Client, query: CallbackQuery):
        await query.answer("✅ Callback working!")

# ==============================
# 🔹 Lifecycle
# ==============================
@asynccontextmanager
async def bot_context(bot: Client):
    logger.info("🚀 Bot starting up...")
    try:
        yield bot
    finally:
        logger.info("🛑 Bot shutting down...")

async def main():
    config = load_config()
    bot = Client(
        "deendayal-bot",
        api_id=config["API_ID"],
        api_hash=config["API_HASH"],
        bot_token=config["BOT_TOKEN"],
    )

    # Start healthcheck webserver
    start_web_server()

    # Register handlers
    register_handlers(bot)

    # Run bot
    async with bot_context(bot):
        await bot.start()
        logger.info(f"🤖 Bot started successfully as @{(await bot.get_me()).username}")
        await asyncio.Event().wait()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
