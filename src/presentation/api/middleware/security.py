"""
Security Middleware: Authentication, rate limiting, etc.
"""

from __future__ import annotations

from typing import Callable
from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from config.settings import get_settings

settings = get_settings()

# Rate limiter
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[f"{settings.rate_limit_per_minute}/minute"],
)

# Security scheme
security = HTTPBearer(auto_error=False)


async def verify_api_key(
    credentials: HTTPAuthorizationCredentials = None,
) -> bool:
    """
    Verify API key from request.
    
    Args:
        credentials: HTTP authorization credentials
        
    Returns:
        True if valid, False otherwise
    """
    if not settings.api_key:
        # No API key configured, allow all
        return True
    
    if not credentials:
        return False
    
    return credentials.credentials == settings.api_key


def require_api_key(request: Request) -> None:
    """
    Require API key for protected endpoints.
    
    Raises:
        HTTPException: If API key is invalid or missing
    """
    if not settings.api_key:
        # No API key configured, skip check
        return
    
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required",
        )
    
    if not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format",
        )
    
    api_key = auth_header.replace("Bearer ", "")
    if api_key != settings.api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )

