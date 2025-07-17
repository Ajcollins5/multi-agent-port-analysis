#!/usr/bin/env python3
"""
Environment Variable Validator and Configuration Manager
Provides safe access to environment variables with validation and fallbacks
"""

import os
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum


class EnvVarType(Enum):
    """Environment variable types for validation"""
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    EMAIL = "email"
    URL = "url"
    JSON = "json"


@dataclass
class EnvVarConfig:
    """Configuration for environment variable validation"""
    name: str
    var_type: EnvVarType
    required: bool = True
    default: Optional[Any] = None
    description: str = ""
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    allowed_values: Optional[List[str]] = None
    

class EnvironmentValidator:
    """Validates and provides safe access to environment variables"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.validated_vars: Dict[str, Any] = {}
        self.errors: List[str] = []
        self.warnings: List[str] = []
        
        # Define configuration for all environment variables
        self.env_config = [
            # Core AI/ML Configuration
            EnvVarConfig(
                name="XAI_API_KEY",
                var_type=EnvVarType.STRING,
                required=True,
                description="xAI Grok API key for AI agent functionality",
                min_length=20
            ),
            
            # Email Configuration
            EnvVarConfig(
                name="SMTP_SERVER",
                var_type=EnvVarType.STRING,
                required=False,
                default="smtp.gmail.com",
                description="SMTP server for email notifications"
            ),
            EnvVarConfig(
                name="SMTP_PORT",
                var_type=EnvVarType.INTEGER,
                required=False,
                default=587,
                description="SMTP port for email notifications"
            ),
            EnvVarConfig(
                name="SENDER_EMAIL",
                var_type=EnvVarType.EMAIL,
                required=True,
                description="Email address for sending notifications"
            ),
            EnvVarConfig(
                name="SENDER_PASSWORD",
                var_type=EnvVarType.STRING,
                required=True,
                description="Password/App Password for email authentication",
                min_length=8
            ),
            EnvVarConfig(
                name="TO_EMAIL",
                var_type=EnvVarType.EMAIL,
                required=True,
                description="Recipient email address for notifications"
            ),
            
            # Database Configuration
            EnvVarConfig(
                name="DATABASE_URL",
                var_type=EnvVarType.URL,
                required=False,
                description="Database connection URL (PostgreSQL/MySQL)"
            ),
            EnvVarConfig(
                name="REDIS_URL",
                var_type=EnvVarType.URL,
                required=False,
                description="Redis connection URL for caching"
            ),
            
            # Deployment Configuration
            EnvVarConfig(
                name="VERCEL_URL",
                var_type=EnvVarType.URL,
                required=False,
                description="Vercel deployment URL"
            ),
            EnvVarConfig(
                name="ENVIRONMENT",
                var_type=EnvVarType.STRING,
                required=False,
                default="production",
                allowed_values=["development", "staging", "production"],
                description="Deployment environment"
            ),
            
            # Security Configuration
            EnvVarConfig(
                name="CRON_SECRET",
                var_type=EnvVarType.STRING,
                required=False,
                description="Secret key for cron job authentication",
                min_length=16
            ),
            EnvVarConfig(
                name="API_SECRET_KEY",
                var_type=EnvVarType.STRING,
                required=False,
                description="Secret key for API authentication",
                min_length=32
            ),
            
            # Portfolio Configuration
            EnvVarConfig(
                name="DEFAULT_PORTFOLIO",
                var_type=EnvVarType.STRING,
                required=False,
                default="AAPL,GOOGL,MSFT,AMZN,TSLA",
                description="Default portfolio tickers (comma-separated)"
            ),
            EnvVarConfig(
                name="HIGH_VOLATILITY_THRESHOLD",
                var_type=EnvVarType.FLOAT,
                required=False,
                default=0.05,
                description="High volatility threshold for alerts"
            ),
            EnvVarConfig(
                name="MEDIUM_VOLATILITY_THRESHOLD",
                var_type=EnvVarType.FLOAT,
                required=False,
                default=0.02,
                description="Medium volatility threshold for alerts"
            ),
            
            # Feature Flags
            EnvVarConfig(
                name="ENABLE_EMAIL_NOTIFICATIONS",
                var_type=EnvVarType.BOOLEAN,
                required=False,
                default=True,
                description="Enable email notifications"
            ),
            EnvVarConfig(
                name="ENABLE_CACHING",
                var_type=EnvVarType.BOOLEAN,
                required=False,
                default=True,
                description="Enable caching for performance"
            ),
            EnvVarConfig(
                name="DEBUG",
                var_type=EnvVarType.BOOLEAN,
                required=False,
                default=False,
                description="Enable debug mode"
            )
        ]
    
    def _validate_string(self, value: str, config: EnvVarConfig) -> str:
        """Validate string type environment variable"""
        if config.min_length and len(value) < config.min_length:
            raise ValueError(f"{config.name}: minimum length is {config.min_length}")
        
        if config.max_length and len(value) > config.max_length:
            raise ValueError(f"{config.name}: maximum length is {config.max_length}")
        
        if config.allowed_values and value not in config.allowed_values:
            raise ValueError(f"{config.name}: must be one of {config.allowed_values}")
        
        return value
    
    def _validate_integer(self, value: str, config: EnvVarConfig) -> int:
        """Validate integer type environment variable"""
        try:
            return int(value)
        except ValueError:
            raise ValueError(f"{config.name}: must be a valid integer")
    
    def _validate_float(self, value: str, config: EnvVarConfig) -> float:
        """Validate float type environment variable"""
        try:
            return float(value)
        except ValueError:
            raise ValueError(f"{config.name}: must be a valid float")
    
    def _validate_boolean(self, value: str, config: EnvVarConfig) -> bool:
        """Validate boolean type environment variable"""
        if value.lower() in ('true', '1', 'yes', 'on'):
            return True
        elif value.lower() in ('false', '0', 'no', 'off'):
            return False
        else:
            raise ValueError(f"{config.name}: must be a boolean value (true/false)")
    
    def _validate_email(self, value: str, config: EnvVarConfig) -> str:
        """Validate email type environment variable"""
        if '@' not in value or '.' not in value:
            raise ValueError(f"{config.name}: must be a valid email address")
        return value
    
    def _validate_url(self, value: str, config: EnvVarConfig) -> str:
        """Validate URL type environment variable"""
        if not value.startswith(('http://', 'https://', 'postgresql://', 'mysql://', 'redis://')):
            raise ValueError(f"{config.name}: must be a valid URL")
        return value
    
    def _validate_json(self, value: str, config: EnvVarConfig) -> Any:
        """Validate JSON type environment variable"""
        try:
            import json
            return json.loads(value)
        except json.JSONDecodeError:
            raise ValueError(f"{config.name}: must be valid JSON")
    
    def _validate_single_var(self, config: EnvVarConfig) -> Optional[Any]:
        """Validate a single environment variable"""
        raw_value = os.environ.get(config.name)
        
        # Handle missing variables
        if raw_value is None:
            if config.required:
                self.errors.append(f"Required environment variable {config.name} is not set")
                return None
            else:
                if config.default is not None:
                    self.warnings.append(f"Optional environment variable {config.name} not set, using default: {config.default}")
                    return config.default
                return None
        
        # Handle empty string values
        if raw_value == "":
            if config.required:
                self.errors.append(f"Required environment variable {config.name} is empty")
                return None
            else:
                return config.default
        
        # Validate based on type
        try:
            if config.var_type == EnvVarType.STRING:
                return self._validate_string(raw_value, config)
            elif config.var_type == EnvVarType.INTEGER:
                return self._validate_integer(raw_value, config)
            elif config.var_type == EnvVarType.FLOAT:
                return self._validate_float(raw_value, config)
            elif config.var_type == EnvVarType.BOOLEAN:
                return self._validate_boolean(raw_value, config)
            elif config.var_type == EnvVarType.EMAIL:
                return self._validate_email(raw_value, config)
            elif config.var_type == EnvVarType.URL:
                return self._validate_url(raw_value, config)
            elif config.var_type == EnvVarType.JSON:
                return self._validate_json(raw_value, config)
            else:
                self.errors.append(f"Unknown validation type for {config.name}")
                return None
        except ValueError as e:
            self.errors.append(f"Validation error for {config.name}: {str(e)}")
            return None
    
    def validate_all(self) -> Dict[str, Any]:
        """Validate all environment variables"""
        self.validated_vars = {}
        self.errors = []
        self.warnings = []
        
        for config in self.env_config:
            validated_value = self._validate_single_var(config)
            if validated_value is not None:
                self.validated_vars[config.name] = validated_value
        
        return self.validated_vars
    
    def get_config(self, name: str, default: Any = None) -> Any:
        """Get a validated configuration value"""
        if name not in self.validated_vars:
            self.warnings.append(f"Configuration {name} not found in validated variables")
            return default
        return self.validated_vars[name]
    
    def get_validation_report(self) -> Dict[str, Any]:
        """Get a report of validation results"""
        return {
            "success": len(self.errors) == 0,
            "validated_count": len(self.validated_vars),
            "total_count": len(self.env_config),
            "errors": self.errors,
            "warnings": self.warnings,
            "validated_vars": list(self.validated_vars.keys())
        }
    
    def raise_on_errors(self):
        """Raise exception if there are validation errors"""
        if self.errors:
            error_msg = "Environment validation failed:\n" + "\n".join(f"  • {error}" for error in self.errors)
            raise ValueError(error_msg)


# Global instance for use across the application
env_validator = EnvironmentValidator()


def get_config(name: str, default: Any = None) -> Any:
    """Get a validated configuration value (thread-safe)"""
    return env_validator.get_config(name, default)


def validate_environment() -> Dict[str, Any]:
    """Validate all environment variables and return results"""
    return env_validator.validate_all()


def get_validation_report() -> Dict[str, Any]:
    """Get validation report"""
    return env_validator.get_validation_report()


def ensure_environment_valid():
    """Ensure environment is valid or raise exception"""
    env_validator.validate_all()
    env_validator.raise_on_errors()


class SafeConfig:
    """Safe configuration class that prevents direct environment access"""
    
    def __init__(self):
        # Validate environment on initialization
        validate_environment()
        ensure_environment_valid()
    
    # Core Configuration
    @property
    def XAI_API_KEY(self) -> str:
        return get_config("XAI_API_KEY")
    
    # Email Configuration
    @property
    def SMTP_SERVER(self) -> str:
        return get_config("SMTP_SERVER", "smtp.gmail.com")
    
    @property
    def SMTP_PORT(self) -> int:
        return get_config("SMTP_PORT", 587)
    
    @property
    def SENDER_EMAIL(self) -> str:
        return get_config("SENDER_EMAIL")
    
    @property
    def SENDER_PASSWORD(self) -> str:
        return get_config("SENDER_PASSWORD")
    
    @property
    def TO_EMAIL(self) -> str:
        return get_config("TO_EMAIL")
    
    # Database Configuration
    @property
    def DATABASE_URL(self) -> Optional[str]:
        return get_config("DATABASE_URL")
    
    @property
    def REDIS_URL(self) -> Optional[str]:
        return get_config("REDIS_URL")
    
    # Deployment Configuration
    @property
    def VERCEL_URL(self) -> Optional[str]:
        return get_config("VERCEL_URL")
    
    @property
    def ENVIRONMENT(self) -> str:
        return get_config("ENVIRONMENT", "production")
    
    # Security Configuration
    @property
    def CRON_SECRET(self) -> Optional[str]:
        return get_config("CRON_SECRET")
    
    @property
    def API_SECRET_KEY(self) -> Optional[str]:
        return get_config("API_SECRET_KEY")
    
    # Portfolio Configuration
    @property
    def DEFAULT_PORTFOLIO(self) -> str:
        return get_config("DEFAULT_PORTFOLIO", "AAPL,GOOGL,MSFT,AMZN,TSLA")
    
    @property
    def HIGH_VOLATILITY_THRESHOLD(self) -> float:
        return get_config("HIGH_VOLATILITY_THRESHOLD", 0.05)
    
    @property
    def MEDIUM_VOLATILITY_THRESHOLD(self) -> float:
        return get_config("MEDIUM_VOLATILITY_THRESHOLD", 0.02)
    
    # Feature Flags
    @property
    def ENABLE_EMAIL_NOTIFICATIONS(self) -> bool:
        return get_config("ENABLE_EMAIL_NOTIFICATIONS", True)
    
    @property
    def ENABLE_CACHING(self) -> bool:
        return get_config("ENABLE_CACHING", True)
    
    @property
    def DEBUG(self) -> bool:
        return get_config("DEBUG", False)
    
    def get_portfolio_list(self) -> List[str]:
        """Get portfolio as a list of ticker symbols"""
        return [ticker.strip().upper() for ticker in self.DEFAULT_PORTFOLIO.split(',')]
    
    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.ENVIRONMENT == "production"
    
    def is_development(self) -> bool:
        """Check if running in development environment"""
        return self.ENVIRONMENT == "development"
    
    def validate_config(self) -> Dict[str, Any]:
        """Validate configuration and return report"""
        return get_validation_report()


# Global configuration instance
config = SafeConfig() 