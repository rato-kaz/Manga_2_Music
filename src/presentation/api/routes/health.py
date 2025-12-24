"""
Health Check Routes: Endpoints for service health monitoring.
"""

from fastapi import APIRouter

from src.presentation.api.schemas import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """
    Health check endpoint.

    Returns:
        HealthResponse with service status
    """
    return HealthResponse(
        status="healthy",
        version="1.0.0",
    )


@router.get("/", response_model=HealthResponse)
async def root() -> HealthResponse:
    """
    Root endpoint.

    Returns:
        HealthResponse with service status
    """
    return await health_check()
