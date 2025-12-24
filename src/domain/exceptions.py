"""
Domain Exceptions: Custom exceptions for domain layer.

These exceptions represent domain-specific error conditions.
"""


class DomainException(Exception):
    """Base exception for domain layer."""

    pass


class InvalidBoundingBoxError(DomainException):
    """Raised when bounding box is invalid."""

    pass


class InvalidImageError(DomainException):
    """Raised when image is invalid."""

    pass


class PanelNotFoundError(DomainException):
    """Raised when panel is not found."""

    pass


class CharacterNotFoundError(DomainException):
    """Raised when character is not found."""

    pass


class InvalidReadingOrderError(DomainException):
    """Raised when reading order is invalid."""

    pass
