import os
import re
import json
import base64
import logging

from pyrogram import Client, filters, enums, types
from pyrogram.errors import ChannelInvalid, UsernameInvalid, UsernameNotModified

from info import ADMINS, LOG_CHANNEL, FILE_STORE_CHANNEL, PUBLIC_FILE_STORE
from database.ia_filterdb import unpack_new_file_id
from utils import temp

# ==============================
# Logger Setup
# ==============================
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


# ==============================
# Permissions
# ==============================
async def allowed(_, __, message: types.Message) -> bool:
    """Check if user is allowed to generate links."""
    if PUBLIC_FILE_STORE:
        return True
    return bool(message.from_user and message.from_user.id in ADMINS)


# ==============================
# Single File Link Generator
# ==============================
@Client.on_message(filters.command(["link", "plink"]) & filters.create(allowed))
async def gen_link_single(bot: Client, message: types.Message):
    replied = message.reply_to_message
    if not replied:
        return await message.reply("⚠️ Reply to a media message to get a shareable link.")

    if replied.media not in [
        enums.MessageMediaType.VIDEO,
        enums.MessageMediaType.AUDIO,
        enums.MessageMediaType.DOCUMENT,
    ]:
        return await message.reply("⚠️ Only Video, Audio, or Document messages are supported.")

    if message.has_protected_content and message.chat.id not in ADMINS:
        return await message.reply("⚠️ Protected content can't be shared.")

    file_id, _ = unpack_new_file_id(getattr(replied, replied.media.value).file_id)
    prefix = "filep_" if message.text.lower().startswith("/plink") else "file_"
    encoded = base64.urlsafe_b64encode(f"{prefix}{file_id}".encode()).decode().strip("=")

    await message.reply(
        f"✅ Here is your link:\n\n👉 https://t.me/{temp.U_NAME}?start={encoded}"
    )


# ==============================
# Batch Link Generator
# ==============================
@Client.on_message(filters.command(["batch", "pbatch"]) & filters.create(allowed))
async def gen_link_batch(bot: Client, message: types.Message):
    parts = message.text.strip().split(" ")
    if len(parts) != 3:
        return await message.reply(
            "⚠️ Use correct format.\n\nExample:\n"
            "<code>/batch https://t.me/ChannelName/10 https://t.me/ChannelName/20</code>"
        )

    cmd, first, last = parts
    regex = re.compile(r"(https://)?(t\.me|telegram\.me|telegram\.dog)/(c/)?(\d+|[a-zA-Z_0-9]+)/(\d+)$")

    # Validate first link
    f_match = regex.match(first)
    if not f_match:
        return await message.reply("⚠️ Invalid first link.")
    f_chat_id, f_msg_id = f_match.group(4), int(f_match.group(5))
    if f_chat_id.isnumeric():
        f_chat_id = int(f"-100{f_chat_id}")

    # Validate last link
    l_match = regex.match(last)
    if not l_match:
        return await message.reply("⚠️ Invalid last link.")
    l_chat_id, l_msg_id = l_match.group(4), int(l_match.group(5))
    if l_chat_id.isnumeric():
        l_chat_id = int(f"-100{l_chat_id}")

    if f_chat_id != l_chat_id:
        return await message.reply("⚠️ Chat IDs do not match.")

    # Ensure bot has access
    try:
        chat_id = (await bot.get_chat(f_chat_id)).id
    except ChannelInvalid:
        return await message.reply("❌ Private channel/group. Make me admin to index the files.")
    except (UsernameInvalid, UsernameNotModified):
        return await message.reply("❌ Invalid link specified.")
    except Exception as e:
        return await message.reply(f"⚠️ Error: {e}")

    # Status message
    sts = await message.reply("⏳ Generating batch link... This may take some time.")

    # If using file store channel
    if chat_id in FILE_STORE_CHANNEL:
        string = f"{f_msg_id}_{l_msg_id}_{chat_id}_{cmd.lower().strip()}"
        b_64 = base64.urlsafe_b64encode(string.encode()).decode().strip("=")
        return await sts.edit(
            f"✅ Here is your link:\n\n👉 https://t.me/{temp.U_NAME}?start=DSTORE-{b_64}"
        )

    # ==============================
    # Without DB (Direct File Store)
    # ==============================
    total, processed = l_msg_id - f_msg_id, 0
    collected_files = []

    FRMT = (
        "📦 Generating Batch...\n\n"
        "Total Messages: `{total}`\n"
        "Processed: `{current}`\n"
        "Remaining: `{rem}`\n"
        "Status: `{sts}`"
    )

    async for msg in bot.iter_messages(f_chat_id, l_msg_id, f_msg_id):
        processed += 1
        if not msg or msg.empty or msg.service or not msg.media:
            continue

        try:
            file_type = msg.media
            file = getattr(msg, file_type.value)
            if file:
                collected_files.append(
                    {
                        "file_id": file.file_id,
                        "caption": getattr(msg, "caption", "") or "",
                        "title": getattr(file, "file_name", ""),
                        "size": file.file_size,
                        "protect": cmd.lower().strip() == "/pbatch",
                    }
                )
        except Exception as e:
            logger.warning(f"Skipping message {msg.id}: {e}")

        # Update progress every 20 messages
        if processed % 20 == 0:
            try:
                await sts.edit(
                    FRMT.format(
                        total=total,
                        current=processed,
                        rem=total - processed,
                        sts="Saving Messages",
                    )
                )
            except Exception:
                pass

    # Save batch file
    batch_file = f"batch_{message.from_user.id}.json"
    with open(batch_file, "w+", encoding="utf-8") as out:
        json.dump(collected_files, out, ensure_ascii=False, indent=2)

    post = await bot.send_document(
        LOG_CHANNEL,
        batch_file,
        file_name="Batch.json",
        caption="⚠️ Generated for filestore.",
    )
    os.remove(batch_file)

    file_id, _ = unpack_new_file_id(post.document.file_id)
    await sts.edit(
        f"✅ Batch Link Generated!\n\n"
        f"Contains `{len(collected_files)}` files.\n\n"
        f"👉 https://t.me/{temp.U_NAME}?start=BATCH-{file_id}"
    )