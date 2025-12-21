"""
Manga Processing Service: Application service for processing manga chapters.

This service orchestrates the full pipeline processing.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional
import time
import uuid

from src.core.pipeline.full_pipeline import process_manga_chapter, process_manga_volume
from src.presentation.api.exceptions import ProcessingError, ValidationError


class MangaProcessingService:
    """Service for processing manga chapters and volumes."""
    
    def __init__(self, output_base_dir: Path = Path("output")):
        """
        Initialize manga processing service.
        
        Args:
            output_base_dir: Base directory for output files
        """
        self.output_base_dir = output_base_dir
        self.output_base_dir.mkdir(parents=True, exist_ok=True)
    
    def process_chapter(
        self,
        manga_name: str,
        chapter_number: int,
        image_paths: List[str],
        *,
        enable_reading_order: bool = True,
        enable_character_reid: bool = True,
        enable_manpu: bool = True,
        enable_onomatopoeia: bool = True,
        enable_speaker_diarization: bool = True,
        enable_bgm: bool = True,
        enable_sfx: bool = True,
        enable_tts: bool = True,
        device: str = "cuda",
        text_language: str = "ja",
    ) -> Dict:
        """
        Process a single manga chapter.
        
        Args:
            manga_name: Name of the manga
            chapter_number: Chapter number
            image_paths: List of image file paths
            enable_*: Feature flags
            device: Device to use
            text_language: Language code
            
        Returns:
            Dictionary with processing results
            
        Raises:
            ProcessingError: If processing fails
            ValidationError: If input validation fails
        """
        # Validate inputs
        if not image_paths:
            raise ValidationError("At least one image path is required")
        
        # Convert string paths to Path objects
        try:
            chapter_images = [Path(path) for path in image_paths]
            
            # Validate all paths exist
            for img_path in chapter_images:
                if not img_path.exists():
                    raise ValidationError(f"Image file not found: {img_path}")
        except Exception as e:
            raise ValidationError(f"Invalid image paths: {e}") from e
        
        # Prepare output directory
        output_dir = self.output_base_dir / manga_name / f"chapter_{chapter_number}"
        
        # Process chapter
        start_time = time.time()
        
        try:
            result = process_manga_chapter(
                chapter_images=chapter_images,
                manga_name=manga_name,
                chapter_number=chapter_number,
                output_dir=output_dir,
                enable_reading_order=enable_reading_order,
                enable_character_reid=enable_character_reid,
                enable_manpu=enable_manpu,
                enable_onomatopoeia=enable_onomatopoeia,
                enable_speaker_diarization=enable_speaker_diarization,
                enable_bgm=enable_bgm,
                enable_sfx=enable_sfx,
                enable_tts=enable_tts,
                device=device,
                text_language=text_language,
            )
            
            processing_time = time.time() - start_time
            result["processing_time_seconds"] = processing_time
            
            return result
            
        except Exception as e:
            raise ProcessingError(
                f"Failed to process chapter {chapter_number}: {str(e)}",
                detail={"chapter_number": chapter_number, "manga_name": manga_name}
            ) from e
    
    def process_volume(
        self,
        manga_root: str,
        max_chapters: Optional[int] = None,
        *,
        enable_reading_order: bool = True,
        enable_character_reid: bool = True,
        enable_manpu: bool = True,
        enable_onomatopoeia: bool = True,
        enable_speaker_diarization: bool = True,
        enable_bgm: bool = True,
        enable_sfx: bool = True,
        enable_tts: bool = True,
        device: str = "cuda",
        text_language: str = "ja",
    ) -> Dict:
        """
        Process an entire manga volume.
        
        Args:
            manga_root: Root directory containing chapter folders
            max_chapters: Maximum chapters to process
            enable_*: Feature flags
            device: Device to use
            text_language: Language code
            
        Returns:
            Dictionary with processing results
            
        Raises:
            ProcessingError: If processing fails
            ValidationError: If input validation fails
        """
        # Validate manga root
        manga_root_path = Path(manga_root)
        if not manga_root_path.exists() or not manga_root_path.is_dir():
            raise ValidationError(f"Manga root directory not found: {manga_root}")
        
        # Process volume
        start_time = time.time()
        
        try:
            results = process_manga_volume(
                manga_root=manga_root_path,
                output_root=self.output_base_dir,
                max_chapters=max_chapters,
                enable_reading_order=enable_reading_order,
                enable_character_reid=enable_character_reid,
                enable_manpu=enable_manpu,
                enable_onomatopoeia=enable_onomatopoeia,
                enable_speaker_diarization=enable_speaker_diarization,
                enable_bgm=enable_bgm,
                enable_sfx=enable_sfx,
                enable_tts=enable_tts,
                device=device,
                text_language=text_language,
            )
            
            processing_time = time.time() - start_time
            
            return {
                "manga_name": manga_root_path.name,
                "chapters_processed": len(results),
                "chapters": results,
                "total_processing_time_seconds": processing_time,
            }
            
        except Exception as e:
            raise ProcessingError(
                f"Failed to process volume: {str(e)}",
                detail={"manga_root": manga_root}
            ) from e

