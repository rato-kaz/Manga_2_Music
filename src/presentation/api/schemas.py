"""
API Schemas: Pydantic models for request/response validation.

These schemas define the API contract and provide automatic validation.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, validator

# ============================================================================
# Request Schemas
# ============================================================================


class ProcessChapterRequest(BaseModel):
    """Request schema for processing a manga chapter."""

    manga_name: str = Field(..., description="Name of the manga")
    chapter_number: int = Field(..., ge=1, description="Chapter number")
    image_paths: List[str] = Field(..., min_items=1, description="List of image file paths")

    # Optional flags
    enable_reading_order: bool = Field(True, description="Enable reading order resolution")
    enable_character_reid: bool = Field(True, description="Enable character re-identification")
    enable_manpu: bool = Field(True, description="Enable manpu detection")
    enable_onomatopoeia: bool = Field(True, description="Enable onomatopoeia classification")
    enable_speaker_diarization: bool = Field(True, description="Enable speaker diarization")
    enable_bgm: bool = Field(True, description="Enable BGM generation")
    enable_sfx: bool = Field(True, description="Enable SFX generation")
    enable_tts: bool = Field(True, description="Enable TTS generation")

    # Model options
    device: str = Field("cuda", description="Device to use (cpu or cuda)")
    text_language: str = Field("ja", description="Text language code")

    @validator("image_paths")
    def validate_image_paths(cls, v: List[str]) -> List[str]:
        """Validate that image paths exist."""
        for path_str in v:
            path = Path(path_str)
            if not path.exists():
                raise ValueError(f"Image file not found: {path_str}")
        return v

    @validator("device")
    def validate_device(cls, v: str) -> str:
        """Validate device option."""
        if v not in ["cpu", "cuda"]:
            raise ValueError("Device must be 'cpu' or 'cuda'")
        return v


class ProcessVolumeRequest(BaseModel):
    """Request schema for processing an entire manga volume."""

    manga_root: str = Field(..., description="Root directory containing chapter folders")
    max_chapters: Optional[int] = Field(None, ge=1, description="Maximum chapters to process")

    # Same flags as ProcessChapterRequest
    enable_reading_order: bool = Field(True, description="Enable reading order resolution")
    enable_character_reid: bool = Field(True, description="Enable character re-identification")
    enable_manpu: bool = Field(True, description="Enable manpu detection")
    enable_onomatopoeia: bool = Field(True, description="Enable onomatopoeia classification")
    enable_speaker_diarization: bool = Field(True, description="Enable speaker diarization")
    enable_bgm: bool = Field(True, description="Enable BGM generation")
    enable_sfx: bool = Field(True, description="Enable SFX generation")
    enable_tts: bool = Field(True, description="Enable TTS generation")

    device: str = Field("cuda", description="Device to use (cpu or cuda)")
    text_language: str = Field("ja", description="Text language code")

    @validator("manga_root")
    def validate_manga_root(cls, v: str) -> str:
        """Validate that manga root directory exists."""
        path = Path(v)
        if not path.exists() or not path.is_dir():
            raise ValueError(f"Manga root directory not found: {v}")
        return v


# ============================================================================
# Response Schemas
# ============================================================================


class ProcessingStatus(BaseModel):
    """Status of a processing job."""

    job_id: str = Field(..., description="Unique job identifier")
    status: str = Field(..., description="Job status: pending, processing, completed, failed")
    progress: float = Field(0.0, ge=0.0, le=100.0, description="Progress percentage")
    current_stage: Optional[str] = Field(None, description="Current processing stage")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class ChapterResult(BaseModel):
    """Result of processing a chapter."""

    chapter_number: int = Field(..., description="Chapter number")
    manga_name: str = Field(..., description="Manga name")
    status: str = Field(..., description="Processing status")
    metadata_json_path: Optional[str] = Field(None, description="Path to metadata JSON")
    final_audio_path: Optional[str] = Field(None, description="Path to final audio file")
    audio_dir: Optional[str] = Field(None, description="Directory containing audio files")
    speech_dir: Optional[str] = Field(None, description="Directory containing speech files")
    num_pages: int = Field(..., description="Number of pages processed")
    num_panels: int = Field(..., description="Number of panels processed")
    processing_time_seconds: Optional[float] = Field(None, description="Processing time in seconds")


class VolumeResult(BaseModel):
    """Result of processing an entire volume."""

    manga_name: str = Field(..., description="Manga name")
    chapters_processed: int = Field(..., description="Number of chapters processed")
    chapters: List[ChapterResult] = Field(default_factory=list, description="Chapter results")
    total_processing_time_seconds: Optional[float] = Field(
        None, description="Total processing time"
    )


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = Field("healthy", description="Service status")
    version: str = Field(..., description="API version")
    timestamp: datetime = Field(default_factory=datetime.now)


class ErrorResponse(BaseModel):
    """Error response schema."""

    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    detail: Optional[Dict[str, Any]] = Field(None, description="Additional error details")


# ============================================================================
# Metadata Schemas (for API responses)
# ============================================================================


class PanelMetadata(BaseModel):
    """Panel metadata for API response."""

    panel_id: int
    reading_order: Optional[int] = None
    scene_type: Optional[str] = None
    emotions: List[str] = Field(default_factory=list)
    timeline: Optional[Dict[str, float]] = None


class PageMetadata(BaseModel):
    """Page metadata for API response."""

    page_id: int
    panels: List[PanelMetadata] = Field(default_factory=list)


class ChapterMetadata(BaseModel):
    """Chapter metadata for API response."""

    chapter_number: int
    manga_name: str
    pages: List[PageMetadata] = Field(default_factory=list)
    total_panels: int
    total_duration_seconds: Optional[float] = None
