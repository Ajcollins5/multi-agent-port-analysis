#!/usr/bin/env python3

"""
Environment Variable Validator for Multi-Agent Portfolio Analysis
Provides robust validation, error handling, and logging for Vercel serverless environment
"""

import os
import logging
import sys
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import json

# Configure logging for serverless environment
class ServerlessLogger:
    """Custom logger optimized for Vercel serverless functions"""
    
    def __init__(self, name: str = "portfolio_analysis"):
        self.name = name
        self.logger = logging.getLogger(name)
        
        # Configure for serverless environment
        if not self.logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
    
    def info(self, message: str, **kwargs):
        """Log info message with context"""
        self.logger.info(self._format_message(message, **kwargs))
    
    def warning(self, message: str, **kwargs):
        """Log warning message with context"""
        self.logger.warning(self._format_message(message, **kwargs))
    
    def error(self, message: str, **kwargs):
        """Log error message with context"""
        self.logger.error(self._format_message(message, **kwargs))
    
    def critical(self, message: str, **kwargs):
        """Log critical message with context"""
        self.logger.critical(self._format_message(message, **kwargs))
    
    def _format_message(self, message: str, **kwargs) -> str:
        """Format message with additional context"""
        context = {
            "timestamp": datetime.now().isoformat(),
            "environment": os.environ.get("VERCEL_ENV", "unknown"),
            "function": os.environ.get("VERCEL_URL", "local"),
            **kwargs
        }
        return f"{message} | Context: {json.dumps(context, default=str)}"

# Global logger instance
logger = ServerlessLogger()

class EnvironmentValidator:
    """Validates environment variables with comprehensive error handling"""
    
    def __init__(self):
        self.required_vars = {
            "XAI_API_KEY": {
                "description": "Grok 4 API key for AI analysis",
                "type": str,
                "validation": self._validate_api_key,
                "sensitive": True
            },
            "SENDER_EMAIL": {
                "description": "Email address for notifications",
                "type": str,
                "validation": self._validate_email,
                "sensitive": True
            },
            "SENDER_PASSWORD": {
                "description": "Email password/app password",
                "type": str,
                "validation": self._validate_password,
                "sensitive": True
            },
            "TO_EMAIL": {
                "description": "Recipient email for alerts",
                "type": str,
                "validation": self._validate_email,
                "sensitive": True
            }
        }
        
        self.optional_vars = {
            "SMTP_SERVER": {
                "description": "SMTP server for email",
                "type": str,
                "default": "smtp.gmail.com",
                "validation": self._validate_smtp_server
            },
            "SMTP_PORT": {
                "description": "SMTP port",
                "type": int,
                "default": 587,
                "validation": self._validate_port
            },
            "DATABASE_URL": {
                "description": "External database URL",
                "type": str,
                "default": "",
                "validation": self._validate_database_url
            },
            # Redis has been migrated to Supabase
            # "REDIS_URL": {
            #     "description": "Redis cache URL",
            #     "type": str,
            #     "default": "",
            #     "validation": self._validate_redis_url
            # },
            "VERCEL_URL": {
                "description": "Vercel deployment URL",
                "type": str,
                "default": "",
                "validation": self._validate_url
            },
            "ENVIRONMENT": {
                "description": "Deployment environment",
                "type": str,
                "default": "development",
                "validation": self._validate_environment
            },
            "HIGH_VOLATILITY_THRESHOLD": {
                "description": "High volatility threshold",
                "type": float,
                "default": 0.05,
                "validation": self._validate_threshold
            },
            "DEFAULT_PORTFOLIO": {
                "description": "Default portfolio tickers",
                "type": str,
                "default": "AAPL,GOOGL,MSFT,AMZN,TSLA",
                "validation": self._validate_portfolio
            },
            "CRON_SECRET": {
                "description": "Secret for cron job authentication",
                "type": str,
                "default": "",
                "validation": self._validate_secret,
                "sensitive": True
            },
            "API_SECRET_KEY": {
                "description": "API secret key",
                "type": str,
                "default": "",
                "validation": self._validate_secret,
                "sensitive": True
            }
        }
        
        self.validation_results = {}
        self.errors = []
        self.warnings = []
    
    def validate_all(self) -> Dict[str, Any]:
        """Validate all environment variables"""
        logger.info("Starting environment validation")
        
        # Validate required variables
        for var_name, config in self.required_vars.items():
            self._validate_variable(var_name, config, required=True)
        
        # Validate optional variables
        for var_name, config in self.optional_vars.items():
            self._validate_variable(var_name, config, required=False)
        
        # Generate validation summary
        validation_summary = {
            "success": len(self.errors) == 0,
            "timestamp": datetime.now().isoformat(),
            "environment": os.environ.get("VERCEL_ENV", "unknown"),
            "total_variables": len(self.required_vars) + len(self.optional_vars),
            "required_valid": len([v for v in self.validation_results.values() if v.get("required") and v.get("valid")]),
            "optional_valid": len([v for v in self.validation_results.values() if not v.get("required") and v.get("valid")]),
            "errors": self.errors,
            "warnings": self.warnings,
            "variables": self._sanitize_results()
        }
        
        if validation_summary["success"]:
            logger.info("Environment validation completed successfully")
        else:
            logger.error("Environment validation failed", errors=self.errors)
        
        return validation_summary
    
    def _validate_variable(self, var_name: str, config: Dict[str, Any], required: bool):
        """Validate individual environment variable"""
        try:
            value = os.environ.get(var_name)
            
            if required and not value:
                error_msg = f"Required environment variable {var_name} is missing"
                self.errors.append({
                    "variable": var_name,
                    "error": error_msg,
                    "description": config.get("description", "No description"),
                    "required": True
                })
                logger.error(error_msg, variable=var_name)
                return
            
            if not value and not required:
                # Use default value
                value = config.get("default", "")
                if value:
                    logger.info(f"Using default value for {var_name}")
            
            # Type conversion
            if value and config.get("type") == int:
                try:
                    value = int(value)
                except ValueError:
                    error_msg = f"Invalid integer value for {var_name}"
                    self.errors.append({
                        "variable": var_name,
                        "error": error_msg,
                        "required": required
                    })
                    logger.error(error_msg, variable=var_name)
                    return
            
            if value and config.get("type") == float:
                try:
                    value = float(value)
                except ValueError:
                    error_msg = f"Invalid float value for {var_name}"
                    self.errors.append({
                        "variable": var_name,
                        "error": error_msg,
                        "required": required
                    })
                    logger.error(error_msg, variable=var_name)
                    return
            
            # Custom validation
            if value and config.get("validation"):
                validation_result = config["validation"](value)
                if not validation_result.get("valid"):
                    error_msg = f"Validation failed for {var_name}: {validation_result.get('error')}"
                    self.errors.append({
                        "variable": var_name,
                        "error": error_msg,
                        "required": required
                    })
                    logger.error(error_msg, variable=var_name)
                    return
                
                if validation_result.get("warning"):
                    warning_msg = f"Warning for {var_name}: {validation_result.get('warning')}"
                    self.warnings.append({
                        "variable": var_name,
                        "warning": warning_msg
                    })
                    logger.warning(warning_msg, variable=var_name)
            
            # Store validation result
            self.validation_results[var_name] = {
                "valid": True,
                "value": value,
                "required": required,
                "description": config.get("description", ""),
                "sensitive": config.get("sensitive", False)
            }
            
        except Exception as e:
            error_msg = f"Unexpected error validating {var_name}: {str(e)}"
            self.errors.append({
                "variable": var_name,
                "error": error_msg,
                "required": required
            })
            logger.error(error_msg, variable=var_name, exception=str(e))
    
    def _validate_api_key(self, value: str) -> Dict[str, Any]:
        """Validate API key format"""
        if not value.startswith("xai-"):
            return {"valid": False, "error": "XAI API key must start with 'xai-'"}
        if len(value) < 20:
            return {"valid": False, "error": "API key appears to be too short"}
        return {"valid": True}
    
    def _validate_email(self, value: str) -> Dict[str, Any]:
        """Validate email format"""
        if "@" not in value or "." not in value:
            return {"valid": False, "error": "Invalid email format"}
        return {"valid": True}
    
    def _validate_password(self, value: str) -> Dict[str, Any]:
        """Validate password strength"""
        if len(value) < 8:
            return {"valid": False, "error": "Password must be at least 8 characters"}
        return {"valid": True}
    
    def _validate_smtp_server(self, value: str) -> Dict[str, Any]:
        """Validate SMTP server"""
        if not value or "." not in value:
            return {"valid": False, "error": "Invalid SMTP server format"}
        return {"valid": True}
    
    def _validate_port(self, value: int) -> Dict[str, Any]:
        """Validate port number"""
        if not isinstance(value, int) or value < 1 or value > 65535:
            return {"valid": False, "error": "Invalid port number"}
        return {"valid": True}
    
    def _validate_database_url(self, value: str) -> Dict[str, Any]:
        """Validate database URL"""
        if not value:
            return {"valid": True}  # Optional
        if not value.startswith(("postgresql://", "mysql://", "sqlite://")):
            return {"valid": False, "error": "Invalid database URL format"}
        return {"valid": True}
    
    # Redis validation removed - migrated to Supabase
    # def _validate_redis_url(self, value: str) -> Dict[str, Any]:
    #     """Validate Redis URL"""
    #     if not value:
    #         return {"valid": True}  # Optional
    #     if not value.startswith("redis://"):
    #         return {"valid": False, "error": "Invalid Redis URL format"}
    #     return {"valid": True}
    
    def _validate_url(self, value: str) -> Dict[str, Any]:
        """Validate URL format"""
        if not value:
            return {"valid": True}  # Optional
        if not value.startswith(("http://", "https://")):
            return {"valid": False, "error": "Invalid URL format"}
        return {"valid": True}
    
    def _validate_environment(self, value: str) -> Dict[str, Any]:
        """Validate environment value"""
        valid_envs = ["development", "staging", "production"]
        if value not in valid_envs:
            return {"valid": False, "error": f"Environment must be one of: {', '.join(valid_envs)}"}
        return {"valid": True}
    
    def _validate_threshold(self, value: float) -> Dict[str, Any]:
        """Validate volatility threshold"""
        if not isinstance(value, (int, float)) or value < 0 or value > 1:
            return {"valid": False, "error": "Threshold must be between 0 and 1"}
        return {"valid": True}
    
    def _validate_portfolio(self, value: str) -> Dict[str, Any]:
        """Validate portfolio ticker format"""
        if not value:
            return {"valid": False, "error": "Portfolio cannot be empty"}
        
        tickers = [t.strip().upper() for t in value.split(",")]
        for ticker in tickers:
            if not ticker.isalpha() or len(ticker) > 5:
                return {"valid": False, "error": f"Invalid ticker format: {ticker}"}
        
        if len(tickers) > 50:
            return {"valid": True, "warning": "Portfolio has more than 50 tickers, may impact performance"}
        
        return {"valid": True}
    
    def _validate_secret(self, value: str) -> Dict[str, Any]:
        """Validate secret key"""
        if not value:
            return {"valid": True}  # Optional
        if len(value) < 16:
            return {"valid": False, "error": "Secret key must be at least 16 characters"}
        return {"valid": True}
    
    def _sanitize_results(self) -> Dict[str, Any]:
        """Sanitize validation results for output"""
        sanitized = {}
        for var_name, result in self.validation_results.items():
            sanitized[var_name] = {
                "valid": result["valid"],
                "required": result["required"],
                "description": result["description"],
                "has_value": bool(result.get("value")),
                "sensitive": result.get("sensitive", False)
            }
            # Don't include actual values for sensitive variables
            if not result.get("sensitive"):
                sanitized[var_name]["value"] = result.get("value")
        return sanitized

class ErrorHandler:
    """Comprehensive error handling for serverless environment"""
    
    def __init__(self):
        self.error_counts = {}
        self.last_errors = []
    
    def handle_error(self, error: Exception, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Handle and log error with context"""
        error_type = type(error).__name__
        error_message = str(error)
        timestamp = datetime.now().isoformat()
        
        # Count error occurrences
        self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1
        
        # Create error record
        error_record = {
            "error_type": error_type,
            "message": error_message,
            "timestamp": timestamp,
            "context": context or {},
            "count": self.error_counts[error_type],
            "environment": os.environ.get("VERCEL_ENV", "unknown")
        }
        
        # Store recent errors
        self.last_errors.append(error_record)
        if len(self.last_errors) > 100:
            self.last_errors.pop(0)
        
        # Log error with context
        logger.error(
            f"Error occurred: {error_type}",
            error_message=error_message,
            context=context or {},
            count=self.error_counts[error_type]
        )
        
        return error_record
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Get error summary for monitoring"""
        return {
            "total_errors": sum(self.error_counts.values()),
            "error_types": dict(self.error_counts),
            "recent_errors": self.last_errors[-10:],  # Last 10 errors
            "timestamp": datetime.now().isoformat()
        }

# Global instances
env_validator = EnvironmentValidator()
error_handler = ErrorHandler()

def validate_environment() -> Dict[str, Any]:
    """Validate environment variables - main entry point"""
    return env_validator.validate_all()

def handle_error(error: Exception, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Handle error - main entry point"""
    return error_handler.handle_error(error, context)

def get_error_summary() -> Dict[str, Any]:
    """Get error summary - main entry point"""
    return error_handler.get_error_summary()

# Export for Vercel
def handler(request):
    """Vercel serverless function handler for environment validation"""
    try:
        if request.method == "POST":
            body = request.get_json() or {}
            action = body.get("action", "validate")
            
            if action == "validate":
                result = validate_environment()
                return json.dumps(result)
            
            elif action == "error_summary":
                result = get_error_summary()
                return json.dumps(result)
            
            else:
                return json.dumps({
                    "error": "Invalid action",
                    "available_actions": ["validate", "error_summary"]
                })
        
        else:
            return json.dumps({
                "service": "EnvironmentValidator",
                "description": "Environment validation and error handling for serverless functions",
                "endpoints": [
                    "POST - validate: Validate all environment variables",
                    "POST - error_summary: Get error summary"
                ],
                "features": [
                    "Comprehensive env var validation",
                    "Robust error handling",
                    "Serverless logging",
                    "Security-aware sanitization"
                ],
                "status": "active"
            })
            
    except Exception as e:
        error_record = handle_error(e, {"action": "env_validation"})
        return json.dumps({
            "error": "Environment validation failed",
            "details": error_record
        })

# Export handler for Vercel
app = handler

# CLI interface for testing
if __name__ == "__main__":
    print("Environment Validation Results:")
    print("=" * 50)
    
    results = validate_environment()
    
    if results["success"]:
        print("✅ All environment variables are valid!")
    else:
        print("❌ Environment validation failed!")
        for error in results["errors"]:
            print(f"  - {error['variable']}: {error['error']}")
    
    if results["warnings"]:
        print("\n⚠️  Warnings:")
        for warning in results["warnings"]:
            print(f"  - {warning['variable']}: {warning['warning']}")
    
    print(f"\nValidation Summary:")
    print(f"  Required variables valid: {results['required_valid']}")
    print(f"  Optional variables valid: {results['optional_valid']}")
    print(f"  Total variables: {results['total_variables']}")
    
    # Test error handling
    print("\n" + "=" * 50)
    print("Testing Error Handler:")
    
    try:
        raise ValueError("Test error for demonstration")
    except Exception as e:
        error_record = handle_error(e, {"test": True})
        print(f"Error handled: {error_record['error_type']}")
    
    error_summary = get_error_summary()
    print(f"Total errors handled: {error_summary['total_errors']}") 