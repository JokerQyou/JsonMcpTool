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
from operations import update_key

class TestUpdateKey(unittest.TestCase):
    """Test cases for the update_key operation"""
    
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
    
    def test_update_simple_string_value(self):
        """Test updating a simple string value"""
        update_key(self.temp_sample, 'dashboard.title', 'Updated Dashboard')
        
        with open(self.temp_sample, 'r') as f:
            data = json.load(f)
        
        self.assertEqual(data['dashboard']['title'], 'Updated Dashboard')
    
    def test_update_nested_string_value(self):
        """Test updating a deeply nested string value"""
        update_key(self.temp_sample, 'auth.login.title', 'Updated Sign In')
        
        with open(self.temp_sample, 'r') as f:
            data = json.load(f)
        
        self.assertEqual(data['auth']['login']['title'], 'Updated Sign In')
    
    def test_update_value_with_different_type(self):
        """Test updating a value with a different data type"""
        # Update string to number
        update_key(self.temp_simple, 'simple', 42)
        
        with open(self.temp_simple, 'r') as f:
            data = json.load(f)
        
        self.assertEqual(data['simple'], 42)
        
        # Update number to boolean
        update_key(self.temp_simple, 'number', True)
        
        with open(self.temp_simple, 'r') as f:
            data = json.load(f)
        
        self.assertTrue(data['number'])
    
    def test_update_object_value(self):
        """Test updating an entire object"""
        new_validation = {
            "required": "Updated required message",
            "email": "Updated email message",
            "phone": "Invalid phone number"
        }
        
        update_key(self.temp_sample, 'forms.validation', new_validation)
        
        with open(self.temp_sample, 'r') as f:
            data = json.load(f)
        
        self.assertEqual(data['forms']['validation'], new_validation)
    
    def test_update_array_value(self):
        """Test updating an array value"""
        new_array = ["new_item1", "new_item2", {"newKey": "newValue"}]
        update_key(self.temp_simple, 'array', new_array)
        
        with open(self.temp_simple, 'r') as f:
            data = json.load(f)
        
        self.assertEqual(data['array'], new_array)
    
    def test_update_to_null_value(self):
        """Test updating a value to null"""
        update_key(self.temp_simple, 'simple', None)
        
        with open(self.temp_simple, 'r') as f:
            data = json.load(f)
        
        self.assertIsNone(data['simple'])
    
    def test_update_preserves_other_values(self):
        """Test that updating a key preserves other values in the same object"""
        # Store original validation object
        with open(self.temp_sample, 'r') as f:
            original_data = json.load(f)
        original_email = original_data['forms']['validation']['email']
        
        # Update only the 'required' field
        update_key(self.temp_sample, 'forms.validation.required', 'Updated required field')
        
        with open(self.temp_sample, 'r') as f:
            data = json.load(f)
        
        # Verify the updated field
        self.assertEqual(data['forms']['validation']['required'], 'Updated required field')
        # Verify other fields are preserved
        self.assertEqual(data['forms']['validation']['email'], original_email)
    
    def test_update_root_level_key(self):
        """Test updating a root-level key"""
        update_key(self.temp_simple, 'simple', 'Updated root value')
        
        with open(self.temp_simple, 'r') as f:
            data = json.load(f)
        
        self.assertEqual(data['simple'], 'Updated root value')
    
    def test_update_with_special_characters(self):
        """Test updating with special characters and Unicode"""
        special_value = 'Updated with "quotes" and \\backslashes\\ and émojis 🎉'
        update_key(self.temp_sample, 'dashboard.title', special_value)
        
        with open(self.temp_sample, 'r') as f:
            data = json.load(f)
        
        self.assertEqual(data['dashboard']['title'], special_value)
    
    def test_update_interpolation_strings(self):
        """Test updating I18Next interpolation strings"""
        interpolated_value = 'Welcome back, {{username}}! You have {{count}} messages.'
        update_key(self.temp_sample, 'dashboard.welcome', interpolated_value)
        
        with open(self.temp_sample, 'r') as f:
            data = json.load(f)
        
        self.assertEqual(data['dashboard']['welcome'], interpolated_value)
    
    def test_update_nonexistent_key_fails(self):
        """Test that updating a nonexistent key raises an error"""
        with self.assertRaises(KeyError) as context:
            update_key(self.temp_sample, 'nonexistent.key', 'New Value')
        
        self.assertIn("KEY_NOT_FOUND", str(context.exception))
        self.assertIn("nonexistent.key", str(context.exception))
    
    def test_update_partial_path_not_exists(self):
        """Test updating when part of the path doesn't exist"""
        with self.assertRaises(KeyError) as context:
            update_key(self.temp_sample, 'dashboard.nonexistent.key', 'Value')
        
        self.assertIn("KEY_NOT_FOUND", str(context.exception))
    
    def test_update_key_to_nonexistent_file(self):
        """Test updating a key in a file that doesn't exist"""
        nonexistent_file = self.temp_dir / "nonexistent.json"
        
        with self.assertRaises(FileNotFoundError) as context:
            update_key(nonexistent_file, 'any.key', 'value')
        
        self.assertIn("FILE_NOT_FOUND", str(context.exception))
    
    def test_update_key_invalid_path(self):
        """Test updating with invalid path"""
        with self.assertRaises(ValueError) as context:
            update_key(self.temp_sample, '', 'value')
        
        self.assertIn("INVALID_PATH", str(context.exception))
        
        with self.assertRaises(ValueError) as context:
            update_key(self.temp_sample, None, 'value')
        
        self.assertIn("INVALID_PATH", str(context.exception))
    
    def test_update_key_in_invalid_json_file(self):
        """Test updating a key in a file with invalid JSON"""
        invalid_file = self.temp_dir / "invalid.json"
        shutil.copy2(self.test_dir / "invalid.json", invalid_file)
        
        with self.assertRaises(ValueError) as context:
            update_key(invalid_file, 'any.key', 'value')
        
        self.assertIn("INVALID_JSON", str(context.exception))
    
    def test_update_preserves_file_structure(self):
        """Test that updating preserves the overall file structure"""
        # Store original data
        with open(self.temp_sample, 'r') as f:
            original_data = json.load(f)
        
        update_key(self.temp_sample, 'dashboard.title', 'Updated Title')
        
        # Load modified data
        with open(self.temp_sample, 'r') as f:
            modified_data = json.load(f)
        
        # Verify the update
        self.assertEqual(modified_data['dashboard']['title'], 'Updated Title')
        
        # Verify structure is preserved (same top-level keys)
        self.assertEqual(set(original_data.keys()), set(modified_data.keys()))
        
        # Verify other sections are unchanged
        self.assertEqual(original_data['forms'], modified_data['forms'])
        self.assertEqual(original_data['alerts'], modified_data['alerts'])
    
    def test_update_complex_nested_structure(self):
        """Test updating within a complex nested structure"""
        # Update a deeply nested value
        update_key(self.temp_sample, 'auth.login.password', 'Updated Password Label')
        
        with open(self.temp_sample, 'r') as f:
            data = json.load(f)
        
        self.assertEqual(data['auth']['login']['password'], 'Updated Password Label')
        # Verify other auth.login fields are preserved
        self.assertEqual(data['auth']['login']['title'], 'Sign In')
        self.assertEqual(data['auth']['login']['email'], 'Email Address')
    
    def test_update_same_value_succeeds(self):
        """Test that updating a key with the same value succeeds"""
        original_title = 'Dashboard'
        update_key(self.temp_sample, 'dashboard.title', original_title)
        
        with open(self.temp_sample, 'r') as f:
            data = json.load(f)
        
        self.assertEqual(data['dashboard']['title'], original_title)
    
    def test_update_empty_string_value(self):
        """Test updating with empty string value"""
        update_key(self.temp_sample, 'dashboard.title', '')
        
        with open(self.temp_sample, 'r') as f:
            data = json.load(f)
        
        self.assertEqual(data['dashboard']['title'], '')
    
    def test_update_very_long_value(self):
        """Test updating with a very long string value"""
        long_value = 'A' * 10000  # 10KB string
        update_key(self.temp_sample, 'dashboard.title', long_value)
        
        with open(self.temp_sample, 'r') as f:
            data = json.load(f)
        
        self.assertEqual(data['dashboard']['title'], long_value)


if __name__ == '__main__':
    unittest.main()