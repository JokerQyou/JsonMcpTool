import unittest
import json
import tempfile
import os
import shutil
from pathlib import Path

class TestValidateJson(unittest.TestCase):
    """Test cases for the validate_json operation"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_dir = Path(__file__).parent.parent / "fixtures"
        self.temp_dir = Path(tempfile.mkdtemp())
        
        # Valid JSON files
        self.sample_file = self.test_dir / "sample_i18n.json"
        self.simple_file = self.test_dir / "simple_test.json"
        self.empty_file = self.test_dir / "empty.json"
        
        # Invalid JSON file
        self.invalid_file = self.test_dir / "invalid.json"
    
    def tearDown(self):
        """Clean up temporary files"""
        shutil.rmtree(self.temp_dir)
    
    def test_validate_valid_json_files(self):
        """Test validating valid JSON files"""
        # Sample i18n file
        result = validate_json(self.sample_file)
        self.assertTrue(result['valid'])
        self.assertIsNone(result['error'])
        self.assertEqual(result['file'], str(self.sample_file))
        
        # Simple test file
        result = validate_json(self.simple_file)
        self.assertTrue(result['valid'])
        self.assertIsNone(result['error'])
        
        # Empty JSON object
        result = validate_json(self.empty_file)
        self.assertTrue(result['valid'])
        self.assertIsNone(result['error'])
    
    def test_validate_invalid_json_file(self):
        """Test validating an invalid JSON file"""
        result = validate_json(self.invalid_file)
        
        self.assertFalse(result['valid'])
        self.assertIsNotNone(result['error'])
        self.assertIn('error_type', result)
        self.assertEqual(result['error_type'], 'PARSE_ERROR')
        self.assertIn('message', result['error'])
        self.assertIn('line', result['error'])
        self.assertEqual(result['file'], str(self.invalid_file))
    
    def test_validate_json_syntax_errors(self):
        """Test validating JSON files with various syntax errors"""
        
        # Missing closing brace
        missing_brace_file = self.temp_dir / "missing_brace.json"
        with open(missing_brace_file, 'w') as f:
            f.write('{"key": "value"')
        
        result = validate_json(missing_brace_file)
        self.assertFalse(result['valid'])
        self.assertEqual(result['error_type'], 'PARSE_ERROR')
        self.assertIn('brace', result['error']['message'].lower())
        
        # Missing comma
        missing_comma_file = self.temp_dir / "missing_comma.json"
        with open(missing_comma_file, 'w') as f:
            f.write('{"key1": "value1" "key2": "value2"}')
        
        result = validate_json(missing_comma_file)
        self.assertFalse(result['valid'])
        self.assertEqual(result['error_type'], 'PARSE_ERROR')
        
        # Trailing comma (may be invalid depending on JSON parser)
        trailing_comma_file = self.temp_dir / "trailing_comma.json"
        with open(trailing_comma_file, 'w') as f:
            f.write('{"key1": "value1", "key2": "value2",}')
        
        result = validate_json(trailing_comma_file)
        # Note: Some JSON parsers allow trailing commas, others don't
        # The test should handle both cases
        if not result['valid']:
            self.assertEqual(result['error_type'], 'PARSE_ERROR')
    
    def test_validate_json_string_errors(self):
        """Test validating JSON files with string-related errors"""
        
        # Unescaped quotes
        unescaped_quotes_file = self.temp_dir / "unescaped_quotes.json"
        with open(unescaped_quotes_file, 'w') as f:
            f.write('{"key": "value with "quotes" inside"}')
        
        result = validate_json(unescaped_quotes_file)
        self.assertFalse(result['valid'])
        self.assertEqual(result['error_type'], 'PARSE_ERROR')
        
        # Unterminated string
        unterminated_string_file = self.temp_dir / "unterminated_string.json"
        with open(unterminated_string_file, 'w') as f:
            f.write('{"key": "unterminated string')
        
        result = validate_json(unterminated_string_file)
        self.assertFalse(result['valid'])
        self.assertEqual(result['error_type'], 'PARSE_ERROR')
    
    def test_validate_json_number_errors(self):
        """Test validating JSON files with number-related errors"""
        
        # Invalid number format
        invalid_number_file = self.temp_dir / "invalid_number.json"
        with open(invalid_number_file, 'w') as f:
            f.write('{"key": 123.45.67}')  # Invalid number
        
        result = validate_json(invalid_number_file)
        self.assertFalse(result['valid'])
        self.assertEqual(result['error_type'], 'PARSE_ERROR')
    
    def test_validate_empty_file(self):
        """Test validating an empty file"""
        empty_content_file = self.temp_dir / "empty_content.json"
        with open(empty_content_file, 'w') as f:
            pass  # Create empty file
        
        result = validate_json(empty_content_file)
        self.assertFalse(result['valid'])
        self.assertEqual(result['error_type'], 'PARSE_ERROR')
        self.assertIn('empty', result['error']['message'].lower())
    
    def test_validate_whitespace_only_file(self):
        """Test validating a file with only whitespace"""
        whitespace_file = self.temp_dir / "whitespace.json"
        with open(whitespace_file, 'w') as f:
            f.write('   \n\t  \n  ')  # Only whitespace
        
        result = validate_json(whitespace_file)
        self.assertFalse(result['valid'])
        self.assertEqual(result['error_type'], 'PARSE_ERROR')
    
    def test_validate_large_valid_json(self):
        """Test validating a large valid JSON file"""
        large_json_file = self.temp_dir / "large_valid.json"
        
        # Create a large JSON structure
        large_data = {}
        for i in range(1000):
            large_data[f'section_{i}'] = {
                'title': f'Title {i}',
                'description': f'Description for section {i}',
                'items': [f'item_{j}' for j in range(10)],
                'metadata': {
                    'created': f'2023-01-{i%30 + 1:02d}',
                    'author': f'Author {i}',
                    'tags': [f'tag_{k}' for k in range(5)]
                }
            }
        
        with open(large_json_file, 'w') as f:
            json.dump(large_data, f, indent=2)
        
        result = validate_json(large_json_file)
        self.assertTrue(result['valid'])
        self.assertIsNone(result['error'])
    
    def test_validate_complex_nested_structure(self):
        """Test validating complex nested JSON structures"""
        complex_file = self.temp_dir / "complex.json"
        
        complex_data = {
            "users": [
                {
                    "id": 1,
                    "name": "John Doe",
                    "email": "john@example.com",
                    "settings": {
                        "theme": "dark",
                        "notifications": {
                            "email": True,
                            "push": False,
                            "sms": None
                        }
                    },
                    "roles": ["admin", "user"]
                }
            ],
            "config": {
                "api": {
                    "version": "v1",
                    "endpoints": {
                        "users": "/api/v1/users",
                        "auth": "/api/v1/auth"
                    }
                }
            }
        }
        
        with open(complex_file, 'w') as f:
            json.dump(complex_data, f, indent=2)
        
        result = validate_json(complex_file)
        self.assertTrue(result['valid'])
        self.assertIsNone(result['error'])
    
    def test_validate_unicode_content(self):
        """Test validating JSON files with Unicode content"""
        unicode_file = self.temp_dir / "unicode.json"
        
        unicode_data = {
            "greetings": {
                "english": "Hello World!",
                "spanish": "¡Hola Mundo!",
                "chinese": "你好世界",
                "japanese": "こんにちは世界",
                "emoji": "👋 🌍 🎉",
                "special_chars": "àáâãäåæçèéêëìíîïñòóôõöùúûüý"
            }
        }
        
        with open(unicode_file, 'w', encoding='utf-8') as f:
            json.dump(unicode_data, f, indent=2, ensure_ascii=False)
        
        result = validate_json(unicode_file)
        self.assertTrue(result['valid'])
        self.assertIsNone(result['error'])
    
    def test_validate_nonexistent_file(self):
        """Test validating a file that doesn't exist"""
        nonexistent_file = self.temp_dir / "nonexistent.json"
        
        with self.assertRaises(FileNotFoundError) as context:
            validate_json(nonexistent_file)
        
        self.assertIn("FILE_NOT_FOUND", str(context.exception))
    
    def test_validate_json_return_format(self):
        """Test that validate_json returns the correct format"""
        # Valid file
        result = validate_json(self.sample_file)
        
        # Check required fields
        self.assertIn('valid', result)
        self.assertIn('file', result)
        self.assertIn('error', result)
        
        self.assertIsInstance(result['valid'], bool)
        self.assertIsInstance(result['file'], str)
        
        # Invalid file
        result = validate_json(self.invalid_file)
        
        self.assertIn('valid', result)
        self.assertIn('file', result)
        self.assertIn('error', result)
        self.assertIn('error_type', result)
        
        self.assertIsInstance(result['valid'], bool)
        self.assertIsInstance(result['file'], str)
        self.assertIsInstance(result['error'], dict)
        self.assertIn('message', result['error'])
        self.assertIn('line', result['error'])
    
    def test_validate_json_with_comments(self):
        """Test validating JSON with comments (should be invalid in strict JSON)"""
        json_with_comments_file = self.temp_dir / "with_comments.json"
        
        with open(json_with_comments_file, 'w') as f:
            f.write('''
            {
                // This is a comment
                "key": "value",
                /* This is a block comment */
                "another_key": "another_value"
            }
            ''')
        
        result = validate_json(json_with_comments_file)
        # Standard JSON doesn't allow comments
        self.assertFalse(result['valid'])
        self.assertEqual(result['error_type'], 'PARSE_ERROR')
    
    def test_validate_json_with_single_quotes(self):
        """Test validating JSON with single quotes (should be invalid)"""
        single_quotes_file = self.temp_dir / "single_quotes.json"
        
        with open(single_quotes_file, 'w') as f:
            f.write("{'key': 'value'}")  # Single quotes are not valid JSON
        
        result = validate_json(single_quotes_file)
        self.assertFalse(result['valid'])
        self.assertEqual(result['error_type'], 'PARSE_ERROR')
    
    def test_validate_json_error_line_reporting(self):
        """Test that validation reports accurate line numbers for errors"""
        multiline_error_file = self.temp_dir / "multiline_error.json"
        
        with open(multiline_error_file, 'w') as f:
            f.write('''{
    "line1": "value1",
    "line2": "value2",
    "line3": "value3"
    "line4": "value4"
}''')  # Missing comma after line3
        
        result = validate_json(multiline_error_file)
        self.assertFalse(result['valid'])
        self.assertEqual(result['error_type'], 'PARSE_ERROR')
        
        # Error should be around line 4 or 5
        self.assertGreaterEqual(result['error']['line'], 4)
        self.assertLessEqual(result['error']['line'], 5)
    
    def test_validate_json_performance_reporting(self):
        """Test that validation includes performance metrics (optional)"""
        result = validate_json(self.sample_file)
        
        # Performance metrics are optional but useful
        if 'performance' in result:
            self.assertIn('parse_time', result['performance'])
            self.assertIn('file_size', result['performance'])
            self.assertIsInstance(result['performance']['parse_time'], (int, float))
            self.assertIsInstance(result['performance']['file_size'], int)


def validate_json(file_path):
    """
    Mock implementation of validate_json for testing
    This would be replaced with the actual implementation
    """
    import time
    start_time = time.time()
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"FILE_NOT_FOUND: File {file_path} not found")
    
    # Get file size
    file_size = os.path.getsize(file_path)
    
    if file_size == 0:
        return {
            'valid': False,
            'file': str(file_path),
            'error_type': 'PARSE_ERROR',
            'error': {
                'message': 'File is empty',
                'line': 1,
                'column': 1
            },
            'performance': {
                'parse_time': time.time() - start_time,
                'file_size': file_size
            }
        }
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check for whitespace-only content
        if not content.strip():
            return {
                'valid': False,
                'file': str(file_path),
                'error_type': 'PARSE_ERROR',
                'error': {
                    'message': 'File contains only whitespace',
                    'line': 1,
                    'column': 1
                },
                'performance': {
                    'parse_time': time.time() - start_time,
                    'file_size': file_size
                }
            }
        
        # Try to parse the JSON
        json.loads(content)
        
        return {
            'valid': True,
            'file': str(file_path),
            'error': None,
            'performance': {
                'parse_time': time.time() - start_time,
                'file_size': file_size
            }
        }
        
    except json.JSONDecodeError as e:
        return {
            'valid': False,
            'file': str(file_path),
            'error_type': 'PARSE_ERROR',
            'error': {
                'message': str(e),
                'line': e.lineno,
                'column': e.colno
            },
            'performance': {
                'parse_time': time.time() - start_time,
                'file_size': file_size
            }
        }
    except Exception as e:
        return {
            'valid': False,
            'file': str(file_path),
            'error_type': 'UNKNOWN_ERROR',
            'error': {
                'message': str(e),
                'line': 0,
                'column': 0
            },
            'performance': {
                'parse_time': time.time() - start_time,
                'file_size': file_size
            }
        }


if __name__ == '__main__':
    unittest.main()