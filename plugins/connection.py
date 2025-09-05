from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from Deendayal_botz.database.connections_mdb import add_connection, all_connections, if_active, delete_connection
from Deendayal_botz.info import ADMINS
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)


# -------------------------------
# CONNECT COMMAND
# -------------------------------
@Client.on_message((filters.private | filters.group) & filters.command("connect"))
async def addconnection(client, message):
    userid = message.from_user.id if message.from_user else None
    if not userid:
        return await message.reply("You are anonymous admin. Use /connect <group_id> in PM")

    chat_type = message.chat.type

    # Private Chat -> user must provide group_id
    if chat_type == enums.ChatType.PRIVATE:
        try:
            _, group_id = message.text.split(" ", 1)
            group_id = int(group_id.strip())
        except Exception:
            return await message.reply_text(
                "<b>Enter in correct format!</b>\n\n"
                "<code>/connect groupid</code>\n\n"
                "<i>Get your Group ID by adding me to your group and using <code>/id</code></i>",
                quote=True
            )

    # Group or Supergroup
    elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        group_id = message.chat.id

    # Check if user is admin in that group
    try:
        st = await client.get_chat_member(group_id, userid)
        if (
            st.status not in [enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER]
            and str(userid) not in ADMINS
        ):
            return await message.reply_text("You must be an admin in that group!", quote=True)
    except Exception as e:
        logger.exception(e)
        return await message.reply_text(
            "Invalid Group ID!\n\nIf correct, make sure I’m present in that group.",
            quote=True
        )

    # Check if bot is admin in that group
    try:
        st = await client.get_chat_member(group_id, "me")
        if st.status != enums.ChatMemberStatus.ADMINISTRATOR:
            return await message.reply_text("I need to be an admin in that group!", quote=True)

        ttl = await client.get_chat(group_id)
        title = ttl.title

        # Save connection
        addcon = await add_connection(str(group_id), str(userid))
        if addcon:
            await message.reply_text(
                f"✅ Successfully connected to **{title}**\nNow you can manage your group from my PM!",
                quote=True,
                parse_mode=enums.ParseMode.MARKDOWN
            )
            if chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
                await client.send_message(
                    userid,
                    f"Connected to **{title}** ✅",
                    parse_mode=enums.ParseMode.MARKDOWN
                )
        else:
            await message.reply_text("⚠️ You're already connected to this chat!", quote=True)

    except Exception as e:
        logger.exception(e)
        await message.reply_text("❌ Some error occurred! Try again later.", quote=True)


# -------------------------------
# DISCONNECT COMMAND
# -------------------------------
@Client.on_message((filters.private | filters.group) & filters.command("disconnect"))
async def deleteconnection(client, message):
    userid = message.from_user.id if message.from_user else None
    if not userid:
        return await message.reply("You are anonymous admin. Use /disconnect <group_id> in PM")

    chat_type = message.chat.type

    if chat_type == enums.ChatType.PRIVATE:
        return await message.reply_text("Run /connections to view or disconnect from groups!", quote=True)

    elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        group_id = message.chat.id

        st = await client.get_chat_member(group_id, userid)
        if (
            st.status not in [enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER]
            and str(userid) not in ADMINS
        ):
            return

        delcon = await delete_connection(str(userid), str(group_id))
        if delcon:
            await message.reply_text("✅ Successfully disconnected from this chat", quote=True)
        else:
            await message.reply_text("⚠️ This chat isn’t connected!\nUse /connect to connect first.", quote=True)


# -------------------------------
# CONNECTIONS LIST
# -------------------------------
@Client.on_message(filters.private & filters.command("connections"))
async def connections(client, message):
    userid = str(message.from_user.id)

    groupids = await all_connections(userid)
    if not groupids:
        return await message.reply_text(
            "⚠️ No active connections found!\nConnect to some groups first.",
            quote=True
        )

    buttons = []
    for groupid in groupids:
        try:
            chat = await client.get_chat(int(groupid))
            title = chat.title
            active = await if_active(userid, str(groupid))
            act = " ✅ ACTIVE" if active else ""
            buttons.append(
                [InlineKeyboardButton(text=f"{title}{act}", callback_data=f"groupcb:{groupid}:{act}")]
            )
        except Exception as e:
            logger.warning(f"Failed to fetch group {groupid}: {e}")

    if buttons:
        await message.reply_text(
            "📌 Your connected groups:\n\n",
            reply_markup=InlineKeyboardMarkup(buttons),
            quote=True
        )
    else:
        await message.reply_text(
            "⚠️ No active connections found!\nConnect to some groups first.",
            quote=True
        )
