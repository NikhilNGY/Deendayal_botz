#!/usr/bin/env python3
"""
Modern configuration management for Deendayal Bot.
Fully compatible with Pydantic v2 / pydantic-settings.
"""

import re
from enum import Enum
from typing import List, Optional, Union
from urllib.parse import urlparse

# Pydantic v2 imports
from pydantic import Field, field_validator, model_validator, root_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from Deendayal_botz.script import script
from Deendayal_botz.token_parser import TokenParser

# ============================
# Constants and Patterns
# ============================

ID_PATTERN = re.compile(r'^-?\d+$')

# ============================
# Enums
# ============================

class LogLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class Environment(str, Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"

# ============================
# Configuration Classes
# ============================

class BotConfiguration(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    session: str = Field(default="KR_PICTURE")
    api_id: int = Field(..., description="Telegram API ID")
    api_hash: str = Field(..., description="Telegram API Hash")
    bot_token: str = Field(..., description="Bot token from BotFather")
    cache_time: int = Field(default=300, ge=0)
    use_caption_filter: bool = Field(default=True)

    @field_validator('api_id')
    def check_api_id(cls, v):
        if v <= 0:
            raise ValueError("API ID must be positive")
        return v

    @field_validator('bot_token')
    def check_bot_token(cls, v):
        if not v or len(v) < 10:
            raise ValueError("Bot token is required and must be valid")
        return v


class MediaConfiguration(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="MEDIA_", case_sensitive=False)

    pics: List[str] = Field(default=["https://envs.sh/t3L.jpg"])
    normal_image: str = Field(default="https://graph.org/file/e20b5fdaf217252964202.jpg", alias="NOR_IMG")
    welcome_video: str = Field(default="https://graph.org/file/60e8a622b14796e4448ce.mp4", alias="MELCOW_VID")
    spell_image: str = Field(default="https://envs.sh/t3L.jpg", alias="SPELL_IMG")
    subscription_image: str = Field(default="https://graph.org/file/242b7f1b52743938d81f1.jpg", alias="SUBSCRIPTION")
    fsub_pics: List[str] = Field(default=["https://graph.org/file/7478ff3eac37f4329c3d8.jpg"])

    @field_validator('pics', 'fsub_pics', mode='before')
    def split_urls(cls, v):
        if isinstance(v, str):
            return v.split()
        return v

    @field_validator('normal_image', 'welcome_video', 'spell_image', 'subscription_image')
    def validate_urls(cls, v):
        parsed = urlparse(v)
        if not all([parsed.scheme, parsed.netloc]):
            raise ValueError(f"Invalid URL: {v}")
        return v


class ChannelConfiguration(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="CHANNEL_", case_sensitive=False)

    admins: List[Union[int, str]] = Field(default=[2068233407, 2098589219])
    channels: List[Union[int, str]] = Field(default=[-1001683081282])
    log_channel: int = Field(default=-1001693006436)
    bin_channel: int = Field(default=-1001693006436)
    movie_update_channel: int = Field(default=-1001683081282, alias="DEENDAYAL_MOVIE_UPDATE_CHANNEL")
    premium_logs: int = Field(default=-1001693006436)
    auth_channel: Optional[int] = None
    delete_channels: List[Union[int, str]] = Field(default=[-1001396923650])
    support_chat_id: int = Field(default=-1002241869735)
    request_channel: int = Field(default=-1002617590596, alias="REQST_CHANNEL")
    multi_fsub: List[int] = Field(default=[])

    @field_validator('admins', 'channels', 'delete_channels', mode='before')
    def parse_ids(cls, v):
        if isinstance(v, str):
            return [int(x) if ID_PATTERN.match(x) else x for x in v.split()]
        return v

    @field_validator('multi_fsub', mode='before')
    def parse_multi_fsub(cls, v):
        if isinstance(v, str):
            return [int(x) for x in v.split() if ID_PATTERN.match(x)]
        return v


class DatabaseConfiguration(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="DB_", case_sensitive=False)

    primary_uri: str = Field(..., alias="DATABASE_URI")
    secondary_uri: Optional[str] = Field(default=None, alias="DATABASE_URI2")
    database_name: str = Field(default="Filter2")
    collection_name: str = Field(default="KR_PICTURE")

    @field_validator('primary_uri')
    def validate_primary_uri(cls, v):
        if not v:
            raise ValueError("Primary database URI is required")
        return v


class FeatureConfiguration(BaseSettings):
    model_config = SettingsConfigDict(case_sensitive=False)

    movie_update_notification: bool = Field(default=True, alias="DEENDAYAL_MOVIE_UPDATE_NOTIFICATION")
    image_fetch: bool = Field(default=True, alias="DEENDAYAL_IMAGE_FETCH")
    verify_users: bool = Field(default=False, alias="VERIFY")
    verify_expire_days: int = Field(default=1, ge=1, alias="DEENDAYAL_VERIFY_EXPIRE")
    verified_log_channel: int = Field(default=-1001693006436, alias="DEENDAYAL_VERIFIED_LOG")
    enable_shortlink: bool = Field(default=False, alias="IS_SHORTLINK")
    shortlink_url: str = Field(default="vplink.in")
    shortlink_api: str = Field(default="")
    enable_tutorial: bool = Field(default=False, alias="IS_TUTORIAL")
    no_results_msg: bool = Field(default=True)
    max_buttons: int = Field(default=5, ge=1, le=10, alias="MAX_B_TN")
    max_btn_enabled: bool = Field(default=True, alias="MAX_BTN")
    imdb_enabled: bool = Field(default=False, alias="IMDB")
    auto_filter: bool = Field(default=True, alias="AUTO_FFILTER")
    auto_delete: bool = Field(default=True, alias="AUTO_DELETE")
    delete_time: int = Field(default=900, ge=60)
    single_button: bool = Field(default=True)
    long_imdb_description: bool = Field(default=False)
    spell_check_reply: bool = Field(default=True)
    protect_content: bool = Field(default=True)
    public_file_store: bool = Field(default=True)
    pm_search: bool = Field(default=False)
    emoji_mode: bool = Field(default=False)
    stream_mode: bool = Field(default=False)


class ServerConfiguration(BaseSettings):
    model_config = SettingsConfigDict(case_sensitive=False)

    port: int = Field(default=8080, ge=1, le=65535)
    bind_address: str = Field(default="0.0.0.0", alias="WEB_SERVER_BIND_ADDRESS")
    workers: int = Field(default=4, ge=1, le=32)
    sleep_threshold: int = Field(default=60, ge=10)
    ping_interval: int = Field(default=1200, ge=300)
    app_name: Optional[str] = None
    has_ssl: bool = Field(default=True)
    no_port: bool = Field(default=False)

    @property
    def on_heroku(self) -> bool:
        return bool(self.app_name)

    @property
    def fqdn(self) -> str:
        return f"{self.app_name}.herokuapp.com" if self.on_heroku else self.bind_address

    @property
    def base_url(self) -> str:
        protocol = "https" if self.has_ssl else "http"
        port_suffix = "" if self.no_port else f":{self.port}"
        return f"{protocol}://{self.fqdn}{port_suffix}/"


class PaymentConfiguration(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="PAYMENT_", case_sensitive=False)

    qr_code: str = Field(default="https://envs.sh/t3L.jpg", alias="QR_CODE")
    owner_upi_id: str = Field(default="xyz@123")


class LinksConfiguration(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="LINK_", case_sensitive=False)

    group: str = Field(default="https://t.me/+x6OfRDdUPrUwZTZl", alias="GRP_LNK")
    channel: str = Field(default="https://t.me/+fDkIGNmk5BU5ODVl", alias="CHNL_LNK")
    owner: str = Field(default="https://t.me/NIKHIL5757H", alias="OWNER_LNK")
    movie_update: str = Field(default="https://t.me/KR_PICTURE", alias="DEENDAYAL_MOVIE_UPDATE_CHANNEL_LNK")
    tutorial: str = Field(default="https://t.me/how_to_opan_linkz/6", alias="TUTORIAL")
    how_to_verify: str = Field(default="https://t.me/how_to_opan_linkz/6")


# ============================
# Main Combined Config
# ============================

class DeendayalBotConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        validate_default=True
    )

    bot: BotConfiguration = Field(default_factory=BotConfiguration)
    media: MediaConfiguration = Field(default_factory=MediaConfiguration)
    channels: ChannelConfiguration = Field(default_factory=ChannelConfiguration)
    database: DatabaseConfiguration = Field(default_factory=DatabaseConfiguration)
    features: FeatureConfiguration = Field(default_factory=FeatureConfiguration)
    server: ServerConfiguration = Field(default_factory=ServerConfiguration)
    payment: PaymentConfiguration = Field(default_factory=PaymentConfiguration)
    links: LinksConfiguration = Field(default_factory=LinksConfiguration)

    owner_id: int = Field(default=2068233407, alias="OWNERID")
    msg_alert: str = Field(default="Share & Support Us ♥️")
    session_name: str = Field(default="DeendayalBot")
    custom_file_caption: str = Field(default="")
    batch_file_caption: str = Field(default="")
    imdb_template: str = Field(default="")
    auth_users: List[Union[int, str]] = Field(default=[])
    premium_users: List[Union[int, str]] = Field(default=[])
    file_store_channels: List[int] = Field(default=[])
    caption_languages: List[str] = Field(default=[
        "Bhojpuri","Hindi","Bengali","Tamil","English","Bangla","Telugu",
        "Malayalam","Kannada","Marathi","Punjabi","Bengoli","Gujarati",
        "Korean","Spanish","French","German","Chinese","Arabic",
        "Portuguese","Russian","Japanese","Odia","Assamese","Urdu"
    ])
    reactions: List[str] = Field(default=[
        "🤝","😇","🤗","😍","👍","🎅","😐","🥰","🤩","😱","🤣","😘",
        "👏","😛","😈","🎉","⚡️","🫡","🤓","😎","🏆","🔥","🤭","🌚",
        "🆒","👻","😁"
    ])

    @root_validator
    def set_defaults(cls, values):
        # Fallback captions/templates
        values['custom_file_caption'] = values.get('custom_file_caption') or getattr(script, 'CAPTION', '')
        values['batch_file_caption'] = values.get('batch_file_caption') or values['custom_file_caption']
        values['imdb_template'] = values.get('imdb_template') or getattr(script, 'IMDB_TEMPLATE_TXT', '')
        return values

    @field_validator('auth_users', 'premium_users', 'file_store_channels', mode='before')
    def parse_lists(cls, v):
        if isinstance(v, str):
            return [int(x) if ID_PATTERN.match(x) else x for x in v.split()]
        return v

    @property
    def multi_client(self) -> dict:
        parser = TokenParser(self.bot.bot_token)
        return {1: self.bot.bot_token}

    @property
    def log_summary(self) -> str:
        return "\n".join([
            f"IMDB Results: {'enabled' if self.features.imdb_enabled else 'disabled'}",
            f"PM Redirect: {'enabled' if not self.features.pm_search else 'disabled'}",
            f"Single Button Mode: {'enabled' if self.features.single_button else 'disabled'}",
            f"Custom Caption: {self.custom_file_caption[:50] if self.custom_file_caption else 'Default'}",
            f"Long IMDB Description: {'enabled' if self.features.long_imdb_description else 'disabled'}",
            f"Spell Check: {'enabled' if self.features.spell_check_reply else 'disabled'}",
            f"Auto Delete: {'enabled' if self.features.auto_delete else 'disabled'} ({self.features.delete_time}s)",
        ])


# ============================
# Global Config Instance
# ============================

try:
    config = DeendayalBotConfig()
except Exception as e:
    print(f"Configuration error: {e}")
    raise
