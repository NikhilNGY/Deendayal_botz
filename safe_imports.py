"""
Safe Import Wrapper

This module ensures missing local imports (like `database`) won't crash the bot.
Instead, it falls back to mock objects with warnings.
"""

import logging
from types import SimpleNamespace

logger = logging.getLogger(__name__)

def safe_import(module_name: str, fallback: dict = None):
    """
    Try importing a module. If not found, return a mock object instead.
    """
    try:
        module = __import__(module_name, fromlist=["*"])
        logger.info(f"✅ Successfully imported {module_name}")
        return module
    except ModuleNotFoundError as e:
        logger.warning(f"⚠️ Could not import {module_name}: {e}. Using fallback.")
        return SimpleNamespace(**(fallback or {}))
