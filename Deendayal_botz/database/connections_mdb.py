import pymongo
from Deendayal_botz.info import DATABASE_URI, DATABASE_NAME
import logging

# Logger setup
logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

# MongoDB connection
try:
    myclient = pymongo.MongoClient(DATABASE_URI)
    mydb = myclient[DATABASE_NAME]
    mycol = mydb["CONNECTION"]
except Exception as e:
    logger.exception(f"MongoDB connection failed: {e}", exc_info=True)
    raise


# -------------------------------
# ADD CONNECTION
# -------------------------------
async def add_connection(group_id: str, user_id: str) -> bool:
    """Add a connection between user and group."""
    try:
        query = mycol.find_one({"_id": user_id}, {"_id": 0, "active_group": 0})

        if query:
            group_ids = [x["group_id"] for x in query.get("group_details", [])]
            if group_id in group_ids:
                return False

        group_details = {"group_id": group_id}

        if mycol.count_documents({"_id": user_id}) == 0:
            # New user record
            data = {
                "_id": user_id,
                "group_details": [group_details],
                "active_group": group_id,
            }
            mycol.insert_one(data)
        else:
            # Update existing record
            mycol.update_one(
                {"_id": user_id},
                {
                    "$push": {"group_details": group_details},
                    "$set": {"active_group": group_id},
                },
            )
        return True

    except Exception as e:
        logger.exception(f"Error adding connection: {e}", exc_info=True)
        return False


# -------------------------------
# ACTIVE CONNECTION
# -------------------------------
async def active_connection(user_id: str):
    """Return the active group_id for a user, or None."""
    try:
        query = mycol.find_one({"_id": user_id}, {"_id": 0, "group_details": 0})
        if not query:
            return None
        return int(query.get("active_group")) if query.get("active_group") else None
    except Exception as e:
        logger.exception(f"Error fetching active connection: {e}", exc_info=True)
        return None


# -------------------------------
# ALL CONNECTIONS
# -------------------------------
async def all_connections(user_id: str):
    """Return all group_ids for a user."""
    try:
        query = mycol.find_one({"_id": user_id}, {"_id": 0, "active_group": 0})
        if query:
            return [x["group_id"] for x in query.get("group_details", [])]
        return None
    except Exception as e:
        logger.exception(f"Error fetching all connections: {e}", exc_info=True)
        return None


# -------------------------------
# IF ACTIVE
# -------------------------------
async def if_active(user_id: str, group_id: str) -> bool:
    """Check if a group is the active one for a user."""
    try:
        query = mycol.find_one({"_id": user_id}, {"_id": 0, "group_details": 0})
        return query is not None and query.get("active_group") == group_id
    except Exception as e:
        logger.exception(f"Error checking active group: {e}", exc_info=True)
        return False


# -------------------------------
# MAKE ACTIVE
# -------------------------------
async def make_active(user_id: str, group_id: str) -> bool:
    """Set a group as active for a user."""
    try:
        update = mycol.update_one({"_id": user_id}, {"$set": {"active_group": group_id}})
        return update.modified_count > 0
    except Exception as e:
        logger.exception(f"Error making group active: {e}", exc_info=True)
        return False


# -------------------------------
# MAKE INACTIVE
# -------------------------------
async def make_inactive(user_id: str) -> bool:
    """Set active_group to None for a user."""
    try:
        update = mycol.update_one({"_id": user_id}, {"$set": {"active_group": None}})
        return update.modified_count > 0
    except Exception as e:
        logger.exception(f"Error making user inactive: {e}", exc_info=True)
        return False


# -------------------------------
# DELETE CONNECTION
# -------------------------------
async def delete_connection(user_id: str, group_id: str) -> bool:
    """Remove a group connection for a user."""
    try:
        update = mycol.update_one(
            {"_id": user_id}, {"$pull": {"group_details": {"group_id": group_id}}}
        )
        if update.modified_count == 0:
            return False

        query = mycol.find_one({"_id": user_id}, {"_id": 0})
        if not query:
            return False

        if query.get("group_details"):
            # If deleted group was active, switch to the last group in list
            if query.get("active_group") == group_id:
                last_group_id = query["group_details"][-1]["group_id"]
                mycol.update_one(
                    {"_id": user_id}, {"$set": {"active_group": last_group_id}}
                )
        else:
            # No groups left → deactivate
            mycol.update_one({"_id": user_id}, {"$set": {"active_group": None}})

        return True
    except Exception as e:
        logger.exception(f"Error deleting connection: {e}", exc_info=True)
        return False
