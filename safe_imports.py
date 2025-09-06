"""
Safe Import Wrapper

Prevents crashes if local modules are missing.
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
        logger.info(f"✅ Imported {module_name}")
        return module
    except ModuleNotFoundError as e:
        logger.warning(f"⚠️ Missing {module_name}: {e}. Using fallback.")
        return SimpleNamespace(**(fallback or {}))
