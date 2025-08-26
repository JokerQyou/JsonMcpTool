#!/usr/bin/env python3
"""
Test runner for JsonMcpTool test suite
Runs unit tests, integration tests, and performance tests
"""

import unittest
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def run_unit_tests():
    """Run all unit tests"""
    print("=" * 60)
    print("RUNNING UNIT TESTS")
    print("=" * 60)
    
    loader = unittest.TestLoader()
    suite = loader.discover('tests/unit', pattern='test_*.py')
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()

def run_integration_tests():
    """Run integration tests"""
    print("\\n" + "=" * 60)
    print("RUNNING INTEGRATION TESTS")
    print("=" * 60)
    
    loader = unittest.TestLoader()
    suite = loader.discover('tests/integration', pattern='test_*.py')
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()

def run_performance_tests():
    """Run performance tests"""
    print("\\n" + "=" * 60)
    print("RUNNING PERFORMANCE TESTS")
    print("=" * 60)
    
    loader = unittest.TestLoader()
    suite = loader.discover('tests/performance', pattern='test_*.py')
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()

def main():
    """Main test runner"""
    import argparse
    
    parser = argparse.ArgumentParser(description='JsonMcpTool Test Runner')
    parser.add_argument('--unit', action='store_true', help='Run only unit tests')
    parser.add_argument('--integration', action='store_true', help='Run only integration tests')
    parser.add_argument('--performance', action='store_true', help='Run only performance tests')
    parser.add_argument('--all', action='store_true', help='Run all tests (default)')
    
    args = parser.parse_args()
    
    # If no specific test type is requested, run all
    if not (args.unit or args.integration or args.performance):
        args.all = True
    
    success = True
    
    if args.unit or args.all:
        success &= run_unit_tests()
    
    if args.integration or args.all:
        success &= run_integration_tests()
    
    if args.performance or args.all:
        success &= run_performance_tests()
    
    print("\\n" + "=" * 60)
    if success:
        print("ALL TESTS PASSED ✓")
        sys.exit(0)
    else:
        print("SOME TESTS FAILED ✗")
        sys.exit(1)

if __name__ == '__main__':
    main()