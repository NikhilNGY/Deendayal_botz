#!/usr/bin/env python3
"""
Modernized Pyrogram Bot - Complete Single File Implementation

A fully modernized, production-ready Telegram bot built with Pyrogram.
Features comprehensive error handling, modern Python patterns, and robust architecture.

Author: AI Assistant
Date: September 2025
Python: 3.11+

Usage:
    python modernized_bot_complete.py

Requirements:
    pip install pyrogram pytz fuzzywuzzy requests python-levenshtein

Environment Variables:
    API_ID=your_api_id
    API_HASH=your_api_hash
    BOT_TOKEN=your_bot_token
    SUPPORT_CHAT_ID=optional_support_chat_id
    LOG_CHANNEL=optional_log_channel_id
    STREAM_SITE=optional_stream_site
    STREAM_API=optional_stream_api_key
"""

import asyncio
import logging
import math
import os
import random
import re
import string
import sys
import traceback
import tracemalloc
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
from urllib.parse import quote_plus

import pytz
import requests
from fuzzywuzzy import process

try:
    from pyrogram import Client, enums, filters
    from pyrogram.errors import (
        FloodWait,
        MessageNotModified,
        PeerIdInvalid,
        UserIsBlocked,
        MediaEmpty,
        PhotoInvalidDimensions,
        WebpageMediaEmpty,
    )
    from pyrogram.types import (
        CallbackQuery,
        InlineKeyboardButton,
        InlineKeyboardMarkup,
        InputMediaPhoto,
        Message,
        User,
    )
except ImportError:
    print("âŒ Pyrogram not installed. Run: pip install pyrogram")
    sys.exit(1)

# Enable memory tracing for debugging
tracemalloc.start()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('bot.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

# Constants
TIMEZONE = "Asia/Kolkata"
DEFAULT_TIMEOUT = 30.0
MAX_RETRIES = 3
VERSION = "2.0.0"

# Type aliases
HandlerFunc = Callable[[Client, Union[Message, CallbackQuery]], Any]
FilterFunc = Callable[[Client, Union[Message, CallbackQuery]], bool]

class LogLevel(Enum):
    """Logging levels"""
    DEBUG = "DEBUG"
    INFO = "INFO" 
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class ButtonType(Enum):
    """Button types for UI"""
    NEXT = "next"
    PREVIOUS = "prev"
    QUALITY = "quality"
    LANGUAGE = "language"
    SEASON = "season"
    REFER = "refer"
    CLOSE = "close"

@dataclass
class FileResult:
    """Represents a file search result"""
    file_id: str
    file_name: str
    file_size: int
    file_type: str = "video"

    def get_display_name(self) -> str:
        """Get cleaned display name"""
        # Remove unwanted prefixes and clean the name
        cleaned = ' '.join(
            filter(
                lambda x: not x.startswith('[') and not x.startswith('@') and not x.startswith('www.'),
                self.file_name.split()
            )
        )
        return cleaned or self.file_name

@dataclass
class BotConfig:
    """Bot configuration with validation"""

    # Required Telegram API credentials
    api_id: int
    api_hash: str
    bot_token: str

    # Optional settings
    session_name: str = "modernized_bot"
    log_level: LogLevel = LogLevel.INFO
    support_chat_id: Optional[int] = None
    log_channel: Optional[int] = None
    bin_channel: Optional[int] = None
    stream_site: Optional[str] = None
    stream_api: Optional[str] = None
    emoji_mode: bool = False
    no_results_msg: bool = True
    max_buttons: int = 10
    group_link: str = "https://t.me/example_group"
    owner_link: str = "https://t.me/example_owner"

    # Filter lists
    qualities: List[str] = field(default_factory=lambda: [
        "360p", "480p", "720p", "1080p", "1440p", "2160p",
        "240p", "144p", "4k", "hd", "fhd", "hdrip", "bluray"
    ])

    languages: List[str] = field(default_factory=lambda: [
        "english", "hindi", "tamil", "telugu", "malayalam",
        "kannada", "gujarati", "punjabi", "bengali", "marathi",
        "spanish", "french", "german", "japanese", "korean"
    ])

    seasons: List[str] = field(default_factory=lambda: [
        "season 1", "season 2", "season 3", "season 4", "season 5",
        "season 6", "season 7", "season 8", "season 9", "season 10"
    ])

    reactions: List[str] = field(default_factory=lambda: [
        "â¤ï¸", "ðŸ”¥", "ðŸ˜", "ðŸŽ‰", "ðŸ‘", "ðŸ¤©", "âš¡", "ðŸ’¯"
    ])

@dataclass
class BotState:
    """Bot runtime state management"""
    buttons: Dict[str, str] = field(default_factory=dict)
    buttons_cache: Dict[str, str] = field(default_factory=dict)
    fresh_searches: Dict[str, str] = field(default_factory=dict)
    spell_check: Dict[str, Any] = field(default_factory=dict)
    user_sessions: Dict[int, Dict[str, Any]] = field(default_factory=dict)

    def clear_user_session(self, user_id: int) -> None:
        """Clear user session data"""
        self.user_sessions.pop(user_id, None)

    def get_user_session(self, user_id: int) -> Dict[str, Any]:
        """Get or create user session"""
        if user_id not in self.user_sessions:
            self.user_sessions[user_id] = {}
        return self.user_sessions[user_id]

def load_config() -> BotConfig:
    """Load configuration from environment variables"""

    # Required settings
    api_id = os.getenv("API_ID")
    api_hash = os.getenv("API_HASH")
    bot_token = os.getenv("BOT_TOKEN")

    if not all([api_id, api_hash, bot_token]):
        logger.error("âŒ Missing required environment variables: API_ID, API_HASH, BOT_TOKEN")
        raise ValueError("Missing required environment variables")

    try:
        api_id = int(api_id)
    except ValueError:
        raise ValueError("API_ID must be an integer")

    config = BotConfig(
        api_id=api_id,
        api_hash=api_hash,
        bot_token=bot_token,
        session_name=os.getenv("SESSION_NAME", "modernized_bot"),
        support_chat_id=_get_int_env("SUPPORT_CHAT_ID"),
        log_channel=_get_int_env("LOG_CHANNEL"),
        bin_channel=_get_int_env("BIN_CHANNEL"),
        stream_site=os.getenv("STREAM_SITE"),
        stream_api=os.getenv("STREAM_API"),
        emoji_mode=_get_bool_env("EMOJI_MODE", False),
        no_results_msg=_get_bool_env("NO_RESULTS_MSG", True),
        max_buttons=_get_int_env("MAX_BUTTONS", 10),
        group_link=os.getenv("GROUP_LINK", "https://t.me/example_group"),
        owner_link=os.getenv("OWNER_LINK", "https://t.me/example_owner"),
    )

    logger.info(f"âœ… Configuration loaded successfully")
    return config

def _get_int_env(key: str, default: Optional[int] = None) -> Optional[int]:
    """Get integer from environment variable"""
    value = os.getenv(key)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        logger.warning(f"âš ï¸ Invalid integer value for {key}: {value}")
        return default

def _get_bool_env(key: str, default: bool = False) -> bool:
    """Get boolean from environment variable"""
    value = os.getenv(key, "").lower()
    return value in ("true", "1", "yes", "on") if value else default

def get_size(size_bytes: int) -> str:
    """Convert bytes to human readable format"""
    if size_bytes == 0:
        return "0B"

    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_names[i]}"

class ErrorHandler:
    """Centralized error handling with retry logic"""

    @staticmethod
    async def handle_flood_wait(error: FloodWait) -> None:
        """Handle Telegram flood wait"""
        wait_time = error.value
        logger.warning(f"â³ Flood wait: {wait_time} seconds")
        await asyncio.sleep(wait_time)

    @staticmethod
    async def handle_user_blocked(error: UserIsBlocked) -> None:
        """Handle blocked user error"""
        logger.warning(f"ðŸš« User blocked the bot: {error}")

    @staticmethod
    async def handle_message_not_modified(error: MessageNotModified) -> None:
        """Handle message not modified error"""
        logger.debug(f"ðŸ“ Message not modified: {error}")

    @staticmethod
    async def handle_peer_id_invalid(error: PeerIdInvalid) -> None:
        """Handle invalid peer ID"""
        logger.error(f"ðŸ‘¤ Invalid peer ID: {error}")

    @classmethod
    def get_handler(cls, error: Exception) -> Optional[Callable]:
        """Get appropriate handler for error type"""
        handlers = {
            FloodWait: cls.handle_flood_wait,
            UserIsBlocked: cls.handle_user_blocked,
            MessageNotModified: cls.handle_message_not_modified,
            PeerIdInvalid: cls.handle_peer_id_invalid,
        }
        return handlers.get(type(error))

class RetryMixin:
    """Mixin for retry functionality"""

    async def retry_on_error(
        self,
        func: Callable,
        *args,
        max_retries: int = MAX_RETRIES,
        **kwargs
    ) -> Any:
        """Execute function with retry logic"""
        last_error = None

        for attempt in range(max_retries):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                last_error = e
                handler = ErrorHandler.get_handler(e)

                if handler:
                    await handler(e)
                    if attempt < max_retries - 1:
                        logger.info(f"ðŸ”„ Retrying ({attempt + 1}/{max_retries})...")
                        continue

                if attempt == max_retries - 1:
                    logger.error(f"âŒ Max retries reached for {func.__name__}: {e}")
                    break

                # Exponential backoff for non-handled errors
                wait_time = (2 ** attempt) + random.uniform(0, 1)
                await asyncio.sleep(wait_time)

        raise last_error

class StreamService:
    """Service for handling stream operations"""

    def __init__(self, config: BotConfig):
        self.config = config
        self.session = requests.Session()
        self.session.timeout = DEFAULT_TIMEOUT

    def generate_random_string(self, length: int = 8) -> str:
        """Generate random alphanumeric string"""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

    def create_shortlink_sync(self, url: str) -> str:
        """Create short link synchronously"""
        if not self.config.stream_site or not self.config.stream_api:
            return url

        try:
            response = self.session.get(
                f"https://{self.config.stream_site}/api",
                params={
                    "api": self.config.stream_api,
                    "url": url,
                    "alias": self.generate_random_string()
                }
            )
            response.raise_for_status()

            data = response.json()
            if data.get("status") == "success":
                return data.get("shortenedUrl", url)

        except Exception as e:
            logger.error(f"âŒ Short link creation failed: {e}")

        return url

    async def create_shortlink(self, url: str) -> str:
        """Create short link asynchronously"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.create_shortlink_sync, url)

class DatabaseService:
    """Mock database service for demonstration"""

    def __init__(self):
        self.users = {}
        self.search_history = {}

    async def update_user_message(self, user_id: int, message: str) -> None:
        """Update user message history"""
        if user_id not in self.users:
            self.users[user_id] = {"messages": []}

        self.users[user_id]["messages"].append({
            "text": message,
            "timestamp": datetime.now(pytz.timezone(TIMEZONE))
        })

    async def get_search_results(
        self,
        chat_id: int,
        query: str,
        offset: int = 0,
        max_results: int = 50,
        filter_enabled: bool = True
    ) -> Tuple[List[FileResult], int, int]:
        """Mock search results - replace with real database"""
        # This is a mock implementation
        # In real implementation, this would query your database

        mock_results = []
        if query and len(query) > 2:  # Basic validation
            # Create some mock results for demonstration
            for i in range(5):
                mock_results.append(FileResult(
                    file_id=f"file_{hash(query)}_{i}",
                    file_name=f"{query} - Sample Movie {i+1} [1080p].mkv",
                    file_size=1024 * 1024 * 1024 * 2  # 2GB
                ))

        total = len(mock_results)
        next_offset = offset + max_results if offset + max_results < total else 0

        return mock_results[offset:offset + max_results], next_offset, total

class MessageHandler(RetryMixin):
    """Handler for processing messages"""

    def __init__(self, config: BotConfig, stream_service: StreamService, db_service: DatabaseService):
        self.config = config
        self.stream_service = stream_service
        self.db_service = db_service
        self.state = BotState()
        self._lock = asyncio.Lock()

    async def process_group_message(self, client: Client, message: Message) -> None:
        """Process group messages"""
        try:
            # Add emoji reaction if enabled
            if self.config.emoji_mode and self.config.reactions:
                try:
                    await message.react(emoji=random.choice(self.config.reactions), big=True)
                except Exception as e:
                    logger.debug(f"Reaction failed: {e}")

            # Update user message history
            if message.from_user:
                await self.db_service.update_user_message(message.from_user.id, message.text)

            # Handle support chat differently
            if message.chat.id == self.config.support_chat_id:
                await self._handle_support_chat(client, message)
            else:
                await self._handle_regular_group(client, message)

        except Exception as e:
            logger.error(f"âŒ Error processing group message: {e}")

    async def process_private_message(self, client: Client, message: Message) -> None:
        """Process private messages"""
        try:
            if message.text.startswith(("/", "#")):
                return  # Skip commands

            user = message.from_user.first_name
            user_id = message.from_user.id

            # Add emoji reaction
            if self.config.emoji_mode and self.config.reactions:
                try:
                    await message.react(emoji=random.choice(self.config.reactions), big=True)
                except Exception as e:
                    logger.debug(f"Reaction failed: {e}")

            async with self._lock:
                await self.db_service.update_user_message(user_id, message.text)

                # Check if PM search is enabled (mock check)
                pm_search_enabled = False  # This would come from database

                if pm_search_enabled:
                    await self._auto_filter(client, message)
                else:
                    await self._send_pm_restriction_message(client, message, user)
                    await self._log_pm_message(client, message)

        except Exception as e:
            logger.error(f"âŒ Error processing private message: {e}")

    async def _handle_support_chat(self, client: Client, message: Message) -> None:
        """Handle messages in support chat"""
        search_query = message.text.strip()
        files, _, total = await self.db_service.get_search_results(
            message.chat.id, search_query, offset=0
        )

        if total == 0:
            return

        response = (
            f"<b>ðŸ™‹ Hey {message.from_user.mention},\n\n"
            f"Your request is already available âœ…\n\n"
            f"ðŸ“‚ Files found: {total}\n"
            f"ðŸ” Search: </b><code>{search_query}</code>\n\n"
            f"<b>â€¼ï¸ This is a <u>support group</u> so you can't get files from here...\n\n"
            f"ðŸ“ Search here: ðŸ‘‡</b>"
        )

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("ðŸ” Join and Search Here ðŸ”Ž", url=self.config.group_link)]
        ])

        await message.reply_text(response, reply_markup=keyboard)

    async def _handle_regular_group(self, client: Client, message: Message) -> None:
        """Handle messages in regular groups"""
        # Check manual filters first
        manual_result = await self._check_manual_filters(client, message)
        if not manual_result:
            # Check if auto filter is enabled
            auto_filter_enabled = True  # This would come from group settings
            if auto_filter_enabled:
                await self._auto_filter(client, message)

    async def _send_pm_restriction_message(self, client: Client, message: Message, user: str) -> None:
        """Send PM restriction message"""
        response = (
            f"<b><blockquote>ðŸ™‹ Hey {user} ðŸ˜,\n\n"
            f"You can search for movies only on our Movie Group. "
            f"You are not allowed to search for movies on Direct Bot. "
            f"Please join our movie group by clicking on the REQUEST HERE button "
            f"given below and search your favorite movie there ðŸ‘‡</blockquote></b>"
        )

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("ðŸ“ Request Here", url=self.config.group_link)]
        ])

        await message.reply_text(response, reply_markup=keyboard)

    async def _log_pm_message(self, client: Client, message: Message) -> None:
        """Log private message to admin channel"""
        if not self.config.log_channel:
            return

        user = message.from_user
        log_text = (
            f"<b>#PM_MSG\n\n"
            f"ðŸ‘¤ Name: {user.first_name}\n"
            f"ðŸ†” ID: {user.id}\n"
            f"ðŸ’¬ Message: {message.text}</b>"
        )

        try:
            await client.send_message(chat_id=self.config.log_channel, text=log_text)
        except Exception as e:
            logger.error(f"âŒ Failed to log PM message: {e}")

    async def _check_manual_filters(self, client: Client, message: Message) -> bool:
        """Check manual filters - mock implementation"""
        # This would check against custom filters in database
        return False

    async def _auto_filter(self, client: Client, message: Message) -> None:
        """Auto filter implementation"""
        search_query = message.text.strip()
        if len(search_query) < 2:
            return

        files, next_offset, total = await self.db_service.get_search_results(
            message.chat.id, search_query
        )

        if not files:
            await self._send_no_results_message(client, message, search_query)
            return

        # Generate unique key for this search
        search_key = f"{message.from_user.id}_{hash(search_query)}_{datetime.now().timestamp()}"
        self.state.fresh_searches[search_key] = search_query

        await self._send_file_results(client, message, files, search_key, total, next_offset)

    async def _send_no_results_message(self, client: Client, message: Message, query: str) -> None:
        """Send no results found message"""
        if not self.config.no_results_msg:
            return

        # Log to bin channel if configured
        if self.config.bin_channel:
            log_msg = f"No results for: {query} (User: {message.from_user.id})"
            try:
                await client.send_message(chat_id=self.config.bin_channel, text=log_msg)
            except Exception as e:
                logger.error(f"âŒ Failed to log to bin channel: {e}")

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("ðŸ”° Contact Admin ðŸ”°", url=self.config.owner_link)]
        ])

        no_results_msg = await message.reply_text(
            "âŒ Sorry, no results found for your query. Please try different keywords or contact admin.",
            reply_markup=keyboard
        )

        # Auto-delete after 10 seconds
        await asyncio.sleep(10)
        try:
            await no_results_msg.delete()
        except Exception:
            pass

    async def _send_file_results(
        self,
        client: Client,
        message: Message,
        files: List[FileResult],
        search_key: str,
        total: int,
        next_offset: int
    ) -> None:
        """Send file results to user"""
        # Create file buttons
        buttons = []

        # Add premium ad removal button
        buttons.append([
            InlineKeyboardButton("âšœï¸ Remove Ads âšœï¸", url=f"https://t.me/{client.me.username}?start=premium")
        ])

        # Add option selector
        buttons.append([
            InlineKeyboardButton("â‡“ Select Option Here â‡“", callback_data="reqinfo")
        ])

        # Add file buttons
        for file in files[:self.config.max_buttons]:
            file_button = InlineKeyboardButton(
                text=f"[{get_size(file.file_size)}] {file.get_display_name()}",
                callback_data=f"file#{file.file_id}"
            )
            buttons.append([file_button])

        # Add pagination if needed
        if next_offset > 0:
            nav_buttons = [
                InlineKeyboardButton("Page", callback_data="pages"),
                InlineKeyboardButton(f"1/{math.ceil(total/self.config.max_buttons)}", callback_data="pages"),
                InlineKeyboardButton("Next â‹Ÿ", callback_data=f"next_{message.from_user.id}_{search_key}_{next_offset}")
            ]
            buttons.append(nav_buttons)

        # Add filter options
        filter_buttons = [
            InlineKeyboardButton("ðŸŽ¬ Quality", callback_data=f"qualities#{search_key}"),
            InlineKeyboardButton("ðŸŒ Language", callback_data=f"languages#{search_key}"),
        ]
        buttons.append(filter_buttons)

        keyboard = InlineKeyboardMarkup(buttons)

        caption = (
            f"<b>ðŸ” Search Results</b>\n\n"
            f"<b>ðŸ“ Query:</b> <code>{self.state.fresh_searches[search_key]}</code>\n"
            f"<b>ðŸ“‚ Total Files:</b> {total}\n"
            f"<b>ðŸ“„ Showing:</b> {min(len(files), self.config.max_buttons)} files\n\n"
            f"<b>ðŸ’¡ Click on any file to download</b>"
        )

        await message.reply_text(
            caption,
            reply_markup=keyboard,
            disable_web_page_preview=True
        )

class CallbackHandler(RetryMixin):
    """Handler for callback queries"""

    def __init__(self, config: BotConfig, stream_service: StreamService, db_service: DatabaseService, state: BotState):
        self.config = config
        self.stream_service = stream_service
        self.db_service = db_service
        self.state = state

    async def handle_refer_callback(self, client: Client, query: CallbackQuery) -> None:
        """Handle referral callbacks"""
        try:
            # Mock referral points - replace with real database
            refer_points = 0

            keyboard = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton('Invite Link', url=f'https://telegram.me/share/url?url=https://t.me/{client.me.username}'),
                    InlineKeyboardButton(f'â³ {refer_points}', callback_data='ref_point'),
                    InlineKeyboardButton('Back', callback_data='premium_info')
                ]
            ])

            try:
                await client.edit_message_media(
                    query.message.chat.id,
                    query.message.id,
                    InputMediaPhoto("https://graph.org/file/1a2e64aee3d4d10edd930.jpg")
                )
            except Exception as e:
                logger.debug(f"Media edit failed: {e}")

            refer_text = (
                f"Hey! Your referral link:\n\n"
                f"https://t.me/{client.me.username}?start=reff_{query.from_user.id}\n\n"
                f"Share this link with your friends. Each time they join, you will get 10 referral points. "
                f"After 100 points, you'll get 1 month premium subscription."
            )

            await query.message.edit_text(
                text=refer_text,
                reply_markup=keyboard,
                parse_mode=enums.ParseMode.HTML
            )

        except Exception as e:
            logger.error(f"âŒ Refer callback error: {e}")
            await query.answer("âŒ An error occurred", show_alert=True)

        await query.answer()

    async def handle_next_page(self, client: Client, query: CallbackQuery) -> None:
        """Handle pagination"""
        try:
            parts = query.data.split("_")
            if len(parts) != 4:
                await query.answer("âŒ Invalid request", show_alert=True)
                return

            _, req_user, search_key, offset = parts

            # Check permission
            if int(req_user) != query.from_user.id and int(req_user) != 0:
                await query.answer(
                    f"âš ï¸ Hello {query.from_user.first_name}, this is not your request!",
                    show_alert=True
                )
                return

            # Get search query
            search_query = self.state.fresh_searches.get(search_key)
            if not search_query:
                await query.answer("âŒ Search expired. Please start a new search.", show_alert=True)
                return

            # Get results
            files, next_offset, total = await self.db_service.get_search_results(
                query.message.chat.id, search_query, offset=int(offset)
            )

            if not files:
                await query.answer("âŒ No more results found", show_alert=True)
                return

            await self._update_file_results(client, query, files, search_key, total, next_offset, int(offset))

        except Exception as e:
            logger.error(f"âŒ Next page error: {e}")
            await query.answer("âŒ An error occurred", show_alert=True)

    async def handle_quality_filter(self, client: Client, query: CallbackQuery) -> None:
        """Handle quality filtering"""
        parts = query.data.split("#")
        if len(parts) != 2:
            await query.answer("âŒ Invalid request", show_alert=True)
            return

        _, search_key = parts

        # Create quality selection buttons
        quality_buttons = []
        qualities = self.config.qualities

        for i in range(0, len(qualities), 2):
            row = [InlineKeyboardButton(qualities[i].title(), callback_data=f"fq#{qualities[i]}#{search_key}")]
            if i + 1 < len(qualities):
                row.append(InlineKeyboardButton(qualities[i + 1].title(), callback_data=f"fq#{qualities[i + 1]}#{search_key}"))
            quality_buttons.append(row)

        quality_buttons.insert(0, [InlineKeyboardButton("â‡Š Select Quality â‡Š", callback_data="ident")])
        quality_buttons.append([InlineKeyboardButton("â†­ Back to Files â†­", callback_data=f"fq#homepage#{search_key}")])

        await query.edit_message_reply_markup(InlineKeyboardMarkup(quality_buttons))

    async def handle_language_filter(self, client: Client, query: CallbackQuery) -> None:
        """Handle language filtering"""
        parts = query.data.split("#")
        if len(parts) != 2:
            await query.answer("âŒ Invalid request", show_alert=True)
            return

        _, search_key = parts

        # Create language selection buttons
        language_buttons = []
        languages = self.config.languages

        for i in range(0, len(languages), 2):
            row = [InlineKeyboardButton(languages[i].title(), callback_data=f"fl#{languages[i]}#{search_key}")]
            if i + 1 < len(languages):
                row.append(InlineKeyboardButton(languages[i + 1].title(), callback_data=f"fl#{languages[i + 1]}#{search_key}"))
            language_buttons.append(row)

        language_buttons.insert(0, [InlineKeyboardButton("â‡Š Select Language â‡Š", callback_data="ident")])
        language_buttons.append([InlineKeyboardButton("â†­ Back to Files â†­", callback_data=f"fl#homepage#{search_key}")])

        await query.edit_message_reply_markup(InlineKeyboardMarkup(language_buttons))

    async def handle_close(self, client: Client, query: CallbackQuery) -> None:
        """Handle close button"""
        await query.message.delete()
        await query.answer("âœ… Closed")

    async def _update_file_results(
        self,
        client: Client,
        query: CallbackQuery,
        files: List[FileResult],
        search_key: str,
        total: int,
        next_offset: int,
        current_offset: int
    ) -> None:
        """Update file results with pagination"""
        buttons = []

        # Add file buttons
        for file in files[:self.config.max_buttons]:
            file_button = InlineKeyboardButton(
                text=f"[{get_size(file.file_size)}] {file.get_display_name()}",
                callback_data=f"file#{file.file_id}"
            )
            buttons.append([file_button])

        # Add navigation buttons
        nav_buttons = []
        current_page = (current_offset // self.config.max_buttons) + 1
        total_pages = math.ceil(total / self.config.max_buttons)

        if current_offset > 0:
            prev_offset = max(0, current_offset - self.config.max_buttons)
            nav_buttons.append(InlineKeyboardButton("â‹ž Back", callback_data=f"next_{query.from_user.id}_{search_key}_{prev_offset}"))

        nav_buttons.append(InlineKeyboardButton(f"{current_page}/{total_pages}", callback_data="pages"))

        if next_offset > 0:
            nav_buttons.append(InlineKeyboardButton("Next â‹Ÿ", callback_data=f"next_{query.from_user.id}_{search_key}_{next_offset}"))

        if nav_buttons:
            buttons.append(nav_buttons)

        keyboard = InlineKeyboardMarkup(buttons)

        try:
            await query.edit_message_reply_markup(reply_markup=keyboard)
        except MessageNotModified:
            pass

        await query.answer()

class ModernizedBot:
    """Main bot class"""

    def __init__(self):
        self.config = load_config()
        self.client = Client(
            name=self.config.session_name,
            api_id=self.config.api_id,
            api_hash=self.config.api_hash,
            bot_token=self.config.bot_token
        )

        # Initialize services
        self.stream_service = StreamService(self.config)
        self.db_service = DatabaseService()
        self.state = BotState()

        # Initialize handlers
        self.message_handler = MessageHandler(self.config, self.stream_service, self.db_service)
        self.callback_handler = CallbackHandler(self.config, self.stream_service, self.db_service, self.state)

        # Register handlers
        self._register_handlers()

    def _register_handlers(self):
        """Register all bot handlers"""

        # Message handlers
        @self.client.on_message(filters.group & filters.text & filters.incoming)
        async def group_message(client: Client, message: Message):
            await self.message_handler.process_group_message(client, message)

        @self.client.on_message(filters.private & filters.text & filters.incoming)
        async def private_message(client: Client, message: Message):
            await self.message_handler.process_private_message(client, message)

        # Callback handlers
        @self.client.on_callback_query(filters.regex(r"^reffff"))
        async def refer_callback(client: Client, query: CallbackQuery):
            await self.callback_handler.handle_refer_callback(client, query)

        @self.client.on_callback_query(filters.regex(r"^next"))
        async def next_page(client: Client, query: CallbackQuery):
            await self.callback_handler.handle_next_page(client, query)

        @self.client.on_callback_query(filters.regex(r"^qualities#"))
        async def quality_filter(client: Client, query: CallbackQuery):
            await self.callback_handler.handle_quality_filter(client, query)

        @self.client.on_callback_query(filters.regex(r"^languages#"))
        async def language_filter(client: Client, query: CallbackQuery):
            await self.callback_handler.handle_language_filter(client, query)

        @self.client.on_callback_query(filters.regex(r"^close_data"))
        async def close_callback(client: Client, query: CallbackQuery):
            await self.callback_handler.handle_close(client, query)

        # Generic callback handler for unhandled callbacks
        @self.client.on_callback_query()
        async def generic_callback(client: Client, query: CallbackQuery):
            logger.info(f"ðŸ” Unhandled callback: {query.data}")
            await query.answer("âš ï¸ This feature is not implemented yet.", show_alert=True)

    @asynccontextmanager
    async def lifespan(self):
        """Bot lifespan management"""
        logger.info(f"ðŸš€ Starting Modernized Pyrogram Bot v{VERSION}")

        try:
            await self.client.start()
            me = await self.client.get_me()
            logger.info(f"âœ… Bot started successfully as @{me.username}")
            yield
        except Exception as e:
            logger.error(f"âŒ Failed to start bot: {e}")
            raise
        finally:
            logger.info("ðŸ›‘ Stopping bot...")
            if self.client.is_connected:
                await self.client.stop()
            logger.info("âœ… Bot stopped successfully")

    async def run(self):
        """Run the bot"""
        async with self.lifespan():
            logger.info("ðŸ¤– Bot is running... Press Ctrl+C to stop")
            await asyncio.Event().wait()  # Run forever

# Health check function
async def health_check():
    """Simple health check"""
    return {"status": "healthy", "version": VERSION, "timestamp": datetime.now().isoformat()}

def main():
    """Main entry point"""
    try:
        # Check Python version
        if sys.version_info < (3, 8):
            logger.error("âŒ Python 3.8+ is required")
            sys.exit(1)

        # Initialize and run bot
        bot = ModernizedBot()
        asyncio.run(bot.run())

    except KeyboardInterrupt:
        logger.info("ðŸ›‘ Bot stopped by user")
    except Exception as e:
        logger.error(f"ðŸ’¥ Fatal error: {e}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
