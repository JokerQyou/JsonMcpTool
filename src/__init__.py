"""
JsonMcpTool - MCP Tool for JSON Processing

Main package for efficient JSON file operations, specifically designed for I18Next translation files.
"""

from .operations import (
    get_key,
    add_key,
    update_key,
    rename_key,
    remove_key,
    list_keys,
    key_exists,
    validate_json
)

from .json_handler import JsonHandler
from .path_resolver import PathResolver

__version__ = "0.1.0"
__all__ = [
    "get_key",
    "add_key", 
    "update_key",
    "rename_key",
    "remove_key",
    "list_keys",
    "key_exists",
    "validate_json",
    "JsonHandler",
    "PathResolver"
]