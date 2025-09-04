"""
token_parser.py — Utility to parse multiple bot tokens from environment variables.

Looks for env vars named MULTI_TOKEN1, MULTI_TOKEN2, ... and stores them in a dict.
"""

import os
from typing import Dict, Optional


class TokenParser:
    def __init__(self, config_file: Optional[str] = None) -> None:
        """
        Initialize TokenParser.

        Args:
            config_file (Optional[str]): Path to an optional config file for tokens (not used yet).
        """
        self.tokens: Dict[int, str] = {}
        self.config_file = config_file

    def parse_from_env(self) -> Dict[int, str]:
        """
        Parse bot tokens from environment variables named MULTI_TOKEN*.

        Returns:
            Dict[int, str]: Mapping of index → token string.
                Example: {1: "123:ABC", 2: "456:XYZ"}
        """
        # Grab only keys starting with MULTI_TOKEN and sort for consistency
        env_tokens = {
            key: val for key, val in os.environ.items() if key.startswith("MULTI_TOKEN")
        }

        # Sort by key name (MULTI_TOKEN1, MULTI_TOKEN2, ...)
        sorted_tokens = sorted(env_tokens.items(), key=lambda item: item[0])

        self.tokens = {idx + 1: token for idx, (_, token) in enumerate(sorted_tokens)}

        return self.tokens

    def get_token(self, index: int) -> Optional[str]:
        """
        Get a specific token by index.

        Args:
            index (int): Index number (1-based).

        Returns:
            Optional[str]: Token string if found, else None.
        """
        return self.tokens.get(index)