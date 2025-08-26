"""
JsonMcpTool Test Suite

This package contains comprehensive tests for the JsonMcpTool MCP server.

Test Structure:
- unit/: Unit tests for individual operations
- integration/: Integration tests for combined operations
- performance/: Performance tests for large files
- fixtures/: Test data files

Running Tests:
- python tests/run_tests.py --all      # Run all tests
- python tests/run_tests.py --unit     # Run only unit tests
- python tests/run_tests.py --integration  # Run only integration tests
- python tests/run_tests.py --performance  # Run only performance tests

Individual Test Files:
- test_get_key.py: Tests for retrieving values by key path
- test_add_key.py: Tests for adding new key-value pairs
- test_update_key.py: Tests for updating existing keys
- test_rename_key.py: Tests for renaming keys
- test_remove_key.py: Tests for removing keys
- test_list_keys.py: Tests for listing keys at a path
- test_key_exists.py: Tests for checking key existence
- test_validate_json.py: Tests for JSON validation
- test_json_operations.py: Integration tests for combined operations
- test_performance.py: Performance tests for large files

Test Fixtures:
- sample_i18n.json: Sample I18Next translation file
- simple_test.json: Simple JSON with various data types
- empty.json: Empty JSON object
- invalid.json: Invalid JSON for error testing

Each test file includes mock implementations of the operations for testing purposes.
In the actual implementation, these would be replaced with the real MCP server operations.
"""