import pymongo
from Deendayal_botz.info import DATABASE_URI, DATABASE_NAME
from pyrogram import enums
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

# MongoDB client
myclient = pymongo.MongoClient(DATABASE_URI)
mydb = myclient[DATABASE_NAME]


async def add_filter(grp_id, text, reply_text, btn, file, alert):
    mycol = mydb[str(grp_id)]
    data = {
        "text": str(text),
        "reply": str(reply_text),
        "btn": str(btn),
        "file": str(file),
        "alert": str(alert)
    }
    try:
        mycol.update_one({"text": str(text)}, {"$set": data}, upsert=True)
    except Exception:
        logger.exception("Some error occurred while adding filter!", exc_info=True)


async def find_filter(group_id, name):
    mycol = mydb[str(group_id)]
    query = mycol.find_one({"text": name})

    if query:
        reply_text = query.get("reply")
        btn = query.get("btn")
        fileid = query.get("file")
        alert = query.get("alert")
        return reply_text, btn, alert, fileid
    return None, None, None, None


async def get_filters(group_id):
    mycol = mydb[str(group_id)]
    texts = []

    try:
        for file in mycol.find():
            texts.append(file["text"])
    except Exception:
        pass
    return texts


async def delete_filter(message, text, group_id):
    mycol = mydb[str(group_id)]
    myquery = {"text": text}
    query = mycol.count_documents(myquery)

    if query >= 1:
        mycol.delete_one(myquery)
        await message.reply_text(
            f"`{text}` deleted. I will not respond to that filter anymore.",
            quote=True,
            parse_mode=enums.ParseMode.MARKDOWN
        )
    else:
        await message.reply_text("Couldn't find that filter!", quote=True)


async def del_all(message, group_id, title):
    if str(group_id) not in mydb.list_collection_names():
        await message.edit_text(f"Nothing to remove in {title}!")
        return

    mycol = mydb[str(group_id)]
    try:
        mycol.drop()
        await message.edit_text(f"All filters from {title} have been removed")
    except Exception:
        await message.edit_text("Couldn't remove all filters from group!")


async def count_filters(group_id):
    mycol = mydb[str(group_id)]
    count = mycol.count_documents({})
    return count if count > 0 else False


async def filter_stats():
    collections = mydb.list_collection_names()

    if "CONNECTION" in collections:
        collections.remove("CONNECTION")

    totalcount = 0
    for collection in collections:
        mycol = mydb[collection]
        totalcount += mycol.count_documents({})

    totalcollections = len(collections)

    return totalcollections, totalcount
