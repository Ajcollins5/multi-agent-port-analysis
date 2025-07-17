#!/usr/bin/env python3
"""
Deployment Debug Script for Vercel
This script helps debug deployment issues by testing various endpoints and configurations.
"""

import os
import sys
import json
import requests
import subprocess
from datetime import datetime
from typing import Dict, Any, List, Optional

class DeploymentDebugger:
    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url or os.getenv('VERCEL_URL', 'http://localhost:5000')
        if not self.base_url.startswith('http'):
            self.base_url = f"https://{self.base_url}"
        
        self.test_results = []
        self.start_time = datetime.now()
        
    def log_test(self, test_name: str, success: bool, message: str, details: Optional[Dict[str, Any]] = None):
        """Log test results for debugging"""
        result = {
            'test': test_name,
            'success': success,
            'message': message,
            'details': details or {},
            'timestamp': datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅" if success else "❌"
        print(f"{status} {test_name}: {message}")
        
        if details:
            for key, value in details.items():
                print(f"   {key}: {value}")
    
    def test_vercel_config(self):
        """Test Vercel configuration"""
        try:
            with open('vercel.json', 'r') as f:
                config = json.load(f)
            
            # Check for required fields
            required_fields = ['functions', 'routes', 'ignoreCommand']
            missing_fields = [field for field in required_fields if field not in config]
            
            if missing_fields:
                self.log_test(
                    "Vercel Config",
                    False,
                    f"Missing required fields: {', '.join(missing_fields)}",
                    {'config': config}
                )
                return False
            
            # Check ignoreCommand
            if config.get('ignoreCommand') != 'exit 0':
                self.log_test(
                    "Vercel Config",
                    False,
                    f"ignoreCommand is not 'exit 0': {config.get('ignoreCommand')}",
                    {'ignoreCommand': config.get('ignoreCommand')}
                )
                return False
            
            # Check Python runtime versions
            python_versions = set()
            for func_name, func_config in config.get('functions', {}).items():
                if 'runtime' in func_config:
                    python_versions.add(func_config['runtime'])
            
            self.log_test(
                "Vercel Config",
                True,
                "Configuration is valid",
                {
                    'python_versions': list(python_versions),
                    'function_count': len(config.get('functions', {})),
                    'route_count': len(config.get('routes', []))
                }
            )
            return True
            
        except Exception as e:
            self.log_test(
                "Vercel Config",
                False,
                f"Error reading vercel.json: {str(e)}",
                {'error': str(e)}
            )
            return False
    
    def test_requirements(self):
        """Test Python requirements"""
        try:
            with open('requirements.txt', 'r') as f:
                requirements = f.read().strip()
            
            # Check for critical dependencies
            critical_deps = ['flask', 'yfinance', 'pandas', 'numpy', 'requests']
            missing_deps = []
            
            for dep in critical_deps:
                if dep not in requirements:
                    missing_deps.append(dep)
            
            if missing_deps:
                self.log_test(
                    "Python Requirements",
                    False,
                    f"Missing critical dependencies: {', '.join(missing_deps)}",
                    {'requirements': requirements}
                )
                return False
            
            # Count total dependencies
            lines = [line.strip() for line in requirements.split('\n') if line.strip() and not line.startswith('#')]
            
            self.log_test(
                "Python Requirements",
                True,
                "Requirements file is valid",
                {
                    'total_dependencies': len(lines),
                    'critical_deps_present': all(dep in requirements for dep in critical_deps)
                }
            )
            return True
            
        except Exception as e:
            self.log_test(
                "Python Requirements",
                False,
                f"Error reading requirements.txt: {str(e)}",
                {'error': str(e)}
            )
            return False
    
    def test_api_endpoints(self):
        """Test API endpoints"""
        endpoints = [
            '/api/health',
            '/api/portfolio',
            '/api/analysis',
            '/api/storage/stats'
        ]
        
        all_passed = True
        
        for endpoint in endpoints:
            try:
                url = f"{self.base_url}{endpoint}"
                response = requests.get(url, timeout=10)
                
                if response.status_code == 200:
                    self.log_test(
                        f"API {endpoint}",
                        True,
                        f"Response: {response.status_code}",
                        {'response_time': f"{response.elapsed.total_seconds():.2f}s"}
                    )
                else:
                    self.log_test(
                        f"API {endpoint}",
                        False,
                        f"HTTP {response.status_code}: {response.text[:100]}",
                        {'status_code': response.status_code}
                    )
                    all_passed = False
                    
            except Exception as e:
                self.log_test(
                    f"API {endpoint}",
                    False,
                    f"Connection error: {str(e)}",
                    {'error': str(e)}
                )
                all_passed = False
        
        return all_passed
    
    def test_git_status(self):
        """Test Git status for deployment"""
        try:
            # Check if we're in a git repository
            result = subprocess.run(['git', 'status', '--porcelain'], 
                                  capture_output=True, text=True)
            
            if result.returncode != 0:
                self.log_test(
                    "Git Status",
                    False,
                    "Not in a git repository",
                    {'error': result.stderr}
                )
                return False
            
            # Check for uncommitted changes
            if result.stdout.strip():
                self.log_test(
                    "Git Status",
                    False,
                    "Uncommitted changes detected",
                    {'changes': result.stdout}
                )
                return False
            
            # Check current branch
            branch_result = subprocess.run(['git', 'branch', '--show-current'], 
                                         capture_output=True, text=True)
            
            self.log_test(
                "Git Status",
                True,
                "Repository is clean",
                {'branch': branch_result.stdout.strip()}
            )
            return True
            
        except Exception as e:
            self.log_test(
                "Git Status",
                False,
                f"Error checking git status: {str(e)}",
                {'error': str(e)}
            )
            return False
    
    def test_environment_variables(self):
        """Test environment variables"""
        required_env_vars = [
            'XAI_API_KEY',
            'SMTP_SERVER',
            'SENDER_EMAIL',
            'TO_EMAIL'
        ]
        
        missing_vars = []
        present_vars = []
        
        for var in required_env_vars:
            if os.getenv(var):
                present_vars.append(var)
            else:
                missing_vars.append(var)
        
        if missing_vars:
            self.log_test(
                "Environment Variables",
                False,
                f"Missing required environment variables: {', '.join(missing_vars)}",
                {
                    'missing': missing_vars,
                    'present': present_vars
                }
            )
            return False
        
        self.log_test(
            "Environment Variables",
            True,
            "All required environment variables are present",
            {'variables': present_vars}
        )
        return True
    
    def run_all_tests(self):
        """Run all deployment tests"""
        print("🚀 Starting Deployment Debug Tests")
        print(f"📍 Testing URL: {self.base_url}")
        print("-" * 50)
        
        tests = [
            self.test_vercel_config,
            self.test_requirements,
            self.test_git_status,
            self.test_environment_variables,
            self.test_api_endpoints
        ]
        
        passed_tests = 0
        total_tests = len(tests)
        
        for test in tests:
            if test():
                passed_tests += 1
            print()  # Add spacing between tests
        
        # Summary
        print("=" * 50)
        print(f"🎯 Test Results: {passed_tests}/{total_tests} passed")
        
        if passed_tests == total_tests:
            print("✅ All tests passed! Ready for deployment.")
        else:
            print("❌ Some tests failed. Review the issues above.")
            
        # Save detailed results
        self.save_debug_report()
        
        return passed_tests == total_tests
    
    def save_debug_report(self):
        """Save detailed debug report"""
        report = {
            'timestamp': self.start_time.isoformat(),
            'base_url': self.base_url,
            'duration': (datetime.now() - self.start_time).total_seconds(),
            'results': self.test_results,
            'summary': {
                'total_tests': len(self.test_results),
                'passed': sum(1 for r in self.test_results if r['success']),
                'failed': sum(1 for r in self.test_results if not r['success'])
            }
        }
        
        with open('deployment_debug_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"📊 Detailed report saved to: deployment_debug_report.json")

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Debug Vercel deployment')
    parser.add_argument('--url', '-u', help='Base URL to test (default: VERCEL_URL env var)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    debugger = DeploymentDebugger(args.url)
    success = debugger.run_all_tests()
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main() 