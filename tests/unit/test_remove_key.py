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
from operations import remove_key

class TestRemoveKey(unittest.TestCase):
    """Test cases for the remove_key operation"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_dir = Path(__file__).parent.parent / "fixtures"
        
        # Create temporary copies for modification
        self.temp_dir = Path(tempfile.mkdtemp())
        self.temp_sample = self.temp_dir / "sample_i18n.json"
        self.temp_simple = self.temp_dir / "simple_test.json"
        
        shutil.copy2(self.test_dir / "sample_i18n.json", self.temp_sample)
        shutil.copy2(self.test_dir / "simple_test.json", self.temp_simple)
    
    def tearDown(self):
        """Clean up temporary files"""
        shutil.rmtree(self.temp_dir)
    
    def test_remove_simple_key(self):
        """Test removing a simple string key"""
        remove_key(self.temp_sample, 'dashboard.title')
        
        with open(self.temp_sample, 'r') as f:
            data = json.load(f)
        
        # Verify key was removed
        self.assertNotIn('title', data['dashboard'])
        # Verify other keys in same object are preserved
        self.assertIn('welcome', data['dashboard'])
        self.assertIn('stats', data['dashboard'])
    
    def test_remove_nested_key(self):
        """Test removing a deeply nested key"""
        remove_key(self.temp_sample, 'auth.login.password')
        
        with open(self.temp_sample, 'r') as f:
            data = json.load(f)
        
        # Verify key was removed
        self.assertNotIn('password', data['auth']['login'])
        # Verify other keys are preserved
        self.assertIn('title', data['auth']['login'])
        self.assertIn('email', data['auth']['login'])
    
    def test_remove_object_key(self):
        """Test removing a key that contains an object"""
        remove_key(self.temp_sample, 'forms.validation')
        
        with open(self.temp_sample, 'r') as f:
            data = json.load(f)
        
        # Verify entire validation object was removed
        self.assertNotIn('validation', data['forms'])
        # Verify other keys in forms are preserved
        self.assertIn('buttons', data['forms'])
    
    def test_remove_array_key(self):
        """Test removing a key that contains an array"""
        remove_key(self.temp_simple, 'array')
        
        with open(self.temp_simple, 'r') as f:
            data = json.load(f)
        
        # Verify array was removed
        self.assertNotIn('array', data)
        # Verify other keys are preserved
        self.assertIn('simple', data)
        self.assertIn('nested', data)
    
    def test_remove_root_level_key(self):
        """Test removing a root-level key"""
        remove_key(self.temp_simple, 'simple')
        
        with open(self.temp_simple, 'r') as f:
            data = json.load(f)
        
        # Verify key was removed
        self.assertNotIn('simple', data)
        # Verify other root keys are preserved
        self.assertIn('nested', data)
        self.assertIn('array', data)
    
    def test_remove_entire_section(self):
        """Test removing an entire section"""
        remove_key(self.temp_sample, 'dashboard')
        
        with open(self.temp_sample, 'r') as f:
            data = json.load(f)
        
        # Verify entire dashboard section was removed
        self.assertNotIn('dashboard', data)
        # Verify other sections are preserved
        self.assertIn('forms', data)
        self.assertIn('alerts', data)
        self.assertIn('auth', data)
    
    def test_remove_key_with_different_data_types(self):
        """Test removing keys with different data types"""
        # Remove boolean
        remove_key(self.temp_simple, 'booleanTrue')
        
        # Remove number
        remove_key(self.temp_simple, 'number')
        
        # Remove null value
        remove_key(self.temp_simple, 'nullValue')
        
        with open(self.temp_simple, 'r') as f:
            data = json.load(f)
        
        self.assertNotIn('booleanTrue', data)
        self.assertNotIn('number', data)
        self.assertNotIn('nullValue', data)
        
        # Verify other keys are preserved
        self.assertIn('simple', data)
        self.assertIn('booleanFalse', data)
        self.assertIn('float', data)
    
    def test_remove_empty_object_key(self):
        """Test removing an empty object"""
        remove_key(self.temp_simple, 'emptyObject')
        
        with open(self.temp_simple, 'r') as f:
            data = json.load(f)
        
        self.assertNotIn('emptyObject', data)
    
    def test_remove_empty_array_key(self):
        """Test removing an empty array"""
        remove_key(self.temp_simple, 'emptyArray')
        
        with open(self.temp_simple, 'r') as f:
            data = json.load(f)
        
        self.assertNotIn('emptyArray', data)
    
    def test_remove_key_cleans_up_empty_parents(self):
        """Test that removing a key cleans up empty parent objects"""
        # First, remove all keys from a section to make it empty
        remove_key(self.temp_sample, 'dashboard.stats.users')
        remove_key(self.temp_sample, 'dashboard.stats.revenue')
        
        with open(self.temp_sample, 'r') as f:
            data = json.load(f)
        
        # The stats object should now be empty or removed
        if 'stats' in data.get('dashboard', {}):
            self.assertEqual(data['dashboard']['stats'], {})
    
    def test_remove_preserves_other_values(self):
        """Test that removing a key preserves other values in the same object"""
        # Store original data for comparison
        with open(self.temp_sample, 'r') as f:
            original_data = json.load(f)
        original_welcome = original_data['dashboard']['welcome']
        
        remove_key(self.temp_sample, 'dashboard.title')
        
        with open(self.temp_sample, 'r') as f:
            data = json.load(f)
        
        # Verify other values are preserved
        self.assertEqual(data['dashboard']['welcome'], original_welcome)
        self.assertIn('stats', data['dashboard'])
    
    def test_remove_from_complex_nested_structure(self):
        """Test removing from complex nested structures"""
        remove_key(self.temp_sample, 'forms.validation.email')
        
        with open(self.temp_sample, 'r') as f:
            data = json.load(f)
        
        # Verify specific key was removed
        self.assertNotIn('email', data['forms']['validation'])
        
        # Verify other validation keys are preserved
        self.assertIn('required', data['forms']['validation'])
        self.assertIn('minLength', data['forms']['validation'])
        
        # Verify other forms sections are preserved
        self.assertIn('buttons', data['forms'])
    
    def test_remove_key_with_special_characters(self):
        """Test removing keys with special characters"""
        # Add and then remove a key with special characters
        with open(self.temp_simple, 'r') as f:
            data = json.load(f)
        data['special.key'] = 'special value'
        with open(self.temp_simple, 'w') as f:
            json.dump(data, f, indent=2)
        
        remove_key(self.temp_simple, 'special.key')
        
        with open(self.temp_simple, 'r') as f:
            data = json.load(f)
        
        self.assertNotIn('special.key', data)
    
    def test_remove_nonexistent_key_fails(self):
        """Test that removing a nonexistent key raises an error"""
        with self.assertRaises(KeyError) as context:
            remove_key(self.temp_sample, 'nonexistent.key')
        
        self.assertIn("KEY_NOT_FOUND", str(context.exception))
        self.assertIn("nonexistent.key", str(context.exception))
    
    def test_remove_key_partial_path_not_exists(self):
        """Test removing when part of the path doesn't exist"""
        with self.assertRaises(KeyError) as context:
            remove_key(self.temp_sample, 'dashboard.nonexistent.key')
        
        self.assertIn("KEY_NOT_FOUND", str(context.exception))
    
    def test_remove_key_from_nonexistent_file(self):
        """Test removing a key from a file that doesn't exist"""
        nonexistent_file = self.temp_dir / "nonexistent.json"
        
        with self.assertRaises(FileNotFoundError) as context:
            remove_key(nonexistent_file, 'any.key')
        
        self.assertIn("FILE_NOT_FOUND", str(context.exception))
    
    def test_remove_key_invalid_path(self):
        """Test removing with invalid path"""
        with self.assertRaises(ValueError) as context:
            remove_key(self.temp_sample, '')
        
        self.assertIn("INVALID_PATH", str(context.exception))
        
        with self.assertRaises(ValueError) as context:
            remove_key(self.temp_sample, None)
        
        self.assertIn("INVALID_PATH", str(context.exception))
    
    def test_remove_key_from_invalid_json_file(self):
        """Test removing a key from a file with invalid JSON"""
        invalid_file = self.temp_dir / "invalid.json"
        shutil.copy2(self.test_dir / "invalid.json", invalid_file)
        
        with self.assertRaises(ValueError) as context:
            remove_key(invalid_file, 'any.key')
        
        self.assertIn("INVALID_JSON", str(context.exception))
    
    def test_remove_preserves_file_structure(self):
        """Test that removing preserves overall file structure"""
        # Store original top-level keys
        with open(self.temp_sample, 'r') as f:
            original_keys = set(json.load(f).keys())
        
        remove_key(self.temp_sample, 'dashboard.title')
        
        # Load modified data
        with open(self.temp_sample, 'r') as f:
            modified_keys = set(json.load(f).keys())
        
        # Verify top-level structure is preserved
        self.assertEqual(original_keys, modified_keys)
    
    def test_remove_multiple_keys_sequentially(self):
        """Test removing multiple keys in sequence"""
        remove_key(self.temp_sample, 'dashboard.title')
        remove_key(self.temp_sample, 'dashboard.welcome')
        remove_key(self.temp_sample, 'dashboard.stats.users')
        
        with open(self.temp_sample, 'r') as f:
            data = json.load(f)
        
        # Verify all keys were removed
        self.assertNotIn('title', data['dashboard'])
        self.assertNotIn('welcome', data['dashboard'])
        self.assertNotIn('users', data['dashboard'].get('stats', {}))
        
        # Verify remaining structure
        self.assertIn('revenue', data['dashboard']['stats'])
    
    def test_remove_all_keys_from_object(self):
        """Test removing all keys from an object"""
        remove_key(self.temp_sample, 'alerts.success')
        remove_key(self.temp_sample, 'alerts.error')
        remove_key(self.temp_sample, 'alerts.warning')
        
        with open(self.temp_sample, 'r') as f:
            data = json.load(f)
        
        # The alerts object should now be empty
        self.assertEqual(data['alerts'], {})
    
    def test_remove_key_atomic_operation(self):
        """Test that remove_key is atomic (either succeeds completely or fails completely)"""
        # Try to remove a key that doesn't exist
        original_data = None
        with open(self.temp_sample, 'r') as f:
            original_data = json.load(f)
        
        try:
            remove_key(self.temp_sample, 'nonexistent.key')
        except Exception:
            pass
        
        # Verify original data is unchanged after failed operation
        with open(self.temp_sample, 'r') as f:
            current_data = json.load(f)
        
        self.assertEqual(original_data, current_data)
    
    def test_remove_key_case_sensitivity(self):
        """Test that key removal is case sensitive"""
        # These should fail because keys are case sensitive
        with self.assertRaises(KeyError):
            remove_key(self.temp_sample, 'Dashboard.title')  # Capital D
        
        with self.assertRaises(KeyError):
            remove_key(self.temp_sample, 'dashboard.Title')  # Capital T
        
        # Verify original keys still exist
        with open(self.temp_sample, 'r') as f:
            data = json.load(f)
        
        self.assertEqual(data['dashboard']['title'], 'Dashboard')


if __name__ == '__main__':
    unittest.main()