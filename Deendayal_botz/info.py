#!/usr/bin/env python3
"""
Modern configuration management for Deendayal Bot using Pydantic v2.
"""

import re
from enum import Enum
from pathlib import Path
from typing import List, Optional, Union
from urllib.parse import urlparse

from pydantic import BaseSettings, Field, field_validator, model_validator
from pydantic_settings import SettingsConfigDict

from Deendayal_botz.script import script
from Deendayal_botz.token_parser import TokenParser

# ============================
# Constants and Enums
# ============================

ID_PATTERN = re.compile(r'^-?\d+$')

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
# Configuration Sections
# ============================

class BotConfiguration(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
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

    @field_validator('pics', 'fsub_pics', pre=True)
    def parse_url_list(cls, v):
        if isinstance(v, str):
            return v.split()
        return v

    @field_validator('normal_image', 'welcome_video', 'spell_image', 'subscription_image')
    def validate_url(cls, v):
        parsed = urlparse(v)
        if not parsed.scheme or not parsed.netloc:
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

    @field_validator('admins', 'channels', 'delete_channels', pre=True)
    def parse_id_list(cls, v):
        if isinstance(v, str):
            return [int(x) if ID_PATTERN.match(x) else x for x in v.split()]
        return v

    @field_validator('multi_fsub', pre=True)
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

# ============================
# Main Bot Config
# ============================

class DeendayalBotConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore")

    bot: BotConfiguration = Field(default_factory=BotConfiguration)
    media: MediaConfiguration = Field(default_factory=MediaConfiguration)
    channels: ChannelConfiguration = Field(default_factory=ChannelConfiguration)
    database: DatabaseConfiguration = Field(default_factory=DatabaseConfiguration)
    features: FeatureConfiguration = Field(default_factory=FeatureConfiguration)

    owner_id: int = Field(default=2068233407, alias="OWNERID")
    session_name: str = Field(default="DeendayalBot")
    custom_file_caption: str = ""
    batch_file_caption: str = ""
    imdb_template: str = ""

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

    @field_validator('auth_users', 'premium_users', pre=True)
    def parse_user_lists(cls, v):
        if isinstance(v, str):
            return [int(x) if ID_PATTERN.match(x) else x for x in v.split()]
        return v

    @field_validator('file_store_channels', pre=True)
    def parse_file_store_channels(cls, v):
        if isinstance(v, str):
            return [int(x) for x in v.split() if ID_PATTERN.match(x)]
        return v

    @model_validator(mode='before')
    def set_default_captions(cls, values):
        if not values.get('custom_file_caption'):
            values['custom_file_caption'] = getattr(script, 'CAPTION', '')
        if not values.get('batch_file_caption'):
            values['batch_file_caption'] = values.get('custom_file_caption', '')
        if not values.get('imdb_template'):
            values['imdb_template'] = getattr(script, 'IMDB_TEMPLATE_TXT', '')
        return values

    @property
    def multi_client(self) -> dict:
        parser = TokenParser(self.bot.bot_token)
        return {1: self.bot.bot_token}

# ============================
# Configuration Instance
# ============================

try:
    config = DeendayalBotConfig()
except Exception as e:
    print(f"Configuration error: {e}")
    raise
