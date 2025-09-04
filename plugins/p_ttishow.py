from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.errors import MessageTooLong, PeerIdInvalid, ChatAdminRequired
from info import ADMINS, LOG_CHANNEL, OWNER_LNK, MELCOW_VID
from database.users_chats_db import db, db2
from database.ia_filterdb import Media, Media2
from utils import get_size, temp, get_settings, get_readable_time
from script import script
import asyncio
import psutil
import time
from bot import botStartTime


# ===================================================================
#   GROUP MANAGEMENT
# ===================================================================

@Client.on_message(filters.new_chat_members & filters.group)
async def handle_new_chat_members(bot, message):
    """Handle new members when the bot or users join a group."""
    new_ids = [u.id for u in message.new_chat_members]

    # If the bot is added to a group
    if temp.ME in new_ids:
        if not await db.get_chat(message.chat.id):
            total = await bot.get_chat_members_count(message.chat.id)
            added_by = message.from_user.mention if message.from_user else "Anonymous"
            await bot.send_message(
                LOG_CHANNEL,
                script.LOG_TEXT_G.format(message.chat.title, message.chat.id, total, added_by),
            )
            await db.add_chat(message.chat.id, message.chat.title)

        # If the group is banned
        if message.chat.id in temp.BANNED_CHATS:
            buttons = [[InlineKeyboardButton("📌 Contact Support 📌", url=OWNER_LNK)]]
            msg = await message.reply(
                text=(
                    "<b><blockquote>"
                    "This chat is restricted from using me 🚫\n\n"
                    "If you want to know more, please contact support."
                    "</blockquote></b>"
                ),
                reply_markup=InlineKeyboardMarkup(buttons),
            )
            try:
                await msg.pin()
            except:
                pass
            await bot.leave_chat(message.chat.id)
            return

        # Normal welcome for being added
        buttons = [[InlineKeyboardButton("👩‍🌾 Bot Owner 👩‍🌾", url=OWNER_LNK)]]
        await message.reply_text(
            f"<b><blockquote>Thanks for adding me to {message.chat.title} ❣️\n\n"
            "For questions & doubts, contact support.</blockquote></b>",
            reply_markup=InlineKeyboardMarkup(buttons),
        )

    else:  # Normal users joined
        settings = await get_settings(message.chat.id)
        if settings["welcome"]:
            for u in message.new_chat_members:
                if temp.MELCOW.get("welcome"):
                    try:
                        await temp.MELCOW["welcome"].delete()
                    except:
                        pass
                temp.MELCOW["welcome"] = await message.reply_video(
                    video=MELCOW_VID,
                    caption=script.MELCOW_ENG.format(u.mention, message.chat.title),
                    reply_markup=InlineKeyboardMarkup(
                        [[InlineKeyboardButton("📌 Contact Support 📌", url=OWNER_LNK)]]
                    ),
                    parse_mode=enums.ParseMode.HTML,
                )

        if settings["auto_delete"]:
            await asyncio.sleep(600)
            try:
                await temp.MELCOW["welcome"].delete()
            except:
                pass


# ===================================================================
#   ADMIN COMMANDS (LEAVE, ENABLE, DISABLE)
# ===================================================================

@Client.on_message(filters.command("leave") & filters.user(ADMINS))
async def leave_chat(bot, message):
    """Force bot to leave a group."""
    if len(message.command) == 1:
        return await message.reply("Usage: /leave <chat_id>")

    chat = message.command[1]
    try:
        chat = int(chat)
    except ValueError:
        pass

    try:
        await bot.send_message(
            chat_id=chat,
            text="<b>My admin has asked me to leave this group. Goodbye! 👋</b>",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📌 Contact Support 📌", url=OWNER_LNK)]]),
        )
        await bot.leave_chat(chat)
        await message.reply(f"Left the chat `{chat}`")
    except Exception as e:
        await message.reply(f"Error - {e}")


@Client.on_message(filters.command("disable") & filters.user(ADMINS))
async def disable_chat(bot, message):
    """Disable a group from using the bot."""
    if len(message.command) == 1:
        return await message.reply("Usage: /disable <chat_id> [reason]")

    chat = message.command[1]
    reason = message.text.split(None, 2)[2] if len(message.text.split(None)) > 2 else "No reason provided"

    try:
        chat_id = int(chat)
    except ValueError:
        return await message.reply("Invalid chat ID")

    record = await db.get_chat(chat_id)
    if not record:
        return await message.reply("Chat not found in DB")
    if record["is_disabled"]:
        return await message.reply(f"This chat is already disabled:\nReason: <code>{record['reason']}</code>")

    await db.disable_chat(chat_id, reason)
    temp.BANNED_CHATS.append(chat_id)
    await message.reply("Chat successfully disabled")

    try:
        await bot.send_message(
            chat_id=chat_id,
            text=f"<b>This chat has been disabled.\nReason: <code>{reason}</code></b>",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📌 Contact Support 📌", url=OWNER_LNK)]]),
        )
        await bot.leave_chat(chat_id)
    except Exception as e:
        await message.reply(f"Error - {e}")


@Client.on_message(filters.command("enable") & filters.user(ADMINS))
async def enable_chat(bot, message):
    """Re-enable a previously disabled chat."""
    if len(message.command) == 1:
        return await message.reply("Usage: /enable <chat_id>")

    try:
        chat_id = int(message.command[1])
    except ValueError:
        return await message.reply("Invalid chat ID")

    record = await db.get_chat(chat_id)
    if not record:
        return await message.reply("Chat not found in DB")
    if not record.get("is_disabled"):
        return await message.reply("This chat is not disabled.")

    await db.re_enable_chat(chat_id)
    temp.BANNED_CHATS.remove(chat_id)
    await message.reply("Chat successfully re-enabled")


# ===================================================================
#   ADMIN COMMANDS (STATS, INVITE, BAN, USERS/CHATS LIST)
# ===================================================================

@Client.on_message(filters.command("stats") & filters.user(ADMINS))
async def show_stats(bot, message):
    """Show bot usage statistics."""
    reply = await message.reply("Fetching stats...")

    total_users = await db.total_users_count()
    total_chats = await db.total_chat_count()
    premium_users = await db.all_premium_users()

    file_count = await Media.count_documents()
    size = await db.get_db_size()
    free = get_size(536870912 - size)

    files2 = await Media2.count_documents()
    size2 = await db2.get_db_size()
    free2 = get_size(536870912 - size2)

    uptime = get_readable_time(time.time() - botStartTime)
    ram = psutil.virtual_memory().percent
    cpu = psutil.cpu_percent()

    await reply.edit(
        script.STATUS_TXT.format(
            total_users, total_chats, premium_users,
            file_count, get_size(size), free,
            files2, get_size(size2), free2,
            uptime, ram, cpu, file_count + files2
        )
    )


@Client.on_message(filters.command("invite") & filters.user(ADMINS))
async def generate_invite(bot, message):
    """Generate an invite link for a chat."""
    if len(message.command) == 1:
        return await message.reply("Usage: /invite <chat_id>")

    try:
        chat_id = int(message.command[1])
    except ValueError:
        return await message.reply("Invalid chat ID")

    try:
        link = await bot.create_chat_invite_link(chat_id)
    except ChatAdminRequired:
        return await message.reply("Failed: I need admin rights to generate invite links.")
    except Exception as e:
        return await message.reply(f"Error - {e}")

    await message.reply(f"Here is your invite link:\n{link.invite_link}")


@Client.on_message(filters.command("ban") & filters.user(ADMINS))
async def ban_user(bot, message):
    """Ban a user globally from using the bot."""
    if len(message.command) == 1:
        return await message.reply("Usage: /ban <user_id|username> [reason]")

    args = message.text.split(None)
    user_ref = args[1]
    reason = args[2] if len(args) > 2 else "No reason provided"

    try:
        user = await bot.get_users(int(user_ref) if user_ref.isdigit() else user_ref)
    except PeerIdInvalid:
        return await message.reply("Invalid user, make sure I’ve interacted with them before.")
    except Exception as e:
        return await message.reply(f"Error - {e}")

    record = await db.get_ban_status(user.id)
    if record["is_banned"]:
        return await message.reply(f"{user.mention} is already banned.\nReason: {record['ban_reason']}")

    await db.ban_user(user.id, reason)
    temp.BANNED_USERS.append(user.id)
    await message.reply(f"✅ {user.mention} has been banned.")


@Client.on_message(filters.command("unban") & filters.user(ADMINS))
async def unban_user(bot, message):
    """Unban a previously banned user."""
    if len(message.command) == 1:
        return await message.reply("Usage: /unban <user_id|username>")

    user_ref = message.command[1]

    try:
        user = await bot.get_users(int(user_ref) if user_ref.isdigit() else user_ref)
    except Exception as e:
        return await message.reply(f"Error - {e}")

    record = await db.get_ban_status(user.id)
    if not record["is_banned"]:
        return await message.reply(f"{user.mention} is not banned.")

    await db.remove_ban(user.id)
    if user.id in temp.BANNED_USERS:
        temp.BANNED_USERS.remove(user.id)

    await message.reply(f"✅ {user.mention} has been unbanned.")


@Client.on_message(filters.command("users") & filters.user(ADMINS))
async def list_users(bot, message):
    """List all users in the database."""
    reply = await message.reply("Fetching users...")
    users = await db.get_all_users()

    out = "👥 Users in DB:\n\n"
    async for user in users:
        out += f"<a href='tg://user?id={user['id']}'>{user['name']}</a>"
        if user["ban_status"]["is_banned"]:
            out += " (🚫 Banned)"
        out += "\n"

    try:
        await reply.edit_text(out)
    except MessageTooLong:
        with open("users.txt", "w+") as f:
            f.write(out)
        await message.reply_document("users.txt", caption="User list")


@Client.on_message(filters.command("chats") & filters.user(ADMINS))
async def list_chats(bot, message):
    """List all chats in the database."""
    reply = await message.reply("Fetching chats...")
    chats = await db.get_all_chats()

    out = "💬 Chats in DB:\n\n"
    async for chat in chats:
        out += f"**Title:** `{chat['title']}`\n**ID:** `{chat['id']}`"
        if chat["chat_status"]["is_disabled"]:
            out += " (🚫 Disabled)"
        out += "\n"

    try:
        await reply.edit_text(out)
    except MessageTooLong:
        with open("chats.txt", "w+") as f:
            f.write(out)
        await message.reply_document("chats.txt", caption="Chat list")