import os
import re
from os import getenv
from script import script

# ============================
# Utility Functions
# ============================

id_pattern = re.compile(r'^-?\d+$')

def is_enabled(value: str, default: bool = False) -> bool:
    """
    Convert environment string values to booleans.
    Accepted true values: true, yes, 1, enable, y
    Accepted false values: false, no, 0, disable, n
    """
    if not value:
        return default
    value = value.lower()
    if value in ["true", "yes", "1", "enable", "y"]:
        return True
    elif value in ["false", "no", "0", "disable", "n"]:
        return False
    return default


# ============================
# Bot Information
# ============================

SESSION = getenv("SESSION", "KR_PICTURE")
API_ID = int(getenv("API_ID", "2468192"))
API_HASH = getenv("API_HASH", "4906b3f8f198ec0e24edb2c197677678")
BOT_TOKEN = getenv("BOT_TOKEN", "")

# ============================
# Bot Settings
# ============================

CACHE_TIME = int(getenv("CACHE_TIME", 300))
USE_CAPTION_FILTER = is_enabled(getenv("USE_CAPTION_FILTER", "True"), True)

PICS = getenv("PICS", "https://envs.sh/t3L.jpg").split()
NOR_IMG = getenv("NOR_IMG", "https://graph.org/file/e20b5fdaf217252964202.jpg")
MELCOW_VID = getenv("MELCOW_VID", "https://graph.org/file/60e8a622b14796e4448ce.mp4")
SPELL_IMG = getenv("SPELL_IMG", "https://envs.sh/t3L.jpg")
SUBSCRIPTION = getenv("SUBSCRIPTION", "https://graph.org/file/242b7f1b52743938d81f1.jpg")
FSUB_PICS = getenv("FSUB_PICS", "https://graph.org/file/7478ff3eac37f4329c3d8.jpg").split()

# ============================
# Admins, Channels & Users
# ============================

ADMINS = [int(a) if id_pattern.match(a) else a for a in getenv("ADMINS", "2068233407 2098589219").split()]
CHANNELS = [int(c) if id_pattern.match(c) else c for c in getenv("CHANNELS", "-1001683081282").split()]

LOG_CHANNEL = int(getenv("LOG_CHANNEL", "-1001693006436"))
BIN_CHANNEL = int(getenv("BIN_CHANNEL", "-1001693006436"))
DEENDAYAL_MOVIE_UPDATE_CHANNEL = int(getenv("DEENDAYAL_MOVIE_UPDATE_CHANNEL", "-1001683081282"))
PREMIUM_LOGS = int(getenv("PREMIUM_LOGS", "-1001693006436"))

AUTH_CHANNEL_RAW = getenv("AUTH_CHANNEL", "-1001951277428")
AUTH_CHANNEL = int(AUTH_CHANNEL_RAW) if AUTH_CHANNEL_RAW and id_pattern.match(AUTH_CHANNEL_RAW) else None

DELETE_CHANNELS = [int(d) if id_pattern.match(d) else d for d in getenv("DELETE_CHANNELS", "-1001396923650").split()]
SUPPORT_CHAT_ID = int(getenv("SUPPORT_CHAT_ID", "-1002241869735"))
REQST_CHANNEL = int(getenv("REQST_CHANNEL_ID", "-1002617590596"))

MULTI_FSUB = [int(ch) for ch in getenv("MULTI_FSUB", "").split() if id_pattern.match(ch)]

# ============================
# Payment
# ============================

QR_CODE = getenv("QR_CODE", "https://envs.sh/t3L.jpg")
OWNER_UPI_ID = getenv("OWNER_UPI_ID", "xyz@123")


# Multi-client setup
parser = TokenParser()
MULTI_CLIENT = parser.parse_from_env()  # {1: "token1", 2: "token2", ...}


# ============================
# MongoDB
# ============================

DATABASE_URI = getenv("DATABASE_URI", "")
DATABASE_URI2 = getenv("DATABASE_URI2", "")
DATABASE_NAME = getenv("DATABASE_NAME", "Filter2")
COLLECTION_NAME = getenv("COLLECTION_NAME", "KR_PICTURE")

# ============================
# Movie Notification & Updates
# ============================

DEENDAYAL_MOVIE_UPDATE_NOTIFICATION = is_enabled(getenv("DEENDAYAL_MOVIE_UPDATE_NOTIFICATION", "True"), True)
DEENDAYAL_IMAGE_FETCH = is_enabled(getenv("DEENDAYAL_IMAGE_FETCH", "True"), True)

CAPTION_LANGUAGES = [
    "Bhojpuri", "Hindi", "Bengali", "Tamil", "English", "Bangla", "Telugu",
    "Malayalam", "Kannada", "Marathi", "Punjabi", "Bengoli", "Gujarati",
    "Korean", "Spanish", "French", "German", "Chinese", "Arabic",
    "Portuguese", "Russian", "Japanese", "Odia", "Assamese", "Urdu"
]

# ============================
# Verification
# ============================

VERIFY = is_enabled(getenv("VERIFY", "False"))
DEENDAYAL_VERIFY_EXPIRE = int(getenv("DEENDAYAL_VERIFY_EXPIRE", "1"))
DEENDAYAL_VERIFIED_LOG = int(getenv("DEENDAYAL_VERIFIED_LOG", "-1001693006436"))
HOW_TO_VERIFY = getenv("HOW_TO_VERIFY", "https://t.me/how_to_opan_linkz/6")

# ============================
# Shortener
# ============================

IS_SHORTLINK = is_enabled(getenv("IS_SHORTLINK", "False"))
SHORTLINK_URL = getenv("SHORTLINK_URL", "vplink.in")
SHORTLINK_API = getenv("SHORTLINK_API", "")
TUTORIAL = getenv("TUTORIAL", "https://t.me/how_to_opan_linkz/6")
IS_TUTORIAL = is_enabled(getenv("IS_TUTORIAL", "False"))

# ============================
# Links
# ============================

GRP_LNK = getenv("GRP_LNK", "https://t.me/+x6OfRDdUPrUwZTZl")
CHNL_LNK = getenv("CHNL_LNK", "https://t.me/+fDkIGNmk5BU5ODVl")
OWNER_LNK = getenv("OWNER_LNK", "https://t.me/NIKHIL5757H")
DEENDAYAL_MOVIE_UPDATE_CHANNEL_LNK = getenv("DEENDAYAL_MOVIE_UPDATE_CHANNEL_LNK", "https://t.me/KR_PICTURE")
OWNERID = int(getenv("OWNERID", "2068233407"))

# ============================
# Users
# ============================

AUTH_USERS = ADMINS + [int(u) if id_pattern.match(u) else u for u in getenv("AUTH_USERS", "").split()]
PREMIUM_USER = [int(u) if id_pattern.match(u) else u for u in getenv("PREMIUM_USER", "").split()]

# ============================
# Misc
# ============================

NO_RESULTS_MSG = is_enabled(getenv("NO_RESULTS_MSG", "True"), True)
MAX_B_TN = int(getenv("MAX_B_TN", "5"))
MAX_BTN = is_enabled(getenv("MAX_BTN", "True"), True)
PORT = int(getenv("PORT", "8080"))
MSG_ALRT = getenv("MSG_ALRT", "Share & Support Us ♥️")
SUPPORT_CHAT = getenv("SUPPORT_CHAT", GRP_LNK)
P_TTI_SHOW_OFF = is_enabled(getenv("P_TTI_SHOW_OFF", "True"), True)
IMDB = is_enabled(getenv("IMDB", "False"))
AUTO_FFILTER = is_enabled(getenv("AUTO_FFILTER", "True"))
AUTO_DELETE = is_enabled(getenv("AUTO_DELETE", "True"))
DELETE_TIME = int(getenv("DELETE_TIME", "900"))
SINGLE_BUTTON = is_enabled(getenv("SINGLE_BUTTON", "True"))
CUSTOM_FILE_CAPTION = getenv("CUSTOM_FILE_CAPTION", script.CAPTION)
BATCH_FILE_CAPTION = getenv("BATCH_FILE_CAPTION", CUSTOM_FILE_CAPTION)
IMDB_TEMPLATE = getenv("IMDB_TEMPLATE", script.IMDB_TEMPLATE_TXT)
LONG_IMDB_DESCRIPTION = is_enabled(getenv("LONG_IMDB_DESCRIPTION", "False"))
SPELL_CHECK_REPLY = is_enabled(getenv("SPELL_CHECK_REPLY", "True"))
MAX_LIST_ELM = getenv("MAX_LIST_ELM", None)

INDEX_REQ_CHANNEL = int(getenv("INDEX_REQ_CHANNEL", LOG_CHANNEL))
FILE_STORE_CHANNEL = [int(c) for c in getenv("FILE_STORE_CHANNEL", "").split()]
MELCOW_NEW_USERS = is_enabled(getenv("MELCOW_NEW_USERS", "False"))
PROTECT_CONTENT = is_enabled(getenv("PROTECT_CONTENT", "True"))
PUBLIC_FILE_STORE = is_enabled(getenv("PUBLIC_FILE_STORE", "True"))
PM_SEARCH = is_enabled(getenv("PM_SEARCH", "False"))
EMOJI_MODE = is_enabled(getenv("EMOJI_MODE", "False"))

# ============================
# Server / Web
# ============================

STREAM_MODE = is_enabled(getenv("STREAM_MODE", "False"))
NO_PORT = is_enabled(getenv("NO_PORT", "False"))
APP_NAME = getenv("APP_NAME") if "DYNO" in os.environ else None
ON_HEROKU = bool(APP_NAME)

BIND_ADDRESS = getenv("WEB_SERVER_BIND_ADDRESS", "0.0.0.0")
FQDN = getenv("FQDN", BIND_ADDRESS) if not ON_HEROKU else f"{APP_NAME}.herokuapp.com"

HAS_SSL = is_enabled(getenv("HAS_SSL", "True"))
URL = f"{'https' if HAS_SSL else 'http'}://{FQDN}{'' if NO_PORT else ':' + str(PORT)}/"

SLEEP_THRESHOLD = int(getenv("SLEEP_THRESHOLD", "60"))
WORKERS = int(getenv("WORKERS", "4"))
SESSION_NAME = getenv("SESSION_NAME", "DeendayalBot")
PING_INTERVAL = int(getenv("PING_INTERVAL", "1200"))

# ============================
# Reactions
# ============================

REACTIONS = [
    "🤝", "😇", "🤗", "😍", "👍", "🎅", "😐", "🥰", "🤩", "😱", "🤣", "😘",
    "👏", "😛", "😈", "🎉", "⚡️", "🫡", "🤓", "😎", "🏆", "🔥", "🤭", "🌚",
    "🆒", "👻", "😁"
]

# ============================
# Commands (Admin & Bot)
# ============================

# (keep your existing commands list & Bot_cmds dict unchanged here...)

# ============================
# Logs
# ============================

LOG_STR = "Current Customized Configurations are:-\n"
LOG_STR += "IMDB Results are enabled.\n" if IMDB else "IMDB Results are disabled.\n"
LOG_STR += "Redirect to /start in PM is enabled.\n" if P_TTI_SHOW_OFF else "Direct PM files enabled.\n"
LOG_STR += "Single button mode is enabled.\n" if SINGLE_BUTTON else "Separate buttons mode enabled.\n"
LOG_STR += f"Custom caption: {CUSTOM_FILE_CAPTION}\n" if CUSTOM_FILE_CAPTION else "Default caption enabled.\n"
LOG_STR += "Long IMDB storyline enabled.\n" if LONG_IMDB_DESCRIPTION else "Short IMDB plot enabled.\n"
LOG_STR += "Spell check is enabled.\n" if SPELL_CHECK_REPLY else "Spell check is disabled.\n"
