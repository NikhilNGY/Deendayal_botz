#!/usr/bin/env python3
"""
Modern configuration management for Deendayal Bot.
Uses Pydantic BaseSettings for type-safe environment variable parsing and validation.
"""

import re
from enum import Enum
from pathlib import Path
from typing import List, Optional, Union
from urllib.parse import urlparse

from pydantic import BaseSettings, Field, validator, root_validator
from pydantic_settings import SettingsConfigDict

from Deendayal_botz.script import script
from Deendayal_botz.token_parser import TokenParser


# ============================
# Enums and Constants
# ============================

class LogLevel(str, Enum):
    """Available log levels."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class Environment(str, Enum):
    """Deployment environments."""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


# Compiled regex patterns for validation
ID_PATTERN = re.compile(r'^-?\d+$')


# ============================
# Configuration Classes
# ============================

class BotConfiguration(BaseSettings):
    """Core bot configuration settings."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Bot credentials
    session: str = Field(default="KR_PICTURE", description="Bot session name")
    api_id: int = Field(..., description="Telegram API ID")
    api_hash: str = Field(..., description="Telegram API Hash")
    bot_token: str = Field(..., description="Bot token from BotFather")
    
    # Bot behavior settings
    cache_time: int = Field(default=300, ge=0, description="Cache time in seconds")
    use_caption_filter: bool = Field(default=True, description="Enable caption filtering")
    
    @validator('api_id')
    def validate_api_id(cls, v):
        if v <= 0:
            raise ValueError("API ID must be positive")
        return v
    
    @validator('bot_token')
    def validate_bot_token(cls, v):
        if not v or len(v) < 10:
            raise ValueError("Bot token is required and must be valid")
        return v


class MediaConfiguration(BaseSettings):
    """Media and file configuration."""
    
    model_config = SettingsConfigDict(
        env_prefix="MEDIA_",
        case_sensitive=False
    )
    
    pics: List[str] = Field(
        default=["https://envs.sh/t3L.jpg"],
        description="Default picture URLs"
    )
    normal_image: str = Field(
        default="https://graph.org/file/e20b5fdaf217252964202.jpg",
        alias="NOR_IMG"
    )
    welcome_video: str = Field(
        default="https://graph.org/file/60e8a622b14796e4448ce.mp4",
        alias="MELCOW_VID"
    )
    spell_image: str = Field(
        default="https://envs.sh/t3L.jpg",
        alias="SPELL_IMG"
    )
    subscription_image: str = Field(
        default="https://graph.org/file/242b7f1b52743938d81f1.jpg",
        alias="SUBSCRIPTION"
    )
    fsub_pics: List[str] = Field(
        default=["https://graph.org/file/7478ff3eac37f4329c3d8.jpg"],
        description="Force subscription pictures"
    )
    
    @validator('pics', 'fsub_pics', pre=True)
    def parse_url_list(cls, v):
        if isinstance(v, str):
            return v.split()
        return v
    
    @validator('normal_image', 'welcome_video', 'spell_image', 'subscription_image')
    def validate_url(cls, v):
        try:
            result = urlparse(v)
            if not all([result.scheme, result.netloc]):
                raise ValueError("Invalid URL format")
        except Exception:
            raise ValueError("Invalid URL")
        return v


class ChannelConfiguration(BaseSettings):
    """Channel and user configuration."""
    
    model_config = SettingsConfigDict(
        env_prefix="CHANNEL_",
        case_sensitive=False
    )
    
    admins: List[Union[int, str]] = Field(
        default=[2068233407, 2098589219],
        description="Bot admin user IDs"
    )
    channels: List[Union[int, str]] = Field(
        default=[-1001683081282],
        description="Source channel IDs"
    )
    log_channel: int = Field(
        default=-1001693006436,
        description="Log channel ID"
    )
    bin_channel: int = Field(
        default=-1001693006436,
        description="Binary storage channel ID"
    )
    movie_update_channel: int = Field(
        default=-1001683081282,
        description="Movie update channel ID",
        alias="DEENDAYAL_MOVIE_UPDATE_CHANNEL"
    )
    premium_logs: int = Field(
        default=-1001693006436,
        description="Premium user logs channel"
    )
    auth_channel: Optional[int] = Field(
        default=None,
        description="Authorization channel ID"
    )
    delete_channels: List[Union[int, str]] = Field(
        default=[-1001396923650],
        description="Auto-delete channels"
    )
    support_chat_id: int = Field(default=-1002241869735)
    request_channel: int = Field(
        default=-1002617590596,
        alias="REQST_CHANNEL"
    )
    multi_fsub: List[int] = Field(
        default=[],
        description="Multiple force subscription channels"
    )
    
    @validator('admins', 'channels', 'delete_channels', pre=True)
    def parse_id_list(cls, v):
        if isinstance(v, str):
            return [int(x) if ID_PATTERN.match(x) else x for x in v.split()]
        return v
    
    @validator('multi_fsub', pre=True)
    def parse_int_list(cls, v):
        if isinstance(v, str):
            return [int(x) for x in v.split() if ID_PATTERN.match(x)]
        return v


class DatabaseConfiguration(BaseSettings):
    """Database configuration."""
    
    model_config = SettingsConfigDict(
        env_prefix="DB_",
        case_sensitive=False
    )
    
    primary_uri: str = Field(..., alias="DATABASE_URI", description="Primary database URI")
    secondary_uri: Optional[str] = Field(
        default=None,
        alias="DATABASE_URI2",
        description="Secondary database URI for failover"
    )
    database_name: str = Field(default="Filter2", description="Database name")
    collection_name: str = Field(default="KR_PICTURE", description="Collection name")
    
    @validator('primary_uri')
    def validate_primary_uri(cls, v):
        if not v:
            raise ValueError("Primary database URI is required")
        return v


class FeatureConfiguration(BaseSettings):
    """Feature flags and toggles."""
    
    model_config = SettingsConfigDict(
        case_sensitive=False
    )
    
    # Movie and notification features
    movie_update_notification: bool = Field(
        default=True,
        alias="DEENDAYAL_MOVIE_UPDATE_NOTIFICATION"
    )
    image_fetch: bool = Field(
        default=True,
        alias="DEENDAYAL_IMAGE_FETCH"
    )
    
    # Verification system
    verify_users: bool = Field(default=False, alias="VERIFY")
    verify_expire_days: int = Field(
        default=1,
        ge=1,
        alias="DEENDAYAL_VERIFY_EXPIRE"
    )
    verified_log_channel: int = Field(
        default=-1001693006436,
        alias="DEENDAYAL_VERIFIED_LOG"
    )
    
    # Shortener
    enable_shortlink: bool = Field(default=False, alias="IS_SHORTLINK")
    shortlink_url: str = Field(default="vplink.in")
    shortlink_api: str = Field(default="")
    enable_tutorial: bool = Field(default=False, alias="IS_TUTORIAL")
    
    # Bot behavior
    no_results_msg: bool = Field(default=True)
    max_buttons: int = Field(default=5, ge=1, le=10, alias="MAX_B_TN")
    max_btn_enabled: bool = Field(default=True, alias="MAX_BTN")
    imdb_enabled: bool = Field(default=False, alias="IMDB")
    auto_filter: bool = Field(default=True, alias="AUTO_FFILTER")
    auto_delete: bool = Field(default=True, alias="AUTO_DELETE")
    delete_time: int = Field(default=900, ge=60, description="Delete time in seconds")
    single_button: bool = Field(default=True)
    long_imdb_description: bool = Field(default=False)
    spell_check_reply: bool = Field(default=True)
    protect_content: bool = Field(default=True)
    public_file_store: bool = Field(default=True)
    pm_search: bool = Field(default=False)
    emoji_mode: bool = Field(default=False)
    stream_mode: bool = Field(default=False)


class ServerConfiguration(BaseSettings):
    """Web server configuration."""
    
    model_config = SettingsConfigDict(
        case_sensitive=False
    )
    
    port: int = Field(default=8080, ge=1, le=65535)
    bind_address: str = Field(default="0.0.0.0", alias="WEB_SERVER_BIND_ADDRESS")
    workers: int = Field(default=4, ge=1, le=32)
    sleep_threshold: int = Field(default=60, ge=10)
    ping_interval: int = Field(default=1200, ge=300)
    
    # Heroku/Cloud deployment
    app_name: Optional[str] = Field(default=None)
    has_ssl: bool = Field(default=True)
    no_port: bool = Field(default=False)
    
    @property
    def on_heroku(self) -> bool:
        """Check if running on Heroku."""
        return bool(self.app_name)
    
    @property
    def fqdn(self) -> str:
        """Get fully qualified domain name."""
        if self.on_heroku:
            return f"{self.app_name}.herokuapp.com"
        return self.bind_address
    
    @property
    def base_url(self) -> str:
        """Get base URL for the application."""
        protocol = "https" if self.has_ssl else "http"
        port_suffix = "" if self.no_port else f":{self.port}"
        return f"{protocol}://{self.fqdn}{port_suffix}/"


class PaymentConfiguration(BaseSettings):
    """Payment system configuration."""
    
    model_config = SettingsConfigDict(
        env_prefix="PAYMENT_",
        case_sensitive=False
    )
    
    qr_code: str = Field(
        default="https://envs.sh/t3L.jpg",
        alias="QR_CODE"
    )
    owner_upi_id: str = Field(default="xyz@123")


class LinksConfiguration(BaseSettings):
    """External links configuration."""
    
    model_config = SettingsConfigDict(
        env_prefix="LINK_",
        case_sensitive=False
    )
    
    group: str = Field(
        default="https://t.me/+x6OfRDdUPrUwZTZl",
        alias="GRP_LNK"
    )
    channel: str = Field(
        default="https://t.me/+fDkIGNmk5BU5ODVl",
        alias="CHNL_LNK"
    )
    owner: str = Field(
        default="https://t.me/NIKHIL5757H",
        alias="OWNER_LNK"
    )
    movie_update: str = Field(
        default="https://t.me/KR_PICTURE",
        alias="DEENDAYAL_MOVIE_UPDATE_CHANNEL_LNK"
    )
    tutorial: str = Field(
        default="https://t.me/how_to_opan_linkz/6",
        alias="TUTORIAL"
    )
    how_to_verify: str = Field(
        default="https://t.me/how_to_opan_linkz/6"
    )


# ============================
# Main Configuration Class
# ============================

class DeendayalBotConfig(BaseSettings):
    """Main configuration class that combines all settings."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        validate_default=True,
        extra="ignore"
    )
    
    # Configuration sections
    bot: BotConfiguration = Field(default_factory=BotConfiguration)
    media: MediaConfiguration = Field(default_factory=MediaConfiguration)
    channels: ChannelConfiguration = Field(default_factory=ChannelConfiguration)
    database: DatabaseConfiguration = Field(default_factory=DatabaseConfiguration)
    features: FeatureConfiguration = Field(default_factory=FeatureConfiguration)
    server: ServerConfiguration = Field(default_factory=ServerConfiguration)
    payment: PaymentConfiguration = Field(default_factory=PaymentConfiguration)
    links: LinksConfiguration = Field(default_factory=LinksConfiguration)
    
    # Direct settings for backward compatibility
    owner_id: int = Field(default=2068233407, alias="OWNERID")
    msg_alert: str = Field(default="Share & Support Us ♥️")
    session_name: str = Field(default="DeendayalBot")
    
    # File captions and templates
    custom_file_caption: str = Field(default="", description="Custom file caption")
    batch_file_caption: str = Field(default="", description="Batch file caption")
    imdb_template: str = Field(default="", description="IMDB template")
    
    # User lists
    auth_users: List[Union[int, str]] = Field(default=[], description="Authorized users")
    premium_users: List[Union[int, str]] = Field(default=[], description="Premium users")
    file_store_channels: List[int] = Field(default=[], description="File store channels")
    
    # Caption languages
    caption_languages: List[str] = Field(
        default=[
            "Bhojpuri", "Hindi", "Bengali", "Tamil", "English", "Bangla", "Telugu",
            "Malayalam", "Kannada", "Marathi", "Punjabi", "Bengoli", "Gujarati",
            "Korean", "Spanish", "French", "German", "Chinese", "Arabic",
            "Portuguese", "Russian", "Japanese", "Odia", "Assamese", "Urdu"
        ]
    )
    
    # Reactions
    reactions: List[str] = Field(
        default=[
            "🤝", "😇", "🤗", "😍", "👍", "🎅", "😐", "🥰", "🤩", "😱", "🤣", "😘",
            "👏", "😛", "😈", "🎉", "⚡️", "🫡", "🤓", "😎", "🏆", "🔥", "🤭", "🌚",
            "🆒", "👻", "😁"
        ]
    )
    
    @root_validator
    def validate_configuration(cls, values):
        """Validate configuration consistency."""
        # Set default captions if not provided
        if not values.get('custom_file_caption'):
            values['custom_file_caption'] = getattr(script, 'CAPTION', '')
        
        if not values.get('batch_file_caption'):
            values['batch_file_caption'] = values['custom_file_caption']
        
        if not values.get('imdb_template'):
            values['imdb_template'] = getattr(script, 'IMDB_TEMPLATE_TXT', '')
        
        return values
    
    @validator('auth_users', 'premium_users', pre=True)
    def parse_user_lists(cls, v):
        if isinstance(v, str):
            return [int(x) if ID_PATTERN.match(x) else x for x in v.split()]
        return v
    
    @validator('file_store_channels', pre=True)
    def parse_channel_list(cls, v):
        if isinstance(v, str):
            return [int(x) for x in v.split() if ID_PATTERN.match(x)]
        return v
    
    @property
    def multi_client(self) -> dict:
        """Get multi-client configuration."""
        parser = TokenParser(self.bot.bot_token)
        return {1: self.bot.bot_token}
    
    @property
    def log_summary(self) -> str:
        """Generate configuration summary for logging."""
        config_info = [
            "Current Customized Configurations:",
            f"IMDB Results: {'enabled' if self.features.imdb_enabled else 'disabled'}",
            f"PM Redirect: {'enabled' if not self.features.pm_search else 'disabled'}",
            f"Single Button Mode: {'enabled' if self.features.single_button else 'disabled'}",
            f"Custom Caption: {self.custom_file_caption[:50] if self.custom_file_caption else 'Default'}",
            f"Long IMDB Description: {'enabled' if self.features.long_imdb_description else 'disabled'}",
            f"Spell Check: {'enabled' if self.features.spell_check_reply else 'disabled'}",
            f"Auto Delete: {'enabled' if self.features.auto_delete else 'disabled'} ({self.features.delete_time}s)",
        ]
        return "\n".join(config_info)


# ============================
# Configuration Instance
# ============================

# Create global configuration instance
try:
    config = DeendayalBotConfig()
except Exception as e:
    print(f"Configuration error: {e}")
    raise


# ============================
# Backward Compatibility
# ============================

# Export individual settings for backward compatibility
SESSION = config.bot.session
API_ID = config.bot.api_id
API_HASH = config.bot.api_hash
BOT_TOKEN = config.bot.bot_token
CACHE_TIME = config.bot.cache_time
USE_CAPTION_FILTER = config.bot.use_caption_filter

# Media settings
PICS = config.media.pics
NOR_IMG = config.media.normal_image
MELCOW_VID = config.media.welcome_video
SPELL_IMG = config.media.spell_image
SUBSCRIPTION = config.media.subscription_image
FSUB_PICS = config.media.fsub_pics

# Channel settings
ADMINS = config.channels.admins
CHANNELS = config.channels.channels
LOG_CHANNEL = config.channels.log_channel
BIN_CHANNEL = config.channels.bin_channel
DEENDAYAL_MOVIE_UPDATE_CHANNEL = config.channels.movie_update_channel
PREMIUM_LOGS = config.channels.premium_logs
AUTH_CHANNEL = config.channels.auth_channel
DELETE_CHANNELS = config.channels.delete_channels
SUPPORT_CHAT_ID = config.channels.support_chat_id
REQST_CHANNEL = config.channels.request_channel
MULTI_FSUB = config.channels.multi_fsub

# Database settings
DATABASE_URI = config.database.primary_uri
DATABASE_URI2 = config.database.secondary_uri
DATABASE_NAME = config.database.database_name
COLLECTION_NAME = config.database.collection_name

# Feature settings
DEENDAYAL_MOVIE_UPDATE_NOTIFICATION = config.features.movie_update_notification
DEENDAYAL_IMAGE_FETCH = config.features.image_fetch
VERIFY = config.features.verify_users
DEENDAYAL_VERIFY_EXPIRE = config.features.verify_expire_days
DEENDAYAL_VERIFIED_LOG = config.features.verified_log_channel
IS_SHORTLINK = config.features.enable_shortlink
SHORTLINK_URL = config.features.shortlink_url
SHORTLINK_API = config.features.shortlink_api
IS_TUTORIAL = config.features.enable_tutorial

# Server settings
PORT = config.server.port
BIND_ADDRESS = config.server.bind_address
WORKERS = config.server.workers
ON_HEROKU = config.server.on_heroku
URL = config.server.base_url
FQDN = config.server.fqdn
HAS_SSL = config.server.has_ssl
NO_PORT = config.server.no_port
SLEEP_THRESHOLD = config.server.sleep_threshold
PING_INTERVAL = config.server.ping_interval
SESSION_NAME = config.session_name

# Payment settings
QR_CODE = config.payment.qr_code
OWNER_UPI_ID = config.payment.owner_upi_id

# Links
GRP_LNK = config.links.group
CHNL_LNK = config.links.channel
OWNER_LNK = config.links.owner
DEENDAYAL_MOVIE_UPDATE_CHANNEL_LNK = config.links.movie_update
TUTORIAL = config.links.tutorial
HOW_TO_VERIFY = config.links.how_to_verify

# Other settings
OWNERID = config.owner_id
MSG_ALRT = config.msg_alert
AUTH_USERS = config.channels.admins + config.auth_users
PREMIUM_USER = config.premium_users
CAPTION_LANGUAGES = config.caption_languages
REACTIONS = config.reactions
CUSTOM_FILE_CAPTION = config.custom_file_caption
BATCH_FILE_CAPTION = config.batch_file_caption
IMDB_TEMPLATE = config.imdb_template
MULTI_CLIENT = config.multi_client

# Feature flags
NO_RESULTS_MSG = config.features.no_results_msg
MAX_B_TN = config.features.max_buttons
MAX_BTN = config.features.max_btn_enabled
IMDB = config.features.imdb_enabled
AUTO_FFILTER = config.features.auto_filter
AUTO_DELETE = config.features.auto_delete
DELETE_TIME = config.features.delete_time
SINGLE_BUTTON = config.features.single_button
LONG_IMDB_DESCRIPTION = config.features.long_imdb_description
SPELL_CHECK_REPLY = config.features.spell_check_reply
PROTECT_CONTENT = config.features.protect_content
PUBLIC_FILE_STORE = config.features.public_file_store
PM_SEARCH = config.features.pm_search
EMOJI_MODE = config.features.emoji_mode

# Additional settings
INDEX_REQ_CHANNEL = LOG_CHANNEL
FILE_STORE_CHANNEL = config.file_store_channels
MELCOW_NEW_USERS = False
STREAM_MODE = config.features.stream_mode

# Log string
LOG_STR = config.log_summary

if __name__ == "__main__":
    # Print configuration summary when run directly
    print("Deendayal Bot Configuration:")
    print("=" * 50)
    print(config.log_summary)
    print("=" * 50)
    print("✅ Configuration loaded successfully!")
