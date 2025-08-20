"""
Logging Configuration Utilities

This module provides functions to configure the loguru logger based on application settings.
"""

from loguru import logger
from core.config import Settings


def configure_logger(settings: Settings) -> None:
    """
    Configure the loguru logger based on application settings.
    
    Args:
        settings: Application configuration containing log level settings
    """
    # Remove default logger to avoid duplicate logs
    logger.remove()
    
    # Determine the log level
    # If debug mode is enabled, force DEBUG level regardless of LOG_LEVEL setting
    if settings.DEBUG_MODE:
        log_level = "DEBUG"
    else:
        log_level = settings.LOG_LEVEL
# If log level is NONE, disable all logging
    if log_level == "NONE":
        # Logger is already removed, so no need to add any handlers
        return
    
    # Add console handler with the appropriate log level
    logger.add(
        sink=lambda msg: print(msg, end=""),  # Print to stdout
        level=log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        colorize=True
    )
    
    logger.debug(f"Logger configured with level: {log_level}")


def update_logger_config(settings: Settings) -> None:
    """
    Update the logger configuration when settings change.
    
    Args:
        settings: Updated application configuration
    """
    configure_logger(settings)