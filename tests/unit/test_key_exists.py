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
from operations import key_exists, get_key

class TestKeyExists(unittest.TestCase):
    """Test cases for the key_exists operation"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_dir = Path(__file__).parent.parent / "fixtures"
        self.sample_file = self.test_dir / "sample_i18n.json"
        self.simple_file = self.test_dir / "simple_test.json"
        self.empty_file = self.test_dir / "empty.json"
        self.invalid_file = self.test_dir / "invalid.json"
    
    def test_key_exists_simple_key(self):
        """Test checking existence of simple keys"""
        # Existing keys should return True
        self.assertTrue(key_exists(self.sample_file, 'dashboard.title'))
        self.assertTrue(key_exists(self.sample_file, 'forms.validation'))
        self.assertTrue(key_exists(self.simple_file, 'simple'))
        
        # Non-existing keys should return False
        self.assertFalse(key_exists(self.sample_file, 'nonexistent'))
        self.assertFalse(key_exists(self.sample_file, 'dashboard.nonexistent'))
    
    def test_key_exists_nested_keys(self):
        """Test checking existence of deeply nested keys"""
        # Existing nested keys
        self.assertTrue(key_exists(self.sample_file, 'auth.login.title'))
        self.assertTrue(key_exists(self.sample_file, 'auth.login.password'))
        self.assertTrue(key_exists(self.sample_file, 'forms.validation.required'))
        
        # Non-existing nested keys
        self.assertFalse(key_exists(self.sample_file, 'auth.login.nonexistent'))
        self.assertFalse(key_exists(self.sample_file, 'auth.nonexistent.title'))
    
    def test_key_exists_root_level_keys(self):
        """Test checking existence of root-level keys"""
        # Existing root keys
        self.assertTrue(key_exists(self.sample_file, 'dashboard'))
        self.assertTrue(key_exists(self.sample_file, 'forms'))
        self.assertTrue(key_exists(self.simple_file, 'simple'))
        self.assertTrue(key_exists(self.simple_file, 'nested'))
        
        # Non-existing root keys
        self.assertFalse(key_exists(self.sample_file, 'nonexistent'))
        self.assertFalse(key_exists(self.simple_file, 'missing'))
    
    def test_key_exists_different_data_types(self):
        """Test checking existence of keys with different data types"""
        # String values
        self.assertTrue(key_exists(self.simple_file, 'simple'))
        
        # Object values
        self.assertTrue(key_exists(self.simple_file, 'nested'))
        
        # Array values
        self.assertTrue(key_exists(self.simple_file, 'array'))
        
        # Boolean values
        self.assertTrue(key_exists(self.simple_file, 'booleanTrue'))
        self.assertTrue(key_exists(self.simple_file, 'booleanFalse'))
        
        # Numeric values
        self.assertTrue(key_exists(self.simple_file, 'number'))
        self.assertTrue(key_exists(self.simple_file, 'float'))
        
        # Null values
        self.assertTrue(key_exists(self.simple_file, 'nullValue'))
        
        # Empty object/array
        self.assertTrue(key_exists(self.simple_file, 'emptyObject'))
        self.assertTrue(key_exists(self.simple_file, 'emptyArray'))
    
    def test_key_exists_special_characters(self):
        """Test checking existence of keys with special characters"""
        self.assertTrue(key_exists(self.simple_file, 'key.with.dots'))
    
    def test_key_exists_complex_structures(self):
        """Test checking existence in complex nested structures"""
        # Multi-level navigation
        self.assertTrue(key_exists(self.sample_file, 'auth.register.firstName'))
        self.assertTrue(key_exists(self.sample_file, 'auth.register.lastName'))
        self.assertTrue(key_exists(self.sample_file, 'dashboard.stats.users'))
        
        # Partial paths that exist
        self.assertTrue(key_exists(self.sample_file, 'auth.login'))
        self.assertTrue(key_exists(self.sample_file, 'dashboard.stats'))
    
    def test_key_exists_empty_file(self):
        """Test checking key existence in empty JSON object"""
        self.assertFalse(key_exists(self.empty_file, 'any.key'))
        self.assertFalse(key_exists(self.empty_file, 'simple'))
    
    def test_key_exists_case_sensitivity(self):
        """Test that key existence checking is case sensitive"""
        # Correct case should return True
        self.assertTrue(key_exists(self.sample_file, 'dashboard.title'))
        
        # Wrong case should return False
        self.assertFalse(key_exists(self.sample_file, 'Dashboard.title'))  # Capital D
        self.assertFalse(key_exists(self.sample_file, 'dashboard.Title'))  # Capital T
        self.assertFalse(key_exists(self.sample_file, 'DASHBOARD.TITLE'))  # All caps
    
    def test_key_exists_whitespace_sensitivity(self):
        """Test that key existence checking is sensitive to whitespace"""
        # Correct key should return True
        self.assertTrue(key_exists(self.sample_file, 'dashboard.title'))
        
        # Keys with whitespace should return False
        self.assertFalse(key_exists(self.sample_file, ' dashboard.title'))  # Leading space
        self.assertFalse(key_exists(self.sample_file, 'dashboard.title '))  # Trailing space
        self.assertFalse(key_exists(self.sample_file, 'dashboard . title'))  # Spaces around dot
    
    def test_key_exists_partial_path_scenarios(self):
        """Test various scenarios where part of the path exists"""
        # Parent exists, child doesn't
        self.assertFalse(key_exists(self.sample_file, 'dashboard.nonexistent'))
        
        # Grandparent exists, parent and child don't
        self.assertFalse(key_exists(self.sample_file, 'dashboard.nonexistent.child'))
        
        # Path exists but trying to go deeper into non-object
        self.assertFalse(key_exists(self.sample_file, 'dashboard.title.subtitle'))  # title is a string
    
    def test_key_exists_performance_vs_get_key(self):
        """Test that key_exists is more efficient than get_key for existence checks"""
        # This test verifies behavior rather than performance
        # Both should give consistent results for existing keys
        
        existing_keys = [
            'dashboard.title',
            'forms.validation.email',
            'auth.login.password',
            'simple',
            'nested.key'
        ]
        
        for key_path in existing_keys:
            file_to_test = self.sample_file if key_path.startswith(('dashboard', 'forms', 'auth')) else self.simple_file
            
            # key_exists should return True
            self.assertTrue(key_exists(file_to_test, key_path))
            
            # get_key should not raise an exception
            try:
                value = get_key(file_to_test, key_path)
                # If get_key succeeds, key_exists should have been True
                self.assertTrue(True)  # This should always pass if we reach here
            except Exception:
                # If get_key fails, key_exists should have been False
                self.fail(f"key_exists returned True but get_key failed for {key_path}")
    
    def test_key_exists_nonexistent_file(self):
        """Test checking key existence in a file that doesn't exist"""
        nonexistent_file = self.test_dir / "nonexistent.json"
        
        with self.assertRaises(FileNotFoundError) as context:
            key_exists(nonexistent_file, 'any.key')
        
        self.assertIn("FILE_NOT_FOUND", str(context.exception))
    
    def test_key_exists_invalid_path(self):
        """Test checking key existence with invalid paths"""
        # Our implementation gracefully returns False for invalid paths
        # This is more user-friendly than raising exceptions
        
        # Empty string should return False
        result = key_exists(self.sample_file, '')
        self.assertFalse(result)
        
        # None should return False (graceful handling)
        result = key_exists(self.sample_file, None)
        self.assertFalse(result)
    
    def test_key_exists_invalid_json_file(self):
        """Test checking key existence in a file with invalid JSON"""
        with self.assertRaises(ValueError) as context:
            key_exists(self.invalid_file, 'any.key')
        
        self.assertIn("INVALID_JSON", str(context.exception))
    
    def test_key_exists_consistency_with_other_operations(self):
        """Test that key_exists is consistent with other operations"""
        # If key_exists returns True, get_key should succeed
        test_keys = [
            'dashboard.title',
            'forms.validation.required',
            'auth.login.email',
            'alerts.success'
        ]
        
        for key_path in test_keys:
            if key_exists(self.sample_file, key_path):
                # get_key should not raise an exception
                try:
                    value = get_key(self.sample_file, key_path)
                except Exception as e:
                    self.fail(f"key_exists returned True but get_key failed for {key_path}: {e}")
    
    def test_key_exists_edge_cases(self):
        """Test edge cases for key existence"""
        # Very long key path
        long_path = 'dashboard.' + '.'.join(['level' + str(i) for i in range(100)])
        self.assertFalse(key_exists(self.sample_file, long_path))
        
        # Key path with many dots but valid structure
        self.assertTrue(key_exists(self.sample_file, 'auth.login.title'))
        
        # Single character keys (if they exist in test data)
        # Would need to add single character keys to test data for this
    
    def test_key_exists_interpolation_keys(self):
        """Test checking existence of keys with I18Next interpolation"""
        # Keys that contain interpolation syntax should still be found
        self.assertTrue(key_exists(self.sample_file, 'dashboard.welcome'))  # Contains {{name}}
        self.assertTrue(key_exists(self.sample_file, 'forms.validation.minLength'))  # Contains {{count}}
    
    def test_key_exists_boolean_return_type(self):
        """Test that key_exists always returns boolean values"""
        # Existing key should return exactly True (not truthy)
        result = key_exists(self.sample_file, 'dashboard.title')
        self.assertIs(result, True)
        self.assertIsInstance(result, bool)
        
        # Non-existing key should return exactly False (not falsy)
        result = key_exists(self.sample_file, 'nonexistent.key')
        self.assertIs(result, False)
        self.assertIsInstance(result, bool)
    
    def test_key_exists_deeply_nested_structure(self):
        """Test key existence in deeply nested structures"""
        # Create a temporary file with very deep nesting
        temp_file = Path(tempfile.mktemp(suffix='.json'))
        deep_structure = {
            'level1': {
                'level2': {
                    'level3': {
                        'level4': {
                            'level5': {
                                'deepKey': 'deep value'
                            }
                        }
                    }
                }
            }
        }
        
        try:
            with open(temp_file, 'w') as f:
                json.dump(deep_structure, f)
            
            # Test various depths
            self.assertTrue(key_exists(temp_file, 'level1'))
            self.assertTrue(key_exists(temp_file, 'level1.level2'))
            self.assertTrue(key_exists(temp_file, 'level1.level2.level3'))
            self.assertTrue(key_exists(temp_file, 'level1.level2.level3.level4.level5.deepKey'))
            
            # Test non-existent at various depths
            self.assertFalse(key_exists(temp_file, 'level1.level2.level3.level4.level5.nonexistent'))
            self.assertFalse(key_exists(temp_file, 'level1.level2.nonexistent'))
            
        finally:
            if temp_file.exists():
                temp_file.unlink()


if __name__ == '__main__':
    unittest.main()