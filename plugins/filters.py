
import io
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from database.filters_mdb import add_filter, get_filters, delete_filter, count_filters
from database.connections_mdb import active_connection
from utils import get_file_id, parser, split_quotes
from Deendayal_botz.info import ADMINS


# -------------------------------
# ADD FILTER
# -------------------------------
@Client.on_message(filters.command(["filter", "add"]) & filters.incoming)
async def addfilter(client, message):
    user = message.from_user
    if not user:
        return await message.reply("You are anonymous admin. Use /connect {message.chat.id} in PM")

    userid = str(user.id)
    chat_type = message.chat.type
    args = message.text.split(None, 1)

    # Get group id
    if chat_type == enums.ChatType.PRIVATE:
        grp_id = await active_connection(userid)
        if not grp_id:
            return await message.reply("I'm not connected to any groups!", quote=True)
        try:
            chat = await client.get_chat(grp_id)
            title = chat.title
        except:
            return await message.reply("Make sure I'm present in your group!!", quote=True)
    elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        grp_id = message.chat.id
        title = message.chat.title
    else:
        return

    # Permission check
    st = await client.get_chat_member(grp_id, int(userid))
    if (
        st.status not in [enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER]
        and userid not in ADMINS
    ):
        return

    if len(args) < 2:
        return await message.reply("Command Incomplete :(", quote=True)

    extracted = split_quotes(args[1])
    keyword = extracted[0].lower()

    if not message.reply_to_message and len(extracted) < 2:
        return await message.reply("Add some content to save your filter!", quote=True)

    fileid, reply_text, btn, alert = None, "", [], None

    # Case 1: text + button (without reply)
    if len(extracted) >= 2 and not message.reply_to_message:
        reply_text, btn, alert = parser(extracted[1], keyword)
        if not reply_text:
            return await message.reply("You cannot have buttons alone, give some text!", quote=True)

    # Case 2: reply with buttons
    elif message.reply_to_message and message.reply_to_message.reply_markup:
        rm = message.reply_to_message.reply_markup
        btn = rm.inline_keyboard
        msg = get_file_id(message.reply_to_message)
        if msg:
            fileid = msg.file_id
            reply_text = message.reply_to_message.caption or ""
        else:
            reply_text = message.reply_to_message.text or ""
        alert = None

    # Case 3: reply with media
    elif message.reply_to_message and message.reply_to_message.media:
        msg = get_file_id(message.reply_to_message)
        fileid = msg.file_id if msg else None
        reply_text, btn, alert = parser(
            message.reply_to_message.caption or extracted[1] if len(extracted) > 1 else "",
            keyword
        )

    # Case 4: reply with text
    elif message.reply_to_message and message.reply_to_message.text:
        reply_text, btn, alert = parser(message.reply_to_message.text, keyword)

    await add_filter(grp_id, keyword, reply_text, btn, fileid, alert)

    await message.reply_text(
        f"✅ Filter for `{keyword}` added in **{title}**",
        parse_mode=enums.ParseMode.MARKDOWN,
        quote=True
    )


# -------------------------------
# VIEW FILTERS
# -------------------------------
@Client.on_message(filters.command(["viewfilters", "filters"]) & filters.incoming)
async def get_all(client, message):
    user = message.from_user
    if not user:
        return await message.reply("You are anonymous admin. Use /connect {message.chat.id} in PM")

    userid = str(user.id)
    chat_type = message.chat.type

    # Get group id
    if chat_type == enums.ChatType.PRIVATE:
        grp_id = await active_connection(userid)
        if not grp_id:
            return await message.reply("I'm not connected to any groups!", quote=True)
        try:
            chat = await client.get_chat(grp_id)
            title = chat.title
        except:
            return await message.reply("Make sure I'm present in your group!!", quote=True)
    elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        grp_id = message.chat.id
        title = message.chat.title
    else:
        return

    # Permission check
    st = await client.get_chat_member(grp_id, int(userid))
    if (
        st.status not in [enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER]
        and userid not in ADMINS
    ):
        return

    filters_list = await get_filters(grp_id)
    count = await count_filters(grp_id)

    if not count:
        return await message.reply(f"There are no active filters in **{title}**", quote=True)

    filter_text = f"📂 Total filters in **{title}**: {count}\n\n"
    filter_text += "\n".join([f" × `{word}`" for word in filters_list])

    if len(filter_text) > 4096:
        with io.BytesIO(filter_text.encode()) as f:
            f.name = "filters.txt"
            await message.reply_document(document=f, quote=True)
    else:
        await message.reply_text(filter_text, parse_mode=enums.ParseMode.MARKDOWN, quote=True)


# -------------------------------
# DELETE FILTER
# -------------------------------
@Client.on_message(filters.command("del") & filters.incoming)
async def deletefilter(client, message):
    user = message.from_user
    if not user:
        return await message.reply("You are anonymous admin. Use /connect {message.chat.id} in PM")

    userid = str(user.id)
    chat_type = message.chat.type

    # Get group id
    if chat_type == enums.ChatType.PRIVATE:
        grp_id = await active_connection(userid)
        if not grp_id:
            return await message.reply("I'm not connected to any groups!", quote=True)
        try:
            chat = await client.get_chat(grp_id)
            title = chat.title
        except:
            return await message.reply("Make sure I'm present in your group!!", quote=True)
    elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        grp_id = message.chat.id
    else:
        return

    # Permission check
    st = await client.get_chat_member(grp_id, int(userid))
    if (
        st.status not in [enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER]
        and userid not in ADMINS
    ):
        return

    try:
        _, text = message.text.split(" ", 1)
    except:
        return await message.reply(
            "❌ Mention the filter name you want to delete!\n\n"
            "`/del filtername`\n\n"
            "Use /viewfilters to view all available filters",
            parse_mode=enums.ParseMode.MARKDOWN,
            quote=True
        )

    query = text.strip().lower()
    await delete_filter(message, query, grp_id)


# -------------------------------
# DELETE ALL FILTERS
# -------------------------------
@Client.on_message(filters.command("delall") & filters.incoming)
async def delallconfirm(client, message):
    user = message.from_user
    if not user:
        return await message.reply("You are anonymous admin. Use /connect {message.chat.id} in PM")

    userid = str(user.id)
    chat_type = message.chat.type

    # Get group id
    if chat_type == enums.ChatType.PRIVATE:
        grp_id = await active_connection(userid)
        if not grp_id:
            return await message.reply("I'm not connected to any groups!", quote=True)
        try:
            chat = await client.get_chat(grp_id)
            title = chat.title
        except:
            return await message.reply("Make sure I'm present in your group!!", quote=True)
    elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        grp_id = message.chat.id
        title = message.chat.title
    else:
        return

    # Only owner or global admin can delete all
    st = await client.get_chat_member(grp_id, int(userid))
    if st.status == enums.ChatMemberStatus.OWNER or userid in ADMINS:
        await message.reply_text(
            f"⚠️ This will delete all filters from **{title}**.\nDo you want to continue?",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ YES", callback_data="delallconfirm")],
                [InlineKeyboardButton("❌ CANCEL", callback_data="delallcancel")]
            ]),
            quote=True
        )
