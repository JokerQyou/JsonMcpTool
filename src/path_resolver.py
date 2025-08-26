"""
Path Resolver Module

Handles dot-notation key path resolution for nested JSON structures.
Supports complex path navigation and validation.
"""

from typing import Any, Dict, List, Optional, Union


class PathResolver:
    """Handles path resolution for nested JSON structures"""
    
    @staticmethod
    def validate_path(key_path: Optional[str]) -> str:
        """
        Validate a key path
        
        Args:
            key_path: The key path to validate
            
        Returns:
            Validated key path (unchanged)
            
        Raises:
            ValueError: If path is invalid
        """
        if key_path is None:
            raise ValueError("INVALID_PATH: Key path cannot be None")
        
        if not isinstance(key_path, str):
            raise ValueError("INVALID_PATH: Key path must be a string")
        
        if key_path == '':
            raise ValueError("INVALID_PATH: Key path cannot be empty")
        
        return key_path
    
    @staticmethod
    def split_path(key_path: str) -> List[str]:
        """
        Split a dot-notation path into individual keys
        
        Args:
            key_path: Dot-notation path (e.g., 'section.subsection.key')
            
        Returns:
            List of individual keys
            
        Examples:
            split_path('a.b.c') -> ['a', 'b', 'c']
            split_path('simple') -> ['simple']
        """
        if not key_path:
            return []
        
        return key_path.split('.')
    
    @staticmethod
    def navigate_to_key(data: Dict[str, Any], key_path: str) -> Any:
        """
        Navigate through nested structure to get value at key path
        
        Args:
            data: Root JSON data dictionary
            key_path: Dot-notation path to navigate
            
        Returns:
            Value at the specified path
            
        Raises:
            KeyError: If key path doesn't exist
            TypeError: If trying to navigate through non-dict value
        """
        validated_path = PathResolver.validate_path(key_path)
        
        # First, try the whole path as a single key (handles keys with dots)
        if isinstance(data, dict) and validated_path in data:
            return data[validated_path]
        
        # If that fails, try dot-separated navigation
        keys = PathResolver.split_path(validated_path)
        current = data
        
        for i, key in enumerate(keys):
            if not isinstance(current, dict):
                partial_path = '.'.join(keys[:i])
                raise TypeError(f"PATH_ERROR: Cannot navigate through non-object value at '{partial_path}'")
            
            if key not in current:
                raise KeyError(f"KEY_NOT_FOUND: Key '{key_path}' not found")
            
            current = current[key]
        
        return current
    
    @staticmethod
    def navigate_to_parent(data: Dict[str, Any], key_path: str) -> tuple[Dict[str, Any], str]:
        """
        Navigate to the parent of the target key
        
        Args:
            data: Root JSON data dictionary
            key_path: Dot-notation path to target key
            
        Returns:
            Tuple of (parent_dict, final_key)
            
        Raises:
            KeyError: If parent path doesn't exist
            TypeError: If trying to navigate through non-dict value
        """
        validated_path = PathResolver.validate_path(key_path)
        keys = PathResolver.split_path(validated_path)
        
        if len(keys) == 1:
            # Key is at root level
            return data, keys[0]
        
        # Navigate to parent
        parent_path = '.'.join(keys[:-1])
        parent = PathResolver.navigate_to_key(data, parent_path)
        
        if not isinstance(parent, dict):
            raise TypeError(f"PATH_ERROR: Parent at '{parent_path}' is not an object")
        
        return parent, keys[-1]
    
    @staticmethod
    def key_exists(data: Dict[str, Any], key_path: str) -> bool:
        """
        Check if a key path exists in the data structure
        
        Args:
            data: Root JSON data dictionary
            key_path: Dot-notation path to check
            
        Returns:
            True if key exists, False otherwise
        """
        try:
            validated_path = PathResolver.validate_path(key_path)
            
            # First, try the whole path as a single key (handles keys with dots)
            if isinstance(data, dict) and validated_path in data:
                return True
            
            # If that fails, try dot-separated navigation
            PathResolver.navigate_to_key(data, key_path)
            return True
        except (KeyError, TypeError, ValueError):
            return False
    
    @staticmethod
    def create_nested_path(data: Dict[str, Any], key_path: str) -> Dict[str, Any]:
        """
        Create nested path structure, creating intermediate objects as needed
        
        Args:
            data: Root JSON data dictionary (modified in place)
            key_path: Dot-notation path to create
            
        Returns:
            The parent dictionary where the final key should be set
            
        Raises:
            ValueError: If path conflicts with existing non-object value
        """
        validated_path = PathResolver.validate_path(key_path)
        keys = PathResolver.split_path(validated_path)
        
        if len(keys) == 1:
            # Root level key
            return data
        
        current = data
        
        # Create intermediate objects
        for i, key in enumerate(keys[:-1]):
            if key not in current:
                current[key] = {}
            elif not isinstance(current[key], dict):
                partial_path = '.'.join(keys[:i+1])
                raise ValueError(f"PATH_CONFLICT: Cannot create nested path through non-object value at '{partial_path}'")
            
            current = current[key]
        
        return current
    
    @staticmethod
    def get_all_keys_at_path(data: Dict[str, Any], key_path: Optional[str] = None) -> List[str]:
        """
        Get all immediate child keys at the specified path
        
        Args:
            data: Root JSON data dictionary
            key_path: Path to get keys from (None for root level)
            
        Returns:
            List of immediate child key names
            
        Raises:
            KeyError: If path doesn't exist
            TypeError: If path points to non-object value
        """
        if key_path is None:
            target = data
        else:
            target = PathResolver.navigate_to_key(data, key_path)
        
        if not isinstance(target, dict):
            path_desc = "root" if key_path is None else f"'{key_path}'"
            raise TypeError(f"NOT_OBJECT: Value at {path_desc} is not an object, cannot list keys")
        
        return list(target.keys())
    
    @staticmethod
    def remove_key_at_path(data: Dict[str, Any], key_path: str) -> Any:
        """
        Remove a key at the specified path and return its value
        
        Args:
            data: Root JSON data dictionary (modified in place)
            key_path: Path to key to remove
            
        Returns:
            The removed value
            
        Raises:
            KeyError: If key doesn't exist
        """
        validated_path = PathResolver.validate_path(key_path)
        
        # First, try the whole path as a single key (handles keys with dots)
        if isinstance(data, dict) and validated_path in data:
            return data.pop(validated_path)
        
        # If that fails, try dot-separated navigation
        parent, final_key = PathResolver.navigate_to_parent(data, key_path)
        
        if final_key not in parent:
            raise KeyError(f"KEY_NOT_FOUND: Key '{key_path}' not found")
        
        return parent.pop(final_key)
    
    @staticmethod
    def set_value_at_path(data: Dict[str, Any], key_path: str, value: Any, create_path: bool = False) -> None:
        """
        Set a value at the specified path
        
        Args:
            data: Root JSON data dictionary (modified in place)
            key_path: Path where to set the value
            value: Value to set
            create_path: Whether to create intermediate objects if they don't exist
            
        Raises:
            KeyError: If path doesn't exist and create_path is False
            ValueError: If path conflicts with existing structure
        """
        if create_path:
            parent = PathResolver.create_nested_path(data, key_path)
            final_key = PathResolver.split_path(key_path)[-1]
        else:
            parent, final_key = PathResolver.navigate_to_parent(data, key_path)
        
        parent[final_key] = value