"""
Processing Routes: Endpoints for manga processing.

These routes handle chapter and volume processing requests.
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Request
from typing import Dict

from src.application.services.manga_processor import MangaProcessingService
from src.presentation.api.schemas import (
    ProcessChapterRequest,
    ProcessVolumeRequest,
    ChapterResult,
    VolumeResult,
)
from src.presentation.api.dependencies import get_processing_service
from src.presentation.api.exceptions import ProcessingError, ValidationError
from src.presentation.api.middleware.security import limiter, require_api_key
from src.infrastructure.logger import get_logger

logger = get_logger(__name__)


router = APIRouter(prefix="/api/v1/processing", tags=["processing"])


@router.post("/chapter", response_model=ChapterResult, status_code=202)
@limiter.limit("10/minute")  # Rate limiting
async def process_chapter(
    request: Request,
    body: ProcessChapterRequest,
    background_tasks: BackgroundTasks,
    service: MangaProcessingService = Depends(get_processing_service),
) -> ChapterResult:
    """
    Process a single manga chapter.
    
    This endpoint accepts chapter images and processes them through the full pipeline.
    Processing happens asynchronously in the background.
    
    Args:
        request: FastAPI request object
        body: Processing request with chapter details
        background_tasks: FastAPI background tasks
        service: Manga processing service
        
    Returns:
        ChapterResult with processing status
        
    Raises:
        HTTPException: If processing fails
    """
    # Optional: Require API key for protected endpoints
    # require_api_key(request)
    
    logger.info(f"Processing chapter {body.chapter_number} of {body.manga_name}")
    
    try:
        result = service.process_chapter(
            manga_name=body.manga_name,
            chapter_number=body.chapter_number,
            image_paths=body.image_paths,
            enable_reading_order=body.enable_reading_order,
            enable_character_reid=body.enable_character_reid,
            enable_manpu=body.enable_manpu,
            enable_onomatopoeia=body.enable_onomatopoeia,
            enable_speaker_diarization=body.enable_speaker_diarization,
            enable_bgm=body.enable_bgm,
            enable_sfx=body.enable_sfx,
            enable_tts=body.enable_tts,
            device=body.device,
            text_language=body.text_language,
        )
        
        logger.info(f"Chapter {body.chapter_number} processed successfully")
        return ChapterResult(**result)
        
    except ValidationError as e:
        logger.warning(f"Validation error: {e.message}")
        raise HTTPException(status_code=400, detail=e.message)
    except ProcessingError as e:
        logger.error(f"Processing error: {e.message}", exc_info=True)
        raise HTTPException(status_code=500, detail=e.message)


@router.post("/volume", response_model=VolumeResult, status_code=202)
@limiter.limit("5/minute")  # Lower rate limit for volume processing
async def process_volume(
    request: Request,
    body: ProcessVolumeRequest,
    background_tasks: BackgroundTasks,
    service: MangaProcessingService = Depends(get_processing_service),
) -> VolumeResult:
    """
    Process an entire manga volume.
    
    This endpoint processes multiple chapters from a manga root directory.
    Processing happens asynchronously in the background.
    
    Args:
        request: FastAPI request object
        body: Processing request with volume details
        background_tasks: FastAPI background tasks
        service: Manga processing service
        
    Returns:
        VolumeResult with processing status
        
    Raises:
        HTTPException: If processing fails
    """
    # Optional: Require API key for protected endpoints
    # require_api_key(request)
    
    logger.info(f"Processing volume from {body.manga_root}")
    
    try:
        result = service.process_volume(
            manga_root=body.manga_root,
            max_chapters=body.max_chapters,
            enable_reading_order=body.enable_reading_order,
            enable_character_reid=body.enable_character_reid,
            enable_manpu=body.enable_manpu,
            enable_onomatopoeia=body.enable_onomatopoeia,
            enable_speaker_diarization=body.enable_speaker_diarization,
            enable_bgm=body.enable_bgm,
            enable_sfx=body.enable_sfx,
            enable_tts=body.enable_tts,
            device=body.device,
            text_language=body.text_language,
        )
        
        logger.info(f"Volume processed successfully: {result['chapters_processed']} chapters")
        return VolumeResult(**result)
        
    except ValidationError as e:
        logger.warning(f"Validation error: {e.message}")
        raise HTTPException(status_code=400, detail=e.message)
    except ProcessingError as e:
        logger.error(f"Processing error: {e.message}", exc_info=True)
        raise HTTPException(status_code=500, detail=e.message)

