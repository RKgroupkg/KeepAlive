# keepalive/config.py
import os
from typing import Dict, Any, Optional

class KeepAliveConfig:
    """
    Configuration handler for KeepAliveService.
    Loads configuration from environment variables or defaults.
    """
    
    ENV_PREFIX = "KEEPALIVE_"
    
    # Default configuration
    DEFAULTS = {
        "PING_INTERVAL": 60,
        "PING_ENDPOINT": "alive",
        "PING_MESSAGE": "I am alive!",
        "PORT": 10000,
        "HOST": "0.0.0.0",
        "TIMEZONE": "UTC",
        "LOG_LEVEL": "INFO",
        "USE_FLASK": True,
    }
    
    # Environment variable mapping (ENV_VAR_NAME -> config_key)
    ENV_MAPPING = {
        "KEEPALIVE_INTERVAL": "PING_INTERVAL",
        "KEEPALIVE_ENDPOINT": "PING_ENDPOINT",
        "KEEPALIVE_MESSAGE": "PING_MESSAGE",
        "KEEPALIVE_PORT": "PORT",
        "KEEPALIVE_HOST": "HOST",
        "KEEPALIVE_TIMEZONE": "TIMEZONE",
        "KEEPALIVE_LOG_LEVEL": "LOG_LEVEL",
        "KEEPALIVE_USE_FLASK": "USE_FLASK",
        "RENDER_EXTERNAL_URL": "EXTERNAL_URL",
        "KOYEB_URL": "EXTERNAL_URL",
        "RAILWAY_STATIC_URL": "EXTERNAL_URL",
        "HEROKU_APP_URL": "EXTERNAL_URL",
    }
    
    # Type converters for environment variables
    TYPE_CONVERTERS = {
        "PING_INTERVAL": int,
        "PORT": int,
        "USE_FLASK": lambda x: str(x).lower() in ("true", "1", "yes"),
    }
    
    @classmethod
    def load(cls, overrides: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Load configuration from environment variables and override with provided values.
        
        Args:
            overrides: Dictionary of configuration overrides
            
        Returns:
            Dictionary of configuration values
        """
        config = cls.DEFAULTS.copy()
        
        # Load from environment variables
        for env_var, config_key in cls.ENV_MAPPING.items():
            if env_var in os.environ:
                value = os.environ[env_var]
                if config_key in cls.TYPE_CONVERTERS:
                    value = cls.TYPE_CONVERTERS[config_key](value)
                config[config_key] = value
        
        # Apply overrides
        if overrides:
            config.update(overrides)
        
        # Convert log level string to int if needed
        if isinstance(config.get("LOG_LEVEL"), str):
            import logging
            log_levels = {
                "DEBUG": logging.DEBUG,
                "INFO": logging.INFO,
                "WARNING": logging.WARNING,
                "ERROR": logging.ERROR,
                "CRITICAL": logging.CRITICAL,
            }
            config["LOG_LEVEL"] = log_levels.get(config["LOG_LEVEL"].upper(), logging.INFO)
        
        return config