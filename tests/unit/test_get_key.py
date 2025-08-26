import unittest
import json
import tempfile
import os
import sys
from pathlib import Path

# Add src directory to path to import our implementation
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
from json_handler import JsonHandler
from path_resolver import PathResolver
from operations import get_key

class TestGetKey(unittest.TestCase):
    """Test cases for the get_key operation"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_dir = Path(__file__).parent.parent / "fixtures"
        self.sample_file = self.test_dir / "sample_i18n.json"
        self.simple_file = self.test_dir / "simple_test.json"
        self.empty_file = self.test_dir / "empty.json"
        self.invalid_file = self.test_dir / "invalid.json"
        
        # Load sample data for comparison
        with open(self.sample_file, 'r') as f:
            self.sample_data = json.load(f)
    
    def test_get_simple_key(self):
        """Test getting a simple top-level key"""
        # Expected: get_key('dashboard.title') → "Dashboard"
        result = get_key(self.sample_file, 'dashboard.title')
        self.assertEqual(result, "Dashboard")
    
    def test_get_nested_object(self):
        """Test getting a nested object"""
        # Expected: get_key('forms.validation') → {"required": "This field is required", ...}
        result = get_key(self.sample_file, 'forms.validation')
        expected = {
            "required": "This field is required",
            "email": "Please enter a valid email",
            "minLength": "Minimum {{count}} characters required"
        }
        self.assertEqual(result, expected)
    
    def test_get_deeply_nested_key(self):
        """Test getting a deeply nested key"""
        # Expected: get_key('auth.login.title') → "Sign In"
        result = get_key(self.sample_file, 'auth.login.title')
        self.assertEqual(result, "Sign In")
    
    def test_get_root_level_key(self):
        """Test getting a root-level key"""
        result = get_key(self.simple_file, 'simple')
        self.assertEqual(result, "value")
    
    def test_get_key_with_dots_in_name(self):
        """Test getting a key that contains dots in its name"""
        result = get_key(self.simple_file, 'key.with.dots')
        self.assertEqual(result, "dotted key value")
    
    def test_get_array_value(self):
        """Test getting an array value"""
        result = get_key(self.simple_file, 'array')
        expected = ["item1", "item2", {"arrayObject": "value"}]
        self.assertEqual(result, expected)
    
    def test_get_different_data_types(self):
        """Test getting different JSON data types"""
        # Null value
        result = get_key(self.simple_file, 'nullValue')
        self.assertIsNone(result)
        
        # Boolean values
        result = get_key(self.simple_file, 'booleanTrue')
        self.assertTrue(result)
        
        result = get_key(self.simple_file, 'booleanFalse')
        self.assertFalse(result)
        
        # Numeric values
        result = get_key(self.simple_file, 'number')
        self.assertEqual(result, 42)
        
        result = get_key(self.simple_file, 'float')
        self.assertEqual(result, 3.14)
    
    def test_get_empty_object(self):
        """Test getting an empty object"""
        result = get_key(self.simple_file, 'emptyObject')
        self.assertEqual(result, {})
    
    def test_get_empty_array(self):
        """Test getting an empty array"""
        result = get_key(self.simple_file, 'emptyArray')
        self.assertEqual(result, [])
    
    def test_get_nonexistent_key(self):
        """Test getting a key that doesn't exist"""
        with self.assertRaises(KeyError) as context:
            get_key(self.sample_file, 'nonexistent.key')
        
        self.assertIn("KEY_NOT_FOUND", str(context.exception))
        self.assertIn("nonexistent.key", str(context.exception))
    
    def test_get_key_from_nonexistent_file(self):
        """Test getting a key from a file that doesn't exist"""
        nonexistent_file = self.test_dir / "nonexistent.json"
        
        with self.assertRaises(FileNotFoundError) as context:
            get_key(nonexistent_file, 'any.key')
        
        self.assertIn("FILE_NOT_FOUND", str(context.exception))
    
    def test_get_key_from_invalid_json(self):
        """Test getting a key from an invalid JSON file"""
        with self.assertRaises(ValueError) as context:
            get_key(self.invalid_file, 'any.key')
        
        self.assertIn("INVALID_JSON", str(context.exception))
    
    def test_get_key_invalid_path_format(self):
        """Test getting a key with invalid path format"""
        with self.assertRaises(ValueError) as context:
            get_key(self.sample_file, '')
        
        self.assertIn("INVALID_PATH", str(context.exception))
        
        with self.assertRaises(ValueError) as context:
            get_key(self.sample_file, None)
        
        self.assertIn("INVALID_PATH", str(context.exception))
    
    def test_get_key_from_empty_file(self):
        """Test getting a key from an empty JSON object"""
        with self.assertRaises(KeyError) as context:
            get_key(self.empty_file, 'any.key')
        
        self.assertIn("KEY_NOT_FOUND", str(context.exception))
    
    def test_get_key_partial_path_exists(self):
        """Test getting a key where part of the path exists but not the full path"""
        # 'dashboard' exists but 'dashboard.nonexistent' doesn't
        with self.assertRaises(KeyError) as context:
            get_key(self.sample_file, 'dashboard.nonexistent')
        
        self.assertIn("KEY_NOT_FOUND", str(context.exception))
    
    def test_get_key_case_sensitivity(self):
        """Test that key paths are case sensitive"""
        with self.assertRaises(KeyError):
            get_key(self.sample_file, 'Dashboard.title')  # Capital D
        
        with self.assertRaises(KeyError):
            get_key(self.sample_file, 'dashboard.Title')  # Capital T
    
    def test_get_key_whitespace_handling(self):
        """Test handling of whitespace in key paths"""
        with self.assertRaises(KeyError):
            get_key(self.sample_file, ' dashboard.title')  # Leading space
        
        with self.assertRaises(KeyError):
            get_key(self.sample_file, 'dashboard.title ')  # Trailing space
        
        with self.assertRaises(KeyError):
            get_key(self.sample_file, 'dashboard . title')  # Spaces around dots


if __name__ == '__main__':
    unittest.main()