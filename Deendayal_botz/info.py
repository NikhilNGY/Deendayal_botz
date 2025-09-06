import re
import os
from os import environ, getenv
from Deendayal_botz.script import script

# Utility functions
id_pattern = re.compile(r'^-?\d+$')  # fixed regex (accepts negative IDs too)

def is_enabled(value, default):
    if str(value).lower() in ["true", "yes", "1", "enable", "y"]:
        return True
    elif str(value).lower() in ["false", "no", "0", "disable", "n"]:
        return False
    else:
        return default


# ============================
# Bot Information Configuration
# ============================
SESSION = environ.get('SESSION', 'KR_PICTURE')
API_ID = int(environ.get('API_ID', '22525529'))
API_HASH = environ.get('API_HASH', '840111f82bbd1d2d3de5055afccf6a92')
BOT_TOKEN = environ.get('BOT_TOKEN', "")


# ============================
# Bot Settings Configuration
# ============================
CACHE_TIME = int(environ.get('CACHE_TIME', 300))
USE_CAPTION_FILTER = is_enabled(environ.get('USE_CAPTION_FILTER', "True"), True)
INDEX_CAPTION = is_enabled(environ.get('SAVE_CAPTION', "True"), True)
PM_SEARCH = bool(environ.get('PM_SEARCH', True))  # PM Search On (True) / Off (False)
EMOJI_MODE = bool(environ.get('EMOJI_MODE', False))  # Emoji status On (True) / Off (False)
PICS = (environ.get('PICS', 'https://envs.sh/t3L.jpg')).split()
NOR_IMG = environ.get("NOR_IMG", "https://graph.org/file/e20b5fdaf217252964202.jpg")
MELCOW_PHOTO = environ.get("MELCOW_PHOTO", "https://envs.sh/t3L.jpg")
SPELL_IMG = environ.get("SPELL_IMG", "https://graph.org/file/13702ae26fb05df52667c.jpg")
SUBSCRIPTION = environ.get('SUBSCRIPTION', 'https://graph.org/file/242b7f1b52743938d81f1.jpg')
FSUB_PICS = (environ.get('FSUB_PICS', 'https://graph.org/file/7478ff3eac37f4329c3d8.jpg')).split()


# ============================
# IMDB Settings
# ============================
IMDB = is_enabled(environ.get('IMDB', "False"), False)
LONG_IMDB_DESCRIPTION = is_enabled(environ.get("LONG_IMDB_DESCRIPTION", "False"), False)
IMDB_TEMPLATE = environ.get("IMDB_TEMPLATE", f"{script.IMDB_TEMPLATE_TXT}")
SPELL_CHECK_REPLY = is_enabled(environ.get("SPELL_CHECK_REPLY", "True"), True)
MAX_LIST_ELM = environ.get("MAX_LIST_ELM", None)

# Example default languages
CAPTION_LANGUAGES = ["en", "hi", "kn"]  # English, Hindi, Kannada


# ============================
# Admin, Channels & Users Configuration
# ============================
ADMINS = [int(admin) if id_pattern.match(admin) else admin for admin in environ.get('ADMINS', '2068233407,2098589219').split(",")]
CHANNELS = [int(ch) if id_pattern.match(ch) else ch for ch in environ.get('CHANNELS', '-1001951277428').split(",")]

OWNERID = int(environ.get('OWNERID', '2068233407'))
LOG_CHANNEL = int(environ.get('LOG_CHANNEL', '-1001693006436'))
BIN_CHANNEL = int(environ.get('BIN_CHANNEL', '-1001693006436'))
PREMIUM_LOGS = int(environ.get('PREMIUM_LOGS', '-1001693006436'))
DELETE_CHANNELS = [int(dch) if id_pattern.match(dch) else dch for dch in environ.get('DELETE_CHANNELS', '-1001396923650').split(",")]
SUPPORT_CHAT_ID = environ.get('SUPPORT_CHAT_ID', '-1002241869735')
DEENDAYAL_MOVIE_UPDATE_CHANNEL = environ.get("DEENDAYAL_MOVIE_UPDATE_CHANNEL", "-1002129955308")
REQST_CHANNEL = environ.get('REQST_CHANNEL_ID', '-1002071201127')
SUPPORT_CHAT = environ.get('SUPPORT_CHAT', 'https://t.me/+sGC3kK3Q9L1kNDNl')

AUTH_CHANNEL = [int(fch) if id_pattern.match(fch) else fch for fch in environ.get('AUTH_CHANNEL', '-1001951277428').split()]
MULTI_FSUB = [int(cid) for cid in environ.get('MULTI_FSUB', '-1002495956089').split() if id_pattern.match(cid)]


# ============================
# Payment Configuration
# ============================
QR_CODE = environ.get('QR_CODE', '')
OWNER_UPI_ID = environ.get('OWNER_UPI_ID', 'xyz@123')

STAR_PREMIUM_PLANS = {
    10: "7day",
    20: "15day",
    40: "1month",
    55: "45day",
    75: "60day",
}


# ============================
# MongoDB Configuration
# ============================
DATABASE_URI = environ.get('DATABASE_URI', "")
DATABASE_NAME = environ.get('DATABASE_NAME', "Filter2")
COLLECTION_NAME = environ.get('COLLECTION_NAME', 'KR_PICTURE')

MULTIPLE_DB = is_enabled(environ.get('MULTIPLE_DB', "False"), False)
DATABASE_URI2 = environ.get('DATABASE_URI2', DATABASE_URI)


# ============================
# Movie Notification & Update Settings
# ============================
MOVIE_UPDATE_NOTIFICATION = is_enabled(environ.get('MOVIE_UPDATE_NOTIFICATION', "False"), False)
MOVIE_UPDATE_CHANNEL = int(environ.get('MOVIE_UPDATE_CHANNEL', '-1001951277428'))
DEENDAYAL_IMAGE_FETCH = is_enabled(environ.get('DEENDAYAL_IMAGE_FETCH', "True"), True)
LINK_PREVIEW = is_enabled(environ.get('LINK_PREVIEW', "False"), False)
ABOVE_PREVIEW = is_enabled(environ.get('ABOVE_PREVIEW', "True"), True)
TMDB_API_KEY = environ.get('TMDB_API_KEY', '')
TMDB_POSTER = is_enabled(environ.get('TMDB_POSTER', "False"), False)
LANDSCAPE_POSTER = is_enabled(environ.get('LANDSCAPE_POSTER', "True"), True)


# ============================
# Verification Settings
# ============================
VERIFY = is_enabled(environ.get('VERIFY', "False"), False)
DEENDAYAL_VERIFY_EXPIRE = int(environ.get('DEENDAYAL_VERIFY_EXPIRE', 24))
DEENDAYAL_VERIFIED_LOG = int(environ.get('DEENDAYAL_VERIFIED_LOG', '-1001693006436'))
HOW_TO_VERIFY = environ.get('HOW_TO_VERIFY', 'https://t.me/how_to_opan_linkz/6')

IS_VERIFY = is_enabled(environ.get('IS_VERIFY', "False"), False)
LOG_VR_CHANNEL = int(environ.get('LOG_VR_CHANNEL', '-100'))
LOG_API_CHANNEL = int(environ.get('LOG_API_CHANNEL', '-100'))
VERIFY_IMG = environ.get("VERIFY_IMG", "https://telegra.ph/file/9ecc5d6e4df5b83424896.jpg")


# ============================
# Shortener / Tutorial
# ============================
SHORTLINK_URL = environ.get("SHORTLINK_URL", "")
SHORTLINK_API = environ.get("SHORTLINK_API", "")
IS_SHORTLINK = environ.get("IS_SHORTLINK", "")
IS_TUTORIAL = is_enabled(environ.get('IS_TUTORIAL', "False"), False)

SHORTENER_API = environ.get("SHORTENER_API", "")
SHORTENER_WEBSITE = environ.get("SHORTENER_WEBSITE", "omegalinks.in")
SHORTENER_API2 = environ.get("SHORTENER_API2", "")
SHORTENER_WEBSITE2 = environ.get("SHORTENER_WEBSITE2", "omegalinks.in")
SHORTENER_API3 = environ.get("SHORTENER_API3", "")
SHORTENER_WEBSITE3 = environ.get("SHORTENER_WEBSITE3", "omegalinks.in")

TWO_VERIFY_GAP = int(environ.get('TWO_VERIFY_GAP', "1200"))
THREE_VERIFY_GAP = int(environ.get('THREE_VERIFY_GAP', "54000"))


# ============================
# Server & Web Configuration
# ============================
NO_PORT = is_enabled(environ.get('NO_PORT', "False"), False)
APP_NAME = environ.get('APP_NAME')
ON_HEROKU = 'DYNO' in environ

BIND_ADRESS = str(getenv('WEB_SERVER_BIND_ADDRESS', '0.0.0.0'))
FQDN = str(getenv('FQDN', BIND_ADRESS)) if not ON_HEROKU or getenv('FQDN') else f"{APP_NAME}.herokuapp.com"

HAS_SSL = is_enabled(getenv('HAS_SSL', "True"), True)
if HAS_SSL:
    URL = f"https://{FQDN}/"
else:
    URL = f"http://{FQDN}/"


# ============================
# Reactions
# ============================
REACTIONS = ["🤝", "😇", "🤗", "😍", "👍", "🎅", "🥰", "🔥", "🎉", "😎"]

# ============================
# Command Settings
# ============================
COMMAND_HAND_LER = environ.get("COMMAND_HAND_LER", "/")
START_COMMAND = environ.get("START_COMMAND", "start")
HELP_COMMAND = environ.get("HELP_COMMAND", "help")
ABOUT_COMMAND = environ.get("ABOUT_COMMAND", "about")
SOURCE_COMMAND = environ.get("SOURCE_COMMAND", "source")
MANUELFILTER_COMMAND = environ.get("MANUELFILTER_COMMAND", "filter")
BUTTON_COMMAND = environ.get("BUTTON_COMMAND", "button")
DELETE_COMMAND = environ.get("DELETE_COMMAND", "del")
DELETEALL_COMMAND = environ.get("DELETEALL_COMMAND", "delall")
DELETEALLFILTER_COMMAND = environ.get("DELETEALLFILTER_COMMAND", "delfilter")
DELETEALLBUTTON_COMMAND = environ.get("DELETEALLBUTTON_COMMAND", "delbutton")
LIST_COMMAND = environ.get("LIST_COMMAND", "list")
SETTINGS_COMMAND = environ.get("SETTINGS_COMMAND", "settings")
RESTART_COMMAND = environ.get("RESTART_COMMAND", "restart")
LOG_COMMAND = environ.get("LOG_COMMAND", "log")
ID_COMMAND = environ.get("ID_COMMAND", "id")
INFO_COMMAND = environ.get("INFO_COMMAND", "info")
USERS_COMMAND = environ.get("USERS_COMMAND", "users")
BROADCAST_COMMAND = environ.get("BROADCAST_COMMAND", "broadcast")
PING_COMMAND = environ.get("PING_COMMAND", "ping")
STATS_COMMAND = environ.get("STATS_COMMAND", "stats")
JSON_COMMAND = environ.get("JSON_COMMAND", "json")
PURGE_COMMAND = environ.get("PURGE_COMMAND", "purge")
PURGEALL_COMMAND = environ.get("PURGEALL_COMMAND", "purgeall")
CONNECT_COMMAND = environ.get("CONNECT_COMMAND", "connect")
DISCONNECT_COMMAND = environ.get("DISCONNECT_COMMAND", "disconnect")
CONNECTIONS_COMMAND = environ.get("CONNECTIONS_COMMAND", "connections")
IMDB_COMMAND = environ.get("IMDB_COMMAND", "imdb")
SHORTENER_COMMAND = environ.get("SHORTENER_COMMAND", "short")
REQST_COMMAND = environ.get("REQST_COMMAND", "request")
PREMIUM_COMMAND = environ.get("PREMIUM_COMMAND", "premium")
PLAN_COMMAND = environ.get("PLAN_COMMAND", "plans")


# ============================
# Bot Functionalities
# ============================
NO_RESULTS_MSG = bool(environ.get("NO_RESULTS_MSG", True))  # True if you want no results messages in Log Channel
DELETE_TIME = int(environ.get('DELETE_TIME', 900))
MAX_B_TN = int(environ.get("MAX_B_TN", "20"))
MAX_BTN = is_enabled((environ.get('MAX_BTN', "True")), True)
LANGUAGES = [lng.strip() for lng in environ.get("LANGUAGES", "en").split(",")]
PM_SEARCH = is_enabled(environ.get("PM_SEARCH", "False"), False)
AUTO_DELETE = is_enabled(environ.get("AUTO_DELETE", "True"), True)
WELCOME_DELETE = is_enabled(environ.get("WELCOME_DELETE", "True"), True)
FILE_AUTO_DELETE = is_enabled(environ.get("FILE_AUTO_DELETE", "True"), True)
AUTO_FFILTER = is_enabled(environ.get("AUTO_FFILTER", "True"), True)
PM_IMDB = is_enabled(environ.get("PM_IMDB", "False"), False)
PM_FILTER = is_enabled(environ.get("PM_FILTER", "True"), True)
PM_BUTTON = is_enabled(environ.get("PM_BUTTON", "True"), True)
LOG_VR_CHANNEL = int(environ.get('LOG_VR_CHANNEL', '-100'))
PORT = environ.get("PORT", "8080")
MSG_ALRT = environ.get('MSG_ALRT', 'Share & Support Us ♥️')


# ============================
# File Settings
# ============================
FILE_PROTECT = is_enabled(environ.get("FILE_PROTECT", "False"), False)
PROTECT_CONTENT = is_enabled(environ.get("PROTECT_CONTENT", "False"), False)
SINGLE_BUTTON = is_enabled((environ.get('SINGLE_BUTTON', "False")), False) # pm & Group button or link mode (True) / Off (False)
CUSTOM_FILE_CAPTION = environ.get("CUSTOM_FILE_CAPTION", f"{script.CAPTION}")
BATCH_FILE_CAPTION = environ.get("BATCH_FILE_CAPTION", CUSTOM_FILE_CAPTION)

# ============================
# Filter Mode
# ============================
BUTTON_MODE = environ.get("BUTTON_MODE", "single")  # default single
BUTTON_MODE = BUTTON_MODE if BUTTON_MODE in ["single", "double"] else "single"
INDEX_REQ_CHANNEL = int(environ.get('INDEX_REQ_CHANNEL', LOG_CHANNEL))
FILE_STORE_CHANNEL = [int(ch) for ch in (environ.get('FILE_STORE_CHANNEL', '')).split()]
MELCOW_NEW_USERS = is_enabled((environ.get('MELCOW_NEW_USERS', "False")), False)

# ============================
# Miscellaneous
# ============================
BAD_WORDS = environ.get("BAD_WORDS", "").split()  # avoid NoneType error
MUTE_USERS = [int(uid) for uid in environ.get("MUTE_USERS", "").split() if uid.isdigit()]

# Fake File settings
FAKE_CAPTION = environ.get("FAKE_CAPTION", "This is a fake caption")
FAKE_FILE = is_enabled(environ.get("FAKE_FILE", "False"), False)

# ============================
# Done! Config successfully loaded
# ============================
print("✅ Config loaded successfully with no errors")

# ============================
# Logs Configuration
# ============================
LOG_STR = "Current Customized Configurations are:-\n"
LOG_STR += ("IMDB Results are enabled.\n" if True else "IMDB Results are disabled.\n")
LOG_STR += (f"CUSTOM_FILE_CAPTION: {script.CAPTION}\n")
