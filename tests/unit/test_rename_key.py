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
from operations import rename_key

class TestRenameKey(unittest.TestCase):
    """Test cases for the rename_key operation"""
    
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
    
    def test_rename_simple_key(self):
        """Test renaming a simple key"""
        rename_key(self.temp_sample, 'dashboard.title', 'dashboard.heading')
        
        with open(self.temp_sample, 'r') as f:
            data = json.load(f)
        
        # Verify new key exists with original value
        self.assertEqual(data['dashboard']['heading'], 'Dashboard')
        # Verify old key no longer exists
        self.assertNotIn('title', data['dashboard'])
    
    def test_rename_nested_key(self):
        """Test renaming a deeply nested key"""
        rename_key(self.temp_sample, 'auth.login.title', 'auth.login.heading')
        
        with open(self.temp_sample, 'r') as f:
            data = json.load(f)
        
        self.assertEqual(data['auth']['login']['heading'], 'Sign In')
        self.assertNotIn('title', data['auth']['login'])
    
    def test_rename_key_with_object_value(self):
        """Test renaming a key that contains an object"""
        rename_key(self.temp_sample, 'forms.validation', 'forms.rules')
        
        with open(self.temp_sample, 'r') as f:
            data = json.load(f)
        
        # Verify the object was moved
        expected_rules = {
            "required": "This field is required",
            "email": "Please enter a valid email",
            "minLength": "Minimum {{count}} characters required"
        }
        self.assertEqual(data['forms']['rules'], expected_rules)
        self.assertNotIn('validation', data['forms'])
    
    def test_rename_key_with_array_value(self):
        """Test renaming a key that contains an array"""
        rename_key(self.temp_simple, 'array', 'items')
        
        with open(self.temp_simple, 'r') as f:
            data = json.load(f)
        
        expected_array = ["item1", "item2", {"arrayObject": "value"}]
        self.assertEqual(data['items'], expected_array)
        self.assertNotIn('array', data)
    
    def test_rename_root_level_key(self):
        """Test renaming a root-level key"""
        rename_key(self.temp_simple, 'simple', 'basic')
        
        with open(self.temp_simple, 'r') as f:
            data = json.load(f)
        
        self.assertEqual(data['basic'], 'value')
        self.assertNotIn('simple', data)
    
    def test_rename_key_across_sections(self):
        """Test renaming a key from one section to another"""
        rename_key(self.temp_sample, 'dashboard.title', 'alerts.dashboard_title')
        
        with open(self.temp_sample, 'r') as f:
            data = json.load(f)
        
        self.assertEqual(data['alerts']['dashboard_title'], 'Dashboard')
        self.assertNotIn('title', data['dashboard'])
    
    def test_rename_key_to_different_nesting_level(self):
        """Test renaming a key to a different nesting level"""
        # Move from nested to root
        rename_key(self.temp_sample, 'dashboard.title', 'page_title')
        
        with open(self.temp_sample, 'r') as f:
            data = json.load(f)
        
        self.assertEqual(data['page_title'], 'Dashboard')
        self.assertNotIn('title', data['dashboard'])
        
        # Move from root to nested (using simple file)
        rename_key(self.temp_simple, 'simple', 'nested.simple')
        
        with open(self.temp_simple, 'r') as f:
            data = json.load(f)
        
        self.assertEqual(data['nested']['simple'], 'value')
        self.assertNotIn('simple', data)
    
    def test_rename_key_creates_intermediate_objects(self):
        """Test that renaming creates intermediate objects when needed"""
        rename_key(self.temp_sample, 'dashboard.title', 'new.section.subsection.title')
        
        with open(self.temp_sample, 'r') as f:
            data = json.load(f)
        
        self.assertEqual(data['new']['section']['subsection']['title'], 'Dashboard')
        self.assertNotIn('title', data['dashboard'])
        
        # Verify intermediate objects were created
        self.assertIsInstance(data['new'], dict)
        self.assertIsInstance(data['new']['section'], dict)
        self.assertIsInstance(data['new']['section']['subsection'], dict)
    
    def test_rename_preserves_other_values(self):
        """Test that renaming preserves other values in the same object"""
        # Store original welcome message
        with open(self.temp_sample, 'r') as f:
            original_welcome = json.load(f)['dashboard']['welcome']
        
        rename_key(self.temp_sample, 'dashboard.title', 'dashboard.heading')
        
        with open(self.temp_sample, 'r') as f:
            data = json.load(f)
        
        # Verify rename worked
        self.assertEqual(data['dashboard']['heading'], 'Dashboard')
        # Verify other values preserved
        self.assertEqual(data['dashboard']['welcome'], original_welcome)
    
    def test_rename_key_with_special_characters(self):
        """Test renaming keys with special characters"""
        # Add a key with special characters first
        with open(self.temp_simple, 'r') as f:
            data = json.load(f)
        data['special.key'] = 'special value'
        with open(self.temp_simple, 'w') as f:
            json.dump(data, f, indent=2)
        
        rename_key(self.temp_simple, 'special.key', 'renamed_special_key')
        
        with open(self.temp_simple, 'r') as f:
            data = json.load(f)
        
        self.assertEqual(data['renamed_special_key'], 'special value')
        self.assertNotIn('special.key', data)
    
    def test_rename_nonexistent_key_fails(self):
        """Test that renaming a nonexistent key raises an error"""
        with self.assertRaises(KeyError) as context:
            rename_key(self.temp_sample, 'nonexistent.key', 'new.name')
        
        self.assertIn("KEY_NOT_FOUND", str(context.exception))
        self.assertIn("nonexistent.key", str(context.exception))
    
    def test_rename_to_existing_key_fails(self):
        """Test that renaming to an existing key raises an error"""
        with self.assertRaises(ValueError) as context:
            rename_key(self.temp_sample, 'dashboard.title', 'dashboard.welcome')
        
        self.assertIn("KEY_EXISTS", str(context.exception))
        self.assertIn("dashboard.welcome", str(context.exception))
        
        # Verify original data is unchanged
        with open(self.temp_sample, 'r') as f:
            data = json.load(f)
        self.assertEqual(data['dashboard']['title'], 'Dashboard')
        self.assertIn('welcome', data['dashboard'])
    
    def test_rename_key_to_same_name_fails(self):
        """Test that renaming a key to itself raises an error"""
        with self.assertRaises(ValueError) as context:
            rename_key(self.temp_sample, 'dashboard.title', 'dashboard.title')
        
        self.assertIn("SAME_KEY", str(context.exception))
    
    def test_rename_key_invalid_old_path(self):
        """Test renaming with invalid old path"""
        with self.assertRaises(ValueError) as context:
            rename_key(self.temp_sample, '', 'new.name')
        
        self.assertIn("INVALID_PATH", str(context.exception))
        
        with self.assertRaises(ValueError) as context:
            rename_key(self.temp_sample, None, 'new.name')
        
        self.assertIn("INVALID_PATH", str(context.exception))
    
    def test_rename_key_invalid_new_path(self):
        """Test renaming with invalid new path"""
        with self.assertRaises(ValueError) as context:
            rename_key(self.temp_sample, 'dashboard.title', '')
        
        self.assertIn("INVALID_PATH", str(context.exception))
        
        with self.assertRaises(ValueError) as context:
            rename_key(self.temp_sample, 'dashboard.title', None)
        
        self.assertIn("INVALID_PATH", str(context.exception))
    
    def test_rename_key_nonexistent_file(self):
        """Test renaming in a file that doesn't exist"""
        nonexistent_file = self.temp_dir / "nonexistent.json"
        
        with self.assertRaises(FileNotFoundError) as context:
            rename_key(nonexistent_file, 'old.key', 'new.key')
        
        self.assertIn("FILE_NOT_FOUND", str(context.exception))
    
    def test_rename_key_invalid_json_file(self):
        """Test renaming in a file with invalid JSON"""
        invalid_file = self.temp_dir / "invalid.json"
        shutil.copy2(self.test_dir / "invalid.json", invalid_file)
        
        with self.assertRaises(ValueError) as context:
            rename_key(invalid_file, 'old.key', 'new.key')
        
        self.assertIn("INVALID_JSON", str(context.exception))
    
    def test_rename_preserves_file_structure(self):
        """Test that renaming preserves overall file structure"""
        # Store original data
        with open(self.temp_sample, 'r') as f:
            original_data = json.load(f)
        
        rename_key(self.temp_sample, 'dashboard.title', 'dashboard.heading')
        
        # Load modified data
        with open(self.temp_sample, 'r') as f:
            modified_data = json.load(f)
        
        # Verify structure is preserved (same top-level keys)
        self.assertEqual(set(original_data.keys()), set(modified_data.keys()))
        
        # Verify other sections are unchanged
        self.assertEqual(original_data['forms'], modified_data['forms'])
        self.assertEqual(original_data['alerts'], modified_data['alerts'])
    
    def test_rename_entire_section(self):
        """Test renaming an entire section"""
        rename_key(self.temp_sample, 'dashboard', 'main_page')
        
        with open(self.temp_sample, 'r') as f:
            data = json.load(f)
        
        # Verify entire dashboard section moved to main_page
        self.assertIn('main_page', data)
        self.assertNotIn('dashboard', data)
        
        # Verify content is preserved
        self.assertEqual(data['main_page']['title'], 'Dashboard')
        self.assertIn('welcome', data['main_page'])
        self.assertIn('stats', data['main_page'])
    
    def test_rename_complex_nested_structure(self):
        """Test renaming within complex nested structures"""
        rename_key(self.temp_sample, 'auth.login', 'auth.signin')
        
        with open(self.temp_sample, 'r') as f:
            data = json.load(f)
        
        # Verify the entire login section was renamed
        self.assertIn('signin', data['auth'])
        self.assertNotIn('login', data['auth'])
        
        # Verify content is preserved
        self.assertEqual(data['auth']['signin']['title'], 'Sign In')
        self.assertEqual(data['auth']['signin']['email'], 'Email Address')
        
        # Verify other auth sections are preserved
        self.assertIn('register', data['auth'])


if __name__ == '__main__':
    unittest.main()