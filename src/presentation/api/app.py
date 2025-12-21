"""
FastAPI Application: Main application setup and configuration.

This module creates and configures the FastAPI app instance.
"""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
import uvicorn

from src.presentation.api.routes import processing, health
from src.presentation.api.exceptions import APIException
from src.presentation.api.schemas import ErrorResponse
from src.infrastructure.logging_config import setup_logging
from src.infrastructure.logger import get_logger
from src.presentation.api.middleware.security import limiter, _rate_limit_exceeded_handler
from config.settings import get_settings
from pathlib import Path

settings = get_settings()

# Setup logging
log_file = Path(settings.log_file) if settings.log_file else None
setup_logging(
    log_level=settings.log_level,
    log_file=log_file,
    config_file=Path(settings.log_config_file) if settings.log_config_file else None,
)
logger = get_logger(__name__)


def create_app() -> FastAPI:
    """
    Create and configure FastAPI application.
    
    Returns:
        Configured FastAPI app instance
    """
    logger.info("Initializing FastAPI application")
    
    app = FastAPI(
        title="Manga-to-Music API",
        description="API for converting manga to audio experience",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )
    
    # Add CORS middleware
    cors_origins = settings.cors_origins if settings.cors_origins else ["*"]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=settings.cors_allow_credentials,
        allow_methods=["GET", "POST"],
        allow_headers=["*"],
    )
    
    # Add rate limiting
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    
    # Register routes
    app.include_router(health.router)
    app.include_router(processing.router)
    
    # Error handlers
    @app.exception_handler(APIException)
    async def api_exception_handler(request: Request, exc: APIException) -> JSONResponse:
        """Handle API exceptions."""
        logger.error(
            f"API exception: {exc.__class__.__name__} - {exc.message}",
            extra={"status_code": exc.status_code, "detail": exc.detail}
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(
                error=exc.__class__.__name__,
                message=exc.message,
                detail=exc.detail,
            ).dict(),
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """Handle general exceptions."""
        logger.exception("Unhandled exception", exc_info=exc)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponse(
                error="InternalServerError",
                message=str(exc),
            ).dict(),
        )
    
    logger.info("FastAPI application initialized successfully")
    return app


# Create app instance
app = create_app()


def main() -> None:
    """Run the FastAPI application."""
    logger.info(f"Starting FastAPI server on {settings.api_host}:{settings.api_port}")
    logger.info(f"Environment: {'Production' if settings.is_production else 'Development'}")
    
    uvicorn.run(
        "src.presentation.api.app:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload and not settings.is_production,
        log_config=None,  # Use our own logging config
    )


if __name__ == "__main__":
    main()
