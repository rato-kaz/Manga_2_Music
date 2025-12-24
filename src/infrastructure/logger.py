"""
Logger Module: Convenience module for getting loggers.

This provides a simple interface for getting loggers throughout the application.
"""

import logging
from typing import Optional

# Default logger instance
_default_logger: Optional[logging.Logger] = None


def get_logger(name: str = None) -> logging.Logger:
    """
    Get a logger instance.

    Args:
        name: Logger name (defaults to caller's module name)

    Returns:
        Logger instance
    """
    if name is None:
        import inspect

        frame = inspect.currentframe().f_back
        name = frame.f_globals.get("__name__", "root")

    return logging.getLogger(name)


def setup_default_logging(log_level: str = "INFO") -> None:
    """
    Setup default logging configuration.

    Args:
        log_level: Logging level
    """
    from src.infrastructure.logging_config import setup_logging

    setup_logging(log_level=log_level)
