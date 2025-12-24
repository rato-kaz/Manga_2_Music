"""
Infrastructure Exceptions: Exceptions for infrastructure layer.

These exceptions represent infrastructure-specific errors.
"""


class InfrastructureException(Exception):
    """Base exception for infrastructure layer."""

    pass


class ModelLoadError(InfrastructureException):
    """Raised when model fails to load."""

    pass


class ModelInferenceError(InfrastructureException):
    """Raised when model inference fails."""

    pass


class FileOperationError(InfrastructureException):
    """Raised when file operations fail."""

    pass


class AudioGenerationError(InfrastructureException):
    """Raised when audio generation fails."""

    pass


class TTSGenerationError(InfrastructureException):
    """Raised when TTS generation fails."""

    pass
