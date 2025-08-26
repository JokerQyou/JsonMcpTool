import unittest
import json
import tempfile
import os
import shutil
from pathlib import Path
import sys

# Add the unit test directory to the path to import the mock implementations
sys.path.append(str(Path(__file__).parent.parent / 'unit'))

from test_get_key import get_key
from test_add_key import add_key
from test_update_key import update_key
from test_rename_key import rename_key
from test_remove_key import remove_key
from test_list_keys import list_keys
from test_key_exists import key_exists
from test_validate_json import validate_json

class TestJsonToolsIntegration(unittest.TestCase):
    """Integration tests for all JSON operations working together"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_dir = Path(__file__).parent.parent / "fixtures"
        self.temp_dir = Path(tempfile.mkdtemp())
        
        # Create working copies
        self.working_file = self.temp_dir / "working_i18n.json"
        shutil.copy2(self.test_dir / "sample_i18n.json", self.working_file)
        
        # Create empty file for building from scratch
        self.build_file = self.temp_dir / "build_from_scratch.json"
        with open(self.build_file, 'w') as f:
            json.dump({}, f)
    
    def tearDown(self):
        """Clean up temporary files"""
        shutil.rmtree(self.temp_dir)
    
    def test_crud_workflow(self):
        """Test complete CRUD workflow on a single key"""
        key_path = 'new_feature.title'
        
        # 1. Verify key doesn't exist initially
        self.assertFalse(key_exists(self.working_file, key_path))
        
        # 2. Add the key
        add_key(self.working_file, key_path, 'New Feature Title')
        
        # 3. Verify key now exists
        self.assertTrue(key_exists(self.working_file, key_path))
        
        # 4. Read the key
        value = get_key(self.working_file, key_path)
        self.assertEqual(value, 'New Feature Title')
        
        # 5. Update the key
        update_key(self.working_file, key_path, 'Updated Feature Title')
        
        # 6. Verify the update
        updated_value = get_key(self.working_file, key_path)
        self.assertEqual(updated_value, 'Updated Feature Title')
        
        # 7. Rename the key
        new_key_path = 'new_feature.heading'
        rename_key(self.working_file, key_path, new_key_path)
        
        # 8. Verify rename worked
        self.assertFalse(key_exists(self.working_file, key_path))
        self.assertTrue(key_exists(self.working_file, new_key_path))
        renamed_value = get_key(self.working_file, new_key_path)
        self.assertEqual(renamed_value, 'Updated Feature Title')
        
        # 9. Remove the key
        remove_key(self.working_file, new_key_path)
        
        # 10. Verify removal
        self.assertFalse(key_exists(self.working_file, new_key_path))
    
    def test_build_translation_structure_from_scratch(self):
        """Test building a complete translation structure from empty file"""
        
        # Build a complete i18n structure
        translations = {
            'app.title': 'My Application',
            'app.description': 'A sample application',
            'navigation.home': 'Home',
            'navigation.about': 'About',
            'navigation.contact': 'Contact',
            'forms.login.title': 'Sign In',
            'forms.login.username': 'Username',
            'forms.login.password': 'Password',
            'forms.login.submit': 'Sign In',
            'forms.register.title': 'Create Account',
            'forms.register.email': 'Email Address',
            'forms.register.confirm_password': 'Confirm Password',
            'messages.success': 'Operation completed successfully',
            'messages.error': 'An error occurred',
            'messages.validation.required': 'This field is required'
        }
        
        # Add all keys
        for key_path, value in translations.items():
            add_key(self.build_file, key_path, value)
        
        # Verify structure was built correctly
        with open(self.build_file, 'r') as f:
            data = json.load(f)
        
        # Check top-level structure
        expected_top_level = ['app', 'navigation', 'forms', 'messages']
        self.assertEqual(sorted(data.keys()), sorted(expected_top_level))
        
        # Verify nested structure
        self.assertEqual(data['app']['title'], 'My Application')
        self.assertEqual(data['forms']['login']['username'], 'Username')
        self.assertEqual(data['messages']['validation']['required'], 'This field is required')
        
        # Verify all keys exist
        for key_path in translations.keys():
            self.assertTrue(key_exists(self.build_file, key_path))
    
    def test_complex_restructuring_workflow(self):
        """Test complex restructuring of existing translation file"""
        
        # 1. List existing structure
        root_keys = list_keys(self.working_file)
        self.assertIn('dashboard', root_keys)
        self.assertIn('forms', root_keys)
        
        # 2. Move dashboard section to main_page
        dashboard_content = get_key(self.working_file, 'dashboard')
        add_key(self.working_file, 'main_page', dashboard_content)
        remove_key(self.working_file, 'dashboard')
        
        # 3. Verify move
        self.assertFalse(key_exists(self.working_file, 'dashboard'))
        self.assertTrue(key_exists(self.working_file, 'main_page'))
        self.assertEqual(get_key(self.working_file, 'main_page.title'), 'Dashboard')
        
        # 4. Restructure forms section
        forms_keys = list_keys(self.working_file, 'forms')
        self.assertIn('validation', forms_keys)
        self.assertIn('buttons', forms_keys)
        
        # Move validation to common section
        validation_content = get_key(self.working_file, 'forms.validation')
        add_key(self.working_file, 'common.validation', validation_content)
        remove_key(self.working_file, 'forms.validation')
        
        # 5. Verify restructuring
        self.assertTrue(key_exists(self.working_file, 'common.validation.required'))
        self.assertFalse(key_exists(self.working_file, 'forms.validation'))
        
        # 6. Add new translations to existing sections
        add_key(self.working_file, 'main_page.subtitle', 'Welcome to the dashboard')
        add_key(self.working_file, 'common.loading', 'Loading...')
        
        # 7. Verify final structure
        final_root_keys = list_keys(self.working_file)
        expected_keys = ['main_page', 'forms', 'alerts', 'navigation', 'auth', 'common']
        self.assertEqual(sorted(final_root_keys), sorted(expected_keys))
    
    def test_error_recovery_workflow(self):
        """Test error handling and recovery in complex workflows"""
        
        # 1. Try to add existing key (should fail)
        with self.assertRaises(ValueError):
            add_key(self.working_file, 'dashboard.title', 'New Title')
        
        # Verify original data is unchanged
        original_title = get_key(self.working_file, 'dashboard.title')
        self.assertEqual(original_title, 'Dashboard')
        
        # 2. Try to update non-existent key (should fail)
        with self.assertRaises(KeyError):
            update_key(self.working_file, 'nonexistent.key', 'Some value')
        
        # 3. Try to rename to existing key (should fail)
        with self.assertRaises(ValueError):
            rename_key(self.working_file, 'dashboard.title', 'dashboard.welcome')
        
        # Verify original structure is preserved
        self.assertTrue(key_exists(self.working_file, 'dashboard.title'))
        self.assertTrue(key_exists(self.working_file, 'dashboard.welcome'))
        
        # 4. Try to remove non-existent key (should fail)
        with self.assertRaises(KeyError):
            remove_key(self.working_file, 'nonexistent.section.key')
        
        # 5. Verify file integrity after errors
        validation_result = validate_json(self.working_file)
        self.assertTrue(validation_result['valid'])
    
    def test_bulk_operations_workflow(self):
        """Test performing bulk operations efficiently"""
        
        # 1. Add multiple related keys
        notification_keys = {
            'notifications.email.subject': 'Email Notification',
            'notifications.email.body': 'You have a new message',
            'notifications.push.title': 'Push Notification',
            'notifications.push.body': 'Tap to view details',
            'notifications.sms.message': 'SMS: You have an update'
        }
        
        for key_path, value in notification_keys.items():
            add_key(self.working_file, key_path, value)
        
        # 2. Verify all keys were added
        for key_path in notification_keys.keys():
            self.assertTrue(key_exists(self.working_file, key_path))
        
        # 3. Update multiple keys with common pattern
        email_keys = list_keys(self.working_file, 'notifications.email')
        for key in email_keys:
            current_value = get_key(self.working_file, f'notifications.email.{key}')
            updated_value = f"[Updated] {current_value}"
            update_key(self.working_file, f'notifications.email.{key}', updated_value)
        
        # 4. Verify updates
        updated_subject = get_key(self.working_file, 'notifications.email.subject')
        self.assertTrue(updated_subject.startswith('[Updated]'))
        
        # 5. Remove entire notification section
        remove_key(self.working_file, 'notifications')
        
        # 6. Verify removal
        self.assertFalse(key_exists(self.working_file, 'notifications'))
        for key_path in notification_keys.keys():
            self.assertFalse(key_exists(self.working_file, key_path))
    
    def test_i18next_specific_workflow(self):
        """Test workflow specific to I18Next translation patterns"""
        
        # 1. Add pluralization keys
        add_key(self.working_file, 'items.item', 'item')
        add_key(self.working_file, 'items.item_plural', 'items')
        
        # 2. Add interpolation strings
        add_key(self.working_file, 'welcome.user', 'Welcome, {{username}}!')
        add_key(self.working_file, 'cart.items', 'You have {{count}} items in your cart')
        
        # 3. Add nested namespaces
        add_key(self.working_file, 'errors.validation.email', 'Invalid email format')
        add_key(self.working_file, 'errors.validation.password', 'Password must be at least {{min}} characters')
        add_key(self.working_file, 'errors.network.timeout', 'Request timed out')
        add_key(self.working_file, 'errors.network.offline', 'No internet connection')
        
        # 4. Verify I18Next patterns work correctly
        welcome_msg = get_key(self.working_file, 'welcome.user')
        self.assertIn('{{username}}', welcome_msg)
        
        cart_msg = get_key(self.working_file, 'cart.items')
        self.assertIn('{{count}}', cart_msg)
        
        password_error = get_key(self.working_file, 'errors.validation.password')
        self.assertIn('{{min}}', password_error)
        
        # 5. Test namespace listing
        error_categories = list_keys(self.working_file, 'errors')
        self.assertIn('validation', error_categories)
        self.assertIn('network', error_categories)
        
        validation_errors = list_keys(self.working_file, 'errors.validation')
        self.assertIn('email', validation_errors)
        self.assertIn('password', validation_errors)
    
    def test_file_consistency_across_operations(self):
        """Test that file remains consistent across multiple operations"""
        
        # Record initial state
        initial_validation = validate_json(self.working_file)
        self.assertTrue(initial_validation['valid'])
        
        initial_keys = list_keys(self.working_file)
        
        # Perform various operations
        operations = [
            lambda: add_key(self.working_file, 'temp.test1', 'value1'),
            lambda: add_key(self.working_file, 'temp.test2', {'nested': 'value'}),
            lambda: update_key(self.working_file, 'temp.test1', 'updated_value1'),
            lambda: rename_key(self.working_file, 'temp.test1', 'temp.renamed_test1'),
            lambda: remove_key(self.working_file, 'temp.test2'),
            lambda: remove_key(self.working_file, 'temp.renamed_test1')
        ]
        
        for operation in operations:
            operation()
            
            # Verify file is still valid JSON after each operation
            validation_result = validate_json(self.working_file)
            self.assertTrue(validation_result['valid'], 
                           f"File became invalid after operation: {operation}")
        
        # Verify we're back to original structure
        final_keys = list_keys(self.working_file)
        self.assertEqual(sorted(initial_keys), sorted(final_keys))
        
        # Verify specific original values are preserved
        self.assertEqual(get_key(self.working_file, 'dashboard.title'), 'Dashboard')
        self.assertEqual(get_key(self.working_file, 'forms.buttons.submit'), 'Submit')
    
    def test_concurrent_section_modifications(self):
        """Test modifying different sections of the same file"""
        
        # Work on different sections simultaneously (simulating concurrent access)
        
        # Modify dashboard section
        add_key(self.working_file, 'dashboard.new_field', 'New Dashboard Field')
        update_key(self.working_file, 'dashboard.title', 'Updated Dashboard')
        
        # Modify forms section  
        add_key(self.working_file, 'forms.new_validation.custom', 'Custom validation message')
        update_key(self.working_file, 'forms.buttons.submit', 'Submit Form')
        
        # Modify auth section
        add_key(self.working_file, 'auth.logout.title', 'Sign Out')
        rename_key(self.working_file, 'auth.login.title', 'auth.login.heading')
        
        # Verify all modifications worked
        self.assertEqual(get_key(self.working_file, 'dashboard.new_field'), 'New Dashboard Field')
        self.assertEqual(get_key(self.working_file, 'dashboard.title'), 'Updated Dashboard')
        
        self.assertEqual(get_key(self.working_file, 'forms.new_validation.custom'), 'Custom validation message')
        self.assertEqual(get_key(self.working_file, 'forms.buttons.submit'), 'Submit Form')
        
        self.assertEqual(get_key(self.working_file, 'auth.logout.title'), 'Sign Out')
        self.assertFalse(key_exists(self.working_file, 'auth.login.title'))
        self.assertTrue(key_exists(self.working_file, 'auth.login.heading'))
        
        # Verify file integrity
        validation_result = validate_json(self.working_file)
        self.assertTrue(validation_result['valid'])


if __name__ == '__main__':
    unittest.main()