"""Project-specific exceptions."""

from __future__ import annotations


class GFJDError(Exception):
    """Base error for expected project failures."""


class ConfigurationError(GFJDError):
    """Raised when programme or repository configuration is invalid."""


class ValidationFailure(GFJDError):
    """Raised when validation must stop a command."""


class ReleaseVerificationError(GFJDError):
    """Raised when a release bundle cannot be verified."""
