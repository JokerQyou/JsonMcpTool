"""
JSON Operations Module

Implements the core JSON operations for the MCP tool:
- get_key: Retrieve value by key path
- add_key: Add new key-value pair
- update_key: Update existing key
- rename_key: Rename existing key
- remove_key: Remove key and value
- list_keys: List keys at a path
- key_exists: Check if key exists
- validate_json: Validate JSON syntax
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import time

from json_handler import JsonHandler
from path_resolver import PathResolver


def get_key(file_path: Union[str, Path], key_path: str) -> Any:
    """
    Retrieve value by dot-notation key path
    
    Args:
        file_path: Path to JSON file
        key_path: Dot-notation path to key (e.g., 'section.subsection.key')
        
    Returns:
        Value at the specified key path (string, object, array, etc.)
        
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file contains invalid JSON or key path is invalid
        KeyError: If key path doesn't exist
        
    Examples:
        get_key('translations.json', 'dashboard.title') → "Dashboard"
        get_key('translations.json', 'forms.validation') → {"required": "...", "email": "..."}
    """
    handler = JsonHandler(file_path)
    data = handler.load_json()
    
    try:
        return PathResolver.navigate_to_key(data, key_path)
    except KeyError:
        raise KeyError(f"KEY_NOT_FOUND: Key '{key_path}' not found in {file_path}")
    except TypeError as e:
        raise ValueError(str(e))


def add_key(file_path: Union[str, Path], key_path: str, value: Any) -> None:
    """
    Add new key-value pair
    
    Args:
        file_path: Path to JSON file
        key_path: Dot-notation path for new key
        value: Value to set (string, object, array, etc.)
        
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file contains invalid JSON, key path is invalid, or key already exists
        
    Examples:
        add_key('translations.json', 'alerts.success', 'Operation completed')
        add_key('translations.json', 'modals.confirm', {'title': 'Confirm', 'cancel': 'Cancel'})
    """
    handler = JsonHandler(file_path)
    data = handler.load_json()
    
    # Check if key already exists
    if PathResolver.key_exists(data, key_path):
        raise ValueError(f"KEY_EXISTS: Key '{key_path}' already exists in {file_path}")
    
    try:
        # Create the nested path and set the value
        PathResolver.set_value_at_path(data, key_path, value, create_path=True)
        
        # Save the updated data
        handler.save_json(data)
        
    except ValueError as e:
        if "PATH_CONFLICT" in str(e):
            raise ValueError(str(e))
        raise ValueError(f"ADD_KEY_ERROR: Failed to add key '{key_path}': {e}")


def update_key(file_path: Union[str, Path], key_path: str, value: Any) -> None:
    """
    Update existing key with new value
    
    Args:
        file_path: Path to JSON file
        key_path: Dot-notation path to existing key
        value: New value to set
        
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file contains invalid JSON or key path is invalid
        KeyError: If key doesn't exist
        
    Examples:
        update_key('translations.json', 'dashboard.title', 'Updated Dashboard')
        update_key('translations.json', 'forms.validation', {'required': 'New message'})
    """
    handler = JsonHandler(file_path)
    data = handler.load_json()
    
    # Validate path first
    try:
        PathResolver.validate_path(key_path)
    except ValueError as e:
        raise ValueError(str(e))
    
    # Check if key exists
    if not PathResolver.key_exists(data, key_path):
        raise KeyError(f"KEY_NOT_FOUND: Key '{key_path}' not found in {file_path}")
    
    try:
        # Update the value
        PathResolver.set_value_at_path(data, key_path, value, create_path=False)
        
        # Save the updated data
        handler.save_json(data)
        
    except (KeyError, TypeError) as e:
        raise KeyError(f"KEY_NOT_FOUND: Key '{key_path}' not found in {file_path}")
    except Exception as e:
        raise ValueError(f"UPDATE_KEY_ERROR: Failed to update key '{key_path}': {e}")


def rename_key(file_path: Union[str, Path], old_path: str, new_path: str) -> None:
    """
    Rename existing key (move value from old path to new path)
    
    Args:
        file_path: Path to JSON file
        old_path: Current dot-notation path
        new_path: New dot-notation path
        
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file contains invalid JSON, paths are invalid, or new key already exists
        KeyError: If old key doesn't exist
        
    Examples:
        rename_key('translations.json', 'dashboard.title', 'dashboard.heading')
        rename_key('translations.json', 'forms.validation', 'common.validation')
    """
    if old_path == new_path:
        raise ValueError("SAME_KEY: Old and new key paths cannot be the same")
    
    # Validate paths first
    try:
        PathResolver.validate_path(old_path)
        PathResolver.validate_path(new_path)
    except ValueError as e:
        raise ValueError(str(e))
    
    handler = JsonHandler(file_path)
    data = handler.load_json()
    
    # Check if old key exists
    if not PathResolver.key_exists(data, old_path):
        raise KeyError(f"KEY_NOT_FOUND: Key '{old_path}' not found in {file_path}")
    
    # Check if new key already exists
    if PathResolver.key_exists(data, new_path):
        raise ValueError(f"KEY_EXISTS: Key '{new_path}' already exists in {file_path}")
    
    try:
        # Get the value from old location
        value = PathResolver.navigate_to_key(data, old_path)
        
        # Set value at new location (create path if needed)
        PathResolver.set_value_at_path(data, new_path, value, create_path=True)
        
        # Remove from old location
        PathResolver.remove_key_at_path(data, old_path)
        
        # Save the updated data
        handler.save_json(data)
        
    except Exception as e:
        raise ValueError(f"RENAME_KEY_ERROR: Failed to rename key '{old_path}' to '{new_path}': {e}")


def remove_key(file_path: Union[str, Path], key_path: str) -> Any:
    """
    Remove key and return its value
    
    Args:
        file_path: Path to JSON file
        key_path: Dot-notation path to key to remove
        
    Returns:
        The value that was removed
        
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file contains invalid JSON or key path is invalid
        KeyError: If key doesn't exist
        
    Examples:
        remove_key('translations.json', 'obsolete.section')
        old_value = remove_key('translations.json', 'dashboard.old_field')
    """
    handler = JsonHandler(file_path)
    data = handler.load_json()
    
    # Validate path first
    try:
        PathResolver.validate_path(key_path)
    except ValueError as e:
        raise ValueError(str(e))
    
    # Check if key exists
    if not PathResolver.key_exists(data, key_path):
        raise KeyError(f"KEY_NOT_FOUND: Key '{key_path}' not found in {file_path}")
    
    try:
        # Remove the key and get its value
        removed_value = PathResolver.remove_key_at_path(data, key_path)
        
        # Save the updated data
        handler.save_json(data)
        
        return removed_value
        
    except Exception as e:
        raise ValueError(f"REMOVE_KEY_ERROR: Failed to remove key '{key_path}': {e}")


def list_keys(file_path: Union[str, Path], key_path: Optional[str] = None) -> List[str]:
    """
    List all immediate child keys at the specified path
    
    Args:
        file_path: Path to JSON file
        key_path: Dot-notation path to list keys from (None for root level)
        
    Returns:
        List of immediate child key names
        
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file contains invalid JSON or key path is invalid
        KeyError: If key path doesn't exist
        TypeError: If path points to non-object value
        
    Examples:
        list_keys('translations.json') → ['dashboard', 'forms', 'alerts']
        list_keys('translations.json', 'dashboard') → ['title', 'welcome', 'stats']
    """
    handler = JsonHandler(file_path)
    data = handler.load_json()
    
    try:
        return PathResolver.get_all_keys_at_path(data, key_path)
    except KeyError:
        path_desc = "root" if key_path is None else f"'{key_path}'"
        raise KeyError(f"KEY_NOT_FOUND: Key {path_desc} not found in {file_path}")
    except TypeError as e:
        raise TypeError(str(e))


def key_exists(file_path: Union[str, Path], key_path: str) -> bool:
    """
    Check if a key exists at the specified path
    
    Args:
        file_path: Path to JSON file
        key_path: Dot-notation path to check
        
    Returns:
        True if key exists, False otherwise
        
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file contains invalid JSON or key path is invalid
        
    Examples:
        key_exists('translations.json', 'dashboard.title') → True
        key_exists('translations.json', 'nonexistent.key') → False
    """
    handler = JsonHandler(file_path)
    data = handler.load_json()
    
    return PathResolver.key_exists(data, key_path)


def validate_json(file_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Validate JSON file syntax and structure
    
    Args:
        file_path: Path to JSON file to validate
        
    Returns:
        Dictionary with validation results:
        {
            'valid': bool,
            'file': str,
            'error': dict or None,
            'error_type': str (if invalid),
            'performance': dict (optional)
        }
        
    Raises:
        FileNotFoundError: If file doesn't exist
        
    Examples:
        validate_json('valid.json') → {'valid': True, 'file': 'valid.json', 'error': None}
        validate_json('invalid.json') → {'valid': False, 'error_type': 'PARSE_ERROR', ...}
    """
    start_time = time.time()
    handler = JsonHandler(file_path)
    
    # Get basic file info
    file_info = handler.get_file_info()
    
    result = handler.validate_json_syntax()
    
    # Add performance metrics
    result['performance'] = {
        'parse_time': time.time() - start_time,
        'file_size': file_info.get('size_bytes', 0)
    }
    
    return result