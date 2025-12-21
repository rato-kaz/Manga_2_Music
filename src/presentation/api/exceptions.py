"""
API Exceptions: Custom exceptions for API layer.

These exceptions are caught by FastAPI error handlers.
"""

from typing import Optional, Dict, Any


class APIException(Exception):
    """Base exception for API layer."""
    
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        detail: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.detail = detail or {}
        super().__init__(self.message)


class ValidationError(APIException):
    """Raised when request validation fails."""
    
    def __init__(self, message: str, detail: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=400, detail=detail)


class NotFoundError(APIException):
    """Raised when resource is not found."""
    
    def __init__(self, message: str, detail: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=404, detail=detail)


class ProcessingError(APIException):
    """Raised when processing fails."""
    
    def __init__(self, message: str, detail: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=500, detail=detail)


class JobNotFoundError(NotFoundError):
    """Raised when job is not found."""
    pass

