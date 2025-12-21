"""
API Dependencies: Dependency injection for FastAPI.

This module provides dependencies for route handlers.
"""

from pathlib import Path
from typing import Generator

from src.application.services.manga_processor import MangaProcessingService


def get_processing_service() -> Generator[MangaProcessingService, None, None]:
    """
    Dependency for manga processing service.
    
    Yields:
        MangaProcessingService instance
    """
    output_dir = Path("output")
    service = MangaProcessingService(output_base_dir=output_dir)
    yield service

