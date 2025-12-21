"""
Application Settings: Environment-based configuration.

This module provides centralized configuration management using Pydantic Settings.
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field, validator


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Settings
    api_host: str = Field("0.0.0.0", description="API host")
    api_port: int = Field(8000, ge=1, le=65535, description="API port")
    api_reload: bool = Field(False, description="Enable auto-reload (dev only)")
    
    # CORS Settings
    cors_origins: str = Field("", description="Comma-separated list of allowed origins")
    cors_allow_credentials: bool = Field(True, description="Allow credentials in CORS")
    
    # Logging
    log_level: str = Field("INFO", description="Logging level")
    log_file: Optional[str] = Field(None, description="Log file path")
    log_config_file: Optional[str] = Field(None, description="Logging config YAML file")
    
    # Processing Settings
    default_device: str = Field("cuda", description="Default device (cpu/cuda)")
    default_text_language: str = Field("ja", description="Default text language")
    output_base_dir: str = Field("output", description="Base output directory")
    
    # Model Settings
    magi_model_name: str = Field("ragavsachdeva/magiv2", description="MAGI model name")
    pages_per_batch: int = Field(2, ge=1, description="Pages per batch")
    ocr_batch_size: int = Field(16, ge=1, description="OCR batch size")
    max_long_edge: int = Field(1600, ge=1, description="Max image long edge")
    
    # Feature Flags
    enable_reading_order: bool = Field(True, description="Enable reading order")
    enable_character_reid: bool = Field(True, description="Enable character re-ID")
    enable_manpu: bool = Field(True, description="Enable manpu detection")
    enable_onomatopoeia: bool = Field(True, description="Enable onomatopoeia")
    enable_speaker_diarization: bool = Field(True, description="Enable speaker diarization")
    enable_bgm: bool = Field(True, description="Enable BGM generation")
    enable_sfx: bool = Field(True, description="Enable SFX generation")
    enable_tts: bool = Field(True, description="Enable TTS")
    
    # Security
    api_key: Optional[str] = Field(None, description="API key for authentication")
    rate_limit_per_minute: int = Field(60, ge=1, description="Rate limit per minute")
    
    # External Services
    openai_base_url: Optional[str] = Field(None, description="OpenAI base URL")
    openai_api_key: Optional[str] = Field(None, description="OpenAI API key")
    openai_model: Optional[str] = Field(None, description="OpenAI model name")
    
    @validator("cors_origins")
    def parse_cors_origins(cls, v: str) -> List[str]:
        """Parse comma-separated CORS origins."""
        if not v:
            return []
        return [origin.strip() for origin in v.split(",") if origin.strip()]
    
    @validator("log_level")
    def validate_log_level(cls, v: str) -> str:
        """Validate log level."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of {valid_levels}")
        return v.upper()
    
    @validator("default_device")
    def validate_device(cls, v: str) -> str:
        """Validate device."""
        if v not in ["cpu", "cuda"]:
            raise ValueError("Device must be 'cpu' or 'cuda'")
        return v
    
    @property
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.log_level != "DEBUG" and not self.api_reload
    
    @property
    def output_path(self) -> Path:
        """Get output directory as Path."""
        return Path(self.output_base_dir)
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """
    Get application settings (singleton pattern).
    
    Returns:
        Settings instance
    """
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings

