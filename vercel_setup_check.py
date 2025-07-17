#!/usr/bin/env python3
"""
Vercel Setup Check Script

Verifies all required environment variables are properly configured 
for the multi-agent portfolio analysis system deployment.
"""

import os
import sys
from typing import Dict, List, Tuple


class VercelSetupChecker:
    """Comprehensive environment variable validation for Vercel deployment"""
    
    # Required environment variables for core functionality
    REQUIRED_VARS = {
        "XAI_API_KEY": "XAI Grok API key for AI agents",
        "SENDER_EMAIL": "Email address for sending notifications",
        "SENDER_PASSWORD": "Email password/app password for SMTP authentication",
        "TO_EMAIL": "Recipient email address for notifications"
    }
    
    # Optional environment variables with defaults
    OPTIONAL_VARS = {
        "SMTP_SERVER": "SMTP server (defaults to smtp.gmail.com)",
        "SMTP_PORT": "SMTP port (defaults to 587)",
        "DATABASE_URL": "Database connection string (optional)",
        "REDIS_URL": "Redis connection string (optional)",
        "VERCEL_URL": "Vercel deployment URL",
        "CRON_SECRET": "Secret for cron job authentication",
        "ENVIRONMENT": "Environment type (production, preview, development)",
        "DEFAULT_PORTFOLIO": "Default portfolio tickers",
        "HIGH_VOLATILITY_THRESHOLD": "High volatility threshold (defaults to 0.05)",
        "API_SECRET_KEY": "API secret key for authentication"
    }
    
    def __init__(self):
        self.missing_required = []
        self.missing_optional = []
        self.configured_vars = []
        
    def check_environment_variables(self) -> Tuple[bool, Dict[str, List[str]]]:
        """Check all environment variables and return status
        
        Returns:
            Tuple of (is_ready, results_dict)
        """
        # Check required variables
        for var, description in self.REQUIRED_VARS.items():
            value = os.getenv(var)
            if value:
                self.configured_vars.append((var, description, "✅ Set"))
            else:
                self.missing_required.append((var, description))
        
        # Check optional variables
        for var, description in self.OPTIONAL_VARS.items():
            value = os.getenv(var)
            if value:
                self.configured_vars.append((var, description, "✅ Set"))
            else:
                self.missing_optional.append((var, description))
        
        is_ready = len(self.missing_required) == 0
        
        results = {
            "configured": self.configured_vars,
            "missing_required": self.missing_required,
            "missing_optional": self.missing_optional,
            "is_ready": is_ready
        }
        
        return is_ready, results
    
    def validate_email_configuration(self) -> List[str]:
        """Validate email configuration specifically"""
        issues = []
        
        sender_email = os.getenv("SENDER_EMAIL")
        sender_password = os.getenv("SENDER_PASSWORD")
        
        if sender_email and "@" not in sender_email:
            issues.append("SENDER_EMAIL appears to be invalid (missing @)")
        
        if sender_password and len(sender_password) < 8:
            issues.append("SENDER_PASSWORD appears to be too short (should be app password)")
        
        return issues
    
    def validate_api_key(self) -> List[str]:
        """Validate XAI API key format"""
        issues = []
        
        api_key = os.getenv("XAI_API_KEY")
        if api_key:
            if not api_key.startswith("xai-"):
                issues.append("XAI_API_KEY should start with 'xai-'")
            if len(api_key) < 20:
                issues.append("XAI_API_KEY appears to be too short")
        
        return issues
    
    def print_results(self, results: Dict[str, List]) -> None:
        """Print formatted results"""
        print("\n" + "="*60)
        print("🔍 VERCEL DEPLOYMENT SETUP CHECK")
        print("="*60)
        
        # Print configured variables
        if results["configured"]:
            print("\n✅ CONFIGURED ENVIRONMENT VARIABLES:")
            for var, desc, status in results["configured"]:
                print(f"  {status} {var:<25} - {desc}")
        
        # Print missing required variables
        if results["missing_required"]:
            print("\n❌ MISSING REQUIRED VARIABLES:")
            for var, desc in results["missing_required"]:
                print(f"  ❌ {var:<25} - {desc}")
        
        # Print missing optional variables
        if results["missing_optional"]:
            print("\n⚠️  MISSING OPTIONAL VARIABLES:")
            for var, desc in results["missing_optional"]:
                print(f"  ⚠️  {var:<25} - {desc}")
        
        # Print validation issues
        email_issues = self.validate_email_configuration()
        api_issues = self.validate_api_key()
        
        if email_issues or api_issues:
            print("\n🔧 VALIDATION ISSUES:")
            for issue in email_issues + api_issues:
                print(f"  ⚠️  {issue}")
        
        # Print final status
        print("\n" + "="*60)
        if results["is_ready"]:
            print("🚀 READY FOR DEPLOYMENT")
            print("All required environment variables are configured!")
        else:
            print("❌ NOT READY FOR DEPLOYMENT")
            print(f"Missing {len(results['missing_required'])} required variable(s)")
            print("\nTo configure missing variables:")
            print("1. Go to Vercel Dashboard > Project > Settings > Environment Variables")
            print("2. Add the missing variables listed above")
            print("3. Set sensitive variables (API keys, passwords) as 'Sensitive'")
            print("4. Run this script again to verify")
        
        print("="*60)
        
        # Print setup instructions for missing variables
        if results["missing_required"]:
            print("\n📋 SETUP INSTRUCTIONS:")
            print("Add these environment variables in Vercel Dashboard:")
            print()
            for var, desc in results["missing_required"]:
                print(f"Variable: {var}")
                print(f"Description: {desc}")
                print(f"Sensitive: {'Yes' if 'KEY' in var or 'PASSWORD' in var else 'No'}")
                print(f"Environments: Production, Preview, Development")
                print()

def main():
    """Main function to run the setup check"""
    checker = VercelSetupChecker()
    is_ready, results = checker.check_environment_variables()
    checker.print_results(results)
    
    # Return appropriate exit code
    if is_ready:
        return 0
    else:
        return 1

def check_for_testing() -> bool:
    """Quick check function for testing integration
    
    Returns:
        bool: True if ready for deployment, False otherwise
    """
    checker = VercelSetupChecker()
    is_ready, _ = checker.check_environment_variables()
    return is_ready

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 