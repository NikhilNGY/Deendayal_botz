import motor.motor_asyncio
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
import datetime

from info import (
    DATABASE_NAME, DATABASE_URI, DATABASE_URI2,
    IMDB, IMDB_TEMPLATE, MELCOW_NEW_USERS, P_TTI_SHOW_OFF,
    SINGLE_BUTTON, SPELL_CHECK_REPLY, PROTECT_CONTENT,
    AUTO_DELETE, MAX_BTN, AUTO_FFILTER,
    SHORTLINK_API, SHORTLINK_URL, IS_SHORTLINK,
    TUTORIAL, IS_TUTORIAL, VERIFY, PM_SEARCH, MULTI_FSUB,
    DEENDAYAL_MOVIE_UPDATE_NOTIFICATION
)

# --- Synchronous Mongo (for user filenames only) ---
mongo_client = MongoClient(DATABASE_URI)
mongo_db = mongo_client["filename"]

async def add_name(user_id: int, filename: str) -> bool:
    """Add filename entry under a user. Returns False if already exists."""
    user_db = mongo_db[str(user_id)]
    if user_db.find_one({"_id": filename}):
        return False
    try:
        user_db.insert_one({"_id": filename})
        return True
    except DuplicateKeyError:
        return False

async def delete_all_msg(user_id: int):
    """Delete all stored filenames for a user."""
    user_db = mongo_db[str(user_id)]
    user_db.delete_many({})


# --- Async Mongo Database Wrapper ---
class Database:
    def __init__(self, uri: str, database_name: str):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[database_name]

        # Collections
        self.col = self.db["users"]
        self.grp = self.db["groups"]
        self.users = self.db["users_premium"]
        self.req = self.db["requests"]
        self.botcol = self.db["deendayal"]
        self.bot_id_col = self.db["bot_id"]

    # --- Join Request ---
    async def find_join_req(self, id: int) -> bool:
        return bool(await self.req.find_one({"id": id}))

    async def add_join_req(self, id: int):
        await self.req.insert_one({"id": id})

    async def del_join_req(self):
        await self.req.drop()

    # --- User / Group Templates ---
    def new_user(self, id: int, name: str) -> dict:
        return {
            "id": id,
            "name": name,
            "ban_status": {"is_banned": False, "ban_reason": ""}
        }

    def new_group(self, id: int, title: str) -> dict:
        return {
            "id": id,
            "title": title,
            "chat_status": {"is_disabled": False, "reason": ""}
        }

    # --- Verification ---
    async def update_verification(self, id: int, date: str, time: str):
        await self.col.update_one(
            {"id": id},
            {"$set": {"verification_status": {"date": str(date), "time": str(time)}}}
        )

    async def get_verified(self, id: int) -> dict:
        default = {"date": "1999-12-31", "time": "23:59:59"}
        user = await self.col.find_one({"id": id})
        return user.get("verification_status", default) if user else default

    # --- Users ---
    async def add_user(self, id: int, name: str):
        await self.col.insert_one(self.new_user(id, name))

    async def is_user_exist(self, id: int) -> bool:
        return bool(await self.col.find_one({"id": id}))

    async def total_users_count(self) -> int:
        return await self.col.count_documents({})

    async def remove_ban(self, id: int):
        await self.col.update_one({"id": id}, {"$set": {"ban_status": {"is_banned": False, "ban_reason": ""}}})

    async def ban_user(self, id: int, reason: str = "No Reason"):
        await self.col.update_one({"id": id}, {"$set": {"ban_status": {"is_banned": True, "ban_reason": reason}}})

    async def get_ban_status(self, id: int) -> dict:
        user = await self.col.find_one({"id": id})
        return user.get("ban_status", {"is_banned": False, "ban_reason": ""}) if user else {"is_banned": False, "ban_reason": ""}

    async def get_all_users(self):
        return self.col.find({})

    async def delete_user(self, id: int):
        await self.col.delete_many({"id": id})

    # --- Groups ---
    async def add_chat(self, id: int, title: str):
        await self.grp.insert_one(self.new_group(id, title))

    async def get_chat(self, id: int):
        chat = await self.grp.find_one({"id": id})
        return chat.get("chat_status") if chat else False

    async def disable_chat(self, id: int, reason: str = "No Reason"):
        await self.grp.update_one({"id": id}, {"$set": {"chat_status": {"is_disabled": True, "reason": reason}}})

    async def re_enable_chat(self, id: int):
        await self.grp.update_one({"id": id}, {"$set": {"chat_status": {"is_disabled": False, "reason": ""}}})

    async def total_chat_count(self) -> int:
        return await self.grp.count_documents({})

    async def get_all_chats(self):
        return self.grp.find({})

    async def delete_chat(self, id: int):
        await self.grp.delete_many({"id": id})

    async def get_banned(self):
        users = [u["id"] async for u in self.col.find({"ban_status.is_banned": True})]
        chats = [c["id"] async for c in self.grp.find({"chat_status.is_disabled": True})]
        return users, chats

    # --- Settings ---
    async def update_settings(self, id: int, settings: dict):
        await self.grp.update_one({"id": id}, {"$set": {"settings": settings}})

    async def get_settings(self, id: int) -> dict:
        defaults = {
            "button": SINGLE_BUTTON,
            "botpm": P_TTI_SHOW_OFF,
            "file_secure": PROTECT_CONTENT,
            "imdb": IMDB,
            "spell_check": SPELL_CHECK_REPLY,
            "welcome": MELCOW_NEW_USERS,
            "auto_delete": AUTO_DELETE,
            "auto_ffilter": AUTO_FFILTER,
            "max_btn": MAX_BTN,
            "template": IMDB_TEMPLATE,
            "shortlink": SHORTLINK_URL,
            "shortlink_api": SHORTLINK_API,
            "is_shortlink": IS_SHORTLINK,
            "tutorial": TUTORIAL,
            "is_tutorial": IS_TUTORIAL,
            "is_verify": VERIFY,
            "fsub": MULTI_FSUB
        }
        chat = await self.grp.find_one({"id": id})
        return chat.get("settings", defaults) if chat else defaults

    # --- DB Info ---
    async def get_db_size(self) -> int:
        stats = await self.db.command("dbstats")
        return stats["dataSize"]

    # --- Premium Users ---
    async def get_user(self, id: int):
        return await self.users.find_one({"id": id})

    async def update_user(self, data: dict):
        await self.users.update_one({"id": data["id"]}, {"$set": data}, upsert=True)

    async def has_premium_access(self, id: int) -> bool:
        user = await self.get_user(id)
        if not user:
            return False
        expiry = user.get("expiry_time")
        if isinstance(expiry, datetime.datetime) and datetime.datetime.now() <= expiry:
            return True
        if expiry:
            await self.users.update_one({"id": id}, {"$set": {"expiry_time": None}})
        return False

    async def get_expired(self, now: datetime.datetime):
        return [u async for u in self.users.find({"expiry_time": {"$lt": now}})]

    async def remove_premium_access(self, id: int):
        await self.users.update_one({"id": id}, {"$set": {"expiry_time": None}})

    async def check_trial_status(self, id: int) -> bool:
        user = await self.get_user(id)
        return user.get("has_free_trial", False) if user else False

    async def give_free_trial(self, id: int, minutes: int = 5):
        expiry = datetime.datetime.now() + datetime.timedelta(minutes=minutes)
        data = {"id": id, "expiry_time": expiry, "has_free_trial": True}
        await self.users.update_one({"id": id}, {"$set": data}, upsert=True)

    async def all_premium_users(self) -> int:
        return await self.users.count_documents({"expiry_time": {"$gt": datetime.datetime.now()}})

    # --- Bot Settings ---
    async def get_bot_setting(self, bot_id: int, key: str, default):
        bot = await self.botcol.find_one({"id": bot_id}, {key: 1, "_id": 0})
        return bot.get(key, default) if bot else default

    async def update_bot_setting(self, bot_id: int, key: str, value):
        await self.botcol.update_one({"id": bot_id}, {"$set": {key: value}}, upsert=True)

    async def pm_search_status(self, bot_id: int):
        return await self.get_bot_setting(bot_id, "PM_SEARCH", PM_SEARCH)

    async def update_pm_search_status(self, bot_id: int, enable: bool):
        await self.update_bot_setting(bot_id, "PM_SEARCH", enable)

    async def movie_update_status(self, bot_id: int):
        return await self.get_bot_setting(bot_id, "DEENDAYAL_MOVIE_UPDATE_NOTIFICATION", DEENDAYAL_MOVIE_UPDATE_NOTIFICATION)

    async def update_movie_update_status(self, bot_id: int, enable: bool):
        await self.update_bot_setting(bot_id, "DEENDAYAL_MOVIE_UPDATE_NOTIFICATION", enable)


# --- Instances ---
db = Database(DATABASE_URI, DATABASE_NAME)
db2 = Database(DATABASE_URI2, DATABASE_NAME)