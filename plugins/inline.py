import logging
from pyrogram import Client, emoji, filters
from pyrogram.errors.exceptions.bad_request_400 import QueryIdInvalid
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InlineQueryResultCachedDocument,
    InlineQuery,
)
from database.ia_filterdb import get_search_results
from utils import is_req_subscribed, get_size, temp
from info import CACHE_TIME, AUTH_USERS, AUTH_CHANNEL, CUSTOM_FILE_CAPTION
from database.connections_mdb import active_connection

logger = logging.getLogger(__name__)
cache_time = 0 if AUTH_USERS or AUTH_CHANNEL else CACHE_TIME


async def inline_users(query: InlineQuery) -> bool:
    """Check if user is allowed to use inline mode"""
    if AUTH_USERS:
        return query.from_user and query.from_user.id in AUTH_USERS
    return query.from_user and query.from_user.id not in temp.BANNED_USERS


@Client.on_inline_query()
async def answer(bot, query: InlineQuery):
    """Show search results for given inline query"""
    chat_id = await active_connection(str(query.from_user.id))

    if not await inline_users(query):
        await query.answer(
            results=[],
            cache_time=0,
            switch_pm_text="Not allowed ❌",
            switch_pm_parameter="unauthorized",
        )
        return

    if AUTH_CHANNEL and not await is_req_subscribed(bot, query):
        await query.answer(
            results=[],
            cache_time=0,
            switch_pm_text=(
                "🙏 Please join the channel to access files.\n\n"
                "ಚಲನಚಿತ್ರ ಪಡೆಯಲು JOIN CHANNEL ಕ್ಲಿಕ್ ಮಾಡಿ ಮತ್ತು ಸೇರಿ."
            ),
            switch_pm_parameter="subscribe",
        )
        return

    results = []

    # Handle query with optional "|type"
    if "|" in query.query:
        string, file_type = query.query.split("|", maxsplit=1)
        string = string.strip() or ""
        file_type = file_type.strip().lower() or None
    else:
        string = query.query.strip()
        file_type = None

    offset = int(query.offset or 0)
    reply_markup = get_reply_markup(string)

    files, next_offset, total = await get_search_results(
        chat_id,
        string,
        file_type=file_type,
        max_results=10,
        offset=offset,
    )

    for file in files:
        title = file.file_name
        size = get_size(file.file_size)
        f_caption = file.caption

        if CUSTOM_FILE_CAPTION:
            try:
                f_caption = CUSTOM_FILE_CAPTION.format(
                    file_name=title or "",
                    file_size=size or "",
                    file_caption=f_caption or "",
                )
            except Exception:
                logger.exception("Error formatting caption")
                f_caption = f_caption or title
        if not f_caption:
            f_caption = title

        results.append(
            InlineQueryResultCachedDocument(
                title=title,
                document_file_id=file.file_id,
                caption=f_caption,
                description=f"Size: {size}\nType: {file.file_type}",
                reply_markup=reply_markup,
            )
        )

    # Send results
    try:
        if results:
            switch_pm_text = f"{emoji.FILE_FOLDER} Results - {total}"
            if string:
                switch_pm_text += f" for {string}"

            await query.answer(
                results=results,
                is_personal=True,
                cache_time=cache_time,
                switch_pm_text=switch_pm_text,
                switch_pm_parameter="start",
                next_offset=str(next_offset),
            )
        else:
            switch_pm_text = f"{emoji.CROSS_MARK} No results"
            if string:
                switch_pm_text += f' for "{string}"'

            await query.answer(
                results=[],
                is_personal=True,
                cache_time=cache_time,
                switch_pm_text=switch_pm_text,
                switch_pm_parameter="empty",
            )
    except QueryIdInvalid:
        pass
    except Exception:
        logger.exception("Error answering inline query", exc_info=True)


def get_reply_markup(query: str):
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("🔍 Search again", switch_inline_query_current_chat=query)]]
    )