#!/usr/bin/env python
"""
Setup logging for the application.

This script initializes logging configuration at application startup.
"""

from pathlib import Path
from src.infrastructure.logging_config import setup_logging


def main() -> None:
    """Setup logging configuration."""
    # Try to load from config file first
    config_file = Path("config/logging.yaml")
    
    if config_file.exists():
        setup_logging(config_file=config_file)
        print("Logging configured from config/logging.yaml")
    else:
        # Use default configuration
        log_file = Path("logs/app.log")
        setup_logging(
            log_level="INFO",
            log_file=log_file,
        )
        print(f"Logging configured (default). Log file: {log_file}")


if __name__ == "__main__":
    main()

