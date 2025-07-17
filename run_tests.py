#!/usr/bin/env python3
"""
Test Runner for Multi-Agent Portfolio Analysis System

Runs comprehensive tests with pre-test environment validation
and proper setup for the multi-agent system.
"""

import os
import sys
import unittest
import subprocess
from typing import Optional, List
from vercel_setup_check import VercelSetupChecker, check_for_testing


class TestRunner:
    """Comprehensive test runner with environment validation"""
    
    def __init__(self):
        self.setup_checker = VercelSetupChecker()
        self.test_modules = [
            'test_tools',
            'test_agents',
            'test_integration'
        ]
        
    def run_setup_check(self, skip_on_failure: bool = False) -> bool:
        """Run pre-test setup validation
        
        Args:
            skip_on_failure: If True, continue tests even if setup check fails
            
        Returns:
            bool: True if setup is valid, False otherwise
        """
        print("=" * 60)
        print("🔍 PRE-TEST ENVIRONMENT VALIDATION")
        print("=" * 60)
        
        is_ready = check_for_testing()
        
        if not is_ready:
            print("\n⚠️  Environment validation failed!")
            if skip_on_failure:
                print("⏭️  Continuing with tests (skip_on_failure=True)")
                print("Note: Some tests may fail due to missing environment variables")
                return True
            else:
                print("❌ Run 'python vercel_setup_check.py' for detailed information")
                print("Configure missing environment variables before running tests")
                return False
        
        print("✅ Environment validation passed!")
        return True
    
    def setup_test_environment(self) -> None:
        """Set up test environment with mock values"""
        print("\n🧪 Setting up test environment...")
        
        # Mock XAI_API_KEY for testing if not set
        if not os.getenv("XAI_API_KEY"):
            os.environ["XAI_API_KEY"] = "xai-test-key-for-unit-tests-only"
            print("  ✅ Set mock XAI_API_KEY for testing")
        
        # Mock email configuration for testing if not set
        if not os.getenv("SENDER_EMAIL"):
            os.environ["SENDER_EMAIL"] = "test@example.com"
            print("  ✅ Set mock SENDER_EMAIL for testing")
            
        if not os.getenv("SENDER_PASSWORD"):
            os.environ["SENDER_PASSWORD"] = "test-password"
            print("  ✅ Set mock SENDER_PASSWORD for testing")
            
        if not os.getenv("TO_EMAIL"):
            os.environ["TO_EMAIL"] = "recipient@example.com"
            print("  ✅ Set mock TO_EMAIL for testing")
        
        # Set other test environment variables
        os.environ["ENVIRONMENT"] = "testing"
        os.environ["DEBUG"] = "true"
        
        print("  ✅ Test environment configured")
    
    def discover_and_run_tests(self, test_pattern: Optional[str] = None) -> bool:
        """Discover and run tests
        
        Args:
            test_pattern: Optional pattern to filter tests
            
        Returns:
            bool: True if all tests pass, False otherwise
        """
        print("\n🧪 RUNNING TESTS")
        print("=" * 40)
        
        # Set up test discovery
        loader = unittest.TestLoader()
        suite = unittest.TestSuite()
        
        # Add tests from available modules
        for module_name in self.test_modules:
            try:
                module = __import__(module_name)
                module_suite = loader.loadTestsFromModule(module)
                suite.addTest(module_suite)
                print(f"  ✅ Loaded tests from {module_name}")
            except ImportError:
                print(f"  ⚠️  Module {module_name} not found, skipping")
            except Exception as e:
                print(f"  ❌ Error loading {module_name}: {e}")
        
        # Run tests with specific pattern if provided
        if test_pattern:
            print(f"\n🔍 Running tests matching pattern: {test_pattern}")
            suite = loader.loadTestsFromName(test_pattern)
        
        # Run the tests
        runner = unittest.TextTestRunner(verbosity=2, buffer=True)
        result = runner.run(suite)
        
        # Print summary
        print("\n" + "=" * 60)
        if result.wasSuccessful():
            print("🎉 ALL TESTS PASSED!")
            print(f"Ran {result.testsRun} tests successfully")
        else:
            print("❌ SOME TESTS FAILED")
            print(f"Tests run: {result.testsRun}")
            print(f"Failures: {len(result.failures)}")
            print(f"Errors: {len(result.errors)}")
            
            # Print failure details
            if result.failures:
                print("\nFailures:")
                for test, traceback in result.failures:
                    print(f"  - {test}: {traceback}")
                    
            if result.errors:
                print("\nErrors:")
                for test, traceback in result.errors:
                    print(f"  - {test}: {traceback}")
        
        print("=" * 60)
        return result.wasSuccessful()
    
    def run_specific_test_class(self, class_name: str) -> bool:
        """Run a specific test class
        
        Args:
            class_name: Name of the test class to run
            
        Returns:
            bool: True if tests pass, False otherwise
        """
        print(f"\n🎯 Running specific test class: {class_name}")
        return self.discover_and_run_tests(class_name)
    
    def run_all_tests(self, skip_setup_check: bool = False) -> bool:
        """Run all tests with full validation
        
        Args:
            skip_setup_check: Skip environment validation
            
        Returns:
            bool: True if all tests pass, False otherwise
        """
        # Run setup check unless skipped
        if not skip_setup_check:
            if not self.run_setup_check(skip_on_failure=True):
                return False
        
        # Setup test environment
        self.setup_test_environment()
        
        # Run all tests
        return self.discover_and_run_tests()


def main():
    """Main function to run tests with command line arguments"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Run tests for Multi-Agent Portfolio Analysis System")
    parser.add_argument("--skip-setup", action="store_true", help="Skip environment setup validation")
    parser.add_argument("--test-class", help="Run specific test class")
    parser.add_argument("--pattern", help="Run tests matching pattern")
    parser.add_argument("--setup-only", action="store_true", help="Only run setup check, no tests")
    
    args = parser.parse_args()
    
    runner = TestRunner()
    
    # Handle setup-only mode
    if args.setup_only:
        is_ready = runner.run_setup_check()
        return 0 if is_ready else 1
    
    # Handle specific test class
    if args.test_class:
        runner.setup_test_environment()
        success = runner.run_specific_test_class(args.test_class)
        return 0 if success else 1
    
    # Handle pattern matching
    if args.pattern:
        runner.setup_test_environment()
        success = runner.discover_and_run_tests(args.pattern)
        return 0 if success else 1
    
    # Run all tests
    success = runner.run_all_tests(skip_setup_check=args.skip_setup)
    return 0 if success else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 