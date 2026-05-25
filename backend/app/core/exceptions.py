"""Domain-level exceptions translated into HTTP responses by middleware."""
from __future__ import annotations


class DomainError(Exception):
    """Base class — never raise directly."""
    status_code = 500
    code = "internal_error"

    def __init__(self, message: str | None = None):
        super().__init__(message or self.__class__.__name__)
        self.message = message or self.__class__.__name__


class NotFound(DomainError):
    status_code = 404
    code = "not_found"


class Unauthorized(DomainError):
    status_code = 401
    code = "unauthorized"


class Forbidden(DomainError):
    status_code = 403
    code = "forbidden"


class Conflict(DomainError):
    status_code = 409
    code = "conflict"


class ValidationFailed(DomainError):
    status_code = 422
    code = "validation_failed"


class ExternalServiceError(DomainError):
    status_code = 502
    code = "external_service_error"
