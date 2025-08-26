import unittest
import json
import tempfile
import os
import shutil
import sys
from pathlib import Path

# Add src directory to path to import our implementation
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
from json_handler import JsonHandler
from path_resolver import PathResolver
from operations import list_keys

class TestListKeys(unittest.TestCase):
    """Test cases for the list_keys operation"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_dir = Path(__file__).parent.parent / "fixtures"
        self.sample_file = self.test_dir / "sample_i18n.json"
        self.simple_file = self.test_dir / "simple_test.json"
        self.empty_file = self.test_dir / "empty.json"
        self.invalid_file = self.test_dir / "invalid.json"
    
    def test_list_root_keys(self):
        """Test listing all root-level keys"""
        result = list_keys(self.sample_file)
        expected = ['dashboard', 'forms', 'alerts', 'navigation', 'auth']
        
        self.assertEqual(sorted(result), sorted(expected))
    
    def test_list_keys_from_nested_object(self):
        """Test listing keys from a nested object"""
        result = list_keys(self.sample_file, 'dashboard')
        expected = ['title', 'welcome', 'stats']
        
        self.assertEqual(sorted(result), sorted(expected))
    
    def test_list_keys_from_deeply_nested_object(self):
        """Test listing keys from a deeply nested object"""
        result = list_keys(self.sample_file, 'forms.validation')
        expected = ['required', 'email', 'minLength']
        
        self.assertEqual(sorted(result), sorted(expected))
    
    def test_list_keys_from_simple_object(self):
        """Test listing keys from a simple nested object"""
        result = list_keys(self.sample_file, 'dashboard.stats')
        expected = ['users', 'revenue']
        
        self.assertEqual(sorted(result), sorted(expected))
    
    def test_list_keys_various_data_types(self):
        """Test listing keys that contain various data types"""
        result = list_keys(self.simple_file)
        expected = ['simple', 'nested', 'array', 'key.with.dots', 'emptyObject', 
                   'emptyArray', 'nullValue', 'booleanTrue', 'booleanFalse', 
                   'number', 'float']
        
        self.assertEqual(sorted(result), sorted(expected))
    
    def test_list_keys_from_nested_structure(self):
        """Test listing keys from nested structure in simple file"""
        result = list_keys(self.simple_file, 'nested')
        expected = ['key']
        
        self.assertEqual(result, expected)
    
    def test_list_keys_from_empty_object(self):
        """Test listing keys from an empty object"""
        result = list_keys(self.empty_file)
        expected = []
        
        self.assertEqual(result, expected)
    
    def test_list_keys_from_object_with_empty_nested_objects(self):
        """Test listing keys from object containing empty nested objects"""
        result = list_keys(self.simple_file, 'emptyObject')
        expected = []
        
        self.assertEqual(result, expected)
    
    def test_list_keys_with_special_characters(self):
        """Test listing keys that contain special characters"""
        # The key.with.dots key should be listed
        result = list_keys(self.simple_file)
        
        self.assertIn('key.with.dots', result)
    
    def test_list_keys_preserves_order(self):
        """Test that list_keys preserves or returns consistent order"""
        result1 = list_keys(self.sample_file, 'dashboard')
        result2 = list_keys(self.sample_file, 'dashboard')
        
        # Results should be consistent
        self.assertEqual(result1, result2)
    
    def test_list_keys_complex_auth_structure(self):
        """Test listing keys from complex authentication structure"""
        # List auth section keys
        auth_keys = list_keys(self.sample_file, 'auth')
        expected_auth = ['login', 'register']
        self.assertEqual(sorted(auth_keys), sorted(expected_auth))
        
        # List login subsection keys
        login_keys = list_keys(self.sample_file, 'auth.login')
        expected_login = ['title', 'email', 'password', 'remember']
        self.assertEqual(sorted(login_keys), sorted(expected_login))
        
        # List register subsection keys
        register_keys = list_keys(self.sample_file, 'auth.register')
        expected_register = ['title', 'firstName', 'lastName']
        self.assertEqual(sorted(register_keys), sorted(expected_register))
    
    def test_list_keys_nonexistent_path(self):
        """Test listing keys from a path that doesn't exist"""
        with self.assertRaises(KeyError) as context:
            list_keys(self.sample_file, 'nonexistent.path')
        
        self.assertIn("KEY_NOT_FOUND", str(context.exception))
        self.assertIn("nonexistent.path", str(context.exception))
    
    def test_list_keys_partial_path_not_exists(self):
        """Test listing keys when part of the path doesn't exist"""
        with self.assertRaises(KeyError) as context:
            list_keys(self.sample_file, 'dashboard.nonexistent')
        
        self.assertIn("KEY_NOT_FOUND", str(context.exception))
    
    def test_list_keys_from_non_object_value(self):
        """Test listing keys from a value that is not an object"""
        with self.assertRaises(TypeError) as context:
            list_keys(self.sample_file, 'dashboard.title')  # title is a string
        
        self.assertIn("NOT_OBJECT", str(context.exception))
        
        with self.assertRaises(TypeError) as context:
            list_keys(self.simple_file, 'array')  # array is not an object
        
        self.assertIn("NOT_OBJECT", str(context.exception))
    
    def test_list_keys_from_nonexistent_file(self):
        """Test listing keys from a file that doesn't exist"""
        nonexistent_file = self.test_dir / "nonexistent.json"
        
        with self.assertRaises(FileNotFoundError) as context:
            list_keys(nonexistent_file)
        
        self.assertIn("FILE_NOT_FOUND", str(context.exception))
    
    def test_list_keys_invalid_path_format(self):
        """Test listing keys with invalid path format"""
        with self.assertRaises(ValueError) as context:
            list_keys(self.sample_file, '')
        
        self.assertIn("INVALID_PATH", str(context.exception))
    
    def test_list_keys_from_invalid_json_file(self):
        """Test listing keys from an invalid JSON file"""
        with self.assertRaises(ValueError) as context:
            list_keys(self.invalid_file)
        
        self.assertIn("INVALID_JSON", str(context.exception))
    
    def test_list_keys_case_sensitivity(self):
        """Test that key listing is case sensitive"""
        with self.assertRaises(KeyError):
            list_keys(self.sample_file, 'Dashboard')  # Capital D
        
        with self.assertRaises(KeyError):
            list_keys(self.sample_file, 'dashboard.Title')  # Capital T in nested path
    
    def test_list_keys_whitespace_handling(self):
        """Test handling of whitespace in key paths"""
        with self.assertRaises(KeyError):
            list_keys(self.sample_file, ' dashboard')  # Leading space
        
        with self.assertRaises(KeyError):
            list_keys(self.sample_file, 'dashboard ')  # Trailing space
    
    def test_list_keys_returns_immediate_children_only(self):
        """Test that list_keys returns only immediate children, not nested descendants"""
        result = list_keys(self.sample_file, 'auth')
        
        # Should only return immediate children
        expected = ['login', 'register']
        self.assertEqual(sorted(result), sorted(expected))
        
        # Should not include deeply nested keys like 'title', 'email', etc.
        nested_keys = ['title', 'email', 'password', 'firstName', 'lastName']
        for key in nested_keys:
            self.assertNotIn(key, result)
    
    def test_list_keys_empty_string_path(self):
        """Test listing keys with empty string path (should be treated as root)"""
        # Empty string should be invalid
        with self.assertRaises(ValueError):
            list_keys(self.sample_file, '')
    
    def test_list_keys_none_path(self):
        """Test listing keys with None path (should default to root)"""
        result = list_keys(self.sample_file, None)
        expected = ['dashboard', 'forms', 'alerts', 'navigation', 'auth']
        
        self.assertEqual(sorted(result), sorted(expected))
    
    def test_list_keys_single_key_object(self):
        """Test listing keys from an object with only one key"""
        result = list_keys(self.simple_file, 'nested')
        expected = ['key']
        
        self.assertEqual(result, expected)
    
    def test_list_keys_with_numeric_and_boolean_values(self):
        """Test that objects containing various value types are handled correctly"""
        # All these keys contain non-object values, so listing their keys should fail
        non_object_keys = ['simple', 'nullValue', 'booleanTrue', 'booleanFalse', 'number', 'float']
        
        for key in non_object_keys:
            with self.assertRaises(TypeError):
                list_keys(self.simple_file, key)
    
    def test_list_keys_deeply_nested_path(self):
        """Test listing keys from a deeply nested path"""
        # Create a temporary file with deeply nested structure for testing
        temp_file = Path(tempfile.mktemp(suffix='.json'))
        deep_structure = {
            'level1': {
                'level2': {
                    'level3': {
                        'level4': {
                            'key1': 'value1',
                            'key2': 'value2',
                            'key3': 'value3'
                        }
                    }
                }
            }
        }
        
        try:
            with open(temp_file, 'w') as f:
                json.dump(deep_structure, f)
            
            result = list_keys(temp_file, 'level1.level2.level3.level4')
            expected = ['key1', 'key2', 'key3']
            
            self.assertEqual(sorted(result), sorted(expected))
        finally:
            if temp_file.exists():
                temp_file.unlink()


if __name__ == '__main__':
    unittest.main()