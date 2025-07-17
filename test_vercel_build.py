#!/usr/bin/env python3
"""
Vercel Build Process Simulator

This script simulates the Vercel build process to help debug deployment issues:
- Applies .vercelignore filters to see what files would be uploaded
- Tests ignore commands to predict build cancellations
- Validates essential files are present
- Checks for common deployment pitfalls

Usage:
    python test_vercel_build.py
    python test_vercel_build.py --test-ignore-command "exit 0"
    python test_vercel_build.py --verbose
"""

import os
import sys
import subprocess
import tempfile
import shutil
import fnmatch
import argparse
from pathlib import Path
from typing import List, Set, Tuple, Optional
import json


class VercelBuildSimulator:
    """Simulates Vercel build process for debugging deployment issues"""
    
    def __init__(self, repo_path: str = ".", verbose: bool = False):
        self.repo_path = Path(repo_path).resolve()
        self.verbose = verbose
        self.temp_dir = None
        
        # Essential files that must be present for deployment
        self.essential_files = {
            "api/app.py": "Main Flask application",
            "main.py": "Standalone script entry point", 
            "requirements.txt": "Python dependencies",
            "vercel.json": "Vercel configuration",
            "index.html": "Frontend entry point"
        }
        
        # Files that commonly cause issues if missing
        self.important_files = {
            "cloud_config.py": "Cloud configuration",
            "api/supervisor.py": "Agent supervisor",
            "api/agents/": "Agent directory",
            "api/database/": "Database modules",
            "api/notifications/": "Notification system"
        }
        
    def log(self, message: str, level: str = "INFO"):
        """Log messages with optional verbose mode"""
        if self.verbose or level in ["ERROR", "WARNING"]:
            print(f"[{level}] {message}")
    
    def run_command(self, cmd: List[str], cwd: Optional[str] = None, capture_output: bool = True) -> Tuple[int, str, str]:
        """Run a command and return exit code, stdout, stderr"""
        try:
            result = subprocess.run(
                cmd, 
                cwd=cwd or str(self.repo_path),
                capture_output=capture_output,
                text=True,
                timeout=30
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return 1, "", "Command timed out"
        except Exception as e:
            return 1, "", str(e)
    
    def clone_repo_to_temp(self) -> Optional[str]:
        """Clone current repo to temporary directory to simulate Vercel's process"""
        self.log("Creating temporary copy of repository...")
        
        self.temp_dir = tempfile.mkdtemp(prefix="vercel_build_test_")
        
        try:
            # Copy entire repository to temp directory
            shutil.copytree(self.repo_path, Path(self.temp_dir) / "repo", 
                          ignore=shutil.ignore_patterns('.git'))
            
            # Initialize git repo in temp directory for git operations
            repo_temp_path = Path(self.temp_dir) / "repo"
            self.run_command(["git", "init"], cwd=str(repo_temp_path))
            self.run_command(["git", "add", "."], cwd=str(repo_temp_path))
            self.run_command(["git", "commit", "-m", "Initial commit"], cwd=str(repo_temp_path))
            
            self.log(f"Repository copied to: {repo_temp_path}")
            return str(repo_temp_path)
            
        except Exception as e:
            self.log(f"Failed to clone repository: {e}", "ERROR")
            return None
    
    def load_vercelignore(self, repo_path: str) -> List[str]:
        """Load .vercelignore patterns"""
        vercelignore_path = Path(repo_path) / ".vercelignore"
        patterns = []
        
        if vercelignore_path.exists():
            with open(vercelignore_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        patterns.append(line)
            self.log(f"Loaded {len(patterns)} ignore patterns from .vercelignore")
        else:
            self.log("No .vercelignore file found", "WARNING")
        
        return patterns
    
    def should_ignore_file(self, file_path: str, patterns: List[str]) -> Tuple[bool, str]:
        """Check if file should be ignored based on patterns"""
        for pattern in patterns:
            # Handle directory patterns
            if pattern.endswith('/'):
                if file_path.startswith(pattern) or f"/{file_path}".startswith(f"/{pattern}"):
                    return True, pattern
            
            # Handle exact matches
            elif fnmatch.fnmatch(file_path, pattern):
                return True, pattern
                
            # Handle patterns with leading slash (root relative)
            elif pattern.startswith('/') and fnmatch.fnmatch(f"/{file_path}", pattern):
                return True, pattern
                
            # Handle glob patterns
            elif '*' in pattern or '?' in pattern:
                if fnmatch.fnmatch(file_path, pattern):
                    return True, pattern
        
        return False, ""
    
    def apply_vercelignore_filters(self, repo_path: str) -> Tuple[Set[str], Set[str]]:
        """Apply .vercelignore filters and return included/excluded files"""
        patterns = self.load_vercelignore(repo_path)
        
        included_files = set()
        excluded_files = set()
        
        for root, dirs, files in os.walk(repo_path):
            # Skip .git directory
            if '.git' in dirs:
                dirs.remove('.git')
            
            for file in files:
                file_path = Path(root) / file
                relative_path = file_path.relative_to(repo_path)
                relative_str = str(relative_path).replace('\\', '/')
                
                should_ignore, matching_pattern = self.should_ignore_file(relative_str, patterns)
                
                if should_ignore:
                    excluded_files.add(relative_str)
                    if matching_pattern:
                        self.log(f"Excluded: {relative_str} (pattern: {matching_pattern})")
                else:
                    included_files.add(relative_str)
        
        self.log(f"Files after .vercelignore: {len(included_files)} included, {len(excluded_files)} excluded")
        return included_files, excluded_files
    
    def check_essential_files(self, included_files: Set[str]) -> List[str]:
        """Check if essential files are present after filtering"""
        missing_files = []
        
        for file_path, description in self.essential_files.items():
            if file_path not in included_files:
                # Check if it's a directory requirement
                if file_path.endswith('/'):
                    has_files_in_dir = any(f.startswith(file_path) for f in included_files)
                    if not has_files_in_dir:
                        missing_files.append(f"{file_path} ({description})")
                else:
                    missing_files.append(f"{file_path} ({description})")
        
        return missing_files
    
    def test_ignore_command(self, repo_path: str, ignore_command: Optional[str] = None) -> Tuple[int, str]:
        """Test the ignore command to predict build cancellation"""
        if not ignore_command:
            self.log("No ignore command provided, builds will always run")
            return 1, "No ignore command (builds always run)"
        
        self.log(f"Testing ignore command: {ignore_command}")
        
        # Create a dummy commit to test against
        self.run_command(["git", "config", "user.email", "test@example.com"], cwd=repo_path)
        self.run_command(["git", "config", "user.name", "Test User"], cwd=repo_path)
        
        # Make a small change and commit
        test_file = Path(repo_path) / "test_change.txt"
        test_file.write_text("test change")
        self.run_command(["git", "add", "test_change.txt"], cwd=repo_path)
        self.run_command(["git", "commit", "-m", "Test change"], cwd=repo_path)
        
        # Run the ignore command
        exit_code, stdout, stderr = self.run_command(
            ["bash", "-c", ignore_command], 
            cwd=repo_path
        )
        
        # Clean up test file
        test_file.unlink(missing_ok=True)
        
        if exit_code == 0:
            return 0, f"BUILD WILL BE CANCELLED (exit code 0) - Command: {ignore_command}"
        else:
            return 1, f"BUILD WILL PROCEED (exit code {exit_code}) - Command: {ignore_command}"
    
    def validate_vercel_json(self, repo_path: str) -> List[str]:
        """Validate vercel.json configuration"""
        issues = []
        vercel_json_path = Path(repo_path) / "vercel.json"
        
        if not vercel_json_path.exists():
            issues.append("vercel.json file not found")
            return issues
        
        try:
            with open(vercel_json_path, 'r') as f:
                config = json.load(f)
            
            # Check for problematic configurations
            if config.get("ignoreCommand") == "exit 0":
                issues.append("ignoreCommand set to 'exit 0' - this will always cancel builds")
            
            # Check functions configuration
            functions = config.get("functions", {})
            if "api/app.py" not in functions:
                issues.append("api/app.py not configured in functions section")
            
            # Check for builds section
            builds = config.get("builds", [])
            if not builds:
                issues.append("No builds section found - may cause deployment issues")
            
            # Check install command
            install_cmd = config.get("installCommand", "")
            if "pip install" not in install_cmd:
                issues.append("installCommand doesn't include 'pip install' - Python dependencies may not be installed")
                
        except json.JSONDecodeError:
            issues.append("vercel.json is not valid JSON")
        except Exception as e:
            issues.append(f"Error reading vercel.json: {e}")
        
        return issues
    
    def run_full_simulation(self, ignore_command: Optional[str] = None) -> dict:
        """Run complete Vercel build simulation"""
        print("🚀 Starting Vercel Build Process Simulation")
        print("=" * 50)
        
        results = {
            "success": True,
            "issues": [],
            "warnings": [],
            "file_counts": {},
            "missing_files": [],
            "ignore_command_result": None
        }
        
        # Step 1: Clone repository
        temp_repo_path = self.clone_repo_to_temp()
        if not temp_repo_path:
            results["success"] = False
            results["issues"].append("Failed to create temporary repository copy")
            return results
        
        try:
            # Step 2: Apply .vercelignore filters
            print("\n📁 Applying .vercelignore filters...")
            included_files, excluded_files = self.apply_vercelignore_filters(temp_repo_path)
            
            results["file_counts"] = {
                "included": len(included_files),
                "excluded": len(excluded_files),
                "total": len(included_files) + len(excluded_files)
            }
            
            # Step 3: Check essential files
            print("\n🔍 Checking essential files...")
            missing_files = self.check_essential_files(included_files)
            results["missing_files"] = missing_files
            
            if missing_files:
                results["success"] = False
                results["issues"].extend([f"Missing essential file: {f}" for f in missing_files])
            
            # Step 4: Test ignore command
            if ignore_command:
                print(f"\n⚙️  Testing ignore command: {ignore_command}")
                exit_code, message = self.test_ignore_command(temp_repo_path, ignore_command)
                results["ignore_command_result"] = {
                    "exit_code": exit_code,
                    "message": message,
                    "will_cancel": exit_code == 0
                }
                
                if exit_code == 0:
                    results["issues"].append(message)
            
            # Step 5: Validate vercel.json
            print("\n📄 Validating vercel.json...")
            vercel_issues = self.validate_vercel_json(temp_repo_path)
            results["issues"].extend(vercel_issues)
            
            if vercel_issues:
                results["success"] = False
            
            # Step 6: Check for common issues
            print("\n🔧 Checking for common deployment issues...")
            
            # Check if requirements.txt exists and has content
            req_path = Path(temp_repo_path) / "requirements.txt"
            if req_path.exists():
                content = req_path.read_text().strip()
                if not content:
                    results["warnings"].append("requirements.txt is empty")
            
            # Check for Python cache files that might cause issues
            cache_files = [f for f in included_files if "__pycache__" in f or f.endswith(".pyc")]
            if cache_files:
                results["warnings"].append(f"Python cache files detected: {len(cache_files)} files")
            
        finally:
            # Cleanup
            if self.temp_dir:
                shutil.rmtree(self.temp_dir, ignore_errors=True)
        
        return results
    
    def print_results(self, results: dict):
        """Print simulation results in a formatted way"""
        print("\n" + "=" * 50)
        print("📊 SIMULATION RESULTS")
        print("=" * 50)
        
        # Overall status
        status = "✅ PASS" if results["success"] else "❌ FAIL"
        print(f"Overall Status: {status}")
        
        # File counts
        counts = results["file_counts"]
        print(f"\n📁 File Analysis:")
        print(f"   Total files: {counts.get('total', 0)}")
        print(f"   Included: {counts.get('included', 0)}")
        print(f"   Excluded: {counts.get('excluded', 0)}")
        
        # Issues
        if results["issues"]:
            print(f"\n❌ Issues Found ({len(results['issues'])}):")
            for issue in results["issues"]:
                print(f"   • {issue}")
        
        # Warnings  
        if results["warnings"]:
            print(f"\n⚠️  Warnings ({len(results['warnings'])}):")
            for warning in results["warnings"]:
                print(f"   • {warning}")
        
        # Missing files
        if results["missing_files"]:
            print(f"\n🚨 Missing Essential Files:")
            for file in results["missing_files"]:
                print(f"   • {file}")
        
        # Ignore command result
        if results["ignore_command_result"]:
            ignore_result = results["ignore_command_result"]
            status_icon = "🚫" if ignore_result["will_cancel"] else "✅"
            print(f"\n{status_icon} Ignore Command Test:")
            print(f"   {ignore_result['message']}")
        
        # Recommendations
        print(f"\n💡 Recommendations:")
        if not results["success"]:
            print("   • Fix the issues above before deploying")
            print("   • Check .vercelignore to ensure essential files aren't excluded")
            print("   • Validate vercel.json configuration")
        else:
            print("   • Simulation passed! Deploy should work correctly")
            print("   • Monitor actual deployment logs for any runtime issues")


def main():
    parser = argparse.ArgumentParser(description="Simulate Vercel build process")
    parser.add_argument("--test-ignore-command", type=str, 
                      help="Test specific ignore command (e.g., 'exit 0')")
    parser.add_argument("--verbose", action="store_true", 
                      help="Enable verbose logging")
    parser.add_argument("--repo-path", type=str, default=".",
                      help="Path to repository (default: current directory)")
    
    args = parser.parse_args()
    
    # Create simulator
    simulator = VercelBuildSimulator(args.repo_path, args.verbose)
    
    # Run simulation
    results = simulator.run_full_simulation(args.test_ignore_command)
    
    # Print results
    simulator.print_results(results)
    
    # Exit with appropriate code
    sys.exit(0 if results["success"] else 1)


if __name__ == "__main__":
    main() 