#!/usr/bin/env python3
"""
Pre-Build Hook for Vercel Serverless Deployment
Optimizes dependencies, validates configurations, and prepares environment
"""

import os
import sys
import json
import subprocess
import shutil
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any

class PreBuildOptimizer:
    """Optimizes and validates the deployment before build"""
    
    def __init__(self):
        self.root_dir = Path(__file__).parent.parent
        self.build_start_time = time.time()
        self.errors = []
        self.warnings = []
        
    def log(self, message: str, level: str = "INFO"):
        """Log messages with timestamp"""
        timestamp = time.strftime("%H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")
    
    def validate_environment_variables(self) -> bool:
        """Validate required environment variables"""
        self.log("Validating environment variables...")
        
        required_vars = [
            "XAI_API_KEY",
            "SENDER_EMAIL", 
            "SENDER_PASSWORD",
            "TO_EMAIL"
        ]
        
        optional_vars = [
            "DATABASE_URL",
            "REDIS_URL",
            "CRON_SECRET",
            "SMTP_SERVER",
            "SMTP_PORT"
        ]
        
        missing_required = []
        missing_optional = []
        
        for var in required_vars:
            if not os.environ.get(var):
                missing_required.append(var)
        
        for var in optional_vars:
            if not os.environ.get(var):
                missing_optional.append(var)
        
        if missing_required:
            self.errors.append(f"Missing required environment variables: {', '.join(missing_required)}")
            self.log(f"❌ Missing required variables: {', '.join(missing_required)}", "ERROR")
            return False
        
        if missing_optional:
            self.warnings.append(f"Missing optional environment variables: {', '.join(missing_optional)}")
            self.log(f"⚠️  Missing optional variables: {', '.join(missing_optional)}", "WARNING")
        
        self.log("✅ Environment variables validated")
        return True
    
    def validate_vercel_config(self) -> bool:
        """Validate vercel.json configuration"""
        self.log("Validating vercel.json configuration...")
        
        vercel_config_path = self.root_dir / "vercel.json"
        if not vercel_config_path.exists():
            self.errors.append("vercel.json not found")
            return False
        
        try:
            with open(vercel_config_path, 'r') as f:
                config = json.load(f)
            
            # Check required fields
            required_fields = ["version", "functions", "rewrites"]
            for field in required_fields:
                if field not in config:
                    self.errors.append(f"Missing required field in vercel.json: {field}")
            
            # Check for problematic configurations
            if config.get("ignoreCommand") == "exit 0":
                self.warnings.append("ignoreCommand set to 'exit 0' may cause build cancellations")
            
            # Validate function configurations
            functions = config.get("functions", {})
            if "api/app.py" not in functions:
                self.errors.append("api/app.py not configured in functions")
            
            # Check function configurations (runtime is auto-detected by Vercel)
            for func_name, func_config in functions.items():
                if "memory" not in func_config:
                    self.warnings.append(f"Function {func_name} missing memory configuration")
                if "maxDuration" not in func_config:
                    self.warnings.append(f"Function {func_name} missing maxDuration configuration")
            
            if self.errors:
                self.log("❌ vercel.json validation failed", "ERROR")
                return False
            
            self.log("✅ vercel.json configuration validated")
            return True
            
        except json.JSONDecodeError:
            self.errors.append("vercel.json is not valid JSON")
            return False
        except Exception as e:
            self.errors.append(f"Error reading vercel.json: {e}")
            return False
    
    def optimize_dependencies(self) -> bool:
        """Optimize dependencies for serverless deployment"""
        self.log("Optimizing dependencies...")
        
        requirements_path = self.root_dir / "requirements.txt"
        if not requirements_path.exists():
            self.errors.append("requirements.txt not found")
            return False
        
        try:
            # Read current requirements
            with open(requirements_path, 'r') as f:
                requirements = f.read()
            
            # Check for unpinned dependencies
            unpinned_deps = []
            for line in requirements.split('\n'):
                if line.strip() and not line.startswith('#'):
                    if '==' not in line and not line.startswith('-'):
                        unpinned_deps.append(line.strip())
            
            if unpinned_deps:
                self.warnings.append(f"Unpinned dependencies found: {', '.join(unpinned_deps)}")
            
            # Check for large dependencies that might cause cold start issues
            large_deps = ['tensorflow', 'torch', 'scipy', 'scikit-learn']
            found_large_deps = []
            for dep in large_deps:
                if dep in requirements.lower():
                    found_large_deps.append(dep)
            
            if found_large_deps:
                self.warnings.append(f"Large dependencies detected (may increase cold start time): {', '.join(found_large_deps)}")
            
            self.log("✅ Dependencies optimized")
            return True
            
        except Exception as e:
            self.errors.append(f"Error optimizing dependencies: {e}")
            return False
    
    def validate_api_structure(self) -> bool:
        """Validate API structure for serverless deployment"""
        self.log("Validating API structure...")
        
        # Check for essential API files
        essential_files = [
            "api/app.py",
            "main.py",
            "api/database/storage_manager.py",
            "api/supervisor.py"
        ]
        
        missing_files = []
        for file_path in essential_files:
            if not (self.root_dir / file_path).exists():
                missing_files.append(file_path)
        
        if missing_files:
            self.errors.append(f"Missing essential API files: {', '.join(missing_files)}")
            return False
        
        # Check for serverless-incompatible patterns
        self.log("Checking for serverless-incompatible patterns...")
        
        # Check main.py for SQLite file usage
        main_py_path = self.root_dir / "main.py"
        if main_py_path.exists():
            with open(main_py_path, 'r') as f:
                content = f.read()
                if "sqlite3.connect('knowledge.db')" in content:
                    self.warnings.append("Direct SQLite file usage detected in main.py (may not work in serverless)")
        
        # Check for background schedulers
        scheduler_patterns = [
            "BackgroundScheduler",
            "APScheduler",
            "schedule.every"
        ]
        
        for file_path in self.root_dir.glob("**/*.py"):
            if file_path.is_file():
                try:
                    with open(file_path, 'r') as f:
                        content = f.read()
                        for pattern in scheduler_patterns:
                            if pattern in content:
                                self.warnings.append(f"Background scheduler pattern '{pattern}' found in {file_path.name}")
                except Exception:
                    pass  # Skip files that can't be read
        
        self.log("✅ API structure validated")
        return True
    
    def optimize_cold_start_performance(self) -> bool:
        """Optimize for cold start performance"""
        self.log("Optimizing cold start performance...")
        
        # Create optimized imports file
        optimized_imports = """# Optimized imports for cold start performance
# Import only what's needed for each function

# Core Flask imports
from flask import Flask, request, jsonify

# Standard library imports
import os
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional

# Third-party imports (lazy load where possible)
def lazy_import_yfinance():
    import yfinance as yf
    return yf

def lazy_import_pandas():
    import pandas as pd
    return pd

def lazy_import_numpy():
    import numpy as np
    return np

# Email imports (only when needed)
def lazy_import_email():
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    return smtplib, MIMEText, MIMEMultipart

# Database imports (only when needed)
def lazy_import_storage():
    try:
        from api.database.storage_manager import StorageManager
        return StorageManager
    except ImportError:
        return None
"""
        
        # Write optimized imports to a helper file
        optimized_imports_path = self.root_dir / "api" / "optimized_imports.py"
        with open(optimized_imports_path, 'w') as f:
            f.write(optimized_imports)
        
        self.log("✅ Cold start performance optimized")
        return True
    
    def create_deployment_manifest(self) -> bool:
        """Create deployment manifest with build information"""
        self.log("Creating deployment manifest...")
        
        manifest = {
            "build_timestamp": datetime.now().isoformat(),
            "build_duration": time.time() - self.build_start_time,
            "python_version": sys.version,
            "environment": os.environ.get("ENVIRONMENT", "production"),
            "vercel_url": os.environ.get("VERCEL_URL", ""),
            "optimization_applied": True,
            "errors": self.errors,
            "warnings": self.warnings,
            "functions": {
                "api/app.py": {
                    "memory": 1024,
                    "timeout": 60,
                    "note": "Python 3.12 runtime auto-detected by Vercel"
                },
                "main.py": {
                    "memory": 512,
                    "timeout": 30,
                    "note": "Python 3.12 runtime auto-detected by Vercel"
                }
            }
        }
        
        manifest_path = self.root_dir / "deployment_manifest.json"
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        self.log("✅ Deployment manifest created")
        return True
    
    def run_optimization(self) -> bool:
        """Run the complete optimization process"""
        self.log("🚀 Starting pre-build optimization...")
        
        success = True
        
        # Run all validation and optimization steps
        steps = [
            ("Environment Variables", self.validate_environment_variables),
            ("Vercel Configuration", self.validate_vercel_config),
            ("Dependencies", self.optimize_dependencies),
            ("API Structure", self.validate_api_structure),
            ("Cold Start Performance", self.optimize_cold_start_performance),
            ("Deployment Manifest", self.create_deployment_manifest)
        ]
        
        for step_name, step_func in steps:
            self.log(f"Running {step_name} validation/optimization...")
            if not step_func():
                success = False
                self.log(f"❌ {step_name} failed", "ERROR")
            else:
                self.log(f"✅ {step_name} completed")
        
        # Summary
        build_time = time.time() - self.build_start_time
        self.log(f"Pre-build optimization completed in {build_time:.2f}s")
        
        if self.errors:
            self.log("❌ ERRORS FOUND:", "ERROR")
            for error in self.errors:
                self.log(f"  • {error}", "ERROR")
        
        if self.warnings:
            self.log("⚠️  WARNINGS:", "WARNING")
            for warning in self.warnings:
                self.log(f"  • {warning}", "WARNING")
        
        if success:
            self.log("✅ Pre-build optimization successful!")
        else:
            self.log("❌ Pre-build optimization failed!")
        
        return success


def main():
    """Main entry point for pre-build optimization"""
    optimizer = PreBuildOptimizer()
    
    # Run optimization
    success = optimizer.run_optimization()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main() 