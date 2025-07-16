#!/usr/bin/env python3
"""
Test runner for Multi-Agent Portfolio Analysis System
Runs comprehensive tests for all agent tools and functionality
"""

import unittest
import sys
import os

def run_all_tests():
    """Run all tests in the test suite"""
    print("🧪 Running Multi-Agent Portfolio Analysis System Tests")
    print("=" * 60)
    
    # Add current directory to path
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    # Discover and run tests
    loader = unittest.TestLoader()
    start_dir = os.path.dirname(os.path.abspath(__file__))
    
    try:
        # Load tests from test_tools.py
        suite = loader.discover(start_dir, pattern='test_*.py')
        
        # Run tests with detailed output
        runner = unittest.TextTestRunner(
            verbosity=2,
            stream=sys.stdout,
            buffer=True
        )
        
        result = runner.run(suite)
        
        # Print summary
        print("\n" + "=" * 60)
        print("🧪 TEST SUMMARY")
        print("=" * 60)
        print(f"Tests run: {result.testsRun}")
        print(f"Failures: {len(result.failures)}")
        print(f"Errors: {len(result.errors)}")
        print(f"Skipped: {len(result.skipped)}")
        
        if result.failures:
            print("\n❌ FAILURES:")
            for test, traceback in result.failures:
                print(f"  • {test}: {traceback.split('AssertionError:')[-1].strip()}")
        
        if result.errors:
            print("\n💥 ERRORS:")
            for test, traceback in result.errors:
                print(f"  • {test}: {traceback.split('Exception:')[-1].strip()}")
        
        if result.wasSuccessful():
            print("\n✅ ALL TESTS PASSED!")
            return True
        else:
            print("\n❌ SOME TESTS FAILED!")
            return False
            
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False

def run_specific_test(test_class=None):
    """Run specific test class"""
    if test_class:
        print(f"🧪 Running {test_class} tests")
        print("=" * 40)
        
        # Import the test module
        import test_tools
        
        # Get the specific test class
        test_suite = unittest.TestLoader().loadTestsFromName(
            f'test_tools.{test_class}'
        )
        
        # Run the specific test
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(test_suite)
        
        return result.wasSuccessful()
    else:
        return run_all_tests()

def main():
    """Main function with command line options"""
    if len(sys.argv) > 1:
        test_class = sys.argv[1]
        success = run_specific_test(test_class)
    else:
        success = run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 