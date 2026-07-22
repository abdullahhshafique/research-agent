"""
Custom exceptions for the project.
"""


class ValidationError(Exception):
    """Input validation error."""
    pass


class QuotaExceededError(Exception):
    """User quota exceeded."""
    pass