#!/usr/bin/env python3

"""
Pre-deployment Check Script
Validates system configuration before Vercel deployment
"""

import os
import sys
import json
from pathlib import Path

def check_file_exists(file_path: str, description: str) -> bool:
    """Check if a file exists"""
    if os.path.exists(file_path):
        print(f"✅ {description}: {file_path}")
        return True
    else:
        print(f"❌ {description}: {file_path} (NOT FOUND)")
        return False

def check_vercel_config():
    """Check Vercel configuration"""
    print("🔍 Checking Vercel configuration...")
    
    if not check_file_exists("vercel.json", "Vercel config"):
        return False
    
    try:
        with open("vercel.json", "r") as f:
            config = json.load(f)
        
        # Check for conflicting properties
        if "builds" in config and "functions" in config:
            print("❌ ERROR: vercel.json contains both 'builds' and 'functions' properties")
            print("   This will cause deployment to fail. Please remove one of them.")
            return False
        
        # Check functions configuration
        if "functions" in config:
            functions = config["functions"]
            if "api/app.py" not in functions:
                print("❌ ERROR: Main API function (api/app.py) not configured")
                return False
            
            print(f"✅ {len(functions)} serverless functions configured")
        
        # Check rewrites
        if "rewrites" in config:
            rewrites = config["rewrites"]
            api_rewrite = any(r.get("source") == "/api/(.*)" for r in rewrites)
            if not api_rewrite:
                print("❌ ERROR: API rewrite rule not found")
                return False
            print("✅ API routing configured")
        
        print("✅ Vercel configuration is valid")
        return True
        
    except json.JSONDecodeError:
        print("❌ ERROR: vercel.json is not valid JSON")
        return False
    except Exception as e:
        print(f"❌ ERROR: Failed to validate vercel.json: {e}")
        return False

def check_python_files():
    """Check Python files and dependencies"""
    print("\n🐍 Checking Python files...")
    
    checks = [
        ("requirements.txt", "Python dependencies"),
        ("api/app.py", "Main API handler"),
        ("api/supervisor.py", "Supervisor agent"),
        ("api/config/env_validator.py", "Environment validator"),
                    ("api/database/supabase_manager.py", "Supabase database manager"),
        ("api/agents/risk_agent.py", "Risk agent"),
        ("api/agents/news_agent.py", "News agent"),
        ("api/agents/event_sentinel.py", "Event sentinel"),
        ("api/agents/knowledge_curator.py", "Knowledge curator"),
        ("api/notifications/email_handler.py", "Email handler"),
        ("api/scheduler/cron_handler.py", "Cron handler")
    ]
    
    all_exist = True
    for file_path, description in checks:
        if not check_file_exists(file_path, description):
            all_exist = False
    
    return all_exist

def check_environment_vars():
    """Check environment variables"""
    print("\n🔧 Checking environment variables...")
    
    # Add project root to path
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'api'))
    
    try:
        from config.env_validator import validate_environment
        
        results = validate_environment()
        
        if results["success"]:
            print("✅ Environment validation passed")
            print(f"   Required variables: {results['required_valid']}")
            print(f"   Optional variables: {results['optional_valid']}")
            
            if results["warnings"]:
                print("⚠️  Warnings:")
                for warning in results["warnings"]:
                    print(f"   - {warning['variable']}: {warning['warning']}")
            
            return True
        else:
            print("❌ Environment validation failed:")
            for error in results["errors"]:
                print(f"   - {error['variable']}: {error['error']}")
            return False
            
    except ImportError as e:
        print(f"❌ ERROR: Cannot import environment validator: {e}")
        return False
    except Exception as e:
        print(f"❌ ERROR: Environment validation failed: {e}")
        return False

def check_deployment_readiness():
    """Check if deployment is ready"""
    print("\n🚀 Checking deployment readiness...")
    
    # Check if we're in a git repository
    if os.path.exists(".git"):
        print("✅ Git repository detected")
        
        # Check if there are uncommitted changes
        import subprocess
        try:
            result = subprocess.run(["git", "status", "--porcelain"], 
                                  capture_output=True, text=True)
            if result.stdout.strip():
                print("⚠️  Warning: You have uncommitted changes")
                print("   Consider committing your changes before deployment")
            else:
                print("✅ No uncommitted changes")
        except Exception:
            print("⚠️  Warning: Could not check git status")
    else:
        print("⚠️  Warning: Not a git repository")
    
    # Check if Vercel CLI is available
    try:
        import subprocess
        result = subprocess.run(["vercel", "--version"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Vercel CLI available: {result.stdout.strip()}")
            return True
        else:
            print("❌ Vercel CLI not found")
            print("   Install with: npm install -g vercel")
            return False
    except Exception:
        print("❌ Vercel CLI not available")
        return False

def main():
    """Main check function"""
    print("🔍 Pre-deployment System Check")
    print("=" * 50)
    
    checks = [
        check_vercel_config,
        check_python_files,
        check_environment_vars,
        check_deployment_readiness
    ]
    
    all_passed = True
    for check in checks:
        if not check():
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All checks passed! Ready for deployment.")
        print("\nTo deploy, run:")
        print("  ./scripts/deploy.sh")
        print("  or")
        print("  vercel --prod")
        sys.exit(0)
    else:
        print("❌ Some checks failed. Please fix the issues before deployment.")
        sys.exit(1)

if __name__ == "__main__":
    main() 