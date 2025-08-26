import unittest
import json
import tempfile
import os
import shutil
import time
import sys
from pathlib import Path

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

class TestPerformance(unittest.TestCase):
    """Performance tests for JSON operations on large files"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = Path(tempfile.mkdtemp())
        
        # Create different sized test files
        self.small_file = self.temp_dir / "small_1kb.json"
        self.medium_file = self.temp_dir / "medium_100kb.json"  
        self.large_file = self.temp_dir / "large_1mb.json"
        self.xlarge_file = self.temp_dir / "xlarge_10mb.json"
        
        self._create_test_files()
    
    def tearDown(self):
        """Clean up temporary files"""
        shutil.rmtree(self.temp_dir)
    
    def _create_test_files(self):
        """Create test files of various sizes"""
        
        # Small file (~1KB) - 50 translations
        small_data = {}
        for i in range(50):
            small_data[f'key_{i}'] = f'Translation value {i}'
        
        with open(self.small_file, 'w') as f:
            json.dump(small_data, f, indent=2)
        
        # Medium file (~100KB) - nested structure with ~2000 translations
        medium_data = {}
        for section in range(20):
            section_name = f'section_{section}'
            medium_data[section_name] = {}
            
            for subsection in range(10):
                subsection_name = f'subsection_{subsection}'
                medium_data[section_name][subsection_name] = {}
                
                for item in range(10):
                    key = f'item_{item}'
                    value = f'Translation for {section_name}.{subsection_name}.{key} with some longer text to increase file size'
                    medium_data[section_name][subsection_name][key] = value
        
        with open(self.medium_file, 'w') as f:
            json.dump(medium_data, f, indent=2)
        
        # Large file (~1MB) - deeply nested with ~10,000 translations
        large_data = {}
        for namespace in range(50):
            namespace_name = f'namespace_{namespace}'
            large_data[namespace_name] = {}
            
            for section in range(20):
                section_name = f'section_{section}'
                large_data[namespace_name][section_name] = {}
                
                for subsection in range(10):
                    subsection_name = f'subsection_{subsection}'
                    large_data[namespace_name][section_name][subsection_name] = {}
                    
                    # Add various types of translation data
                    for item in range(10):
                        key = f'item_{item}'
                        
                        # Mix of simple strings and complex interpolation
                        if item % 3 == 0:
                            value = f'Simple translation for {key}'
                        elif item % 3 == 1:
                            value = f'Translation with {{interpolation}} for {key} and {{count}} items'
                        else:
                            value = {
                                'singular': f'One {key}',
                                'plural': f'{{count}} {key}s',
                                'description': f'Description for {key} with additional context information'
                            }
                        
                        large_data[namespace_name][section_name][subsection_name][key] = value
        
        with open(self.large_file, 'w') as f:
            json.dump(large_data, f, indent=2)
        
        # Extra large file (~10MB) - extremely nested structure
        xlarge_data = {}
        for root in range(10):
            root_name = f'root_{root}'
            xlarge_data[root_name] = {}
            
            for namespace in range(50):
                namespace_name = f'namespace_{namespace}'
                xlarge_data[root_name][namespace_name] = {}
                
                for section in range(20):
                    section_name = f'section_{section}'
                    xlarge_data[root_name][namespace_name][section_name] = {}
                    
                    for subsection in range(10):
                        subsection_name = f'subsection_{subsection}'
                        xlarge_data[root_name][namespace_name][section_name][subsection_name] = {}
                        
                        for item in range(10):
                            key = f'item_{item}'
                            
                            # Create verbose translation data
                            value = {
                                'short': f'Short {key}',
                                'long': f'This is a much longer translation text for {key} that includes detailed explanations and context information to make the file larger',
                                'metadata': {
                                    'created': f'2023-01-{(item % 30) + 1:02d}',
                                    'author': f'Translator {item}',
                                    'reviewed': item % 5 == 0,
                                    'tags': [f'tag_{j}' for j in range(3)],
                                    'notes': f'Additional notes and context for {key} translation'
                                },
                                'variations': {
                                    'formal': f'Formal version of {key}',
                                    'informal': f'Informal version of {key}',
                                    'technical': f'Technical terminology for {key}'
                                }
                            }
                            
                            xlarge_data[root_name][namespace_name][section_name][subsection_name][key] = value
        
        with open(self.xlarge_file, 'w') as f:
            json.dump(xlarge_data, f, indent=2)
    
    def _measure_operation_time(self, operation_func):
        """Measure the execution time of an operation"""
        start_time = time.time()
        result = operation_func()
        end_time = time.time()
        return result, end_time - start_time
    
    def test_get_key_performance(self):
        """Test get_key performance across different file sizes"""
        test_cases = [
            (self.small_file, 'key_25', 'Small file'),
            (self.medium_file, 'section_10.subsection_5.item_7', 'Medium file'),
            (self.large_file, 'namespace_25.section_10.subsection_5.item_7', 'Large file'),
            (self.xlarge_file, 'root_5.namespace_25.section_10.subsection_5.item_7', 'XLarge file')
        ]
        
        performance_results = {}
        
        for file_path, key_path, description in test_cases:
            # Test existing key
            _, exec_time = self._measure_operation_time(
                lambda: get_key(file_path, key_path)
            )
            
            performance_results[description] = exec_time
            
            # Performance assertions
            if 'Small' in description:
                self.assertLess(exec_time, 0.1, f"get_key on {description} took too long: {exec_time}s")
            elif 'Medium' in description:
                self.assertLess(exec_time, 0.5, f"get_key on {description} took too long: {exec_time}s")
            elif 'Large' in description:
                self.assertLess(exec_time, 2.0, f"get_key on {description} took too long: {exec_time}s")
            else:  # XLarge
                self.assertLess(exec_time, 10.0, f"get_key on {description} took too long: {exec_time}s")
        
        print(f"\\nget_key Performance Results:")
        for desc, time_taken in performance_results.items():
            print(f"  {desc}: {time_taken:.4f}s")
    
    def test_add_key_performance(self):
        """Test add_key performance and memory efficiency"""
        # Create working copies
        test_files = [
            (self.temp_dir / "work_small.json", self.small_file, "Small file"),
            (self.temp_dir / "work_medium.json", self.medium_file, "Medium file"),
            (self.temp_dir / "work_large.json", self.large_file, "Large file")
            # Skip xlarge for add operations to keep test time reasonable
        ]
        
        performance_results = {}
        
        for work_file, source_file, description in test_files:
            shutil.copy2(source_file, work_file)
            
            # Measure add_key performance
            _, exec_time = self._measure_operation_time(
                lambda: add_key(work_file, f'performance_test.new_key', 'Performance test value')
            )
            
            performance_results[description] = exec_time
            
            # Performance assertions
            if 'Small' in description:
                self.assertLess(exec_time, 0.1)
            elif 'Medium' in description:
                self.assertLess(exec_time, 1.0)
            else:  # Large
                self.assertLess(exec_time, 5.0)
            
            # Verify the operation completed successfully
            self.assertTrue(key_exists(work_file, 'performance_test.new_key'))
        
        print(f"\\nadd_key Performance Results:")
        for desc, time_taken in performance_results.items():
            print(f"  {desc}: {time_taken:.4f}s")
    
    def test_update_key_performance(self):
        """Test update_key performance"""
        test_cases = [
            (self.medium_file, 'section_5.subsection_3.item_2', 'Medium file'),
            (self.large_file, 'namespace_10.section_5.subsection_3.item_2', 'Large file')
        ]
        
        performance_results = {}
        
        for source_file, key_path, description in test_cases:
            # Create working copy
            work_file = self.temp_dir / f"update_work_{description.replace(' ', '_').lower()}.json"
            shutil.copy2(source_file, work_file)
            
            # Measure update performance
            _, exec_time = self._measure_operation_time(
                lambda: update_key(work_file, key_path, 'Updated performance test value')
            )
            
            performance_results[description] = exec_time
            
            # Performance assertions
            if 'Medium' in description:
                self.assertLess(exec_time, 1.0)
            else:  # Large
                self.assertLess(exec_time, 5.0)
        
        print(f"\\nupdate_key Performance Results:")
        for desc, time_taken in performance_results.items():
            print(f"  {desc}: {time_taken:.4f}s")
    
    def test_list_keys_performance(self):
        """Test list_keys performance at different nesting levels"""
        test_cases = [
            (self.medium_file, None, 'Medium file - root level'),
            (self.medium_file, 'section_10', 'Medium file - nested level'),
            (self.large_file, None, 'Large file - root level'),
            (self.large_file, 'namespace_20.section_10', 'Large file - nested level'),
            (self.xlarge_file, None, 'XLarge file - root level'),
            (self.xlarge_file, 'root_3.namespace_20', 'XLarge file - nested level')
        ]
        
        performance_results = {}
        
        for file_path, key_path, description in test_cases:
            # Measure list_keys performance
            result, exec_time = self._measure_operation_time(
                lambda: list_keys(file_path, key_path)
            )
            
            performance_results[description] = {
                'time': exec_time,
                'key_count': len(result)
            }
            
            # Performance assertions based on expected key count
            if 'root level' in description:
                if 'Small' in description or 'Medium' in description:
                    self.assertLess(exec_time, 0.5)
                elif 'Large' in description:
                    self.assertLess(exec_time, 2.0)
                else:  # XLarge
                    self.assertLess(exec_time, 10.0)
            else:  # nested level
                self.assertLess(exec_time, 1.0)
        
        print(f"\\nlist_keys Performance Results:")
        for desc, metrics in performance_results.items():
            print(f"  {desc}: {metrics['time']:.4f}s ({metrics['key_count']} keys)")
    
    def test_key_exists_performance(self):
        """Test key_exists performance vs get_key for existence checks"""
        test_file = self.large_file
        test_keys = [
            'namespace_10.section_5.subsection_3.item_2',  # exists
            'namespace_10.section_5.subsection_3.item_999',  # doesn't exist
            'namespace_999.section_5.subsection_3.item_2',  # parent doesn't exist
        ]
        
        print(f"\\nkey_exists vs get_key Performance Comparison:")
        
        for key_path in test_keys:
            # Measure key_exists performance
            exists_result, exists_time = self._measure_operation_time(
                lambda: key_exists(test_file, key_path)
            )
            
            # Measure get_key performance for comparison
            try:
                get_result, get_time = self._measure_operation_time(
                    lambda: get_key(test_file, key_path)
                )
                get_success = True
            except (KeyError, ValueError):
                get_time = None
                get_success = False
            
            # Verify consistency
            if get_success:
                self.assertTrue(exists_result, f"key_exists returned False but get_key succeeded for {key_path}")
            else:
                self.assertFalse(exists_result, f"key_exists returned True but get_key failed for {key_path}")
            
            print(f"  {key_path[:50]}...")
            print(f"    key_exists: {exists_time:.4f}s (result: {exists_result})")
            if get_time:
                print(f"    get_key: {get_time:.4f}s")
                speedup = get_time / exists_time if exists_time > 0 else float('inf')
                print(f"    Speedup: {speedup:.2f}x")
    
    def test_validate_json_performance(self):
        """Test JSON validation performance on large files"""
        test_files = [
            (self.small_file, "Small file"),
            (self.medium_file, "Medium file"), 
            (self.large_file, "Large file"),
            (self.xlarge_file, "XLarge file")
        ]
        
        performance_results = {}
        
        for file_path, description in test_files:
            # Measure validation performance
            result, exec_time = self._measure_operation_time(
                lambda: validate_json(file_path)
            )
            
            file_size = os.path.getsize(file_path)
            performance_results[description] = {
                'time': exec_time,
                'size_mb': file_size / (1024 * 1024),
                'valid': result['valid']
            }
            
            # All test files should be valid
            self.assertTrue(result['valid'])
            
            # Performance assertions based on file size
            size_mb = file_size / (1024 * 1024)
            expected_max_time = max(0.1, size_mb * 2)  # Allow 2 seconds per MB
            self.assertLess(exec_time, expected_max_time, 
                           f"Validation of {description} took too long: {exec_time}s for {size_mb:.2f}MB")
        
        print(f"\\nvalidate_json Performance Results:")
        for desc, metrics in performance_results.items():
            print(f"  {desc}: {metrics['time']:.4f}s ({metrics['size_mb']:.2f}MB)")
    
    def test_bulk_operations_performance(self):
        """Test performance of bulk operations"""
        # Create a working copy of medium file for bulk testing
        work_file = self.temp_dir / "bulk_operations.json"
        shutil.copy2(self.medium_file, work_file)
        
        # Test bulk additions
        bulk_keys = [f'bulk_test.batch_{i}.item_{j}' for i in range(10) for j in range(10)]
        
        start_time = time.time()
        for key_path in bulk_keys:
            add_key(work_file, key_path, f'Bulk value for {key_path}')
        bulk_add_time = time.time() - start_time
        
        # Test bulk updates
        start_time = time.time()
        for key_path in bulk_keys:
            update_key(work_file, key_path, f'Updated bulk value for {key_path}')
        bulk_update_time = time.time() - start_time
        
        # Test bulk removals
        start_time = time.time()
        for key_path in bulk_keys:
            remove_key(work_file, key_path)
        bulk_remove_time = time.time() - start_time
        
        operations_count = len(bulk_keys)
        
        print(f"\\nBulk Operations Performance ({operations_count} operations):")
        print(f"  Bulk add: {bulk_add_time:.4f}s ({bulk_add_time/operations_count*1000:.2f}ms per operation)")
        print(f"  Bulk update: {bulk_update_time:.4f}s ({bulk_update_time/operations_count*1000:.2f}ms per operation)")
        print(f"  Bulk remove: {bulk_remove_time:.4f}s ({bulk_remove_time/operations_count*1000:.2f}ms per operation)")
        
        # Performance assertions
        self.assertLess(bulk_add_time/operations_count, 0.1, "Bulk add operations too slow")
        self.assertLess(bulk_update_time/operations_count, 0.1, "Bulk update operations too slow") 
        self.assertLess(bulk_remove_time/operations_count, 0.1, "Bulk remove operations too slow")
    
    def test_memory_usage_large_files(self):
        """Test that operations don't consume excessive memory with large files"""
        # This is a basic test - in real implementation, you'd use memory profiling tools
        
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Perform operations on the largest file
        test_operations = [
            lambda: get_key(self.xlarge_file, 'root_3.namespace_20.section_10.subsection_5.item_7'),
            lambda: key_exists(self.xlarge_file, 'root_3.namespace_20.section_999'),
            lambda: list_keys(self.xlarge_file, 'root_3.namespace_20'),
            lambda: validate_json(self.xlarge_file)
        ]
        
        max_memory_increase = 0
        
        for operation in test_operations:
            before_memory = process.memory_info().rss / 1024 / 1024
            operation()
            after_memory = process.memory_info().rss / 1024 / 1024
            
            memory_increase = after_memory - initial_memory
            max_memory_increase = max(max_memory_increase, memory_increase)
        
        print(f"\\nMemory Usage:")
        print(f"  Initial memory: {initial_memory:.2f}MB")
        print(f"  Max memory increase: {max_memory_increase:.2f}MB")
        
        # Memory usage should be reasonable (less than 500MB increase for 10MB file)
        self.assertLess(max_memory_increase, 500, 
                       f"Excessive memory usage: {max_memory_increase:.2f}MB increase")
    
    def test_file_size_reporting(self):
        """Test and report actual file sizes for reference"""
        files = [
            (self.small_file, "Small test file"),
            (self.medium_file, "Medium test file"),
            (self.large_file, "Large test file"),
            (self.xlarge_file, "Extra large test file")
        ]
        
        print(f"\\nTest File Sizes:")
        for file_path, description in files:
            size_bytes = os.path.getsize(file_path)
            size_kb = size_bytes / 1024
            size_mb = size_kb / 1024
            
            print(f"  {description}: {size_bytes:,} bytes ({size_kb:.1f}KB, {size_mb:.1f}MB)")


if __name__ == '__main__':
    # Run with verbose output to see performance metrics
    unittest.main(verbosity=2)