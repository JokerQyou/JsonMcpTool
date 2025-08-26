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
from operations import add_key

class TestAddKey(unittest.TestCase):
    """Test cases for the add_key operation"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_dir = Path(__file__).parent.parent / "fixtures"
        
        # Create temporary copies for modification
        self.temp_dir = Path(tempfile.mkdtemp())
        self.temp_sample = self.temp_dir / "sample_i18n.json"
        self.temp_simple = self.temp_dir / "simple_test.json"
        self.temp_empty = self.temp_dir / "empty.json"
        
        shutil.copy2(self.test_dir / "sample_i18n.json", self.temp_sample)
        shutil.copy2(self.test_dir / "simple_test.json", self.temp_simple)
        shutil.copy2(self.test_dir / "empty.json", self.temp_empty)
    
    def tearDown(self):
        """Clean up temporary files"""
        shutil.rmtree(self.temp_dir)
    
    def test_add_simple_string_key(self):
        """Test adding a simple string value"""
        add_key(self.temp_sample, 'new.simple.key', 'New Value')
        
        # Verify the key was added
        with open(self.temp_sample, 'r') as f:
            data = json.load(f)
        
        self.assertEqual(data['new']['simple']['key'], 'New Value')
    
    def test_add_key_to_existing_section(self):
        """Test adding a key to an existing section"""
        add_key(self.temp_sample, 'dashboard.subtitle', 'Welcome to your dashboard')
        
        with open(self.temp_sample, 'r') as f:
            data = json.load(f)
        
        self.assertEqual(data['dashboard']['subtitle'], 'Welcome to your dashboard')
        # Verify existing keys are preserved
        self.assertEqual(data['dashboard']['title'], 'Dashboard')
    
    def test_add_nested_object_value(self):
        """Test adding a nested object value"""
        nested_obj = {
            'title': 'New Modal',
            'buttons': {
                'confirm': 'Confirm Action',
                'cancel': 'Cancel'
            }
        }
        add_key(self.temp_sample, 'modals.confirmation', nested_obj)
        
        with open(self.temp_sample, 'r') as f:
            data = json.load(f)
        
        self.assertEqual(data['modals']['confirmation'], nested_obj)
    
    def test_add_array_value(self):
        """Test adding an array value"""
        array_value = ['option1', 'option2', 'option3']
        add_key(self.temp_sample, 'dropdown.options', array_value)
        
        with open(self.temp_sample, 'r') as f:
            data = json.load(f)
        
        self.assertEqual(data['dropdown']['options'], array_value)
    
    def test_add_different_data_types(self):
        """Test adding different JSON data types"""
        # Boolean
        add_key(self.temp_simple, 'newBoolean', True)
        
        # Number
        add_key(self.temp_simple, 'newNumber', 100)
        
        # Float
        add_key(self.temp_simple, 'newFloat', 99.99)
        
        # Null
        add_key(self.temp_simple, 'newNull', None)
        
        with open(self.temp_simple, 'r') as f:
            data = json.load(f)
        
        self.assertTrue(data['newBoolean'])
        self.assertEqual(data['newNumber'], 100)
        self.assertEqual(data['newFloat'], 99.99)
        self.assertIsNone(data['newNull'])
    
    def test_add_key_to_empty_file(self):
        """Test adding a key to an empty JSON object"""
        add_key(self.temp_empty, 'first.key', 'First value')
        
        with open(self.temp_empty, 'r') as f:
            data = json.load(f)
        
        self.assertEqual(data['first']['key'], 'First value')
    
    def test_add_root_level_key(self):
        """Test adding a root-level key"""
        add_key(self.temp_simple, 'rootKey', 'Root value')
        
        with open(self.temp_simple, 'r') as f:
            data = json.load(f)
        
        self.assertEqual(data['rootKey'], 'Root value')
    
    def test_add_deeply_nested_key(self):
        """Test adding a deeply nested key"""
        add_key(self.temp_empty, 'level1.level2.level3.level4.deep', 'Deep value')
        
        with open(self.temp_empty, 'r') as f:
            data = json.load(f)
        
        self.assertEqual(data['level1']['level2']['level3']['level4']['deep'], 'Deep value')
    
    def test_add_key_with_special_characters(self):
        """Test adding keys and values with special characters"""
        special_value = 'Value with "quotes" and \\backslashes\\ and émojis 🎉'
        add_key(self.temp_simple, 'special.chars', special_value)
        
        with open(self.temp_simple, 'r') as f:
            data = json.load(f)
        
        self.assertEqual(data['special']['chars'], special_value)
    
    def test_add_key_with_unicode(self):
        """Test adding keys and values with Unicode characters"""
        unicode_value = 'Héllo Wörld! 你好世界 🌍'
        add_key(self.temp_simple, 'unicode.test', unicode_value)
        
        with open(self.temp_simple, 'r') as f:
            data = json.load(f)
        
        self.assertEqual(data['unicode']['test'], unicode_value)
    
    def test_add_existing_key_fails(self):
        """Test that adding an existing key raises an error"""
        with self.assertRaises(ValueError) as context:
            add_key(self.temp_sample, 'dashboard.title', 'New Title')
        
        self.assertIn("KEY_EXISTS", str(context.exception))
        self.assertIn("dashboard.title", str(context.exception))
        
        # Verify original value is unchanged
        with open(self.temp_sample, 'r') as f:
            data = json.load(f)
        self.assertEqual(data['dashboard']['title'], 'Dashboard')
    
    def test_add_key_partial_path_exists(self):
        """Test adding a key where part of the path exists"""
        add_key(self.temp_sample, 'dashboard.new.nested.key', 'New nested value')
        
        with open(self.temp_sample, 'r') as f:
            data = json.load(f)
        
        self.assertEqual(data['dashboard']['new']['nested']['key'], 'New nested value')
        # Verify existing dashboard keys are preserved
        self.assertEqual(data['dashboard']['title'], 'Dashboard')
    
    def test_add_key_to_nonexistent_file(self):
        """Test adding a key to a file that doesn't exist"""
        nonexistent_file = self.temp_dir / "nonexistent.json"
        
        with self.assertRaises(FileNotFoundError) as context:
            add_key(nonexistent_file, 'new.key', 'value')
        
        self.assertIn("FILE_NOT_FOUND", str(context.exception))
    
    def test_add_key_invalid_path(self):
        """Test adding a key with invalid path"""
        with self.assertRaises(ValueError) as context:
            add_key(self.temp_sample, '', 'value')
        
        self.assertIn("INVALID_PATH", str(context.exception))
        
        with self.assertRaises(ValueError) as context:
            add_key(self.temp_sample, None, 'value')
        
        self.assertIn("INVALID_PATH", str(context.exception))
    
    def test_add_key_to_invalid_json_file(self):
        """Test adding a key to a file with invalid JSON"""
        invalid_file = self.temp_dir / "invalid.json"
        shutil.copy2(self.test_dir / "invalid.json", invalid_file)
        
        with self.assertRaises(ValueError) as context:
            add_key(invalid_file, 'new.key', 'value')
        
        self.assertIn("INVALID_JSON", str(context.exception))
    
    def test_add_key_preserves_file_structure(self):
        """Test that adding a key preserves the existing file structure"""
        # Store original data
        with open(self.temp_sample, 'r') as f:
            original_data = json.load(f)
        
        add_key(self.temp_sample, 'new.section.key', 'new value')
        
        # Load modified data
        with open(self.temp_sample, 'r') as f:
            modified_data = json.load(f)
        
        # Verify new key exists
        self.assertEqual(modified_data['new']['section']['key'], 'new value')
        
        # Verify all original keys are preserved
        for key in original_data:
            self.assertIn(key, modified_data)
            self.assertEqual(original_data[key], modified_data[key])
    
    def test_add_key_creates_intermediate_objects(self):
        """Test that adding a nested key creates intermediate objects"""
        add_key(self.temp_empty, 'a.b.c.d.e', 'deep value')
        
        with open(self.temp_empty, 'r') as f:
            data = json.load(f)
        
        # Verify intermediate objects were created
        self.assertIsInstance(data['a'], dict)
        self.assertIsInstance(data['a']['b'], dict)
        self.assertIsInstance(data['a']['b']['c'], dict)
        self.assertIsInstance(data['a']['b']['c']['d'], dict)
        self.assertEqual(data['a']['b']['c']['d']['e'], 'deep value')
    
    def test_add_key_atomic_operation(self):
        """Test that add_key is atomic (either succeeds completely or fails completely)"""
        # Try to add a key that conflicts with existing structure
        try:
            # This should fail because 'dashboard.title' already exists as a string
            # and we're trying to add 'dashboard.title.subtitle'
            add_key(self.temp_sample, 'dashboard.title.subtitle', 'value')
        except Exception:
            pass
        
        # Verify original data is unchanged
        with open(self.temp_sample, 'r') as f:
            data = json.load(f)
        
        self.assertEqual(data['dashboard']['title'], 'Dashboard')
        self.assertNotIn('subtitle', data['dashboard'].get('title', {}))


if __name__ == '__main__':
    unittest.main()