#!/usr/bin/env python3
"""
Cloud Configuration Utility for Multi-Agent Portfolio Analysis
Handles environment variables for both Streamlit Cloud and Render deployments
"""

import os
import logging
from typing import Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_config(key: str, default: Any = None) -> Any:
    """
    Get configuration from environment variables or Streamlit secrets
    
    Args:
        key: Configuration key
        default: Default value if key not found
        
    Returns:
        Configuration value
    """
    # Try Streamlit secrets first (for Streamlit Cloud)
    try:
        import streamlit as st
        if hasattr(st, 'secrets') and key in st.secrets:
            return st.secrets[key]
    except (ImportError, AttributeError, KeyError):
        pass
    
    # Fall back to environment variables (for Render and local development)
    return os.environ.get(key, default)

def get_database_config() -> dict:
    """Get database configuration for cloud deployment"""
    return {
        "url": get_config("DATABASE_URL"),
        "type": "postgresql" if get_config("DATABASE_URL", "").startswith("postgresql://") else "sqlite",
        "sqlite_path": get_config("SQLITE_PATH", "knowledge.db")
    }

def get_email_config() -> dict:
    """Get email configuration"""
    return {
        "smtp_server": get_config("SMTP_SERVER", "smtp.gmail.com"),
        "smtp_port": int(get_config("SMTP_PORT", "587")),
        "sender_email": get_config("SENDER_EMAIL"),
        "sender_password": get_config("SENDER_PASSWORD"),
        "to_email": get_config("TO_EMAIL"),
        "enabled": get_config("ENABLE_EMAIL_NOTIFICATIONS", "true").lower() == "true"
    }

def get_api_config() -> dict:
    """Get API configuration"""
    return {
        "xai_api_key": get_config("XAI_API_KEY"),
        "timeout": int(get_config("API_TIMEOUT", "30")),
        "max_retries": int(get_config("MAX_RETRIES", "3")),
        "cache_ttl": int(get_config("CACHE_TTL", "3600"))
    }

def get_portfolio_config() -> dict:
    """Get portfolio configuration"""
    default_portfolio = get_config("DEFAULT_PORTFOLIO", "AAPL,GOOGL,MSFT,TSLA,AMZN")
    return {
        "default_tickers": default_portfolio.split(","),
        "max_tickers": int(get_config("MAX_TICKERS", "20")),
        "analysis_interval": int(get_config("ANALYSIS_INTERVAL", "3600")),
        "high_volatility_threshold": float(get_config("HIGH_VOLATILITY_THRESHOLD", "0.05")),
        "medium_volatility_threshold": float(get_config("MEDIUM_VOLATILITY_THRESHOLD", "0.02"))
    }

def get_feature_flags() -> dict:
    """Get feature flags configuration"""
    return {
        "enable_background_analysis": get_config("ENABLE_BACKGROUND_ANALYSIS", "true").lower() == "true",
        "enable_knowledge_evolution": get_config("ENABLE_KNOWLEDGE_EVOLUTION", "true").lower() == "true",
        "enable_email_notifications": get_config("ENABLE_EMAIL_NOTIFICATIONS", "true").lower() == "true",
        "enable_caching": get_config("ENABLE_CACHING", "true").lower() == "true",
        "enable_error_notifications": get_config("ENABLE_ERROR_NOTIFICATIONS", "false").lower() == "true",
        "enable_analytics": get_config("ENABLE_ANALYTICS", "false").lower() == "true",
        "enable_debug": get_config("DEBUG", "false").lower() == "true"
    }

def get_redis_config() -> dict:
    """Get Redis configuration"""
    return {
        "url": get_config("REDIS_URL"),
        "enabled": get_config("REDIS_URL") is not None,
        "default_ttl": int(get_config("REDIS_DEFAULT_TTL", "3600"))
    }

def validate_config() -> tuple[bool, list[str]]:
    """
    Validate required configuration
    
    Returns:
        Tuple of (is_valid, missing_keys)
    """
    required_keys = [
        "XAI_API_KEY",
        "SENDER_EMAIL",
        "SENDER_PASSWORD",
        "TO_EMAIL"
    ]
    
    missing_keys = []
    for key in required_keys:
        if not get_config(key):
            missing_keys.append(key)
    
    return len(missing_keys) == 0, missing_keys

def log_config_status():
    """Log configuration status for debugging"""
    is_valid, missing_keys = validate_config()
    
    if is_valid:
        logger.info("✅ Configuration validation passed")
    else:
        logger.error(f"❌ Configuration validation failed. Missing keys: {missing_keys}")
    
    # Log feature flags
    flags = get_feature_flags()
    logger.info(f"Feature flags: {flags}")
    
    # Log database type
    db_config = get_database_config()
    logger.info(f"Database type: {db_config['type']}")
    
    # Log Redis status
    redis_config = get_redis_config()
    logger.info(f"Redis enabled: {redis_config['enabled']}")

# Environment detection
def get_environment() -> str:
    """Detect deployment environment"""
    if get_config("STREAMLIT_SHARING_MODE"):
        return "streamlit_cloud"
    elif get_config("RENDER"):
        return "render"
    elif get_config("VERCEL"):
        return "vercel"
    else:
        return "local"

def is_cloud_deployment() -> bool:
    """Check if running in cloud environment"""
    return get_environment() in ["streamlit_cloud", "render", "vercel"]

def get_deployment_info() -> dict:
    """Get deployment information"""
    environment = get_environment()
    return {
        "environment": environment,
        "is_cloud": is_cloud_deployment(),
        "platform": environment,
        "debug_mode": get_feature_flags()["enable_debug"]
    }

# Configuration summary
def get_config_summary() -> dict:
    """Get complete configuration summary"""
    return {
        "deployment": get_deployment_info(),
        "database": get_database_config(),
        "email": {**get_email_config(), "sender_password": "***"},  # Hide password
        "api": {**get_api_config(), "xai_api_key": "***"},  # Hide API key
        "portfolio": get_portfolio_config(),
        "features": get_feature_flags(),
        "redis": get_redis_config()
    }

# Initialize configuration on import
if __name__ == "__main__":
    log_config_status()
    print("Configuration Summary:")
    import json
    print(json.dumps(get_config_summary(), indent=2)) 