from motor.motor_asyncio import AsyncIOMotorClient
from info import DATABASE_URI
from datetime import datetime


class Database:
    def __init__(self, uri: str, db_name: str):
        self.client = AsyncIOMotorClient(uri)
        self.db = self.client[db_name]
        self.users = self.db.users
        self.config = self.db.configuration

    # ================================
    # Top Messages Management
    # ================================
    async def update_top_messages(self, user_id: int, message_text: str):
        user = await self.users.find_one({"user_id": user_id, "messages.text": message_text})

        if not user:
            await self.users.update_one(
                {"user_id": user_id},
                {"$push": {"messages": {"text": message_text, "count": 1}}},
                upsert=True
            )
        else:
            await self.users.update_one(
                {"user_id": user_id, "messages.text": message_text},
                {"$inc": {"messages.$.count": 1}}
            )

    async def get_top_messages(self, limit: int = 30):
        pipeline = [
            {"$unwind": "$messages"},
            {"$group": {"_id": "$messages.text", "count": {"$sum": "$messages.count"}}},
            {"$sort": {"count": -1}},
            {"$limit": limit}
        ]
        results = await self.users.aggregate(pipeline).to_list(limit)
        return [res["_id"] for res in results]

    async def delete_all_messages(self):
        await self.users.delete_many({})

    # ================================
    # Configuration Defaults
    # ================================
    def create_configuration_data(
        self,
        maintenance_mode: bool = False,
        auto_accept: bool = True,
        one_link: bool = True,
        one_link_one_file_group: bool = False,
        private_filter: bool = True,
        group_filter: bool = True,
        terms: bool = True,
        spell_check: bool = True,
        forcesub: bool = True,
        shortener: str = None,
        no_ads: bool = False,
        advertisement: dict = None
    ) -> dict:
        return {
            "maintenance_mode": maintenance_mode,
            "auto_accept": auto_accept,
            "one_link": one_link,
            "one_link_one_file_group": one_link_one_file_group,
            "private_filter": private_filter,
            "group_filter": group_filter,
            "terms": terms,
            "spell_check": spell_check,
            "forcesub": forcesub,
            "shortener": shortener,
            "no_ads": no_ads,
            "advertisement": advertisement,
        }

    # ================================
    # Advertisement Management
    # ================================
    async def update_advertisement(self, ads_string=None, ads_name=None, expiry=None, impression=None):
        config = await self.config.find_one({})
        if not config:
            await self.config.insert_one(self.create_configuration_data())
            config = await self.config.find_one({})

        advertisement = config.get("advertisement", {}) or {}

        advertisement.update({
            "ads_string": ads_string,
            "ads_name": ads_name,
            "expiry": expiry,
            "impression_count": impression
        })

        await self.config.update_one({}, {"$set": {"advertisement": advertisement}}, upsert=True)

    async def update_advertisement_impression(self, impression: int = None):
        await self.config.update_one(
            {}, {"$set": {"advertisement.impression_count": impression}}, upsert=True
        )

    async def get_advertisement(self):
        config = await self.config.find_one({})
        if not config:
            await self.config.insert_one(self.create_configuration_data())
            config = await self.config.find_one({})

        advertisement = config.get("advertisement", None)
        if advertisement:
            return (
                advertisement.get("ads_string"),
                advertisement.get("ads_name"),
                advertisement.get("impression_count")
            )
        return None, None, None

    async def reset_advertisement_if_expired(self):
        config = await self.config.find_one({})
        if config:
            advertisement = config.get("advertisement")
            if advertisement:
                impression_count = advertisement.get("impression_count", 0)
                expiry = advertisement.get("expiry")

                if (impression_count == 0) or (expiry and datetime.now() > expiry):
                    await self.config.update_one({}, {"$set": {"advertisement": None}})

    # ================================
    # Generic Config Manager
    # ================================
    async def update_configuration(self, key: str, value):
        try:
            await self.config.update_one({}, {"$set": {key: value}}, upsert=True)
        except Exception as e:
            print(f"[Config Update Error] {e}")

    async def get_configuration_value(self, key: str):
        config = await self.config.find_one({})
        if not config:
            await self.config.insert_one(self.create_configuration_data())
            config = await self.config.find_one({})
        return config.get(key, False)


# Instance
mdb = Database(DATABASE_URI, "admin_database")
