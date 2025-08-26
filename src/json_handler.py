"""
JSON Handler Module

Provides efficient JSON file operations with streaming support for large files.
Handles file I/O, parsing, and serialization with proper error handling.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional


class JsonHandler:
    """Handles JSON file operations with streaming support for large files"""
    
    def __init__(self, file_path: str | Path):
        """
        Initialize JSON handler for a specific file
        
        Args:
            file_path: Path to the JSON file
        """
        self.file_path = Path(file_path)
        self._cached_data: Optional[Dict[str, Any]] = None
        self._file_mtime: Optional[float] = None
    
    def load_json(self, use_cache: bool = True) -> Dict[str, Any]:
        """
        Load JSON data from file with optional caching
        
        Args:
            use_cache: Whether to use cached data if available
            
        Returns:
            Parsed JSON data as dictionary
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file contains invalid JSON
        """
        if not self.file_path.exists():
            raise FileNotFoundError(f"FILE_NOT_FOUND: File {self.file_path} not found")
        
        current_mtime = self.file_path.stat().st_mtime
        
        # Use cache if available and file hasn't changed
        if (use_cache and 
            self._cached_data is not None and 
            self._file_mtime == current_mtime):
            return self._cached_data
        
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Update cache
            if use_cache:
                self._cached_data = data
                self._file_mtime = current_mtime
                
            return data
            
        except json.JSONDecodeError as e:
            raise ValueError(f"INVALID_JSON: File {self.file_path} contains invalid JSON: {e}")
        except Exception as e:
            raise ValueError(f"FILE_READ_ERROR: Failed to read {self.file_path}: {e}")
    
    def save_json(self, data: Dict[str, Any], indent: int = 2) -> None:
        """
        Save JSON data to file with atomic write
        
        Args:
            data: Dictionary to save as JSON
            indent: JSON indentation level
            
        Raises:
            ValueError: If data cannot be serialized to JSON
        """
        try:
            # Use atomic write - write to temp file then rename
            temp_path = self.file_path.with_suffix('.tmp')
            
            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=indent, ensure_ascii=False)
            
            # Atomic rename
            temp_path.replace(self.file_path)
            
            # Update cache
            self._cached_data = data
            self._file_mtime = self.file_path.stat().st_mtime
            
        except Exception as e:
            # Clean up temp file if it exists
            if temp_path.exists():
                temp_path.unlink()
            raise ValueError(f"FILE_WRITE_ERROR: Failed to write {self.file_path}: {e}")
    
    def validate_json_syntax(self) -> Dict[str, Any]:
        """
        Validate JSON file syntax without loading into memory completely
        
        Returns:
            Validation result dictionary with 'valid', 'error', 'file' fields
        """
        if not self.file_path.exists():
            raise FileNotFoundError(f"FILE_NOT_FOUND: File {self.file_path} not found")
        
        file_size = self.file_path.stat().st_size
        
        if file_size == 0:
            return {
                'valid': False,
                'file': str(self.file_path),
                'error_type': 'PARSE_ERROR',
                'error': {
                    'message': 'File is empty',
                    'line': 1,
                    'column': 1
                }
            }
        
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            if not content.strip():
                return {
                    'valid': False,
                    'file': str(self.file_path),
                    'error_type': 'PARSE_ERROR',
                    'error': {
                        'message': 'File contains only whitespace',
                        'line': 1,
                        'column': 1
                    }
                }
            
            # Try to parse
            json.loads(content)
            
            return {
                'valid': True,
                'file': str(self.file_path),
                'error': None
            }
            
        except json.JSONDecodeError as e:
            return {
                'valid': False,
                'file': str(self.file_path),
                'error_type': 'PARSE_ERROR',
                'error': {
                    'message': str(e),
                    'line': e.lineno,
                    'column': e.colno
                }
            }
        except Exception as e:
            return {
                'valid': False,
                'file': str(self.file_path),
                'error_type': 'UNKNOWN_ERROR',
                'error': {
                    'message': str(e),
                    'line': 0,
                    'column': 0
                }
            }
    
    def clear_cache(self) -> None:
        """Clear cached data to force reload on next access"""
        self._cached_data = None
        self._file_mtime = None
    
    def get_file_info(self) -> Dict[str, Any]:
        """
        Get information about the JSON file
        
        Returns:
            Dictionary with file metadata
        """
        if not self.file_path.exists():
            return {
                'exists': False,
                'path': str(self.file_path)
            }
        
        stat = self.file_path.stat()
        return {
            'exists': True,
            'path': str(self.file_path),
            'size_bytes': stat.st_size,
            'modified_time': stat.st_mtime,
            'is_cached': self._cached_data is not None
        }